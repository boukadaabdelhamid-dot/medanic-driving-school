import { createHash, createHmac, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";
import type { RequestHandler, Response } from "express";
import { pool } from "@workspace/db";

const COOKIE_NAME = "medanic_session";
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7;
const PASSWORD_SCRYPT_BYTES = 64;

export type PublicUser = {
  id: number;
  email: string;
  fullName: string;
  role: "admin" | "trainer";
  permissions: Record<string, boolean>;
};

declare global {
  namespace Express {
    interface Request {
      user?: PublicUser;
    }
  }
}

function sessionSecret() {
  const secret = process.env.SESSION_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error("SESSION_SECRET must contain at least 32 characters.");
  }
  return secret;
}

function safeEqual(left: string, right: string) {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

export function hashPassword(password: string) {
  const salt = randomBytes(16).toString("base64url");
  const derived = scryptSync(password, salt, PASSWORD_SCRYPT_BYTES).toString(
    "base64url",
  );
  return `scrypt$${salt}$${derived}`;
}

export function verifyPassword(password: string, encoded: string) {
  if (encoded.startsWith("scrypt$")) {
    const [, salt, expected] = encoded.split("$");
    if (!salt || !expected) return { valid: false, needsUpgrade: false };
    const actual = scryptSync(password, salt, PASSWORD_SCRYPT_BYTES).toString(
      "base64url",
    );
    return { valid: safeEqual(actual, expected), needsUpgrade: false };
  }

  // The desktop app stores SHA-256 hashes. Upgrade the hash only after a
  // successful login so existing accounts can continue to sign in safely.
  const legacyHash = createHash("sha256").update(password, "utf8").digest("hex");
  const valid =
    /^[a-f0-9]{64}$/i.test(encoded) && safeEqual(legacyHash, encoded.toLowerCase());
  return { valid, needsUpgrade: valid };
}

function signSession(body: string) {
  return createHmac("sha256", sessionSecret()).update(body).digest("base64url");
}

export function setSessionCookie(res: Response, userId: number) {
  const expires = Math.floor(Date.now() / 1000) + SESSION_MAX_AGE_SECONDS;
  const body = `${userId}.${expires}`;
  const token = `${body}.${signSession(body)}`;
  res.cookie(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS * 1000,
  });
}

export function clearSessionCookie(res: Response) {
  res.clearCookie(COOKIE_NAME, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });
}

async function getUserFromRequestCookie(cookie?: string): Promise<PublicUser | null> {
  if (!cookie) return null;
  const lastDot = cookie.lastIndexOf(".");
  if (lastDot < 0) return null;
  const body = cookie.slice(0, lastDot);
  const signature = cookie.slice(lastDot + 1);
  const [idText, expiryText] = body.split(".");
  const id = Number(idText);
  const expires = Number(expiryText);
  if (!Number.isSafeInteger(id) || id < 1 || !Number.isSafeInteger(expires)) {
    return null;
  }
  if (expires <= Math.floor(Date.now() / 1000)) return null;

  let expected: string;
  try {
    expected = signSession(body);
  } catch {
    return null;
  }
  if (!safeEqual(signature, expected)) return null;

  const result = await pool.query(
    `SELECT id, username, full_name, role, permissions
       FROM users WHERE id = $1`,
    [id],
  );
  const row = result.rows[0];
  if (!row) return null;
  const permissions =
    row.permissions && typeof row.permissions === "object"
      ? (row.permissions as Record<string, boolean>)
      : {};
  return {
    id: Number(row.id),
    email: String(row.username),
    fullName: String(row.full_name ?? ""),
    role: row.role === "admin" ? "admin" : "trainer",
    permissions,
  };
}

export const loadOptionalUser: RequestHandler = async (req, _res, next) => {
  try {
    req.user = (await getUserFromRequestCookie(
      req.cookies?.[COOKIE_NAME],
    )) ?? undefined;
    next();
  } catch (error) {
    req.log.error({ err: error }, "Could not load authenticated user");
    next(error);
  }
};

export const requireAuth: RequestHandler = (req, res, next) => {
  if (!req.user) {
    res.status(401).json({ error: "Authentication required." });
    return;
  }
  next();
};

export const requireAdmin: RequestHandler = (req, res, next) => {
  if (req.user?.role !== "admin") {
    res.status(403).json({ error: "Administrator access required." });
    return;
  }
  next();
};

export function requirePermission(permission: string): RequestHandler {
  return (req, res, next) => {
    if (req.user?.role === "admin" || req.user?.permissions[permission]) {
      next();
      return;
    }
    res.status(403).json({ error: "You do not have permission for this action." });
  };
}

export async function userCount() {
  const result = await pool.query<{ count: string }>(
    "SELECT COUNT(*)::text AS count FROM users",
  );
  return Number(result.rows[0]?.count ?? 0);
}

export function publicUser(row: {
  id: number;
  username: string;
  full_name: string;
  role: string;
  permissions: Record<string, boolean> | null;
}): PublicUser {
  return {
    id: Number(row.id),
    email: row.username,
    fullName: row.full_name ?? "",
    role: row.role === "admin" ? "admin" : "trainer",
    permissions: row.permissions ?? {},
  };
}
