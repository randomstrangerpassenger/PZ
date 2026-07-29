from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import dvf_3_3_food_semantic_registry_cutover as transaction_core


REPO_ROOT = Path(__file__).resolve().parents[6]
V2_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2"
ROUND_ROOT = (
    V2_ROOT / "staging" / "dvf_3_3_food_semantic_registry_operational_cutover"
)
ATTEMPTS_ROOT = ROUND_ROOT / "attempts"
ATTEMPT_ID = "attempt-0011"

CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
CURRENT_FACTS_REL = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
CURRENT_MANIFEST_REL = (
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
)

SUCCESSOR_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_current_facts_correction_successor"
    / "successors"
    / "correction-0002"
)
SUCCESSOR_FACTS = SUCCESSOR_ROOT / "successor_facts.jsonl"
SUCCESSOR_MANIFEST = SUCCESSOR_ROOT / "successor_input_manifest.json"
SUCCESSOR_RECEIPT = SUCCESSOR_ROOT / "successor_receipt.json"
PATCH_LEDGER = SUCCESSOR_ROOT / "correction_patch_ledger.jsonl"
NON_TARGET_REPORT = SUCCESSOR_ROOT / "non_target_byte_identity_report.json"
REGRESSION_REPORT = SUCCESSOR_ROOT / "correction_0001_regression_report.json"
COHORT_SUMMARY = SUCCESSOR_ROOT / "cohort_summary.json"
UNRESOLVED_ROWS = SUCCESSOR_ROOT / "unresolved_rows.jsonl"

PREVIOUS_RECEIPT = (
    ATTEMPTS_ROOT
    / "attempt-0010"
    / "closeout"
    / "registry_correction_adoption_receipt.json"
)
INITIAL_G3_RECEIPT = (
    ATTEMPTS_ROOT
    / "attempt-0009"
    / "closeout"
    / "registry_adoption_receipt.json"
)
REGISTRY_CONTRACT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "authority"
    / "food_semantic"
    / "registry_adoption_contract.json"
)
NATURALIZATION_CONTRACT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "food_semantic_registry_adoption_contract.json"
)
CONTRACT_DOC = (
    REPO_ROOT / "docs" / "dvf_3_3_current_facts_correction_successor_contract.md"
)
LOCK_PATH = ROUND_ROOT / ".current-facts-correction-0002.lock"

INPUT_COMMIT = "ea38a238bef5d7e7e283b03adcef22e0bae31e50"
INPUT_TREE = "052edaf9ebf2f8fa5484b4d27e535db59450c61a"
REQUIRED_ANCESTOR = "ca851a1e10bd37be71deded1fcc57b0d8462db48"
PREIMAGE_FACTS_SHA256 = (
    "ca74270191289af064d9d8fa9d739c97b0865d69e255885e815b01565243f46e"
)
PREIMAGE_MANIFEST_SHA256 = (
    "c9670c1625382444fe292158e6b50e65e2ee54316d2903835ebc4f59c199257d"
)
SUCCESSOR_FACTS_SHA256 = (
    "37db2595eff9b58f7b08e59221e950cb529453bd96733fb29171d458e46118f6"
)
SUCCESSOR_MANIFEST_SHA256 = (
    "e5ccc87ad00e3c8f009ad79a294ea771046d16e12a3582908bcb813545e7e63e"
)
SUCCESSOR_RECEIPT_SHA256 = (
    "5d01e7c6d19336ed5231163060e636ad45ff6a79cc6f40faf971a89d4f8810fe"
)
PREVIOUS_RECEIPT_SHA256 = (
    "92cb65656562ec874dafea118c85ce424e2f391f36ee27860029c6fef582978f"
)
INITIAL_G3_RECEIPT_SHA256 = (
    "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
)
REGISTRY_CONTRACT_PREIMAGE_SHA256 = (
    "c6d315e428f600878dc43d896b574398c0fd932d35a5824bbae6dab8e3c7906a"
)
NATURALIZATION_CONTRACT_PREIMAGE_SHA256 = (
    "23647599d56310d4e8ec25dc7b5367b68bcef9f7b51deaabb9bb18358aec3811"
)

PROJECTION_ALLOWED_PATHS = {
    "authority_role",
    "current_facts_correction_successor.current_authority_mutated",
    "current_facts_correction_successor.registry_cutover_attempt_id",
    "current_facts_correction_successor.registry_cutover_performed",
    "current_facts_correction_successor.successor_receipt_path",
    "current_facts_correction_successor.successor_receipt_sha256",
    "facts.path",
    "facts.role",
    "food_semantic_authority.current_adoption_allowed",
    "food_semantic_authority.non_current",
    "food_semantic_authority.registry_adoption_state",
    "food_semantic_authority.registry_cutover_attempt_id",
    "source_promotion.current_facts_correction_adoption_0002_binding",
    "status",
}

PROTECTED_PREFIXES = (
    "Iris/build/description/v2/staging/dvf_3_3_food_semantic_facts_authority/"
    "attempts/attempt-0022/",
    "Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_"
    "operational_cutover/attempts/attempt-0009/",
    "Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_"
    "operational_cutover/attempts/attempt-0010/",
    "Iris/build/description/v2/staging/dvf_3_3_current_facts_correction_"
    "successor/successors/correction-0001/",
    "Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_"
    "public_text_rewrite_closure/",
)
PROTECTED_EXCEPTIONS = {
    (
        "Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_"
        "public_text_rewrite_closure/food_semantic_registry_adoption_contract.json"
    ),
}


class CorrectionCutoverError(RuntimeError):
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


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CorrectionCutoverError(f"json_object_required:{path}")
    return value


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise CorrectionCutoverError(
            f"{label}_mismatch:expected={expected!r}:actual={actual!r}"
        )


def require_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise CorrectionCutoverError(f"{label}_missing:{path}")
    require_equal(sha256_file(path), expected, label)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        raise CorrectionCutoverError(
            f"git_failed:{args}:{result.stderr.strip()}"
        )
    return result


def git_output(*args: str) -> str:
    return git(*args).stdout.strip()


