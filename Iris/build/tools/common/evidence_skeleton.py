"""Shared execution-skeleton helpers for the evidence pipelines.

The two evidence pipelines (``recipe_evidence_pipeline.py`` and
``rightclick_evidence_pipeline.py``) already share the **per-stage** execution
skeleton via ``tools.common.stage_runner.StageRunner`` (both import and drive
it). This module collects the remaining small, **mode-agnostic and
output-neutral** entrypoint glue common to both:

- ``pipeline_banner`` — the run header (stdout only).
- ``require_inputs``  — prerequisite input-existence guard (stdout only).

Deliberately **NOT** shared here (evidence-track authority separation, plan §11):

- canonical-SHA functions — each track has its own canonical spec
  (recipe: compact ``separators=(",", ":")``; right-click: default spaced
  separators). Merging them would change one track's artifact bytes (sealed
  determinism drift) and mix track semantics. Kept per-track on purpose.
- phase logic, decision/authority logic, per-track logging, candidate/proof/
  field-registry handling — stay in their own track modules.

Leaf module: standard library only, so it cannot form an import cycle.
"""
from __future__ import annotations

from pathlib import Path


def pipeline_banner(title: str, width: int = 60) -> None:
    """Print the standard pipeline run header (stdout only, no artifact impact)."""
    bar = "=" * width
    print(bar)
    print(f"  {title}")
    print(bar)


def require_inputs(named_paths: list[tuple[Path, str]]) -> bool:
    """Return ``True`` iff every input path exists.

    On the first missing path, print a FAIL line and return ``False``. This is a
    mode-agnostic prerequisite guard; it never touches an output artifact.
    """
    for path, label in named_paths:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return False
    return True
