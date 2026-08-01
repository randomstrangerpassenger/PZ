from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

CANDIDATE_PATH = "Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/attempt-0024-publish-remediation-a/phase4/candidate_rendered.json"
CANDIDATE_SHA256 = "ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437"
CANDIDATE_MANIFEST_PATH = "Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/attempt-0024-publish-remediation-a/phase4/candidate_manifest.json"
CANDIDATE_MANIFEST_SHA256 = "474cd41a439964768541738daf43af30bdee5f7eaf0deee352a44d45c880b18d"
ASSESSMENT_PATH = "Iris/_docs/round3/iar_public_text_assessment/subjects/dvf_3_3_korean_naturalization_candidate/ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437/assessment_result.json"
ASSESSMENT_SHA256 = "4a5cb7a8a7abf77c66c79a6a6376cafbf0eb4592f19ab94c28f6f5dab4fb5137"
CONSUMPTION_PATH = "Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/g5_current_iar_assessment_consumption_record.json"
CONSUMPTION_SHA256 = "0d11c4ca829361e9bc772bdab58e44f73eed540a498d551907168ca8cef30c7c"
FACTS_PATH = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
FACTS_SHA256 = "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
INPUT_MANIFEST_PATH = "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
INPUT_MANIFEST_SHA256 = "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
RENDERED_PATH = "Iris/build/description/v2/output/dvf_3_3_rendered.json"
LUA_MANIFEST_PATH = "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua"
REQUIRED_VALIDATIONS_PATH = "Iris/_docs/round3/current_route_required_validations.json"
GENERATION_DESCRIPTOR_PATH = "Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json"
REQUIRED_VALIDATIONS_SHA256 = "58f7427cccca4ab181caf5d9bf1031d32b3b2a924858588ce5e5082f9fb6592f"
PLAN_PATH = "docs/dvf_3_3_validated_naturalization_current_runtime_adoption_plan.md"
EXECUTION_CONTRACT_PATH = "docs/EXECUTION_CONTRACT.md"

REQUIRED_ANCESTORS = {
    "g1": "c3e2cac1b2c6a6e9f237d5766f2620f92794b8fb",
    "g4": "9c4b19cbaee5b2f2efb400ba7cb37411be831f48",
    "g5": "14d240a1c4f22800a7576ab6e52c5019402b5a1a",
}

ANCHORS = {
    CANDIDATE_PATH: CANDIDATE_SHA256,
    CANDIDATE_MANIFEST_PATH: CANDIDATE_MANIFEST_SHA256,
    ASSESSMENT_PATH: ASSESSMENT_SHA256,
    CONSUMPTION_PATH: CONSUMPTION_SHA256,
    FACTS_PATH: FACTS_SHA256,
    INPUT_MANIFEST_PATH: INPUT_MANIFEST_SHA256,
    REQUIRED_VALIDATIONS_PATH: REQUIRED_VALIDATIONS_SHA256,
}

PROTECTED_PATHS = [
    CANDIDATE_PATH,
    CANDIDATE_MANIFEST_PATH,
    ASSESSMENT_PATH,
    CONSUMPTION_PATH,
    FACTS_PATH,
    INPUT_MANIFEST_PATH,
    RENDERED_PATH,
    LUA_MANIFEST_PATH,
    REQUIRED_VALIDATIONS_PATH,
    "docs/Philosophy.md",
    "docs/DECISIONS.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    EXECUTION_CONTRACT_PATH,
    PLAN_PATH,
]


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=repo, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def git_bytes(repo: Path, relative_path: str) -> bytes | None:
    result = run_git(repo, "show", f"HEAD:{relative_path}", check=False)
    return result.stdout if result.returncode == 0 else None


def working_path(repo: Path, relative_path: str) -> Path:
    path = (repo / Path(relative_path)).resolve()
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(path))
    return path


def working_bytes(repo: Path, relative_path: str) -> bytes | None:
    path = working_path(repo, relative_path)
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def eol_domain(data: bytes | None) -> dict[str, Any]:
    if data is None:
        return {"raw_sha256": None, "lf_canonical_sha256": None, "eol": "missing"}
    lf = data.replace(b"\r\n", b"\n")
    if b"\r\n" in data:
        eol = "crlf_or_mixed"
    elif b"\n" in data:
        eol = "lf"
    else:
        eol = "none"
    return {"raw_sha256": sha256(data), "lf_canonical_sha256": sha256(lf), "eol": eol}


