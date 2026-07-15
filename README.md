# Banking Knowledge RAG Assistant

![CI](https://github.com/ha7n23/banking-knowledge-rag-assistant/actions/workflows/ci.yml/badge.svg)

A production-style Retrieval-Augmented Generation application for answering banking and fintech knowledge questions using source-grounded document context.

The assistant retrieves relevant knowledge chunks from a local Chroma vector database, builds a grounded prompt, and generates an answer using Gemini. If the documents do not contain enough information, the assistant is instructed to say so rather than invent unsupported details.

## Project Summary

This project demonstrates an end-to-end RAG system with:

- markdown document ingestion
- heading-aware chunking
- local Sentence Transformers embeddings
- Chroma vector storage
- semantic retrieval
- grounded prompt construction
- Gemini answer generation
- FastAPI backend
- retrieval evaluation
- unit and API tests
- Docker support
- GitHub Actions CI

The project is designed with a banking/fintech use case, where answers should be cautious, traceable, and based on available source material.

## Why This Project Matters

Large language models do not automatically know private, updated, or organisation-specific documents. RAG solves this by retrieving relevant source material before generation.

This is especially important in banking because the assistant should not invent:

- refund timelines
- fees
- eligibility rules
- transaction limits
- guarantees
- policy details

Instead, the assistant should answer only from retrieved context and clearly say when the available documents are insufficient.

## Architecture

```text
Raw Documents
↓
Document Loader
↓
Heading-Aware Chunker
↓
Embedding Model
↓
Chroma Vector Store
↓
Retriever
↓
Grounded Prompt Builder
↓
Gemini LLM Client
↓
RAG Service
↓
FastAPI API
```

The project separates ingestion, retrieval, generation, services, API routes, and evaluation into clear modules.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Examples](docs/API_EXAMPLES.md)
- [Evaluation](docs/EVALUATION.md)
- [Design Decisions](docs/DESIGN_DECISIONS.md)

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Chroma
- Sentence Transformers
- Google Gemini
- Pydantic
- Pytest
- Docker
- GitHub Actions

## Project Structure

```text
banking-knowledge-rag-assistant/
  data/
    raw_docs/
      card_disputes.md
      digital_payments.md
      mobile_app_access.md
    chroma_db/

  docs/
    ARCHITECTURE.md
    API_EXAMPLES.md
    EVALUATION.md
    DESIGN_DECISIONS.md

  evaluation/
    evaluation_questions.json

  scripts/
    start_api.sh

  src/
    banking_rag/
      api/
        app.py
        dependencies.py
        routes.py
        schemas.py

      core/
        config.py
        exceptions.py
        schemas.py

      ingestion/
        document_loader.py
        chunker.py
        indexer.py

      retrieval/
        embedding_model.py
        vector_store.py
        retriever.py

      generation/
        prompt_builder.py
        llm_client.py

      services/
        rag_service.py
        evaluation_service.py

      runners/
        run_index.py
        run_query.py
        run_answer.py
        run_eval.py

  tests/
  Dockerfile
  requirements.txt
  pytest.ini
  pyrightconfig.json
  .env.example
  .dockerignore
  .gitignore
  README.md
```

## Core Features

### Document Ingestion

Markdown documents are loaded from:

```text
data/raw_docs/
```

The project currently includes sample banking knowledge documents covering:

- digital payments
- mobile app access
- card disputes

### Heading-Aware Chunking

Documents are split by section headings before being stored in Chroma.

This keeps chunks meaningful and easier to cite, for example:

```text
digital_payments.md / QR Payment Disputes
```

### Local Embeddings

The project uses Sentence Transformers for local embeddings.

The embedding model is lazy-loaded so tests can import the codebase without immediately loading PyTorch or Sentence Transformers.

### Chroma Vector Store

Chroma stores:

- chunk text
- embeddings
- source metadata
- section metadata
- chunk index

The generated Chroma database is ignored by Git because it can be rebuilt from raw documents.

### Retrieval

The retriever embeds a user question and searches Chroma for the most relevant chunks.

The `/retrieve` endpoint exposes retrieved evidence directly, which is useful for debugging retrieval quality.

### Grounded Answer Generation

The RAG service combines:

```text
question
↓
retrieved chunks
↓
grounded prompt
↓
Gemini answer
↓
answer with source references
```

The prompt instructs the model to use only provided context and avoid unsupported claims.

### FastAPI Backend

The API exposes:

```text
GET  /health
POST /retrieve
POST /answer
```

### Evaluation

The retrieval evaluation checks whether the expected source and section are returned as the top retrieval result for each evaluation question.

### Docker

Docker provides a consistent runtime. The container builds the Chroma knowledge base at startup before starting the FastAPI server.

### CI

GitHub Actions runs:

```text
pytest
docker build
```

on every push to `main` and every pull request.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```env
APP_NAME=Banking Knowledge RAG Assistant
ENVIRONMENT=development
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The `.env` file is ignored by Git and should not be committed.

## Build the Knowledge Base

Index the raw documents into Chroma:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_index.py
```

Expected output:

```text
Building banking knowledge base...
Indexed 9 chunks into Chroma.
```

Check Chroma count:

```bash
PYTHONPATH=src python -c "from banking_rag.core.config import CHROMA_DIR, COLLECTION_NAME; from banking_rag.retrieval.vector_store import ChromaVectorStore; store=ChromaVectorStore(CHROMA_DIR, COLLECTION_NAME); print('Chroma count:', store.count())"
```

