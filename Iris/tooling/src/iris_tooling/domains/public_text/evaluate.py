from __future__ import annotations

from fractions import Fraction
from typing import Any


class PublicTextEvaluationError(ValueError):
    """Raised when a public-text rule receives an invalid metric shape."""


def _fraction_from_value(value: dict[str, Any]) -> Fraction:
    if set(value) == {"integer"}:
        integer = value["integer"]
        if not isinstance(integer, int):
            raise PublicTextEvaluationError("threshold integer must be an integer")
        return Fraction(integer, 1)
    if set(value) == {"numerator", "denominator"}:
        numerator = value["numerator"]
        denominator = value["denominator"]
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise PublicTextEvaluationError("rational threshold must use integers")
        if denominator <= 0:
            raise PublicTextEvaluationError(
                "rational threshold denominator must be positive"
            )
        return Fraction(numerator, denominator)
    raise PublicTextEvaluationError(
        "threshold value must be exact integer or rational"
    )


def evaluate_threshold(
    *, numerator: int, denominator: int, threshold: dict[str, Any]
) -> bool:
    if not isinstance(numerator, int) or numerator < 0:
        raise PublicTextEvaluationError(
            "metric numerator must be a nonnegative integer"
        )
    if not isinstance(denominator, int) or denominator <= 0:
        raise PublicTextEvaluationError(
            "metric denominator must be a positive integer"
        )
    operator = threshold.get("operator")
    value = threshold.get("value")
    if operator == "none":
        if value is not None:
            raise PublicTextEvaluationError("none threshold must have null value")
        return True
    if not isinstance(value, dict):
        raise PublicTextEvaluationError("threshold value object is required")
    expected = _fraction_from_value(value)
    actual = (
        Fraction(numerator, 1)
        if set(value) == {"integer"}
        else Fraction(numerator, denominator)
    )
    operations = {
        "eq": actual == expected,
        "le": actual <= expected,
        "lt": actual < expected,
        "ge": actual >= expected,
        "gt": actual > expected,
    }
    if operator not in operations:
        raise PublicTextEvaluationError(f"unknown threshold operator: {operator}")
    return operations[operator]


def determine_qualified_disposition(
    *,
    technical_blocker_count: int,
    effective_blocking_finding_count: int,
    advisory_debt_count: int,
    active_waiver_count: int,
) -> str:
    counts = (
        technical_blocker_count,
        effective_blocking_finding_count,
        advisory_debt_count,
        active_waiver_count,
    )
    if any(not isinstance(value, int) or value < 0 for value in counts):
        raise PublicTextEvaluationError(
            "disposition counts must be nonnegative integers"
        )
    if technical_blocker_count > 0 or effective_blocking_finding_count > 0:
        return "blocked"
    if advisory_debt_count > 0 or active_waiver_count > 0:
        return "deferred_internal_debt"
    return "accepted"
