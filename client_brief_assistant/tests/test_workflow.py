from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.service import ApprovalRequiredError, BriefService, RequestValidationError  # noqa: E402


class BriefWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.service = BriefService(ROOT / "data" / "synthetic_records.json")

    def test_known_client_prioritizes_client_evidence(self) -> None:
        result = self.service.analyze(
            {
                "client_name": "Northstar Retail",
                "engagement_goal": "Explain regional sales performance for the quarterly review.",
            }
        )
        self.assertEqual(result["evidence"][0]["relationship"], "client evidence")
        self.assertGreaterEqual(result["brief"]["evidence_count"], 3)
        self.assertFalse(result["brief"]["abstained"])

    def test_conflicting_source_details_are_flagged(self) -> None:
        result = self.service.analyze(
            {
                "client_name": "Northstar Retail",
                "engagement_goal": "Prepare the quarterly business review.",
            }
        )
        self.assertIn("deadline", result["brief"]["conflicting_fields"])
        self.assertIn("requested_deliverable", result["brief"]["conflicting_fields"])
        self.assertTrue(any("Which is current" in question for question in result["brief"]["clarification_questions"]))

    def test_no_match_abstains_and_keeps_analogs_separate(self) -> None:
        result = self.service.analyze(
            {
                "client_name": "Orchid Labs",
                "engagement_goal": "Prepare a market-entry decision brief.",
            }
        )
        self.assertTrue(result["brief"]["abstained"])
        self.assertEqual(result["brief"]["evidence_count"], 0)
        self.assertGreater(len(result["brief"]["analog_suggestions"]), 0)
        self.assertIn("industry", result["brief"]["required_missing_fields"])

    def test_prompt_injection_source_is_quarantined(self) -> None:
        result = self.service.analyze(
            {
                "client_name": "Apex Harbor Logistics",
                "engagement_goal": "Create a port delay response brief.",
            }
        )
        quarantined = [item for item in result["evidence"] if not item["safe_to_use"]]
        self.assertEqual(len(quarantined), 1)
        self.assertEqual(quarantined[0]["record_id"], "APEX-NOTE-002")
        self.assertTrue(result["brief"]["warnings"])
        background = next(field for field in result["brief"]["fields"] if field["name"] == "background")
        self.assertNotIn("Ignore previous instructions", background["value"])

    def test_malformed_input_is_rejected(self) -> None:
        for payload in (None, [], {}, {"client_name": "Only client"}):
            with self.subTest(payload=payload):
                with self.assertRaises(RequestValidationError):
                    self.service.analyze(payload)

    def test_export_requires_explicit_human_approval(self) -> None:
        result = self.service.analyze(
            {"client_name": "Copperline Energy", "engagement_goal": "Prepare a reliability brief."}
        )
        with self.assertRaises(ApprovalRequiredError):
            self.service.export({"approved": False, "brief": result["brief"]})

    def test_approved_export_returns_markdown_and_json(self) -> None:
        result = self.service.analyze(
            {"client_name": "Copperline Energy", "engagement_goal": "Prepare a reliability brief."}
        )
        exported = self.service.export({"approved": True, "brief": result["brief"]})
        self.assertIn("# Client Brief: Copperline Energy", exported["markdown"])
        self.assertEqual(json.loads(exported["json"])["client_name"], "Copperline Energy")

    def test_deterministic_analysis_is_repeatable(self) -> None:
        request = {"client_name": "Lumen Foods", "engagement_goal": "Assess profitable distributor growth."}
        self.assertEqual(self.service.analyze(request), self.service.analyze(request))


if __name__ == "__main__":
    unittest.main(verbosity=2)
