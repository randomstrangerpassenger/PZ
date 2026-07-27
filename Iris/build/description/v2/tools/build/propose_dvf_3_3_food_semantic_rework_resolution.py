from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_food_semantic.contracts import repo_root
from dvf_3_3_food_semantic.curation_rework_resolution import (
    write_rework_resolution_bundle,
)


DEFAULT_PRIOR_AUTHORITY_ROOT = Path(
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0007/"
    "post_implementation_authority/authority-execution-0001"
)
DEFAULT_OUTPUT_ROOT = Path(
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/"
    "curation_rework_resolution_0001"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the two-item food-semantic rework resolution packet."
    )
    parser.add_argument("--attempt-id", default="attempt-0007")
    parser.add_argument(
        "--prior-authority-root",
        type=Path,
        default=DEFAULT_PRIOR_AUTHORITY_ROOT,
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
    )
    args = parser.parse_args()
    root = repo_root()
    attempt_root = (
        root
        / "Iris/build/description/v2/staging/"
        "dvf_3_3_food_semantic_facts_authority/attempts"
        / args.attempt_id
    )
    prior_root = (
        args.prior_authority_root
        if args.prior_authority_root.is_absolute()
        else root / args.prior_authority_root
    )
    output_root = (
        args.output_root
        if args.output_root.is_absolute()
        else root / args.output_root
    )
    report = write_rework_resolution_bundle(
        root,
        attempt_root,
        prior_authority_root=prior_root,
        output_root=output_root,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["validation_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
