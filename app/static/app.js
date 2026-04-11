const RECENT_RUNS_KEY = "shadow-po-recent-runs";
const MAX_RECENT_RUNS = 8;
let currentTopicId = null;
let topicsListState = "idle";
let selectedTopicState = "unselected";

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

function clearLookupRunIdIfMatches(runId) {
  const input = getField("run-form", "run_id");
  if (input && input.value === runId) {
    input.value = "";
  }
}

function clearContinuationRunIdIfMatches(runId) {
  const input = getField("continue-form", "run_id");
  if (input && input.value === runId) {
    input.value = "";
  }
}

function submitForm(formId) {
  document.getElementById(formId)?.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
}

function relireRun(runId) {
  setLookupRunId(runId);
  scrollToSection("lookup-section");
  submitForm("run-form");
}

function prepareContinuation(runId) {
  setContinuationRunId(runId);
  scrollToSection("actions-section");
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
  const availableActions = options.availableActions || [];
  return `
    <div class="action-bar">
      <button class="secondary" type="button" data-run-action="lookup" data-run-id="${escapeHtml(runId)}">Relire ce run</button>
      ${availableActions.length
        ? `<button class="ghost" type="button" data-run-action="continue" data-run-id="${escapeHtml(runId)}" data-run-actions="${escapeHtml(availableActions.join(","))}">Continuer ce run</button>`
        : ""}
      ${options.parentRunId
        ? `<button class="ghost" type="button" data-run-action="lookup" data-run-id="${escapeHtml(options.parentRunId)}">Relire le parent</button>`
        : ""}
    </div>
  `;
}

