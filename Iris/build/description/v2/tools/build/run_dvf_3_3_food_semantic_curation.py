from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_food_semantic.contracts import repo_root
from dvf_3_3_food_semantic.curation_proposals import (
    materialize_approved_curation,
    record_exact_owner_batch_approvals,
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
    result.add_argument(
        "command",
        choices=("validate", "approve", "materialize"),
    )
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
    result.add_argument("--owner-directive")
    result.add_argument("--approval-rationale")
    result.add_argument("--approval-time")
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
    elif args.command == "approve":
        if args.owner_directive is None:
            raise SystemExit("--owner-directive is required for approve")
        if args.approval_rationale is None:
            raise SystemExit("--approval-rationale is required for approve")
        report = record_exact_owner_batch_approvals(
            proposal_root,
            owner_decisions_path=decisions_path,
            approval_directive=args.owner_directive,
            approval_rationale=args.approval_rationale,
            approval_time=args.approval_time,
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
    status = report.get("status", report.get("validation_status"))
    return 0 if status in {
        "PASS",
        "PASS_COMPLETE",
        "PASS_WITH_REWORK",
        "PENDING",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
