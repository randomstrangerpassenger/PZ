from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence


REPO_ROOT = Path(__file__).resolve().parents[6]
V2_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2"
ROUND_ID = "dvf_3_3_food_semantic_registry_operational_cutover"
ROUND_ROOT = V2_ROOT / "staging" / ROUND_ID
ATTEMPTS_ROOT = ROUND_ROOT / "attempts"
ROUND_DOC_ROOT = REPO_ROOT / "Iris" / "_docs" / "round3" / ROUND_ID

PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "dvf_3_3_food_semantic_registry_operational_cutover_implementation_plan.md"
)
PLAN_REVIEW_PATH = ROUND_DOC_ROOT / "independent_plan_review.json"
BASE_BINDING_PATH = ROUND_DOC_ROOT / "implementation_base_binding.json"

G2_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_facts_authority"
    / "attempts"
    / "attempt-0022"
)
G2_SUCCESSOR_FACTS = (
    G2_ATTEMPT_ROOT / "authority_execution" / "successor_facts.jsonl"
)
G2_SUCCESSOR_MANIFEST = (
    G2_ATTEMPT_ROOT / "authority_execution" / "successor_input_manifest.json"
)
G2_BINDING = (
    G2_ATTEMPT_ROOT
    / "phase11_successor"
    / "selected_successor_input_binding.json"
)
G2_CUTOVER_REQUEST = (
    G2_ATTEMPT_ROOT
    / "authority_execution"
    / "phase11_successor"
    / "registry_cutover_request.json"
)
G2_CLOSEOUT_ROOT = G2_ATTEMPT_ROOT / "phase13_closeout"
G2_TERMINAL_SEAL = G2_CLOSEOUT_ROOT / "terminal_hash_seal.json"
G2_OWNER_SEAL = G2_CLOSEOUT_ROOT / "owner_seal.json"
G2_REVIEW = G2_CLOSEOUT_ROOT / "independent_closeout_review.json"
G2_FINAL_MANIFEST = G2_CLOSEOUT_ROOT / "final_artifact_manifest.json"

CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
CURRENT_ROUTE_VALIDATIONS = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
)
REGISTRY_CONTRACT = (
    REPO_ROOT / "Iris" / "_docs" / "authority" / "food_semantic"
    / "registry_adoption_contract.json"
)
NATURALIZATION_CONTRACT = (
    REPO_ROOT / "Iris" / "_docs" / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "food_semantic_registry_adoption_contract.json"
)

G2_TERMINAL_SUBJECT_COMMIT = "319fa3cf439d72703b888a4ddb19c961c86bf3f7"
GOVERNING_DOC_COMMIT = "f68d1db963ed945d4019215d85a6ad8bf8be9211"
G2_TERMINAL_SEAL_SHA256 = (
    "9a9a37731e8d76399f6b960a0e9beb21bcdd65d8ae39e511337527c5306d0c19"
)
G2_REVIEW_SHA256 = (
    "8c71275aee4c397b959d74bed25848850b36d699736cc1e8657287377105bce6"
)
G2_FINAL_MANIFEST_SHA256 = (
    "7e72bb17d7ff45abcf20fe9ca939f8e52779f3fd0e8da4646265c61b1557d620"
)
G2_BINDING_SHA256 = (
    "bbea40be6c9b174fbc1e25de217646e13584dde1e9fcb18fa424ccd8bf3f2f42"
)
SUCCESSOR_FACTS_SHA256 = (
    "1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40"
)
SUCCESSOR_MANIFEST_SHA256 = (
    "d1dea3b7b871fac90fc6a15ec18d95641a52d566cd62d14ffb0114c2bfb0098a"
)
SCHEMA_SHA256 = (
    "66f9eb59ea2cfec3fb5d647345ce5ab07ae17d0ba70b62c52b6bcaa7e3f32563"
)
PROPOSITION_LICENSE_SHA256 = (
    "60f68c3e06fd148fce55072e1b7420165e10db16fc4e4b132b3fba7ae83e6edd"
)
CURRENT_FACTS_PREIMAGE_SHA256 = (
    "a89af8d75a78a57bd2ac05f07af4246d1ebab862dd4021bd089c5efa6e533be6"
)
CURRENT_MANIFEST_PREIMAGE_SHA256 = (
    "db4c5e827c1aad4175894fb0f5b59db9496c5819cacd86a9f703d3542a05be41"
)
PLAN_SHA256 = (
    "49a472fb499f51c797fafd0b90e31baad7ffd39f59eaf0f93a0548236d674cb2"
)
PLAN_GIT_BLOB_ID = "c5c4e22d991fa150e9d556d1a7ca0d90e2935ebe"
IMPLEMENTATION_BASE_HEAD = "1a4fe5a27f420f84e42f974f2765396d3c9924ab"
IMPLEMENTATION_BASE_TREE = "c04ff1679cf481b4076fc89dbc5681d822fef626"

CURRENT_FACTS_REL = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
CURRENT_MANIFEST_REL = (
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
)
ALLOWED_TARGET_PATHS = [CURRENT_FACTS_REL, CURRENT_MANIFEST_REL]
ATTEMPT_RE = re.compile(r"^attempt-\d{4}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")

PROJECTION_ALLOWED_PATHS = {
    "status",
    "authority_role",
    "facts.path",
    "facts.role",
    "food_semantic_authority.non_current",
    "food_semantic_authority.current_adoption_allowed",
    "food_semantic_authority.registry_adoption_state",
    "food_semantic_authority.registry_cutover_attempt_id",
    "food_semantic_authority.source_successor_manifest_sha256",
    "source_promotion.food_semantic_successor_binding",
}

FINAL_TEST_PATTERNS = (
    "test_dvf_3_3_food_semantic_*.py",
    "test_dvf_3_3_korean_prose_acceptance_gate.py",
    "test_dvf_3_3_korean_prose_semantic_preservation.py",
    "test_dvf_3_3_registry_runtime_compatibility_bridge.py",
    "test_dvf_3_3_registry_runtime_compatibility_package.py",
    "test_dvf_3_3_registry_runtime_compatibility_current.py",
)


class CutoverError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CutoverError(f"invalid_json:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise CutoverError(f"json_root_not_object:{path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, 1):
                if not raw.strip():
                    continue
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise CutoverError(
                        f"jsonl_row_not_object:{path}:{line_number}"
                    )
                rows.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        raise CutoverError(f"invalid_jsonl:{path}:{exc}") from exc
    return rows


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise CutoverError(f"path_outside_repository:{path}") from exc


def path_label(path: Path) -> str:
    try:
        return repo_relative(path)
    except CutoverError:
        return str(path.resolve())


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise CutoverError(f"{label}_missing:{repo_relative(path)}")
    actual = sha256_file(path)
    if actual != expected:
        raise CutoverError(f"{label}_hash_mismatch:{expected}:{actual}")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise CutoverError(f"{label}_mismatch:{expected!r}:{actual!r}")


def write_once_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise CutoverError(f"write_once_path_exists:{path_label(path)}") from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def write_once_json(path: Path, value: Any) -> None:
    write_once_bytes(path, canonical_json_bytes(value))


def ensure_write_once_json(path: Path, value: Any) -> None:
    expected = canonical_json_bytes(value)
    if path.exists():
        require_equal(path.read_bytes(), expected, f"write_once_existing_{path.name}")
        return
    write_once_bytes(path, expected)


def atomic_write_bytes(path: Path, data: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".cutover.tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    directory_fsync = "not_attempted"
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        try:
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
                directory_fsync = "supported_and_completed"
            finally:
                os.close(directory_descriptor)
        except OSError as exc:
            directory_fsync = f"unsupported_or_failed:{type(exc).__name__}"
    finally:
        if temporary.exists():
            temporary.unlink()
    return {
        "file_fsync": "completed",
        "atomic_replace": "completed",
        "parent_directory_fsync": directory_fsync,
        "power_loss_atomicity_claimed": False,
        "intermediate_reader_visibility_zero_claimed": False,
    }


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value))


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = [
        "git",
        "-c",
        f"safe.directory={REPO_ROOT.as_posix()}",
        "-C",
        str(REPO_ROOT),
        *args,
    ]
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        raise CutoverError(
            f"git_command_failed:{' '.join(args)}:{completed.stderr.strip()}"
        )
    return completed


def git_head() -> str:
    return git("rev-parse", "HEAD").stdout.strip()


def git_tree(commit: str = "HEAD") -> str:
    return git("rev-parse", f"{commit}^{{tree}}").stdout.strip()


def git_blob_id(commit: str, relative_path: str) -> str:
    return git("rev-parse", f"{commit}:{relative_path}").stdout.strip()


