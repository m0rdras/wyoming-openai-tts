"""Event handler for clients of the server."""
import argparse
import logging
import os
import wave

from wyoming.audio import AudioChunk, AudioStart, AudioStop
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

        output_path = self.openai_tts.synthesize(
            text=synthesize.text, voice=voice_name
        )

        try:
            with wave.open(output_path, "rb") as wav_file:
                rate = wav_file.getframerate()
                width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()

                await self.write_event(
                    AudioStart(
                        rate=rate,
                        width=width,
                        channels=channels,
                    ).event(),
                )

                # Read and send chunks
                frames_per_chunk = self.cli_args.samples_per_chunk
                while True:
                    chunk = wav_file.readframes(frames_per_chunk)
                    if not chunk:
                        break

                    await self.write_event(
                        AudioChunk(
                            audio=chunk,
                            rate=rate,
                            width=width,
                            channels=channels,
                        ).event(),
                    )

            await self.write_event(AudioStop().event())
            _LOGGER.debug("Completed request")

        finally:
            # Clean up the temporary file
            try:
                os.unlink(output_path)
            except Exception as e:
                _LOGGER.warning(f"Failed to delete temporary file {output_path}: {str(e)}")

        return True