function formatDate(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("fr-FR");
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

function renderConfluencePage(result) {
  return `
    <div class="artifact-card">
      <h3>${escapeHtml(result.title || result.page_id || "Confluence page")}</h3>
      ${renderKvGrid([
        ["Page ID", result.page_id],
        ["Space", result.space_key],
        ["URL", result.url],
      ])}
      ${renderText("Summary", result.summary)}
      ${renderText("Content preview", result.content_preview)}
      ${renderList("Key points", result.key_points)}
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
  if ("page_id" in result && "content_preview" in result) {
    return renderConfluencePage(result);
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

function renderEmptyCard(message) {
  return `<div class="message info">${escapeHtml(message)}</div>`;
}

function inferAvailableActionsFromArtifact(result) {
  if (!result) {
    return [];
  }
  if ("reformulation" in result && "recommended_output" in result) {
    return ["refine_analysis", "draft_ticket", "draft_documentation"];
  }
  if ("source_type" in result && "next_step_hint" in result) {
    return ["refine_analysis", "draft_ticket", "draft_documentation"];
  }
  if ("issue_key" in result && "summary" in result) {
    return ["refine_analysis", "draft_ticket", "draft_documentation"];
  }
  return [];
}

function renderTopicDetailState(state, message = "") {
  if (state === "loading") {
    return renderEmptyCard("Chargement du dossier topic...");
  }
  if (state === "error") {
    return `<div class="message error">${escapeHtml(message || "Le dossier topic n'a pas pu etre charge.")}</div>`;
  }
  if (state === "empty") {
    return renderEmptyCard(
      message ||
        "Aucun sujet cote serveur pour l'instant. Lancez un process, un read ou une continuation pour creer un dossier."
    );
  }
  return renderEmptyCard(message || "Selectionnez un topic pour ouvrir son dossier de travail.");
}

function renderProcessMetaCard(title, payload) {
  return `
    <div class="artifact-card">
      <h3 class="run-focus">
        <span>${escapeHtml(title)}</span>
        <span class="run-pill">Run ID: ${escapeHtml(payload.run_id)}</span>
      </h3>
      ${renderKvGrid([
        ["Run ID", payload.run_id, true],
        ["Topic ID", payload.topic_id, true],
        ["Request type", payload.request_type],
        ["Selected workflow", payload.selected_workflow],
        ["Confidence", payload.confidence],
      ])}
      ${renderRunActions(payload.run_id, { availableActions: payload.available_actions || [] })}
    </div>
  `;
}

function renderProcessLike(payload) {
  const availableActions = inferAvailableActionsFromArtifact(payload.result);
  return `
    ${renderProcessMetaCard("Execution metadata", { ...payload, available_actions: availableActions })}
    <div class="artifact-card">
      <h3>Decision quality</h3>
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
  const availableActions = inferAvailableActionsFromArtifact(payload.result);
  return `
    <div class="artifact-card">
      <h3 class="run-focus">
        <span>Run metadata</span>
        <span class="run-pill">Run ID: ${escapeHtml(payload.run_id)}</span>
      </h3>
      ${renderKvGrid([
        ["Run ID", payload.run_id, true],
        ["Topic ID", payload.topic_id, true],
        ["Status", payload.status],
        ["Parent run ID", payload.parent_run_id],
        ["Continuation action", payload.continuation_action],
        ["Target output", payload.target_output],
        ["Request type", payload.request_type],
        ["Final workflow", payload.final_workflow],
        ["Created at", payload.created_at],
      ])}
      ${renderRunActions(payload.run_id, {
        parentRunId: payload.parent_run_id,
        availableActions,
      })}
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

function renderTopicSummary(topic) {
  return `
    <div class="topic-summary ${currentTopicId === topic.topic_id ? "active" : ""}">
      <div class="topic-summary-head">
        <strong>${escapeHtml(topic.topic_label || topic.topic_id)}</strong>
        <span class="topic-chip">${escapeHtml(topic.status)}</span>
      </div>
      ${renderKvGrid([
        ["Topic ID", topic.topic_id, true],
        ["Updated at", formatDate(topic.updated_at)],
        ["Run count", topic.run_count],
        ["Latest run ID", topic.latest_run_id],
      ])}
      <div class="action-bar">
        <button class="secondary" type="button" data-topic-action="open" data-topic-id="${escapeHtml(topic.topic_id)}">Ouvrir le topic</button>
        <button class="ghost" type="button" data-run-action="lookup" data-run-id="${escapeHtml(topic.latest_run_id)}">Relire le dernier run</button>
      </div>
    </div>
  `;
}

function renderTopicRunCard(run) {
  const workflowLabel = formatWorkflowLabel(run.final_workflow);
  return `
    <div class="topic-run-card">
      <h4>${escapeHtml(workflowLabel)} <span class="topic-chip">${escapeHtml(run.run_id)}</span></h4>
      ${renderKvGrid([
        ["Run ID", run.run_id, true],
        ["Created at", formatDate(run.created_at)],
        ["Artefact", workflowLabel],
        ["Origine", formatRequestTypeLabel(run.request_type)],
        ["Parent run ID", run.parent_run_id],
        ["Continuation action", run.continuation_action],
      ])}
      ${renderText("Raw input", run.raw_input)}
      ${run.available_actions?.length ? renderList("Available actions", run.available_actions) : ""}
      ${renderRunActions(run.run_id, {
        parentRunId: run.parent_run_id,
        availableActions: run.available_actions || [],
      })}
    </div>
  `;
}

function renderTopicDetail(payload) {
  return `
    <div class="artifact-card">
      <h3>${escapeHtml(payload.topic.topic_label || "Topic")}</h3>
      ${renderKvGrid([
        ["Topic ID", payload.topic.topic_id, true],
        ["Status", payload.topic.status],
        ["Created at", formatDate(payload.topic.created_at)],
        ["Updated at", formatDate(payload.topic.updated_at)],
        ["Root run ID", payload.topic.root_run_id],
        ["Latest run ID", payload.topic.latest_run_id],
        ["Run count", payload.topic.run_ids?.length || payload.runs.length],
      ])}
    </div>
    ${payload.root_run
      ? `
        <div class="artifact-card">
          <h3>Root run</h3>
          ${renderKvGrid([
            ["Run ID", payload.root_run.run_id, true],
            ["Workflow", payload.root_run.final_workflow],
            ["Created at", formatDate(payload.root_run.created_at)],
          ])}
          ${renderRunActions(payload.root_run.run_id, {
            parentRunId: payload.root_run.parent_run_id,
            availableActions: payload.root_run.available_actions || [],
          })}
        </div>
      `
      : ""}
    ${payload.latest_run
      ? `
        <div class="artifact-card">
          <h3>Latest run</h3>
          ${renderKvGrid([
            ["Run ID", payload.latest_run.run_id, true],
            ["Workflow", payload.latest_run.final_workflow],
            ["Created at", formatDate(payload.latest_run.created_at)],
          ])}
          ${payload.latest_run.available_actions?.length
            ? renderList("Available actions", payload.latest_run.available_actions)
            : ""}
          ${renderRunActions(payload.latest_run.run_id, {
            parentRunId: payload.latest_run.parent_run_id,
            availableActions: payload.latest_run.available_actions || [],
          })}
        </div>
      `
      : ""}
    <div class="artifact-card">
      <h3>Runs ordonnes</h3>
      <div class="topic-run-list">
        ${payload.runs.map(renderTopicRunCard).join("")}
      </div>
    </div>
    ${renderRawBlock(payload)}
  `;
}

function renderTopicDetailPanel(state, payload = null, message = "") {
  const container = document.getElementById("topic-detail");
  if (state === "loaded" && payload) {
    container.innerHTML = renderTopicDetail(payload);
    return;
  }
  container.innerHTML = renderTopicDetailState(state, message);
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

function removeRecentRun(runId) {
  const filtered = getRecentRuns().filter((item) => item.run_id !== runId);
  saveRecentRuns(filtered);
  renderRecentRuns();
  renderDashboard();
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
    available_actions: entry.available_actions || [],
    source: entry.source || null,
    timestamp: new Date().toISOString(),
  });
  saveRecentRuns(current.slice(0, MAX_RECENT_RUNS));
  applyLatestRun(entry.run_id);
  renderRecentRuns();
  renderDashboard();
  loadTopics();
}

function formatWorkflowLabel(value) {
  const labels = {
    analysis: "Analyse",
    ticket: "Ticket",
    documentation: "Documentation",
    source_summary: "Resume source",
    jira_read: "Lecture Jira",
    confluence_read: "Lecture Confluence",
  };
  return labels[value] || value || "Artefact";
}

function formatRequestTypeLabel(value) {
  const labels = {
    analysis: "Analyse",
    ticket: "Ticket",
    documentation: "Documentation",
    source_summary: "Source",
    jira_read: "Jira",
    confluence_read: "Confluence",
  };
  return labels[value] || value || "Run";
}

function formatRecentRunSource(value) {
  const labels = {
    process: "Demande traitee dans le workspace",
    run_lookup: "Artefact relu dans le workspace",
    continuation: "Artefact issu d'une continuation",
    source_summary: "Artefact issu d'une lecture source",
    jira_read: "Artefact issu d'une lecture Jira",
    confluence_read: "Artefact issu d'une lecture Confluence",
  };
  return labels[value] || "Run memorise";
}

function buildRecentRunSubtitle(item) {
  const parts = [];
  if (item.source) {
    parts.push(formatRecentRunSource(item.source));
  }
  if (item.parent_run_id) {
    parts.push(`Parent ${item.parent_run_id}`);
  }
  return parts.join(" | ");
}

function renderDashboard() {
  const recentRuns = getRecentRuns();
  const recentRunCount = document.getElementById("recent-run-count");
  const topicCount = document.getElementById("topic-count");
  const workspaceFocus = document.getElementById("workspace-focus");

  if (recentRunCount) {
    recentRunCount.textContent = String(recentRuns.length);
  }
  if (topicCount) {
    topicCount.textContent = String(Array.isArray(window.__shadowTopics) ? window.__shadowTopics.length : 0);
  }
  if (workspaceFocus) {
    workspaceFocus.textContent = recentRuns[0] ? formatWorkflowLabel(recentRuns[0].workflow) : "Aucun";
  }
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
            <strong>${escapeHtml(formatWorkflowLabel(item.workflow))}</strong>
            <div class="action-bar">
              <button class="secondary" type="button" data-run-action="lookup" data-run-id="${escapeHtml(item.run_id)}">Relire</button>
              ${item.available_actions?.length
                ? `<button class="ghost" type="button" data-run-action="continue" data-run-id="${escapeHtml(item.run_id)}" data-run-actions="${escapeHtml(item.available_actions.join(","))}">Continuer</button>`
                : ""}
            </div>
          </div>
          <p class="recent-subtitle">${escapeHtml(buildRecentRunSubtitle(item))}</p>
          <div class="recent-meta">
            <span>Run ${escapeHtml(item.run_id)}</span>
            ${item.workflow ? `<span>${escapeHtml(formatWorkflowLabel(item.workflow))}</span>` : ""}
          </div>
        </div>
      `
    )
    .join("");
}

