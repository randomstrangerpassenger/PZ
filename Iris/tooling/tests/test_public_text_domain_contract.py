from __future__ import annotations

import pytest

from iris_tooling.domains.public_text.evaluate import (
    PublicTextEvaluationError,
    determine_qualified_disposition,
    evaluate_threshold,
)
from iris_tooling.domains.public_text.inputs import PublicTextInputError, load_json_bytes
from iris_tooling.domains.public_text.naturalization import select_rank


def test_threshold_and_disposition_are_pure_domain_contracts() -> None:
    assert evaluate_threshold(
        numerator=1,
        denominator=4,
        threshold={"operator": "le", "value": {"numerator": 1, "denominator": 2}},
    )
    assert determine_qualified_disposition(
        technical_blocker_count=0,
        effective_blocking_finding_count=0,
        advisory_debt_count=1,
        active_waiver_count=0,
    ) == "deferred_internal_debt"
    with pytest.raises(PublicTextEvaluationError):
        evaluate_threshold(numerator=-1, denominator=1, threshold={"operator": "none", "value": None})


def test_strict_input_and_candidate_rank_are_deterministic() -> None:
    with pytest.raises(PublicTextInputError, match="duplicate JSON key"):
        load_json_bytes(b'{"a":1,"a":2}', label="fixture")
    assert select_rank("candidate", "stratum", "Base.Hammer") == select_rank(
        "candidate", "stratum", "Base.Hammer"
    )
