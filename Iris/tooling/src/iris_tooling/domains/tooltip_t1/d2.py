from __future__ import annotations

from collections import Counter
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable

from iris_tooling.domains.classification.layer2_contract import (
    OWNER_OUTPUT,
    support_sha256,
    support_universe,
)
from iris_tooling.domains.classification.layer2_validator import validate_owner_output

from .contract import canonical_bytes, git_subject, load_json, sha256_bytes, sha256_file
from .models import TooltipContractError


DIRECT_PARENT_COMMIT = "cb27591e3c6ef40a1b1f08a6e2ceee7047132cf8"
DIRECT_PARENT_TREE = "b23103ace037aa62fc1e24d04901d534de5cc2e8"
RELATION_NAME = "layer2_menu_consumer_relation.jsonl"
RECEIPT_NAME = "run_receipt.json"
HARNESS = Path("Iris/test/lua/fixtures/tags_public_surface_isolation_harness.lua")
PROJECTION_BUILDER = Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua")
CATEGORY_INDEX = Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua")
CLASSIFICATIONS = Path("Iris/media/lua/client/Iris/Data/IrisClassifications.lua")
LAYER2_INPUT_CONTRACT = Path("Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json")
PARITY_CONTRACT = Path("Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json")

_D6_EXCLUSIVE_PATHS = {
    "Iris/_docs/authority/iris_current_authority_manifest.json",
    "Iris/_docs/authority/iris_current_route_index.json",
    "Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json",
    "Iris/build/ENTRYPOINTS.md",
    "docs/DECISIONS.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
}
_PROTECTED_PATHS = {
    "Iris/build/classification/data/classification_layer2_owner_output.json",
    "Iris/build/classification/data/classification_layer2_resolution_registry.json",
    "Iris/build/classification/data/classification_layer2_surface_catalog.json",
    "Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json",
    "Iris/build/description/v2/data/tooltip_t1_layer4_recipe_locale_owner_input.json",
    "Iris/build/description/v2/data/upstream_usecases_by_fulltype.json",
    "Iris/media/lua/client/Iris/Data/IrisClassifications.lua",
    "Iris/_docs/authority/tooltip_t1/tooltip_t1_d5_current_support_disposition.json",
}
_PROTECTED_PREFIXES = (
    "Iris/_docs/authority/classification_layer2/",
    "Iris/_docs/authority/dvf/",
    "Iris/_docs/authority/qg/",
    "Iris/media/lua/client/Iris/Data/IrisLayer3Generations/",
)
_SHARED_PATHS = {
    "Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py",
    "Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py",
    "Iris/tooling/tests/test_tooltip_t1_audit.py",
    "Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json",
    "Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json",
    "Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json",
    "Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TooltipContractError(message)


def _set_sha256(values: Iterable[str]) -> str:
    ordered = sorted(set(values), key=lambda value: value.encode("utf-8"))
    return sha256_bytes(b"".join(value.encode("utf-8") + b"\n" for value in ordered))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TooltipContractError(f"{path}: JSONL row must be an object")
            rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TooltipContractError(f"cannot load {path}: {exc}") from exc
    return rows


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(value))


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def _empty_root(path: Path) -> None:
    _require(not path.exists(), f"output root already exists: {path}")
    path.mkdir(parents=True)


