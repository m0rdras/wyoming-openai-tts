import argparse  # noqa: D100
import asyncio
import contextlib
import logging
from functools import partial
from typing import Any

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

from wyoming_openai_tts.download import get_voices
from wyoming_openai_tts.handler import OpenAIEventHandler
from wyoming_openai_tts.version import __version__

_LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = [
    "af-ZA", "ar-AR", "hy-AM", "az-AZ", "be-BY", "bs-BA", "bg-BG", "ca-ES",
    "zh-CN", "hr-HR", "cs-CZ", "da-DK", "nl-NL", "en-US", "et-EE", "fi-FI",
    "fr-FR", "gl-ES", "de-DE", "el-GR", "he-IL", "hi-IN", "hu-HU", "is-IS",
    "id-ID", "it-IT", "ja-JP", "kn-IN", "kk-KZ", "ko-KR", "lv-LV", "lt-LT",
    "mk-MK", "ms-MY", "mr-IN", "mi-NZ", "ne-NP", "no-NO", "fa-IR", "pl-PL",
    "pt-PT", "ro-RO", "ru-RU", "sr-RS", "sk-SK", "sl-SI", "es-ES", "sw-KE",
    "sv-SE", "tl-PH", "ta-IN", "th-TH", "tr-TR", "uk-UA", "ur-PK", "vi-VN",
    "cy-GB"
]

async def main() -> None:
    """Start Wyoming OpenAI TTS server."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-key",
        required=True,
        help="OpenAI API key",
    )
    parser.add_argument(
        "--voice",
        default="alloy",
        help="Default OpenAI voice to use (alloy, echo, fable, onyx, nova, or shimmer)",
    )
    parser.add_argument(
        "--uri", default="tcp://0.0.0.0:10200", help="unix:// or tcp://"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Log DEBUG messages"
    )
    parser.add_argument(
        "--auto-punctuation",
        default=".?!",
        help="Automatically add punctuation (default: '.?!')",
    )
    parser.add_argument(
        "--samples-per-chunk",
        type=int,
        default=2048,
        help="Number of samples to send in each audio chunk (default: 2048)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)


    # Load voice info
    voices_info = get_voices()

    # Resolve aliases for backwards compatibility with old voice names
    aliases_info: dict[str, Any] = {}
    for voice_info in voices_info.values():
        for voice_alias in voice_info.get("aliases", []):
            aliases_info[voice_alias] = {"_is_alias": True, **voice_info}

    voices_info.update(aliases_info)
    voices = [
        TtsVoice(
            name=voice_name,
            description=get_description(voice_info),
            attribution=Attribution(
                name="OpenAI",
                url="https://github.com/m0rdras/wyoming-openai-tts",
            ),
            installed=True,
            version=__version__,
            languages=SUPPORTED_LANGUAGES,
            #
            # Don't send speakers for now because it overflows StreamReader buffers
            # speakers=[
            #     TtsVoiceSpeaker(name=speaker_name)
            #     for speaker_name in voice_info["speaker_id_map"]
            # ]
            # if voice_info.get("speaker_id_map")
            # else None,
        )
        for voice_name, voice_info in voices_info.items()
        if not voice_info.get("_is_alias", False)
    ]

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="openai-tts",
                description="OpenAI's text-to-speech service",
                attribution=Attribution(
                    name="OpenAI",
                    url="https://github.com/m0rdras/wyoming-openai-tts",
                ),
                installed=True,
                version=__version__,
                voices=sorted(voices, key=lambda v: v.name),
            )
        ],
    )

    # Start server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Ready")
    await server.run(
        partial(
            OpenAIEventHandler,
            wyoming_info,
            args,
        )
    )


# -----------------------------------------------------------------------------


def get_description(voice_info: dict[str, Any]):
    """Get a human readable description for a voice."""
    name = voice_info["name"]
    name = " ".join(name.split("_"))
    quality = voice_info["quality"]

    return f"{name} ({quality})"


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