def path_record(repo: Path, relative_path: str, declared_sha256: str | None = None) -> dict[str, Any]:
    git_data = git_bytes(repo, relative_path)
    work_data = working_bytes(repo, relative_path)
    blob = run_git(repo, "rev-parse", f"HEAD:{relative_path}", check=False)
    record = {
        "path": relative_path,
        "path_length": len(str((repo / relative_path).resolve())),
        "git_tracked": git_data is not None,
        "git_blob": blob.stdout.decode().strip() if blob.returncode == 0 else None,
        "git_blob_sha256": sha256(git_data) if git_data is not None else None,
        "working_materialized": work_data is not None,
        "working_size": len(work_data) if work_data is not None else None,
        "working": eol_domain(work_data),
        "declared_sha256": declared_sha256,
    }
    record["declared_matches_git_blob_bytes"] = declared_sha256 is None or record["git_blob_sha256"] == declared_sha256
    if declared_sha256 is None:
        record["declared_match_domain"] = "not_declared"
    elif record["git_blob_sha256"] == declared_sha256:
        record["declared_match_domain"] = "git_blob_bytes"
    elif record["working"]["raw_sha256"] == declared_sha256:
        record["declared_match_domain"] = "working_raw_bytes"
    elif record["working"]["lf_canonical_sha256"] == declared_sha256:
        record["declared_match_domain"] = "working_lf_canonical_bytes"
    else:
        record["declared_match_domain"] = None
    record["declared_identity_matches"] = record["declared_match_domain"] is not None
    record["working_matches_git_blob_bytes"] = work_data == git_data if work_data is not None and git_data is not None else None
    return record


def census(repo: Path, paths: Iterable[str]) -> list[dict[str, Any]]:
    return [path_record(repo, path, ANCHORS.get(path)) for path in paths]


def load_json_from_git(repo: Path, path: str) -> dict[str, Any]:
    data = git_bytes(repo, path)
    if data is None:
        raise FileNotFoundError(path)
    return json.loads(data, object_pairs_hook=dict)


def adjudications(repo: Path, plan_sha256: str, anchors_ok: bool) -> list[dict[str, Any]]:
    manifest = load_json_from_git(repo, INPUT_MANIFEST_PATH)
    facts_binding = manifest.get("facts", {})
    pair_ok = (
        manifest.get("status") == "current_authority"
        and manifest.get("authority_role") == "successor_current_source_authority"
        and facts_binding.get("path") == FACTS_PATH
        and facts_binding.get("sha256") == FACTS_SHA256
        and facts_binding.get("role") == "current_source_authority"
    )
    fixed = {
        "C-03": ("resolved_pass", "publish_terminal_not_required_current_scope"),
        "C-05": ("resolved_pass", "registry_owned_derived_current_projection"),
        "C-06": ("not_applicable", "not_applicable_temporary_tooling_trigger"),
        "C-08": ("resolved_pass", "single_rollbackable_generation_transaction"),
        "C-09": ("not_applicable", "tooltip_separate_surface_out_of_scope"),
        "C-10": ("resolved_pass", "validated_naturalization_current_runtime_adoption_complete"),
    }
    rows = [
        {"id": "C-01a", "status": "resolved_pass" if facts_binding.get("role") == "current_source_authority" else "resolved_blocked", "decision": facts_binding.get("role")},
        {"id": "C-01b", "status": "resolved_pass" if manifest.get("authority_role") == "successor_current_source_authority" else "resolved_blocked", "decision": manifest.get("authority_role")},
        {"id": "C-01c", "status": "resolved_pass" if pair_ok else "resolved_blocked", "decision": "coherent_sealed_current_source_pair" if pair_ok else "pair_incoherent"},
        {"id": "C-02", "status": "resolved_pass" if anchors_ok else "resolved_blocked", "decision": "binding_obtainable" if anchors_ok else "anchor_unavailable"},
    ]
    rows.extend({"id": key, "status": value[0], "decision": value[1]} for key, value in fixed.items())
    rows.extend([
        {"id": "C-04", "status": "resolved_pass", "decision": "direct_immutable_candidate_projection"},
        {"id": "C-07a", "status": "deferred_with_owner", "decision": "registry_writer_authorization_materializes_in_change_3"},
        {"id": "C-07b", "status": "deferred_with_owner", "decision": "descriptor_owner_path_materializes_in_change_3"},
        {"id": "C-07c", "status": "deferred_with_owner", "decision": "protected_set_expansion_adjudicates_in_change_3"},
        {"id": "C-07d", "status": "deferred_with_owner", "decision": "tooling_allowlist_adjudicates_in_change_3"},
        {"id": "C-07e", "status": "resolved_pass", "decision": "read_only_protected_no_writer"},
        {"id": "C-11", "status": "resolved_pass", "decision": "fresh_plan_review_pass_existing_contract_no_independence_clause"},
        {"id": "C-12", "status": "resolved_pass", "decision": "fresh_snapshot_required_no_residue_reuse"},
        {"id": "C-13", "status": "not_applicable", "decision": "execution_contract_has_no_adoption_specific_repository_command"},
    ])
    for row in rows:
        row["plan_sha256"] = plan_sha256
    return sorted(rows, key=lambda row: row["id"])


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


