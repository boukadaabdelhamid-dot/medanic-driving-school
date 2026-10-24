import app from "./app";
import { db, pool } from "@workspace/db";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { existsSync } from "node:fs";
import path from "node:path";
import { logger } from "./lib/logger";
import { ensureDefaultAccounts } from "./lib/ledger";
import { initializeConfiguredAdminPassword } from "./lib/auth";

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

function workspaceRoot() {
  if (existsSync(path.join(process.cwd(), "lib/db/drizzle"))) {
    return process.cwd();
  }
  return path.resolve(process.cwd(), "../..");
}

async function start() {
  try {
    await migrate(db, {
      migrationsFolder: path.join(workspaceRoot(), "lib/db/drizzle"),
    });
    await ensureDefaultAccounts(pool);
    const initializedAdminPassword = await initializeConfiguredAdminPassword();
    if (initializedAdminPassword) {
      logger.info(
        "Configured the initial administrator password; a password change is required after sign-in",
      );
    }
    app.listen(port, () => {
      logger.info({ port }, "Server listening");
    });
  } catch (error) {
    logger.fatal({ err: error }, "Database migration or server startup failed");
    await pool.end().catch(() => undefined);
    process.exit(1);
  }
}

void start();
