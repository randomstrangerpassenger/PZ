from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]

REBIND_ID = "correction-0002"
SCHEMA_VERSION = "public_text_quality_foundation_current_input_rebind_v2"
START_COMMIT = "80bd00cfedb22bb2ae9ab1d0860706b2cbbe5967"
START_TREE = "396c35dedf2892ba2914079532ecae9513210ec9"
FOUNDATION_COMMIT = "93db1acbfe31949760acef8e388ad07708e54e57"
FOUNDATION_TREE = "19f522a0d47e295bbbfc84644bf0edeb0c30c0f9"
FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
FOUNDATION_READINESS_SHA256 = (
    "34419a8093970c7ffc68d3d968ff90207f63c512971ae9ada87f90cff7f2d263"
)
PREDECESSOR_REBIND_SHA256 = (
    "271121b8cb71614f44620934e7c077bfb9ca863a66e135049164234262e89234"
)
CURRENT_FACTS_SHA256 = (
    "37db2595eff9b58f7b08e59221e950cb529453bd96733fb29171d458e46118f6"
)
CURRENT_MANIFEST_SHA256 = (
    "a105e3790896b30bc25e95839ceb0ee4c88357fed98ec9fa4258790bf0733a1f"
)
ADOPTION_COMMIT = "b1a39deeb5aabec208efdffa0804d3eb5a34aca2"
ADOPTION_TREE = "94d57eb6f0eb48ec0730f35ea99036cf4da37e63"
CORRECTION_RECEIPT_SHA256 = (
    "475239fba798104371d2c9f4fb166c46ceab15bb462015493238a4aff4656f7f"
)
CURRENT_IDENTITY_REPORT_SHA256 = (
    "e194833e73c563edc5345d47cf74924788f133e2a34648ee8af766923e0daa65"
)
TERMINAL_CORRECTION_SEAL_SHA256 = (
    "b54cca40e1dcbf4d279d878a6fba42e244311b33691eb27054d0881ff4682a52"
)
NATURALIZATION_HANDOFF_SHA256 = (
    "6fa93017f037d3ffd5520a9da5ce1c2afdc97c3824de6ce00015e08aca4f068c"
)

FOUNDATION_ROOT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "foundation"
)
FOUNDATION_CONTRACT = FOUNDATION_ROOT / "public_text_quality_foundation_contract.json"
FOUNDATION_READINESS = (
    FOUNDATION_ROOT / "public_text_quality_development_readiness_report.json"
)
PREDECESSOR_REBIND = (
    FOUNDATION_ROOT / "public_text_quality_development_readiness_correction_rebind.json"
)
SUCCESSOR_ROOT = FOUNDATION_ROOT / "readiness_successors" / REBIND_ID
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT
    / "public_text_quality_development_readiness_current_input_rebind.json"
)

G3_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0011"
)
CORRECTION_RECEIPT = (
    G3_ATTEMPT_ROOT / "closeout" / "registry_correction_adoption_receipt.json"
)
CURRENT_IDENTITY_REPORT = (
    G3_ATTEMPT_ROOT / "closeout" / "current_correction_identity_report.json"
)
TERMINAL_CORRECTION_SEAL = (
    G3_ATTEMPT_ROOT / "closeout" / "terminal_correction_hash_seal.json"
)
NATURALIZATION_HANDOFF = (
    G3_ATTEMPT_ROOT / "handoff" / "naturalization_current_input_handoff.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
LIVE_REQUIRED_VALIDATIONS = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
)
NATURALIZATION_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
)

