# Database — `schema.sql` / `seed.sql`

Two hand-authored SQL files for standing up a fresh **Supabase / PostgreSQL**
database directly, without running the Python app.

| File | What it does |
|---|---|
| [`schema.sql`](schema.sql) | Native-PostgreSQL DDL for the six core tables: **users, stores, inspections, violations, complaints, reports**. PKs, FKs (with `ON DELETE` rules), `created_at`/`updated_at` (+ an `updated_at` trigger), CHECK constraints and indexes. |
| [`seed.sql`](seed.sql) | 10 sample stores across **Mumbai, Pune, Nashik** + the users they reference + a small set of inspections / violations / complaints / reports so every table has data. Idempotent (fixed UUIDs, `ON CONFLICT DO NOTHING`). |

## Run

```bash
psql "$DATABASE_URL" -f schema.sql
psql "$DATABASE_URL" -f seed.sql
```

In the Supabase dashboard: **SQL Editor → paste → Run** (both are re-runnable).

Seed logins: `admin@franchiseguard.ai` / `Admin12345!`; every other user /
`Demo1234!`.

## Relationship to the SQLAlchemy models & Alembic

These files are a **standalone reference / bootstrap**. The running application
is normally schema-managed by **Alembic**
([`alembic/versions/0001_initial_schema.py`](alembic/versions/0001_initial_schema.py)),
which is the source of truth for the app and also creates an **`ai_analyses`**
table (omitted here on purpose — this deliverable is the six core tables only).

`schema.sql` deliberately uses idiomatic native Postgres where the ORM migration
uses portable equivalents:

| Concern | `schema.sql` (native) | ORM / Alembic (portable) |
|---|---|---|
| Primary keys | `uuid` + `gen_random_uuid()` | `varchar(36)` via a `GUID` TypeDecorator |
| Enums | `CREATE TYPE ... AS ENUM` | `varchar` + app-side `Enum(native_enum=False)` |
| JSON columns | `jsonb` | `json` |
| `updated_at` | `BEFORE UPDATE` trigger | SQLAlchemy `onupdate=func.now()` |

The SQLAlchemy models read and write correctly against **either** representation
(string ⇄ `uuid`, string ⇄ native enum, and `json`/`jsonb` are interchangeable
to the driver). Pick one per environment:

- **App-managed (recommended for the running service):** `alembic upgrade head`,
  then `python -m app.db.seed`.
- **DB-first / Supabase-first:** `schema.sql` + `seed.sql`, then point
  `DATABASE_URL` at it and run the app (skip `alembic upgrade`).

Do not run both against the same database — you would get two overlapping
schema definitions.
