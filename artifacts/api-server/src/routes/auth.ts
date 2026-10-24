import { Router, type IRouter } from "express";
import {
  GetCurrentUserResponse,
  LoginBody,
  LoginResponse,
  SetupInitialAdminBody,
  SetupInitialAdminResponse,
  UpdateAccountBody,
  UpdateAccountResponse,
} from "@workspace/api-zod";
import { pool } from "@workspace/db";
import {
  clearSessionCookie,
  hashPassword,
  publicUser,
  setSessionCookie,
  userCount,
  verifyPassword,
  type PublicUser,
} from "../lib/auth";

const router: IRouter = Router();
const INITIAL_ADMIN_EMAIL = "admin@midanic.com";
const loginWindows = new Map<string, { count: number; resetAt: number }>();
const LOGIN_LIMIT = 8;
const LOGIN_WINDOW_MS = 10 * 60 * 1000;

function rejectLoginBurst(key: string) {
  const now = Date.now();
  const current = loginWindows.get(key);
  if (!current || current.resetAt <= now) {
    loginWindows.set(key, { count: 1, resetAt: now + LOGIN_WINDOW_MS });
    return false;
  }
  current.count += 1;
  return current.count > LOGIN_LIMIT;
}

function publicUserResponse(user: PublicUser) {
  return {
    id: user.id,
    email: user.email,
    fullName: user.fullName,
    role: user.role,
    permissions: user.permissions,
  };
}

router.get("/auth/setup-required", async (req, res) => {
  try {
    res.json({ required: (await userCount()) === 0 });
  } catch (error) {
    req.log.error({ err: error }, "Could not check initial setup status");
    res.status(503).json({ error: "The database is not available." });
  }
});

router.post("/auth/setup", async (req, res) => {
  const parsed = SetupInitialAdminBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "Review the setup form and try again." });
    return;
  }
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query("SELECT pg_advisory_xact_lock(948271604)");
    const count = await client.query<{ count: string }>(
      "SELECT COUNT(*)::text AS count FROM users",
    );
    if (Number(count.rows[0]?.count ?? 0) > 0) {
      await client.query("ROLLBACK");
      res.status(409).json({ error: "The initial administrator already exists." });
      return;
    }
    const inserted = await client.query(
      `INSERT INTO users (username, password_hash, role, full_name, permissions)
       VALUES ($1, $2, 'admin', $3, '{}'::jsonb)
       RETURNING id, username, full_name, role, permissions`,
      [
        INITIAL_ADMIN_EMAIL,
        hashPassword(parsed.data.password),
        parsed.data.fullName.trim(),
      ],
    );
    await client.query("COMMIT");
    const user = publicUser(inserted.rows[0]);
    setSessionCookie(res, user.id);
    res.status(201).json(SetupInitialAdminResponse.parse(publicUserResponse(user)));
  } catch (error) {
    await client.query("ROLLBACK").catch(() => undefined);
    if ((error as { code?: string }).code === "23505") {
      res.status(409).json({ error: "That email address is already in use." });
      return;
    }
    req.log.error({ err: error }, "Initial administrator setup failed");
    res.status(500).json({ error: "Could not complete initial setup." });
  } finally {
    client.release();
  }
});

router.post("/auth/login", async (req, res) => {
  const key = req.ip || "unknown";
  if (rejectLoginBurst(key)) {
    res.status(429).json({ error: "Too many sign-in attempts. Try again later." });
    return;
  }
  const parsed = LoginBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "Enter an email address and password." });
    return;
  }
  try {
    const result = await pool.query(
      `SELECT id, username, password_hash, full_name, role, permissions
         FROM users WHERE lower(username) = $1`,
      [parsed.data.email.trim().toLowerCase()],
    );
    const row = result.rows[0];
    if (!row) {
      res.status(401).json({ error: "Email or password is incorrect." });
      return;
    }
    const verification = verifyPassword(
      parsed.data.password,
      String(row.password_hash),
    );
    if (!verification.valid) {
      res.status(401).json({ error: "Email or password is incorrect." });
      return;
    }
    if (verification.needsUpgrade) {
      await pool.query("UPDATE users SET password_hash = $1 WHERE id = $2", [
        hashPassword(parsed.data.password),
        row.id,
      ]);
    }
    const user = publicUser(row);
    setSessionCookie(res, user.id);
    res.json(LoginResponse.parse(publicUserResponse(user)));
  } catch (error) {
    if ((error as Error).message.includes("SESSION_SECRET")) {
      res.status(503).json({
        error: "SESSION_SECRET is not configured for this server.",
      });
      return;
    }
    req.log.error({ err: error }, "Sign-in failed");
    res.status(503).json({ error: "Sign-in is temporarily unavailable." });
  }
});

router.patch("/auth/account", async (req, res): Promise<void> => {
  if (!req.user) {
    res.status(401).json({ error: "Authentication required." });
    return;
  }

  const parsed = UpdateAccountBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "Review the account update fields." });
    return;
  }

  const email = parsed.data.email?.trim().toLowerCase();
  if (!email && !parsed.data.newPassword) {
    res.status(400).json({ error: "Provide a new email or password." });
    return;
  }

  try {
    const found = await pool.query(
      `SELECT id, username, password_hash
         FROM users WHERE id = $1`,
      [req.user.id],
    );
    const row = found.rows[0];
    if (!row) {
      res.status(401).json({ error: "Authentication required." });
      return;
    }

    const verification = verifyPassword(
      parsed.data.currentPassword,
      String(row.password_hash),
    );
    if (!verification.valid) {
      res.status(400).json({ error: "The current password is incorrect." });
      return;
    }

    const nextEmail = email ?? String(row.username);
    const nextPasswordHash = parsed.data.newPassword
      ? hashPassword(parsed.data.newPassword)
      : verification.needsUpgrade
        ? hashPassword(parsed.data.currentPassword)
        : String(row.password_hash);
    const updated = await pool.query(
      `UPDATE users
          SET username = $1, password_hash = $2
        WHERE id = $3
        RETURNING id, username, full_name, role, permissions`,
      [nextEmail, nextPasswordHash, req.user.id],
    );
    const user = publicUser(updated.rows[0]);
    res.json(UpdateAccountResponse.parse(publicUserResponse(user)));
  } catch (error) {
    if ((error as { code?: string }).code === "23505") {
      res.status(409).json({ error: "That email address is already in use." });
      return;
    }
    req.log.error({ err: error }, "Account update failed");
    res.status(503).json({ error: "The account could not be updated right now." });
  }
});

router.get("/auth/me", (req, res) => {
  if (!req.user) {
    res.status(401).json({ error: "Authentication required." });
    return;
  }
  res.json(GetCurrentUserResponse.parse(publicUserResponse(req.user)));
});

router.post("/auth/logout", (_req, res) => {
  clearSessionCookie(res);
  res.status(204).end();
});

export default router;
