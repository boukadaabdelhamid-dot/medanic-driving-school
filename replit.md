# Workspace

## Medanic desktop application (imported project)

The imported product is the Python/Tkinter driving-school management app,
not a TypeScript web application. Preserve its existing stack and structure.

- Click **Run** to start the **Medanic Desktop** workflow, then open the
  desktop/VNC viewer to interact with it.
- Launch command: `python scripts/run_medanic.py`.
- Python dependencies are tracked in `pyproject.toml` and `uv.lock`: Pillow,
  reportlab, arabic-reshaper, and python-bidi.
- System dependencies include `python312Packages.tkinter` and `dejavu_fonts`.
  The launcher exposes Nix's separately packaged Tk extension to Python.
- The original license check is unchanged: a new installation has a 48-hour
  trial, after which a legitimate license is required.
- SQLite data is stored beside the main script in `driving_school.db`.
  Back up that file before moving the app or changing data.
- Existing Windows EXE build scripts and local-printer integration are not
  part of this Linux desktop setup. Replit's desktop viewer is not a public
  multi-user website.
- No external API credentials are required to start the desktop app.

The sections below describe the pre-existing workspace scaffolding, not the
imported Medanic application.

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
