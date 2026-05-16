---
inclusion: always
---

# 프로젝트 공통 규칙

FastAPI + Supabase + HTML/JS/CSS 스택의 모든 작업에 적용되는 공통 규칙입니다.

## 1. 응답 언어

- 사용자와의 대화, 문서, 커밋 메시지, docstring은 **한국어**로 작성합니다.
- 코드 식별자(변수/함수/클래스명)는 영어를 사용합니다.

## 2. 디렉터리 레이아웃

```
<repo-root>/
├── app/                # FastAPI 백엔드
├── frontend/           # 정적 프론트엔드 (HTML/CSS/JS)
├── supabase/
│   ├── migrations/     # SQL 마이그레이션
│   └── seed.sql
├── tests/              # 백엔드 테스트
├── .env.example
├── pyproject.toml
└── README.md
```

## 3. 환경 변수

- 모든 비밀값은 `.env`에 보관하고 Git에 커밋하지 않습니다.
- 새 환경 변수가 추가되면 `.env.example`을 동시에 업데이트합니다.
- 필요한 변수 예시:

```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
APP_ENV=development
CORS_ORIGINS=http://localhost:5173
```

## 4. 보안 기본 원칙

- `service_role` 키는 백엔드에서만 사용하고 프론트엔드/로그/응답에 절대 노출하지 않습니다.
- 모든 Supabase 테이블은 RLS를 활성화합니다.
- 사용자 입력은 서버에서 항상 검증(Pydantic 스키마)하고, DB 쿼리는 파라미터 바인딩만 사용합니다.
- 프론트엔드에서는 `innerHTML` 대신 `textContent`를 기본으로 사용합니다.

## 5. API 계약

- 백엔드는 REST + JSON을 사용하고 경로는 `/api/v1/<resource>`로 시작합니다.
- 오류 응답은 일관된 포맷을 사용합니다:

```json
{ "detail": "사람이 읽을 수 있는 메시지", "code": "optional_error_code" }
```

- 성공 응답에는 적절한 HTTP 상태 코드(200/201/204)를 사용하고 `null` 페이로드 대신 빈 객체/배열을 반환합니다.

## 6. 인증 흐름

1. 프론트엔드는 Supabase Auth로 로그인하여 JWT를 획득합니다.
2. 백엔드 호출 시 `Authorization: Bearer <jwt>` 헤더를 첨부합니다.
3. 백엔드는 JWT를 검증하고 사용자 컨텍스트를 의존성으로 주입합니다.
4. 백엔드는 사용자 JWT를 사용해 Supabase에 접근하여 RLS를 활용합니다(필요할 때만 service role 사용).

## 7. 테스트

- 백엔드: `pytest` + `httpx.AsyncClient`로 라우터 통합 테스트를 작성합니다.
- DB가 필요한 테스트는 Supabase 로컬(또는 별도 테스트 프로젝트)에서 실행합니다.
- 새 기능에는 최소한 happy path 1개와 실패 케이스 1개의 테스트를 추가합니다.

## 8. 의존성 관리

- Python: `pyproject.toml`을 기준으로 하고 `requirements.txt`는 lock 용도로만 사용합니다.
- 새 패키지 추가 시 사용 이유를 PR 설명에 기록합니다.
- 프론트엔드는 가능하면 무의존(vanilla)을 유지하고, 필요할 때만 CDN + SRI로 추가합니다.

## 9. 커밋/PR

- 커밋 메시지는 한국어 + Conventional Commits 형식을 권장합니다: `feat: 사용자 가입 API 추가`
- PR에는 변경 요약, 테스트 방법, 스크린샷(UI 변경 시)을 포함합니다.

## 10. 로깅과 관찰성

- 백엔드는 구조화 로그(JSON)를 표준 출력으로 보냅니다.
- 비밀값/PII는 절대 로그에 남기지 않습니다.
- 외부 API 호출은 요청 ID와 소요 시간을 함께 기록합니다.
