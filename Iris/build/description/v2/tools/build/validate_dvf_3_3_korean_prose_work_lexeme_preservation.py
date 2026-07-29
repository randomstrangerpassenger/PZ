from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.compose_layer3_io import file_sha256
    from tools.build.compose_layer3_text import (
        BODY_PLAN_PROFILES_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        STAGING_COMPOSE_CONTEXT,
        build_candidate_rendered,
    )
else:
    from .compose_layer3_io import file_sha256
    from .compose_layer3_text import (
        BODY_PLAN_PROFILES_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        STAGING_COMPOSE_CONTEXT,
        build_candidate_rendered,
    )


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
FACTS_PATH = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
DECISIONS_PATH = V2_ROOT / "data" / "dvf_3_3_decisions.jsonl"
INPUT_MANIFEST_PATH = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
POLICY_PATH = V2_ROOT / "data" / "korean_prose_naturalization" / "korean_prose_policy.json"
COMPILER_PATH = TOOLS_DIR / "compose_layer3_identity.py"

HISTORICAL_REVIEWER_BLOCKER_IDS = (
    "Base.Hammer",
    "Base.Crowbar",
    "Base.MetalPipe",
    "Base.Shovel2",
    "Radio.RadioBlack",
    "Radio.WalkieTalkie2",
    "Radio.TvBlack",
)
CURRENT_REVIEWER_BLOCKER_IDS = (
    "Base.WoodenMallet",
    "Base.ClubHammer",
    "Base.GardenHoe",
    "Base.CordlessPhone",
    "Base.Corkscrew",
    "Base.PlateOrange",
)
COMPILER_FIX_COMMIT = "b399cdbacf884ed97a884e8a0266f94a7e4a13d5"
WORK_PHRASE_PATTERN = re.compile(
    r"(?:[가-힣]+(?:\s+|(?:이나|나|와|과)\s+)){1,4}"
    r"작업(?:에서|으로|에|을|를|과|와|은|는|이|가)?"
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def git_output(*args: str) -> str:
    return subprocess.check_output(
        ("git", *args),
        cwd=REPO_ROOT,
        text=True,
    ).strip()


def compiler_fix_is_ancestor() -> bool:
    return (
        subprocess.run(
            ("git", "merge-base", "--is-ancestor", COMPILER_FIX_COMMIT, "HEAD"),
            cwd=REPO_ROOT,
            check=False,
        ).returncode
        == 0
    )


def extract_damaged_work_phrases(
    *,
    source_values: list[str],
    output_text: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_value in source_values:
        for match in WORK_PHRASE_PATTERN.finditer(source_value):
            source_phrase = match.group(0)
            damaged_phrase = source_phrase.replace("작업", "과정")
            if damaged_phrase in output_text:
                rows.append(
                    {
                        "source_phrase": source_phrase,
                        "damaged_output_phrase": damaged_phrase,
                    }
                )
    return rows


def build_report(
    *,
    source_inventory_path: Path,
    requirement_inventory_path: Path,
    expected_input_commit: str,
    expected_input_tree: str,
) -> dict[str, Any]:
    actual_commit = git_output("rev-parse", "HEAD")
    actual_tree = git_output("rev-parse", "HEAD^{tree}")
    if actual_commit != expected_input_commit:
        raise ValueError(
            f"INPUT_COMMIT_MISMATCH expected={expected_input_commit} actual={actual_commit}"
        )
    if actual_tree != expected_input_tree:
        raise ValueError(
            f"INPUT_TREE_MISMATCH expected={expected_input_tree} actual={actual_tree}"
        )
    if not compiler_fix_is_ancestor():
        raise ValueError(f"COMPILER_FIX_NOT_ANCESTOR {COMPILER_FIX_COMMIT}")

    propositions = load_jsonl(source_inventory_path)
    proposition_by_id = {
        str(row["proposition_id"]): row
        for row in propositions
    }
    source_values_by_item: dict[str, list[str]] = defaultdict(list)
    for row in propositions:
        source_values_by_item[str(row["item_id"])].append(
            str(row.get("source_value") or "")
        )

    with tempfile.TemporaryDirectory(
        prefix="dvf-korean-work-lexeme-detector-"
    ) as temporary_directory:
        projection_root = Path(temporary_directory)
        candidate_path = projection_root / "candidate_rendered.json"
        trace_path = projection_root / "candidate_proposition_trace.jsonl"
        candidate = build_candidate_rendered(
            facts_path=FACTS_PATH,
            decisions_path=DECISIONS_PATH,
            profiles_path=BODY_PLAN_PROFILES_PATH,
            identity_rules_path=IDENTITY_RULES_PATH,
            precedence_rules_path=PRECEDENCE_RULES_PATH,
            policy_path=POLICY_PATH,
            source_proposition_inventory_path=source_inventory_path,
            body_plan_requirement_inventory_path=requirement_inventory_path,
            output_path=candidate_path,
            trace_path=trace_path,
            structural_path=projection_root / "candidate_structural.jsonl",
            proposition_resolution_path=projection_root
            / "candidate_proposition_resolution.jsonl",
            equivalence_proof_path=projection_root
            / "candidate_equivalence_proofs.jsonl",
            attempt_root=projection_root,
            compose_context=STAGING_COMPOSE_CONTEXT,
            expected_policy_sha256=file_sha256(POLICY_PATH),
        )
        candidate_file_sha256 = file_sha256(candidate_path)
        traces = load_jsonl(trace_path)

    entries = candidate["entries"]
    projected_entries = {
        str(item_id): entry
        for item_id, entry in entries.items()
        if entry.get("source") == "korean_prose_candidate_v1"
    }
    generic_work_to_process_rows: list[dict[str, Any]] = []
    compound_damage_rows: list[dict[str, Any]] = []
    introduced_process_rows: list[dict[str, Any]] = []
    trace_rows_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for trace in traces:
        item_id = str(trace["item_id"])
        trace_rows_by_item[item_id].append(trace)
        source_values = [
            str(proposition_by_id[str(proposition_id)].get("source_value") or "")
            for proposition_id in trace.get("proposition_ids", [])
            if str(proposition_id) in proposition_by_id
        ]
        source_text = " ".join(source_values)
        output_text = str(trace.get("text") or "")
        source_work_count = source_text.count("작업")
        output_work_count = output_text.count("작업")
        source_process_count = source_text.count("과정")
        output_process_count = output_text.count("과정")
        lexical_transformation = (
            "lexical_surface_naturalization"
            in trace.get("transformation_ids", [])
        )
        introduced_process_count = max(
            0,
            output_process_count - source_process_count,
        )
        if introduced_process_count:
            introduced_process_rows.append(
                {
                    "item_id": item_id,
                    "clause_id": trace["clause_id"],
                    "realization_rule_id": trace["realization_rule_id"],
                    "lexical_surface_naturalization": lexical_transformation,
                    "source_work_count": source_work_count,
                    "source_process_count": source_process_count,
                    "output_work_count": output_work_count,
                    "output_process_count": output_process_count,
                    "introduced_process_count": introduced_process_count,
                }
            )
        if (
            lexical_transformation
            and source_work_count > output_work_count
            and output_process_count > source_process_count
        ):
            generic_work_to_process_rows.append(
                {
                    "item_id": item_id,
                    "clause_id": trace["clause_id"],
                    "realization_rule_id": trace["realization_rule_id"],
                    "source_values": source_values,
                    "output_text": output_text,
                }
            )
        for damage in extract_damaged_work_phrases(
            source_values=source_values,
            output_text=output_text,
        ):
            compound_damage_rows.append(
                {
                    "item_id": item_id,
                    "clause_id": trace["clause_id"],
                    **damage,
                }
            )

    introduced_rule_counts = Counter(
        str(row["realization_rule_id"])
        for row in introduced_process_rows
    )
    introduced_process_item_ids = sorted(
        {str(row["item_id"]) for row in introduced_process_rows}
    )
    generic_introduced_process_rows = [
        row
        for row in introduced_process_rows
        if row["lexical_surface_naturalization"] is True
    ]

    def regression_rows(
        item_ids: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        generic_failure_ids = {
            str(row["item_id"])
            for row in generic_work_to_process_rows
        }
        compound_failure_ids = {
            str(row["item_id"])
            for row in compound_damage_rows
        }
        for item_id in item_ids:
            source_values = source_values_by_item.get(item_id, [])
            output_text = str(projected_entries.get(item_id, {}).get("text_ko") or "")
            source_work_count = sum(value.count("작업") for value in source_values)
            output_work_count = output_text.count("작업")
            passed = (
                item_id in projected_entries
                and source_work_count > 0
                and output_work_count > 0
                and item_id not in generic_failure_ids
                and item_id not in compound_failure_ids
            )
            rows.append(
                {
                    "item_id": item_id,
                    "source_work_count": source_work_count,
                    "output_work_count": output_work_count,
                    "generic_work_to_process_count": sum(
                        1
                        for row in generic_work_to_process_rows
                        if row["item_id"] == item_id
                    ),
                    "compound_damage_count": sum(
                        1
                        for row in compound_damage_rows
                        if row["item_id"] == item_id
                    ),
                    "status": "PASS" if passed else "FAIL",
                }
            )
        return rows

    historical_rows = regression_rows(HISTORICAL_REVIEWER_BLOCKER_IDS)
    current_rows = regression_rows(CURRENT_REVIEWER_BLOCKER_IDS)
    projected_denominator = len(projected_entries)
    report_pass = all(
        (
            projected_denominator == 2084,
            not generic_work_to_process_rows,
            not generic_introduced_process_rows,
            not compound_damage_rows,
            all(row["status"] == "PASS" for row in historical_rows),
            all(row["status"] == "PASS" for row in current_rows),
        )
    )
    return {
        "schema_version": "dvf-3-3-korean-prose-work-lexeme-preservation-report-v1",
        "status": "PASS" if report_pass else "FAIL",
        "status_scope": "generic_work_lexeme_preservation_only",
        "execution_mode": "temporary_projection_no_naturalization_attempt",
        "input_binding": {
            "commit": actual_commit,
            "tree": actual_tree,
            "compiler_fix_commit": COMPILER_FIX_COMMIT,
            "compiler_fix_is_head_ancestor": True,
            "facts_path": FACTS_PATH.relative_to(REPO_ROOT).as_posix(),
            "facts_sha256": file_sha256(FACTS_PATH),
            "current_manifest_path": INPUT_MANIFEST_PATH.relative_to(
                REPO_ROOT
            ).as_posix(),
            "current_manifest_sha256": file_sha256(INPUT_MANIFEST_PATH),
            "source_inventory_path": source_inventory_path.relative_to(
                REPO_ROOT
            ).as_posix(),
            "source_inventory_sha256": file_sha256(source_inventory_path),
            "requirement_inventory_path": requirement_inventory_path.relative_to(
                REPO_ROOT
            ).as_posix(),
            "requirement_inventory_sha256": file_sha256(
                requirement_inventory_path
            ),
            "compiler_sha256": file_sha256(COMPILER_PATH),
        },
        "projection": {
            "candidate_key_count": len(entries),
            "projected_text_denominator": projected_denominator,
            "unadopted_count": len(entries) - projected_denominator,
            "candidate_file_sha256": candidate_file_sha256,
            "candidate_entries_canonical_sha256": canonical_hash(entries),
            "trace_row_count": len(traces),
        },
        "detectors": {
            "source_work_to_process_generic_transformation": {
                "hit_count": len(generic_work_to_process_rows),
                "rows": generic_work_to_process_rows,
            },
            "parallel_or_compound_work_phrase_damage": {
                "hit_count": len(compound_damage_rows),
                "rows": compound_damage_rows,
            },
            "compiler_introduced_process_without_same_clause_source_process": {
                "observation_count": len(introduced_process_rows),
                "generic_lexical_transformation_count": len(
                    generic_introduced_process_rows
                ),
                "non_generic_semantic_realization_count": (
                    len(introduced_process_rows)
                    - len(generic_introduced_process_rows)
                ),
                "realization_rule_counts": dict(
                    sorted(introduced_rule_counts.items())
                ),
                "item_ids": introduced_process_item_ids,
                "rows_digest": canonical_hash(introduced_process_rows),
                "disposition": (
                    "observed_outside_generic_work_lexeme_remediation_scope"
                ),
            },
        },
        "regression": {
            "historical_attestation_count": len(historical_rows),
            "historical_attestation_rows": historical_rows,
            "current_attestation_count": len(current_rows),
            "current_attestation_rows": current_rows,
            "combined_unique_blocker_count": len(
                set(HISTORICAL_REVIEWER_BLOCKER_IDS)
                | set(CURRENT_REVIEWER_BLOCKER_IDS)
            ),
            "all_pass": all(
                row["status"] == "PASS"
                for row in (*historical_rows, *current_rows)
            ),
        },
        "scope_guards": {
            "item_specific_compiler_exception_count": 0,
            "naturalization_attempt_created": False,
            "phase7_or_phase8_executed": False,
            "publish_executed": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Project the full Korean prose candidate into a temporary directory "
            "and detect context-free 작업-to-과정 corruption."
        )
    )
    parser.add_argument(
        "--source-inventory",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--requirement-inventory",
        type=Path,
        required=True,
    )
    parser.add_argument("--expected-input-commit", required=True)
    parser.add_argument("--expected-input-tree", required=True)
    parser.add_argument("--report-path", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        source_inventory_path=args.source_inventory.resolve(),
        requirement_inventory_path=args.requirement_inventory.resolve(),
        expected_input_commit=args.expected_input_commit,
        expected_input_tree=args.expected_input_tree,
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "projected_text_denominator": report["projection"][
                    "projected_text_denominator"
                ],
                "generic_work_to_process_hit_count": report["detectors"][
                    "source_work_to_process_generic_transformation"
                ]["hit_count"],
                "compound_damage_hit_count": report["detectors"][
                    "parallel_or_compound_work_phrase_damage"
                ]["hit_count"],
                "generic_introduced_process_count": report["detectors"][
                    "compiler_introduced_process_without_same_clause_source_process"
                ]["generic_lexical_transformation_count"],
                "non_generic_introduced_process_observation_count": report[
                    "detectors"
                ][
                    "compiler_introduced_process_without_same_clause_source_process"
                ]["non_generic_semantic_realization_count"],
                "reviewer_blocker_regression_pass": report["regression"][
                    "all_pass"
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
