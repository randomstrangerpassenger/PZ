from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from iris_tooling.build.naturalization_compiler_identity import (
    build_compiler_identity_from_git,
    compiler_identity_matches_claim,
)

from .acceptance_context import (
    ATTEMPT_ID_PATTERN, default_attempts_root, DEFAULT_FOUNDATION_ROOT,
    FIXTURE_MANIFEST, FOUNDATION_CONTRACT_NAME, FOUNDATION_DOCS,
    FOUNDATION_IMPLEMENTATION_FILES, GIT_COMMIT_PATTERN,
    NATURALIZATION_COMPILER_IMPLEMENTATION_FILES, NATURALIZATION_PLAN_DOC,
    PHASE_ARTIFACTS, PLAN_DOC, RAW_DETECTOR_IDS, READINESS_REPORT_NAME,
    REPO_ROOT, REQUIRED_HANDOFF_CONSTITUENT_IDS,
    SATISFIED_REQUIRED_STRUCTURAL_STATUSES, SYNC_CONTRACT_ID,
    TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID, TEXT_HANDOFF_CONSTITUENT_IDS,
)
from .acceptance_emission import (
    canonical_jsonl_bytes, load_jsonl_strict, write_once_bytes,
    write_once_or_same,
)
from .acceptance_foundation_application import validate_foundation
from .acceptance_infrastructure import (
    FoundationContractError, build_protected_snapshot_present_row_from_bytes,
    canonical_hash, canonical_json_bytes, has_unstaged_delta,
    head_text_constituent_record, is_ignored, is_tracked, load_json_strict,
    repo_relative, require_exact_keys, run_git, sha256_bytes, sha256_file,
)
from .acceptance_reporting import source_hash_inventory
from .acceptance_rules import without_volatile_fields

def official_attempt_root(
    attempt_id: str, attempt_root: Path | None = None
) -> Path:
    if not ATTEMPT_ID_PATTERN.fullmatch(attempt_id):
        raise FoundationContractError(
            "official attempt ID must match attempt-<digits>-<lowercase-label>"
        )
    expected = (default_attempts_root() / attempt_id).resolve()
    if attempt_root is None:
        return expected
    resolved = attempt_root.resolve()
    if resolved.is_relative_to(REPO_ROOT.resolve()) and resolved != expected:
        raise FoundationContractError(
            "repository-local attempt root must match the exact attempt namespace"
        )
    return resolved


def phase_root(root: Path, phase: int) -> Path:
    return root / f"phase{phase}"


def require_artifacts(root: Path, phase: int, names: Iterable[str] | None = None) -> None:
    expected = names if names is not None else PHASE_ARTIFACTS[phase]
    missing = [
        repo_relative(phase_root(root, phase) / name)
        for name in expected
        if not (phase_root(root, phase) / name).is_file()
    ]
    if missing:
        raise FoundationContractError(
            f"required Phase {phase} artifacts missing: {missing}"
        )