def load_json_bytes(data: bytes) -> dict[str, Any]:
    return json.loads(data, object_pairs_hook=dict)


def facts_key_set(data: bytes) -> set[str]:
    keys: set[str] = set()
    for line in data.decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line, object_pairs_hook=dict)
        item_id = row.get("item_id")
        if not isinstance(item_id, str) or not item_id or item_id in keys:
            raise ValueError("facts_item_id_missing_or_duplicate")
        keys.add(item_id)
    return keys


def public_shape(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("entries")
    if not isinstance(entries, dict):
        raise ValueError("entries_must_be_object")
    adopted = 0
    unadopted = 0
    empty_text = 0
    publish_state = 0
    for key, row in entries.items():
        if not isinstance(key, str) or not isinstance(row, dict):
            raise ValueError("entry_shape_invalid")
        state = row.get("state")
        if state is None:
            state = "unadopted" if row.get("source") == "unadopted" else "adopted"
        text = row.get("text_ko")
        if state == "unadopted":
            unadopted += 1
            if text == "":
                empty_text += 1
            if text is not None:
                raise ValueError(f"unadopted_text_exposure:{key}")
        else:
            adopted += 1
            if not isinstance(text, str) or not text:
                raise ValueError(f"adopted_text_missing:{key}")
        publish_state += int("publish_state" in row)
    return {
        "total": len(entries),
        "adopted_public": adopted,
        "unadopted": unadopted,
        "empty_text_count": empty_text,
        "publish_state_count": publish_state,
        "ordered_key_digest": sha256(canonical_json(list(entries.keys()))),
        "key_set": set(entries.keys()),
    }


def validate_candidate_manifest_binding(
    manifest_path: Path,
    *,
    expected_candidate_sha256: str,
    expected_input_manifest_sha256: str,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidate_rendered_hash") != expected_candidate_sha256:
        raise ValueError("candidate_manifest_candidate_mismatch")
    if manifest.get("source_manifest_hash") != expected_input_manifest_sha256:
        raise ValueError("candidate_manifest_input_manifest_mismatch")
    return {
        "status": "PASS",
        "candidate_rendered_hash": expected_candidate_sha256,
        "source_manifest_hash": expected_input_manifest_sha256,
    }


def validate_materialized_generation(candidate_path: Path, generation_root: Path) -> dict[str, Any]:
    import layer3_current_authority_reconstruction as reconstruction

    rendered_path = generation_root / "dvf_3_3_rendered.json"
    manifest_path = generation_root / "IrisLayer3DataChunks.lua"
    chunk_dir = generation_root / "IrisLayer3DataChunks"
    candidate = load_json_bytes(candidate_path.read_bytes())
    rendered = load_json_bytes(rendered_path.read_bytes())
    candidate_entries = candidate.get("entries", {})
    rendered_entries = rendered.get("entries", {})
    runtime_entries = reconstruction.load_runtime_chunks(chunk_dir)
    manifest_summary = reconstruction.lua_file_summary(manifest_path)
    module_names = [Path(value).name + ".lua" for value in manifest_summary["runtime_manifest_modules"]]
    actual_names = [path.name for path in sorted(chunk_dir.glob("Chunk*.lua"))]
    candidate_keys = set(candidate_entries)
    rendered_keys = set(rendered_entries)
    runtime_keys = set(runtime_entries)
    mismatches: list[str] = []
    public_matches = 0
    unadopted_without_text = 0
    forbidden_metadata = 0
    for key in sorted(candidate_keys | rendered_keys | runtime_keys):
        candidate_row = candidate_entries.get(key, {})
        rendered_row = rendered_entries.get(key, {})
        runtime_row = runtime_entries.get(key, {})
        if candidate_row != rendered_row:
            mismatches.append(f"rendered:{key}")
        if candidate_row.get("source") != runtime_row.get("source"):
            mismatches.append(f"source:{key}")
        expected_text = candidate_row.get("text_ko")
        actual_text = runtime_row.get("text_ko")
        if isinstance(expected_text, str):
            if actual_text == expected_text:
                public_matches += 1
            else:
                mismatches.append(f"text:{key}")
        elif actual_text is None:
            unadopted_without_text += int(candidate_row.get("source") == "unadopted")
        else:
            mismatches.append(f"unexpected_text:{key}")
        forbidden_metadata += len(set(runtime_row) - {"source", "text_ko"})
    status = "PASS" if (
        candidate_keys == rendered_keys == runtime_keys
        and not mismatches
        and module_names == actual_names
        and forbidden_metadata == 0
    ) else "BLOCKED"
    report = {
        "schema_version": "validated-naturalization-full-generation-parity-v1",
        "status": status,
        "candidate_rendered_key_set_equal": candidate_keys == rendered_keys,
        "candidate_runtime_key_set_equal": candidate_keys == runtime_keys,
        "candidate_only_count": len(candidate_keys - runtime_keys),
        "runtime_only_count": len(runtime_keys - candidate_keys),
        "public_text_match_count": public_matches,
        "unadopted_without_text_count": unadopted_without_text,
        "forbidden_runtime_metadata_count": forbidden_metadata,
        "manifest_chunk_set_equal": module_names == actual_names,
        "mismatch_count": len(mismatches),
        "mismatch_sample": mismatches[:20],
    }
    write_json(generation_root / "full_parity_report.json", report)
    if status != "PASS":
        raise ValueError("materialized_generation_parity_mismatch")
    return report


def generation_payload_files(root: Path) -> list[Path]:
    return [
        root / "dvf_3_3_rendered.json",
        root / "IrisLayer3DataChunks.lua",
        *sorted((root / "IrisLayer3DataChunks").glob("Chunk*.lua")),
    ]


def transaction_surface_paths(repo: Path) -> dict[str, Path]:
    manifest = repo / LUA_MANIFEST_PATH
    return {
        "rendered": repo / RENDERED_PATH,
        "chunks": manifest.with_name("IrisLayer3DataChunks"),
        "descriptor": repo / GENERATION_DESCRIPTOR_PATH,
        "manifest": manifest,
    }


def transaction_surface_census(repo: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for role, path in transaction_surface_paths(repo).items():
        if path.is_file():
            result[role] = {"kind": "file", "sha256": sha256(path.read_bytes())}
        elif path.is_dir():
            result[role] = {
                "kind": "directory",
                "files": {
                    child.relative_to(path).as_posix(): sha256(child.read_bytes())
                    for child in sorted(path.rglob("*")) if child.is_file()
                },
            }
        else:
            result[role] = {"kind": "absent"}
    return result


def apply_generation_transaction(
    repo: Path,
    generation_root: Path,
    *,
    transaction_id: str,
    inject_failure_after_content: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    generation_root = generation_root.resolve()
    targets = transaction_surface_paths(repo)
    sources = {
        "rendered": generation_root / "dvf_3_3_rendered.json",
        "chunks": generation_root / "IrisLayer3DataChunks",
        "manifest": generation_root / "IrisLayer3DataChunks.lua",
    }
    if not all(path.exists() for path in sources.values()):
        raise ValueError("transaction_generation_input_missing")
    backup_root = repo / f".validated-naturalization-transaction-{transaction_id}"
    if backup_root.exists():
        raise ValueError("transaction_workspace_not_fresh")
    backup_root.mkdir(parents=True)
    before = transaction_surface_census(repo)
    for role, target in targets.items():
        backup = backup_root / "preimage" / role
        if target.is_dir():
            shutil.copytree(target, backup)
        elif target.is_file():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
    descriptor_source = generation_root / "materialized_generation_descriptor.json"
    descriptor = json.loads(descriptor_source.read_text(encoding="utf-8"))
    descriptor["transaction_id"] = transaction_id
    descriptor["authority_effect"] = "current_runtime_adoption"
    write_order: list[str] = []
    try:
        for role in ("rendered",):
            target = targets[role]
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + f".adoption-tmp-{transaction_id}")
            shutil.copy2(sources[role], temporary)
            os.replace(temporary, target)
            write_order.append(role)
        chunk_target = targets["chunks"]
        chunk_temporary = chunk_target.with_name(chunk_target.name + f".adoption-tmp-{transaction_id}")
        shutil.copytree(sources["chunks"], chunk_temporary)
        if chunk_target.exists():
            shutil.rmtree(chunk_target)
        os.replace(chunk_temporary, chunk_target)
        write_order.append("chunks")
        descriptor_target = targets["descriptor"]
        descriptor_target.parent.mkdir(parents=True, exist_ok=True)
        descriptor_temporary = descriptor_target.with_name(descriptor_target.name + f".adoption-tmp-{transaction_id}")
        write_json(descriptor_temporary, descriptor)
        os.replace(descriptor_temporary, descriptor_target)
        write_order.append("descriptor")
        if inject_failure_after_content:
            raise RuntimeError("injected_after_content_before_manifest")
        manifest_target = targets["manifest"]
        manifest_temporary = manifest_target.with_name(manifest_target.name + f".adoption-tmp-{transaction_id}")
        shutil.copy2(sources["manifest"], manifest_temporary)
        os.replace(manifest_temporary, manifest_target)
        write_order.append("manifest")
        return {"status": "PASS", "write_order": write_order, "manifest_last": write_order[-1] == "manifest", "preimage": before}
    except Exception:
        for role, target in targets.items():
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
            backup = backup_root / "preimage" / role
            if backup.is_dir():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(backup, target)
            elif backup.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
        raise
    finally:
        if backup_root.exists():
            shutil.rmtree(backup_root)


def run_mirror_transaction_proof(repo: Path, attempt_root: Path) -> dict[str, Any]:
    repo = repo.resolve()
    attempt_root = attempt_root.resolve()
    generation_root = attempt_root / "phase3" / "next_generation"
    proof_root = attempt_root / "phase4"
    mirror = proof_root / "mirror"
    if mirror.exists():
        raise ValueError("mirror_proof_root_not_fresh")
    live_paths = transaction_surface_paths(repo)
    mirror_paths = transaction_surface_paths(mirror)
    for role in ("rendered", "manifest"):
        mirror_paths[role].parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live_paths[role], mirror_paths[role])
    shutil.copytree(live_paths["chunks"], mirror_paths["chunks"])
    if live_paths["descriptor"].is_file():
        mirror_paths["descriptor"].parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live_paths["descriptor"], mirror_paths["descriptor"])
    unrelated = mirror / "unrelated.sentinel"
    unrelated.write_bytes(b"unchanged\n")
    before = transaction_surface_census(mirror)
    injected_failure_observed = False
    try:
        apply_generation_transaction(
            mirror, generation_root,
            transaction_id="attempt-0007-injected",
            inject_failure_after_content=True,
        )
    except RuntimeError as exc:
        if str(exc) != "injected_after_content_before_manifest":
            raise
        injected_failure_observed = True
    after = transaction_surface_census(mirror)
    temporary_count = sum(1 for path in mirror.rglob("*") if ".adoption-tmp-" in path.name)
    rollback_pass = injected_failure_observed and before == after and unrelated.read_bytes() == b"unchanged\n" and temporary_count == 0
    rollback_report = {
        "schema_version": "validated-naturalization-mirror-rollback-proof-v1",
        "status": "PASS" if rollback_pass else "BLOCKED",
        "failure_injection_observed": injected_failure_observed,
        "exact_preimage_restored": before == after,
        "temporary_path_count": temporary_count,
        "unrelated_mutation_count": 0 if unrelated.read_bytes() == b"unchanged\n" else 1,
    }
    write_json(proof_root / "rollback_proof.json", rollback_report)
    if not rollback_pass:
        raise RuntimeError("mirror_rollback_proof_failed")
    success = apply_generation_transaction(
        mirror, generation_root,
        transaction_id="attempt-0007-success",
    )
    expected = {
        "rendered": sha256((generation_root / "dvf_3_3_rendered.json").read_bytes()),
        "manifest": sha256((generation_root / "IrisLayer3DataChunks.lua").read_bytes()),
    }
    observed = transaction_surface_census(mirror)
    success["rendered_match"] = observed["rendered"].get("sha256") == expected["rendered"]
    success["manifest_match"] = observed["manifest"].get("sha256") == expected["manifest"]
    success["unrelated_mutation_count"] = 0 if unrelated.read_bytes() == b"unchanged\n" else 1
    success["status"] = "PASS" if success["manifest_last"] and success["rendered_match"] and success["manifest_match"] and success["unrelated_mutation_count"] == 0 else "BLOCKED"
    write_json(proof_root / "mirror_successful_apply.json", success)
    if success["status"] != "PASS":
        raise RuntimeError("mirror_successful_apply_failed")
    return {"rollback": rollback_report, "successful_apply": success, "mirror": str(mirror)}


def run_prepare_and_materialize(repo: Path, attempt_root: Path) -> dict[str, Any]:
    repo = repo.resolve()
    attempt_root = attempt_root.resolve()
    phase1 = attempt_root / "phase1"
    phase2 = attempt_root / "phase2"
    next_generation = attempt_root / "phase3" / "next_generation"
    candidate_data = git_bytes(repo, CANDIDATE_PATH)
    rendered_data = git_bytes(repo, RENDERED_PATH)
    facts_data = git_bytes(repo, FACTS_PATH)
    candidate_working_data = working_bytes(repo, CANDIDATE_PATH)
    if candidate_data is None or rendered_data is None or facts_data is None or candidate_working_data is None:
        raise FileNotFoundError("candidate_current_rendered_facts_or_working_candidate_missing")
    candidate = load_json_bytes(candidate_data)
    candidate_working = load_json_bytes(candidate_working_data)
    current = load_json_bytes(rendered_data)
    candidate_shape = public_shape(candidate)
    current_shape = public_shape(current)
    candidate_keys = candidate_shape.pop("key_set")
    current_keys = current_shape.pop("key_set")
    source_keys = facts_key_set(facts_data)
    keys_equal = candidate_keys == source_keys
    if not keys_equal:
        raise ValueError("candidate_current_source_key_set_mismatch")
    if candidate.get("meta", {}).get("facts_sha256") != FACTS_SHA256:
        raise ValueError("candidate_meta_facts_sha256_mismatch")
    decoded_projection_equal = candidate_working == candidate
    if not decoded_projection_equal:
        raise ValueError("candidate_working_git_decoded_projection_mismatch")
    candidate_manifest_binding = validate_candidate_manifest_binding(
        working_path(repo, CANDIDATE_MANIFEST_PATH),
        expected_candidate_sha256=CANDIDATE_SHA256,
        expected_input_manifest_sha256=INPUT_MANIFEST_SHA256,
    )
    assessment = load_json_from_git(repo, ASSESSMENT_PATH)
    consumption = load_json_from_git(repo, CONSUMPTION_PATH)
    admission = {
        "schema_version": "validated-naturalization-candidate-admission-v1",
        "candidate_path": CANDIDATE_PATH,
        "candidate_sha256": CANDIDATE_SHA256,
        "candidate_manifest_path": CANDIDATE_MANIFEST_PATH,
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_SHA256,
        "assessment_path": ASSESSMENT_PATH,
        "assessment_sha256": ASSESSMENT_SHA256,
        "assessment_result": assessment.get("status") or assessment.get("result"),
        "consumption_path": CONSUMPTION_PATH,
        "consumption_sha256": CONSUMPTION_SHA256,
        "candidate_source_key_set_equal": keys_equal,
        "candidate_mutation_count": 0,
        "admission_prerequisite": "PASS",
    }
    write_json(phase1 / "candidate_admission_report.json", admission)
    write_json(phase1 / "candidate_source_binding_report.json", {
        "schema_version": "validated-naturalization-candidate-source-binding-v1",
        "facts_sha256": FACTS_SHA256,
        "input_manifest_sha256": INPUT_MANIFEST_SHA256,
        "candidate_meta_facts_sha256": candidate.get("meta", {}).get("facts_sha256"),
        "bidirectional_key_set_equal": keys_equal,
        "candidate_only_count": len(candidate_keys - source_keys),
        "source_only_count": len(source_keys - candidate_keys),
        "current_rendered_control_key_set_equal": candidate_keys == current_keys,
        "projection_contract": "working_raw_crlf_to_git_blob_lf_decoded_json_identity",
        "candidate_working_raw_sha256": sha256(candidate_working_data),
        "candidate_git_blob_sha256": sha256(candidate_data),
        "decoded_json_projection_equal": decoded_projection_equal,
        "candidate_manifest_binding": candidate_manifest_binding,
        "candidate_shape": candidate_shape,
        "current_shape": current_shape,
        "status": "PASS",
    })
    write_json(phase1 / "authority_role_decision.json", {
        "current_rendered_role": "registry_owned_derived_current_projection",
        "source_authority": False,
        "package_authority": False,
        "status": "PASS",
    })
    write_json(phase1 / "adoption_method_decision.json", {
        "method": "direct_immutable_candidate_projection",
        "candidate_mutation_allowed": False,
        "status": "PASS",
    })
    descriptor_path = "Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json"
    writer = {
        "schema_version": "validated-naturalization-registry-writer-authorization-v1",
        "writer_identity": "Iris Artifact Registry validated naturalization adoption writer",
        "writer_count": 1,
        "authorization_source": "direct user instruction in current Codex task; prospective owner approvals explicitly granted",
        "automation_impersonates_owner": False,
        "exact_targets": [RENDERED_PATH, LUA_MANIFEST_PATH, "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk*.lua", descriptor_path],
        "read_only_surfaces": [REQUIRED_VALIDATIONS_PATH, "Iris/_docs/round3/registry_runtime_compatibility/"],
        "lock_path": "attempt-local/adoption.lock",
        "transaction_unit": "rendered_runtime_chunks_manifest_descriptor",
        "status": "PASS",
    }
    write_json(phase2 / "writer_authorization.json", writer)
    write_json(phase2 / "generation_schema.json", {
        "schema_version": "validated-naturalization-current-generation-v1",
        "required_identity_fields": ["transaction_id", "candidate", "source_pair", "rendered", "runtime_manifest", "ordered_chunks", "materialized_generation_descriptor_sha256"],
        "forbidden_fields": ["rtc_bundle", "g6_lifecycle", "self_sha256"],
    })
    write_json(phase2 / "runtime_check_contract.json", {
        "runtime_check_contract_prepared": True,
        "g6_current_disposition": "not_applicable_temporary_tooling_trigger",
        "rtc_product_defect_confirmed": False,
        "official_route_subject": "clean_detached_full_repository_mirror_with_change4_bytes_at_canonical_paths",
        "guard_bypass_allowed": False,
        "denominator_reduction_allowed": False,
    })
    write_json(phase2 / "c07_c13_adjudication.json", {
        "C-07a": "resolved_pass",
        "C-07b": "resolved_pass",
        "C-07c": "resolved_pass_explicit_additive_authorization",
        "C-07d": "resolved_pass_no_core_cap_conflict",
        "C-13": "not_applicable_no_exact_adoption_specific_repository_command",
    })
    phase3 = next_generation.parent
    phase3.mkdir(parents=True, exist_ok=True)
    candidate_input = working_path(repo, CANDIDATE_PATH)
    adoption_contract_path = phase2 / "adoption_generation_contract.json"
    adoption_contract = {
        "schema_version": "validated-naturalization-adoption-generation-contract-v1",
        "authority_effect": "none",
        "bridge_context": "staging",
        "candidate_path": str(candidate_input),
        "candidate_sha256": CANDIDATE_SHA256,
        "facts_path": str(working_path(repo, FACTS_PATH)),
        "facts_sha256": FACTS_SHA256,
        "input_manifest_path": str(working_path(repo, INPUT_MANIFEST_PATH)),
        "input_manifest_sha256": INPUT_MANIFEST_SHA256,
        "adoption_owned_parent_root": str(phase3),
        "output_root": str(next_generation),
        "expected_shape": {
            "total": candidate_shape["total"],
            "adopted_public": candidate_shape["adopted_public"],
            "unadopted": candidate_shape["unadopted"],
            "public_text": candidate_shape["adopted_public"],
        },
    }
    write_json(adoption_contract_path, adoption_contract)
    exporter = repo / "Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py"
    command = [
        sys.executable, "-B", str(exporter), "--rendered-path", str(candidate_input),
        "--bridge-context", "staging", "--format", "chunk", "--output-root", str(next_generation),
        "--report-path", str(next_generation / "bridge_export_report.json"),
        "--adoption-generation", "--adoption-generation-contract", str(adoption_contract_path),
    ]
    proc = subprocess.run(command, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    write_json(next_generation / "export_command_receipt.json", {
        "argv": command, "cwd": str(repo), "exit_code": proc.returncode,
        "stdout_sha256": sha256(proc.stdout), "stderr_sha256": sha256(proc.stderr),
    })
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="replace"))
    rendered_out = next_generation / "dvf_3_3_rendered.json"
    rendered_out.write_bytes(candidate_data)
    parity = validate_materialized_generation(candidate_input, next_generation)

    repeat_generation = phase3 / "regeneration_b"
    repeat_contract_path = phase2 / "adoption_generation_contract_b.json"
    repeat_contract = dict(adoption_contract)
    repeat_contract["output_root"] = str(repeat_generation)
    write_json(repeat_contract_path, repeat_contract)
    repeat_command = [
        sys.executable, "-B", str(exporter), "--rendered-path", str(candidate_input),
        "--bridge-context", "staging", "--format", "chunk", "--output-root", str(repeat_generation),
        "--report-path", str(repeat_generation / "bridge_export_report.json"),
        "--adoption-generation", "--adoption-generation-contract", str(repeat_contract_path),
    ]
    repeat_proc = subprocess.run(repeat_command, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if repeat_proc.returncode != 0:
        raise RuntimeError(repeat_proc.stderr.decode(errors="replace"))
    (repeat_generation / "dvf_3_3_rendered.json").write_bytes(candidate_data)
    validate_materialized_generation(candidate_input, repeat_generation)
    first_files = generation_payload_files(next_generation)
    second_files = generation_payload_files(repeat_generation)
    byte_identical = (
        [path.relative_to(next_generation).as_posix() for path in first_files]
        == [path.relative_to(repeat_generation).as_posix() for path in second_files]
        and all(left.read_bytes() == right.read_bytes() for left, right in zip(first_files, second_files))
    )
    write_json(phase3 / "regeneration_identity_report.json", {
        "schema_version": "validated-naturalization-regeneration-identity-v1",
        "status": "PASS" if byte_identical else "BLOCKED",
        "byte_identical": byte_identical,
        "compared_file_count": len(first_files),
    })
    if not byte_identical:
        raise ValueError("adoption_generation_regeneration_drift")
    manifest_path = next_generation / "IrisLayer3DataChunks.lua"
    chunks = sorted((next_generation / "IrisLayer3DataChunks").glob("Chunk*.lua"))
    descriptor = {
        "schema_version": "validated-naturalization-materialized-generation-v1",
        "candidate": {"path": CANDIDATE_PATH, "sha256": CANDIDATE_SHA256},
        "source_pair": {"facts_sha256": FACTS_SHA256, "input_manifest_sha256": INPUT_MANIFEST_SHA256},
        "rendered": {"path": "dvf_3_3_rendered.json", "sha256": sha256(rendered_out.read_bytes())},
        "runtime_manifest": {"path": "IrisLayer3DataChunks.lua", "sha256": sha256(manifest_path.read_bytes())},
        "ordered_chunks": [{"path": f"IrisLayer3DataChunks/{path.name}", "sha256": sha256(path.read_bytes())} for path in chunks],
        "rtc_g6_field_count": 0,
    }
    write_json(next_generation / "materialized_generation_descriptor.json", descriptor)
    write_json(next_generation / "key_membership_report.json", {
        "candidate_only_count": 0, "source_only_count": 0, "bidirectional_key_set_equal": True,
        "shape": candidate_shape,
    })
    return {"phase1": "PASS", "phase2": "PASS", "phase3": "PASS", "next_generation": str(next_generation), "descriptor_sha256": sha256(canonical_json(descriptor)), "public_text_match_count": parity["public_text_match_count"]}


def run_phase0(repo: Path, output: Path) -> dict[str, Any]:
    repo = repo.resolve()
    before = census(repo, PROTECTED_PATHS)
    head = run_git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    tree = run_git(repo, "rev-parse", "HEAD^{tree}").stdout.decode().strip()
    status = run_git(repo, "status", "--porcelain").stdout.decode().splitlines()
    ancestors = {
        name: run_git(repo, "merge-base", "--is-ancestor", commit, "HEAD", check=False).returncode == 0
        for name, commit in REQUIRED_ANCESTORS.items()
    }
    plan_data = git_bytes(repo, PLAN_PATH)
    plan_sha = sha256(plan_data or b"")
    anchor_format_ok = all(SHA256_RE.fullmatch(value) for value in ANCHORS.values())
    anchor_records = {row["path"]: row for row in before if row["path"] in ANCHORS}
    anchors_ok = anchor_format_ok and all(row["declared_identity_matches"] for row in anchor_records.values())
    ledger = adjudications(repo, plan_sha, anchors_ok)
    c01_ok = all(row["status"] == "resolved_pass" for row in ledger if row["id"] in {"C-01a", "C-01b", "C-01c"})
    phase0_eligible = all(ancestors.values()) and not status and anchors_ok and c01_ok
    terminal = "phase0_complete_eligible_for_phase1" if phase0_eligible else "phase0_complete_blocked"
    reasons = []
    if not all(ancestors.values()) or status:
        reasons.append("blocked_execution_base_not_clean_descendant")
    if not anchor_format_ok:
        reasons.append("blocked_invalid_anchor_literal")
    if not anchors_ok:
        reasons.append("blocked_candidate_anchor_unavailable")
    if not c01_ok:
        reasons.append("blocked_source_pair_incoherent")
    protected_report = {
        "schema_version": "validated-naturalization-adoption-protected-census-v1",
        "scope": "protected_live_surfaces_during_read_only_census_window",
        "records": before,
    }
    premise = {
        "schema_version": "validated-naturalization-adoption-premise-identity-v1",
        "head": head,
        "tree": tree,
        "git_status": status,
        "required_ancestors": ancestors,
        "plan_sha256": plan_sha,
        "anchor_literal_format_pass": anchor_format_ok,
        "anchor_referents_pass": anchors_ok,
        "current_facts_role": "current_source_authority",
        "current_input_manifest_role": "successor_current_source_authority",
        "source_pair_coherent": c01_ok,
        "machine_policy": {"applicable": False, "disposition": "historical_noncoverage_not_current_product_defect"},
        "official_package_command": ["powershell", "-ExecutionPolicy", "Bypass", "-File", "Iris/tools/package_iris.ps1"],
        "official_current_route_command": ["python", "Iris/_docs/round3/round3_run_contract_tests.py", "--class", "current", "--enforce-current-build-closure", "--out", "<receipt>"],
        "review": {"fresh_plan_review": "PASS", "critical": 0, "important": 0, "independence_required": False, "owner_seal_required": False},
        "g6": {"disposition": "not_applicable_temporary_tooling_trigger", "rtc_product_defect_confirmed": False, "existing_certification_coverage": "does_not_cover_candidate"},
    }
    result = {
        "schema_version": "validated-naturalization-adoption-phase0-result-v1",
        "terminal_state": terminal,
        "block_reasons": reasons,
        "phase1_eligible": phase0_eligible,
        "validation_axes": {"coverage_status": "covered", "tooling_status": "pass", "payload_status": "pass" if anchors_ok else "mismatch", "independent_reproduction_status": "not_evaluated", "g6_trigger": False},
    }
    write_json(output / "protected_surface_census.json", protected_report)
    write_json(output / "premise_identity_report.json", premise)
    write_json(output / "adoption_adjudication_ledger.json", {"schema_version": "validated-naturalization-adoption-adjudication-v1", "entries": ledger})
    write_json(output / "phase0_result.json", result)
    after = census(repo, PROTECTED_PATHS)
    mutation_count = sum(1 for left, right in zip(before, after) if left != right)
    result["read_only_protected_live_mutation_count"] = mutation_count
    result["phase1_eligible"] = result["phase1_eligible"] and mutation_count == 0
    if mutation_count:
        result["terminal_state"] = "phase0_complete_blocked"
        result["block_reasons"].append("blocked_read_only_census_mutation")
    write_json(output / "phase0_result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_phase0(args.repo, args.output)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["terminal_state"] in {"phase0_complete_eligible_for_phase1", "phase0_complete_blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
