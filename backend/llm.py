"""
backend/llm.py
===============
A single, provider-agnostic interface for calling an LLM. Supports
OpenAI, Anthropic (Claude), Google Gemini, and Groq — pick one via
`LLM_PROVIDER` in `.env` or the Settings page.

Each provider's SDK is imported lazily (inside its call function) so the
app doesn't crash on startup if you only installed/configured one
provider's package and key.
"""

from __future__ import annotations

from typing import List, Optional

from backend.utils import get_logger
from config import settings

logger = get_logger(__name__)


class LLMError(Exception):
    """Raised when the configured LLM provider fails or is misconfigured."""


def generate_answer(
    system_prompt: str,
    user_prompt: str,
    provider: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Generate a completion from the configured provider.

    All provider-specific request/response shapes are normalized here so
    callers just get back a plain string.
    """
    provider = (provider or settings.llm_provider).lower()
    temperature = settings.temperature if temperature is None else temperature
    max_tokens = settings.max_tokens if max_tokens is None else max_tokens

    dispatch = {
        "openai": _call_openai,
        "anthropic": _call_anthropic,
        "gemini": _call_gemini,
        "groq": _call_groq,
    }
    if provider not in dispatch:
        raise LLMError(
            f"Unknown LLM_PROVIDER '{provider}'. Choose one of: {list(dispatch)}"
        )

    try:
        return dispatch[provider](system_prompt, user_prompt, temperature, max_tokens)
    except LLMError:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM call failed (provider=%s)", provider)
        raise LLMError(
            f"The '{provider}' provider failed: {exc}. "
            "Check your API key and model name in Settings / .env."
        ) from exc


# --------------------------------------------------------------------------- #
# Provider implementations
# --------------------------------------------------------------------------- #
def _call_openai(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    if not settings.openai_api_key:
        raise LLMError("OPENAI_API_KEY is not set.")
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _call_anthropic(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    if not settings.anthropic_api_key:
        raise LLMError("ANTHROPIC_API_KEY is not set.")
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()


def _call_gemini(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    if not settings.gemini_api_key:
        raise LLMError("GEMINI_API_KEY is not set.")
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.gemini_model,
        system_instruction=system_prompt,
    )
    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text.strip()


def _call_groq(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
    if not settings.groq_api_key:
        raise LLMError("GROQ_API_KEY is not set.")
    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.groq_model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def available_providers() -> List[str]:
    """Return providers that currently have an API key configured."""
    available = []
    if settings.openai_api_key:
        available.append("openai")
    if settings.anthropic_api_key:
        available.append("anthropic")
    if settings.gemini_api_key:
        available.append("gemini")
    if settings.groq_api_key:
        available.append("groq")
    return available
