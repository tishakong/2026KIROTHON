from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import scheduler
from .db import seed_if_empty
from .routers import calendar, courses, history, notices, search

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_if_empty()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="학점교류 매칭 MVP", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(search.router)
app.include_router(history.router)
app.include_router(notices.router)
app.include_router(calendar.router)
app.include_router(courses.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/healthz")
def healthz():
    return {"ok": True}
