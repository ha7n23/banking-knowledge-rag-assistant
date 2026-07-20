# Evaluation

## Why Evaluation Matters

A RAG system can fail in multiple ways:

```text
retrieval finds the wrong context
        ↓
LLM receives weak evidence
        ↓
answer becomes incomplete or unsupported
```

It can also fail even when retrieval is correct:

```text
retrieval finds the right context
        ↓
LLM adds unsupported detail
        ↓
answer becomes risky
```

This project evaluates retrieval and generated answers separately so each failure mode can be debugged clearly.

---

## Evaluation Files

Evaluation data is stored in:

```text
evaluation/evaluation_questions.json
evaluation/advanced_retrieval_questions.json
```

Evaluation reports are written to:

```text
evaluation/reports/
```

---

## Basic Retrieval Evaluation

Basic retrieval evaluation checks whether the expected source and section are returned for each question.

Example evaluation item:

```json
{
  "question": "I forgot my mobile banking password. How can I get back in?",
  "expected_top_source": "mobile_app_access.md",
  "expected_top_section": "Password Recovery",
  "expected_answer_type": "direct_answer",
  "expected_behavior": "Mention the forgot password option and registered mobile number verification.",
  "must_not_include": []
}
```

Run basic retrieval evaluation:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_eval
```

Expected result shape:

```text
Passed: 4
Failed: 0
Total: 4
```

---

## Advanced Retrieval Evaluation

Advanced retrieval evaluation tests the stronger retrieval pipeline with messy queries, exact identifiers, metadata filtering, hybrid search, and reranking.

Run baseline semantic retrieval:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_advanced_eval --retrieval-mode semantic
```

Run the full advanced retrieval pipeline:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_advanced_eval --retrieval-mode hybrid --auto-filter --rewrite-query --rerank --candidate-k 6
```

The advanced retrieval pipeline can include:

```text
query rewriting
metadata filter inference
hybrid semantic/keyword retrieval
reranking
```

---

## Retrieval Metrics

The retrieval evaluation tracks:

- top-1 success
- top-k success
- expected source
- expected section
- failed top-k cases

Top-1 success means the expected source and section were the first retrieved result.

Top-k success means the expected source and section appeared anywhere in the retrieved context.

This distinction matters because a RAG answer may still work if the correct evidence appears in the retrieved context, even if it is not ranked first. However, weaker ranking can add noise and reduce answer quality.

---

## Generated Answer Evaluation

Generated answer evaluation checks the final answer produced by the RAG system.

This matters because retrieval can succeed while generation still fails by adding unsupported details.

The answer evaluator checks:

- whether sources are present
- whether citations reference valid source numbers
- whether no-answer questions include insufficient-information language
- whether unsupported forbidden phrases appear
- whether the answer satisfies the expected answer type and behaviour

Run live answer evaluation:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_answer_eval --top-k 3 --retrieval-mode hybrid --auto-filter --rewrite-query --rerank --candidate-k 6 --min-pass-rate 1.0
```

This calls the live Gemini model, so it requires a valid API key and available quota.

---

## No-Answer Evaluation

The evaluation set includes questions where the answer should not be invented.

Example:

```text
What is the exact refund timeline for a failed QR payment?
```

Expected behaviour:

```text
The assistant should say the provided documents do not contain enough information to specify an exact refund timeline.
```

The evaluator checks that unsupported phrases such as invented timelines do not appear when the knowledge base does not contain them.

---

## Citation Validation

The project validates generated citations.

The validator checks whether citations such as:

```text
[Source 1]
[1]
```

refer to retrieved source numbers that actually exist.

This helps catch cases where the LLM invents a citation such as `[Source 9]` when only three retrieved sources were available.

---

## Offline Evaluation Mode

The answer evaluation runner supports deterministic mock answers.

Run offline evaluation:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_answer_eval --mock-answers --min-pass-rate 1.0
```

Offline evaluation is useful because it tests:

- answer evaluation logic
- citation validation
- report writing
- quality gates
- CI behaviour

without calling Gemini.

Live evaluation is still useful for checking real model behaviour. Offline evaluation is better for repeatable CI checks.

---

## Quality Gates

The answer evaluation runner supports a minimum pass-rate quality gate.

Example:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_answer_eval --mock-answers --min-pass-rate 1.0
```

A `--min-pass-rate` of `1.0` requires all evaluation questions to pass.

A lower threshold such as `0.9` can be used as the evaluation set grows.

The runner exits with a non-zero status code if the pass rate is below the configured threshold. This makes the evaluation suitable for CI/CD.

---

## Evaluation Reports

Answer evaluation writes JSON and Markdown reports.

Latest reports:

```text
evaluation/reports/answer_eval_latest.json
evaluation/reports/answer_eval_latest.md
```

Timestamped regression reports:

```text
evaluation/reports/answer_eval_YYYYMMDD_HHMMSS.json
evaluation/reports/answer_eval_YYYYMMDD_HHMMSS.md
```

The JSON report is useful for machine-readable regression tracking.

The Markdown report is useful for human review, GitHub documentation, portfolio review, and interview discussion.

To skip timestamped reports during CI or quick local checks:

```bash
PYTHONPATH=src python -m banking_rag.runners.run_answer_eval --mock-answers --min-pass-rate 1.0 --skip-timestamped-report
```

---

## CI Evaluation

GitHub Actions runs offline answer evaluation as part of CI.

The CI flow is:

```text
run pytest
        ↓
run offline RAG answer evaluation quality gate
        ↓
upload latest evaluation reports as workflow artifacts
        ↓
build Docker image
```

CI uses mock answers so automated checks do not depend on Gemini quota, API keys, external LLM availability, or model randomness.

---

## Current Evaluation Questions

The current evaluation set covers:

- QR payment deducted but merchant did not receive it
- exact refund timeline not present in documents
- mobile banking password recovery
- duplicate debit card charge

---

## Future Evaluation Improvements

Possible future improvements:

- larger evaluation dataset
- more difficult no-answer cases
- more adversarial prompt-injection cases
- human review workflow
- LLM-as-judge checks alongside deterministic checks
- dashboard for evaluation history
- production monitoring and feedback loops
