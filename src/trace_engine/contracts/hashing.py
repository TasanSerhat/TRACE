"""Shared hash function used by the recorder and the verifier (docs/SHARED_FORMATS.md, section 2)."""

import hashlib
import json

GENESIS_HASH = "0" * 64  # prev_hash of the first record of a source


def compute_hash(
    prev_hash: str, sequence_no: int, timestamp: float, source_id: str, data: dict[str, float]
) -> str:
    payload = "|".join(
        [
            prev_hash,
            str(sequence_no),
            f"{timestamp:.3f}",
            source_id,
            json.dumps(data, sort_keys=True, separators=(",", ":")),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
