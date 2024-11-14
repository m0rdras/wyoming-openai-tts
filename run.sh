#!/usr/bin/with-contenv bashio

set -e

bashio::log.info "Loading parameters"
API_KEY="$(bashio::config 'api_key')"

bashio::log.info "API Key configured: ${API_KEY}"

python3 ./__main__.py --uri "tcp://0.0.0.0:12200" --api-key "${API_KEY}" --download-dir /data
