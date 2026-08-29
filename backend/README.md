# FranchiseGuard AI — Backend

Production-ready **FastAPI** service for franchise standards auditing (PS-18):
stores, inspections, violations, complaints, compliance reports, and a pluggable
AI vision-analysis engine. JWT auth with four roles. PostgreSQL via SQLAlchemy 2
+ Alembic. Fully containerised.

> Standalone service — it does **not** depend on the RocketRide platform. The
> RocketRide app can call it over HTTP (CORS is configured), and a
> "Continue with RocketRide" identity bridge has a stub seam at
> `POST /api/v1/auth/rocketride`.

---

## Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12 (works on 3.11+) |
| Framework | FastAPI + Uvicorn, ORJSON responses |
| ORM / migrations | SQLAlchemy 2.0 (sync) + Alembic |
| Validation | Pydantic v2 / pydantic-settings |
| Database | PostgreSQL (Supabase-compatible; SQLite for tests) |
| Auth | OAuth2 password grant, JWT access + refresh (PyJWT), bcrypt |
| Reports | ReportLab (PDF) |
| Container | Multi-stage Dockerfile, non-root, `docker-compose` for local Postgres |

## Layout

```
backend/
├── app/
│   ├── main.py            # app factory, /health, CORS, exception handlers
│   ├── api/               # deps.py (get_db, current user, require_roles), router.py (aggregate)
│   ├── core/              # config, security (hash + JWT), logging, exceptions
│   ├── db/                # engine/session, declarative base, GUID type, seed.py
│   ├── middleware/        # request-id + timing logging middleware
│   ├── models/            # SQLAlchemy models + enums
│   ├── routers/           # auth, stores, inspections, violations, complaints, reports, ai
│   ├── schemas/           # Pydantic request/response models
│   ├── services/          # business logic (routers stay thin)
│   │   └── ai/            # engine interface + SimulatedVisionEngine + Remote stub + catalog
│   └── utils/             # pagination, refs, datetime
├── alembic/               # migration env + versions/0001_initial_schema.py
├── tests/                 # pytest (SQLite), 28 tests covering the full flow
├── scripts/entrypoint.sh  # optional migrate + seed on container start
├── Dockerfile · docker-compose.yml · Makefile
└── requirements.txt · requirements-dev.txt · .env.example
```

## Quick start (local, no Docker)

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env                                     # then edit DATABASE_URL + SECRET_KEY

alembic upgrade head          # create the schema
python -m app.db.seed         # admin + 15 stores + demo inspections/reports
uvicorn app.main:app --reload # http://localhost:8000/docs
```

No Postgres handy? Point at SQLite for a spin:

```bash
DATABASE_URL="sqlite+pysqlite:///./dev.db" AUTO_CREATE_TABLES=true uvicorn app.main:app --reload
```

## Quick start (Docker)

```bash
cd backend
docker compose up --build     # Postgres + API; migrates + seeds automatically
# API on http://localhost:8000  ·  Swagger on /docs
```

## Configuration

Every setting is an environment variable — see [`.env.example`](.env.example) for
the full annotated list. The load-bearing ones:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL. Supabase pooler: use port `6543` **and** set `DATABASE_USE_NULL_POOL=true`. |
| `SECRET_KEY` | JWT signing key — `python -c "import secrets;print(secrets.token_urlsafe(48))"` |
| `BACKEND_CORS_ORIGINS` | Comma-separated browser origins allowed to call the API |
| `AI_PROVIDER` | `simulated` (default) · `openai` / `anthropic` / `rocketride` (stub) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_MINUTES` | token lifetimes |
| `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` | seeded admin account |

## Auth & roles

OAuth2 password grant. `POST /api/v1/auth/login` (form: `username`=email,
`password`) → `{access_token, refresh_token}`. Send `Authorization: Bearer <access>`.
`POST /api/v1/auth/refresh` swaps a refresh token for a new access token.

| Role | Can |
|---|---|
| `admin` | everything, incl. user management + store delete |
| `area_manager` | manage stores, inspections, violations, complaints, reports |
| `inspector` | create/edit inspections, run AI, add/resolve violations, generate reports |
| `franchise_owner` | read-only, scoped to stores they own; file complaints |

`admin` can only be granted by an existing admin (`PATCH /auth/users/{id}/role`)
or the seed — never at self-registration.

## The AI engine

`app/services/ai/` is a pluggable seam:

- **`engine.py`** — `VisionAnalysisEngine` protocol + `get_engine()` factory (reads `AI_PROVIDER`).
- **`simulated.py`** — default. Deterministic mock (faithful port of the frontend's
  `src/lib/ai.ts`): templated findings over a 10-item catalogue, seeded RNG,
  configurable fake latency.
- **`remote.py`** — `RemoteVisionEngine`: the single place to wire a real model
  (OpenAI/Anthropic vision, or a RocketRide vision pipeline). Implement `analyze()`
  → return an `AnalysisOutcome` with `type_code`s from `catalog.py`; nothing
  downstream changes. Raises `NotImplementedError` (HTTP 501) until then.

`POST /api/v1/ai/analyze` (or `/inspections/{id}/analyze`) runs the engine,
persists an `AIAnalysis` row, and writes detections back as `Violation`s.

## Endpoints (v1, prefix `/api/v1`)

