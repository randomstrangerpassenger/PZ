from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable

from iris_tooling.domains.layer4.tooltip_t1_d4 import (
    OWNER_OUTPUT as L4_RECIPE_LOCALE_OWNER_INPUT,
    load_recipe_locale_owner_input,
)
from iris_tooling.domains.classification.layer2_contract import OWNER_OUTPUT, RESOLUTION_CONTRACT
from iris_tooling.domains.classification.layer2_validator import validate_owner_output

from .contract import (
    AUTHORITY_ROOT,
    canonical_bytes,
    fulltype_set_sha256,
    git_subject,
    load_json,
    parse_classifications,
    sha256_bytes,
    sha256_file,
    ratify_open_decisions,
    validate_layer3_owner_output,
    validate_execution_subject,
    validate_contracts,
)
from .models import (
    LocaleSurfaceReadiness,
    MenuParityStatus,
    SemanticSlotState,
    Slot,
    T2Progression,
    TooltipContractError,
    build_handoff_row,
    validate_handoff_row,
)
from .projection import Layer4Candidate, select_layer4, verify_invariants
from .d5 import (
    ITEM_SOURCE,
    TARGETS,
    collision_correction_members,
    exact_identity_metrics,
    resolved_collision_members,
)
from .d2 import HARNESS, PROJECTION_BUILDER, load_relation


L3_POINTER = Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua")
L3_GENERATIONS = Path("Iris/media/lua/client/Iris/Data/IrisLayer3Generations")
L3_INPUT_MANIFEST = Path("Iris/build/description/v2/data/dvf_3_3_input_manifest.json")
L3_TOOLTIP_OWNER_INPUT = Path("Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json")
CLASSIFICATIONS = Path("Iris/media/lua/client/Iris/Data/IrisClassifications.lua")
L4_OWNER_INPUT = Path("Iris/build/description/v2/data/upstream_usecases_by_fulltype.json")
L4_RUNTIME_ROOT = Path("Iris/media/lua/client/Iris/Data/UseCaseDescriptions")
KO_TRANSLATION = Path("Iris/media/lua/shared/translate/ko/Iris_ko.txt")
EN_TRANSLATION = Path("Iris/media/lua/shared/translate/en/Iris_en.txt")
MENU_TOOLTIP_SOURCES = (
    Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua"),
    Path("Iris/media/lua/client/Iris/Data/layer3_renderer.lua"),
    Path("Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua"),
    Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua"),
    Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua"),
    Path("Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua"),
    Path("Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua"),
)

D6_DIRECT_PARENT = "76fe186d44815c9fa061d496ce88224e2ddce082"
D6_DIRECT_PARENT_TREE = "f6532a6fca016feee503ca5c154d90607741f5ee"
D6_REQUIRED_ANCESTRY = {
    "D1": "8bbc40169e86bd2e818c440a823e497f852a1e69",
    "D2": "0e959b3bd7055d58f319fa9d69a5b110bf48b8b7",
    "D3": "e70fcd6fc2dd09bd0f756339f3229b5d1a58681f",
    "D4": "a8fddf747738045df08579ae34b0b727e3cf91ad",
    "D5": "c86b4a747025aa593eddacd7d9c7de7c095ebad8",
}
FROZEN_SUPPORT_COUNT = 2_280
FROZEN_SUPPORT_SHA256 = "3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6"


def classify_progression(upstream_blockers: int, contract_blockers: int, mock_product_decisions: int) -> T2Progression:
    contract_total = contract_blockers + mock_product_decisions
    if upstream_blockers and contract_total:
        return T2Progression.MIXED
    if upstream_blockers:
        return T2Progression.UPSTREAM
    if contract_total:
        return T2Progression.CONTRACT
    return T2Progression.OPEN


def build_progression_record(
    corrections: Iterable[dict[str, Any]],
    source_artifact_refs: Iterable[str] = (),
) -> tuple[dict[str, Any], dict[str, int]]:
    blocking = [row for row in corrections if row.get("t2_blocking") is True]
    blocker_by_owner = dict(sorted(Counter(row["owner"] for row in blocking).items()))
    progression_state = classify_progression(len(blocking), 0, 0)
    progression = {
        "schema_version": "iris-tooltip-t2-progression-v1",
        "T2_FULL_DATA_PROGRESSION": progression_state.value,
        "upstream_blocker_count": len(blocking),
        "contract_blocker_count": 0,
        "mock_consumer_product_decision_count": 0,
        "blocking_cause_classes": ["upstream_structured_input_correction"] if blocking else [],
        "blocking_cause_owners": list(blocker_by_owner),
        "source_artifact_refs": list(source_artifact_refs),
        "acceptance_condition": "all T2-blocking owner corrections are accepted and the affected or owner-ratified full range is re-audited",
        "re_audit_condition": "new exact subject binding",
    }
    return progression, blocker_by_owner


def candidate_closeout_record(
    progression: T2Progression | str,
    *,
    layer2_relation_complete: bool = False,
) -> dict[str, Any]:
    progression_value = progression.value if isinstance(progression, T2Progression) else progression
    validated = ["candidate contract/schema audit", "whole-universe offline audit", "deterministic Layer 4 identity selection", "Layer 4 current consumer identity subset"]
    unvalidated = ["canonical receipt-bound full gate and deterministic comparator", "Layer 3 Menu parity for selected DVF facts lacking independent Menu consumer fact-identity evidence"]
    if layer2_relation_complete:
        validated.append("D2 actual Lua full-set Layer 2 Menu consumer relation")
    else:
        unvalidated.append("Layer 2 Menu parity where owner-resolved identity evidence is unavailable")
    return {
        "schema_version": "iris-tooltip-t1-axis-closeout-v1",
        "contract_and_audit_axis": "partial",
        "T2_FULL_DATA_PROGRESSION": progression_value,
        "formal_closeout_state": "implemented_only",
        "validation_ceiling": "candidate and offline audit only; canonical full-gate Run A/Run B and deterministic comparator exit-0 evidence is not yet bound",
        "validated": validated,
        "unvalidated_but_in_scope": unvalidated,
        "out_of_scope": ["runtime rendering", "actual visual fit", "release/deployment"],
        "non_claims": ["no formal complete claim before same-subject canonical gate success", "no runtime mutation", "no T2 static Lua generation", "no full Menu parity claim"],
    }


def validate_whole_universe(support: set[str], audited_rows: list[dict[str, Any]]) -> dict[str, int]:
    audited = [row.get("full_type") for row in audited_rows]
    counts = Counter(audited)
    duplicate = sum(count - 1 for count in counts.values() if count > 1)
    audited_set = {value for value in audited if isinstance(value, str)}
    return {
        "duplicate_full_type": duplicate,
        "missing_supported_full_type": len(support - audited_set),
        "unexpected_supported_full_type": len(audited_set - support),
        "unclassified_readiness": sum(not row.get("overall_readiness") for row in audited_rows),
    }


def classify_menu_relation(selected_ids: Iterable[str], consumer_ids: set[str]) -> MenuParityStatus:
    selected = tuple(selected_ids)
    if not selected:
        return MenuParityStatus.NOT_APPLICABLE
    if all(identity in consumer_ids for identity in selected):
        return MenuParityStatus.VERIFIED
    return MenuParityStatus.CORRECTION_REQUIRED


def correction_completeness_metrics(
    corrections: Iterable[dict[str, Any]],
    known_reasons: set[str] | dict[str, str],
) -> dict[str, int]:
    rows = list(corrections)
    reason_codes = set(known_reasons)
    expected_owners = known_reasons if isinstance(known_reasons, dict) else {}
    return {
        "unknown_owner": sum(
            not isinstance(row.get("owner"), str)
            or not row["owner"]
            or bool(expected_owners and row.get("reason_code") in expected_owners and row["owner"] != expected_owners[row["reason_code"]])
            for row in rows
        ),
        "unknown_reason_code": sum(row.get("reason_code") not in reason_codes for row in rows),
        "missing_acceptance_condition": sum(not isinstance(row.get("correction_acceptance_condition"), str) or not row["correction_acceptance_condition"] for row in rows),
        "missing_reaudit_condition": sum(not isinstance(row.get("re_audit_condition"), str) or not row["re_audit_condition"] for row in rows),
    }


def source_mutation_count(before: dict[str, str], after: dict[str, str]) -> int:
    return int(before != after)


def menu_owner_output_self_comparison_count(entries: dict[str, Any]) -> int:
    """Count DVF-owner rows that improperly self-issue Menu consumer evidence."""
    return sum(
        isinstance(row, dict) and bool(row.get("menu_consumer_fact_identity_refs"))
        for row in entries.values()
    )


def normalized_collisions(values: Iterable[str]) -> dict[str, tuple[str, ...]]:
    buckets: dict[str, list[str]] = {}
    for value in values:
        buckets.setdefault(value.lower(), []).append(value)
    return {
        key: tuple(sorted(rows))
        for key, rows in buckets.items()
        if len(set(rows)) > 1
    }


def layer2_title_surfaces(owner_row: dict[str, Any]) -> dict[str, str]:
    """Carry both approved D1 labels without resolving or translating identity."""
    return {
        locale: f"[{owner_row['category_surface'][locale]} - {owner_row['primary_subcategory_surface'][locale]}]"
        for locale in ("ko", "en")
    }


def public_surface_reason(text: Any, locale: str, lexical_fixture: dict[str, Any]) -> str | None:
    if not isinstance(text, str) or not text:
        return "LOCALE_SELECTED_SURFACE_MISSING"
    if "\n" in text or "\r" in text:
        return "LINE_FIT_EMBEDDED_NEWLINE"
    tokens = lexical_fixture.get(f"{locale}_forbidden")
    if not isinstance(tokens, list) or not all(isinstance(token, str) and token for token in tokens):
        raise TooltipContractError("lexical guard fixture is malformed")
    comparable = text if locale == "ko" else text.lower()
    if any((token if locale == "ko" else token.lower()) in comparable for token in tokens):
        return "LOCALE_FORBIDDEN_EXPRESSION"
    return None


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def _d6_admission(repository_root: Path, subject: dict[str, Any]) -> dict[str, Any]:
    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=repository_root, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if completed.returncode:
            raise TooltipContractError(completed.stderr.strip() or "D6 ancestry query failed")
        return completed.stdout.strip()

    if git("rev-parse", f"{D6_DIRECT_PARENT}^{{tree}}") != D6_DIRECT_PARENT_TREE:
        raise TooltipContractError("D6 direct-parent tree mismatch")
    ancestry = {"direct_parent": D6_DIRECT_PARENT, **D6_REQUIRED_ANCESTRY}
    for label, commit in ancestry.items():
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, subject["commit"]],
            cwd=repository_root, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if completed.returncode != 0:
            raise TooltipContractError(f"D6 required ancestry missing: {label}={commit}")
    return {
        "schema_version": "iris-tooltip-t1-d6-admission-v1",
        "direct_parent": {"commit": D6_DIRECT_PARENT, "tree": D6_DIRECT_PARENT_TREE},
        "required_ancestry": D6_REQUIRED_ANCESTRY,
        "implementation_subject": {"commit": subject["commit"], "tree": subject["tree"]},
        "working_tree_clean": True,
        "historical_patch_reapplied": False,
    }


