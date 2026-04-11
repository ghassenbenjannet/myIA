from fastapi import FastAPI

from app.api.routes_process import router as process_router

app = FastAPI(
    title="Shadow PO AI",
    version="0.1.0",
    description="MVP backend for Shadow PO AI",
)

app.include_router(process_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
