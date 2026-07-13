"""
Thin wrapper around the OpenRouter API (OpenAI-compatible).

OpenRouter lets you call many models, including several FREE models,
through one API key: https://openrouter.ai

Setup:
    1. Create a free account at https://openrouter.ai
    2. Create an API key (no credit card required for free models)
    3. Copy .env.example to .env and paste your key into OPENROUTER_API_KEY
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Free-tier models on OpenRouter (subject to change - check openrouter.ai/models
# filtered to Price: Free for the current list). qwen3-coder and gpt-oss-20b
# support tool/function calling, which the agent page needs.
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-coder:free")

# Fallback used if the primary free model is rate-limited / unavailable.
FALLBACK_MODEL = os.getenv("OPENROUTER_FALLBACK_MODEL", "openrouter/free")


def get_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to a .env file "
            "(see .env.example) to enable LLM-powered features."
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )


def is_configured() -> bool:
    return bool(OPENROUTER_API_KEY)


def chat_completion(messages, model: str = None, **kwargs):
    """
    Simple, non-tool-calling completion. Returns the response text.
    Falls back to FALLBACK_MODEL if the primary free model call fails
    (e.g. rate limit on the free tier).
    """
    client = get_client()
    model = model or DEFAULT_MODEL

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
    except Exception as primary_error:
        try:
            response = client.chat.completions.create(
                model=FALLBACK_MODEL,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as fallback_error:
            raise RuntimeError(
                f"Both primary ({model}) and fallback ({FALLBACK_MODEL}) "
                f"model calls failed.\nPrimary error: {primary_error}\n"
                f"Fallback error: {fallback_error}"
            )