def git_blob_bytes(commit: str, path: Path) -> bytes:
    relative = repo_relative(path)
    result = subprocess.run(
        ["git", "cat-file", "blob", f"{commit}:{relative}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise CorrectionCutoverError(
            f"git_blob_read_failed:{commit}:{relative}:"
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return result.stdout


def git_text_attribute(path: Path) -> str:
    output = git_output("check-attr", "text", "--", repo_relative(path))
    marker = ": text: "
    if marker not in output:
        raise CorrectionCutoverError(
            f"git_text_attribute_unparseable:{repo_relative(path)}:{output}"
        )
    return output.rsplit(marker, 1)[1]


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    return git("merge-base", "--is-ancestor", ancestor, descendant, check=False).returncode == 0


def require_clean_worktree() -> None:
    require_equal(git_output("status", "--porcelain"), "", "worktree_clean")


def attempt_root(attempt_id: str) -> Path:
    require_equal(attempt_id, ATTEMPT_ID, "attempt_id")
    root = (ATTEMPTS_ROOT / attempt_id).resolve()
    require_equal(root.parent, ATTEMPTS_ROOT.resolve(), "attempt_parent")
    return root


def deep_diff(before: Any, after: Any, path: str = "") -> list[dict[str, Any]]:
    if type(before) is not type(after):
        return [{"path": path, "before": before, "after": after}]
    if isinstance(before, dict):
        result: list[dict[str, Any]] = []
        for key in sorted(set(before) | set(after)):
            child = f"{path}.{key}" if path else key
            if key not in before:
                result.append({"path": child, "before": None, "after": after[key]})
            elif key not in after:
                result.append({"path": child, "before": before[key], "after": None})
            else:
                result.extend(deep_diff(before[key], after[key], child))
        return result
    if isinstance(before, list):
        if before == after:
            return []
        return [{"path": path, "before": before, "after": after}]
    if before != after:
        return [{"path": path, "before": before, "after": after}]
    return []


def protected_inventory(commit: str) -> dict[str, str]:
    output = git_output("ls-tree", "-r", "--full-tree", commit)
    inventory: dict[str, str] = {}
    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        blob = metadata.split()[2]
        normalized = path.replace("\\", "/")
        if (
            any(normalized.startswith(prefix) for prefix in PROTECTED_PREFIXES)
            and normalized not in PROTECTED_EXCEPTIONS
        ):
            inventory[normalized] = blob
        elif (
            normalized.startswith("Iris/build/description/v2/staging/")
            and (
                normalized.endswith("receipt.json")
                or normalized.endswith("terminal_hash_seal.json")
                or normalized.endswith("terminal_correction_hash_seal.json")
            )
        ):
            inventory[normalized] = blob
    return dict(sorted(inventory.items()))


def validate_protected_inventory(commit: str) -> dict[str, Any]:
    expected = protected_inventory(INPUT_COMMIT)
    observed = protected_inventory(commit)
    actual = {path: observed.get(path) for path in expected}
    require_equal(actual, expected, "protected_artifact_inventory")
    return {
        "status": "PASS",
        "protected_path_count": len(expected),
        "inventory_sha256": canonical_hash(expected),
        "input_commit": INPUT_COMMIT,
        "observed_commit": commit,
    }


def validate_entry_identity() -> dict[str, Any]:
    require_equal(git_output("rev-parse", f"{INPUT_COMMIT}^{{tree}}"), INPUT_TREE, "input_tree")
    head = git_output("rev-parse", "HEAD")
    if not git_is_ancestor(INPUT_COMMIT, head):
        raise CorrectionCutoverError("head_not_descendant_of_exact_input_commit")
    if not git_is_ancestor(REQUIRED_ANCESTOR, INPUT_COMMIT):
        raise CorrectionCutoverError("required_ancestor_not_ancestor_of_input")
    return {
        "status": "PASS",
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "required_ancestor": REQUIRED_ANCESTOR,
        "required_ancestor_verified": True,
        "implementation_commit": head,
        "implementation_tree": git_output("rev-parse", "HEAD^{tree}"),
    }


def count_jsonl(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for line in handle if line.strip())


def validate_inputs() -> dict[str, Any]:
    require_hash(CURRENT_FACTS, PREIMAGE_FACTS_SHA256, "current_facts_preimage")
    require_hash(
        CURRENT_MANIFEST,
        PREIMAGE_MANIFEST_SHA256,
        "current_manifest_preimage",
    )
    require_hash(SUCCESSOR_FACTS, SUCCESSOR_FACTS_SHA256, "successor_facts")
    require_hash(
        SUCCESSOR_MANIFEST,
        SUCCESSOR_MANIFEST_SHA256,
        "successor_manifest",
    )
    require_hash(
        SUCCESSOR_RECEIPT,
        SUCCESSOR_RECEIPT_SHA256,
        "successor_receipt",
    )
    require_hash(PREVIOUS_RECEIPT, PREVIOUS_RECEIPT_SHA256, "previous_receipt")
    require_hash(
        INITIAL_G3_RECEIPT,
        INITIAL_G3_RECEIPT_SHA256,
        "initial_g3_receipt",
    )
    require_hash(
        REGISTRY_CONTRACT,
        REGISTRY_CONTRACT_PREIMAGE_SHA256,
        "registry_contract_preimage",
    )
    require_hash(
        NATURALIZATION_CONTRACT,
        NATURALIZATION_CONTRACT_PREIMAGE_SHA256,
        "naturalization_contract_preimage",
    )

    receipt = read_json(SUCCESSOR_RECEIPT)
    require_equal(receipt.get("status"), "PASS", "successor_receipt_status")
    require_equal(
        receipt.get("successor_facts_sha256"),
        SUCCESSOR_FACTS_SHA256,
        "receipt_successor_facts",
    )
    require_equal(
        receipt.get("successor_manifest_sha256"),
        SUCCESSOR_MANIFEST_SHA256,
        "receipt_successor_manifest",
    )
    require_equal(receipt.get("corrected_row_count"), 67, "corrected_row_count")
    require_equal(receipt.get("correction_patch_count"), 70, "patch_count")
    require_equal(receipt.get("unresolved_row_count"), 0, "unresolved_count")
    require_equal(
        receipt.get("layer4_evidence_consumed_count"),
        0,
        "layer4_evidence_consumed",
    )
    require_equal(
        receipt.get("previous_correction_regression_count"),
        0,
        "receipt_previous_correction_regression",
    )
    require_equal(count_jsonl(PATCH_LEDGER), 70, "patch_ledger_line_count")
    require_equal(count_jsonl(UNRESOLVED_ROWS), 0, "unresolved_file_line_count")

    identity = read_json(NON_TARGET_REPORT)
    require_equal(identity.get("status"), "PASS", "non_target_status")
    require_equal(
        identity.get("non_target_byte_identical_count"),
        2038,
        "non_target_identical",
    )
    require_equal(
        identity.get("non_target_row_denominator"),
        2038,
        "non_target_denominator",
    )
    require_equal(
        identity.get("non_target_byte_mismatch_count"),
        0,
        "non_target_mismatch",
    )

    regression = read_json(REGRESSION_REPORT)
    require_equal(regression.get("status"), "PASS", "regression_status")
    require_equal(
        regression.get("previous_corrected_row_denominator"),
        184,
        "previous_correction_denominator",
    )
    require_equal(regression.get("regression_count"), 0, "regression_count")
    require_equal(
        regression.get("successor_preserved_correction_0001_count"),
        184,
        "previous_correction_preserved",
    )
    cohort = read_json(COHORT_SUMMARY)
    require_equal(cohort.get("corrected_row_count"), 67, "cohort_corrected")
    require_equal(cohort.get("correction_patch_count"), 70, "cohort_patches")
    require_equal(cohort.get("unresolved_row_count"), 0, "cohort_unresolved")
    require_equal(
        cohort.get("layer4_evidence_consumed_count"),
        0,
        "cohort_layer4",
    )
    require_equal(count_jsonl(SUCCESSOR_FACTS), 2105, "successor_row_count")
    return {
        "status": "PASS",
        "current_preimages": {
            "facts": PREIMAGE_FACTS_SHA256,
            "manifest": PREIMAGE_MANIFEST_SHA256,
        },
        "successor": {
            "facts": SUCCESSOR_FACTS_SHA256,
            "manifest": SUCCESSOR_MANIFEST_SHA256,
            "receipt": SUCCESSOR_RECEIPT_SHA256,
        },
        "corrected_row_count": 67,
        "correction_patch_count": 70,
        "unresolved_row_count": 0,
        "non_target_byte_identity": "2038/2038",
        "previous_correction_regression": "0/184",
        "layer4_evidence_consumed_count": 0,
    }


def build_current_manifest_projection(attempt_id: str) -> dict[str, Any]:
    source = read_json(SUCCESSOR_MANIFEST)
    projected = copy.deepcopy(source)
    projected["status"] = "current_authority"
    projected["authority_role"] = "successor_current_source_authority"
    projected["facts"]["path"] = CURRENT_FACTS_REL
    projected["facts"]["role"] = "current_source_authority"
    food = projected["food_semantic_authority"]
    food["non_current"] = False
    food["current_adoption_allowed"] = True
    food["registry_adoption_state"] = "current_correction_0002"
    food["registry_cutover_attempt_id"] = attempt_id
    successor_binding = projected["current_facts_correction_successor"]
    successor_binding["registry_cutover_performed"] = True
    successor_binding["current_authority_mutated"] = True
    successor_binding["registry_cutover_attempt_id"] = attempt_id
    successor_binding["successor_receipt_path"] = repo_relative(SUCCESSOR_RECEIPT)
    successor_binding["successor_receipt_sha256"] = SUCCESSOR_RECEIPT_SHA256
    projected["source_promotion"][
        "current_facts_correction_adoption_0002_binding"
    ] = {
        "schema_version": "dvf-3-3-current-facts-correction-adoption-binding-v2",
        "append_only": True,
        "successor_id": "correction-0002",
        "registry_cutover_attempt_id": attempt_id,
        "predecessor_current_facts_sha256": PREIMAGE_FACTS_SHA256,
        "predecessor_current_manifest_sha256": PREIMAGE_MANIFEST_SHA256,
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "sealed_successor_manifest_path": repo_relative(SUCCESSOR_MANIFEST),
        "sealed_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "successor_receipt_path": repo_relative(SUCCESSOR_RECEIPT),
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "previous_correction_receipt_path": repo_relative(PREVIOUS_RECEIPT),
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "initial_g3_adoption_receipt_path": repo_relative(INITIAL_G3_RECEIPT),
        "initial_g3_adoption_receipt_sha256": INITIAL_G3_RECEIPT_SHA256,
        "post_adoption_predecessor_restore_allowed": False,
        "partial_current_allowed": False,
        "dual_current_allowed": False,
    }
    return projected


def validate_projection(projected: dict[str, Any], attempt_id: str) -> list[dict[str, Any]]:
    source = read_json(SUCCESSOR_MANIFEST)
    differences = deep_diff(source, projected)
    actual = {entry["path"] for entry in differences}
    require_equal(actual, PROJECTION_ALLOWED_PATHS, "projection_allowlist")
    require_equal(
        projected,
        build_current_manifest_projection(attempt_id),
        "projection_exact",
    )
    require_equal(
        projected["facts"]["sha256"],
        SUCCESSOR_FACTS_SHA256,
        "projection_facts_sha",
    )
    require_equal(
        projected["current_facts_correction"],
        source["current_facts_correction"],
        "correction_0001_binding_immutable",
    )
    require_equal(
        projected["source_promotion"]["current_facts_correction_binding"],
        source["source_promotion"]["current_facts_correction_binding"],
        "registry_adoption_predecessor_binding_immutable",
    )
    return differences


def candidate_paths(root: Path) -> tuple[Path, Path]:
    return (
        root / "candidate" / "current_facts.jsonl",
        root / "candidate" / "current_input_manifest.json",
    )


def expected_candidates(root: Path) -> dict[str, str]:
    facts, manifest = candidate_paths(root)
    return {"facts": sha256_file(facts), "manifest": sha256_file(manifest)}


def write_once_json(path: Path, value: Any) -> None:
    transaction_core.write_once_json(path, value)


def command_prepare(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    require_clean_worktree()
    if root.exists():
        raise CorrectionCutoverError("attempt_already_exists")
    entry = validate_entry_identity()
    inputs = validate_inputs()
    preservation = validate_protected_inventory(entry["implementation_commit"])
    projection = build_current_manifest_projection(attempt_id)
    differences = validate_projection(projection, attempt_id)

    candidate_facts, candidate_manifest = candidate_paths(root)
    transaction_core.write_once_bytes(candidate_facts, SUCCESSOR_FACTS.read_bytes())
    transaction_core.write_once_bytes(
        candidate_manifest,
        canonical_json_bytes(projection),
    )
    require_equal(
        sha256_file(candidate_facts),
        SUCCESSOR_FACTS_SHA256,
        "candidate_facts",
    )
    candidate_hashes = expected_candidates(root)
    preflight = {
        "schema_version": "dvf-3-3-registry-correction-0002-preimage-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "generated_at": now_iso(),
        "entry_identity": entry,
        "input_validation": inputs,
        "preservation": preservation,
        "candidate_hashes": candidate_hashes,
        "projection_source_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "projection_allowed_paths": sorted(PROJECTION_ALLOWED_PATHS),
        "projection_differences": differences,
        "candidate_first": True,
        "live_current_mutation_count": 0,
        "forbidden_scope_execution_count": 0,
    }
    write_once_json(root / "preflight" / "current_preimage_report.json", preflight)
    authorization = {
        "schema_version": "dvf-3-3-registry-correction-owner-authorization-v2",
        "status": "AUTHORIZED",
        "attempt_id": attempt_id,
        "authority": "project_owner_user_prompt",
        "scope": "correction-0002-registry-current-adoption-only",
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "candidate_hashes": candidate_hashes,
        "one_use_nonce": uuid.uuid4().hex,
        "partial_current_allowed": False,
        "dual_current_allowed": False,
        "post_adoption_predecessor_restore_allowed": False,
        "authorized_at": now_iso(),
    }
    write_once_json(
        root / "authorization" / "owner_correction_cutover_authorization.json",
        authorization,
    )
    return preflight


def _fixture_pair(root: Path) -> tuple[Path, Path, Path, Path]:
    facts_target = root / "targets" / "facts.jsonl"
    manifest_target = root / "targets" / "manifest.json"
    facts_candidate = root / "candidate" / "facts.jsonl"
    manifest_candidate = root / "candidate" / "manifest.json"
    transaction_core.atomic_write_bytes(facts_target, CURRENT_FACTS.read_bytes())
    transaction_core.atomic_write_bytes(
        manifest_target,
        CURRENT_MANIFEST.read_bytes(),
    )
    source_facts, source_manifest = candidate_paths(attempt_root(ATTEMPT_ID))
    transaction_core.atomic_write_bytes(facts_candidate, source_facts.read_bytes())
    transaction_core.atomic_write_bytes(
        manifest_candidate,
        source_manifest.read_bytes(),
    )
    return facts_target, manifest_target, facts_candidate, manifest_candidate


def _restore_uncommitted_fixture(
    root: Path,
    facts_target: Path,
    manifest_target: Path,
) -> dict[str, Any]:
    rollback = transaction_core.restore_snapshots(
        root,
        facts_target,
        manifest_target,
        {"facts": PREIMAGE_FACTS_SHA256, "manifest": PREIMAGE_MANIFEST_SHA256},
    )
    write_once_json(
        root / "transaction" / "startup_recovery.json",
        {
            "schema_version": "dvf-3-3-registry-correction-startup-recovery-v1",
            "status": "PASS",
            "observed_state": read_json(
                root / "transaction" / "cutover_journal.json"
            )["state"],
            "resolution": "both_preimages_restored",
            "same_attempt_retry_allowed": False,
            "rollback": rollback,
        },
    )
    return rollback


def command_failure_injection_check(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    require_equal(preflight.get("status"), "PASS", "preflight_status")
    live_before = {
        "facts": sha256_file(CURRENT_FACTS),
        "manifest": sha256_file(CURRENT_MANIFEST),
    }
    require_equal(
        live_before,
        {"facts": PREIMAGE_FACTS_SHA256, "manifest": PREIMAGE_MANIFEST_SHA256},
        "live_preimage_before_failure_injection",
    )
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="dvf-correction-0002-fi-") as temporary:
        temporary_root = Path(temporary)
        fixture_lock = temporary_root / "exclusive_lock.json"
        with transaction_core.transaction_lock(
            {"mode": "failure_injection_primary_lock"},
            lock_path=fixture_lock,
        ):
            try:
                with transaction_core.transaction_lock(
                    {"mode": "failure_injection_competing_lock"},
                    lock_path=fixture_lock,
                ):
                    raise CorrectionCutoverError(
                        "competing_lock_unexpectedly_acquired"
                    )
            except transaction_core.CutoverError as exc:
                results.append(
                    {
                        "scenario": "exclusive_lock_contention",
                        "status": "PASS",
                        "expected_failure": str(exc),
                    }
                )
        for scenario in ("second_replace", "post_write_verification"):
            fixture = temporary_root / scenario
            targets = _fixture_pair(fixture)
            try:
                transaction_core.execute_pair_transaction(
                    root=fixture,
                    facts_target=targets[0],
                    manifest_target=targets[1],
                    facts_candidate=targets[2],
                    manifest_candidate=targets[3],
                    expected_preimages={
                        "facts": PREIMAGE_FACTS_SHA256,
                        "manifest": PREIMAGE_MANIFEST_SHA256,
                    },
                    expected_candidates=expected_candidates(root),
                    inject_failure=scenario,
                )
            except transaction_core.CutoverError as exc:
                observed = {
                    "facts": sha256_file(targets[0]),
                    "manifest": sha256_file(targets[1]),
                }
                require_equal(
                    observed,
                    {
                        "facts": PREIMAGE_FACTS_SHA256,
                        "manifest": PREIMAGE_MANIFEST_SHA256,
                    },
                    f"{scenario}_rollback",
                )
                failure = read_json(
                    fixture / "transaction" / "transaction_failure.json"
                )
                require_equal(
                    failure.get("rollback", {}).get("status"),
                    "PASS",
                    f"{scenario}_rollback_status",
                )
                results.append(
                    {
                        "scenario": scenario,
                        "status": "PASS",
                        "expected_failure": str(exc),
                        "restored_preimages": observed,
                    }
                )
            else:
                raise CorrectionCutoverError(
                    f"failure_injection_did_not_fail:{scenario}"
                )

        for state in ("facts_replaced", "manifest_replaced"):
            fixture = temporary_root / f"crash_{state}"
            targets = _fixture_pair(fixture)
            transaction_core.create_rollback_snapshots(
                fixture,
                targets[0],
                targets[1],
                {"facts": PREIMAGE_FACTS_SHA256, "manifest": PREIMAGE_MANIFEST_SHA256},
            )
            transaction_core.update_journal(
                fixture,
                state="prepared",
                previous_state=None,
            )
            transaction_core.atomic_write_bytes(
                targets[0],
                targets[2].read_bytes(),
            )
            transaction_core.update_journal(
                fixture,
                state="facts_replaced",
                previous_state="prepared",
            )
            if state == "manifest_replaced":
                transaction_core.atomic_write_bytes(
                    targets[1],
                    targets[3].read_bytes(),
                )
                transaction_core.update_journal(
                    fixture,
                    state="manifest_replaced",
                    previous_state="facts_replaced",
                )
            rollback = _restore_uncommitted_fixture(
                fixture,
                targets[0],
                targets[1],
            )
            results.append(
                {
                    "scenario": f"startup_recovery_after_{state}",
                    "status": "PASS",
                    "resolution": "both_preimages_restored",
                    "rollback": rollback,
                }
            )
    live_after = {
        "facts": sha256_file(CURRENT_FACTS),
        "manifest": sha256_file(CURRENT_MANIFEST),
    }
    require_equal(live_after, live_before, "live_non_mutation_failure_injection")
    report = {
        "schema_version": "dvf-3-3-registry-correction-failure-injection-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "generated_at": now_iso(),
        "isolated_fixture_only": True,
        "scenario_count": len(results),
        "scenarios": results,
        "manifest_last_verified": True,
        "rollback_verified": True,
        "startup_recovery_verified": True,
        "live_current_before": live_before,
        "live_current_after": live_after,
        "live_current_mutation_count": 0,
    }
    write_once_json(root / "preflight" / "failure_injection_report.json", report)
    return report


def build_adoption_receipt(root: Path) -> dict[str, Any]:
    candidates = expected_candidates(root)
    require_equal(candidates["facts"], SUCCESSOR_FACTS_SHA256, "receipt_facts")
    return {
        "schema_version": "dvf-3-3-registry-correction-adoption-receipt-v2",
        "status": "PASS",
        "attempt_id": root.name,
        "successor_id": "correction-0002",
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "predecessor_current_facts_sha256": PREIMAGE_FACTS_SHA256,
        "predecessor_current_manifest_sha256": PREIMAGE_MANIFEST_SHA256,
        "successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "sealed_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "successor_receipt_path": repo_relative(SUCCESSOR_RECEIPT),
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "previous_correction_receipt_path": repo_relative(PREVIOUS_RECEIPT),
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "initial_g3_adoption_receipt_path": repo_relative(INITIAL_G3_RECEIPT),
        "initial_g3_adoption_receipt_sha256": INITIAL_G3_RECEIPT_SHA256,
        "corrected_row_count": 67,
        "correction_patch_count": 70,
        "unresolved_row_count": 0,
        "non_target_byte_identity": "2038/2038",
        "previous_correction_regression": "0/184",
        "layer4_evidence_consumed_count": 0,
        "candidate_first": True,
        "exclusive_lock": True,
        "facts_first": True,
        "manifest_last": True,
        "process_crash_recoverable": True,
        "rollback_snapshot_verified": True,
        "failure_injection_status": "PASS",
        "power_loss_atomicity_claimed": False,
        "single_filesystem_primitive_atomicity_claimed": False,
        "partial_current_allowed": False,
        "dual_current_allowed": False,
        "post_adoption_predecessor_restore_allowed": False,
        "forbidden_scope_execution_count": 0,
        "generated_at": now_iso(),
    }


def build_contract_projection(
    root: Path,
    receipt_path: Path,
) -> dict[str, Any]:
    contract = read_json(REGISTRY_CONTRACT)
    candidate_hashes = expected_candidates(root)
    predecessor_binding = copy.deepcopy(contract["current_correction"])
    binding = {
        "schema_version": "food-semantic-registry-correction-successor-binding-v1",
        "append_only": True,
        "successor_id": "correction-0002",
        "supersedes_successor_id": predecessor_binding["successor_id"],
        "predecessor_binding_sha256": canonical_hash(predecessor_binding),
        "predecessor_current_facts_sha256": PREIMAGE_FACTS_SHA256,
        "predecessor_current_manifest_sha256": PREIMAGE_MANIFEST_SHA256,
        "sealed_successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "sealed_successor_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "sealed_successor_manifest_path": repo_relative(SUCCESSOR_MANIFEST),
        "sealed_successor_manifest_sha256": SUCCESSOR_MANIFEST_SHA256,
        "successor_receipt_path": repo_relative(SUCCESSOR_RECEIPT),
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "registry_cutover_attempt_id": root.name,
        "current_facts_sha256": candidate_hashes["facts"],
        "current_manifest_sha256": candidate_hashes["manifest"],
        "registry_correction_adoption_receipt_path": repo_relative(receipt_path),
        "registry_correction_adoption_receipt_sha256": sha256_file(receipt_path),
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "initial_g3_adoption_receipt_sha256": INITIAL_G3_RECEIPT_SHA256,
        "post_adoption_predecessor_restore_allowed": False,
    }
    projected = copy.deepcopy(contract)
    projected["schema_version"] = "food-semantic-registry-adoption-contract-v4"
    projected["contract_id"] = (
        "dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v4"
    )
    projected["predecessor_contract"] = {
        "schema_version": contract["schema_version"],
        "contract_id": contract["contract_id"],
        "authority_deployment_sha256": REGISTRY_CONTRACT_PREIMAGE_SHA256,
        "naturalization_deployment_sha256": (
            NATURALIZATION_CONTRACT_PREIMAGE_SHA256
        ),
        "current_correction_binding_sha256": canonical_hash(
            contract["current_correction"]
        ),
    }
    projected["current_correction_successors"] = [binding]
    projected["current_correction_selection"] = {
        "successor_id": "correction-0002",
        "binding_path": "current_correction_successors[0]",
        "append_only_predecessor_path": "current_correction",
    }
    projected["registry_runtime_compatibility_successor"] = {
        "applies_when_current_facts_sha256": SUCCESSOR_FACTS_SHA256,
        "current_source_alignment_state": "stale_requires_successor_rtc",
        "successor_rtc_closure_complete": False,
        "live_bridge_runtime_package_publication_allowed": False,
        "rtc_executed_by_this_cutover": False,
    }
    require_equal(
        projected["current_correction"],
        contract["current_correction"],
        "contract_predecessor_binding_immutable",
    )
    return projected


def _authorization_and_nonce(root: Path) -> tuple[dict[str, Any], str]:
    authorization_path = (
        root / "authorization" / "owner_correction_cutover_authorization.json"
    )
    authorization = read_json(authorization_path)
    require_equal(authorization.get("status"), "AUTHORIZED", "authorization_status")
    require_equal(
        authorization.get("candidate_hashes"),
        expected_candidates(root),
        "authorization_candidates",
    )
    nonce = authorization["one_use_nonce"]
    return authorization, nonce


def _validate_consumed_nonce(
    root: Path,
    authorization: dict[str, Any],
    nonce: str,
) -> None:
    consumption = read_json(root / "transaction" / "nonce_consumption.json")
    require_equal(consumption.get("status"), "CONSUMED", "nonce_status")
    require_equal(consumption.get("attempt_id"), root.name, "nonce_attempt")
    require_equal(consumption.get("one_use_nonce"), nonce, "nonce_value")
    require_equal(
        consumption.get("authorization_sha256"),
        sha256_file(
            root
            / "authorization"
            / "owner_correction_cutover_authorization.json"
        ),
        "nonce_authorization",
    )
    require_equal(
        authorization.get("candidate_hashes"),
        expected_candidates(root),
        "consumed_authorization_candidates",
    )


def _recover_or_resume_live_transaction(root: Path) -> str:
    journal_path = root / "transaction" / "cutover_journal.json"
    journal = read_json(journal_path)
    state = journal.get("state")
    actual = {
        "facts": sha256_file(CURRENT_FACTS),
        "manifest": sha256_file(CURRENT_MANIFEST),
    }
    candidates = expected_candidates(root)
    preimages = {
        "facts": PREIMAGE_FACTS_SHA256,
        "manifest": PREIMAGE_MANIFEST_SHA256,
    }
    if state == "committed":
        require_equal(actual, candidates, "committed_resume_pair")
        return "committed_pair_resumed"
    if state == "verified":
        require_equal(actual, candidates, "verified_resume_pair")
        transaction_core.update_journal(
            root,
            state="committed",
            previous_state="verified",
        )
        return "verified_pair_completed"
    if state not in {"prepared", "facts_replaced", "manifest_replaced"}:
        raise CorrectionCutoverError(f"journal_state_not_recoverable:{state}")
    rollback = transaction_core.restore_snapshots(
        root,
        CURRENT_FACTS,
        CURRENT_MANIFEST,
        preimages,
    )
    recovery_path = root / "transaction" / "startup_recovery.json"
    if not recovery_path.exists():
        write_once_json(
            recovery_path,
            {
                "schema_version": (
                    "dvf-3-3-registry-correction-startup-recovery-v1"
                ),
                "status": "PASS",
                "attempt_id": root.name,
                "observed_state": state,
                "observed_pair_before_recovery": actual,
                "resolution": "both_preimages_restored",
                "rollback": rollback,
                "same_attempt_retry_allowed": False,
            },
        )
    raise CorrectionCutoverError(
        "interrupted_transaction_rolled_back_new_attempt_required"
    )


def command_apply(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    failure_report = read_json(root / "preflight" / "failure_injection_report.json")
    require_equal(failure_report.get("status"), "PASS", "failure_injection_status")
    require_equal(expected_candidates(root)["facts"], SUCCESSOR_FACTS_SHA256, "candidate_facts")
    authorization, nonce = _authorization_and_nonce(root)

    with transaction_core.transaction_lock(
        {
            "mode": "correction_0002_apply",
            "attempt_id": attempt_id,
            "input_commit": INPUT_COMMIT,
            "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        },
        lock_path=LOCK_PATH,
    ):
        journal_path = root / "transaction" / "cutover_journal.json"
        if journal_path.exists():
            observed_state = read_json(journal_path).get("state")
            if observed_state in {"verified", "committed"}:
                _validate_consumed_nonce(root, authorization, nonce)
            recovery_resolution = _recover_or_resume_live_transaction(root)
            result = {
                "status": "PASS",
                "installed_candidates": expected_candidates(root),
                "manifest_last_order": True,
                "process_crash_recovery_resolution": recovery_resolution,
                "power_loss_atomicity_claimed": False,
                "intermediate_reader_visibility_zero_claimed": False,
            }
        else:
            validate_inputs()

            def consume_nonce() -> None:
                write_once_json(
                    root / "transaction" / "nonce_consumption.json",
                    {
                        "schema_version": (
                            "dvf-3-3-registry-correction-nonce-consumption-v1"
                        ),
                        "status": "CONSUMED",
                        "attempt_id": attempt_id,
                        "one_use_nonce": nonce,
                        "authorization_sha256": sha256_file(
                            root
                            / "authorization"
                            / "owner_correction_cutover_authorization.json"
                        ),
                        "consumed_at": now_iso(),
                    },
                )

            facts_candidate, manifest_candidate = candidate_paths(root)
            result = transaction_core.execute_pair_transaction(
                root=root,
                facts_target=CURRENT_FACTS,
                manifest_target=CURRENT_MANIFEST,
                facts_candidate=facts_candidate,
                manifest_candidate=manifest_candidate,
                expected_preimages={
                    "facts": PREIMAGE_FACTS_SHA256,
                    "manifest": PREIMAGE_MANIFEST_SHA256,
                },
                expected_candidates=expected_candidates(root),
                before_first_replace=consume_nonce,
            )
            transaction_core.update_journal(
                root,
                state="committed",
                previous_state="verified",
            )

        receipt_path = (
            root / "closeout" / "registry_correction_adoption_receipt.json"
        )
        if receipt_path.exists():
            receipt = read_json(receipt_path)
            require_equal(receipt.get("status"), "PASS", "resumed_receipt_status")
            require_equal(
                receipt.get("current_facts_sha256"),
                SUCCESSOR_FACTS_SHA256,
                "resumed_receipt_facts",
            )
        else:
            write_once_json(receipt_path, build_adoption_receipt(root))
        contract_candidate_path = (
            root / "candidate" / "registry_adoption_contract.json"
        )
        if contract_candidate_path.exists():
            contract_candidate = read_json(contract_candidate_path)
        else:
            contract_candidate = build_contract_projection(root, receipt_path)
            write_once_json(contract_candidate_path, contract_candidate)
        transaction_core.atomic_write_bytes(
            REGISTRY_CONTRACT,
            contract_candidate_path.read_bytes(),
        )
        transaction_core.atomic_write_bytes(
            NATURALIZATION_CONTRACT,
            contract_candidate_path.read_bytes(),
        )
        require_equal(
            read_json(REGISTRY_CONTRACT),
            contract_candidate,
            "registry_contract_projection",
        )
        require_equal(
            read_json(NATURALIZATION_CONTRACT),
            contract_candidate,
            "naturalization_contract_projection",
        )
    return {
        **result,
        "attempt_id": attempt_id,
        "current_facts_sha256": sha256_file(CURRENT_FACTS),
        "current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
        "registry_correction_adoption_receipt_path": repo_relative(receipt_path),
        "registry_correction_adoption_receipt_sha256": sha256_file(receipt_path),
        "append_only_registry_contract_binding": "PASS",
    }


def adoption_allowed_paths(root: Path) -> set[str]:
    return {
        CURRENT_FACTS_REL,
        CURRENT_MANIFEST_REL,
        repo_relative(REGISTRY_CONTRACT),
        repo_relative(NATURALIZATION_CONTRACT),
        *(
            repo_relative(path)
            for path in root.rglob("*")
            if path.is_file()
        ),
    }


def command_verify_adoption_commit(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    require_clean_worktree()
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    implementation_commit = preflight["entry_identity"]["implementation_commit"]
    head = git_output("rev-parse", "HEAD")
    ancestry_path = [
        line
        for line in git_output(
            "rev-list",
            "--ancestry-path",
            "--reverse",
            f"{implementation_commit}..{head}",
        ).splitlines()
        if line
    ]
    if not ancestry_path:
        raise CorrectionCutoverError("adoption_commit_not_found")
    adoption_commit = ancestry_path[0]
    require_equal(
        git_output("rev-parse", f"{adoption_commit}^"),
        implementation_commit,
        "adoption_parent",
    )
    changed = set(
        line
        for line in git_output(
            "diff", "--name-only", f"{implementation_commit}..{adoption_commit}"
        ).splitlines()
        if line
    )
    allowed = adoption_allowed_paths(root)
    unexpected = sorted(changed - allowed)
    if unexpected:
        raise CorrectionCutoverError(
            f"adoption_commit_unexpected_paths:{unexpected}"
        )
    required = {
        CURRENT_FACTS_REL,
        CURRENT_MANIFEST_REL,
        repo_relative(REGISTRY_CONTRACT),
        repo_relative(NATURALIZATION_CONTRACT),
        repo_relative(
            root / "closeout" / "registry_correction_adoption_receipt.json"
        ),
        repo_relative(root / "transaction" / "cutover_journal.json"),
        repo_relative(root / "transaction" / "rollback_current_facts.jsonl"),
        repo_relative(
            root / "transaction" / "rollback_current_input_manifest.json"
        ),
    }
    require_equal(required - changed, set(), "adoption_required_paths")
    candidates = expected_candidates(root)
    require_equal(sha256_file(CURRENT_FACTS), candidates["facts"], "current_facts")
    require_equal(
        sha256_file(CURRENT_MANIFEST),
        candidates["manifest"],
        "current_manifest",
    )
    require_equal(candidates["facts"], SUCCESSOR_FACTS_SHA256, "current_successor")
    journal = read_json(root / "transaction" / "cutover_journal.json")
    require_equal(journal.get("state"), "committed", "journal_state")
    contract_candidate = read_json(
        root / "candidate" / "registry_adoption_contract.json"
    )
    require_equal(read_json(REGISTRY_CONTRACT), contract_candidate, "registry_contract")
    require_equal(
        read_json(NATURALIZATION_CONTRACT),
        contract_candidate,
        "naturalization_contract",
    )
    preservation = validate_protected_inventory(adoption_commit)
    receipt_path = (
        root / "closeout" / "registry_correction_adoption_receipt.json"
    )
    receipt = read_json(receipt_path)
    require_equal(receipt.get("status"), "PASS", "adoption_receipt")

    identity = {
        "schema_version": "dvf-3-3-current-correction-identity-report-v2",
        "status": "PASS",
        "attempt_id": attempt_id,
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "adoption_commit": adoption_commit,
        "adoption_tree": git_output("rev-parse", f"{adoption_commit}^{{tree}}"),
        "current_facts_path": CURRENT_FACTS_REL,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_path": CURRENT_MANIFEST_REL,
        "current_manifest_sha256": candidates["manifest"],
        "successor_facts_byte_identity": True,
        "sealed_non_current_manifest_copied_unchanged": False,
        "current_adoption_projection_validation": "PASS",
        "single_current_identity": True,
        "partial_current_count": 0,
        "dual_current_count": 0,
        "post_adoption_predecessor_restore_allowed": False,
        "preservation": preservation,
        "generated_at": now_iso(),
    }
    identity_path = root / "closeout" / "current_correction_identity_report.json"
    write_once_json(identity_path, identity)

    handoff = {
        "schema_version": "dvf-3-3-naturalization-current-input-handoff-v2",
        "status": "READY_FOR_FOUNDATION_REBIND",
        "attempt_id": attempt_id,
        "registry_adoption_commit": adoption_commit,
        "registry_adoption_tree": identity["adoption_tree"],
        "current_facts_path": CURRENT_FACTS_REL,
        "current_facts_sha256": candidates["facts"],
        "current_manifest_path": CURRENT_MANIFEST_REL,
        "current_manifest_sha256": candidates["manifest"],
        "registry_correction_adoption_receipt_path": repo_relative(receipt_path),
        "registry_correction_adoption_receipt_sha256": sha256_file(receipt_path),
        "required_next_stage": "Foundation_current_input_rebind",
        "naturalization_attempt_started": False,
        "official_publish_started": False,
        "rtc_executed": False,
        "forbidden_direct_phase_reentry": True,
        "generated_at": now_iso(),
    }
    handoff_path = root / "handoff" / "naturalization_current_input_handoff.json"
    write_once_json(handoff_path, handoff)

    terminal = {
        "schema_version": "dvf-3-3-terminal-correction-hash-seal-v2",
        "status": "PASS",
        "attempt_id": attempt_id,
        "successor_id": "correction-0002",
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "adoption_commit": adoption_commit,
        "adoption_tree": identity["adoption_tree"],
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "successor_receipt_sha256": SUCCESSOR_RECEIPT_SHA256,
        "previous_correction_receipt_sha256": PREVIOUS_RECEIPT_SHA256,
        "initial_g3_adoption_receipt_sha256": INITIAL_G3_RECEIPT_SHA256,
        "registry_correction_adoption_receipt_path": repo_relative(receipt_path),
        "registry_correction_adoption_receipt_sha256": sha256_file(receipt_path),
        "current_identity_report_path": repo_relative(identity_path),
        "current_identity_report_sha256": sha256_file(identity_path),
        "naturalization_current_input_handoff_path": repo_relative(handoff_path),
        "naturalization_current_input_handoff_sha256": sha256_file(handoff_path),
        "transaction_journal_sha256": sha256_file(
            root / "transaction" / "cutover_journal.json"
        ),
        "rollback_snapshot_manifest_sha256": sha256_file(
            root / "transaction" / "rollback_snapshot_manifest.json"
        ),
        "failure_injection_report_sha256": sha256_file(
            root / "preflight" / "failure_injection_report.json"
        ),
        "atomicity_model": "process_crash_recoverable_two_file_transaction",
        "manifest_last": True,
        "rollback_verified": True,
        "failure_injection_status": "PASS",
        "post_adoption_predecessor_restore_allowed": False,
        "forbidden_scope_execution_count": 0,
        "generated_at": now_iso(),
    }
    terminal_path = root / "closeout" / "terminal_correction_hash_seal.json"
    write_once_json(terminal_path, terminal)
    return {
        "status": "PASS",
        "adoption_commit": adoption_commit,
        "adoption_tree": identity["adoption_tree"],
        "current_facts_sha256": candidates["facts"],
        "current_manifest_sha256": candidates["manifest"],
        "receipt_path": repo_relative(receipt_path),
        "receipt_sha256": sha256_file(receipt_path),
        "terminal_path": repo_relative(terminal_path),
        "terminal_sha256": sha256_file(terminal_path),
    }


def command_verify_closeout(attempt_id: str) -> dict[str, Any]:
    root = attempt_root(attempt_id)
    require_clean_worktree()
    terminal_path = root / "closeout" / "terminal_correction_hash_seal.json"
    terminal = read_json(terminal_path)
    require_equal(terminal.get("status"), "PASS", "terminal_status")
    require_equal(sha256_file(CURRENT_FACTS), SUCCESSOR_FACTS_SHA256, "current_facts")
    candidate_hashes = expected_candidates(root)
    require_equal(
        sha256_file(CURRENT_MANIFEST),
        candidate_hashes["manifest"],
        "current_manifest",
    )
    closeout_commit = git_output("rev-parse", "HEAD")
    adoption_commit = terminal["adoption_commit"]
    if not git_is_ancestor(adoption_commit, closeout_commit):
        raise CorrectionCutoverError("adoption_not_ancestor_of_closeout")
    required_closeout_paths = (
        terminal_path,
        root / "closeout" / "current_correction_identity_report.json",
        root / "handoff" / "naturalization_current_input_handoff.json",
    )
    for path in required_closeout_paths:
        git("cat-file", "-e", f"HEAD:{repo_relative(path)}")
    byte_identity_paths = [
        CURRENT_FACTS,
        CURRENT_MANIFEST,
        REGISTRY_CONTRACT,
        NATURALIZATION_CONTRACT,
        *sorted(path for path in root.rglob("*") if path.is_file()),
    ]
    byte_mismatches = [
        repo_relative(path)
        for path in byte_identity_paths
        if git_blob_bytes(closeout_commit, path) != path.read_bytes()
    ]
    require_equal(
        byte_mismatches,
        [],
        "committed_working_byte_identity",
    )
    text_attribute_mismatches = [
        {
            "path": repo_relative(path),
            "text_attribute": git_text_attribute(path),
        }
        for path in byte_identity_paths
        if git_text_attribute(path) != "unset"
    ]
    require_equal(
        text_attribute_mismatches,
        [],
        "cross_checkout_byte_identity_attributes",
    )
    require_equal(
        sha256_bytes(
            git_blob_bytes(
                closeout_commit,
                root / "candidate" / "current_facts.jsonl",
            )
        ),
        SUCCESSOR_FACTS_SHA256,
        "committed_candidate_facts_sha256",
    )
    require_equal(
        sha256_bytes(
            git_blob_bytes(
                closeout_commit,
                root / "transaction" / "rollback_current_facts.jsonl",
            )
        ),
        PREIMAGE_FACTS_SHA256,
        "committed_rollback_facts_sha256",
    )
    preservation = validate_protected_inventory(closeout_commit)
    return {
        "schema_version": "dvf-3-3-registry-correction-closeout-verification-v1",
        "status": "PASS",
        "input_commit": INPUT_COMMIT,
        "input_tree": INPUT_TREE,
        "adoption_commit": adoption_commit,
        "adoption_tree": terminal["adoption_tree"],
        "closeout_commit": closeout_commit,
        "closeout_tree": git_output("rev-parse", "HEAD^{tree}"),
        "current_facts_sha256": sha256_file(CURRENT_FACTS),
        "current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
        "receipt_path": terminal["registry_correction_adoption_receipt_path"],
        "receipt_sha256": terminal[
            "registry_correction_adoption_receipt_sha256"
        ],
        "terminal_path": repo_relative(terminal_path),
        "terminal_sha256": sha256_file(terminal_path),
        "atomicity": "PASS",
        "rollback": "PASS",
        "failure_injection": "PASS",
        "committed_working_byte_identity": "PASS",
        "committed_working_byte_identity_path_count": len(byte_identity_paths),
        "cross_checkout_byte_identity_attributes": "PASS",
        "preservation": preservation,
        "worktree_clean": True,
        "next_foundation_session_commit": closeout_commit,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DVF 3-3 correction successor 0002 Registry cutover"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in (
        "prepare",
        "failure-injection-check",
        "apply",
        "verify-adoption-commit",
        "verify-closeout",
    ):
        child = subparsers.add_parser(command)
        child.add_argument("--attempt-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "prepare":
            result = command_prepare(args.attempt_id)
        elif args.command == "failure-injection-check":
            result = command_failure_injection_check(args.attempt_id)
        elif args.command == "apply":
            result = command_apply(args.attempt_id)
        elif args.command == "verify-adoption-commit":
            result = command_verify_adoption_commit(args.attempt_id)
        else:
            result = command_verify_closeout(args.attempt_id)
    except (CorrectionCutoverError, transaction_core.CutoverError) as exc:
        print(
            json.dumps(
                {
                    "schema_version": (
                        "dvf-3-3-current-facts-correction-0002-cutover-error-v1"
                    ),
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
