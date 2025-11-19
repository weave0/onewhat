"""Text-to-Speech engine using Coqui XTTS v2."""

import asyncio
from pathlib import Path

import numpy as np
import torch
from pydantic import BaseModel, Field
from TTS.api import TTS

from ..utils.config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SynthesisResult(BaseModel):
    """TTS synthesis result with metadata."""

    audio: list[float] = Field(description="Audio waveform as list")
    sample_rate: int = Field(description="Audio sample rate (Hz)")
    text: str = Field(description="Input text")
    language: str = Field(description="Target language")
    speaker: str | None = Field(default=None, description="Speaker ID/name")
    model_name: str = Field(description="TTS model used")

    class Config:
        arbitrary_types_allowed = True


class XTTSEngine:
    """
    Text-to-Speech using Coqui XTTS v2.
    
    Supports multilingual synthesis with voice cloning.
    """

    def __init__(
        self,
        model_name: str = settings.TTS_MODEL,
        device: str = settings.TTS_DEVICE,
    ):
        """
        Initialize XTTS engine.
        
        Args:
            model_name: TTS model identifier
            device: Device for inference ('cuda' or 'cpu')
        """
        self.model_name = model_name
        self.device = device

        logger.info("Loading TTS model", model=model_name, device=device)

        # Initialize TTS
        gpu = device == "cuda" and torch.cuda.is_available()
        self.tts = TTS(model_name=model_name, gpu=gpu)

        if gpu:
            logger.info(
                "TTS model loaded on GPU",
                gpu_name=torch.cuda.get_device_name(0),
            )
        else:
            logger.info("TTS model loaded on CPU")

        # Get model info
        self.sample_rate = getattr(
            self.tts.synthesizer.tts_model,
            "sample_rate",
            22050,
        )

        logger.info(
            "XTTS engine ready",
            sample_rate=self.sample_rate,
            languages=self.get_supported_languages(),
        )

    def synthesize(
        self,
        text: str,
        language: str = "en",
        speaker: str | None = None,
        speaker_wav: str | Path | None = None,
    ) -> SynthesisResult:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            language: Target language code (e.g., 'en', 'es')
            speaker: Speaker ID (if multi-speaker model)
            speaker_wav: Path to reference audio for voice cloning
            
        Returns:
            SynthesisResult with audio and metadata
        """
        logger.debug(
            "Synthesizing speech",
            text_length=len(text),
            language=language,
            speaker=speaker,
        )

        # Prepare kwargs
        kwargs = {
            "text": text,
            "language": language,
        }

        if speaker is not None:
            kwargs["speaker"] = speaker

        if speaker_wav is not None:
            kwargs["speaker_wav"] = str(speaker_wav)

        # Synthesize
        audio = self.tts.tts(**kwargs)

        # Convert to numpy array if needed
        if isinstance(audio, list):
            audio_array = np.array(audio, dtype=np.float32)
        else:
            audio_array = audio

        logger.debug(
            "Synthesis complete",
            audio_length=len(audio_array),
            duration_sec=len(audio_array) / self.sample_rate,
        )

        return SynthesisResult(
            audio=audio_array.tolist(),
            sample_rate=self.sample_rate,
            text=text,
            language=language,
            speaker=speaker,
            model_name=self.model_name,
        )

    async def synthesize_async(
        self,
        text: str,
        language: str = "en",
        speaker: str | None = None,
        speaker_wav: str | Path | None = None,
    ) -> SynthesisResult:
        """
        Async synthesis wrapper.
        
        Args:
            text: Text to synthesize
            language: Target language
            speaker: Speaker ID
            speaker_wav: Reference audio for voice cloning
            
        Returns:
            SynthesisResult
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.synthesize,
            text,
            language,
            speaker,
            speaker_wav,
        )

    def synthesize_to_file(
        self,
        text: str,
        output_path: str | Path,
        language: str = "en",
        speaker: str | None = None,
        speaker_wav: str | Path | None = None,
    ) -> Path:
        """
        Synthesize speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Output audio file path
            language: Target language
            speaker: Speaker ID
            speaker_wav: Reference audio for voice cloning
            
        Returns:
            Path to output file
        """
        output_path = Path(output_path)

        logger.debug(
            "Synthesizing to file",
            output_path=str(output_path),
            language=language,
        )

        # Prepare kwargs
        kwargs = {
            "text": text,
            "file_path": str(output_path),
            "language": language,
        }

        if speaker is not None:
            kwargs["speaker"] = speaker

        if speaker_wav is not None:
            kwargs["speaker_wav"] = str(speaker_wav)

        # Synthesize and save
        self.tts.tts_to_file(**kwargs)

        logger.info("Audio saved", path=str(output_path))
        return output_path

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language codes
        """
        try:
            if hasattr(self.tts, "languages"):
                return self.tts.languages
            if hasattr(self.tts.synthesizer, "tts_config"):
                config = self.tts.synthesizer.tts_config
                if hasattr(config, "languages"):
                    return config.languages
        except Exception as e:
            logger.warning("Could not get languages", error=str(e))

        return ["en"]  # Default fallback

    def clone_voice(
        self,
        text: str,
        reference_audio: str | Path,
        language: str = "en",
    ) -> SynthesisResult:
        """
        Clone voice from reference audio and synthesize text.
        
        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio
            language: Target language
            
        Returns:
            SynthesisResult with cloned voice
        """
        logger.info(
            "Cloning voice",
            reference=str(reference_audio),
            language=language,
        )

        return self.synthesize(
            text=text,
            language=language,
            speaker_wav=reference_audio,
        )


def create_tts_engine(
    model_name: str | None = None,
    device: str | None = None,
) -> XTTSEngine:
    """
    Factory function to create TTS engine.
    
    Args:
        model_name: Model identifier (uses default if None)
        device: Device for inference (uses default if None)
        
    Returns:
        Initialized XTTSEngine
    """
    kwargs = {}
    if model_name is not None:
        kwargs["model_name"] = model_name
    if device is not None:
        kwargs["device"] = device

    return XTTSEngine(**kwargs)
