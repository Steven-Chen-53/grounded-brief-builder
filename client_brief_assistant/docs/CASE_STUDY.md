# Case Study: Grounded Brief Builder

## The problem

Client briefs often depend on information spread across prior briefs, notes, emails, and supporting records. The difficult part is not merely generating polished text. It is finding the right evidence, determining which version is current, identifying what is missing, and keeping the reviewer accountable for the final output.

## My approach

I started with the workflow rather than the model. The minimum useful version needed to retrieve evidence, organize it into a reusable schema, expose conflicts, ask targeted clarification questions, and prevent export without human approval.

I used fourteen synthetic records containing known matches, incomplete information, conflicting details, analog examples, a no-match case, and an intentionally malicious source. The application ranks the records, separates exact-client evidence from cross-client analogs, and quarantines instruction-like content before field assembly.

## What I built

- A dependency-free Python web application.
- Explainable TF-IDF retrieval with exact-client prioritization.
- A structured brief schema with field-level source identifiers.
- Missing-field and conflict detection.
- Prompt-injection quarantine.
- An abstention path for unknown clients.
- Editable review fields and approval-gated Markdown/JSON export.
- Eight automated tests covering normal, edge, and adversarial cases.

## Why I did not use an LLM for every step

The evidence and validation rules are deterministic business controls. Using a model for these steps would make the behavior harder to reproduce and audit without improving the business outcome. In a production version, an approved model could rewrite supported content and propose clarification wording, while normal code would continue to control sources, required fields, permissions, and export.

## Observed result

All eight automated tests passed on July 21, 2026. The application correctly retrieved known-client records, exposed conflicts, abstained on an unknown client, quarantined a prompt-injection source, rejected malformed input, blocked unapproved export, produced approved exports, and returned repeatable results.

These are software test results, not production business metrics.

## What I would validate in a pilot

- Brief completion time versus the current process.
- Missing-field and rework rates.
- Groundedness and unsupported-claim rate.
- Conflict detection and abstention quality.
- Reviewer corrections and escalation patterns.
- Repeat usage and adoption.

## Enterprise next steps

I would work with business, platform, security, and responsible-AI owners to add identity, source permissions, approved models, governed storage, evaluation gates, audit logging, monitoring, retention rules, and support ownership. I would not describe those controls as implemented in this demonstration.
