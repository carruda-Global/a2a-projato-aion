import pytest
from src.quality.gates import QualityGates
from src.quality.kalibra_integration import KalibraIntegration


def test_quality_gates_pass():
    gates = QualityGates()
    result = gates.check({"coverage": 95, "security_issues": 0, "duplication": 1}, "#1")
    assert result["passed"] is True


def test_quality_gates_fail():
    gates = QualityGates()
    result = gates.check({"coverage": 50, "security_issues": 2, "duplication": 10}, "#1")
    assert result["passed"] is False


@pytest.mark.asyncio
async def test_kalibra_baseline():
    kalibra = KalibraIntegration()
    result = await kalibra.check_regression({"response_time_ms": 100}, "#1")
    assert result["passed"] is True
    assert result["report"]["baseline_established"] is True
