# **TRACE** 

Cryptographic Integrity, Continuity and Cross-Source Consistency Verification System for Safety-Critical Event Records 

Project Feasibility and Introduction Document  ·  Software Engineering Course  ·  Group Working Document  ·  v4 

|**Project name**|TRACE — Tamper-Resistant Record Audit & Cross-source Evidence Engine|
|---|---|
|**Project type**|Security- and safety-oriented system / software engineering project (not a commercial<br>product; problem-solution oriented)|
|**Case study**|Flight data recording systems (FDR, telemetry, navigation) — entirely on simulation|
|**Generalization goal**|Adaptability of the same audit engine to industrial (PLC/SCADA), autonomous vehicle<br>and satellite event records|
|**Solution approach**|Hash chain + signed Merkle checkpoints + cross-source consistency analysis|
|**Version**|v4 — Requirements kept in plain language (Sections 5–8); Section 4 was extended per<br>the L5 (Software Design) and L6 (Software Architecture Patterns) course content with<br>Architecture Pattern Selection, Component, Data and Behavioral Design, and Design<br>Principles (Coupling / Cohesion). The work split was redone for a 3-person group; the<br>discussion questions were resolved and merged into the document.|
|**Purpose of the document**|To settle the project's scope, requirements, architecture and work split (for a 3-person<br>group) and to provide a basis for the presentation|



## **1. Executive Summary** 

After an accident or a security incident, if we hold digital records, how far can we trust them? TRACE is an audit engine, independent of the source systems, that answers this question along three axes: 

- **Integrity:** Were the records modified, deleted, injected with forged records, reordered or duplicated afterwards? 

- **Continuity and recoverability:** Which record range is missing, and does that range exist in another trustworthy source? 

- **Cross-source consistency:** Do cryptographically valid records contain values that physically contradict each other? 

TRACE does not interfere with the hardware or software of the source systems. It works on simulated multi-source data and, using a hash chain, signed checkpoints and tolerance-based sensor comparison, produces a **forensic audit report** . Flight data is only the case study; the engine itself is designed generically. 

The engineering value of the project lies not in applying encryption or hashing on its own, but in a clearly defined problem, separated actor roles, atomic and testable requirements, and the **verification of injected faults through automated measurement** . 

TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 1 

## **2. Problem Definition (Problem Space)** 

### **2.1 Problem** 

Safety-critical systems produce large amounts of event data. After a failure or a security incident, it must be determined whether the records at hand are **complete, authentic, unmodified and mutually consistent** . This uncertainty breaks down into three root problems: 

- **Lack of non-repudiation:** It is hard to prove that a recovered record was not changed, deliberately or accidentally, between the moment of recovery and the moment of examination. 

- **Uncertainty about loss and gaps:** When data is interrupted, it must be shown systematically which range is missing and whether that range exists in another source. 

- **Valid but wrong data:** A record can be signed and unmodified, yet a faulty sensor or a deceived subsystem may have produced a wrong value. Cryptography alone cannot catch this. 

### **2.2 Dimensions of the Problem Space** 

