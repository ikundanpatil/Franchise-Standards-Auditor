-- ===========================================================================
-- FranchiseGuard AI — PostgreSQL schema (native / Supabase).
--
-- Hand-authored reference DDL for the six core tables:
--   users · stores · inspections · violations · complaints · reports
--
-- This is a STANDALONE bootstrap for a fresh Supabase / PostgreSQL database.
-- The application itself is normally schema-managed by Alembic
-- (backend/alembic/versions/0001_initial_schema.py); that migration is the
-- source of truth for the running app and also creates an `ai_analyses` table,
-- which is intentionally omitted here. Differences from the ORM migration:
--   * native `uuid` PKs with `gen_random_uuid()` (ORM uses a portable String(36))
--   * native `CREATE TYPE ... AS ENUM` (ORM stores enums as VARCHAR)
--   * `jsonb` instead of `json`
--   * an `updated_at` trigger instead of an ORM-side `onupdate`
-- The SQLAlchemy models read/write happily against either representation.
--
-- Safe to re-run: every statement is guarded (IF NOT EXISTS / DO blocks).
-- Requires PostgreSQL 13+ (Supabase is 15/16). `gen_random_uuid()` is built in.
-- ===========================================================================

begin;

-- --- Enum types ------------------------------------------------------------
do $$ begin
  create type user_role as enum ('admin', 'area_manager', 'inspector', 'franchise_owner');
exception when duplicate_object then null; end $$;

