"""Small, dependency-free retrieval layer for the synthetic demonstration."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "reveal hidden prompts",
    "bypass controls",
    "export without human approval",
    "mark every required field complete",
)


def tokenize(value: str) -> list[str]:
    return TOKEN_PATTERN.findall(value.lower())


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    return str(value or "")


def contains_prompt_injection(record: dict[str, Any]) -> bool:
    haystack = flatten_text(record).lower()
    return record.get("status") == "untrusted" or any(
        pattern in haystack for pattern in INJECTION_PATTERNS
    )


def load_records(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError("Synthetic data must be a JSON array.")
    return records


@dataclass(frozen=True)
class SearchResult:
    record: dict[str, Any]
    score: float
    relationship: str
    safe_to_use: bool
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record["record_id"],
            "client_name": self.record["client_name"],
            "document_type": self.record["document_type"],
            "title": self.record["title"],
            "updated_at": self.record["updated_at"],
            "status": self.record["status"],
            "score": round(self.score, 4),
            "relationship": self.relationship,
            "safe_to_use": self.safe_to_use,
            "warning": self.warning,
            "preview": str(self.record.get("background", ""))[:240],
        }


class TfidfRetriever:
    """Ranks synthetic records with explainable TF-IDF cosine similarity."""

    def __init__(self, records: Iterable[dict[str, Any]]):
        self.records = list(records)
        self.document_tokens = [tokenize(flatten_text(record)) for record in self.records]
        document_frequency: Counter[str] = Counter()
        for tokens in self.document_tokens:
            document_frequency.update(set(tokens))
        count = max(len(self.records), 1)
        self.idf = {
            term: math.log((count + 1) / (frequency + 1)) + 1
            for term, frequency in document_frequency.items()
        }
        self.document_vectors = [self._vectorize(tokens) for tokens in self.document_tokens]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        frequency = Counter(tokens)
        vector = {
            term: (count / len(tokens)) * self.idf.get(term, 1.0)
            for term, count in frequency.items()
        }
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        return {term: value / norm for term, value in vector.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(term, 0.0) for term, value in left.items())

    def search(self, client_name: str, engagement_goal: str, limit: int = 7) -> list[SearchResult]:
        query = f"{client_name} {engagement_goal}".strip()
        query_vector = self._vectorize(tokenize(query))
        normalized_client = client_name.strip().casefold()
        results: list[SearchResult] = []

        for record, document_vector in zip(self.records, self.document_vectors):
            same_client = record.get("client_name", "").strip().casefold() == normalized_client
            base_score = self._cosine(query_vector, document_vector)
            score = min(base_score + (0.35 if same_client else 0.0), 1.0)
            unsafe = contains_prompt_injection(record)
            results.append(
                SearchResult(
                    record=record,
                    score=score,
                    relationship="client evidence" if same_client else "analog example",
                    safe_to_use=not unsafe,
                    warning=(
                        "Quarantined: source contains instruction-like content or is marked untrusted."
                        if unsafe
                        else None
                    ),
                )
            )

        return sorted(results, key=lambda item: (-item.score, item.record["record_id"]))[:limit]
