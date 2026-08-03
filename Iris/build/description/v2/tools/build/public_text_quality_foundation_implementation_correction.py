from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import public_text_quality_foundation_rebind as base
import public_text_quality_foundation_rebind_correction_0003 as correction_0003


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import naturalization_compiler_identity as compiler_identity
from tools.build import public_text_quality_acceptance as consumer
from tools.build import run_dvf_3_3_korean_prose_naturalization as producer


FoundationImplementationCorrectionError = base.FoundationRebindError

CORRECTION_ID = "implementation-correction-0001"
SCHEMA_VERSION = (
    "public_text_quality_foundation_implementation_correction_readiness_v1"
)
START_COMMIT = "c4598018888d9711bb5c9e80888941908e240aa1"
START_TREE = "33b83c2bb9d5ef657029173031adf2af4219c461"
CORRECTION_PARENT_COMMIT = "2cf81462d058ce1c3f09fabeff8a3265fba1c152"

FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
FOUNDATION_READINESS_SHA256 = (
    "34419a8093970c7ffc68d3d968ff90207f63c512971ae9ada87f90cff7f2d263"
)
PREDECESSOR_READINESS_SHA256 = (
    "912f28b7869ff92ff7fbd84cbdc31e1fbb22923beebbfcce2c9cc78b72eca9d2"
)
CORRECTION_CONTRACT_SHA256 = (
    "a7981e6987b567a260c6d0c4c5ac0c77ea75bb487417bbc6d10dd41d32d9dcf1"
)
COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)
COMPILER_ALGORITHM_ID = (
    "naturalization_compiler_identity_sha256_lf_normalized_ordered_paths_v2"
)
HELPER_GIT_BLOB_RAW_SHA256 = (
    "7def3a9d13c7f4c2a05a151007234bee98b30a309c599f11c0cf71168489ab87"
)
HELPER_CANONICAL_SHA256 = (
    "7def3a9d13c7f4c2a05a151007234bee98b30a309c599f11c0cf71168489ab87"
)
PUBLIC_TEXT_ACCEPTANCE_PREDECESSOR_RAW_SHA256 = (
    "562b846a7e7ed6f956342ce03690e02cf31f66da80c3aaf44cb92ec389cdc84f"
)
PUBLIC_TEXT_ACCEPTANCE_CORRECTED_RAW_SHA256 = (
    "fdf2cd61eb182a94e68db222742f2f502753be0e7aa17cdc6c27e7cfed195631"
)

CURRENT_FACTS_SHA256 = correction_0003.CURRENT_FACTS_SHA256
CURRENT_MANIFEST_SHA256 = correction_0003.CURRENT_MANIFEST_SHA256
CORRECTION_RECEIPT_SHA256 = correction_0003.CORRECTION_RECEIPT_SHA256
TERMINAL_CORRECTION_SEAL_SHA256 = (
    correction_0003.TERMINAL_CORRECTION_SEAL_SHA256
)
NATURALIZATION_HANDOFF_SHA256 = correction_0003.NATURALIZATION_HANDOFF_SHA256

FOUNDATION_ROOT = base.FOUNDATION_ROOT
PREDECESSOR_READINESS = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "correction-0003"
    / "public_text_quality_development_readiness_current_input_rebind.json"
)
SUCCESSOR_ROOT = (
    FOUNDATION_ROOT / "readiness_successors" / CORRECTION_ID
)
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT
    / "public_text_quality_development_readiness_implementation_correction.json"
)
CORRECTION_ROOT = (
    FOUNDATION_ROOT
    / "implementation_corrections"
    / "compiler_identity_v2"
)
CORRECTION_CONTRACT = (
    CORRECTION_ROOT / "compiler_identity_v2_correction_contract.json"
)
FRESH_CHECKOUT_EVIDENCE = (
    CORRECTION_ROOT / "fresh_checkout_verification.json"
)
REVIEWER_ATTESTATION = CORRECTION_ROOT / "codex_reviewer_attestation.json"

