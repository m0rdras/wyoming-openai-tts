FROM python:3.12-slim-bullseye

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /root/.local/bin/poetry

# Install the Python package
COPY . /app
WORKDIR /app
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 10200

ENTRYPOINT [ "python", "-m", "wyoming_openai_tts"]