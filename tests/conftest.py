"""Fixtures for tests."""

from types import SimpleNamespace
import pytest
from wyoming_openai_tts.openai_tts import OpenAITTS
import os


@pytest.fixture
def configuration():
    """Return configuration."""
    return {
        "voice": "alloy",
    }


@pytest.fixture
def openai_tts(configuration):
    """Return OpenAITTS instance."""
    args = SimpleNamespace(
        api_key=os.environ.get("OPENAI_API_KEY"),
        **configuration
    )
    return OpenAITTS(args)
