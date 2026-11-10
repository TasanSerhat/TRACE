# Shared Formats and Rules

Member 1 writes the data, Members 2 and 3 read it, so these rules must be followed exactly.
If something here is wrong or missing, tell the team and fix this file in a PR.

## 1. Record

Fields (see `contracts/models.py`): `sequence_no` (int), `timestamp` (float, epoch seconds),
`source_id` (str: `FDR`, `TELEMETRY`, `NAVIGATION`), `data` (dict of float), `prev_hash`, `hash`.

- Sequence numbers start at 1 and increase by 1 for each source. Rate is 1 Hz.
- Data keys for the MVP: `altitude_ft`, `speed_kt`.

## 2. Hash chain

```python
GENESIS_HASH = "0" * 64  # prev_hash of the first record of a source


def compute_hash(prev_hash, sequence_no, timestamp, source_id, data):
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
```

The chain is per source: `prev_hash` of record i is `hash` of record i-1 of the same source.
`compute_hash` lives in `src/trace_engine/contracts/hashing.py` so recorder and verifier share one copy.

## 3. Checkpoint (every N records, default 100)

- Leaves are the `hash` values of records `start_seq..end_seq` of one source.
- Merkle parent = `sha256(left_bytes + right_bytes)`; if a level has an odd count, the last node is duplicated.
- `merkle_root` is hex; `signature_hex` is the Ed25519 signature over the raw root bytes.
- The public key (hex) goes into `configs/default_rules.json` (`public_key_hex`).

## 4. Files

One folder per scenario run, for example `output/s01/`:

| File | Content |
|---|---|
| `fdr.json`, `telemetry.json`, `navigation.json` | JSON list of record objects (fields above) |
| `fdr.csv`, ... | same records as CSV; columns `sequence_no,timestamp,source_id,altitude_ft,speed_kt,prev_hash,hash` |
| `checkpoints.json` | JSON list of checkpoint objects |
| `labels.json` | ground truth written by the injector: list of `{"scenario": "S-01", "source_id": ..., "start_seq": ..., "end_seq": ..., "expected_code": ...}` |
| `report.json` | audit output: list of findings (fields of `AuditFinding`) |

`output/` is git-ignored: generated data is never committed.

## 5. Module functions

Each module exposes plain functions; no classes are required. Inputs and outputs use the
objects from `contracts/models.py`. All analyzers return `list[AuditFinding]`.

| Owner | Module | Function |
|---|---|---|
| 3 | `data/ingestor.py` | `load_records(path) -> list[InternalRecord]` (raises or returns `UNSUPPORTED_FORMAT_ERROR` / `SCHEMA_VALIDATION_ERROR` findings) |
| 3 | `data/ingestor.py` | `load_checkpoints(path) -> list[SignedCheckpoint]` |
| 3 | `data/exporter.py` | `export_report(findings, path) -> None` |
| 3 | `application/orchestrator.py` | `run_audit(paths, rules) -> list[AuditFinding]` (the 6 steps of ARCHITECTURE.md 4.4) |
| 1 | `domain/integrity.py` | `verify_integrity(records, checkpoints, rules) -> list[AuditFinding]` |
| 2 | `domain/continuity.py` | `check_order(records)`, `normalize(records) -> list[InternalRecord]`, `check_continuity(records)`, `check_recoverability(gap_findings, backup_streams)` |
| 2 | `domain/consistency.py` | `check_consistency(streams, rules)` |
| 1 | `simulation/generator.py` | `generate(num_records) -> dict[str, list[InternalRecord]]` (keyed by source_id) |
| 1 | `simulation/recorder.py` | `chain_and_checkpoint(records, rules, private_key) -> (records, checkpoints)` |
| 1 | `simulation/injector.py` | one function per scenario S-01..S-07, plus label writing |

Signatures may be extended if needed (add parameters, do not rename) - tell the others in the PR.
