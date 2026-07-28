from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ATTEMPT_ID = "attempt-0022"
ATTEMPT_RELATIVE = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0022"
)
PLAN_PATH = (
    "docs/dvf_3_3_food_semantic_facts_authority_reconstruction_"
    "implementation_plan.md"
)
OWNER_DECISIONS_PATH = (
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/attempt-0022/"
    "owner_decisions.json"
)
EXPECTED_PLAN_SHA256 = (
    "e23fff82de3cf661fb0d22299f708989a7ae75589e70bbfd6e3ec442b1c8d26f"
)
EXPECTED_SCOPE_DIRECTION_SHA256 = (
    "85b4038c4395eab0fd4d3fc9313e1fe461e6225fca3f8d00f9eca525f80f16ea"
)
SCOPED_RECEIPT_NAME = "vc1_focused_validation_receipt.json"
CORRECTION_REVIEW_NAME = "validation_contract_correction_review_v2.json"


class CloseoutOverlayError(RuntimeError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise CloseoutOverlayError(code)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"json_object_required:{path}")
    return value


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise CloseoutOverlayError(
            f"git_failed:{' '.join(args)}:{completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def ensure_attempt_root(repo: Path, attempt_root: Path) -> Path:
    resolved = attempt_root.resolve()
    try:
        relative = resolved.relative_to(repo.resolve()).as_posix()
    except ValueError as exc:
        raise CloseoutOverlayError("attempt_root_outside_repository") from exc
    require(relative == ATTEMPT_RELATIVE, "attempt_root_identity_mismatch")
    return resolved


def prepare_with_vc1_overlay(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    attempt_root = ensure_attempt_root(repo, Path(args.attempt_root))
    owner_decisions = Path(args.owner_decisions).resolve()
    require(
        owner_decisions == (repo / OWNER_DECISIONS_PATH).resolve(),
        "owner_decisions_path_mismatch",
    )
    require(
        run_git(
            repo,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        == "",
        "repository_must_be_clean_before_closeout_overlay",
    )
    plan_path = repo / PLAN_PATH
    require(
        sha256_file(plan_path) == EXPECTED_PLAN_SHA256,
        "current_plan_sha256_mismatch",
    )

    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(attempt_root / "phase13_closeout"))
    from vc1_validation_contract import validate_recorded
    from Iris.build.description.v2.tools.build.dvf_3_3_food_semantic.closeout import (
        prepare_terminal_closeout,
    )
    from Iris.build.description.v2.tools.build.dvf_3_3_food_semantic.contracts import (
        artifact_manifest,
        canonical_json_bytes,
        load_json,
        sha256_bytes,
        write_json,
    )

    validation = validate_recorded(
        argparse.Namespace(repo=str(repo), attempt_root=str(attempt_root))
    )
    require(validation.get("status") == "PASS", "vc1_validation_not_pass")
    original_result = prepare_terminal_closeout(
        repo,
        attempt_root,
        ATTEMPT_ID,
        owner_decisions_path=owner_decisions,
    )
    require(
        original_result.get("status")
        == "READY_FOR_TERMINAL_INDEPENDENT_REVIEW",
        "base_closeout_not_ready",
    )

    phase = attempt_root / "phase13_closeout"
    final_manifest_path = phase / "final_artifact_manifest.json"
    final_manifest = load_json(final_manifest_path)
    rows = [
        row
        for row in final_manifest["artifacts"]
        if row.get("path") != PLAN_PATH
    ]
    plan_row = artifact_manifest([plan_path], root=repo)[0]
    require(
        plan_row["sha256"] == EXPECTED_PLAN_SHA256,
        "plan_manifest_row_sha256_mismatch",
    )
    rows.append(plan_row)
    rows.sort(key=lambda row: row["path"])
    final_manifest.update(
        {
            "artifact_count": len(rows),
            "artifact_manifest_sha256": sha256_bytes(
                canonical_json_bytes(rows)
            ),
            "artifacts": rows,
            "validation_contract": "VC-1+owner-scoped-Appendix-C",
            "current_plan_path": PLAN_PATH,
            "current_plan_sha256": EXPECTED_PLAN_SHA256,
            "current_plan_git_blob_id": run_git(
                repo, "rev-parse", f"HEAD:{PLAN_PATH}"
            ),
            "scope_direction_sha256": EXPECTED_SCOPE_DIRECTION_SHA256,
            "scoped_validation_receipt_sha256": sha256_file(
                phase / SCOPED_RECEIPT_NAME
            ),
            "closeout_overlay_applied": True,
        }
    )
    write_json(final_manifest_path, final_manifest, write_once=False)

    review_request_path = phase / "terminal_review_request.json"
    review_request = load_json(review_request_path)
    pre_vc1_plan = {
        "path": review_request["plan_path"],
        "sha256": review_request["plan_sha256"],
        "git_blob_id": review_request["plan_git_blob_id"],
        "authority": "historical_phase0_traceability",
    }
    review_request.update(
        {
            "reviewed_final_artifact_manifest_sha256": sha256_file(
                final_manifest_path
            ),
            "plan_path": PLAN_PATH,
            "plan_sha256": EXPECTED_PLAN_SHA256,
            "plan_git_blob_id": final_manifest[
                "current_plan_git_blob_id"
            ],
            "plan_identity_authority": "VC-1_owner-scoped-Appendix-C",
            "pre_vc1_traceability_plan": pre_vc1_plan,
            "validation_contract": "VC-1+owner-scoped-Appendix-C",
            "scope_direction_sha256": EXPECTED_SCOPE_DIRECTION_SHA256,
            "correction_review_sha256": sha256_file(
                phase / CORRECTION_REVIEW_NAME
            ),
            "scoped_validation_receipt_sha256": sha256_file(
                phase / SCOPED_RECEIPT_NAME
            ),
            "closeout_overlay_applied": True,
        }
    )
    write_json(review_request_path, review_request, write_once=False)

    final_manifest_check = load_object(final_manifest_path)
    review_request_check = load_object(review_request_path)
    require(
        sum(
            row.get("path") == PLAN_PATH
            for row in final_manifest_check["artifacts"]
        )
        == 1,
        "current_plan_manifest_denominator_mismatch",
    )
    require(
        review_request_check.get("plan_sha256") == EXPECTED_PLAN_SHA256
        and review_request_check.get(
            "reviewed_final_artifact_manifest_sha256"
        )
        == sha256_file(final_manifest_path),
        "terminal_review_request_overlay_mismatch",
    )
    return {
        "status": "READY_FOR_TERMINAL_INDEPENDENT_REVIEW",
        "attempt_id": ATTEMPT_ID,
        "validation_contract": "VC-1+owner-scoped-Appendix-C",
        "final_artifact_manifest_sha256": sha256_file(
            final_manifest_path
        ),
        "terminal_review_request_sha256": sha256_file(
            review_request_path
        ),
        "current_plan_sha256": EXPECTED_PLAN_SHA256,
        "closeout_overlay_applied": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare terminal closeout with the VC-1 plan overlay."
    )
    parser.add_argument("--repo", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--owner-decisions", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = prepare_with_vc1_overlay(args)
    except (
        CloseoutOverlayError,
        OSError,
        RuntimeError,
        KeyError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(
            json.dumps(
                {"status": "BLOCKED", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
