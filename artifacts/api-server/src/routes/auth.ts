import { Router, type IRouter } from "express";
import {
  GetCurrentUserResponse,
  LoginBody,
  LoginResponse,
  SetupInitialAdminBody,
  SetupInitialAdminResponse,
} from "@workspace/api-zod";
import { pool } from "@workspace/db";
import {
  canUseSetupKey,
  clearSessionCookie,
  hashPassword,
  publicUser,
  setSessionCookie,
  userCount,
  validateSetupKey,
  verifyPassword,
  type PublicUser,
} from "../lib/auth";

const router: IRouter = Router();
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
    username: user.username,
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
  if (!canUseSetupKey()) {
    res.status(503).json({
      error: "ADMIN_SETUP_KEY is not configured. Configure it before first setup.",
    });
    return;
  }
  if (!validateSetupKey(parsed.data.setupKey)) {
    res.status(403).json({ error: "The setup key is invalid." });
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
        parsed.data.username.trim(),
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
      res.status(409).json({ error: "That username is already in use." });
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
    res.status(400).json({ error: "Enter a username and password." });
    return;
  }
  try {
    const result = await pool.query(
      `SELECT id, username, password_hash, full_name, role, permissions
         FROM users WHERE username = $1`,
      [parsed.data.username.trim()],
    );
    const row = result.rows[0];
    if (!row) {
      res.status(401).json({ error: "Username or password is incorrect." });
      return;
    }
    const verification = verifyPassword(
      parsed.data.password,
      String(row.password_hash),
    );
    if (!verification.valid) {
      res.status(401).json({ error: "Username or password is incorrect." });
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
