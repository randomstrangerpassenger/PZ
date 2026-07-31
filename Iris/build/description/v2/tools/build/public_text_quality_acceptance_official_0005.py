from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable, Iterator

import public_text_quality_acceptance as base


ATTEMPT_ID = "attempt-0005-official"
START_COMMIT = "9f32b94188be2575af2ec1a884cdeb3096fbcdca"
START_TREE = "7d901ae90b0eece63d9295b112044233425eead4"
EVALUATION_SUBJECT_KIND = "dvf_3_3_korean_naturalization_candidate"
NATURALIZATION_ATTEMPT_ID = "attempt-0024-publish-remediation-a"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
G4_READINESS_SHA256 = (
    "0a8d5c4433d9610dd503ea3add792bd3c3ece0ded5fffdfeab8d7b600fb88a67"
)
G4_PREDECESSOR_READINESS_SHA256 = (
    "01b80e5e70e0e49d0eb956074cc6a0c6f2d15c9c147b5b25cefc12aa1a455421"
)
CURRENT_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
CURRENT_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
PHASE8_HANDOFF_SHA256 = (
    "7fdbb224b3af4231a8bf3f2d37e448a8cdbfb4ed4d9871a83927b22cfdde25ec"
)
PHASE8_CLOSEOUT_SHA256 = (
    "e1dfa84d2e5f1ab1fe959bec228668ca0c5a266c9b377e60baee865f3ca1fa84"
)
TERMINAL_CLOSEOUT_SHA256 = (
    "6a9fd3eb65236aade1ff504423fb6850da95d2b5a9e3882f070b7f043f97049c"
)
CANDIDATE_SHA256 = (
    "ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437"
)
TRACE_SHA256 = (
    "f047c4e53fbe32d430192a2cedbc1db4e4685926643017a608bb7e89c911af06"
)
COMPILER_IDENTITY_ALGORITHM_ID = (
    "naturalization_compiler_identity_sha256_lf_normalized_ordered_paths_v2"
)
COMPILER_AGGREGATE_SHA256 = (
    "2dcff095b1cc34c8fb6d3ad735ac8f9d0ca2affe259f6bb97870b19e7235cc7f"
)

REPO_ROOT = base.REPO_ROOT
V2_ROOT = base.V2_ROOT
ATTEMPT_ROOT = base.DEFAULT_ATTEMPTS_ROOT / ATTEMPT_ID
FOUNDATION_CONTRACT = (
    base.DEFAULT_FOUNDATION_ROOT / base.FOUNDATION_CONTRACT_NAME
)
G4_READINESS = (
    base.DEFAULT_FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0006"
    / "public_text_quality_g5_review_schema_readiness.json"
)
G4_PREDECESSOR_READINESS = (
    base.DEFAULT_FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0005"
    / "public_text_quality_phase0_vcs_parity_readiness.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
NATURALIZATION_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / NATURALIZATION_ATTEMPT_ID
)
PHASE8_HANDOFF = (
    NATURALIZATION_ROOT
    / "phase8"
    / "publish_acceptance_handoff_manifest.json"
)
PHASE8_CLOSEOUT = NATURALIZATION_ROOT / "phase8" / "phase8_closeout.json"
CANDIDATE = NATURALIZATION_ROOT / "phase4" / "candidate_rendered.json"
TRACE = NATURALIZATION_ROOT / "phase4" / "candidate_proposition_trace.jsonl"
TERMINAL_CLOSEOUT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt_0024_terminal_closeout.json"
)
OWNER_INPUT_ROOT = (
    V2_ROOT
    / "owner_inputs"
    / base.ROUND_ID
    / ATTEMPT_ID
)
POLICY_OWNER_INPUT = OWNER_INPUT_ROOT / "policy_ratification_decision.json"
WAIVER_OWNER_INPUT = OWNER_INPUT_ROOT / "applicable_waiver_set.json"

THIS_MODULE = Path(__file__).resolve()
RUNNER_MODULE = THIS_MODULE.with_name(
    "run_public_text_quality_acceptance_official_0005.py"
)
VALIDATOR_MODULE = THIS_MODULE.with_name(
    "validate_public_text_quality_acceptance_official_0005.py"
)
CURRENT_ROUTE_TEST = (
    V2_ROOT / "tests" / "test_public_text_quality_acceptance_current_route.py"
)
PHASE0_SUCCESSOR_BINDING = "official_current_input_binding_report.json"


def _extend_phase_artifacts(phase: int, names: Iterable[str]) -> None:
    current = tuple(base.PHASE_ARTIFACTS[phase])
    base.PHASE_ARTIFACTS[phase] = current + tuple(
        name for name in names if name not in current
    )


_extend_phase_artifacts(0, (PHASE0_SUCCESSOR_BINDING,))


