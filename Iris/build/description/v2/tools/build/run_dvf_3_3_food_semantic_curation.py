from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_food_semantic.contracts import repo_root
from dvf_3_3_food_semantic.curation_proposals import (
    materialize_approved_curation,
    validate_batch_approvals,
)


DEFAULT_PROPOSAL_ROOT = Path(
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/curation_proposals"
)
DEFAULT_DECISIONS = Path(
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/owner_reserved_decisions.json"
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Validate and materialize approved food-semantic curation batches."
    )
    result.add_argument("command", choices=("validate", "materialize"))
    result.add_argument("--proposal-root", type=Path, default=DEFAULT_PROPOSAL_ROOT)
    result.add_argument("--owner-decisions", type=Path, default=DEFAULT_DECISIONS)
    result.add_argument(
        "--authority-root",
        type=Path,
        help=(
            "Attempt-local non-current execution root; protected/current "
            "repository sinks are rejected."
        ),
    )
    result.add_argument("--require-all-approved", action="store_true")
    return result


def _resolve(root: Path, value: Path) -> Path:
    return value if value.is_absolute() else root / value


def main() -> int:
    args = parser().parse_args()
    root = repo_root()
    proposal_root = _resolve(root, args.proposal_root)
    decisions_path = _resolve(root, args.owner_decisions)
    if args.command == "validate":
        report = validate_batch_approvals(
            proposal_root,
            owner_decisions_path=decisions_path,
            require_all_approved=args.require_all_approved,
        )
    else:
        if args.authority_root is None:
            raise SystemExit("--authority-root is required for materialize")
        authority_root = _resolve(root, args.authority_root)
        report = materialize_approved_curation(
            proposal_root,
            authority_root,
            owner_decisions_path=decisions_path,
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] in {"PASS", "PASS_COMPLETE", "PASS_WITH_REWORK", "PENDING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
