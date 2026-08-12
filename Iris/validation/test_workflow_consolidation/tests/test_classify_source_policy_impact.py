from __future__ import annotations

from Iris.validation.test_workflow_consolidation.classify_source_policy_impact import (
    is_under,
    policy_sources,
)


def test_successor_explicit_path_is_outside_default_and_controlled_roots() -> None:
    source = "Iris/validation/test_workflow_consolidation/tests/test_example.py"
    assert not is_under(source, "Iris/build/description/v2/tests")
    assert not is_under(source, "Iris/build/tests/test_evidence_pipeline_cross_track.py")


def test_policy_sources_keeps_route_authority_separate() -> None:
    payload = {
        "reviewed_sources": [
            {"source_file": "Iris/build/description/v2/tests/test_a.py", "classification": "current"}
        ],
        "excluded_sources": [
            {"source_file": "Iris/build/description/v2/tests/test_b.py"}
        ],
    }
    assert policy_sources(payload) == {
        "Iris/build/description/v2/tests/test_a.py": "current",
        "Iris/build/description/v2/tests/test_b.py": "excluded",
    }

