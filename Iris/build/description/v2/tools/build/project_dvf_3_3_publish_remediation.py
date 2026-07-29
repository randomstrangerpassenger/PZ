from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.compose_layer3_text import (
        BODY_PLAN_PROFILES_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        STAGING_COMPOSE_CONTEXT,
        build_candidate_rendered,
    )
    from tools.build import run_dvf_3_3_korean_prose_naturalization as producer
else:
    from .compose_layer3_text import (
        BODY_PLAN_PROFILES_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        STAGING_COMPOSE_CONTEXT,
        build_candidate_rendered,
    )
    from . import run_dvf_3_3_korean_prose_naturalization as producer


REPO_ROOT = producer.REPO_ROOT
BASELINE_ATTEMPT_ROOT = (
    producer.DEFAULT_ATTEMPT_PARENT / "attempt-0023-compiler-identity-v2-a"
)
BASELINE_CANDIDATE = BASELINE_ATTEMPT_ROOT / "phase4" / "candidate_rendered.json"
BASELINE_TRACE = (
    BASELINE_ATTEMPT_ROOT / "phase4" / "candidate_proposition_trace.jsonl"
)
BASELINE_PROPOSITIONS = (
    BASELINE_ATTEMPT_ROOT / "phase2" / "source_proposition_inventory.jsonl"
)
BASELINE_REQUIREMENTS = (
    BASELINE_ATTEMPT_ROOT / "phase2" / "body_plan_requirement_inventory.jsonl"
)
BASELINE_STRUCTURAL = (
    BASELINE_ATTEMPT_ROOT
    / "phase4"
    / "_candidate_structural_satisfaction.jsonl"
)
CORRECTION_RECORD = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "official_attempt_corrections"
    / "attempt-0004"
    / "phase5-review-schema-incompatibility-correction-0001.json"
)
OFFICIAL_PHASE5 = (
    producer.V2_ROOT
    / "staging"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "attempts"
    / "attempt-0004-official"
    / "phase5"
)
OFFICIAL_DISPOSITION = OFFICIAL_PHASE5 / "evaluation_subject_disposition.json"
OFFICIAL_FAILURE_LEDGER = OFFICIAL_PHASE5 / "naturalization_failure_ledger.json"
DISPOSABLE_ROOT = (
    producer.DEFAULT_ATTEMPT_PARENT
    / "projections"
    / "publish-remediation-correction-0001"
)
DURABLE_ROOT = (
    producer.DURABLE_ROOT
    / "compiler_corrections"
    / "publish_remediation_0001"
)
PROJECTED_CANDIDATE = DISPOSABLE_ROOT / "candidate_rendered.json"
PROJECTED_TRACE = DISPOSABLE_ROOT / "candidate_proposition_trace.jsonl"
PROJECTED_STRUCTURAL = DISPOSABLE_ROOT / "candidate_structural_satisfaction.jsonl"
PROJECTED_RESOLUTION = DISPOSABLE_ROOT / "candidate_proposition_resolution.jsonl"
PROJECTED_PROOFS = DISPOSABLE_ROOT / "candidate_equivalence_proofs.jsonl"
CLASSIFICATION_LEDGER = DURABLE_ROOT / "bounded_projection_classification.jsonl"
CHANGED_ITEM_LEDGER = DURABLE_ROOT / "bounded_projection_changed_items.jsonl"
REPORT = DURABLE_ROOT / "bounded_projection_report.json"

EXPECTED = {
    "start_commit": "98f98027be06221f2ec28aad1f4c503ffccd0e28",
    "start_tree": "06890646e52de91217aded7782fd4220b95b4554",
    "correction_record_sha256": (
        "3e8a3c962543d80814ea2c2200e7889648aab9302b4c7f3a416f2ba516c3139f"
    ),
    "official_disposition_sha256": (
        "50e342e91fc453939828c2fe9350c501dedc30aa6cd4fa35562c15b3091f2063"
    ),
    "official_failure_ledger_sha256": (
        "abf0722fe97c35554282d63a535f58352c4552be4ce94229c93a5e7768870993"
    ),
    "baseline_candidate_sha256": (
        "c4d2799ffd931c585b6da2d4d9a7663c2207181f21a822dbea2794f5d3a08787"
    ),
    "baseline_trace_sha256": (
        "b2d94a4cbaa40a488f7a444a7ff8000c23eab5545b0ec57606fb80a18bd17268"
    ),
    "baseline_propositions_sha256": (
        "bda72c837435d44cc1187ce4a6f6e0e61ee752750d4f5bfa9343b5969fbedd85"
    ),
    "baseline_requirements_sha256": (
        "057f3cb5f4ae0896fec6314936dd7b77c2c48778d6ee2ab2bc48a2d63e4dbe89"
    ),
    "baseline_structural_sha256": (
        "bb366fe3e8cfc2d9ee26835279b4dd0f1cca539dd125b9dfad8682b86a2cfd21"
    ),
    "facts_sha256": (
        "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
    ),
    "manifest_sha256": (
        "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
    ),
}

