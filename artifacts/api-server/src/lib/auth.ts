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
  mustChangePassword: boolean;
  permissions: Record<string, boolean>;
};

export const INITIAL_ADMIN_EMAIL = "admin@midanic.com";
const INITIAL_ADMIN_PASSWORD_MIN_LENGTH = 12;

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

export function assertSessionSecretConfigured() {
  sessionSecret();
}

export function getInitialAdminPassword() {
  const password = process.env.INITIAL_ADMIN_PASSWORD;
  if (password && password.length < INITIAL_ADMIN_PASSWORD_MIN_LENGTH) {
    throw new Error(
      `INITIAL_ADMIN_PASSWORD must contain at least ${INITIAL_ADMIN_PASSWORD_MIN_LENGTH} characters.`,
    );
  }
  return password || null;
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

export async function initializeConfiguredAdminPassword() {
  const password = getInitialAdminPassword();
  if (!password) return false;

  sessionSecret();
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("SELECT pg_advisory_xact_lock(948271604)");
    const existing = await client.query<{
      id: number;
      initial_password_configured: boolean;
    }>(
      `SELECT id, initial_password_configured
         FROM users
        WHERE lower(username) = $1
        LIMIT 1
        FOR UPDATE`,
      [INITIAL_ADMIN_EMAIL],
    );
    const admin = existing.rows[0];
    if (!admin || admin.initial_password_configured) {
      await client.query("COMMIT");
      return false;
    }

    await client.query(
      `UPDATE users
          SET password_hash = $1,
              must_change_password = TRUE,
              initial_password_configured = TRUE
        WHERE id = $2`,
      [hashPassword(password), admin.id],
    );
    await client.query("COMMIT");
    return true;
  } catch (error) {
    await client.query("ROLLBACK").catch(() => undefined);
    throw error;
  } finally {
    client.release();
  }
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
    `SELECT id, username, full_name, role, permissions, must_change_password
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
    mustChangePassword: Boolean(row.must_change_password),
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
  if (req.user.mustChangePassword) {
    res.status(403).json({ error: "Change the temporary password to continue." });
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
  must_change_password: boolean;
  permissions: Record<string, boolean> | null;
}): PublicUser {
  return {
    id: Number(row.id),
    email: row.username,
    fullName: row.full_name ?? "",
    role: row.role === "admin" ? "admin" : "trainer",
    mustChangePassword: Boolean(row.must_change_password),
    permissions: row.permissions ?? {},
  };
}
