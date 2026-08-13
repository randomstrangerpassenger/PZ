from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from Iris.build.description.v2.tests.test_public_text_quality_acceptance_current_route import (
    PublicTextQualityAcceptanceCurrentRouteTest,
)


def test_class_lifecycle_owns_exactly_one_phase7_execution() -> None:
    completed = Mock(returncode=0, stdout='{"cases": {}}', stderr="")
    with patch("subprocess.run", return_value=completed) as run:
        PublicTextQualityAcceptanceCurrentRouteTest.setUpClass()
        try:
            first = PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()
            second = PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()
            assert first is second
            assert run.call_count == 1
        finally:
            PublicTextQualityAcceptanceCurrentRouteTest.tearDownClass()


def test_malformed_phase7_output_fails_before_probe_access() -> None:
    completed = Mock(returncode=0, stdout="not-json", stderr="")
    with patch("subprocess.run", return_value=completed), pytest.raises(AssertionError, match="malformed JSON"):
        PublicTextQualityAcceptanceCurrentRouteTest._run_phase7_self_test()
