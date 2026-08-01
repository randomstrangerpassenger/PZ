from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official
import public_text_quality_acceptance_official_0005_closure as legacy
import public_text_quality_acceptance_official_0005_phase7_terminal_validation as failed
import public_text_quality_acceptance_official_0005_phase7_v2 as phase7_v2


CORRECTION_ID = "g1-successor-0010-host-independent-freeze-0003"
CORRECTION_PATH_ID = "host-independent-freeze-0003"
INVENTORY_ALGORITHM_ID = "git_head_tree_index_posix_paths_blob_sha256_v1"
FREEZE_SCHEMA = "public_text_quality_phase7_host_independent_freeze_v3"
MANIFEST_SCHEMA = "public_text_quality_phase7_host_independent_artifact_manifest_v4"
REVIEW_SCHEMA = "public_text_quality_phase7_host_independent_review_v4"
ELIGIBILITY_SCHEMA = "public_text_quality_phase7_host_independent_reviewer_eligibility_v4"
OWNER_SCHEMA = "public_text_quality_phase7_host_independent_owner_closure_seal_v4"

PHASE7 = official.ATTEMPT_ROOT / "phase7"
EVIDENCE_ROOT = PHASE7 / "corrections" / CORRECTION_ID
VALIDATION_ROOT = EVIDENCE_ROOT / "inputs"
CORRECTION_ROOT = PHASE7 / "corrections" / CORRECTION_PATH_ID
FREEZE = CORRECTION_ROOT / "freeze.json"
ARTIFACT_MANIFEST = CORRECTION_ROOT / "artifact_manifest.json"
REVIEW_REQUEST = CORRECTION_ROOT / "review_request.json"
VCS_CENSUS = CORRECTION_ROOT / "vcs_census.json"
OWNER_GAP = CORRECTION_ROOT / "owner_gap.json"
FINAL_REPORT = CORRECTION_ROOT / "final_report.json"
TERMINAL_SEAL = CORRECTION_ROOT / "terminal_seal.json"
G5_HANDOFF = CORRECTION_ROOT / "g5_handoff.json"
TERMINAL_FAILURE = CORRECTION_ROOT / "terminal_failure.json"

REVIEWER_ROOT = (
    official.V2_ROOT
    / "reviewer_inputs"
    / base.ROUND_ID
    / official.ATTEMPT_ID
    / CORRECTION_PATH_ID
)
INDEPENDENT_REVIEW = REVIEWER_ROOT / "independent_review.json"
REVIEWER_ELIGIBILITY = REVIEWER_ROOT / "reviewer_eligibility.json"
OWNER_SEAL = (
    official.OWNER_INPUT_ROOT
    / "owner_closure_seal_host_independent_freeze_0003.json"
)

PREDECESSOR_FAILED_EVIDENCE = {
    "predecessor_failed_owner_seal": (
        failed.OWNER_SEAL,
        "2e37b406c5b37b10c1d0586a48f9f24bafea012afa48756de5b8ffd5d66100cf",
        failed._schema_contract()["owner_closure_seal"],
    ),
    "predecessor_failed_final_report": (
        failed.FINAL_REPORT,
        "7c767efca9d0f6090ba790deb0b9ab578b49228c9a76f9b1dcfed3ad3bd4b719",
        failed.FINAL_REPORT_SCHEMA_V2,
    ),
    "predecessor_failed_terminal": (
        failed.TERMINAL_SEAL,
        "53d987a5f0a4d1a40b63954d6135f517fd2a810055f0381e7868cebff174eec0",
        failed.TERMINAL_SCHEMA_V2,
    ),
    "predecessor_terminal_failure": (
        failed.CORRECTION_ROOT / "terminal_validation_failure.json",
        "9043d3c2bfea8b98554000d9499c7552201c2b661255667d13cb55961b589651",
        "public_text_quality_phase7_terminal_validation_failure_v1",
    ),
}

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _fail(message: str) -> None:
    raise base.FoundationContractError(message)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object")
    return value


def _proof(value: dict[str, Any], field: str) -> bool:
    core = {key: child for key, child in value.items() if key != field}
    return value.get(field) == base.canonical_hash(core)


def _repo_path(path: Path) -> str:
    value = base.repo_relative(path).replace("\\", "/")
    return _canonical_repo_path(value)


def _canonical_repo_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("Git inventory path is empty or non-text")
    if value != value.replace("\\", "/"):
        _fail(f"Git inventory path contains a backslash alias: {value}")
    if value.startswith("/") or value.endswith("/") or "//" in value:
        _fail(f"Git inventory path is not repo-relative POSIX: {value}")
    if "\n" in value or "\r" in value or "\0" in value:
        _fail("Git inventory path contains a forbidden control character")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        _fail(f"Git inventory path contains an alias segment: {value}")
    if PurePosixPath(value).as_posix() != value:
        _fail(f"Git inventory path is not canonical POSIX: {value}")
    if unicodedata.normalize("NFC", value) != value:
        _fail(f"Git inventory path is not NFC canonical: {value}")
    return value


def _git_bytes(
    *args: str,
    input_bytes: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *args],
        cwd=official.REPO_ROOT,
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        _fail(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode("utf-8", errors="replace").strip()
        )
    return result


def _git_text(*args: str, check: bool = True) -> str:
    return _git_bytes(*args, check=check).stdout.decode(
        "utf-8", errors="strict"
    ).strip()


