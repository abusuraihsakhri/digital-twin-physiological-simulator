/**
 * Browser implementation of the three deterministic rule checks in
 * agents/workers.py. No physiological ODE or clinical decision model is implied.
 */
export const LIMITS = Object.freeze({ primary: 25, secondary: 12 });

export function evaluateTask(input) {
  const taskId = String(input.task_id ?? "").trim();
  const target = String(input.target_identifier ?? "").trim();
  const descriptor = String(input.status_descriptor ?? "").trim();
  const primary = Number(input.primary_metric);
  const secondary = Number(input.secondary_metric);
  const critical = input.is_critical_flag === true;

  if (!taskId || !target || !descriptor) {
    throw new Error("Task ID, target identifier, and descriptor are required.");
  }
  if ([taskId, target, descriptor].some(value => value.length > 128)) {
    throw new Error("Text inputs must not exceed 128 characters.");
  }
  if (input.primary_metric === "" || input.secondary_metric === "" ||
      !Number.isFinite(primary) || !Number.isFinite(secondary)) {
    throw new Error("Both measurements must be finite numeric values.");
  }

  const alerts = [];
  if (primary > LIMITS.primary) {
    alerts.push({
      origin_worker: "InvariantQCWorker",
      urgency: "ELEVATED_RISK",
      summary: "Primary Metric Threshold Exceeded",
      technical_details: `Primary measurement (${primary.toFixed(2)}) exceeds the demonstration limit (25.00).`,
      actionable_remediation: "Review the selected threshold and input assumptions."
    });
  }
  if (critical || secondary > LIMITS.secondary) {
    alerts.push({
      origin_worker: "SafetyEscalationWorker",
      urgency: critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Safety Rule Triggered",
      technical_details: `CriticalFlag=${critical} with secondary index ${secondary.toFixed(2)} (limit 12.00).`,
      actionable_remediation: "Review the trigger; no clinical action is prescribed by this demonstration."
    });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
        .some(flag => descriptor.toUpperCase().includes(flag))) {
    alerts.push({
      origin_worker: "ProtocolConformanceWorker",
      urgency: "ELEVATED_RISK",
      summary: "Descriptor Anomaly Detected",
      technical_details: `Descriptor "${descriptor}" contains an anomaly token.`,
      actionable_remediation: "Check the descriptor and source record."
    });
  }
  const criticalCount = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
  const urgency = criticalCount ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  const integrity = criticalCount ? "RECALIBRATION_REQUIRED" :
    alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL";
  return {
    mode: "local_rule_evaluation",
    task_id: taskId,
    target_identifier: target,
    overall_urgency: urgency,
    integrity_status: integrity,
    total_alerts: alerts.length,
    critical_alerts_count: criticalCount,
    alerts,
    parameters: { primary_metric: primary, secondary_metric: secondary,
      status_descriptor: descriptor, is_critical_flag: critical },
    notice: "Demonstration thresholds only. No ODE integration, validation, HMAC audit signing, or clinical inference."
  };
}
