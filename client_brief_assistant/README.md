# Grounded Brief Builder

Grounded Brief Builder is a sanitized portfolio demonstration of how I approach an applied AI workflow: understand the business task, retrieve relevant evidence, create a structured draft, expose uncertainty, and require human review before export.

> I built this demonstration after learning about a representative client-brief workflow during a Visa screening process. It uses synthetic data and is intended to show how I approach workflow discovery, retrieval, structured drafting, validation, and human review. It is not a Visa system and has not been deployed or used by Visa.

## Problem

Client-brief information may be distributed across approved briefs, meeting notes, emails, and data-readiness documents. Manually finding the current information can create delay, missing fields, conflicting details, and avoidable rework.

The MVP supports a business user who needs to:

1. Enter a client and engagement goal.
2. Retrieve relevant prior records.
3. See the source evidence and source health.
4. Draft a structured brief without inventing unsupported facts.
5. Resolve missing or conflicting fields.
6. Review and edit the output.
7. Approve the result before Markdown or JSON export.

## Why the offline implementation is intentional

The demonstration runs with Python's standard library and does not require a paid model API. It uses deterministic TF-IDF retrieval and evidence assembly so every evaluator can run the same workflow and reproduce the tests.

An approved language model could later improve narrative drafting and clarification wording. It would sit behind the same evidence, validation, and approval boundaries; it would not decide whether a fact is supported.

## Quick start

Requirements: Python 3.9 or newer. The verified local run used Python 3.9.6.

```bash
python3 app.py
```

Open `http://127.0.0.1:8765`.

Run the tests:

```bash
python3 run_tests.py
```

No credentials, subscriptions, installations, or external services are required.

## Interface walkthrough

![Request screen](docs/screenshots/01_request.png)

![Evidence and clarification screen](docs/screenshots/02_evidence.png)

![Prompt-injection quarantine](docs/screenshots/04_quarantine.png)

![Human approval before export](docs/screenshots/03_review.png)

## Demonstration scenarios

### 1. Known client with conflicts

- Client: `Northstar Retail`
- Goal: `Prepare an executive brief explaining regional sales performance and decisions needed for the next quarterly review.`
- Expected behavior: retrieves four client records, shows conflicting deadline, audience, background, and deliverable information, and asks targeted clarification questions.

### 2. No matching client

- Client: `Orchid Labs`
- Goal: `Prepare a market-entry decision brief.`
- Expected behavior: abstains from drafting client facts, shows only clearly labeled analog examples, and requests the missing intake information.

### 3. Prompt-injection attempt

- Client: `Apex Harbor Logistics`
- Goal: `Create a port delay response brief.`
- Expected behavior: retrieves the approved source, quarantines the malicious uploaded note, displays the warning, and excludes the malicious content from drafted fields.

## Architecture

```mermaid
flowchart LR
    U["Business user"] --> W["Python web interface"]
    W --> R["TF-IDF retrieval"]
    R --> S["Synthetic source records"]
    R --> G["Source health and injection checks"]
    G --> D["Deterministic field assembly"]
    D --> V["Required-field and conflict validation"]
    V --> H["Human review and edits"]
    H -->|Approved| E["Markdown / JSON export"]
    H -->|Not approved| B["Export blocked"]
```

The solution favors a controlled workflow over open-ended agent behavior because the steps and approval boundary are known. A production version could use an agent only where flexible tool selection creates measurable value.

## Repository structure

```text
app.py                         Local HTTP server and API
data/synthetic_records.json    Fourteen clearly synthetic records
src/retrieval.py               Explainable ranking and source quarantine
src/briefing.py                Field-level evidence assembly and validation
src/service.py                 Request, analysis, and export boundaries
static/                        Browser interface
tests/test_workflow.py         Automated workflow and control tests
docs/                          Case study, demo, test results, and limitations
```

## Controls demonstrated

- Field-level evidence identifiers.
- User-input labels separate from retrieved facts.
- Missing required fields remain empty.
- Conflicting scalar values remain visible.
- Analog examples cannot become client facts.
- Untrusted instruction-like sources are quarantined.
- No-match requests abstain instead of guessing.
- Human approval is required for export.
- Request content is not written to application logs.
- All sample clients, people, and records are synthetic.

## Evaluation

Eight automated tests were executed successfully on July 21, 2026:

- known-client retrieval;
- conflicting source details;
- no-match abstention;
- prompt-injection quarantine;
- malformed input;
- approval-gated export;
- approved Markdown/JSON export; and
- deterministic repeatability.

See `docs/TEST_RESULTS.md` for the executed output. These tests validate software behavior; they do not establish user adoption, time savings, or production accuracy.

## AI-assisted development

I used an AI coding assistant to accelerate implementation. I treated generated code as an untrusted draft: I reviewed the modules, kept the architecture small enough to explain, wrote focused tests around failure cases, executed the tests, and documented what remains mocked or out of scope.

## Production extensions

A production implementation would require Visa-approved patterns and ownership for:

- authentication, role-based authorization, and least-privilege access;
- permission-aware retrieval and source-level access enforcement;
- approved Microsoft or enterprise model integration;
- SharePoint or another governed system of record;
- versioned schemas, source freshness, retention, and deletion;
- evaluation sets for groundedness, completeness, abstention, and harmful output;
- structured audit logs that avoid unnecessary sensitive content;
- monitoring for quality, latency, cost, rework, and adoption;
- security and responsible-AI review; and
- support, escalation, rollback, and ongoing ownership.

## Claim boundaries

- This is a new portfolio demonstration, not a Visa project.
- The data and observed test results are synthetic.
- No business-impact or adoption metrics are claimed.
- The offline version uses deterministic drafting, not a live generative model.
