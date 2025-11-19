"""End-to-end translation pipeline orchestration."""

import asyncio
import time
from enum import Enum
from typing import AsyncGenerator

import numpy as np
from pydantic import BaseModel, Field

from ..asr.whisper_engine import WhisperEngine, create_asr_engine
from ..nmt.nllb_engine import NLLBEngine, create_nmt_engine
from ..tts.xtts_engine import XTTSEngine, create_tts_engine
from ..utils.logging import get_logger

logger = get_logger(__name__)


class PipelineStage(str, Enum):
    """Pipeline processing stages."""

    ASR = "asr"
    NMT = "nmt"
    TTS = "tts"


class TranslationRequest(BaseModel):
    """Request for translation pipeline."""

    audio: list[float] = Field(description="Input audio waveform")
    sample_rate: int = Field(default=16000, description="Sample rate (Hz)")
    source_lang: str = Field(description="Source language code")
    target_lang: str = Field(description="Target language code")
    speaker_wav: str | None = Field(
        default=None,
        description="Reference audio for voice cloning",
    )


class TranslationResponse(BaseModel):
    """Response from translation pipeline."""

    audio: list[float] = Field(description="Translated audio waveform")
    sample_rate: int = Field(description="Output sample rate (Hz)")
    transcription: str = Field(description="Source language transcription")
    translation: str = Field(description="Target language translation")
    source_lang: str = Field(description="Source language")
    target_lang: str = Field(description="Target language")
    latency_ms: float = Field(description="Total latency (ms)")
    stage_latencies: dict[str, float] = Field(
        description="Per-stage latencies (ms)"
    )
    confidences: dict[str, float] = Field(
        description="Confidence scores per stage"
    )


