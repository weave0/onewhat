"""Neural Machine Translation engine using Meta's NLLB-200 model."""

import asyncio
from typing import Any

import torch
from pydantic import BaseModel, Field
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    NllbTokenizer,
)

from ..utils.config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TranslationResult(BaseModel):
    """Translation result with metadata."""

    text: str = Field(description="Translated text")
    source_lang: str = Field(description="Source language code")
    target_lang: str = Field(description="Target language code")
    confidence: float = Field(
        description="Translation confidence score (0-1)",
        ge=0.0,
        le=1.0,
    )
    model_name: str = Field(description="Model used for translation")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class NLLBEngine:
    """
    Neural Machine Translation using Meta's NLLB-200 model.
    
    Supports 200 languages with state-of-the-art quality.
    """

    def __init__(
        self,
        model_name: str = settings.NMT_MODEL,
        device: str = settings.NMT_DEVICE,
        max_length: int = settings.NMT_MAX_LENGTH,
    ):
        """
        Initialize NLLB translation engine.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device for inference ('cuda' or 'cpu')
            max_length: Maximum translation length
        """
        self.model_name = model_name
        self.device = device
        self.max_length = max_length

        logger.info("Loading NLLB model", model=model_name, device=device)

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # Move to device
        if device == "cuda" and torch.cuda.is_available():
            self.model = self.model.cuda()
            logger.info("Model loaded on GPU", gpu_name=torch.cuda.get_device_name(0))
        else:
            self.model = self.model.cpu()
            logger.info("Model loaded on CPU")

        # Set to eval mode
        self.model.eval()

        logger.info("NLLB engine ready")

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int | None = None,
    ) -> TranslationResult:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'eng_Latn')
            target_lang: Target language code (e.g., 'spa_Latn')
            max_length: Maximum output length (uses default if None)
            
        Returns:
            TranslationResult with translation and metadata
        """
        max_length = max_length or self.max_length

        logger.debug(
            "Translating",
            source_lang=source_lang,
            target_lang=target_lang,
            text_length=len(text),
        )

        # Set source language
        if isinstance(self.tokenizer, NllbTokenizer):
            self.tokenizer.src_lang = source_lang

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )

        # Move to device
        if self.device == "cuda" and torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Generate translation
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[target_lang],
                max_length=max_length,
                num_beams=5,
                early_stopping=True,
            )

        # Decode
        translated_text = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
        )[0]

        # Calculate confidence (from generation scores)
        confidence = self._calculate_confidence(generated_tokens)

        logger.debug(
            "Translation complete",
            output_length=len(translated_text),
            confidence=confidence,
        )

        return TranslationResult(
            text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=confidence,
            model_name=self.model_name,
            metadata={
                "input_length": len(text),
                "output_length": len(translated_text),
            },
        )

    async def translate_async(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int | None = None,
    ) -> TranslationResult:
        """
        Async translation wrapper.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            max_length: Maximum output length
            
        Returns:
            TranslationResult
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.translate,
            text,
            source_lang,
            target_lang,
            max_length,
        )

    def translate_batch(
        self,
        texts: list[str],
        source_lang: str,
        target_lang: str,
        max_length: int | None = None,
    ) -> list[TranslationResult]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            max_length: Maximum output length
            
        Returns:
            List of TranslationResults
        """
        max_length = max_length or self.max_length

        logger.debug(
            "Batch translation",
            batch_size=len(texts),
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # Set source language
        if isinstance(self.tokenizer, NllbTokenizer):
            self.tokenizer.src_lang = source_lang

        # Tokenize batch
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )

        # Move to device
        if self.device == "cuda" and torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Generate translations
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[target_lang],
                max_length=max_length,
                num_beams=5,
                early_stopping=True,
            )

        # Decode all
        translated_texts = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
        )

        # Build results
        results = []
        for i, translated_text in enumerate(translated_texts):
            confidence = self._calculate_confidence(generated_tokens[i:i+1])
            results.append(
                TranslationResult(
                    text=translated_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    confidence=confidence,
                    model_name=self.model_name,
                    metadata={
                        "input_length": len(texts[i]),
                        "output_length": len(translated_text),
                    },
                )
            )

        logger.debug("Batch translation complete", count=len(results))
        return results

    def _calculate_confidence(self, tokens: torch.Tensor) -> float:
        """
        Calculate translation confidence from generated tokens.
        
        Args:
            tokens: Generated token IDs
            
        Returns:
            Confidence score (0-1)
        """
        # Placeholder: In production, use model scores
        # For now, return fixed high confidence
        return 0.95

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of NLLB language codes
        """
        if isinstance(self.tokenizer, NllbTokenizer):
            return list(self.tokenizer.lang_code_to_id.keys())
        return []


def create_nmt_engine(
    model_name: str | None = None,
    device: str | None = None,
    max_length: int | None = None,
) -> NLLBEngine:
    """
    Factory function to create NMT engine.
    
    Args:
        model_name: Model identifier (uses default if None)
        device: Device for inference (uses default if None)
        max_length: Max translation length (uses default if None)
        
    Returns:
        Initialized NLLBEngine
    """
    kwargs = {}
    if model_name is not None:
        kwargs["model_name"] = model_name
    if device is not None:
        kwargs["device"] = device
    if max_length is not None:
        kwargs["max_length"] = max_length

    return NLLBEngine(**kwargs)
