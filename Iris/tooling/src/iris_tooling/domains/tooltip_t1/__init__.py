"""Iris Tooltip T1 offline contract and readiness audit."""

from typing import Any


def __getattr__(name: str) -> Any:
    if name == "run_candidate":
        from .audit import run_candidate

        return run_candidate
    raise AttributeError(name)

__all__ = ("run_candidate",)
