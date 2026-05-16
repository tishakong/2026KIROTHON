const $ = (sel) => document.querySelector(sel);

const UNIV_NAMES = {
  yonsei: "연세대학교",
  sogang: "서강대학교",
  hongik: "홍익대학교",
  sookmyung: "숙명여자대학교",
};

let calendar;

async function loadHistory() {
  const r = await fetch("/api/history");
  const data = await r.json();
  const ul = $("#history");
  ul.innerHTML = "";
  if (!data.length) {
    ul.innerHTML = '<li class="muted">아직 검색 기록이 없습니다.</li>';
    return;
  }
  for (const h of data) {
    const li = document.createElement("li");
    const date = new Date(h.created_at).toLocaleString("ko-KR");
    li.innerHTML = `<a href="#" data-q="${h.query}">${h.query}</a>
      <div class="muted">${date} · ${h.matched_count}건</div>`;
    li.querySelector("a").addEventListener("click", (e) => {
      e.preventDefault();
      $("#q").value = h.query;
      runSearch(h.query);
    });
    ul.appendChild(li);
  }
}

async function loadNotices() {
  const r = await fetch("/api/notices");
  const data = await r.json();
  const ul = $("#notices");
  ul.innerHTML = "";
  if (!data.length) {
    ul.innerHTML = '<li class="muted">공지사항이 아직 없습니다.</li>';
    return;
  }
  for (const n of data.slice(0, 10)) {
    const li = document.createElement("li");
    li.innerHTML = `
      <a href="${n.url || "#"}" target="_blank" rel="noopener">${n.title}</a>
      ${n.summary ? `<div class="summary">${n.summary}</div>` : ""}
      ${n.constraints ? `<div class="constraints">⚠ ${n.constraints}</div>` : ""}
    `;
    ul.appendChild(li);
  }
}

async function loadCalendar(query) {
  const url = query
    ? `/api/calendar?q=${encodeURIComponent(query)}`
    : `/api/calendar`;
  const events = await fetch(url).then((r) => r.json());

  if (!calendar) {
    calendar = new FullCalendar.Calendar($("#calendar"), {
      initialView: "dayGridMonth",
      height: 480,
      locale: "ko",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,listWeek",
      },
      events,
      eventClick: (info) => {
        const docs = info.event.extendedProps.documents || [];
        alert(
          `${info.event.title}\n` +
            `기간: ${info.event.startStr} ~ ${info.event.endStr || ""}\n` +
            (docs.length ? `필요 서류: ${docs.join(", ")}` : "")
        );
      },
    });
    calendar.render();
  } else {
    calendar.removeAllEvents();
    calendar.addEventSource(events);
  }
}

function renderResults(payload) {
  const box = $("#results");
  box.innerHTML = "";
  if (!payload.matches.length) {
    box.innerHTML = '<p class="muted">매칭되는 강의를 찾지 못했습니다.</p>';
  }
  for (const m of payload.matches) {
    const c = m.course;
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <span class="score">${m.score.toFixed(0)}점</span>
      <div class="title">${c.title}
        <span class="muted">· ${UNIV_NAMES[c.university_id] || c.university_id}</span>
      </div>
      <div class="meta">${c.department || ""} ${c.code ? "· " + c.code : ""}
        ${c.credits ? "· " + c.credits + "학점" : ""}</div>
      <div class="desc">${c.description || ""}</div>
      <div class="meta" style="margin-top:6px;color:#4359ff;">${m.reason}</div>
    `;
    box.appendChild(div);
  }

  const apply = $("#apply-info");
  apply.innerHTML = "";
  if (!payload.apply_info.length) {
    apply.innerHTML = '<p class="muted">매칭 결과가 있어야 신청 정보가 표시됩니다.</p>';
  }
  for (const u of payload.apply_info) {
    const period =
      u.apply_start && u.apply_end
        ? `${u.apply_start} ~ ${u.apply_end}`
        : "기간 미정";
    const div = document.createElement("div");
    div.className = "univ";
    div.innerHTML = `
      <h3>${u.name_ko}</h3>
      <small>신청 기간: ${period}</small><br/>
      ${u.apply_url ? `<small><a href="${u.apply_url}" target="_blank">신청 페이지</a></small>` : ""}
      <ul class="docs">
        ${(u.documents || []).map((d) => `<li>${d}</li>`).join("")}
      </ul>
    `;
    apply.appendChild(div);
  }
}

async function runSearch(q) {
  const r = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  if (!r.ok) {
    alert("검색 실패");
    return;
  }
  const payload = await r.json();
  renderResults(payload);
  loadCalendar(q);
  loadHistory();
}

$("#search-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = $("#q").value.trim();
  if (!q) return;
  runSearch(q);
});

// initial load
loadHistory();
loadNotices();
loadCalendar();
