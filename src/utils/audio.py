"""Audio processing utilities."""

import io
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment


def load_audio(
    audio_path: str | Path,
    sample_rate: int = 16000,
    mono: bool = True,
) -> np.ndarray:
    """
    Load audio file and convert to numpy array.
    
    Args:
        audio_path: Path to audio file
        sample_rate: Target sample rate (Hz)
        mono: Convert to mono if True
        
    Returns:
        Audio waveform as numpy array
    """
    audio, sr = librosa.load(
        audio_path,
        sr=sample_rate,
        mono=mono,
    )
    return audio


def save_audio(
    audio: np.ndarray,
    output_path: str | Path,
    sample_rate: int = 16000,
    format: str = "wav",
) -> None:
    """
    Save numpy array as audio file.
    
    Args:
        audio: Audio waveform
        output_path: Output file path
        sample_rate: Sample rate (Hz)
        format: Audio format (wav, mp3, ogg, etc.)
    """
    sf.write(
        str(output_path),
        audio,
        sample_rate,
        format=format,
    )


def bytes_to_audio(
    audio_bytes: bytes,
    sample_rate: int = 16000,
) -> np.ndarray:
    """
    Convert audio bytes to numpy array.
    
    Args:
        audio_bytes: Raw audio bytes
        sample_rate: Sample rate (Hz)
        
    Returns:
        Audio waveform as numpy array
    """
    # Try to load with soundfile first (most formats)
    try:
        audio, sr = sf.read(io.BytesIO(audio_bytes))
        if sr != sample_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
        return audio
    except Exception:
        # Fall back to pydub for other formats (mp3, etc.)
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio_segment = audio_segment.set_frame_rate(sample_rate).set_channels(1)
        audio = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        audio = audio / np.iinfo(audio_segment.array_type).max
        return audio


def audio_to_bytes(
    audio: np.ndarray,
    sample_rate: int = 16000,
    format: str = "wav",
) -> bytes:
    """
    Convert numpy array to audio bytes.
    
    Args:
        audio: Audio waveform
        sample_rate: Sample rate (Hz)
        format: Audio format
        
    Returns:
        Audio as bytes
    """
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format=format)
    buffer.seek(0)
    return buffer.read()


def resample_audio(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: int,
) -> np.ndarray:
    """
    Resample audio to target sample rate.
    
    Args:
        audio: Audio waveform
        orig_sr: Original sample rate
        target_sr: Target sample rate
        
    Returns:
        Resampled audio
    """
    return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """
    Normalize audio to [-1, 1] range.
    
    Args:
        audio: Audio waveform
        
    Returns:
        Normalized audio
    """
    max_val = np.abs(audio).max()
    if max_val > 0:
        return audio / max_val
    return audio


def split_on_silence(
    audio: np.ndarray,
    sample_rate: int = 16000,
    min_silence_len: int = 500,
    silence_thresh: float = -40.0,
    keep_silence: int = 200,
) -> list[np.ndarray]:
    """
    Split audio on silence.
    
    Args:
        audio: Audio waveform
        sample_rate: Sample rate (Hz)
        min_silence_len: Minimum silence length (ms)
        silence_thresh: Silence threshold (dB)
        keep_silence: Amount of silence to keep (ms)
        
    Returns:
        List of audio segments
    """
    # Convert to AudioSegment
    audio_int16 = (audio * 32767).astype(np.int16)
    audio_segment = AudioSegment(
        audio_int16.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1,
    )
    
    # Split on silence
    from pydub.silence import split_on_silence as pydub_split
    
    chunks = pydub_split(
        audio_segment,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
    )
    
    # Convert back to numpy arrays
    result = []
    for chunk in chunks:
        samples = np.array(chunk.get_array_of_samples(), dtype=np.float32)
        samples = samples / 32767.0
        result.append(samples)
    
    return result
