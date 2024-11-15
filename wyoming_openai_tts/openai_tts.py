"""OpenAI TTS."""
import logging
import tempfile
import time
from pathlib import Path
from openai import OpenAI

_LOGGER = logging.getLogger(__name__)

class OpenAITTS:
    """Class to handle OpenAI TTS."""

    def __init__(self, args) -> None:
        """Initialize."""
        _LOGGER.debug("Initialize OpenAI TTS")
        _LOGGER.info("OpenAI Key: %s", args.api_key)
        self.args = args
        self.client = OpenAI(api_key=args.api_key)

        # Use provided output directory or create a temporary one
        self.output_dir = getattr(args, 'output_dir', None)
        if self.output_dir is None:
            self._temp_dir = tempfile.TemporaryDirectory()  # Store the object to prevent cleanup
            self.output_dir = Path(self._temp_dir.name)
        else:
            self.output_dir = Path(self.output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text, voice=None):
        """Synthesize text to speech."""
        _LOGGER.debug(f"Requested TTS for [{text}]")
        if voice is None:
            voice = self.args.voice

        try:
            file_name = self.output_dir / f"{time.monotonic_ns()}.wav"

            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="wav",
            )

            response.write_to_file(str(file_name))
            _LOGGER.debug(f"Speech synthesized for text [{text}]")
            return str(file_name)

        except Exception as e:
            _LOGGER.warning(f"Speech synthesis failed: {str(e)}")
            return None
