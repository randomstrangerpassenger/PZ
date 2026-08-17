from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from Iris.build.description.v2.tests.test_public_text_quality_acceptance_current_route import (
    PublicTextQualityAcceptanceCurrentRouteTest,
)


def test_class_lifecycle_owns_exactly_one_phase7_execution() -> None:
    completed = Mock(
        returncode=0,
        stdout=json.dumps(
            {
                "cases": {
                    "historical_v1_and_current_v2_acceptance": {
                        "historical_dispatch": "historical_v1",
                        "current_dispatch": "current_v2_successor_0010",
                    },
                    "unknown_and_malformed_schema_rejection": {"status": "PASS"},
                    "successor_transaction_hash_mismatch_rejection": {
                        "status": "PASS",
                        "mismatch_field_count": 3,
                    },
                    "deterministic_document_replay": {"status": "PASS"},
                }
            }
        ),
        stderr="",
    )
    with patch("subprocess.run", return_value=completed) as run, patch.object(
        PublicTextQualityAcceptanceCurrentRouteTest,
        "_git",
        return_value="fixture-git-identity",
    ):
        PublicTextQualityAcceptanceCurrentRouteTest.setUpClass()
        try:
            first = PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()
            second = PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()
            assert first is second
            assert run.call_count == 1
            assert first.context.route_class == "all_explicit_path"
            assert [probe.status for probe in first.probe_results] == ["PASS"] * 4
        finally:
            PublicTextQualityAcceptanceCurrentRouteTest.tearDownClass()


def test_malformed_phase7_output_fails_before_probe_access() -> None:
    completed = Mock(returncode=0, stdout="not-json", stderr="")
    with patch("subprocess.run", return_value=completed), pytest.raises(AssertionError, match="malformed JSON"):
        PublicTextQualityAcceptanceCurrentRouteTest._run_phase7_self_test()
