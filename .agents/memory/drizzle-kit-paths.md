---
name: Drizzle Kit migration paths
description: Path configuration required for Drizzle Kit migration generation in this workspace.
---

Keep Drizzle Kit `schema` and `out` paths relative to the database package (for example, `./src/schema/index.ts` and `./drizzle`), not absolute paths derived from `__dirname`.

**Why:** The installed Drizzle Kit prepended the working directory to the absolute output path, so it looked for migration snapshots under an invalid `.//home/...` path and failed to generate.

**How to apply:** Run migration generation through the `@workspace/db` package script and verify it creates the next SQL migration and snapshot in `lib/db/drizzle/`.
