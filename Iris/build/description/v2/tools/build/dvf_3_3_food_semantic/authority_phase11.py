from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .authority_phase9_10 import (
    CURRENT_FACTS,
    CURRENT_MANIFEST,
    FORBIDDEN_REGISTRY,
    OWNER_DECISIONS,
    PROPOSITION_LICENSE,
    SCHEMA,
    _bundle_artifact,
    _validate_bundled_authority_contracts,
)
from .contracts import (
    FoodSemanticError,
    canonical_json_bytes,
    identity,
    load_json,
    load_jsonl,
    relative_posix,
    repo_root,
    sha256_bytes,
    sha256_file,
    write_once_bytes,
)


PHASE9_10_OUTPUT_REVIEW_SHA256 = (
    "d679374037286737867295bf6cbe5ea9f5a944cbc9e3ee3d1f7e13da9297b23b"
)
PHASE9_10_REVIEWED_COMMIT_SHA = (
    "8797392ef674d937f39ffa6c3432283d0848e51d"
)
IMPLEMENTATION_BUNDLE_SHA256 = (
    "41352d42779ecbc86fd122f08d6388f22a69d1b29a5caa8e4f352a9a414b9205"
)
OWNER_DECISIONS_SHA256 = (
    "3abf570cc58a791a729671c3731f524b75acb9ec8e5cd5f89afb4c6097e6213a"
)

PHASE9_FILES = {
    "approved_automatic_fact_ledger.jsonl",
    "arbitrary_inference_zero_report.json",
    "coverage_reconciliation_report.json",
    "forbidden_inference_registry_binding.json",
    "full_317_semantic_disposition.jsonl",
    "layer4_non_promotion_report.json",
    "phase9_authority_execution_receipt.json",
    "semantic_consistency_report.json",
    "singleton_disposition_closure.json",
    "unsupported_fact_zero_report.json",
}
PHASE10_FILES = {
    "candidate_determinism_report.json",
    "candidate_diff_report.json",
    "candidate_lineage_bundle.jsonl",
    "candidate_successor_facts.jsonl",
    "candidate_successor_input_manifest.json",
    "candidate_validation_report.json",
    "phase10_candidate_receipt.json",
    "writer_attempt_manifest.json",
}


def _logical_row_count(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for raw in handle if raw.strip())


def _expected_reviewed_artifacts(
    authority_root: Path,
    *,
    root: Path,
) -> set[str]:
    return {
        relative_posix(authority_root / "phase9_coverage" / name, root=root)
        for name in PHASE9_FILES
    } | {
        relative_posix(authority_root / "phase10_candidate" / name, root=root)
        for name in PHASE10_FILES
    }


def _validate_identity_row(
    root: Path,
    row: dict[str, Any],
    *,
    require_row_count: bool = False,
) -> Path:
    relative = row.get("path")
    if not isinstance(relative, str):
        raise FoodSemanticError("reviewed artifact path is missing")
    path = root / relative
    if (
        not path.is_file()
        or sha256_file(path) != row.get("sha256")
        or path.stat().st_size != row.get("byte_count")
    ):
        raise FoodSemanticError(
            f"reviewed artifact identity mismatch: {relative}"
        )
    if require_row_count:
        observed_row_count = (
            _logical_row_count(path) if path.suffix == ".jsonl" else 1
        )
        if row.get("row_count") != observed_row_count:
            raise FoodSemanticError(
                f"reviewed artifact row count mismatch: {relative}"
            )
    return path


