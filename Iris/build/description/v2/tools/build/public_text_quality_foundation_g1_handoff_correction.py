from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import public_text_quality_foundation_implementation_correction as predecessor
import public_text_quality_foundation_rebind as foundation


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as acceptance


FoundationCorrectionError = foundation.FoundationRebindError

CORRECTION_ID = "implementation-correction-0002"
SCHEMA_VERSION = (
    "public_text_quality_foundation_g1_handoff_correction_readiness_v1"
)
START_COMMIT = "0c0424994261d12356aa745c285f7d1ca6a542a8"
START_TREE = "80ff0a3b265edf70c267f8cc43f230af42760843"
START_PARENT_COMMIT = "046b680e82089c4ee8ff5c9fb3d71f9ef1ebde0b"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
PREDECESSOR_READINESS_SHA256 = (
    "1257393ad67dbab62ae9c6159ab6b5b680cf61967aa5f212306f36986336a7b3"
)
CORRECTED_ACCEPTANCE_RAW_SHA256 = (
    "3e3fca1f2cfcfc995768d9e78f1f6d25b3daa1ec2a388ef4b954c170a5375bb5"
)
IDENTITY_TEST_RAW_SHA256 = (
    "9ed282f090916a0530a066e8e5ac2d30dd416c258e8d084d3a4a65e7f2c8c4b7"
)

FOUNDATION_ROOT = foundation.FOUNDATION_ROOT
PREDECESSOR_READINESS = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0001"
    / "public_text_quality_development_readiness_implementation_correction.json"
)
SUCCESSOR_ROOT = (
    FOUNDATION_ROOT / "readiness_successors" / CORRECTION_ID
)
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT
    / "public_text_quality_development_readiness_g1_handoff_correction.json"
)

PUBLIC_TEXT_ACCEPTANCE = TOOLS_DIR / "public_text_quality_acceptance.py"
IDENTITY_TEST = (
    V2_ROOT / "tests" / "test_public_text_constituent_identity.py"
)
PHASE8_HANDOFF = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt-0022-particle-correction-a"
    / "phase8"
    / "publish_acceptance_handoff_manifest.json"
)

CLEAN_CHECKOUT_ROOT = REPO_ROOT / "Iris" / "validation" / "clean_checkout"
GATE_MANIFEST = (
    CLEAN_CHECKOUT_ROOT
    / "evidence"
    / "full_repository_gate_manifest_successor_0002.json"
)
GATE_CLOSEOUT = (
    CLEAN_CHECKOUT_ROOT
    / "authority"
    / "full_repository_technical_debt_closeout_successor_0002.json"
)
REQUIRED_TEST_PATHS = (
    V2_ROOT / "tests" / "test_dvf_3_3_korean_prose_policy.py",
    V2_ROOT / "tests" / "test_dvf_3_3_korean_prose_candidate_route.py",
)
REQUIRED_TEST_COUNTS = {
    foundation._repo_relative(REQUIRED_TEST_PATHS[0]): 5,
    foundation._repo_relative(REQUIRED_TEST_PATHS[1]): 2,
}
INTEGRATION_ADDED_PATHS = frozenset(
    {
        foundation._repo_relative(GATE_MANIFEST),
        foundation._repo_relative(GATE_CLOSEOUT),
    }
)
CLEAN_CHECKOUT_TRACKED_PATH_COUNT = 31