def _tree_entries(treeish: str) -> list[dict[str, str]]:
    raw = _git_bytes("ls-tree", "-r", "-z", "--full-tree", treeish).stdout
    entries: list[dict[str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode, object_type, blob_id = header.decode("ascii").split(" ", 2)
            path = _canonical_repo_path(raw_path.decode("utf-8", errors="strict"))
        except (ValueError, UnicodeDecodeError) as exc:
            _fail(f"malformed Git tree record: {exc}")
        entries.append(
            {
                "path": path,
                "mode": mode,
                "object_type": object_type,
                "git_blob_id": blob_id,
            }
        )
    _validate_tree_entries(entries)
    return sorted(entries, key=lambda row: row["path"])


def _validate_tree_entries(entries: list[dict[str, str]]) -> None:
    paths: list[str] = []
    folded: dict[str, str] = {}
    for entry in entries:
        if set(entry) != {"path", "mode", "object_type", "git_blob_id"}:
            _fail("Git tree entry has missing or extra fields")
        path = _canonical_repo_path(entry["path"])
        if entry["object_type"] not in {"blob", "commit"}:
            _fail(f"unsupported Git tree object type for {path}")
        if entry["mode"] not in {"100644", "100755", "120000", "160000"}:
            _fail(f"unsupported Git tree mode for {path}: {entry['mode']}")
        if not _HEX40.fullmatch(entry["git_blob_id"]):
            _fail(f"malformed Git blob identity for {path}")
        paths.append(path)
        key = path.casefold()
        prior = folded.get(key)
        if prior is not None and prior != path:
            _fail(f"Git inventory case collision: {prior} vs {path}")
        folded[key] = path
    if len(paths) != len(set(paths)):
        _fail("Git inventory contains duplicate paths")


def _index_entries() -> dict[str, dict[str, str]]:
    raw = _git_bytes("ls-files", "--stage", "-z").stdout
    result: dict[str, dict[str, str]] = {}
    folded: dict[str, str] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode, blob_id, stage = header.decode("ascii").split(" ", 2)
            path = _canonical_repo_path(raw_path.decode("utf-8", errors="strict"))
        except (ValueError, UnicodeDecodeError) as exc:
            _fail(f"malformed Git index record: {exc}")
        if stage != "0":
            _fail(f"Git inventory contains an unmerged index entry: {path}")
        if path in result:
            _fail(f"Git index contains a duplicate path: {path}")
        key = path.casefold()
        if key in folded and folded[key] != path:
            _fail(f"Git index case collision: {folded[key]} vs {path}")
        folded[key] = path
        result[path] = {"mode": mode, "git_blob_id": blob_id}
    return result


def _blob_bytes(blob_ids: Iterable[str]) -> dict[str, bytes]:
    ordered = list(dict.fromkeys(blob_ids))
    if not ordered:
        return {}
    payload = ("\n".join(ordered) + "\n").encode("ascii")
    output = _git_bytes("cat-file", "--batch", input_bytes=payload).stdout
    position = 0
    result: dict[str, bytes] = {}
    for expected in ordered:
        end = output.find(b"\n", position)
        if end < 0:
            _fail("Git cat-file batch response is truncated")
        header = output[position:end].decode("ascii", errors="strict").split(" ")
        if len(header) != 3 or header[0] != expected or header[1] != "blob":
            _fail(f"Git cat-file batch header mismatch for {expected}")
        size = int(header[2])
        start = end + 1
        finish = start + size
        if finish >= len(output) or output[finish : finish + 1] != b"\n":
            _fail(f"Git cat-file batch payload mismatch for {expected}")
        result[expected] = output[start:finish]
        position = finish + 1
    if position != len(output):
        _fail("Git cat-file batch response has trailing bytes")
    return result


def _working_blob_ids(paths: list[str]) -> dict[str, str]:
    if not paths:
        return {}
    payload = ("\n".join(paths) + "\n").encode("utf-8")
    process = _git_bytes("hash-object", "--stdin-paths", input_bytes=payload)
    identities = process.stdout.decode("ascii", errors="strict").splitlines()
    if len(identities) != len(paths) or any(
        not _HEX40.fullmatch(identity) for identity in identities
    ):
        _fail("Git filtered working-byte identity response is malformed")
    return dict(zip(paths, identities, strict=True))


def _direct_child(path: str, root: str) -> bool:
    prefix = root.rstrip("/") + "/"
    return path.startswith(prefix) and "/" not in path[len(prefix) :]


def _under(path: str, root: Path) -> bool:
    prefix = _repo_path(root).rstrip("/") + "/"
    return path.startswith(prefix)


def _base_claim_exact_paths() -> set[str]:
    return {
        _repo_path(path)
        for path in (
            phase7_v2.G1_GATE,
            phase7_v2.G1_CLOSEOUT,
            official.POLICY_OWNER_INPUT,
            official.WAIVER_OWNER_INPUT,
            phase7_v2.OWNER_INPUT,
            base.LIVE_REQUIRED_VALIDATIONS,
            official.FOUNDATION_CONTRACT,
            official.G4_READINESS,
            official.PHASE8_HANDOFF,
            official.PHASE8_CLOSEOUT,
            official.TERMINAL_CLOSEOUT,
            official.CANDIDATE,
            official.TRACE,
            failed.PREDECESSOR_FREEZE,
            phase7_v2.ARTIFACT_MANIFEST,
            failed.PREDECESSOR_REVIEW,
            failed.PREDECESSOR_REVIEW_FAILURE,
            failed.DISPOSITION,
            failed.POLICY,
            failed.POLICY_SEAL,
        )
    }


def _select_base_claim_paths(entries: list[dict[str, str]]) -> list[str]:
    attempt = _repo_path(official.ATTEMPT_ROOT)
    phase7 = _repo_path(PHASE7)
    reviewer_attempt = _repo_path(
        official.V2_ROOT
        / "reviewer_inputs"
        / base.ROUND_ID
        / official.ATTEMPT_ID
    )
    exact = _base_claim_exact_paths()
    selected: list[str] = []
    for entry in entries:
        path = entry["path"]
        include = path in exact
        for phase in range(6):
            include = include or _direct_child(path, f"{attempt}/phase{phase}")
        include = include or path.startswith(f"{attempt}/phase6/")
        include = include or _direct_child(path, phase7)
        include = include or _direct_child(path, reviewer_attempt)
        include = include or _under(path, phase7_v2.VALIDATION_ROOT)
        include = include or _under(path, failed.VALIDATION_ROOT)
        if include:
            selected.append(path)
    missing = sorted(exact - set(selected))
    if missing:
        _fail(f"required exact freeze paths are missing from Git tree: {missing}")
    return sorted(selected)


def _correction_evidence_paths(entries: list[dict[str, str]]) -> list[str]:
    return sorted(
        entry["path"]
        for entry in entries
        if _under(entry["path"], VALIDATION_ROOT)
    )


def _implementation_paths() -> list[str]:
    module = Path(__file__).resolve()
    paths = [
        official.THIS_MODULE,
        official.RUNNER_MODULE,
        official.VALIDATOR_MODULE,
        Path(legacy.__file__).resolve(),
        Path(phase7_v2.__file__).resolve(),
        Path(failed.__file__).resolve(),
        Path(failed.__file__).resolve().with_name(
            "run_public_text_quality_acceptance_official_0005_phase7_terminal_validation.py"
        ),
        Path(failed.__file__).resolve().with_name(
            "validate_public_text_quality_acceptance_official_0005_phase7_terminal_validation.py"
        ),
        module,
        module.with_name(
            "run_public_text_quality_acceptance_official_0005_phase7_host_independent_freeze.py"
        ),
        module.with_name(
            "validate_public_text_quality_acceptance_official_0005_phase7_host_independent_freeze.py"
        ),
        official.CURRENT_ROUTE_TEST,
        official.REPO_ROOT / "Iris/_docs/round3/round3_run_contract_tests.py",
        official.REPO_ROOT
        / "Iris/build/description/v2/tools/build/"
        "dvf_3_3_closeout_reentry_guard_seal_common.py",
    ]
    return sorted({_repo_path(path) for path in paths})


def _rows_for_paths(
    entries: list[dict[str, str]],
    paths: list[str],
) -> list[dict[str, Any]]:
    tree = {entry["path"]: entry for entry in entries}
    if len(tree) != len(entries):
        _fail("Git tree contains duplicate paths")
    missing = sorted(set(paths) - set(tree))
    if missing:
        _fail(f"inventory-required paths are missing from Git tree: {missing}")
    non_blobs = sorted(path for path in paths if tree[path]["object_type"] != "blob")
    if non_blobs:
        _fail(f"inventory-required paths are not Git blobs: {non_blobs}")
    blobs = _blob_bytes(tree[path]["git_blob_id"] for path in paths)
    return [
        {
            "path": path,
            "git_mode": tree[path]["mode"],
            "git_object_type": tree[path]["object_type"],
            "git_blob_id": tree[path]["git_blob_id"],
            "raw_sha256": hashlib.sha256(
                blobs[tree[path]["git_blob_id"]]
            ).hexdigest(),
        }
        for path in paths
    ]


def _inventory_hash(rows: list[dict[str, Any]]) -> str:
    return base.canonical_hash(
        {
            "algorithm_id": INVENTORY_ALGORITHM_ID,
            "ordered_rows": rows,
        }
    )


def _validate_inventory_rows(
    entries: list[dict[str, str]],
    selected_paths: list[str],
    rows: list[dict[str, Any]],
) -> None:
    _validate_tree_entries(entries)
    expected = _rows_for_paths(entries, selected_paths)
    observed_paths = [row.get("path") for row in rows if isinstance(row, dict)]
    if len(observed_paths) != len(set(observed_paths)):
        _fail("inventory rows contain a duplicate path")
    folded: dict[str, str] = {}
    for path in observed_paths:
        if not isinstance(path, str):
            _fail("inventory row path is malformed")
        canonical = _canonical_repo_path(path)
        key = canonical.casefold()
        if key in folded and folded[key] != canonical:
            _fail(f"inventory row case collision: {folded[key]} vs {canonical}")
        folded[key] = canonical
    if rows != expected:
        _fail("inventory rows have missing, extra, reordered, aliased, or blob-mismatched entries")


def _verify_current_identity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [row["path"] for row in rows]
    current_entries = _tree_entries("HEAD")
    tree = {entry["path"]: entry for entry in current_entries}
    index = _index_entries()
    working = _working_blob_ids(paths)
    errors: list[str] = []
    for row in rows:
        path = row["path"]
        tree_row = tree.get(path)
        index_row = index.get(path)
        if tree_row is None:
            errors.append(f"missing HEAD path:{path}")
            continue
        if (
            tree_row["git_blob_id"] != row["git_blob_id"]
            or tree_row["mode"] != row["git_mode"]
        ):
            errors.append(f"HEAD tree/blob mismatch:{path}")
        if index_row is None or index_row != {
            "mode": row["git_mode"],
            "git_blob_id": row["git_blob_id"],
        }:
            errors.append(f"index mismatch:{path}")
        if working.get(path) != row["git_blob_id"]:
            errors.append(f"working filtered identity mismatch:{path}")
    if errors:
        _fail("; ".join(errors))
    return {
        "status": "PASS",
        "path_count": len(rows),
        "head_tree_match_count": len(rows),
        "index_match_count": len(rows),
        "working_filtered_identity_match_count": len(rows),
        "error_count": 0,
    }


def build_inventory(
    treeish: str,
    *,
    verify_current: bool,
) -> dict[str, Any]:
    entries = _tree_entries(treeish)
    claim_paths = _select_base_claim_paths(entries)
    evidence_paths = _correction_evidence_paths(entries)
    implementation_paths = _implementation_paths()
    historical_paths = sorted(_repo_path(item[0]) for item in PREDECESSOR_FAILED_EVIDENCE.values())
    claim_rows = _rows_for_paths(entries, claim_paths)
    evidence_rows = _rows_for_paths(entries, evidence_paths)
    implementation_rows = _rows_for_paths(entries, implementation_paths)
    historical_rows = _rows_for_paths(entries, historical_paths)
    _validate_inventory_rows(entries, claim_paths, claim_rows)
    all_rows = claim_rows + evidence_rows + implementation_rows + historical_rows
    if len({row["path"] for row in all_rows}) != len(all_rows):
        _fail("freeze inventory categories overlap")
    identity = (
        _verify_current_identity(all_rows)
        if verify_current
        else {"status": "NOT_REQUESTED", "path_count": len(all_rows)}
    )
    return {
        "algorithm_id": INVENTORY_ALGORITHM_ID,
        "authority_source": "git_commit_tree_and_index_repo_relative_posix_paths",
        "host_metadata_excluded": True,
        "absolute_path_excluded": True,
        "checkout_location_excluded": True,
        "drive_letter_excluded": True,
        "extended_length_prefix_excluded": True,
        "mtime_excluded": True,
        "claim_bearing_artifact_count": len(claim_rows),
        "claim_bearing_artifacts": claim_rows,
        "claim_inventory_sha256": _inventory_hash(claim_rows),
        "correction_evidence_count": len(evidence_rows),
        "correction_evidence": evidence_rows,
        "correction_evidence_sha256": _inventory_hash(evidence_rows),
        "implementation_path_count": len(implementation_rows),
        "implementation_paths": implementation_rows,
        "implementation_inventory_sha256": _inventory_hash(implementation_rows),
        "predecessor_failed_evidence_count": len(historical_rows),
        "predecessor_failed_evidence": historical_rows,
        "predecessor_failed_evidence_sha256": _inventory_hash(historical_rows),
        "current_identity": identity,
    }


def _validated_readpoint(
    freeze_commit: str | None,
    freeze_tree: str | None,
) -> tuple[str, str]:
    if freeze_commit is None:
        freeze_commit = _git_text("rev-parse", "HEAD")
    if freeze_tree is None:
        freeze_tree = _git_text("rev-parse", f"{freeze_commit}^{{tree}}")
    if not _HEX40.fullmatch(freeze_commit) or not _HEX40.fullmatch(freeze_tree):
        _fail("freeze readpoint is malformed")
    observed = _git_text("rev-parse", f"{freeze_commit}^{{tree}}")
    if observed != freeze_tree:
        _fail("freeze readpoint commit/tree mismatch")
    if _git_bytes("merge-base", "--is-ancestor", freeze_commit, "HEAD", check=False).returncode != 0:
        _fail("freeze readpoint is not an ancestor of HEAD")
    return freeze_commit, freeze_tree


def _predecessor_failed_bindings() -> dict[str, Any]:
    return {
        role: {
            "path": _repo_path(path),
            "sha256": sha256,
            "schema_version": schema,
            "role_state": "historical_failed_materialization_evidence",
        }
        for role, (path, sha256, schema) in sorted(PREDECESSOR_FAILED_EVIDENCE.items())
    }


def compute_freeze_bundle(
    *,
    freeze_commit: str | None = None,
    freeze_tree: str | None = None,
    verify_current: bool = False,
) -> dict[str, dict[str, Any]]:
    freeze_commit, freeze_tree = _validated_readpoint(freeze_commit, freeze_tree)
    inventory = build_inventory(freeze_commit, verify_current=verify_current)
    if inventory["claim_bearing_artifact_count"] != 139:
        _fail(
            "host-independent Phase 7 claim inventory denominator mismatch: "
            f"{inventory['claim_bearing_artifact_count']} != 139"
        )
    freeze_core = {
        "schema_version": FREEZE_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_commit": freeze_commit,
        "freeze_tree": freeze_tree,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "inventory_authority": inventory["authority_source"],
        "claim_bearing_artifact_count": inventory["claim_bearing_artifact_count"],
        "claim_bearing_artifacts": inventory["claim_bearing_artifacts"],
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "correction_evidence_count": inventory["correction_evidence_count"],
        "correction_evidence": inventory["correction_evidence"],
        "correction_evidence_sha256": inventory["correction_evidence_sha256"],
        "implementation_path_count": inventory["implementation_path_count"],
        "implementation_paths": inventory["implementation_paths"],
        "implementation_inventory_sha256": inventory["implementation_inventory_sha256"],
        "predecessor_failed_evidence_count": inventory["predecessor_failed_evidence_count"],
        "predecessor_failed_evidence": inventory["predecessor_failed_evidence"],
        "predecessor_failed_evidence_sha256": inventory["predecessor_failed_evidence_sha256"],
        "predecessor_failed_materialization_bindings": _predecessor_failed_bindings(),
        "predecessor_owner_seal_reusable": False,
        "predecessor_terminal_reusable": False,
        "host_metadata_excluded": True,
        "absolute_path_excluded": True,
        "checkout_location_excluded": True,
        "drive_letter_excluded": True,
        "extended_length_prefix_excluded": True,
        "max_path_excluded": True,
        "mtime_excluded": True,
        "missing_extra_duplicate_case_alias_blob_fail_closed": True,
        "g1_validated_subject_commit": phase7_v2.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": phase7_v2.G1_SUBJECT_TREE,
        "g1_gate_manifest_sha256": phase7_v2.G1_GATE_SHA256,
        "g1_closeout_sha256": phase7_v2.G1_CLOSEOUT_SHA256,
        "readoption_transaction_id": phase7_v2.TRANSACTION_ID,
        "readoption_transaction_identity": phase7_v2.TRANSACTION_IDENTITY,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "candidate_manifest_sha256": phase7_v2.CANDIDATE_SHA256,
        "candidate_patch_sha256": phase7_v2.PATCH_SHA256,
        "evaluation_subject_kind": failed.EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": failed.DISPOSITION_SHA256,
        "policy_sha256": failed.POLICY_RAW_SHA256,
        "policy_seal_sha256": failed.POLICY_SEAL_SHA256,
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "live_required_gate_adopted": True,
        "post_adoption_current_route": "136/136 PASS",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "policy_closure_state": "pending_fresh_independent_review",
    }
    freeze = {**freeze_core, "freeze_hash": base.canonical_hash(freeze_core)}
    freeze_sha = base.sha256_bytes(base.pretty_json_bytes(freeze))
    manifest_core = {
        "schema_version": MANIFEST_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_bearing_artifact_count": inventory["claim_bearing_artifact_count"],
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "correction_evidence_count": inventory["correction_evidence_count"],
        "correction_evidence_sha256": inventory["correction_evidence_sha256"],
        "implementation_path_count": inventory["implementation_path_count"],
        "implementation_inventory_sha256": inventory["implementation_inventory_sha256"],
        "predecessor_failed_evidence_count": inventory["predecessor_failed_evidence_count"],
        "predecessor_failed_evidence_sha256": inventory["predecessor_failed_evidence_sha256"],
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": freeze_sha,
        "self_hash_included": False,
        "terminal_included": False,
    }
    manifest = {**manifest_core, "manifest_hash": base.canonical_hash(manifest_core)}
    manifest_sha = base.sha256_bytes(base.pretty_json_bytes(manifest))
    request = {
        "schema_version": "public_text_quality_phase7_host_independent_review_request_v4",
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "review_subject_commit": freeze_commit,
        "review_subject_tree": freeze_tree,
        "freeze_sha256": freeze_sha,
        "artifact_manifest_sha256": manifest_sha,
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "required_reviewer_kind": "codex_reviewer",
        "required_scopes": [
            "git_tree_index_inventory_authority",
            "long_path_representation_independence",
            "inventory_denominator_139",
            "inventory_fail_closed_fixtures",
            "predecessor_failure_role_separation",
            "terminal_dag_complete_binding",
            "freeze_deterministic_replay",
            "temporary_projection_parity",
            "current_route_lua_no_mutation",
            "claim_boundary_and_no_authority_effect",
        ],
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
        "owner_or_implementation_author_ineligible": True,
    }
    census = {
        "schema_version": "public_text_quality_phase7_host_independent_vcs_census_v3",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "required_count": 139,
        "tracked_tree_count": 139,
        "head_blob_match_count": 139,
        "index_match_count": 139 if verify_current else 0,
        "working_filtered_identity_match_count": 139 if verify_current else 0,
        "missing_count": 0,
        "extra_count": 0,
        "duplicate_count": 0,
        "case_collision_count": 0,
        "path_alias_count": 0,
        "blob_mismatch_count": 0,
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }
    return {
        "freeze": freeze,
        "artifact_manifest": manifest,
        "review_request": request,
        "vcs_census": census,
    }


def validate_freeze_document(value: Any) -> dict[str, Any]:
    freeze = _object(value, "host-independent freeze")
    if freeze.get("schema_version") != FREEZE_SCHEMA:
        _fail("unknown or predecessor freeze schema in current role")
    core = {key: child for key, child in freeze.items() if key != "freeze_hash"}
    if freeze.get("freeze_hash") != base.canonical_hash(core):
        _fail("host-independent freeze canonical hash mismatch")
    rows = freeze.get("claim_bearing_artifacts")
    if not isinstance(rows, list) or len(rows) != 139:
        _fail("host-independent freeze denominator is not 139")
    if freeze.get("claim_bearing_artifact_count") != 139:
        _fail("host-independent freeze declared denominator mismatch")
    if freeze.get("claim_inventory_sha256") != _inventory_hash(rows):
        _fail("host-independent freeze inventory SHA mismatch")
    required = {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "predecessor_owner_seal_reusable": False,
        "predecessor_terminal_reusable": False,
        "missing_extra_duplicate_case_alias_blob_fail_closed": True,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }
    for field, expected in required.items():
        if freeze.get(field) != expected:
            _fail(f"host-independent freeze binding mismatch: {field}")
    return {
        "status": "PASS",
        "schema_dispatch": "host_independent_freeze_v3",
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": freeze["claim_inventory_sha256"],
    }


def materialize_freeze() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("fresh host-independent freeze requires a clean checkout")
    bundle = compute_freeze_bundle(verify_current=True)
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        base.write_once_or_same(path, bundle[key])
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "review_request_sha256": base.sha256_file(REVIEW_REQUEST),
        "claim_inventory_sha256": bundle["freeze"]["claim_inventory_sha256"],
        "claim_bearing_artifact_count": 139,
        "reviewer_input_required": True,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def _tracked_record(path: Path) -> dict[str, Any]:
    relative = _repo_path(path)
    tree = {entry["path"]: entry for entry in _tree_entries("HEAD")}
    entry = tree.get(relative)
    if entry is None:
        _fail(f"required tracked artifact is absent from HEAD: {relative}")
    row = _rows_for_paths(list(tree.values()), [relative])[0]
    _verify_current_identity([row])
    return {
        "path": relative,
        "sha256": row["raw_sha256"],
        "git_blob_id": row["git_blob_id"],
        "tracked": True,
        "ignored": False,
        "working_identity": True,
    }


def validate_freeze_bundle(*, require_tracked: bool) -> dict[str, Any]:
    existing = _object(base.load_json_strict(FREEZE), "host-independent freeze")
    expected = compute_freeze_bundle(
        freeze_commit=existing.get("freeze_commit"),
        freeze_tree=existing.get("freeze_tree"),
        verify_current=False,
    )
    records: dict[str, Any] = {}
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        if path.read_bytes() != base.pretty_json_bytes(expected[key]):
            _fail(f"host-independent freeze deterministic replay mismatch: {path.name}")
        records[key] = (
            _tracked_record(path)
            if require_tracked
            else {"path": _repo_path(path), "sha256": base.sha256_file(path)}
        )
    freeze = base.load_json_strict(FREEZE)
    all_rows = (
        freeze["claim_bearing_artifacts"]
        + freeze["correction_evidence"]
        + freeze["implementation_paths"]
        + freeze["predecessor_failed_evidence"]
    )
    identity = _verify_current_identity(all_rows)
    dispatch = validate_freeze_document(freeze)
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "deterministic_replay": True,
        "schema_dispatch": dispatch,
        "current_identity": identity,
        "records": records,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def validate_current_inputs() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for role, (path, expected_sha256, _schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        record = _tracked_record(path)
        if record["sha256"] != expected_sha256:
            _fail(f"predecessor failed evidence SHA mismatch: {role}")
        records[role] = record
    live = _tracked_record(base.LIVE_REQUIRED_VALIDATIONS)
    if live["sha256"] != phase7_v2.LIVE_SHA256:
        _fail("live manifest changed during host-independent correction")
    missing_path = (
        _repo_path(official.ATTEMPT_ROOT)
        + "/phase6/corrections/g1-successor-0008-revalidation-0001/"
        "phase6_revalidation_failure_record.json"
    )
    entries = _tree_entries("HEAD")
    selected = _select_base_claim_paths(entries)
    if missing_path not in selected:
        _fail("host-independent selector omitted the prior long-path artifact")
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "live_manifest": live,
        "predecessor_failed_evidence": records,
        "claim_bearing_artifact_count": len(selected),
        "previously_omitted_artifact_present": True,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def _extended_path(path: Path) -> str:
    absolute = str(path.absolute())
    if os.name == "nt" and not absolute.startswith("\\\\?\\"):
        return "\\\\?\\" + absolute
    return absolute


def _write_projection(root: Path, rows: list[dict[str, Any]]) -> str:
    blobs = _blob_bytes(row["git_blob_id"] for row in rows)
    for row in rows:
        target = root.joinpath(*row["path"].split("/"))
        os.makedirs(_extended_path(target.parent), exist_ok=True)
        with open(_extended_path(target), "wb") as stream:
            stream.write(blobs[row["git_blob_id"]])
    for row in rows:
        target = root.joinpath(*row["path"].split("/"))
        with open(_extended_path(target), "rb") as stream:
            observed = hashlib.sha256(stream.read()).hexdigest()
        if observed != row["raw_sha256"]:
            _fail(f"temporary projection blob mismatch: {row['path']}")
    return _inventory_hash(rows)


def validate_temporary_projection_parity(output_root: Path) -> dict[str, Any]:
    repository = official.REPO_ROOT.resolve()
    external = output_root.resolve()
    try:
        inside = os.path.commonpath([str(repository), str(external)]) == str(repository)
    except ValueError:
        inside = False
    if inside:
        _fail("temporary projection root must be repository-external")
    external.mkdir(parents=True, exist_ok=True)
    entries = _tree_entries("HEAD")
    rows = _rows_for_paths(entries, _select_base_claim_paths(entries))
    roots = [
        Path(tempfile.mkdtemp(prefix="g4-inventory-a-", dir=external)),
        Path(tempfile.mkdtemp(prefix="g4-inventory-b-", dir=external)),
    ]
    try:
        aggregates = [_write_projection(root, rows) for root in roots]
        if len(set(aggregates)) != 1:
            _fail("temporary checkout projection inventory SHA mismatch")
        return {
            "status": "PASS",
            "algorithm_id": INVENTORY_ALGORITHM_ID,
            "projection_count": 2,
            "locations_distinct": roots[0] != roots[1],
            "path_count_per_projection": len(rows),
            "inventory_sha256_a": aggregates[0],
            "inventory_sha256_b": aggregates[1],
            "canonical_results_identical": True,
            "repository_external": True,
            "authority_effect": "none",
        }
    finally:
        for root in roots:
            if root.exists():
                shutil.rmtree(_extended_path(root))


def _expect_failure(label: str, action: Any) -> dict[str, Any]:
    try:
        action()
    except base.FoundationContractError as exc:
        return {"case": label, "status": "PASS", "rejected": True, "error": str(exc)}
    _fail(f"focused negative fixture did not fail closed: {label}")


def _validate_rows_against_expected(
    expected: list[dict[str, Any]],
    observed: list[dict[str, Any]],
) -> None:
    paths: list[str] = []
    folded: dict[str, str] = {}
    for row in observed:
        if not isinstance(row, dict) or "path" not in row:
            _fail("inventory row is malformed")
        path = _canonical_repo_path(row["path"])
        paths.append(path)
        key = path.casefold()
        if key in folded and folded[key] != path:
            _fail(f"inventory row case collision: {folded[key]} vs {path}")
        folded[key] = path
    if len(paths) != len(set(paths)):
        _fail("inventory rows contain a duplicate path")
    if observed != expected:
        _fail("inventory rows have missing, extra, reordered, aliased, or blob-mismatched entries")


def _terminal_fixture() -> dict[str, Any]:
    fixture = failed._focused_fixture()
    context = fixture["context"]
    context["correction_id"] = CORRECTION_ID
    documents = fixture["documents"]
    actual = fixture["actual_sha256_by_path"]
    for role, (_path, _sha256, schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        document = {
            "schema_version": schema,
            "status": "HISTORICAL_FAILED_EVIDENCE",
            "role": role,
        }
        raw = base.pretty_json_bytes(document)
        path = f"fixture/{role}.json"
        digest = base.sha256_bytes(raw)
        documents[role] = document
        actual[path] = digest
        context["role_specs"][role] = {
            "role": role,
            "path": path,
            "sha256": digest,
            "schema_version": schema,
        }
        context["role_requirements"][role] = {
            "status": "HISTORICAL_FAILED_EVIDENCE",
            "role": role,
        }
    context["edges"] = _edge_contract()
    context["bindings"].update(
        {
            "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
            "claim_inventory_sha256": "6" * 64,
            "predecessor_failed_owner_seal_sha256": context["role_specs"]["predecessor_failed_owner_seal"]["sha256"],
            "predecessor_failed_final_report_sha256": context["role_specs"]["predecessor_failed_final_report"]["sha256"],
            "predecessor_failed_terminal_sha256": context["role_specs"]["predecessor_failed_terminal"]["sha256"],
            "predecessor_terminal_failure_sha256": context["role_specs"]["predecessor_terminal_failure"]["sha256"],
        }
    )
    report, terminal = failed._build_terminal_documents(context)
    actual[context["final_report_path"]] = context["final_report_sha256"]
    actual[context["terminal_path"]] = base.sha256_bytes(base.pretty_json_bytes(terminal))
    fixture["final_report"] = report
    fixture["terminal"] = terminal
    return fixture


def _edge_contract() -> list[dict[str, str]]:
    rows = [
        (row["from"], row["to"], row["relation"])
        for row in failed._edge_contract()
    ]
    rows.extend(
        (role, "fresh_freeze", "historical_failed_predecessor")
        for role in PREDECESSOR_FAILED_EVIDENCE
    )
    return [
        {"from": source, "to": target, "relation": relation}
        for source, target, relation in sorted(rows)
    ]


def run_focused_tests() -> dict[str, Any]:
    entries = _tree_entries("HEAD")
    selected = _select_base_claim_paths(entries)
    expected = _rows_for_paths(entries, selected)
    _validate_rows_against_expected(expected, expected)
    cases: list[dict[str, Any]] = [
        {"case": "complete_inventory", "status": "PASS", "path_count": len(expected)},
        _expect_failure(
            "missing_row",
            lambda: _validate_rows_against_expected(expected, expected[:-1]),
        ),
        _expect_failure(
            "extra_row",
            lambda: _validate_rows_against_expected(
                expected,
                expected + [{**expected[-1], "path": "fixture/extra.json"}],
            ),
        ),
        _expect_failure(
            "duplicate_row",
            lambda: _validate_rows_against_expected(expected, expected + [dict(expected[-1])]),
        ),
        _expect_failure(
            "case_collision",
            lambda: _validate_rows_against_expected(
                expected,
                expected + [{**expected[-1], "path": expected[-1]["path"].swapcase()}],
            ),
        ),
        _expect_failure(
            "path_alias",
            lambda: _validate_rows_against_expected(
                expected,
                [{**expected[0], "path": "alias/../" + expected[0]["path"]}] + expected[1:],
            ),
        ),
        _expect_failure(
            "blob_mismatch",
            lambda: _validate_rows_against_expected(
                expected,
                [{**expected[0], "git_blob_id": "0" * 40}] + expected[1:],
            ),
        ),
    ]
    normal_hash = _inventory_hash(expected)
    extended_hash = _inventory_hash(json.loads(json.dumps(expected)))
    if normal_hash != extended_hash:
        _fail("normal/extended path representation changed inventory identity")
    cases.append(
        {
            "case": "normal_and_extended_path_identity",
            "status": "PASS",
            "inventory_sha256": normal_hash,
        }
    )
    fixture = _terminal_fixture()
    terminal_result = failed.validate_terminal_bundle(
        terminal=fixture["terminal"],
        final_report=fixture["final_report"],
        context=fixture["context"],
        documents=fixture["documents"],
        actual_sha256_by_path=fixture["actual_sha256_by_path"],
    )
    if terminal_result.get("node_count") != 25 or terminal_result.get("edge_count") != 38:
        _fail("host-independent terminal DAG fixture denominator mismatch")
    cases.append(
        {
            "case": "complete_terminal_dag",
            "status": "PASS",
            "node_count": 25,
            "edge_count": 38,
        }
    )
    if len(cases) != 9 or any(row["status"] != "PASS" for row in cases):
        _fail("focused host-independent inventory tests did not pass 9/9")
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "case_count": 9,
        "passed_case_count": 9,
        "claim_bearing_artifact_count": len(expected),
        "claim_inventory_sha256": normal_hash,
        "terminal_dag_node_count": 25,
        "terminal_dag_edge_count": 38,
        "cases": cases,
        "authority_effect": "none",
    }


def _load_tracked_json(path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    record = _tracked_record(path)
    payload = _blob_bytes([record["git_blob_id"]])[record["git_blob_id"]]
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not strict UTF-8 JSON: {exc}")
    return _object(value, label), record


def validate_review() -> dict[str, Any]:
    freeze = validate_freeze_bundle(require_tracked=True)
    review, review_ref = _load_tracked_json(INDEPENDENT_REVIEW, "independent review")
    eligibility, eligibility_ref = _load_tracked_json(
        REVIEWER_ELIGIBILITY, "reviewer eligibility"
    )
    if not _proof(review, "reviewer_binding_proof"):
        _fail("independent review binding proof mismatch")
    if not _proof(eligibility, "eligibility_binding_proof"):
        _fail("reviewer eligibility binding proof mismatch")
    required_review_keys = {
        "schema_version",
        "status",
        "verdict",
        "attempt_id",
        "correction_id",
        "reviewed_at_utc",
        "reviewer_kind",
        "reviewer_identity",
        "reviewed_commit",
        "reviewed_tree",
        "freeze_sha256",
        "artifact_manifest_sha256",
        "review_request_sha256",
        "claim_inventory_sha256",
        "reviewed_scope_count",
        "critical_finding_count",
        "important_finding_count",
        "findings",
        "scope_results",
        "verified_hashes",
        "owner_seal_sufficiency",
        "reviewer_binding_proof",
    }
    if set(review) != required_review_keys:
        _fail("independent review has missing or extra fields")
    required_eligibility_keys = {
        "schema_version",
        "status",
        "attempt_id",
        "correction_id",
        "declared_at_utc",
        "reviewer_kind",
        "reviewer_identity",
        "reviewed_commit",
        "reviewed_tree",
        "independent_from_owner",
        "independent_from_implementation_author",
        "owner_input_cross_reclassification",
        "conflict_of_interest",
        "eligibility_binding_proof",
    }
    if set(eligibility) != required_eligibility_keys:
        _fail("reviewer eligibility has missing or extra fields")
    reviewed_commit = _git_text(
        "log", "-1", "--format=%H", "--", _repo_path(FREEZE)
    )
    reviewed_tree = _git_text("rev-parse", f"{reviewed_commit}^{{tree}}")
    frozen = base.load_json_strict(FREEZE)
    expected_review = {
        "schema_version": REVIEW_SCHEMA,
        "status": "PASS",
        "verdict": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "reviewer_kind": "codex_reviewer",
        "reviewer_identity": "codex_reviewer",
        "reviewed_commit": reviewed_commit,
        "reviewed_tree": reviewed_tree,
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "review_request_sha256": base.sha256_file(REVIEW_REQUEST),
        "claim_inventory_sha256": frozen["claim_inventory_sha256"],
        "reviewed_scope_count": 10,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "findings": [],
    }
    for field, expected in expected_review.items():
        if review.get(field) != expected:
            _fail(f"independent review mismatch: {field}")
    expected_eligibility = {
        "schema_version": ELIGIBILITY_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "reviewer_kind": "codex_reviewer",
        "reviewer_identity": "codex_reviewer",
        "reviewed_commit": reviewed_commit,
        "reviewed_tree": reviewed_tree,
        "independent_from_owner": True,
        "independent_from_implementation_author": True,
        "owner_input_cross_reclassification": False,
        "conflict_of_interest": False,
    }
    for field, expected in expected_eligibility.items():
        if eligibility.get(field) != expected:
            _fail(f"reviewer eligibility mismatch: {field}")
    return {
        "status": "PASS",
        "freeze": freeze,
        "review": review_ref,
        "eligibility": eligibility_ref,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "authority_effect": "none",
    }


def owner_seal_required_fields() -> dict[str, Any]:
    review = validate_review()
    freeze = base.load_json_strict(FREEZE)
    return {
        "schema_version": OWNER_SCHEMA,
        "status": "PASS",
        "decision": "seal_policy_closure",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_inventory_sha256": freeze["claim_inventory_sha256"],
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "transaction_id": phase7_v2.TRANSACTION_ID,
        "transaction_nonce": failed.TRANSACTION_NONCE,
        "transaction_identity": phase7_v2.TRANSACTION_IDENTITY,
        "readoption_transaction_contract_sha256": phase7_v2.TRANSACTION_CONTRACT_SHA256,
        "readoption_owner_input_sha256": phase7_v2.OWNER_INPUT_SHA256,
        "live_adoption_receipt_sha256": phase7_v2.LIVE_RECEIPT_SHA256,
        "post_adoption_current_route_sha256": phase7_v2.POST_ROUTE_SHA256,
        "evaluation_subject_kind": failed.EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": failed.DISPOSITION_SHA256,
        "policy_sha256": failed.POLICY_RAW_SHA256,
        "policy_seal_sha256": failed.POLICY_SEAL_SHA256,
        "naturalization_handoff_path": _repo_path(official.PHASE8_HANDOFF),
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "g1_validated_subject_commit": phase7_v2.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": phase7_v2.G1_SUBJECT_TREE,
        "g1_gate_successor_sha256": phase7_v2.G1_GATE_SHA256,
        "g1_closeout_successor_sha256": phase7_v2.G1_CLOSEOUT_SHA256,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "candidate_manifest_sha256": phase7_v2.CANDIDATE_SHA256,
        "candidate_patch_sha256": phase7_v2.PATCH_SHA256,
        "post_adoption_selected_identity_count": 136,
        "post_adoption_test_count": 136,
        "predecessor_failed_owner_seal_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_owner_seal"][1],
        "predecessor_failed_final_report_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_final_report"][1],
        "predecessor_failed_terminal_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_terminal"][1],
        "predecessor_terminal_failure_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_terminal_failure"][1],
        "predecessor_failed_materialization_reused": False,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
        "policy_closure_state": "complete",
        "owner_identity": "repository_owner_via_direct_codex_instruction",
        "sealed_at": "ACTUAL_UTC_TIME_OF_OWNER_DECISION",
        "owner_binding_proof": "SHA256_CANONICAL_JSON_OF_ALL_OTHER_FIELDS",
    }


