-- NOEMA Supabase/Postgres schema proposal v1.0
-- STATUS: DESIGN DRAFT ONLY. NOT EXECUTED.
-- Apply only to a dedicated NOEMA Supabase project after review.
-- Keep service_role/secret credentials server-side only.

begin;

create schema if not exists noema_private;
revoke all on schema noema_private from public, anon, authenticated;

create table if not exists public.research_entries (
  id text primary key
    check (id ~ '^NOEMA-[0-9]{4}-[0-9]{3}$'),
  slug text not null unique
    check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  title text not null check (length(btrim(title)) >= 3),
  category text not null check (length(btrim(category)) >= 2),
  summary text not null check (length(btrim(summary)) >= 20),
  content_markdown text not null default '',
  status text not null default 'draft'
    check (status in ('draft', 'review', 'preliminary', 'published', 'retracted')),
  version integer not null default 1 check (version > 0),
  created_by uuid not null references auth.users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  published_at timestamptz,
  retraction_note text,
  check (status <> 'published' or published_at is not null),
  check (status <> 'retracted' or length(btrim(coalesce(retraction_note, ''))) > 0)
);

create index if not exists research_entries_public_listing_idx
  on public.research_entries (status, published_at desc, created_at desc);
create index if not exists research_entries_author_idx
  on public.research_entries (created_by, updated_at desc);

create table if not exists public.research_sources (
  id uuid primary key default gen_random_uuid(),
  research_id text not null references public.research_entries(id) on delete cascade,
  ordinal integer not null check (ordinal > 0),
  title text not null check (length(btrim(title)) >= 3),
  authors text[] not null default '{}',
  citation text not null check (length(btrim(citation)) >= 10),
  url text not null check (url ~ '^https?://'),
  source_type text not null check (length(btrim(source_type)) >= 2),
  publication_date text
    check (publication_date is null or publication_date ~ '^[0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?$'),
  accessed_at date not null,
  version_label text,
  notes text,
  created_at timestamptz not null default now(),
  unique (research_id, ordinal)
);

create index if not exists research_sources_research_idx
  on public.research_sources (research_id, ordinal);

create table if not exists public.research_artifacts (
  id uuid primary key default gen_random_uuid(),
  research_id text not null references public.research_entries(id) on delete cascade,
  artifact_kind text not null check (artifact_kind in ('dataset', 'code', 'result', 'figure', 'protocol', 'other')),
  title text not null check (length(btrim(title)) >= 2),
  source_url text check (source_url is null or source_url ~ '^https?://'),
  storage_path text,
  sha256 text check (sha256 is null or sha256 ~ '^[a-f0-9]{64}$'),
  license text,
  is_public boolean not null default false,
  created_at timestamptz not null default now(),
  check (source_url is not null or storage_path is not null)
);

create index if not exists research_artifacts_research_idx
  on public.research_artifacts (research_id, artifact_kind);

create table if not exists public.research_reviews (
  id uuid primary key default gen_random_uuid(),
  research_id text not null references public.research_entries(id) on delete cascade,
  reviewed_version integer not null check (reviewed_version > 0),
  reviewer_id uuid not null references auth.users(id) on delete restrict,
  decision text not null check (decision in ('approve', 'changes_requested', 'reject')),
  review_summary text not null check (length(btrim(review_summary)) >= 10),
  reviewed_at timestamptz not null default now(),
  unique (research_id, reviewed_version, reviewer_id)
);

create index if not exists research_reviews_research_version_idx
  on public.research_reviews (research_id, reviewed_version, decision);

create table if not exists public.research_comments (
  id uuid primary key default gen_random_uuid(),
  research_id text not null references public.research_entries(id) on delete cascade,
  parent_comment_id uuid references public.research_comments(id) on delete cascade,
  author_id uuid not null references auth.users(id) on delete restrict,
  body text not null check (length(btrim(body)) between 2 and 10000),
  moderation_state text not null default 'visible'
    check (moderation_state in ('visible', 'hidden')),
  created_at timestamptz not null default now()
);

create index if not exists research_comments_thread_idx
  on public.research_comments (research_id, created_at);

-- Private operational telemetry. Never expose this schema through the Data API.
create table if not exists noema_private.automation_runs (
  id uuid primary key default gen_random_uuid(),
  run_key text not null unique,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null default 'running'
    check (status in ('running', 'succeeded', 'failed', 'no_update')),
  research_id text references public.research_entries(id) on delete set null,
  git_commit_sha text,
  ci_run_url text,
  pages_run_url text,
  result_summary jsonb not null default '{}'::jsonb
);

