# Build stage
FROM python:3.13-slim AS builder

# Install build dependencies and update pip
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.4

# Update pip and install poetry and build in a single layer
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "poetry==$POETRY_VERSION" build

# Copy only dependency files first to leverage Docker cache
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Copy the rest of the application and build wheel
COPY . .
RUN poetry build --format wheel \
    && pip wheel --no-deps --no-index --wheel-dir /wheels dist/*.whl

# Runtime stage
FROM python:3.13-slim AS runtime

# Update pip in runtime image
RUN pip install --no-cache-dir --upgrade pip

# Copy wheel and install it with root user action specified
COPY --from=builder /wheels/*.whl /tmp/
RUN pip install --no-cache-dir --root-user-action=ignore /tmp/*.whl && rm /tmp/*.whl

EXPOSE 10200

# Use array form of ENTRYPOINT for better signal handling
ENTRYPOINT ["python", "-m", "wyoming_openai_tts"]