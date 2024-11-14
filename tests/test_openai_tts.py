"""Tests for the OpenAITTS class."""

def test_initialize(openai_tts, configuration):
    """Test initialization."""
    assert openai_tts.args.voice == configuration["voice"]
    assert openai_tts.client is not None
    assert openai_tts.output_dir is not None

def test_synthesize(openai_tts):
    """Test synthesize."""
    text = "Hello, world!"
    voice = "alloy"

    result = openai_tts.synthesize(text, voice)
    assert result.endswith(".wav")