| Group | Highlights |
|---|---|
| `auth` | register, login, login/json, refresh, me, users (admin), rocketride (stub) |
| `stores` | CRUD, filters, `/regions`, `/{id}/inspections`, `/{id}/complaints`, `/{id}/history` |
| `inspections` | CRUD, `/submit`, `/analyze`, `/violations`, `/report` |
| `violations` | list/filter, `PATCH` status transitions (resolve / waive → timestamps + store re-score) |
| `complaints` | intake, `PATCH` triage, `/trends` (weekly buckets) |
| `reports` | list, detail, `POST` generate, `GET /{id}/pdf`, `POST /{id}/share` |
| `ai` | `/engine`, `/analyze`, `/analyses`, `/analyses/{id}` |
| meta | `GET /health` (liveness + DB check), `/docs`, `/redoc`, `/api/v1/openapi.json` |

Errors use a stable envelope: `{"error": {"code": "...", "message": "...", "details": ...}}`.

## End-to-end inspection flow

`POST /inspection/upload` → `POST /inspection/analyze` runs the full pipeline and
persists everything; the dashboard is a live read, so it reflects the result on
the next call.

```
upload image ─▶ Supabase Storage ─▶ YOLO (or simulated) ─▶ violations in Postgres
   ─▶ Gemini complaint triage ─▶ Risk Engine (compliance score) ─▶ compliance report
   ─▶ report saved to DB ─▶ dashboard metrics update
```

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/inspection/upload` | multipart (`store_id`, `images[]`, `complaint_text?`, `checklist?`) → creates an inspection, pushes each image to Supabase Storage (degrades to a warning if unconfigured), returns `inspection_id` + `ws_url` |
| `POST /api/v1/inspection/analyze` | `{inspection_id, complaint_text?, background_report?, save_report_to_supabase?, seed?}` → vision → violations → Gemini → **Risk Engine** → report. Structured JSON: detections, `violations_persisted`, `risk{score,compliance_score,level,breakdown}`, `complaint_analysis`, `report{id,reference,status,pending}`, `warnings[]` |
| `GET /api/v1/dashboard/summary` | live KPIs, risk mix, compliance trend (6 mo), today's inspections, recent alerts |
| `GET /api/v1/stores/{id}/risk-history` | per-inspection `risk_score` / `compliance_score` points over a window + open/resolved counts |
| `GET /api/v1/reports/{id}` | full report (unchanged) |
| `WS /api/v1/ws/inspections/{id}?token=<jwt>` | live progress: `{stage, progress, message, data}` — `connected → detecting → complaint → scoring → report → done` |
| `WS /api/v1/ws/dashboard?token=<jwt>` | a `refresh` ping whenever any analysis completes |

**Risk Engine** (`app/services/risk_service.py`): `severity-weighted violations
(6/16/34) + 4·failed-checklist-area + complaint bump (3/8/16)` → clamped 0–100
risk score; `compliance = 100 − risk`; bands 85/70/50.

**Background report**: `background_report=true` returns a `draft` placeholder
report id immediately and finishes generation in a FastAPI `BackgroundTask`
(Gemini narrative + optional Supabase persist), announcing `report ready` on the
inspection WebSocket.

WebSocket fan-out is in-process (`app/realtime/progress.py`); multi-worker needs
Redis pub/sub behind the same `publish`/`subscribe` surface.

## External integrations (`app/integrations/`)

All secrets come from `.env` — nothing hardcoded. An unconfigured integration
returns HTTP 503 `integration_not_configured`; the API still boots.

| Module | Reads | Provides | Used by |
|---|---|---|---|
| `gemini_client.py` | `GEMINI_API_KEY`, `GEMINI_MODEL` | `analyze_complaint()`, `generate_report()` (REST `generateContent`, JSON out, retries) | `POST /ai/complaints/analyze`, `POST /ai/reports/generate` |
| `supabase_client.py` | `SUPABASE_URL`, `SUPABASE_KEY` | `upload_inspection_image()` (Storage), `save_report()` (PostgREST) | `POST /ai/vision/detect?upload=true`, `POST /ai/reports/generate?save_to_supabase=true` |
| `vision_service.py` | *no API key* — `VISION_BACKEND=yolo`, `YOLO_MODEL_PATH` | `analyze_image()` — local Ultralytics YOLO, mapped to the violation catalogue | `POST /ai/vision/detect` |

`GET /ai/integrations` reports which are configured (no secrets). YOLO needs the
optional extras: `pip install -r requirements-vision.txt` + a model file.

## Raw SQL — `schema.sql` / `seed.sql`

Native-Postgres bootstrap for a Supabase-first setup (6 tables, no `ai_analyses`).
See [DATABASE.md](DATABASE.md). Use **either** this **or** Alembic, not both.

## Migrations

```bash
alembic upgrade head                          # apply
alembic revision --autogenerate -m "add X"    # diff models -> new migration
alembic downgrade -1                          # roll back one
```

`alembic/env.py` reads `DATABASE_URL` from settings and renders the portable
`GUID` column type as `String(36)`.

## Tests

```bash
pytest                # 28 tests, SQLite, no external services
pytest --cov=app
```

Covers: health/OpenAPI, the full auth + RBAC matrix, store CRUD/filters,
the inspection → AI analyze → violations → report → PDF flow, seed determinism,
and error paths.

## Notes / not included

- Sync SQLAlchemy (not async) — simpler, fine for this workload.
- No rate limiting, no email delivery, no object storage for evidence images
  (evidence is metadata only). Row-level scoping is enforced for
  `franchise_owner`; other roles see all rows.
- The RocketRide identity bridge is a documented stub, per design.
