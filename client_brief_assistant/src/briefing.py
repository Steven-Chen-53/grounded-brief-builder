"""Evidence-grounded brief assembly and deterministic validation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .retrieval import SearchResult


FIELD_ORDER = (
    "client_name",
    "industry",
    "business_goal",
    "audience",
    "background",
    "key_questions",
    "requested_deliverable",
    "deadline",
    "stakeholders",
    "constraints",
)
LIST_FIELDS = {"key_questions", "stakeholders", "constraints"}
MERGED_TEXT_FIELDS = {"background"}
REQUIRED_FIELDS = {
    "client_name",
    "industry",
    "business_goal",
    "audience",
    "requested_deliverable",
    "deadline",
    "stakeholders",
    "constraints",
}


def _display(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return str(value or "")


def _unique(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for value in values:
        key = _display(value).strip().casefold()
        if key and key not in seen:
            seen.add(key)
            output.append(value)
    return output


def _merge_lists(values: list[Any]) -> list[str]:
    flattened: list[str] = []
    for value in values:
        if isinstance(value, list):
            flattened.extend(str(item) for item in value if str(item).strip())
        elif str(value or "").strip():
            flattened.append(str(value))
    return _unique(flattened)


def _merge_text(values: list[Any]) -> str:
    return "\n\n".join(_display(value) for value in _unique(values))


def _clarification(field: str, values: list[Any] | None = None) -> str:
    labels = {
        "industry": "What industry label should appear in the brief?",
        "business_goal": "What decision or outcome should this engagement support?",
        "audience": "Who is the primary audience for the final brief?",
        "requested_deliverable": "What exact deliverable should be produced?",
        "deadline": "What is the confirmed delivery deadline?",
        "stakeholders": "Who owns the engagement and who must review it?",
        "constraints": "What data, policy, timing, or distribution constraints apply?",
        "background": "What context does the reviewer need before reading the analysis?",
        "key_questions": "Which two or three questions must the brief answer?",
    }
    if values:
        options = "; ".join(_display(value).replace("\n", " ") for value in values)
        return f"Conflicting values were found for {field.replace('_', ' ')}: {options}. Which is current?"
    return labels.get(field, f"Please confirm {field.replace('_', ' ')}.")


def assemble_brief(
    client_name: str,
    engagement_goal: str,
    search_results: list[SearchResult],
) -> dict[str, Any]:
    normalized_client = client_name.strip().casefold()
    factual_results = [
        result
        for result in search_results
        if result.relationship == "client evidence"
        and result.safe_to_use
        and result.record.get("client_name", "").strip().casefold() == normalized_client
    ]
    quarantined = [result for result in search_results if not result.safe_to_use]
    analogs = [result for result in search_results if result.relationship == "analog example" and result.safe_to_use]
    sources_by_field: dict[str, list[str]] = defaultdict(list)
    values_by_field: dict[str, list[Any]] = defaultdict(list)

    for result in factual_results:
        record = result.record
        for field in FIELD_ORDER:
            value = record.get(field)
            if value not in (None, "", []):
                values_by_field[field].append(value)
                sources_by_field[field].append(record["record_id"])

    fields: list[dict[str, Any]] = []
    questions: list[str] = []
    conflicts: list[str] = []
    missing: list[str] = []

    for field in FIELD_ORDER:
        if field == "client_name":
            fields.append(
                {
                    "name": field,
                    "value": client_name.strip(),
                    "status": "user provided",
                    "evidence": [],
                }
            )
            continue
        if field == "business_goal" and engagement_goal.strip():
            fields.append(
                {
                    "name": field,
                    "value": engagement_goal.strip(),
                    "status": "user provided",
                    "evidence": [],
                }
            )
            continue

        values = values_by_field.get(field, [])
        evidence = list(dict.fromkeys(sources_by_field.get(field, [])))
        if not values:
            fields.append({"name": field, "value": "", "status": "missing", "evidence": []})
            missing.append(field)
            questions.append(_clarification(field))
            continue

        if field in LIST_FIELDS:
            merged = _merge_lists(values)
            fields.append(
                {
                    "name": field,
                    "value": _display(merged),
                    "status": "supported",
                    "evidence": evidence,
                }
            )
            continue

        if field in MERGED_TEXT_FIELDS:
            fields.append(
                {
                    "name": field,
                    "value": _merge_text(values),
                    "status": "supported",
                    "evidence": evidence,
                }
            )
            continue

        unique_values = _unique(values)
        if len(unique_values) == 1:
            fields.append(
                {
                    "name": field,
                    "value": _display(unique_values[0]),
                    "status": "supported",
                    "evidence": evidence,
                }
            )
        else:
            fields.append(
                {
                    "name": field,
                    "value": _display(unique_values[0]),
                    "alternatives": [_display(value) for value in unique_values[1:]],
                    "status": "conflicting",
                    "evidence": evidence,
                }
            )
            conflicts.append(field)
            questions.append(_clarification(field, unique_values))

    required_missing = [field for field in missing if field in REQUIRED_FIELDS]
    warnings = [result.warning for result in quarantined if result.warning]
    if quarantined:
        warnings.append("Quarantined sources were displayed for auditability but excluded from every drafted field.")

    return {
        "client_name": client_name.strip(),
        "engagement_goal": engagement_goal.strip(),
        "abstained": not factual_results,
        "ready_for_review": bool(factual_results) and not required_missing and not conflicts,
        "fields": fields,
        "missing_fields": missing,
        "required_missing_fields": required_missing,
        "conflicting_fields": conflicts,
        "clarification_questions": questions,
        "warnings": list(dict.fromkeys(warnings)),
        "analog_suggestions": [
            {
                "record_id": result.record["record_id"],
                "client_name": result.record["client_name"],
                "requested_deliverable": result.record.get("requested_deliverable", ""),
                "note": "Analog only; do not use as a client fact.",
            }
            for result in analogs[:2]
        ],
        "evidence_count": len(factual_results),
    }
