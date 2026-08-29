from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

from .models import SLOT_ORDER, SUPPORTED_LOCALES, TooltipContractError


AUTHORITY_ROOT = Path("Iris/_docs/authority/tooltip_t1")
DECISION_CONTRACT = AUTHORITY_ROOT / "tooltip_t1_decision_contract.json"
CONTRACT_FILES = (
    DECISION_CONTRACT,
    AUTHORITY_ROOT / "tooltip_display_contract.json",
    AUTHORITY_ROOT / "layer2_tooltip_input_contract.json",
    AUTHORITY_ROOT / "layer3_tooltip_input_contract.json",
    AUTHORITY_ROOT / "layer4_tooltip_projection_contract.json",
    AUTHORITY_ROOT / "tooltip_locale_menu_parity_contract.json",
    AUTHORITY_ROOT / "tooltip_t2_handoff.schema.json",
    AUTHORITY_ROOT / "tooltip_readiness_reason_registry.json",
    AUTHORITY_ROOT / "tooltip_t1_tool_disposition_contract.json",
)

FIXED_DECISIONS = {
    "P-1": "separate_axes",
    "P-3": "compact_display_preserve_semantic_slot_order",
    "P-9": "forbidden",
    "P-11": "logical_0_to_4_and_no_embedded_newline_only",
    "P-12": "contract_offline_deterministic_regression_only",
}
OPEN_DECISIONS = {"P-2", "P-4", "P-5", "P-6", "P-7", "P-8"}
OWNER_AMENDED_DECISIONS = {
    "P-10": "optional_layer2_applicability_with_display_silence",
}
FIXED_AUTHORITY_CLASSES = {
    "approved_roadmap_fixed_premise",
    "execution_contract_mapping",
    "sealed_presentation_principle",
    "sealed_principle_applied_to_adjacent_scope",
    "execution_scope_boundary",
    "execution_contract_exact",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TooltipContractError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TooltipContractError(f"{path}: expected JSON object")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TooltipContractError(message)


def _string_list(value: Any, label: str, *, nonempty: bool = True) -> list[str]:
    _require(isinstance(value, list), f"{label}: expected array")
    _require(all(isinstance(item, str) and item for item in value), f"{label}: expected non-empty strings")
    if nonempty:
        _require(bool(value), f"{label}: must not be empty")
    return value


def _validate_contract_values(values: dict[Path, dict[str, Any]]) -> str:
    decision = values[DECISION_CONTRACT]
    _require(decision.get("schema_version") == "iris-tooltip-t1-decision-contract-v1", "decision schema version mismatch")
    _require(decision.get("status") == "ratification_template", "decision contract must remain a pre-evidence ratification template")
    _require(decision.get("subject_binding") == "execution_subject_binding_v1", "decision subject binding mismatch")
    support_predicate = decision.get("support_predicate")
    _require(
        isinstance(support_predicate, dict)
        and support_predicate.get("id") == "current-owner-fulltype-union-v1"
        and support_predicate.get("definition") == "case-sensitive union of current Layer 2 classification, pointer-selected Layer 3 canonical, and current Layer 4 seed FullTypes",
        "support predicate must preserve exact case-sensitive FullType identities",
    )

    bundle_lines = "".join(
        f"{relative.name}={sha256_bytes(canonical_bytes(values[relative]))}\n"
        for relative in CONTRACT_FILES
        if relative != DECISION_CONTRACT
    )
    bundle_sha256 = sha256_bytes(bundle_lines.encode("utf-8"))
    rows = decision.get("decisions")
    _require(isinstance(rows, list), "decision table must be an array")
    _require(
        all(isinstance(row, dict) for row in rows)
        and [row.get("decision_id") for row in rows] == [f"P-{index}" for index in range(1, 13)],
        "canonical P-1 through P-12 table is incomplete or unordered",
    )
    required_fields = {
        "decision_id", "exact_question", "status", "allowed_choices", "required_choice",
        "selected_choice", "owner", "rationale", "evidence_refs", "subject_binding",
        "dependent_phases", "must_close_before", "contract_sha256",
    }
    for row in rows:
        decision_id = row["decision_id"]
        _require(required_fields.issubset(row), f"{decision_id}: decision fields incomplete")
        _require(isinstance(row["exact_question"], str) and bool(row["exact_question"]), f"{decision_id}: exact question missing")
        owners = _string_list(row["owner"], f"{decision_id}.owner")
        _require(bool(owners), f"{decision_id}: owner missing")
        allowed = _string_list(row["allowed_choices"], f"{decision_id}.allowed_choices", nonempty=False)
        _string_list(row["evidence_refs"], f"{decision_id}.evidence_refs")
        _string_list(row["dependent_phases"], f"{decision_id}.dependent_phases")
        _require(row["subject_binding"] == "execution_subject_binding_v1", f"{decision_id}: subject binding mismatch")
        _require(row["contract_sha256"] == bundle_sha256, f"{decision_id}: contract bundle identity mismatch")
        if decision_id in FIXED_DECISIONS:
            expected = FIXED_DECISIONS[decision_id]
            _require(row["status"] == "already_fixed", f"{decision_id}: fixed status mismatch")
            _require(row["required_choice"] == expected and row["selected_choice"] == expected, f"{decision_id}: fixed choice mismatch")
            refs = row.get("authority_references")
            _require(isinstance(refs, list) and bool(refs), f"{decision_id}: fixed authority binding missing")
            for ref in refs:
                _require(isinstance(ref, dict), f"{decision_id}: malformed authority reference")
                _require(ref.get("class") in FIXED_AUTHORITY_CLASSES, f"{decision_id}: inadmissible authority class")
                _require(ref.get("scope") in {"exact", "adjacent_application"}, f"{decision_id}: authority scope mismatch")
                _require(isinstance(ref.get("reference"), str) and bool(ref["reference"]), f"{decision_id}: authority reference missing")
        elif decision_id in OWNER_AMENDED_DECISIONS:
            expected = OWNER_AMENDED_DECISIONS[decision_id]
            _require(row["status"] == "owner_amended_successor", f"{decision_id}: owner amendment status mismatch")
            _require(row["required_choice"] == expected and row["selected_choice"] == expected, f"{decision_id}: owner amendment choice mismatch")
            _require(expected in allowed, f"{decision_id}: owner amendment choice is not allowed")
            refs = row.get("authority_references")
            _require(
                isinstance(refs, list)
                and len(refs) == 1
                and refs[0].get("class") == "explicit_product_contract_owner_amendment"
                and refs[0].get("scope") == "exact"
                and isinstance(refs[0].get("reference"), str)
                and bool(refs[0]["reference"]),
                f"{decision_id}: owner amendment authority binding mismatch",
            )
        else:
            _require(decision_id in OPEN_DECISIONS and row["status"] == "open_in_T1", f"{decision_id}: open status mismatch")
            _require(row["required_choice"] is None, f"{decision_id}: open decision cannot have required_choice")
            _require(isinstance(row["selected_choice"], str) and row["selected_choice"] in allowed, f"{decision_id}: selected choice is not allowed")
            expected_ref = f"pre_ratification_decision_evidence.json#records.{decision_id}"
            _require(expected_ref in row["evidence_refs"], f"{decision_id}: exact W1-A evidence record ref missing")

    display = values[AUTHORITY_ROOT / "tooltip_display_contract.json"]
    _require(display.get("schema_version") == "iris-tooltip-display-contract-v1", "display schema version mismatch")
    _require(tuple(display.get("slot_order", ())) == SLOT_ORDER, "display slot identity mismatch")
    _require(tuple(display.get("supported_locales", ())) == SUPPORTED_LOCALES, "display locale identity mismatch")
    _require(display.get("defect_compaction_allowed") is False, "display defect compaction must be forbidden")
    gates = display.get("hard_gates")
    _require(isinstance(gates, dict) and gates.get("maximum_logical_rows") == 4 and gates.get("embedded_newline_allowed") is False, "display hard gates mismatch")

    layer2 = values[AUTHORITY_ROOT / "layer2_tooltip_input_contract.json"]
    _require(layer2.get("current_route") == "no_admissible_authority_relation", "Layer 2 route mismatch")
    _require(layer2.get("raw_tag_resolution_allowed") is False and layer2.get("runtime_resolver_reimplementation_allowed") is False, "Layer 2 raw inference prohibition mismatch")
    layer2_candidate = layer2.get("workstream_candidate_route")
    _require(
        isinstance(layer2_candidate, dict)
        and layer2_candidate.get("path") == "Iris/build/classification/data/classification_layer2_owner_output.json"
        and layer2_candidate.get("schema") == "Iris/_docs/authority/classification_layer2/classification_layer2_owner_output.schema.json"
        and layer2_candidate.get("current_ecosystem_adoption") == "pending_T1_D6",
        "Layer 2 workstream candidate route mismatch",
    )
    layer2_amendment = layer2.get("successor_owner_amendment")
    _require(
        isinstance(layer2_amendment, dict)
        and layer2_amendment.get("layer2_is_required_for_every_support_fulltype") is False
        and layer2_amendment.get("applicability_rule") == "admissible_current_owner_category_and_primary_v1"
        and layer2_amendment.get("display_silence_disposition") == "omit_S1_without_placeholder_and_compact_S2_through_S4"
        and layer2_amendment.get("display_silence_is_classification_correction") is False
        and layer2_amendment.get("display_silence_is_t2_blocker") is False
        and layer2_amendment.get("per_fulltype_positive_absence_required") is False
        and layer2_amendment.get("menu_surface_coverage_must_equal_tooltip") is False
        and layer2_amendment.get("d2_owns_menu_relation_and_applicable_na_parity") is True,
        "Layer 2 successor owner amendment mismatch",
    )
    layer3 = values[AUTHORITY_ROOT / "layer3_tooltip_input_contract.json"]
    _require(layer3.get("identity_before_locale") is True, "Layer 3 identity/readiness ordering mismatch")
    _require(all(layer3.get(key) is False for key in ("body_truncation_allowed", "body_summarization_allowed", "body_rewrite_allowed", "multiple_core_fact_synthesis_allowed")), "Layer 3 body rewrite prohibition mismatch")
    layer3_owner_output = layer3.get("current_owner_output")
    _require(
        isinstance(layer3_owner_output, dict)
        and layer3_owner_output.get("path") == "Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json"
        and layer3_owner_output.get("producer") == "iris_tooling.build.build_layer3_english_localization"
        and layer3_owner_output.get("entry_count") == 1314,
        "Layer 3 current Tooltip owner output adoption mismatch",
    )
    menu_evidence_ownership = layer3.get("menu_consumer_evidence_ownership")
    _require(
        isinstance(menu_evidence_ownership, dict)
        and menu_evidence_ownership.get("owner") == "Menu consumer owner"
        and menu_evidence_ownership.get("dvf_owner_output_may_issue_consumer_identity_refs") is False
        and menu_evidence_ownership.get("independent_evidence_required_for_verified") is True,
        "Layer 3 Menu consumer evidence ownership mismatch",
    )
    absence = layer3.get("absence_mapping")
    _require(isinstance(absence, dict) and absence.get("missing_owner_row") == "upstream_identity_correction_required", "Layer 3 absence mapping mismatch")

    layer4 = values[AUTHORITY_ROOT / "layer4_tooltip_projection_contract.json"]
    _require(layer4.get("maximum_selected") == 2, "Layer 4 capacity mismatch")
    _require(layer4.get("single_source_rule") == "up_to_two_from_single_source" and layer4.get("both_source_rule") == "one_recipe_plus_one_rightclick", "Layer 4 source equivalence mismatch")
    _require(layer4.get("pipeline") == ["semantic_public_eligibility", "stable_order", "exact_identity_dedupe", "source_equivalence", "bounded_selection", "selected_identity_freeze", "locale_lookup", "menu_evidence_lookup"], "Layer 4 pipeline mismatch")
    adoption = layer4.get("current_input_adoption")
    _require(isinstance(adoption, dict), "Layer 4 current input adoption missing")
    _require(adoption.get("path") == "Iris/build/description/v2/data/upstream_usecases_by_fulltype.json", "Layer 4 input must use current owner data, not reproduction baseline")
    _require(adoption.get("classification") == "current" and adoption.get("role") == "read_only_layer4_owner_identity_input", "Layer 4 input adoption role mismatch")

    parity = values[AUTHORITY_ROOT / "tooltip_locale_menu_parity_contract.json"]
    _require(tuple(parity.get("supported_locales", ())) == SUPPORTED_LOCALES, "parity locale mismatch")
    _require(parity.get("cross_locale_fallback_allowed") is False and parity.get("locale_dependent_reselection_allowed") is False, "locale fallback/reselection must be forbidden")
    _require(parity.get("missing_or_contradictory_authority_relation_t2_blocking") is True, "parity relation blocker mismatch")
    rightclick_locale = parity.get("current_rightclick_locale_route")
    _require(
        isinstance(rightclick_locale, dict)
        and rightclick_locale.get("identity_relation_path") == "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua#RIGHTCLICK_LABEL_KEYS"
        and rightclick_locale.get("adoption_rule") == "exact selected rightclick identity to current translation key to exact KO/EN surface only",
        "current right-click locale authority route mismatch",
    )
    layer3_shared = parity.get("current_layer3_shared_authority_route")
    _require(
        isinstance(layer3_shared, dict)
        and layer3_shared.get("evidence_class") == "shared_authority_relation_not_independent_consumer_evidence"
        and layer3_shared.get("status") == "unverified_without_independent_consumer_evidence"
        and parity.get("dvf_owner_output_may_self_issue_menu_consumer_evidence") is False,
        "Layer 3 shared Menu authority relation mismatch",
    )

    handoff = values[AUTHORITY_ROOT / "tooltip_t2_handoff.schema.json"]
    _require(handoff.get("schema_version") == "iris-tooltip-t2-handoff-schema-v1", "handoff schema version mismatch")
    _require(handoff.get("generation_condition") == "T2_FULL_DATA_PROGRESSION equals OPEN only", "handoff OPEN-only condition missing")
    invariants = handoff.get("x-iris-invariants")
    _require(isinstance(invariants, dict) and invariants.get("slot_order") == list(SLOT_ORDER) and invariants.get("slot_ids_unique") is True and invariants.get("surface_forbids_cr_lf") is True, "handoff semantic invariants missing")
    surface_props = handoff.get("properties", {}).get("slots", {}).get("items", {}).get("properties", {}).get("localized_surfaces", {}).get("properties", {})
    _require(all(isinstance(surface_props.get(locale), dict) and surface_props[locale].get("pattern") == r"^[^\r\n]+$" for locale in SUPPORTED_LOCALES), "handoff CR/LF schema gate missing")

    registry = values[AUTHORITY_ROOT / "tooltip_readiness_reason_registry.json"]
    reasons = registry.get("reasons")
    _require(isinstance(reasons, list) and bool(reasons) and all(isinstance(row, dict) for row in reasons), "reason registry malformed")
    codes = [row.get("code") for row in reasons]
    _require(all(isinstance(code, str) and code for code in codes) and len(codes) == len(set(codes)), "reason registry codes must be unique")
    for row in reasons:
        _require(isinstance(row.get("owner"), str) and row["owner"] and isinstance(row.get("layer"), str) and row["layer"], f"{row.get('code')}: reason owner/layer missing")
        _require(isinstance(row.get("t2_blocking"), bool), f"{row.get('code')}: reason blocker type mismatch")
        _require(isinstance(row.get("acceptance"), str) and row["acceptance"] and isinstance(row.get("re_audit"), str) and row["re_audit"], f"{row.get('code')}: reason acceptance/re-audit missing")

    tools = values[AUTHORITY_ROOT / "tooltip_t1_tool_disposition_contract.json"]
    entries = tools.get("entries")
    _require(isinstance(entries, list) and any(isinstance(row, dict) and row.get("path") == "Iris/tooling/src/iris_tooling/domains/tooltip_t1" and row.get("disposition") == "current_required" for row in entries), "current Tooltip T1 tool route missing")
    _require(any(isinstance(row, dict) and row.get("disposition") == "historical" and row.get("current_execution_allowed") is False for row in entries), "historical tool disposition missing")
    finalization = tools.get("post_gate_finalization")
    _require(isinstance(finalization, dict), "Tooltip T1 post-gate finalization contract missing")
    _require(finalization.get("candidate_contract_and_audit_axis") == "partial" and finalization.get("candidate_formal_closeout_state") == "implemented_only", "Tooltip T1 candidate closeout axis mismatch")
    _require(finalization.get("complete_requires_same_subject_run_a_run_b_and_comparator_exit_0") is True and finalization.get("failed_or_mismatched_gate_writes_complete_closeout") is False, "Tooltip T1 complete closeout gate mismatch")
    _require(finalization.get("output_root") == "repository_external_empty", "Tooltip T1 final closeout output boundary mismatch")
    return bundle_sha256


def validate_contracts(repository_root: Path, supplied_decision_sha256: str) -> dict[str, str]:
    try:
        identities: dict[str, str] = {}
        values: dict[Path, dict[str, Any]] = {}
        for relative in CONTRACT_FILES:
            path = repository_root / relative
            values[relative] = load_json(path)
            identities[relative.as_posix()] = sha256_file(path)
        actual = identities[DECISION_CONTRACT.as_posix()]
        _require(supplied_decision_sha256 == actual, "decision contract SHA-256 mismatch")
        _validate_contract_values(values)
        adoption = values[AUTHORITY_ROOT / "layer4_tooltip_projection_contract.json"]["current_input_adoption"]
        adoption_path = repository_root / adoption["path"]
        _require(sha256_file(adoption_path) == adoption.get("sha256"), "Layer 4 current input adoption SHA-256 mismatch")
        manifest = load_json(repository_root / "Iris/_docs/authority/iris_current_authority_manifest.json")
        entries = manifest.get("entries")
        _require(isinstance(entries, list), "current authority manifest entries missing")
        adopted_entries = [row for row in entries if isinstance(row, dict) and row.get("path") == adoption["path"]]
        _require(len(adopted_entries) == 1 and adopted_entries[0].get("sha256") == adoption["sha256"] and adopted_entries[0].get("classification") == "current", "Layer 4 exact current authority manifest adoption missing")
        layer3_owner_output = values[AUTHORITY_ROOT / "layer3_tooltip_input_contract.json"]["current_owner_output"]
        layer3_owner_value = load_json(repository_root / layer3_owner_output["path"])
        _require(
            sha256_bytes(canonical_bytes(layer3_owner_value)) == layer3_owner_output.get("canonical_sha256"),
            "Layer 3 current Tooltip owner output canonical SHA-256 mismatch",
        )
        route = load_json(repository_root / "Iris/_docs/authority/iris_current_route_index.json")
        route_text = json.dumps(route, ensure_ascii=False)
        _require("Iris/_docs/authority/tooltip_t1" in route_text and "docs/iris_tooltip_t1_display_contract_policy.md" in route_text, "current Tooltip T1 route mismatch")
        return identities
    except TooltipContractError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise TooltipContractError(f"malformed Tooltip T1 contract bundle: {exc}") from exc


def ratify_open_decisions(
    decision: dict[str, Any],
    evidence: dict[str, Any],
    *,
    evidence_sha256: str,
    subject_identity_sha256: str,
) -> list[dict[str, Any]]:
    _require(evidence.get("schema_version") == "iris-tooltip-pre-ratification-decision-evidence-v1", "W1-A evidence schema mismatch")
    _require(evidence.get("phase") == "W1-A_read_only_complete", "W1-A evidence phase mismatch")
    _require(evidence.get("subject_identity_sha256") == subject_identity_sha256, "W1-A evidence subject mismatch")
    _require(sha256_bytes(canonical_bytes(evidence)) == evidence_sha256, "W1-A evidence hash mismatch")
    records = evidence.get("records")
    _require(isinstance(records, dict), "W1-A evidence records missing")
    adopted: list[dict[str, Any]] = []
    for row in decision.get("decisions", []):
        if row.get("status") != "open_in_T1":
            continue
        decision_id = row["decision_id"]
        record = records.get(decision_id)
        _require(isinstance(record, dict), f"{decision_id}: W1-A record missing")
        _require(record.get("decision_id") == decision_id, f"{decision_id}: W1-A record identity mismatch")
        _require(record.get("subject_identity_sha256") == subject_identity_sha256, f"{decision_id}: W1-A record subject mismatch")
        _require(record.get("evidence_state") in {"present", "absent", "mixed"}, f"{decision_id}: W1-A evidence state missing")
        adopted.append({
            "decision_id": decision_id,
            "selected_choice": row["selected_choice"],
            "evidence_ref": f"pre_ratification_decision_evidence.json#records.{decision_id}",
            "evidence_sha256": evidence_sha256,
            "subject_identity_sha256": subject_identity_sha256,
        })
    _require({row["decision_id"] for row in adopted} == OPEN_DECISIONS, "open decision ratification set mismatch")
    return adopted


def git_subject(repository_root: Path) -> dict[str, Any]:
    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=repository_root, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if completed.returncode:
            raise TooltipContractError(completed.stderr.strip() or "git subject query failed")
        return completed.stdout.strip()
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    return {
        "schema_version": "iris-tooltip-t1-subject-binding-v1",
        "commit": git("rev-parse", "HEAD"),
        "tree": git("show", "-s", "--format=%T", "HEAD"),
        "working_tree_clean": not bool(status),
        "dirty_path_count": len(status.splitlines()) if status else 0,
        "dirty_state_sha256": sha256_bytes((status + ("\n" if status else "")).encode("utf-8")),
    }


def validate_execution_subject(
    subject: dict[str, Any],
    *,
    expected_commit: str | None = None,
) -> None:
    _require(subject.get("working_tree_clean") is True, "blocked_subject_binding: candidate run requires a clean checkout")
    _require(isinstance(subject.get("commit"), str) and len(subject["commit"]) == 40, "blocked_subject_binding: commit identity missing")
    _require(isinstance(subject.get("tree"), str) and len(subject["tree"]) == 40, "blocked_subject_binding: tree identity missing")
    if expected_commit is not None:
        _require(subject["commit"] == expected_commit, "blocked_subject_binding: stale commit")


_CLASSIFICATION_ROW = re.compile(r'^\s*\["([^"]+)"\]\s*=\s*\{\s*((?:"[^"]+"\s*,?\s*)+)\},\s*$')
_QUOTED = re.compile(r'"([^"]+)"')


def parse_classifications(path: Path) -> dict[str, tuple[str, ...]]:
    rows: dict[str, tuple[str, ...]] = {}
    in_primary = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("IrisPrimarySubcategory"):
            in_primary = True
        if in_primary:
            continue
        match = _CLASSIFICATION_ROW.match(line)
        if not match:
            continue
        full_type = match.group(1)
        if full_type in rows:
            raise TooltipContractError(f"duplicate classification FullType: {full_type}")
        rows[full_type] = tuple(_QUOTED.findall(match.group(2)))
    if not rows:
        raise TooltipContractError("classification census is empty")
    return rows


def parse_lua_string_map(paths: Iterable[Path]) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r'^\s*\[?"?([^"\]=\s]+)"?\]?\s*=\s*"((?:[^"\\]|\\.)*)"')
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if match:
                result[match.group(1)] = bytes(match.group(2), "utf-8").decode("unicode_escape") if "\\" in match.group(2) else match.group(2)
    return result