WORK_PATTERN = re.compile(r"작업(?!장)")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
ACTION_LEXEMES = (
    "가공",
    "갈아",
    "걸쳐",
    "고정",
    "교체",
    "꺼내",
    "끼우",
    "나눠",
    "다듬",
    "담아",
    "던지",
    "들어",
    "마시",
    "맞추",
    "메고",
    "묶",
    "바르",
    "보강",
    "분리",
    "분해",
    "비우",
    "설치",
    "세우",
    "소독",
    "연결",
    "옮기",
    "읽",
    "익히",
    "입고",
    "자르",
    "정돈",
    "정리",
    "조립",
    "조이",
    "주조",
    "찍",
    "채우",
    "펼쳐",
    "풀",
    "휘두르",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            for row in rows
        ),
        encoding="utf-8",
        newline="\n",
    )


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def grammar_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    patterns = (
        ("work_from_case", r"작업에서"),
        ("work_dative_case", r"작업에"),
        ("work_object_case", r"작업을"),
        ("work_during", r"작업 중"),
        ("work_instrumental_case", r"작업으로"),
        ("work_additive_case", r"작업에도"),
        ("work_place_compound", r"작업 장소"),
        ("work_site_compound", r"작업 현장"),
        ("work_vehicle_compound", r"작업 차량"),
        ("work_zone_compound", r"작업 구역"),
    )
    for grammar_id, pattern in patterns:
        for match in re.finditer(pattern, text):
            rows.append(
                {
                    "grammar_id": grammar_id,
                    "surface": match.group(0),
                    "particle_or_compound_tail": match.group(0)[2:],
                }
            )
    if WORK_PATTERN.search(text) and not rows:
        rows.append(
            {
                "grammar_id": "work_other",
                "surface": "작업",
                "particle_or_compound_tail": "",
            }
        )
    return rows


def action_lexemes(text: str) -> list[str]:
    return sorted({value for value in ACTION_LEXEMES if value in text})


def trace_by_item(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result[str(row["item_id"])].append(row)
    return result


def proposition_by_item(
    rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result[str(row["item_id"])].append(row)
    return result


def detector_hits(
    candidate: dict[str, Any],
    traces: list[dict[str, Any]],
    propositions: list[dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, set[str]]:
    trace_map = trace_by_item(traces)
    proposition_map = proposition_by_item(propositions)
    eligible = {
        item_id: entry
        for item_id, entry in candidate["entries"].items()
        if entry.get("source") == "korean_prose_candidate_v1"
    }
    skeletons = Counter(
        producer.text_skeleton(str(entry["text_ko"]))
        for entry in eligible.values()
    )
    result = {str(value): set() for value in policy["raw_detector_ids"]}
    for item_id, entry in sorted(eligible.items()):
        skeleton = producer.text_skeleton(str(entry["text_ko"]))
        for detector_id in result:
            hit, _ = producer.detector_hit(
                detector_id,
                item_id=item_id,
                entry=entry,
                trace_rows=trace_map[item_id],
                proposition_rows=proposition_map[item_id],
                skeleton_count=skeletons[skeleton],
                candidate_count=len(eligible),
                policy=policy,
            )
            if hit:
                result[detector_id].add(item_id)
    return result


def count_axis(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[key]) for row in rows).items()))


def classify_rule_ids(
    before: str,
    target_detector_ids: set[str],
) -> list[str]:
    rules: list[str] = []
    if "banned_internal_abstraction" in target_detector_ids:
        if re.search(r"작업 (?:차량|현장|장소|구역)", before):
            rules.append("work_acquisition_surface_fusion_v1")
        if "작업에서" in before:
            rules.append("work_context_concrete_action_fusion_v1")
        if re.search(r"작업에 (?:들어가는|필요한)", before):
            rules.append("work_nominal_role_fusion_v1")
        if "작업에 쓰는" in before or "나 작업에 함께 쓰는" in before:
            rules.append("work_use_adjunct_fusion_v1")
        if re.search(r"작업(?: 중|을 준비|으로|에도)", before):
            rules.append("work_case_role_realization_v1")
        if not rules:
            rules.append("work_grammar_fallback_v1")
    if "repeated_identity_noun_window" in target_detector_ids:
        rules.append("identity_use_terminal_zero_anaphora_v1")
    if "paragraph_fragmentation" in target_detector_ids:
        rules.append("minimum_fragment_form_fusion_v1")
    return sorted(set(rules))