do $$ begin
  create type risk_level as enum ('low', 'medium', 'high', 'critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type severity as enum ('minor', 'major', 'critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type store_status as enum ('active', 'onboarding', 'suspended', 'closed');
exception when duplicate_object then null; end $$;

do $$ begin
  create type inspection_status as enum
    ('scheduled', 'in_progress', 'analyzing', 'completed', 'cancelled');
exception when duplicate_object then null; end $$;

do $$ begin
  create type inspection_method as enum ('ai_photo', 'ai_video', 'on_site');
exception when duplicate_object then null; end $$;

do $$ begin
  create type inspection_source as enum
    ('scheduled', 'ad_hoc', 'complaint_followup', 'reinspection');
exception when duplicate_object then null; end $$;

do $$ begin
  create type violation_status as enum ('open', 'in_remediation', 'resolved', 'waived');
exception when duplicate_object then null; end $$;

do $$ begin
  create type complaint_status as enum
    ('new', 'triaged', 'investigating', 'resolved', 'dismissed');
exception when duplicate_object then null; end $$;

do $$ begin
  create type complaint_channel as enum ('app', 'phone', 'email', 'walk_in', 'social');
exception when duplicate_object then null; end $$;

do $$ begin
  create type report_status as enum ('draft', 'final');
exception when duplicate_object then null; end $$;

-- --- updated_at trigger --------------------------------------------------------
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at := now();
  return new;
end;
$$ language plpgsql;

-- ===========================================================================
-- users
-- ===========================================================================
create table if not exists users (
    id               uuid         primary key default gen_random_uuid(),
    email            varchar(320) not null,
    hashed_password  varchar(255) not null,
    full_name        varchar(160) not null,
    role             user_role    not null default 'inspector',
    is_active        boolean      not null default true,
    phone            varchar(40),
    region           varchar(80),
    last_login_at    timestamptz,
    external_subject varchar(255),               -- reserved: RocketRide identity bridge
    created_at       timestamptz  not null default now(),
    updated_at       timestamptz  not null default now(),
    constraint uq_users_email            unique (email),
    constraint uq_users_external_subject unique (external_subject)
);
create index if not exists ix_users_role   on users (role);
create index if not exists ix_users_region on users (region);
create unique index if not exists uq_users_email_lower on users (lower(email));

drop trigger if exists trg_users_updated_at on users;
create trigger trg_users_updated_at before update on users
    for each row execute function set_updated_at();

-- ===========================================================================
-- stores
-- ===========================================================================
create table if not exists stores (
    id                   uuid         primary key default gen_random_uuid(),
    code                 varchar(24)  not null,
    name                 varchar(160) not null,
    brand                varchar(80)  not null default 'FranchiseGuard',
    region               varchar(80)  not null,
    address              varchar(255) not null,
    city                 varchar(120),
    country              varchar(80),
    latitude             double precision,
    longitude            double precision,
    status               store_status not null default 'active',
    risk_level           risk_level   not null default 'low',
    compliance_score     integer      not null default 100,
    open_violation_count integer      not null default 0,
    opened_on            date,
    last_inspection_at   timestamptz,
    next_inspection_due  date,
    manager_id           uuid         references users (id) on delete set null,
    owner_id             uuid         references users (id) on delete set null,
    tags                 jsonb        not null default '[]'::jsonb,
    created_at           timestamptz  not null default now(),
    updated_at           timestamptz  not null default now(),
    constraint uq_stores_code                unique (code),
    constraint ck_stores_compliance_score    check (compliance_score between 0 and 100)
);
create index if not exists ix_stores_region     on stores (region);
create index if not exists ix_stores_status     on stores (status);
create index if not exists ix_stores_risk_level on stores (risk_level);
create index if not exists ix_stores_manager_id on stores (manager_id);
create index if not exists ix_stores_owner_id   on stores (owner_id);

drop trigger if exists trg_stores_updated_at on stores;
create trigger trg_stores_updated_at before update on stores
    for each row execute function set_updated_at();

-- ===========================================================================
-- inspections
-- ===========================================================================
create table if not exists inspections (
    id               uuid              primary key default gen_random_uuid(),
    store_id         uuid              not null references stores (id) on delete cascade,
    inspector_id     uuid              references users (id) on delete set null,
    status           inspection_status not null default 'scheduled',
    method           inspection_method not null default 'ai_photo',
    source           inspection_source not null default 'scheduled',
    scheduled_for    timestamptz,
    started_at       timestamptz,
    completed_at     timestamptz,
    checklist        jsonb             not null default '[]'::jsonb,
    complaint_text   text,
    image_label      varchar(160),
    frame_count      integer           not null default 1,
    evidence         jsonb             not null default '[]'::jsonb,
    risk_score       integer,
    risk_level       risk_level,
    compliance_score integer,
    summary          text,
    model_version    varchar(48),
    created_at       timestamptz       not null default now(),
    updated_at       timestamptz       not null default now(),
    constraint ck_inspections_risk_score       check (risk_score is null or risk_score between 0 and 100),
    constraint ck_inspections_compliance_score check (compliance_score is null or compliance_score between 0 and 100)
);
create index if not exists ix_inspections_store_id       on inspections (store_id);
create index if not exists ix_inspections_inspector_id   on inspections (inspector_id);
create index if not exists ix_inspections_status         on inspections (status);
create index if not exists ix_inspections_store_created  on inspections (store_id, created_at desc);

drop trigger if exists trg_inspections_updated_at on inspections;
create trigger trg_inspections_updated_at before update on inspections
    for each row execute function set_updated_at();

-- ===========================================================================
-- violations
-- ===========================================================================
create table if not exists violations (
    id              uuid             primary key default gen_random_uuid(),
    inspection_id   uuid             references inspections (id) on delete cascade,
    store_id        uuid             not null references stores (id) on delete cascade,
    type_code       varchar(48)      not null,
    label           varchar(160)     not null,
    category        varchar(80)      not null,
    severity        severity         not null,
    status          violation_status not null default 'open',
    confidence      double precision,
    bounding_box    jsonb,
    standard_ref    varchar(120),
    explanation     text,
    remediation     text,
    detected_at     timestamptz      not null default now(),
    due_at          timestamptz,
    resolved_at     timestamptz,
    resolved_by_id  uuid             references users (id) on delete set null,
    resolution_note text,
    created_at      timestamptz      not null default now(),
    updated_at      timestamptz      not null default now(),
    constraint ck_violations_confidence check (confidence is null or confidence between 0 and 1)
);
create index if not exists ix_violations_inspection_id on violations (inspection_id);
create index if not exists ix_violations_store_id      on violations (store_id);
create index if not exists ix_violations_type_code     on violations (type_code);
create index if not exists ix_violations_category      on violations (category);
create index if not exists ix_violations_severity      on violations (severity);
create index if not exists ix_violations_status        on violations (status);
create index if not exists ix_violations_store_status  on violations (store_id, status);

drop trigger if exists trg_violations_updated_at on violations;
create trigger trg_violations_updated_at before update on violations
    for each row execute function set_updated_at();

-- ===========================================================================
-- complaints
-- ===========================================================================
create table if not exists complaints (
    id                   uuid              primary key default gen_random_uuid(),
    store_id             uuid              not null references stores (id) on delete cascade,
    channel              complaint_channel not null default 'app',
    status               complaint_status  not null default 'new',
    severity             severity,
    reporter_name        varchar(160),
    reporter_contact     varchar(255),
    subject              varchar(200),
    body                 text              not null,
    received_at          timestamptz       not null default now(),
    triaged_by_id        uuid              references users (id) on delete set null,
    triaged_at           timestamptz,
    linked_inspection_id uuid              references inspections (id) on delete set null,
    resolution_note      text,
    resolved_at          timestamptz,
    tags                 jsonb             not null default '[]'::jsonb,
    created_at           timestamptz       not null default now(),
    updated_at           timestamptz       not null default now()
);
create index if not exists ix_complaints_store_id on complaints (store_id);
create index if not exists ix_complaints_status   on complaints (status);
create index if not exists ix_complaints_channel  on complaints (channel);
create index if not exists ix_complaints_received on complaints (received_at desc);

drop trigger if exists trg_complaints_updated_at on complaints;
create trigger trg_complaints_updated_at before update on complaints
    for each row execute function set_updated_at();

-- ===========================================================================
-- reports  (one per inspection)
-- ===========================================================================
create table if not exists reports (
    id               uuid          primary key default gen_random_uuid(),
    inspection_id    uuid          not null references inspections (id) on delete cascade,
    store_id         uuid          not null references stores (id) on delete cascade,
    reference        varchar(32)   not null,
    status           report_status not null default 'draft',
    risk_score       integer       not null,
    risk_level       risk_level    not null,
    grade            varchar(2)    not null,
    minor_count      integer       not null default 0,
    major_count      integer       not null default 0,
    critical_count   integer       not null default 0,
    summary          text          not null,
    recommendations  jsonb         not null default '[]'::jsonb,
    timeline         jsonb         not null default '[]'::jsonb,
    evidence         jsonb         not null default '[]'::jsonb,
    inspector_name   varchar(160),
    model_version    varchar(48),
    generated_by_id  uuid          references users (id) on delete set null,
    generated_at     timestamptz   not null default now(),
    pdf_generated_at timestamptz,
    share_token      varchar(64),
    shared_at        timestamptz,
    created_at       timestamptz   not null default now(),
    updated_at       timestamptz   not null default now(),
    constraint uq_reports_inspection_id unique (inspection_id),
    constraint uq_reports_reference     unique (reference),
    constraint uq_reports_share_token   unique (share_token),
    constraint ck_reports_risk_score    check (risk_score between 0 and 100)
);
create index if not exists ix_reports_store_id on reports (store_id);
create index if not exists ix_reports_status   on reports (status);

drop trigger if exists trg_reports_updated_at on reports;
create trigger trg_reports_updated_at before update on reports
    for each row execute function set_updated_at();

commit;
