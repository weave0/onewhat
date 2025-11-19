#!/usr/bin/env python3
"""Download and cache all required models."""

import logging

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from TTS.api import TTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_nmt_model():
    """Download NLLB translation model."""
    logger.info("Downloading NLLB-200 model...")
    model_name = "facebook/nllb-200-distilled-600M"

    logger.info("Downloading tokenizer...")
    AutoTokenizer.from_pretrained(model_name)

    logger.info("Downloading model...")
    AutoModelForSeq2SeqLM.from_pretrained(model_name)

    logger.info("✅ NLLB model downloaded")


def download_tts_model():
    """Download XTTS model."""
    logger.info("Downloading XTTS v2 model...")
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

    TTS(model_name=model_name)

    logger.info("✅ XTTS model downloaded")


def main():
    """Download all models."""
    logger.info("🚀 Downloading models for OneWhat Translation System")
    logger.info("=" * 60)

    try:
        # NMT model
        download_nmt_model()

        # TTS model
        download_tts_model()

        logger.info("=" * 60)
        logger.info("✅ All models downloaded successfully!")

    except Exception as e:
        logger.error(f"❌ Error downloading models: {e}")
        raise


if __name__ == "__main__":
    main()
