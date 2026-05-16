from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import scheduler
from .db import seed_if_empty
from .routers import calendar, courses, history, notices, search

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_if_empty()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="학점교류 매칭 MVP", lifespan=lifespan)

# CORS 설정 — 프론트엔드에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(search.router)
app.include_router(history.router)
app.include_router(notices.router)
app.include_router(calendar.router)
app.include_router(courses.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """credit-exchange-ui.html을 메인 페이지로 서빙"""
    html_path = ROOT_DIR / "credit-exchange-ui.html"
    return FileResponse(html_path, media_type="text/html")


@app.get("/healthz")
def healthz():
    return {"ok": True}
