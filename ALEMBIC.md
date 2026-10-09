# Alembic guide

How database migrations work in this project.

## Setup (one-time)

The migration tooling needs a running Postgres and a driver to talk to it. Both are already in place:

- `docker-compose.yml` — Postgres 16 container (`itemproject-db`), db/user/pass all `itemproject`, port `5432`
- `psycopg2-binary` — installed in `.venv`, required for SQLAlchemy/Alembic to connect to Postgres
- `alembic/env.py` — reads the connection string from the `DATABASE_URL` env var, falling back to `postgresql://itemproject:itemproject@localhost:5432/itemproject` if unset. It also imports `Base` from `app/adapters/orm.py` and sets `target_metadata = Base.metadata`, which is what makes autogenerate possible.

## Day to day

```bash
make start                 # start Postgres (waits until it's actually ready)
source .venv/bin/activate  # activate the venv so `alembic` is on PATH
```

### 1. Change your model

Edit `app/adapters/orm.py` (the SQLAlchemy models — `Base`, `ItemModel`, etc). This file is the source of truth Alembic diffs against; it is intentionally separate from `app/domain/entity/item.py`, which is the plain domain entity and has no SQLAlchemy in it.

### 2. Generate a migration

```bash
alembic revision --autogenerate -m "short description of the change"
```

This connects to the live DB, reflects its current schema, diffs it against `Base.metadata`, and writes a new file in `alembic/versions/`.

**Always open the generated file before applying it.** Check for two things:

- The `upgrade()`/`downgrade()` bodies actually contain `op.` calls — not just `pass`. An empty body means Alembic saw no diff (or something went wrong writing the file) and applying it will be a silent no-op.
- The diff matches what you expected. Autogenerate is good but not perfect — it won't detect table/column renames (it sees them as a drop + add), doesn't track `CHECK` constraints well, and needs `nullable=False` columns on non-empty tables to have a `server_default` or a manual data backfill step, or the `ALTER TABLE` will fail.

### 3. Apply it

```bash
alembic upgrade head
```

### 4. Verify it actually landed

Don't just trust the command exit code — check the real schema:

```bash
docker compose exec -T db psql -U itemproject -d itemproject -c "\d items"
```

or:

```bash
alembic current   # should print the new revision id as head
```

## Other useful commands

| Command | What it does |
|---|---|
| `alembic history` | Lists all revisions in order, marks which is `(head)` |
| `alembic current` | Shows which revision the DB is actually stamped at |
| `alembic downgrade -1` | Rolls back the most recent migration |
| `alembic upgrade <revision>` | Upgrades/downgrades to a specific revision id |
| `alembic revision -m "..."` | Creates an **empty** migration for you to write by hand (no `--autogenerate`) — use this only when you need something autogenerate can't express, e.g. data migrations, renames, custom SQL |

## Production workflow

Everything above is fine for local dev, where you're the only one touching the DB and it's OK to rewrite history if something breaks. None of that holds once migrations are shared or run against a real environment — treat migration files as immutable, append-only history from the moment they're committed.

### Commit migrations immediately, and never rewrite an applied one

A migration file that's been merged (or even just pushed to a shared branch) has effectively already run somewhere, or will soon. Once that's true:

- **Never edit, delete, or renumber an existing migration file.** If it's wrong, write a *new* migration that corrects it. Rewriting history (like consolidating `bffe85b88c41` earlier in this project) is only safe because those files had never left this machine — do it once anything's shared and every other environment's `alembic_version` pointer breaks, exactly like the `KeyError` you hit today, except now on a database you can't just re-stamp by hand.
- Commit the migration file in the **same PR** as the model change that produced it. A model change without its migration (or a migration without the model change) is a broken PR.
- Keep a single linear head. If two branches each add a migration off the same parent, merging them creates two heads and `alembic upgrade head` becomes ambiguous. Run `alembic heads` before merging; if there's more than one, resolve it with `alembic merge` or by rebasing one branch's revision onto the other's.

### Running migrations against a real environment

- Migrations run as their **own deploy step**, before the new application code starts serving traffic — not inside app startup (`on_startup` hooks) and not from a developer's laptop against a prod `DATABASE_URL`. A CI/CD pipeline step (or a Kubernetes init container / one-off job) runs `alembic upgrade head` with environment-specific credentials, and the deploy only proceeds if that step succeeds.
- Each environment gets its own `DATABASE_URL` (dev/staging/prod), injected as a secret by the deploy system — never hardcoded, never the same credentials as local. `alembic/env.py` already reads it from the environment for exactly this reason.
- Take a backup (or confirm automated backups are current) immediately before running a migration against production. `alembic downgrade` is not a substitute for a backup — some operations (dropping a column, deleting data) aren't reversible by a downgrade even if you wrote one.
- Test the migration against a copy of production-shaped data first (staging, or a restored backup) — especially for anything on a large or hot table. `alembic upgrade head` on an empty local dev DB tells you almost nothing about how long an `ALTER TABLE` will lock a multi-million-row table in prod.

### Writing migrations that are safe to deploy

- **Expand/contract for anything that could break the currently-running app.** Old application code is still running against the DB during a rolling deploy, so a migration that drops or renames a column the old code still reads will break it mid-deploy. Split it into separate migrations/deploys instead: add the new column (expand) → deploy code that writes to both/reads the new one → backfill data → deploy code that stops using the old column → drop the old column (contract).
- **Adding a `NOT NULL` column to a non-empty table** needs a `server_default` (so the `ALTER TABLE` can fill existing rows) or a two-step migration: add it nullable, backfill the data, then add the `NOT NULL` constraint in a follow-up migration. Without one of these, the migration will fail — or on Postgres, succeed but hold a long lock while it rewrites every row.
- Prefer additive, backwards-compatible changes over destructive ones where possible, and assume any migration that isn't purely additive needs its own deploy, not to be bundled with unrelated app changes.
- Always re-read the autogenerated file before committing it (see "Always open the generated file before applying it" above) — this matters even more in production, where an empty or wrong migration silently passing CI means broken state on every environment it touches, not just your laptop.

## Notes specific to this project

- Postgres doesn't need to be restarted for schema changes — `docker compose` just needs the container running; `make start` is idempotent (safe to re-run, it no-ops if already up).
- `make stop` stops the container without deleting data; `make down` removes the container **and** its volume (all data gone) — only use this if you want a clean slate.
- Never hand-edit an already-applied migration file to "fix" it after the fact — Alembic tracks the current revision in the `alembic_version` table and won't re-run something it already thinks succeeded. If a migration was wrong, write a new one that corrects it (or `downgrade` past it, delete it, and regenerate, but only if it was never applied anywhere but your own machine).
