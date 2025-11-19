"""
OneWhat Speech Recognition (ASR) Engine using OpenAI Whisper.

This module provides state-of-the-art speech recognition with:
- Multi-language support (99+ languages)
- Streaming and batch processing
- GPU acceleration
- Model optimization (INT8 quantization, CTranslate2)
"""

import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional

import numpy as np
import torch
from faster_whisper import WhisperModel
from pydantic import BaseModel, Field

from ..utils.config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TranscriptionResult(BaseModel):
    """Transcription result with metadata."""

    text: str
    language: str
    confidence: float = Field(ge=0.0, le=1.0)
    segments: list[dict] = Field(default_factory=list)
    processing_time_ms: float


class WhisperEngine:
    """
    Optimized Whisper ASR engine using faster-whisper (CTranslate2).
    
    Features:
    - 4x faster than standard Whisper
    - INT8 quantization for efficiency
    - Streaming support
    - Language detection
    - Timestamp-accurate transcription
    """

    def __init__(
        self,
        model_name: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
        download_root: Optional[Path] = None,
    ):
        """
        Initialize Whisper engine.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large-v3)
            device: Device to run on (cuda, cpu)
            compute_type: Precision (float16, int8, int8_float16)
            download_root: Where to store/load models
        """
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        
        logger.info(
            f"Loading Whisper model: {model_name}",
            extra={"device": device, "compute_type": compute_type},
        )
        
        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=str(download_root) if download_root else None,
        )
        
        logger.info("Whisper model loaded successfully")

    async def transcribe(
        self,
        audio: np.ndarray,
        source_language: Optional[str] = None,
        task: str = "transcribe",
        beam_size: int = 5,
        best_of: int = 5,
        temperature: float = 0.0,
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.
        
        Args:
            audio: Audio waveform as numpy array (16kHz, mono)
            source_language: Source language code (e.g., 'en', 'es'). Auto-detect if None
            task: 'transcribe' or 'translate' (to English)
            beam_size: Beam search size (higher = more accurate but slower)
            best_of: Number of candidates when sampling (higher = better quality)
            temperature: Sampling temperature (0 = greedy, higher = more random)
            
        Returns:
            TranscriptionResult with text and metadata
        """
        import time
        
        start_time = time.time()
        
        # Run transcription in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: self.model.transcribe(
                audio,
                language=source_language,
                task=task,
                beam_size=beam_size,
                best_of=best_of,
                temperature=temperature,
                vad_filter=True,  # Voice Activity Detection filter
                vad_parameters=dict(min_silence_duration_ms=500),
            ),
        )
        
        # Convert generator to list
        segments_list = list(segments)
        
        # Combine all segment texts
        full_text = " ".join(segment.text.strip() for segment in segments_list)
        
        # Calculate average confidence
        confidences = [segment.avg_logprob for segment in segments_list]
        avg_confidence = float(np.exp(np.mean(confidences))) if confidences else 0.0
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        result = TranscriptionResult(
            text=full_text,
            language=info.language,
            confidence=avg_confidence,
            segments=[
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                    "confidence": float(np.exp(seg.avg_logprob)),
                }
                for seg in segments_list
            ],
            processing_time_ms=processing_time,
        )
        
        logger.debug(
            f"Transcribed {len(segments_list)} segments",
            extra={
                "language": result.language,
                "confidence": result.confidence,
                "processing_time_ms": result.processing_time_ms,
            },
        )
        
        return result

    async def transcribe_streaming(
        self,
        audio_stream: AsyncIterator[np.ndarray],
        source_language: Optional[str] = None,
        chunk_length_s: float = 5.0,
    ) -> AsyncIterator[TranscriptionResult]:
        """
        Stream transcription for real-time audio.
        
        Args:
            audio_stream: Async iterator of audio chunks
            source_language: Source language code
            chunk_length_s: Length of each chunk in seconds
            
        Yields:
            TranscriptionResult for each processed chunk
        """
        buffer = np.array([], dtype=np.float32)
        chunk_size = int(chunk_length_s * 16000)  # 16kHz sample rate
        
        async for audio_chunk in audio_stream:
            buffer = np.concatenate([buffer, audio_chunk])
            
            # Process when buffer is large enough
            while len(buffer) >= chunk_size:
                chunk = buffer[:chunk_size]
                buffer = buffer[chunk_size:]
                
                result = await self.transcribe(
                    chunk,
                    source_language=source_language,
                    beam_size=3,  # Faster for real-time
                    best_of=3,
                )
                
                yield result
        
        # Process remaining audio in buffer
        if len(buffer) > 0:
            result = await self.transcribe(
                buffer,
                source_language=source_language,
                beam_size=3,
                best_of=3,
            )
            yield result

    def detect_language(self, audio: np.ndarray) -> tuple[str, float]:
        """
        Detect the language of the audio.
        
        Args:
            audio: Audio waveform as numpy array
            
        Returns:
            (language_code, confidence)
        """
        # Use first 30 seconds for language detection
        audio_sample = audio[: 30 * 16000]
        
        segments, info = self.model.transcribe(
            audio_sample,
            language=None,  # Auto-detect
            task="transcribe",
        )
        
        return info.language, info.language_probability


class StreamingASR:
    """
    Real-time streaming ASR with voice activity detection and buffering.
    
    Optimized for low-latency real-time transcription with:
    - Voice Activity Detection (VAD)
    - Intelligent buffering
    - Overlapping windows for context
    """

    def __init__(
        self,
        whisper_engine: WhisperEngine,
        vad_threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        max_speech_duration_s: float = 30.0,
    ):
        """
        Initialize streaming ASR.
        
        Args:
            whisper_engine: Whisper engine instance
            vad_threshold: Voice activity detection threshold
            min_speech_duration_ms: Minimum speech duration to process
            max_speech_duration_s: Maximum speech duration per chunk
        """
        self.engine = whisper_engine
        self.vad_threshold = vad_threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.max_speech_duration_s = max_speech_duration_s
        
        self.buffer = np.array([], dtype=np.float32)
        self.is_speaking = False

    async def process_chunk(
        self,
        audio_chunk: np.ndarray,
        source_language: Optional[str] = None,
    ) -> Optional[TranscriptionResult]:
        """
        Process a single audio chunk.
        
        Args:
            audio_chunk: Audio data (16kHz, mono)
            source_language: Source language code
            
        Returns:
            TranscriptionResult if speech detected and processed, None otherwise
        """
        # Add to buffer
        self.buffer = np.concatenate([self.buffer, audio_chunk])
        
        # Check if buffer exceeds max duration
        max_samples = int(self.max_speech_duration_s * 16000)
        
        if len(self.buffer) >= max_samples:
            # Process accumulated audio
            result = await self.engine.transcribe(
                self.buffer,
                source_language=source_language,
                beam_size=3,  # Faster for streaming
            )
            
            # Keep last 1 second for context
            overlap_samples = 16000
            self.buffer = self.buffer[-overlap_samples:]
            
            return result
        
        return None

    def reset(self) -> None:
        """Reset the buffer and state."""
        self.buffer = np.array([], dtype=np.float32)
        self.is_speaking = False


# Factory function for easy initialization
async def create_asr_engine(
    model_name: Optional[str] = None,
    device: Optional[str] = None,
    compute_type: Optional[str] = None,
) -> WhisperEngine:
    """
    Create and initialize ASR engine with default settings from config.
    
    Args:
        model_name: Override default model name
        device: Override default device
        compute_type: Override default compute type
        
    Returns:
        Initialized WhisperEngine
    """
    return WhisperEngine(
        model_name=model_name or settings.WHISPER_MODEL,
        device=device or settings.WHISPER_DEVICE,
        compute_type=compute_type or settings.WHISPER_COMPUTE_TYPE,
        download_root=settings.MODELS_DIR / "whisper",
    )
