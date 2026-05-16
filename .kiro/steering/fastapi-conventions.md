---
inclusion: fileMatch
fileMatchPattern: "**/app/**/*.py"
---

# FastAPI 백엔드 규칙

FastAPI 기반 백엔드 코드 작성 시 이 규칙을 따릅니다.

## 1. 프로젝트 구조

```
app/
├── api/
│   └── routes/        # 엔드포인트 라우터 (도메인별 분리)
├── models/            # Pydantic 스키마 (Request/Response)
├── services/          # 비즈니스 로직
├── modules/           # 외부 연동, 유틸리티
├── bot/               # 봇/에이전트 관련 모듈
└── main.py            # FastAPI 앱 엔트리포인트
```

라우터는 도메인 단위로 분리하고 `app/api/routes/<domain>.py`에 작성합니다.

## 2. 라우터 작성 규칙

- 라우터는 `APIRouter`로 정의하고 `prefix`와 `tags`를 명시합니다.
- 경로는 kebab-case 대신 명사형 복수(`/users`, `/projects`)를 사용합니다.
- 각 엔드포인트에는 `response_model`과 한글 `summary`를 작성합니다.

```python
from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",
)
async def create_user(payload: UserCreate) -> UserResponse:
    """새로운 사용자를 생성하고 정보를 반환합니다."""
    try:
        return await UserService.create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

## 3. Pydantic 모델 분리

- 입력은 `*Create`, `*Update` / 출력은 `*Response` 접미사를 사용합니다.
- DB 모델과 API 모델은 분리하고, 변환은 서비스 계층에서 수행합니다.
- `model_config = ConfigDict(from_attributes=True)`로 ORM 객체 변환을 허용합니다.

```python
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """사용자 생성 요청 스키마."""
    email: EmailStr
    name: str


class UserResponse(BaseModel):
    """사용자 응답 스키마."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    name: str
```

## 4. 의존성 주입

- 인증, DB 클라이언트, 설정 등은 `Depends`로 주입합니다.
- 공통 의존성은 `app/api/deps.py`에 모읍니다.

```python
from fastapi import Depends
from app.modules.supabase_client import get_supabase

@router.get("/me", response_model=UserResponse)
async def read_me(
    current_user: UserResponse = Depends(get_current_user),
    supabase = Depends(get_supabase),
) -> UserResponse:
    ...
```

## 5. 비동기 우선

- I/O를 수행하는 라우터/서비스는 `async def`로 작성합니다.
- 동기 라이브러리는 `anyio.to_thread.run_sync` 또는 `asyncio.to_thread`로 래핑합니다.

## 6. 에러 처리

- 사용자에게 보여줄 오류는 `HTTPException`으로 변환합니다.
- 도메인 예외는 `app/services` 레벨에서 정의하고 라우터에서 HTTP 코드로 매핑합니다.
- 예기치 못한 오류는 글로벌 `exception_handler`에서 500으로 처리하고 로깅합니다.

```python
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    """모든 예외를 잡아 500으로 응답하고 로그를 남깁니다."""
    logger.exception("처리되지 않은 예외", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "internal error"})
```

## 7. 설정 관리

- 환경 변수는 `pydantic-settings`의 `BaseSettings`로 관리합니다.
- 비밀값은 절대 코드에 하드코딩하지 않고 `.env`에서 읽습니다.
- `.env.example`을 항상 최신 상태로 유지합니다.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """애플리케이션 설정."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
```

## 8. CORS

- 프론트엔드 도메인을 명시적으로 화이트리스트에 등록합니다.
- 개발 중에도 `allow_origins=["*"]`는 피하고 `http://localhost:5173` 등 구체적으로 지정합니다.

## 9. 로깅

- `print` 대신 `logging`을 사용합니다.
- 요청 단위 컨텍스트(`request_id`)를 미들웨어에서 주입해 추적 가능하게 합니다.
