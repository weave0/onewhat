#!/usr/bin/env python3
"""Quick test script to verify installation."""

import asyncio
import logging

import numpy as np

from src.orchestration.pipeline import TranslationRequest, create_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_pipeline():
    """Test the translation pipeline."""
    logger.info("🧪 Testing OneWhat Translation Pipeline")
    logger.info("=" * 60)

    # Create test audio (1 second of silence)
    sample_rate = 16000
    audio = np.zeros(sample_rate, dtype=np.float32)

    # Create pipeline
    logger.info("Initializing pipeline...")
    pipeline = create_pipeline()
    logger.info("✅ Pipeline initialized")

    # Create request
    request = TranslationRequest(
        audio=audio.tolist(),
        sample_rate=sample_rate,
        source_lang="en",
        target_lang="es",
    )

    # Test translation
    logger.info("Testing translation...")
    try:
        response = await pipeline.translate(request)
        logger.info("✅ Translation successful")
        logger.info(f"   Latency: {response.latency_ms:.2f}ms")
        logger.info(f"   Stages: {response.stage_latencies}")

    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        raise

    logger.info("=" * 60)
    logger.info("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_pipeline())
