---
inclusion: fileMatch
fileMatchPattern: "**/{supabase,db,migrations}/**/*"
---

# Supabase 사용 규칙

Supabase를 데이터/인증 백엔드로 사용할 때 이 규칙을 따릅니다.

## 1. 키 분리

- `SUPABASE_ANON_KEY`: 프론트엔드 전용. 브라우저 노출 가능.
- `SUPABASE_SERVICE_ROLE_KEY`: 서버 전용. **절대 프론트엔드에 노출 금지**, Git 커밋 금지.
- 서버에서 RLS 우회가 필요한 작업만 service role을 사용하고, 일반 요청은 사용자 JWT로 처리합니다.

## 2. 클라이언트 초기화

- 백엔드: `supabase-py` 클라이언트를 싱글톤으로 관리하고 의존성 주입으로 전달합니다.
- 프론트엔드: `@supabase/supabase-js` 클라이언트는 모듈 단일 인스턴스로 export합니다.

```python
# app/modules/supabase_client.py
from functools import lru_cache
from supabase import Client, create_client
from app.core.config import settings

@lru_cache
def get_supabase() -> Client:
    """서버 측 Supabase 클라이언트를 반환합니다."""
    return create_client(settings.supabase_url, settings.supabase_service_key)
```

## 3. Row Level Security (RLS)

- 모든 테이블에 RLS를 **반드시 활성화**합니다.
- 정책은 `auth.uid()`를 기준으로 작성하며, 익명 접근이 필요한 경우만 명시적으로 허용합니다.
- 정책 변경은 마이그레이션 파일(`supabase/migrations/*.sql`)로 관리합니다.

```sql
-- 본인 데이터만 조회 가능
create policy "users can read own profile"
on public.profiles
for select
using (auth.uid() = id);
```

## 4. 스키마 규칙

- 테이블명: 복수형 snake_case (`users`, `credit_transactions`)
- 컬럼명: snake_case
- 기본키: `id uuid primary key default gen_random_uuid()`
- 타임스탬프: `created_at timestamptz default now()`, `updated_at timestamptz`
- 외래키는 명시적으로 `on delete` 동작(보통 `cascade` 또는 `restrict`)을 지정합니다.

## 5. 마이그레이션

- 스키마 변경은 항상 SQL 마이그레이션 파일로 작성합니다.
- 파일명은 `YYYYMMDDHHMMSS_description.sql` 포맷을 사용합니다.
- 로컬에서 `supabase db reset`으로 검증 후 커밋합니다.

## 6. 인증

- 프론트엔드에서 로그인 후 받은 JWT를 `Authorization: Bearer <token>` 헤더로 백엔드에 전달합니다.
- 백엔드는 토큰을 검증하고 `auth.uid()`에 해당하는 사용자 정보를 의존성으로 주입합니다.
- 비밀번호 재설정, 이메일 인증은 Supabase Auth의 내장 기능을 우선 사용합니다.

## 7. 쿼리 작성

- 가능하면 SQL 뷰/RPC 함수로 비즈니스 로직을 캡슐화합니다.
- N+1을 피하기 위해 `select("*, related_table(*)")` 형태의 조인 쿼리를 사용합니다.
- 페이지네이션은 `range(start, end)` 또는 keyset 기반으로 일관되게 적용합니다.

## 8. Storage

- 버킷명은 kebab-case (`user-uploads`).
- public 버킷은 정적 자산에만 사용하고, 사용자 데이터는 private + signed URL을 사용합니다.

## 9. Realtime

- 구독은 컴포넌트 unmount 시점에 반드시 `unsubscribe`합니다.
- 민감한 테이블은 RLS와 별개로 publication 설정으로 노출 범위를 제한합니다.

## 10. 비밀 관리

- `.env`에만 키를 보관하고 `.env.example`에는 빈 값으로 키 이름만 노출합니다.
- 어떠한 경우에도 `service_role` 키를 응답 본문, 로그, 클라이언트 번들에 포함하지 않습니다.
