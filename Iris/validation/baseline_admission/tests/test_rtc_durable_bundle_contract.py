from __future__ import annotations

from Iris.validation.baseline_admission.iris_baseline_admission_common import CONTEXT


def test_composite_context_is_distinct_from_standalone_gate() -> None:
    assert CONTEXT == "composite_baseline_admission_chain_stage_6"
    assert CONTEXT != "standalone_full_gate"
