const form = document.getElementById("answer-form");
const queryInput = document.getElementById("query");
const retrievalModeInput = document.getElementById("retrieval-mode");
const topKInput = document.getElementById("top-k");
const candidateKInput = document.getElementById("candidate-k");
const autoFilterInput = document.getElementById("auto-filter");
const rewriteQueryInput = document.getElementById("rewrite-query");
const rerankInput = document.getElementById("rerank");
const submitButton = document.getElementById("submit-button");

const statusPill = document.getElementById("status-pill");
const errorBox = document.getElementById("error-box");
const answerText = document.getElementById("answer-text");
const sourcesList = document.getElementById("sources-list");
const traceList = document.getElementById("trace-list");
const chunksList = document.getElementById("chunks-list");

function setStatus(label, statusClass) {
  statusPill.textContent = label;
  statusPill.className = `status-pill ${statusClass}`;
}

function setError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function createTextElement(tagName, className, textContent) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = textContent;
  return element;
}

function renderSources(sources) {
  sourcesList.innerHTML = "";

  if (!sources || sources.length === 0) {
    sourcesList.textContent = "No sources returned.";
    sourcesList.className = "empty-state";
    return;
  }

  sourcesList.className = "";

  sources.forEach((source, index) => {
    const item = document.createElement("div");
    item.className = "source-item";

    const title = createTextElement(
      "div",
      "source-title",
      `[${index + 1}] ${source.source} — ${source.section}`
    );

    const pageText = source.page_number ? `Page ${source.page_number}` : "No page";
    const fileType = source.file_type || "unknown type";

    const meta = createTextElement(
      "div",
      "source-meta",
      `${fileType} · ${pageText} · chunk ${source.chunk_index}`
    );

    item.appendChild(title);
    item.appendChild(meta);
    sourcesList.appendChild(item);
  });
}

function renderTrace(data) {
  const metadataFilter = data.metadata_filter
    ? JSON.stringify(data.metadata_filter)
    : "None";

  traceList.innerHTML = `
    <div>
      <dt>Retrieval query</dt>
      <dd>${escapeHtml(data.retrieval_query || "-")}</dd>
    </div>
    <div>
      <dt>Metadata filter</dt>
      <dd>${escapeHtml(metadataFilter)}</dd>
    </div>
    <div>
      <dt>Retrieval mode</dt>
      <dd>${escapeHtml(data.retrieval_mode || "-")}</dd>
    </div>
    <div>
      <dt>Rerank enabled</dt>
      <dd>${String(data.rerank_enabled)}</dd>
    </div>
    <div>
      <dt>Query rewritten</dt>
      <dd>${String(data.query_was_rewritten)}</dd>
    </div>
    <div>
      <dt>Rewrite reason</dt>
      <dd>${escapeHtml(data.rewrite_reason || "-")}</dd>
    </div>
  `;
}

function renderChunks(chunks) {
  chunksList.innerHTML = "";

  if (!chunks || chunks.length === 0) {
    chunksList.textContent = "No retrieved chunks returned.";
    chunksList.className = "empty-state";
    return;
  }

  chunksList.className = "";

  chunks.forEach((chunk, index) => {
    const item = document.createElement("div");
    item.className = "chunk-item";

    const title = createTextElement(
      "div",
      "source-title",
      `Chunk ${index + 1}: ${chunk.source} — ${chunk.section}`
    );

    const meta = createTextElement(
      "div",
      "chunk-meta",
      `Distance: ${formatDistance(chunk.distance)}`
    );

    const text = createTextElement("div", "chunk-text", chunk.text);

    item.appendChild(title);
    item.appendChild(meta);
    item.appendChild(text);
    chunksList.appendChild(item);
  });
}

function formatDistance(distance) {
  if (distance === null || distance === undefined) {
    return "-";
  }

  return Number(distance).toFixed(4);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function buildPayload() {
  return {
    query: queryInput.value.trim(),
    top_k: Number(topKInput.value),
    retrieval_mode: retrievalModeInput.value,
    auto_filter: autoFilterInput.checked,
    rewrite_query: rewriteQueryInput.checked,
    rerank: rerankInput.checked,
    candidate_k: Number(candidateKInput.value),
  };
}

async function submitQuestion(event) {
  event.preventDefault();

  const payload = buildPayload();

  if (!payload.query) {
    setError("Please enter a question.");
    return;
  }

  clearError();
  setStatus("Running", "loading");
  submitButton.disabled = true;
  answerText.textContent = "Generating answer...";

  try {
    const response = await fetch("/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Request failed with ${response.status}`);
    }

    const data = await response.json();

    answerText.textContent = data.answer;
    renderSources(data.sources);
    renderTrace(data);
    renderChunks(data.retrieved_chunks);
    setStatus("Success", "success");
  } catch (error) {
    setStatus("Error", "error");
    setError(error.message);
    answerText.textContent = "The request failed. Check the error message above.";
  } finally {
    submitButton.disabled = false;
  }
}

document.querySelectorAll(".example-chip").forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.textContent;
  });
});

form.addEventListener("submit", submitQuestion);