def _constituent_map(handoff: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = handoff.get("constituents")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise FoundationContractError("handoff constituents must be an object array")
    identifiers = [row.get("id") for row in rows]
    if identifiers != list(REQUIRED_HANDOFF_CONSTITUENT_IDS):
        raise FoundationContractError("handoff constituent order/schema mismatch")
    if handoff.get("constituent_id_order") != list(REQUIRED_HANDOFF_CONSTITUENT_IDS):
        raise FoundationContractError("handoff declared constituent order mismatch")
    return {str(row["id"]): row for row in rows}


def validate_candidate_handoff(
    handoff_path: Path,
    *,
    expected_subject_kind: str = "dvf_3_3_korean_naturalization_candidate",
) -> dict[str, Any]:
    handoff = load_json_strict(handoff_path)
    require_exact_keys(
        handoff,
        required=(
            "schema_version",
            "synchronization_contract_id",
            "naturalization_attempt_id",
            "requested_evaluation_subject_kind",
            "candidate_runtime_parity_applicability",
            "candidate_runtime_parity_reason",
            "constituents",
            "constituent_id_order",
            "post_handoff_mutation_effect",
            "registry_runtime_pass_claim_allowed",
            "write_once",
        ),
        label="naturalization publish handoff",
    )
    if handoff["schema_version"] != "naturalization_publish_handoff_required_schema_v1":
        raise FoundationContractError("handoff schema version mismatch")
    if handoff["synchronization_contract_id"] != SYNC_CONTRACT_ID:
        raise FoundationContractError("handoff synchronization contract mismatch")
    if handoff["requested_evaluation_subject_kind"] != expected_subject_kind:
        raise FoundationContractError("handoff evaluation subject kind mismatch")
    if (
        handoff["candidate_runtime_parity_applicability"] != "not_applicable"
        or handoff["candidate_runtime_parity_reason"]
        != "candidate_not_registry_adopted"
        or handoff["registry_runtime_pass_claim_allowed"] is not False
    ):
        raise FoundationContractError("candidate runtime parity claim boundary mismatch")
    if (
        handoff["post_handoff_mutation_effect"] != "stale"
        or handoff["write_once"] is not True
    ):
        raise FoundationContractError("handoff immutability contract mismatch")
    constituents = _constituent_map(handoff)
    mismatches: list[str] = []
    path_rows: list[dict[str, Any]] = []
    for identifier in REQUIRED_HANDOFF_CONSTITUENT_IDS:
        row = constituents[identifier]
        if row.get("present") is not True:
            mismatches.append(f"{identifier}:not_present")
            continue
        if "path" in row:
            path = REPO_ROOT / str(row["path"])
            if identifier not in TEXT_HANDOFF_CONSTITUENT_IDS:
                mismatches.append(f"{identifier}:non_text_path_constituent")
                continue
            try:
                identity = head_text_constituent_record(
                    path,
                    row.get("sha256"),
                )
            except FoundationContractError as exc:
                identity = {
                    "algorithm_id": TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID,
                    "path": repo_relative(path),
                    "declared_sha256": row.get("sha256"),
                    "match": False,
                    "identity_error": str(exc),
                }
            path_rows.append({"id": identifier, **identity})
        elif "value" in row:
            actual = sha256_bytes(canonical_json_bytes(row["value"]) + b"\n")
            if actual != row.get("sha256"):
                mismatches.append(f"{identifier}:value_hash_mismatch")
        else:
            mismatches.append(f"{identifier}:missing_path_or_value")
    mismatches.extend(
        f"{row['id']}:path_hash_mismatch" for row in path_rows if not row["match"]
    )
    if mismatches:
        raise FoundationContractError(f"stale handoff constituents: {mismatches}")
    foundation_path_row = next(
        row for row in path_rows if row["id"] == "foundation_contract_hash"
    )
    if foundation_path_row["path"] != repo_relative(
        DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
    ):
        raise FoundationContractError("handoff foundation contract is stale")
    candidate_manifest_path = (
        REPO_ROOT / str(constituents["candidate_manifest_hash"]["path"])
    )
    candidate_manifest_relative = repo_relative(candidate_manifest_path)
    compiler_readpoint = run_git(
        "log",
        "-1",
        "--format=%H",
        "--",
        candidate_manifest_relative,
    ).stdout.strip()
    if not GIT_COMMIT_PATTERN.fullmatch(compiler_readpoint):
        raise FoundationContractError(
            "handoff candidate compiler readpoint is unavailable"
        )
    compiler_identity = build_compiler_identity_from_git(
        REPO_ROOT,
        compiler_readpoint,
    )
    compiler_aggregate_hash = str(compiler_identity["aggregate_sha256"])
    compiler_claim = constituents["compiler_implementation_hash"].get("value")
    if not compiler_identity_matches_claim(compiler_claim, compiler_identity):
        raise FoundationContractError(
            "handoff naturalization compiler implementation is stale"
        )
    candidate_manifest = load_json_strict(candidate_manifest_path)
    if (
        candidate_manifest.get("schema_version")
        != "dvf-3-3-korean-prose-candidate-manifest-v2"
        or candidate_manifest.get("compiler_identity") != compiler_identity
        or candidate_manifest.get("compiler_implementation_hash")
        != compiler_aggregate_hash
    ):
        raise FoundationContractError(
            "handoff candidate compiler identity evidence is stale"
        )
    return {
        "handoff": handoff,
        "constituents": constituents,
        "path_rows": path_rows,
        "handoff_raw_sha256": sha256_file(handoff_path),
        "compiler_identity": compiler_identity,
        "compiler_inventory": compiler_identity["ordered_files"],
        "compiler_aggregate_hash": compiler_aggregate_hash,
        "compiler_readpoint_commit": compiler_readpoint,
        "compiler_readpoint_tree": run_git(
            "rev-parse", f"{compiler_readpoint}^{{tree}}"
        ).stdout.strip(),
    }


def handoff_artifact_path(
    validation: dict[str, Any], identifier: str
) -> Path:
    row = validation["constituents"][identifier]
    if "path" not in row:
        raise FoundationContractError(f"handoff constituent has no path: {identifier}")
    return REPO_ROOT / str(row["path"])


def _semantic_failure_count(report: dict[str, Any]) -> int:
    fields = (
        "missing_proposition_resolution_count",
        "qualifier_modality_limitation_preservation_failure_count",
        "unresolved_proposition_reference_count",
        "forbidden_transformation_count",
        "unknown_transformation_count",
        "invalid_structural_status_count",
        "not_applicable_without_reason_count",
    )
    return sum(int(report.get(field, 0)) for field in fields)


HUMAN_REVIEW_RUBRIC_IDS = (
    "readability",
    "naturalness",
    "semantic_fidelity",
    "public_suitability",
)


def _human_review_technical_blocker(reasons: list[str]) -> None:
    raise FoundationContractError(
        "human review schema technical blocker: "
        + ",".join(sorted(set(reasons)))
    )


def human_review_blocker_count(
    *,
    review_sample: dict[str, Any],
    review_decision: dict[str, Any],
    required_denominator: int,
) -> int:
    mode = review_decision.get("decision_mode")
    expected_digest = review_sample.get("selected_ordered_digest")
    if mode == "exact_full_candidate_external_review":
        errors: list[str] = []
        if review_decision.get("status") != "PASS":
            errors.append("exact_full_status_not_pass")
        if review_decision.get("reviewed_denominator") != required_denominator:
            errors.append("exact_full_denominator_mismatch")
        if review_decision.get("selected_ordered_digest") != expected_digest:
            errors.append("exact_full_digest_mismatch")
        aggregate = review_decision.get("rubric_aggregate")
        if (
            not isinstance(aggregate, dict)
            or set(aggregate) != set(HUMAN_REVIEW_RUBRIC_IDS)
        ):
            errors.append("exact_full_rubric_aggregate_incomplete")
            aggregate = {}
        for rubric_id in HUMAN_REVIEW_RUBRIC_IDS:
            counts = aggregate.get(rubric_id)
            if (
                not isinstance(counts, dict)
                or set(counts) != {"pass", "fail"}
                or type(counts.get("pass")) is not int
                or type(counts.get("fail")) is not int
                or counts.get("pass") != required_denominator
                or counts.get("fail") != 0
            ):
                errors.append(
                    f"exact_full_rubric_aggregate_mismatch:{rubric_id}"
                )
        blocker_count = review_decision.get("blocker_count")
        blocker_item_ids = review_decision.get("blocker_item_ids")
        blockers = review_decision.get("blockers")
        if (
            type(blocker_count) is not int
            or blocker_count != 0
            or blocker_item_ids != []
            or blockers != []
        ):
            errors.append("exact_full_blocker_list_mismatch")
        if errors:
            _human_review_technical_blocker(errors)
        return int(blocker_count)

    if mode == "exact_sample_uniform_owner_approval":
        if review_decision.get("selected_ordered_digest") != expected_digest:
            _human_review_technical_blocker(
                ["sampled_uniform_digest_mismatch"]
            )
        uniform_review = review_decision.get("uniform_review")
        if not isinstance(uniform_review, dict) or not uniform_review:
            _human_review_technical_blocker(
                ["sampled_uniform_review_incomplete"]
            )
        return (
            0
            if review_decision.get("status") == "approved"
            and all(value == "pass" for value in uniform_review.values())
            else required_denominator
        )

    _human_review_technical_blocker(
        [f"unknown_decision_mode:{mode!r}"]
    )
    raise AssertionError("unreachable")


def compute_candidate_metric_snapshot(
    validation: dict[str, Any],
) -> dict[str, Any]:
    candidate_path = handoff_artifact_path(validation, "candidate_rendered_hash")
    candidate_manifest_path = handoff_artifact_path(validation, "candidate_manifest_hash")
    source_manifest_path = handoff_artifact_path(
        validation, "source_proposition_manifest_hash"
    )
    structural_path = handoff_artifact_path(
        validation, "structural_satisfaction_ledger_hash"
    )
    semantic_path = handoff_artifact_path(validation, "semantic_preservation_report_hash")
    raw_path = handoff_artifact_path(validation, "raw_detector_report_hash")
    review_sample_path = handoff_artifact_path(
        validation, "human_review_sample_manifest_hash"
    )
    review_decision_path = handoff_artifact_path(
        validation, "human_review_decision_hash"
    )

    candidate = load_json_strict(candidate_path)
    candidate_manifest = load_json_strict(candidate_manifest_path)
    source_manifest = load_json_strict(source_manifest_path)
    structural_rows = load_jsonl_strict(structural_path)
    semantic = load_json_strict(semantic_path)
    raw = load_json_strict(raw_path)
    review_sample = load_json_strict(review_sample_path)
    review_decision = load_json_strict(review_decision_path)
    candidate_declared_hash = validation["constituents"][
        "candidate_rendered_hash"
    ]["sha256"]

    entries = candidate.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise FoundationContractError("candidate rendered entries must be nonempty object")
    item_ids = sorted(entries)
    if len(item_ids) != len(set(item_ids)):
        raise FoundationContractError("duplicate exact candidate item identity")
    candidate_denominator = raw.get("candidate_denominator")
    if not isinstance(candidate_denominator, int) or candidate_denominator <= 0:
        raise FoundationContractError("candidate denominator must be positive integer")
    if candidate_manifest.get("candidate_emission_count") != candidate_denominator:
        raise FoundationContractError("candidate emission/denominator mismatch")
    if candidate_manifest.get("source_universe_count") != len(item_ids):
        raise FoundationContractError("candidate source universe/key count mismatch")
    if candidate_manifest.get("unadopted_count") != len(item_ids) - candidate_denominator:
        raise FoundationContractError("candidate explicit unadopted count mismatch")

    source_count = source_manifest.get("proposition_count")
    if not isinstance(source_count, int) or source_count <= 0:
        raise FoundationContractError("source proposition denominator invalid")
    required_rows = [
        row
        for row in structural_rows
        if row.get("required") is True
        and row.get("emission_eligible") is True
    ]
    illegal_required_not_required = sum(
        row.get("status") == "not_required" for row in required_rows
    )
    unsatisfied = sum(
        row.get("status") not in SATISFIED_REQUIRED_STRUCTURAL_STATUSES
        for row in required_rows
    )
    transformation_rows = [
        row
        for row in structural_rows
        if row.get("emission_eligible") is True
        and row.get("status")
        in ("satisfied_by_verified_fusion", "satisfied_by_verified_suppression")
    ]
    equivalence_failures = int(
        semantic.get("equivalence_proof_missing_or_mismatch_count", 0)
    )
    if illegal_required_not_required:
        equivalence_failures += illegal_required_not_required

    detector_ids = raw.get("configured_detector_ids")
    if detector_ids != list(RAW_DETECTOR_IDS):
        raise FoundationContractError("raw detector configured ID/order mismatch")
    hit_counts = raw.get("detector_hit_counts")
    if not isinstance(hit_counts, dict):
        raise FoundationContractError("raw detector hit counts missing")
    if (
        raw.get("raw_detector_full_candidate_completeness_pass") is not True
        or raw.get("detector_opportunity_count")
        != candidate_denominator * len(RAW_DETECTOR_IDS)
        or raw.get("expected_detector_opportunity_count")
        != candidate_denominator * len(RAW_DETECTOR_IDS)
    ):
        raise FoundationContractError("raw detector completeness mismatch")

    selected = review_sample.get("selected_item_ids")
    selected_denominator = review_sample.get("selected_required_denominator")
    if (
        not isinstance(selected, list)
        or len(selected) != selected_denominator
        or len(selected) != len(set(selected))
        or review_sample.get("candidate_rendered_hash") != candidate_declared_hash
        or review_decision.get("candidate_rendered_hash") != candidate_declared_hash
    ):
        _human_review_technical_blocker(
            ["human_review_denominator_or_candidate_binding_mismatch"]
        )
    human_review_failures = human_review_blocker_count(
        review_sample=review_sample,
        review_decision=review_decision,
        required_denominator=selected_denominator,
    )

    denominators: dict[str, int] = {
        "naturalization_candidate_item_v1": candidate_denominator,
        "naturalization_source_proposition_v1": source_count,
        "naturalization_required_body_plan_role_v1": len(required_rows),
        "naturalization_fusion_suppression_transformation_v1": max(
            0, len(transformation_rows)
        ),
        "naturalization_human_review_required_v1": selected_denominator,
    }
    for detector_id in RAW_DETECTOR_IDS:
        denominators[
            f"naturalization_raw_detector_opportunity_v1:{detector_id}"
        ] = candidate_denominator

    numerators = {
        "semantic_preservation_failure": _semantic_failure_count(semantic),
        "unsatisfied_required_body_plan_role": unsatisfied,
        "equivalence_proof_failure": equivalence_failures,
        "compiler_invalid_pattern": (
            0
            if candidate_manifest.get("candidate_content_hash_count") == 1
            and candidate_manifest.get("candidate_volatile_metadata_field_count") == 0
            else 1
        ),
        **{
            detector_id: int(hit_counts.get(detector_id, 0))
            for detector_id in RAW_DETECTOR_IDS
        },
        "human_review_blocker_required_denominator": int(human_review_failures),
    }
    contract = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    registrations = [
        row
        for row in contract["metric_registry_candidate"]["registrations"]
        if "dvf_3_3_korean_naturalization_candidate"
        in row["applicable_subject_kinds"]
    ]
    rows: list[dict[str, Any]] = []
    for registration in registrations:
        metric_id = registration["metric_id"]
        denominator_id = registration["denominator_id"]
        denominator = denominators.get(denominator_id)
        if denominator is None or denominator <= 0:
            raise FoundationContractError(
                f"candidate denominator missing or zero: {denominator_id}"
            )
        rows.append(
            {
                "metric_id": metric_id,
                "denominator_id": denominator_id,
                "disposition_class": registration["disposition_class"],
                "numerator": numerators[metric_id],
                "denominator": denominator,
                "exact_ratio": {
                    "numerator": numerators[metric_id],
                    "denominator": denominator,
                },
            }
        )
    return {
        "schema_version": "public_text_quality_candidate_metric_snapshot_v1",
        "evaluation_subject_kind": "dvf_3_3_korean_naturalization_candidate",
        "evaluation_subject_hash": candidate_declared_hash,
        "candidate_key_count": len(item_ids),
        "quality_evaluable_candidate_count": candidate_denominator,
        "explicit_unadopted_count": len(item_ids) - candidate_denominator,
        "source_proposition_count": source_count,
        "required_body_plan_role_count": len(required_rows),
        "fusion_suppression_transformation_count": len(transformation_rows),
        "human_review_required_denominator": selected_denominator,
        "metric_rows": rows,
        "metric_projection_hash": canonical_hash(rows),
        "technical_blocker_count": 0,
    }


def _candidate_entries_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = load_json_strict(handoff_artifact_path(validation, "candidate_rendered_hash"))
    entries = candidate.get("entries")
    if not isinstance(entries, dict):
        raise FoundationContractError("candidate entries must be an object")
    rows = []
    for item_id in sorted(entries):
        payload = entries[item_id]
        if not isinstance(payload, dict):
            raise FoundationContractError(f"candidate payload is not object: {item_id}")
        rows.append({"item_id": item_id, "payload": without_volatile_fields(payload)})
    return rows


def candidate_protected_snapshot(validation: dict[str, Any]) -> list[dict[str, Any]]:
    report = load_json_strict(
        handoff_artifact_path(validation, "protected_surface_no_mutation_report_hash")
    )
    if (
        report.get("protected_surface_no_mutation_pass") is not True
        or report.get("protected_surface_mutation_count") != 0
    ):
        raise FoundationContractError("naturalization protected surface report is not PASS")
    after_snapshot = report.get("after_snapshot")
    rows = (
        after_snapshot.get("files")
        if isinstance(after_snapshot, dict)
        else after_snapshot
    )
    if not isinstance(rows, list):
        raise FoundationContractError("protected after snapshot missing")
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or "path" not in row
            or not isinstance(row.get("exists"), bool)
        ):
            raise FoundationContractError("protected snapshot row invalid")
        relative = str(row["path"])
        pure_path = PurePosixPath(relative)
        if (
            not relative
            or pure_path.is_absolute()
            or ".." in pure_path.parts
            or "\\" in relative
        ):
            raise FoundationContractError(
                "protected snapshot path must be repo-relative POSIX"
            )
        path = REPO_ROOT / relative
        if not path.resolve().is_relative_to(REPO_ROOT.resolve()):
            raise FoundationContractError(
                f"protected snapshot path escaped repository: {relative}"
            )
        declared_exists = row["exists"]
        if not declared_exists:
            if path.exists() or row.get("sha256") is not None:
                raise FoundationContractError(
                    f"protected surface stale before Publish attempt: {relative}"
                )
            normalized.append(
                {
                    "path": relative,
                    "present": False,
                    "sha256": None,
                }
            )
            continue
        if not path.is_file():
            raise FoundationContractError(
                f"protected surface stale before Publish attempt: {relative}"
            )
        if not is_tracked(path):
            raise FoundationContractError(
                f"protected surface is untracked: {relative}"
            )
        if is_ignored(path):
            raise FoundationContractError(
                f"protected surface is ignored: {relative}"
            )
        head_blob_id = run_git("rev-parse", f"HEAD:{relative}").stdout.strip()
        head_blob = subprocess.run(
            ["git", "cat-file", "blob", head_blob_id],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        if head_blob.returncode != 0:
            raise FoundationContractError(
                f"cannot read protected surface HEAD blob: {relative}"
            )
        filtered_working_blob_id = run_git(
            "hash-object", "--", relative
        ).stdout.strip()
        text_attribute_output = run_git(
            "check-attr", "text", "--", relative
        ).stdout.strip()
        text_attribute = text_attribute_output.rsplit(": ", 1)[-1]
        normalized.append(build_protected_snapshot_present_row_from_bytes(
            repo_relative_posix_path=relative,
            declared_sha256=row.get("sha256"),
            head_blob_id=head_blob_id,
            head_blob_raw=head_blob.stdout,
            working_raw=path.read_bytes(),
            filtered_working_blob_id=filtered_working_blob_id,
            text_attribute=text_attribute,
        ))
    return normalized


def vcs_preflight(paths: Iterable[Path]) -> dict[str, Any]:
    unique = sorted({path.resolve() for path in paths}, key=lambda path: repo_relative(path))
    rows = []
    for path in unique:
        relative = repo_relative(path)
        present = path.is_file()
        tracked = is_tracked(path)
        head_blob_id = None
        filtered_working_blob_id = None
        head_working_identity = False
        if present and tracked:
            head_result = run_git(
                "rev-parse",
                f"HEAD:{relative}",
                check=False,
            )
            working_result = run_git(
                "hash-object",
                "--",
                relative,
                check=False,
            )
            if head_result.returncode == 0 and working_result.returncode == 0:
                head_blob_id = head_result.stdout.strip()
                filtered_working_blob_id = working_result.stdout.strip()
                head_working_identity = (
                    bool(head_blob_id)
                    and head_blob_id == filtered_working_blob_id
                )
        rows.append(
            {
                "path": relative,
                "present": present,
                "tracked": tracked,
                "ignored": is_ignored(path),
                "unstaged_delta": has_unstaged_delta(path),
                "head_git_blob_id": head_blob_id,
                "filtered_working_blob_id": filtered_working_blob_id,
                "head_working_identity": head_working_identity,
            }
        )
    blockers = [
        row["path"]
        for row in rows
        if not row["present"]
        or not row["tracked"]
        or row["ignored"]
        or row["unstaged_delta"]
        or not row["head_working_identity"]
    ]
    return {
        "schema_version": "public_text_quality_vcs_required_surface_preflight_v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_path_count": len(rows),
        "present_count": sum(row["present"] for row in rows),
        "tracked_count": sum(row["tracked"] for row in rows),
        "ignored_count": sum(row["ignored"] for row in rows),
        "unstaged_delta_count": sum(row["unstaged_delta"] for row in rows),
        "head_working_identity_count": sum(
            row["head_working_identity"] for row in rows
        ),
        "blocker_paths": blockers,
        "rows": rows,
    }


PHASE0_REQUIRED_VCS_CONSUMERS = frozenset(
    {"phase0-no-write-preflight", "phase0-binding"}
)


def phase0_required_vcs_paths(
    *,
    subject_handoff: Path,
    handoff_validation: dict[str, Any],
) -> tuple[Path, ...]:
    handoff_path = subject_handoff.resolve()
    foundation_contract_path = DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
    readiness_path = DEFAULT_FOUNDATION_ROOT / READINESS_REPORT_NAME
    required = {
        path.resolve()
        for path in (
            PLAN_DOC,
            NATURALIZATION_PLAN_DOC,
            foundation_contract_path,
            readiness_path,
            handoff_path,
            FIXTURE_MANIFEST,
            *FOUNDATION_DOCS,
            *FOUNDATION_IMPLEMENTATION_FILES,
            *NATURALIZATION_COMPILER_IMPLEMENTATION_FILES,
            *(
                REPO_ROOT / str(row["path"])
                for row in handoff_validation["constituents"].values()
                if "path" in row
            ),
        )
    }
    return tuple(sorted(required, key=repo_relative))


def phase0_required_vcs_preflight(
    *,
    subject_handoff: Path,
    consumer: str,
    handoff_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if consumer not in PHASE0_REQUIRED_VCS_CONSUMERS:
        raise FoundationContractError(
            f"unsupported Phase 0 VCS-preflight consumer: {consumer}"
        )
    validation = (
        validate_candidate_handoff(subject_handoff.resolve())
        if handoff_validation is None
        else handoff_validation
    )
    paths = phase0_required_vcs_paths(
        subject_handoff=subject_handoff,
        handoff_validation=validation,
    )
    preflight = vcs_preflight(paths)
    required_path_set = [repo_relative(path) for path in paths]
    return {
        "consumer": consumer,
        "handoff_validation": validation,
        "required_path_set": required_path_set,
        "required_path_set_sha256": canonical_hash(required_path_set),
        "vcs_preflight": preflight,
    }


def require_phase0_required_vcs_preflight(
    *,
    subject_handoff: Path,
    consumer: str,
    handoff_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = phase0_required_vcs_preflight(
        subject_handoff=subject_handoff,
        consumer=consumer,
        handoff_validation=handoff_validation,
    )
    preflight = result["vcs_preflight"]
    if preflight["status"] != "PASS":
        raise FoundationContractError(
            f"required input VCS preflight failed: {preflight['blocker_paths']}"
        )
    return result


def build_phase0_binding(
    *,
    attempt_id: str,
    evaluation_subject_kind: str,
    subject_handoff: Path,
    attempt_root: Path | None = None,
) -> dict[str, Any]:
    if evaluation_subject_kind != "dvf_3_3_korean_naturalization_candidate":
        raise FoundationContractError(
            "S3 synchronized official attempt requires the naturalization candidate subject"
        )
    root = official_attempt_root(attempt_id, attempt_root)
    if root.exists():
        raise FoundationContractError(
            f"official attempt ID/root already exists: {repo_relative(root)}"
        )
    foundation_validation = validate_foundation(
        foundation_id="ptqa-foundation-v1"
    )
    handoff_path = subject_handoff.resolve()
    phase0_vcs = require_phase0_required_vcs_preflight(
        subject_handoff=handoff_path,
        consumer="phase0-binding",
    )
    validation = phase0_vcs["handoff_validation"]
    preflight = phase0_vcs["vcs_preflight"]
    candidate_path = handoff_artifact_path(validation, "candidate_rendered_hash")
    entries_rows = _candidate_entries_rows(validation)
    metric_snapshot = compute_candidate_metric_snapshot(validation)
    protected_before = candidate_protected_snapshot(validation)
    foundation_contract_path = DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
    readiness_path = DEFAULT_FOUNDATION_ROOT / READINESS_REPORT_NAME

    p0 = phase_root(root, 0)
    entries_bytes = canonical_jsonl_bytes(entries_rows)
    metric_rows = metric_snapshot["metric_rows"]
    metric_bytes = canonical_jsonl_bytes(metric_rows)
    evaluation_subject = {
        "schema_version": "public_text_quality_evaluation_subject_manifest_v1",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": evaluation_subject_kind,
        "evaluation_subject_path": repo_relative(candidate_path),
        "evaluation_subject_hash": sha256_file(candidate_path),
        "naturalization_attempt_id": validation["handoff"][
            "naturalization_attempt_id"
        ],
        "naturalization_handoff_path": repo_relative(handoff_path),
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_allowed": False,
        "authority_effect": "official_evaluation_input_binding_only",
    }
    handoff_binding = {
        "schema_version": "public_text_quality_cross_plan_handoff_binding_v1",
        "status": "PASS",
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "naturalization_attempt_id": validation["handoff"][
            "naturalization_attempt_id"
        ],
        "handoff_path": repo_relative(handoff_path),
        "handoff_raw_sha256": validation["handoff_raw_sha256"],
        "required_constituent_count": len(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "present_constituent_count": len(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "constituent_hash_mismatch_count": 0,
        "foundation_contract_hash": validation["constituents"][
            "foundation_contract_hash"
        ]["sha256"],
        "current_foundation_contract_hash": sha256_file(
            foundation_contract_path
        ),
        "runtime_parity_applicability": "not_applicable",
        "runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_count": 0,
        "post_handoff_mutation_count": 0,
    }
    constituent_manifest = {
        "schema_version": "public_text_quality_current_input_constituent_manifest_v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": evaluation_subject_kind,
        "foundation_contract": {
            "path": repo_relative(foundation_contract_path),
            "raw_sha256": sha256_file(foundation_contract_path),
        },
        "foundation_readiness": {
            "path": repo_relative(readiness_path),
            "raw_sha256": sha256_file(readiness_path),
            "status": foundation_validation["status"],
        },
        "handoff": {
            "path": repo_relative(handoff_path),
            "raw_sha256": validation["handoff_raw_sha256"],
        },
        "constituents": validation["path_rows"],
        "ignored_rendered_direct_authority_read_count": 0,
    }
    entries_digest = {
        "schema_version": "public_text_quality_canonical_entries_digest_v1",
        "row_count": len(entries_rows),
        "sha256": sha256_bytes(entries_bytes),
        "ordering": "item_id_ascending_exact_case",
        "encoding": "utf-8",
        "line_ending": "lf",
        "volatile_metadata_excluded": True,
    }
    metric_digest = {
        "schema_version": "public_text_quality_canonical_metric_projection_digest_v1",
        "metric_count": len(metric_rows),
        "sha256": sha256_bytes(metric_bytes),
        "normalized_projection_hash": metric_snapshot["metric_projection_hash"],
        "candidate_metric_recomputed_independently": True,
    }
    binding_core = {
        "attempt_id": attempt_id,
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "foundation_contract_hash": sha256_file(foundation_contract_path),
        "evaluation_subject_kind": evaluation_subject_kind,
        "evaluation_subject_hash": sha256_file(candidate_path),
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
        "constituent_hashes": [
            {"id": row["id"], "sha256": row["sha256"]}
            for row in validation["handoff"]["constituents"]
        ],
        "canonical_entries_sha256": entries_digest["sha256"],
        "canonical_metric_projection_sha256": metric_digest["sha256"],
        "metric_registry_candidate_hash": load_json_strict(
            foundation_contract_path
        )["metric_registry_candidate_hash"],
        "denominator_registry_candidate_hash": load_json_strict(
            foundation_contract_path
        )["denominator_registry_candidate_hash"],
        "policy_candidate_hash": load_json_strict(foundation_contract_path)[
            "policy_candidate_hash"
        ],
        "tool_hashes": source_hash_inventory(FOUNDATION_IMPLEMENTATION_FILES),
    }
    binding = {
        "schema_version": "public_text_quality_acceptance_input_binding_v1",
        **binding_core,
        "binding_hash": canonical_hash(binding_core),
        "binding_fresh": True,
        "authority_effect": "official_evaluation_input_binding_only",
        "official_disposition": "not_issued",
    }

    write_once_or_same(p0 / "evaluation_subject_manifest.json", evaluation_subject)
    write_once_or_same(
        p0 / "cross_plan_handoff_binding_report.json", handoff_binding
    )
    write_once_or_same(
        p0 / "current_input_constituent_manifest.json", constituent_manifest
    )
    write_once_bytes(p0 / "canonical_entries_projection.jsonl", entries_bytes)
    write_once_or_same(p0 / "canonical_entries_digest.json", entries_digest)
    write_once_bytes(p0 / "canonical_metric_projection.jsonl", metric_bytes)
    write_once_or_same(
        p0 / "canonical_metric_projection_digest.json", metric_digest
    )
    write_once_or_same(p0 / "acceptance_input_binding_manifest.json", binding)
    protected_after = candidate_protected_snapshot(validation)
    protected_report = {
        "schema_version": "public_text_quality_protected_surface_no_mutation_v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "before_snapshot": protected_before,
        "after_snapshot": protected_after,
        "changed_count": sum(
            left != right for left, right in zip(protected_before, protected_after)
        ),
        "source_rendered_lua_runtime_package_mutation_count": 0,
    }
    if protected_report["status"] != "PASS":
        raise FoundationContractError("protected surface changed during Phase 0")
    write_once_or_same(
        p0 / "protected_surface_no_mutation_report.json", protected_report
    )
    write_once_or_same(p0 / "vcs_required_surface_preflight.json", preflight)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase0-binding",
        "attempt_root": repo_relative(root),
        "evaluation_subject_kind": evaluation_subject_kind,
        "evaluation_subject_hash": evaluation_subject["evaluation_subject_hash"],
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
        "binding_hash": binding["binding_hash"],
        "canonical_entry_count": len(entries_rows),
        "canonical_metric_count": len(metric_rows),
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "incomplete",
    }

__all__ = (
    "build_phase0_binding", "candidate_protected_snapshot",
    "compute_candidate_metric_snapshot", "handoff_artifact_path",
    "human_review_blocker_count", "official_attempt_root",
    "PHASE0_REQUIRED_VCS_CONSUMERS", "phase0_required_vcs_paths",
    "phase0_required_vcs_preflight",
    "phase_root", "require_artifacts",
    "require_phase0_required_vcs_preflight", "validate_candidate_handoff",
    "vcs_preflight",
)
