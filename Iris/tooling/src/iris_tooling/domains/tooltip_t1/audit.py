from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any, Iterable

from .contract import (
    AUTHORITY_ROOT,
    canonical_bytes,
    git_subject,
    load_json,
    parse_classifications,
    sha256_bytes,
    sha256_file,
    ratify_open_decisions,
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
)
from .projection import Layer4Candidate, select_layer4, verify_invariants


L3_POINTER = Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua")
L3_GENERATIONS = Path("Iris/media/lua/client/Iris/Data/IrisLayer3Generations")
L3_INPUT_MANIFEST = Path("Iris/build/description/v2/data/dvf_3_3_input_manifest.json")
CLASSIFICATIONS = Path("Iris/media/lua/client/Iris/Data/IrisClassifications.lua")
L4_OWNER_INPUT = Path("Iris/build/description/v2/data/upstream_usecases_by_fulltype.json")
L4_RUNTIME_ROOT = Path("Iris/media/lua/client/Iris/Data/UseCaseDescriptions")
KO_TRANSLATION = Path("Iris/media/lua/shared/translate/ko/Iris_ko.txt")
EN_TRANSLATION = Path("Iris/media/lua/shared/translate/en/Iris_en.txt")
MENU_TOOLTIP_SOURCES = (
    Path("Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua"),
    Path("Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua"),
    Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua"),
    Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua"),
    Path("Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua"),
    Path("Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua"),
)


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


