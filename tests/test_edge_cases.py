"""
Edge case tests for Digital Twin Physiological Simulator.
Tests security hardening, input validation, and error handling.
"""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor
from physiotwin_simulator.engine import FrontierDomainEngine
from cli import main


class TestNaNInfValidation:
    """Test that NaN and Inf values are rejected."""

    def test_nan_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"))

    def test_inf_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("inf"))

    def test_neg_inf_secondary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0, secondary_metric=float("-inf"))

    def test_valid_finite_values_accepted(self):
        p = SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0, secondary_metric=5.0)
        assert p.primary_metric == 10.0
        assert p.secondary_metric == 5.0

    def test_engine_rejects_nan_primary(self):
        with pytest.raises(ValueError, match="finite"):
            FrontierDomainEngine.evaluate_primary_parameter(float("nan"))

    def test_engine_rejects_inf_secondary(self):
        with pytest.raises(ValueError, match="finite"):
            FrontierDomainEngine.evaluate_secondary_kinetics(float("inf"), False)


class TestPHIGuardRedaction:
    """Test PHI guard redaction functionality."""

    def test_redact_phi_mrn(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678")
        assert "MRN-12345678" not in result
        assert "[REDACTED_IDENTIFIER]" in result

    def test_redact_phi_ssn(self):
        result = PHIGuard.redact_phi("SSN: 123-45-6789")
        assert "123-45-6789" not in result

    def test_redact_phi_email(self):
        result = PHIGuard.redact_phi("Contact user@example.com for info")
        assert "user@example.com" not in result

    def test_clean_text_unchanged(self):
        clean = "Analytical assay specimen KEY-001 optimal"
        assert PHIGuard.redact_phi(clean) == clean


class TestAuditTrailSecurity:
    """Test audit trail security improvements."""

    def test_audit_trail_without_secret_uses_ephemeral_key(self):
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail(secret_key=None)
            # Check that a warning was issued
            assert any("AUDIT_SECRET_KEY" in str(warning.message) for warning in w)
        assert trail.secret_key != b""

    def test_audit_trail_with_explicit_key(self):
        trail = AuditTrail(secret_key="my-secret-key")
        assert trail.secret_key == b"my-secret-key"

    def test_audit_trail_integrity_verification(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "TEST_EVENT", {"data": "value1"})
        trail.log("actor2", "tier2", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_trail_detects_tampering(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor1", "tier1", "TEST_EVENT", {"data": "value1"})
        trail.log("actor2", "tier2", "TEST_EVENT", {"data": "value2"})
        # Tamper with the chain
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False


class TestCLIErrorHandling:
    """Test CLI error handling for file operations."""

    def test_batch_missing_file_returns_error(self):
        result = main(["batch", "-i", "nonexistent_file.csv"])
        assert result == 1

    def test_batch_with_valid_file(self, tmp_path):
        # Create a temporary CSV file
        csv_file = tmp_path / "test_input.csv"
        csv_file.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nTASK-01,TARGET-01,12.0,4.0,False,NOMINAL\n")
        output_file = tmp_path / "test_output.csv"
        result = main(["batch", "-i", str(csv_file), "-o", str(output_file)])
        assert result == 0
        assert output_file.exists()


class TestSupervisorEdgeCases:
    """Test supervisor with edge case inputs."""

    def test_supervisor_with_boundary_values(self):
        supervisor = SystemSupervisor(model_provider="mock")
        # Test with exactly the threshold value
        payload = SystemTaskPayload(
            task_id="BOUNDARY-01",
            target_identifier="KEY-01",
            primary_metric=25.0,  # Exactly at threshold
            secondary_metric=12.0,  # Exactly at threshold
            status_descriptor="NOMINAL"
        )
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.ROUTINE

    def test_supervisor_with_extreme_values(self):
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="EXTREME-01",
            target_identifier="KEY-01",
            primary_metric=1e6,  # Very large value
            secondary_metric=0.001,  # Very small value
            status_descriptor="NOMINAL"
        )
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.ELEVATED
