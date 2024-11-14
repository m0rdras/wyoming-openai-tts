# Build stage
FROM python:3.13-slim as builder

# Install build dependencies
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.7.1

# Install poetry and build dependencies in a single layer
RUN pip install "poetry==$POETRY_VERSION" build

# Copy only dependency files first to leverage Docker cache
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies and build wheel
COPY . .
RUN poetry build --format wheel \
    && pip wheel --no-deps --no-index --wheel-dir /wheels dist/*.whl

# Runtime stage
FROM python:3.13-slim as runtime

# Copy wheel and install it
COPY --from=builder /wheels/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

EXPOSE 10200

# Use array form of ENTRYPOINT for better signal handling
ENTRYPOINT ["python", "-m", "wyoming_openai_tts"]