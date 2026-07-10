# Banking Knowledge RAG Assistant

A production-style Retrieval-Augmented Generation assistant for banking and fintech knowledge documents.

The assistant answers questions using retrieved document context and cites the sources used. If the documents do not contain enough information, it should say so instead of inventing unsupported details.

## Goal

This project demonstrates a clean RAG application architecture:

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

## Architecture

```text
Documents
↓
Ingestion
↓
Chunking
↓
Embeddings
↓
Chroma vector store
↓
Retriever
↓
Prompt builder
↓
LLM client
↓
Grounded answer with sources