def git_blob_bytes(commit: str, relative_path: str) -> bytes:
    command = [
        "git",
        "-c",
        f"safe.directory={REPO_ROOT.as_posix()}",
        "-C",
        str(REPO_ROOT),
        "show",
        f"{commit}:{relative_path}",
    ]
    completed = subprocess.run(command, capture_output=True, check=False)
    if completed.returncode != 0:
        raise CutoverError(
            f"git_blob_read_failed:{commit}:{relative_path}:"
            f"{completed.stderr.decode(errors='replace').strip()}"
        )
    return completed.stdout


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    return (
        git(
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
            check=False,
        ).returncode
        == 0
    )


def require_clean_candidate_entry() -> None:
    status = git("status", "--porcelain=v1", "--untracked-files=all").stdout
    if status.strip():
        raise CutoverError(f"candidate_entry_worktree_not_clean:{status.strip()}")


def require_tracked_worktree_clean(label: str) -> None:
    if git("diff", "--quiet", check=False).returncode != 0:
        raise CutoverError(f"{label}_tracked_worktree_not_clean")
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        raise CutoverError(f"{label}_index_not_clean")


def deep_diff(
    predecessor: Any,
    successor: Any,
    prefix: str = "",
) -> list[dict[str, Any]]:
    if isinstance(predecessor, dict) and isinstance(successor, dict):
        rows: list[dict[str, Any]] = []
        for key in sorted(set(predecessor) | set(successor)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in predecessor:
                rows.append(
                    {
                        "path": path,
                        "change": "added",
                        "before": None,
                        "after": successor[key],
                    }
                )
            elif key not in successor:
                rows.append(
                    {
                        "path": path,
                        "change": "removed",
                        "before": predecessor[key],
                        "after": None,
                    }
                )
            else:
                rows.extend(deep_diff(predecessor[key], successor[key], path))
        return rows
    if predecessor != successor:
        return [
            {
                "path": prefix,
                "change": "changed",
                "before": predecessor,
                "after": successor,
            }
        ]
    return []


def build_current_manifest_projection(
    successor_manifest: dict[str, Any],
    attempt_id: str,
) -> dict[str, Any]:
    projected = copy.deepcopy(successor_manifest)
    projected["status"] = "current_authority"
    projected["authority_role"] = "successor_current_source_authority"
    projected["facts"]["path"] = CURRENT_FACTS_REL
    projected["facts"]["role"] = "current_source_authority"
    food = projected["food_semantic_authority"]
    food["non_current"] = False
    food["current_adoption_allowed"] = True
    food["registry_adoption_state"] = "current"
    food["registry_cutover_attempt_id"] = attempt_id
    food["source_successor_manifest_sha256"] = SUCCESSOR_MANIFEST_SHA256
    projected["source_promotion"]["food_semantic_successor_binding"] = {
        "source_attempt_id": "attempt-0022",
        "selected_successor_binding_path": repo_relative(G2_BINDING),
        "selected_successor_binding_sha256": G2_BINDING_SHA256,
        "successor_facts_path": repo_relative(G2_SUCCESSOR_FACTS),
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "successor_manifest_path": repo_relative(G2_SUCCESSOR_MANIFEST),
        "successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "schema_sha256": SCHEMA_SHA256,
        "proposition_license_sha256": PROPOSITION_LICENSE_SHA256,
        "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "predecessor_current_manifest_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "terminal_hash_seal_path": repo_relative(G2_TERMINAL_SEAL),
        "terminal_hash_seal_sha256": G2_TERMINAL_SEAL_SHA256,
    }
    return projected


def validate_projection(
    successor_manifest: dict[str, Any],
    projected: dict[str, Any],
    attempt_id: str,
) -> list[dict[str, Any]]:
    differences = deep_diff(successor_manifest, projected)
    actual_paths = {row["path"] for row in differences}
    if actual_paths != PROJECTION_ALLOWED_PATHS:
        unexpected = sorted(actual_paths - PROJECTION_ALLOWED_PATHS)
        missing = sorted(PROJECTION_ALLOWED_PATHS - actual_paths)
        raise CutoverError(
            f"manifest_projection_allowlist_mismatch:"
            f"unexpected={unexpected}:missing={missing}"
        )
    require_equal(projected["status"], "current_authority", "projected_status")
    require_equal(
        projected["authority_role"],
        "successor_current_source_authority",
        "projected_authority_role",
    )
    require_equal(
        projected["facts"]["sha256"],
        SUCCESSOR_FACTS_SHA256,
        "projected_facts_sha256",
    )
    require_equal(
        projected["food_semantic_authority"]["registry_cutover_attempt_id"],
        attempt_id,
        "projected_attempt_id",
    )
    return differences


def validate_successor_rows(
    predecessor_path: Path = CURRENT_FACTS,
) -> dict[str, Any]:
    successor_rows = read_jsonl(G2_SUCCESSOR_FACTS)
    predecessor_rows = read_jsonl(predecessor_path)
    require_equal(len(successor_rows), 2105, "successor_row_count")
    require_equal(len(predecessor_rows), 2105, "predecessor_row_count")
    successor_food = [
        row for row in successor_rows if row.get("food_semantic_assertions")
    ]
    proposition_count = sum(
        len(row.get("food_semantic_assertions", [])) for row in successor_food
    )
    require_equal(len(successor_food), 317, "successor_food_target_count")
    require_equal(proposition_count, 718, "successor_proposition_count")

    exact_members = ["Base.LemonGrass", "Base.Lemongrass"]
    predecessor_by_id = {row.get("item_id"): row for row in predecessor_rows}
    successor_by_id = {row.get("item_id"): row for row in successor_rows}
    for item_id in exact_members:
        if item_id not in predecessor_by_id or item_id not in successor_by_id:
            raise CutoverError(f"rtc_collision_member_missing:{item_id}")

    def payload_hash(row: dict[str, Any]) -> str:
        payload = {key: value for key, value in row.items() if key != "item_id"}
        return sha256_bytes(canonical_json_bytes(payload))

    predecessor_hashes = [
        payload_hash(predecessor_by_id[item_id]) for item_id in exact_members
    ]
    successor_hashes = [
        payload_hash(successor_by_id[item_id]) for item_id in exact_members
    ]
    require_equal(
        len(set(predecessor_hashes)),
        1,
        "predecessor_collision_payload_identity_count",
    )
    require_equal(
        len(set(successor_hashes)),
        2,
        "successor_collision_payload_identity_count",
    )
    return {
        "schema_version": "food-semantic-rtc-collision-impact-v1",
        "status": "PASS",
        "collision_group_id": "ascii-lower-fd527de5892ca80a",
        "comparison_key": "base.lemongrass",
        "exact_member_count": 2,
        "exact_members": exact_members,
        "comparison_collision_group_count": 1,
        "predecessor_source_payload_hashes": dict(
            zip(exact_members, predecessor_hashes, strict=True)
        ),
        "successor_source_payload_hashes": dict(
            zip(exact_members, successor_hashes, strict=True)
        ),
        "predecessor_source_payload_equivalence": True,
        "successor_source_payload_equivalence": False,
        "current_source_alignment_state": "stale_requires_successor_rtc",
        "applies_when_current_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "successor_rtc_closure_complete": False,
    }


def validate_contracts_and_marker() -> None:
    require_equal(
        REGISTRY_CONTRACT.read_bytes(),
        NATURALIZATION_CONTRACT.read_bytes(),
        "registry_contract_byte_identity",
    )
    contract = read_json(REGISTRY_CONTRACT)
    require_equal(
        contract.get("schema_version"),
        "food-semantic-registry-adoption-contract-v2",
        "registry_contract_schema",
    )
    selected = contract.get("selected_successor", {})
    require_equal(
        selected.get("facts_sha256"),
        SUCCESSOR_FACTS_SHA256,
        "contract_successor_facts",
    )
    require_equal(
        selected.get("manifest_sha256"),
        SUCCESSOR_MANIFEST_SHA256,
        "contract_successor_manifest",
    )
    marker = read_json(CURRENT_ROUTE_VALIDATIONS).get(
        "registry_runtime_compatibility",
        {},
    ).get("current_source_alignment")
    if not isinstance(marker, dict):
        raise CutoverError("rtc_current_source_alignment_marker_missing")
    expected = {
        "schema_version": "rtc-current-source-alignment-staleness-v1",
        "state": "stale_requires_successor_rtc",
        "applies_when_current_facts_path": CURRENT_FACTS_REL,
        "applies_when_current_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "collision_group_id": "ascii-lower-fd527de5892ca80a",
        "exact_members": ["Base.LemonGrass", "Base.Lemongrass"],
        "predecessor_source_payload_equivalence": True,
        "successor_source_payload_equivalence": False,
        "live_bridge_runtime_package_publication_allowed": False,
        "isolated_successor_candidate_probe_allowed": True,
        "successor_rtc_closure_complete": False,
    }
    require_equal(marker, expected, "rtc_current_source_alignment_marker")


def validate_g2_chain(implementation_commit: str) -> dict[str, Any]:
    if not git_is_ancestor(G2_TERMINAL_SUBJECT_COMMIT, implementation_commit):
        raise CutoverError("g2_terminal_subject_not_implementation_ancestor")
    if not git_is_ancestor(GOVERNING_DOC_COMMIT, implementation_commit):
        raise CutoverError("governing_doc_not_implementation_ancestor")
    require_hash(G2_TERMINAL_SEAL, G2_TERMINAL_SEAL_SHA256, "g2_terminal_seal")
    require_hash(G2_REVIEW, G2_REVIEW_SHA256, "g2_independent_review")
    require_hash(
        G2_FINAL_MANIFEST,
        G2_FINAL_MANIFEST_SHA256,
        "g2_final_artifact_manifest",
    )
    require_hash(G2_BINDING, G2_BINDING_SHA256, "g2_successor_binding")
    require_hash(G2_SUCCESSOR_FACTS, SUCCESSOR_FACTS_SHA256, "g2_successor_facts")
    require_hash(
        G2_SUCCESSOR_MANIFEST,
        SUCCESSOR_MANIFEST_SHA256,
        "g2_successor_manifest",
    )
    terminal = read_json(G2_TERMINAL_SEAL)
    owner = read_json(G2_OWNER_SEAL)
    review = read_json(G2_REVIEW)
    request = read_json(G2_CUTOVER_REQUEST)
    require_equal(terminal.get("status"), "PASS", "g2_terminal_status")
    require_equal(terminal.get("attempt_id"), "attempt-0022", "g2_terminal_attempt")
    require_equal(
        terminal.get("owner_seal_sha256"),
        sha256_file(G2_OWNER_SEAL),
        "g2_terminal_owner_binding",
    )
    require_equal(
        terminal.get("independent_closeout_review_sha256"),
        sha256_file(G2_REVIEW),
        "g2_terminal_review_binding",
    )
    require_equal(
        terminal.get("final_artifact_manifest_sha256"),
        sha256_file(G2_FINAL_MANIFEST),
        "g2_terminal_manifest_binding",
    )
    require_equal(owner.get("verdict"), "PASS", "g2_owner_verdict")
    require_equal(
        owner.get("independent_closeout_review_sha256"),
        sha256_file(G2_REVIEW),
        "g2_owner_review_binding",
    )
    require_equal(review.get("verdict"), "PASS", "g2_review_verdict")
    require_equal(
        review.get("reviewed_final_artifact_manifest_sha256"),
        sha256_file(G2_FINAL_MANIFEST),
        "g2_review_manifest_binding",
    )
    require_equal(
        request.get("selected_successor_input_binding_sha256"),
        G2_BINDING_SHA256,
        "g2_cutover_binding",
    )
    require_equal(
        request.get("successor_facts_sha256"),
        SUCCESSOR_FACTS_SHA256,
        "g2_cutover_facts",
    )
    require_equal(
        request.get("successor_input_manifest_sha256"),
        SUCCESSOR_MANIFEST_SHA256,
        "g2_cutover_manifest",
    )
    return {
        "terminal_hash_seal_sha256": sha256_file(G2_TERMINAL_SEAL),
        "owner_seal_sha256": sha256_file(G2_OWNER_SEAL),
        "independent_review_sha256": sha256_file(G2_REVIEW),
        "final_artifact_manifest_sha256": sha256_file(G2_FINAL_MANIFEST),
        "selected_successor_binding_sha256": sha256_file(G2_BINDING),
        "successor_facts_sha256": sha256_file(G2_SUCCESSOR_FACTS),
        "successor_manifest_sha256": sha256_file(G2_SUCCESSOR_MANIFEST),
    }


def validate_implementation_binding() -> dict[str, str]:
    base = read_json(BASE_BINDING_PATH)
    review = read_json(PLAN_REVIEW_PATH)
    require_equal(base.get("status"), "PASS", "implementation_base_status")
    require_equal(
        base.get("implementation_base_head"),
        IMPLEMENTATION_BASE_HEAD,
        "implementation_base_head",
    )
    require_equal(
        base.get("implementation_base_tree"),
        IMPLEMENTATION_BASE_TREE,
        "implementation_base_tree",
    )
    require_equal(
        base.get("reviewed_plan_sha256"),
        PLAN_SHA256,
        "base_reviewed_plan_sha256",
    )
    require_equal(
        base.get("reviewed_plan_git_blob_id"),
        PLAN_GIT_BLOB_ID,
        "base_reviewed_plan_blob",
    )
    require_equal(review.get("verdict"), "PASS", "independent_plan_review")
    require_hash(PLAN_PATH, PLAN_SHA256, "reviewed_plan")
    implementation_commit = git_head()
    implementation_tree = git_tree(implementation_commit)
    if not git_is_ancestor(IMPLEMENTATION_BASE_HEAD, implementation_commit):
        raise CutoverError("implementation_base_not_ancestor")
    require_equal(
        git_blob_id(
            implementation_commit,
            repo_relative(PLAN_PATH),
        ),
        PLAN_GIT_BLOB_ID,
        "implementation_plan_git_blob",
    )
    require_equal(
        sha256_bytes(
            git_blob_bytes(implementation_commit, repo_relative(PLAN_PATH))
        ),
        PLAN_SHA256,
        "implementation_plan_git_blob_sha256",
    )
    return {
        "implementation_commit": implementation_commit,
        "implementation_tree": implementation_tree,
    }


def attempt_root(attempt_id: str) -> Path:
    if not ATTEMPT_RE.fullmatch(attempt_id):
        raise CutoverError(f"invalid_attempt_id:{attempt_id}")
    path = (ATTEMPTS_ROOT / attempt_id).resolve()
    if path.parent != ATTEMPTS_ROOT.resolve():
        raise CutoverError(f"attempt_path_escape:{attempt_id}")
    return path


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


@contextmanager
def transaction_lock(
    binding: dict[str, Any],
    *,
    error_release_guard: Callable[[], bool] | None = None,
    lock_path: Path | None = None,
) -> Iterator[None]:
    selected_lock_path = (
        lock_path if lock_path is not None else ROUND_ROOT / "transaction.lock"
    )
    selected_lock_path.parent.mkdir(parents=True, exist_ok=True)
    if selected_lock_path.exists():
        stale = read_json(selected_lock_path)
        stale_pid = stale.get("pid")
        if not isinstance(stale_pid, int) or process_is_alive(stale_pid):
            raise CutoverError("round_transaction_lock_active_or_invalid")
        selected_lock_path.unlink()
    payload = {
        "schema_version": "food-semantic-registry-cutover-lock-v1",
        "round_id": ROUND_ID,
        "pid": os.getpid(),
        "acquired_at": now_iso(),
        **binding,
    }
    write_once_json(selected_lock_path, payload)
    release_lock = True
    try:
        yield
    except BaseException:
        if error_release_guard is None:
            release_lock = True
        else:
            try:
                release_lock = error_release_guard()
            except BaseException:
                release_lock = False
        raise
    finally:
        if release_lock and selected_lock_path.exists():
            observed = read_json(selected_lock_path)
            if observed.get("pid") == os.getpid():
                selected_lock_path.unlink()


def journal_path(root: Path) -> Path:
    return root / "transaction" / "cutover_journal.json"


def update_journal(
    root: Path,
    *,
    state: str,
    previous_state: str | None,
    durability: dict[str, Any] | None = None,
) -> None:
    allowed = {
        None: "prepared",
        "prepared": "facts_replaced",
        "facts_replaced": "manifest_replaced",
        "manifest_replaced": "verified",
        "verified": "committed",
    }
    if allowed.get(previous_state) != state:
        raise CutoverError(
            f"journal_transition_invalid:{previous_state!r}:{state!r}"
        )
    path = journal_path(root)
    if previous_state is None:
        payload: dict[str, Any] = {
            "schema_version": "food-semantic-registry-cutover-journal-v1",
            "round_id": ROUND_ID,
            "attempt_id": root.name,
            "state": state,
            "state_history": [{"state": state, "time": now_iso()}],
            "power_loss_atomicity_claimed": False,
            "intermediate_reader_visibility_zero_claimed": False,
            "canonical_adoption_status": "pending_adoption_commit",
        }
    else:
        payload = read_json(path)
        require_equal(payload.get("state"), previous_state, "journal_previous_state")
        payload["state"] = state
        payload["state_history"].append({"state": state, "time": now_iso()})
    if durability is not None:
        payload.setdefault("durability", {})[state] = durability
    atomic_write_json(path, payload)


def snapshot_paths(root: Path) -> tuple[Path, Path, Path]:
    transaction = root / "transaction"
    return (
        transaction / "rollback_current_facts.jsonl",
        transaction / "rollback_current_input_manifest.json",
        transaction / "rollback_snapshot_manifest.json",
    )


def create_rollback_snapshots(
    root: Path,
    facts_target: Path,
    manifest_target: Path,
    expected_preimages: dict[str, str],
) -> dict[str, Any]:
    facts_snapshot, manifest_snapshot, snapshot_manifest = snapshot_paths(root)
    facts_bytes = facts_target.read_bytes()
    manifest_bytes = manifest_target.read_bytes()
    require_equal(
        sha256_bytes(facts_bytes),
        expected_preimages["facts"],
        "locked_facts_preimage",
    )
    require_equal(
        sha256_bytes(manifest_bytes),
        expected_preimages["manifest"],
        "locked_manifest_preimage",
    )
    write_once_bytes(facts_snapshot, facts_bytes)
    write_once_bytes(manifest_snapshot, manifest_bytes)
    payload = {
        "schema_version": "food-semantic-registry-cutover-rollback-snapshot-v1",
        "status": "READY",
        "attempt_id": root.name,
        "targets": {
            "facts": {
                "target_path": path_label(facts_target),
                "snapshot_path": path_label(facts_snapshot),
                "sha256": sha256_bytes(facts_bytes),
                "byte_count": len(facts_bytes),
            },
            "manifest": {
                "target_path": path_label(manifest_target),
                "snapshot_path": path_label(manifest_snapshot),
                "sha256": sha256_bytes(manifest_bytes),
                "byte_count": len(manifest_bytes),
            },
        },
    }
    write_once_json(snapshot_manifest, payload)
    return payload


def restore_snapshots(
    root: Path,
    facts_target: Path,
    manifest_target: Path,
    expected_preimages: dict[str, str],
) -> dict[str, Any]:
    facts_snapshot, manifest_snapshot, _ = snapshot_paths(root)
    facts_durability = atomic_write_bytes(facts_target, facts_snapshot.read_bytes())
    manifest_durability = atomic_write_bytes(
        manifest_target,
        manifest_snapshot.read_bytes(),
    )
    actual = {
        "facts": sha256_file(facts_target),
        "manifest": sha256_file(manifest_target),
    }
    require_equal(actual, expected_preimages, "rollback_restored_preimages")
    return {
        "status": "PASS",
        "restored_preimages": actual,
        "durability": {
            "facts": facts_durability,
            "manifest": manifest_durability,
        },
    }


def execute_pair_transaction(
    *,
    root: Path,
    facts_target: Path,
    manifest_target: Path,
    facts_candidate: Path,
    manifest_candidate: Path,
    expected_preimages: dict[str, str],
    expected_candidates: dict[str, str],
    inject_failure: str | None = None,
    before_first_replace: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    create_rollback_snapshots(
        root,
        facts_target,
        manifest_target,
        expected_preimages,
    )
    update_journal(root, state="prepared", previous_state=None)
    try:
        if before_first_replace is not None:
            before_first_replace()
        facts_durability = atomic_write_bytes(
            facts_target,
            facts_candidate.read_bytes(),
        )
        update_journal(
            root,
            state="facts_replaced",
            previous_state="prepared",
            durability=facts_durability,
        )
        if inject_failure == "second_replace":
            raise CutoverError("injected_second_replace_failure")
        manifest_durability = atomic_write_bytes(
            manifest_target,
            manifest_candidate.read_bytes(),
        )
        update_journal(
            root,
            state="manifest_replaced",
            previous_state="facts_replaced",
            durability=manifest_durability,
        )
        actual = {
            "facts": sha256_file(facts_target),
            "manifest": sha256_file(manifest_target),
        }
        require_equal(actual, expected_candidates, "installed_candidate_hashes")
        if inject_failure == "post_write_verification":
            raise CutoverError("injected_post_write_verification_failure")
        update_journal(
            root,
            state="verified",
            previous_state="manifest_replaced",
        )
        return {
            "status": "PASS",
            "installed_candidates": actual,
            "manifest_last_order": True,
            "power_loss_atomicity_claimed": False,
            "intermediate_reader_visibility_zero_claimed": False,
        }
    except BaseException as exc:
        rollback = restore_snapshots(
            root,
            facts_target,
            manifest_target,
            expected_preimages,
        )
        failure_path = root / "transaction" / "transaction_failure.json"
        if not failure_path.exists():
            write_once_json(
                failure_path,
                {
                    "schema_version": "food-semantic-registry-cutover-failure-v1",
                    "status": "FAILED",
                    "attempt_id": root.name,
                    "failure_type": type(exc).__name__,
                    "failure_message": str(exc),
                    "rollback": rollback,
                    "same_attempt_retry_allowed": False,
                },
            )
        raise


def candidate_paths(root: Path) -> tuple[Path, Path]:
    return (
        root / "candidate" / "current_facts.jsonl",
        root / "candidate" / "current_input_manifest.json",
    )


def expected_pair_hashes(root: Path) -> tuple[dict[str, str], dict[str, str]]:
    facts_candidate, manifest_candidate = candidate_paths(root)
    return (
        {
            "facts": CURRENT_FACTS_PREIMAGE_SHA256,
            "manifest": CURRENT_MANIFEST_PREIMAGE_SHA256,
        },
        {
            "facts": sha256_file(facts_candidate),
            "manifest": sha256_file(manifest_candidate),
        },
    )


def recover_pair_state(
    *,
    root: Path,
    facts_target: Path,
    manifest_target: Path,
    expected_preimages: dict[str, str],
    expected_candidates: dict[str, str],
    commit_verified_callback: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    journal = read_json(journal_path(root))
    state = journal.get("state")
    actual = {
        "facts": sha256_file(facts_target),
        "manifest": sha256_file(manifest_target),
    }
    failure_path = root / "transaction" / "transaction_failure.json"
    if state == "committed":
        require_equal(actual, expected_candidates, "committed_recovery_identity")
        return {"attempt_id": root.name, "resolution": "already_committed"}
    if failure_path.is_file():
        failure = read_json(failure_path)
        require_equal(
            failure.get("rollback", {}).get("status"),
            "PASS",
            "prior_failure_rollback",
        )
        require_equal(actual, expected_preimages, "prior_failure_preimages")
        return {"attempt_id": root.name, "resolution": "already_rolled_back"}
    if state == "verified" and actual == expected_candidates:
        if commit_verified_callback is not None:
            commit_verified_callback()
        update_journal(root, state="committed", previous_state="verified")
        return {
            "attempt_id": root.name,
            "resolution": "verified_candidates_committed",
        }
    rollback = restore_snapshots(
        root,
        facts_target,
        manifest_target,
        expected_preimages,
    )
    recovery_path = root / "transaction" / "startup_recovery.json"
    if not recovery_path.exists():
        write_once_json(
            recovery_path,
            {
                "schema_version": "food-semantic-registry-cutover-recovery-v1",
                "status": "PASS",
                "attempt_id": root.name,
                "observed_state": state,
                "resolution": "both_preimages_restored",
                "rollback": rollback,
                "same_attempt_retry_allowed": False,
            },
        )
    return {
        "attempt_id": root.name,
        "resolution": "both_preimages_restored",
    }


def recover_attempt(root: Path) -> dict[str, Any]:
    expected_preimages, expected_candidates = expected_pair_hashes(root)
    return recover_pair_state(
        root=root,
        facts_target=CURRENT_FACTS,
        manifest_target=CURRENT_MANIFEST,
        expected_preimages=expected_preimages,
        expected_candidates=expected_candidates,
        commit_verified_callback=lambda: create_adoption_receipts(root),
    )


def startup_recovery(exclude_attempt: str | None = None) -> list[dict[str, Any]]:
    recovered: list[dict[str, Any]] = []
    if not ATTEMPTS_ROOT.exists():
        return recovered
    for journal in sorted(ATTEMPTS_ROOT.glob("attempt-*/transaction/cutover_journal.json")):
        root = journal.parents[1]
        if root.name == exclude_attempt:
            continue
        state = read_json(journal).get("state")
        if state == "committed":
            continue
        failure_path = root / "transaction" / "transaction_failure.json"
        if failure_path.is_file():
            failure = read_json(failure_path)
            if (
                failure.get("status") == "FAILED"
                and failure.get("rollback", {}).get("status") == "PASS"
                and failure.get("rollback", {}).get("restored_preimages")
                == {
                    "facts": CURRENT_FACTS_PREIMAGE_SHA256,
                    "manifest": CURRENT_MANIFEST_PREIMAGE_SHA256,
                }
            ):
                continue
        recovery_path = root / "transaction" / "startup_recovery.json"
        if recovery_path.is_file():
            recovery = read_json(recovery_path)
            if (
                recovery.get("status") == "PASS"
                and recovery.get("resolution") == "both_preimages_restored"
                and recovery.get("rollback", {}).get("restored_preimages")
                == {
                    "facts": CURRENT_FACTS_PREIMAGE_SHA256,
                    "manifest": CURRENT_MANIFEST_PREIMAGE_SHA256,
                }
            ):
                continue
        recovered.append(recover_attempt(root))
    return recovered


def command_prepare(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    if root.exists():
        raise CutoverError(f"attempt_already_exists:{attempt_id}")
    with transaction_lock(
        {
            "mode": "prepare_startup_recovery",
            "attempt_id": attempt_id,
            "allowed_target_paths": ALLOWED_TARGET_PATHS,
        }
    ):
        initial_recovery = startup_recovery()
    if initial_recovery:
        raise CutoverError(
            "startup_recovery_completed_commit_evidence_before_prepare:"
            f"{initial_recovery}"
        )
    require_clean_candidate_entry()
    implementation = validate_implementation_binding()
    g2_chain = validate_g2_chain(implementation["implementation_commit"])
    require_hash(CURRENT_FACTS, CURRENT_FACTS_PREIMAGE_SHA256, "current_facts_preimage")
    require_hash(
        CURRENT_MANIFEST,
        CURRENT_MANIFEST_PREIMAGE_SHA256,
        "current_manifest_preimage",
    )
    validate_contracts_and_marker()
    collision = validate_successor_rows()
    successor_manifest = read_json(G2_SUCCESSOR_MANIFEST)
    require_equal(
        successor_manifest["food_semantic_authority"]["schema_sha256"],
        SCHEMA_SHA256,
        "successor_schema_sha256",
    )
    require_equal(
        successor_manifest["food_semantic_authority"][
            "proposition_license_sha256"
        ],
        PROPOSITION_LICENSE_SHA256,
        "successor_license_sha256",
    )
    projected = build_current_manifest_projection(successor_manifest, attempt_id)
    differences = validate_projection(successor_manifest, projected, attempt_id)
    with transaction_lock(
        {
            "mode": "prepare",
            "attempt_id": attempt_id,
            "allowed_target_paths": ALLOWED_TARGET_PATHS,
        }
    ):
        recovered = startup_recovery()
        require_hash(
            CURRENT_FACTS,
            CURRENT_FACTS_PREIMAGE_SHA256,
            "locked_prepare_current_facts_preimage",
        )
        require_hash(
            CURRENT_MANIFEST,
            CURRENT_MANIFEST_PREIMAGE_SHA256,
            "locked_prepare_current_manifest_preimage",
        )
        root.mkdir(parents=True)
        facts_candidate, manifest_candidate = candidate_paths(root)
        write_once_bytes(facts_candidate, G2_SUCCESSOR_FACTS.read_bytes())
        write_once_json(manifest_candidate, projected)
        write_once_json(
            root / "candidate" / "adoption_projection_diff.json",
            {
                "schema_version": "food-semantic-adoption-projection-diff-v1",
                "status": "PASS",
                "attempt_id": attempt_id,
                "allowlisted_paths": sorted(PROJECTION_ALLOWED_PATHS),
                "differences": differences,
                "manifest_allowlisted_delta_violation_count": 0,
            },
        )
        write_once_json(
            root / "preflight" / "current_preimage_report.json",
            {
                "schema_version": "food-semantic-current-preimage-report-v1",
                "status": "PASS",
                "attempt_id": attempt_id,
                "candidate_entry_tracked_worktree_clean": True,
                "implementation_commit": implementation["implementation_commit"],
                "implementation_tree": implementation["implementation_tree"],
                "plan_sha256": PLAN_SHA256,
                "plan_git_blob_id": PLAN_GIT_BLOB_ID,
                "g2_chain": g2_chain,
                "current_preimages": {
                    "facts": {
                        "path": CURRENT_FACTS_REL,
                        "working_sha256": sha256_file(CURRENT_FACTS),
                        "git_blob_id": git_blob_id(
                            implementation["implementation_commit"],
                            CURRENT_FACTS_REL,
                        ),
                        "git_blob_sha256": sha256_bytes(
                            git_blob_bytes(
                                implementation["implementation_commit"],
                                CURRENT_FACTS_REL,
                            )
                        ),
                    },
                    "manifest": {
                        "path": CURRENT_MANIFEST_REL,
                        "working_sha256": sha256_file(CURRENT_MANIFEST),
                        "git_blob_id": git_blob_id(
                            implementation["implementation_commit"],
                            CURRENT_MANIFEST_REL,
                        ),
                        "git_blob_sha256": sha256_bytes(
                            git_blob_bytes(
                                implementation["implementation_commit"],
                                CURRENT_MANIFEST_REL,
                            )
                        ),
                    },
                },
                "current_preimage_mismatch_count": 0,
            },
        )
        write_once_json(
            root
            / "preflight"
            / "registry_runtime_compatibility_collision_impact_report.json",
            collision,
        )
        write_once_json(
            root / "preflight" / "startup_recovery_report.json",
            {
                "schema_version": "food-semantic-startup-recovery-report-v1",
                "status": "PASS",
                "attempt_id": attempt_id,
                "prior_unresolved_journal_count": 0,
                "recovered_journals": recovered,
            },
        )
    return {
        "status": "READY_FOR_PRE_CUTOVER_REVIEW",
        "attempt_id": attempt_id,
        **implementation,
        "candidate_current_facts_sha256": sha256_file(facts_candidate),
        "candidate_current_manifest_sha256": sha256_file(manifest_candidate),
        "current_facts_preimage_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "current_manifest_preimage_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "owner_authorization_required": True,
    }


def validate_pre_cutover_review(root: Path) -> tuple[dict[str, Any], str]:
    path = root / "reviews" / "independent_pre_cutover_review.json"
    review = read_json(path)
    facts_candidate, manifest_candidate = candidate_paths(root)
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    require_equal(review.get("verdict"), "PASS", "pre_cutover_review_verdict")
    require_equal(review.get("status"), "PASS", "pre_cutover_review_status")
    require_equal(review.get("attempt_id"), root.name, "pre_cutover_review_attempt")
    require_equal(
        review.get("reviewed_implementation_commit"),
        preflight.get("implementation_commit"),
        "pre_cutover_review_commit",
    )
    require_equal(
        review.get("reviewed_implementation_tree"),
        preflight.get("implementation_tree"),
        "pre_cutover_review_tree",
    )
    require_equal(
        review.get("candidate_current_facts_sha256"),
        sha256_file(facts_candidate),
        "pre_cutover_review_facts",
    )
    require_equal(
        review.get("candidate_current_manifest_sha256"),
        sha256_file(manifest_candidate),
        "pre_cutover_review_manifest",
    )
    counts = review.get("finding_counts", {})
    require_equal(counts.get("critical"), 0, "pre_cutover_critical_count")
    require_equal(counts.get("important"), 0, "pre_cutover_important_count")
    require_equal(review.get("tests_executed"), False, "pre_cutover_tests_executed")
    require_equal(review.get("files_modified"), False, "pre_cutover_files_modified")
    reviewer_identity = review.get("reviewer_identity")
    if (
        not isinstance(reviewer_identity, str)
        or not reviewer_identity.startswith("Codex Reviewer /root/")
    ):
        raise CutoverError("pre_cutover_reviewer_identity_invalid")
    return review, sha256_file(path)


def authorization_expected(root: Path) -> dict[str, Any]:
    _, review_sha256 = validate_pre_cutover_review(root)
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    facts_candidate, manifest_candidate = candidate_paths(root)
    return {
        "verdict": "PASS",
        "plan_sha256": PLAN_SHA256,
        "plan_git_blob_id": PLAN_GIT_BLOB_ID,
        "implementation_commit": preflight["implementation_commit"],
        "implementation_tree": preflight["implementation_tree"],
        "cutover_attempt_id": root.name,
        "pre_cutover_review_sha256": review_sha256,
        "selected_successor_binding_sha256": G2_BINDING_SHA256,
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "candidate_current_facts_sha256": sha256_file(facts_candidate),
        "candidate_current_manifest_sha256": sha256_file(manifest_candidate),
        "current_facts_preimage_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "current_manifest_preimage_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "allowed_target_paths": ALLOWED_TARGET_PATHS,
    }


def command_authorization_template(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    expected = authorization_expected(root)
    return {
        "schema_version": "food-semantic-registry-cutover-owner-authorization-v1",
        **expected,
        "authorization_nonce": "<owner-issued-one-use-nonce>",
        "approver_identity": "<owner-identity>",
        "approval_time": "<owner-approval-time>",
    }


def validate_authorization_payload(
    authorization: dict[str, Any],
    expected: dict[str, Any],
    nonce_path: Path,
) -> None:
    for key, expected_value in expected.items():
        require_equal(
            authorization.get(key),
            expected_value,
            f"owner_authorization_{key}",
        )
    nonce = authorization.get("authorization_nonce")
    approver = authorization.get("approver_identity")
    approval_time = authorization.get("approval_time")
    if not isinstance(nonce, str) or len(nonce.strip()) < 16:
        raise CutoverError("owner_authorization_nonce_invalid")
    if not isinstance(approver, str) or not approver.strip():
        raise CutoverError("owner_authorization_approver_invalid")
    if not isinstance(approval_time, str) or not approval_time.strip():
        raise CutoverError("owner_authorization_time_invalid")
    try:
        parsed_approval_time = datetime.fromisoformat(
            approval_time.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise CutoverError("owner_authorization_time_invalid") from exc
    if parsed_approval_time.tzinfo is None:
        raise CutoverError("owner_authorization_time_timezone_missing")
    if nonce_path.exists():
        raise CutoverError("owner_authorization_nonce_already_consumed")


def validate_owner_authorization(root: Path) -> tuple[dict[str, Any], str]:
    path = root / "authorization" / "owner_cutover_authorization.json"
    authorization = read_json(path)
    expected = authorization_expected(root)
    nonce_path = root / "transaction" / "nonce_consumption.json"
    validate_authorization_payload(authorization, expected, nonce_path)
    for consumed_path in ATTEMPTS_ROOT.glob(
        "attempt-*/transaction/nonce_consumption.json"
    ):
        if consumed_path.resolve() == nonce_path.resolve():
            continue
        consumed = read_json(consumed_path)
        if consumed.get("authorization_nonce") == authorization[
            "authorization_nonce"
        ]:
            raise CutoverError(
                f"owner_authorization_nonce_replayed_across_attempts:"
                f"{repo_relative(consumed_path)}"
            )
    return authorization, sha256_file(path)


def validate_apply_repository_readpoint(root: Path) -> None:
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    expected_commit = preflight.get("implementation_commit")
    expected_tree = preflight.get("implementation_tree")
    require_equal(git_head(), expected_commit, "apply_implementation_head")
    require_equal(
        git_tree(str(expected_commit)),
        expected_tree,
        "apply_implementation_tree",
    )
    require_tracked_worktree_clean("apply")
    require_equal(
        git_blob_id(str(expected_commit), repo_relative(PLAN_PATH)),
        PLAN_GIT_BLOB_ID,
        "apply_plan_git_blob",
    )
    require_equal(
        sha256_bytes(
            git_blob_bytes(str(expected_commit), repo_relative(PLAN_PATH))
        ),
        PLAN_SHA256,
        "apply_plan_git_blob_sha256",
    )


def create_adoption_receipts(root: Path) -> tuple[Path, Path]:
    facts_candidate, manifest_candidate = candidate_paths(root)
    authorization_path = (
        root / "authorization" / "owner_cutover_authorization.json"
    )
    review_path = root / "reviews" / "independent_pre_cutover_review.json"
    receipt_path = root / "closeout" / "registry_adoption_receipt.json"
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    receipt = {
        "schema_version": "food-semantic-registry-adoption-receipt-v1",
        "status": "PASS",
        "attempt_id": root.name,
        "implementation_commit": preflight["implementation_commit"],
        "implementation_tree": preflight["implementation_tree"],
        "food_semantic_registry_adoption": "current_adoption_complete",
        "selected_successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "selected_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "current_facts_sha256": sha256_file(CURRENT_FACTS),
        "current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
        "projected_current_manifest_sha256": sha256_file(manifest_candidate),
        "current_manifest_adopted_successor_manifest_sha256": (
            SUCCESSOR_MANIFEST_SHA256
        ),
        "candidate_current_facts_sha256": sha256_file(facts_candidate),
        "candidate_current_manifest_sha256": sha256_file(manifest_candidate),
        "selected_schema_sha256": SCHEMA_SHA256,
        "selected_proposition_license_sha256": PROPOSITION_LICENSE_SHA256,
        "manifest_allowlisted_delta_violation_count": 0,
        "current_identity_ambiguity_count": 0,
        "partial_or_dual_current_count": 0,
        "g2_mutation_count": 0,
        "rendered_lua_runtime_package_mutation_count": 0,
        "official_naturalization_retry_allowed": True,
        "registry_runtime_compatibility_current_source_alignment": (
            "stale_requires_successor_rtc"
        ),
        "successor_registry_runtime_compatibility_closure": False,
        "runtime_package_compatibility": "not_evaluated",
        "owner_authorization_sha256": sha256_file(authorization_path),
        "pre_cutover_review_sha256": sha256_file(review_path),
        "git_blob_identity_status": "pending_adoption_commit",
        "power_loss_atomicity_claimed": False,
        "intermediate_reader_visibility_zero_claimed": False,
    }
    require_equal(
        receipt["selected_successor_facts_sha256"],
        receipt["current_facts_sha256"],
        "receipt_current_successor_facts",
    )
    require_equal(
        receipt["current_manifest_sha256"],
        receipt["projected_current_manifest_sha256"],
        "receipt_current_projected_manifest",
    )
    ensure_write_once_json(receipt_path, receipt)
    handoff_path = (
        root / "closeout" / "naturalization_phase2_current_handoff.json"
    )
    ensure_write_once_json(
        handoff_path,
        {
            "schema_version": "food-semantic-naturalization-phase2-handoff-v2",
            "status": "PASS",
            "attempt_id": root.name,
            "registry_adoption_receipt_path": repo_relative(receipt_path),
            "registry_adoption_receipt_sha256": sha256_file(receipt_path),
            "current_facts_sha256": SUCCESSOR_FACTS_SHA256,
            "current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
            "current_manifest_projection_validation": "PASS",
            "selected_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
            "schema_sha256": SCHEMA_SHA256,
            "proposition_license_sha256": PROPOSITION_LICENSE_SHA256,
            "official_naturalization_retry_allowed": True,
            "fresh_naturalization_attempt_required": True,
            "naturalization_phase_3_through_8_complete": False,
            "publish_boundary_pass": False,
        },
    )
    return receipt_path, handoff_path


def command_apply(attempt_id: str, inject_failure: str | None = None) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    with transaction_lock(
        {
            "mode": "apply_startup_recovery",
            "attempt_id": attempt_id,
            "allowed_target_paths": ALLOWED_TARGET_PATHS,
        }
    ):
        initial_recovery = startup_recovery()
    if initial_recovery:
        raise CutoverError(
            "startup_recovery_completed_commit_evidence_before_apply:"
            f"{initial_recovery}"
        )
    validate_apply_repository_readpoint(root)
    authorization, authorization_sha256 = validate_owner_authorization(root)
    facts_candidate, manifest_candidate = candidate_paths(root)
    expected_preimages, expected_candidates = expected_pair_hashes(root)
    require_equal(
        expected_candidates["facts"],
        SUCCESSOR_FACTS_SHA256,
        "candidate_successor_facts",
    )

    def apply_error_release_guard() -> bool:
        nonce_path = root / "transaction" / "nonce_consumption.json"
        if not nonce_path.exists():
            return True
        failure_path = root / "transaction" / "transaction_failure.json"
        if not failure_path.is_file():
            return False
        try:
            failure = read_json(failure_path)
            actual = {
                "facts": sha256_file(CURRENT_FACTS),
                "manifest": sha256_file(CURRENT_MANIFEST),
            }
        except (CutoverError, OSError):
            return False
        return (
            failure.get("rollback", {}).get("status") == "PASS"
            and actual == expected_preimages
        )

    with transaction_lock(
        {
            "mode": "apply",
            "attempt_id": attempt_id,
            "allowed_target_paths": ALLOWED_TARGET_PATHS,
            "current_preimages": expected_preimages,
            "candidate_hashes": expected_candidates,
            "authorization_nonce": authorization["authorization_nonce"],
        },
        error_release_guard=apply_error_release_guard,
    ):
        startup_recovery(exclude_attempt=attempt_id)
        validate_apply_repository_readpoint(root)
        require_equal(
            {
                "facts": sha256_file(CURRENT_FACTS),
                "manifest": sha256_file(CURRENT_MANIFEST),
            },
            expected_preimages,
            "apply_locked_preimages",
        )
        nonce_path = root / "transaction" / "nonce_consumption.json"

        def consume_nonce() -> None:
            write_once_json(
                nonce_path,
                {
                    "schema_version": "food-semantic-cutover-nonce-consumption-v1",
                    "status": "CONSUMED",
                    "attempt_id": attempt_id,
                    "authorization_nonce": authorization["authorization_nonce"],
                    "owner_authorization_sha256": authorization_sha256,
                    "consumed_at": now_iso(),
                    "same_attempt_retry_allowed": False,
                },
            )

        transaction = execute_pair_transaction(
            root=root,
            facts_target=CURRENT_FACTS,
            manifest_target=CURRENT_MANIFEST,
            facts_candidate=facts_candidate,
            manifest_candidate=manifest_candidate,
            expected_preimages=expected_preimages,
            expected_candidates=expected_candidates,
            inject_failure=inject_failure,
            before_first_replace=consume_nonce,
        )
        receipt_path, handoff_path = create_adoption_receipts(root)
        update_journal(root, state="committed", previous_state="verified")
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "transaction": transaction,
        "registry_adoption_receipt_path": repo_relative(receipt_path),
        "registry_adoption_receipt_sha256": sha256_file(receipt_path),
        "naturalization_handoff_path": repo_relative(handoff_path),
        "naturalization_handoff_sha256": sha256_file(handoff_path),
        "canonical_adoption_status": "pending_adoption_commit",
    }


def command_verify_committed(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    journal = read_json(journal_path(root))
    require_equal(journal.get("state"), "committed", "transaction_journal_state")
    head = git_head()
    tree = git_tree(head)
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    implementation_commit = preflight["implementation_commit"]
    implementation_tree = preflight["implementation_tree"]
    require_equal(
        git_tree(implementation_commit),
        implementation_tree,
        "committed_implementation_tree",
    )
    parent_row = git("rev-list", "--parents", "-n", "1", head).stdout.split()
    if len(parent_row) != 2 or parent_row[1] != implementation_commit:
        raise CutoverError(
            "adoption_commit_not_single_direct_child_of_implementation"
        )
    changed_paths = [
        row
        for row in git(
            "diff",
            "--name-only",
            implementation_commit,
            head,
        ).stdout.splitlines()
        if row
    ]
    attempt_prefix = repo_relative(root) + "/"
    unexpected_paths = [
        path
        for path in changed_paths
        if path not in ALLOWED_TARGET_PATHS
        and not path.startswith(attempt_prefix)
    ]
    if unexpected_paths:
        raise CutoverError(
            f"adoption_commit_unexpected_paths:{unexpected_paths}"
        )
    required_adoption_paths = {
        CURRENT_FACTS_REL,
        CURRENT_MANIFEST_REL,
        repo_relative(
            root / "closeout" / "registry_adoption_receipt.json"
        ),
        repo_relative(
            root / "closeout" / "naturalization_phase2_current_handoff.json"
        ),
        repo_relative(
            root / "authorization" / "owner_cutover_authorization.json"
        ),
        repo_relative(
            root / "reviews" / "independent_pre_cutover_review.json"
        ),
        repo_relative(root / "transaction" / "cutover_journal.json"),
    }
    missing_adoption_paths = sorted(required_adoption_paths - set(changed_paths))
    if missing_adoption_paths:
        raise CutoverError(
            f"adoption_commit_required_paths_missing:{missing_adoption_paths}"
        )
    require_tracked_worktree_clean("verify_committed")
    facts_working = sha256_file(CURRENT_FACTS)
    manifest_working = sha256_file(CURRENT_MANIFEST)
    facts_blob_bytes = git_blob_bytes(head, CURRENT_FACTS_REL)
    manifest_blob_bytes = git_blob_bytes(head, CURRENT_MANIFEST_REL)
    facts_blob_sha = sha256_bytes(facts_blob_bytes)
    manifest_blob_sha = sha256_bytes(manifest_blob_bytes)
    require_equal(facts_working, SUCCESSOR_FACTS_SHA256, "committed_facts_working")
    require_equal(facts_blob_sha, facts_working, "committed_facts_blob_working")
    require_equal(
        manifest_blob_sha,
        manifest_working,
        "committed_manifest_blob_working",
    )
    receipt_path = root / "closeout" / "registry_adoption_receipt.json"
    receipt_rel = repo_relative(receipt_path)
    require_equal(
        sha256_bytes(git_blob_bytes(head, receipt_rel)),
        sha256_file(receipt_path),
        "committed_adoption_receipt",
    )
    eol = git(
        "ls-files",
        "--eol",
        "--",
        CURRENT_FACTS_REL,
        CURRENT_MANIFEST_REL,
    ).stdout
    eol_rows = [line for line in eol.splitlines() if line.strip()]
    if len(eol_rows) != 2 or any("attr/-text" not in row for row in eol_rows):
        raise CutoverError(f"current_authority_eol_attribute_invalid:{eol_rows}")
    report_path = root / "closeout" / "current_identity_report.json"
    write_once_json(
        report_path,
        {
            "schema_version": "food-semantic-current-identity-report-v1",
            "status": "PASS",
            "attempt_id": attempt_id,
            "adoption_commit": head,
            "adoption_tree": tree,
            "implementation_commit": implementation_commit,
            "implementation_tree": implementation_tree,
            "adoption_changed_paths": changed_paths,
            "facts": {
                "path": CURRENT_FACTS_REL,
                "working_sha256": facts_working,
                "git_blob_id": git_blob_id(head, CURRENT_FACTS_REL),
                "git_blob_sha256": facts_blob_sha,
                "byte_identity": facts_blob_sha == facts_working,
            },
            "manifest": {
                "path": CURRENT_MANIFEST_REL,
                "working_sha256": manifest_working,
                "git_blob_id": git_blob_id(head, CURRENT_MANIFEST_REL),
                "git_blob_sha256": manifest_blob_sha,
                "byte_identity": manifest_blob_sha == manifest_working,
            },
            "git_ls_files_eol": eol_rows,
            "current_identity_ambiguity_count": 0,
            "partial_or_dual_current_count": 0,
            "canonical_adoption_readpoint": True,
        },
    )
    return read_json(report_path)


def artifact_validation(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    identity = read_json(root / "closeout" / "current_identity_report.json")
    receipt = read_json(root / "closeout" / "registry_adoption_receipt.json")
    authorization = read_json(
        root / "authorization" / "owner_cutover_authorization.json"
    )
    journal = read_json(journal_path(root))
    validate_contracts_and_marker()
    predecessor_snapshot = (
        root / "transaction" / "rollback_current_facts.jsonl"
    )
    collision = validate_successor_rows(predecessor_snapshot)
    successor_manifest = read_json(G2_SUCCESSOR_MANIFEST)
    projected = read_json(CURRENT_MANIFEST)
    differences = validate_projection(successor_manifest, projected, attempt_id)
    require_equal(len(read_jsonl(CURRENT_FACTS)), 2105, "current_facts_row_count")
    require_equal(identity.get("status"), "PASS", "current_identity_status")
    require_equal(receipt.get("status"), "PASS", "adoption_receipt_status")
    require_equal(authorization.get("verdict"), "PASS", "authorization_status")
    require_equal(journal.get("state"), "committed", "journal_committed")
    validate_g2_chain(identity["adoption_commit"])
    status = git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        "Iris/build/description/v2/tools/build/"
        "dvf_3_3_food_semantic_registry_cutover.py",
        "Iris/build/description/v2/tests/"
        "test_dvf_3_3_food_semantic_registry_cutover.py",
        repo_relative(root / "candidate"),
        repo_relative(root / "preflight"),
        repo_relative(root / "reviews"),
        repo_relative(root / "authorization"),
        repo_relative(root / "transaction"),
        repo_relative(root / "closeout" / "registry_adoption_receipt.json"),
        repo_relative(
            root / "closeout" / "naturalization_phase2_current_handoff.json"
        ),
    ).stdout
    if status.strip():
        raise CutoverError(f"cutover_artifacts_not_tracked:{status.strip()}")
    return {
        "status": "PASS",
        "current_facts_row_count": 2105,
        "food_target_member_count": 317,
        "proposition_count": 718,
        "manifest_projection_difference_count": len(differences),
        "manifest_allowlisted_delta_violation_count": 0,
        "current_facts_git_blob_working_identity": True,
        "current_manifest_git_blob_working_identity": True,
        "g2_mutation_count": 0,
        "rendered_lua_runtime_package_mutation_count": 0,
        "rtc_collision_impact": collision,
    }


def parse_test_count(output: str) -> int | None:
    match = re.search(r"Ran (\d+) tests?", output)
    return int(match.group(1)) if match else None


def command_run_final_validation(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    identity = read_json(root / "closeout" / "current_identity_report.json")
    require_equal(
        git_head(),
        identity.get("adoption_commit"),
        "final_validation_adoption_head",
    )
    require_equal(
        git_tree(),
        identity.get("adoption_tree"),
        "final_validation_adoption_tree",
    )
    require_tracked_worktree_clean("final_validation")
    artifact_report = artifact_validation(attempt_id)
    runs_root = root / "closeout" / "final_validation_runs"
    existing = sorted(runs_root.glob("run-*.json")) if runs_root.exists() else []
    run_id = f"run-{len(existing) + 1:04d}"
    results: list[dict[str, Any]] = []
    tests_root = V2_ROOT / "tests"
    for pattern in FINAL_TEST_PATTERNS:
        command = [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "Iris/build/description/v2/tests",
            "-p",
            pattern,
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        combined = completed.stdout + completed.stderr
        result = {
            "pattern": pattern,
            "command": command,
            "exit_code": completed.returncode,
            "test_count": parse_test_count(combined),
            "stdout_sha256": sha256_bytes(completed.stdout.encode("utf-8")),
            "stderr_sha256": sha256_bytes(completed.stderr.encode("utf-8")),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        results.append(result)
        print(combined, end="")
    status = "PASS" if all(row["exit_code"] == 0 for row in results) else "FAIL"
    run_path = runs_root / f"{run_id}.json"
    write_once_json(
        run_path,
        {
            "schema_version": "food-semantic-scoped-final-validation-run-v1",
            "status": status,
            "attempt_id": attempt_id,
            "run_id": run_id,
            "results": results,
            "full_repository_gate_execution_count": 0,
            "direct_all_test_discovery_execution_count": 0,
            "out_of_scope_test_execution_count": 0,
        },
    )
    if status != "PASS":
        raise CutoverError(f"scoped_final_validation_failed:{repo_relative(run_path)}")
    receipt_path = root / "closeout" / "final_validation_receipt.json"
    if receipt_path.exists():
        raise CutoverError("final_validation_receipt_already_exists")
    write_once_json(
        receipt_path,
        {
            "schema_version": "food-semantic-scoped-final-validation-receipt-v1",
            "status": "PASS",
            "attempt_id": attempt_id,
            "validation_run_path": repo_relative(run_path),
            "validation_run_sha256": sha256_file(run_path),
            "results": [
                {
                    key: row[key]
                    for key in (
                        "pattern",
                        "command",
                        "exit_code",
                        "test_count",
                        "stdout_sha256",
                        "stderr_sha256",
                    )
                }
                for row in results
            ],
            "artifact_validation": artifact_report,
            "scoped_final_validation": "PASS",
            "registry_runtime_compatibility_current_source_alignment": (
                "stale_requires_successor_rtc"
            ),
            "full_repository_gate_execution_count": 0,
            "direct_all_test_discovery_execution_count": 0,
            "out_of_scope_test_execution_count": 0,
        },
    )
    return read_json(receipt_path)


def validate_closeout_review(root: Path) -> tuple[dict[str, Any], str]:
    path = root / "closeout" / "independent_closeout_review.json"
    review = read_json(path)
    pre_review = read_json(root / "reviews" / "independent_pre_cutover_review.json")
    identity_path = root / "closeout" / "current_identity_report.json"
    validation_path = root / "closeout" / "final_validation_receipt.json"
    require_equal(review.get("verdict"), "PASS", "closeout_review_verdict")
    require_equal(review.get("status"), "PASS", "closeout_review_status")
    require_equal(review.get("attempt_id"), root.name, "closeout_review_attempt")
    require_equal(
        review.get("reviewed_adoption_commit"),
        read_json(identity_path).get("adoption_commit"),
        "closeout_review_adoption_commit",
    )
    require_equal(
        review.get("reviewed_adoption_tree"),
        read_json(identity_path).get("adoption_tree"),
        "closeout_review_adoption_tree",
    )
    require_equal(
        review.get("current_identity_report_sha256"),
        sha256_file(identity_path),
        "closeout_review_identity",
    )
    require_equal(
        review.get("final_validation_receipt_sha256"),
        sha256_file(validation_path),
        "closeout_review_validation",
    )
    if review.get("reviewer_identity") == pre_review.get("reviewer_identity"):
        raise CutoverError("closeout_reviewer_not_distinct")
    counts = review.get("finding_counts", {})
    require_equal(counts.get("critical"), 0, "closeout_critical_count")
    require_equal(counts.get("important"), 0, "closeout_important_count")
    require_equal(review.get("tests_executed"), False, "closeout_tests_executed")
    require_equal(review.get("files_modified"), False, "closeout_files_modified")
    return review, sha256_file(path)


def owner_seal_expected(root: Path) -> dict[str, Any]:
    _, review_sha256 = validate_closeout_review(root)
    identity = read_json(root / "closeout" / "current_identity_report.json")
    return {
        "final_signoff_status": "PASS",
        "attempt_id": root.name,
        "adoption_commit": identity["adoption_commit"],
        "adoption_tree": identity["adoption_tree"],
        "registry_adoption_receipt_sha256": sha256_file(
            root / "closeout" / "registry_adoption_receipt.json"
        ),
        "current_identity_report_sha256": sha256_file(
            root / "closeout" / "current_identity_report.json"
        ),
        "final_validation_receipt_sha256": sha256_file(
            root / "closeout" / "final_validation_receipt.json"
        ),
        "independent_closeout_review_sha256": review_sha256,
        "terminal_claim": (
            "DVF 3-3 Food Semantic Registry Adoption = current_adoption_complete"
        ),
    }


def command_owner_seal_template(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    return {
        "schema_version": "food-semantic-registry-adoption-owner-seal-v1",
        **owner_seal_expected(root),
        "approver_identity": "<owner-identity>",
        "approval_time": "<owner-approval-time>",
    }


def command_finalize(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    identity = read_json(root / "closeout" / "current_identity_report.json")
    require_equal(
        git_head(),
        identity.get("adoption_commit"),
        "finalize_adoption_head",
    )
    require_equal(
        git_tree(),
        identity.get("adoption_tree"),
        "finalize_adoption_tree",
    )
    require_tracked_worktree_clean("finalize")
    require_equal(
        sha256_bytes(git_blob_bytes(git_head(), CURRENT_FACTS_REL)),
        sha256_file(CURRENT_FACTS),
        "finalize_current_facts_blob_working",
    )
    require_equal(
        sha256_bytes(git_blob_bytes(git_head(), CURRENT_MANIFEST_REL)),
        sha256_file(CURRENT_MANIFEST),
        "finalize_current_manifest_blob_working",
    )
    owner_path = root / "closeout" / "owner_seal.json"
    owner = read_json(owner_path)
    expected = owner_seal_expected(root)
    for key, expected_value in expected.items():
        require_equal(owner.get(key), expected_value, f"owner_seal_{key}")
    if not isinstance(owner.get("approver_identity"), str) or not owner[
        "approver_identity"
    ].strip():
        raise CutoverError("owner_seal_approver_invalid")
    if not isinstance(owner.get("approval_time"), str) or not owner[
        "approval_time"
    ].strip():
        raise CutoverError("owner_seal_time_invalid")
    try:
        parsed_owner_seal_time = datetime.fromisoformat(
            owner["approval_time"].replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise CutoverError("owner_seal_time_invalid") from exc
    if parsed_owner_seal_time.tzinfo is None:
        raise CutoverError("owner_seal_time_timezone_missing")
    terminal_path = root / "closeout" / "terminal_hash_seal.json"
    artifacts = {
        "registry_adoption_receipt_sha256": sha256_file(
            root / "closeout" / "registry_adoption_receipt.json"
        ),
        "current_identity_report_sha256": sha256_file(
            root / "closeout" / "current_identity_report.json"
        ),
        "naturalization_phase2_current_handoff_sha256": sha256_file(
            root / "closeout" / "naturalization_phase2_current_handoff.json"
        ),
        "final_validation_receipt_sha256": sha256_file(
            root / "closeout" / "final_validation_receipt.json"
        ),
        "independent_closeout_review_sha256": sha256_file(
            root / "closeout" / "independent_closeout_review.json"
        ),
        "owner_seal_sha256": sha256_file(owner_path),
    }
    terminal = {
        "schema_version": "food-semantic-registry-adoption-terminal-hash-seal-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "food_semantic_registry_adoption": "current_adoption_complete",
        "terminal_claim": (
            "DVF 3-3 Food Semantic Registry Adoption = current_adoption_complete"
        ),
        "artifacts": artifacts,
        "current_facts_sha256": sha256_file(CURRENT_FACTS),
        "current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
        "selected_successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "selected_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "current_manifest_projection_validation": "PASS",
        "current_identity_ambiguity_count": 0,
        "partial_or_dual_current_count": 0,
        "g2_mutation_count": 0,
        "rendered_lua_runtime_package_mutation_count": 0,
        "scoped_final_validation": "PASS",
        "independent_closeout_review": "PASS",
        "owner_final_seal": "PASS",
        "terminal_hash_seal": "PASS",
        "official_naturalization_retry_allowed": True,
        "registry_runtime_compatibility_current_source_alignment": (
            "stale_requires_successor_rtc"
        ),
        "non_claims": {
            "naturalization_phase_3_through_8_complete": False,
            "publish_boundary_pass": False,
            "runtime_package_compatibility": "not_evaluated",
            "successor_registry_runtime_compatibility_closure": False,
            "public_repetition_issue_removed": "not_yet_claimed",
            "power_loss_atomicity_claimed": False,
            "intermediate_reader_visibility_zero_claimed": False,
        },
        "post_terminal_claim_bearing_change_allowed": False,
    }
    write_once_json(terminal_path, terminal)
    return {
        **terminal,
        "terminal_hash_seal_sha256": sha256_file(terminal_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DVF 3-3 Food Semantic Registry operational cutover"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in (
        "prepare",
        "authorization-template",
        "apply",
        "verify-committed",
        "run-final-validation",
        "owner-seal-template",
        "finalize",
    ):
        child = subparsers.add_parser(name)
        child.add_argument("--attempt-id", required=True)
        if name == "apply":
            child.add_argument(
                "--inject-failure",
                choices=("second_replace", "post_write_verification"),
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = command_prepare(args.attempt_id)
        elif args.command == "authorization-template":
            result = command_authorization_template(args.attempt_id)
        elif args.command == "apply":
            result = command_apply(args.attempt_id, args.inject_failure)
        elif args.command == "verify-committed":
            result = command_verify_committed(args.attempt_id)
        elif args.command == "run-final-validation":
            result = command_run_final_validation(args.attempt_id)
        elif args.command == "owner-seal-template":
            result = command_owner_seal_template(args.attempt_id)
        else:
            result = command_finalize(args.attempt_id)
    except CutoverError as exc:
        print(
            json.dumps(
                {
                    "schema_version": "food-semantic-registry-cutover-error-v1",
                    "status": "BLOCKED",
                    "failure": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