FOUNDATION_MEANING_PATHS = (
    "Iris/build/description/v2/tools/build/public_text_quality_acceptance.py",
    "Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py",
    "Iris/build/description/v2/tools/build/validate_public_text_quality_acceptance.py",
    "Iris/build/description/v2/tests/test_public_text_quality_metric_contract.py",
    "Iris/build/description/v2/tests/test_public_text_quality_acceptance_policy.py",
    "Iris/build/description/v2/tests/test_public_text_quality_acceptance.py",
    "Iris/build/description/v2/tests/test_public_text_quality_acceptance_fixtures.py",
    "Iris/build/description/v2/tests/fixtures/public_text_quality_acceptance/foundation_fixtures.json",
    "docs/public_text_quality_metric_contract.md",
    "docs/public_text_quality_denominator_contract.md",
    "docs/public_text_quality_acceptance_policy.md",
    "docs/public_text_quality_acceptance_claim_boundary.md",
    "docs/public_text_quality_exception_policy.md",
    "docs/public_text_quality_waiver_policy.md",
    "docs/public_text_quality_freshness_policy.md",
    "Iris/_docs/round3/iris_publish_boundary_public_text_quality_acceptance_policy_closure/foundation/public_text_quality_foundation_contract.json",
    "Iris/_docs/round3/iris_publish_boundary_public_text_quality_acceptance_policy_closure/foundation/public_text_quality_development_readiness_report.json",
)
IMPLEMENTATION_FILES = (
    TOOLS_DIR / "public_text_quality_foundation_rebind.py",
    TOOLS_DIR / "run_public_text_quality_foundation_rebind.py",
    TOOLS_DIR / "validate_public_text_quality_foundation_rebind.py",
)
PROJECTION_HASH_FIELDS = (
    "upstream_prerequisite_binding_hash",
    "metric_registry_candidate_hash",
    "denominator_registry_candidate_hash",
    "policy_candidate_hash",
    "detector_mapping_candidate_hash",
    "human_review_selection_contract_hash",
    "runner_validator_interface_hash",
    "required_handoff_schema_hash",
    "freshness_contract_hash",
    "synchronization_projection_hash",
)


class FoundationRebindError(RuntimeError):
    pass


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
        raise FoundationRebindError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result


def _git_blob_bytes(blob_id: str) -> bytes:
    result = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationRebindError(f"cannot read Git blob {blob_id}")
    return result.stdout


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise FoundationRebindError(f"cannot hash {path}: {exc}") from exc


