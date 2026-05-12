#!/usr/bin/env python3
"""
extract_merge_candidates.py  (Round 2)

usecases_by_fulltype + use_case_registry에서
수렴 후보를 자동 추출 (정적 집합 비교만, 의미 추론 금지).

== 등급 기준 ==
  A) 부분집합 + co-occurrence 100% + delta ≤ 2
  B) Jaccard ≥ 0.97 AND min(support) ≥ 20
  C) Jaccard ≥ 0.95 (관찰 전용, 적용 안 함)

== 안전 장치 ==
  - legacy=true rule 제외
  - 동일 source_type끼리만 비교
  - 대표 선택: label_map 존재 우선 → 사전순 최소

출력: registry_merge_candidates.v2.4.json
"""

import json
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parents[2]
IRIS_DIR = BUILD_DIR.parent
DATA_DIR = BUILD_DIR / "data" / "v2.4"
USECASES_PATH = IRIS_DIR / "output" / "usecases_by_fulltype.v2.4.json"
REGISTRY_PATH = DATA_DIR / "use_case_registry.v2.4.json"
LABELMAP_PATH = DATA_DIR / "usecase_label_map.json"
OUTPUT_PATH = DATA_DIR / "registry_merge_candidates.v2.4.json"

# 등급 컷
GRADE_A_DELTA_MAX = 2
GRADE_B_JACCARD_MIN = 0.97
GRADE_B_SUPPORT_MIN = 20
GRADE_C_JACCARD_MIN = 0.95


def classify_source_type(rule_id: str) -> str:
    """rule_id에서 source_type 추론 (정적 네이밍 규칙)."""
    if rule_id.startswith("rule_"):
        return "rightclick"
    elif rule_id.startswith("Tool.") or rule_id.startswith("Resource."):
        return "classification_recipe"
    return "unknown"


