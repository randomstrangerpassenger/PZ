from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_food_semantic.contracts import repo_root
from dvf_3_3_food_semantic.curation_proposals import (
    record_exact_owner_batch_approvals,
    validate_batch_approvals,
)
from dvf_3_3_food_semantic.curation_rework_resolution import (
    materialize_resolved_curation,
)


DEFAULT_PROPOSAL_ROOT = Path(
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/"
    "curation_rework_resolution_0001"
)
DEFAULT_PRIOR_AUTHORITY_ROOT = Path(
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0007/"
    "post_implementation_authority/authority-execution-0001"
)
DEFAULT_DECISIONS = Path(
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/"
    "owner_reserved_decisions.json"
)


def _resolve(root: Path, value: Path) -> Path:
    return value if value.is_absolute() else root / value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Approve, validate, or materialize rework resolution."
    )
    parser.add_argument(
        "command",
        choices=("validate", "approve", "materialize"),
    )
    parser.add_argument(
        "--proposal-root",
        type=Path,
        default=DEFAULT_PROPOSAL_ROOT,
    )
    parser.add_argument(
        "--prior-authority-root",
        type=Path,
        default=DEFAULT_PRIOR_AUTHORITY_ROOT,
    )
    parser.add_argument("--successor-authority-root", type=Path)
    parser.add_argument(
        "--owner-decisions",
        type=Path,
        default=DEFAULT_DECISIONS,
    )
    parser.add_argument("--owner-directive")
    parser.add_argument("--approval-rationale")
    parser.add_argument("--approval-time")
    parser.add_argument("--require-all-approved", action="store_true")
    args = parser.parse_args()
    root = repo_root()
    proposal_root = _resolve(root, args.proposal_root)
    decisions_path = _resolve(root, args.owner_decisions)
    prior_root = _resolve(root, args.prior_authority_root)
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
        if args.successor_authority_root is None:
            raise SystemExit(
                "--successor-authority-root is required for materialize"
            )
        report = materialize_resolved_curation(
            proposal_root,
            prior_authority_root=prior_root,
            successor_authority_root=_resolve(
                root,
                args.successor_authority_root,
            ),
            owner_decisions_path=decisions_path,
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    status = report.get("status", report.get("validation_status"))
    return 0 if status in {
        "PASS",
        "PASS_COMPLETE",
        "PENDING",
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
