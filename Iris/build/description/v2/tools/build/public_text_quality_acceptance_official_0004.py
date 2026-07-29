from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable

import public_text_quality_acceptance as base


ATTEMPT_ID = "attempt-0004-official"
START_COMMIT = "d966007e3b584d1befcd777f73d2fa9687333692"
START_TREE = "b85fcd34d2ddd5e31bd9bc5a4d730d71801b5b33"
EVALUATION_SUBJECT_KIND = "dvf_3_3_korean_naturalization_candidate"
NATURALIZATION_ATTEMPT_ID = "attempt-0023-compiler-identity-v2-a"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
G4_READINESS_SHA256 = (
    "8d52c65a17565c39eb623d3213e7c209ace5b0a2204b05b8eeea0da1bede61e0"
)
G4_PREDECESSOR_READINESS_SHA256 = (
    "fa96bbdeddbcb287fd5c9c39894385729cc1d165bc1281a00f8ee031f3c85e59"
)
G4_G1_HANDOFF_READINESS_SHA256 = (
    "abe9ce479647ed1f126a3c11ab5dd7c9c11afdd1c757fd68241eef58f8095e25"
)
G4_COMPILER_READINESS_SHA256 = (
    "1257393ad67dbab62ae9c6159ab6b5b680cf61967aa5f212306f36986336a7b3"
)
G4_AB_CANONICAL_SHA256 = (
    "62b6eb0a0be79cbfe99b5072058cc1d0e1ff60885cc10a2e0fd8341bd709b4f1"
)
CURRENT_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
CURRENT_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
PHASE8_HANDOFF_SHA256 = (
    "2cf743005bacb939a830bd04b448a061220f58fcbd64b745c8cf00972082a9c6"
)
PHASE8_CLOSEOUT_SHA256 = (
    "e8df68e1d7cd47d66001041df1b7c57ee024b5cd23795889fb32efb7297e0d41"
)
TERMINAL_CLOSEOUT_SHA256 = (
    "368847892c7a24c57469b47f8e16504f5b0822a094e79ecfee497b77a1d435f4"
)
CANDIDATE_SHA256 = (
    "c4d2799ffd931c585b6da2d4d9a7663c2207181f21a822dbea2794f5d3a08787"
)
TRACE_SHA256 = (
    "b2d94a4cbaa40a488f7a444a7ff8000c23eab5545b0ec57606fb80a18bd17268"
)
COMPILER_IDENTITY_ALGORITHM_ID = (
    "naturalization_compiler_identity_sha256_lf_normalized_ordered_paths_v2"
)
COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)

REPO_ROOT = base.REPO_ROOT
V2_ROOT = base.V2_ROOT
ATTEMPT_ROOT = base.DEFAULT_ATTEMPTS_ROOT / ATTEMPT_ID
FOUNDATION_CONTRACT = base.DEFAULT_FOUNDATION_ROOT / base.FOUNDATION_CONTRACT_NAME
G4_READINESS = (
    base.DEFAULT_FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0004"
    / "public_text_quality_protected_snapshot_identity_readiness.json"
)
G4_PREDECESSOR_READINESS = (
    base.DEFAULT_FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0003"
    / "public_text_quality_g1_gate_classification_readiness.json"
)
G4_G1_HANDOFF_READINESS = (
    base.DEFAULT_FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0002"
    / "public_text_quality_development_readiness_g1_handoff_correction.json"
)
G4_COMPILER_READINESS = (
    base.DEFAULT_FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0001"
    / "public_text_quality_development_readiness_implementation_correction.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
NATURALIZATION_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / NATURALIZATION_ATTEMPT_ID
)
PHASE8_HANDOFF = NATURALIZATION_ROOT / "phase8" / "publish_acceptance_handoff_manifest.json"
PHASE8_CLOSEOUT = NATURALIZATION_ROOT / "phase8" / "phase8_closeout.json"
TERMINAL_CLOSEOUT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt_0023_terminal_closeout.json"
)
CANDIDATE = NATURALIZATION_ROOT / "phase4" / "candidate_rendered.json"
TRACE = NATURALIZATION_ROOT / "phase4" / "candidate_proposition_trace.jsonl"
CURRENT_ROUTE_TEST = (
    V2_ROOT / "tests" / "test_public_text_quality_acceptance_current_route.py"
)

PHASE0_SUCCESSOR_BINDING = "official_current_input_binding_report.json"
PHASE5_EXCEPTION_REPORT = "evaluation_subject_exception_application_report.json"
PHASE5_WAIVER_REPORT = "evaluation_subject_waiver_application_report.json"
PHASE5_EFFECTIVE_REPORT = "evaluation_subject_effective_finding_report.json"
PHASE5_SUCCESSOR_BINDING = "current_input_successor_disposition_binding_report.json"


def _extend_phase_artifacts(phase: int, names: Iterable[str]) -> None:
    current = tuple(base.PHASE_ARTIFACTS[phase])
    base.PHASE_ARTIFACTS[phase] = current + tuple(
        name for name in names if name not in current
    )


_extend_phase_artifacts(0, (PHASE0_SUCCESSOR_BINDING,))
_extend_phase_artifacts(
    5,
    (
        PHASE5_EXCEPTION_REPORT,
        PHASE5_WAIVER_REPORT,
        PHASE5_EFFECTIVE_REPORT,
        PHASE5_SUCCESSOR_BINDING,
    ),
)


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
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
            f"official successor wrapper requires attempt ID {ATTEMPT_ID}"
        )


