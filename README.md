# Wyoming OpenAI TTS
Wyoming protocol server for OpenAI text-to-speech.

This Python package provides a Wyoming integration for OpenAI text-to-speech and can be directly used with [Home Assistant](https://www.home-assistant.io/) voice and [Rhasspy](https://github.com/rhasspy/rhasspy3).

## OpenAI API
This program uses OpenAI's text-to-speech API. You will need an OpenAI API key to use this service. OpenAI charges per character for TTS usage. Please check their [pricing page](https://openai.com/pricing) for current rates.

## Installation
1. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com)
2. Install the package using Poetry:
  ```sh
  poetry install
  ```

- **Home Assistant Add-On**
  Add the following repository as an add-on repository to your Home Assistant, or click the button below.
  [https://github.com/m0rdras/wyoming-openai-tts](https://github.com/m0rdras/wyoming-openai-tts)

  [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fhugobloem%2Fhomeassistant-addons)

- **Docker container**
  To run as a Docker container use the following command:
  ```bash
  docker run ghcr.io/m0rdras/wyoming-openai-tts-noha:latest --<key> <value>
  ```
  For the relevant keys please look at [the table below](#usage)

## Usage
Depending on the installation method parameters are parsed differently. However, the same options are used for each of the installation methods and can be found in the table below. Your service region and subscription key can be found on the speech service resource page (step 5 the Azure Speech service instructions).

For the bare-metal Python install the program is run as follows:
```python
python -m wyoming-openai-tts --<key> <value>
```

| Key | Optional | Description |
|---|---|---|
| `api-key` | No | OpenAI API key |
| `uri` | No | Uri where the server will be broadcasted e.g., `tcp://0.0.0.0:10200` |
| `download-dir` | Yes | Directory to download voices.json into (default: /tmp/) |
| `voice` | Yes | Default voice to set for transcription (default: `alloy`) |
| `auto-punctuation` | Yes | Automatically add punctuation (default: `".?!"`) |
| `samples-per-chunk` | Yes | Number of samples per audio chunk (default: 1024) |
