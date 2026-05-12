"""
수렴 후보 사전 분석 (Planning용)

usecases_by_fulltype에서:
1. 각 use_case_id의 matched fulltype 집합 추출
2. fulltype 집합이 동일하거나 매우 유사한 use_case_id 쌍 탐지
3. 항상 같이 등장하는 use_case_id 쌍 탐지 (co-occurrence)
"""
import json
from pathlib import Path
from itertools import combinations

USECASES_PATH = Path("output/usecases_by_fulltype.v2.4.json")
REGISTRY_PATH = Path("build/data/v2.4/use_case_registry.v2.4.json")

def main():
    with open(USECASES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        registry = json.load(f)

    fulltypes = data["fulltypes"]

    # 1) use_case_id → set of fulltypes
    ucid_to_fulltypes: dict[str, set[str]] = {}
    # 2) fulltype → set of use_case_ids (for co-occurrence)
    ft_to_ucids: dict[str, set[str]] = {}

    for ft, ft_data in fulltypes.items():
        for uc in ft_data.get("use_cases", []):
            ucid = uc["use_case_id"]
            if ucid not in ucid_to_fulltypes:
                ucid_to_fulltypes[ucid] = set()
            ucid_to_fulltypes[ucid].add(ft)

            if ft not in ft_to_ucids:
                ft_to_ucids[ft] = set()
            ft_to_ucids[ft].add(ucid)

    print("=" * 70)
    print("1) use_case_id별 매칭 fulltype 수")
    print("=" * 70)
    for ucid in sorted(ucid_to_fulltypes.keys()):
        print(f"  {ucid}: {len(ucid_to_fulltypes[ucid])} fulltypes")

    # 3) Jaccard 유사도 계산 (모든 쌍)
    print("\n" + "=" * 70)
    print("2) Jaccard >= 0.8인 use_case_id 쌍")
    print("=" * 70)
    all_ucids = sorted(ucid_to_fulltypes.keys())
    high_sim_pairs = []
    for a, b in combinations(all_ucids, 2):
        set_a = ucid_to_fulltypes[a]
        set_b = ucid_to_fulltypes[b]
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        jaccard = intersection / union if union > 0 else 0
        if jaccard >= 0.8:
            high_sim_pairs.append((a, b, jaccard, intersection, union))

    if high_sim_pairs:
        for a, b, j, inter, union in sorted(high_sim_pairs, key=lambda x: -x[2]):
            print(f"  {a} <-> {b}")
            print(f"    Jaccard={j:.4f}  intersection={inter}  union={union}")
    else:
        print("  (없음)")

    # 4) 항상 같이 등장하는 쌍 (co-occurrence = 100%)
    print("\n" + "=" * 70)
    print("3) 항상 같이 등장하는 use_case_id 쌍 (support(A) == support(B))")
    print("=" * 70)
    cooccur_pairs = []
    for a, b in combinations(all_ucids, 2):
        set_a = ucid_to_fulltypes[a]
        set_b = ucid_to_fulltypes[b]
        if set_a == set_b:
            cooccur_pairs.append((a, b, len(set_a)))

    if cooccur_pairs:
        for a, b, count in cooccur_pairs:
            print(f"  {a} == {b}  ({count} fulltypes)")
    else:
        print("  (완전 동일 집합 없음)")

    # 5) 부분집합 관계 (A의 전체가 B에 포함)
    print("\n" + "=" * 70)
    print("4) 부분집합 관계 (support(A) <= support(B), |A| >= 5)")
    print("=" * 70)
    subset_pairs = []
    for a, b in combinations(all_ucids, 2):
        set_a = ucid_to_fulltypes[a]
        set_b = ucid_to_fulltypes[b]
        if len(set_a) >= 5 and set_a <= set_b:
            subset_pairs.append((a, b, len(set_a), len(set_b)))
        elif len(set_b) >= 5 and set_b <= set_a:
            subset_pairs.append((b, a, len(set_b), len(set_a)))

    if subset_pairs:
        for sub, sup, sub_c, sup_c in sorted(subset_pairs, key=lambda x: -x[2]):
            print(f"  {sub} ({sub_c}) <= {sup} ({sup_c})")
    else:
        print("  (없음)")

    # 6) registry에서 "같은 use_case_id를 공유하는 rule 그룹"
    print("\n" + "=" * 70)
    print("5) 동일 use_case_id에 매핑된 rule_id 그룹")
    print("=" * 70)
    ucid_to_rules: dict[str, list[str]] = {}
    for rule_id, rule_data in registry["rules"].items():
        ucid = rule_data["use_case_id"]
        if ucid not in ucid_to_rules:
            ucid_to_rules[ucid] = []
        ucid_to_rules[ucid].append(rule_id)

    for ucid in sorted(ucid_to_rules.keys()):
        rules = ucid_to_rules[ucid]
        if len(rules) > 1:
            print(f"  {ucid}: {rules}")

    # 7) 총 행동 라인 수
    total_lines = sum(len(ft_data.get("use_cases", [])) for ft_data in fulltypes.values())
    unique_fulltypes = len(fulltypes)
    print(f"\n총 fulltype 수: {unique_fulltypes}")
    print(f"총 행동 라인 수: {total_lines}")
    print(f"평균 행동 라인/fulltype: {total_lines/unique_fulltypes:.2f}")

if __name__ == "__main__":
    main()
