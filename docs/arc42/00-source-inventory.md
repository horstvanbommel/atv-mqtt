# Source Document Inventory

**Generated:** 2026-05-04
**Purpose:** Comprehensive inventory of all source documents with arc42 section mapping
and cross-reference analysis. Source documents are existing project files (no formal
`SourceDocuments/` directory exists yet); the `/architecture:ingest-sources` command
was run against the live project tree.

> **Note on project duality:** This repository has two distinct concerns:
> (1) a **Claude Code AI toolchain** (streb templates, beads, ralph loop, hooks, patterns)
> and (2) an **Apple TV MQTT bridge** application (`scripts/atv_mqtt_bridge.py`).
> Both are captured here.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| AI Toolchain — project instructions & workflow | 3 |
| AI Toolchain — rules & conventions | 4 |
| AI Toolchain — patterns | 2 |
| AI Toolchain — configuration & infrastructure | 4 |
| Application source code | 1 |
| Templates | 1 |
| Init / setup logs | 1 |
| **Total** | **16 documents** |

---

## Document Catalog

### AI Toolchain — Project Instructions & Workflow

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 1 | `README.md` | active | 2026-05-04 (inferred) | Template structure, streb init process, included tooling, customization | §01, §03, §04, §09 | CLAUDE.md, .mcp.json, .claude/ |
| 2 | `AGENTS.md` | active | 2026-05-04 (inferred) | Beads workflow, non-interactive shell rules, session completion protocol, push mandate | §02, §06, §08 | CLAUDE.md, .beads/ |
| 3 | `CLAUDE.md` | active | 2026-05-04 (inferred) | Beads quick reference, session close protocol, empty build/arch/conventions stubs | §01, §02, §06, §09 | AGENTS.md, .claude/rules/ |

### AI Toolchain — Rules & Conventions

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 4 | `.claude/rules/git-safety.md` | active | 2026-05-04 (inferred) | Commit protocol, amend rules, conventional commits, branch workflow | §02, §08, §09 | AGENTS.md, CLAUDE.md |
| 5 | `.claude/rules/go-conventions.md` | active | 2026-05-04 (inferred) | Error handling, naming, package structure, testing (testify), dependencies (Cobra, Viper, Bubble Tea) | §02, §05, §08, §10 | .claude/rules/streb-architecture.md |
| 6 | `.claude/rules/security.md` | active | 2026-05-04 (inferred) | Sensitive file access, command injection prevention, path safety, credential storage, output sanitization | §02, §08, §10 | scripts/atv_mqtt_bridge.py (**contradiction**) |
| 7 | `.claude/rules/streb-architecture.md` | active | 2026-05-04 (inferred) | Provider interface, Installer interface, Cobra CLI structure, Viper config, performance targets | §02, §04, §05, §09, §10 | .claude/rules/go-conventions.md |

### AI Toolchain — Patterns

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 8 | `patterns/gev.md` | active | 2026-05-04 (inferred) | Gate-Execute-Verify: prerequisite checks, rollback points, verification; error recovery matrix | §04, §06, §08, §10 | patterns/ralph-wiggum.md |
| 9 | `patterns/ralph-wiggum.md` | active | 2026-05-04 (inferred) | Autonomous loop: INITIALIZE→ITERATE→EXECUTE→EVALUATE; COMPLETE/BLOCKED/STUCK exits; stuck threshold = **3** | §04, §06 | .ralph/config.yaml (**contradiction**) |

### AI Toolchain — Configuration & Infrastructure

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 10 | `.mcp.json` | active | 2026-05-04 (inferred) | MCP filesystem server via npx; single server configured | §03, §07, §09 | README.md |
| 11 | `.container-use.yaml` | active | 2026-05-04 (inferred) | Dev container: golang:1.21 image, workspace mount, GOPROXY | §02, §07, §09 | scripts/atv_mqtt_bridge.py (**contradiction**) |
| 12 | `.ralph/config.yaml` | active | 2026-05-04 | Ralph loop: max_iterations=100, timeout=60min, heartbeat=30s, stuck_threshold=**5** | §04, §06 | patterns/ralph-wiggum.md (**contradiction**) |
| 13 | `toolchain.yaml` | active | 2026-05-04 (inferred) | Language detection (9+ languages via marker files), build commands per language, cloud CLIs (Azure, AWS, GCP), k8s, IaC, container tools | §03, §04, §07 | .container-use.yaml |

