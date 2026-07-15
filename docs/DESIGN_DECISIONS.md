# Design Decisions

## 1. Markdown Documents First

This project starts with markdown documents instead of PDFs.

Reason:

- markdown is easier to parse reliably
- headings are explicit
- chunking behaviour is easier to inspect
- the RAG pipeline can be tested clearly before adding messy document formats

Future versions can add PDF ingestion.

## 2. Heading-Aware Chunking

The project uses heading-aware chunking instead of only splitting by fixed character count.

Reason:

- banking knowledge is usually structured by topic
- headings provide useful metadata
- chunks stay more meaningful
- retrieved results are easier to cite

Example section metadata:

```text
digital_payments.md / QR Payment Disputes
```

## 3. Local Sentence Transformers Embeddings

The project uses local embeddings through Sentence Transformers.

Reason:

- no embedding API cost
- works offline after model download
- suitable for portfolio and local development
- keeps the retrieval pipeline provider-independent

The model is lazy-loaded so imports and unit tests do not immediately load PyTorch.

## 4. Chroma Vector Store

Chroma is used as the local vector store.

Reason:

- simple local persistence
- good for prototyping and portfolio projects
- metadata support
- easy to rebuild from raw documents

The generated Chroma database is ignored by Git because it can be rebuilt.

## 5. Retrieval and Generation Are Separate

The project separates retrieval from generation.

Reason:

- retrieval can be tested independently
- weak retrieval can be debugged before blaming the LLM
- `/retrieve` endpoint exposes evidence directly
- `/answer` endpoint runs the full RAG pipeline

## 6. Grounded Prompt Rules

The prompt tells the LLM to:

- use only provided context
- avoid outside knowledge
- avoid inventing timelines, fees, limits, guarantees, or policy details
- say when the documents do not contain enough information
- cite sources used

This is important for banking and fintech scenarios where unsupported claims can be risky.

## 7. Gemini for Answer Generation

Gemini is used for grounded answer generation.

Reason:

- accessible API
- suitable for portfolio demonstration
- easy to swap later because the project uses a text generation protocol

Future versions could add provider switching for Gemini, Groq, Mistral, or OpenAI-compatible APIs.

## 8. Fake Clients in Tests

Tests use fake retrievers and fake LLM clients.

Reason:

- no live API calls in tests
- no API keys needed in CI
- tests are deterministic
- tests run faster

## 9. Docker Runtime

Docker is used to provide a consistent runtime.

Reason:

- avoids local environment issues
- makes the app easier to run on another machine
- prepares the project for deployment
- builds the Chroma index at startup

This is especially useful on Windows machines where local PyTorch DLLs may be blocked by security policies.

## 10. GitHub Actions CI

The project uses GitHub Actions to run:

```text
pytest
docker build
```

Reason:

- validates the code on every push
- catches broken tests
- checks the Docker image still builds
- improves portfolio credibility


## Metadata Filtering

The project adds document-level metadata during ingestion, including:

- document type
- product
- channel
- authority

This allows retrieval to be restricted to a relevant subset of the knowledge base.

For example, card-related questions can be filtered to card documents, while mobile app access questions can be filtered to mobile app documents.

Metadata filtering is useful in banking because policies and procedures often differ by product, channel, region, customer type, and document authority.

## Conservative Automatic Metadata Filtering

The project includes a small deterministic metadata filter router.

It only applies a filter when the query clearly points to a product area such as mobile app access, cards, or digital payments.

If the query is unclear, no metadata filter is applied.

This avoids over-filtering, which can cause the retriever to miss the correct answer.

## Hybrid Retrieval

The project includes a simple hybrid retriever that combines semantic retrieval with keyword scoring.

Semantic retrieval is useful for meaning-based queries.

Keyword scoring is useful for exact identifiers such as:

- policy codes
- error codes
- transaction reference patterns
- product names
- acronyms

The hybrid score combines semantic rank and keyword score so that exact matches can influence the final retrieval ranking.

## Reranking

The project includes a lightweight reranking stage after candidate retrieval.

The reranker combines:

- original retrieval rank
- keyword overlap with the chunk text
- keyword overlap with the source and section metadata

This demonstrates the two-stage retrieval pattern used in many production RAG systems.

In production, this layer could be replaced with a neural cross-encoder reranker or a managed reranking API.

## Query Rewriting

The project includes conservative query rewriting for messy user queries.

The rewriter only changes the query when the intent is obvious, such as:

- QR payment deducted but merchant did not receive confirmation
- mobile app password recovery
- duplicate card charge

If the query is unclear, the original query is preserved.

This reduces the risk of changing the user's meaning while still improving retrieval for informal or incomplete user questions.