# Banking Knowledge RAG Assistant

A production-style Retrieval-Augmented Generation assistant for banking and fintech knowledge documents.

The assistant is designed to answer questions using retrieved document context. If the documents do not contain enough information, the assistant should say so instead of inventing unsupported details.

## Goal

This project demonstrates a clean RAG application architecture using:

- document loading
- heading-aware chunking
- local embeddings with Sentence Transformers
- Chroma vector storage
- semantic retrieval
- source-grounded prompt generation
- Gemini answer generation
- no-answer handling
- retrieval evaluation
- tests and deployment polish

## Why This Project Matters

RAG systems are useful when an LLM needs access to private, updated, or domain-specific knowledge.

Instead of relying only on the model's training data, this project builds a searchable banking knowledge base. User questions are matched against stored document chunks, and the most relevant chunks are later used as grounded context for answer generation.

This is especially important in banking and fintech because answers should be traceable, cautious, and based on source material.

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
Prompt Builder
↓
LLM Client
↓
Grounded Answer with Sources
```

## Current Project Structure

```text
banking-knowledge-rag-assistant/
  data/
    raw_docs/
      card_disputes.md
      digital_payments.md
      mobile_app_access.md
    chroma_db/

  evaluation/

  src/
    banking_rag/
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

      runners/
        run_index.py
        run_query.py
        run_eval.py

  tests/
  README.md
  requirements.txt
  pytest.ini
  pyrightconfig.json
  .env.example
  .gitignore
```

## Core Components

### `core/`

Contains shared project configuration, schemas, and custom exceptions.

- `config.py` stores project paths, model names, Chroma settings, and environment variables.
- `schemas.py` defines shared Pydantic models such as `RawDocument` and `DocumentChunk`.
- `exceptions.py` defines custom errors for clearer debugging.

### `ingestion/`

Handles the document preparation stage.

- `document_loader.py` loads markdown documents from `data/raw_docs/`.
- `chunker.py` splits documents into clean, heading-aware chunks.
- `indexer.py` builds the searchable knowledge base by loading, chunking, embedding, and storing chunks.

### `retrieval/`

Handles embeddings and vector storage.

- `embedding_model.py` wraps a local Sentence Transformers model.
- `vector_store.py` wraps Chroma operations for adding, querying, and counting chunks.
- `retriever.py` will handle user-question retrieval in the next phase.

### `generation/`

Reserved for grounded prompt building and LLM answer generation.

### `services/`

Reserved for orchestration logic that combines retrieval and generation.

### `runners/`

Contains command-line entry points for indexing, querying, and evaluation.

## Tech Stack

- Python
- Chroma
- Sentence Transformers
- Google Gemini
- Python-dotenv
- Pydantic
- Pytest

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
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The `.env` file is ignored by Git and should not be committed.

## Raw Documents

Sample banking knowledge documents are stored in:

```text
data/raw_docs/
```

Current sample documents:

- `digital_payments.md`
- `mobile_app_access.md`
- `card_disputes.md`

These documents are intentionally small and controlled so the RAG pipeline can be tested clearly before expanding to larger or messier documents.

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

The generated Chroma database is stored locally in:

```text
data/chroma_db/
```

This folder is ignored by Git because it can be rebuilt from the raw documents.

## Query the Knowledge Base

After indexing, retrieve relevant chunks for a question:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_query.py --query "What should happen if my QR payment was deducted but the merchant did not receive it?"
```

Example expected top result:
```text
Source: digital_payments.md
Section: QR Payment Disputes
```

## Check Chroma Count

After indexing, confirm that chunks were stored:

```bash
PYTHONPATH=src python -c "from banking_rag.core.config import CHROMA_DIR, COLLECTION_NAME; from banking_rag.retrieval.vector_store import ChromaVectorStore; store=ChromaVectorStore(CHROMA_DIR, COLLECTION_NAME); print('Chroma count:', store.count())"
```

Expected output:

```text
Chroma count: 9
```

## Tests

Run the test suite:

```bash
pytest
```

The current tests cover:

- markdown document loading
- empty document handling
- missing document directory handling
- heading-aware chunking
- source and section metadata preservation
- Chroma vector storage
- Chroma querying
- indexing from sample documents

## Current Status

Phase 3 complete:

- Clean project structure created
- Core configuration added
- Shared Pydantic schemas added
- Custom exceptions added
- Markdown document loader implemented
- Heading-aware chunker implemented
- Sample banking knowledge documents added
- Local Sentence Transformers embedding wrapper added
- Chroma vector store wrapper added
- Knowledge base indexer added
- Index runner added
- Retrieved chunk schema added
- Retrieval service added
- Query runner added
- Unit tests added for loading, chunking, vector storage, indexing, and retrieval
- Chroma index builds successfully with 9 chunks
