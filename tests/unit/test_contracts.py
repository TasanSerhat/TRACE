import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from trace_engine.contracts.codes import FindingCode
from trace_engine.contracts.hashing import GENESIS_HASH, compute_hash
from trace_engine.contracts.models import AuditRules, InternalRecord


def test_finding_codes_count():
    assert len(FindingCode) == 16


def test_record_is_immutable():
    record = InternalRecord(1, 0.0, "FDR", {"altitude_ft": 1.0}, GENESIS_HASH, "x")
    with pytest.raises(FrozenInstanceError):
        record.sequence_no = 2


def test_compute_hash_is_deterministic():
    a = compute_hash(GENESIS_HASH, 1, 100.0, "FDR", {"altitude_ft": 10000.0, "speed_kt": 440.0})
    b = compute_hash(GENESIS_HASH, 1, 100.0, "FDR", {"speed_kt": 440.0, "altitude_ft": 10000.0})
    assert a == b and len(a) == 64


def test_default_rules_file_matches_dataclass():
    path = Path(__file__).parents[2] / "configs" / "default_rules.json"
    assert AuditRules(**json.loads(path.read_text())) == AuditRules()