def _require_sha(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise base.FoundationContractError(f"{label} is missing: {base.repo_relative(path)}")
    actual = base.sha256_file(path)
    if actual != expected:
        raise base.FoundationContractError(
            f"{label} raw SHA mismatch: expected {expected}, got {actual}"
        )


def _raw_vcs_record(
    path: Path,
    *,
    expected_sha256: str | None = None,
    require_text_unset: bool = True,
) -> dict[str, Any]:
    if not path.is_file():
        raise base.FoundationContractError(
            f"required current input missing: {base.repo_relative(path)}"
        )
    if not base._is_tracked(path):
        raise base.FoundationContractError(
            f"required current input must be tracked: {base.repo_relative(path)}"
        )
    ignored_by_current_rules = base._is_ignored(path)
    relative = base.repo_relative(path)
    head_blob = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    working_blob = _git("hash-object", "--no-filters", "--", relative).stdout.strip()
    if head_blob != working_blob:
        raise base.FoundationContractError(
            f"Git blob/working raw-byte identity mismatch: {relative}"
        )
    raw_sha = base.sha256_file(path)
    if expected_sha256 is not None and raw_sha != expected_sha256:
        raise base.FoundationContractError(
            f"raw SHA mismatch for {relative}: expected {expected_sha256}, got {raw_sha}"
        )
    attr = _git("check-attr", "text", "--", relative).stdout.strip()
    text_unset = attr.endswith(": text: unset")
    if require_text_unset and not text_unset:
        raise base.FoundationContractError(f"required input lacks exact -text: {relative}")
    return {
        "path": relative,
        "sha256": raw_sha,
        "git_blob_id": head_blob,
        "working_raw_blob_id": working_blob,
        "git_blob_working_byte_identity": True,
        "tracked": True,
        "ignored": ignored_by_current_rules,
        "tracked_file_ignore_effect": "none",
        "text_attribute": "unset" if text_unset else attr.rsplit(": ", 1)[-1],
    }


def _validate_readpoints() -> dict[str, Any]:
    start_tree = _git("show", "-s", "--format=%T", START_COMMIT).stdout.strip()
    if start_tree != START_TREE:
        raise base.FoundationContractError("official start commit/tree mismatch")
    if _git("merge-base", "--is-ancestor", START_COMMIT, "HEAD", check=False).returncode:
        raise base.FoundationContractError("official start commit is not an ancestor of HEAD")
    return {
        "start_commit": START_COMMIT,
        "start_tree": START_TREE,
        "execution_head": base.git_head(),
        "execution_tree": _git("show", "-s", "--format=%T", "HEAD").stdout.strip(),
        "start_commit_is_ancestor": True,
    }


def _validate_g4_readiness() -> dict[str, Any]:
    record = _raw_vcs_record(G4_READINESS, expected_sha256=G4_READINESS_SHA256)
    value = base.load_json_strict(G4_READINESS)
    expected = {
        "schema_version": (
            "public_text_quality_foundation_protected_snapshot_identity_"
            "correction_readiness_v1"
        ),
        "correction_id": "implementation-correction-0004",
        "status": "PASS",
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "protected_surface_mutation_count": 0,
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "handoff_text_constituent_freshness_algorithm_changed": False,
        "protected_snapshot_identity_implementation_changed": True,
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            raise base.FoundationContractError(f"G4 readiness field mismatch: {key}")
    predecessor_binding = value.get("predecessor_readiness", {})
    foundation = value.get("foundation_semantics", {}).get(
        "foundation_contract", {}
    )
    if (
        predecessor_binding.get("path") != base.repo_relative(G4_PREDECESSOR_READINESS)
        or predecessor_binding.get("sha256") != G4_PREDECESSOR_READINESS_SHA256
        or predecessor_binding.get("correction_id") != "implementation-correction-0003"
        or predecessor_binding.get("predecessor_mutated") is not False
        or foundation.get("sha256") != FOUNDATION_CONTRACT_SHA256
        or value.get("foundation_semantics", {}).get(
            "meaning_path_count"
        )
        != 17
        or value.get("foundation_semantics", {}).get(
            "unchanged_meaning_path_count"
        )
        != 16
        or value.get("foundation_semantics", {}).get(
            "intentionally_corrected_meaning_path_count"
        )
        != 1
        or value.get("foundation_semantics", {}).get(
            "protected_snapshot_identity_algorithm_id"
        )
        != base.PROTECTED_SNAPSHOT_IDENTITY_ALGORITHM_ID
    ):
        raise base.FoundationContractError("G4 readiness predecessor binding mismatch")
    predecessor_record = _raw_vcs_record(
        G4_PREDECESSOR_READINESS,
        expected_sha256=G4_PREDECESSOR_READINESS_SHA256,
    )
    predecessor = base.load_json_strict(G4_PREDECESSOR_READINESS)
    g1_handoff_binding = predecessor.get("predecessor_readiness", {})
    if (
        predecessor.get("schema_version")
        != (
            "public_text_quality_foundation_g1_gate_classification_"
            "correction_readiness_v1"
        )
        or predecessor.get("correction_id") != "implementation-correction-0003"
        or predecessor.get("status") != "PASS"
        or predecessor.get("authority_effect") != "none"
        or g1_handoff_binding.get("path")
        != base.repo_relative(G4_G1_HANDOFF_READINESS)
        or g1_handoff_binding.get("sha256")
        != G4_G1_HANDOFF_READINESS_SHA256
        or g1_handoff_binding.get("correction_id")
        != "implementation-correction-0002"
        or g1_handoff_binding.get("predecessor_mutated") is not False
    ):
        raise base.FoundationContractError(
            "G4 readiness implementation predecessor mismatch"
        )
    gate = value.get("g1_clean_checkout_correction", {})
    census = gate.get("census", {})
    if (
        gate.get("status") != "PASS"
        or gate.get("canonical_result_sha256") != G4_AB_CANONICAL_SHA256
        or gate.get("run_a_result") != "185/185 PASS"
        or gate.get("run_b_result") != "185/185 PASS"
        or gate.get("blocking_condition_count") != 0
        or census
        != {
            "tracked": 93,
            "required": 33,
            "historical": 55,
            "obsolete": 3,
            "fixture": 2,
            "unresolved_dependency": 0,
        }
    ):
        raise base.FoundationContractError(
            "G4 readiness G1 gate-classification binding mismatch"
        )
    g1_handoff_record = _raw_vcs_record(
        G4_G1_HANDOFF_READINESS,
        expected_sha256=G4_G1_HANDOFF_READINESS_SHA256,
    )
    g1_handoff = base.load_json_strict(G4_G1_HANDOFF_READINESS)
    compiler_binding = g1_handoff.get("predecessor_readiness", {})
    if (
        g1_handoff.get("schema_version")
        != "public_text_quality_foundation_g1_handoff_correction_readiness_v1"
        or g1_handoff.get("correction_id") != "implementation-correction-0002"
        or g1_handoff.get("status") != "PASS"
        or g1_handoff.get("authority_effect") != "none"
        or compiler_binding.get("path") != base.repo_relative(G4_COMPILER_READINESS)
        or compiler_binding.get("sha256") != G4_COMPILER_READINESS_SHA256
        or compiler_binding.get("correction_id") != "implementation-correction-0001"
        or compiler_binding.get("predecessor_mutated") is not False
    ):
        raise base.FoundationContractError(
            "G4 readiness G1-handoff predecessor mismatch"
        )
    compiler_record = _raw_vcs_record(
        G4_COMPILER_READINESS,
        expected_sha256=G4_COMPILER_READINESS_SHA256,
    )
    compiler_readiness = base.load_json_strict(G4_COMPILER_READINESS)
    compiler = compiler_readiness.get("compiler_identity_correction", {})
    registry = compiler_readiness.get("registry_current_inputs", {})
    if (
        compiler_readiness.get("schema_version")
        != "public_text_quality_foundation_implementation_correction_readiness_v1"
        or compiler_readiness.get("correction_id") != "implementation-correction-0001"
        or compiler_readiness.get("status") != "PASS"
        or compiler_readiness.get("authority_effect") != "none"
        or compiler.get("algorithm_id") != COMPILER_IDENTITY_ALGORITHM_ID
        or compiler.get("compiler_aggregate_sha256") != COMPILER_AGGREGATE_SHA256
        or compiler.get("compiler_path_count") != 9
        or compiler.get("identity_helper_in_compiler_aggregate") is not False
        or compiler.get("producer_consumer_shared_helper_identity") is not True
        or compiler.get("producer_consumer_path_order_identity") is not True
        or registry.get("current_facts", {}).get("sha256") != CURRENT_FACTS_SHA256
        or registry.get("current_manifest", {}).get("sha256")
        != CURRENT_MANIFEST_SHA256
    ):
        raise base.FoundationContractError(
            "G4 readiness compiler/current-input predecessor mismatch"
        )
    return {
        **record,
        "predecessor_readiness": predecessor_record,
        "g1_handoff_readiness": g1_handoff_record,
        "compiler_readiness": compiler_record,
        "g1_ab_canonical_sha256": G4_AB_CANONICAL_SHA256,
        "compiler_identity_algorithm_id": COMPILER_IDENTITY_ALGORITHM_ID,
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
    }


def _sealed_text_vcs_record(
    path: Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    record = base._head_text_constituent_record(path, expected_sha256)
    if record.get("match") is not True:
        raise base.FoundationContractError(
            f"sealed text identity mismatch: {base.repo_relative(path)}"
        )
    return {
        **record,
        "sealed_expected_sha256": expected_sha256,
        "raw_head_git_identity_strict": True,
    }


def validate_current_inputs(*, require_clean: bool) -> dict[str, Any]:
    readpoint = _validate_readpoints()
    if require_clean:
        status = _git("status", "--porcelain=v1", "--untracked-files=all").stdout
        if status:
            raise base.FoundationContractError(
                "Phase 0 requires a clean materialized execution checkout"
            )
    fixed_records = {
        "foundation_contract": _raw_vcs_record(
            FOUNDATION_CONTRACT, expected_sha256=FOUNDATION_CONTRACT_SHA256
        ),
        "g4_readiness": _validate_g4_readiness(),
        "current_facts": _raw_vcs_record(
            CURRENT_FACTS, expected_sha256=CURRENT_FACTS_SHA256
        ),
        "current_manifest": _raw_vcs_record(
            CURRENT_MANIFEST, expected_sha256=CURRENT_MANIFEST_SHA256
        ),
        "phase8_handoff": _raw_vcs_record(
            PHASE8_HANDOFF,
            expected_sha256=PHASE8_HANDOFF_SHA256,
            require_text_unset=False,
        ),
        "phase8_closeout": _raw_vcs_record(
            PHASE8_CLOSEOUT,
            expected_sha256=PHASE8_CLOSEOUT_SHA256,
            require_text_unset=False,
        ),
        "terminal_closeout": _raw_vcs_record(
            TERMINAL_CLOSEOUT,
            expected_sha256=TERMINAL_CLOSEOUT_SHA256,
            require_text_unset=False,
        ),
        "trace": _sealed_text_vcs_record(
            TRACE,
            expected_sha256=TRACE_SHA256,
        ),
    }
    handoff_validation = base.validate_candidate_handoff(PHASE8_HANDOFF)
    handoff = handoff_validation["handoff"]
    if (
        handoff["naturalization_attempt_id"] != NATURALIZATION_ATTEMPT_ID
        or handoff["requested_evaluation_subject_kind"] != EVALUATION_SUBJECT_KIND
        or handoff_validation["handoff_raw_sha256"] != PHASE8_HANDOFF_SHA256
        or handoff_validation["constituents"]["candidate_rendered_hash"]["sha256"]
        != CANDIDATE_SHA256
        or handoff_validation["compiler_aggregate_hash"]
        != COMPILER_AGGREGATE_SHA256
    ):
        raise base.FoundationContractError("Naturalization handoff identity mismatch")
    constituent_records = handoff_validation["path_rows"]
    candidate_record = next(
        row for row in constituent_records if row["id"] == "candidate_rendered_hash"
    )
    if (
        candidate_record["path"] != base.repo_relative(CANDIDATE)
        or candidate_record["declared_sha256"] != CANDIDATE_SHA256
        or candidate_record["match"] is not True
    ):
        raise base.FoundationContractError("Naturalization candidate identity mismatch")
    fixed_records["candidate"] = {
        **candidate_record,
        "sealed_expected_sha256": CANDIDATE_SHA256,
        "raw_head_git_identity_strict": True,
    }
    closeout = base.load_json_strict(PHASE8_CLOSEOUT)
    if (
        closeout.get("schema_version") != "dvf-3-3-naturalization-phase8-closeout-v1"
        or closeout.get("status") != "HANDOFF_COMPLETE"
        or closeout.get("naturalization_attempt_id") != NATURALIZATION_ATTEMPT_ID
        or closeout.get("candidate_rendered_sha256") != CANDIDATE_SHA256
        or closeout.get("publish_acceptance_handoff_manifest_sha256")
        != PHASE8_HANDOFF_SHA256
        or closeout.get("human_review_blocker_count") != 0
        or closeout.get("live_gate_mutated") is not False
        or closeout.get("official_publish_attempt_created") is not False
    ):
        raise base.FoundationContractError("Phase 8 closeout contract mismatch")
    terminal = base.load_json_strict(TERMINAL_CLOSEOUT)
    terminal_handoff = terminal.get("phase8_handoff", {})
    if (
        terminal.get("status") != "PASS"
        or terminal.get("attempts", {}).get("primary") != NATURALIZATION_ATTEMPT_ID
        or terminal_handoff.get("status") != "HANDOFF_COMPLETE"
        or terminal_handoff.get("publish_acceptance_handoff_manifest_sha256")
        != PHASE8_HANDOFF_SHA256
        or terminal_handoff.get("phase8_closeout_sha256") != PHASE8_CLOSEOUT_SHA256
        or terminal.get("scope_guards", {}).get("live_gate_mutated") is not False
    ):
        raise base.FoundationContractError("Naturalization terminal closeout mismatch")
    return {
        "readpoint": readpoint,
        "records": fixed_records,
        "handoff_constituent_records": constituent_records,
        "handoff_required_constituent_count": len(base.REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "handoff_constituent_hash_mismatch_count": 0,
        "candidate_trace_sha256": TRACE_SHA256,
        "compiler_identity_algorithm_id": COMPILER_IDENTITY_ALGORITHM_ID,
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "current_checkout_input_fresh": True,
        "protected_input_mutation_count": 0,
    }


def _current_foundation_validation_shim(
    *, foundation_id: str, foundation_root: Path = base.DEFAULT_FOUNDATION_ROOT
) -> dict[str, Any]:
    if foundation_root.resolve() != base.DEFAULT_FOUNDATION_ROOT.resolve():
        raise base.FoundationContractError("official successor requires tracked G4 foundation root")
    if foundation_id != "ptqa-foundation-v1":
        raise base.FoundationContractError("established official runner foundation selector changed")
    current = validate_current_inputs(require_clean=False)
    return {
        "status": "PASS",
        "foundation_id": base.load_json_strict(FOUNDATION_CONTRACT)["foundation_id"],
        "foundation_contract_raw_sha256": FOUNDATION_CONTRACT_SHA256,
        "readiness_successor_raw_sha256": G4_READINESS_SHA256,
        "current_facts_sha256": CURRENT_FACTS_SHA256,
        "current_manifest_sha256": CURRENT_MANIFEST_SHA256,
        "protected_surface_mutation_count": current["protected_input_mutation_count"],
        "authority_effect": "none",
    }


def _phase0_successor_report(
    *, attempt_id: str, current: dict[str, Any]
) -> dict[str, Any]:
    root = base.official_attempt_root(attempt_id)
    binding = base.load_json_strict(
        base.phase_root(root, 0) / "acceptance_input_binding_manifest.json"
    )
    return {
        "schema_version": "public_text_quality_official_current_input_binding_v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        "candidate_trace_sha256": TRACE_SHA256,
        "naturalization_attempt_id": NATURALIZATION_ATTEMPT_ID,
        "phase8_handoff_sha256": PHASE8_HANDOFF_SHA256,
        "phase8_closeout_sha256": PHASE8_CLOSEOUT_SHA256,
        "terminal_closeout_sha256": TERMINAL_CLOSEOUT_SHA256,
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "g4_readiness_successor_sha256": G4_READINESS_SHA256,
        "current_facts_sha256": CURRENT_FACTS_SHA256,
        "current_manifest_sha256": CURRENT_MANIFEST_SHA256,
        "start_readpoint": current["readpoint"],
        "acceptance_input_binding_hash": binding["binding_hash"],
        "handoff_required_constituent_count": current[
            "handoff_required_constituent_count"
        ],
        "handoff_constituent_hash_mismatch_count": 0,
        "input_records": current["records"],
        "handoff_constituent_records": current["handoff_constituent_records"],
        "current_checkout_input_fresh": True,
        "protected_surface_mutation_count": 0,
        "evaluation_subject_disposition": "not_issued",
        "authority_effect": "official_evaluation_input_binding_only",
        "live_gate_adopted": False,
        "policy_closure_state": "incomplete",
    }


def _validate_phase0_successor(root: Path) -> dict[str, Any]:
    path = base.phase_root(root, 0) / PHASE0_SUCCESSOR_BINDING
    if not path.is_file():
        raise base.FoundationContractError("official current-input binding report is missing")
    report = base.load_json_strict(path)
    current = validate_current_inputs(require_clean=False)
    if (
        report.get("status") != "PASS"
        or report.get("attempt_id") != ATTEMPT_ID
        or report.get("evaluation_subject_sha256") != CANDIDATE_SHA256
        or report.get("candidate_trace_sha256") != TRACE_SHA256
        or report.get("phase8_handoff_sha256") != PHASE8_HANDOFF_SHA256
        or report.get("phase8_closeout_sha256") != PHASE8_CLOSEOUT_SHA256
        or report.get("terminal_closeout_sha256") != TERMINAL_CLOSEOUT_SHA256
        or report.get("foundation_contract_sha256") != FOUNDATION_CONTRACT_SHA256
        or report.get("g4_readiness_successor_sha256") != G4_READINESS_SHA256
        or report.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or report.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or report.get("handoff_constituent_hash_mismatch_count") != 0
        or report.get("protected_surface_mutation_count") != 0
        or report.get("live_gate_adopted") is not False
    ):
        raise base.FoundationContractError("official current-input binding report is stale")
    execution_head = report.get("start_readpoint", {}).get("execution_head")
    if (
        not isinstance(execution_head, str)
        or _git("merge-base", "--is-ancestor", execution_head, "HEAD", check=False).returncode
    ):
        raise base.FoundationContractError("Phase 0 execution HEAD is not an ancestor")
    return {
        "status": "PASS",
        "path": base.repo_relative(path),
        "raw_sha256": base.sha256_file(path),
        "input_fresh": current["current_checkout_input_fresh"],
        "protected_surface_mutation_count": 0,
    }


def _write_phase5_companions(root: Path) -> None:
    p5 = base.phase_root(root, 5)
    raw = base.load_json_strict(p5 / "evaluation_subject_raw_metric_report.json")
    disposition = base.load_json_strict(p5 / "evaluation_subject_disposition.json")
    phase0_binding = _validate_phase0_successor(root)
    exceptions = {
        "schema_version": "public_text_quality_exception_application_report_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        **raw["exception_application"],
    }
    waivers = {
        "schema_version": "public_text_quality_waiver_application_report_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        **raw["waiver_application"],
    }
    effective = {
        "schema_version": "public_text_quality_effective_finding_report_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        "qualified_disposition": disposition["qualified_disposition"],
        "technical_blocker_count": disposition["technical_blocker_count"],
        "effective_blocking_finding_count": disposition[
            "effective_blocking_finding_count"
        ],
        "advisory_debt_count": disposition["advisory_debt_count"],
        "active_waiver_count": disposition["active_waiver_count"],
        "effective_findings": raw["effective_findings"],
        "omitted_blocking_or_advisory_finding_count": raw[
            "omitted_blocking_or_advisory_finding_count"
        ],
    }
    successor_binding = {
        "schema_version": "public_text_quality_current_input_disposition_binding_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "phase0_current_input_binding_path": phase0_binding["path"],
        "phase0_current_input_binding_sha256": phase0_binding["raw_sha256"],
        "evaluation_subject_disposition_path": base.repo_relative(
            p5 / "evaluation_subject_disposition.json"
        ),
        "evaluation_subject_disposition_sha256": base.sha256_file(
            p5 / "evaluation_subject_disposition.json"
        ),
        "evaluation_subject_disposition_hash": disposition["disposition_hash"],
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        "candidate_trace_sha256": TRACE_SHA256,
        "phase8_handoff_sha256": PHASE8_HANDOFF_SHA256,
        "phase8_closeout_sha256": PHASE8_CLOSEOUT_SHA256,
        "terminal_closeout_sha256": TERMINAL_CLOSEOUT_SHA256,
        "g4_readiness_successor_sha256": G4_READINESS_SHA256,
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "current_facts_sha256": CURRENT_FACTS_SHA256,
        "current_manifest_sha256": CURRENT_MANIFEST_SHA256,
        "qualified_disposition": disposition["qualified_disposition"],
        "adoption_timing": disposition["synchronization_return"]["adoption_timing"],
        "current_checkout_input_fresh": True,
        "protected_surface_mutation_count": 0,
        "live_gate_adopted": False,
        "policy_closure_state": "incomplete",
    }
    base.write_once_or_same(p5 / PHASE5_EXCEPTION_REPORT, exceptions)
    base.write_once_or_same(p5 / PHASE5_WAIVER_REPORT, waivers)
    base.write_once_or_same(p5 / PHASE5_EFFECTIVE_REPORT, effective)
    base.write_once_or_same(p5 / PHASE5_SUCCESSOR_BINDING, successor_binding)
    if disposition["qualified_disposition"] != "accepted":
        base.write_once_or_same(
            p5 / "naturalization_failure_ledger.json",
            {
                "schema_version": "public_text_quality_naturalization_failure_ledger_v1",
                "status": disposition["qualified_disposition"],
                "attempt_id": ATTEMPT_ID,
                "evaluation_subject_sha256": CANDIDATE_SHA256,
                "exact_failure_count": len(disposition["exact_failure_ledger"]),
                "exact_failures": disposition["exact_failure_ledger"],
                "return_phase": disposition["synchronization_return"][
                    "earliest_affected_naturalization_phase"
                ],
                "adoption_timing": "after_remediation",
                "live_gate_adoption_allowed": False,
                "phase7_allowed": False,
                "policy_closure_state": "incomplete",
            },
        )


def _validate_phase5_companions(root: Path) -> dict[str, Any]:
    p5 = base.phase_root(root, 5)
    disposition = base.load_json_strict(p5 / "evaluation_subject_disposition.json")
    raw = base.load_json_strict(p5 / "evaluation_subject_raw_metric_report.json")
    exception = base.load_json_strict(p5 / PHASE5_EXCEPTION_REPORT)
    waiver = base.load_json_strict(p5 / PHASE5_WAIVER_REPORT)
    effective = base.load_json_strict(p5 / PHASE5_EFFECTIVE_REPORT)
    successor = base.load_json_strict(p5 / PHASE5_SUCCESSOR_BINDING)
    phase0 = _validate_phase0_successor(root)
    if (
        exception.get("status") != "PASS"
        or exception.get("raw_metric_mutation_count") != 0
        or waiver.get("status") != "PASS"
        or waiver.get("raw_metric_mutation_count") != 0
        or effective.get("status") != "PASS"
        or effective.get("qualified_disposition")
        != disposition["qualified_disposition"]
        or effective.get("effective_findings") != raw["effective_findings"]
        or effective.get("omitted_blocking_or_advisory_finding_count") != 0
        or successor.get("status") != "PASS"
        or successor.get("phase0_current_input_binding_sha256") != phase0["raw_sha256"]
        or successor.get("evaluation_subject_disposition_hash")
        != disposition["disposition_hash"]
        or successor.get("g4_readiness_successor_sha256") != G4_READINESS_SHA256
        or successor.get("protected_surface_mutation_count") != 0
        or successor.get("live_gate_adopted") is not False
    ):
        raise base.FoundationContractError("Phase 5 separated finding/binding reports failed")
    if disposition["qualified_disposition"] != "accepted":
        failure = base.load_json_strict(p5 / "naturalization_failure_ledger.json")
        if (
            failure.get("adoption_timing") != "after_remediation"
            or failure.get("live_gate_adoption_allowed") is not False
        ):
            raise base.FoundationContractError("non-accepted failure ledger invalid")
    return {
        "status": "PASS",
        "qualified_disposition": disposition["qualified_disposition"],
        "disposition_raw_sha256": base.sha256_file(
            p5 / "evaluation_subject_disposition.json"
        ),
        "disposition_hash": disposition["disposition_hash"],
        "technical_blocker_count": disposition["technical_blocker_count"],
        "effective_blocking_finding_count": disposition[
            "effective_blocking_finding_count"
        ],
        "advisory_debt_count": disposition["advisory_debt_count"],
        "active_waiver_count": disposition["active_waiver_count"],
        "adoption_timing": disposition["synchronization_return"]["adoption_timing"],
    }


def _preserving_pretty_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _tracked_not_ignored(path: Path) -> bool:
    return path.is_file() and base._is_tracked(path) and not base._is_ignored(path)


def _candidate_required_entries(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p0 = base.phase_root(root, 0)
    p1 = base.phase_root(root, 1)
    p2 = base.phase_root(root, 2)
    p4 = base.phase_root(root, 4)
    p5 = base.phase_root(root, 5)
    p6 = base.phase_root(root, 6)
    artifacts = [
        {
            "path": base.repo_relative(p0 / "acceptance_input_binding_manifest.json"),
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
            "path": base.repo_relative(p4 / "adversarial_fixture_manifest.json"),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(p5 / "evaluation_subject_disposition.json"),
            "checks": [{"field": "qualified_disposition", "equals": "accepted"}],
        },
        {
            "path": base.repo_relative(p5 / PHASE5_SUCCESSOR_BINDING),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(
                p6 / "stale_disposition_consumption_guard_report.json"
            ),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(p6 / "pre_adoption_protected_surface_report.json"),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
        {
            "path": base.repo_relative(p6 / "required_artifact_recensus_report.json"),
            "checks": [{"field": "status", "equals": "PASS"}],
        },
    ]
    test = {
        "test_id": (
            "test_public_text_quality_acceptance_current_route."
            "PublicTextQualityAcceptanceCurrentRouteTest."
            "test_required_gate_runs_standalone_subprocess"
        ),
        "reason": "standalone Publish Boundary public-text acceptance required gate",
        "role": "publish_boundary_public_text_acceptance_required_validation",
        "required": True,
    }
    return artifacts, test


def build_phase6_gate_candidate(*, attempt_id: str) -> dict[str, Any]:
    _require_attempt_id(attempt_id)
    root = base.official_attempt_root(attempt_id)
    phase5 = _validate_phase5_companions(root)
    if phase5["qualified_disposition"] != "accepted":
        raise base.FoundationContractError(
            "Phase 6 candidate is forbidden for non-accepted synchronized candidate"
        )
    prerequisite_paths = [
        path
        for phase in range(0, 6)
        for name in base.PHASE_ARTIFACTS[phase]
        for path in (base.phase_root(root, phase) / name,)
    ]
    if any(not _tracked_not_ignored(path) for path in prerequisite_paths):
        missing = [
            base.repo_relative(path)
            for path in prerequisite_paths
            if not _tracked_not_ignored(path)
        ]
        raise base.FoundationContractError(
            f"Phase 6 candidate prerequisites must be staged/tracked: {missing}"
        )
    if not _tracked_not_ignored(CURRENT_ROUTE_TEST):
        raise base.FoundationContractError("Phase 6 current-route test must be staged/tracked")
    live_before = _raw_vcs_record(base.LIVE_REQUIRED_VALIDATIONS)
    p6 = base.phase_root(root, 6)
    current_input = validate_current_inputs(require_clean=False)
    stale_guard = {
        "schema_version": "public_text_quality_stale_disposition_consumption_guard_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "evaluation_subject_sha256": CANDIDATE_SHA256,
        "evaluation_subject_disposition_sha256": phase5["disposition_raw_sha256"],
        "evaluation_subject_disposition_hash": phase5["disposition_hash"],
        "phase0_current_input_binding_sha256": base.sha256_file(
            base.phase_root(root, 0) / PHASE0_SUCCESSOR_BINDING
        ),
        "g4_readiness_successor_sha256": G4_READINESS_SHA256,
        "current_checkout_input_fresh": True,
        "stale_disposition_consumption_count": 0,
    }
    protected = {
        "schema_version": "public_text_quality_phase6_pre_adoption_protected_surface_v1",
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
    recensus = {
        "schema_version": "public_text_quality_required_artifact_recensus_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "base_required_artifact_count": len(
            base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)["required_artifacts"]
        ),
        "base_required_test_count": len(
            base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)["required_tests"]
        ),
        "publish_required_artifact_addition_count": len(artifacts),
        "publish_required_test_addition_count": 1,
        "prerequisite_tracked_count": len(prerequisite_paths),
        "prerequisite_required_count": len(prerequisite_paths),
        "prerequisite_ignored_count": 0,
        "same_run_phase6_artifacts_require_staging_before_candidate_route": True,
        "candidate_route_recensus_authority": "fresh_validator_and_route_execution",
    }
    gitignore_report = {
        "schema_version": "public_text_quality_gitignore_exact_unignore_patch_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "unignore_materialized_before_phase0": True,
        "live_adoption_gitignore_change_required": False,
        "live_adoption_gitignore_diff": [],
    }
    base.write_once_or_same(
        p6 / "stale_disposition_consumption_guard_report.json", stale_guard
    )
    base.write_once_or_same(p6 / "pre_adoption_protected_surface_report.json", protected)
    base.write_once_or_same(p6 / "required_artifact_recensus_report.json", recensus)
    base.write_once_or_same(p6 / "gitignore_exact_unignore_patch.json", gitignore_report)

    live_manifest = base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)
    candidate_manifest = deepcopy(live_manifest)
    candidate_manifest["required_artifacts"].extend(artifacts)
    candidate_manifest["required_tests"].append(required_test)
    candidate_path = p6 / "required_gate_candidate.json"
    base.write_once_bytes(candidate_path, _preserving_pretty_bytes(candidate_manifest))
    candidate_sha = base.sha256_file(candidate_path)
    patch = {
        "schema_version": "public_text_quality_required_gate_patch_v1",
        "status": "PASS",
        "attempt_id": ATTEMPT_ID,
        "target_path": base.repo_relative(base.LIVE_REQUIRED_VALIDATIONS),
        "base_manifest_sha256": live_before["sha256"],
        "candidate_manifest_path": base.repo_relative(candidate_path),
        "candidate_manifest_sha256": candidate_sha,
        "operation": "append_only_required_artifacts_and_required_tests",
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
        "schema_version": "public_text_quality_required_gate_adoption_contract_v1",
        "status": "AWAITING_EXPLICIT_LIVE_GATE_APPROVAL",
        "attempt_id": ATTEMPT_ID,
        "candidate_manifest_sha256": candidate_sha,
        "candidate_patch_sha256": patch_sha,
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": phase5["disposition_hash"],
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
        "live_manifest_path": base.repo_relative(base.LIVE_REQUIRED_VALIDATIONS),
        "live_manifest_base_sha256": live_before["sha256"],
        "live_manifest_mutated": False,
        "authority_effect": "none",
        "phase7_allowed": False,
        "policy_closure_state": "incomplete",
        "rollback_contract": {
            "precondition": "live manifest must still match base SHA before adoption",
            "rollback_operation": "restore exact base manifest bytes",
            "rollback_target_path": base.repo_relative(base.LIVE_REQUIRED_VALIDATIONS),
            "rollback_base_sha256": live_before["sha256"],
            "post_rollback_validation": "run current route with restored live manifest",
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
            "- Adoption state: `AWAITING_EXPLICIT_LIVE_GATE_APPROVAL`\n\n"
            "Legacy Combined DVF Governance Route PASS\n"
            "!= public text accepted\n"
            "!= Public Text Quality Acceptance Policy Closure\n"
            "!= Publish Boundary PASS\n"
            "!= package-ready\n"
            "!= release-ready\n"
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
    phase5 = _validate_phase5_companions(root)
    if phase5["qualified_disposition"] != "accepted":
        raise base.FoundationContractError("gate candidate forbidden for non-accepted subject")
    p6 = base.phase_root(root, 6)
    candidate_path = p6 / "required_gate_candidate.json"
    patch_path = p6 / "required_gate_patch.json"
    contract_path = p6 / "required_gate_adoption_contract.json"
    for path in (
        candidate_path,
        patch_path,
        contract_path,
        p6 / "required_gate_adoption_contract.md",
        p6 / "gitignore_exact_unignore_patch.json",
        p6 / "required_artifact_recensus_report.json",
        p6 / "stale_disposition_consumption_guard_report.json",
        p6 / "pre_adoption_protected_surface_report.json",
    ):
        if not path.is_file():
            raise base.FoundationContractError(
                f"Phase 6 candidate artifact missing: {base.repo_relative(path)}"
            )
    live = base.load_json_strict(base.LIVE_REQUIRED_VALIDATIONS)
    candidate = base.load_json_strict(candidate_path)
    patch = base.load_json_strict(patch_path)
    contract = base.load_json_strict(contract_path)
    artifacts = patch["added_required_artifacts"]
    tests = patch["added_required_tests"]
    if (
        candidate["required_artifacts"]
        != [*live["required_artifacts"], *artifacts]
        or candidate["required_tests"] != [*live["required_tests"], *tests]
    ):
        raise base.FoundationContractError("candidate manifest is not an additive-only projection")
    live_without_lists = {
        key: value
        for key, value in live.items()
        if key not in ("required_artifacts", "required_tests")
    }
    candidate_without_lists = {
        key: value
        for key, value in candidate.items()
        if key not in ("required_artifacts", "required_tests")
    }
    if live_without_lists != candidate_without_lists:
        raise base.FoundationContractError("candidate manifest changes non-additive fields")
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
        raise base.FoundationContractError("Phase 6 approval contract/hash mismatch")
    required_paths = [REPO_ROOT / row["path"] for row in artifacts]
    missing_or_untracked = [
        base.repo_relative(path)
        for path in required_paths
        if not _tracked_not_ignored(path)
    ]
    if missing_or_untracked:
        raise base.FoundationContractError(
            f"candidate required artifact recensus failed: {missing_or_untracked}"
        )
    if not _tracked_not_ignored(CURRENT_ROUTE_TEST):
        raise base.FoundationContractError("candidate required test is not tracked")
    live_record = _raw_vcs_record(base.LIVE_REQUIRED_VALIDATIONS)
    if live_record["sha256"] != contract["live_manifest_base_sha256"]:
        raise base.FoundationContractError("live manifest changed before approval")
    return {
        "status": "PASS",
        "candidate_manifest_path": base.repo_relative(candidate_path),
        "candidate_manifest_sha256": candidate_sha,
        "candidate_patch_sha256": patch_sha,
        "required_artifact_recensus": {
            "required_count": len(required_paths),
            "tracked_count": len(required_paths),
            "ignored_count": 0,
            "missing_count": 0,
        },
        "required_test_recensus": {
            "required_count": 1,
            "tracked_count": 1,
            "ignored_count": 0,
            "missing_count": 0,
        },
        "live_manifest_mutated": False,
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
            raise base.FoundationContractError("official successor subject kind mismatch")
        if subject_handoff is None or subject_handoff.resolve() != PHASE8_HANDOFF.resolve():
            raise base.FoundationContractError("official successor handoff path mismatch")
        if ATTEMPT_ROOT.exists():
            raise base.FoundationContractError("fresh official attempt root already exists")
        status_before = _git(
            "status", "--porcelain=v1", "--untracked-files=all"
        ).stdout
        if status_before:
            raise base.FoundationContractError(
                "Phase 0 no-write preflight requires a clean checkout"
            )
        current = validate_current_inputs(require_clean=True)
        status_after = _git(
            "status", "--porcelain=v1", "--untracked-files=all"
        ).stdout
        if status_after != status_before or ATTEMPT_ROOT.exists():
            raise base.FoundationContractError(
                "Phase 0 no-write preflight mutated the checkout or consumed the attempt"
            )
        return {
            "schema_version": (
                "public_text_quality_official_phase0_no_write_preflight_v1"
            ),
            "status": "PASS",
            "attempt_id": ATTEMPT_ID,
            "attempt_root_created": False,
            "official_attempt_consumed": False,
            "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "evaluation_subject_sha256": CANDIDATE_SHA256,
            "naturalization_attempt_id": NATURALIZATION_ATTEMPT_ID,
            "phase8_handoff_sha256": PHASE8_HANDOFF_SHA256,
            "phase8_closeout_sha256": PHASE8_CLOSEOUT_SHA256,
            "terminal_closeout_sha256": TERMINAL_CLOSEOUT_SHA256,
            "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
            "g4_readiness_successor_sha256": G4_READINESS_SHA256,
            "compiler_identity_algorithm_id": COMPILER_IDENTITY_ALGORITHM_ID,
            "compiler_aggregate_sha256": current["compiler_aggregate_sha256"],
            "current_checkout_input_fresh": True,
            "source_checkout_clean_before": True,
            "source_checkout_clean_after": True,
            "protected_surface_mutation_count": 0,
            "live_gate_mutation_count": 0,
            "official_disposition": "not_issued",
            "authority_effect": "none",
            "live_gate_adopted": False,
            "policy_closure_state": "not_started",
            "readpoint": current["readpoint"],
        }
    if mode == "phase0-binding":
        if evaluation_subject_kind != EVALUATION_SUBJECT_KIND:
            raise base.FoundationContractError("official successor subject kind mismatch")
        if subject_handoff is None or subject_handoff.resolve() != PHASE8_HANDOFF.resolve():
            raise base.FoundationContractError("official successor handoff path mismatch")
        if ATTEMPT_ROOT.exists():
            raise base.FoundationContractError("fresh official attempt root already exists")
        current = validate_current_inputs(require_clean=True)
        original = base.validate_foundation
        base.validate_foundation = _current_foundation_validation_shim
        try:
            result = base.run_official_mode(
                attempt_id=attempt_id,
                mode=mode,
                evaluation_subject_kind=evaluation_subject_kind,
                subject_handoff=subject_handoff,
            )
        finally:
            base.validate_foundation = original
        base.write_once_or_same(
            base.phase_root(ATTEMPT_ROOT, 0) / PHASE0_SUCCESSOR_BINDING,
            _phase0_successor_report(attempt_id=attempt_id, current=current),
        )
        return {
            **result,
            "start_commit": START_COMMIT,
            "start_tree": START_TREE,
            "g4_readiness_successor_sha256": G4_READINESS_SHA256,
            "current_facts_sha256": CURRENT_FACTS_SHA256,
            "current_manifest_sha256": CURRENT_MANIFEST_SHA256,
            "phase8_closeout_sha256": PHASE8_CLOSEOUT_SHA256,
            "terminal_closeout_sha256": TERMINAL_CLOSEOUT_SHA256,
            "candidate_trace_sha256": TRACE_SHA256,
        }
    if evaluation_subject_kind is not None or subject_handoff is not None:
        raise base.FoundationContractError(
            "evaluation subject arguments are only allowed for phase0-binding"
        )
    _validate_phase0_successor(ATTEMPT_ROOT)
    if mode == "phase6-gate-candidate":
        return build_phase6_gate_candidate(attempt_id=attempt_id)
    if mode in ("phase6-adopt-gate", "phase7-freeze", "phase7-finalize"):
        raise base.FoundationContractError(
            f"{mode} is forbidden before explicit live-gate approval"
        )
    result = base.run_official_mode(attempt_id=attempt_id, mode=mode)
    if mode == "phase5-disposition":
        _write_phase5_companions(ATTEMPT_ROOT)
        result = {**result, **_validate_phase5_companions(ATTEMPT_ROOT)}
    return result


def validate_official_attempt(*, attempt_id: str, requirement: str) -> dict[str, Any]:
    _require_attempt_id(attempt_id)
    root = base.official_attempt_root(attempt_id)
    if requirement in ("phase0", "phase1", "phase2", "phase3", "phase4", "phase5"):
        result = base.validate_official_attempt(
            attempt_id=attempt_id, requirement=requirement
        )
        successor = _validate_phase0_successor(root)
        if requirement == "phase5":
            result = {**result, **_validate_phase5_companions(root)}
        return {
            **result,
            "official_current_input_binding_sha256": successor["raw_sha256"],
            "g4_readiness_successor_sha256": G4_READINESS_SHA256,
            "protected_surface_mutation_count": 0,
        }
    if requirement == "gate-candidate":
        return {
            "schema_version": "public_text_quality_official_validation_result_v1",
            "status": "PASS",
            "attempt_id": ATTEMPT_ID,
            "requirement": "gate-candidate",
            "no_write": True,
            **_validate_gate_candidate(root),
        }
    if requirement == "required-gate":
        phase5 = _validate_phase5_companions(root)
        return {
            "schema_version": "public_text_quality_required_gate_result_v1",
            "status": (
                "PASS"
                if phase5["qualified_disposition"] == "accepted"
                else "QUALIFIED_DEBT"
                if phase5["qualified_disposition"] == "deferred_internal_debt"
                else "BLOCKED"
            ),
            "attempt_id": ATTEMPT_ID,
            "qualified_disposition": phase5["qualified_disposition"],
            "evaluation_subject_sha256": CANDIDATE_SHA256,
            "g4_readiness_successor_sha256": G4_READINESS_SHA256,
            "policy_closure_state": "incomplete",
            "publish_boundary_pass_claimed": False,
            "package_or_release_ready_claimed": False,
        }
    raise base.FoundationContractError(
        f"{requirement} is forbidden or incomplete before explicit live-gate approval"
    )
