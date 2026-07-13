FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/raw_docs/ ./data/raw_docs/
COPY evaluation/ ./evaluation/
COPY scripts/ ./scripts/

RUN chmod +x scripts/start_api.sh

EXPOSE 8000

CMD ["scripts/start_api.sh"]