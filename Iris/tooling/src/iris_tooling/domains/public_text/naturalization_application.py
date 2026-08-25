from __future__ import annotations

from .naturalization_handoff import *  # noqa: F401,F403


def run_naturalization_mode(
    *,
    attempt_id: str,
    mode: str,
    attempt_root: Path | None = None,
    provenance_inputs: NaturalizationProvenanceInputs | None = None,
) -> dict[str, Any]:
    root = attempt_root_for(attempt_id, attempt_root)
    if mode == "phase0-preflight":
        if provenance_inputs is None:
            raise NaturalizationError(
                "phase0-preflight requires explicit roadmap, plan-review, and cycle2-review inputs"
            )
        return build_phase0(
            attempt_id,
            root,
            provenance_inputs=provenance_inputs,
        )
    builders = {
        "phase1-census": build_phase1,
        "phase2-source-inventory": build_phase2,
        "phase3-compiler-evidence": build_phase3,
        "phase4-candidate": build_phase4,
        "phase5-semantic": build_phase5_semantic,
        "phase5-adversarial": build_phase5_adversarial,
        "phase6-raw-detectors": build_phase6,
        "phase7-human-review-sample": build_phase7,
        "phase8-publish-handoff": build_phase8_handoff,
    }
    try:
        builder = builders[mode]
    except KeyError as exc:
        raise NaturalizationError(f"unknown naturalization mode: {mode}") from exc
    return builder(attempt_id, root)

__all__ = [
    name for name in globals() if not name.startswith("__")
]
