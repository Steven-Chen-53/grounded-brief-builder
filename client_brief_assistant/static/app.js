let currentAnalysis = null;

const byId = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

async function loadClients() {
  try {
    const response = await fetch("/api/clients");
    const data = await response.json();
    byId("client-options").innerHTML = data.clients
      .map((client) => `<option value="${escapeHtml(client)}"></option>`)
      .join("");
  } catch {
    // The example value remains available if this optional convenience request fails.
  }
}

function setMessage(text, isError = false) {
  const target = byId("message");
  target.textContent = text;
  target.classList.toggle("error", isError);
}

function renderEvidence(evidence) {
  byId("evidence-list").innerHTML = evidence.map((item) => {
    const percentage = Math.round(item.score * 100);
    return `<article class="evidence-card ${item.safe_to_use ? "" : "quarantined"}">
      <div class="score">${percentage}%</div>
      <div>
        <div class="evidence-meta">
          <span class="tag ${item.relationship === "client evidence" ? "client" : ""}">${escapeHtml(item.relationship)}</span>
          <span class="tag">${escapeHtml(item.document_type.replaceAll("_", " "))}</span>
          <span class="tag">${escapeHtml(item.record_id)}</span>
        </div>
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.preview)}</p>
        ${item.warning ? `<div class="warning-box">${escapeHtml(item.warning)}</div>` : ""}
      </div>
    </article>`;
  }).join("");
}

function renderExceptions(brief) {
  const warnings = brief.warnings.length
    ? brief.warnings.map((warning) => `<div class="warning-box">${escapeHtml(warning)}</div>`).join("")
    : '<div class="info-box">No quarantined sources were used in the draft.</div>';
  byId("warnings").innerHTML = warnings;
  byId("questions").innerHTML = brief.clarification_questions.length
    ? brief.clarification_questions.map((question) => `<li>${escapeHtml(question)}</li>`).join("")
    : "<li>No clarification is required before human review.</li>";
  byId("analogs").innerHTML = brief.analog_suggestions.length
    ? `<p class="eyebrow">Analog examples</p>${brief.analog_suggestions.map((item) =>
        `<div class="analog-item"><strong>${escapeHtml(item.client_name)}</strong>: ${escapeHtml(item.requested_deliverable)}<br />${escapeHtml(item.note)}</div>`
      ).join("")}`
    : "";
}

function renderFields(fields) {
  byId("field-list").innerHTML = fields.map((field, index) => {
    const statusClass = field.status.replaceAll(" ", "-");
    const evidence = field.evidence.length ? field.evidence.join(", ") : "User input / no source";
    const alternatives = field.alternatives?.length
      ? `<div class="alternatives">Other retrieved value: ${escapeHtml(field.alternatives.join(" | "))}</div>`
      : "";
    return `<div class="draft-field">
      <div><div class="field-name">${escapeHtml(field.name.replaceAll("_", " "))}</div><div class="field-source">${escapeHtml(evidence)}</div></div>
      <div><textarea data-field-index="${index}" aria-label="${escapeHtml(field.name)}">${escapeHtml(field.value)}</textarea>${alternatives}</div>
      <span class="status-badge ${statusClass}">${escapeHtml(field.status)}</span>
    </div>`;
  }).join("");
}

function renderAnalysis(data) {
  currentAnalysis = data;
  const brief = data.brief;
  byId("results").classList.remove("hidden");
  byId("evidence-count").textContent = brief.evidence_count;
  byId("missing-count").textContent = brief.missing_fields.length;
  byId("conflict-count").textContent = brief.conflicting_fields.length;
  byId("review-status").textContent = brief.abstained ? "Abstained" : (brief.ready_for_review ? "Ready to review" : "Needs clarification");
  byId("approval").checked = false;
  renderEvidence(data.evidence);
  renderExceptions(brief);
  renderFields(brief.fields);
  byId("results").scrollIntoView({ behavior: "smooth", block: "start" });
}

byId("request-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = byId("analyze-button");
  button.disabled = true;
  setMessage("Retrieving synthetic sources and checking field-level evidence...");
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_name: byId("client-name").value,
        engagement_goal: byId("engagement-goal").value,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed.");
    renderAnalysis(data);
    setMessage(data.synthetic_data_notice);
  } catch (error) {
    setMessage(error.message || "Analysis failed.", true);
  } finally {
    button.disabled = false;
  }
});

byId("toggle-evidence").addEventListener("click", () => {
  const list = byId("evidence-list");
  const hidden = list.classList.toggle("hidden");
  byId("toggle-evidence").textContent = hidden ? "Show evidence" : "Hide evidence";
});

function collectEditedBrief() {
  if (!currentAnalysis) return null;
  const brief = structuredClone(currentAnalysis.brief);
  document.querySelectorAll("[data-field-index]").forEach((input) => {
    brief.fields[Number(input.dataset.fieldIndex)].value = input.value;
  });
  return brief;
}

function download(filename, content, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function exportBrief(kind) {
  if (!currentAnalysis) return;
  setMessage("Checking approval and preparing export...");
  try {
    const response = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approved: byId("approval").checked, brief: collectEditedBrief() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Export failed.");
    const slug = currentAnalysis.brief.client_name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || "client";
    if (kind === "markdown") download(`${slug}-brief.md`, data.markdown, "text/markdown");
    else download(`${slug}-brief.json`, data.json, "application/json");
    setMessage("Approved brief exported. The export includes field status and evidence identifiers.");
  } catch (error) {
    setMessage(error.message || "Export failed.", true);
  }
}

byId("export-md").addEventListener("click", () => exportBrief("markdown"));
byId("export-json").addEventListener("click", () => exportBrief("json"));
loadClients();
