#!/usr/bin/env python3
import asyncio
import wave
from pathlib import Path
import sys

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.tts import Synthesize
from wyoming.client import AsyncTcpClient

async def main():
    if len(sys.argv) != 3:
        print("Usage: poetry run python test_tts_client.py 'text to speak' output.wav")
        sys.exit(1)

    text = sys.argv[1]
    wav_path = Path(sys.argv[2])

    print(f"Connecting to Wyoming server at localhost:10200...")
    async with AsyncTcpClient('localhost', 10200) as client:
        print(f"Sending text to synthesize: {text}")

        # Request synthesis
        await client.write_event(
            Synthesize(
                text=text,
                voice=None,  # Use default voice
            ).event()
        )

        # Prepare WAV file
        wav_file = None

        # Process response
        while True:
            event = await client.read_event()
            if event is None:
                break

            if AudioStart.is_type(event.type):
                # First audio chunk incoming, create WAV file
                audio_start = AudioStart.from_event(event)
                wav_file = wave.open(str(wav_path), 'wb')
                wav_file.setnchannels(audio_start.channels)
                wav_file.setsampwidth(audio_start.width)
                wav_file.setframerate(audio_start.rate)
                print(f"Creating WAV file: {wav_path}")
                print(f"Format: {audio_start.rate}Hz, {audio_start.width*8}bit, {audio_start.channels} channels")

            elif AudioChunk.is_type(event.type):
                # Write audio chunk to WAV file
                chunk = AudioChunk.from_event(event)
                if wav_file:
                    wav_file.writeframes(chunk.audio)

            elif AudioStop.is_type(event.type):
                # Close WAV file
                if wav_file:
                    wav_file.close()
                break

        print(f"Saved audio to: {wav_path}")

if __name__ == "__main__":
    asyncio.run(main())