def _git(
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise base.FoundationContractError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result


def _require_attempt_id(attempt_id: str) -> None:
    if attempt_id != ATTEMPT_ID:
        raise base.FoundationContractError(
            f"official wrapper requires attempt ID {ATTEMPT_ID}"
        )


def _readpoint() -> dict[str, Any]:
    tree = _git("show", "-s", "--format=%T", START_COMMIT).stdout.strip()
    if tree != START_TREE:
        raise base.FoundationContractError(
            "official attempt start commit/tree mismatch"
        )
    if _git(
        "merge-base",
        "--is-ancestor",
        START_COMMIT,
        "HEAD",
        check=False,
    ).returncode:
        raise base.FoundationContractError(
            "official attempt start commit is not an ancestor of HEAD"
        )
    return {
        "start_commit": START_COMMIT,
        "start_tree": START_TREE,
        "execution_commit": base.git_head(),
        "execution_tree": _git(
            "show",
            "-s",
            "--format=%T",
            "HEAD",
        ).stdout.strip(),
        "start_commit_is_ancestor": True,
    }


def _sealed_text_record(
    path: Path,
    expected_sha256: str,
) -> dict[str, Any]:
    if base._is_ignored(path):
        raise base.FoundationContractError(
            f"required input is ignored: {base.repo_relative(path)}"
        )
    if base._has_unstaged_delta(path):
        raise base.FoundationContractError(
            f"required input has unstaged delta: {base.repo_relative(path)}"
        )
    record = base._head_text_constituent_record(path, expected_sha256)
    if record.get("match") is not True:
        raise base.FoundationContractError(
            f"required text input identity mismatch: {base.repo_relative(path)}"
        )
    return record


def _validate_g4_readiness() -> dict[str, Any]:
    record = _sealed_text_record(G4_READINESS, G4_READINESS_SHA256)
    value = base.load_json_strict(G4_READINESS)
    g1 = value.get("g1_clean_checkout", {})
    g5 = value.get("g5_naturalization", {})
    semantics = value.get("foundation_semantics", {})
    predecessor = value.get("predecessor_readiness", {})
    if (
        value.get("schema_version")
        != (
            "public_text_quality_foundation_g5_review_schema_correction_"
            "readiness_v1"
        )
        or value.get("correction_id") != "implementation-correction-0006"
        or value.get("status") != "PASS"
        or value.get("authority_effect") != "none"
        or value.get("protected_surface_mutation_count") != 0
        or value.get("foundation_contract_semantics_changed") is not False
        or value.get(
            "policy_threshold_denominator_detector_semantics_changed"
        )
        is not False
        or predecessor.get("sha256") != G4_PREDECESSOR_READINESS_SHA256
        or predecessor.get("predecessor_mutated") is not False
        or g1.get("status") != "PASS"
        or g1.get("run_a_result") != "199/199 PASS"
        or g1.get("run_b_result") != "199/199 PASS"
        or g1.get("canonical_result_sha256")
        != "528979411eeb8eb95df97c0d15f05cbd9a05bd41e6bb4d1fff344b4b2c39d21f"
        or g1.get("census", {}).get("unresolved_dependency") != 0
        or g5.get("status") != "PASS"
        or g5.get("primary_attempt_id") != NATURALIZATION_ATTEMPT_ID
        or g5.get("compiler_identity", {}).get("aggregate_sha256")
        != COMPILER_AGGREGATE_SHA256
        or g5.get("human_review_numerator") != 0
        or g5.get("raw_detector_hit_count") != 0
        or g5.get("blocking_condition_count") != 0
        or semantics.get(
            "exact_full_metric_numerator_source"
        )
        != "validated_blocker_count"
        or semantics.get(
            "unknown_or_incomplete_review_schema_effect"
        )
        != "technical_blocker_fail_closed"
        or semantics.get("foundation_contract", {}).get("sha256")
        != FOUNDATION_CONTRACT_SHA256
    ):
        raise base.FoundationContractError("G4 readiness successor is stale")
    return {
        **record,
        "status": "PASS",
        "correction_id": value["correction_id"],
        "authority_effect": value["authority_effect"],
        "protected_surface_mutation_count": 0,
    }


def _metric_projection(
    handoff_validation: dict[str, Any],
) -> dict[str, Any]:
    snapshot = base.compute_candidate_metric_snapshot(handoff_validation)
    rows = {
        row["metric_id"]: row
        for row in snapshot.get("metric_rows", [])
    }
    human = rows.get("human_review_blocker_required_denominator", {})
    raw_detector_hit_count = sum(
        int(rows.get(metric_id, {}).get("numerator", -1))
        for metric_id in base.RAW_DETECTOR_IDS
    )
    raw_detector_opportunity_count = sum(
        int(rows.get(metric_id, {}).get("denominator", -1))
        for metric_id in base.RAW_DETECTOR_IDS
    )
    if (
        snapshot.get("technical_blocker_count") != 0
        or human.get("numerator") != 0
        or human.get("denominator") != 2084
        or raw_detector_hit_count != 0
        or raw_detector_opportunity_count != 14588
    ):
        raise base.FoundationContractError(
            "corrected G5 metric projection is not publish-preflight clean"
        )
    return {
        "snapshot": snapshot,
        "human_review_numerator": 0,
        "human_review_denominator": 2084,
        "raw_detector_hit_count": 0,
        "raw_detector_opportunity_count": 14588,
        "technical_blocker_count": 0,
    }


def validate_current_inputs(*, require_clean: bool) -> dict[str, Any]:
    readpoint = _readpoint()
    if require_clean:
        status = _git(
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).stdout
        if status:
            raise base.FoundationContractError(
                "official execution requires a clean checkout"
            )
    records = {
        "foundation_contract": _sealed_text_record(
            FOUNDATION_CONTRACT,
            FOUNDATION_CONTRACT_SHA256,
        ),
        "g4_readiness": _validate_g4_readiness(),
        "current_facts": _sealed_text_record(
            CURRENT_FACTS,
            CURRENT_FACTS_SHA256,
        ),
        "current_manifest": _sealed_text_record(
            CURRENT_MANIFEST,
            CURRENT_MANIFEST_SHA256,
        ),
        "phase8_handoff": _sealed_text_record(
            PHASE8_HANDOFF,
            PHASE8_HANDOFF_SHA256,
        ),
        "phase8_closeout": _sealed_text_record(
            PHASE8_CLOSEOUT,
            PHASE8_CLOSEOUT_SHA256,
        ),
        "terminal_closeout": _sealed_text_record(
            TERMINAL_CLOSEOUT,
            TERMINAL_CLOSEOUT_SHA256,
        ),
        "candidate": _sealed_text_record(
            CANDIDATE,
            CANDIDATE_SHA256,
        ),
        "trace": _sealed_text_record(TRACE, TRACE_SHA256),
    }
    compiler = base.build_compiler_identity(REPO_ROOT)
    if (
        compiler.get("algorithm_id") != COMPILER_IDENTITY_ALGORITHM_ID
        or compiler.get("aggregate_sha256") != COMPILER_AGGREGATE_SHA256
    ):
        raise base.FoundationContractError("compiler identity is stale")
    handoff_validation = base.validate_candidate_handoff(PHASE8_HANDOFF)
    handoff = handoff_validation["handoff"]
    if (
        handoff.get("naturalization_attempt_id")
        != NATURALIZATION_ATTEMPT_ID
        or handoff.get("requested_evaluation_subject_kind")
        != EVALUATION_SUBJECT_KIND
        or handoff_validation.get("handoff_raw_sha256")
        != PHASE8_HANDOFF_SHA256
        or handoff_validation.get("compiler_aggregate_hash")
        != COMPILER_AGGREGATE_SHA256
        or handoff_validation.get("constituents", {}).get(
            "candidate_rendered_hash", {}
        ).get("sha256")
        != CANDIDATE_SHA256
    ):
        raise base.FoundationContractError("G5 handoff is stale")
    closeout = base.load_json_strict(PHASE8_CLOSEOUT)
    terminal = base.load_json_strict(TERMINAL_CLOSEOUT)
    if (
        closeout.get("status") != "HANDOFF_COMPLETE"
        or closeout.get("naturalization_attempt_id")
        != NATURALIZATION_ATTEMPT_ID
        or closeout.get("candidate_rendered_sha256") != CANDIDATE_SHA256
        or closeout.get("publish_acceptance_handoff_manifest_sha256")
        != PHASE8_HANDOFF_SHA256
        or closeout.get("human_review_blocker_count") != 0
        or closeout.get("human_review_denominator") != 2084
        or terminal.get("status") != "HANDOFF_COMPLETE"
        or terminal.get("attempts", {}).get("primary")
        != NATURALIZATION_ATTEMPT_ID
        or terminal.get("phase8_handoff", {}).get("handoff_sha256")
        != PHASE8_HANDOFF_SHA256
        or terminal.get("phase8_handoff", {}).get("phase8_closeout_sha256")
        != PHASE8_CLOSEOUT_SHA256
    ):
        raise base.FoundationContractError("G5 closeout is stale")
    metrics = _metric_projection(handoff_validation)
    return {
        "status": "PASS",
        "readpoint": readpoint,
        "records": records,
        "handoff_validation": handoff_validation,
        "compiler_identity": compiler,
        "metrics": metrics,
        "protected_surface_mutation_count": 0,
        "live_gate_mutation_count": 0,
        "authority_effect": "none",
    }


def _official_required_vcs_preflight(
    *,
    handoff_validation: dict[str, Any],
    consumer: str,
) -> dict[str, Any]:
    base_result = base.phase0_required_vcs_preflight(
        subject_handoff=PHASE8_HANDOFF,
        consumer=consumer,
        handoff_validation=handoff_validation,
    )
    paths = set(
        base.phase0_required_vcs_paths(
            subject_handoff=PHASE8_HANDOFF,
            handoff_validation=handoff_validation,
        )
    )
    paths.update(
        {
            G4_READINESS,
            CURRENT_FACTS,
            CURRENT_MANIFEST,
            PHASE8_CLOSEOUT,
            TERMINAL_CLOSEOUT,
            CANDIDATE,
            TRACE,
            THIS_MODULE,
            RUNNER_MODULE,
            VALIDATOR_MODULE,
        }
    )
    ordered_paths = tuple(sorted(paths, key=base.repo_relative))
    vcs = base._vcs_preflight(ordered_paths)
    path_set = [base.repo_relative(path) for path in ordered_paths]
    if vcs.get("status") != "PASS":
        raise base.FoundationContractError(
            f"official required input VCS preflight failed: "
            f"{vcs.get('blocker_paths')}"
        )
    return {
        "status": "PASS",
        "consumer": consumer,
        "base_required_path_count": base_result[
            "vcs_preflight"
        ]["required_path_count"],
        "required_path_count": len(path_set),
        "required_path_set": path_set,
        "required_path_set_sha256": base.canonical_hash(path_set),
        "vcs_preflight": vcs,
    }


def _current_foundation_validation_shim(
    *,
    foundation_id: str,
    foundation_root: Path = base.DEFAULT_FOUNDATION_ROOT,
) -> dict[str, Any]:
    if foundation_id != "ptqa-foundation-v1":
        raise base.FoundationContractError(
            "official Foundation selector changed"
        )
    if foundation_root.resolve() != base.DEFAULT_FOUNDATION_ROOT.resolve():
        raise base.FoundationContractError(
            "official Foundation root changed"
        )
    current = validate_current_inputs(require_clean=False)
    return {
        "status": "PASS",
        "foundation_id": "ptqa-foundation-v1",
        "foundation_contract_raw_sha256": FOUNDATION_CONTRACT_SHA256,
        "readiness_successor_raw_sha256": G4_READINESS_SHA256,
        "protected_surface_mutation_count": current[
            "protected_surface_mutation_count"
        ],
        "authority_effect": "none",
    }


@contextmanager
def _owner_input_namespace() -> Iterator[None]:
    original = base.OWNER_INPUT_ROOT
    base.OWNER_INPUT_ROOT = OWNER_INPUT_ROOT
    try:
        yield
    finally:
        base.OWNER_INPUT_ROOT = original


def _phase0_successor_report(
    *,
    current: dict[str, Any],
    vcs: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": (
            "public_text_quality_official_current_input_binding_v2"
        ),
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "start_commit": START_COMMIT,
        "start_tree": START_TREE,
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "g4_readiness_path": base.repo_relative(G4_READINESS),
        "g4_readiness_sha256": G4_READINESS_SHA256,
        "naturalization_attempt_id": NATURALIZATION_ATTEMPT_ID,
        "phase8_handoff_sha256": PHASE8_HANDOFF_SHA256,
        "phase8_closeout_sha256": PHASE8_CLOSEOUT_SHA256,
        "terminal_closeout_sha256": TERMINAL_CLOSEOUT_SHA256,
        "candidate_sha256": CANDIDATE_SHA256,
        "trace_sha256": TRACE_SHA256,
        "compiler_identity_algorithm_id": (
            COMPILER_IDENTITY_ALGORITHM_ID
        ),
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "human_review_numerator": current["metrics"][
            "human_review_numerator"
        ],
        "raw_detector_hit_count": current["metrics"][
            "raw_detector_hit_count"
        ],
        "required_vcs_path_count": vcs["required_path_count"],
        "required_vcs_path_set_sha256": vcs[
            "required_path_set_sha256"
        ],
        "ignored_required_input_count": vcs[
            "vcs_preflight"
        ]["ignored_count"],
        "protected_surface_mutation_count": 0,
        "live_gate_mutation_count": 0,
        "authority_effect": "official_evaluation_input_binding_only",
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def _validate_phase0_successor(root: Path) -> dict[str, Any]:
    path = base.phase_root(root, 0) / PHASE0_SUCCESSOR_BINDING
    value = base.load_json_strict(path)
    current = validate_current_inputs(require_clean=False)
    vcs = _official_required_vcs_preflight(
        handoff_validation=current["handoff_validation"],
        consumer="phase0-binding",
    )
    expected = _phase0_successor_report(current=current, vcs=vcs)
    if value != expected:
        raise base.FoundationContractError(
            "attempt-0005 current-input binding is stale"
        )
    return {
        "status": "PASS",
        "path": base.repo_relative(path),
        "sha256": base.sha256_file(path),
        "required_vcs_path_count": vcs["required_path_count"],
        "required_vcs_path_set_sha256": vcs[
            "required_path_set_sha256"
        ],
    }


def _preserving_pretty_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _tracked_not_ignored(path: Path) -> bool:
    return (
        path.is_file()
        and base._is_tracked(path)
        and not base._is_ignored(path)
        and not base._has_unstaged_delta(path)
    )


def _live_manifest_record() -> dict[str, Any]:
    path = base.LIVE_REQUIRED_VALIDATIONS
    relative = base.repo_relative(path)
    if not _tracked_not_ignored(path):
        raise base.FoundationContractError(
            "live required-validation manifest is not tracked and clean"
        )
    head_blob_id = _git(
        "rev-parse",
        f"HEAD:{relative}",
    ).stdout.strip()
    blob = subprocess.run(
        ["git", "cat-file", "blob", head_blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if blob.returncode != 0:
        raise base.FoundationContractError(
            "cannot read live required-validation HEAD blob"
        )
    filtered_working_blob_id = _git(
        "hash-object",
        "--",
        relative,
    ).stdout.strip()
    if filtered_working_blob_id != head_blob_id:
        raise base.FoundationContractError(
            "live required-validation manifest working identity is stale"
        )
    return {
        "path": relative,
        "sha256": base.sha256_bytes(blob.stdout),
        "head_git_blob_id": head_blob_id,
        "filtered_working_blob_id": filtered_working_blob_id,
        "tracked": True,
        "ignored": False,
        "unstaged_delta": False,
        "head_working_identity": True,
    }


def _candidate_required_entries(
    root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p0 = base.phase_root(root, 0)
    p1 = base.phase_root(root, 1)
    p2 = base.phase_root(root, 2)
    p4 = base.phase_root(root, 4)
    p5 = base.phase_root(root, 5)
    p6 = base.phase_root(root, 6)
    artifacts = [
        {
            "path": base.repo_relative(
                p0 / "acceptance_input_binding_manifest.json"
            ),
            "checks": [{"field": "binding_fresh", "equals": True}],
        },
        {
            "path": base.repo_relative(p0 / PHASE0_SUCCESSOR_BINDING),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(
                p1 / "metric_denominator_contract_validation_report.json"
            ),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(p2 / "policy_hash_seal.json"),
            "checks": [{"field": "policy_ratified", "equals": True}],
        },
        {
            "path": base.repo_relative(
                p4 / "adversarial_fixture_manifest.json"
            ),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(
                p5 / "evaluation_subject_disposition.json"
            ),
            "checks": [
                {
                    "field": "qualified_disposition",
                    "equals": "accepted",
                }
            ],
        },
        {
            "path": base.repo_relative(
                p5 / "evaluation_subject_disposition_hash_manifest.json"
            ),
            "checks": [
                {
                    "field": "schema_version",
                    "equals": (
                        "public_text_quality_disposition_hash_manifest_v1"
                    ),
                }
            ],
        },
        {
            "path": base.repo_relative(
                p6 / "stale_disposition_consumption_guard_report.json"
            ),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(
                p6 / "pre_adoption_protected_surface_report.json"
            ),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(
                p6 / "required_artifact_recensus_report.json"
            ),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
    ]
    required_test = {
        "test_id": (
            "test_public_text_quality_acceptance_current_route."
            "PublicTextQualityAcceptanceCurrentRouteTest."
            "test_required_gate_runs_standalone_subprocess"
        ),
        "reason": (
            "standalone Publish Boundary public-text acceptance "
            "required gate"
        ),
        "role": (
            "publish_boundary_public_text_acceptance_required_validation"
        ),
        "required": True,
    }
    return artifacts, required_test


def build_phase6_gate_candidate(*, attempt_id: str) -> dict[str, Any]:
    _require_attempt_id(attempt_id)
    root = base.official_attempt_root(attempt_id)
    phase5_validation = base.validate_official_attempt(
        attempt_id=attempt_id,
        requirement="phase5",
    )
    disposition_path = (
        base.phase_root(root, 5)
        / "evaluation_subject_disposition.json"
    )
    disposition = base.load_json_strict(disposition_path)
    if (
        phase5_validation.get("qualified_disposition") != "accepted"
        or disposition.get("qualified_disposition") != "accepted"
    ):
        raise base.FoundationContractError(
            "Phase 6 candidate is forbidden for non-accepted subject"
        )
    prerequisite_paths = [
        base.phase_root(root, phase) / name
        for phase in range(0, 6)
        for name in base.PHASE_ARTIFACTS[phase]
    ]
    prerequisite_paths.extend(
        [
            base.phase_root(root, 2)
            / "policy_ratification_record.json",
            base.phase_root(root, 2) / "policy_hash_seal.json",
        ]
    )
    unready = [
        base.repo_relative(path)
        for path in prerequisite_paths
        if not _tracked_not_ignored(path)
    ]
    if unready:
        raise base.FoundationContractError(
            f"Phase 6 prerequisites are not tracked and clean: {unready}"
        )
    if not _tracked_not_ignored(CURRENT_ROUTE_TEST):
        raise base.FoundationContractError(
            "Phase 6 current-route test is not tracked and clean"
        )
    live_before = _live_manifest_record()
    current = validate_current_inputs(require_clean=True)
    p6 = base.phase_root(root, 6)
    stale_guard = {
        "schema_version": (
            "public_text_quality_stale_disposition_consumption_guard_v1"
        ),
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        "evaluation_subject_disposition_sha256": base.sha256_file(
            disposition_path
        ),
        "evaluation_subject_disposition_hash": disposition[
            "disposition_hash"
        ],
        "phase0_current_input_binding_sha256": base.sha256_file(
            base.phase_root(root, 0) / PHASE0_SUCCESSOR_BINDING
        ),
        "g4_readiness_successor_sha256": G4_READINESS_SHA256,
        "current_checkout_input_fresh": current["status"] == "PASS",
        "stale_disposition_consumption_count": 0,
    }
    protected = {
        "schema_version": (
            "public_text_quality_phase6_pre_adoption_protected_surface_v1"
        ),
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "live_required_validation_manifest_before": live_before,
        "live_required_validation_manifest_after": live_before,
        "live_manifest_mutation_count": 0,
        "facts_manifest_foundation_candidate_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "authority_effect": "none",
    }
    artifacts, required_test = _candidate_required_entries(root)
    live_manifest = base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)
    recensus = {
        "schema_version": (
            "public_text_quality_required_artifact_recensus_v1"
        ),
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "base_required_artifact_count": len(
            live_manifest["required_artifacts"]
        ),
        "base_required_test_count": len(
            live_manifest["required_tests"]
        ),
        "publish_required_artifact_addition_count": len(artifacts),
        "publish_required_test_addition_count": 1,
        "prerequisite_tracked_count": len(prerequisite_paths),
        "prerequisite_required_count": len(prerequisite_paths),
        "prerequisite_ignored_count": 0,
        "candidate_route_recensus_authority": (
            "fresh_validator_and_route_execution"
        ),
    }
    gitignore_report = {
        "schema_version": (
            "public_text_quality_gitignore_exact_unignore_patch_v1"
        ),
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "exact_phase6_unignore_materialized": True,
        "broad_unignore_count": 0,
        "live_adoption_gitignore_change_required": False,
        "live_adoption_gitignore_diff": [],
    }
    base.write_once_or_same(
        p6 / "stale_disposition_consumption_guard_report.json",
        stale_guard,
    )
    base.write_once_or_same(
        p6 / "pre_adoption_protected_surface_report.json",
        protected,
    )
    base.write_once_or_same(
        p6 / "required_artifact_recensus_report.json",
        recensus,
    )
    base.write_once_or_same(
        p6 / "gitignore_exact_unignore_patch.json",
        gitignore_report,
    )
    candidate_manifest = deepcopy(live_manifest)
    candidate_manifest["required_artifacts"].extend(artifacts)
    candidate_manifest["required_tests"].append(required_test)
    candidate_path = p6 / "required_gate_candidate.json"
    base.write_once_bytes(
        candidate_path,
        _preserving_pretty_bytes(candidate_manifest),
    )
    candidate_sha = base.sha256_file(candidate_path)
    patch = {
        "schema_version": "public_text_quality_required_gate_patch_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "target_path": base.repo_relative(
            base.LIVE_REQUIRED_VALIDATIONS
        ),
        "base_manifest_sha256": live_before["sha256"],
        "candidate_manifest_path": base.repo_relative(candidate_path),
        "candidate_manifest_sha256": candidate_sha,
        "operation": (
            "append_only_required_artifacts_and_required_tests"
        ),
        "added_required_artifacts": artifacts,
        "added_required_tests": [required_test],
        "removed_required_artifact_count": 0,
        "modified_required_artifact_count": 0,
        "removed_required_test_count": 0,
        "modified_required_test_count": 0,
        "existing_entry_reorder_count": 0,
        "live_manifest_mutated": False,
    }
    patch_path = p6 / "required_gate_patch.json"
    base.write_once_or_same(patch_path, patch)
    patch_sha = base.sha256_file(patch_path)
    contract = {
        "schema_version": (
            "public_text_quality_required_gate_adoption_contract_v1"
        ),
        "status": "AWAITING_EXPLICIT_LIVE_GATE_APPROVAL",
        "attempt_id": ATTEMPT_ID,
        "candidate_manifest_sha256": candidate_sha,
        "candidate_patch_sha256": patch_sha,
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": disposition[
            "disposition_hash"
        ],
        "naturalization_handoff_manifest_hash": PHASE8_HANDOFF_SHA256,
        "expected_post_adoption_official_route_state": "PASS",
        "expected_exit_code": 0,
        "exact_blocker_attribution": "none",
        "adoption_timing": "immediate_after_explicit_owner_approval",
        "owner_acknowledgement": "pending",
        "owner_authorization": False,
        "owner_identity": None,
        "authorized_at": None,
        "owner_binding_proof": None,
        "live_manifest_path": base.repo_relative(
            base.LIVE_REQUIRED_VALIDATIONS
        ),
        "live_manifest_base_sha256": live_before["sha256"],
        "live_manifest_mutated": False,
        "authority_effect": "none",
        "phase7_allowed": False,
        "policy_closure_state": "incomplete",
        "rollback_contract": {
            "precondition": (
                "live manifest must still match base SHA before adoption"
            ),
            "rollback_operation": "restore exact base manifest bytes",
            "rollback_target_path": base.repo_relative(
                base.LIVE_REQUIRED_VALIDATIONS
            ),
            "rollback_base_sha256": live_before["sha256"],
            "post_rollback_validation": (
                "run current route with restored live manifest"
            ),
        },
    }
    contract_path = p6 / "required_gate_adoption_contract.json"
    base.write_once_or_same(contract_path, contract)
    base.write_once_text(
        p6 / "required_gate_adoption_contract.md",
        (
            "# Publish Boundary Phase 6 Gate Candidate\n\n"
            f"- Attempt: `{ATTEMPT_ID}`\n"
            f"- Candidate manifest SHA-256: `{candidate_sha}`\n"
            f"- Candidate patch SHA-256: `{patch_sha}`\n"
            "- Evaluation subject disposition: `accepted`\n"
            "- Authority effect: `none`\n"
            "- Live manifest mutation: `false`\n"
            "- Adoption state: "
            "`AWAITING_EXPLICIT_LIVE_GATE_APPROVAL`\n"
        ),
    )
    return {
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "mode": "phase6-gate-candidate",
        "candidate_manifest_path": base.repo_relative(candidate_path),
        "candidate_manifest_sha256": candidate_sha,
        "candidate_patch_path": base.repo_relative(patch_path),
        "candidate_patch_sha256": patch_sha,
        "base_manifest_sha256": live_before["sha256"],
        "required_artifact_addition_count": len(artifacts),
        "required_test_addition_count": 1,
        "live_manifest_mutated": False,
        "authority_effect": "none",
        "adoption_timing": "immediate_after_explicit_owner_approval",
        "approval_required": True,
        "phase7_allowed": False,
        "policy_closure_state": "incomplete",
    }


def _validate_gate_candidate(root: Path) -> dict[str, Any]:
    phase5 = base.validate_official_attempt(
        attempt_id=ATTEMPT_ID,
        requirement="phase5",
    )
    if phase5.get("qualified_disposition") != "accepted":
        raise base.FoundationContractError(
            "gate candidate requires accepted Phase 5"
        )
    p6 = base.phase_root(root, 6)
    candidate_path = p6 / "required_gate_candidate.json"
    patch_path = p6 / "required_gate_patch.json"
    contract_path = p6 / "required_gate_adoption_contract.json"
    route_path = p6 / "candidate_current_route_result.json"
    required_paths = (
        candidate_path,
        patch_path,
        contract_path,
        p6 / "required_gate_adoption_contract.md",
        p6 / "gitignore_exact_unignore_patch.json",
        p6 / "required_artifact_recensus_report.json",
        p6 / "stale_disposition_consumption_guard_report.json",
        p6 / "pre_adoption_protected_surface_report.json",
        route_path,
    )
    missing = [
        base.repo_relative(path)
        for path in required_paths
        if not path.is_file()
    ]
    if missing:
        raise base.FoundationContractError(
            f"Phase 6 candidate artifact missing: {missing}"
        )
    live = base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)
    candidate = base.load_json_strict(candidate_path)
    patch = base.load_json_strict(patch_path)
    contract = base.load_json_strict(contract_path)
    route = base.load_json_strict(route_path)
    artifacts = patch["added_required_artifacts"]
    tests = patch["added_required_tests"]
    if (
        candidate["required_artifacts"]
        != [*live["required_artifacts"], *artifacts]
        or candidate["required_tests"]
        != [*live["required_tests"], *tests]
    ):
        raise base.FoundationContractError(
            "candidate manifest is not additive-only"
        )
    live_other = {
        key: value
        for key, value in live.items()
        if key not in ("required_artifacts", "required_tests")
    }
    candidate_other = {
        key: value
        for key, value in candidate.items()
        if key not in ("required_artifacts", "required_tests")
    }
    if live_other != candidate_other:
        raise base.FoundationContractError(
            "candidate manifest changes non-additive fields"
        )
    candidate_sha = base.sha256_file(candidate_path)
    patch_sha = base.sha256_file(patch_path)
    if (
        patch.get("candidate_manifest_sha256") != candidate_sha
        or contract.get("candidate_manifest_sha256") != candidate_sha
        or contract.get("candidate_patch_sha256") != patch_sha
        or contract.get("owner_authorization") is not False
        or contract.get("live_manifest_mutated") is not False
        or contract.get("authority_effect") != "none"
        or contract.get("phase7_allowed") is not False
    ):
        raise base.FoundationContractError(
            "Phase 6 approval contract/hash mismatch"
        )
    added_paths = [REPO_ROOT / row["path"] for row in artifacts]
    unready = [
        base.repo_relative(path)
        for path in added_paths
        if not _tracked_not_ignored(path)
    ]
    if unready or not _tracked_not_ignored(CURRENT_ROUTE_TEST):
        raise base.FoundationContractError(
            f"candidate required recensus failed: {unready}"
        )
    required = route.get("required_validations", {})
    if (
        route.get("schema_version") != "round3-contract-test-run-v1"
        or route.get("contract_class") != "current"
        or route.get("closure_enforced") is not True
        or route.get("success") is not True
        or route.get("errors") != []
        or route.get("failures") != []
        or required.get("success") is not True
        or required.get("errors") != []
        or required.get("required_artifact_count")
        != len(candidate["required_artifacts"])
        or required.get("required_test_count")
        != len({row["test_id"] for row in candidate["required_tests"]})
    ):
        raise base.FoundationContractError(
            "candidate current-route result is not PASS"
        )
    live_record = _live_manifest_record()
    if live_record["sha256"] != contract["live_manifest_base_sha256"]:
        raise base.FoundationContractError(
            "live manifest changed before owner approval"
        )
    return {
        "status": "PASS",
        "candidate_manifest_path": base.repo_relative(candidate_path),
        "candidate_manifest_sha256": candidate_sha,
        "candidate_patch_sha256": patch_sha,
        "candidate_current_route_result_sha256": base.sha256_file(
            route_path
        ),
        "candidate_current_route_exit_code": 0,
        "candidate_current_route_test_count": route["test_count"],
        "execution_class": "sandbox_candidate",
        "official_route": False,
        "required_artifact_recensus": {
            "required_count": len(added_paths),
            "tracked_count": len(added_paths),
            "ignored_count": 0,
            "missing_count": 0,
        },
        "required_test_recensus": {
            "required_count": 1,
            "tracked_count": 1,
            "ignored_count": 0,
            "missing_count": 0,
        },
        "live_manifest_base_sha256": live_record["sha256"],
        "live_manifest_mutated": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "adoption_timing": contract["adoption_timing"],
        "approval_required": True,
        "phase7_allowed": False,
        "policy_closure_state": "incomplete",
    }


def run_official_mode(
    *,
    attempt_id: str,
    mode: str,
    evaluation_subject_kind: str | None = None,
    subject_handoff: Path | None = None,
) -> dict[str, Any]:
    _require_attempt_id(attempt_id)
    if mode == "phase0-no-write-preflight":
        if evaluation_subject_kind != EVALUATION_SUBJECT_KIND:
            raise base.FoundationContractError(
                "official evaluation subject kind mismatch"
            )
        if (
            subject_handoff is None
            or subject_handoff.resolve() != PHASE8_HANDOFF.resolve()
        ):
            raise base.FoundationContractError(
                "official handoff path mismatch"
            )
        if ATTEMPT_ROOT.exists():
            raise base.FoundationContractError(
                "attempt-0005 root already exists"
            )
        status_before = _git(
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).stdout
        if status_before:
            raise base.FoundationContractError(
                "no-write preflight requires a clean checkout"
            )
        current = validate_current_inputs(require_clean=True)
        protected_before = base._protected_snapshot(
            current["handoff_validation"]
        )
        vcs = _official_required_vcs_preflight(
            handoff_validation=current["handoff_validation"],
            consumer="phase0-no-write-preflight",
        )
        protected_after = base._protected_snapshot(
            current["handoff_validation"]
        )
        status_after = _git(
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).stdout
        if (
            protected_before != protected_after
            or status_before != status_after
            or ATTEMPT_ROOT.exists()
        ):
            raise base.FoundationContractError(
                "no-write preflight mutated protected or attempt state"
            )
        return {
            "schema_version": (
                "public_text_quality_official_phase0_no_write_preflight_v2"
            ),
            "status": "PASS",
            "attempt_id": ATTEMPT_ID,
            "attempt_root_created": False,
            "official_attempt_consumed": False,
            "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "evaluation_subject_sha256": CANDIDATE_SHA256,
            "g4_readiness_sha256": G4_READINESS_SHA256,
            "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
            "phase8_handoff_sha256": PHASE8_HANDOFF_SHA256,
            "human_review_numerator": 0,
            "raw_detector_hit_count": 0,
            "required_input_vcs_preflight_status": "PASS",
            "required_vcs_path_count": vcs["required_path_count"],
            "required_vcs_path_set_sha256": vcs[
                "required_path_set_sha256"
            ],
            "ignored_required_input_count": vcs[
                "vcs_preflight"
            ]["ignored_count"],
            "source_checkout_clean_before": True,
            "source_checkout_clean_after": True,
            "protected_surface_mutation_count": 0,
            "live_gate_mutation_count": 0,
            "authority_effect": "none",
            "official_disposition": "not_issued",
            "policy_closure_state": "not_started",
            "readpoint": current["readpoint"],
        }
    if mode == "phase0-binding":
        if evaluation_subject_kind != EVALUATION_SUBJECT_KIND:
            raise base.FoundationContractError(
                "official evaluation subject kind mismatch"
            )
        if (
            subject_handoff is None
            or subject_handoff.resolve() != PHASE8_HANDOFF.resolve()
        ):
            raise base.FoundationContractError(
                "official handoff path mismatch"
            )
        if ATTEMPT_ROOT.exists():
            raise base.FoundationContractError(
                "attempt-0005 root already exists"
            )
        current = validate_current_inputs(require_clean=True)
        vcs = _official_required_vcs_preflight(
            handoff_validation=current["handoff_validation"],
            consumer="phase0-binding",
        )
        original = base.validate_foundation
        base.validate_foundation = _current_foundation_validation_shim
        try:
            result = base.run_official_mode(
                attempt_id=attempt_id,
                mode=mode,
                evaluation_subject_kind=evaluation_subject_kind,
                subject_handoff=PHASE8_HANDOFF,
            )
        finally:
            base.validate_foundation = original
        base.write_once_or_same(
            base.phase_root(ATTEMPT_ROOT, 0) / PHASE0_SUCCESSOR_BINDING,
            _phase0_successor_report(current=current, vcs=vcs),
        )
        return {
            **result,
            "start_commit": START_COMMIT,
            "start_tree": START_TREE,
            "g4_readiness_sha256": G4_READINESS_SHA256,
            "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
            "protected_surface_mutation_count": 0,
            "live_gate_mutation_count": 0,
        }
    if evaluation_subject_kind is not None or subject_handoff is not None:
        raise base.FoundationContractError(
            "subject arguments are only allowed for Phase 0"
        )
    _validate_phase0_successor(ATTEMPT_ROOT)
    if mode in (
        "phase6-revalidate",
        "phase6-adopt-gate",
        "phase6-post-adoption-route",
        "phase7-freeze",
        "phase7-finalize",
    ):
        from public_text_quality_acceptance_official_0005_closure import (
            adopt_live_gate,
            build_phase6_revalidation,
            build_phase7_finalize,
            build_phase7_freeze,
            run_bounded_post_adoption_route,
        )

        dispatch = {
            "phase6-revalidate": build_phase6_revalidation,
            "phase6-adopt-gate": adopt_live_gate,
            "phase6-post-adoption-route": run_bounded_post_adoption_route,
            "phase7-freeze": build_phase7_freeze,
            "phase7-finalize": build_phase7_finalize,
        }
        return dispatch[mode]()
    if mode == "phase2-policy":
        with _owner_input_namespace():
            return base.run_official_mode(
                attempt_id=attempt_id,
                mode=mode,
            )
    if mode == "phase6-gate-candidate":
        return build_phase6_gate_candidate(attempt_id=attempt_id)
    return base.run_official_mode(attempt_id=attempt_id, mode=mode)


def validate_official_attempt(
    *,
    attempt_id: str,
    requirement: str,
) -> dict[str, Any]:
    _require_attempt_id(attempt_id)
    if requirement == "gate-candidate":
        from public_text_quality_acceptance_official_0005_closure import (
            validate_phase6_revalidation,
        )

        return {
            "schema_version": (
                "public_text_quality_official_validation_result_v1"
            ),
            "status": "PASS",
            "attempt_id": ATTEMPT_ID,
            "requirement": "gate-candidate",
            "no_write": True,
            **validate_phase6_revalidation(require_tracked=True),
        }
    if requirement == "required-gate":
        from public_text_quality_acceptance_official_0005_closure import (
            validate_required_gate,
        )
        return validate_required_gate()
    if requirement == "phase6":
        from public_text_quality_acceptance_official_0005_closure import (
            validate_phase6,
        )

        return validate_phase6()
    if requirement == "independent-review":
        from public_text_quality_acceptance_official_0005_closure import (
            validate_independent_review,
        )

        return validate_independent_review()
    if requirement == "owner-seal":
        from public_text_quality_acceptance_official_0005_closure import (
            validate_owner_seal,
        )

        return validate_owner_seal()
    if requirement == "terminal-seal":
        from public_text_quality_acceptance_official_0005_closure import (
            validate_terminal,
        )

        return validate_terminal()
    if requirement not in (
        "phase0",
        "phase1",
        "phase2",
        "phase3",
        "phase4",
        "phase5",
    ):
        raise base.FoundationContractError(
            f"unsupported attempt-0005 validation requirement: {requirement}"
        )
    result = base.validate_official_attempt(
        attempt_id=attempt_id,
        requirement=requirement,
    )
    successor = _validate_phase0_successor(ATTEMPT_ROOT)
    return {
        **result,
        "official_current_input_binding_sha256": successor["sha256"],
        "g4_readiness_sha256": G4_READINESS_SHA256,
        "protected_surface_mutation_count": 0,
        "live_gate_mutation_count": 0,
    }