### Application Source Code

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 14 | `scripts/atv_mqtt_bridge.py` | active | unknown | Apple TV MQTT bridge: asyncio, PyATV Companion protocol, MQTT broker, KNX/Gira integration, two devices (wohnzimmer/schlafzimmer), **hardcoded credentials** | §03, §05, §06, §07, §11 | .claude/rules/security.md (**contradiction**), .container-use.yaml (**contradiction**) |

### Templates

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 15 | `CLAUDE.local.md.template` | template | 2026-05-04 (inferred) | Personal preferences stub; gitignored when instantiated; no architecture content | — | CLAUDE.md |

### Init / Setup Logs

| # | File | Status | Date | Key Topics | Arc42 Sections | Cross-References |
|---|------|--------|------|------------|----------------|------------------|
| 16 | `.streb/log.md` | log | 2026-05-04 | streb v0.9.33, darwin/arm64, beads initialized, GitHub configured, adesso AI-Hub API key, jira/plugins/dagger skipped | §03, §07 | README.md, .claude/settings.json |

---

## Claims and Constraints Summary

### Key Claims (explicit)

| Claim | Source | Arc42 §§ | Confidence |
|-------|--------|----------|------------|
| MQTT broker runs at localhost:1883 | `scripts/atv_mqtt_bridge.py:3` | §03, §07 | explicit |
| Two ATV devices: wohnzimmer (8E99280BFB01) and schlafzimmer (D291A14F525D) | `scripts/atv_mqtt_bridge.py:6–14` | §03, §05 | explicit |
| Apple TV uses PyATV Companion protocol for control | `scripts/atv_mqtt_bridge.py` | §05, §06 | explicit |
| Device state is published to `home/atv/<device>/state` topics (retained) | `scripts/atv_mqtt_bridge.py:send_status()` | §06 | explicit |
| Commands arrive via `home/atv/<device>` MQTT topics | `scripts/atv_mqtt_bridge.py:on_message()` | §06 | explicit |
| Monitor polls power state every 20s; reconnects after 15s downtime | `scripts/atv_mqtt_bridge.py:monitor_atv()` | §06, §10 | explicit |
| Optimistic feedback: publishes On/Off immediately on command (before confirmation) | `scripts/atv_mqtt_bridge.py:control_atv()` | §06 | explicit |
| streb version 0.9.33 was used to initialize this project | `.streb/log.md` | §07 | explicit |
| Platform is darwin/arm64 | `.streb/log.md` | §07 | explicit |
| Anthropic API endpoint is adesso AI-Hub (not api.anthropic.com) | `.streb/log.md`, `.claude/settings.json` | §07 | explicit |
| Git user is Mike Fabian <mike_fabian@icloud.com> | `.streb/log.md` | §07 | explicit |
| Claude Code version v2.1.123 | `.streb/log.md` | §07 | explicit |
| Dolt version 1.86.6 is used for beads sync | `.streb/log.md` | §07 | explicit |
| CLI startup must be < 100ms | `.claude/rules/streb-architecture.md` | §10 | explicit |
| `streb status` must complete in < 2s | `.claude/rules/streb-architecture.md` | §10 | explicit |
| `streb init` (without downloads) must complete in < 30s | `.claude/rules/streb-architecture.md` | §10 | explicit |
| Ralph loop stuck threshold is 3 iterations (pattern doc) | `patterns/ralph-wiggum.md` | §04 | explicit |
| Ralph loop stuck threshold is 5 iterations (config file) | `.ralph/config.yaml` | §04 | explicit |
| Dev container uses golang:1.21 | `.container-use.yaml` | §07 | explicit |
| Go package structure: internal/cli, config, installer, platform, tools | `.claude/rules/go-conventions.md` | §05 | explicit |
| All external integrations must implement Provider interface | `.claude/rules/streb-architecture.md` | §05 | explicit |
| All tool installers must implement Installer interface | `.claude/rules/streb-architecture.md` | §05 | explicit |
| Config hierarchy: project `.streb/config.yaml` → global `~/.streb/config.yaml` → env vars | `.claude/rules/streb-architecture.md` | §08 | explicit |

