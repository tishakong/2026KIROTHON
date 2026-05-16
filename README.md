# 학점교류 매칭 MVP

신촌 인근 3개 대학(연세대, 서강대, 홍익대)의 강의를 대상으로,
숙명여대 학생이 듣고 싶은 강의명을 입력하면 인정 가능한 타대학 강의를
추천하고, 신청 마감 기간/공지사항을 모아 보여주는 MVP.

## 기술 스택
- Python 3.10+
- FastAPI
- Supabase (Postgres)
- APScheduler (매일 18시 공지 크롤링)
- BeautifulSoup4 + httpx (크롤러)
- 바닐라 JS + FullCalendar(CDN) 프론트

## 디렉토리
```
app/
  main.py              # FastAPI 엔트리, 정적/템플릿, 스케줄러 기동
  config.py            # 환경변수
  db.py                # Supabase 클라이언트
  schemas.py           # Pydantic 모델
  routers/
    search.py          # 강의 검색 → 매칭 → 추천
    notices.py         # 공지/마감일 조회
    history.py         # 검색 기록
  services/
    matcher.py         # 강의 비교·매칭 로직 (LLM 훅 자리)
    course_lookup.py   # 설명 없으면 외부 검색으로 보강
  crawlers/
    base.py
    yonsei.py          # TODO: 사용자가 링크/구조 붙여넣을 자리
    sogang.py          # TODO
    hongik.py          # 홍익대 경영학부 개설과목 (실 API 연동 완료)
    sookmyung_notice.py# 숙명 공지 크롤러 (스켈레톤)
  scheduler.py         # 매일 18시 잡
  templates/index.html # 검색창 + 히스토리 + 캘린더 UI
  static/app.js
supabase_schema.sql    # 테이블 DDL
```

## 실행
```bash
pip install -r requirements.txt
copy .env.example .env   # Windows
# .env 채우기
uvicorn app.main:app --reload
```

브라우저: http://localhost:8000

## Supabase 스키마
`supabase_schema.sql` 을 Supabase SQL editor에서 실행.

## 크롤러 채우는 곳
`app/crawlers/yonsei.py`, `sogang.py` 안의 `TODO` 블록에
- 학과 커리큘럼 페이지 URL
- 신청 기간 페이지 URL
- HTML 셀렉터(과목명/설명/기간 등)
를 붙여넣으면 됩니다. 인터페이스(`fetch_courses`, `fetch_periods`)는 고정.

## MVP 흐름
1. `/api/search?q=강의명` → 3개 대학 캐시된 강의에서 유사 매칭 →
   설명 비어있으면 `course_lookup.search_description` 으로 보강 →
   추천 결과 + 신청 기간 + 필요 서류 반환
2. 검색 시 `search_history` 에 저장
3. 매일 18:00 숙명 공지 페이지 크롤링 → `notices` 테이블 upsert
4. `/calendar` 데이터: 매칭된 대학들의 신청 마감일만 노출
