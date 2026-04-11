const RECENT_RUNS_KEY = "shadow-po-recent-runs";
const MAX_RECENT_RUNS = 8;

function stringify(value) {
  return JSON.stringify(value, null, 2);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function getField(formId, name) {
  return document.querySelector(`#${formId} [name="${name}"]`);
}

function scrollToSection(sectionId) {
  document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function markPrefilled(input) {
  if (!input) {
    return;
  }
  input.classList.add("prefilled");
  window.clearTimeout(input._prefillTimer);
  input._prefillTimer = window.setTimeout(() => input.classList.remove("prefilled"), 1400);
}

function setLookupRunId(runId) {
  const input = getField("run-form", "run_id");
  if (!input) {
    return;
  }
  input.value = runId;
  markPrefilled(input);
}

function setContinuationRunId(runId) {
  const input = getField("continue-form", "run_id");
  if (!input) {
    return;
  }
  input.value = runId;
  markPrefilled(input);
}

function applyLatestRun(runId) {
  if (!runId) {
    return;
  }
  setLookupRunId(runId);
  setContinuationRunId(runId);
}

function submitForm(formId) {
  document.getElementById(formId)?.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
}

function relireRun(runId) {
  setLookupRunId(runId);
  scrollToSection("run-section");
  submitForm("run-form");
}

function prepareContinuation(runId) {
  setContinuationRunId(runId);
  scrollToSection("continue-section");
  getField("continue-form", "action")?.focus();
}

function renderList(title, items) {
  if (!items || items.length === 0) {
    return "";
  }
  return `
    <div class="list-block">
      <h4>${escapeHtml(title)}</h4>
      <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
  `;
}

function renderText(title, value) {
  if (!value) {
    return "";
  }
  return `
    <div class="text-block">
      <h4>${escapeHtml(title)}</h4>
      <p>${escapeHtml(value)}</p>
    </div>
  `;
}

function renderKvGrid(entries) {
  const filtered = entries.filter(([, value]) => value !== null && value !== undefined && value !== "");
  if (!filtered.length) {
    return "";
  }
  return `
    <div class="kv-grid">
      ${filtered
        .map(
          ([label, value, strong]) => `
            <div class="kv-item ${strong ? "strong" : ""}">
              <strong>${escapeHtml(label)}</strong>
              <span>${escapeHtml(Array.isArray(value) ? value.join(", ") : value)}</span>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function renderRunActions(runId, options = {}) {
  if (!runId) {
    return "";
  }
  return `
    <div class="action-bar">
      <button class="secondary" type="button" data-run-action="lookup" data-run-id="${escapeHtml(runId)}">Relire ce run</button>
      <button class="ghost" type="button" data-run-action="continue" data-run-id="${escapeHtml(runId)}">Continuer ce run</button>
      ${options.parentRunId
        ? `<button class="ghost" type="button" data-run-action="lookup" data-run-id="${escapeHtml(options.parentRunId)}">Relire le parent</button>`
        : ""}
    </div>
  `;
}

function renderDocumentation(result) {
  return `
    <div class="artifact-card">
      <h3>${escapeHtml(result.title || "Documentation")}</h3>
      ${renderText("Summary", result.summary)}
      ${renderText("Context", result.context)}
      ${result.sections
        .map((section) => {
          const content = Array.isArray(section.content)
            ? `<ul>${section.content.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
            : `<p>${escapeHtml(section.content)}</p>`;
          return `<div class="text-block"><h4>${escapeHtml(section.title)}</h4>${content}</div>`;
        })
        .join("")}
    </div>
  `;
}

function renderTicket(result) {
  return `
    <div class="artifact-card">
      <h3>${escapeHtml(result.title || "Ticket")}</h3>
      ${renderKvGrid([
        ["Ticket type", result.ticket_type],
        ["Business goal", result.business_goal],
      ])}
      ${renderText("Context", result.context)}
      ${renderText("Description", result.description)}
      ${renderText("Current behavior", result.current_behavior)}
      ${renderText("Expected behavior", result.expected_behavior)}
      ${renderList("Business impacts", result.business_impacts)}
      ${renderList("Technical impacts", result.technical_impacts)}
      ${renderList("Dependencies", result.dependencies)}
      ${renderList("Open points", result.open_points)}
      ${renderList("Acceptance criteria", result.acceptance_criteria)}
    </div>
  `;
}

function renderAnalysis(result) {
  return `
    <div class="artifact-card">
      <h3>Analysis</h3>
      ${renderText("Reformulation", result.reformulation)}
      ${renderText("Request summary", result.request_summary)}
      ${renderKvGrid([
        ["Detected type", result.detected_type],
        ["Recommended output", result.recommended_output],
      ])}
      ${renderText("Context hint", result.context_hint)}
      ${renderText("Current behavior", result.current_behavior)}
      ${renderText("Expected behavior", result.expected_behavior)}
      ${renderList("Business impacts", result.business_impacts)}
      ${renderList("Technical impacts", result.technical_impacts)}
      ${renderList("Dependencies", result.dependencies)}
      ${renderList("Ambiguities", result.ambiguities)}
      ${renderList("Risks", result.risks)}
      ${renderList("Open questions", result.open_questions)}
      ${renderText("Recommended next step", result.recommended_next_step)}
    </div>
  `;
}

function renderSourceSummary(result) {
  return `
    <div class="artifact-card">
      <h3>${escapeHtml(result.source_title || result.source_ref || "Source summary")}</h3>
      ${renderKvGrid([
        ["Source type", result.source_type],
        ["Source ref", result.source_ref],
      ])}
      ${renderText("Summary", result.summary)}
      ${renderList("Key points", result.key_points)}
      ${renderList("Open questions", result.open_questions)}
      ${renderText("Next step hint", result.next_step_hint)}
    </div>
  `;
}

function renderJiraIssue(result) {
  return `
    <div class="artifact-card">
      <h3>${escapeHtml(result.issue_key)} - ${escapeHtml(result.title || "")}</h3>
      ${renderKvGrid([
        ["Status", result.status],
        ["Issue type", result.issue_type],
        ["Priority", result.priority],
        ["Assignee", result.assignee],
        ["Labels", result.labels],
        ["URL", result.url],
      ])}
      ${renderText("Summary", result.summary)}
      ${renderText("Description", result.description)}
      ${renderList("Open points", result.open_points)}
    </div>
  `;
}

function renderUnknown(result) {
  return `
    <div class="artifact-card">
      <h3>Raw payload</h3>
      <div class="raw">
        <pre>${escapeHtml(stringify(result))}</pre>
      </div>
    </div>
  `;
}

function renderArtifact(result) {
  if (!result) {
    return "";
  }
  if ("reformulation" in result && "recommended_output" in result) {
    return renderAnalysis(result);
  }
  if ("ticket_type" in result && "acceptance_criteria" in result) {
    return renderTicket(result);
  }
  if ("document_type" in result && "sections" in result) {
    return renderDocumentation(result);
  }
  if ("source_type" in result && "next_step_hint" in result) {
    return renderSourceSummary(result);
  }
  if ("issue_key" in result && "summary" in result) {
    return renderJiraIssue(result);
  }
  return renderUnknown(result);
}

function renderRawBlock(payload) {
  return `
    <div class="artifact-card raw">
      <details>
        <summary>Raw payload</summary>
        <pre>${escapeHtml(stringify(payload))}</pre>
      </details>
    </div>
  `;
}

function renderProcessLike(payload) {
  return `
    <div class="artifact-card">
      <h3 class="run-focus">
        <span>Execution metadata</span>
        <span class="run-pill">Run ID: ${escapeHtml(payload.run_id)}</span>
      </h3>
      ${renderKvGrid([
        ["Run ID", payload.run_id, true],
        ["Request type", payload.request_type],
        ["Selected workflow", payload.selected_workflow],
        ["Confidence", payload.confidence],
      ])}
      ${renderRunActions(payload.run_id)}
      ${renderList("Quality checks", payload.quality_checks || [])}
      ${renderList("Warnings", payload.warnings || [])}
    </div>
    ${renderArtifact(payload.result)}
    ${payload.intermediate_analysis ? renderArtifact(payload.intermediate_analysis) : ""}
    ${payload.context_used
      ? `
        <div class="artifact-card">
          <h3>Context used</h3>
          ${renderKvGrid([
            ["Source", payload.context_used.source_name],
            ["Confidence hint", payload.context_used.confidence_hint],
          ])}
          ${renderText("Summary", payload.context_used.summary)}
          ${renderList("Snippets", payload.context_used.snippets || [])}
        </div>
      `
      : ""}
    ${renderRawBlock(payload)}
  `;
}

function renderRun(payload) {
  return `
    <div class="artifact-card">
      <h3 class="run-focus">
        <span>Run metadata</span>
        <span class="run-pill">Run ID: ${escapeHtml(payload.run_id)}</span>
      </h3>
      ${renderKvGrid([
        ["Run ID", payload.run_id, true],
        ["Status", payload.status],
        ["Parent run ID", payload.parent_run_id],
        ["Continuation action", payload.continuation_action],
        ["Target output", payload.target_output],
        ["Request type", payload.request_type],
        ["Final workflow", payload.final_workflow],
        ["Created at", payload.created_at],
      ])}
      ${renderRunActions(payload.run_id, { parentRunId: payload.parent_run_id })}
      ${renderText("Raw input", payload.raw_input)}
    </div>
    ${renderArtifact(payload.result)}
    ${payload.intermediate_analysis ? renderArtifact(payload.intermediate_analysis) : ""}
    ${payload.context_used
      ? `
        <div class="artifact-card">
          <h3>Context used</h3>
          ${renderText("Summary", payload.context_used.summary)}
          ${renderList("Snippets", payload.context_used.snippets || [])}
        </div>
      `
      : ""}
    ${renderRawBlock(payload)}
  `;
}

function removeInlineStatus(container) {
  container.querySelector(".inline-status")?.remove();
}

function showInlineStatus(container, type, message) {
  removeInlineStatus(container);
  container.insertAdjacentHTML(
    "afterbegin",
    `<div class="message ${type} inline-status">${escapeHtml(message)}</div>`
  );
}

function getRecentRuns() {
  try {
    const raw = window.localStorage.getItem(RECENT_RUNS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveRecentRuns(items) {
  window.localStorage.setItem(RECENT_RUNS_KEY, JSON.stringify(items));
}

function rememberRun(entry) {
  if (!entry?.run_id) {
    return;
  }
  const current = getRecentRuns().filter((item) => item.run_id !== entry.run_id);
  current.unshift({
    run_id: entry.run_id,
    workflow: entry.workflow || null,
    request_type: entry.request_type || null,
    parent_run_id: entry.parent_run_id || null,
    source: entry.source || null,
    timestamp: new Date().toISOString(),
  });
  saveRecentRuns(current.slice(0, MAX_RECENT_RUNS));
  applyLatestRun(entry.run_id);
  renderRecentRuns();
}

function renderRecentRuns() {
  const container = document.getElementById("recent-runs");
  const recentRuns = getRecentRuns();
  if (!recentRuns.length) {
    container.classList.add("empty");
    container.innerHTML = "";
    return;
  }

  container.classList.remove("empty");
  container.innerHTML = recentRuns
    .map(
      (item) => `
        <div class="recent-item">
          <div class="recent-title">
            <strong>${escapeHtml(item.run_id)}</strong>
            <div class="action-bar">
              <button class="secondary" type="button" data-run-action="lookup" data-run-id="${escapeHtml(item.run_id)}">Relire</button>
              <button class="ghost" type="button" data-run-action="continue" data-run-id="${escapeHtml(item.run_id)}">Continuer</button>
            </div>
          </div>
          <div class="recent-meta">
            ${item.workflow ? `<span>workflow: ${escapeHtml(item.workflow)}</span>` : ""}
            ${item.request_type ? `<span>type: ${escapeHtml(item.request_type)}</span>` : ""}
            ${item.parent_run_id ? `<span>parent: ${escapeHtml(item.parent_run_id)}</span>` : ""}
            ${item.source ? `<span>source: ${escapeHtml(item.source)}</span>` : ""}
          </div>
        </div>
      `
    )
    .join("");
}

async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail || `HTTP ${response.status}`;
    throw new Error(`${response.status} - ${detail}`);
  }
  return payload;
}

function bindJsonForm(formId, outputId, buildRequest, requestFn, renderFn, onSuccess) {
  const form = document.getElementById(formId);
  const output = document.getElementById(outputId);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showInlineStatus(output, "ok", "Execution en cours...");
    try {
      const payload = await requestFn(buildRequest(new FormData(form)));
      output.innerHTML = renderFn(payload);
      onSuccess?.(payload);
    } catch (error) {
      showInlineStatus(output, "error", error.message || "Erreur reseau");
    }
  });
}

bindJsonForm(
  "process-form",
  "process-output",
  (formData) => ({
    user_input: formData.get("user_input"),
    context_hint: formData.get("context_hint") || null,
    target_output: formData.get("target_output"),
  }),
  (payload) => apiRequest("/process", { method: "POST", body: stringify(payload) }),
  renderProcessLike,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: payload.selected_workflow,
      request_type: payload.request_type,
      source: "process",
    })
);

bindJsonForm(
  "run-form",
  "run-output",
  (formData) => formData.get("run_id"),
  (runId) => apiRequest(`/runs/${encodeURIComponent(runId)}`),
  renderRun,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: payload.final_workflow,
      request_type: payload.request_type,
      parent_run_id: payload.parent_run_id,
      source: "run_lookup",
    })
);

bindJsonForm(
  "continue-form",
  "continue-output",
  (formData) => ({
    run_id: formData.get("run_id"),
    action: formData.get("action"),
  }),
  (payload) =>
    apiRequest(`/runs/${encodeURIComponent(payload.run_id)}/continue`, {
      method: "POST",
      body: stringify({ action: payload.action }),
    }),
  renderProcessLike,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: payload.selected_workflow,
      request_type: payload.request_type,
      source: "continuation",
    })
);

bindJsonForm(
  "source-form",
  "source-output",
  (formData) => ({
    source_type: formData.get("source_type"),
    source_ref: formData.get("source_ref"),
    context_hint: formData.get("context_hint") || null,
  }),
  (payload) => apiRequest("/source-summary", { method: "POST", body: stringify(payload) }),
  (payload) => `
    <div class="artifact-card">
      <h3 class="run-focus">
        <span>Source summary metadata</span>
        <span class="run-pill">Run ID: ${escapeHtml(payload.run_id)}</span>
      </h3>
      ${renderKvGrid([["Run ID", payload.run_id, true]])}
      ${renderRunActions(payload.run_id)}
    </div>
    ${renderArtifact(payload.result)}
    ${renderRawBlock(payload)}
  `,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: "source_summary",
      request_type: "source_summary",
      source: "source_summary",
    })
);

bindJsonForm(
  "jira-form",
  "jira-output",
  (formData) => ({
    issue_key: formData.get("issue_key"),
  }),
  (payload) => apiRequest("/jira-read", { method: "POST", body: stringify(payload) }),
  (payload) => `
    <div class="artifact-card">
      <h3 class="run-focus">
        <span>Jira read metadata</span>
        <span class="run-pill">Run ID: ${escapeHtml(payload.run_id)}</span>
      </h3>
      ${renderKvGrid([["Run ID", payload.run_id, true]])}
      ${renderRunActions(payload.run_id)}
    </div>
    ${renderArtifact(payload.result)}
    ${renderRawBlock(payload)}
  `,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: "jira_read",
      request_type: "jira_read",
      source: "jira_read",
    })
);

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-run-action]");
  if (!button) {
    return;
  }

  const runId = button.getAttribute("data-run-id");
  const action = button.getAttribute("data-run-action");
  if (!runId || !action) {
    return;
  }

  if (action === "lookup") {
    relireRun(runId);
    return;
  }

  if (action === "continue") {
    prepareContinuation(runId);
  }
});

const latestRun = getRecentRuns()[0]?.run_id;
if (latestRun) {
  applyLatestRun(latestRun);
}
renderRecentRuns();
