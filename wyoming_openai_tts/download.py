"""Utility for loading OpenAI voices."""

import json
import logging
from pathlib import Path
from typing import Any, Union

_DIR = Path(__file__).parent
_LOGGER = logging.getLogger(__name__)

class VoiceNotFoundError(Exception):
    """Raised when a voice is not found."""

    pass

def get_voices() -> dict[str, Any]:
    """Load available voices from embedded JSON file."""
    voices_embedded = _DIR / "voices.json"
    _LOGGER.debug("Loading %s", voices_embedded)
    with open(voices_embedded, encoding="utf-8") as voices_file:
        return json.load(voices_file)["voices"]

def find_voice(name: str, download_dir: Union[str, Path]) -> dict[str, Any]:
    """Look for the files for a voice.

    Returns: Dict of voice info
    """
    voices = get_voices(download_dir)
    if name in voices:
        return voices[name]

    raise VoiceNotFoundError(name)
