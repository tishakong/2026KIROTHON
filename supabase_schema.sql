-- 대학 마스터
create table if not exists universities (
  id            text primary key,           -- 'yonsei' | 'sogang' | 'ewha' | 'sookmyung'
  name_ko       text not null,
  apply_url     text,
  notice_url    text,
  documents     jsonb default '[]'::jsonb,  -- 신청 서류 목록
  apply_start   date,
  apply_end     date,
  updated_at    timestamptz default now()
);

-- 타대학 강의 캐시
create table if not exists courses (
  id            bigserial primary key,
  university_id text references universities(id),
  department    text,
  code          text,
  title         text not null,
  description   text,
  credits       numeric,
  source_url    text,
  raw           jsonb,
  updated_at    timestamptz default now()
);
create index if not exists courses_title_idx on courses using gin (to_tsvector('simple', title));
create index if not exists courses_univ_idx on courses(university_id);

-- 검색 기록
create table if not exists search_history (
  id           bigserial primary key,
  query        text not null,
  matched_count int default 0,
  created_at   timestamptz default now()
);

-- 공지사항
create table if not exists notices (
  id           bigserial primary key,
  source       text not null,         -- 'sookmyung'
  external_id  text,                  -- 사이트 게시글 id (있으면)
  title        text not null,
  url          text,
  posted_at    date,
  summary      text,
  constraints  text,
  raw          jsonb,
  created_at   timestamptz default now(),
  unique (source, external_id)
);

-- 매칭 결과 캐시(선택)
create table if not exists match_cache (
  id           bigserial primary key,
  query        text not null,
  payload      jsonb not null,
  created_at   timestamptz default now()
);
