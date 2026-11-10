# TRACE

**Tamper-Resistant Record Audit & Cross-source Evidence Engine**: an audit engine for safety-critical event records, using a hash chain, signed Merkle checkpoints and cross-source consistency analysis. Case study: flight data (simulated).

- Design and requirements: [ARCHITECTURE.md](ARCHITECTURE.md) (source: `docs/TRACE_Feasibility_Report_v4_EN.docx`)
- Team workflow and setup: [CONTRIBUTING.md](CONTRIBUTING.md)

## Structure
```
src/trace_engine/
  contracts/     shared data models and finding codes
  presentation/  CLI                                   (Member 3)
  application/   AuditOrchestrator                     (Member 3)
  domain/        integrity / continuity / consistency  (Members 1, 2)
  data/          ingestor, exporter                    (Member 3)
  simulation/    generator, recorder, injector         (Member 1)
configs/         default audit rules
tests/           unit, scenarios (S-01..S-07), benchmarks
```

## Team
| Member | Branch | Scope |
|---|---|---|
| 1 | `feat/sim-and-integrity` | simulation + integrity verification (FR-04, FR-05) |
| 2 | `feat/continuity-and-consistency` | continuity + consistency (FR-06..FR-11) |
| 3 | `feat/ingestion-and-orchestrator` | ingestor, orchestrator, exporter, CLI (FR-01..03, FR-13, FR-14) |
