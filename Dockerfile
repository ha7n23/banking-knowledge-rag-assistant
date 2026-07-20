# syntax=docker/dockerfile:1.7

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-docker.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip && \
    python -m pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu && \
    python -m pip install -r requirements-docker.txt

COPY src/ ./src/
COPY data/raw_docs/ ./data/raw_docs/
COPY evaluation/ ./evaluation/
COPY scripts/ ./scripts/

RUN chmod +x scripts/start_api.sh

EXPOSE 8000

CMD ["scripts/start_api.sh"]