IMPLEMENTATION_FILES = (
    TOOLS_DIR / "public_text_quality_foundation_g1_handoff_correction.py",
    TOOLS_DIR / "run_public_text_quality_foundation_g1_handoff_correction.py",
    TOOLS_DIR
    / "validate_public_text_quality_foundation_g1_handoff_correction.py",
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonicalize(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _blob_bytes(revision: str, relative: str) -> tuple[str, bytes]:
    blob_id = foundation._git(
        "rev-parse", f"{revision}:{relative}"
    ).stdout.strip()
    return blob_id, foundation._git_blob_bytes(blob_id)


def _index_or_head_blob(relative: str) -> str:
    staged = foundation._git("rev-parse", f":{relative}", check=False)
    if staged.returncode == 0:
        return staged.stdout.strip()
    head = foundation._git("rev-parse", f"HEAD:{relative}", check=False)
    if head.returncode != 0:
        raise FoundationCorrectionError(
            f"cannot resolve tracked correction blob: {relative}"
        )
    return head.stdout.strip()


def _tracked_record(
    path: Path,
    *,
    expected_raw_sha256: str | None = None,
) -> dict[str, Any]:
    if (
        not path.is_file()
        or not foundation._is_tracked(path)
        or foundation._is_ignored(path)
    ):
        raise FoundationCorrectionError(
            f"required tracked correction path is unavailable: {path}"
        )
    relative = foundation._repo_relative(path)
    blob_id = _index_or_head_blob(relative)
    blob_bytes = foundation._git_blob_bytes(blob_id)
    working_bytes = path.read_bytes()
    blob_raw_sha256 = _sha256(blob_bytes)
    blob_canonical_sha256 = _sha256(_canonicalize(blob_bytes))
    working_canonical_sha256 = _sha256(_canonicalize(working_bytes))
    filtered_working_blob_id = foundation._git(
        "hash-object", "--", relative
    ).stdout.strip()
    if (
        filtered_working_blob_id != blob_id
        or working_canonical_sha256 != blob_canonical_sha256
        or (
            expected_raw_sha256 is not None
            and blob_raw_sha256 != expected_raw_sha256
        )
    ):
        raise FoundationCorrectionError(
            f"tracked correction identity mismatch: {relative}"
        )
    return {
        "path": relative,
        "git_blob_id": blob_id,
        "git_blob_raw_sha256": blob_raw_sha256,
        "lf_canonical_sha256": blob_canonical_sha256,
        "working_lf_canonical_sha256": working_canonical_sha256,
        "git_filtered_working_identity": True,
        "canonical_working_identity": True,
        "tracked": True,
        "ignored": False,
    }


def _start_current_unchanged_record(path: Path) -> dict[str, Any]:
    relative = foundation._repo_relative(path)
    start_blob_id, start_bytes = _blob_bytes(START_COMMIT, relative)
    current = _tracked_record(path)
    if (
        current["git_blob_id"] != start_blob_id
        or current["git_blob_raw_sha256"] != _sha256(start_bytes)
    ):
        raise FoundationCorrectionError(
            f"start/current identity changed unexpectedly: {relative}"
        )
    return {
        **current,
        "source_commit": START_COMMIT,
        "source_tree": START_TREE,
        "start_current_git_blob_identity": True,
    }


def _validate_start_readpoint(*, require_exact_head: bool) -> dict[str, Any]:
    actual_tree = foundation._git(
        "show", "-s", "--format=%T", START_COMMIT
    ).stdout.strip()
    if actual_tree != START_TREE:
        raise FoundationCorrectionError(
            "G1 integration start commit/tree mismatch"
        )
    actual_parent = foundation._git(
        "rev-parse", f"{START_COMMIT}^"
    ).stdout.strip()
    if actual_parent != START_PARENT_COMMIT:
        raise FoundationCorrectionError(
            "G1 integration parent commit mismatch"
        )
    integration_paths = frozenset(
        line
        for line in foundation._git(
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            START_COMMIT,
        ).stdout.splitlines()
        if line
    )
    if integration_paths != INTEGRATION_ADDED_PATHS:
        raise FoundationCorrectionError(
            "G1 integration delta is not the exact two gate successor seals"
        )
    head = foundation._git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != START_COMMIT:
            raise FoundationCorrectionError(
                "successor build requires exact G1 integration HEAD"
            )
    else:
        foundation._require_ancestor(START_COMMIT, head)
    return {
        "commit": START_COMMIT,
        "tree": START_TREE,
        "parent_commit": START_PARENT_COMMIT,
        "integration_added_paths": sorted(integration_paths),
        "integration_added_path_count": len(integration_paths),
        "exact_head_required_for_build": True,
        "start_commit_is_ancestor_of_validation_head": True,
    }


def _validate_predecessor_readiness() -> dict[str, Any]:
    record = foundation._raw_tracked_record(
        PREDECESSOR_READINESS,
        PREDECESSOR_READINESS_SHA256,
    )
    readiness = foundation._load_json(PREDECESSOR_READINESS)
    if (
        readiness.get("schema_version")
        != (
            "public_text_quality_foundation_implementation_"
            "correction_readiness_v1"
        )
        or readiness.get("status") != "PASS"
        or readiness.get("correction_id") != "implementation-correction-0001"
        or readiness.get("authority_effect") != "none"
        or readiness.get("foundation_contract_semantics_changed") is not False
        or readiness.get("policy_threshold_denominator_detector_semantics_changed")
        is not False
        or readiness.get("protected_surface_mutation_count") != 0
    ):
        raise FoundationCorrectionError(
            "implementation-correction-0001 predecessor is invalid"
        )
    return {
        **record,
        "correction_id": "implementation-correction-0001",
        "append_only_successor_required": True,
        "predecessor_mutated": False,
    }


def _foundation_meaning_record(relative: str) -> dict[str, Any]:
    path = REPO_ROOT / relative
    start_blob_id, start_bytes = _blob_bytes(START_COMMIT, relative)
    if relative == foundation._repo_relative(PUBLIC_TEXT_ACCEPTANCE):
        corrected = _tracked_record(
            path,
            expected_raw_sha256=CORRECTED_ACCEPTANCE_RAW_SHA256,
        )
        if corrected["git_blob_id"] == start_blob_id:
            raise FoundationCorrectionError(
                "handoff freshness correction did not change its intended path"
            )
        return {
            "path": relative,
            "classification": (
                "intended_crlf_independent_text_constituent_freshness_correction"
            ),
            "start_git_blob_id": start_blob_id,
            "start_git_blob_raw_sha256": _sha256(start_bytes),
            "corrected_git_blob_id": corrected["git_blob_id"],
            "corrected_git_blob_raw_sha256": corrected[
                "git_blob_raw_sha256"
            ],
            "corrected_lf_canonical_sha256": corrected[
                "lf_canonical_sha256"
            ],
            "current_filtered_and_canonical_identity": True,
            "policy_threshold_denominator_detector_change_count": 0,
        }
    current = _start_current_unchanged_record(path)
    return {
        "path": relative,
        "classification": "byte_identical_unchanged_foundation_meaning",
        "git_blob_id": current["git_blob_id"],
        "git_blob_raw_sha256": current["git_blob_raw_sha256"],
        "start_current_git_blob_identity": True,
    }


def _validate_foundation_semantics() -> dict[str, Any]:
    contract = foundation._raw_tracked_record(
        foundation.FOUNDATION_CONTRACT,
        FOUNDATION_CONTRACT_SHA256,
    )
    records = [
        _foundation_meaning_record(relative)
        for relative in foundation.FOUNDATION_MEANING_PATHS
    ]
    intended = [
        row for row in records if row["classification"].startswith("intended_")
    ]
    unchanged = [
        row
        for row in records
        if row["classification"]
        == "byte_identical_unchanged_foundation_meaning"
    ]
    if len(records) != 17 or len(intended) != 1 or len(unchanged) != 16:
        raise FoundationCorrectionError(
            "Foundation meaning path census is not exact"
        )
    return {
        "foundation_contract": contract,
        "meaning_path_count": 17,
        "unchanged_meaning_path_count": 16,
        "intended_implementation_correction_path_count": 1,
        "unexpected_meaning_path_change_count": 0,
        "meaning_paths": records,
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "candidate_or_handoff_semantics_changed": False,
    }


def _clean_checkout_tracked_paths_at_start() -> list[str]:
    prefix = foundation._repo_relative(CLEAN_CHECKOUT_ROOT)
    paths = [
        line
        for line in foundation._git(
            "ls-tree",
            "-r",
            "--name-only",
            START_COMMIT,
            "--",
            prefix,
        ).stdout.splitlines()
        if line
    ]
    current = [
        line
        for line in foundation._git(
            "ls-files", "--", prefix
        ).stdout.splitlines()
        if line
    ]
    if (
        len(paths) != CLEAN_CHECKOUT_TRACKED_PATH_COUNT
        or paths != current
        or len(set(paths)) != len(paths)
    ):
        raise FoundationCorrectionError(
            "current clean-checkout tracked gate census changed"
        )
    return paths


def _validate_clean_checkout_gate() -> dict[str, Any]:
    tracked_paths = _clean_checkout_tracked_paths_at_start()
    rows = [
        _start_current_unchanged_record(REPO_ROOT / relative)
        for relative in tracked_paths
    ]
    gate_record = next(
        row
        for row in rows
        if row["path"] == foundation._repo_relative(GATE_MANIFEST)
    )
    closeout_record = next(
        row
        for row in rows
        if row["path"] == foundation._repo_relative(GATE_CLOSEOUT)
    )
    gate = foundation._load_json(GATE_MANIFEST)
    closeout = foundation._load_json(GATE_CLOSEOUT)
    required_tests = [
        _start_current_unchanged_record(path)
        for path in REQUIRED_TEST_PATHS
    ]
    test_ports = gate.get("required_test_ports", {})
    policy = test_ports.get("policy", {})
    candidate_route = test_ports.get("candidate_route", {})
    if (
        gate.get("schema_version")
        != "iris-clean-checkout-full-repository-gate-manifest-v2"
        or gate.get("manifest_state") != "frozen"
        or gate.get("status") != "PASS"
        or gate.get("claim_boundary", {}).get(
            "full_required_repository_clean_checkout_reproducibility"
        )
        != "PASS"
        or gate.get("claim_boundary", {}).get("publish_return_allowed")
        is not False
        or gate.get("execution_reproducibility", {}).get(
            "required_execution_unit_count"
        )
        != 177
        or gate.get("execution_reproducibility", {}).get(
            "passed_execution_unit_count"
        )
        != 177
        or policy.get("path")
        != foundation._repo_relative(REQUIRED_TEST_PATHS[0])
        or policy.get("test_count") != 5
        or policy.get("passed_test_count") != 5
        or policy.get("status") != "PASS"
        or policy.get("historical_blob_id")
        != required_tests[0]["git_blob_id"]
        or policy.get("current_blob_id")
        != required_tests[0]["git_blob_id"]
        or candidate_route.get("path")
        != foundation._repo_relative(REQUIRED_TEST_PATHS[1])
        or candidate_route.get("test_count") != 2
        or candidate_route.get("passed_test_count") != 2
        or candidate_route.get("status") != "PASS"
        or candidate_route.get("historical_blob_id")
        != required_tests[1]["git_blob_id"]
        or candidate_route.get("current_blob_id")
        != required_tests[1]["git_blob_id"]
        or closeout.get("schema_version")
        != (
            "iris_clean_checkout_full_repository_technical_debt_"
            "closeout_successor_v2"
        )
        or closeout.get("status")
        != "integration_complete_downstream_freshness_blocked"
        or closeout.get("technical_gate", {}).get("status") != "PASS"
        or closeout.get("freshness_disposition", {}).get(
            "publish_return_allowed"
        )
        is not False
        or closeout.get("lineage_preservation", {}).get(
            "official_attempt_0004_consumed"
        )
        is not False
        or closeout.get("successor_boundary", {}).get(
            "tests_rerun_for_this_successor_record"
        )
        is not False
    ):
        raise FoundationCorrectionError(
            "current clean-checkout gate or seven required tests are invalid"
        )
    if sum(REQUIRED_TEST_COUNTS.values()) != 7:
        raise FoundationCorrectionError("required G1 test count is not seven")
    return {
        "status": "PASS",
        "source_integration_commit": START_COMMIT,
        "source_integration_tree": START_TREE,
        "tracked_gate_surface_count": len(rows),
        "tracked_gate_surface": rows,
        "tracked_gate_surface_aggregate_sha256": foundation._canonical_hash(
            rows
        ),
        "gate_manifest": gate_record,
        "gate_closeout": closeout_record,
        "required_test_source_count": len(required_tests),
        "required_test_case_count": 7,
        "required_test_case_breakdown": REQUIRED_TEST_COUNTS,
        "required_test_sources": required_tests,
        "required_execution_unit_count": 177,
        "passed_execution_unit_count": 177,
        "publish_return_allowed": False,
    }


def _text_identity_probes() -> dict[str, Any]:
    blob = b"alpha\nbeta\n"
    declared = _sha256(blob.replace(b"\n", b"\r\n"))
    variants = {
        "lf": blob,
        "crlf": blob.replace(b"\n", b"\r\n"),
        "lone_cr": blob.replace(b"\n", b"\r"),
    }
    variant_rows = {
        name: acceptance.build_text_constituent_identity_from_bytes(
            repo_relative_posix_path="Iris/example/constituent.json",
            declared_sha256=declared,
            head_blob_id="1" * 40,
            head_blob_raw=blob,
            working_raw=raw,
            filtered_working_blob_id="2" * 40,
        )
        for name, raw in variants.items()
    }
    if not all(row["match"] for row in variant_rows.values()):
        raise FoundationCorrectionError(
            "text constituent line-ending metamorphic probe failed"
        )
    changed = acceptance.build_text_constituent_identity_from_bytes(
        repo_relative_posix_path="Iris/example/constituent.json",
        declared_sha256=_sha256(blob),
        head_blob_id="1" * 40,
        head_blob_raw=blob,
        working_raw=b"alpha\nBeta\n",
        filtered_working_blob_id="2" * 40,
    )
    if changed["match"]:
        raise FoundationCorrectionError(
            "text constituent one-byte semantic change did not become stale"
        )
    first_location = acceptance.build_text_constituent_identity_from_bytes(
        repo_relative_posix_path="Iris/example/constituent.json",
        declared_sha256=declared,
        head_blob_id="1" * 40,
        head_blob_raw=blob,
        working_raw=blob,
        filtered_working_blob_id="2" * 40,
    )
    second_location = acceptance.build_text_constituent_identity_from_bytes(
        repo_relative_posix_path="Iris/example/constituent.json",
        declared_sha256=declared,
        head_blob_id="1" * 40,
        head_blob_raw=blob,
        working_raw=blob.replace(b"\n", b"\r\n"),
        filtered_working_blob_id="2" * 40,
    )
    if first_location != second_location:
        raise FoundationCorrectionError(
            "text constituent identity depends on checkout representation"
        )
    return {
        "algorithm_id": acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID,
        "authority_hash_source": "HEAD_git_blob_raw",
        "working_identity_modes": [
            "git_filtered_identity",
            "crlf_and_lone_cr_to_lf_canonical_identity",
        ],
        "json_semantic_normalization_applied": False,
        "line_ending_metamorphic": {
            "status": "PASS",
            "variant_count": 3,
            "all_variants_fresh": True,
            "authority_git_blob_raw_sha256": _sha256(blob),
        },
        "semantic_one_byte_change": {
            "status": "PASS",
            "changed_byte_count": 1,
            "stale": True,
            "changed_working_lf_canonical_sha256": changed[
                "working_lf_canonical_sha256"
            ],
        },
        "checkout_location_independence": {
            "status": "PASS",
            "identity_equal": True,
            "absolute_path_or_host_metadata_in_identity": False,
        },
    }


def _validate_handoff_freshness_correction() -> dict[str, Any]:
    acceptance_record = _tracked_record(
        PUBLIC_TEXT_ACCEPTANCE,
        expected_raw_sha256=CORRECTED_ACCEPTANCE_RAW_SHA256,
    )
    test_record = _tracked_record(
        IDENTITY_TEST,
        expected_raw_sha256=IDENTITY_TEST_RAW_SHA256,
    )
    handoff_record = _start_current_unchanged_record(PHASE8_HANDOFF)
    if (
        acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        != (
            "git_head_blob_raw_sha256_with_filtered_or_"
            "lf_canonical_working_v1"
        )
        or len(acceptance.TEXT_HANDOFF_CONSTITUENT_IDS) != 13
    ):
        raise FoundationCorrectionError(
            "text constituent identity implementation contract is invalid"
        )
    return {
        "public_text_quality_acceptance": acceptance_record,
        "regression_test": test_record,
        "existing_phase8_handoff": handoff_record,
        "existing_phase8_handoff_modified": False,
        "text_constituent_count": 13,
        "identity_probes": _text_identity_probes(),
    }


def _protected_paths() -> list[Path]:
    protected = set(predecessor._protected_paths())
    protected.add(PREDECESSOR_READINESS)
    protected.update(REPO_ROOT / path for path in _clean_checkout_tracked_paths_at_start())
    protected.update(REQUIRED_TEST_PATHS)
    protected.update(
        {
            PUBLIC_TEXT_ACCEPTANCE,
            IDENTITY_TEST,
            PHASE8_HANDOFF,
            REPO_ROOT / ".gitignore",
            REPO_ROOT / ".gitattributes",
            *IMPLEMENTATION_FILES,
        }
    )
    protected.discard(SUCCESSOR_PATH)
    return sorted(protected, key=foundation._repo_relative)


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_paths():
        present = path.is_file()
        rows.append(
            {
                "path": foundation._repo_relative(path),
                "present": present,
                "raw_sha256": (
                    foundation._sha256_file(path) if present else None
                ),
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": (
            "public_text_quality_foundation_g1_handoff_"
            "correction_no_write_snapshot_v1"
        ),
        "surface_count": len(rows),
        "surface_hash": foundation._canonical_hash(rows),
        "surfaces": rows,
    }


def _no_write_guard(
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before["surfaces"]}
    after_rows = {row["path"]: row for row in after["surfaces"]}
    changed = sorted(
        path
        for path in set(before_rows) | set(after_rows)
        if before_rows.get(path) != after_rows.get(path)
    )
    if changed:
        raise FoundationCorrectionError(
            f"protected correction surface changed: {changed}"
        )
    return {
        "schema_version": (
            "public_text_quality_foundation_g1_handoff_"
            "correction_no_write_guard_v1"
        ),
        "status": "PASS",
        "before_snapshot_hash": foundation._canonical_hash(before),
        "after_snapshot_hash": foundation._canonical_hash(after),
        "protected_surface_mutation_count": 0,
        "changed_paths": [],
        "authority_effect": "none",
    }


def _implementation_hashes() -> list[dict[str, Any]]:
    rows = []
    for path in IMPLEMENTATION_FILES:
        if not path.is_file():
            raise FoundationCorrectionError(
                f"correction implementation file is missing: {path}"
            )
        rows.append(
            {
                "path": foundation._repo_relative(path),
                "hash_algorithm": "sha256_utf8_lf_normalized_v1",
                "sha256": foundation._sha256_lf(path),
            }
        )
    return rows


def build_successor_projection(
    *,
    require_exact_start_head: bool,
    no_write_guard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_kind": (
            "append_only_foundation_implementation_and_readiness_correction"
        ),
        "purpose": (
            "Bind the G1-current clean-checkout gate and seven required tests "
            "into the protected Foundation surface while making text "
            "constituent freshness independent of Windows line endings."
        ),
        "execution_start_readpoint": _validate_start_readpoint(
            require_exact_head=require_exact_start_head
        ),
        "predecessor_readiness": _validate_predecessor_readiness(),
        "foundation_semantics": _validate_foundation_semantics(),
        "g1_current_clean_checkout_gate": _validate_clean_checkout_gate(),
        "handoff_text_constituent_freshness": (
            _validate_handoff_freshness_correction()
        ),
        "successor_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "scope_boundaries": {
            "foundation_contract_modified": False,
            "policy_threshold_denominator_detector_modified": False,
            "candidate_modified": False,
            "phase8_handoff_modified": False,
            "naturalization_attempt_created_or_executed": False,
            "official_attempt_0004_created_or_executed": False,
            "live_gate_modified": False,
            "runtime_lua_package_modified": False,
            "new_worktree_or_repository_copy_created": False,
        },
        "foundation_contract_semantics_changed": False,
        "policy_threshold_denominator_detector_semantics_changed": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "next_stage": "fresh_naturalization_attempt_phase0",
    }


