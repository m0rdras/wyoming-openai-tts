"""Event handler for clients of the server."""
import argparse
import logging

from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from .openai_tts import OpenAITTS

_LOGGER = logging.getLogger(__name__)


class OpenAIEventHandler(AsyncEventHandler):
    """Event handler for clients of the server."""

    def __init__(
            self,
            wyoming_info: Info,
            cli_args: argparse.Namespace,
            *args,
            **kwargs,
    ) -> None:
        """Initialize."""
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.openai_tts = OpenAITTS(cli_args)

    async def handle_event(self, event: Event) -> bool:
        """Handle an event."""
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        if not Synthesize.is_type(event.type):
            _LOGGER.warning("Unexpected event: %s", event)
            return True

        synthesize = Synthesize.from_event(event)
        _LOGGER.debug(synthesize)

        raw_text = synthesize.text

        # Join multiple lines
        text = " ".join(raw_text.strip().splitlines())

        if self.cli_args.auto_punctuation and text:
            # Add automatic punctuation (important for some voices)
            has_punctuation = False
            for punc_char in self.cli_args.auto_punctuation:
                if text[-1] == punc_char:
                    has_punctuation = True
                    break

            if not has_punctuation:
                text = text + self.cli_args.auto_punctuation[0]

        voice_name = synthesize.voice.name if synthesize.voice else self.cli_args.voice

        success = await self.openai_tts.stream_to_wyoming(
            text=text,
            voice=voice_name,
            event_handler=self,
            samples_per_chunk=self.cli_args.samples_per_chunk
        )

        return success
