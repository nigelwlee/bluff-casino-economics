from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import calculator, chat, scenarios

app = FastAPI(
    title="Bluff Casino Economics API",
    version="0.1.0",
    description="VIP P&L calculator + company projections + AI agent",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator.router)
app.include_router(chat.router)
app.include_router(scenarios.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