def _git(repository_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repository_root, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if completed.returncode:
        raise TooltipContractError(completed.stderr.strip() or "git query failed")
    return completed.stdout.strip()


def _observed_projection(repository_root: Path, support: tuple[str, ...], scratch: Path) -> dict[str, dict[str, Any]]:
    lua = shutil.which("lua")
    _require(lua is not None, "required standalone Lua executable is unavailable")
    support_input = scratch / ".d2_support_input.txt"
    support_input.write_bytes(b"".join(value.encode("utf-8") + b"\n" for value in support))
    try:
        completed = subprocess.run(
            [
                lua,
                str(repository_root / HARNESS),
                str(repository_root),
                "d2-projection",
                str(support_input),
            ],
            cwd=repository_root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    finally:
        support_input.unlink(missing_ok=True)
    _require(
        completed.returncode == 0,
        "actual Browser projection failed: " + (completed.stdout + completed.stderr).strip(),
    )
    observed: dict[str, dict[str, Any]] = {}
    pass_count: int | None = None
    for line in completed.stdout.splitlines():
        if line.startswith("IRIS_D2_ROW\t"):
            fields = line.split("\t")
            _require(len(fields) == 12, "actual Browser projection row shape mismatch")
            (
                _, full_type, memberships, primary_category, primary_subcategory,
                primary_tag, category_key, subcategory_key, explicit_primary,
                presentation_category, presentation_subcategory, accepted_count,
            ) = fields
            _require(full_type not in observed, f"duplicate actual Browser FullType: {full_type}")
            observed[full_type] = {
                "memberships": memberships.split(",") if memberships else [],
                "primary_location": (
                    {"category": primary_category, "subcategory": primary_subcategory}
                    if primary_category and primary_subcategory else None
                ),
                "primary_tag": primary_tag or None,
                "category_label_key": category_key or None,
                "primary_subcategory_label_key": subcategory_key or None,
                "explicit_primary": explicit_primary or None,
                "presentation_primary_location": (
                    {"category": presentation_category, "subcategory": presentation_subcategory}
                    if presentation_category and presentation_subcategory else None
                ),
                "accepted_membership_count": int(accepted_count),
            }
        elif line.startswith("IRIS_D2_PROJECTION_PASS count="):
            pass_count = int(line.rsplit("=", 1)[1])
    _require(pass_count == len(support), "actual Browser projection terminal count mismatch")
    _require(set(observed) == set(support), "actual Browser projection support coverage mismatch")
    return observed


def _location_tag(location: Any) -> str | None:
    if not isinstance(location, dict):
        return None
    category = location.get("category")
    subcategory = location.get("subcategory")
    if not isinstance(category, str) or not isinstance(subcategory, str):
        return None
    return f"{category}.{subcategory}"


def _expected_observed_mismatches(expected: dict[str, Any], observed: dict[str, Any]) -> list[str]:
    primary = expected["primary_subcategory_id"]
    category = expected["category_id"]
    category_key = expected["category_surface"]["key"]
    subcategory_key = expected["primary_subcategory_surface"]["key"]
    actual_primary = _location_tag(observed.get("primary_location"))
    actual_identity = (
        f"{observed['primary_location']['category']}|{observed['primary_tag']}"
        if isinstance(observed.get("primary_location"), dict) and observed.get("primary_tag") else None
    )
    checks = {
        "membership": sorted(observed.get("memberships", [])) == sorted(expected["memberships"]),
        "navigation_primary": actual_primary == primary,
        "display_primary": observed.get("primary_tag") == primary,
        "navigation_category": (
            isinstance(observed.get("primary_location"), dict)
            and observed["primary_location"].get("category") == category
        ),
        "classification_identity": actual_identity == expected["classification_identity"],
        "category_label_key": observed.get("category_label_key") == category_key,
        "subcategory_label_key": observed.get("primary_subcategory_label_key") == subcategory_key,
        "category_label_source": (
            isinstance(expected["category_surface"].get("authority_ref"), str)
            and bool(expected["category_surface"]["authority_ref"])
            and f"#{category_key}" in expected["category_surface"].get("provenance_ref", "")
        ),
        "subcategory_label_source": (
            isinstance(expected["primary_subcategory_surface"].get("authority_ref"), str)
            and bool(expected["primary_subcategory_surface"]["authority_ref"])
            and f"#{subcategory_key}" in expected["primary_subcategory_surface"].get("provenance_ref", "")
        ),
    }
    return [name for name, matches in checks.items() if not matches]


def validate_relation_lifecycle(
    rows: Iterable[dict[str, Any]],
    applicable: set[str],
    display_silence: set[str],
) -> dict[str, int]:
    values = list(rows)
    by_full_type: dict[str, dict[str, Any]] = {}
    counts: Counter[str] = Counter()
    for row in values:
        _require(row.get("schema_version") == "iris-tooltip-t1-d2-layer2-menu-relation-row-v1", "D2 relation row schema mismatch")
        full_type = row.get("full_type")
        _require(isinstance(full_type, str) and full_type and full_type not in by_full_type, "D2 relation exact FullType missing or duplicated")
        by_full_type[full_type] = row
        disposition = row.get("disposition")
        mismatches = row.get("mismatch_kinds")
        _require(isinstance(mismatches, list) and all(isinstance(value, str) for value in mismatches), f"D2 mismatch list malformed: {full_type}")
        if full_type in applicable:
            _require(row.get("layer2_applicability") == "layer2_applicable", f"D2 applicable state mismatch: {full_type}")
            _require(disposition in {"verified", "correction_required"}, f"D2 applicable disposition mismatch: {full_type}")
            _require((disposition == "verified") == (not mismatches), f"D2 applicable mismatch/disposition inconsistency: {full_type}")
            _require(isinstance(row.get("expected"), dict) and isinstance(row.get("observed"), dict), f"D2 applicable tuple missing: {full_type}")
        elif full_type in display_silence:
            _require(row.get("layer2_applicability") == "layer2_display_silence", f"D2 silence state mismatch: {full_type}")
            _require(disposition == "not_applicable" and not mismatches, f"D2 silence disposition mismatch: {full_type}")
            _require(row.get("expected") is None and isinstance(row.get("observed"), dict), f"D2 silence tuple boundary mismatch: {full_type}")
        else:
            raise TooltipContractError(f"D2 relation contains unsupported FullType: {full_type}")
        counts[str(disposition)] += 1
    _require(set(by_full_type) == applicable | display_silence, "D2 relation support exact set mismatch")
    _require(not (applicable & display_silence), "D2 relation applicability partition overlaps")
    return dict(sorted(counts.items()))


def load_relation(repository_root: Path, relation_path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    receipt_path = relation_path.with_name(RECEIPT_NAME)
    _require(relation_path.is_file() and receipt_path.is_file(), "D2 relation/receipt input is missing")
    receipt = load_json(receipt_path)
    _require(receipt.get("schema_version") == "iris-tooltip-t1-d2-run-receipt-v1", "D2 relation receipt schema mismatch")
    _require(receipt.get("artifact_sha256") == sha256_file(relation_path), "D2 relation artifact hash mismatch")
    owner = load_json(repository_root / OWNER_OUTPUT)
    applicable = {row["full_type"] for row in owner.get("rows", []) if isinstance(row, dict)}
    silence = {row["full_type"] for row in owner.get("layer2_display_silence_entries", []) if isinstance(row, dict)}
    rows = _read_jsonl(relation_path)
    counts = validate_relation_lifecycle(rows, applicable, silence)
    _require(receipt.get("disposition_distribution") == counts, "D2 relation receipt distribution mismatch")
    _require(receipt.get("support_sha256") == _set_sha256(applicable | silence), "D2 relation receipt support identity mismatch")
    return {row["full_type"]: row for row in rows}, receipt


def materialize(repository_root: Path, output_root: Path) -> dict[str, Any]:
    subject = git_subject(repository_root)
    _require(subject.get("working_tree_clean") is True, "D2 materialization requires a clean exact subject")
    validation = validate_owner_output(repository_root)
    support = support_universe(repository_root)
    _require(validation["frozen_support_count"] == len(support), "D2 support count mismatch")
    _require(validation["frozen_support_sha256"] == support_sha256(support), "D2 support hash mismatch")
    owner = load_json(repository_root / OWNER_OUTPUT)
    expected = {row["full_type"]: row for row in owner["rows"]}
    silence_rows = {row["full_type"]: row for row in owner["layer2_display_silence_entries"]}
    _require(set(expected) | set(silence_rows) == set(support), "D2 owner partition union mismatch")
    _require(not (set(expected) & set(silence_rows)), "D2 owner partition overlap")

    _empty_root(output_root)
    observed = _observed_projection(repository_root, support, output_root)
    relation_rows: list[dict[str, Any]] = []
    bounded_delta: set[str] = set()
    mismatch_distribution: Counter[str] = Counter()
    for full_type in support:
        actual = observed[full_type]
        if full_type in expected:
            expected_row = expected[full_type]
            mismatches = _expected_observed_mismatches(expected_row, actual)
            explicit = actual.get("explicit_primary")
            presentation = _location_tag(actual.get("presentation_primary_location"))
            if explicit is not None:
                _require(isinstance(explicit, str) and explicit.count(".") == 1, f"malformed explicit primary: {full_type}")
                _require(explicit in actual["memberships"], f"explicit primary is not an accepted membership: {full_type}")
                _require(actual.get("primary_tag") == explicit, f"explicit primary display mismatch: {full_type}")
                _require(_location_tag(actual.get("primary_location")) == explicit, f"explicit primary navigation mismatch: {full_type}")
                if presentation != explicit:
                    bounded_delta.add(full_type)
            else:
                _require(_location_tag(actual.get("primary_location")) == presentation, f"non-override presentation behavior changed: {full_type}")
            for mismatch in mismatches:
                mismatch_distribution[mismatch] += 1
            expected_tuple = {
                "classification_identity": expected_row["classification_identity"],
                "memberships": expected_row["memberships"],
                "category_id": expected_row["category_id"],
                "primary_subcategory_id": expected_row["primary_subcategory_id"],
                "category_label_key": expected_row["category_surface"]["key"],
                "category_label_authority_ref": expected_row["category_surface"]["authority_ref"],
                "category_label_provenance_ref": expected_row["category_surface"]["provenance_ref"],
                "primary_subcategory_label_key": expected_row["primary_subcategory_surface"]["key"],
                "primary_subcategory_label_authority_ref": expected_row["primary_subcategory_surface"]["authority_ref"],
                "primary_subcategory_label_provenance_ref": expected_row["primary_subcategory_surface"]["provenance_ref"],
                "classification_authority_ref": expected_row["classification_authority_ref"],
                "classification_provenance_ref": expected_row["classification_provenance_ref"],
            }
            relation_rows.append({
                "schema_version": "iris-tooltip-t1-d2-layer2-menu-relation-row-v1",
                "full_type": full_type,
                "layer2_applicability": "layer2_applicable",
                "disposition": "verified" if not mismatches else "correction_required",
                "expected": expected_tuple,
                "observed": actual,
                "mismatch_kinds": mismatches,
                "consumer_source_refs": [
                    CLASSIFICATIONS.as_posix(),
                    PROJECTION_BUILDER.as_posix(),
                    CATEGORY_INDEX.as_posix(),
                ],
            })
        else:
            relation_rows.append({
                "schema_version": "iris-tooltip-t1-d2-layer2-menu-relation-row-v1",
                "full_type": full_type,
                "layer2_applicability": "layer2_display_silence",
                "disposition": "not_applicable",
                "expected": None,
                "observed": actual,
                "mismatch_kinds": [],
                "display_silence_reason": silence_rows[full_type]["display_silence_reason"],
                "consumer_source_refs": [CLASSIFICATIONS.as_posix(), PROJECTION_BUILDER.as_posix()],
            })
    counts = validate_relation_lifecycle(relation_rows, set(expected), set(silence_rows))
    _require(counts.get("correction_required", 0) == 0, f"D2 consumer relation mismatch: {dict(mismatch_distribution)}")
    _require(not (bounded_delta & set(silence_rows)), "display-silence Browser behavior delta detected")

    relation_path = output_root / RELATION_NAME
    _write_jsonl(relation_path, relation_rows)
    receipt = {
        "schema_version": "iris-tooltip-t1-d2-run-receipt-v1",
        "status": "complete",
        "subject_commit": subject["commit"],
        "subject_tree": subject["tree"],
        "support_count": len(support),
        "support_sha256": _set_sha256(support),
        "applicable_count": len(expected),
        "applicable_sha256": _set_sha256(expected),
        "display_silence_count": len(silence_rows),
        "display_silence_sha256": _set_sha256(silence_rows),
        "actual_lua_coverage_count": len(observed),
        "actual_lua_coverage_sha256": _set_sha256(observed),
        "disposition_distribution": counts,
        "verified_sha256": _set_sha256(row["full_type"] for row in relation_rows if row["disposition"] == "verified"),
        "not_applicable_sha256": _set_sha256(row["full_type"] for row in relation_rows if row["disposition"] == "not_applicable"),
        "correction_required_sha256": _set_sha256(row["full_type"] for row in relation_rows if row["disposition"] == "correction_required"),
        "bounded_browser_delta_count": len(bounded_delta),
        "bounded_browser_delta_sha256": _set_sha256(bounded_delta),
        "mismatch_distribution": dict(sorted(mismatch_distribution.items())),
        "machine_invariants": {
            "owner_output_self_comparison": 0,
            "rendered_string_inference": 0,
            "normalized_key_join": 0,
            "display_silence_menu_delta": 0,
        },
        "artifact_sha256": sha256_file(relation_path),
    }
    _write_json(output_root / RECEIPT_NAME, receipt)
    return receipt


def _validated_audit_root(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    receipt = load_json(root / "run_receipt.json")
    _require(receipt.get("schema_version") == "iris-tooltip-t1-run-receipt-v1", f"invalid Tooltip audit receipt: {root}")
    artifacts = receipt.get("artifacts")
    _require(isinstance(artifacts, dict), f"Tooltip audit artifact map missing: {root}")
    for name in ("tooltip_readiness_manifest.jsonl", "upstream_correction_ledger.jsonl"):
        _require(artifacts.get(name) == sha256_file(root / name), f"Tooltip audit artifact hash mismatch: {name}")
    return (
        _read_jsonl(root / "tooltip_readiness_manifest.jsonl"),
        _read_jsonl(root / "upstream_correction_ledger.jsonl"),
        receipt,
    )


def _blob(repository_root: Path, revision: str, path: str) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", f"{revision}:{path}"], cwd=repository_root, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def finalize_bundle(
    repository_root: Path,
    run_a_root: Path,
    run_b_root: Path,
    baseline_audit_root: Path,
    candidate_audit_root: Path,
    bundle_root: Path,
    validation_exit_codes: dict[str, int],
) -> dict[str, Any]:
    run_a_rows, run_a_receipt = load_relation(repository_root, run_a_root / RELATION_NAME)
    run_b_rows, run_b_receipt = load_relation(repository_root, run_b_root / RELATION_NAME)
    _require((run_a_root / RELATION_NAME).read_bytes() == (run_b_root / RELATION_NAME).read_bytes(), "D2 canonical relation A/B mismatch")
    _require(canonical_bytes(run_a_receipt) == canonical_bytes(run_b_receipt), "D2 run receipt A/B mismatch")
    baseline_rows, baseline_corrections, baseline_receipt = _validated_audit_root(baseline_audit_root)
    candidate_rows, candidate_corrections, candidate_receipt = _validated_audit_root(candidate_audit_root)
    support = set(run_a_rows)
    baseline_layer2 = {
        row["full_type"] for row in baseline_corrections
        if row.get("layer") == "cross-layer" and row.get("reason_code") == "PARITY_AUTHORITY_RELATION_MISSING"
    }
    candidate_layer2 = {
        row["full_type"] for row in candidate_corrections
        if row.get("layer") == "cross-layer" and row.get("reason_code") == "PARITY_AUTHORITY_RELATION_MISSING"
    }
    _require(baseline_layer2 == support, "baseline Layer 2 correction exact set mismatch")
    _require(not candidate_layer2, "candidate Layer 2 correction remains")
    baseline_non_d2 = [row for row in baseline_corrections if row["full_type"] not in baseline_layer2 or row.get("layer") != "cross-layer"]
    candidate_non_d2 = [row for row in candidate_corrections if row["full_type"] not in candidate_layer2 or row.get("layer") != "cross-layer"]
    _require(canonical_bytes(baseline_non_d2) == canonical_bytes(candidate_non_d2), "non-D2 correction delta detected")
    baseline_parity = [
        {"full_type": row["full_type"], "layer3": row["menu_parity_by_layer"]["layer3"], "layer4": row["menu_parity_by_layer"]["layer4"]}
        for row in baseline_rows
    ]
    candidate_parity = [
        {"full_type": row["full_type"], "layer3": row["menu_parity_by_layer"]["layer3"], "layer4": row["menu_parity_by_layer"]["layer4"]}
        for row in candidate_rows
    ]
    _require(canonical_bytes(baseline_parity) == canonical_bytes(candidate_parity), "non-D2 parity delta detected")
    _require(all(code == 0 for code in validation_exit_codes.values()), "required validation exit code is nonzero")

    subject = git_subject(repository_root)
    _require(subject.get("working_tree_clean") is True, "D2 bundle requires a clean final subject")
    changed = _git(repository_root, "diff", "--name-only", f"{DIRECT_PARENT_COMMIT}..{subject['commit']}").splitlines()
    changed_set = set(changed)
    _require(not (changed_set & _D6_EXCLUSIVE_PATHS), "D6-exclusive path delta detected")
    protected = {
        path for path in changed
        if path in _PROTECTED_PATHS or any(path.startswith(prefix) for prefix in _PROTECTED_PREFIXES)
    }
    _require(not protected, f"D1/D3/D4/D5 protected path delta detected: {sorted(protected)}")
    shared_delta = [
        {
            "path": path,
            "base_blob": _blob(repository_root, DIRECT_PARENT_COMMIT, path),
            "proposed_blob": _blob(repository_root, subject["commit"], path),
            "workstream_reason": "T1-D2 Layer 2 Menu consumer relation closure",
            "merge_invariant": "preserve D1 partition and Layer 3/4/D5 dispositions",
        }
        for path in changed if path in _SHARED_PATHS
    ]
    _require(bundle_root.is_dir(), "D2 bundle root must contain run_a and run_b")
    _require((bundle_root / "run_a").resolve() == run_a_root.resolve(), "D2 run_a bundle placement mismatch")
    _require((bundle_root / "run_b").resolve() == run_b_root.resolve(), "D2 run_b bundle placement mismatch")

    artifact_hashes = {
        "run_a/layer2_menu_consumer_relation.jsonl": sha256_file(run_a_root / RELATION_NAME),
        "run_a/run_receipt.json": sha256_file(run_a_root / RECEIPT_NAME),
        "run_b/layer2_menu_consumer_relation.jsonl": sha256_file(run_b_root / RELATION_NAME),
        "run_b/run_receipt.json": sha256_file(run_b_root / RECEIPT_NAME),
    }
    manifest = {
        "schema_version": "iris-tooltip-t1-d2-integration-manifest-v1",
        "workstream_id": "T1-D2",
        "terminal_state": "complete",
        "direct_parent_commit": DIRECT_PARENT_COMMIT,
        "direct_parent_tree": DIRECT_PARENT_TREE,
        "final_subject_commit": subject["commit"],
        "final_subject_tree": subject["tree"],
        "declared_byte_checkout_preparation": {
            "mixed_eol_materialization": True,
            "normalized_git_content_delta": 0,
            "semantic_delta": 0,
        },
        "d1_partition": {
            "support_count": run_a_receipt["support_count"],
            "support_sha256": run_a_receipt["support_sha256"],
            "applicable_count": run_a_receipt["applicable_count"],
            "applicable_sha256": run_a_receipt["applicable_sha256"],
            "display_silence_count": run_a_receipt["display_silence_count"],
            "display_silence_sha256": run_a_receipt["display_silence_sha256"],
        },
        "starting_correction_distribution": [],
        "remaining_correction_distribution": [],
        "relation_distribution": run_a_receipt["disposition_distribution"],
        "verified_sha256": run_a_receipt["verified_sha256"],
        "not_applicable_sha256": run_a_receipt["not_applicable_sha256"],
        "correction_required_sha256": run_a_receipt["correction_required_sha256"],
        "bounded_browser_delta_count": run_a_receipt["bounded_browser_delta_count"],
        "bounded_browser_delta_sha256": run_a_receipt["bounded_browser_delta_sha256"],
        "owner_refs": [OWNER_OUTPUT.as_posix(), LAYER2_INPUT_CONTRACT.as_posix(), PARITY_CONTRACT.as_posix()],
        "evidence_refs": [PROJECTION_BUILDER.as_posix(), CATEGORY_INDEX.as_posix(), HARNESS.as_posix()],
        "artifact_hashes": artifact_hashes,
        "shared_path_delta": shared_delta,
        "protected_non_target_invariance": {
            "d1_d3_d4_d5_protected_delta": 0,
            "non_d2_correction_delta": 0,
            "non_d2_parity_delta": 0,
            "d6_exclusive_path_delta": 0,
        },
        "validation_receipts": {
            **validation_exit_codes,
            "baseline_audit_run_receipt_sha256": sha256_file(baseline_audit_root / "run_receipt.json"),
            "candidate_audit_run_receipt_sha256": sha256_file(candidate_audit_root / "run_receipt.json"),
            "relation_a_b_canonical_match": True,
        },
        "claim_ceiling": {
            "static_layer2_browser_consumer_relation_complete": True,
            "current_ecosystem_adoption": "pending_T1_D6",
            "runtime_verification": "pending_T3",
            "production_t2_handoff": "absent",
        },
        "integration_instructions": "T1-D6 must merge shared_path_delta, adopt current routes, and run the integrated canonical gate once.",
    }
    # JSON object keys cannot be tuples; encode correction distributions explicitly.
    manifest["starting_correction_distribution"] = [
        {"owner": owner, "reason_code": reason, "count": count}
        for (owner, reason), count in sorted(Counter((row["owner"], row["reason_code"]) for row in baseline_corrections).items())
    ]
    manifest["remaining_correction_distribution"] = [
        {"owner": owner, "reason_code": reason, "count": count}
        for (owner, reason), count in sorted(Counter((row["owner"], row["reason_code"]) for row in candidate_corrections).items())
    ]
    manifest_path = bundle_root / "t1d2_integration_manifest.json"
    _write_json(manifest_path, manifest)
    bundle_receipt = {
        "schema_version": "iris-tooltip-t1-d2-bundle-receipt-v1",
        "terminal_state": "complete",
        "manifest_sha256": sha256_file(manifest_path),
        "artifact_hashes": artifact_hashes,
    }
    _write_json(bundle_root / "t1d2_bundle_receipt.json", bundle_receipt)
    loaded_receipt = load_json(bundle_root / "t1d2_bundle_receipt.json")
    _require(loaded_receipt == bundle_receipt, "D2 bundle receipt round-trip mismatch")
    _require(loaded_receipt["manifest_sha256"] == sha256_file(manifest_path), "D2 bundle manifest hash mismatch")
    for relative, digest in artifact_hashes.items():
        _require(sha256_file(bundle_root / relative) == digest, f"D2 bundle artifact hash mismatch: {relative}")
    return bundle_receipt