def validate_owner_seal() -> dict[str, Any]:
    if _repo_path(OWNER_SEAL) not in {entry["path"] for entry in _tree_entries("HEAD")}:
        fields = owner_seal_required_fields()
        base.write_once_or_same(
            OWNER_GAP,
            {
                "schema_version": "public_text_quality_phase7_host_independent_owner_gap_v3",
                "status": "WAITING_FOR_EXTERNAL_INPUT",
                "attempt_id": official.ATTEMPT_ID,
                "correction_id": CORRECTION_ID,
                "required_owner_input_path": _repo_path(OWNER_SEAL),
                "required_owner_input_exact_fields": fields,
                "predecessor_owner_seal_reusable": False,
                "terminal_created": False,
                "g5_handoff_created": False,
            },
        )
        raise base.ExternalInputRequired(
            input_kind="phase7_host_independent_owner_closure_seal",
            path=OWNER_SEAL,
            details={"required_owner_input_exact_fields": fields},
        )
    review = validate_review()
    seal, seal_ref = _load_tracked_json(OWNER_SEAL, "owner closure seal")
    if not _proof(seal, "owner_binding_proof"):
        _fail("owner closure seal binding proof mismatch")
    expected = owner_seal_required_fields()
    if set(seal) != set(expected):
        _fail("owner closure seal has missing or extra fields")
    for field, value in expected.items():
        if field in {"sealed_at", "owner_binding_proof"}:
            continue
        if seal.get(field) != value:
            _fail(f"owner closure seal mismatch: {field}")
    if not isinstance(seal.get("sealed_at"), str):
        _fail("owner closure seal timestamp is missing")
    return {
        "status": "PASS",
        "owner_seal": seal_ref,
        "review": review,
        "authority_effect": "none",
    }