function resetContinuationFormAvailability() {
  const actionField = getField("continue-form", "action");
  if (!actionField) {
    return;
  }
  Array.from(actionField.options).forEach((option) => {
    option.disabled = false;
  });
}

function applyContinuationAvailability(runId, availableActions) {
  setContinuationRunId(runId);
  const actionField = getField("continue-form", "action");
  const output = document.getElementById("continue-output");
  if (!actionField) {
    return;
  }

  resetContinuationFormAvailability();

  if (!availableActions.length) {
    actionField.value = "";
    Array.from(actionField.options).forEach((option) => {
      if (option.value) {
        option.disabled = true;
      }
    });
    showInlineStatus(output, "info", "Aucune continuation disponible pour ce run.");
    return;
  }

  Array.from(actionField.options).forEach((option) => {
    if (option.value && !availableActions.includes(option.value)) {
      option.disabled = true;
    }
  });
  actionField.value = availableActions[0];
  showInlineStatus(output, "ok", `Continuation prete avec l'action ${availableActions[0]}.`);
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
    const error = new Error(`${response.status} - ${detail}`);
    error.status = response.status;
    error.detail = detail;
    error.path = path;
    throw error;
  }
  return payload;
}

async function loadTopics() {
  const container = document.getElementById("topics-list");
  topicsListState = "loading";
  container.classList.remove("empty");
  container.innerHTML = `<div class="message ok inline-status">Chargement des topics...</div>`;
  try {
    const topics = await apiRequest("/topics");
    window.__shadowTopics = topics;
    renderDashboard();
    if (!topics.length) {
      topicsListState = "empty";
      container.innerHTML = "";
      container.classList.add("empty");
      currentTopicId = null;
      if (selectedTopicState !== "loaded") {
        selectedTopicState = "empty";
        renderTopicDetailPanel("empty");
      }
      return;
    }
    topicsListState = "loaded";
    container.classList.remove("empty");
    container.innerHTML = topics.map(renderTopicSummary).join("");
    if (selectedTopicState !== "loaded" && selectedTopicState !== "loading") {
      selectedTopicState = "unselected";
      renderTopicDetailPanel("unselected");
    }
  } catch (error) {
    topicsListState = "error";
    window.__shadowTopics = [];
    renderDashboard();
    container.innerHTML = `<div class="message error">${escapeHtml(error.message || "Erreur reseau")}</div>`;
    if (selectedTopicState !== "loaded") {
      selectedTopicState = "error";
      renderTopicDetailPanel("error", null, "La liste des topics n'a pas pu etre chargee.");
    }
  }
}

