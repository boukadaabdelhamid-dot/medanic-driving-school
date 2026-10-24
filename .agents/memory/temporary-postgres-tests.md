---
name: Temporary PostgreSQL tests
description: Runtime setup for isolated local PostgreSQL integration tests.
---

When running an isolated PostgreSQL test server, set `unix_socket_directories` to the temporary test directory and bind TCP to `127.0.0.1`.

**Why:** The runtime's PostgreSQL default socket directory `/run/postgresql` may not exist, which prevents the local server from starting.

**How to apply:** Pass `-c unix_socket_directories=<temporary-directory>` in the `pg_ctl -o` startup arguments; do not use the workspace or production database for isolated auth tests.