def _validate_correction_id(correction_id: str) -> None:
    if correction_id != CORRECTION_ID:
        raise FoundationCorrectionError(
            f"only the exact correction ID {CORRECTION_ID} is allowed"
        )


def build_successor(correction_id: str) -> dict[str, Any]:
    _validate_correction_id(correction_id)
    if SUCCESSOR_PATH.exists():
        raise FoundationCorrectionError(
            "append-only G1/handoff readiness successor already exists"
        )
    protected_before = protected_snapshot()
    guard = _no_write_guard(protected_before, protected_snapshot())
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(foundation._pretty_json_bytes(successor))
    _no_write_guard(protected_before, protected_snapshot())
    return {
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_successor_path": foundation._repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": foundation._sha256_file(
            SUCCESSOR_PATH
        ),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": PREDECESSOR_READINESS_SHA256,
        "clean_checkout_gate_path_count": CLEAN_CHECKOUT_TRACKED_PATH_COUNT,
        "required_test_case_count": 7,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
    }


def _require_successor_vcs_state() -> dict[str, Any]:
    if (
        not SUCCESSOR_PATH.is_file()
        or not foundation._is_tracked(SUCCESSOR_PATH)
        or foundation._is_ignored(SUCCESSOR_PATH)
    ):
        raise FoundationCorrectionError(
            "G1/handoff readiness successor must be tracked and unignored"
        )
    relative = foundation._repo_relative(SUCCESSOR_PATH)
    blob_id = _index_or_head_blob(relative)
    working_raw_blob_id = foundation._git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    if blob_id != working_raw_blob_id:
        raise FoundationCorrectionError(
            "successor staged/working raw-byte identity mismatch"
        )
    attr = foundation._git(
        "check-attr", "text", "--", relative
    ).stdout.strip()
    if not attr.endswith(": text: unset"):
        raise FoundationCorrectionError(
            "G1/handoff successor requires exact -text"
        )
    return {
        "tracked": True,
        "ignored": False,
        "text_attribute": "unset",
        "git_blob_id": blob_id,
        "working_raw_blob_id": working_raw_blob_id,
        "git_blob_working_byte_identity": True,
    }


def validate_successor(correction_id: str) -> dict[str, Any]:
    _validate_correction_id(correction_id)
    if not SUCCESSOR_PATH.is_file():
        raise FoundationCorrectionError(
            "G1/handoff readiness successor is missing"
        )
    successor_bytes_before = SUCCESSOR_PATH.read_bytes()
    successor = foundation._load_json(SUCCESSOR_PATH)
    protected_before = protected_snapshot()
    guard = _no_write_guard(protected_before, protected_snapshot())
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationCorrectionError(
            "G1/handoff readiness successor differs from exact projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes_before:
        raise FoundationCorrectionError(
            "no-write validator changed successor bytes"
        )
    _no_write_guard(protected_before, protected_snapshot())
    return {
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_successor_path": foundation._repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": foundation._sha256_file(
            SUCCESSOR_PATH
        ),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": PREDECESSOR_READINESS_SHA256,
        "clean_checkout_gate_path_count": CLEAN_CHECKOUT_TRACKED_PATH_COUNT,
        "required_test_case_count": 7,
        "text_constituent_identity_algorithm_id": (
            acceptance.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
        ),
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
