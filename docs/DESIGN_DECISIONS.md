# Design Decisions

## 1. Banking Support RAG Use Case

The project uses a banking support knowledge base because banking answers need to be cautious, traceable, and grounded.

The assistant should not invent refund timelines, fees, limits, eligibility rules, guarantees, or policy details.

This makes the project a good fit for demonstrating RAG, source citations, no-answer behaviour, evaluation, and safety controls.

---

## 2. Markdown-First Knowledge Base

The project starts with Markdown documents because they are easy to parse and inspect.

Reasons:

- headings are explicit
- chunking behaviour is easy to understand
- source sections are easy to cite
- the retrieval pipeline can be tested clearly before dealing with messy document formats

The project also supports basic PDF ingestion, but Markdown remains the clearest format for the small demo knowledge base.

---

## 3. Basic PDF Ingestion

PDF ingestion is intentionally simple and transparent.

PDFs are loaded page by page, cleaned, and converted into markdown-like sections:

```text
# policy.pdf

## Page 1
Extracted page text...

## Page 2
Extracted page text...
```

This preserves page-level traceability while keeping the ingestion flow compatible with the existing heading-aware chunker.

Real production PDFs may need more robust table extraction, OCR, layout parsing, and document-quality checks.

---

## 4. Heading-Aware Chunking

The project uses heading-aware chunking instead of only splitting by fixed character count.

Reasons:

- banking knowledge is usually structured by topic
- headings provide useful metadata
- chunks stay more meaningful
- retrieved results are easier to cite

Example section metadata:

```text
digital_payments.md / QR Payment Disputes
```

---

## 5. Local Sentence Transformers Embeddings

The project uses local embeddings through Sentence Transformers.

Reasons:

- no embedding API cost
- works offline after model download
- suitable for portfolio and local development
- keeps retrieval provider-independent

The embedding model is lazy-loaded so imports and unit tests do not immediately load PyTorch.

---

## 6. Chroma Vector Store

Chroma is used as the local vector store.

Reasons:

- simple local persistence
- metadata support
- easy to rebuild from raw documents
- appropriate for a local portfolio project

The generated Chroma database is ignored by Git because it can be rebuilt from the raw knowledge documents.

---

## 7. Retrieval and Generation Are Separate

Retrieval and generation are separated deliberately.

Reasons:

- retrieval can be tested independently
- weak retrieval can be debugged before blaming the LLM
- `/retrieve` exposes evidence directly
- `/answer` runs the full RAG pipeline
- evaluation can target retrieval and answers separately

This separation makes the project easier to test, explain, and extend.

---

## 8. Metadata Filtering

The project adds document-level metadata during ingestion, including:

- document type
- product
- channel
- authority

This allows retrieval to be restricted to a relevant subset of the knowledge base.

Metadata filtering is useful in banking because policies and procedures often differ by product, channel, region, customer type, and document authority.

---

## 9. Conservative Automatic Metadata Filtering

The project includes a small deterministic metadata filter router.

It only applies a filter when the query clearly points to a product area such as mobile app access, cards, or digital payments.

If the query is unclear, no metadata filter is applied.

This avoids over-filtering, which can cause the retriever to miss the correct answer.

---

## 10. Hybrid Retrieval

The project includes hybrid retrieval that combines semantic retrieval with keyword scoring.

Semantic retrieval is useful for meaning-based queries.

Keyword scoring is useful for exact identifiers such as:

- policy codes
- error codes
- transaction reference patterns
- product names
- acronyms

The hybrid score combines semantic and keyword signals so exact matches can influence final ranking.

---

## 11. Lightweight Reranking

The project includes a lightweight reranking stage after candidate retrieval.

The reranker combines:

- original retrieval rank
- keyword overlap with the chunk text
- keyword overlap with the source and section metadata

This demonstrates the two-stage retrieval pattern used in many production RAG systems.

In production, this layer could be replaced with a neural cross-encoder reranker or a managed reranking API.

---

## 12. Conservative Query Rewriting

The project includes conservative query rewriting for messy user queries.

