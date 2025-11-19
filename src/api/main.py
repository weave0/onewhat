"""FastAPI server for real-time translation API."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..orchestration.pipeline import (
    TranslationPipeline,
    TranslationRequest,
    create_pipeline,
)
from ..utils.config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Global pipeline instance
pipeline: TranslationPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup/shutdown."""
    global pipeline

    logger.info("Starting OneWhat Translation API")

    # Initialize pipeline
    pipeline = create_pipeline()

    logger.info("API ready")

    yield

    # Cleanup
    logger.info("Shutting down")


# Create FastAPI app
app = FastAPI(
    title="OneWhat Translation API",
    description="Real-time speech translation API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")


class LanguageInfo(BaseModel):
    """Language information."""

    code: str = Field(description="Language code")
    name: str = Field(description="Language name")


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """Root endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )


@app.get("/languages")
async def get_languages() -> dict[str, list[str]]:
    """Get supported languages."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    return {
        "supported_languages": [
            "en", "es", "fr", "de", "zh", "ja", "ko",
            "ar", "hi", "pt", "ru", "it",
        ],
        "total": 200,  # NLLB supports 200 languages
    }


@app.post("/translate")
async def translate(request: TranslationRequest) -> dict:
    """
    Translate audio from source to target language.
    
    Args:
        request: Translation request
        
    Returns:
        Translation response with audio and metadata
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        logger.info(
            "Translation request",
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        response = await pipeline.translate(request)

        logger.info(
            "Translation successful",
            latency_ms=response.latency_ms,
        )

        return response.model_dump()

    except Exception as e:
        logger.error("Translation failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}",
        )


@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for streaming translation.
    
    Client sends audio chunks, receives translated audio in real-time.
    """
    await websocket.accept()

    if pipeline is None:
        await websocket.close(code=1011, reason="Pipeline not initialized")
        return

    logger.info("WebSocket connection established")

    try:
        # Receive initial config
        config = await websocket.receive_json()
        source_lang = config.get("source_lang", "en")
        target_lang = config.get("target_lang", "es")
        sample_rate = config.get("sample_rate", 16000)

        logger.info(
            "WebSocket config",
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # Create async generator from WebSocket
        async def audio_generator() -> AsyncGenerator[bytes, None]:
            while True:
                try:
                    data = await websocket.receive_bytes()
                    yield data
                except WebSocketDisconnect:
                    break

        # Stream translations
        async for response in pipeline.translate_streaming(
            audio_generator(),
            source_lang=source_lang,
            target_lang=target_lang,
            sample_rate=sample_rate,
        ):
            await websocket.send_json(response.model_dump())

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error", error=str(e), exc_info=True)
        await websocket.close(code=1011, reason=str(e))


@app.get("/metrics")
async def metrics() -> JSONResponse:
    """
    Prometheus metrics endpoint.
    
    Returns:
        Metrics in Prometheus format
    """
    # TODO: Implement Prometheus metrics
    return JSONResponse(
        content={
            "message": "Metrics endpoint - Prometheus integration pending"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
