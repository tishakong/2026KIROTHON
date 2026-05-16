---
inclusion: fileMatch
fileMatchPattern: "**/*.{html,css,js}"
---

# 프론트엔드(HTML/CSS/JS) 규칙

순수 HTML/CSS/JavaScript로 프론트엔드를 작성할 때 이 규칙을 따릅니다.

## 1. 파일 구조

```
frontend/
├── index.html
├── css/
│   ├── reset.css
│   └── main.css
├── js/
│   ├── api.js          # 백엔드/Supabase 호출
│   ├── auth.js         # 인증 헬퍼
│   ├── components/     # 재사용 UI 조각
│   └── pages/          # 페이지별 진입 모듈
└── assets/
```

- JS 모듈은 ES Modules(`<script type="module">`)로 로드합니다.
- 페이지별 진입점은 `js/pages/<page>.js`에 두고 `DOMContentLoaded`에서 초기화합니다.

## 2. HTML

- 시맨틱 태그(`<header>`, `<main>`, `<nav>`, `<section>`, `<article>`)를 우선 사용합니다.
- 폼 요소는 `<label for="...">`로 라벨을 명시하고, 입력에는 `name`, `autocomplete`, `required`를 적절히 지정합니다.
- 이미지/아이콘에는 의미 있는 `alt` 텍스트를 작성합니다(장식용은 `alt=""`).
- `lang="ko"`를 `<html>`에 지정합니다.

## 3. CSS

- BEM 네이밍 (`block__element--modifier`) 또는 단일 책임 유틸리티 클래스 중 하나를 일관되게 사용합니다.
- 색상, 간격, 폰트 등은 CSS 변수(`:root { --color-primary: ... }`)로 관리합니다.
- `px` 대신 본문 텍스트는 `rem`, 간격은 `rem`/`em`, 미디어 쿼리는 `em`을 권장합니다.
- 모바일 우선(min-width 미디어 쿼리)으로 작성합니다.

```css
:root {
  --color-primary: #4f46e5;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --radius-md: 0.5rem;
}

.button {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: white;
}
```

## 4. JavaScript

- 변수는 `const` 우선, 재할당이 필요할 때만 `let`. `var`는 사용 금지.
- 함수/변수명은 camelCase, 클래스/컴포넌트명은 PascalCase, 상수는 UPPER_SNAKE_CASE.
- 비동기 작업은 `async/await`을 사용하고 `try/catch`로 오류를 처리합니다.
- DOM 조회 결과는 캐싱하여 반복 조회를 피합니다.

```js
// js/api.js
const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API ${response.status}: ${detail}`);
  }
  return response.json();
}
```

## 5. API 호출

- 모든 fetch 호출은 `js/api.js`의 헬퍼를 통과하도록 합니다.
- Supabase JWT가 있다면 `Authorization: Bearer <token>`을 자동으로 부착합니다.
- 환경별 base URL은 빌드 시점의 환경 변수 또는 `window.__APP_CONFIG__`로 주입합니다.

## 6. 상태 관리

- 작은 앱은 모듈 레벨 변수 + 이벤트로 충분합니다.
- 페이지 간 공유 상태는 `localStorage`(비민감) 또는 `sessionStorage`에 저장합니다.
- JWT는 메모리에 보관하고, 새로고침 복원이 필요하면 `localStorage`에 두되 XSS 노출 위험을 감안합니다.

## 7. 접근성 (a11y)

- 모든 인터랙티브 요소는 키보드로 조작 가능해야 합니다.
- 포커스 스타일(`:focus-visible`)을 절대 제거하지 않습니다.
- 색상 대비는 WCAG AA(4.5:1) 이상을 목표로 합니다.
- ARIA 속성은 시맨틱 HTML로 표현 불가할 때만 사용합니다.

## 8. 보안

- 사용자 입력은 `textContent`로 삽입하고 `innerHTML`은 신뢰된 콘텐츠에만 사용합니다.
- 외부 라이브러리는 SRI(integrity) 해시를 포함해 로드합니다.
- 민감 키(`service_role` 등)는 절대 프론트엔드에 포함하지 않습니다.

## 9. 빌드/배포

- 정적 파일은 그대로 서빙 가능하므로 별도 번들러 없이 시작하되, 규모가 커지면 Vite 도입을 검토합니다.
- 캐시 무효화를 위해 배포 시 파일명에 해시를 포함하거나 `?v=` 쿼리를 활용합니다.
