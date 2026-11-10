"""Immutable data objects passed between layers (ARCHITECTURE.md Sections 3.1, 4.3, 4.6)."""

from dataclasses import dataclass

from .codes import FindingCode


@dataclass(frozen=True)
class InternalRecord:
    sequence_no: int
    timestamp: float  # epoch seconds
    source_id: str  # e.g. "FDR", "TELEMETRY", "NAVIGATION"
    data: dict[str, float]  # e.g. {"altitude_ft": 10020.0, "speed_kt": 445.0}
    prev_hash: str
    hash: str


@dataclass(frozen=True)
class SignedCheckpoint:
    source_id: str
    start_seq: int
    end_seq: int
    merkle_root: str  # hex
    signature_hex: str  # Ed25519 signature over merkle_root


@dataclass(frozen=True)
class AuditFinding:
    """Carries the evidence fields required by NFR-06."""

    finding_code: FindingCode
    source_id: str
    start_seq: int
    end_seq: int
    event_timestamp: float
    expected_value: str | None
    observed_value: str | None
    message: str


@dataclass(frozen=True)
class AuditRules:
    """Defaults from ARCHITECTURE.md Section 4.6; also stored in configs/default_rules.json."""

    checkpoint_interval_n: int = 100
    public_key_hex: str = ""
    clock_skew_ms: float = 500.0
    altitude_tolerance_ft: float = 50.0
    speed_tolerance_kt: float = 5.0