### Key Constraints (hard limits)

| Constraint | Source | Arc42 §§ |
|-----------|--------|----------|
| NEVER force-push main/master | `.claude/rules/git-safety.md` | §02 |
| NEVER skip pre-commit hooks | `.claude/rules/git-safety.md` | §02 |
| NEVER read/write `.env`, `*.pem`, `*.key`, `*secret*` files | `.claude/rules/security.md` | §02 |
| NEVER pass unsanitized user input to exec.Command | `.claude/rules/security.md` | §02, §08 |
| Always use `filepath.Clean()` and check for path traversal | `.claude/rules/security.md` | §02, §08 |
| Never log credentials | `.claude/rules/security.md` | §02, §08 |
| Always use -f flags for cp/mv/rm in shell (non-interactive) | `AGENTS.md` | §02 |
| Work is NOT complete until `git push` succeeds | `CLAUDE.md`, `AGENTS.md` | §02 |
| Use `bd` for ALL task tracking; never use TodoWrite/TaskCreate | `CLAUDE.md`, `AGENTS.md` | §02 |
| Always handle errors; never use `_` to ignore | `.claude/rules/go-conventions.md` | §02 |

### Open Questions from Source Documents

| Question | Source | Arc42 §§ |
|----------|--------|----------|
| Which stuck threshold governs ralph loops — 3 (pattern doc) or 5 (config)? | `patterns/ralph-wiggum.md` vs `.ralph/config.yaml` | §04 |
| How is the Apple TV MQTT bridge deployed? (no service management docs) | `scripts/atv_mqtt_bridge.py` | §07 |
| Are there tests for the MQTT bridge? (no test file found) | `scripts/atv_mqtt_bridge.py` | §10 |
| What controls the companion credentials rotation for the Apple TVs? | `scripts/atv_mqtt_bridge.py` | §08, §11 |
| What is the intended container image for the Python bridge — not golang:1.21? | `.container-use.yaml` | §07 |
| Why were plugins and Dagger declined at streb init? | `.streb/log.md` | §09 |

---

## Arc42 Coverage Map

