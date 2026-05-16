---
inclusion: fileMatch
fileMatchPattern: "*.py"
---


# Python 코딩 규칙

이 프로젝트의 모든 Python 코드는 아래 규칙을 따릅니다.

## 1. 한글 Docstring

모든 함수와 클래스에 한글로 docstring을 작성합니다.

```python
def calculate_total(prices: list[float]) -> float:
    """
    가격 목록의 합계를 계산합니다.

    Args:
        prices: 가격 목록 (float 리스트)

    Returns:
        모든 가격의 합계 (float)
    """
    return sum(prices)
```

## 2. 변수명은 snake_case 사용

모든 변수명, 함수명, 모듈명은 snake_case를 사용합니다.
클래스명은 PascalCase를 사용합니다.

```python
# 올바른 예
user_name = "홍길동"
total_price = 10000
max_retry_count = 3

# 잘못된 예
userName = "홍길동"       # camelCase 금지
TotalPrice = 10000       # PascalCase는 클래스명에만 사용
```

## 3. 타입 힌트 필수

모든 함수의 매개변수와 반환값에 타입 힌트를 명시합니다.

```python
def get_user(user_id: int) -> dict[str, str]:
    """사용자 ID로 사용자 정보를 조회합니다."""
    ...

def send_message(recipient: str, message: str) -> bool:
    """메시지를 전송하고 성공 여부를 반환합니다."""
    ...

# None을 반환하는 경우
def log_event(event_name: str) -> None:
    """이벤트를 로그에 기록합니다."""
    ...
```

## 4. 에러 처리는 try-except 사용

예외가 발생할 수 있는 모든 코드는 try-except로 처리합니다.
광범위한 `except Exception`보다 구체적인 예외 타입을 명시합니다.

```python
def read_file(file_path: str) -> str:
    """
    파일 내용을 읽어 반환합니다.

    Args:
        file_path: 읽을 파일의 경로

    Returns:
        파일 내용 문자열

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        PermissionError: 파일 읽기 권한이 없을 때
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        raise
    except PermissionError:
        print(f"파일 읽기 권한이 없습니다: {file_path}")
        raise
```