def _validate_phase9_10_output_review(
    root: Path,
    attempt_root: Path,
    authority_root: Path,
) -> dict[str, Any]:
    review_path = authority_root / "phase9_10_external_output_review.json"
    if (
        not review_path.is_file()
        or sha256_file(review_path) != PHASE9_10_OUTPUT_REVIEW_SHA256
    ):
        raise FoodSemanticError(
            "Phase 9/10 external output review identity mismatch"
        )
    review = load_json(review_path)
    counts = review.get("finding_counts", {})
    target = review.get("review_target", {})
    if (
        review.get("verdict") != "PASS"
        or review.get("review_verdict") != "PASS"
        or review.get("phase9_10_scope_verdict") != "PASS"
        or review.get("phase9_10_output_scope_verdict") != "PASS"
        or review.get("phase9_10_external_output_review_passed") is not True
        or review.get("reviewer_identity") != "Codex Reviewer"
        or review.get("reviewer_is_implementation_author") is not False
        or counts.get("critical") != 0
        or counts.get("important") != 0
        or counts.get("minor") != 0
        or review.get("phase11_execution_allowed") is not True
        or review.get("current_mutation_authorized") is not False
        or review.get("current_adoption_allowed") is not False
        or review.get("terminal_independent_gate_credit") != 0
        or review.get("reviewed_commit_sha")
        != PHASE9_10_REVIEWED_COMMIT_SHA
        or target.get("authority_root")
        != relative_posix(authority_root, root=root)
        or target.get("bound_attempt_id") != attempt_root.name
        or target.get("reviewed_total_artifact_count") != 18
        or target.get("commit_changed_current_or_protected_path_count") != 0
        or review.get("actual_phase11_execution_performed_by_review")
        is not False
        or review.get("actual_current_adoption_performed_by_review")
        is not False
        or review.get("actual_terminal_review_performed_by_review")
        is not False
    ):
        raise FoodSemanticError(
            "Phase 9/10 external output review is not exact PASS"
        )
    reviewed = review.get("reviewed_artifacts")
    if not isinstance(reviewed, list):
        raise FoodSemanticError("reviewed artifact manifest is missing")
    reviewed_by_path = {row.get("path"): row for row in reviewed}
    expected = _expected_reviewed_artifacts(authority_root, root=root)
    if len(reviewed) != 18 or set(reviewed_by_path) != expected:
        raise FoodSemanticError("reviewed Phase 9/10 artifact set mismatch")
    for row in reviewed:
        _validate_identity_row(root, row, require_row_count=True)

    implementation_chain = review.get("reviewed_implementation_chain", {})
    implementation_review = implementation_chain.get(
        "external_implementation_review", {}
    )
    implementation_review_path = root / str(
        implementation_review.get("path", "")
    )
    if (
        not implementation_review_path.is_file()
        or sha256_file(implementation_review_path)
        != implementation_review.get("sha256")
        or implementation_review.get("verdict") != "PASS"
        or implementation_review.get("authority_execution_allowed") is not True
    ):
        raise FoodSemanticError(
            "Phase 9/10 external implementation review chain mismatch"
        )
    phase8_chain = review.get("reviewed_phase8_authority_chain", {})
    if (
        phase8_chain.get("owner_decisions", {}).get("sha256")
        != OWNER_DECISIONS_SHA256
        or phase8_chain.get("implementation_complete_bundle", {}).get(
            "sha256"
        )
        != IMPLEMENTATION_BUNDLE_SHA256
    ):
        raise FoodSemanticError("Phase 8 authority chain identity mismatch")
    return review


def _decision_by_id(
    decisions: dict[str, Any],
    decision_id: str,
) -> dict[str, Any]:
    matches = [
        row
        for row in decisions.get("decisions", [])
        if row.get("decision_id") == decision_id
    ]
    if len(matches) != 1:
        raise FoodSemanticError(f"owner decision {decision_id} is not unique")
    return matches[0]