async function openTopic(topicId) {
  selectedTopicState = "loading";
  renderTopicDetailPanel("loading");
  try {
    const payload = await apiRequest(`/topics/${encodeURIComponent(topicId)}`);
    currentTopicId = topicId;
    selectedTopicState = "loaded";
    renderTopicDetailPanel("loaded", payload);
    renderRecentRuns();
    await loadTopics();
  } catch (error) {
    selectedTopicState = "error";
    renderTopicDetailPanel("error", null, error.message || "Erreur reseau");
  }
}

function handleStaleRun(runId, targetOutput, statusContainer) {
  removeRecentRun(runId);
  clearLookupRunIdIfMatches(runId);
  clearContinuationRunIdIfMatches(runId);
  resetContinuationFormAvailability();
  if (statusContainer) {
    showInlineStatus(
      statusContainer,
      "error",
      `Le run ${runId} n'existe plus cote serveur, probablement apres redemarrage du backend in-memory.`
    );
  }
  if (targetOutput && !targetOutput.innerHTML.trim()) {
    targetOutput.innerHTML = renderEmptyCard("Le run demande n'est plus disponible cote serveur.");
  }
}

async function validateLatestRunPrefill() {
  const latestRun = getRecentRuns()[0]?.run_id;
  if (!latestRun) {
    return;
  }

  try {
    await apiRequest(`/runs/${encodeURIComponent(latestRun)}`);
    applyLatestRun(latestRun);
  } catch (error) {
    if (error.status === 404) {
      handleStaleRun(latestRun, document.getElementById("run-output"), document.getElementById("recent-runs"));
    }
  }
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
      const built = buildRequest(new FormData(form));
      const runId = typeof built === "string" ? built : built?.run_id;
      if (error.status === 404 && runId) {
        handleStaleRun(runId, output, output);
        return;
      }
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
      available_actions: inferAvailableActionsFromArtifact(payload.result),
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
      available_actions: inferAvailableActionsFromArtifact(payload.result),
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
      available_actions: inferAvailableActionsFromArtifact(payload.result),
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
    ${renderProcessMetaCard("Source summary metadata", {
      run_id: payload.run_id,
      topic_id: payload.topic_id,
      request_type: "source_summary",
      selected_workflow: "source_summary",
      confidence: "n/a",
      available_actions: inferAvailableActionsFromArtifact(payload.result),
    })}
    ${renderArtifact(payload.result)}
    ${renderRawBlock(payload)}
  `,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: "source_summary",
      request_type: "source_summary",
      available_actions: inferAvailableActionsFromArtifact(payload.result),
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
    ${renderProcessMetaCard("Jira read metadata", {
      run_id: payload.run_id,
      topic_id: payload.topic_id,
      request_type: "jira_read",
      selected_workflow: "jira_read",
      confidence: "n/a",
      available_actions: inferAvailableActionsFromArtifact(payload.result),
    })}
    ${renderArtifact(payload.result)}
    ${renderRawBlock(payload)}
  `,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: "jira_read",
      request_type: "jira_read",
      available_actions: inferAvailableActionsFromArtifact(payload.result),
      source: "jira_read",
    })
);

