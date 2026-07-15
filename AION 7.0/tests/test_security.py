import pytest
from src.security.aip_registry import AIPRegistry
from src.security.abac import ABACEngine
from src.security.audit import MerkleChainAudit
from src.security.sanitization import PIISanitizer


def test_aip_register():
    registry = AIPRegistry()
    result = registry.register_agent("#99", "Test Agent", "admin")
    assert result["status"] == "active"
    assert registry.verify_agent("#99") is True


def test_aip_revoke():
    registry = AIPRegistry()
    registry.register_agent("#99", "Test Agent", "admin")
    registry.revoke_agent("#99")
    assert registry.verify_agent("#99") is False


def test_abac_allow():
    abac = ABACEngine()
    result = abac.evaluate({"role": "admin"}, "delete", {"type": "agent:#1"})
    assert result is True


def test_abac_deny():
    abac = ABACEngine()
    result = abac.evaluate({"role": "anonymous"}, "delete", {"type": "agent:#1"})
    assert result is False


def test_merkle_chain():
    audit = MerkleChainAudit()
    h1 = audit.add_entry("#1", "execute", {"input": "test"})
    h2 = audit.add_entry("#2", "execute", {"input": "test2"})
    assert audit.verify_chain() is True


def test_sanitization():
    sanitizer = PIISanitizer()
    text = "CPF: 123.456.789-00, Email: user@test.com"
    result = sanitizer.sanitize(text)
    assert "123.456.789-00" not in result
    assert "user@test.com" not in result
