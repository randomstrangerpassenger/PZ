"""Repository gate input and evidence contracts."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from Iris.validation.execution import checkout_environment as clean_checkout_common
from Iris.validation.execution.checkout_environment import (
    CleanCheckoutError,
    blob_id,
    bytes_at_commit,
    canonical_compact_json_bytes,
    git_identity,
    git_text,
    json_at_commit,
    sha256_bytes,
)


TAXONOMY_PATH = "Iris/_docs/round3/round3_test_taxonomy.json"
REQUIRED_MANIFEST_PATH = (
    "Iris/validation/execution/required_validations.json"
)
PYTEST_INI_PATH = "pytest.ini"
CANONICAL_GATE_PATH = (
    "Iris/validation/execution/contracts/scoped_test_gate.json"
)
FULL_REPOSITORY_GATE_PATH = (
    "Iris/validation/execution/contracts/repository_test_gate.json"
)
CURRENT_ENVIRONMENT_LOCATOR_PATH = clean_checkout_common.CURRENT_ENVIRONMENT_LOCATOR
OUTPUT_POLICY_PATH = (
    "Iris/validation/execution/contracts/test_execution_output_policy.json"
)
EVIDENCE_OWNER_APPROVAL_PATH = (
    "Iris/_docs/refactor/repository_evidence_lightweighting/"
    "owner_policy_approval.json"
)
RUNNER_PATH = (
    "Iris/validation/execution/run_repository_tests.py"
)
COMMON_MODULE_PATH = (
    "Iris/validation/execution/checkout_environment.py"
)
REPOSITORY_IMPORT_PREFIXES = (
    "",
    "Iris",
    "Iris/_docs/round3/registry_runtime_compatibility/bootstrap",
    "Iris/evidence/rightclick",
    "Iris/build",
    "Iris/build/description/v2",
    "Iris/build/description/v2/tests",
    "Iris/build/description/v2/tools",
    "Iris/build/description/v2/tools/build",
    "Iris/build/tests",
    "Iris/test",
    "Iris/validation/execution",
    "Iris/validation/execution/tests",
)


def _validate_consumer_integration_evidence(
    repo: Path,
    commit: str,
    contract: dict[str, Any],
    tracked: set[str],
    required_dependency_paths: set[str],
) -> list[dict[str, str]]:
    rows = contract.get("consumer_integration_evidence_policy", {}).get(
        "explicit_evidence_roles", []
    )
    validated: list[dict[str, str]] = []
    seen: set[str] = set()
    required_keys = {
        "evidence_id",
        "path",
        "sha256",
        "deterministic_result_hash",
        "execution_role",
        "authority_class",
        "evidence_role",
        "reason",
    }
    for row in rows:
        if not isinstance(row, dict) or set(row) != required_keys:
            raise CleanCheckoutError(
                "invalid consumer integration evidence schema"
            )
        path = row["path"]
        if (
            not isinstance(path, str)
            or path not in tracked
            or path in seen
            or path in required_dependency_paths
            or row["execution_role"] != "not_required"
            or row["authority_class"] != "historical_optional_evidence"
            or row["evidence_role"] != "consumer_integration_evidence"
            or not isinstance(row["evidence_id"], str)
            or not row["evidence_id"].strip()
            or not isinstance(row["reason"], str)
            or not row["reason"].strip()
        ):
            raise CleanCheckoutError(
                f"invalid consumer integration evidence disposition: {path!r}"
            )
        payload = bytes_at_commit(repo, commit, path)
        if sha256_bytes(payload) != row["sha256"]:
            raise CleanCheckoutError(
                f"consumer integration evidence SHA-256 mismatch: {path}"
            )
        try:
            result = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CleanCheckoutError(
                f"consumer integration evidence is not strict JSON: {path}"
            ) from exc
        if (
            not isinstance(result, dict)
            or result.get("deterministic_result_hash")
            != row["deterministic_result_hash"]
        ):
            raise CleanCheckoutError(
                "consumer integration evidence deterministic result hash "
                f"mismatch: {path}"
            )
        seen.add(path)
        validated.append({key: row[key] for key in sorted(required_keys)})
    return sorted(validated, key=lambda row: row["path"])


def _line_ending_sha256_variants(payload: bytes) -> set[str]:
    normalized = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return {
        sha256_bytes(normalized),
        sha256_bytes(normalized.replace(b"\n", b"\r\n")),
        sha256_bytes(normalized.replace(b"\n", b"\r")),
    }


def _normalized_compiler_rows(
    repo: Path, commit: str, ordered_paths: list[str]
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in ordered_paths:
        canonical = (
            bytes_at_commit(repo, commit, path)
            .replace(b"\r\n", b"\n")
            .replace(b"\r", b"\n")
        )
        rows.append({"path": path, "sha256_lf": sha256_bytes(canonical)})
    return rows


def _compiler_aggregate_sha256(
    algorithm_id: str, ordered_files: list[dict[str, str]]
) -> str:
    payload = {
        "algorithm_id": algorithm_id,
        "ordered_files": [
            {"path": row["path"], "sha256": row["sha256_lf"]}
            for row in ordered_files
        ],
    }
    return sha256_bytes(canonical_compact_json_bytes(payload))


def _git_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-C",
            str(repo),
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _git_commit_is_available(repo: Path, commit: str) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "-C",
            str(repo),
            "rev-parse",
            "--verify",
            f"{commit}^{{commit}}",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode == 0


def _validate_g5_compiler_identity_transition(
    repo: Path,
    subject_commit: str,
    compiler: dict[str, Any],
    transition: dict[str, Any],
    allow_owner_pruned_current_basis: bool,
) -> dict[str, Any]:
    expected_compiler_keys = {
        "algorithm_id",
        "historical_attested_aggregate_sha256",
        "current_aggregate_sha256",
        "ordered_paths",
        "successor_transition",
    }
    if set(compiler) != expected_compiler_keys:
        raise CleanCheckoutError("invalid G5 compiler identity contract schema")
    ordered_paths = compiler["ordered_paths"]
    if (
        not isinstance(ordered_paths, list)
        or not ordered_paths
        or len(ordered_paths) != len(set(ordered_paths))
        or any(not isinstance(path, str) or not path for path in ordered_paths)
    ):
        raise CleanCheckoutError("invalid G5 compiler ordered path contract")
    expected_transition_keys = {
        "schema_version",
        "status",
        "authority",
        "record_mode",
        "claim_boundary",
        "algorithm_id",
        "historical_gate_integration_basis",
        "current_identity_basis",
        "changed_rows",
        "changed_constituent_count",
        "unchanged_constituent_count",
        "non_claims",
    }
    transition_schema = transition.get("schema_version")
    if (
        set(transition) != expected_transition_keys
        or transition_schema
        not in {
            "iris-clean-checkout-g5-compiler-identity-successor-v1",
            "iris-clean-checkout-g5-compiler-identity-successor-v2",
            "iris-clean-checkout-g5-compiler-identity-successor-v3",
        }
        or transition["status"] != "PASS"
        or transition["algorithm_id"] != compiler["algorithm_id"]
        or not isinstance(transition["non_claims"], list)
        or not transition["non_claims"]
        or any(
            not isinstance(row, str) or not row.strip()
            for row in transition["non_claims"]
        )
    ):
        raise CleanCheckoutError("invalid G5 compiler successor transition schema")

    expected_basis_keys = {"commit", "tree", "aggregate_sha256", "ordered_files"}

    current_basis_was_pruned = False

    def validate_basis(name: str) -> tuple[dict[str, Any], list[dict[str, str]], str]:
        nonlocal current_basis_was_pruned
        basis = transition[name]
        if not isinstance(basis, dict) or set(basis) != expected_basis_keys:
            raise CleanCheckoutError(f"invalid G5 compiler {name} schema")
        basis_is_available = _git_commit_is_available(repo, basis["commit"])
        if not basis_is_available:
            if name != "current_identity_basis" or not allow_owner_pruned_current_basis:
                raise CleanCheckoutError(
                    f"G5 compiler {name} Git object is unavailable"
                )
            current_basis_was_pruned = True
            actual_rows = basis["ordered_files"]
        else:
            identity = git_identity(repo, basis["commit"])
            if identity != {"commit": basis["commit"], "tree": basis["tree"]}:
                raise CleanCheckoutError(f"G5 compiler {name} identity mismatch")
            basis_paths = [row["path"] for row in basis["ordered_files"]]
            if (
                not basis_paths
                or len(basis_paths) != len(set(basis_paths))
                or (
                    name == "current_identity_basis"
                    and basis_paths != ordered_paths
                )
                or (
                    transition_schema.endswith("-v1")
                    and basis_paths != ordered_paths
                )
            ):
                raise CleanCheckoutError(
                    f"invalid G5 compiler {name} ordered paths"
                )
            actual_rows = _normalized_compiler_rows(
                repo, basis["commit"], basis_paths
            )
        if basis["ordered_files"] != actual_rows:
            raise CleanCheckoutError(f"G5 compiler {name} ordered files mismatch")
        aggregate = _compiler_aggregate_sha256(
            compiler["algorithm_id"], actual_rows
        )
        if basis["aggregate_sha256"] != aggregate:
            raise CleanCheckoutError(f"G5 compiler {name} aggregate mismatch")
        return basis, actual_rows, aggregate

    historical, historical_rows, historical_aggregate = validate_basis(
        "historical_gate_integration_basis"
    )
    current_basis, current_basis_rows, current_aggregate = validate_basis(
        "current_identity_basis"
    )
    if current_basis_was_pruned:
        if not _git_is_ancestor(repo, historical["commit"], subject_commit):
            raise CleanCheckoutError("G5 compiler historical ancestry mismatch")
    elif (
        not _git_is_ancestor(repo, historical["commit"], current_basis["commit"])
        or not _git_is_ancestor(repo, current_basis["commit"], subject_commit)
    ):
        raise CleanCheckoutError("G5 compiler successor ancestry mismatch")
    subject_rows = _normalized_compiler_rows(repo, subject_commit, ordered_paths)
    if subject_rows != current_basis_rows:
        raise CleanCheckoutError("G5 current compiler identity changed after bridge basis")
    if not current_basis_was_pruned:
        for path in ordered_paths:
            basis_last_writer = git_text(
                repo,
                "log",
                "-1",
                "--format=%H",
                current_basis["commit"],
                "--",
                path,
            ).strip()
            subject_last_writer = git_text(
                repo,
                "log",
                "-1",
                "--format=%H",
                subject_commit,
                "--",
                path,
            ).strip()
            if (
                subject_last_writer != basis_last_writer
                or blob_id(repo, subject_commit, path)
                != blob_id(repo, current_basis["commit"], path)
            ):
                raise CleanCheckoutError(
                    f"G5 compiler path changed after bridge basis: {path}"
                )
    if (
        compiler["historical_attested_aggregate_sha256"]
        != historical_aggregate
        or compiler["current_aggregate_sha256"] != current_aggregate
    ):
        raise CleanCheckoutError("G5 compiler contract aggregate split mismatch")

    expected_changed_rows: list[dict[str, Any]] = []
    if transition_schema.endswith("-v3"):
        historical_by_name = {
            Path(row["path"]).name: row for row in historical_rows
        }
        current_names = {Path(row["path"]).name for row in current_basis_rows}
        if len(historical_by_name) != len(historical_rows) or not set(
            historical_by_name
        ).issubset(current_names):
            raise CleanCheckoutError(
                "G5 compiler historical/current constituent mapping mismatch"
            )
        paired_rows = [
            (historical_by_name.get(Path(row["path"]).name), row)
            for row in current_basis_rows
        ]
    else:
        if len(historical_rows) != len(current_basis_rows):
            raise CleanCheckoutError("invalid G5 compiler basis cardinality")
        paired_rows = list(zip(historical_rows, current_basis_rows, strict=True))

    for historical_row, current_row in paired_rows:
        if historical_row is None:
            historical_path = None
            historical_sha = None
        else:
            historical_path = historical_row["path"]
            historical_sha = historical_row["sha256_lf"]
        current_path = current_row["path"]
        current_sha = current_row["sha256_lf"]
        if historical_path == current_path and historical_sha == current_sha:
            continue
        provenance_commit = (
            subject_commit if current_basis_was_pruned else current_basis["commit"]
        )
        last_writer_commit = git_text(
            repo,
            "log",
            "-1",
            "--format=%H",
            provenance_commit,
            "--",
            current_path,
        ).strip()
        last_writer_identity = git_identity(repo, last_writer_commit)
        if (
            not _git_is_ancestor(
                repo, last_writer_commit, provenance_commit
            )
            or _normalized_compiler_rows(
                repo, last_writer_commit, [current_path]
            )[0][
                "sha256_lf"
            ]
            != current_sha
        ):
            raise CleanCheckoutError(
                "G5 compiler last-writer provenance mismatch: "
                f"{current_path}"
            )
        changed_row = {
            "path": current_path,
            "historical_sha256_lf": historical_sha,
            "current_sha256_lf": current_sha,
            "current_last_writer_commit": last_writer_identity["commit"],
            "current_last_writer_tree": last_writer_identity["tree"],
        }
        if transition_schema.endswith(("-v2", "-v3")):
            changed_row = {
                "historical_path": historical_path,
                **changed_row,
            }
        expected_changed_rows.append(changed_row)
    if transition["changed_rows"] != expected_changed_rows:
        raise CleanCheckoutError("G5 compiler derived changed-row mismatch")
    if (
        transition["changed_constituent_count"] != len(expected_changed_rows)
        or transition["unchanged_constituent_count"]
        != len(ordered_paths) - len(expected_changed_rows)
    ):
        raise CleanCheckoutError("G5 compiler transition count mismatch")
    return {
        "algorithm_id": compiler["algorithm_id"],
        "ordered_path_count": len(ordered_paths),
        "historical_attested_aggregate_sha256": historical_aggregate,
        "current_aggregate_sha256": current_aggregate,
        "changed_constituent_count": len(expected_changed_rows),
        "unchanged_constituent_count": len(ordered_paths)
        - len(expected_changed_rows),
        "current_basis_validation_mode": (
            "owner_pruned_revalidated_from_subject"
            if current_basis_was_pruned
            else "exact_git_object"
        ),
    }


def _validate_current_capsule_required_evidence(
    repo: Path,
    commit: str,
    contract: dict[str, Any],
    tracked: set[str],
) -> dict[str, Any]:
    g5 = contract["g5_required_evidence"]
    binding = g5["capsule_manifest"]
    manifest_path = binding["path"]
    if binding.get("hash_mode") != "git_blob_raw_sha256" or manifest_path not in tracked:
        raise CleanCheckoutError("invalid current capsule manifest binding")
    raw = bytes_at_commit(repo, commit, manifest_path)
    raw_sha256 = sha256_bytes(raw)
    if raw_sha256 != binding["git_blob_raw_sha256"]:
        raise CleanCheckoutError("current capsule manifest identity mismatch")
    manifest = json.loads(raw)
    if (
        manifest.get("schema_version") != "iris_current_required_evidence_capsule_v1"
        or manifest.get("claim_id") != "current_capsule_attestation_v2"
        or manifest.get("superseded_claim_id") != "raw_repository_evidence_v1"
        or manifest.get("external_archive_is_current_route_dependency") is not False
    ):
        raise CleanCheckoutError("current capsule claim transition mismatch")

    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 18:
        raise CleanCheckoutError("current capsule direct-row coverage mismatch")
    source_paths: set[str] = set()
    raw_paths: dict[str, tuple[int, str]] = {}
    raw_rows = 0
    digest_rows = 0
    for row in rows:
        source_path = row.get("source_logical_path")
        disposition = row.get("disposition")
        if (
            not isinstance(source_path, str)
            or not source_path.startswith("Iris/build/description/v2/staging/")
            or source_path in source_paths
            or row.get("predecessor_claim_id") != "raw_repository_evidence_v1"
            or row.get("successor_claim_id") != "current_capsule_attestation_v2"
        ):
            raise CleanCheckoutError("invalid current capsule source row")
        source_paths.add(source_path)
        source_sha256 = row.get("source_sha256")
        source_bytes = row.get("source_bytes")
        if (
            not isinstance(source_sha256, str)
            or len(source_sha256) != 64
            or not isinstance(source_bytes, int)
            or source_bytes < 0
        ):
            raise CleanCheckoutError("invalid current capsule source identity")
        capsule_path = row.get("capsule_path")
        if disposition == "raw_capsule":
            raw_rows += 1
            if (
                not isinstance(capsule_path, str)
                or not capsule_path.startswith(
                    "Iris/validation/clean_checkout/evidence/current_required_v1/objects/"
                )
                or capsule_path not in tracked
            ):
                raise CleanCheckoutError("invalid current capsule raw path")
            existing = raw_paths.setdefault(capsule_path, (source_bytes, source_sha256))
            if existing != (source_bytes, source_sha256):
                raise CleanCheckoutError("current capsule object collision")
        elif disposition == "digest_capsule":
            digest_rows += 1
            if capsule_path is not None:
                raise CleanCheckoutError("digest capsule row retained raw bytes")
        else:
            raise CleanCheckoutError("unsupported current capsule disposition")

    retained_bytes = 0
    for path, (expected_bytes, expected_sha256) in raw_paths.items():
        object_raw = bytes_at_commit(repo, commit, path)
        if len(object_raw) != expected_bytes or sha256_bytes(object_raw) != expected_sha256:
            raise CleanCheckoutError("current capsule object identity mismatch")
        retained_bytes += len(object_raw)
    ceiling = manifest.get("current_capsule_hard_ceiling_bytes")
    if (
        ceiling != 2_359_296
        or retained_bytes != manifest.get("raw_retained_bytes")
        or retained_bytes > ceiling
        or len(raw_paths) != manifest.get("raw_unique_object_count")
        or raw_rows != manifest.get("raw_capsule_row_count")
        or digest_rows != manifest.get("digest_capsule_row_count")
        or raw_rows != 14
        or digest_rows != 4
    ):
        raise CleanCheckoutError("current capsule count or budget mismatch")
    broader = manifest.get("broader_staging_closure", {})
    if (
        broader.get("row_count") != 4645
        or broader.get("raw_capsule_rows") != 14
        or broader.get("digest_capsule_rows") != 3388
        or broader.get("historical_archive_rows") != 1243
        or broader.get("unresolved_blocker") != 0
    ):
        raise CleanCheckoutError("broader staging closure mismatch")

    compiler = g5["compiler_identity"]
    for path in compiler["ordered_paths"]:
        if path not in tracked:
            raise CleanCheckoutError(f"G5 compiler constituent is not tracked: {path}")
    transition_binding = compiler["successor_transition"]
    transition_raw = bytes_at_commit(repo, commit, transition_binding["path"])
    if sha256_bytes(transition_raw) != transition_binding["git_blob_raw_sha256"]:
        raise CleanCheckoutError("G5 compiler successor raw identity mismatch")
    compiler_validation = _validate_g5_compiler_identity_transition(
        repo, commit, compiler, json.loads(transition_raw), True
    )

    required_paths = g5["current_required_paths"]
    if (
        len(required_paths) != len(set(required_paths))
        or manifest_path not in required_paths
        or transition_binding["path"] not in required_paths
        or set(raw_paths) - set(required_paths)
        or any(
            path.startswith("Iris/build/description/v2/staging/")
            or path.startswith("Iris/build/description/v2/tools/")
            for path in required_paths
        )
    ):
        raise CleanCheckoutError("invalid current capsule required-path contract")
    missing = sorted(set(required_paths) - tracked)
    if missing:
        raise CleanCheckoutError(
            "current capsule required path is not tracked: " + ", ".join(missing)
        )
    return {
        "status": "PASS",
        "claim_id": "current_capsule_attestation_v2",
        "capsule_manifest_sha256": raw_sha256,
        "direct_row_count": len(rows),
        "raw_capsule_row_count": raw_rows,
        "digest_capsule_row_count": digest_rows,
        "raw_unique_object_count": len(raw_paths),
        "raw_retained_bytes": retained_bytes,
        "hard_ceiling_bytes": ceiling,
        "broader_staging_row_count": broader["row_count"],
        "compiler_identity": compiler_validation,
        "current_required_path_count": len(required_paths),
        "external_archive_dependency": False,
    }


def _validate_g5_required_evidence(
    repo: Path,
    commit: str,
    contract: dict[str, Any],
    tracked: set[str],
) -> dict[str, Any]:
    if contract["g5_required_evidence"].get("claim_id") == "current_capsule_attestation_v2":
        return _validate_current_capsule_required_evidence(repo, commit, contract, tracked)
    owner_approval = json_at_commit(repo, commit, EVIDENCE_OWNER_APPROVAL_PATH)
    pruned_history = owner_approval["decisions"].get(
        "pruned_git_history_validation"
    )
    allow_owner_pruned_current_basis = bool(
        isinstance(pruned_history, dict)
        and pruned_history.get("approved") is True
        and pruned_history.get("checkpoint_id") == "terminal_successor_c50"
        and pruned_history.get("disposition")
        == "revalidate_recorded_compiler_rows_against_reachable_subject"
    )
    g5 = contract["g5_required_evidence"]
    binding_rows: list[dict[str, Any]] = []
    binding_by_id: dict[str, dict[str, Any]] = {}
    for binding in g5["evidence_bindings"]:
        binding_id = binding["binding_id"]
        path = binding["path"]
        if binding_id in binding_by_id or path not in tracked:
            raise CleanCheckoutError(
                f"invalid or untracked G5 evidence binding: {binding_id}"
            )
        raw = bytes_at_commit(repo, commit, path)
        raw_sha256 = sha256_bytes(raw)
        if raw_sha256 != binding["git_blob_raw_sha256"]:
            raise CleanCheckoutError(
                f"G5 Git-blob raw identity mismatch: {binding_id}"
            )
        hash_mode = binding["hash_mode"]
        if hash_mode == "git_blob_raw_sha256":
            declared_match = raw_sha256 == binding["declared_sha256"]
        elif hash_mode == "line_ending_equivalent_text_sha256_v1":
            declared_match = (
                binding["declared_sha256"]
                in _line_ending_sha256_variants(raw)
            )
        else:
            raise CleanCheckoutError(
                f"unsupported G5 evidence hash mode: {hash_mode}"
            )
        if not declared_match:
            raise CleanCheckoutError(
                f"G5 declared evidence identity mismatch: {binding_id}"
            )
        row = {
            "binding_id": binding_id,
            "path": path,
            "hash_mode": hash_mode,
            "declared_sha256": binding["declared_sha256"],
            "git_blob_raw_sha256": raw_sha256,
            "declared_identity_match": True,
        }
        binding_rows.append(row)
        binding_by_id[binding_id] = binding

    compiler = g5["compiler_identity"]
    for path in compiler["ordered_paths"]:
        if path not in tracked:
            raise CleanCheckoutError(
                f"G5 compiler constituent is not tracked: {path}"
            )
    transition_binding = compiler["successor_transition"]
    if (
        set(transition_binding)
        != {"path", "git_blob_raw_sha256", "hash_mode"}
        or transition_binding["hash_mode"] != "git_blob_raw_sha256"
        or transition_binding["path"] not in tracked
    ):
        raise CleanCheckoutError("invalid G5 compiler successor binding")
    transition_raw = bytes_at_commit(
        repo, commit, transition_binding["path"]
    )
    transition_sha256 = sha256_bytes(transition_raw)
    if transition_sha256 != transition_binding["git_blob_raw_sha256"]:
        raise CleanCheckoutError("G5 compiler successor raw identity mismatch")
    transition = json.loads(transition_raw)
    compiler_validation = _validate_g5_compiler_identity_transition(
        repo,
        commit,
        compiler,
        transition,
        allow_owner_pruned_current_basis,
    )
    compiler_validation["successor_transition"] = {
        "path": transition_binding["path"],
        "git_blob_raw_sha256": transition_sha256,
        "hash_mode": transition_binding["hash_mode"],
        "schema_version": transition["schema_version"],
        "status": transition["status"],
    }
    historical_aggregate_sha256 = compiler_validation[
        "historical_attested_aggregate_sha256"
    ]

    handoff = json_at_commit(
        repo,
        commit,
        binding_by_id["phase8_handoff"]["path"],
    )
    path_constituents = {
        row["path"]: row
        for row in handoff["constituents"]
        if isinstance(row.get("path"), str)
    }
    expected_constituent_paths = set(
        g5["handoff_path_bearing_constituents"]
    )
    if set(path_constituents) != expected_constituent_paths:
        raise CleanCheckoutError(
            "G5 handoff path-bearing constituent set mismatch"
        )
    for path, row in path_constituents.items():
        if path not in tracked:
            raise CleanCheckoutError(
                f"G5 handoff constituent is not tracked: {path}"
            )
        if row["sha256"] not in _line_ending_sha256_variants(
            bytes_at_commit(repo, commit, path)
        ):
            raise CleanCheckoutError(
                f"G5 handoff constituent identity mismatch: {path}"
            )
    handoff_by_id = {row["id"]: row for row in handoff["constituents"]}
    if (
        handoff["naturalization_attempt_id"] != g5["primary_attempt_id"]
        or handoff_by_id["compiler_implementation_hash"]["value"]
        != historical_aggregate_sha256
        or handoff_by_id["candidate_rendered_hash"]["sha256"]
        != binding_by_id["candidate"]["declared_sha256"]
    ):
        raise CleanCheckoutError("G5 handoff binding mismatch")

    phase8_closeout = json_at_commit(
        repo,
        commit,
        binding_by_id["phase8_closeout"]["path"],
    )
    if (
        phase8_closeout["naturalization_attempt_id"]
        != g5["primary_attempt_id"]
        or phase8_closeout["candidate_rendered_sha256"]
        != binding_by_id["candidate"]["declared_sha256"]
        or phase8_closeout["publish_acceptance_handoff_manifest_sha256"]
        != binding_by_id["phase8_handoff"]["declared_sha256"]
    ):
        raise CleanCheckoutError("G5 Phase 8 closeout binding mismatch")

    terminal = json_at_commit(
        repo,
        commit,
        binding_by_id["terminal_closeout"]["path"],
    )
    if (
        terminal["attempts"]["primary"] != g5["primary_attempt_id"]
        or terminal["attempts"]["replay"] != g5["replay_attempt_id"]
        or terminal["compiler_identity"]["aggregate_sha256"]
        != historical_aggregate_sha256
        or terminal["phase0_through_phase6_ab"]["candidate_sha256"]
        != binding_by_id["candidate"]["declared_sha256"]
        or terminal["phase0_through_phase6_ab"]["trace_sha256"]
        != binding_by_id["trace"]["declared_sha256"]
        or terminal["phase8_handoff"]["handoff_sha256"]
        != binding_by_id["phase8_handoff"]["declared_sha256"]
        or terminal["phase8_handoff"]["phase8_closeout_sha256"]
        != binding_by_id["phase8_closeout"]["declared_sha256"]
    ):
        raise CleanCheckoutError("G5 terminal closeout binding mismatch")

    g4_required_paths = g5["g4_required_paths"]
    if (
        len(g4_required_paths) != len(set(g4_required_paths))
        or not expected_constituent_paths.issubset(g4_required_paths)
        or binding_by_id["phase8_handoff"]["path"]
        not in g4_required_paths
        or transition_binding["path"] not in g4_required_paths
    ):
        raise CleanCheckoutError("invalid G5-to-G4 required path contract")
    missing_g4_paths = sorted(set(g4_required_paths) - tracked)
    if missing_g4_paths:
        raise CleanCheckoutError(
            "G5-to-G4 required path is not tracked: "
            + ", ".join(missing_g4_paths)
        )
    return {
        "status": "PASS",
        "primary_attempt_id": g5["primary_attempt_id"],
        "replay_attempt_id": g5["replay_attempt_id"],
        "binding_rows": sorted(
            binding_rows, key=lambda row: row["binding_id"]
        ),
        "compiler_identity": compiler_validation,
        "handoff_path_bearing_constituent_count": len(
            path_constituents
        ),
        "g4_required_path_count": len(g4_required_paths),
        "candidate_trace_handoff_identity": "PASS",
    }