bindJsonForm(
  "confluence-form",
  "confluence-output",
  (formData) => ({
    page_id: formData.get("page_id"),
  }),
  (payload) => apiRequest("/confluence-read", { method: "POST", body: stringify(payload) }),
  (payload) => `
    ${renderProcessMetaCard("Confluence read metadata", {
      run_id: payload.run_id,
      topic_id: payload.topic_id,
      request_type: "confluence_read",
      selected_workflow: "confluence_read",
      confidence: "n/a",
      available_actions: inferAvailableActionsFromArtifact(payload.result),
    })}
    ${renderArtifact(payload.result)}
    ${renderRawBlock(payload)}
  `,
  (payload) =>
    rememberRun({
      run_id: payload.run_id,
      workflow: "confluence_read",
      request_type: "confluence_read",
      available_actions: inferAvailableActionsFromArtifact(payload.result),
      source: "confluence_read",
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
    const actions = (button.getAttribute("data-run-actions") || "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    prepareContinuation(runId);
    applyContinuationAvailability(runId, actions);
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-topic-action]");
  if (!button) {
    return;
  }
  const topicId = button.getAttribute("data-topic-id");
  const action = button.getAttribute("data-topic-action");
  if (!topicId || action !== "open") {
    return;
  }
  scrollToSection("topics-section");
  openTopic(topicId);
});

document.getElementById("topics-refresh")?.addEventListener("click", () => {
  loadTopics();
});

getField("continue-form", "run_id")?.addEventListener("input", () => {
  resetContinuationFormAvailability();
});

getField("process-form", "user_input")?.addEventListener("input", (event) => {
  const value = event.target.value || "";
  const normalized = value.toLowerCase();
  const lineCount = value.split(/\r?\n/).length;
  let score = 0;

  if (value.length > 1200) {
    score += 1;
  }
  if (lineCount > 18) {
    score += 1;
  }
  if (/^\s*(diff --git|@@ |\+\+\+ |--- )/m.test(value)) {
    score += 2;
  }
  if (/\b(traceback|exception|stack trace|nullpointer|error:|warn:|debug:|info:)\b/.test(normalized)) {
    score += 1;
  }
  if (/\b(select\s+.+\s+from|post\s+\/|get\s+\/|patch\s+\/|put\s+\/|delete\s+\/)\b/.test(normalized)) {
    score += 1;
  }
  if (/[{}\[\]]/.test(value) && lineCount > 8) {
    score += 1;
  }

  document.getElementById("process-warning")?.classList.toggle("is-hidden", score < 2);
});

renderTopicDetailPanel("unselected");
renderRecentRuns();
renderDashboard();
loadTopics();
validateLatestRunPrefill();
