from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401 — 注册所有模型到 SQLModel.metadata

from app.database import init_db
from app.seed import seed
from app.routers import dashboard, accounts, snapshots, companies, salaries, data_io, expenses


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(title="家庭资产看板", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router)
app.include_router(accounts.router)
app.include_router(snapshots.router)
app.include_router(companies.router)
app.include_router(salaries.router)
app.include_router(data_io.router)
app.include_router(expenses.router)