def candidate_closeout_record(progression: T2Progression | str) -> dict[str, Any]:
    progression_value = progression.value if isinstance(progression, T2Progression) else progression
    return {
        "schema_version": "iris-tooltip-t1-axis-closeout-v1",
        "contract_and_audit_axis": "partial",
        "T2_FULL_DATA_PROGRESSION": progression_value,
        "formal_closeout_state": "implemented_only",
        "validation_ceiling": "candidate and offline audit only; canonical full-gate Run A/Run B and deterministic comparator exit-0 evidence is not yet bound",
        "validated": ["candidate contract/schema audit", "whole-universe offline audit", "deterministic Layer 4 identity selection", "Layer 4 current consumer identity subset"],
        "unvalidated_but_in_scope": ["canonical receipt-bound full gate and deterministic comparator", "Layer 2 Menu parity where owner-resolved identity evidence is unavailable", "Layer 3 Menu parity for rows lacking approved Tooltip fact identity"],
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


def normalized_collisions(values: Iterable[str]) -> dict[str, tuple[str, ...]]:
    buckets: dict[str, list[str]] = {}
    for value in values:
        buckets.setdefault(value.lower(), []).append(value)
    return {
        key: tuple(sorted(rows))
        for key, rows in buckets.items()
        if len(set(rows)) > 1
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


def _validate_candidate_closeout(
    repository_root: Path,
    candidate_root: Path,
    expected_receipt_sha256: str,
) -> tuple[dict[str, str], dict[str, Any], dict[str, str]]:
    root = _require_external(repository_root, candidate_root, "candidate root")
    receipt_path = root / "run_receipt.json"
    receipt_sha256 = _require_hash(receipt_path, expected_receipt_sha256, "candidate run receipt")
    receipt = _load_json_object(receipt_path, "candidate run receipt")
    if receipt.get("schema_version") != "iris-tooltip-t1-run-receipt-v1":
        raise TooltipContractError("candidate run receipt schema mismatch")
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
    }


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
    expected_subject, candidate_closeout, candidate_receipt = _validate_candidate_closeout(
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
        _require_hash(canonical_path, canonical_ref.get("sha256"), f"{label} canonical result")

    output = _require_external(repository_root, output_root, "final closeout output root")
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise TooltipContractError("final closeout output root must be empty")
    else:
        output.mkdir(parents=True)
    final_record = {
        "schema_version": "iris-tooltip-t1-axis-closeout-v2",
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
        "validation_ceiling": "offline Tooltip T1 contract/audit plus same-subject canonical Run A, Run B, and deterministic comparator; no runtime, visual, release, or upstream-correction completion claim",
        "T2_FULL_DATA_PROGRESSION": candidate_closeout["T2_FULL_DATA_PROGRESSION"],
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
            "no upstream correction resolution",
            "no release/deployment readiness claim",
        ],
    }
    final_path = output / "axis_separated_final_closeout_record.json"
    _write_json(final_path, final_record)
    return {
        "contract_and_audit_axis": "complete",
        "formal_closeout_state": "complete",
        "T2_FULL_DATA_PROGRESSION": final_record["T2_FULL_DATA_PROGRESSION"],
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


def _layer4_candidates(row: dict[str, Any]) -> list[Layer4Candidate]:
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
        candidates.append(
            Layer4Candidate(
                interaction_id=identity,
                source=source,
                public_state="public",
                line_kind=str(item.get("line_kind") or "unknown"),
                requirement_only=bool(item.get("requirement_only", False)),
                stable_order_key=item.get("stable_order_key"),
                localized_surfaces=item.get("display_by_locale"),
                menu_consumer_identity_ref=None,
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


def _slot_selected_layer4(slot_id: str, candidate: Layer4Candidate, lexical_fixture: dict[str, Any]) -> Slot:
    surfaces = candidate.localized_surfaces if isinstance(candidate.localized_surfaces, dict) else {}
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
        CLASSIFICATIONS,
        L3_POINTER,
        L3_INPUT_MANIFEST,
        L3_GENERATIONS / generation_id / "generation_descriptor.json",
        L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json",
        L4_OWNER_INPUT,
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
    masked: dict[str, str] = {}
    restored: dict[str, str] = {}
    for full_type, candidates in sorted(by_full_type.items()):
        result = verify_invariants(candidates)
        base[full_type] = result["permutation"]["base_selected_identity_sha256"]
        permuted[full_type] = result["permutation"]["permuted_selected_identity_sha256"]
        masked[full_type] = result["readiness_masking"]["masked_selected_identity_sha256"]
        restored[full_type] = result["readiness_masking"]["restored_selected_identity_sha256"]
    digest = lambda value: sha256_bytes(canonical_bytes(value))
    identities = {"base": digest(base), "permuted": digest(permuted), "masked": digest(masked), "restored": digest(restored)}
    if len(set(identities.values())) != 1:
        raise TooltipContractError("IDENTITY_READINESS_FEEDBACK_VIOLATION")
    return {
        "schema_version": "iris-tooltip-layer4-invariance-v1",
        "candidate_full_type_count": len(by_full_type),
        "permutation": {
            "base_selected_identity_sha256": identities["base"],
            "permuted_selected_identity_sha256": identities["permuted"],
            "changed": False,
        },
        "readiness_masking": {
            "base_selected_identity_sha256": identities["base"],
            "masked_selected_identity_sha256": identities["masked"],
            "restored_selected_identity_sha256": identities["restored"],
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

    # W0: validate the tracked contract template and bind an exact clean subject.
    contract_hashes = validate_contracts(repository_root, decision_contract_sha256)
    subject = git_subject(repository_root)
    validate_execution_subject(subject)

    pointer_text = (repository_root / L3_POINTER).read_text(encoding="utf-8")
    generation_id = _generation_id(pointer_text)
    input_hashes_before = _source_hashes(repository_root, generation_id)
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
    subject["subject_identity_sha256"] = sha256_bytes(canonical_bytes(subject_identity))

    classifications = parse_classifications(repository_root / CLASSIFICATIONS)
    rendered = load_json(repository_root / L3_GENERATIONS / generation_id / "dvf_3_3_rendered.json")
    layer3 = rendered.get("entries")
    if not isinstance(layer3, dict):
        raise TooltipContractError("Layer 3 rendered entries missing")
    descriptions = load_json(repository_root / L4_OWNER_INPUT)
    layer4 = descriptions.get("fulltypes")
    if not isinstance(layer4, dict):
        raise TooltipContractError("Layer 4 fulltypes missing")
    runtime_layer4 = _runtime_layer4_identities(repository_root)
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
        "P-8": {"evidence_state": "mixed", "observation": "Layer 3 role-material identities and locale payloads are separate", "canonical_count": len(layer3), "en_count": len(l3_en_keys)},
        "P-10": {"evidence_state": "absent", "observation": "no owner-issued Layer 2 resolved identity or independent per-row Menu identity route"},
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
            "layer2_resolved_owner_output": "absent",
            "layer2_independent_menu_consumer_identity": "absent",
            "layer3_single_tooltip_fact_identity_and_surfaces": "absent",
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
    collision_members = {value for rows in support_collisions.values() for value in rows}
    by_full_type = {full_type: _layer4_candidates(layer4.get(full_type, {})) for full_type in support}
    invariance = _invariance(by_full_type)

    audit_rows: list[dict[str, Any]] = []
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
        if full_type in collision_members:
            corrections.append(_correction(
                full_type, "support", "Iris presentation-contract owner", "SUPPORT_NORMALIZED_COLLISION",
                "explicit owner disposition for the distinct case-sensitive FullTypes in this normalized collision",
            ))
        # P-10: current raw tags and runtime resolver are census evidence only;
        # no owner-issued resolved identity exists for Tooltip consumption.
        slots.append(_slot_correction("S1", "CLASSIFICATION_RESOLVED_IDENTITY_MISSING"))
        corrections.append(_correction(
            full_type, "layer2", "Classification owner", "CLASSIFICATION_RESOLVED_IDENTITY_MISSING",
            "resolved classification/category/primary-subcategory identity with KO/EN surfaces",
        ))
        corrections.append(_correction(
            full_type, "cross-layer", "Menu consumer owner", "PARITY_AUTHORITY_RELATION_MISSING",
            "shared Layer 2 owner/Menu public identity authority relation",
        ))

        l3 = layer3.get(full_type)
        role_material = l3.get("role_material") if isinstance(l3, dict) else None
        core_ids_value = role_material.get("core_source_fact_ids") if isinstance(role_material, dict) else None
        valid_core_ids = isinstance(core_ids_value, list) and all(isinstance(value, str) and value for value in core_ids_value)
        core_ids = list(core_ids_value) if valid_core_ids else []
        l3_proof = f"{(L3_GENERATIONS / generation_id / 'dvf_3_3_rendered.json').as_posix()}#entries/{full_type}/role_material/core_source_fact_ids"
        if isinstance(l3, dict) and isinstance(role_material, dict) and valid_core_ids and not core_ids:
            slots.append(_slot_absent("S2", "DVF_CORE_DESCRIPTION_ABSENCE_PROVED", l3_proof))
            absence_distribution[f"layer3|locale=all|reason=DVF_CORE_DESCRIPTION_ABSENCE_PROVED|authority={(L3_GENERATIONS / generation_id / 'dvf_3_3_rendered.json').as_posix()}"] += 1
        elif isinstance(l3, dict) and isinstance(role_material, dict) and valid_core_ids:
            slots.append(_slot_correction("S2", "DVF_TOOLTIP_FACT_IDENTITY_MISSING"))
            corrections.append(_correction(
                full_type, "layer3", "DVF owner", "DVF_TOOLTIP_FACT_IDENTITY_MISSING",
                "one owner-approved core-description fact identity with complete KO/EN single-line surfaces",
            ))
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
            slot = _slot_selected_layer4(slot_id, candidate, lexical_fixture)
            slots.append(slot)
            if slot.t2_blocking:
                for locale in ("ko", "en"):
                    if slot.locale_readiness[locale] is LocaleSurfaceReadiness.CORRECTION_REQUIRED:
                        reason = public_surface_reason(candidate.localized_surfaces.get(locale) if isinstance(candidate.localized_surfaces, dict) else None, locale, lexical_fixture)
                        correction_reason = reason or "LOCALE_SELECTED_SURFACE_MISSING"
                        corrections.append(_correction(
                            full_type, "layer4", reason_owners[correction_reason], correction_reason,
                            "explicit selected-identity single-line display_by_locale surface passing the exact lexical fixture",
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
            "layer2": MenuParityStatus.CORRECTION_REQUIRED,
            "layer3": MenuParityStatus.NOT_APPLICABLE
            if slots[1].semantic_state is SemanticSlotState.LEGITIMATE_ABSENCE
            else MenuParityStatus.CORRECTION_REQUIRED,
            "layer4": classify_menu_relation((candidate.interaction_id for candidate in selected), runtime_identities),
        }
        for layer, status in parity.items():
            parity_distribution[f"{layer}:{status.value}"] += 1
        ko_count = sum(slot.displayable("ko") for slot in slots)
        en_count = sum(slot.displayable("en") for slot in slots)
        t2_blocking = any(slot.t2_blocking for slot in slots)
        parity_view = {
            layer: {
                "status": status.value,
                "authority_relation_ref": f"{L4_OWNER_INPUT.as_posix()} -> {L4_RUNTIME_ROOT.as_posix()}/Chunk*.lua" if layer == "layer4" and selected else None,
                "independent_consumer_evidence_ref": "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua#label_key" if layer == "layer4" and selected else None,
                "owner": "Menu consumer owner",
                "re_audit_condition": "T3 runtime adoption observation" if status is MenuParityStatus.UNVERIFIED else "new exact owner-corrected subject",
            }
            for layer, status in parity.items()
        }
        row_reasons = {reason for slot in slots for reason in slot.reason_codes}
        if MenuParityStatus.UNVERIFIED in parity.values():
            row_reasons.add("PARITY_CONSUMER_EVIDENCE_UNVERIFIED")
        row_corrections = corrections[correction_start:]
        row_reasons.update(correction["reason_code"] for correction in row_corrections)
        row_owners = {correction["owner"] for correction in row_corrections}
        for slot in slots:
            if slot.semantic_state is SemanticSlotState.LEGITIMATE_ABSENCE:
                row_owners.add("DVF owner" if slot.slot_id == "S2" else "QG owner")
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
                "resolved_identity": None,
                "authority_ref": CLASSIFICATIONS.as_posix(),
                "menu_consumer_identity_ref": None,
            },
            "layer3": {
                "owner_row_present": isinstance(l3, dict),
                "core_source_fact_ids": list(core_ids),
                "approved_tooltip_fact_id": None,
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

    progression, blocker_by_owner = build_progression_record(corrections, input_hashes_before)
    universe_metrics = validate_whole_universe(set(support), audit_rows)
    input_hashes_after = _source_hashes(repository_root, generation_id)
    source_mutation = source_mutation_count(input_hashes_before, input_hashes_after)
    correction_metrics = correction_completeness_metrics(corrections, reason_owners)
    zero_metrics = {
        **universe_metrics,
        **correction_metrics,
        "raw_semantic_inference_path": int(load_json(repository_root / AUTHORITY_ROOT / "layer2_tooltip_input_contract.json").get("raw_tag_resolution_allowed") is not False),
        "locale_dependent_reselection": int(load_json(repository_root / AUTHORITY_ROOT / "tooltip_locale_menu_parity_contract.json").get("locale_dependent_reselection_allowed") is not False),
        "cross_locale_fallback": int(load_json(repository_root / AUTHORITY_ROOT / "tooltip_locale_menu_parity_contract.json").get("cross_locale_fallback_allowed") is not False),
        "menu_parity_unclassified": sum(not isinstance(row.get("menu_parity_by_layer"), dict) or set(row["menu_parity_by_layer"]) != {"layer2", "layer3", "layer4"} for row in audit_rows),
        "menu_owner_output_self_comparison": int(L4_OWNER_INPUT.parent == L4_RUNTIME_ROOT.parent),
        "mock_consumer_product_decision": 0,
        "progression_unknown_blocking_cause_owner": 0,
        "source_equivalence_contract_violation": sum(row["layer4_source_equivalence"]["violation"] for row in audit_rows),
        "supported_row_removed_for_readiness_defect": 0,
        "layer4_selection_changed_by_locale_readiness": int(invariance["readiness_masking"]["locale_readiness_changed_selection"]),
        "layer4_selection_changed_by_menu_evidence": int(invariance["readiness_masking"]["menu_evidence_changed_selection"]),
        "source_mutation": source_mutation,
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
        "layer2_owner_route": "gap:no_admissible_resolved_identity_output",
        "layer3_owner_route": "current generation has source ids/body but no approved Tooltip fact identity/surface",
        "layer4_owner_route": f"current owner data {L4_OWNER_INPUT.as_posix()} supplies public identities; reproduction baseline is not consumed",
        "menu_consumer_evidence_route": f"current runtime {L4_RUNTIME_ROOT.as_posix()}/Chunk*.lua label_key identities consumed by IrisBrowserInteractionProjection.lua",
        "tooltip_runtime_route": "read_only_non_verdict_baseline",
    }
    fixture_result = {
        "schema_version": "iris-tooltip-contract-fixture-result-v1",
        "expectations_sha256": sha256_bytes(canonical_bytes(fixture_expectations)),
        "slot_order_match": fixture_expectations.get("slot_order") == ["S1", "S2", "S3", "S4"],
        "progression_match": fixture_expectations.get("blocked_progression") == T2Progression.UPSTREAM.value,
        "self_seeded_from_audit": False,
    }
    if not fixture_result["slot_order_match"] or not fixture_result["progression_match"]:
        raise TooltipContractError("tracked contract fixture mismatch")

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
        candidate_closeout_record(progression["T2_FULL_DATA_PROGRESSION"]),
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