Expected output:

```text
Chroma count: 9
```

## Query the Knowledge Base

Retrieve relevant chunks without generating an LLM answer:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_query.py --query "What should happen if my QR payment was deducted but the merchant did not receive it?"
```

Expected top result:

```text
digital_payments.md / QR Payment Disputes
```

## Generate a Grounded Answer

Run the full RAG pipeline:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_answer.py --query "What is the exact refund timeline for a failed QR payment?"
```

Expected behaviour:

```text
The provided documents do not contain enough information regarding the exact refund timeline...
```

The assistant should not invent a refund timeline unless the retrieved documents contain one.

## Run the API

Start the FastAPI server:

```bash
PYTHONPATH=src uvicorn banking_rag.api.app:app --reload
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

```text
GET  /health
POST /retrieve
POST /answer
```

### Retrieve Evidence Chunks

Example request body for `/retrieve`:

```json
{
  "query": "What should happen if my QR payment was deducted but the merchant did not receive it?",
  "top_k": 3
}
```

### Generate a Grounded Answer

Example request body for `/answer`:

```json
{
  "query": "What is the exact refund timeline for a failed QR payment?",
  "top_k": 3
}
```

## Run Evaluation

Run retrieval evaluation:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_eval.py
```

Expected result:

```text
Passed: 4
Failed: 0
Total: 4
```

The evaluation checks whether retrieval returns the expected top source and section.

## Run Tests

Run the full test suite:

```bash
pytest
```

The tests cover:

- document loading
- chunking
- vector storage
- indexing
- retrieval
- prompt building
- RAG service orchestration
- evaluation service
- FastAPI endpoints

Tests use fake retrievers and fake LLM clients where appropriate, so the test suite does not require live LLM calls.

## Docker

Build the image:

```bash
docker build -t banking-knowledge-rag-assistant .
```

Run the API without passing environment variables:

```bash
docker run --rm -p 8000:8000 banking-knowledge-rag-assistant
```

This supports `/health` and `/retrieve`.

Run with Gemini API key support:

```bash
docker run --rm --env-file .env -p 8000:8000 banking-knowledge-rag-assistant
```

The container startup flow is:

```text
build Chroma knowledge base
↓
start FastAPI server
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Windows Note

This project uses Sentence Transformers, which depends on PyTorch for local embeddings.

On some managed Windows machines, Application Control policies may block PyTorch DLL files. If that happens, run the project through Docker. The Docker container provides a Linux runtime and builds the Chroma knowledge base at startup.

## Continuous Integration

This project uses GitHub Actions.

On every push to `main` and every pull request, CI:

- installs dependencies
- runs the pytest test suite
- builds the Docker image

Workflow file:

```text
.github/workflows/ci.yml
```

## Example Questions

Supported question:

```text
I forgot my mobile banking password. How can I get back in?
```

Expected behaviour:

```text
The assistant should mention the forgot password option and registered mobile number verification.
```

Unsupported detail question:

```text
What is the exact refund timeline for a failed QR payment?
```

Expected behaviour:

```text
The assistant should say the documents do not contain enough information to specify the exact refund timeline.
```

## Current Status

Advanced RAG Phase 4 complete:

- RAG pipeline implemented end-to-end
- Markdown document ingestion added
- Document-level metadata inference added
- Heading-aware chunking added
- Local Sentence Transformers embeddings added
- Chroma vector storage with metadata added
- Semantic retrieval added
- Metadata-filtered retrieval added
- Conservative automatic metadata filter inference added
- Simple keyword scoring added
- Hybrid semantic + keyword retrieval added
- Grounded prompt builder added
- Gemini LLM client added
- RAG service added
- Improved retrieval evaluation added
- Top-1 and top-k retrieval evaluation supported
- No-answer metadata and unsafe phrase checks prepared
- FastAPI backend added
- Docker support added
- GitHub Actions CI added
- Documentation added
- Unit and API tests passing

## Future Improvements

Potential next improvements:

- add PDF ingestion
- add hybrid search
- add reranking
- add answer-level evaluation
- add streaming answers
- add authentication for API endpoints
- add cloud deployment
- add more realistic banking documents
- add provider switching for multiple LLMs

## Metadata-Filtered Retrieval

The query runner supports optional metadata filters:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_query.py --query "I forgot my mobile banking password" --product mobile_app
```

Available sample metadata fields include:
```text
product: digital_payments, mobile_app, cards
channel: qr, mobile_app, card
document_type: policy
```

## Automatic Metadata Filtering

The query runner can infer simple metadata filters from clear user queries:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_query.py --query "I forgot my mobile banking password" --auto-filter
```

Example inferred filters:

```text
password/login/mobile app → product: mobile_app
card/charged twice/lost card → product: cards
QR/merchant did not receive/payment deducted → product: digital_payments
```

The router is intentionally conservative. If the query is unclear, no filter is applied and retrieval searches all chunks.

## Hybrid Retrieval

The query runner supports semantic and hybrid retrieval modes.

Semantic mode:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_query.py --query "What does RAAST-P2M-042 mean?" --retrieval-mode semantic
```

Hybrid Mode:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_query.py --query "What does RAAST-P2M-042 mean?" --retrieval-mode hybrid
```

Hybrid Retrieval combines:

```text
semantic rank + keyword score
```

This is useful for exact identifiers such as policy codes, error codes, product codes, and transaction references.