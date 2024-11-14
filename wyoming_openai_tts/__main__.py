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
                name="Microsoft",
                url="https://github.com/hugobloem/wyoming-microsoft-tts",
            ),
            installed=True,
            version=__version__,
            languages=[
                voice_info.get("language", {}).get(
                    "code",
                    voice_info.get("espeak", {}).get("voice", voice_name.split("_")[0]),
                )
            ],
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
