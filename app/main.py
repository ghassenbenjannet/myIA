from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_process import router as process_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Shadow PO AI",
    version="0.1.0",
    description="MVP backend for Shadow PO AI",
)

app.include_router(process_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def workspace() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
