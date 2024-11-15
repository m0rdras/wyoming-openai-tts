from wyoming_openai_tts.openai_tts import OpenAITTS
from types import SimpleNamespace
import os
from pathlib import Path

# Create output directory
output_dir = Path("./test_output")
output_dir.mkdir(exist_ok=True)

# Create test configuration
args = SimpleNamespace(
    api_key=os.environ.get("OPENAI_API_KEY"),  # Make sure to set this env variable
    voice="alloy",
    output_dir=output_dir,
)

# Initialize TTS
tts = OpenAITTS(args)

# Test synthesis
output_file = tts.synthesize("Hello, this is a test of OpenAI text to speech!")
print(f"Audio saved to: {output_file}")
