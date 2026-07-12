from banking_rag.core.schemas import RetrievedChunk


def build_context_block(retrieved_chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a source-labelled context block."""
    context_blocks: list[str] = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_blocks.append(
            f"[Source {index}]\n"
            f"Document: {chunk.source}\n"
            f"Section: {chunk.section}\n"
            f"Chunk index: {chunk.chunk_index}\n"
            f"Distance: {chunk.distance:.4f}\n"
            f"Text:\n{chunk.text}"
        )

    return "\n\n---\n\n".join(context_blocks)


def build_grounded_prompt(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str:
    """Build a grounded RAG prompt from retrieved chunks."""
    context = build_context_block(retrieved_chunks)

    return f"""
You are a banking knowledge assistant.

Answer the user's question using only the provided context.

Rules:
- Use only the provided context.
- Do not use outside knowledge.
- Do not invent timelines, fees, limits, eligibility criteria, guarantees, or policy details.
- If the context does not contain enough information, say that the provided documents do not contain enough information.
- Keep the answer clear, professional, and concise.
- Include the sources used at the end of the answer.
- Cite sources using the format: Source: [Source number] document name, section name.

Context:
{context}

User question:
{question}

Answer:
""".strip()