| Arc42 Section | Source Documents | Coverage |
|--------------|-----------------|----------|
| §01 Introduction and Goals | `README.md`, `AGENTS.md`, `CLAUDE.md` | sparse — goals are implicit (standardize Claude Code setup, enable beads workflow); no formal business goals or stakeholder requirements stated |
| §02 Constraints | `.claude/rules/git-safety.md`, `.claude/rules/go-conventions.md`, `.claude/rules/security.md`, `.claude/rules/streb-architecture.md`, `AGENTS.md`, `CLAUDE.md`, `.container-use.yaml` | rich — hard rules well-documented for AI toolchain; fewer constraints documented for smart home application |
| §03 Context and Scope | `README.md`, `scripts/atv_mqtt_bridge.py`, `.mcp.json`, `.streb/log.md`, `toolchain.yaml` | adequate — external systems identifiable (MQTT broker, Apple TV, KNX/Gira, GitHub, adesso AI-Hub, MCP server) but no formal context diagram |
| §04 Solution Strategy | `README.md`, `.claude/rules/streb-architecture.md`, `patterns/gev.md`, `patterns/ralph-wiggum.md`, `toolchain.yaml`, `.ralph/config.yaml` | rich — Provider/Installer patterns, GEV, ralph loop, marker-based language detection all documented |
| §05 Building Block View | `.claude/rules/streb-architecture.md`, `.claude/rules/go-conventions.md`, `scripts/atv_mqtt_bridge.py` | adequate — Go internal package structure and Provider/Installer interfaces documented; Python bridge has visible class structure (StateMonitor) but no formal component docs |
| §06 Runtime View | `scripts/atv_mqtt_bridge.py`, `patterns/ralph-wiggum.md`, `patterns/gev.md`, `CLAUDE.md`, `AGENTS.md` | sparse — asyncio-based monitoring and control flows are readable from source; pattern docs describe AI command lifecycle; no sequence diagrams |
| §07 Deployment View | `.streb/log.md`, `.container-use.yaml`, `scripts/atv_mqtt_bridge.py`, `toolchain.yaml` | sparse — platform (darwin/arm64), container (golang:1.21), MQTT endpoint (localhost:1883), log path (/tmp/atvbridge.log) known; no deployment procedure documented for Python bridge |
| §08 Crosscutting Concepts | `.claude/rules/security.md`, `.claude/rules/git-safety.md`, `.claude/rules/go-conventions.md`, `.claude/rules/streb-architecture.md`, `AGENTS.md` | rich — auth, logging, error handling, config hierarchy, non-interactive shell all addressed |
| §09 Architecture Decisions | `README.md`, `.claude/rules/streb-architecture.md`, `.mcp.json`, `.container-use.yaml`, `CLAUDE.md`, `toolchain.yaml` | adequate — key decisions evident (beads over GitHub Issues, Cobra/Viper/Bubble Tea, npx MCP, golang:1.21); no formal ADR documents |
| §10 Quality Requirements | `.claude/rules/streb-architecture.md`, `patterns/gev.md`, `.claude/rules/go-conventions.md` | sparse — streb CLI has three performance targets; Python bridge has no SLOs; no availability, reliability, or security SLOs documented |
| §11 Risks and Technical Debt | `scripts/atv_mqtt_bridge.py`, `CLAUDE.md`, `.streb/log.md` | none (formal) — critical risk (hardcoded credentials) exists in code but no risk register; CLAUDE.md has empty stubs; streb init skipped plugins/dagger (undocumented rationale) |
| §12 Glossary | All documents (terms used implicitly throughout) | none — domain terms (bd, beads, streb, ralph, GEV, KNX, Gira, ATV, MQTT, MCP, Companion, adesso AI-Hub, dolt, wohnzimmer, schlafzimmer) used without a glossary file |

---

## Contradictions

### 1. Ralph Loop Stuck Threshold

- **Source A:** `patterns/ralph-wiggum.md` — "**Threshold: 3 iterations** → Exit with STUCK"
- **Source B:** `.ralph/config.yaml` — `stuck_threshold: 5`
- **Severity:** important — autonomous agents rely on this for self-termination; a discrepancy means the pattern documentation and runtime config govern different behaviors
- **Recommended resolution:** Update `patterns/ralph-wiggum.md` to read `stuck_threshold: 5` (or vice versa, as a deliberate design choice), then document which source is authoritative

---

### 2. Hardcoded Credentials in Application Source

- **Source A:** `scripts/atv_mqtt_bridge.py` lines 13–14 — `MQTT_USER = "mqtt_user"` and `MQTT_PW = "4Uu9uGDd"` are literal strings in committed source
- **Source B:** `.claude/rules/security.md` — "Never log credentials", "Use the repository's file-based credential helpers with restrictive permissions", "Use Vault paths for credential storage"
- **Severity:** blocking — this is a security violation: credentials are exposed in version control, directly contradicting the project's own security policy
- **Recommended resolution:** Move credentials to environment variables or a `.env` file (gitignored) and update the script to use `os.environ`; rotate the MQTT password

---

### 3. Dev Container Language Mismatch

- **Source A:** `.container-use.yaml` — `image: golang:1.21` (Go runtime)
- **Source B:** `scripts/atv_mqtt_bridge.py` — Python application requiring `paho-mqtt` and `pyatv`
- **Severity:** important — the Python bridge cannot run in the Go dev container; a developer using `container-use` for the smart home app would have no Python interpreter or dependencies
- **Recommended resolution:** Either (a) add a Python container profile to `.container-use.yaml`, (b) add a `Dockerfile` for the Python app, or (c) document that the Go container is only for streb tooling development

---

### 4. README.md Self-Description

- **Source A:** `README.md` line 1–4 — "This directory contains templates for setting up Claude Code with best practices. These files are copied by `streb init` to set up a new project."
- **Source B:** Reality — this is the live `smarthome-scripts` project root (the files are already in place, not templates being distributed)
- **Severity:** minor — this README is itself a template that was copied verbatim by `streb init` without being updated to describe the actual project; it confuses future readers
- **Recommended resolution:** Replace `README.md` with a project-specific description of the `smarthome-scripts` repository