class TranslationPipeline:
    """
    End-to-end real-time translation pipeline.
    
    Orchestrates ASR → NMT → TTS for seamless translation.
    """

    def __init__(
        self,
        asr_engine: WhisperEngine | None = None,
        nmt_engine: NLLBEngine | None = None,
        tts_engine: XTTSEngine | None = None,
    ):
        """
        Initialize translation pipeline.
        
        Args:
            asr_engine: Speech recognition engine
            nmt_engine: Translation engine
            tts_engine: Speech synthesis engine
        """
        logger.info("Initializing translation pipeline")

        # Initialize engines
        self.asr_engine = asr_engine or create_asr_engine()
        self.nmt_engine = nmt_engine or create_nmt_engine()
        self.tts_engine = tts_engine or create_tts_engine()

        logger.info("Translation pipeline ready")

    async def translate(
        self,
        request: TranslationRequest,
    ) -> TranslationResponse:
        """
        Translate audio from source to target language.
        
        Args:
            request: Translation request with audio and parameters
            
        Returns:
            TranslationResponse with translated audio and metadata
        """
        start_time = time.time()
        stage_latencies = {}
        confidences = {}

        # Convert audio to numpy array
        audio_array = np.array(request.audio, dtype=np.float32)

        logger.info(
            "Starting translation",
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            audio_duration=len(audio_array) / request.sample_rate,
        )

        # Stage 1: ASR (Speech to Text)
        asr_start = time.time()
        asr_result = await self.asr_engine.transcribe_async(
            audio_array,
            language=request.source_lang,
        )
        stage_latencies["asr"] = (time.time() - asr_start) * 1000
        confidences["asr"] = asr_result.confidence

        logger.info(
            "ASR complete",
            text=asr_result.text,
            latency_ms=stage_latencies["asr"],
        )

        # Stage 2: NMT (Text Translation)
        nmt_start = time.time()
        
        # Convert language codes to NLLB format if needed
        nllb_source = self._to_nllb_code(request.source_lang)
        nllb_target = self._to_nllb_code(request.target_lang)
        
        nmt_result = await self.nmt_engine.translate_async(
            asr_result.text,
            source_lang=nllb_source,
            target_lang=nllb_target,
        )
        stage_latencies["nmt"] = (time.time() - nmt_start) * 1000
        confidences["nmt"] = nmt_result.confidence

        logger.info(
            "NMT complete",
            translation=nmt_result.text,
            latency_ms=stage_latencies["nmt"],
        )

        # Stage 3: TTS (Text to Speech)
        tts_start = time.time()
        
        # Convert NLLB code to TTS language
        tts_lang = self._to_tts_code(request.target_lang)
        
        tts_result = await self.tts_engine.synthesize_async(
            nmt_result.text,
            language=tts_lang,
            speaker_wav=request.speaker_wav,
        )
        stage_latencies["tts"] = (time.time() - tts_start) * 1000

        logger.info(
            "TTS complete",
            audio_duration=len(tts_result.audio) / tts_result.sample_rate,
            latency_ms=stage_latencies["tts"],
        )

        # Calculate total latency
        total_latency = (time.time() - start_time) * 1000

        logger.info(
            "Translation complete",
            total_latency_ms=total_latency,
            stages=stage_latencies,
        )

        return TranslationResponse(
            audio=tts_result.audio,
            sample_rate=tts_result.sample_rate,
            transcription=asr_result.text,
            translation=nmt_result.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            latency_ms=total_latency,
            stage_latencies=stage_latencies,
            confidences=confidences,
        )

    async def translate_streaming(
        self,
        audio_chunks: AsyncGenerator[bytes, None],
        source_lang: str,
        target_lang: str,
        sample_rate: int = 16000,
    ) -> AsyncGenerator[TranslationResponse, None]:
        """
        Streaming translation for real-time audio.
        
        Args:
            audio_chunks: Async generator of audio chunks
            source_lang: Source language code
            target_lang: Target language code
            sample_rate: Audio sample rate
            
        Yields:
            TranslationResponse for each processed segment
        """
        logger.info(
            "Starting streaming translation",
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # This is a simplified streaming implementation
        # In production, implement proper VAD and chunking
        buffer = []

        async for chunk in audio_chunks:
            # Convert bytes to audio
            audio_array = np.frombuffer(chunk, dtype=np.float32)
            buffer.extend(audio_array.tolist())

            # Process when buffer reaches threshold (e.g., 2 seconds)
            if len(buffer) >= sample_rate * 2:
                request = TranslationRequest(
                    audio=buffer,
                    sample_rate=sample_rate,
                    source_lang=source_lang,
                    target_lang=target_lang,
                )

                response = await self.translate(request)
                yield response

                # Clear buffer
                buffer = []

        # Process remaining buffer
        if buffer:
            request = TranslationRequest(
                audio=buffer,
                sample_rate=sample_rate,
                source_lang=source_lang,
                target_lang=target_lang,
            )

            response = await self.translate(request)
            yield response

    def _to_nllb_code(self, lang_code: str) -> str:
        """
        Convert language code to NLLB format.
        
        Args:
            lang_code: Input language code (ISO 639-1 or NLLB)
            
        Returns:
            NLLB language code (e.g., 'eng_Latn', 'spa_Latn')
        """
        # Map common codes to NLLB format
        nllb_map = {
            "en": "eng_Latn",
            "es": "spa_Latn",
            "fr": "fra_Latn",
            "de": "deu_Latn",
            "zh": "zho_Hans",
            "ja": "jpn_Jpan",
            "ko": "kor_Hang",
            "ar": "arb_Arab",
            "hi": "hin_Deva",
            "pt": "por_Latn",
            "ru": "rus_Cyrl",
            "it": "ita_Latn",
        }

        # Return mapped or original if already in NLLB format
        return nllb_map.get(lang_code, lang_code)

    def _to_tts_code(self, lang_code: str) -> str:
        """
        Convert language code to TTS format.
        
        Args:
            lang_code: Input language code
            
        Returns:
            TTS language code (e.g., 'en', 'es')
        """
        # Map NLLB codes to TTS codes
        tts_map = {
            "eng_Latn": "en",
            "spa_Latn": "es",
            "fra_Latn": "fr",
            "deu_Latn": "de",
            "zho_Hans": "zh-cn",
            "jpn_Jpan": "ja",
            "kor_Hang": "ko",
            "arb_Arab": "ar",
            "hin_Deva": "hi",
            "por_Latn": "pt",
            "rus_Cyrl": "ru",
            "ita_Latn": "it",
        }

        # Return mapped or extract first part if simple code
        if lang_code in tts_map:
            return tts_map[lang_code]
        
        # If already simple code, return as-is
        if len(lang_code) == 2:
            return lang_code
        
        # Otherwise extract base code
        return lang_code.split("_")[0][:2]


def create_pipeline(
    asr_engine: WhisperEngine | None = None,
    nmt_engine: NLLBEngine | None = None,
    tts_engine: XTTSEngine | None = None,
) -> TranslationPipeline:
    """
    Factory function to create translation pipeline.
    
    Args:
        asr_engine: Custom ASR engine (optional)
        nmt_engine: Custom NMT engine (optional)
        tts_engine: Custom TTS engine (optional)
        
    Returns:
        Initialized TranslationPipeline
    """
    return TranslationPipeline(
        asr_engine=asr_engine,
        nmt_engine=nmt_engine,
        tts_engine=tts_engine,
    )
