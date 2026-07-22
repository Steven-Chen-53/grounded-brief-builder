# Limitations and Production Next Steps

## Current limitations

- Synthetic JSON records only; no enterprise source connector.
- Deterministic TF-IDF retrieval rather than semantic embeddings.
- Deterministic structured drafting; no live generative model.
- No authentication, authorization, or permission-aware retrieval.
- Human approval is a local workflow control, not an authenticated electronic approval.
- Conflict detection compares normalized values; it does not reason about whether one document supersedes another.
- Prompt-injection quarantine uses explicit patterns and source trust status; a production system needs layered content security and adversarial evaluation.
- No persistent application database, analytics, monitoring service, or support workflow.
- No production user research, adoption data, or business-impact metrics.

## Production next steps

1. Confirm the current process, source of record, reviewers, and decision rights.
2. Integrate approved storage and preserve source permissions during retrieval.
3. Add identity, roles, least-privilege access, and authenticated approvals.
4. Add an approved embedding and model service behind explicit interfaces.
5. Build representative evaluation sets with business owners.
6. Add structured audit logs, monitoring, incident handling, and rollback.
7. Define retention, deletion, source freshness, and versioning.
8. Run a limited pilot and compare completion time, missing fields, rework, groundedness, abstention, and adoption against the baseline.
9. Assign long-term ownership for sources, prompts, evaluation, support, and change control.