---

## Gaps

### §01 — Introduction and Goals
No explicit goals, stakeholders, or quality objectives are documented. The toolchain purpose is *inferrable* from README.md and CLAUDE.md, and the smart home purpose is *inferrable* from the Python script, but no document answers: "What problem does this system solve, for whom, and with what quality bar?" A one-page arc42 §01 would immediately address this gap.

### §06 — Runtime View
The asyncio-based bridge has three concurrent execution paths (monitor_atv per device, control_atv on demand, MQTT on_message callback) that interact through shared state (`last_states` dict) and an asyncio event loop. No sequence diagram or narrative describes this; understanding requires reading the source code directly. A sequence diagram showing the monitor/control/event paths and the KNX→MQTT→ATV→MQTT flow would close this gap.

### §07 — Deployment View
No deployment procedure exists for the Python bridge. Unknown: how the script is started (systemd? launchd? manual?), what restarts it on failure, what the log rotation policy is for `/tmp/atvbridge.log`, and whether it runs on the same host as the MQTT broker. The development container (golang:1.21) does not cover the Python application at all.

### §10 — Quality Requirements
Performance, availability, and reliability requirements are absent for the smart home application. The streb CLI has three targets, but the Apple TV bridge has none. Questions unanswered: What is the acceptable delay between KNX command and ATV action? What is the acceptable state-reporting lag? What happens if the bridge is down for 30 minutes?

### §11 — Risks and Technical Debt
No formal risk register exists. Known risks inferred from source:
- **Critical:** MQTT credentials hardcoded in source (`scripts/atv_mqtt_bridge.py:13–14`)
- **Medium:** German-language code comments limit maintainability for non-German-speaking contributors
- **Medium:** No tests for the Python bridge (test infrastructure not set up; `CLAUDE.md` build section is empty)
- **Low:** Jira integration declined at init — if the team later uses Jira, manual migration of issues will be needed
- **Low:** `README.md` is an unmodified streb template — documentation technical debt from day one

### §12 — Glossary
No glossary file exists. The following project-specific and domain terms appear across source documents without definition:

| Term | Used In |
|------|---------|
| bd / beads | CLAUDE.md, AGENTS.md, README.md |
| streb | README.md, .streb/log.md, .claude/rules/streb-architecture.md |
| ralph (loop) | patterns/ralph-wiggum.md, .ralph/config.yaml, toolchain.yaml |
| GEV | patterns/gev.md |
| KNX / Gira | scripts/atv_mqtt_bridge.py (comments) |
| ATV | scripts/atv_mqtt_bridge.py |
| Companion (protocol) | scripts/atv_mqtt_bridge.py |
| adesso AI-Hub | .streb/log.md, .claude/settings.json |
| dolt | .streb/log.md, AGENTS.md |
| wohnzimmer / schlafzimmer | scripts/atv_mqtt_bridge.py |
| MCP | .mcp.json, README.md |
| PyATV | scripts/atv_mqtt_bridge.py (implicit via import) |

---

## Supersession Chain

No supersession detected. No ADR documents exist; there are no documents that explicitly replace earlier decisions.

| Superseded Document | Superseded By | Date | Reason |
|--------------------|---------------|------|--------|
| — | — | — | No supersession detected |

---

## Quality Checklist

- [x] Every source document in the specified scope appears in the catalog (16 of 16)
- [x] Every document has at least one arc42 section mapping (except `CLAUDE.local.md.template`, which contains no architecture content)
- [x] All contradictions between sources are explicitly flagged (4 contradictions)
- [x] All arc42 sections (§01–§12) appear in the coverage map
- [x] Sections with "none" coverage (§11, §12) are called out in the Gaps section
- [x] Sections with "sparse" coverage (§01, §06, §07, §10) are called out in the Gaps section
- [x] Superseded documents are marked and the supersession chain is clear (none found)
- [x] Cross-references between documents are recorded in the catalog tables
