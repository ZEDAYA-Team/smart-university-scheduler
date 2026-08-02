# Smart University Timetable Management System

SUTMS generates and validates conflict-free university timetables for AAU CNCS using Google OR-Tools CP-SAT.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string
- The scheduling worker uses the Python environment created from `pyproject.toml`; install dependencies with `uv sync` when setting up a fresh environment.

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `lib/api-spec/openapi.yaml` — source of truth for scheduling request and response contracts
- `artifacts/api-server/src/routes/scheduling.ts` — scheduling API endpoints and request validation
- `artifacts/api-server/src/scheduling/solver.py` — OR-Tools CP-SAT model and conflict detector
- `artifacts/api-server/src/scheduling/worker.ts` — bounded Node-to-Python worker bridge
- `lib/api-client-react/src/generated/` — generated React Query hooks and TypeScript types

## Architecture decisions

- Scheduling is isolated as a Python OR-Tools worker while the existing Node API remains the transport and authentication boundary.
- The first scheduling slice accepts in-memory scheduling data, matching the paper ERD without prematurely locking the unreviewed database design into migrations.
- Fixed time slots are represented by day and minute ranges; overlapping ranges are treated as conflicts, not only identical slot IDs.
- Student enrollment is represented as `studentIds` on each offering in this API slice and can later be populated from the ERD's `ENROLLMENT` table.

## Product

- `GET /api/scheduling/health` reports OR-Tools availability.
- `POST /api/scheduling/generate` creates a timetable while enforcing room, lecturer, section, student, capacity, room type, and availability constraints.
- `POST /api/scheduling/conflicts` validates manual or edited placements and returns human-readable conflict codes.

## User preferences

- Authentication already exists and is outside the scheduling implementation; scheduling routes do not replace or duplicate it.

## Gotchas

- Run API commands from the workspace root when possible. The managed API workflow changes its working directory, so the worker bridge resolves both artifact-local and workspace-root paths.
- After changing `lib/api-spec/openapi.yaml`, run `pnpm --filter @workspace/api-spec run codegen`.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