def _sha256_lf(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise FoundationRebindError(f"cannot read UTF-8 text {path}: {exc}") from exc
    return _sha256_bytes(
        text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    )


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FoundationRebindError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FoundationRebindError(f"JSON root must be an object: {path}")
    return value


def _pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _canonical_hash(value: Any) -> str:
    return _sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def _is_tracked(path: Path) -> bool:
    return (
        _git(
            "ls-files",
            "--error-unmatch",
            "--",
            _repo_relative(path),
            check=False,
        ).returncode
        == 0
    )


def _is_ignored(path: Path) -> bool:
    result = _git(
        "check-ignore",
        "--no-index",
        "-v",
        "--",
        _repo_relative(path),
        check=False,
    )
    if result.returncode != 0:
        return False
    matched_rule = result.stdout.split("\t", 1)[0].rsplit(":", 1)[-1]
    return not matched_rule.startswith("!")


def _require_ancestor(commit: str, descendant: str) -> None:
    result = _git("merge-base", "--is-ancestor", commit, descendant, check=False)
    if result.returncode != 0:
        raise FoundationRebindError(
            f"required ancestor relationship missing: {commit} -> {descendant}"
        )


def _validate_start_readpoint(*, require_exact_head: bool) -> dict[str, Any]:
    actual_tree = _git("show", "-s", "--format=%T", START_COMMIT).stdout.strip()
    if actual_tree != START_TREE:
        raise FoundationRebindError("rebind start commit/tree mismatch")
    head = _git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != START_COMMIT:
            raise FoundationRebindError(
                "rebind build must start at the exact correction-0002 closeout commit"
            )
    else:
        _require_ancestor(START_COMMIT, head)
    return {
        "commit": START_COMMIT,
        "tree": START_TREE,
        "exact_head_required_for_build": True,
        "start_commit_is_ancestor_of_validation_head": True,
    }


def _raw_tracked_record(path: Path, expected_sha256: str) -> dict[str, Any]:
    if not path.is_file() or not _is_tracked(path):
        raise FoundationRebindError(
            f"required raw prerequisite is missing or untracked: {_repo_relative(path)}"
        )
    relative = _repo_relative(path)
    head_blob_id = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    working_raw_blob_id = _git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    working_sha256 = _sha256_file(path)
    git_blob_sha256 = _sha256_bytes(_git_blob_bytes(head_blob_id))
    if (
        working_sha256 != expected_sha256
        or git_blob_sha256 != expected_sha256
        or working_raw_blob_id != head_blob_id
    ):
        raise FoundationRebindError(
            f"raw Git/working identity mismatch: {relative}"
        )
    return {
        "path": relative,
        "sha256": expected_sha256,
        "git_blob_id": head_blob_id,
        "git_blob_sha256": git_blob_sha256,
        "working_raw_blob_id": working_raw_blob_id,
        "git_blob_working_byte_identity": True,
        "tracked": True,
        "ignored_by_current_rules": _is_ignored(path),
    }


def _filtered_tracked_record(
    path: Path, expected_working_raw_sha256: str
) -> dict[str, Any]:
    if not path.is_file() or not _is_tracked(path):
        raise FoundationRebindError(
            f"required filtered prerequisite is missing or untracked: {_repo_relative(path)}"
        )
    relative = _repo_relative(path)
    head_blob_id = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    filtered_working_blob_id = _git("hash-object", "--", relative).stdout.strip()
    working_raw_sha256 = _sha256_file(path)
    if (
        filtered_working_blob_id != head_blob_id
        or working_raw_sha256 != expected_working_raw_sha256
    ):
        raise FoundationRebindError(
            f"filtered Git/working identity mismatch: {relative}"
        )
    return {
        "path": relative,
        "working_raw_sha256": working_raw_sha256,
        "git_blob_id": head_blob_id,
        "git_blob_sha256": _sha256_bytes(_git_blob_bytes(head_blob_id)),
        "filtered_working_blob_id": filtered_working_blob_id,
        "git_filtered_working_identity": True,
        "tracked": True,
        "ignored_by_current_rules": _is_ignored(path),
    }


def _foundation_meaning_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative in FOUNDATION_MEANING_PATHS:
        path = REPO_ROOT / relative
        if not path.is_file() or not _is_tracked(path):
            raise FoundationRebindError(
                f"immutable Foundation meaning path missing or untracked: {relative}"
            )
        predecessor_blob = _git(
            "rev-parse", f"{FOUNDATION_COMMIT}:{relative}"
        ).stdout.strip()
        current_blob = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
        filtered_working_blob = _git("hash-object", "--", relative).stdout.strip()
        if predecessor_blob != current_blob or filtered_working_blob != current_blob:
            raise FoundationRebindError(
                f"immutable Foundation meaning changed: {relative}"
            )
        records.append(
            {
                "path": relative,
                "git_blob_id": current_blob,
                "predecessor_current_blob_identity": True,
                "git_filtered_working_identity": True,
            }
        )
    return records


def _validate_immutable_foundation() -> dict[str, Any]:
    tree = _git("show", "-s", "--format=%T", FOUNDATION_COMMIT).stdout.strip()
    if tree != FOUNDATION_TREE:
        raise FoundationRebindError("immutable Foundation commit/tree mismatch")
    _require_ancestor(FOUNDATION_COMMIT, START_COMMIT)
    contract_record = _raw_tracked_record(
        FOUNDATION_CONTRACT, FOUNDATION_CONTRACT_SHA256
    )
    readiness_record = _raw_tracked_record(
        FOUNDATION_READINESS, FOUNDATION_READINESS_SHA256
    )
    contract = _load_json(FOUNDATION_CONTRACT)
    readiness = _load_json(FOUNDATION_READINESS)
    if (
        contract.get("foundation_contract_version") != "2.0.0"
        or contract.get("authority_effect") != "none"
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
        raise FoundationRebindError("immutable Foundation authority boundary mismatch")
    projection_hashes = {
        field: contract.get(field) for field in PROJECTION_HASH_FIELDS
    }
    if any(
        not isinstance(value, str) or len(value) != 64
        for value in projection_hashes.values()
    ):
        raise FoundationRebindError("immutable Foundation projection hashes missing")
    meaning_records = _foundation_meaning_records()
    return {
        "foundation_commit": FOUNDATION_COMMIT,
        "foundation_tree": FOUNDATION_TREE,
        "foundation_contract": contract_record,
        "foundation_contract_canonical_sha256": _canonical_hash(contract),
        "foundation_readiness": readiness_record,
        "projection_hashes": projection_hashes,
        "projection_hash_count": len(projection_hashes),
        "meaning_path_count": len(meaning_records),
        "meaning_path_mismatch_count": 0,
        "meaning_paths": meaning_records,
        "foundation_contract_mutated": False,
        "foundation_readiness_mutated": False,
        "foundation_meaning_changed": False,
    }


def _validate_predecessor_rebind() -> dict[str, Any]:
    record = _filtered_tracked_record(
        PREDECESSOR_REBIND, PREDECESSOR_REBIND_SHA256
    )
    predecessor = _load_json(PREDECESSOR_REBIND)
    immutable = predecessor.get("immutable_foundation", {})
    if (
        predecessor.get("schema_version")
        != "dvf-3-3-g4-development-readiness-correction-rebind-v1"
        or predecessor.get("status") != "PASS"
        or predecessor.get("rebind_id") != "correction-0001"
        or immutable.get("foundation_contract_sha256")
        != FOUNDATION_CONTRACT_SHA256
        or immutable.get("foundation_readiness_sha256")
        != FOUNDATION_READINESS_SHA256
    ):
        raise FoundationRebindError("predecessor correction rebind is invalid")
    return {
        **record,
        "rebind_id": "correction-0001",
        "append_only_successor_required": True,
        "predecessor_mutated": False,
    }


def _validate_registry_correction() -> dict[str, Any]:
    receipt_record = _raw_tracked_record(
        CORRECTION_RECEIPT, CORRECTION_RECEIPT_SHA256
    )
    identity_record = _raw_tracked_record(
        CURRENT_IDENTITY_REPORT, CURRENT_IDENTITY_REPORT_SHA256
    )
    terminal_record = _raw_tracked_record(
        TERMINAL_CORRECTION_SEAL, TERMINAL_CORRECTION_SEAL_SHA256
    )
    handoff_record = _raw_tracked_record(
        NATURALIZATION_HANDOFF, NATURALIZATION_HANDOFF_SHA256
    )
    facts_record = _raw_tracked_record(CURRENT_FACTS, CURRENT_FACTS_SHA256)
    manifest_record = _raw_tracked_record(
        CURRENT_MANIFEST, CURRENT_MANIFEST_SHA256
    )
    receipt = _load_json(CORRECTION_RECEIPT)
    identity = _load_json(CURRENT_IDENTITY_REPORT)
    terminal = _load_json(TERMINAL_CORRECTION_SEAL)
    handoff = _load_json(NATURALIZATION_HANDOFF)
    manifest = _load_json(CURRENT_MANIFEST)
    actual_adoption_tree = _git(
        "show", "-s", "--format=%T", ADOPTION_COMMIT
    ).stdout.strip()
    _require_ancestor(ADOPTION_COMMIT, START_COMMIT)
    correction_binding = (
        manifest.get("source_promotion", {})
        .get("current_facts_correction_adoption_0002_binding", {})
    )
    food_authority = manifest.get("food_semantic_authority", {})
    invalid = (
        actual_adoption_tree != ADOPTION_TREE
        or receipt.get("schema_version")
        != "dvf-3-3-registry-correction-adoption-receipt-v2"
        or receipt.get("status") != "PASS"
        or receipt.get("attempt_id") != "attempt-0011"
        or receipt.get("successor_id") != REBIND_ID
        or receipt.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or receipt.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or receipt.get("forbidden_scope_execution_count") != 0
        or identity.get("schema_version")
        != "dvf-3-3-current-correction-identity-report-v2"
        or identity.get("status") != "PASS"
        or identity.get("adoption_commit") != ADOPTION_COMMIT
        or identity.get("adoption_tree") != ADOPTION_TREE
        or identity.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or identity.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or identity.get("single_current_identity") is not True
        or identity.get("partial_current_count") != 0
        or identity.get("dual_current_count") != 0
        or terminal.get("schema_version")
        != "dvf-3-3-terminal-correction-hash-seal-v2"
        or terminal.get("status") != "PASS"
        or terminal.get("adoption_commit") != ADOPTION_COMMIT
        or terminal.get("adoption_tree") != ADOPTION_TREE
        or terminal.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or terminal.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or terminal.get("registry_correction_adoption_receipt_sha256")
        != CORRECTION_RECEIPT_SHA256
        or terminal.get("current_identity_report_sha256")
        != CURRENT_IDENTITY_REPORT_SHA256
        or terminal.get("naturalization_current_input_handoff_sha256")
        != NATURALIZATION_HANDOFF_SHA256
        or terminal.get("forbidden_scope_execution_count") != 0
        or handoff.get("schema_version")
        != "dvf-3-3-naturalization-current-input-handoff-v2"
        or handoff.get("status") != "READY_FOR_FOUNDATION_REBIND"
        or handoff.get("required_next_stage") != "Foundation_current_input_rebind"
        or handoff.get("registry_adoption_commit") != ADOPTION_COMMIT
        or handoff.get("registry_adoption_tree") != ADOPTION_TREE
        or handoff.get("registry_correction_adoption_receipt_sha256")
        != CORRECTION_RECEIPT_SHA256
        or handoff.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or handoff.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or handoff.get("naturalization_attempt_started") is not False
        or handoff.get("official_publish_started") is not False
        or handoff.get("rtc_executed") is not False
        or manifest.get("facts", {}).get("sha256") != CURRENT_FACTS_SHA256
        or food_authority.get("registry_cutover_attempt_id") != "attempt-0011"
        or food_authority.get("registry_adoption_state")
        != "current_correction_0002"
        or correction_binding.get("append_only") is not True
        or correction_binding.get("successor_id") != REBIND_ID
        or correction_binding.get("successor_facts_sha256")
        != CURRENT_FACTS_SHA256
        or correction_binding.get("registry_cutover_attempt_id")
        != "attempt-0011"
    )
    if invalid:
        raise FoundationRebindError(
            "correction-0002 G3/current-input evidence binding is invalid"
        )
    return {
        "successor_id": REBIND_ID,
        "registry_cutover_attempt_id": "attempt-0011",
        "adoption_commit": ADOPTION_COMMIT,
        "adoption_tree": ADOPTION_TREE,
        "adoption_tree_matches_commit": True,
        "correction_adoption_receipt": receipt_record,
        "current_identity_report": identity_record,
        "terminal_correction_seal": terminal_record,
        "naturalization_current_input_handoff": handoff_record,
        "current_facts": facts_record,
        "current_manifest": manifest_record,
        "current_identity_ambiguity_count": 0,
        "partial_or_dual_current_count": 0,
        "forbidden_scope_execution_count": 0,
    }


def _protected_paths() -> list[Path]:
    fixed = {
        FOUNDATION_CONTRACT,
        FOUNDATION_READINESS,
        PREDECESSOR_REBIND,
        CORRECTION_RECEIPT,
        CURRENT_IDENTITY_REPORT,
        TERMINAL_CORRECTION_SEAL,
        NATURALIZATION_HANDOFF,
        CURRENT_FACTS,
        CURRENT_MANIFEST,
        LIVE_REQUIRED_VALIDATIONS,
        V2_ROOT / "data" / "dvf_3_3_decisions.jsonl",
        V2_ROOT / "data" / "dvf_3_3_overlay_support.jsonl",
        V2_ROOT / "data" / "compose_profiles_v2.json",
        V2_ROOT / "data" / "compose_profile_identity_hint_rules.json",
        V2_ROOT / "data" / "compose_profile_conflict_precedence_rules.json",
        V2_ROOT / "output" / "dvf_3_3_rendered.json",
        V2_ROOT / "output" / "style_normalization_changes.jsonl",
        V2_ROOT / "output" / "compose_requeue_candidates.jsonl",
    }
    fixed.update(REPO_ROOT / relative for relative in FOUNDATION_MEANING_PATHS)
    recursive_roots = (
        REPO_ROOT / "Iris" / "media" / "lua",
        REPO_ROOT / "Iris" / "Contents" / "mods" / "Iris",
        V2_ROOT
        / "staging"
        / "iris_publish_boundary_public_text_quality_acceptance_policy_closure",
        NATURALIZATION_ATTEMPT_ROOT,
        G3_ATTEMPT_ROOT,
    )
    for root in recursive_roots:
        if root.is_dir():
            fixed.update(path for path in root.rglob("*") if path.is_file())
    fixed.discard(SUCCESSOR_PATH)
    return sorted(fixed, key=_repo_relative)


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_paths():
        present = path.is_file()
        rows.append(
            {
                "path": _repo_relative(path),
                "present": present,
                "raw_sha256": _sha256_file(path) if present else None,
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": "public_text_quality_foundation_rebind_no_write_snapshot_v1",
        "surface_count": len(rows),
        "surface_hash": _canonical_hash(rows),
        "surfaces": rows,
    }


def _no_write_guard(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    before_rows = {row["path"]: row for row in before["surfaces"]}
    after_rows = {row["path"]: row for row in after["surfaces"]}
    changed = sorted(
        path
        for path in set(before_rows) | set(after_rows)
        if before_rows.get(path) != after_rows.get(path)
    )
    if changed:
        raise FoundationRebindError(
            f"protected rebind surface changed: {changed}"
        )
    return {
        "schema_version": "public_text_quality_foundation_rebind_no_write_guard_v1",
        "status": "PASS",
        "before_snapshot_hash": _canonical_hash(before),
        "after_snapshot_hash": _canonical_hash(after),
        "protected_surface_mutation_count": 0,
        "changed_paths": [],
        "source_rendered_lua_runtime_package_authority_effect": "none",
    }


def _implementation_hashes() -> list[dict[str, Any]]:
    rows = []
    for path in IMPLEMENTATION_FILES:
        if not path.is_file():
            raise FoundationRebindError(
                f"rebind implementation file missing: {path}"
            )
        rows.append(
            {
                "path": _repo_relative(path),
                "hash_algorithm": "sha256_utf8_lf_normalized_v1",
                "sha256": _sha256_lf(path),
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
        "rebind_id": REBIND_ID,
        "rebind_kind": "append_only_current_input_readiness_successor",
        "purpose": (
            "Bind immutable G4 Foundation readiness to correction-0002 current "
            "inputs without changing Foundation contract or evaluation semantics."
        ),
        "execution_start_readpoint": _validate_start_readpoint(
            require_exact_head=require_exact_start_head
        ),
        "immutable_foundation": _validate_immutable_foundation(),
        "predecessor_readiness_rebind": _validate_predecessor_rebind(),
        "registry_correction_adoption": _validate_registry_correction(),
        "rebind_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "naturalization_prerequisites": {
            "g4_development_readiness_rebound": True,
            "fresh_naturalization_attempt_must_start_at_phase": 0,
            "naturalization_attempt_created": False,
            "naturalization_phase2_through_phase8_executed": False,
            "current_input_handoff_consumed_as_identity_only": True,
        },
        "publish_boundary": {
            "official_publish_attempt_created": False,
            "public_text_candidate_evaluated": False,
            "live_publish_gate_mutated": False,
            "policy_ratified": False,
        },
        "runtime_boundary": {
            "rtc_executed": False,
            "runtime_mutated": False,
            "package_mutated": False,
            "runtime_package_publication_claim_effect": (
                "none_fail_closed_out_of_scope"
            ),
        },
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "foundation_contract_semantics_changed": False,
        "foundation_validator_semantics_changed": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "next_stage": "fresh_naturalization_attempt_phase0",
    }


def _validate_rebind_id(rebind_id: str) -> None:
    if rebind_id != REBIND_ID:
        raise FoundationRebindError(
            f"only the exact append-only rebind ID {REBIND_ID} is allowed"
        )


def build_rebind(rebind_id: str) -> dict[str, Any]:
    _validate_rebind_id(rebind_id)
    if SUCCESSOR_PATH.exists():
        raise FoundationRebindError(
            f"append-only readiness successor already exists: {_repo_relative(SUCCESSOR_PATH)}"
        )
    protected_before = protected_snapshot()
    protected_after_projection = protected_snapshot()
    guard = _no_write_guard(protected_before, protected_after_projection)
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(_pretty_json_bytes(successor))
    protected_final = protected_snapshot()
    _no_write_guard(protected_before, protected_final)
    return {
        "status": "PASS",
        "rebind_id": REBIND_ID,
        "readiness_successor_path": _repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": _sha256_file(SUCCESSOR_PATH),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }


def _require_successor_vcs_state() -> dict[str, Any]:
    if not SUCCESSOR_PATH.is_file() or not _is_tracked(SUCCESSOR_PATH):
        raise FoundationRebindError(
            "readiness successor must be present and tracked before validation"
        )
    if _is_ignored(SUCCESSOR_PATH):
        raise FoundationRebindError("readiness successor must not be ignored")
    relative = _repo_relative(SUCCESSOR_PATH)
    staged_or_head_blob = _git("rev-parse", f":{relative}", check=False)
    if staged_or_head_blob.returncode != 0:
        staged_or_head_blob = _git("rev-parse", f"HEAD:{relative}", check=False)
    if staged_or_head_blob.returncode != 0:
        raise FoundationRebindError("cannot resolve readiness successor Git blob")
    blob_id = staged_or_head_blob.stdout.strip()
    working_raw_blob_id = _git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    if blob_id != working_raw_blob_id:
        raise FoundationRebindError(
            "readiness successor staged/working raw-byte identity mismatch"
        )
    attr = _git("check-attr", "text", "--", relative).stdout.strip()
    if not attr.endswith(": text: unset"):
        raise FoundationRebindError(
            "readiness successor must have an exact -text attribute"
        )
    return {
        "tracked": True,
        "ignored": False,
        "text_attribute": "unset",
        "git_blob_id": blob_id,
        "working_raw_blob_id": working_raw_blob_id,
        "git_blob_working_byte_identity": True,
    }


def validate_rebind(rebind_id: str) -> dict[str, Any]:
    _validate_rebind_id(rebind_id)
    if not SUCCESSOR_PATH.is_file():
        raise FoundationRebindError("readiness successor is missing")
    successor_bytes_before = SUCCESSOR_PATH.read_bytes()
    successor = _load_json(SUCCESSOR_PATH)
    protected_before = protected_snapshot()
    protected_after_projection = protected_snapshot()
    guard = _no_write_guard(protected_before, protected_after_projection)
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationRebindError(
            "readiness successor is stale or differs from exact correction-0002 projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes_before:
        raise FoundationRebindError("no-write validator changed successor bytes")
    protected_final = protected_snapshot()
    _no_write_guard(protected_before, protected_final)
    return {
        "status": "PASS",
        "rebind_id": REBIND_ID,
        "readiness_successor_path": _repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": _sha256_file(SUCCESSOR_PATH),
        "foundation_contract_sha256": FOUNDATION_CONTRACT_SHA256,
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
