FROM python:3.12-bullseye

WORKDIR /app

ENV POETRY_VERSION=1.8.4 \
    POETRY_NO_INTERACTION=1 \
    PIP_VERSION=24.3.1 \
    PIP_DISABLE_PIP_VERSION_CHECK=true \
    PIP_DEFAULT_TIMEOUT=60

COPY pyproject.toml poetry.lock /app/
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends libpq-dev && \
    pip install --no-cache-dir --upgrade pip==${PIP_VERSION} && \
    pip install --no-cache-dir poetry==${POETRY_VERSION} && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . /app