#!/bin/bash

# Default values
DEFAULT_VOICE="alloy"
DEFAULT_PORT=10200
DEFAULT_HOST="0.0.0.0"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running in HASSIO
if command -v bashio &> /dev/null; then
    log "Running in Home Assistant environment"
    API_KEY="$(bashio::config 'api_key')"
    VOICE="$(bashio::config 'voice' $DEFAULT_VOICE)"
else
    log "Running in standalone environment"
    # Check for required API key
    if [ -z "$OPENAI_API_KEY" ]; then
        log "Error: OPENAI_API_KEY environment variable is required"
        exit 1
    fi
    API_KEY="$OPENAI_API_KEY"
    VOICE="${VOICE:-$DEFAULT_VOICE}"
fi

# Construct the command
CMD="python -m wyoming_openai_tts \
    --api-key \"${API_KEY}\" \
    --voice \"${VOICE}\" \
    --uri tcp://${DEFAULT_HOST}:${DEFAULT_PORT}"

# Add debug if enabled
if [ "${DEBUG}" = "true" ]; then
    CMD="${CMD} --debug"
fi

log "Starting Wyoming OpenAI TTS server..."
log "Voice: ${VOICE}"
log "Port: ${DEFAULT_PORT}"

# Execute the command
exec $CMD 