The rewriter only changes the query when the intent is obvious, such as:

- QR payment deducted but merchant did not receive confirmation
- mobile app password recovery
- duplicate card charge

If the query is unclear, the original query is preserved.

This reduces the risk of changing the user's meaning while still improving retrieval for informal or incomplete user questions.

---

## 13. Reusable Retrieval Pipeline

Advanced retrieval logic is implemented in a reusable retrieval pipeline instead of being embedded directly in one script.

The same retrieval pipeline can be used by:

- CLI runners
- FastAPI endpoints
- the RAG answer service
- evaluation scripts

This is closer to production-style application design than keeping retrieval orchestration inside a one-off runner.

---

## 14. Grounded Prompt Rules

The prompt tells the LLM to:

- use only provided context
- avoid outside knowledge
- avoid inventing timelines, fees, limits, guarantees, or policy details
- say when the documents do not contain enough information
- cite sources used

This is important for banking and fintech scenarios where unsupported claims can be risky.

---

## 15. Prompt-Injection Safety Rules

Retrieved documents are treated as untrusted reference material, not instructions.

The model is explicitly told not to follow instructions inside retrieved documents, including instructions to ignore rules, reveal prompts, change roles, fabricate details, or use outside knowledge.

This matters because RAG systems can retrieve malicious or poorly controlled text.

---

## 16. Gemini for Answer Generation

Gemini is used for grounded answer generation.

Reasons:

- accessible API for development
- suitable for portfolio demonstration
- easy to swap later because generation is isolated behind a client/service layer

Future versions could support multiple providers such as Gemini, Groq, Mistral, or OpenAI-compatible APIs.

---

## 17. Citation Validation

Generated citations are treated as model output that needs validation.

The citation validator checks whether citations such as `[Source 1]` or `[1]` refer to retrieved source numbers that actually exist.

This catches cases where the model invents invalid citations.

---

## 18. Answer Evaluation and Quality Gates

The project evaluates generated answers for grounding, citation validity, no-answer behaviour, and forbidden unsupported claims.

The answer evaluation runner supports a minimum pass-rate quality gate.

This makes the evaluation suitable for CI because the runner can fail with a non-zero exit code when quality drops below the threshold.

---

## 19. Offline Mock Evaluation Mode

The project includes deterministic mock answers for offline answer evaluation.

Reasons:

- no live API calls in CI
- no API keys needed for evaluation checks
- avoids Gemini quota issues
- deterministic behaviour
- faster and safer automated checks

Live evaluation is still useful for checking real model behaviour, but offline evaluation is better for repeatable CI quality gates.

---

## 20. Evaluation Reports

Answer evaluation writes JSON and Markdown reports.

Reasons:

- JSON is machine-readable for regression tracking
- Markdown is human-readable for review and portfolio discussion
- timestamped reports make it easier to compare quality over time
- latest reports are convenient for quick checks

CI uploads the latest reports as workflow artifacts.

---

## 21. Lightweight FastAPI Web UI

The project includes a simple FastAPI-served browser UI instead of adding React immediately.

Reasons:

- no Node.js setup
- no separate frontend server
- no Docker Compose needed
- easier to maintain inside the current project
- better for demos than Swagger-only testing

A full React frontend is a good future improvement, especially for a larger capstone project.

---

## 22. Docker Runtime

Docker is used to provide a consistent runtime.

Reasons:

- avoids local environment issues
- makes the app easier to run on another machine
- prepares the project for deployment
- builds the Chroma index at startup
- helps avoid Windows-specific PyTorch DLL restrictions

The Docker build uses Docker-specific requirements and BuildKit cache support to reduce repeated dependency installation time.

---

## 23. GitHub Actions CI

GitHub Actions runs:

```text
pytest
offline RAG answer evaluation quality gate
upload evaluation reports
Docker build
```

Reasons:

- validates code on every push
- catches broken tests
- checks evaluation logic and quality gates
- preserves evaluation reports from CI
- checks the Docker image still builds
- improves portfolio credibility