def main():
    print("=" * 60)
    print("extract_merge_candidates.py  (Round 2)")
    print("=" * 60)

    # ── 데이터 로드 ──
    with open(USECASES_PATH, encoding="utf-8") as f:
        usecases = json.load(f)
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        registry = json.load(f)

    # label_map 로드 (대표 선택용)
    labelmap_ucids: set[str] = set()
    if LABELMAP_PATH.exists():
        with open(LABELMAP_PATH, encoding="utf-8") as f:
            lm = json.load(f)
        labelmap_ucids = set(lm.get("labels", {}).keys())

    fulltypes = usecases["fulltypes"]
    rules = registry["rules"]

    # ── rule_id → support set (fulltype 집합) ──
    # rule_id는 use_case_id를 경유하여 fulltype에 매칭됨
    rule_to_fts: dict[str, set[str]] = {}
    for ft, ft_data in fulltypes.items():
        for uc in ft_data.get("use_cases", []):
            for src in uc.get("evidence_sources", []):
                rid = src.get("rule_id")
                if rid:
                    rule_to_fts.setdefault(rid, set()).add(ft)

    # ── 필터링: legacy 제외, registry에 존재하는 rule만 ──
    active_rule_ids = []
    for rule_id in sorted(rule_to_fts.keys()):
        if rule_id not in rules:
            continue
        rule_data = rules[rule_id]
        if rule_data.get("legacy", False):
            print(f"  SKIP (legacy): {rule_id}")
            continue
        active_rule_ids.append(rule_id)

    print(f"\n  Active rules for comparison: {len(active_rule_ids)}")

    # ── 역색인: fulltype → [rule_ids] (교집합이 1+ 인 pair만 탐색) ──
    ft_to_rules: dict[str, list[str]] = {}
    for rid in active_rule_ids:
        for ft in rule_to_fts[rid]:
            ft_to_rules.setdefault(ft, []).append(rid)

    # ── 후보 pair 탐색 (역색인으로 효율적 탐색) ──
    candidate_pairs: set[tuple[str, str]] = set()
    for ft, ft_rules in ft_to_rules.items():
        if len(ft_rules) < 2:
            continue
        for i in range(len(ft_rules)):
            for j in range(i + 1, len(ft_rules)):
                a, b = ft_rules[i], ft_rules[j]
                pair = (min(a, b), max(a, b))
                candidate_pairs.add(pair)

    print(f"  Candidate pairs (intersection>=1): {len(candidate_pairs)}")

    # ── 각 pair에 대해 등급 계산 ──
    candidates = []
    group_counter = 0

    for a, b in sorted(candidate_pairs):
        # source_type 분리: 동일 source_type끼리만
        st_a = classify_source_type(a)
        st_b = classify_source_type(b)
        if st_a != st_b:
            continue

        set_a = rule_to_fts[a]
        set_b = rule_to_fts[b]
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        jaccard = intersection / union if union > 0 else 0
        subset_a_in_b = set_a <= set_b
        subset_b_in_a = set_b <= set_a
        delta = abs(len(set_a) - len(set_b))
        support_min = min(len(set_a), len(set_b))

        # ── 등급 판정 ──
        grade = None
        reasons = []

        # A등급: 부분집합 + co-occurrence 100% + delta ≤ 2
        if (subset_a_in_b or subset_b_in_a) and delta <= GRADE_A_DELTA_MAX:
            grade = "A"
            if subset_a_in_b:
                reasons.append("subset_a_in_b")
            if subset_b_in_a:
                reasons.append("subset_b_in_a")
            reasons.append(f"delta={delta}")
            if set_a == set_b:
                reasons.append("co_occurrence_100%")

        # B등급: Jaccard ≥ 0.97 AND support ≥ 20
        if grade is None and jaccard >= GRADE_B_JACCARD_MIN and support_min >= GRADE_B_SUPPORT_MIN:
            grade = "B"
            reasons.append(f"jaccard_{jaccard:.4f}")
            reasons.append(f"support_min={support_min}")

        # C등급: Jaccard ≥ 0.95
        if grade is None and jaccard >= GRADE_C_JACCARD_MIN:
            grade = "C"
            reasons.append(f"jaccard_{jaccard:.4f}")

        if grade is None:
            continue

        # ── 대표 use_case_id 선택 ──
        ucid_a = rules[a]["use_case_id"]
        ucid_b = rules[b]["use_case_id"]

        # 더 큰 support 쪽이 target (subset 방향 규칙)
        if len(set_a) >= len(set_b):
            primary, secondary = ucid_a, ucid_b
        else:
            primary, secondary = ucid_b, ucid_a

        # label_map 우선 → 사전순
        if primary in labelmap_ucids and secondary not in labelmap_ucids:
            proposed_target = primary
        elif secondary in labelmap_ucids and primary not in labelmap_ucids:
            proposed_target = secondary
        else:
            proposed_target = min(primary, secondary)

        group_counter += 1
        candidate = {
            "group_id": f"cand_{group_counter:06d}",
            "rule_ids": [a, b],
            "use_case_ids": [ucid_a, ucid_b],
            "stats": {
                "support_a": len(set_a),
                "support_b": len(set_b),
                "intersection": intersection,
                "union": union,
                "jaccard": round(jaccard, 4),
                "subset_a_in_b": subset_a_in_b,
                "subset_b_in_a": subset_b_in_a,
                "delta": delta,
            },
            "grade": grade,
            "reason": reasons,
            "source_type": st_a,
            "proposed_target_use_case_id": proposed_target,
        }
        candidates.append(candidate)

    # ── 결정성 정렬: grade(A>B>C) → -jaccard → -support_min → lex ──
    grade_order = {"A": 0, "B": 1, "C": 2}
    candidates.sort(key=lambda c: (
        grade_order.get(c["grade"], 99),
        -c["stats"]["jaccard"],
        -min(c["stats"]["support_a"], c["stats"]["support_b"]),
        c["proposed_target_use_case_id"],
        tuple(c["rule_ids"]),
    ))

    # ── 출력 ──
    output = {
        "version": "v2.4",
        "round": 2,
        "grade_criteria": {
            "A": f"subset + co_occurrence + delta<={GRADE_A_DELTA_MAX}",
            "B": f"jaccard>={GRADE_B_JACCARD_MIN} AND support>={GRADE_B_SUPPORT_MIN}",
            "C": f"jaccard>={GRADE_C_JACCARD_MIN} (observe only)",
        },
        "candidate_count": len(candidates),
        "grade_summary": {
            "A": sum(1 for c in candidates if c["grade"] == "A"),
            "B": sum(1 for c in candidates if c["grade"] == "B"),
            "C": sum(1 for c in candidates if c["grade"] == "C"),
        },
        "candidates": candidates,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Candidates found: {len(candidates)}")
    for grade_label in ["A", "B", "C"]:
        grade_items = [c for c in candidates if c["grade"] == grade_label]
        if grade_items:
            print(f"\n  ── Grade {grade_label} ({len(grade_items)}) ──")
            for c in grade_items:
                print(f"    [{c['group_id']}] {c['rule_ids']}")
                print(f"      J={c['stats']['jaccard']}, grade={c['grade']}, reasons={c['reason']}")
                print(f"      proposed_target={c['proposed_target_use_case_id']}")

    print(f"\n  Written: {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
