# API Examples

The API is built with FastAPI.

Start the server locally:

```bash
PYTHONPATH=src uvicorn banking_rag.api.app:app --reload
```

Or run through Docker:

```bash
docker run --rm --env-file .env -p 8000:8000 banking-knowledge-rag-assistant
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

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

## Retrieve Evidence Chunks

The `/retrieve` endpoint only retrieves relevant chunks. It does not generate a final LLM answer.

### Request

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

## Generate Grounded Answer

The `/answer` endpoint runs the full RAG pipeline.

```text
query → retrieval → grounded prompt → Gemini → answer with sources
```

### Request

```bash
curl -X POST "http://127.0.0.1:8000/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the exact refund timeline for a failed QR payment?",
    "top_k": 3
  }'
```

### Expected Behaviour

If the documents do not contain the exact refund timeline, the assistant should say that the provided documents do not contain enough information.

It should not invent a timeline such as 24 hours, 3 working days, or 7 days unless that information exists in the retrieved context.

### Example Response Shape

```json
{
  "question": "What is the exact refund timeline for a failed QR payment?",
  "answer": "The provided documents do not contain enough information regarding the exact refund timeline for a failed QR payment...",
  "sources": [
    {
      "source": "digital_payments.md",
      "section": "QR Payment Disputes",
      "chunk_index": 0,
      "distance": 0.463
    }
  ],
  "retrieved_chunks": [
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

## Example Supported Question

```bash
curl -X POST "http://127.0.0.1:8000/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I forgot my mobile banking password. How can I get back in?",
    "top_k": 3
  }'
```

Expected behaviour:

- mention the forgot password option
- mention registered mobile number verification
- cite the relevant source section