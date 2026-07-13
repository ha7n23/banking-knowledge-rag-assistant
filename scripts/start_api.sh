#!/usr/bin/env bash
set -e

echo "Building Chroma knowledge base..."
python -m banking_rag.runners.run_index

echo "Starting FastAPI server..."
uvicorn banking_rag.api.app:app --host 0.0.0.0 --port 8000