def _validate_owner_branch_decisions(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    path = root / OWNER_DECISIONS
    if not path.is_file() or sha256_file(path) != OWNER_DECISIONS_SHA256:
        raise FoodSemanticError("owner decision record identity mismatch")
    decisions = load_json(path)
    if (
        decisions.get("record_status") != "approved"
        or decisions.get("approver_identity") != "repository_owner"
        or decisions.get("bound_implementation_complete_bundle_sha256")
        != IMPLEMENTATION_BUNDLE_SHA256
        or decisions.get("current_authority_mutation_authorized") is not False
        or decisions.get("registry_operational_cutover_authorized") is not False
    ):
        raise FoodSemanticError("owner decision envelope is not exact approved")
    d9 = _decision_by_id(decisions, "D9")
    d12 = _decision_by_id(decisions, "D12")
    if (
        d9.get("status") != "approved"
        or d9.get("selected_option")
        != "branch_B_sealed_non_current_handoff_and_future_registry_request"
        or d9.get("selection_parameters")
        != {
            "selected_branch": "B",
            "future_registry_cutover_request_allowed": True,
            "current_mutation_allowed": False,
            "separate_registry_operational_cutover_plan_required": True,
        }
        or d9.get("bound_implementation_complete_bundle_sha256")
        != IMPLEMENTATION_BUNDLE_SHA256
    ):
        raise FoodSemanticError("owner decision D9 does not authorize Branch B")
    if (
        d12.get("status") != "approved"
        or d12.get("selected_option")
        != "registry_owned_additive_correction_successor"
        or d12.get("selection_parameters")
        != {
            "correction_owner": "Iris Artifact Registry",
            "operational_route": (
                "separate_reviewed_registry_operational_cutover_plan"
            ),
            "predecessor_current_reentry_allowed": False,
            "predecessor_fallback_after_future_promotion_allowed": False,
            "partial_or_dual_current_allowed": False,
        }
        or d12.get("bound_implementation_complete_bundle_sha256")
        != IMPLEMENTATION_BUNDLE_SHA256
    ):
        raise FoodSemanticError(
            "owner decision D12 correction route mismatch"
        )
    return decisions, d9, d12


def _validate_contract_bindings(
    root: Path,
    attempt_root: Path,
    output_review: dict[str, Any],
) -> dict[str, Any]:
    contracts = _validate_bundled_authority_contracts(root, attempt_root)
    reviewed = {
        row.get("path"): row
        for row in output_review.get("reviewed_sealed_contracts", [])
    }
    expected = {
        SCHEMA.as_posix(): contracts["identities"]["schema"],
        PROPOSITION_LICENSE.as_posix(): contracts["identities"][
            "proposition_license"
        ],
        FORBIDDEN_REGISTRY.as_posix(): contracts["identities"][
            "forbidden_registry"
        ],
    }
    if set(reviewed) != set(expected):
        raise FoodSemanticError("reviewed sealed contract set mismatch")
    for relative, bundle_row in expected.items():
        review_row = reviewed[relative]
        if (
            review_row.get("sha256") != bundle_row.get("sha256")
            or review_row.get("byte_count") != bundle_row.get("byte_count")
            or review_row.get("implementation_bundle_identity_match")
            is not True
            or review_row.get("phase9_receipt_binding_match") is not True
        ):
            raise FoodSemanticError(
                f"reviewed sealed contract identity mismatch: {relative}"
            )
    return contracts


def _validate_phase10_candidate(
    root: Path,
    authority_root: Path,
    output_review: dict[str, Any],
    contracts: dict[str, Any],
) -> dict[str, Any]:
    phase10 = authority_root / "phase10_candidate"
    facts_path = phase10 / "candidate_successor_facts.jsonl"
    manifest_path = phase10 / "candidate_successor_input_manifest.json"
    lineage_path = phase10 / "candidate_lineage_bundle.jsonl"
    receipt_path = phase10 / "phase10_candidate_receipt.json"
    diff_path = phase10 / "candidate_diff_report.json"
    validation_path = phase10 / "candidate_validation_report.json"
    determinism_path = phase10 / "candidate_determinism_report.json"

    receipt = load_json(receipt_path)
    manifest = load_json(manifest_path)
    diff = load_json(diff_path)
    validation = load_json(validation_path)
    determinism = load_json(determinism_path)
    rows = load_jsonl(facts_path)
    lineage = load_jsonl(lineage_path)
    item_ids = [row.get("item_id") for row in rows]
    assertion_count = sum(
        len(row.get("food_semantic_assertions", [])) for row in rows
    )
    target_count = sum(
        row.get("food_semantic_authority_state") == "approved_candidate"
        for row in rows
    )
    schema_sha = contracts["identities"]["schema"]["sha256"]
    license_sha = contracts["identities"]["proposition_license"]["sha256"]
    manifest_authority = manifest.get("food_semantic_authority", {})
    reviewed_candidate = output_review.get("candidate_reconciliation", {})
    if (
        receipt.get("status") != "PASS"
        or receipt.get("candidate_successor_facts_sha256")
        != sha256_file(facts_path)
        or receipt.get("candidate_successor_input_manifest_sha256")
        != sha256_file(manifest_path)
        or receipt.get("approved_food_semantic_schema_sha256") != schema_sha
        or receipt.get("approved_proposition_licensing_contract_sha256")
        != license_sha
        or receipt.get("target_member_count") != 317
        or receipt.get("approved_assertion_count") != 322
        or receipt.get("current_facts_mutation_count") != 0
        or receipt.get("current_manifest_mutation_count") != 0
        or receipt.get("current_adoption") is not False
        or len(rows) != 2105
        or len(set(item_ids)) != 2105
        or target_count != 317
        or assertion_count != 322
        or len(lineage) != 322
        or manifest.get("status") != "approved_non_current_candidate"
        or manifest.get("authority_role")
        != "non_current_food_semantic_authority_candidate"
        or manifest.get("facts", {}).get("sha256") != sha256_file(facts_path)
        or manifest.get("facts", {}).get("row_count") != 2105
        or manifest_authority.get("authority_bearing") is not True
        or manifest_authority.get("approved_assertion_count") != 322
        or manifest_authority.get("approved_item_count") != 317
        or manifest_authority.get("schema_sha256") != schema_sha
        or manifest_authority.get("proposition_license_sha256") != license_sha
        or manifest_authority.get("current_adoption_allowed") is not False
        or diff.get("changed_target_count") != 317
        or diff.get("non_target_count") != 1788
        or diff.get("non_target_row_byte_mismatch_count") != 0
        or diff.get("out_of_scope_field_write_count") != 0
        or validation.get("status") != "PASS"
        or validation.get("candidate_lineage_coverage") != 1.0
        or validation.get("writer_current_sink_count") != 0
        or validation.get("writer_unapproved_fact_count") != 0
        or determinism.get("status") != "PASS"
        or determinism.get("candidate_same_input_same_output") is not True
        or reviewed_candidate.get("candidate_row_count") != 2105
        or reviewed_candidate.get("changed_target_count") != 317
        or reviewed_candidate.get("non_target_raw_byte_mismatch_count") != 0
        or reviewed_candidate.get("candidate_assertion_count") != 322
    ):
        raise FoodSemanticError("reviewed Phase 10 candidate closure mismatch")
    return {
        "facts_path": facts_path,
        "facts_bytes": facts_path.read_bytes(),
        "manifest_path": manifest_path,
        "manifest": manifest,
        "lineage_path": lineage_path,
        "receipt_path": receipt_path,
        "receipt": receipt,
    }


def _validate_current_and_protected(
    root: Path,
    attempt_root: Path,
    output_review: dict[str, Any],
) -> list[dict[str, Any]]:
    reviewed = output_review.get("current_and_protected_identity", {})
    current_pairs = [
        (root / CURRENT_FACTS, reviewed.get("current_facts", {})),
        (root / CURRENT_MANIFEST, reviewed.get("current_manifest", {})),
    ]
    for path, row in current_pairs:
        if (
            not path.is_file()
            or sha256_file(path) != row.get("sha256")
            or path.stat().st_size != row.get("byte_count")
            or row.get("git_and_worktree_identity_match") is not True
        ):
            raise FoodSemanticError(
                f"current authority identity changed: {path}"
            )
    protected_path = (
        attempt_root / "phase1_census/protected_surface_hashes_before.json"
    )
    _bundle_artifact(root, attempt_root, protected_path)
    protected = load_json(protected_path)
    after_rows: list[dict[str, Any]] = []
    for row in protected.get("artifacts", []):
        path = root / row["path"]
        observed = sha256_file(path) if path.is_file() else None
        if observed != row.get("sha256"):
            raise FoodSemanticError(
                f"protected surface identity changed: {row['path']}"
            )
        after_rows.append(
            {
                "path": row["path"],
                "before_sha256": row["sha256"],
                "after_sha256": observed,
                "changed": False,
            }
        )
    if len(after_rows) != len(protected.get("artifacts", [])):
        raise FoodSemanticError("protected surface inventory mismatch")
    return after_rows


def _require_phase11_output_sink(
    attempt_root: Path,
    authority_root: Path,
    output_root: Path,
) -> None:
    try:
        output_root.resolve().relative_to(authority_root.resolve())
    except ValueError as exc:
        raise FoodSemanticError(
            "Phase 11 output root must remain authority-execution-local"
        ) from exc
    if output_root.resolve() == authority_root.resolve():
        raise FoodSemanticError("Phase 11 output root cannot be authority root")
    if not (
        output_root.name.startswith("phase11_successor")
        or output_root.name.startswith("p11-fixture-")
    ):
        raise FoodSemanticError("Phase 11 output root name is not allowed")
    try:
        output_root.resolve().relative_to(attempt_root.resolve())
    except ValueError as exc:
        raise FoodSemanticError("Phase 11 output escapes attempt root") from exc
    normalized = "/" + output_root.resolve().as_posix().lower().strip("/") + "/"
    if any(
        fragment in normalized
        for fragment in ("/data/", "/output/", "/media/lua/", "/package/")
    ):
        raise FoodSemanticError("Phase 11 output intersects protected sink")


def _artifact_row(
    path: Path,
    payload: bytes,
    *,
    root: Path,
    row_count: int | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": relative_posix(path, root=root),
        "sha256": sha256_bytes(payload),
        "byte_count": len(payload),
    }
    if row_count is not None:
        row["row_count"] = row_count
    return row


def _preflight_and_write(payloads: dict[Path, bytes]) -> None:
    for path, payload in payloads.items():
        if path.exists() and path.read_bytes() != payload:
            raise FoodSemanticError(
                f"write-once Phase 11 artifact already differs: {path}"
            )
    for path, payload in sorted(
        payloads.items(), key=lambda pair: pair[0].as_posix()
    ):
        write_once_bytes(path, payload)


def _phase11_payloads(
    root: Path,
    attempt_root: Path,
    authority_root: Path,
    output_root: Path,
) -> tuple[dict[Path, bytes], dict[str, Any]]:
    _require_phase11_output_sink(attempt_root, authority_root, output_root)
    output_review = _validate_phase9_10_output_review(
        root,
        attempt_root,
        authority_root,
    )
    decisions, d9, d12 = _validate_owner_branch_decisions(root)
    contracts = _validate_contract_bindings(root, attempt_root, output_review)
    candidate = _validate_phase10_candidate(
        root,
        authority_root,
        output_review,
        contracts,
    )
    protected_rows = _validate_current_and_protected(
        root,
        attempt_root,
        output_review,
    )

    bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    if sha256_file(bundle_path) != IMPLEMENTATION_BUNDLE_SHA256:
        raise FoodSemanticError("implementation bundle identity changed")
    schema_sha = contracts["identities"]["schema"]["sha256"]
    license_sha = contracts["identities"]["proposition_license"]["sha256"]
    forbidden_sha = contracts["identities"]["forbidden_registry"]["sha256"]
    output_review_path = authority_root / "phase9_10_external_output_review.json"

    successor_facts_path = output_root / "sealed_successor_facts.jsonl"
    successor_manifest_path = (
        output_root / "sealed_successor_input_manifest.json"
    )
    successor_facts_payload = candidate["facts_bytes"]
    successor_facts_sha = sha256_bytes(successor_facts_payload)

    authorization = {
        "schema_version": "food-semantic-phase11-successor-authorization-v1",
        "status": "AUTHORIZED",
        "branch": "B",
        "implementation_complete_bundle_sha256": IMPLEMENTATION_BUNDLE_SHA256,
        "owner_decisions_sha256": OWNER_DECISIONS_SHA256,
        "owner_decision_D9": {
            "selected_option": d9["selected_option"],
            "approval_time": d9["approval_time"],
            "selected_branch": "B",
        },
        "owner_decision_D12": {
            "selected_option": d12["selected_option"],
            "approval_time": d12["approval_time"],
            "correction_owner": "Iris Artifact Registry",
        },
        "semantic_approval": "PASS_COMPLETE_322_ASSERTIONS",
        "phase9_10_external_output_review_sha256": sha256_file(
            output_review_path
        ),
        "phase9_10_external_output_review_verdict": "PASS",
        "candidate_facts_sha256": sha256_file(candidate["facts_path"]),
        "candidate_manifest_sha256": sha256_file(candidate["manifest_path"]),
        "current_mutation_allowed": False,
        "current_adoption_allowed": False,
        "registry_operational_cutover_authorized": False,
    }
    authorization_path = output_root / "successor_authorization.json"
    authorization_payload = canonical_json_bytes(authorization)
    authorization_sha = sha256_bytes(authorization_payload)

    successor_manifest = deepcopy(candidate["manifest"])
    successor_manifest["authority_role"] = (
        "sealed_non_current_food_semantic_successor"
    )
    successor_manifest["status"] = "sealed_non_current_successor"
    successor_manifest["facts"] = {
        **successor_manifest["facts"],
        "path": relative_posix(successor_facts_path, root=root),
        "sha256": successor_facts_sha,
        "role": "sealed_non_current_successor_input",
    }
    successor_manifest["food_semantic_authority"] = {
        **successor_manifest["food_semantic_authority"],
        "phase10_candidate_receipt_sha256": sha256_file(
            candidate["receipt_path"]
        ),
        "phase9_10_external_output_review_sha256": sha256_file(
            output_review_path
        ),
        "successor_authorization_sha256": authorization_sha,
        "selected_branch": "B",
        "sealed_non_current": True,
        "current_adoption_allowed": False,
    }
    successor_manifest_payload = canonical_json_bytes(successor_manifest)
    successor_manifest_sha = sha256_bytes(successor_manifest_payload)

    selected_binding = {
        "schema_version": "food-semantic-selected-successor-input-binding-v1",
        "status": "SEALED",
        "selected_branch": "B",
        "successor_facts_path": relative_posix(
            successor_facts_path,
            root=root,
        ),
        "successor_facts_sha256": successor_facts_sha,
        "successor_input_manifest_path": relative_posix(
            successor_manifest_path,
            root=root,
        ),
        "successor_input_manifest_sha256": successor_manifest_sha,
        "approved_food_semantic_schema_path": SCHEMA.as_posix(),
        "approved_food_semantic_schema_sha256": schema_sha,
        "approved_proposition_licensing_contract_path": (
            PROPOSITION_LICENSE.as_posix()
        ),
        "approved_proposition_licensing_contract_sha256": license_sha,
        "current": False,
        "current_adoption_allowed": False,
        "only_authorized_phase12_input": True,
    }
    selected_binding_path = (
        output_root / "selected_successor_input_binding.json"
    )
    selected_binding_payload = canonical_json_bytes(selected_binding)
    selected_binding_sha = sha256_bytes(selected_binding_payload)

    candidate_manifest_allowed_changes = [
        "authority_role",
        "status",
        "facts.path",
        "facts.role",
        (
            "food_semantic_authority."
            "phase10_candidate_receipt_sha256"
        ),
        (
            "food_semantic_authority."
            "phase9_10_external_output_review_sha256"
        ),
        "food_semantic_authority.successor_authorization_sha256",
        "food_semantic_authority.selected_branch",
        "food_semantic_authority.sealed_non_current",
    ]
    candidate_to_successor = {
        "schema_version": "food-semantic-candidate-to-successor-identity-v1",
        "status": "PASS",
        "candidate_facts": asdict(identity(candidate["facts_path"], root=root)),
        "successor_facts": _artifact_row(
            successor_facts_path,
            successor_facts_payload,
            root=root,
            row_count=2105,
        ),
        "candidate_successor_facts_byte_identical": True,
        "candidate_manifest": asdict(
            identity(candidate["manifest_path"], root=root)
        ),
        "successor_manifest": _artifact_row(
            successor_manifest_path,
            successor_manifest_payload,
            root=root,
        ),
        "manifest_derivation_allowed_changed_fields": (
            candidate_manifest_allowed_changes
        ),
        "manifest_derivation_out_of_scope_change_count": 0,
        "approved_assertion_count": 322,
        "target_member_count": 317,
        "non_target_row_byte_mismatch_count": 0,
    }

    current_facts_review = output_review["current_and_protected_identity"][
        "current_facts"
    ]
    current_manifest_review = output_review[
        "current_and_protected_identity"
    ]["current_manifest"]
    registry_diff = {
        "schema_version": "food-semantic-registry-candidate-diff-v1",
        "status": "PROPOSAL_ONLY",
        "current_facts": {
            "path": current_facts_review["path"],
            "sha256": current_facts_review["sha256"],
            "row_count": 2105,
        },
        "current_manifest": {
            "path": current_manifest_review["path"],
            "sha256": current_manifest_review["sha256"],
        },
        "successor_facts": {
            "path": relative_posix(successor_facts_path, root=root),
            "sha256": successor_facts_sha,
            "row_count": 2105,
        },
        "successor_manifest": {
            "path": relative_posix(successor_manifest_path, root=root),
            "sha256": successor_manifest_sha,
        },
        "affected_row_count": 317,
        "unchanged_row_count": 1788,
        "approved_assertion_count": 322,
        "non_target_row_byte_mismatch_count": 0,
        "current_mutation_count": 0,
        "registry_adoption_receipt_emitted_count": 0,
    }
    registry_diff_path = (
        output_root / "registry_candidate_diff_manifest.json"
    )
    registry_diff_payload = canonical_json_bytes(registry_diff)
    registry_diff_sha = sha256_bytes(registry_diff_payload)

    registry_request = {
        "schema_version": "food-semantic-registry-cutover-request-v1",
        "status": "PENDING_SEPARATE_REGISTRY_REVIEW",
        "request_owner": "Iris Artifact Registry",
        "requested_action": (
            "review sealed successor for a future atomic operational cutover"
        ),
        "selected_successor_input_binding_sha256": selected_binding_sha,
        "registry_candidate_diff_manifest_sha256": registry_diff_sha,
        "successor_authorization_sha256": authorization_sha,
        "owner_decision_D9": d9["selected_option"],
        "owner_decision_D12": d12["selected_option"],
        "correction_contract": {
            **d12["selection_parameters"],
            "correction_successor_must_be_additive": True,
        },
        "atomic_allowed_states": [
            "predecessor_current_intact",
            "successor_current_fully_adopted",
        ],
        "partial_or_dual_current_allowed": False,
        "predecessor_fallback_allowed": False,
        "separate_reviewed_operational_cutover_plan_required": True,
        "current_mutation_requested_by_this_execution": False,
        "current_mutation_authorized_by_this_execution": False,
        "registry_adoption_receipt_emitted_count": 0,
        "required_validation_freshness_reseal_after_future_cutover": True,
        "official_naturalization_retry_requires_fresh_attempt_after_cutover": True,
    }

    pre_review = {
        "schema_version": "food-semantic-phase11-pre-successor-review-v1",
        "status": "PASS",
        "candidate_semantic_review": "PASS",
        "phase9_10_external_output_review_path": relative_posix(
            output_review_path,
            root=root,
        ),
        "phase9_10_external_output_review_sha256": sha256_file(
            output_review_path
        ),
        "reviewer_identity": "Codex Reviewer",
        "finding_counts": {"critical": 0, "important": 0, "minor": 0},
        "phase11_execution_allowed": True,
        "current_mutation_authorized": False,
        "terminal_independent_gate_credit": 0,
    }
    facts_identity_report = {
        "schema_version": "food-semantic-successor-facts-identity-v1",
        "status": "PASS",
        "candidate_facts_sha256": sha256_file(candidate["facts_path"]),
        "successor_facts_sha256": successor_facts_sha,
        "candidate_successor_byte_identity": True,
        "row_count": 2105,
        "target_member_count": 317,
        "approved_assertion_count": 322,
        "successor_identity_sealed": True,
        "non_current": True,
        "current_adoption": False,
    }
    manifest_identity_report = {
        "schema_version": "food-semantic-successor-manifest-identity-v1",
        "status": "PASS",
        "candidate_manifest_sha256": sha256_file(candidate["manifest_path"]),
        "successor_manifest_sha256": successor_manifest_sha,
        "derivation_allowed_changed_fields": candidate_manifest_allowed_changes,
        "derivation_out_of_scope_change_count": 0,
        "successor_facts_sha256_bound": True,
        "schema_sha256_bound": True,
        "proposition_license_sha256_bound": True,
        "successor_identity_sealed": True,
        "non_current": True,
        "current_adoption": False,
    }
    predecessor_disposition = {
        "schema_version": "food-semantic-predecessor-disposition-v1",
        "status": "PASS",
        "predecessor_current_facts_sha256": current_facts_review["sha256"],
        "predecessor_current_manifest_sha256": current_manifest_review["sha256"],
        "predecessor_current_remains_intact": True,
        "predecessor_current_reentry_allowed": False,
        "predecessor_fallback_after_future_promotion_allowed": False,
        "dual_current": 0,
        "current_identity_ambiguity": 0,
    }
    protected_after = {
        "schema_version": "food-semantic-protected-surface-after-v1",
        "status": "PASS",
        "artifacts": protected_rows,
        "changed_count": 0,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "rendered_lua_runtime_package_change": 0,
    }
    divergence = {
        "schema_version": "food-semantic-declared-divergence-v1",
        "status": "PASS",
        "selected_branch": "B",
        "successor_is_non_current": True,
        "successor_facts_sha256": successor_facts_sha,
        "successor_manifest_sha256": successor_manifest_sha,
        "current_facts_sha256": current_facts_review["sha256"],
        "current_manifest_sha256": current_manifest_review["sha256"],
        "unchanged_rendered_runtime_payload_references_predecessor": True,
        "affected_row_count": 317,
        "allowed_divergence_scope": (
            "sealed non-current source successor versus intact predecessor current"
        ),
        "resolution_owner": "Iris Artifact Registry",
        "resolution_scope": (
            "separate reviewed Registry operational cutover plan"
        ),
        "live_current_source_runtime_divergence_created": False,
        "undeclared_divergence_count": 0,
    }
    freshness = {
        "schema_version": "food-semantic-freshness-impact-v1",
        "status": "DECLARED_NOT_RESEALED",
        "current_freshness_changed": False,
        "successor_is_non_current": True,
        "future_registry_cutover_would_stale_required_validation": True,
        "future_registry_cutover_requires_freshness_reseal": True,
        "official_naturalization_retry_allowed": False,
        "official_naturalization_retry_deferred_until_registry_adoption": True,
        "fresh_naturalization_attempt_required_after_future_adoption": True,
        "downstream_closure_restored_by_this_declaration": False,
    }
    defect_schema = {
        "schema_version": "food-semantic-current-authority-defect-v1",
        "required": [
            "defect_identity",
            "affected_rows_and_propositions",
            "defect_discovery_evidence",
            "correction_successor_unavailable_reason",
            "current_source_rendered_divergence_update",
            "required_gate_status",
            "owner_scoped_correction_round_route",
        ],
        "correction_owner": "Iris Artifact Registry",
        "predecessor_current_reentry": 0,
        "predecessor_fallback": 0,
        "partial_or_dual_current": 0,
        "success_terminal_state": False,
        "proposal_only_not_issued": True,
    }

    payloads: dict[Path, bytes] = {
        successor_facts_path: successor_facts_payload,
        successor_manifest_path: successor_manifest_payload,
        authorization_path: authorization_payload,
        selected_binding_path: selected_binding_payload,
        output_root / "pre_successor_review.json": canonical_json_bytes(
            pre_review
        ),
        output_root
        / "candidate_to_successor_identity_manifest.json": canonical_json_bytes(
            candidate_to_successor
        ),
        output_root / "successor_facts_identity_report.json": canonical_json_bytes(
            facts_identity_report
        ),
        output_root
        / "successor_manifest_identity_report.json": canonical_json_bytes(
            manifest_identity_report
        ),
        output_root / "predecessor_disposition_report.json": canonical_json_bytes(
            predecessor_disposition
        ),
        output_root / "protected_surface_hashes_after.json": canonical_json_bytes(
            protected_after
        ),
        output_root / "declared_divergence_report.json": canonical_json_bytes(
            divergence
        ),
        output_root / "freshness_impact_report.json": canonical_json_bytes(
            freshness
        ),
        output_root / "registry_candidate_diff_manifest.json": (
            registry_diff_payload
        ),
        output_root / "registry_cutover_request.json": canonical_json_bytes(
            registry_request
        ),
        output_root / "current_authority_defect_declared.schema.json": (
            canonical_json_bytes(defect_schema)
        ),
    }

    receipt_artifacts = [
        _artifact_row(
            path,
            payload,
            root=root,
            row_count=2105 if path == successor_facts_path else None,
        )
        for path, payload in sorted(
            payloads.items(), key=lambda pair: pair[0].as_posix()
        )
    ]
    sealed_receipt = {
        "schema_version": "food-semantic-sealed-successor-receipt-v1",
        "status": "SEALED_NON_CURRENT_SUCCESSOR",
        "branch": "B",
        "successor_facts_sha256": successor_facts_sha,
        "successor_manifest_sha256": successor_manifest_sha,
        "schema_sha256": schema_sha,
        "proposition_license_sha256": license_sha,
        "forbidden_inference_registry_sha256": forbidden_sha,
        "authorization_sha256": authorization_sha,
        "selected_successor_input_binding_sha256": selected_binding_sha,
        "phase9_10_external_output_review_sha256": sha256_file(
            output_review_path
        ),
        "owner_decisions_sha256": OWNER_DECISIONS_SHA256,
        "non_current": True,
        "current_mutation_authorized": False,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "rendered_lua_runtime_package_change": 0,
        "registry_adoption_receipt_emitted_count": 0,
        "target_member_count": 317,
        "approved_assertion_count": 322,
        "artifacts": receipt_artifacts,
    }
    sealed_receipt_path = output_root / "sealed_successor_receipt.json"
    sealed_receipt_payload = canonical_json_bytes(sealed_receipt)
    payloads[sealed_receipt_path] = sealed_receipt_payload

    execution_receipt = {
        "schema_version": "food-semantic-phase11-execution-receipt-v1",
        "status": "PASS",
        "phase11_root": relative_posix(output_root, root=root),
        "sealed_successor_receipt_sha256": sha256_bytes(
            sealed_receipt_payload
        ),
        "selected_successor_input_binding_sha256": selected_binding_sha,
        "registry_cutover_request_sha256": sha256_bytes(
            payloads[output_root / "registry_cutover_request.json"]
        ),
        "artifact_count_excluding_self": len(payloads),
        "artifacts": [
            _artifact_row(
                path,
                payload,
                root=root,
                row_count=2105 if path == successor_facts_path else None,
            )
            for path, payload in sorted(
                payloads.items(), key=lambda pair: pair[0].as_posix()
            )
        ],
        "selected_branch": "B",
        "sealed_successor_handoff_complete": True,
        "current_authority_reconstruction_complete": False,
        "canonical_complete": False,
        "current_mutation_authorized": False,
        "registry_operational_cutover_executed": False,
        "terminal_independent_gate_credit": 0,
    }
    execution_receipt_path = output_root / "phase11_execution_receipt.json"
    execution_receipt_payload = canonical_json_bytes(execution_receipt)
    payloads[execution_receipt_path] = execution_receipt_payload

    result = {
        "schema_version": "food-semantic-authority-phase11-execution-v1",
        "status": "PASS",
        "selected_branch": "B",
        "successor_facts_sha256": successor_facts_sha,
        "successor_input_manifest_sha256": successor_manifest_sha,
        "selected_successor_input_binding_sha256": selected_binding_sha,
        "sealed_successor_receipt_sha256": sha256_bytes(
            sealed_receipt_payload
        ),
        "phase11_execution_receipt_sha256": sha256_bytes(
            execution_receipt_payload
        ),
        "target_member_count": 317,
        "approved_assertion_count": 322,
        "non_current": True,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "registry_operational_cutover_executed": False,
    }
    return payloads, result


def _validate_phase11_external_implementation_review(
    root: Path,
    authority_root: Path,
) -> dict[str, Any]:
    review_path = (
        authority_root / "phase11_external_implementation_review.json"
    )
    if not review_path.is_file():
        raise FoodSemanticError(
            "Phase 11 external implementation review is missing"
        )
    review = load_json(review_path)
    required_code_paths = {
        (
            "Iris/build/description/v2/tools/build/"
            "dvf_3_3_food_semantic/authority_phase11.py"
        ),
        (
            "Iris/build/description/v2/tools/build/"
            "run_dvf_3_3_food_semantic_authority_phase11.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_dvf_3_3_food_semantic_authority_phase11.py"
        ),
    }
    reviewed = review.get("reviewed_code_artifacts")
    if not isinstance(reviewed, list):
        raise FoodSemanticError(
            "Phase 11 reviewed code artifact manifest is missing"
        )
    reviewed_by_path = {row.get("path"): row for row in reviewed}
    if set(reviewed_by_path) != required_code_paths:
        raise FoodSemanticError("Phase 11 reviewed code artifact set mismatch")
    for relative, row in reviewed_by_path.items():
        path = root / relative
        if (
            not path.is_file()
            or sha256_file(path) != row.get("sha256")
            or path.stat().st_size != row.get("byte_count")
        ):
            raise FoodSemanticError(
                f"Phase 11 reviewed code identity mismatch: {relative}"
            )
    counts = review.get("finding_counts", {})
    if (
        review.get("verdict") != "PASS"
        or review.get("review_verdict") != "PASS"
        or review.get("phase11_scope_verdict") != "PASS"
        or review.get("reviewer_identity") != "Codex Reviewer"
        or review.get("reviewer_is_implementation_author") is not False
        or counts.get("critical") != 0
        or counts.get("important") != 0
        or counts.get("minor") != 0
        or review.get("phase11_execution_allowed") is not True
        or review.get("current_mutation_authorized") is not False
        or review.get("current_adoption_allowed") is not False
        or review.get("terminal_independent_gate_credit") != 0
        or review.get("reviewed_phase9_10_output_review_sha256")
        != PHASE9_10_OUTPUT_REVIEW_SHA256
        or review.get("reviewed_owner_decisions_sha256")
        != OWNER_DECISIONS_SHA256
        or review.get("actual_phase11_execution_performed_by_review")
        is not False
        or review.get("actual_current_adoption_performed_by_review")
        is not False
        or review.get("actual_terminal_review_performed_by_review")
        is not False
    ):
        raise FoodSemanticError(
            "Phase 11 external implementation review is not exact PASS"
        )
    return review


def _materialize_authority_phase11_fixture(
    root: Path,
    attempt_root: Path,
    authority_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    payloads, result = _phase11_payloads(
        root,
        attempt_root,
        authority_root,
        output_root,
    )
    _preflight_and_write(payloads)
    return result


def run_authority_phase11(
    *,
    root: Path | None = None,
    attempt_id: str = "attempt-0007",
    execution_id: str = "authority-execution-0002",
) -> dict[str, Any]:
    resolved_root = (root or repo_root()).resolve()
    attempt_root = (
        resolved_root
        / "Iris/build/description/v2/staging/"
        "dvf_3_3_food_semantic_facts_authority/attempts"
        / attempt_id
    )
    authority_root = (
        attempt_root / "post_implementation_authority" / execution_id
    )
    output_root = authority_root / "phase11_successor"
    _validate_phase11_external_implementation_review(
        resolved_root,
        authority_root,
    )
    return _materialize_authority_phase11_fixture(
        resolved_root,
        attempt_root,
        authority_root,
        output_root,
    )