-- RLS must cover every exposed table. Private telemetry is separately restricted.
alter table public.research_entries enable row level security;
alter table public.research_sources enable row level security;
alter table public.research_artifacts enable row level security;
alter table public.research_reviews enable row level security;
alter table public.research_comments enable row level security;
alter table noema_private.automation_runs enable row level security;

-- Explicit grants are intentional: Data API table exposure and RLS are separate controls.
grant usage on schema public to anon, authenticated;
grant select on public.research_entries, public.research_sources,
  public.research_artifacts, public.research_comments to anon, authenticated;
grant select on public.research_reviews to authenticated;
grant insert, update, delete on public.research_entries,
  public.research_sources, public.research_artifacts to authenticated;
grant insert on public.research_reviews, public.research_comments to authenticated;
grant all on public.research_entries, public.research_sources,
  public.research_artifacts, public.research_reviews,
  public.research_comments to service_role;

grant usage on schema noema_private to service_role;
grant all on noema_private.automation_runs to service_role;
revoke all on noema_private.automation_runs from public, anon, authenticated;

-- Trusted roles must be provisioned in app_metadata by an administrator.
-- Do not use user_metadata for authorization.
-- Editor helper expression:
-- coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
--   in ('editor', 'admin'), false)

drop policy if exists "public can read public research" on public.research_entries;
create policy "public can read public research"
  on public.research_entries for select to anon, authenticated
  using (
    status in ('preliminary', 'published', 'retracted')
    or created_by = (select auth.uid())
    or coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
      in ('editor', 'admin'), false)
  );

drop policy if exists "signed in users create own drafts" on public.research_entries;
create policy "signed in users create own drafts"
  on public.research_entries for insert to authenticated
  with check (created_by = (select auth.uid()) and status = 'draft');

drop policy if exists "authors edit own drafts" on public.research_entries;
create policy "authors edit own drafts"
  on public.research_entries for update to authenticated
  using (created_by = (select auth.uid()) and status = 'draft')
  with check (created_by = (select auth.uid()) and status = 'draft');

drop policy if exists "editors update research" on public.research_entries;
create policy "editors update research"
  on public.research_entries for update to authenticated
  using (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false))
  with check (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false));

drop policy if exists "editors insert research" on public.research_entries;
create policy "editors insert research"
  on public.research_entries for insert to authenticated
  with check (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false));

drop policy if exists "admins delete research" on public.research_entries;
create policy "admins delete research"
  on public.research_entries for delete to authenticated
  using (((select auth.jwt())->'app_metadata'->>'noema_role') = 'admin');

drop policy if exists "read sources for visible research" on public.research_sources;
create policy "read sources for visible research"
  on public.research_sources for select to anon, authenticated
  using (
    exists (
      select 1 from public.research_entries e
      where e.id = research_id
        and (
          e.status in ('preliminary', 'published', 'retracted')
          or e.created_by = (select auth.uid())
          or coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
            in ('editor', 'admin'), false)
        )
    )
  );

drop policy if exists "authors add sources to own drafts" on public.research_sources;
create policy "authors add sources to own drafts"
  on public.research_sources for insert to authenticated
  with check (
    exists (
      select 1 from public.research_entries e
      where e.id = research_id and e.created_by = (select auth.uid())
        and e.status = 'draft'
    )
  );

drop policy if exists "authors update own draft sources" on public.research_sources;
create policy "authors update own draft sources"
  on public.research_sources for update to authenticated
  using (exists (
    select 1 from public.research_entries e
    where e.id = research_id and e.created_by = (select auth.uid())
      and e.status = 'draft'
  ))
  with check (exists (
    select 1 from public.research_entries e
    where e.id = research_id and e.created_by = (select auth.uid())
      and e.status = 'draft'
  ));

drop policy if exists "authors delete own draft sources" on public.research_sources;
create policy "authors delete own draft sources"
  on public.research_sources for delete to authenticated
  using (exists (
    select 1 from public.research_entries e
    where e.id = research_id and e.created_by = (select auth.uid())
      and e.status = 'draft'
  ));

drop policy if exists "editors manage sources" on public.research_sources;
create policy "editors manage sources"
  on public.research_sources for all to authenticated
  using (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false))
  with check (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false));

drop policy if exists "read public artifacts" on public.research_artifacts;
create policy "read public artifacts"
  on public.research_artifacts for select to anon, authenticated
  using (
    is_public and exists (
      select 1 from public.research_entries e
      where e.id = research_id
        and e.status in ('preliminary', 'published', 'retracted')
    )
    or exists (
      select 1 from public.research_entries e
      where e.id = research_id and e.created_by = (select auth.uid())
    )
    or coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
      in ('editor', 'admin'), false)
  );

