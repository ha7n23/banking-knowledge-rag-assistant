# API Examples

The API is built with FastAPI and can be used through the browser UI, Swagger docs, or direct HTTP requests.

Start locally:

```bash
PYTHONPATH=src python -m uvicorn banking_rag.api.app:app --reload
```

Or run through Docker:

```bash
docker run --rm --env-file .env -p 8000:8000 banking-knowledge-rag-assistant
```

Open the browser UI:

```text
http://127.0.0.1:8000/
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

---

## Health Check

### Request

```bash
curl http://127.0.0.1:8000/health
```

### Example Response

```json
{
  "status": "ok",
  "app_name": "Banking Knowledge RAG Assistant",
  "environment": "development"
}
```

---

## Retrieve Evidence Chunks

The `/retrieve` endpoint retrieves relevant chunks. It does not generate a final LLM answer.

This is useful for debugging retrieval quality before testing generation.

### Basic Request

```bash
curl -X POST "http://127.0.0.1:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What should happen if my QR payment was deducted but the merchant did not receive it?",
    "top_k": 3
  }'
```

### Example Response Shape

```json
{
  "query": "What should happen if my QR payment was deducted but the merchant did not receive it?",
  "chunks": [
    {
      "text": "Relevant retrieved text appears here.",
      "source": "digital_payments.md",
      "section": "QR Payment Disputes",
      "chunk_index": 0,
      "distance": 0.463
    }
  ]
}
```

---

## Generate a Grounded Answer

The `/answer` endpoint runs the full RAG pipeline:

```text
query
        ↓
optional query rewriting
        ↓
optional metadata filtering
        ↓
retrieval
        ↓
optional reranking
        ↓
grounded prompt
        ↓
Gemini
        ↓
answer with sources and traceability
```

### Recommended Advanced Request

```bash
curl -X POST "http://127.0.0.1:8000/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "money gone shop says no",
    "top_k": 3,
    "retrieval_mode": "hybrid",
    "auto_filter": true,
    "rewrite_query": true,
    "rerank": true,
    "candidate_k": 6
  }'
```

### Example Response Shape

```json
{
  "question": "money gone shop says no",
  "answer": "If a QR payment is deducted from a customer's account but the merchant does not receive the funds... Source: [Source 1] digital_payments.md, QR Payment Disputes.",
  "sources": [
    {
      "source": "digital_payments.md",
      "section": "QR Payment Disputes",
      "chunk_index": 0,
      "distance": 0.685,
      "file_type": "markdown",
      "page_number": null
    }
  ],
  "retrieved_chunks": [
    {
      "text": "Relevant retrieved text appears here.",
      "source": "digital_payments.md",
      "section": "QR Payment Disputes",
      "chunk_index": 0,
      "distance": 0.685
    }
  ],
  "retrieval_query": "QR payment deducted from customer account but merchant did not receive payment confirmation",
  "metadata_filter": {
    "product": "digital_payments"
  },
  "retrieval_mode": "hybrid",
  "rerank_enabled": true,
  "query_was_rewritten": true,
  "rewrite_reason": "Detected likely QR payment deducted but merchant not received issue."
}
```

---

## No-Answer Behaviour

Question:

```text
What is the exact refund timeline for a failed QR payment?
```

Expected behaviour:

```text
The assistant should say the provided documents do not contain enough information to specify an exact refund timeline.
```

It should not invent a timeline such as 24 hours, 3 working days, or 7 days unless that information exists in the retrieved context.

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the exact refund timeline for a failed QR payment?",
    "top_k": 3,
    "retrieval_mode": "hybrid",
    "auto_filter": true,
    "rewrite_query": true,
    "rerank": true,
    "candidate_k": 6
  }'
```

---

## Other Example Questions

```text
I forgot my mobile banking password. How can I get back in?
```

Expected behaviour:

- mention the forgot password option
- mention registered mobile number verification
- cite the relevant source section

```text
My debit card payment was charged twice at the same shop.
```

Expected behaviour:

- explain that duplicate card transactions can be reported
- mention review using transaction logs, merchant records, and settlement information
- cite the relevant source section

---

## Request Field Notes

`query` is the user question.

`top_k` controls how many final chunks are returned.

`retrieval_mode` can be:

```text
semantic
hybrid
```

`auto_filter` enables deterministic metadata filter inference.

`rewrite_query` enables conservative query rewriting for clear messy queries.

`rerank` enables the lightweight reranker.

`candidate_k` controls how many candidate chunks are retrieved before reranking.
