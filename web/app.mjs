import { evaluateTask, LIMITS } from "./rules.mjs";

const form = document.querySelector("#audit-form");
const error = document.querySelector("#error");
const results = document.querySelector("#results");
const summary = document.querySelector("#summary");
const alerts = document.querySelector("#alerts");
const exportButton = document.querySelector("#export-button");
const statusElement = document.querySelector("#m-status");
const countElement = document.querySelector("#m-tasks");
const alertCountElement = document.querySelector("#m-alerts");
const ruleElement = document.querySelector("#rule-info");
let lastResult = null;
let tasksProcessed = 0;
let alertsTriggered = 0;

ruleElement.textContent = `Primary > ${LIMITS.primary}; secondary > ${LIMITS.secondary}; critical flag; anomaly descriptor keywords.`;

function appendLine(parent, tag, className, value) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = value;
  parent.appendChild(element);
  return element;
}

function render(result) {
  results.hidden = false;
  document.querySelector("#before-run").hidden = true;
  summary.replaceChildren();
  alerts.replaceChildren();
  const classification = result.overall_urgency.replaceAll("_", " ");
  appendLine(summary, "strong", "classification", classification);
  appendLine(summary, "p", "subtle", `${result.total_alerts} triggered rule(s) · ${result.integrity_status.replaceAll("_", " ")}`);
  appendLine(summary, "p", "subtle", `Task: ${result.task_id} · Target: ${result.target_identifier}`);

  if (!result.alerts.length) {
    appendLine(alerts, "p", "empty", "No rules triggered for these demonstration inputs.");
  } else {
    for (const alert of result.alerts) {
      const card = document.createElement("article");
      card.className = "alert-card";
      appendLine(card, "h3", "", alert.summary);
      appendLine(card, "p", "subtle", alert.origin_worker + " · " + alert.urgency);
      appendLine(card, "p", "", alert.technical_details);
      appendLine(card, "p", "subtle", alert.actionable_remediation);
      alerts.appendChild(card);
    }
  }
  statusElement.textContent = result.overall_urgency === "ROUTINE" ? "NO RULES TRIGGERED" : "RULES TRIGGERED";
  statusElement.dataset.state = result.overall_urgency;
  countElement.textContent = String(tasksProcessed);
  alertCountElement.textContent = String(alertsTriggered);
  exportButton.disabled = false;
}

form.addEventListener("submit", event => {
  event.preventDefault();
  error.textContent = "";
  const fields = new FormData(form);
  try {
    const result = evaluateTask({
      task_id: fields.get("task_id"),
      target_identifier: fields.get("target_identifier"),
      primary_metric: fields.get("primary_metric"),
      secondary_metric: fields.get("secondary_metric"),
      status_descriptor: fields.get("status_descriptor"),
      is_critical_flag: fields.has("is_critical_flag")
    });
    lastResult = result;
    tasksProcessed += 1;
    alertsTriggered += result.total_alerts;
    render(result);
  } catch (err) {
    error.textContent = err instanceof Error ? err.message : "Unable to evaluate inputs.";
  }
});

exportButton.addEventListener("click", () => {
  if (!lastResult) return;
  const file = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
  const url = URL.createObjectURL(file);
  const link = document.createElement("a");
  link.href = url;
  link.download = "physiotwin-rule-evaluation.json";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});