|**Dimension**|**Question to be answered**|**TRACE component**|
|---|---|---|
|**Integrity**|Was it modified? Deleted? Was a record inserted?<br>Was the order broken? Was it duplicated?|Hash chain + signed checkpoint|
|**Continuity /**|Which range is missing? Does the same data exist|Gap and recoverability analyzer|
|**i**<br>**Availability**|in a secondary source?||
|**Consistency**|Do the sources report the same physical<br>phenomenon with compatible values?|Cross-source consistency analyzer|



### **2.3 Research / Engineering Question** 

##### **Core question** 

When partial data loss or tampering is suspected, how can the **integrity, continuity, authenticity and crosssource consistency** of safety-critical event data be verified with cryptographic and analytic methods, and what is the time and storage cost of this verification? 

## **3. Solution Space** 

### **3.1 Approach** 

- **Independent audit layer:** Source systems are not modified; the audit is a separate layer added on top of the records. 

- **Append-only hash chain:** Each record contains the hash of the previous record; a single change in the past breaks the chain. 

- **Signed checkpoints:** A Merkle root is computed every N records and signed with Ed25519. Even if an attacker recomputes the hash chain from scratch, they cannot produce a valid signature. 

- **Multi-source redundancy:** The recoverability of lost segments is analyzed by comparing the primary recorder, the secondary recorder and the ground-station checkpoint. 

TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 2 

- **Cross-consistency engine:** Values reported by simultaneous sources for the same quantity are compared against defined tolerance thresholds. 

- **Standard libraries:** No cryptographic algorithm is invented; mature libraries (e.g. Python cryptography, Java BouncyCastle) are used for SHA-256 and Ed25519. 

Chain rule: 

Hi = SHA-256( Hi−1 ‖ Seqi ‖ Timestampi ‖ Sourcei ‖ Datai ) 

Record structure held by the audit layer: 

|**Field**|**Purpose**|
|---|---|
|sequence_no|Continuity and ordering check; gap and duplicate detection|
|timestamp|Time ordering and cross-source pairing|
|source_id|Which source the record came from (FDR, telemetry, navigation…)|
|data|Sensor / event payload (altitude, speed, engine RPM, etc.)|
|prev_hash|Chain link|
|hash|The record's digest in the chain|



### **3.2 Threat Model and Assumptions** 

To keep clear what the guarantees cover, we start the project with the following assumptions: 

- **A1:** Signed checkpoints (or their digests) are stored in a separate trust domain that an attacker with access to the record files cannot reach (e.g. ground station / separate store). 

- **A2:** The signing private key cannot be captured by the attacker. Key management infrastructure (HSM etc.) is outside the project scope. 

- **A3:** The attacker can modify the record files afterwards (modification, deletion, insertion, reordering, duplication) but cannot produce a valid signed checkpoint. 

- **A4:** The clocks of the sources are approximately synchronized; clock skew (Δt) is a configurable tolerance parameter. 

### **3.3 Why Is Blockchain Not Used?** 

The distinguishing feature of a blockchain is distributed consensus. In this problem, several mutually distrusting parties do not need to agree on a shared ledger; a single audit layer is sufficient. A hash chain, a Merkle tree and a digital signature provide the required tamper-evident structure with lower latency and storage overhead. Adding a blockchain would needlessly enlarge the project and scatter its focus. 

TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 3 

### **3.4 Scope** 

|**In scope**|**Out of scope**|
|---|---|
|Synthetic multi-source data generator|Real black-box hardware and proprietary record formats|
|Fault / attack injector (with ground-truth labels)|Encryption for record confidentiality (AES-GCM) — the|
|Hash chain and signed checkpoint layer (simulated)|main problem is integrity and consistency|
|Integrity, continuity, recoverability and cross-|Key management infrastructure (HSM, PKI)<br>i i|
|consistency analysis|Embedded / real-time operation|
|Forensic report (JSON) and status-coded timeline|Distributed consensus (blockchain)|
|summary<br>i|Cryptographic recovery of lost data (not possible)|
|Performance and detection-rate measurements|Root-cause / intent detection|



## **4. System Architecture and Software Design (L5 & L6)** 

The table below gives an overview of the system's subsystems (simulation, secure recording, audit engine, reporting). The internal design of the audit engine is given in Sections 4.1–4.5 (architecture pattern, components, data, behavior and design principles); technical decisions and the code dictionary are in Sections 4.6–4.7. 

|**Subsystem**|**Components**|**Responsibility**|
|---|---|---|
|**1. Simulation**|Synthetic flight data generator<br>Fault / attack injector|Produces simultaneous streams for FDR,<br>telemetry and navigation; injects controlled<br>anomalies after recording and writes what was<br>injected to a label file.|
|**2. Secure recording**<br>**(simulated)**|Hash chain writer<br>Checkpoint generator (Merkle root +<br>Ed25519)|Chaining at recording time and periodic signed<br>checkpoints. A module independent of the<br>audit engine.|
|**3. TRACE audit engine**|Parser and schema validator<br>Integrity and continuity auditor<br>Gap and recovery analyzer<br>Cross-consistency analyzer|Validates the record files, classifies anomalies<br>by type and produces evidence.|
|**4. Reporting**|Forensic report generator<br>Timeline summary (CLI or simple<br>dashboard)|Green (safe), yellow (source inconsistency), red<br>(tampering / deletion) display and the JSON<br>forensic report.|



##### **Design note: measurability** 

Because the injector simulates the attacker, it interferes with the output of the recording layer from outside and writes what it did to a label file. The audit engine's report is automatically compared with these labels; thus the detection rate and the false alarm rate are measured in a repeatable way rather than by hand. 

### **4.1 Architecture Pattern Selection and Justification (L6 — Architecture Patterns)** 

The TRACE system uses a **Modular Monolith** pattern structured with **Layered Architecture** principles and a **Stateless** processing model. The patterns examined in L6 were selected or rejected for the reasons below: 

TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 4 

|**Architecture pattern (L6)**|**TRACE decision**|**Engineering justification**|
|---|---|---|
|**Layered Modular**<br>**Monolith**|**Selected**(main<br>architecture)|All verification components run in a single process (in-process).<br>Because there is no network latency, verifying 100,000 records in<br>under 3 seconds (NFR-01) is achievable. Splitting the internal<br>structure into layers avoids the tight coupling of a classic<br>monolith.|
|**Stateless model**|**Selected**<br>(processing model)|The audit engine keeps no state in memory between runs. This<br>guarantees that the same input and rules produce exactly the<br>same result on every run (NFR-03 repeatability).|
|**Three-Tier / Client-**<br>**Server**|**Suitable**(for UI<br>separation)|The user interface (CLI or web dashboard — Presentation Tier),<br>the audit engine (Application / Logic Tier) and the record files<br>(Data Tier) are kept separate.|
|**Microservice**<br>**Architecture**|**Rejected**|Splitting components into separate network services adds<br>serialization, network latency and deployment complexity; it puts<br>the NFR-01 performance target at risk.|
|**Serverless (FaaS)**|**Rejected**|Container start-up latency (cold start) and dependence on<br>external cloud infrastructure are unsuitable for offline forensic<br>examination scenarios.|
|**Peer-to-Peer (P2P)**|**Rejected**|The absence of a central authority and the need for distributed<br>consensus (like the blockchain rejected in Section 3.3) create<br>unnecessary complexity for a single audit engine.|



### **4.2 Layered Architecture and Component Design (L5 — Architectural & Component Design)** 

The system is divided, with a one-way top-down dependency rule, into 4 layers and 7 main components with high cohesion. An upper layer only calls the interfaces offered by lower layers; a lower layer does not know the upper layer. 

|**Layer**|**Component**|**Responsibility (internal logic)**|**Provided interface**|**Required interface**|
|---|---|---|---|---|
|**1.**<br>**Presentation /**<br>**UI**|AuditCLI/<br>DashboardView|Takes file and rule inputs from<br>the user; visualizes the report<br>and the color-coded timeline<br>(FR-14).|User command / screen<br>interaction|AuditOrchestrator|
|**2. Application**|AuditOrchestrator|Coordinates the audit pipeline<br>in the correct order; manages<br>fault isolation when a source is<br>corrupted (NFR-04).|runAudit(files, config)|All domain analyzers,<br>RecordIngestor,<br>ReportExporter|
|**3. Domain /**<br>**Business logic**|IntegrityVerifier|Verifies the digest chain<br>(FR-04) and the signed<br>checkpoints (FR-05).|verifyIntegrity(stream,<br>checkpoints)|Standard cryptography<br>library (NFR-08)|
|**3. Domain /**<br>**Business logic**|ContinuityAnalyzer|Catches order violations, time<br>going backwards and duplicate<br>records (FR-06); determines<br>gaps and recoverability from<br>backups (FR-07, FR-08).|checkOrder(stream),<br>checkContinuity(stream)<br>,<br>checkRecoverability(gap<br>s, backups)|Sorted internal record<br>stream|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 5 

|**Layer**|**Component**|**Responsibility (internal logic)**|**Provided interface**|**Required interface**|
|---|---|---|---|---|
|**3. Domain /**<br>**Business logic**|ConsistencyAnalyzer|Pairs sources within a time<br>window (FR-09); detects<br>deviations (FR-10) and the<br>suspect source (FR-11).|checkConsistency(aligne<br>dStreams, rules)|Time-aligned<br>measurement values|
|**4. Data /**<br>**Persistence**|RecordIngestor<br>(adapter)|Reads different file formats<br>and converts them into the<br>standard internal structure<br>(FR-01 – FR-03, NFR-07).|loadRecords(path)|File system (CSV /<br>JSON)|
|**4. Data /**<br>**Persistence**|ReportExporter|Exports the findings as a<br>structured audit report<br>(FR-13).|exportReport(findings)|File system (JSON)|



_Note: The simulation, the fault injector and secure recording (hash chain writer) are independent test-generator components located outside the audit engine (Section 4 overview table)._ 

### **4.3 Data Design (L5 — Data Design)** 

In line with the L5 methodology, data design is defined through the **data at rest / data in motion** distinction and **3 levels of abstraction** . 

|**Data state**|**Counterpart in TRACE**|
|---|---|
|**Data at Rest (persistent**|Raw event record files, signed checkpoint files, the rule configuration file and the final<br>i|
|**data)**|audit report are stored on disk, file-based.|
|**Data in Motion (data in**<br>**l**|RecordIngestorreads the data and passes it between layers in memory as immutable|
|**flight)**|InternalRecordandAuditFindingdata objects.|



|**Data model level**|**Content**|
|---|---|
|**Conceptual**|The system has 5 core entities: Data Source, Event Record, Checkpoint, Audit Finding,<br>Audit Report.<br>Relationships: Source → Record (1:N); Checkpoint → Record (1:N); Finding → Audit<br>Report (N:1). A checkpoint carries the record range it covers, the Merkle root and the<br>signature.|
|**Logical**|Technology-independent: each Event Record is identified by the composite key<br>(source_id, sequence_no). Each Audit Finding contains the 5 mandatory attributes<br>required by NFR-06: finding type, source ID, start / end range, event time, expected /<br>observed value.|
|**Physical**|Instead of a heavy database management system (DBMS), the NFR-01 target (under 3<br>seconds) is met by using**CSV and JSON files**for input / output and, at runtime,**in-**<br>**memory arrays / hash maps indexed by source ID and sequence number**.|



### **4.4 Behavioral Design and Runtime Audit Order (L5 — Behavioral Design)** 

To prevent false alarms (phantom gaps), the order in which components interact at runtime and the states the data passes through are bound to the following **deterministic 6-step workflow** : 

1. **Rule and key loading:** AuditOrchestrator validates the configuration parameters (FR-12); if a setting is invalid, it stops the process before starting. 

TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 6 

2. **Isolated data reading:** RecordIngestor reads the source files (FR-01 – FR-03). If a source is completely corrupted, it logs the error and continues with the healthy sources (NFR-04). 

3. **Integrity, order and duplicate check on the raw stream:** While the records are still in their original file order, IntegrityVerifier (FR-04, FR-05) runs first, followed by the order / duplicate check (FR-06) inside ContinuityAnalyzer. 

4. **Sorting and de-duplication (normalization):** 1002, 1004, 1003 — displaced records like these must not trigger a false “missing record” warning, so the stream is sorted by sequence number and duplicates are removed. Findings produced in the previous step are preserved and go into the report. 

5. **Gap, recoverability and cross-consistency analysis:** On the normalized stream, missing ranges (FR-07) and recoverability from backup sources (FR-08) are determined; cross-source deviations (FR-09 – FR-11) are computed in simultaneous windows. If all three sources diverge from one another, no majority exists, so an “ambiguous conflict” is recorded. 

6. **Report and timeline generation:** All findings are merged and a structured report (FR-13) and a Green / Yellow / Red status timeline (FR-14) are exported. 

This order eliminates the risk of phantom gaps arising from the dependency between FR-06 and FR-07; the S-04 success criterion “no false missing range is produced” is the test of this workflow. 

### **4.5 Application of Software Design Principles (L5 — Design Principles)** 

The 7 core design principles of the L5 course content are made concrete in the TRACE architecture as follows: 

|**Design principle (L5)**|**Concrete counterpart in the TRACE project**|
|---|---|
|**1. Modularisation (Divide &**<br>**Conquer)**|The system is divided into independently developable and testable modules:<br>simulation, data loading, integrity, continuity, consistency and reporting.|
|**2. Abstraction (procedural &**<br>**data)**|**Data abstraction:**Raw CSV / JSON lines are represented by theInternalRecord<br>abstraction.<br>**Procedural abstraction:**Complex verification steps are abstracted behind clear<br>operations such asverifyIntegrity().|
|**3. Encapsulation (information**<br>**hiding)**|The details of cryptographic digest computation and Merkle tree construction<br>are encapsulated insideIntegrityVerifier; external modules only see the<br>verification result.|
|**4. Low Coupling**|**Content, Common and Control coupling are forbidden:**Modules do not use<br>shared global variables and do not interfere with each other's internal code or<br>flow.<br>**External coupling is isolated:**File format dependence is kept only in the<br>RecordIngestoradapter (NFR-07).<br>**Data and Message coupling are used:**Analyzers receive only the data fields they<br>need (InternalRecord) and return standardAuditFindingmessages.|
|**5. High Cohesion**|Each module focuses on a single purpose (e.g.ConsistencyAnalyzerdoes not<br>verify cryptographic signatures; it only compares sensor values).|
|**6. Sufficiency**|Each analyzer module contains within itself all the algorithmic logic and<br>parameters it needs to make its own audit decision.|
|**7. Completeness**|The union of the designed modules covers all 7 defined user stories, 14<br>functional requirements and 8 non-functional requirements, leaving no item<br>uncovered (Section 7).|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 7 

### **4.6 Technical Design Decisions** 

The requirements in Sections 5–8 are deliberately written to be technology-independent. The concrete choices on how we will meet the requirements (file format, algorithm, parameter symbols, measurement environment) are collected in one place, below. The choices settled in the group meeting (the “Group decision” rows) are also included in this table. If a choice changes, only this table is updated. 

|**Topic**<br>**Input file formats**|**Choice**<br>CSV and JSON|**Related requirement**<br>FR-01, FR-03|
|---|---|---|
|**Mandatory record fields**|Each record carries these fields: sequence_no, timestamp,<br>source_id, data, prev_hash, hash (see Section 3.1)|FR-02|
|**Change detection**|Chain digest with SHA-256: each record's digest is bound<br>to the previous record's digest|FR-04|
|**Checkpoint**|A binary Merkle tree root is computed every N records and<br>signed with Ed25519|FR-05|
|**Configurable parameters**|Checkpoint interval (N), trusted public key, clock-skew<br>window (±Δt), measurement tolerance threshold (±ε)|FR-09, FR-10, FR-12|
|**Report format**|JSON forensic report; the timeline is shown via CLI or a<br>simple dashboard|FR-13, FR-14|
|**Finding and error codes**|The dictionary in Section 4.7|FR-02 – FR-12|
|**Performance reference**<br>**environment**|4-core CPU, 16 GB RAM; mature standard libraries for<br>digest and signature operations|NFR-01, NFR-08|
|**Storage overhead**<br>**measurement**|prev_hash + hash + checkpoint signature share ≤ 160 B /<br>record|NFR-02|
|**Repeatability and fault**<br>**isolation measurement**|Comparison of the output JSON's digest (hash) (100 runs);<br>process exit code 0 when a corrupted source is injected|NFR-03, NFR-04|
|**Extensibility**|The parser layer is abstracted behind an adapter interface;<br>0 lines changed in the core audit modules|NFR-07|
|**Group decision:**<br>**development language**|Python 3. hashlib is used for SHA-256 and the<br>cryptography library for Ed25519. The 3-second target for<br>100,000 records is verified by a performance trial in the<br>first phase; if necessary, heavy steps are accelerated with<br>vectorized operations.|NFR-01, NFR-08|
|**Group decision: case study**<br>**and generalization**|The main case is flight data. The generalization claim is<br>shown by auditing a small second record schema (e.g. an<br>industrial sensor record, CSV) with an additional<br>RecordIngestor adapter; no changes are made to the audit<br>modules.|NFR-07|
|**Group decision: MVP**<br>**boundary**|All Must requirements (FR-01 – FR-11, FR-13) form the<br>MVP. The Should items FR-12 (comprehensive setting<br>validation), FR-14 (color-coded timeline) and the second<br>adapter are stretch goals. In the MVP, parameters are read<br>with their default values from a configuration file.|FR-12, FR-14|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 8 

|**Topic**|**Choice**|**Related requirement**|
|---|---|---|
|**Group decision: audit order**|First the order and duplicate check (in source order), then<br>gap analysis on the sorted and de-duplicated stream<br>(Section 4.4).|FR-06, FR-07|
|**Group decision: cross-**<br>**checked quantities**|Altitude and speed are checked in the MVP; engine RPM is<br>a stretch goal. Initial deviation limits: altitude ±50 ft, speed<br>±5 knots.|FR-09, FR-10, FR-11|
|**Group decision: ε and Δt**<br>**values**|Clock skew Δt = ±500 ms (assuming a 1 Hz recording rate).<br>The deviation limits (ε) start from the values above; they<br>are calibrated so that the number of false alarms on clean<br>simulation data is 0, and the result is reported with the<br>metric in Section 8.2.|FR-09, FR-10, FR-12|
|**Group decision: if all three**<br>**sources diverge**|Since no majority forms, no source is flagged as suspect;<br>the range is recorded as an “ambiguous conflict” and the<br>report shows the values of all three sources together. The<br>FR-11 text does not change; this case falls into the same<br>class as the two-source ambiguity.|FR-11|
|**Group decision:**<br>**confidentiality**|Confidentiality (AES-GCM) is out of scope (Section 3.4); the<br>main problem is integrity and consistency.|—|
|**Group decision: code**<br>**dictionary**|The dictionary in Section 4.7 is kept as a design detail<br>without simplification. Requirements and acceptance<br>criteria use only plain wording; the codes are for<br>development and testing.|FR-02 – FR-12|
|**Group decision:**<br>**presentation responsibility**|The slides for the second presentation are prepared<br>according to the simplified tables in this document; each<br>member writes the slides for their own module, and<br>Member 3 compiles them and does the final check (Section<br>9.5).|—|



### **4.7 Finding and Error Code Dictionary** 

The software-internal counterparts of the plain expressions shown to the user. Requirements and acceptance criteria use only the expressions on the left; the codes are a design detail to be consulted during development and testing. 

|**Expression shown to the user**|**Internal code**|**Related requirement**|
|---|---|---|
|**Incomplete record notification**|SCHEMA_VALIDATION_ERROR|FR-02|
|**Rejection of unsupported /**<br>**unreadable file**|UNSUPPORTED_FORMAT_ERROR|FR-03|
|**Verified (no change)**|INTEGRITY_VERIFIED|FR-04|
|**Integrity violation warning**|HASH_CHAIN_MISMATCH|FR-04|
|**Forgery (signature violation) warning**|CHECKPOINT_SIGNATURE_INVALID|FR-05|
|**Order violation**|SEQUENCE_ORDER_ANOMALY|FR-06|
|**Time-flow violation**|TIMESTAMP_MONOTONICITY_ANOMALY|FR-06|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 9 

|**Expression shown to the user**|**Internal code**|**Related requirement**|
|---|---|---|
|**Duplicate record**|DUPLICATE_RECORD_DETECTED|FR-06|
|**Missing record range**|SEQUENCE_GAP_DETECTED|FR-07|
|**Recoverable from backup**|RECOVERABLE_FROM_SECONDARY|FR-08|
|**Unrecoverable**|UNRECOVERABLE_GAP|FR-08|
|**Consistent (no deviation)**|CONSISTENT|FR-10|
|**Cross-source disagreement warning**|CROSS_SOURCE_DIVERGENCE|FR-10|
|**Suspect source**|SUSPECT_SOURCE|FR-11|
|**Ambiguous conflict**|AMBIGUOUS_SOURCE_CONFLICT|FR-11|
|**Invalid setting warning**|INVALID_CONFIGURATION_PARAMETER|FR-12|



## **5. Actors and User Stories (L3)** 

### **5.1 Target User Roles** 

|**Role**<br>**ID**|**Role**|**Area of responsibility**|**Main goal**|
|---|---|---|---|
|**R-01**|Accident Investigator|Integrity and<br>reporting|To verify that recovered records were not tampered<br>with and to submit an evidence-based report to the<br>investigation file|
|**R-02**|Forensic Investigator|Continuity and data<br>preparation|To verify multi-source record packages; to<br>determine ordering / duplicate problems and the<br>recoverability of missing records from other sources|
|**R-03**|Flight Safety Engineer|Cross-source<br>consistency|To detect physical measurement contradictions<br>between records that passed the security checks,<br>and suspect sensors|
|**R-04**|Audit Administrator|Trusted keys and<br>rules|To configure trusted signing keys, the checkpoint<br>frequency, the permitted clock difference and the<br>measurement deviation limits|



### **5.2 Core Concepts** 

The following concepts appear in the user stories and requirements. Their plain meanings are given so that a reader who does not know the project can follow the text. 

|**Concept**|**Meaning**|
|---|---|
|**Record**|A single event line written by a system at a specific moment (e.g. the altitude and<br>speed value at that moment).|
|**Source**|The system that produces the records (e.g. flight data recorder, telemetry,<br>navigation).|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 10 

|**Concept**|**Meaning**|
|---|---|
|**Backup source**|A second system that independently records the same event; used for comparison if<br>something is missing from the main record.|
|**Security digest**|A short code that links each record to the records before it. If one of the records is<br>changed later, this link breaks and the change is noticed.|
|**Checkpoint**|A “seal” taken at certain intervals and digitally signed. Even if an attacker re-edits the<br>records from scratch, they cannot produce the valid signature.|
|**Missing record range**|Records skipped in the numbering, i.e. lost or deleted (e.g. 1245 coming directly after<br>1200).|
|**Disagreement**|Two or more independent sources reporting contradictory values for the same<br>quantity at the same time.|



### **5.3 User Stories and Acceptance Criteria (INVEST-compliant)** 

All stories are written according to the Connextra template (Role – Want – Value), sized according to the INVEST principles (Independent, Negotiable, Valuable, Estimable, Small, Testable), and each is tied to multiple Given / When / Then acceptance criteria (AC) covering both the normal flow and the error / anomaly case. The acceptance criteria are written in plain language that a reader who does not know the system can understand; technical details such as field names, error codes and algorithms are deliberately left to Sections 4.6–4.7. 

#### **US-01 — Loading and checking record files** 

|**Role**|Forensic Investigator|
|---|---|
|**Priority**|Must|
|**Story**|As a Forensic Investigator, I want to load record files from multiple sources and check that<br>they are complete and readable, so that I can filter out damaged or incomplete files before<br>the audit starts.|
|**AC-01.1**<br>**Valid file upload**|**Given**a record file containing all mandatory information is provided,<br>**When**the file is uploaded to the system,<br>**Then**the system must separate the records by the source they belong to and show the total<br>number of records read.|
|**AC-01.2**<br>**Missing information**|**Given**some records lack mandatory information such as date, sequence number or<br>measurement value,<br>**When**the file is checked,<br>**Then**the system must tell the user which information is missing in which records.|
|**AC-01.3**<br>**Unsupported file**|**Given**a file of a type the system cannot read or does not support is provided,<br>**When**the upload is started,<br>**Then**the system must reject the file and show a message explaining why.|



#### **US-02 — Verifying whether records were modified** 

|**Role**|Accident Investigator|
|---|---|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 11 

|**Priority**|Must|
|---|---|
|**Story**|As an Accident Investigator, I want to verify whether the recovered records have been<br>altered or forged since they were originally written, so that I can base the investigation on<br>trustworthy digital evidence.|
|**AC-02.1**<br>**Unmodified records**|**Given**a record package with no tampering is uploaded,<br>**When**integrity verification is run,<br>**Then**the system must mark all records as “verified”.|
|**AC-02.2**<br>**Value change and**<br>**first point of**<br>**tampering**|**Given**the altitude value of record 1042 was later changed from 10,000 ft to 7,000 ft,<br>**When**integrity verification is run,<br>**Then**the system must raise an integrity violation warning indicating the first record where<br>tampering began (1042).|
|**AC-02.3**<br>**Forged records or**<br>**signature violation**|**Given**a record group is uploaded that was re-edited from scratch after modification to look<br>consistent but is not sealed with a valid signature,<br>**When**checkpoint verification is run,<br>**Then**the system must raise a forgery (signature violation) warning for that record group.|



#### **US-03 — Detecting ordering and duplication problems** 

|**Role**|Forensic Investigator|
|---|---|
|**Priority**|Must|
|**Story**|As a Forensic Investigator, I want to detect out-of-order and duplicated records within a<br>source stream, so that I can verify the chronological fidelity of the event sequence.|
|**AC-03.1**|**Given**in a source, record 1004 appears before record 1003,|
|**Order violation**|**When**the ordering check is run,<br>**Then**the system must report these two records as an “order violation”.|
|**AC-03.2**|**Given**a record's event time appears earlier than that of the record preceding it,|
|**Time going**|**When**the ordering check is run,|
|**backwards**|**Then**the system must report this situation as a “time-flow violation”.|
|**AC-03.3**|**Given**there is more than one record with the same sequence number in the same source,|
|**Duplicate record**|**When**the duplicate check is run,<br>**Then**the system must report the duplicated record's number as a “duplicate record”.|



#### **US-04 — Analyzing lost data ranges and recoverability** 

|**Role**|Forensic Investigator|
|---|---|
|**Priority**|Must|
|**Story**|As a Forensic Investigator, I want to identify missing record intervals in a primary source and<br>check their availability in backup sources, so that I can determine which missing segments<br>are recoverable.|
|**AC-04.1**|**Given**in the primary source, record 1245 comes directly after record 1200,|
|**Missing record**|**When**gap analysis is run,|
|**range**|**Then**the system must report the range 1201–1244 as a “missing range”.|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 12 

|**AC-04.2**|**Given**the counterpart of the range 1201–1244 missing in the primary source exists verified<br>i|
|---|---|
|**Data available in a**|in a backup source (e.g. ground-station telemetry),|
|**backup source**|**When**recoverability analysis is run,|
||**Then**the system must classify this range as “recoverable from backup” and state which<br>backup source holds it.|
|**AC-04.3**|**Given**the missing record range is not present in any backup source,|
|**Unrecoverable data**|**When**recoverability analysis is run,|
|**loss**|**Then**the system must mark that range as “unrecoverable”.|



#### **US-05 — Cross-source consistency audit** 

|**Role**|Flight Safety Engineer|
|---|---|
|**Priority**|Must|
|**Story**|As a Flight Safety Engineer, I want to compare simultaneous measurements from<br>independent sources against acceptable deviation limits, so that I can identify faulty or<br>spoofed sensors even when their records pass all integrity checks.|
|**AC-05.1**<br>**Consistency within**<br>**limits**|**Given**the difference between the altitude values reported by all matched sources stays<br>within the acceptable limit (±50 ft),<br>**When**cross-source consistency analysis is run,<br>**Then**the system must mark the relevant time range as “consistent”.|
|**AC-05.2**<br>**Suspect source with**<br>**three or more**<br>**sources**|**Given**at the same moment the flight data recorder reports 10,020 ft, telemetry 10,018 ft<br>and navigation 7,420 ft, and the acceptable difference is ±50 ft,<br>**When**cross-source consistency analysis is run,<br>**Then**the system must raise a disagreement warning and flag the navigation source, which<br>diverges from the other two, as suspect.|
|**AC-05.3**<br>**Ambiguous conflict**<br>**with two sources**|**Given**in a time range with only two sources, the difference between the values exceeds the<br>acceptable limit,<br>**When**cross-source consistency analysis is run,<br>**Then**the system must raise a disagreement warning and record the situation as an<br>“ambiguous conflict”, because it cannot be determined which source is faulty.|



#### **US-06 — Configuring audit rules** 

|**Role**|Audit Administrator|
|---|---|
|**Priority**|Should|
|**Story**|As an Audit Administrator, I want to configure checkpoint frequency, trusted signing keys,<br>permitted clock difference between sources, and acceptable measurement deviation, so<br>that I can adapt the verification rules to different recording profiles without changing the<br>software.|
|**AC-06.1**<br>**Applying settings**|**Given**checkpoints are configured to occur every 100 records and the altitude deviation limit<br>is set to ±50 ft,<br>**When**a package of 1,000 records is audited,<br>**Then**the system must verify using 10 checkpoints and the ±50 ft limit.|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 13 

|**AC-06.2**|**Given**the checkpoint frequency is entered as zero or negative, or the deviation limit is|
|---|---|
|**Blocking invalid**|entered as negative,|
|**settings**|**When**the settings are read,|
||**Then**the system must show a warning indicating which setting is invalid, without starting<br>the audit.|



#### **US-07 — Reviewing the audit report and timeline** 

|**Role**|Accident Investigator|
|---|---|
|**Priority**|Must (audit report) / Should (color-coded timeline)|
|**Story**|As an Accident Investigator, I want to review a structured forensic report and a status<br>timeline of all findings, so that I can document which segments of the event log are<br>trustworthy.|
|**AC-07.1**|**Given**the audit is completed,|
|**Structured evidence**|**When**the report is exported,|
|**report**|**Then**the report must contain, for each finding, the finding type, the related source, the<br>affected record range, the event time and the evidence summary.|
|**AC-07.2**|**Given**the audit results are produced,|
|**Timeline with**<br>**ii**|**When**the timeline is generated,|
|**status classification**|**Then**each record range must be labeled Verified (green), Cross-source deviation (yellow) or<br>Integrity / continuity violation (red).|



## **6. System Requirements (L4)** 

### **6.1 Functional Requirements (FR)** 

##### **Design rule: atomicity, testability and plain language** 

Each functional requirement (FR-01 – FR-14) defines **a single discrete, atomic and directly testable** behavior with the pattern “The system shall …”. The requirements describe **what** the system will do, **not how** : they contain no field names, error codes, file formats or algorithm names, and are written in plain language that a reader who does not know the project can understand. These technical decisions are collected in Section 3 and Section 4 (4.6 and 4.7); the requirements do not change even if the technology choice changes. Each requirement contains a condition, a system behavior and an observable output (warning or report). 

#### **A. Data loading and checking** 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-01**|The system shall allow event record files from different<br>data sources to be imported.|Valid record files are<br>loaded without error<br>and separated by source|Must|US-01|
|**FR-02**|The system shall verify that each imported record<br>contains all required information (such as time, sequence<br>number, source and measured value) and notify the user<br>of any incomplete records.|A file containing<br>incomplete records is<br>reported to the user|Must|US-01|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 14 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-03**|The system shall reject unsupported or unreadable files<br>and inform the user of the reason.|Unsupported and<br>corrupted file upload<br>test|Must|US-01|



#### **B. Integrity verification** 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-04**|The system shall check whether imported records were<br>modified after being recorded and, when a modification<br>is found, raise an integrity violation alert identifying the<br>first affected record and its event time.|Scenario S-01 (value<br>modification) test|Must|US-02|
|**FR-05**|The system shall compare record groups against trusted<br>signed checkpoints and raise a forgery alert for any<br>record group whose checkpoint signature cannot be<br>verified or does not match the records.|Scenario S-03 (forged<br>record insertion) test|Must|US-02|



#### **C. Continuity, ordering and recoverability analysis** 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-06**|The system shall detect and report records that are out<br>of order within a source (for example, a newer record<br>appearing before an older one) or that appear more than<br>once.|Scenarios S-04<br>(reordering) and S-05<br>(duplication) tests|Must|US-03|
|**FR-07**|The system shall detect interruptions in a source’s record<br>stream and report each missing interval with its start and<br>end points.|Scenario S-02 (record<br>deletion) missing-range<br>test|Must|US-04|
|**FR-08**|The system shall check whether each missing interval is<br>available in verified backup sources and classify it as<br>recoverable from backup or unrecoverable.|Scenario S-06 (partial<br>data loss) recoverability<br>test|Must|US-04|



##### **Design link: audit order** 

To prevent the displacement of records (FR-06) from producing a false “missing record range” (FR-07) warning, the rule that the order and duplicate checks are run first at runtime, and gap analysis is run afterwards on the sorted stream, is settled under Section 4.4 (Behavioral Design). 

#### **D. Cross-source consistency analysis** 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-09**|The system shall pair records from different sources that<br>belong to the same moment, within a permitted time<br>difference.|Time-wise matching of<br>different source streams|Must|US-05|
|**FR-10**|The system shall raise a disagreement alert when paired<br>sources report values for the same measurement that<br>f      i|Scenario S-07 (cross-<br>source contradiction)|Must|US-05|
||differ by more than the acceptable deviation.|test|||



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 15 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-11**|The system shall flag the source that differs from the<br>others as suspect when three or more sources are<br>compared during a disagreement, and record an<br>unresolved disagreement when only two sources are<br>available.|Three-source<br>comparison and two-<br>source ambiguity test|Must|US-05|



#### **E. Configuration and reporting** 

|**ID**|**Requirement statement**|**Verification target**|**Priority**|**Story**|
|---|---|---|---|---|
|**FR-12**|The system shall allow an administrator to adjust audit<br>rules (checkpoint frequency, trusted signing keys,<br>permitted clock difference and acceptable measurement<br>deviation) without code changes, and shall reject invalid<br>values.|Boundary test with valid<br>and invalid setting<br>values|Should|US-06|
|**FR-13**|The system shall produce an exportable, structured audit<br>report containing every finding with its type, source,<br>record range, time and supporting evidence.|Each finding in the<br>produced report<br>contains the required<br>information|Must|US-07|
|**FR-14**|The system shall present a status timeline marking each<br>audited record range as Verified (green), Source<br>Deviation (yellow) or Integrity / Continuity Violation<br>(red).|Timeline statuses match<br>the test labels|Should|US-07|



### **6.2 Non-Functional Requirements (NFR — FURPS+)** 

Non-functional requirements are defined not with abstract expressions such as “fast” or “secure” but as quality constraints that can be tested with numeric thresholds. 

|**ID**|**Category / attribute**|**Measurable requirement**|**Verification criterion**|
|---|---|---|---|
|**NFR-01**|Performance<br>Verification time|On a standard laptop, verifying a multi-source<br>data package of 100,000 records must complete<br>in under 3 seconds.|Time measurement: under 3<br>seconds for 100,000 records|
|**NFR-02**|Performance<br>Storage overhead|The security information added to records for<br>verification must not exceed an average of 160<br>bytes per record (about the length of a short<br>text message).|File size comparison: average<br>increase per record of 160<br>bytes or less|
|**NFR-03**|Reliability<br>Repeatability|When the same record files are re-audited with<br>the same rules, the system must produce<br>exactly the same results every time.|Repeating the same audit 100<br>times and verifying that the<br>reports are exactly identical|
|**NFR-04**|Reliability<br>Fault tolerance|Even if one of the loaded data sources is too<br>damaged to read, the system must not stop,<br>must report the problem, and must complete<br>the audit of the remaining healthy sources.|Deliberately corrupting one<br>source and seeing the audit<br>complete smoothly with the<br>remaining sources|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 16 

|**ID**|**Category / attribute**|**Measurable requirement**|**Verification criterion**|
|---|---|---|---|
|**NFR-05**|Security<br>Tamper-detection<br>certainty|Assuming the signing key has not fallen into the<br>attacker's hands (see Section 3.2), all later<br>modification, deletion, insertion, reordering and<br>duplication tampering of records must be<br>detected; no false alarm must be produced on<br>untampered data.|100% of injected tampering in<br>the test data found; 0 false<br>alarms on clean data|
|**NFR-06**|Usability<br>Forensic evidence<br>completeness|Each finding in the reports must contain the<br>following five pieces of information so that the<br>expert can examine it without extra<br>computation: finding type, related source,<br>affected record range, event time, and expected<br>versus observed value.|All five pieces of information<br>present in all findings in the<br>report|
|**NFR-07**|Supportability<br>Extensibility|The data reading part and the audit part of the<br>system must be designed separately, so that<br>adding a new record type does not require<br>rewriting the existing audit rules.|Showing that a second record<br>type can be added without<br>changing the audit rules|
|**NFR-08**|Design constraint<br>Standard security<br>methods|Only industry-standard, mature and publicly<br>available methods and libraries must be used for<br>security operations; the team must not develop<br>its own encryption method (the chosen methods<br>are in Section 4.6).|Listing the components used<br>and verifying by code review|



## **7. Traceability and Verification Matrix** 

The matrix maps which atomic functional requirements (FR-01 – FR-14), which quality constraints (NFR-01 – NFR-08) and which injected test scenarios (S-01 – S-07) verify each user story. Every FR and NFR is linked to at least one story, and every scenario is linked to at least one story. 

|**Story**|**Title**|**FR**|**NFR**|**Verification / scenario**|
|---|---|---|---|---|
|**US-01**|Loading and checking<br>record files|FR-01, FR-02,<br>FR-03|NFR-04 (fault tolerance),<br>NFR-07 (extensibility)|Corrupted, incomplete<br>and unsupported file<br>upload tests|
|**US-02**|Verifying whether<br>records were<br>modified|FR-04, FR-05|NFR-01, NFR-02, NFR-03,<br>NFR-05, NFR-08|S-01 (value modification),<br>S-03 (forged record<br>insertion)|
|**US-03**|Detecting ordering<br>and duplication<br>problems|FR-06|NFR-01, NFR-03, NFR-05|S-04 (reordering), S-05<br>(duplication)|
|**US-04**|Lost data ranges and<br>recoverability|FR-07, FR-08|NFR-01, NFR-03, NFR-05|S-02 (record deletion),<br>S-06 (partial data loss)|
|**US-05**|Cross-source<br>consistency audit|FR-09, FR-10,<br>FR-11|NFR-01, NFR-03, NFR-06<br>(evidence completeness)|S-07 (cross-source<br>contradiction)|
|**US-06**|Configuring audit<br>rules|FR-12|NFR-03, NFR-08|Valid / invalid setting<br>value tests|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 17 

|**Story**|**Title**|**FR**|**NFR**|**Verification / scenario**|
|---|---|---|---|---|
|**US-07**|Audit report and<br>i|FR-13, FR-14|NFR-03, NFR-06 (five|S-01 – S-07 combined end-|
||timeline||mandatory evidence items)|to-end audit scenario|



## **8. Test Strategy and Measurable Success Criteria** 

### **8.1 Fault / Attack Scenarios** 

|**No**|**Scenario**|**Expected output**|**Success criterion**|
|---|---|---|---|
|S-01|Value modification: a record<br>value is changed (altitude 10,000<br>→ 7,000 ft)|Integrity violation warning showing the<br>first modified record and its time — FR-04|All injected<br>modifications are<br>detected|
|S-02|Record deletion: records 1005–<br>1020 are deleted|Range 1005–1020 reported as missing —<br>FR-07|Detected; the range is<br>reported correctly|
|S-03|Forged record insertion: a<br>forged record is inserted, or all<br>security links are re-edited from<br>scratch|Forgery (signature violation) warning —<br>FR-05 (and / or integrity violation warning<br>— FR-04)|Detected|
|S-04|Reordering: two adjacent<br>records swap places|Order violation warning — FR-06 (plus an<br>integrity violation warning — FR-04)|Detected; no false<br>“missing range”<br>warning is produced|
|S-05|Duplication: the same record<br>number appears twice|Duplicate record warning — FR-06|Detected|
|S-06|Partial data loss: the primary<br>recorder is cut at record 1451,<br>the secondary recorder remains<br>intact up to 2000|Range 1451–2000 reported as missing and<br>classified “recoverable from backup”;<br>“unrecoverable” if absent in the secondary<br>source — FR-07, FR-08|Recoverability class is<br>reported correctly|
|S-07|Cross-source contradiction:<br>records that passed the security<br>checks but whose navigation<br>altitude contradicts the other<br>sources|Disagreement warning and suspect-source<br>flag (3+ sources) or “ambiguous conflict” (2<br>sources) — FR-10, FR-11|Deviation and suspect<br>source are flagged; the<br>false alarm rate is<br>measured separately|



### **8.2 Metrics to Be Measured** 

|**Metric**|**Definition and target**|
|---|---|
|**Detection rate**|The rate at which injected tampering is caught; target 100% for tampering types<br>based on the security digest and signature|
|**False alarm rate**|The rate of false alarms produced on clean, untampered data; target 0 for<br>integrity alarms, measured and reported for cross-source deviation alarms|
|**Verification time**|Verification time for 10,000 / 50,000 / 100,000 records; target under 3 seconds<br>for 100,000 records (NFR-01)|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 18 

|**Metric**|**Definition and target**|
|---|---|
|**Storage overhead**|Security information added per record; target an average of 160 bytes or less<br>(NFR-02)|
|**Time cost of security**<br>**operations**|Separate measurement of the time taken by record chaining and by signature<br>verification|
|**Recovery rate**|The rate at which missing ranges present in a backup source are correctly<br>reported as “recoverable from backup”|



##### **What does “100% detection” cover?** 

Integrity and signature checks give definitive results: under the assumption that the signing key has not fallen into the attacker's hands (see Section 3.2, A2), all injected tampering is expected to be caught (NFR-05). Cross-source comparison, however, relies on acceptable deviation limits; here the target is not 100%, but **reporting the detection rate and the false alarm rate together.** Making this distinction from the start also strengthens the defense. 

## **9. Feasibility Assessment** 

### **9.1 Technical Feasibility** 

- No physical aircraft, sensors or embedded hardware are needed; the whole system is software-based and test-oriented. 

- The cryptographic components are built with mature open-source libraries; there is no algorithm development risk. 

- Since the simulation, recording, audit and reporting layers are independent modules, they can be developed in parallel. 

- The data volume (10,000–100,000 records) can be processed on an ordinary laptop. 

### **9.2 Proposed Phases** 

A sequence compatible with the course flow is proposed; the weekly distribution will be set within the group according to the semester calendar. 

1. **Requirements:** problem definition, roles, user stories, FR / NFR, traceability matrix (L2–L4). 

2. **Architecture and design:** common record schema, module interfaces, technical design decisions and the finding / error code dictionary (Sections 4.1 – 4.7), the audit order decision (Section 4.4). 

3. **Core development (MVP):** data generator, data loading and checking (FR-01 – FR-03), integrity and checkpoint verification (FR-04 – FR-05), order, duplicate and gap detection (FR-06 – FR-07; scenarios S-01 – S-05), CLI report. 

4. **Analyzers:** recoverability (FR-08, S-06), cross-consistency (FR-09 – FR-11, S-07), audit report (FR-13). 

5. **Testing, measurement and iteration:** collecting metrics, tuning thresholds; configuration (FR-12) and timeline (FR-14) are stretch. 

TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 19 

### **9.3 Cost** 

There is no hardware or license cost; only open-source libraries and a standard development environment are needed. 

### **9.4 Risks** 

|**Risk**|**Level**|**Mitigation**|
|---|---|---|
|Scope creep (7 stories, 14 FR,<br>generalization, dashboard)|High|MVP / stretch split (Must / Should); the S-01 – S-07 core is<br>completed first|
|The project being perceived as a<br>“cryptography demo”|Medium|Emphasis: requirements analysis, cross-consistency and<br>measurable testing|
|False alarms in semantic analysis|High|Thresholds are parametric; false alarm measurement on<br>clean data; majority comparison with three or more sources|
|Findings triggering one another<br>(e.g. reordering → false gap)|Medium|Audit order decision (Section 4.4) and the “no false gap is<br>produced” criterion for S-04|
|Synthetic data being unrealistic|Medium|A simple physical consistency model (altitude–speed<br>continuity); the aim is verifiability, not realism|
|Timestamp / clock skew|Medium|Δt is defined as a parameter; controlled skew is applied in<br>the simulation|
|Integration mismatch between<br>modules|Medium|The record schema and interface contract are frozen in the<br>first phase|
|Performance target not being<br>met (NFR-01)|Low|Early measurement; hashlib and vectorized operations<br>(Python), separate optimization of heavy steps if needed|
|Workload imbalance in a 3-<br>person group|Medium|Stretch goals (FR-12, FR-14, second adapter) are left to after<br>the MVP; the shared data objects and interface contract are<br>frozen together in the first phase|



### **9.5 Work Split (3-person group)** 

|**Member**|**Field**|**Responsibility**|
|---|---|---|
|**Member 1**|Simulation, secure recording and<br>integrity verification|Synthetic data generator, fault / attack injector, label<br>file; hash chain writer, Merkle tree, checkpoint<br>signing;IntegrityVerifier(FR-04 – FR-05); NFR-02,<br>NFR-05, NFR-08 measurements; scenarios S-01 –<br>S-03|
|**Member 2**|Analytics engine|ContinuityAnalyzerandConsistencyAnalyzer; the<br>sorting and de-duplication step (Section 4.4, step 4);<br>FR-06 – FR-11; scenarios S-04 – S-07; measurement<br>of the false alarm rate and the recovery rate|
|**Member 3**|Data ingestion, orchestration,<br>reporting and testing|RecordIngestor(and the second adapter),<br>AuditOrchestrator,ReportExporter, CLI / dashboard;<br>FR-01 – FR-03, FR-12 – FR-14; test infrastructure and<br>metric collection (NFR-01, NFR-03, NFR-04, NFR-06,<br>NFR-07); compiling the presentation slides|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 20 

_Shared responsibility: the InternalRecord and AuditFinding data objects and the module interfaces (Section 4.2) form a contract prepared jointly by the three members and frozen in the first phase; each member writes the unit tests for their own module. If an imbalance arises, Member 3's stretch work (FR-12, FR-14, second adapter) is left to after the MVP._ 

## **10. Limitations** 

- To position the project honestly, we admit from the start what TRACE cannot do: 

   - Cryptography does not bring lost data back; it only proves the absence and reports whether the data exists in another source. 

   - The cause of a gap (physical damage or deliberate deletion) cannot be distinguished cryptographically; TRACE reports not the cause but the gap itself and its evidence. 

   - Truncation of the records at the end of the chain can be caught beyond the last signed checkpoint only with a secondary source or an external checkpoint. 

   - If the signing key is captured, the system's guarantee becomes invalid (A2). 

   - A cross-source deviation is an indicator, not proof of tampering; a faulty sensor produces the same alarm. With two sources only an inconsistency can be reported (“ambiguous conflict”); which one is faulty cannot be determined. If all three sources diverge from one another, no majority forms, so an “ambiguous conflict” is recorded in the same way. 

   - The results are valid for simulated data; they have not been validated with real flight data. 

## **11. Conclusion** 

- **It is problem-oriented:** It is not a commercial product; it is an engineering problem seeking an answer to the question “can we trust digital evidence after an incident?”. 

- **It fits the course content:** Problem / solution space, separated roles, INVEST-compliant stories, atomic FRs and measurable NFRs emerge naturally. 

- **It is traceable and measurable:** Every story is tied to FRs, NFRs and test scenarios; success is shown numerically through injection and detection-rate / time metrics. 

- **It has design depth (L5 / L6):** A layered modular monolith architecture, component, data and behavioral design, and the low-coupling / high-cohesion principles make the path from requirements to code traceable. 

- **It is original:** It combines integrity, loss analysis and cross-consistency; it goes beyond a standalone encryption or hash demonstration. 

|**Course outcome**|**Counterpart in this document**|
|---|---|
|**L2 — Problem / solution**<br>**definition**|Sections 2 and 3|
|**L3 — User stories**|Section 5|
|**L4 — System**<br>**requirements**|Section 6|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 21 

|**Course outcome**|**Counterpart in this document**|
|---|---|
|**L5 — Software design**<br>**(component, data,**<br>**behavior, principles)**|Sections 4.2, 4.3, 4.4, 4.5, 4.6 and 4.7|
|**L6 — Software**<br>**architecture patterns**|Sections 4.1 and 4.2|
|**Traceability and**<br>**verification**|Sections 7 and 8|



TRACE — Feasibility and Introduction Document v4 (EN)  |  Page 22 