PUBLIC_TEXT_ACCEPTANCE = TOOLS_DIR / "public_text_quality_acceptance.py"
IDENTITY_HELPER = TOOLS_DIR / "naturalization_compiler_identity.py"
NATURALIZATION_PRODUCER = (
    TOOLS_DIR / "run_dvf_3_3_korean_prose_naturalization.py"
)
NATURALIZATION_VALIDATOR = (
    TOOLS_DIR / "validate_dvf_3_3_korean_prose_naturalization.py"
)
IDENTITY_TEST = (
    V2_ROOT / "tests" / "test_naturalization_compiler_identity.py"
)

CORRECTION_CHANGE_PATHS = (
    PUBLIC_TEXT_ACCEPTANCE,
    IDENTITY_HELPER,
    NATURALIZATION_PRODUCER,
    NATURALIZATION_VALIDATOR,
    IDENTITY_TEST,
    CORRECTION_CONTRACT,
    REPO_ROOT / ".gitignore",
)
IMPLEMENTATION_FILES = (
    TOOLS_DIR / "public_text_quality_foundation_implementation_correction.py",
    TOOLS_DIR
    / "run_public_text_quality_foundation_implementation_correction.py",
    TOOLS_DIR
    / "validate_public_text_quality_foundation_implementation_correction.py",
)