def compiler_invalid_count(
    candidate: dict[str, Any],
    traces: list[dict[str, Any]],
    policy: dict[str, Any],
) -> int:
    allowed = set(policy["transformation_registry"])
    maximum = int(policy["compiler_invalid_patterns"]["maximum_sentence_characters"])
    count = 0
    for entry in candidate["entries"].values():
        if entry.get("source") != "korean_prose_candidate_v1":
            continue
        text = str(entry.get("text_ko") or "")
        if not text:
            count += 1
        count += sum(
            len(sentence.strip()) > maximum
            for sentence in re.split(r"[.!?]\s*", text)
            if sentence.strip()
        )
    count += sum(
        transformation not in allowed
        for row in traces
        for transformation in row.get("transformation_ids", [])
    )
    return count


def main() -> int:
    required = (
        CORRECTION_RECORD,
        OFFICIAL_DISPOSITION,
        OFFICIAL_FAILURE_LEDGER,
        BASELINE_CANDIDATE,
        BASELINE_TRACE,
        BASELINE_PROPOSITIONS,
        BASELINE_REQUIREMENTS,
        BASELINE_STRUCTURAL,
        producer.FACTS_PATH,
        producer.INPUT_MANIFEST,
        producer.DECISIONS_PATH,
        producer.POLICY_PATH,
    )
    missing = [repo_relative(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing bounded projection input: {missing}")

    input_checks = {
        "correction_record_sha256_match": (
            sha256_file(CORRECTION_RECORD) == EXPECTED["correction_record_sha256"]
        ),
        "official_disposition_immutable_sha256_match": (
            sha256_file(OFFICIAL_DISPOSITION)
            == EXPECTED["official_disposition_sha256"]
        ),
        "official_failure_ledger_immutable_sha256_match": (
            sha256_file(OFFICIAL_FAILURE_LEDGER)
            == EXPECTED["official_failure_ledger_sha256"]
        ),
        "baseline_candidate_sha256_match": (
            sha256_file(BASELINE_CANDIDATE)
            == EXPECTED["baseline_candidate_sha256"]
        ),
        "baseline_trace_sha256_match": (
            sha256_file(BASELINE_TRACE) == EXPECTED["baseline_trace_sha256"]
        ),
        "baseline_propositions_sha256_match": (
            sha256_file(BASELINE_PROPOSITIONS)
            == EXPECTED["baseline_propositions_sha256"]
        ),
        "baseline_requirements_sha256_match": (
            sha256_file(BASELINE_REQUIREMENTS)
            == EXPECTED["baseline_requirements_sha256"]
        ),
        "baseline_structural_sha256_match": (
            sha256_file(BASELINE_STRUCTURAL)
            == EXPECTED["baseline_structural_sha256"]
        ),
        "facts_sha256_match": (
            sha256_file(producer.FACTS_PATH) == EXPECTED["facts_sha256"]
        ),
        "manifest_sha256_match": (
            sha256_file(producer.INPUT_MANIFEST) == EXPECTED["manifest_sha256"]
        ),
    }
    if not all(input_checks.values()):
        raise RuntimeError(
            "bounded projection input identity mismatch: "
            + repr(sorted(key for key, passed in input_checks.items() if not passed))
        )

    baseline = load_json(BASELINE_CANDIDATE)
    baseline_traces = load_jsonl(BASELINE_TRACE)
    propositions = load_jsonl(BASELINE_PROPOSITIONS)
    facts = {
        str(row["item_id"]): row for row in load_jsonl(producer.FACTS_PATH)
    }
    trace_before = trace_by_item(baseline_traces)
    policy = load_json(producer.POLICY_PATH)
    before_hits = detector_hits(
        baseline,
        baseline_traces,
        propositions,
        policy,
    )
    target_before_ids = set().union(
        before_hits["banned_internal_abstraction"],
        before_hits["repeated_identity_noun_window"],
        before_hits["paragraph_fragmentation"],
    )

    classification_rows: list[dict[str, Any]] = []
    for item_id in sorted(before_hits["banned_internal_abstraction"]):
        entry = baseline["entries"][item_id]
        text = str(entry["text_ko"])
        item_facts = facts[item_id]
        cluster = item_facts.get("slot_meta", {}).get(
            "interaction_cluster", {}
        )
        sentences = SENTENCE_SPLIT.split(text)
        hit_indexes = [
            index for index, sentence in enumerate(sentences)
            if WORK_PATTERN.search(sentence)
        ]
        following = [
            sentences[index + 1] for index in hit_indexes
            if index + 1 < len(sentences)
        ]
        hit_actions = sorted(
            {
                action
                for index in hit_indexes
                for action in action_lexemes(sentences[index])
            }
        )
        following_actions = sorted(
            {action for sentence in following for action in action_lexemes(sentence)}
        )
        classification_rows.append(
            {
                "item_id": item_id,
                "fact_origin_primary_use": list(
                    item_facts.get("fact_origin", {}).get("primary_use", [])
                ),
                "resolved_profile": entry.get("resolved_profile"),
                "interaction_cluster_selected_cluster": cluster.get(
                    "selected_cluster"
                ),
                "interaction_cluster_selected_role": cluster.get("selected_role"),
                "realization_rule_ids": sorted(
                    {
                        str(row["realization_rule_id"])
                        for row in trace_before[item_id]
                        if WORK_PATTERN.search(str(row.get("text") or ""))
                    }
                ),
                "work_grammar": grammar_rows(text),
                "hit_sentence_count": len(hit_indexes),
                "hit_sentence_concrete_action_lexemes": hit_actions,
                "following_sentences": following,
                "following_sentence_concrete_action_lexemes": following_actions,
                "following_action_duplicate_lexemes": sorted(
                    set(hit_actions).intersection(following_actions)
                ),
                "following_action_duplicate": bool(
                    set(hit_actions).intersection(following_actions)
                ),
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "text_ko": text,
            }
        )

    build_candidate_rendered(
        facts_path=producer.FACTS_PATH,
        decisions_path=producer.DECISIONS_PATH,
        profiles_path=BODY_PLAN_PROFILES_PATH,
        identity_rules_path=IDENTITY_RULES_PATH,
        precedence_rules_path=PRECEDENCE_RULES_PATH,
        policy_path=producer.POLICY_PATH,
        source_proposition_inventory_path=BASELINE_PROPOSITIONS,
        body_plan_requirement_inventory_path=BASELINE_REQUIREMENTS,
        output_path=PROJECTED_CANDIDATE,
        trace_path=PROJECTED_TRACE,
        structural_path=PROJECTED_STRUCTURAL,
        proposition_resolution_path=PROJECTED_RESOLUTION,
        equivalence_proof_path=PROJECTED_PROOFS,
        attempt_root=DISPOSABLE_ROOT,
        compose_context=STAGING_COMPOSE_CONTEXT,
        expected_policy_sha256=sha256_file(producer.POLICY_PATH),
    )

    projected = load_json(PROJECTED_CANDIDATE)
    projected_traces = load_jsonl(PROJECTED_TRACE)
    after_hits = detector_hits(
        projected,
        projected_traces,
        propositions,
        policy,
    )
    changed_rows: list[dict[str, Any]] = []
    for item_id in sorted(baseline["entries"]):
        before_entry = baseline["entries"][item_id]
        after_entry = projected["entries"][item_id]
        before_text = before_entry.get("text_ko")
        after_text = after_entry.get("text_ko")
        if before_text == after_text:
            continue
        target_detector_ids = {
            detector_id
            for detector_id in (
                "banned_internal_abstraction",
                "repeated_identity_noun_window",
                "paragraph_fragmentation",
            )
            if item_id in before_hits[detector_id]
        }
        changed_rows.append(
            {
                "item_id": item_id,
                "expected_rule_ids": classify_rule_ids(
                    str(before_text or ""),
                    target_detector_ids,
                ),
                "before_detector_ids": sorted(target_detector_ids),
                "before_text_sha256": hashlib.sha256(
                    str(before_text or "").encode("utf-8")
                ).hexdigest(),
                "after_text_sha256": hashlib.sha256(
                    str(after_text or "").encode("utf-8")
                ).hexdigest(),
                "before_text_ko": before_text,
                "after_text_ko": after_text,
            }
        )

    changed_ids = {str(row["item_id"]) for row in changed_rows}
    rule_impacts: Counter[str] = Counter(
        rule_id
        for row in changed_rows
        for rule_id in row["expected_rule_ids"]
    )
    trace_after = trace_by_item(projected_traces)
    proposition_regression_ids = sorted(
        item_id
        for item_id in baseline["entries"]
        if {
            str(value)
            for row in trace_before.get(item_id, [])
            for value in row.get("proposition_ids", [])
        }
        != {
            str(value)
            for row in trace_after.get(item_id, [])
            for value in row.get("proposition_ids", [])
        }
    )
    baseline_unadopted = {
        item_id
        for item_id, entry in baseline["entries"].items()
        if entry.get("source") != "korean_prose_candidate_v1"
    }
    projected_unadopted = {
        item_id
        for item_id, entry in projected["entries"].items()
        if entry.get("source") != "korean_prose_candidate_v1"
    }
    other_new_hits = sorted(
        {
            (detector_id, item_id)
            for detector_id, item_ids in after_hits.items()
            for item_id in item_ids - before_hits[detector_id]
        }
    )
    code_text = (
        REPO_ROOT
        / "Iris"
        / "build"
        / "description"
        / "v2"
        / "tools"
        / "build"
        / "compose_layer3_identity.py"
    ).read_text(encoding="utf-8")
    item_specific_branch_count = len(set(re.findall(r"Base\.[A-Za-z0-9_]+", code_text)))
    checks = {
        "baseline_banned_internal_abstraction_is_673": (
            len(before_hits["banned_internal_abstraction"]) == 673
        ),
        "baseline_repeated_identity_noun_window_is_2": (
            len(before_hits["repeated_identity_noun_window"]) == 2
        ),
        "baseline_paragraph_fragmentation_is_1": (
            len(before_hits["paragraph_fragmentation"]) == 1
        ),
        "banned_internal_abstraction_zero": (
            len(after_hits["banned_internal_abstraction"]) == 0
        ),
        "repeated_identity_noun_window_zero": (
            len(after_hits["repeated_identity_noun_window"]) == 0
        ),
        "paragraph_fragmentation_zero": (
            len(after_hits["paragraph_fragmentation"]) == 0
        ),
        "all_other_raw_detector_new_hit_zero": not other_new_hits,
        "compiler_invalid_zero": (
            compiler_invalid_count(projected, projected_traces, policy) == 0
        ),
        "candidate_key_count_unchanged": (
            set(baseline["entries"]) == set(projected["entries"])
        ),
        "unadopted_count_and_members_unchanged": (
            baseline_unadopted == projected_unadopted
        ),
        "source_proposition_loss_or_addition_zero": not proposition_regression_ids,
        "structural_satisfaction_regression_zero": (
            sha256_file(PROJECTED_STRUCTURAL)
            == EXPECTED["baseline_structural_sha256"]
        ),
        "item_specific_branch_override_patch_zero": (
            item_specific_branch_count == 0
        ),
        "unexpected_text_change_zero": (
            changed_ids == target_before_ids
        ),
        "facts_unchanged": (
            sha256_file(producer.FACTS_PATH) == EXPECTED["facts_sha256"]
        ),
        "manifest_unchanged": (
            sha256_file(producer.INPUT_MANIFEST) == EXPECTED["manifest_sha256"]
        ),
    }

    aggregate_axes = {
        "fact_origin_primary_use": dict(
            sorted(
                Counter(
                    "|".join(row["fact_origin_primary_use"])
                    for row in classification_rows
                ).items()
            )
        ),
        "resolved_profile": count_axis(classification_rows, "resolved_profile"),
        "interaction_cluster_selected_cluster": count_axis(
            classification_rows,
            "interaction_cluster_selected_cluster",
        ),
        "interaction_cluster_selected_role": count_axis(
            classification_rows,
            "interaction_cluster_selected_role",
        ),
        "realization_rule_id": dict(
            sorted(
                Counter(
                    rule_id
                    for row in classification_rows
                    for rule_id in row["realization_rule_ids"]
                ).items()
            )
        ),
        "work_grammar": dict(
            sorted(
                Counter(
                    grammar["grammar_id"]
                    for row in classification_rows
                    for grammar in row["work_grammar"]
                ).items()
            )
        ),
        "following_action_duplicate": dict(
            sorted(
                Counter(
                    str(row["following_action_duplicate"]).lower()
                    for row in classification_rows
                ).items()
            )
        ),
    }
    failed = sorted(key for key, passed in checks.items() if not passed)
    report = {
        "schema_version": "dvf-3-3-publish-remediation-bounded-projection-v1",
        "status": "PASS" if not failed else "FAIL",
        "record_mode": "pre_attempt_disposable_non_authoritative_projection",
        "attempt_id_consumed": False,
        "authority_effect": "none",
        "start_commit": EXPECTED["start_commit"],
        "start_tree": EXPECTED["start_tree"],
        "correction_record": {
            "path": repo_relative(CORRECTION_RECORD),
            "sha256": sha256_file(CORRECTION_RECORD),
        },
        "immutable_official_attempt_evidence": {
            "attempt_id": "attempt-0004-official",
            "disposition_path": repo_relative(OFFICIAL_DISPOSITION),
            "disposition_sha256": sha256_file(OFFICIAL_DISPOSITION),
            "failure_ledger_path": repo_relative(OFFICIAL_FAILURE_LEDGER),
            "failure_ledger_sha256": sha256_file(OFFICIAL_FAILURE_LEDGER),
            "modified_or_recomputed": False,
        },
        "input_checks": input_checks,
        "classification": {
            "classified_item_count": len(classification_rows),
            "required_item_count": 673,
            "classification_ledger_path": repo_relative(CLASSIFICATION_LEDGER),
            "classification_ledger_sha256": None,
            "aggregate_axes": aggregate_axes,
        },
        "expected_rule_impact_counts": dict(sorted(rule_impacts.items())),
        "detector_before": {
            detector_id: len(item_ids)
            for detector_id, item_ids in sorted(before_hits.items())
        },
        "detector_after": {
            detector_id: len(item_ids)
            for detector_id, item_ids in sorted(after_hits.items())
        },
        "other_new_raw_detector_hits": [
            {"detector_id": detector_id, "item_id": item_id}
            for detector_id, item_id in other_new_hits
        ],
        "changed_item_count": len(changed_rows),
        "expected_changed_item_count": len(target_before_ids),
        "unexpected_changed_item_count": len(changed_ids - target_before_ids),
        "missing_expected_changed_item_count": len(target_before_ids - changed_ids),
        "changed_item_ledger_path": repo_relative(CHANGED_ITEM_LEDGER),
        "changed_item_ledger_sha256": None,
        "candidate_key_count_before": len(baseline["entries"]),
        "candidate_key_count_after": len(projected["entries"]),
        "unadopted_count_before": len(baseline_unadopted),
        "unadopted_count_after": len(projected_unadopted),
        "source_proposition_regression_count": len(proposition_regression_ids),
        "source_proposition_regression_item_ids": proposition_regression_ids,
        "structural_satisfaction_before_sha256": EXPECTED[
            "baseline_structural_sha256"
        ],
        "structural_satisfaction_after_sha256": sha256_file(PROJECTED_STRUCTURAL),
        "structural_satisfaction_regression_count": (
            0
            if sha256_file(PROJECTED_STRUCTURAL)
            == EXPECTED["baseline_structural_sha256"]
            else 1
        ),
        "compiler_invalid_count": compiler_invalid_count(
            projected,
            projected_traces,
            policy,
        ),
        "item_specific_branch_override_patch_count": item_specific_branch_count,
        "projected_candidate_path": repo_relative(PROJECTED_CANDIDATE),
        "projected_candidate_sha256": sha256_file(PROJECTED_CANDIDATE),
        "projected_trace_path": repo_relative(PROJECTED_TRACE),
        "projected_trace_sha256": sha256_file(PROJECTED_TRACE),
        "checks": checks,
        "failed_checks": failed,
        "scope_guards": {
            "facts_or_manifest_mutated": False,
            "policy_detector_or_threshold_mutated": False,
            "attempt_0023_modified_or_resumed": False,
            "attempt_0024_created": False,
            "official_publish_attempt_created_or_resumed": False,
            "live_gate_g1_g4_runtime_lua_package_mutated": False,
            "new_worktree_or_repository_clone_created": False,
        },
    }
    write_jsonl(CLASSIFICATION_LEDGER, classification_rows)
    write_jsonl(CHANGED_ITEM_LEDGER, changed_rows)
    report["classification"]["classification_ledger_sha256"] = sha256_file(
        CLASSIFICATION_LEDGER
    )
    report["changed_item_ledger_sha256"] = sha256_file(CHANGED_ITEM_LEDGER)
    write_json(REPORT, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "classified_item_count": len(classification_rows),
                "changed_item_count": len(changed_rows),
                "detector_before": report["detector_before"],
                "detector_after": report["detector_after"],
                "failed_checks": failed,
                "report_path": repo_relative(REPORT),
                "report_sha256": sha256_file(REPORT),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
