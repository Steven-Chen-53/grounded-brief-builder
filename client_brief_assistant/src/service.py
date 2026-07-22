"""Application service functions shared by the web server and tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .briefing import assemble_brief
from .retrieval import TfidfRetriever, load_records


class RequestValidationError(ValueError):
    pass


class ApprovalRequiredError(PermissionError):
    pass


class BriefService:
    def __init__(self, data_path: str | Path):
        self.records = load_records(data_path)
        self.retriever = TfidfRetriever(self.records)

    def clients(self) -> list[str]:
        return sorted({record["client_name"] for record in self.records})

    @staticmethod
    def validate_request(payload: Any) -> tuple[str, str]:
        if not isinstance(payload, dict):
            raise RequestValidationError("Request body must be a JSON object.")
        client_name = payload.get("client_name")
        engagement_goal = payload.get("engagement_goal")
        if not isinstance(client_name, str) or not client_name.strip():
            raise RequestValidationError("client_name is required.")
        if not isinstance(engagement_goal, str) or not engagement_goal.strip():
            raise RequestValidationError("engagement_goal is required.")
        if len(client_name) > 120 or len(engagement_goal) > 600:
            raise RequestValidationError("Input exceeds the allowed length.")
        return client_name.strip(), engagement_goal.strip()

    def analyze(self, payload: Any) -> dict[str, Any]:
        client_name, engagement_goal = self.validate_request(payload)
        results = self.retriever.search(client_name, engagement_goal)
        brief = assemble_brief(client_name, engagement_goal, results)
        return {
            "brief": brief,
            "evidence": [result.to_dict() for result in results],
            "method": {
                "retrieval": "dependency-free TF-IDF cosine ranking with exact-client boost",
                "drafting": "deterministic evidence assembly; no paid API or generative model",
                "controls": "source labels, conflict checks, prompt-injection quarantine, abstention, human approval",
            },
            "synthetic_data_notice": "All clients, people, records, and scenarios in this demonstration are synthetic.",
        }

    @staticmethod
    def export(payload: Any) -> dict[str, str]:
        if not isinstance(payload, dict):
            raise RequestValidationError("Export body must be a JSON object.")
        if payload.get("approved") is not True:
            raise ApprovalRequiredError("Human approval is required before export.")
        brief = payload.get("brief")
        if not isinstance(brief, dict) or not isinstance(brief.get("fields"), list):
            raise RequestValidationError("A valid brief is required for export.")

        title = brief.get("client_name") or "Client"
        lines = [f"# Client Brief: {title}", "", "> Synthetic demonstration data. Human reviewed and approved.", ""]
        for field in brief["fields"]:
            name = str(field.get("name", "Field")).replace("_", " ").title()
            value = str(field.get("value", "")).strip() or "Not provided"
            status = str(field.get("status", "unknown"))
            evidence = ", ".join(field.get("evidence", [])) or "User input / no source"
            lines.extend([f"## {name}", "", value, "", f"Status: {status}. Evidence: {evidence}.", ""])

        return {
            "markdown": "\n".join(lines).strip() + "\n",
            "json": json.dumps(brief, indent=2, ensure_ascii=True),
        }