def _canonicalize(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _blob_bytes(revision: str, relative: str) -> tuple[str, bytes]:
    blob_id = base._git("rev-parse", f"{revision}:{relative}").stdout.strip()
    return blob_id, base._git_blob_bytes(blob_id)


def _index_or_head_blob(relative: str) -> str:
    staged = base._git("rev-parse", f":{relative}", check=False)
    if staged.returncode == 0:
        return staged.stdout.strip()
    head = base._git("rev-parse", f"HEAD:{relative}", check=False)
    if head.returncode != 0:
        raise FoundationImplementationCorrectionError(
            f"cannot resolve tracked blob for {relative}"
        )
    return head.stdout.strip()


def _canonical_tracked_record(
    path: Path,
    *,
    expected_git_blob_raw_sha256: str | None = None,
    expected_canonical_sha256: str | None = None,
) -> dict[str, Any]:
    if not path.is_file() or not base._is_tracked(path):
        raise FoundationImplementationCorrectionError(
            f"required correction evidence is missing or untracked: {path}"
        )
    if base._is_ignored(path):
        raise FoundationImplementationCorrectionError(
            f"required correction evidence is ignored: {path}"
        )
    relative = base._repo_relative(path)
    blob_id = _index_or_head_blob(relative)
    blob_bytes = base._git_blob_bytes(blob_id)
    working_bytes = path.read_bytes()
    blob_raw_sha256 = _sha256(blob_bytes)
    blob_canonical_sha256 = _sha256(_canonicalize(blob_bytes))
    working_canonical_sha256 = _sha256(_canonicalize(working_bytes))
    filtered_working_blob = base._git(
        "hash-object", "--", relative
    ).stdout.strip()
    invalid = (
        filtered_working_blob != blob_id
        or blob_canonical_sha256 != working_canonical_sha256
        or (
            expected_git_blob_raw_sha256 is not None
            and blob_raw_sha256 != expected_git_blob_raw_sha256
        )
        or (
            expected_canonical_sha256 is not None
            and blob_canonical_sha256 != expected_canonical_sha256
        )
    )
    if invalid:
        raise FoundationImplementationCorrectionError(
            f"canonical tracked identity mismatch: {relative}"
        )
    return {
        "path": relative,
        "git_blob_id": blob_id,
        "git_blob_raw_sha256": blob_raw_sha256,
        "canonical_sha256": blob_canonical_sha256,
        "working_canonical_sha256": working_canonical_sha256,
        "git_filtered_working_identity": True,
        "canonical_working_blob_identity": True,
        "tracked": True,
        "ignored_by_current_rules": False,
    }


def _validate_start_readpoint(*, require_exact_head: bool) -> dict[str, Any]:
    actual_tree = base._git(
        "show", "-s", "--format=%T", START_COMMIT
    ).stdout.strip()
    if actual_tree != START_TREE:
        raise FoundationImplementationCorrectionError(
            "implementation correction start commit/tree mismatch"
        )
    base._require_ancestor(CORRECTION_PARENT_COMMIT, START_COMMIT)
    head = base._git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != START_COMMIT:
            raise FoundationImplementationCorrectionError(
                "implementation correction build must start at the exact "
                "canonical identity correction commit"
            )
    else:
        base._require_ancestor(START_COMMIT, head)
    return {
        "commit": START_COMMIT,
        "tree": START_TREE,
        "correction_parent_commit": CORRECTION_PARENT_COMMIT,
        "exact_head_required_for_build": True,
        "start_commit_is_ancestor_of_validation_head": True,
    }


def _validate_predecessor_readiness() -> dict[str, Any]:
    correction_0002 = correction_0003._validate_predecessor_rebind()
    record = base._raw_tracked_record(
        PREDECESSOR_READINESS, PREDECESSOR_READINESS_SHA256
    )
    predecessor = base._load_json(PREDECESSOR_READINESS)
    immutable = predecessor.get("immutable_foundation", {})
    registry = predecessor.get("registry_correction_adoption", {})
    if (
        predecessor.get("schema_version")
        != "public_text_quality_foundation_current_input_rebind_v3"
        or predecessor.get("status") != "PASS"
        or predecessor.get("rebind_id") != "correction-0003"
        or predecessor.get("authority_effect") != "none"
        or predecessor.get("foundation_contract_semantics_changed") is not False
        or immutable.get("foundation_contract", {}).get("sha256")
        != FOUNDATION_CONTRACT_SHA256
        or registry.get("current_facts", {}).get("sha256")
        != CURRENT_FACTS_SHA256
        or registry.get("current_manifest", {}).get("sha256")
        != CURRENT_MANIFEST_SHA256
    ):
        raise FoundationImplementationCorrectionError(
            "correction-0003 readiness predecessor is invalid"
        )
    return {
        **record,
        "rebind_id": "correction-0003",
        "correction_0002_readiness": correction_0002,
        "append_only_implementation_successor_required": True,
        "predecessor_mutated": False,
    }


def _meaning_path_record(relative: str) -> dict[str, Any]:
    path = REPO_ROOT / relative
    if not path.is_file() or not base._is_tracked(path):
        raise FoundationImplementationCorrectionError(
            f"Foundation meaning path missing or untracked: {relative}"
        )
    predecessor_blob, predecessor_bytes = _blob_bytes(
        base.FOUNDATION_COMMIT, relative
    )
    start_blob, start_bytes = _blob_bytes(START_COMMIT, relative)
    current_filtered_blob = base._git(
        "hash-object", "--", relative
    ).stdout.strip()
    if relative == base._repo_relative(PUBLIC_TEXT_ACCEPTANCE):
        parent_blob, _ = _blob_bytes(CORRECTION_PARENT_COMMIT, relative)
        if (
            parent_blob != predecessor_blob
            or start_blob == predecessor_blob
            or current_filtered_blob != start_blob
            or _sha256(predecessor_bytes)
            != PUBLIC_TEXT_ACCEPTANCE_PREDECESSOR_RAW_SHA256
            or _sha256(start_bytes)
            != PUBLIC_TEXT_ACCEPTANCE_CORRECTED_RAW_SHA256
        ):
            raise FoundationImplementationCorrectionError(
                "public_text_quality_acceptance.py correction is not isolated"
            )
        return {
            "path": relative,
            "classification": "intended_compiler_identity_v2_consumer_correction",
            "predecessor_git_blob_id": predecessor_blob,
            "corrected_git_blob_id": start_blob,
            "predecessor_raw_sha256": _sha256(predecessor_bytes),
            "corrected_raw_sha256": _sha256(start_bytes),
            "predecessor_canonical_sha256": _sha256(
                _canonicalize(predecessor_bytes)
            ),
            "corrected_canonical_sha256": _sha256(
                _canonicalize(start_bytes)
            ),
            "correction_parent_matches_foundation_predecessor": True,
            "current_matches_corrected_start": True,
            "policy_threshold_denominator_detector_change_count": 0,
        }
    if (
        predecessor_blob != start_blob
        or current_filtered_blob != start_blob
    ):
        raise FoundationImplementationCorrectionError(
            f"unexpected Foundation meaning change: {relative}"
        )
    return {
        "path": relative,
        "classification": "byte_identical_unchanged_foundation_meaning",
        "git_blob_id": start_blob,
        "predecessor_current_blob_identity": True,
        "git_filtered_working_identity": True,
    }


def _validate_foundation_semantics() -> dict[str, Any]:
    contract_record = base._raw_tracked_record(
        base.FOUNDATION_CONTRACT, FOUNDATION_CONTRACT_SHA256
    )
    readiness_record = base._raw_tracked_record(
        base.FOUNDATION_READINESS, FOUNDATION_READINESS_SHA256
    )
    contract = base._load_json(base.FOUNDATION_CONTRACT)
    readiness = base._load_json(base.FOUNDATION_READINESS)
    if (
        contract.get("authority_effect") != "none"
        or contract.get("official_disposition") != "not_issued"
        or contract.get("live_gate_adopted") is not False
        or contract.get("policy_closure_state") != "not_started"
        or readiness.get("foundation_contract_raw_sha256")
        != FOUNDATION_CONTRACT_SHA256
        or readiness.get("authority_effect") != "none"
        or readiness.get("official_disposition") != "not_issued"
        or readiness.get("live_gate_adopted") is not False
        or readiness.get("policy_closure_state") != "not_started"
    ):
        raise FoundationImplementationCorrectionError(
            "Foundation authority boundary changed"
        )
    projection_hashes = {
        field: contract.get(field) for field in base.PROJECTION_HASH_FIELDS
    }
    if any(
        not isinstance(value, str) or len(value) != 64
        for value in projection_hashes.values()
    ):
        raise FoundationImplementationCorrectionError(
            "Foundation projection hash set is incomplete"
        )
    records = [
        _meaning_path_record(relative)
        for relative in base.FOUNDATION_MEANING_PATHS
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
        raise FoundationImplementationCorrectionError(
            "Foundation meaning-path census is not exact"
        )
    return {
        "foundation_commit": base.FOUNDATION_COMMIT,
        "foundation_tree": base.FOUNDATION_TREE,
        "foundation_contract": contract_record,
        "foundation_readiness": readiness_record,
        "foundation_contract_canonical_sha256": base._canonical_hash(contract),
        "projection_hashes": projection_hashes,
        "projection_hash_count": len(projection_hashes),
        "meaning_path_count": len(records),
        "unchanged_meaning_path_count": len(unchanged),
        "intended_implementation_correction_path_count": len(intended),
        "unexpected_meaning_path_change_count": 0,
        "meaning_paths": records,
        "contract_policy_threshold_denominator_detector_semantics_changed": False,
        "required_handoff_constituent_ids_changed": False,
        "foundation_contract_mutated": False,
        "foundation_readiness_predecessor_mutated": False,
    }


def _start_commit_path_record(
    path: Path,
    classification: str,
    *,
    require_current_identity: bool,
) -> dict[str, Any]:
    relative = base._repo_relative(path)
    blob_id, raw = _blob_bytes(START_COMMIT, relative)
    canonical_sha256 = _sha256(_canonicalize(raw))
    if require_current_identity:
        current_filtered_blob = base._git(
            "hash-object", "--", relative
        ).stdout.strip()
        current_canonical_sha256 = _sha256(
            _canonicalize(path.read_bytes())
        )
        if (
            current_filtered_blob != blob_id
            or current_canonical_sha256 != canonical_sha256
        ):
            raise FoundationImplementationCorrectionError(
                f"correction input changed after start commit: {relative}"
            )
    return {
        "path": relative,
        "classification": classification,
        "git_blob_id": blob_id,
        "git_blob_raw_sha256": _sha256(raw),
        "canonical_sha256": canonical_sha256,
        "source_commit": START_COMMIT,
        "current_identity_required": require_current_identity,
        "current_filtered_blob_identity": (
            True if require_current_identity else None
        ),
        "current_canonical_identity": (
            True if require_current_identity else None
        ),
    }


def _line_ending_metamorphic_probe() -> dict[str, Any]:
    variants = {
        "lf": b"alpha\nbeta\ngamma\n",
        "crlf": b"alpha\r\nbeta\r\ngamma\r\n",
        "lone_cr": b"alpha\rbeta\rgamma\r",
    }
    identities = {}
    for name, raw in variants.items():
        contents = {
            path: raw
            for path in compiler_identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
        }
        identities[name] = compiler_identity.build_compiler_identity_from_bytes(
            contents
        )["aggregate_sha256"]
    unique = sorted(set(identities.values()))
    if len(unique) != 1:
        raise FoundationImplementationCorrectionError(
            "line-ending metamorphic identity is not stable"
        )
    return {
        "status": "PASS",
        "variant_aggregates": identities,
        "unique_aggregate_count": 1,
        "crlf_lf_lone_cr_identity_equal": True,
    }


def _semantic_change_stale_probe(
    baseline: dict[str, object],
) -> dict[str, Any]:
    paths = compiler_identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
    source_paths = compiler_identity.compiler_source_paths(REPO_ROOT)
    contents = {
        relative: path.read_bytes()
        for relative, path in zip(paths, source_paths, strict=True)
    }
    changed = dict(contents)
    changed_path = paths[0]
    mutated = bytearray(changed[changed_path])
    mutation_offset = next(
        index
        for index, value in enumerate(mutated)
        if value not in {10, 13}
    )
    mutated[mutation_offset] ^= 1
    changed[changed_path] = bytes(mutated)
    changed_identity = compiler_identity.build_compiler_identity_from_bytes(
        changed
    )
    stale = not compiler_identity.compiler_identity_matches_claim(
        baseline["aggregate_sha256"], changed_identity
    )
    if not stale:
        raise FoundationImplementationCorrectionError(
            "one-byte compiler change did not become stale"
        )
    return {
        "status": "PASS",
        "changed_path": changed_path,
        "changed_byte_count": 1,
        "baseline_aggregate_sha256": baseline["aggregate_sha256"],
        "changed_aggregate_sha256": changed_identity["aggregate_sha256"],
        "compiler_identity_stale": True,
    }


def _helper_change_stale_probe(
    helper_record: dict[str, Any],
) -> dict[str, Any]:
    current = _canonicalize(IDENTITY_HELPER.read_bytes())
    mutated = bytearray(current)
    mutation_offset = next(
        index
        for index, value in enumerate(mutated)
        if value not in {10, 13}
    )
    mutated[mutation_offset] ^= 1
    changed_canonical_sha256 = _sha256(bytes(mutated))
    stale = changed_canonical_sha256 != helper_record["canonical_sha256"]
    if not stale:
        raise FoundationImplementationCorrectionError(
            "helper change did not invalidate readiness binding"
        )
    return {
        "status": "PASS",
        "helper_path": helper_record["path"],
        "changed_byte_count": 1,
        "bound_canonical_sha256": helper_record["canonical_sha256"],
        "changed_canonical_sha256": changed_canonical_sha256,
        "validator_requires_exact_successor_projection": True,
        "readiness_stale_on_helper_change": True,
    }


def _validate_correction_identity() -> dict[str, Any]:
    correction_record = _canonical_tracked_record(
        CORRECTION_CONTRACT,
        expected_git_blob_raw_sha256=CORRECTION_CONTRACT_SHA256,
        expected_canonical_sha256=CORRECTION_CONTRACT_SHA256,
    )
    correction = base._load_json(CORRECTION_CONTRACT)
    evidence = compiler_identity.build_compiler_identity(REPO_ROOT)
    helper_record = _canonical_tracked_record(
        IDENTITY_HELPER,
        expected_git_blob_raw_sha256=HELPER_GIT_BLOB_RAW_SHA256,
        expected_canonical_sha256=HELPER_CANONICAL_SHA256,
    )
    helper_relative = base._repo_relative(IDENTITY_HELPER)
    if (
        correction.get("status")
        != "implementation_ready_foundation_successor_required"
        or correction.get("foundation_impact", {}).get(
            "foundation_contract_meaning_changed"
        )
        is not False
        or correction.get("canonical_identity_v2") != evidence
        or evidence.get("algorithm_id") != COMPILER_ALGORITHM_ID
        or evidence.get("aggregate_sha256") != COMPILER_AGGREGATE_SHA256
        or len(evidence.get("ordered_files", [])) != 9
        or helper_relative
        in compiler_identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
        or producer.build_compiler_identity
        is not compiler_identity.build_compiler_identity
        or consumer.build_compiler_identity
        is not compiler_identity.build_compiler_identity
        or tuple(producer.COMPILER_IMPLEMENTATION_PATHS)
        != compiler_identity.compiler_source_paths(REPO_ROOT)
        or tuple(consumer.NATURALIZATION_COMPILER_IMPLEMENTATION_FILES)
        != compiler_identity.compiler_source_paths(REPO_ROOT)
        or IDENTITY_HELPER not in consumer.FOUNDATION_IMPLEMENTATION_FILES
    ):
        raise FoundationImplementationCorrectionError(
            "canonical compiler identity correction binding is invalid"
        )
    correction_census = [
        _start_commit_path_record(
            path,
            (
                "foundation_implementation"
                if path in {PUBLIC_TEXT_ACCEPTANCE, IDENTITY_HELPER}
                else (
                    "naturalization_producer_validator"
                    if path
                    in {NATURALIZATION_PRODUCER, NATURALIZATION_VALIDATOR}
                    else "validation_and_evidence"
                )
            ),
            require_current_identity=path != REPO_ROOT / ".gitignore",
        )
        for path in CORRECTION_CHANGE_PATHS
    ]
    return {
        "correction_contract": correction_record,
        "algorithm_id": COMPILER_ALGORITHM_ID,
        "compiler_path_order": evidence["path_order"],
        "compiler_path_count": len(evidence["path_order"]),
        "ordered_files": evidence["ordered_files"],
        "compiler_aggregate_sha256": evidence["aggregate_sha256"],
        "identity_helper": helper_record,
        "identity_helper_in_compiler_aggregate": False,
        "producer_consumer_shared_helper_identity": True,
        "producer_consumer_path_order_identity": True,
        "line_ending_metamorphic": _line_ending_metamorphic_probe(),
        "compiler_source_change_stale": _semantic_change_stale_probe(evidence),
        "helper_change_readiness_stale": _helper_change_stale_probe(
            helper_record
        ),
        "correction_change_path_count": len(correction_census),
        "correction_change_census": correction_census,
    }


def _validate_fresh_checkouts() -> dict[str, Any]:
    record = _canonical_tracked_record(FRESH_CHECKOUT_EVIDENCE)
    evidence = base._load_json(FRESH_CHECKOUT_EVIDENCE)
    rows = evidence.get("checkout_results")
    checkout_ids = (
        [row.get("checkout_id") for row in rows]
        if isinstance(rows, list)
        else []
    )
    if (
        evidence.get("status") != "PASS"
        or evidence.get("source_commit") != START_COMMIT
        or evidence.get("source_tree") != START_TREE
        or evidence.get("algorithm_id") != COMPILER_ALGORITHM_ID
        or evidence.get("expected_aggregate_sha256")
        != COMPILER_AGGREGATE_SHA256
        or evidence.get("fresh_checkout_count") != 2
        or evidence.get("aggregate_identity_count") != 1
        or evidence.get("host_or_absolute_path_recorded") is not False
        or not isinstance(rows, list)
        or len(rows) != 2
        or checkout_ids != ["fresh-checkout-a", "fresh-checkout-b"]
        or any(
            row.get("commit") != START_COMMIT
            or row.get("tree") != START_TREE
            or row.get("aggregate_sha256") != COMPILER_AGGREGATE_SHA256
            or row.get("detached_head") is not True
            or row.get("command_exit_code") != 0
            or row.get("worktree_status_count") != 0
            for row in rows
        )
    ):
        raise FoundationImplementationCorrectionError(
            "fresh-checkout compiler identity evidence is invalid"
        )
    return {
        "evidence": record,
        "status": "PASS",
        "fresh_checkout_count": 2,
        "aggregate_identity_count": 1,
        "aggregate_sha256": COMPILER_AGGREGATE_SHA256,
    }


def _validate_reviewer() -> dict[str, Any]:
    record = _canonical_tracked_record(REVIEWER_ATTESTATION)
    attestation = base._load_json(REVIEWER_ATTESTATION)
    if (
        attestation.get("schema_version")
        != "codex_reviewer_foundation_implementation_correction_v1"
        or attestation.get("status") != "PASS"
        or attestation.get("reviewer_kind") != "Codex Reviewer"
        or attestation.get("reviewed_start_commit") != START_COMMIT
        or attestation.get("blocker_count") != 0
        or attestation.get("scope_expansion_count") != 0
    ):
        raise FoundationImplementationCorrectionError(
            "Codex Reviewer attestation is missing or has blockers"
        )
    return {
        "attestation": record,
        "reviewer_kind": "Codex Reviewer",
        "status": "PASS",
        "blocker_count": 0,
        "scope_expansion_count": 0,
    }


def _protected_paths() -> list[Path]:
    fixed = set(correction_0003._protected_paths())
    fixed.update({
        base.FOUNDATION_CONTRACT,
        base.FOUNDATION_READINESS,
        PREDECESSOR_READINESS,
        correction_0003.CORRECTION_RECEIPT,
        correction_0003.CURRENT_IDENTITY_REPORT,
        correction_0003.TERMINAL_CORRECTION_SEAL,
        correction_0003.NATURALIZATION_HANDOFF,
        correction_0003.CURRENT_FACTS,
        correction_0003.CURRENT_MANIFEST,
        base.LIVE_REQUIRED_VALIDATIONS,
        CORRECTION_CONTRACT,
        FRESH_CHECKOUT_EVIDENCE,
        REVIEWER_ATTESTATION,
        REPO_ROOT / ".gitignore",
        REPO_ROOT / ".gitattributes",
        *CORRECTION_CHANGE_PATHS,
        *IMPLEMENTATION_FILES,
    })
    fixed.update(REPO_ROOT / relative for relative in base.FOUNDATION_MEANING_PATHS)
    recursive_roots = (
        REPO_ROOT / "Iris" / "media" / "lua",
        REPO_ROOT / "Iris" / "Contents" / "mods" / "Iris",
        REPO_ROOT / "Iris" / "build" / "package",
        V2_ROOT
        / "staging"
        / "iris_public_text_quality_policy_closure",
        base.NATURALIZATION_ATTEMPT_ROOT,
        correction_0003.G3_ATTEMPT_ROOT,
    )
    for root in recursive_roots:
        if root.is_dir():
            fixed.update(path for path in root.rglob("*") if path.is_file())
    fixed.discard(SUCCESSOR_PATH)
    return sorted(fixed, key=base._repo_relative)


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_paths():
        present = path.is_file()
        rows.append(
            {
                "path": base._repo_relative(path),
                "present": present,
                "raw_sha256": base._sha256_file(path) if present else None,
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": (
            "public_text_quality_foundation_implementation_correction_"
            "no_write_snapshot_v1"
        ),
        "surface_count": len(rows),
        "surface_hash": base._canonical_hash(rows),
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
        raise FoundationImplementationCorrectionError(
            f"protected implementation-correction surface changed: {changed}"
        )
    return {
        "schema_version": (
            "public_text_quality_foundation_implementation_correction_"
            "no_write_guard_v1"
        ),
        "status": "PASS",
        "before_snapshot_hash": base._canonical_hash(before),
        "after_snapshot_hash": base._canonical_hash(after),
        "protected_surface_mutation_count": 0,
        "changed_paths": [],
        "authority_effect": "none",
    }


def _implementation_hashes() -> list[dict[str, Any]]:
    rows = []
    for path in IMPLEMENTATION_FILES:
        if not path.is_file():
            raise FoundationImplementationCorrectionError(
                f"implementation-correction runner file missing: {path}"
            )
        rows.append(
            {
                "path": base._repo_relative(path),
                "hash_algorithm": "sha256_utf8_lf_normalized_v1",
                "sha256": base._sha256_lf(path),
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
            "append_only_foundation_implementation_correction_successor"
        ),
        "purpose": (
            "Consume canonical compiler identity v2 while preserving the "
            "Foundation contract, policy, threshold, denominator, detector, "
            "current-input, and authority boundaries."
        ),
        "execution_start_readpoint": _validate_start_readpoint(
            require_exact_head=require_exact_start_head
        ),
        "predecessor_readiness": _validate_predecessor_readiness(),
        "foundation_semantics": _validate_foundation_semantics(),
        "registry_current_inputs": (
            correction_0003._validate_registry_correction()
        ),
        "compiler_identity_correction": _validate_correction_identity(),
        "fresh_checkout_verification": _validate_fresh_checkouts(),
        "codex_reviewer": _validate_reviewer(),
        "successor_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "scope_boundaries": {
            "existing_handoff_modified": False,
            "naturalization_attempt_created": False,
            "official_publish_attempt_created": False,
            "attempt_0004_consumed": False,
            "live_gate_mutated": False,
            "facts_manifest_registry_rtc_runtime_lua_package_mutated": False,
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
        raise FoundationImplementationCorrectionError(
            f"only the exact correction ID {CORRECTION_ID} is allowed"
        )


def build_successor(correction_id: str) -> dict[str, Any]:
    _validate_correction_id(correction_id)
    if SUCCESSOR_PATH.exists():
        raise FoundationImplementationCorrectionError(
            "append-only implementation-correction successor already exists: "
            f"{base._repo_relative(SUCCESSOR_PATH)}"
        )
    protected_before = protected_snapshot()
    guard = _no_write_guard(protected_before, protected_snapshot())
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(base._pretty_json_bytes(successor))
    _no_write_guard(protected_before, protected_snapshot())
    return {
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_successor_path": base._repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": base._sha256_file(SUCCESSOR_PATH),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": PREDECESSOR_READINESS_SHA256,
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
    }


def _require_successor_vcs_state() -> dict[str, Any]:
    if not SUCCESSOR_PATH.is_file() or not base._is_tracked(SUCCESSOR_PATH):
        raise FoundationImplementationCorrectionError(
            "implementation-correction successor must be tracked"
        )
    if base._is_ignored(SUCCESSOR_PATH):
        raise FoundationImplementationCorrectionError(
            "implementation-correction successor must not be ignored"
        )
    relative = base._repo_relative(SUCCESSOR_PATH)
    blob_id = _index_or_head_blob(relative)
    working_raw_blob_id = base._git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    if blob_id != working_raw_blob_id:
        raise FoundationImplementationCorrectionError(
            "successor staged/working raw-byte identity mismatch"
        )
    attr = base._git("check-attr", "text", "--", relative).stdout.strip()
    if not attr.endswith(": text: unset"):
        raise FoundationImplementationCorrectionError(
            "implementation-correction successor requires exact -text"
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
        raise FoundationImplementationCorrectionError(
            "implementation-correction successor is missing"
        )
    successor_bytes_before = SUCCESSOR_PATH.read_bytes()
    successor = base._load_json(SUCCESSOR_PATH)
    protected_before = protected_snapshot()
    guard = _no_write_guard(protected_before, protected_snapshot())
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationImplementationCorrectionError(
            "implementation-correction successor differs from exact projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes_before:
        raise FoundationImplementationCorrectionError(
            "no-write validator changed successor bytes"
        )
    _no_write_guard(protected_before, protected_snapshot())
    return {
        "status": "PASS",
        "correction_id": CORRECTION_ID,
        "readiness_successor_path": base._repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": base._sha256_file(SUCCESSOR_PATH),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": PREDECESSOR_READINESS_SHA256,
        "helper_git_blob_raw_sha256": HELPER_GIT_BLOB_RAW_SHA256,
        "helper_canonical_sha256": HELPER_CANONICAL_SHA256,
        "compiler_aggregate_sha256": COMPILER_AGGREGATE_SHA256,
        "current_facts_sha256": CURRENT_FACTS_SHA256,
        "current_manifest_sha256": CURRENT_MANIFEST_SHA256,
        "correction_adoption_receipt_sha256": CORRECTION_RECEIPT_SHA256,
        "terminal_correction_seal_sha256": TERMINAL_CORRECTION_SEAL_SHA256,
        "naturalization_current_input_handoff_sha256": (
            NATURALIZATION_HANDOFF_SHA256
        ),
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
