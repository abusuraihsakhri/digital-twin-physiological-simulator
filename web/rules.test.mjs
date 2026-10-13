import test from "node:test";
import assert from "node:assert/strict";
import { evaluateTask, LIMITS } from "./rules.mjs";

function input(overrides = {}) {
  return {
    task_id: "DEMO-01", target_identifier: "SYNTHETIC-1",
    primary_metric: 12, secondary_metric: 4,
    status_descriptor: "NOMINAL", is_critical_flag: false, ...overrides
  };
}

test("boundary values do not trigger rules", () => {
  const result = evaluateTask(input({
    primary_metric: LIMITS.primary, secondary_metric: LIMITS.secondary
  }));
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
});

test("primary and secondary thresholds produce elevated alerts", () => {
  const result = evaluateTask(input({ primary_metric: 25.01, secondary_metric: 12.01 }));
  assert.equal(result.overall_urgency, "ELEVATED_RISK");
  assert.equal(result.total_alerts, 2);
  assert.equal(result.critical_alerts_count, 0);
});

test("explicit critical flag takes precedence over elevated rules", () => {
  const result = evaluateTask(input({ is_critical_flag: true, status_descriptor: "DISCORDANT" }));
  assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(result.critical_alerts_count, 1);
  assert.equal(result.total_alerts, 2);
});

test("descriptor matching is case-insensitive", () => {
  assert.equal(evaluateTask(input({ status_descriptor: "anomaly" })).total_alerts, 1);
});

test("empty, non-finite, and overlong values are rejected", () => {
  assert.throws(() => evaluateTask(input({ primary_metric: "" })), /finite/);
  assert.throws(() => evaluateTask(input({ secondary_metric: Infinity })), /finite/);
  assert.throws(() => evaluateTask(input({ task_id: "" })), /required/);
  assert.throws(() => evaluateTask(input({ target_identifier: "X".repeat(129) })), /128/);
});

test("false string is never treated as an explicit true flag", () => {
  assert.equal(evaluateTask(input({ is_critical_flag: "false" })).overall_urgency, "ROUTINE");
});
