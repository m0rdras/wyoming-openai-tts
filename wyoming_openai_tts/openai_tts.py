"""OpenAI TTS."""
import logging
import wave
import io
import asyncio
import struct
from openai import OpenAI
from wyoming.audio import AudioChunk, AudioStart, AudioStop

_LOGGER = logging.getLogger(__name__)

class OpenAITTS:
    """Class to handle OpenAI TTS."""

    def __init__(self, args) -> None:
        """Initialize."""
        _LOGGER.debug("Initialize OpenAI TTS")
        self.args = args
        self.client = OpenAI(api_key=args.api_key)

    async def stream_to_wyoming(self, text, voice, event_handler, samples_per_chunk):
        """Stream audio directly to Wyoming."""
        _LOGGER.debug(f"Requested TTS for [{text}]")
        if voice is None:
            voice = self.args.voice

        try:
            with self.client.audio.speech.with_streaming_response.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                    response_format="wav",
            ) as response:
                # Buffer for WAV header
                header_buffer = bytearray()
                data_buffer = io.BytesIO()
                header_complete = False

                for chunk in response.iter_bytes(chunk_size=1024):
                    if not header_complete:
                        header_buffer.extend(chunk)
                        if len(header_buffer) >= 44:  # WAV header size
                            # Process header
                            fmt_chunk_size = struct.unpack('<I', header_buffer[16:20])[0]
                            header_size = 44 if fmt_chunk_size == 16 else 44 + (fmt_chunk_size - 16)

                            if len(header_buffer) >= header_size:
                                # Parse WAV header
                                with io.BytesIO(header_buffer[:header_size]) as header_io:
                                    with wave.open(header_io, 'rb') as wav_header:
                                        rate = wav_header.getframerate()
                                        width = wav_header.getsampwidth()
                                        channels = wav_header.getnchannels()

                                # Send audio start event
                                await event_handler.write_event(
                                    AudioStart(
                                        rate=rate,
                                        width=width,
                                        channels=channels,
                                    ).event()
                                )

                                # Add remaining data to buffer
                                data_buffer.write(header_buffer[header_size:])
                                header_complete = True
                            continue

                    data_buffer.write(chunk)

                    # Process complete audio chunks
                    bytes_per_chunk = width * channels * samples_per_chunk
                    while data_buffer.tell() >= bytes_per_chunk:
                        data_buffer.seek(0)
                        audio_chunk = data_buffer.read(bytes_per_chunk)
                        remaining = data_buffer.read()
                        data_buffer = io.BytesIO()
                        data_buffer.write(remaining)

                        await event_handler.write_event(
                            AudioChunk(
                                audio=audio_chunk,
                                rate=rate,
                                width=width,
                                channels=channels,
                            ).event()
                        )
                        await asyncio.sleep(0.001)  # Small delay for backpressure

                # Send any remaining data
                if data_buffer.tell() > 0:
                    data_buffer.seek(0)
                    final_chunk = data_buffer.read()
                    if final_chunk:
                        await event_handler.write_event(
                            AudioChunk(
                                audio=final_chunk,
                                rate=rate,
                                width=width,
                                channels=channels,
                            ).event()
                        )

                # Send audio stop event
                await event_handler.write_event(AudioStop().event())
                _LOGGER.debug("Completed streaming TTS")
                return True

        except Exception as e:
            _LOGGER.warning(f"Speech synthesis failed: {str(e)}")
            return False