drop policy if exists "authors add artifacts to own drafts" on public.research_artifacts;
create policy "authors add artifacts to own drafts"
  on public.research_artifacts for insert to authenticated
  with check (
    exists (
      select 1 from public.research_entries e
      where e.id = research_id and e.created_by = (select auth.uid())
        and e.status = 'draft'
    )
  );

drop policy if exists "authors update own draft artifacts" on public.research_artifacts;
create policy "authors update own draft artifacts"
  on public.research_artifacts for update to authenticated
  using (exists (
    select 1 from public.research_entries e
    where e.id = research_id and e.created_by = (select auth.uid())
      and e.status = 'draft'
  ))
  with check (exists (
    select 1 from public.research_entries e
    where e.id = research_id and e.created_by = (select auth.uid())
      and e.status = 'draft'
  ));

drop policy if exists "authors delete own draft artifacts" on public.research_artifacts;
create policy "authors delete own draft artifacts"
  on public.research_artifacts for delete to authenticated
  using (exists (
    select 1 from public.research_entries e
    where e.id = research_id and e.created_by = (select auth.uid())
      and e.status = 'draft'
  ));

drop policy if exists "editors manage artifacts" on public.research_artifacts;
create policy "editors manage artifacts"
  on public.research_artifacts for all to authenticated
  using (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false))
  with check (coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
    in ('editor', 'admin'), false));

drop policy if exists "participants read reviews" on public.research_reviews;
create policy "participants read reviews"
  on public.research_reviews for select to authenticated
  using (
    reviewer_id = (select auth.uid())
    or exists (
      select 1 from public.research_entries e
      where e.id = research_id and e.created_by = (select auth.uid())
    )
    or coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
      in ('editor', 'admin'), false)
  );

drop policy if exists "eligible reviewers submit independent review" on public.research_reviews;
create policy "eligible reviewers submit independent review"
  on public.research_reviews for insert to authenticated
  with check (
    reviewer_id = (select auth.uid())
    and coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
      in ('reviewer', 'editor', 'admin'), false)
    and exists (
      select 1 from public.research_entries e
      where e.id = research_id and e.status = 'review'
        and e.created_by <> (select auth.uid())
        and e.version = reviewed_version
    )
  );

drop policy if exists "read visible discussion" on public.research_comments;
create policy "read visible discussion"
  on public.research_comments for select to anon, authenticated
  using (
    (moderation_state = 'visible' and exists (
      select 1 from public.research_entries e
      where e.id = research_id
        and e.status in ('preliminary', 'published', 'retracted')
    ))
    or author_id = (select auth.uid())
    or coalesce(((select auth.jwt())->'app_metadata'->>'noema_role')
      in ('editor', 'admin'), false)
  );

drop policy if exists "signed in users comment on public research" on public.research_comments;
create policy "signed in users comment on public research"
  on public.research_comments for insert to authenticated
  with check (
    author_id = (select auth.uid())
    and exists (
      select 1 from public.research_entries e
      where e.id = research_id
        and e.status in ('preliminary', 'published', 'retracted')
    )
  );

-- Prevent a research entry from becoming published without an approved review
-- of the exact same version by a reviewer who is not its author.
create or replace function noema_private.require_approved_review_before_publish()
returns trigger
language plpgsql
security definer
set search_path = ''
as $function$
begin
  if new.status = 'published' then
    if tg_op = 'INSERT' then
      if not exists (
        select 1
        from public.research_reviews r
        where r.research_id = new.id
          and r.reviewed_version = new.version
          and r.decision = 'approve'
          and r.reviewer_id <> new.created_by
      ) then
        raise exception 'Publishing requires an approved review for the exact current version by a non-author reviewer';
      end if;
    elsif old.status <> 'published' or new.version <> old.version then
      if not exists (
        select 1
        from public.research_reviews r
        where r.research_id = new.id
          and r.reviewed_version = new.version
          and r.decision = 'approve'
          and r.reviewer_id <> new.created_by
      ) then
        raise exception 'Publishing requires an approved review for the exact current version by a non-author reviewer';
      end if;
    end if;
  end if;
  return new;
end;
$function$;

revoke all on function noema_private.require_approved_review_before_publish()
  from public, anon, authenticated;

drop trigger if exists require_approved_review_before_publish
  on public.research_entries;
create trigger require_approved_review_before_publish
  before insert or update of status, version on public.research_entries
  for each row execute function noema_private.require_approved_review_before_publish();

-- No client role may read operational automation runs.
revoke all on noema_private.automation_runs from public, anon, authenticated;

commit;
