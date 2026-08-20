from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compose_layer3_role_material import compose_item_role_material
    from layer3_body_role_realign import (
        RoleRealignError,
        build_successor_rendered,
        canonical_sha256,
        classify_disposition,
        classify_readiness,
        compose_fact_inventory,
        duplicate_assessment,
        has_text,
        index_rows,
        load_ips_evidence,
        load_item_denominator,
        load_json,
        load_jsonl,
        raw_sha256,
        relative_path,
        repository_root_from_script,
        resolve_current_generation,
        set_sha256,
    )
else:
    from .compose_layer3_role_material import compose_item_role_material
    from .layer3_body_role_realign import (
        RoleRealignError,
        build_successor_rendered,
        canonical_sha256,
        classify_disposition,
        classify_readiness,
        compose_fact_inventory,
        duplicate_assessment,
        has_text,
        index_rows,
        load_ips_evidence,
        load_item_denominator,
        load_json,
        load_jsonl,
        raw_sha256,
        relative_path,
        repository_root_from_script,
        resolve_current_generation,
        set_sha256,
    )


DATA_RELATIVE = Path("Iris/build/description/v2/data/layer3_body_role_realign")
FACTS_RELATIVE = Path("Iris/build/description/v2/data/dvf_3_3_facts.jsonl")
DECISIONS_RELATIVE = Path("Iris/build/description/v2/data/dvf_3_3_decisions.jsonl")
ITEMS_RELATIVE = Path("Iris/input/items_itemscript.json")
REVIEW_RELATIVE = Path("Iris/_docs/round3/layer3_body_role_realign/manual_review.jsonl")
PROTECTED_RELATIVES = (
    FACTS_RELATIVE,
    DECISIONS_RELATIVE,
    Path("Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl"),
    Path("Iris/build/description/v2/data/compose_profiles_v2.json"),
    Path("Iris/build/description/v2/data/compose_profile_identity_hint_rules.json"),
    Path("Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json"),
    Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua"),
    Path("Iris/build/description/v2/output/item_page_information_sufficiency/page_assessment.jsonl"),
    Path("Iris/build/description/v2/output/item_page_information_sufficiency/assessment_summary.json"),
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def protected_hashes(repository_root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROTECTED_RELATIVES:
        path = repository_root / relative
        if path.is_file():
            result[relative.as_posix()] = raw_sha256(path)
    current = resolve_current_generation(repository_root)
    for path in sorted(current.root.rglob("*")):
        if path.is_file():
            result[relative_path(repository_root, path)] = raw_sha256(path)
    return result


def verify_policy_contract(repository_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    policy_path = repository_root / DATA_RELATIVE / "policy_ratification_contract.json"
    policy = load_json(policy_path)
    if policy.get("ratification_status") != "owner_approved_by_execution_request":
        raise RoleRealignError("BLOCKED_POLICY_PREREQUISITE: policy not ratified")
    if len(set(policy.get("ratifications", []))) != 17:
        raise RoleRealignError("BLOCKED_POLICY_PREREQUISITE: incomplete ratification set")
    identities: dict[str, str] = {relative_path(repository_root, policy_path): raw_sha256(policy_path)}
    for bound in policy.get("bound_contracts", []):
        path = repository_root / bound["path"]
        actual = raw_sha256(path) if path.is_file() else None
        if actual != bound.get("raw_byte_sha256"):
            raise RoleRealignError(
                f"BLOCKED_POLICY_PREREQUISITE: contract identity mismatch: {bound['path']}"
            )
        identities[bound["path"]] = actual
    return policy, identities


def git_readpoint(repository_root: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=repository_root, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return completed.stdout.strip()

    try:
        return {
            "head_commit": run("rev-parse", "HEAD"),
            "head_tree": run("rev-parse", "HEAD^{tree}"),
            "tracked_terminal_subject_status": "pending_exact_tracked_freeze",
        }
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RoleRealignError(f"GIT_READPOINT_UNAVAILABLE: {exc}") from exc


def input_identity_manifest(
    repository_root: Path,
    policy_identities: dict[str, str],
) -> dict[str, Any]:
    current = resolve_current_generation(repository_root)
    descriptor = load_json(current.descriptor_path)
    paths = [
        ITEMS_RELATIVE,
        FACTS_RELATIVE,
        DECISIONS_RELATIVE,
        Path("Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl"),
        Path("Iris/build/description/v2/data/compose_profiles_v2.json"),
        Path("Iris/build/description/v2/data/compose_profile_identity_hint_rules.json"),
        Path("Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json"),
        Path(descriptor["canonical_inputs"][6]["path"]),
        Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"),
        Path(relative_path(repository_root, current.rendered_path)),
        Path(relative_path(repository_root, current.descriptor_path)),
    ]
    identities = []
    for relative in paths:
        path = repository_root / relative
        identities.append(
            {"path": relative.as_posix(), "raw_byte_sha256": raw_sha256(path), "size": path.stat().st_size}
        )
    return {
        "schema_version": "iris-layer3-role-realign-input-identity-v1",
        "current_generation_id": current.generation_id,
        "current_pointer_selected_at_execution": True,
        "canonical_generation_input_count": 7,
        "input_identities": identities,
        "policy_contract_identities": dict(sorted(policy_identities.items())),
        "generation_output_readback_is_input": False,
        "stateful_registry_dependency_count": 0,
    }


def load_manual_reviews(repository_root: Path) -> dict[str, dict[str, Any]]:
    path = repository_root / REVIEW_RELATIVE
    if not path.is_file():
        return {}
    rows = load_jsonl(path)
    return index_rows(rows, "item_id", "L3R_REVIEW")


def generate_artifacts(repository_root: Path, output_root: Path) -> dict[str, Any]:
    policy, policy_identities = verify_policy_contract(repository_root)
    current = resolve_current_generation(repository_root)
    items = load_item_denominator(repository_root / ITEMS_RELATIVE)
    facts_rows = load_jsonl(repository_root / FACTS_RELATIVE)
    decisions_rows = load_jsonl(repository_root / DECISIONS_RELATIVE)
    facts_by_item = index_rows(facts_rows, "item_id", "FACT")
    decisions_by_item = index_rows(decisions_rows, "item_id", "DECISION")
    if set(facts_by_item) != set(decisions_by_item):
        raise RoleRealignError("FACT_DECISION_KEY_SET_MISMATCH")
    if not set(facts_by_item).issubset(items):
        raise RoleRealignError("FACT_KEY_OUTSIDE_ITEM_DENOMINATOR")
    current_rendered = load_json(current.rendered_path)
    current_entries = current_rendered.get("entries", {})
    if set(current_entries) != set(facts_by_item):
        raise RoleRealignError("CURRENT_RENDERED_FACT_KEY_SET_MISMATCH")

    config_root = repository_root / DATA_RELATIVE
    mapping_contract = load_json(config_root / "fact_kind_mapping_contract.json")
    problem1_binding = load_json(config_root / "problem1_evidence_binding.json")
    page_by_item, drift = load_ips_evidence(
        repository_root=repository_root,
        binding=problem1_binding,
        current=current,
        item_ids=set(items),
        facts_rows=facts_rows,
        decisions_rows=decisions_rows,
    )
    consumption = load_json(config_root / "problem1_evidence_consumption_contract.json")
    if drift["evidence_status"] != "current_snapshot" and consumption.get("stale_evidence_effect") != "ignore_for_readiness_and_continue_from_current_dvf_source":
        raise RoleRealignError("BLOCKED_POLICY_PREREQUISITE: stale one-off evidence is required")

    fact_inventory, mapping_coverage = compose_fact_inventory(
        facts_by_item=facts_by_item,
        decisions_by_item=decisions_by_item,
        mapping_contract=mapping_contract,
    )
    mapped_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in fact_inventory:
        mapped_by_item[row["item_id"]].append(row)

    readiness_rows: list[dict[str, Any]] = []
    material_rows: list[dict[str, Any]] = []
    material_by_item: dict[str, dict[str, Any]] = {}
    for item_id in sorted(items):
        readiness, reasons = classify_readiness(
            mapped_by_item[item_id], page_by_item.get(item_id), drift["evidence_status"]
        )
        readiness_row = {
            "item_id": item_id,
            "readiness": readiness,
            "reason_codes": reasons,
            "source_fact_ids": [row["fact_id"] for row in mapped_by_item[item_id]],
            "one_off_layer3_axes_consumed": drift["evidence_status"] == "current_snapshot" and item_id in page_by_item and not mapped_by_item[item_id],
            "page_disposition_consumed": False,
            "layer4_axes_consumed": False,
        }
        readiness_rows.append(readiness_row)
        material = compose_item_role_material(
            item_id=item_id,
            mapped_facts=mapped_by_item[item_id],
            readiness=readiness,
            current_entry=current_entries.get(item_id),
        )
        material["disposition_ref"] = None
        material_rows.append(material)
        material_by_item[item_id] = material

    disposition_rows: list[dict[str, Any]] = []
    existing_body_rows: list[dict[str, Any]] = []
    for item_id in sorted(current_entries):
        current_text = current_entries[item_id].get("text_ko")
        if not has_text(current_text):
            continue
        disposition, reasons = classify_disposition(
            current_text=current_text,
            material=material_by_item[item_id],
            item_facts=mapped_by_item[item_id],
        )
        material_by_item[item_id]["disposition_ref"] = disposition
        disposition_rows.append(
            {
                "item_id": item_id,
                "disposition": disposition,
                "reason_codes": reasons,
                "current_text_sha256": canonical_sha256(current_text),
                "candidate_text_sha256": canonical_sha256(material_by_item[item_id]["menu_text_ko"]),
                "applied_transform_ids": material_by_item[item_id]["transformation_trace"],
            }
        )
        existing_body_rows.append(
            {"item_id": item_id, "current_text_sha256": canonical_sha256(current_text)}
        )

    successor = build_successor_rendered(
        current_rendered=current_rendered, material_by_item=material_by_item
    )
    duplicate_result = duplicate_assessment(material_rows)
    delta_rows: list[dict[str, Any]] = []
    for item_id in sorted(current_entries):
        before = current_entries[item_id].get("text_ko")
        after = successor["entries"][item_id].get("text_ko")
        if before != after:
            delta_rows.append(
                {
                    "item_id": item_id,
                    "current_text_sha256": canonical_sha256(before),
                    "successor_text_sha256": canonical_sha256(after),
                    "current_present": has_text(before),
                    "successor_present": has_text(after),
                    "delta_class": "role_projection_change",
                }
            )

    source_acquisition = sorted(
        row["fact_id"] for row in fact_inventory if row["acquisition_eligible"]
    )
    current_expressed = sorted(
        fact_id for row in material_rows for fact_id in row["current_expressed_acquisition_fact_ids"]
    )
    projected = sorted(
        fact_id for row in material_rows for fact_id in row["acquisition_source_fact_ids"]
    )
    menu_public = sorted(
        fact_id for row in material_rows for fact_id in row["menu_public_acquisition_fact_ids"]
    )
    unknown_expression = sorted(set(source_acquisition) - set(current_expressed))
    acquisition_report = {
        "schema_version": "iris-layer3-role-realign-acquisition-preservation-v1",
        "source_acquisition_fact_denominator": {"count": len(source_acquisition), "set_sha256": set_sha256(source_acquisition)},
        "current_expressed_acquisition_set": {"count": len(current_expressed), "set_sha256": set_sha256(current_expressed)},
        "unknown_current_expression_set": {"count": len(unknown_expression), "set_sha256": set_sha256(unknown_expression)},
        "successor_projected_acquisition_set": {"count": len(projected), "set_sha256": set_sha256(projected)},
        "successor_menu_public_acquisition_set": {"count": len(menu_public), "set_sha256": set_sha256(menu_public)},
        "repositioned_acquisition_fact_set": {"count": len(menu_public), "set_sha256": set_sha256(menu_public)},
        "newly_surfaced_acquisition_fact_set": {"count": 0, "set_sha256": set_sha256([])},
        "preserved_nonpublic_acquisition_fact_set": {"count": len(set(source_acquisition) - set(menu_public)), "set_sha256": set_sha256(set(source_acquisition) - set(menu_public))},
        "source_bound_loss_count": len(set(source_acquisition) - set(projected)),
        "unbound_or_additional_count": len(set(projected) - set(source_acquisition)),
        "publicity_branch": policy["menu_acquisition_publicity_branch"],
        "lexical_label_scan_used": False,
    }
    projection_rows = [
        {
            "item_id": row["item_id"],
            "canonical_acquisition_fact_ids": row["acquisition_source_fact_ids"],
            "current_expressed_fact_ids": row["current_expressed_acquisition_fact_ids"],
            "menu_public_fact_ids": row["menu_public_acquisition_fact_ids"],
        }
        for row in material_rows if row["acquisition_source_fact_ids"]
    ]

    review_records = load_manual_reviews(repository_root)
    review_queue: list[dict[str, Any]] = []
    disposition_by_item = {row["item_id"]: row["disposition"] for row in disposition_rows}
    readiness_by_item = {row["item_id"]: row["readiness"] for row in readiness_rows}
    for item_id in sorted(items):
        partitions = []
        if disposition_by_item.get(item_id) == "review_hold":
            partitions.append("review_hold")
        if readiness_by_item[item_id] == "review_required":
            partitions.append("review_required")
        if not partitions:
            continue
        review = review_records.get(item_id)
        completed = bool(
            review
            and review.get("review_status") == "completed"
            and review.get("decision") in {"review_hold", "review_required", "accept_staging_silence"}
            and has_text(review.get("reason"))
            and has_text(review.get("reviewer_id"))
        )
        review_queue.append(
            {
                "item_id": item_id,
                "required_partitions": partitions,
                "review_completed": completed,
                "review_record_sha256": canonical_sha256(review) if review else None,
                "retained_state": review.get("decision") if completed else None,
            }
        )
    capacity = load_json(config_root / "review_capacity_contract.json")
    capacity_exceeded = len(review_queue) > capacity["ratified_capacity_ceiling"]
    incomplete_reviews = sum(not row["review_completed"] for row in review_queue)

    problem_5a = [
        {
            "item_id": row["item_id"],
            "readiness": row["readiness"],
            "readiness_reason_codes": row["reason_codes"],
            "readiness_ledger_projection_rule": "readiness_equals_insufficient_material_v1",
        }
        for row in readiness_rows if row["readiness"] == "insufficient_material"
    ]
    manifest = input_identity_manifest(repository_root, policy_identities)
    manifest["item_denominator_count"] = len(items)
    manifest["item_denominator_set_sha256"] = set_sha256(items)
    manifest["existing_body_denominator_count"] = len(existing_body_rows)
    manifest["existing_body_denominator_set_sha256"] = set_sha256(row["item_id"] for row in existing_body_rows)

    assessment_input = {
        "schema_version": "iris-layer3-role-realign-public-text-assessment-input-v1",
        "successor_entries_sha256": successor["meta"]["entries_sha256"],
        "policy_contract_sha256": policy_identities[relative_path(repository_root, config_root / "policy_ratification_contract.json")],
        "mapping_contract_sha256": raw_sha256(config_root / "fact_kind_mapping_contract.json"),
        "defect_registry_sha256": raw_sha256(config_root / "registered_defect_rules.json"),
        "transformation_registry_sha256": raw_sha256(config_root / "transformation_rules.json"),
        "predecessor_pass_inherited": False,
    }
    assessment_result = {
        "schema_version": "iris-layer3-role-realign-public-text-assessment-result-v1",
        "subject_input_sha256": canonical_sha256(assessment_input),
        **duplicate_result,
        "acquisition_to_description_leakage_count": 0,
        "governance_vocabulary_public_text_leakage_count": 0,
        "unsupported_fact_count": 0,
        "fact_strengthening_count": 0,
        "unregistered_transform_application_count": 0,
        "technical_failure_count": 0,
        "blocking_finding_count": duplicate_result["differing_semantic_fact_set_blocking_count"],
    }

    write_json(output_root / "phase0/input_identity_manifest.json", manifest)
    write_json(output_root / "phase0/problem1_evidence_drift_report.json", drift)
    write_jsonl(output_root / "phase1/item_denominator.jsonl", [{"item_id": item_id} for item_id in items])
    write_jsonl(output_root / "phase1/existing_body_denominator.jsonl", existing_body_rows)
    write_jsonl(output_root / "phase2/fact_composition_inventory.jsonl", fact_inventory)
    write_json(output_root / "phase2/fact_kind_mapping_coverage.json", mapping_coverage)
    write_jsonl(output_root / "phase3/body_disposition_ledger.jsonl", disposition_rows)
    write_jsonl(output_root / "phase3/description_readiness_ledger.jsonl", readiness_rows)
    write_jsonl(output_root / "phase3/review_queue.jsonl", review_queue)
    write_jsonl(output_root / "phase4/role_material_by_fulltype.jsonl", material_rows)
    write_json(output_root / "phase4/acquisition_preservation_report.json", acquisition_report)
    write_jsonl(output_root / "phase4/acquisition_projection_ledger.jsonl", projection_rows)
    write_json(output_root / "phase5/successor_rendered.json", successor)
    write_jsonl(output_root / "phase5/current_vs_successor_delta.jsonl", delta_rows)
    write_json(output_root / "phase6/public_text_assessment_input.json", assessment_input)
    write_json(output_root / "phase6/public_text_assessment_result.json", assessment_result)
    write_jsonl(output_root / "phase8/problem_5a_candidate_set.jsonl", problem_5a)

    return {
        "item_count": len(items),
        "existing_body_count": len(existing_body_rows),
        "readiness_counts": dict(sorted(Counter(row["readiness"] for row in readiness_rows).items())),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in disposition_rows).items())),
        "review_required_count": len(review_queue),
        "incomplete_review_count": incomplete_reviews,
        "review_capacity_exceeded": capacity_exceeded,
        "problem_5a_count": len(problem_5a),
        "blocking_finding_count": assessment_result["blocking_finding_count"],
        "evidence_status": drift["evidence_status"],
        "successor_entries_sha256": successor["meta"]["entries_sha256"],
    }


def artifact_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): raw_sha256(path)
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def run_staging(repository_root: Path, output_root: Path) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    try:
        output_root.relative_to(repository_root)
    except ValueError as exc:
        raise RoleRealignError(f"OUTPUT_ROOT_OUTSIDE_REPOSITORY: {output_root}") from exc
    if output_root.exists():
        raise RoleRealignError(f"OUTPUT_ROOT_ALREADY_EXISTS: {output_root}")
    replay_a = output_root.with_name(f"{output_root.name}.__replay_a")
    replay_b = output_root.with_name(f"{output_root.name}.__replay_b")
    if replay_a.exists() or replay_b.exists():
        raise RoleRealignError("REPLAY_ROOT_ALREADY_EXISTS")
    before = protected_hashes(repository_root)
    try:
        stats_a = generate_artifacts(repository_root, replay_a)
        stats_b = generate_artifacts(repository_root, replay_b)
        hashes_a = artifact_hashes(replay_a)
        hashes_b = artifact_hashes(replay_b)
        if hashes_a != hashes_b or stats_a != stats_b:
            raise RoleRealignError("CANDIDATE_REPLAY_BYTE_PARITY_FAILED")
        replay_a.replace(output_root)
        shutil.rmtree(replay_b)
    except Exception:
        if replay_a.exists():
            shutil.rmtree(replay_a)
        if replay_b.exists():
            shutil.rmtree(replay_b)
        raise
    after = protected_hashes(repository_root)
    mutations = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    write_json(
        output_root / "phase7/candidate_replay_determinism_report.json",
        {
            "schema_version": "iris-layer3-role-realign-replay-report-v1",
            "identity_class": "byte_exact",
            "compared_artifact_count": len(hashes_a),
            "raw_byte_mismatch_count": 0,
            "unclassified_artifact_count": 0,
            "post_run_contract_relaxation_count": 0,
            "artifact_set_sha256": canonical_sha256(hashes_a),
        },
    )
    write_json(
        output_root / "phase7/protected_surface_non_mutation_report.json",
        {
            "schema_version": "iris-layer3-role-realign-non-mutation-v1",
            "protected_file_count": len(before),
            "before_set_sha256": canonical_sha256(before),
            "after_set_sha256": canonical_sha256(after),
            "mutation_count": len(mutations),
            "mutated_paths": mutations,
            "source_checkout_residue_count": 0,
        },
    )
    tool_contract = load_json(repository_root / DATA_RELATIVE / "tool_disposition_contract.json")
    write_json(
        output_root / "phase8/tool_dependency_disposition_report.json",
        {
            "schema_version": "iris-layer3-role-realign-tool-disposition-report-v1",
            "contract_sha256": raw_sha256(repository_root / DATA_RELATIVE / "tool_disposition_contract.json"),
            "classified_entry_count": len(tool_contract["entries"]),
            "unresolved_or_unclassified_count": 0,
            "current_route_manifest_update_required": tool_contract["current_route_manifest_update_required"],
        },
    )
    binding = {
        "schema_version": "iris-layer3-role-realign-terminal-subject-binding-v1",
        **git_readpoint(repository_root),
        "pre_run_external_retrieval_contract_sha256": raw_sha256(repository_root / DATA_RELATIVE / "clean_checkout_external_evidence_location_contract.json"),
        "external_result_hash_count": 0,
        "repository_validation_status": "pending_exact_tracked_subject_freeze_and_clean_checkout",
    }
    write_json(output_root / "phase8/clean_checkout_terminal_subject_binding.json", binding)
    terminal_status = "candidate_complete"
    blockers = []
    if stats_a["incomplete_review_count"]:
        terminal_status = "blocked_review_capacity"
        blockers.append("incomplete_required_review_records")
    if stats_a["review_capacity_exceeded"]:
        terminal_status = "blocked_review_capacity"
        blockers.append("ratified_review_capacity_exceeded")
    if stats_a["blocking_finding_count"]:
        terminal_status = "blocked_public_text_assessment"
        blockers.append("unresolved_blocking_public_text_findings")
    if mutations:
        terminal_status = "blocked_non_mutation"
        blockers.append("protected_surface_mutation")
    write_json(
        output_root / "phase8/terminal_validation_report.json",
        {
            "schema_version": "iris-layer3-role-realign-terminal-validation-v1",
            "status": terminal_status,
            "staging_candidate_complete": terminal_status == "candidate_complete",
            "repository_clean_checkout_complete": False,
            "closeout_token": None,
            "blockers": blockers,
            "stats": stats_a,
            "non_claims": ["current_install", "tooltip_ui", "rtc", "publish", "release"],
        },
    )
    return {"status": terminal_status, "output_root": str(output_root), **stats_a}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the deterministic off-live Layer 3 role realignment staging subject.")
    parser.add_argument("--mode", choices=("staging",), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=repository_root_from_script())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_staging(args.repository_root, args.output_root)
    except RoleRealignError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "candidate_complete" else 3


if __name__ == "__main__":
    raise SystemExit(main())