def _strict_candidate_result(
    output_root: Path,
    subject: dict[str, Any],
    contract_hashes: dict[str, str],
    admission: dict[str, Any],
    support: list[str],
    audited_slots: dict[str, tuple[Slot, ...]],
    corrections: list[dict[str, Any]],
    progression: dict[str, Any],
    blocker_by_owner: dict[str, int],
    layer2_relation_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    progression_value = progression["T2_FULL_DATA_PROGRESSION"]
    blocking = [row for row in corrections if row.get("t2_blocking") is True]
    correction_summary = {
        "correction_total": len(corrections),
        "t2_blocking_correction_total": len(blocking),
        "blocker_by_owner": blocker_by_owner,
        "blocker_by_reason": dict(sorted(Counter(row["reason_code"] for row in blocking).items())),
        "owner_blocker_sum": sum(blocker_by_owner.values()),
    }
    layer2_distribution = dict(sorted(Counter(
        row.get("disposition") for row in layer2_relation_rows.values()
    ).items()))
    closeout = candidate_closeout_record(progression_value, layer2_relation_complete=True)
    base_receipt = {
        "schema_version": "iris-tooltip-t1-run-receipt-v1",
        "candidate_mode": "strict_t2_handoff",
        "admission": admission,
        "T2_FULL_DATA_PROGRESSION": progression_value,
        "candidate_closeout": closeout,
        "progression": progression,
        "correction_summary": correction_summary,
        "layer2_relation_distribution": layer2_distribution,
        "source_mutation": 0,
    }
    if progression_value != T2Progression.OPEN.value:
        _write_json(output_root / "run_receipt.json", {
            **base_receipt,
            "subject_binding_sha256": None,
            "artifacts": {},
            "production_t2_handoff": "absent",
        })
        return {
            "support_count": len(support),
            "correction_count": len(corrections),
            "progression": progression_value,
            "production_t2_handoff": "absent",
            "run_receipt_sha256": sha256_file(output_root / "run_receipt.json"),
        }

    support_sha256 = fulltype_set_sha256(support)
    if len(support) != FROZEN_SUPPORT_COUNT or support_sha256 != FROZEN_SUPPORT_SHA256:
        raise TooltipContractError("strict handoff support binding mismatch")
    handoff_rows = [
        build_handoff_row(full_type, audited_slots[full_type], progression=T2Progression.OPEN)
        for full_type in support
    ]
    handoff_fulltypes = [row["full_type"] for row in handoff_rows]
    if len(handoff_fulltypes) != len(set(handoff_fulltypes)) or handoff_fulltypes != support:
        raise TooltipContractError("strict handoff exact FullType set mismatch")

    subject_path = output_root / "subject_binding.json"
    input_path = output_root / "t2_handoff_input.jsonl"
    receipt_path = output_root / "run_receipt.json"
    manifest_path = output_root / "t2_handoff_manifest.json"
    _write_json(subject_path, subject)
    _write_jsonl(input_path, handoff_rows)
    handoff_input_sha256 = sha256_file(input_path)
    artifacts = {
        "subject_binding.json": sha256_file(subject_path),
        "t2_handoff_input.jsonl": handoff_input_sha256,
    }
    receipt = {
        **base_receipt,
        "subject_binding_sha256": artifacts["subject_binding.json"],
        "artifacts": artifacts,
        "support": {"count": len(support), "sha256": support_sha256},
        "handoff": {
            "row_count": len(handoff_rows),
            "fulltype_sha256": fulltype_set_sha256(handoff_fulltypes),
            "input_sha256": handoff_input_sha256,
        },
        "authority_contract_bundle_sha256": contract_hashes["authority_contract_bundle_sha256"],
        "production_t2_handoff": "candidate_present",
    }
    _write_json(receipt_path, receipt)
    receipt_sha256 = sha256_file(receipt_path)
    manifest = {
        "schema_version": "iris-tooltip-t2-handoff-manifest-v1",
        "subject": {"commit": subject["commit"], "tree": subject["tree"]},
        "support_count": len(support),
        "support_sha256": support_sha256,
        "handoff_row_count": len(handoff_rows),
        "handoff_fulltype_sha256": fulltype_set_sha256(handoff_fulltypes),
        "handoff_input_sha256": handoff_input_sha256,
        "authority_contract_bundle_sha256": contract_hashes["authority_contract_bundle_sha256"],
        "candidate_run_receipt_sha256": receipt_sha256,
    }
    _write_json(manifest_path, manifest)
    return {
        "support_count": len(support),
        "support_sha256": support_sha256,
        "correction_count": len(corrections),
        "progression": progression_value,
        "handoff_row_count": len(handoff_rows),
        "handoff_input_sha256": handoff_input_sha256,
        "handoff_manifest_sha256": sha256_file(manifest_path),
        "production_t2_handoff": "candidate_present",
        "run_receipt_sha256": receipt_sha256,
    }


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TooltipContractError(f"{label} is unavailable or malformed: {exc}") from exc
    if not isinstance(value, dict):
        raise TooltipContractError(f"{label} must be a JSON object")
    return value


def _require_external(repository_root: Path, path: Path, label: str) -> Path:
    resolved_repo = repository_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(resolved_repo)
    except ValueError:
        return resolved
    raise TooltipContractError(f"{label} must be repository-external")


def _require_hash(path: Path, expected: str, label: str) -> str:
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise TooltipContractError(f"{label} has no valid lowercase SHA-256 binding")
    if not path.is_file():
        raise TooltipContractError(f"{label} is missing")
    actual = sha256_file(path)
    if actual != expected:
        raise TooltipContractError(f"{label} SHA-256 mismatch")
    return actual


def _subject_equal(actual: Any, expected: dict[str, str]) -> bool:
    return (
        isinstance(actual, dict)
        and actual.get("commit") == expected["commit"]
        and actual.get("tree") == expected["tree"]
    )


def _read_jsonl_objects(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        raw = path.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines() if line]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TooltipContractError(f"{label} is unavailable or malformed: {exc}") from exc
    if not all(isinstance(row, dict) for row in rows):
        raise TooltipContractError(f"{label} must contain JSON objects")
    if raw != b"".join(canonical_bytes(row) for row in rows):
        raise TooltipContractError(f"{label} is not canonical JSONL")
    return rows


def _validate_strict_candidate(
    repository_root: Path,
    root: Path,
    receipt: dict[str, Any],
    receipt_sha256: str,
) -> tuple[dict[str, str], dict[str, Any], dict[str, str], dict[str, Any]]:
    expected_names = {
        "subject_binding.json", "t2_handoff_input.jsonl",
        "t2_handoff_manifest.json", "run_receipt.json",
    }
    if {path.name for path in root.iterdir()} != expected_names:
        raise TooltipContractError("strict candidate root file set mismatch")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {
        "subject_binding.json", "t2_handoff_input.jsonl",
    }:
        raise TooltipContractError("strict candidate artifact binding mismatch")
    for name, digest in artifacts.items():
        _require_hash(root / name, digest, f"strict candidate artifact {name}")

    subject_path = root / "subject_binding.json"
    _require_hash(subject_path, receipt.get("subject_binding_sha256"), "candidate subject binding")
    subject = _load_json_object(subject_path, "candidate subject binding")
    expected_subject = {"commit": subject.get("commit"), "tree": subject.get("tree")}
    if not all(isinstance(expected_subject[key], str) and len(expected_subject[key]) == 40 for key in ("commit", "tree")):
        raise TooltipContractError("candidate subject identity is incomplete")
    current_subject = git_subject(repository_root)
    validate_execution_subject(current_subject, expected_commit=expected_subject["commit"])
    if current_subject["tree"] != expected_subject["tree"]:
        raise TooltipContractError("candidate subject tree differs from finalizer checkout")

    closeout = receipt.get("candidate_closeout")
    if not isinstance(closeout, dict) or closeout.get("contract_and_audit_axis") != "partial" or closeout.get("formal_closeout_state") != "implemented_only":
        raise TooltipContractError("candidate closeout must remain partial/implemented_only before canonical gate success")
    progression = receipt.get("progression")
    if not isinstance(progression, dict) or progression.get("T2_FULL_DATA_PROGRESSION") != T2Progression.OPEN.value:
        raise TooltipContractError("strict candidate progression must be OPEN")
    if receipt.get("T2_FULL_DATA_PROGRESSION") != T2Progression.OPEN.value or closeout.get("T2_FULL_DATA_PROGRESSION") != T2Progression.OPEN.value:
        raise TooltipContractError("candidate T2 progression bindings disagree")
    if progression.get("upstream_blocker_count") != 0 or progression.get("contract_blocker_count") != 0:
        raise TooltipContractError("strict candidate blocker count is nonzero")
    correction = receipt.get("correction_summary")
    if (
        not isinstance(correction, dict)
        or correction.get("t2_blocking_correction_total") != 0
        or correction.get("owner_blocker_sum") != 0
        or correction.get("blocker_by_owner") != {}
        or correction.get("blocker_by_reason") != {}
    ):
        raise TooltipContractError("strict candidate correction summary is not blocker-free")
    if receipt.get("layer2_relation_distribution") != {
        "not_applicable": 874, "verified": 1406,
    }:
        raise TooltipContractError("strict candidate Layer 2 relation distribution mismatch")
    if receipt.get("production_t2_handoff") != "candidate_present":
        raise TooltipContractError("strict candidate handoff presence claim missing")

    manifest_path = root / "t2_handoff_manifest.json"
    manifest = _load_json_object(manifest_path, "T2 handoff manifest")
    required_manifest_fields = {
        "schema_version", "subject", "support_count", "support_sha256",
        "handoff_row_count", "handoff_fulltype_sha256", "handoff_input_sha256",
        "authority_contract_bundle_sha256", "candidate_run_receipt_sha256",
    }
    if set(manifest) != required_manifest_fields or manifest.get("schema_version") != "iris-tooltip-t2-handoff-manifest-v1":
        raise TooltipContractError("T2 handoff manifest fields mismatch")
    if not _subject_equal(manifest.get("subject"), expected_subject):
        raise TooltipContractError("T2 handoff manifest subject mismatch")
    if manifest.get("candidate_run_receipt_sha256") != receipt_sha256:
        raise TooltipContractError("T2 handoff manifest receipt binding mismatch")
    if manifest.get("support_count") != FROZEN_SUPPORT_COUNT or manifest.get("support_sha256") != FROZEN_SUPPORT_SHA256:
        raise TooltipContractError("T2 handoff manifest support binding mismatch")
    contract_bundle = subject.get("contract_sha256", {}).get("authority_contract_bundle_sha256")
    if (
        not isinstance(contract_bundle, str)
        or manifest.get("authority_contract_bundle_sha256") != contract_bundle
        or receipt.get("authority_contract_bundle_sha256") != contract_bundle
    ):
        raise TooltipContractError("T2 handoff authority contract bundle mismatch")

    input_path = root / "t2_handoff_input.jsonl"
    rows = _read_jsonl_objects(input_path, "T2 handoff input")
    for row in rows:
        validate_handoff_row(row)
        if row.get("subject_binding_ref") != "subject_binding.json":
            raise TooltipContractError("T2 handoff subject binding reference mismatch")
    fulltypes = [row["full_type"] for row in rows]
    if len(fulltypes) != len(set(fulltypes)):
        raise TooltipContractError("T2 handoff duplicate exact FullType")
    handoff_fulltype_sha256 = fulltype_set_sha256(fulltypes)
    input_sha256 = sha256_file(input_path)
    if (
        len(rows) != FROZEN_SUPPORT_COUNT
        or handoff_fulltype_sha256 != FROZEN_SUPPORT_SHA256
        or manifest.get("handoff_row_count") != len(rows)
        or manifest.get("handoff_fulltype_sha256") != handoff_fulltype_sha256
        or manifest.get("handoff_input_sha256") != input_sha256
        or receipt.get("handoff") != {
            "row_count": len(rows),
            "fulltype_sha256": handoff_fulltype_sha256,
            "input_sha256": input_sha256,
        }
        or receipt.get("support") != {"count": FROZEN_SUPPORT_COUNT, "sha256": FROZEN_SUPPORT_SHA256}
    ):
        raise TooltipContractError("T2 handoff exact-set or hash binding mismatch")
    return expected_subject, closeout, {
        "path": (root / "run_receipt.json").resolve().as_posix(),
        "sha256": receipt_sha256,
    }, {
        "root": root,
        "manifest": manifest,
        "artifact_sha256": {
            "subject_binding.json": sha256_file(subject_path),
            "t2_handoff_input.jsonl": input_sha256,
            "t2_handoff_manifest.json": sha256_file(manifest_path),
        },
    }


def _validate_candidate_closeout(
    repository_root: Path,
    candidate_root: Path,
    expected_receipt_sha256: str,
) -> tuple[dict[str, str], dict[str, Any], dict[str, str], dict[str, Any] | None]:
    root = _require_external(repository_root, candidate_root, "candidate root")
    receipt_path = root / "run_receipt.json"
    receipt_sha256 = _require_hash(receipt_path, expected_receipt_sha256, "candidate run receipt")
    receipt = _load_json_object(receipt_path, "candidate run receipt")
    if receipt.get("schema_version") != "iris-tooltip-t1-run-receipt-v1":
        raise TooltipContractError("candidate run receipt schema mismatch")
    if receipt.get("candidate_mode") == "strict_t2_handoff":
        return _validate_strict_candidate(repository_root, root, receipt, receipt_sha256)
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise TooltipContractError("candidate run receipt artifact binding is missing")
    for name, digest in artifacts.items():
        if not isinstance(name, str) or Path(name).name != name:
            raise TooltipContractError("candidate artifact name is not a direct child")
        _require_hash(root / name, digest, f"candidate artifact {name}")
    subject_path = root / "subject_binding.json"
    _require_hash(subject_path, receipt.get("subject_binding_sha256"), "candidate subject binding")
    subject = _load_json_object(subject_path, "candidate subject binding")
    expected_subject = {"commit": subject.get("commit"), "tree": subject.get("tree")}
    if not all(isinstance(expected_subject[key], str) and len(expected_subject[key]) == 40 for key in ("commit", "tree")):
        raise TooltipContractError("candidate subject identity is incomplete")
    current_subject = git_subject(repository_root)
    validate_execution_subject(current_subject, expected_commit=expected_subject["commit"])
    if current_subject["tree"] != expected_subject["tree"]:
        raise TooltipContractError("candidate subject tree differs from finalizer checkout")
    closeout = _load_json_object(root / "axis_separated_closeout_record.json", "candidate closeout")
    if closeout.get("contract_and_audit_axis") != "partial" or closeout.get("formal_closeout_state") != "implemented_only":
        raise TooltipContractError("candidate closeout must remain partial/implemented_only before canonical gate success")
    progression = _load_json_object(root / "t2_progression_record.json", "candidate T2 progression")
    progression_value = progression.get("T2_FULL_DATA_PROGRESSION")
    if progression_value != receipt.get("T2_FULL_DATA_PROGRESSION") or progression_value != closeout.get("T2_FULL_DATA_PROGRESSION"):
        raise TooltipContractError("candidate T2 progression bindings disagree")
    return expected_subject, closeout, {
        "path": receipt_path.resolve().as_posix(),
        "sha256": receipt_sha256,
    }, None


def _validate_gate_chain(
    repository_root: Path,
    orchestration_path: Path,
    expected_subject: dict[str, str],
) -> dict[str, Any]:
    path = _require_external(repository_root, orchestration_path, "full-gate orchestration receipt")
    payload = _load_json_object(path, "full-gate orchestration receipt")
    if payload.get("schema_version") != "iris-clean-checkout-orchestration-receipt-v1":
        raise TooltipContractError("full-gate orchestration schema mismatch")
    if payload.get("launch_status") != "succeeded" or payload.get("native_exit_code") != 0 or payload.get("receipt_write_status") != "succeeded":
        raise TooltipContractError("full-gate orchestration did not exit 0 successfully")
    if not _subject_equal(payload.get("identity", {}).get("subject"), expected_subject):
        raise TooltipContractError("full-gate orchestration subject mismatch")
    environment = payload.get("environment")
    if not isinstance(environment, dict) or environment.get("configured") is not True or environment.get("restored") is not True:
        raise TooltipContractError("full-gate environment lifecycle is incomplete")
    result_ref = payload.get("result_receipt")
    if not isinstance(result_ref, dict) or result_ref.get("exists") is not True:
        raise TooltipContractError("full-gate result receipt binding is missing")
    result_path = _require_external(repository_root, Path(str(result_ref.get("path"))), "full-gate result receipt")
    result_sha256 = _require_hash(result_path, result_ref.get("sha256"), "full-gate result receipt")
    result = _load_json_object(result_path, "full-gate result receipt")
    if result.get("status") != "PASS" or not _subject_equal(result.get("subject"), expected_subject):
        raise TooltipContractError("full-gate result receipt is not same-subject PASS")
    return {
        "claim_id": payload.get("claim_id"),
        "orchestration_receipt": {"path": path.as_posix(), "sha256": sha256_file(path)},
        "result_receipt": {"path": result_path.as_posix(), "sha256": result_sha256},
    }


def finalize_closeout(
    repository_root: Path,
    candidate_root: Path,
    candidate_run_receipt_sha256: str,
    run_a_orchestration_receipt: Path,
    run_b_orchestration_receipt: Path,
    comparator_receipt: Path,
    output_root: Path,
) -> dict[str, Any]:
    expected_subject, candidate_closeout, candidate_receipt, strict_candidate = _validate_candidate_closeout(
        repository_root, candidate_root, candidate_run_receipt_sha256
    )
    run_a = _validate_gate_chain(repository_root, run_a_orchestration_receipt, expected_subject)
    run_b = _validate_gate_chain(repository_root, run_b_orchestration_receipt, expected_subject)
    if run_a["claim_id"] != run_b["claim_id"]:
        raise TooltipContractError("Run A and Run B claim IDs differ")
    compare_path = _require_external(repository_root, comparator_receipt, "deterministic comparator receipt")
    comparator = _load_json_object(compare_path, "deterministic comparator receipt")
    if comparator.get("schema_version") != "iris-clean-checkout-compare-receipt-v1":
        raise TooltipContractError("deterministic comparator receipt schema mismatch")
    if comparator.get("status") != "succeeded" or comparator.get("native_exit_code") != 0 or comparator.get("receipt_write_status") != "succeeded":
        raise TooltipContractError("deterministic comparator did not exit 0 successfully")
    if comparator.get("claim_id") != run_a["claim_id"] or not _subject_equal(comparator.get("subject"), expected_subject):
        raise TooltipContractError("deterministic comparator claim or subject mismatch")
    compare_environment = comparator.get("environment")
    if not isinstance(compare_environment, dict) or compare_environment.get("configured") is not True or compare_environment.get("restored") is not True:
        raise TooltipContractError("deterministic comparator environment lifecycle is incomplete")
    chains = comparator.get("run_chains")
    if not isinstance(chains, dict):
        raise TooltipContractError("deterministic comparator run-chain binding is missing")
    canonical_hashes: list[str] = []
    for label, gate in (("run_a", run_a), ("run_b", run_b)):
        chain = chains.get(label)
        if not isinstance(chain, dict):
            raise TooltipContractError(f"deterministic comparator {label} binding is missing")
        orchestration_ref = chain.get("orchestration_receipt")
        result_ref = chain.get("inner_run_receipt")
        canonical_ref = chain.get("canonical_result")
        expected_orchestration_ref = {
            **gate["orchestration_receipt"],
            "claim_id": gate["claim_id"],
        }
        if orchestration_ref != expected_orchestration_ref or result_ref != gate["result_receipt"]:
            raise TooltipContractError(f"deterministic comparator {label} receipt binding mismatch")
        if not isinstance(canonical_ref, dict):
            raise TooltipContractError(f"deterministic comparator {label} canonical result binding missing")
        canonical_path = _require_external(repository_root, Path(str(canonical_ref.get("path"))), f"{label} canonical result")
        canonical_hashes.append(_require_hash(canonical_path, canonical_ref.get("sha256"), f"{label} canonical result"))
    if len(set(canonical_hashes)) != 1:
        raise TooltipContractError("Run A and Run B canonical results differ")

    output = _require_external(repository_root, output_root, "final closeout output root")
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise TooltipContractError("final closeout output root must be empty")
    else:
        output.mkdir(parents=True)
    final_record = {
        "schema_version": "iris-tooltip-t1-axis-closeout-v3" if strict_candidate else "iris-tooltip-t1-axis-closeout-v2",
        "contract_and_audit_axis": "complete",
        "formal_closeout_state": "complete",
        "subject": expected_subject,
        "candidate_run_receipt": candidate_receipt,
        "canonical_full_gate": {
            "claim_id": run_a["claim_id"],
            "run_a": run_a,
            "run_b": run_b,
            "deterministic_comparator_receipt": {
                "path": compare_path.as_posix(),
                "sha256": sha256_file(compare_path),
            },
        },
        "validation_ceiling": (
            "offline Tooltip T1 contract/audit, strict 2,280-row T2 handoff, fresh installed CLI, same-subject canonical Run A, Run B, deterministic comparator, and finalizer; no static Tooltip Lua, runtime, visual, T2/T3 implementation, release, or deployment claim"
            if strict_candidate else
            "offline Tooltip T1 contract/audit plus same-subject canonical Run A, Run B, and deterministic comparator; no runtime, visual, release, or upstream-correction completion claim"
        ),
        "T2_FULL_DATA_PROGRESSION": candidate_closeout["T2_FULL_DATA_PROGRESSION"],
        "production_t2_handoff": "present" if strict_candidate else "absent",
        "validated": [
            *candidate_closeout["validated"],
            "same-subject canonical clean-checkout Run A",
            "same-subject canonical clean-checkout Run B",
            "deterministic Run A/Run B comparator",
        ],
        "unvalidated_but_in_scope": [row for row in candidate_closeout["unvalidated_but_in_scope"] if not row.startswith("canonical receipt-bound")],
        "out_of_scope": candidate_closeout["out_of_scope"],
        "non_claims": [
            "no runtime mutation",
            "no T2 static Lua generation",
            "no full Menu parity claim",
            "no upstream correction resolution" if not strict_candidate else "no Tooltip static Lua or T2/T3 implementation claim",
            "no release/deployment readiness claim",
        ],
    }
    if strict_candidate:
        final_record["strict_t2_handoff"] = {
            "support_count": strict_candidate["manifest"]["support_count"],
            "support_sha256": strict_candidate["manifest"]["support_sha256"],
            "handoff_row_count": strict_candidate["manifest"]["handoff_row_count"],
            "candidate_final_bytes_equal": True,
            "artifact_sha256": strict_candidate["artifact_sha256"],
        }
        for name in ("subject_binding.json", "t2_handoff_input.jsonl", "t2_handoff_manifest.json"):
            shutil.copyfile(strict_candidate["root"] / name, output / name)
    final_path = output / "axis_separated_final_closeout_record.json"
    _write_json(final_path, final_record)
    return {
        "contract_and_audit_axis": "complete",
        "formal_closeout_state": "complete",
        "T2_FULL_DATA_PROGRESSION": final_record["T2_FULL_DATA_PROGRESSION"],
        "production_t2_handoff": final_record["production_t2_handoff"],
        "final_root": output.resolve().as_posix(),
        "final_closeout_path": final_path.resolve().as_posix(),
        "final_closeout_sha256": sha256_file(final_path),
    }


def _generation_id(pointer_text: str) -> str:
    match = re.search(r'generation_id\s*=\s*"([^"]+)"', pointer_text)
    if not match:
        raise TooltipContractError("Layer 3 current pointer has no generation_id")
    return match.group(1)


def _english_layer3_keys(repository_root: Path) -> set[str]:
    root = repository_root / "Iris/media/lua/client/Iris/Data/Layer3English"
    pattern = re.compile(r'^\s*\["([^"]+)"\]\s*=')
    keys: set[str] = set()
    for path in sorted(root.glob("Chunk*.lua")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if match:
                keys.add(match.group(1))
    return keys


def _runtime_rightclick_surfaces(repository_root: Path) -> dict[str, dict[str, str]]:
    projection = (repository_root / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua").read_text(encoding="utf-8")
    identity_to_key = dict(re.findall(
        r'^\s*\["([^"]+)"\]\s*=\s*"(Iris_Interaction_[A-Za-z0-9_]+)",\s*$',
        projection,
        re.MULTILINE,
    ))
    localized: dict[str, dict[str, str]] = {}
    by_locale: dict[str, dict[str, str]] = {}
    for locale, path in (("ko", KO_TRANSLATION), ("en", EN_TRANSLATION)):
        text = (repository_root / path).read_text(encoding="utf-8")
        by_locale[locale] = dict(re.findall(
            r'^\s*(Iris_Interaction_[A-Za-z0-9_]+)\s*=\s*"([^"]+)",\s*$',
            text,
            re.MULTILINE,
        ))
    for identity, key in identity_to_key.items():
        if key in by_locale["ko"] and key in by_locale["en"]:
            localized[identity] = {
                "ko": by_locale["ko"][key],
                "en": by_locale["en"][key],
            }
    return localized


def _layer4_candidates(
    row: dict[str, Any],
) -> list[Layer4Candidate]:
    items = row.get("use_cases") or []
    if not isinstance(items, list):
        raise TooltipContractError("Layer 4 items must be an array")
    candidates: list[Layer4Candidate] = []
    for item in items:
        identity = item.get("use_case_id")
        if not isinstance(identity, str):
            identity = ""
        surface = item.get("surface")
        source = "recipe" if surface == "recipe_ui" else "rightclick" if surface == "context_menu" else str(surface)
        if source == "recipe" and "display_by_locale" in item:
            raise TooltipContractError(
                f"{identity}: LAYER4_RECIPE_EMBEDDED_LOCALE_AUTHORITY_CEILING_VIOLATION"
            )
        candidates.append(
            Layer4Candidate(
                interaction_id=identity,
                source=source,
                public_state="public",
                line_kind=str(item.get("line_kind") or "unknown"),
                requirement_only=bool(item.get("requirement_only", False)),
                stable_order_key=item.get("stable_order_key"),
            )
        )
    return candidates


def _runtime_layer4_identities(repository_root: Path) -> dict[str, set[str]]:
    full_type_pattern = re.compile(r'^chunk\["([^"]+)"\]\s*=\s*\{')
    identity_pattern = re.compile(r'label_key\s*=\s*"([^"]+)"')
    result: dict[str, set[str]] = {}
    for path in sorted((repository_root / L4_RUNTIME_ROOT).glob("Chunk*.lua")):
        current: str | None = None
        for line in path.read_text(encoding="utf-8").splitlines():
            full_type_match = full_type_pattern.match(line)
            if full_type_match:
                current = full_type_match.group(1)
                result.setdefault(current, set())
                continue
            identity_match = identity_pattern.search(line)
            if current and identity_match:
                result[current].add(identity_match.group(1))
    if not result:
        raise TooltipContractError("current Layer 4 consumer identity census is empty")
    return result


def _slot_absent(slot_id: str, reason: str, authority_ref: str) -> Slot:
    return Slot(
        slot_id=slot_id,
        semantic_identity=None,
        semantic_state=SemanticSlotState.LEGITIMATE_ABSENCE,
        localized_surfaces={"ko": None, "en": None},
        locale_readiness={
            "ko": LocaleSurfaceReadiness.NOT_APPLICABLE,
            "en": LocaleSurfaceReadiness.NOT_APPLICABLE,
        },
        reason_codes=(reason,),
        authority_ref=authority_ref,
    )


def _slot_correction(slot_id: str, reason: str) -> Slot:
    return Slot(
        slot_id=slot_id,
        semantic_identity=None,
        semantic_state=SemanticSlotState.CORRECTION_REQUIRED,
        localized_surfaces={"ko": None, "en": None},
        locale_readiness={
            "ko": LocaleSurfaceReadiness.CORRECTION_REQUIRED,
            "en": LocaleSurfaceReadiness.CORRECTION_REQUIRED,
        },
        reason_codes=(reason,),
        t2_blocking=True,
    )


def _slot_selected_owner(
    slot_id: str,
    semantic_identity: str,
    localized_surfaces: dict[str, str],
    authority_ref: str,
) -> Slot:
    return Slot(
        slot_id=slot_id,
        semantic_identity=semantic_identity,
        semantic_state=SemanticSlotState.SELECTED,
        localized_surfaces=localized_surfaces,
        locale_readiness={
            "ko": LocaleSurfaceReadiness.READY,
            "en": LocaleSurfaceReadiness.READY,
        },
        authority_ref=authority_ref,
    )


def _slot_selected_layer4(
    slot_id: str,
    candidate: Layer4Candidate,
    recipe_locale_entries: dict[str, dict[str, Any]],
    rightclick_surfaces: dict[str, dict[str, str]],
    lexical_fixture: dict[str, Any],
) -> Slot:
    if candidate.source == "recipe":
        owner_record = recipe_locale_entries.get(candidate.interaction_id)
        surfaces = owner_record.get("localized_surfaces") if isinstance(owner_record, dict) else {}
        authority_ref = owner_record.get("authority_ref") if isinstance(owner_record, dict) else None
    elif candidate.source == "rightclick":
        surfaces = rightclick_surfaces.get(candidate.interaction_id, {})
        authority_ref = "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua#RIGHTCLICK_LABEL_KEYS"
    else:
        surfaces = {}
        authority_ref = None
    normalized = {locale: surfaces.get(locale) for locale in ("ko", "en")}
    surface_reasons = {locale: public_surface_reason(normalized[locale], locale, lexical_fixture) for locale in ("ko", "en")}
    readiness = {locale: LocaleSurfaceReadiness.READY if reason is None else LocaleSurfaceReadiness.CORRECTION_REQUIRED for locale, reason in surface_reasons.items()}
    blocking = any(value is LocaleSurfaceReadiness.CORRECTION_REQUIRED for value in readiness.values())
    reasons = tuple(sorted({reason for reason in surface_reasons.values() if reason is not None}))
    return Slot(
        slot_id=slot_id,
        semantic_identity=candidate.interaction_id,
        semantic_state=SemanticSlotState.SELECTED,
        localized_surfaces=normalized,
        locale_readiness=readiness,
        reason_codes=reasons,
        t2_blocking=blocking,
        authority_ref=authority_ref,
    )


def _correction(
    full_type: str,
    layer: str,
    owner: str,
    reason: str,
    expected: str,
    selected_identity: str | None = None,
    locale: str = "all",
) -> dict[str, Any]:
    return {
        "full_type": full_type,
        "locale": locale,
        "layer": layer,
        "owner": owner,
        "observed_state": reason.lower(),
        "expected_contract": expected,
        "reason_code": reason,
        "selected_identity_ref": selected_identity,
        "t2_blocking": True,
        "correction_acceptance_condition": f"{owner} publishes the required structured {layer} input for this identity",
        "re_audit_condition": "rerun Tooltip T1 on a new exact subject containing the accepted owner correction",
        "subject_binding_ref": "subject_binding.json",
    }


def _source_hashes(repository_root: Path, generation_id: str) -> dict[str, str]:
    paths = [
        ITEM_SOURCE,
        CLASSIFICATIONS,
        OWNER_OUTPUT,
        L3_POINTER,
        L3_INPUT_MANIFEST,
        L3_TOOLTIP_OWNER_INPUT,
        L3_GENERATIONS / generation_id / "generation_descriptor.json",
        L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json",
        L4_OWNER_INPUT,
        L4_RECIPE_LOCALE_OWNER_INPUT,
        KO_TRANSLATION,
        EN_TRANSLATION,
        *MENU_TOOLTIP_SOURCES,
        Path("Iris/_docs/authority/iris_current_authority_manifest.json"),
        Path("Iris/_docs/authority/iris_current_route_index.json"),
        *sorted(
            path.relative_to(repository_root)
            for path in (repository_root / L4_RUNTIME_ROOT).glob("Chunk*.lua")
        ),
    ]
    return {path.as_posix(): sha256_file(repository_root / path) for path in paths}


def _invariance(by_full_type: dict[str, list[Layer4Candidate]]) -> dict[str, Any]:
    base: dict[str, str] = {}
    permuted: dict[str, str] = {}
    selection_fields: list[str] | None = None
    for full_type, candidates in sorted(by_full_type.items()):
        result = verify_invariants(candidates)
        base[full_type] = result["permutation"]["base_selected_identity_sha256"]
        permuted[full_type] = result["permutation"]["permuted_selected_identity_sha256"]
        fields = result["readiness_isolation"]["selection_input_fields"]
        if selection_fields is None:
            selection_fields = fields
        elif selection_fields != fields:
            raise TooltipContractError("IDENTITY_READINESS_FEEDBACK_VIOLATION")
    digest = lambda value: sha256_bytes(canonical_bytes(value))
    identities = {"base": digest(base), "permuted": digest(permuted)}
    if len(set(identities.values())) != 1:
        raise TooltipContractError("IDENTITY_READINESS_FEEDBACK_VIOLATION")
    return {
        "schema_version": "iris-tooltip-layer4-invariance-v2",
        "candidate_full_type_count": len(by_full_type),
        "permutation": {
            "base_selected_identity_sha256": identities["base"],
            "permuted_selected_identity_sha256": identities["permuted"],
            "changed": False,
        },
        "readiness_isolation": {
            "base_selected_identity_sha256": identities["base"],
            "selection_input_fields": selection_fields or [],
            "forbidden_readiness_fields_present": False,
            "locale_readiness_changed_selection": False,
            "menu_evidence_changed_selection": False,
        },
    }


def run_candidate(
    repository_root: Path,
    output_root: Path,
    decision_contract_sha256: str,
    *,
    verify_selection_invariants: bool,
    layer2_menu_relation: Path | None = None,
    strict_production_handoff: bool = False,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    if output_root == repository_root or repository_root in output_root.parents:
        raise TooltipContractError("output root must be repository-external")
    if output_root.exists() and any(output_root.iterdir()):
        raise TooltipContractError("output root must be empty")
    output_root.mkdir(parents=True, exist_ok=True)
    if not verify_selection_invariants:
        raise TooltipContractError("blocked_contract_incompleteness: --verify-invariants is mandatory")
    if strict_production_handoff and layer2_menu_relation is None:
        raise TooltipContractError("strict production handoff requires --layer2-menu-relation")

    # W0: validate the tracked contract template and bind an exact clean subject.
    contract_hashes = validate_contracts(repository_root, decision_contract_sha256)
    subject = git_subject(repository_root)
    validate_execution_subject(subject)
    admission = _d6_admission(repository_root, subject) if strict_production_handoff else {}

    pointer_text = (repository_root / L3_POINTER).read_text(encoding="utf-8")
    generation_id = _generation_id(pointer_text)
    input_hashes_before = _source_hashes(repository_root, generation_id)
    layer2_relation_rows: dict[str, dict[str, Any]] = {}
    layer2_relation_receipt: dict[str, Any] | None = None
    if layer2_menu_relation is not None:
        relation_path = layer2_menu_relation.resolve()
        layer2_relation_rows, layer2_relation_receipt = load_relation(repository_root, relation_path)
        subject["layer2_menu_relation_sha256"] = sha256_file(relation_path)
        subject["layer2_menu_relation_receipt_sha256"] = sha256_file(relation_path.with_name("run_receipt.json"))
    subject["generation_id"] = generation_id
    subject["input_sha256"] = input_hashes_before
    subject["contract_sha256"] = contract_hashes
    subject_identity = {
        "commit": subject["commit"],
        "tree": subject["tree"],
        "generation_id": generation_id,
        "input_sha256": input_hashes_before,
        "contract_sha256": contract_hashes,
    }
    if layer2_relation_receipt is not None:
        subject_identity["layer2_menu_relation_sha256"] = subject["layer2_menu_relation_sha256"]
        subject_identity["layer2_menu_relation_receipt_sha256"] = subject["layer2_menu_relation_receipt_sha256"]
    subject["subject_identity_sha256"] = sha256_bytes(canonical_bytes(subject_identity))

    classifications = parse_classifications(repository_root / CLASSIFICATIONS)
    layer2_validation = validate_owner_output(repository_root)
    layer2_owner_output = load_json(repository_root / OWNER_OUTPUT)
    layer2_owner_rows = {
        row["full_type"]: row
        for row in layer2_owner_output.get("rows", [])
        if isinstance(row, dict) and isinstance(row.get("full_type"), str)
    }
    layer2_display_silence = {
        row["full_type"]: row
        for row in layer2_owner_output.get("layer2_display_silence_entries", [])
        if isinstance(row, dict) and isinstance(row.get("full_type"), str)
    }
    rendered = load_json(repository_root / L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json")
    layer3 = rendered.get("entries")
    if not isinstance(layer3, dict):
        raise TooltipContractError("Layer 3 rendered entries missing")
    layer3_tooltip_owner = load_json(repository_root / L3_TOOLTIP_OWNER_INPUT)
    layer3_tooltip_entries, layer3_tooltip_absences = validate_layer3_owner_output(
        layer3_tooltip_owner,
        expected_generation_id=generation_id,
    )
    descriptions = load_json(repository_root / L4_OWNER_INPUT)
    layer4 = descriptions.get("fulltypes")
    if not isinstance(layer4, dict):
        raise TooltipContractError("Layer 4 fulltypes missing")
    runtime_layer4 = _runtime_layer4_identities(repository_root)
    current_rightclick_surfaces = _runtime_rightclick_surfaces(repository_root)
    recipe_locale_entries = load_recipe_locale_owner_input(repository_root)
    l3_en_keys = _english_layer3_keys(repository_root)

    # W1-A: read-only adjacent-universe census.  No support freeze or selection
    # occurs before the evidence hash is built and the open decisions are closed.
    adjacent_sets = {
        "layer2_classification": set(classifications),
        "layer3_canonical": set(layer3),
        "layer3_public_ko": {key for key, row in layer3.items() if isinstance(row, dict) and bool(row.get("text_ko"))},
        "layer3_public_en": set(l3_en_keys),
        "layer4_owner": set(layer4),
        "layer4_runtime_consumer": set(runtime_layer4),
    }
    census_candidates = {
        full_type: _layer4_candidates(row)
        for full_type, row in layer4.items()
        if isinstance(full_type, str) and isinstance(row, dict)
    }
    eligible_source_shapes: Counter[str] = Counter()
    duplicate_identity_rows = 0
    explicit_stable_keys = 0
    for candidates in census_candidates.values():
        eligible = [
            candidate for candidate in candidates
            if candidate.interaction_id
            and candidate.source in {"recipe", "rightclick"}
            and candidate.public_state == "public"
            and candidate.line_kind == "evidence"
            and not candidate.requirement_only
            and not candidate.interaction_id.startswith("uc.exclusion.")
        ]
        sources = {candidate.source for candidate in eligible}
        shape = "both" if sources == {"recipe", "rightclick"} else "recipe_only" if sources == {"recipe"} else "rightclick_only" if sources == {"rightclick"} else "none"
        eligible_source_shapes[shape] += 1
        identities = [candidate.interaction_id for candidate in eligible]
        duplicate_identity_rows += len(identities) - len(set(identities))
        explicit_stable_keys += sum(bool(candidate.stable_order_key) for candidate in eligible)
    proposed_union = set().union(*adjacent_sets.values())
    set_differences = {
        f"union_without_{name}": len(proposed_union - values)
        for name, values in adjacent_sets.items()
    }
    evidence_records = {
        "P-2": {"evidence_state": "mixed", "observation": "adjacent owner universes differ", "counts": set_differences},
        "P-4": {"evidence_state": "present", "observation": "single-source rows are present", "counts": dict(eligible_source_shapes)},
        "P-5": {"evidence_state": "present" if eligible_source_shapes["both"] else "absent", "observation": "both-source eligible rows census", "count": eligible_source_shapes["both"]},
        "P-6": {"evidence_state": "present" if explicit_stable_keys else "absent", "observation": "explicit stable Layer 4 order keys", "count": explicit_stable_keys},
        "P-7": {"evidence_state": "present" if duplicate_identity_rows else "absent", "observation": "exact duplicate interaction identities", "count": duplicate_identity_rows},
        "P-8": {"evidence_state": "present", "observation": "Layer 3 owner publishes exact single-core Tooltip facts and independently validated explicit absence dispositions", "canonical_count": len(layer3), "tooltip_fact_count": len(layer3_tooltip_entries), "tooltip_absence_count": len(layer3_tooltip_absences), "en_count": len(l3_en_keys)},
        "P-10": {
            "evidence_state": "mixed",
            "observation": (
                "D1 owner output is joined to actual Lua Browser consumer tuples through the D2 candidate relation"
                if layer2_relation_receipt is not None
                else "D1 owner output resolves only evidence-backed rows; independent per-row Menu identity remains absent"
            ),
            "resolved_entry_count": layer2_validation["resolved_entry_count"],
            "remaining_entry_count": layer2_validation["remaining_entry_count"],
        },
    }
    for decision_id, record in evidence_records.items():
        record["decision_id"] = decision_id
        record["subject_identity_sha256"] = subject["subject_identity_sha256"]
    evidence = {
        "schema_version": "iris-tooltip-pre-ratification-decision-evidence-v1",
        "phase": "W1-A_read_only_complete",
        "subject_identity_sha256": subject["subject_identity_sha256"],
        "subject_binding": {"commit": subject["commit"], "tree": subject["tree"], "input_sha256": input_hashes_before},
        "adjacent_universe_counts": {name: len(values) for name, values in adjacent_sets.items()},
        "set_differences": set_differences,
        "records": evidence_records,
        "findings": {
            "layer2_resolved_owner_output": layer2_validation["status"],
            "layer2_independent_menu_consumer_identity": "present_in_d2_candidate_relation" if layer2_relation_receipt is not None else "absent",
            "layer3_single_tooltip_fact_identity_and_surfaces": "present_with_explicit_owner_absence_partition",
            "layer4_explicit_stable_order_key": "present" if explicit_stable_keys else "absent",
            "layer4_current_owner_input": L4_OWNER_INPUT.as_posix(),
            "layer4_current_consumer_identity_route": f"{L4_RUNTIME_ROOT.as_posix()}/Chunk*.lua",
            "renderer_logical_row_limit": 4,
            "embedded_newline_hard_gate": True,
        },
    }
    evidence_sha256 = sha256_bytes(canonical_bytes(evidence))
    decision = load_json(repository_root / AUTHORITY_ROOT / "tooltip_t1_decision_contract.json")
    adopted_open_decisions = ratify_open_decisions(
        decision,
        evidence,
        evidence_sha256=evidence_sha256,
        subject_identity_sha256=subject["subject_identity_sha256"],
    )

    # W1-B: the owner-ratified support predicate is applied only after G1.
    support = sorted(set(classifications) | set(layer3) | set(layer4))
    support_collisions = normalized_collisions(support)
    support_collision_members = {
        full_type
        for members in support_collisions.values()
        for full_type in members
    }
    resolved_support_collision_members, d5_applicability = resolved_collision_members(repository_root)
    unresolved_support_collision_members = collision_correction_members(
        support_collisions,
        resolved_support_collision_members,
    )
    by_full_type = {
        full_type: _layer4_candidates(layer4.get(full_type, {}))
        for full_type in support
    }
    invariance = _invariance(by_full_type)

    audit_rows: list[dict[str, Any]] = []
    audited_slots: dict[str, tuple[Slot, ...]] = {}
    corrections: list[dict[str, Any]] = []
    candidate_dispositions: Counter[str] = Counter()
    source_universe: Counter[str] = Counter()
    absence_distribution: Counter[str] = Counter()
    parity_distribution: Counter[str] = Counter()
    reason_registry = load_json(repository_root / AUTHORITY_ROOT / "tooltip_readiness_reason_registry.json")
    known_reasons = {row["code"] for row in reason_registry.get("reasons", [])}
    reason_owners = {row["code"]: row["owner"] for row in reason_registry.get("reasons", [])}
    fixture_expectations = load_json(repository_root / "Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json")
    lexical_fixture = fixture_expectations.get("lexical_guard")
    if not isinstance(lexical_fixture, dict):
        raise TooltipContractError("tracked lexical guard fixture missing")

    for full_type in support:
        slots: list[Slot] = []
        correction_start = len(corrections)
        # Exact case-sensitive identities remain in the denominator, while a
        # normalized collision remains an explicit support-owner correction.
        if full_type in unresolved_support_collision_members:
            corrections.append(_correction(
                full_type,
                "support",
                "Iris presentation-contract owner",
                "SUPPORT_NORMALIZED_COLLISION",
                "explicit owner disposition preserving both exact case-sensitive FullType identities",
            ))
        # P-10: consume only the independently validated D1 owner output. Raw
        # tags remain census evidence and are never resolved by this consumer.
        layer2_owner_row = layer2_owner_rows.get(full_type)
        if isinstance(layer2_owner_row, dict) and layer2_owner_row.get("terminal_state") == "resolved":
            surface = layer2_title_surfaces(layer2_owner_row)
            slots.append(Slot(
                "S1",
                layer2_owner_row["classification_identity"],
                SemanticSlotState.SELECTED,
                {"ko": surface["ko"], "en": surface["en"]},
                {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY},
                authority_ref=layer2_owner_row["classification_authority_ref"],
            ))
        elif full_type in layer2_display_silence:
            silence_row = layer2_display_silence[full_type]
            slots.append(_slot_absent(
                "S1",
                silence_row["display_silence_reason"],
                f"{RESOLUTION_CONTRACT.as_posix()}#successor_amendment",
            ))
            absence_distribution[
                "layer2|locale=all|reason="
                f"{silence_row['display_silence_reason']}|authority={RESOLUTION_CONTRACT.as_posix()}"
            ] += 1
        else:
            raise TooltipContractError(f"Layer 2 applicability partition missing: {full_type}")
        layer2_relation_row = layer2_relation_rows.get(full_type)
        if isinstance(layer2_owner_row, dict):
            layer2_parity = (
                MenuParityStatus.VERIFIED
                if isinstance(layer2_relation_row, dict) and layer2_relation_row.get("disposition") == "verified"
                else MenuParityStatus.CORRECTION_REQUIRED
            )
        else:
            layer2_parity = (
                MenuParityStatus.NOT_APPLICABLE
                if isinstance(layer2_relation_row, dict) and layer2_relation_row.get("disposition") == "not_applicable"
                else MenuParityStatus.CORRECTION_REQUIRED
            )
        if layer2_parity is MenuParityStatus.CORRECTION_REQUIRED:
            corrections.append(_correction(
                full_type, "cross-layer", "Menu consumer owner", "PARITY_AUTHORITY_RELATION_MISSING",
                "actual Lua Browser consumer tuple matching the exact D1 Layer 2 disposition",
            ))

        l3 = layer3.get(full_type)
        role_material = l3.get("role_material") if isinstance(l3, dict) else None
        core_ids_value = role_material.get("core_source_fact_ids") if isinstance(role_material, dict) else None
        valid_core_ids = isinstance(core_ids_value, list) and all(isinstance(value, str) and value for value in core_ids_value)
        core_ids = list(core_ids_value) if valid_core_ids else []
        owner_absence = layer3_tooltip_absences.get(full_type)
        l3_proof = f"{(L3_GENERATIONS / generation_id / 'dvf_3_3_rendered.json').as_posix()}#entries/{full_type}/role_material/core_source_fact_ids"
        if owner_absence is not None and isinstance(l3, dict):
            slots.append(_slot_correction("S2", "DVF_TOOLTIP_FACT_IDENTITY_MISSING"))
            corrections.append(_correction(
                full_type, "layer3", "DVF owner", "DVF_TOOLTIP_FACT_IDENTITY_MISSING",
                "one non-conflicting owner disposition for the exact current Layer 3 identity",
            ))
        elif isinstance(l3, dict) and isinstance(role_material, dict) and valid_core_ids and not core_ids:
            slots.append(_slot_absent("S2", "DVF_CORE_DESCRIPTION_ABSENCE_PROVED", l3_proof))
            absence_distribution[f"layer3|locale=all|reason=DVF_CORE_DESCRIPTION_ABSENCE_PROVED|authority={(L3_GENERATIONS / generation_id / 'dvf_3_3_rendered.json').as_posix()}"] += 1
        elif isinstance(l3, dict) and isinstance(role_material, dict) and valid_core_ids:
            owner_fact = layer3_tooltip_entries.get(full_type)
            surfaces = owner_fact.get("localized_surfaces") if isinstance(owner_fact, dict) else None
            owner_fact_ready = (
                len(core_ids) == 1
                and isinstance(owner_fact, dict)
                and owner_fact.get("fact_id") == core_ids[0]
                and owner_fact.get("fact_kind") == "core_description"
                and owner_fact.get("source_fact_ids") == core_ids
                and owner_fact.get("upstream_readiness") == "owner_approved"
                and owner_fact.get("tooltip_eligibility") == "eligible"
                and isinstance(owner_fact.get("source_ref"), str)
                and bool(owner_fact.get("source_ref"))
                and isinstance(owner_fact.get("authority_ref"), str)
                and bool(owner_fact.get("authority_ref"))
                and isinstance(surfaces, dict)
                and set(surfaces) == {"ko", "en"}
                and all(isinstance(value, str) and value and "\n" not in value and "\r" not in value for value in surfaces.values())
            )
            if owner_fact_ready:
                slots.append(_slot_selected_owner(
                    "S2",
                    str(owner_fact["fact_id"]),
                    {"ko": str(surfaces["ko"]), "en": str(surfaces["en"])},
                    f"{L3_TOOLTIP_OWNER_INPUT.as_posix()}#entries/{full_type}",
                ))
            else:
                slots.append(_slot_correction("S2", "DVF_TOOLTIP_FACT_IDENTITY_MISSING"))
                corrections.append(_correction(
                    full_type, "layer3", "DVF owner", "DVF_TOOLTIP_FACT_IDENTITY_MISSING",
                    "one owner-approved core-description fact identity with complete KO/EN single-line surfaces",
                ))
        elif isinstance(owner_absence, dict):
            absence_proof = f"{L3_TOOLTIP_OWNER_INPUT.as_posix()}#absence_entries/{full_type}"
            slots.append(_slot_absent("S2", str(owner_absence["absence_reason_code"]), absence_proof))
            absence_distribution[f"layer3|locale=all|reason={owner_absence['absence_reason_code']}|authority={L3_TOOLTIP_OWNER_INPUT.as_posix()}"] += 1
        else:
            slots.append(_slot_correction("S2", "DVF_OWNER_ROW_MISSING"))
            corrections.append(_correction(
                full_type, "layer3", "DVF owner", "DVF_OWNER_ROW_MISSING",
                "owner disposition proving legitimate absence or an approved Tooltip fact",
            ))

        selected, dispositions = select_layer4(by_full_type[full_type])
        identity_defect = False
        for result in dispositions:
            candidate_dispositions[result.disposition] += 1
            if result.disposition == "correction_missing_identity":
                identity_defect = True
                corrections.append(_correction(
                    full_type, "layer4", "QG identity owner", "QG_MISSING_IDENTITY",
                    "stable public interaction identity",
                ))
        eligible_sources = {
            result.candidate.source for result in dispositions
            if result.disposition in {"selected", "excluded_capacity", "excluded_exact_duplicate_identity"}
        }
        selected_sources = {row.source for row in selected}
        eligible_shape = "both" if eligible_sources == {"recipe", "rightclick"} else "recipe_only" if eligible_sources == {"recipe"} else "rightclick_only" if eligible_sources == {"rightclick"} else "none"
        selected_shape = "both" if selected_sources == {"recipe", "rightclick"} else "recipe_only" if selected_sources == {"recipe"} else "rightclick_only" if selected_sources == {"rightclick"} else "none"
        source_universe[f"eligible:{eligible_shape}"] += 1
        source_universe[f"selected:{selected_shape}"] += 1
        source_equivalence_violation = int(eligible_shape == "both" and selected_shape != "both")
        l4_absence_proof = f"{L4_OWNER_INPUT.as_posix()}#fulltypes/{full_type}/eligible_public_interactions=0"
        for index, slot_id in enumerate(("S3", "S4")):
            if index >= len(selected):
                if identity_defect:
                    slots.append(_slot_correction(slot_id, "QG_MISSING_IDENTITY"))
                else:
                    slots.append(_slot_absent(slot_id, "QG_NO_SELECTED_PUBLIC_INTERACTION", l4_absence_proof))
                    absence_distribution[f"layer4|locale=all|slot={slot_id}|reason=QG_NO_SELECTED_PUBLIC_INTERACTION|authority={L4_OWNER_INPUT.as_posix()}"] += 1
                continue
            candidate = selected[index]
            slot = _slot_selected_layer4(
                slot_id,
                candidate,
                recipe_locale_entries,
                current_rightclick_surfaces,
                lexical_fixture,
            )
            slots.append(slot)
            if slot.t2_blocking:
                for locale in ("ko", "en"):
                    if slot.locale_readiness[locale] is LocaleSurfaceReadiness.CORRECTION_REQUIRED:
                        resolved_surfaces = (
                            recipe_locale_entries.get(candidate.interaction_id, {}).get("localized_surfaces", {})
                            if candidate.source == "recipe"
                            else current_rightclick_surfaces.get(candidate.interaction_id, {})
                        )
                        reason = public_surface_reason(resolved_surfaces.get(locale), locale, lexical_fixture)
                        correction_reason = reason or "LOCALE_SELECTED_SURFACE_MISSING"
                        expected_surface_contract = (
                            "exact selected Recipe identity in the separate QG locale owner output with an explicit KO/EN pair"
                            if candidate.source == "recipe"
                            else "exact selected Right-click identity in the existing translation route with an explicit KO/EN pair"
                        )
                        corrections.append(_correction(
                            full_type, "layer4", reason_owners[correction_reason], correction_reason,
                            expected_surface_contract,
                            selected_identity=candidate.interaction_id,
                            locale=locale,
                        ))

        runtime_identities = runtime_layer4.get(full_type, set())
        missing_consumer_identities = [candidate.interaction_id for candidate in selected if candidate.interaction_id not in runtime_identities]
        for identity in missing_consumer_identities:
            corrections.append(_correction(
                full_type, "layer4-menu", "Menu consumer owner", "PARITY_AUTHORITY_RELATION_MISSING",
                "selected Layer 4 identity present in the current Browser/Menu-consumed runtime identity set",
                selected_identity=identity,
            ))
        parity = {
            "layer2": layer2_parity,
            "layer3": MenuParityStatus.NOT_APPLICABLE
            if slots[1].semantic_state is SemanticSlotState.LEGITIMATE_ABSENCE
            else MenuParityStatus.UNVERIFIED
            if slots[1].semantic_state is SemanticSlotState.SELECTED
            else MenuParityStatus.CORRECTION_REQUIRED,
            "layer4": classify_menu_relation((candidate.interaction_id for candidate in selected), runtime_identities),
        }
        for layer, status in parity.items():
            parity_distribution[f"{layer}:{status.value}"] += 1
        ko_count = sum(slot.displayable("ko") for slot in slots)
        en_count = sum(slot.displayable("en") for slot in slots)
        t2_blocking = any(slot.t2_blocking for slot in slots)
        parity_view: dict[str, dict[str, Any]] = {}
        for layer, status in parity.items():
            authority_relation_ref = None
            independent_consumer_evidence_ref = None
            if layer == "layer2" and status in {MenuParityStatus.VERIFIED, MenuParityStatus.NOT_APPLICABLE}:
                authority_relation_ref = f"{OWNER_OUTPUT.as_posix()} -> D2 layer2_menu_consumer_relation.jsonl#{full_type}"
                independent_consumer_evidence_ref = f"{PROJECTION_BUILDER.as_posix()} via {HARNESS.as_posix()}"
            elif layer == "layer3" and status is MenuParityStatus.UNVERIFIED:
                authority_relation_ref = (
                    f"{(L3_GENERATIONS / generation_id / 'dvf_3_3_rendered.json').as_posix()}#entries/{full_type}"
                    " -> Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"
                    " -> Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua#get"
                    " -> Iris/media/lua/client/Iris/Data/layer3_renderer.lua#getText"
                    " -> Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua#layer3Payload"
                )
            elif layer == "layer4" and selected:
                authority_relation_ref = f"{L4_OWNER_INPUT.as_posix()} -> {L4_RUNTIME_ROOT.as_posix()}/Chunk*.lua"
                independent_consumer_evidence_ref = "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua#label_key"
            parity_view[layer] = {
                "status": status.value,
                "authority_relation_ref": authority_relation_ref,
                "independent_consumer_evidence_ref": independent_consumer_evidence_ref,
                "owner": "Menu consumer owner",
                "re_audit_condition": "T3 independent Menu consumer fact-identity observation" if status is MenuParityStatus.UNVERIFIED else "new exact owner-corrected subject",
            }
        row_reasons = {reason for slot in slots for reason in slot.reason_codes}
        if MenuParityStatus.UNVERIFIED in parity.values():
            row_reasons.add("PARITY_CONSUMER_EVIDENCE_UNVERIFIED")
        row_corrections = corrections[correction_start:]
        row_reasons.update(correction["reason_code"] for correction in row_corrections)
        row_owners = {correction["owner"] for correction in row_corrections}
        for slot in slots:
            if slot.semantic_state is SemanticSlotState.LEGITIMATE_ABSENCE:
                row_owners.add(
                    "Classification owner" if slot.slot_id == "S1"
                    else "DVF owner" if slot.slot_id == "S2"
                    else "QG owner"
                )
        if MenuParityStatus.UNVERIFIED in parity.values():
            row_owners.add("Menu consumer owner")
        correction_blocking = any(correction["t2_blocking"] for correction in row_corrections)
        t2_blocking = t2_blocking or correction_blocking
        row = {
            "full_type": full_type,
            "support_state": "supported",
            "support_rule_id": "current-owner-fulltype-union-v1",
            "classification": {
                "raw_membership_present": full_type in classifications,
                "raw_tag_count": len(classifications.get(full_type, ())),
                "layer2_applicability": "layer2_applicable" if isinstance(layer2_owner_row, dict) else "layer2_display_silence",
                "display_silence_reason": layer2_display_silence.get(full_type, {}).get("display_silence_reason"),
                "resolved_identity": layer2_owner_row.get("classification_identity") if isinstance(layer2_owner_row, dict) else None,
                "terminal_state": layer2_owner_row.get("terminal_state") if isinstance(layer2_owner_row, dict) else "layer2_display_silence",
                "authority_ref": layer2_owner_row.get("classification_authority_ref") if isinstance(layer2_owner_row, dict) else f"{RESOLUTION_CONTRACT.as_posix()}#successor_amendment",
                "provenance_ref": layer2_owner_row.get("classification_provenance_ref") if isinstance(layer2_owner_row, dict) else None,
                "menu_consumer_identity_ref": (
                    f"D2 layer2_menu_consumer_relation.jsonl#{full_type}"
                    if layer2_parity is MenuParityStatus.VERIFIED else None
                ),
            },
            "layer3": {
                "owner_row_present": isinstance(l3, dict) or isinstance(owner_absence, dict),
                "owner_fact_row_present": full_type in layer3_tooltip_entries,
                "owner_absence_row_present": isinstance(owner_absence, dict),
                "core_source_fact_ids": list(core_ids),
                "approved_tooltip_fact_id": slots[1].semantic_identity if slots[1].semantic_state is SemanticSlotState.SELECTED else None,
                "ko_public_body_present": bool(isinstance(l3, dict) and l3.get("text_ko")),
                "en_public_key_present": full_type in l3_en_keys,
            },
            "recipe_candidates": [
                {"interaction_id": result.candidate.interaction_id, "disposition": result.disposition}
                for result in dispositions if result.candidate.source == "recipe"
            ],
            "rightclick_candidates": [
                {"interaction_id": result.candidate.interaction_id, "disposition": result.disposition}
                for result in dispositions if result.candidate.source == "rightclick"
            ],
            "layer4_selected": [
                {"interaction_id": candidate.interaction_id, "source": candidate.source, "slot_id": ("S3", "S4")[index]}
                for index, candidate in enumerate(selected)
            ],
            "layer4_source_equivalence": {
                "eligible_shape": eligible_shape,
                "selected_shape": selected_shape,
                "violation": source_equivalence_violation,
                "owner_input_ref": L4_OWNER_INPUT.as_posix(),
                "consumer_identity_ref": f"{L4_RUNTIME_ROOT.as_posix()}/Chunk*.lua",
            },
            "ko_slot_count": ko_count,
            "en_slot_count": en_count,
            "semantic_slot_states": {slot.slot_id: slot.semantic_state.value for slot in slots},
            "ko_readiness": {slot.slot_id: slot.locale_readiness["ko"].value for slot in slots},
            "en_readiness": {slot.slot_id: slot.locale_readiness["en"].value for slot in slots},
            "overall_readiness": "correction_required" if t2_blocking else "ready",
            "menu_parity_by_layer": parity_view,
            "owner": sorted(row_owners),
            "reason_codes": sorted(row_reasons),
            "t2_blocking": t2_blocking,
            "slots": [slot.to_dict() for slot in slots],
            "subject": "subject_binding.json",
        }
        audit_rows.append(row)
        audited_slots[full_type] = tuple(slots)

    progression, blocker_by_owner = build_progression_record(corrections, input_hashes_before)
    universe_metrics = validate_whole_universe(set(support), audit_rows)
    input_hashes_after = _source_hashes(repository_root, generation_id)
    source_mutation = source_mutation_count(input_hashes_before, input_hashes_after)
    correction_metrics = correction_completeness_metrics(corrections, reason_owners)
    d5_target_correction_rows = [
        row["full_type"] for row in corrections
        if row.get("reason_code") == "SUPPORT_NORMALIZED_COLLISION" and row.get("full_type") in TARGETS
    ]
    d5_identity_metrics = exact_identity_metrics(
        support,
        (row["full_type"] for row in audit_rows),
        support_collisions.get("base.lemongrass", ()),
        d5_target_correction_rows,
    )
    zero_metrics = {
        **universe_metrics,
        **correction_metrics,
        "raw_semantic_inference_path": int(load_json(repository_root / AUTHORITY_ROOT / "layer2_tooltip_input_contract.json").get("raw_tag_resolution_allowed") is not False),
        "locale_dependent_reselection": int(load_json(repository_root / AUTHORITY_ROOT / "tooltip_locale_menu_parity_contract.json").get("locale_dependent_reselection_allowed") is not False),
        "cross_locale_fallback": int(load_json(repository_root / AUTHORITY_ROOT / "tooltip_locale_menu_parity_contract.json").get("cross_locale_fallback_allowed") is not False),
        "menu_parity_unclassified": sum(not isinstance(row.get("menu_parity_by_layer"), dict) or set(row["menu_parity_by_layer"]) != {"layer2", "layer3", "layer4"} for row in audit_rows),
        "menu_owner_output_self_comparison": menu_owner_output_self_comparison_count(layer3_tooltip_entries),
        "mock_consumer_product_decision": 0,
        "progression_unknown_blocking_cause_owner": 0,
        "source_equivalence_contract_violation": sum(row["layer4_source_equivalence"]["violation"] for row in audit_rows),
        "supported_row_removed_for_readiness_defect": 0,
        "layer4_selection_changed_by_locale_readiness": int(invariance["readiness_isolation"]["locale_readiness_changed_selection"]),
        "layer4_selection_changed_by_menu_evidence": int(invariance["readiness_isolation"]["menu_evidence_changed_selection"]),
        "layer4_recipe_embedded_locale_authority_ceiling_violation": 0,
        "source_mutation": source_mutation,
        **{f"d5_{name}": value for name, value in d5_identity_metrics.items()},
    }
    nonzero_required = {name: value for name, value in zero_metrics.items() if value != 0}
    if nonzero_required:
        raise TooltipContractError(f"whole-universe invariant failure: {nonzero_required}")
    summary = {
        "schema_version": "iris-tooltip-support-universe-summary-v1",
        "support_predicate": "current-owner-fulltype-union-v1",
        "support_count": len(support),
        "audited_supported_count": len(audit_rows),
        "adjacent_universes": {
            "layer2_classification": len(classifications),
            "layer3_canonical": len(layer3),
            "layer3_public_ko": sum(bool(row.get("text_ko")) for row in layer3.values() if isinstance(row, dict)),
            "layer3_public_en": len(l3_en_keys),
            "layer4_owner": len(layer4),
            "layer4_runtime_consumer": len(runtime_layer4),
        },
        "set_differences": {
            "support_without_layer2": len(set(support) - set(classifications)),
            "support_without_layer3": len(set(support) - set(layer3)),
            "support_without_layer4": len(set(support) - set(layer4)),
        },
        "candidate_disposition": dict(sorted(candidate_dispositions.items())),
        "normalized_full_type_collisions": {key: list(rows) for key, rows in sorted(support_collisions.items())},
        "source_distribution": dict(sorted(source_universe.items())),
        "legitimate_absence_distribution": dict(sorted(absence_distribution.items())),
        "menu_parity_distribution": dict(sorted(parity_distribution.items())),
        "t2_blocker_by_owner": blocker_by_owner,
        "metrics": zero_metrics,
    }
    inventory = {
        "schema_version": "iris-tooltip-input-authority-inventory-v1",
        "subject_binding_ref": "subject_binding.json",
        "paths": {path: {"sha256": digest, "role": "read_only_current_input"} for path, digest in input_hashes_before.items()},
        "layer2_owner_route": f"T1-D1 isolated candidate {OWNER_OUTPUT.as_posix()} status={layer2_validation['status']}; D2 candidate relation={'present' if layer2_relation_receipt is not None else 'absent'}; current ecosystem adoption remains pending_T1_D6",
        "layer3_owner_route": f"current fact/explicit-absence owner projection {L3_TOOLTIP_OWNER_INPUT.as_posix()}; DVF fact identity/readiness is separate from Menu parity evidence",
        "layer4_owner_route": f"current owner data {L4_OWNER_INPUT.as_posix()} supplies public identities; selected Recipe locale readiness resolves post-selection through {L4_RECIPE_LOCALE_OWNER_INPUT.as_posix()}; reproduction baseline is not consumed",
        "layer4_current_rightclick_locale_route": "current Browser interaction projection identity-to-translation-key relation plus exact Iris_ko/Iris_en translations",
        "menu_consumer_evidence_route": f"Layer 4 current runtime {L4_RUNTIME_ROOT.as_posix()}/Chunk*.lua label_key identities are independently consumed by IrisBrowserInteractionProjection.lua; Layer 3 has only the shared current-generation FullType route through IrisItemDetailModelAssembler.lua and remains unverified pending independent fact-identity evidence",
        "tooltip_runtime_route": "read_only_non_verdict_baseline",
    }
    fixture_result = {
        "schema_version": "iris-tooltip-contract-fixture-result-v1",
        "expectations_sha256": sha256_bytes(canonical_bytes(fixture_expectations)),
        "slot_order_match": fixture_expectations.get("slot_order") == ["S1", "S2", "S3", "S4"],
        "progression_match": fixture_expectations.get("blocked_progression") == T2Progression.UPSTREAM.value,
        "recipe_locale_lookup_match": fixture_expectations.get("recipe_locale_lookup_stage") == "post_selected_identity_freeze",
        "selection_candidate_fields_match": fixture_expectations.get("selection_candidate_forbidden_fields") == ["localized_surfaces", "menu_consumer_identity_ref"],
        "self_seeded_from_audit": False,
    }
    if not all(
        fixture_result[key]
        for key in (
            "slot_order_match",
            "progression_match",
            "recipe_locale_lookup_match",
            "selection_candidate_fields_match",
        )
    ):
        raise TooltipContractError("tracked contract fixture mismatch")

    if strict_production_handoff:
        return _strict_candidate_result(
            output_root,
            subject,
            contract_hashes,
            admission,
            support,
            audited_slots,
            corrections,
            progression,
            blocker_by_owner,
            layer2_relation_rows,
        )

    _write_json(output_root / "subject_binding.json", subject)
    _write_jsonl(output_root / "tooltip_support_universe_census.jsonl", (
        {
            "full_type": full_type,
            "support_state": "supported",
            "inclusion_rule_id": "current-owner-fulltype-union-v1",
            "source_authority_ref": [
                name for name, universe in (("layer2", classifications), ("layer3", layer3), ("layer4", layer4)) if full_type in universe
            ],
            "subject_binding": "subject_binding.json",
        }
        for full_type in support
    ))
    _write_json(output_root / "tooltip_support_universe_summary.json", summary)
    d5_target_corrections = sorted(d5_target_correction_rows)
    d5_raw_members = summary["normalized_full_type_collisions"].get("base.lemongrass", [])
    _write_json(output_root / "d5_owner_disposition_validation_report.json", {
        "schema_version": "iris-tooltip-t1-d5-owner-disposition-validation-v1",
        "authority_ref": "Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.json",
        "authority_binding_valid": True,
        "owner_semantic_judgment_correctness_validated": False,
    })
    _write_json(output_root / "d5_disposition_applicability_report.json", d5_applicability)
    _write_json(output_root / "d5_post_disposition_support_set.json", {
        "schema_version": "iris-tooltip-t1-d5-post-disposition-support-set-v1",
        "support_count": len(support),
        "support_sha256": sha256_bytes(canonical_bytes(support)),
        "target_exact_set": sorted(set(TARGETS) & set(support)),
    })
    _write_json(output_root / "d5_raw_collision_observation.json", {
        "schema_version": "iris-tooltip-t1-d5-raw-collision-observation-v1",
        "normalized_diagnostic_key": "base.lemongrass",
        "exact_members": d5_raw_members,
        "detector_preserved": True,
    })
    _write_json(output_root / "d5_closure_provenance.json", {
        "schema_version": "iris-tooltip-t1-d5-closure-provenance-v1",
        "selected": "owner_disposition_reconciliation" if d5_applicability["applicable"] else None,
        "forbidden_counts": {
            "detector_disable": 0,
            "reason_code_removal": 0,
            "pre_owner_denominator_exclusion": 0,
            "unsupported_normalized_merge": 0,
        },
    })
    _write_json(output_root / "d5_stage_exact_key_sets_after.json", {
        "schema_version": "iris-tooltip-t1-d5-stage-exact-key-sets-v1",
        "support": sorted(set(TARGETS) & set(support)),
        "readiness": sorted(row["full_type"] for row in audit_rows if row["full_type"] in TARGETS),
        "raw_collision_observation": d5_raw_members,
        "support_normalized_collision_correction": d5_target_corrections,
        "t2_blocking_support_normalized_collision": sorted(
            row["full_type"] for row in corrections
            if row.get("reason_code") == "SUPPORT_NORMALIZED_COLLISION"
            and row.get("t2_blocking") is True
            and row.get("full_type") in TARGETS
        ),
    })
    _write_json(output_root / "d5_exact_identity_preservation_report.json", {
        "schema_version": "iris-tooltip-t1-d5-exact-identity-preservation-v1",
        "target_exact_set": list(TARGETS),
        "support_target_exact_set": sorted(set(TARGETS) & set(support)),
        "raw_collision_target_exact_set": d5_raw_members,
        "correction_target_exact_set": d5_target_corrections,
        **d5_identity_metrics,
    })
    _write_json(output_root / "current_tooltip_input_authority_inventory.json", inventory)
    _write_json(output_root / "pre_ratification_decision_evidence.json", evidence)
    adoption_paths = [
        Path("docs/DECISIONS.md"), Path("docs/ARCHITECTURE.md"), Path("docs/ROADMAP.md"),
        Path("docs/iris_tooltip_t1_display_contract_policy.md"),
    ]
    _write_json(output_root / "decision_adoption_receipt.json", {
        "schema_version": "iris-tooltip-t1-decision-adoption-receipt-v1",
        "owner_ratification_source": "user_prompt_preapproval_2026-08-27",
        "decision_contract_sha256": decision_contract_sha256,
        "contract_schema_sha256": contract_hashes,
        "adoption_document_sha256": {path.as_posix(): sha256_file(repository_root / path) for path in adoption_paths},
        "pre_ratification_evidence_sha256": evidence_sha256,
        "subject_identity_sha256": subject["subject_identity_sha256"],
        "open_decision_adoptions": adopted_open_decisions,
        "phase_order": ["W0", "W1-A", "G1-A/B/C", "W1-B"],
        "formal_validation_ceiling": "implemented_only_until_required_focused_candidate_and_full_gate_evidence_exit_0",
        "status": "same_subject_owner_ratified",
    })
    _write_jsonl(output_root / "contract_fixture_expectations.jsonl", [fixture_expectations])
    _write_json(output_root / "contract_fixture_result.json", fixture_result)
    _write_json(output_root / "layer4_invariance_result.json", invariance)
    _write_jsonl(output_root / "tooltip_readiness_manifest.jsonl", audit_rows)
    _write_jsonl(output_root / "upstream_correction_ledger.jsonl", corrections)
    _write_json(output_root / "t2_progression_record.json", progression)
    _write_json(output_root / "bounded_validation_report.json", {
        "schema_version": "iris-tooltip-t1-bounded-validation-report-v1",
        "whole_universe_equation": len(support) == len(audit_rows),
        "zero_metrics": zero_metrics,
        "invariants_verified": True,
        "runtime_validation_claimed": False,
    })
    _write_json(
        output_root / "axis_separated_closeout_record.json",
        candidate_closeout_record(
            progression["T2_FULL_DATA_PROGRESSION"],
            layer2_relation_complete=layer2_relation_receipt is not None,
        ),
    )

    if source_mutation:
        raise TooltipContractError("blocked_source_mutation")
    artifacts = {
        path.name: sha256_file(path)
        for path in sorted(output_root.iterdir())
        if path.name != "run_receipt.json"
    }
    receipt = {
        "schema_version": "iris-tooltip-t1-run-receipt-v1",
        "subject_binding_sha256": sha256_file(output_root / "subject_binding.json"),
        "artifacts": artifacts,
        "T2_FULL_DATA_PROGRESSION": progression["T2_FULL_DATA_PROGRESSION"],
        "source_mutation": 0,
    }
    _write_json(output_root / "run_receipt.json", receipt)
    return {
        "support_count": len(support),
        "correction_count": len(corrections),
        "progression": progression["T2_FULL_DATA_PROGRESSION"],
        "run_receipt_sha256": sha256_file(output_root / "run_receipt.json"),
    }
