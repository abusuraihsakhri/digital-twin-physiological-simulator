"""Regression checks for signature validation, batch coercion, and HTTP handling."""
import csv

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail
from cli import main as main_cli
from physiotwin_simulator.cli import main as physiology_cli


def test_audit_verification_authenticates_entry_fields():
    ledger = AuditTrail(secret_key="regression-key")
    ledger.log("worker", "tier", "EVENT", {"value": 1})
    ledger.log("worker", "tier", "EVENT", {"value": 2})
    assert ledger.verify_integrity()
    ledger.logs[1]["actor_tier"] = "attacker"
    assert ledger.verify_integrity() is False


def test_ledger_reads_do_not_allow_external_mutation():
    ledger = AuditTrail(secret_key="regression-key")
    ledger.log("worker", "tier", "EVENT", {"value": 1})
    copies = ledger.get_trail()
    copies[0]["current_hash"] = "forged"
    assert ledger.verify_integrity()
    assert ledger.get_trail()[0]["current_hash"] != "forged"


@pytest.mark.parametrize(("run", "status_field", "nominal"), [
    (main_cli, "overall_urgency", "ROUTINE"),
    (physiology_cli, "overall_status", "NOMINAL_OPTIMAL"),
])
def test_batch_parses_false_flag(tmp_path, run, status_field, nominal):
    source = tmp_path / "input.csv"
    target = tmp_path / "output.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n"
        "T1,SYNTHETIC-1,12,4,NOMINAL,False\n"
    )
    assert run(["batch", "-i", str(source), "-o", str(target)]) == 0
    with target.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0][status_field] == nominal


@pytest.mark.parametrize("run", [main_cli, physiology_cli])
def test_batch_rejects_ambiguous_boolean(tmp_path, run, capsys):
    source = tmp_path / "input.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n"
        "T1,SYNTHETIC-1,12,4,NOMINAL,perhaps\n"
    )
    assert run(["batch", "-i", str(source), "-o", str(tmp_path / "out.csv")]) == 1
    assert "row 2" in capsys.readouterr().err


def test_http_rejects_phi_in_nested_attributes():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T1",
        "target_identifier": "SYNTHETIC-1",
        "primary_metric": 12,
        "attributes": {"nested": {"contact": "someone@example.com"}},
    })
    assert response.status_code == 422
    assert "someone@example.com" not in response.text