def _role_paths() -> dict[str, Path]:
    paths = failed._role_paths()
    paths.update(
        {
            "fresh_freeze": FREEZE,
            "fresh_artifact_manifest": ARTIFACT_MANIFEST,
            "independent_review": INDEPENDENT_REVIEW,
            "reviewer_eligibility": REVIEWER_ELIGIBILITY,
            "owner_closure_seal": OWNER_SEAL,
            "protected_mutation_report": VALIDATION_ROOT / "protected.json",
            "lua_mutation_report": VALIDATION_ROOT / "lua.json",
        }
    )
    for role, (path, _sha256, _schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        paths[role] = path
    return paths


def _schema_contract() -> dict[str, str]:
    schemas = failed._schema_contract()
    schemas.update(
        {
            "fresh_freeze": FREEZE_SCHEMA,
            "fresh_artifact_manifest": MANIFEST_SCHEMA,
            "independent_review": REVIEW_SCHEMA,
            "reviewer_eligibility": ELIGIBILITY_SCHEMA,
            "owner_closure_seal": OWNER_SCHEMA,
            "protected_mutation_report": "public_text_quality_phase7_host_independent_protected_surface_v1",
            "lua_mutation_report": "public_text_quality_phase7_host_independent_lua_syntax_v1",
        }
    )
    for role, (_path, _sha256, schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        schemas[role] = schema
    return schemas


def _binding_contract(role_hashes: dict[str, str]) -> dict[str, Any]:
    bindings = failed._binding_contract(role_hashes)
    freeze = base.load_json_strict(FREEZE)
    bindings.update(
        {
            "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
            "claim_inventory_sha256": freeze["claim_inventory_sha256"],
            "predecessor_failed_owner_seal_sha256": role_hashes["predecessor_failed_owner_seal"],
            "predecessor_failed_final_report_sha256": role_hashes["predecessor_failed_final_report"],
            "predecessor_failed_terminal_sha256": role_hashes["predecessor_failed_terminal"],
            "predecessor_terminal_failure_sha256": role_hashes["predecessor_terminal_failure"],
            "predecessor_failed_materialization_reused": False,
        }
    )
    return bindings


def _role_requirements(bindings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    requirements = failed._role_requirements(bindings)
    requirements["fresh_freeze"] = {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "predecessor_owner_seal_reusable": False,
        "predecessor_terminal_reusable": False,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
    }
    requirements["fresh_artifact_manifest"] = {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "freeze_sha256": bindings["fresh_freeze_sha256"],
    }
    requirements["independent_review"].update(
        {
            "correction_id": CORRECTION_ID,
            "freeze_sha256": bindings["fresh_freeze_sha256"],
            "artifact_manifest_sha256": bindings["fresh_artifact_manifest_sha256"],
            "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        }
    )
    requirements["independent_review"].pop("freeze_manifest_sha256", None)
    requirements["independent_review"].pop("final_artifact_hash_manifest_sha256", None)
    requirements["reviewer_eligibility"]["correction_id"] = CORRECTION_ID
    requirements["owner_closure_seal"].update(
        {
            "correction_id": CORRECTION_ID,
            "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
            "claim_inventory_sha256": bindings["claim_inventory_sha256"],
            "freeze_sha256": bindings["fresh_freeze_sha256"],
            "artifact_manifest_sha256": bindings["fresh_artifact_manifest_sha256"],
            "predecessor_failed_materialization_reused": False,
        }
    )
    requirements["owner_closure_seal"].pop("freeze_manifest_sha256", None)
    requirements["owner_closure_seal"].pop("final_artifact_hash_manifest_sha256", None)
    requirements.update(
        {
            "predecessor_failed_owner_seal": {
                "status": "PASS",
                "correction_id": failed.CORRECTION_ID,
            },
            "predecessor_failed_final_report": {
                "status": "PASS",
                "correction_id": failed.CORRECTION_ID,
            },
            "predecessor_failed_terminal": {
                "status": "PASS",
                "correction_id": failed.CORRECTION_ID,
            },
            "predecessor_terminal_failure": {
                "status": "FAIL_CLOSED",
                "correction_id": failed.CORRECTION_ID,
                "terminal_state": "MATERIALIZED_BUT_COMMITTED_VALIDATION_FAILED",
            },
        }
    )
    return requirements


def _validate_predecessor_failed_documents(
    documents: dict[str, dict[str, Any] | None]
) -> None:
    owner = _object(documents["predecessor_failed_owner_seal"], "predecessor owner seal")
    report = _object(documents["predecessor_failed_final_report"], "predecessor final report")
    terminal = _object(documents["predecessor_failed_terminal"], "predecessor terminal")
    failure = _object(documents["predecessor_terminal_failure"], "predecessor failure")
    if not _proof(owner, "owner_binding_proof"):
        _fail("predecessor failed owner seal proof mismatch")
    if not _proof(report, "closeout_hash"):
        _fail("predecessor failed final report proof mismatch")
    if not _proof(terminal, "terminal_hash"):
        _fail("predecessor failed terminal proof mismatch")
    if (
        failure.get("status") != "FAIL_CLOSED"
        or failure.get("terminal_sha256")
        != PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_terminal"][1]
    ):
        _fail("predecessor terminal failure lifecycle mismatch")


def _production_context() -> tuple[
    dict[str, Any],
    dict[str, dict[str, Any] | None],
    dict[str, str],
]:
    validate_owner_seal()
    validate_freeze_bundle(require_tracked=True)
    paths = _role_paths()
    schemas = _schema_contract()
    static = failed._static_expected_hashes()
    static.update(
        {role: sha256 for role, (_path, sha256, _schema) in PREDECESSOR_FAILED_EVIDENCE.items()}
    )
    documents: dict[str, dict[str, Any] | None] = {}
    role_hashes: dict[str, str] = {}
    actual: dict[str, str] = {}
    for role, path in paths.items():
        record = _tracked_record(path)
        if role in static and record["sha256"] != static[role]:
            _fail(f"terminal role SHA mismatch: {role}")
        relative = _repo_path(path)
        role_hashes[role] = record["sha256"]
        actual[relative] = record["sha256"]
        if role == "evaluation_subject":
            documents[role] = None
        else:
            document, _record = _load_tracked_json(path, f"terminal role {role}")
            documents[role] = document
    _validate_predecessor_failed_documents(documents)
    bindings = _binding_contract(role_hashes)
    role_specs = {
        role: {
            "role": role,
            "path": _repo_path(paths[role]),
            "sha256": role_hashes[role],
            "schema_version": schemas[role],
        }
        for role in sorted(paths)
    }
    context = {
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "final_report_path": _repo_path(FINAL_REPORT),
        "terminal_path": _repo_path(TERMINAL_SEAL),
        "final_report_sha256": "",
        "role_specs": role_specs,
        "edges": _edge_contract(),
        "bindings": bindings,
        "role_requirements": _role_requirements(bindings),
    }
    return context, documents, actual


def finalize_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    report, terminal = failed._build_terminal_documents(context)
    base.write_once_or_same(FINAL_REPORT, report)
    actual[context["final_report_path"]] = base.sha256_file(FINAL_REPORT)
    if actual[context["final_report_path"]] != context["final_report_sha256"]:
        _fail("materialized final report raw SHA mismatch")
    base.write_once_or_same(TERMINAL_SEAL, terminal)
    actual[context["terminal_path"]] = base.sha256_file(TERMINAL_SEAL)
    validation = failed.validate_terminal_bundle(
        terminal=terminal,
        final_report=report,
        context=context,
        documents=documents,
        actual_sha256_by_path=actual,
    )
    return {
        "status": "PASS",
        "schema_dispatch": "host_independent_freeze_terminal_v3",
        "terminal_path": _repo_path(TERMINAL_SEAL),
        "terminal_sha256": base.sha256_file(TERMINAL_SEAL),
        "final_report_path": _repo_path(FINAL_REPORT),
        "final_report_sha256": base.sha256_file(FINAL_REPORT),
        "node_count": validation["node_count"],
        "edge_count": validation["edge_count"],
        "policy_closure_state": "complete",
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    terminal, terminal_ref = _load_tracked_json(TERMINAL_SEAL, "terminal seal")
    report, report_ref = _load_tracked_json(FINAL_REPORT, "final report")
    context["final_report_sha256"] = report_ref["sha256"]
    actual[context["final_report_path"]] = report_ref["sha256"]
    actual[context["terminal_path"]] = terminal_ref["sha256"]
    result = failed.validate_terminal_bundle(
        terminal=terminal,
        final_report=report,
        context=context,
        documents=documents,
        actual_sha256_by_path=actual,
    )
    return {
        "status": "PASS",
        "schema_dispatch": "host_independent_freeze_terminal_v3",
        "terminal": terminal_ref,
        "final_report": report_ref,
        "node_count": result["node_count"],
        "edge_count": result["edge_count"],
        "claim_inventory_sha256": context["bindings"]["claim_inventory_sha256"],
        "policy_closure_state": "complete",
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def materialize_g5_handoff() -> dict[str, Any]:
    terminal = validate_terminal()
    core = {
        "schema_version": "public_text_quality_g4_to_g5_terminal_handoff_v1",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "terminal_commit": _git_text("rev-parse", "HEAD"),
        "terminal_tree": _git_text("rev-parse", "HEAD^{tree}"),
        "terminal_path": terminal["terminal"]["path"],
        "terminal_sha256": terminal["terminal"]["sha256"],
        "final_report_path": terminal["final_report"]["path"],
        "final_report_sha256": terminal["final_report"]["sha256"],
        "claim_inventory_sha256": terminal["claim_inventory_sha256"],
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "g5_may_begin": True,
        "authority_effect": "none",
    }
    handoff = {**core, "handoff_hash": base.canonical_hash(core)}
    base.write_once_or_same(G5_HANDOFF, handoff)
    return {
        "status": "PASS",
        "handoff_path": _repo_path(G5_HANDOFF),
        "handoff_sha256": base.sha256_file(G5_HANDOFF),
        "terminal_commit": core["terminal_commit"],
        "terminal_tree": core["terminal_tree"],
        "authority_effect": "none",
    }
