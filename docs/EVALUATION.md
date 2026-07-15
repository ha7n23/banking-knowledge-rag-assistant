# Evaluation

## Why Evaluation Matters

A RAG system depends heavily on retrieval quality.

If retrieval returns weak or irrelevant chunks, the language model receives poor context and may produce an unsupported or incomplete answer.

This project evaluates retrieval separately from generation.

```text
Bad retrieval → weak context → weak answer
Good retrieval → relevant context → grounded answer
```

## Evaluation Dataset

Evaluation questions are stored in:

```text
evaluation/evaluation_questions.json
```

Each evaluation item contains:

```text
question
expected_top_source
expected_top_section
expected_behavior
```

Example:

```json
{
  "question": "I forgot my mobile banking password. How can I get back in?",
  "expected_top_source": "mobile_app_access.md",
  "expected_top_section": "Password Recovery",
  "expected_behavior": "Mention the forgot password option and registered mobile number verification."
}
```

## What Is Evaluated

The current evaluation checks whether the top retrieved chunk matches the expected:

```text
source
section
```

This is a retrieval-focused evaluation.

It does not currently score the generated answer automatically because LLM wording can vary. Instead, the expected answer behaviour is included for manual review.

## Run Evaluation

First build the index:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_index.py
```

Then run:

```bash
PYTHONPATH=src python src/banking_rag/runners/run_eval.py
```

Expected result:

```text
Passed: 4
Failed: 0
Total: 4
```

## Current Evaluation Questions

The current set covers:

- QR payment deducted but merchant did not receive it
- exact refund timeline not present in documents
- mobile banking password recovery
- duplicate debit card charge

## Why This Is Useful

This evaluation helps catch retrieval regressions.

For example, if a chunking change causes password questions to retrieve the wrong document, the evaluation will fail even if the code still runs.

## Future Improvements

Possible future evaluation improvements:

- check whether the expected source appears anywhere in top-k, not only top-1
- add answer-level grading
- add no-answer classification checks
- add more documents and more evaluation questions
- save evaluation results as JSON or markdown reports
- add retrieval precision and recall metrics

## Advanced Retrieval Metrics

The evaluation now tracks both top-1 and top-k success.

Top-1 success means the expected source and section were the first retrieved result.

Top-k success means the expected source and section appeared anywhere in the retrieved context.

This distinction matters because a RAG answer may still work if the right evidence is in the retrieved context, but weaker ranking can add noise and reduce answer quality.

The evaluation set also includes:

- expected answer type
- expected answer behaviour
- phrases that must not appear in unsupported answers