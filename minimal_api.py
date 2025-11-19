"""Minimal FastAPI server for testing - NO AI models, just endpoints."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="OneWhat API - Minimal Test")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


@app.get("/")
async def root():
    return {"message": "OneWhat Translation API - Minimal Mode", "status": "running"}


@app.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="1.0.0-minimal",
        message="Server is running - AI models disabled for testing"
    )


@app.get("/test")
async def test():
    return {
        "test": "passed",
        "server": "uvicorn",
        "framework": "fastapi",
        "models_loaded": False,
        "message": "Minimal API is working - ready for full deployment"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
