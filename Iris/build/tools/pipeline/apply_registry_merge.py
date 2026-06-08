#!/usr/bin/env python3
"""
apply_registry_merge.py  (Round 2)

accept 리스트를 읽어 use_case_registry.v2.4.json 수정.
registry 수정만 하고 종료 (재빌드 호출 금지).

== Round 2 검증 강화 ==
  - FAIL-LOUD: target_use_case_id가 기존 ID인지 확인 (신규 생성 금지)
  - FAIL-LOUD: rule_id 중복 소속 금지
  - Δ 지표 자동 산출

출력:
  - 수정된 use_case_registry.v2.4.json
  - 변경 요약 리포트 (stdout)
"""

import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parents[2]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from tools.common.versions import BUILD_VERSION

IRIS_DIR = BUILD_DIR.parent
DATA_DIR = BUILD_DIR / "data" / BUILD_VERSION
ACCEPT_PATH = DATA_DIR / f"registry_merge_accept.{BUILD_VERSION}.json"
REGISTRY_PATH = DATA_DIR / f"use_case_registry.{BUILD_VERSION}.json"
USECASES_PATH = IRIS_DIR / "output" / f"usecases_by_fulltype.{BUILD_VERSION}.json"

from tools.common.io import load_json, write_json


def main():
    print("=" * 60)
    print("apply_registry_merge.py  (Round 2)")
    print("=" * 60)

    # ── Accept 리스트 로드 ──
    if not ACCEPT_PATH.exists():
        print(f"  FAIL: {ACCEPT_PATH} not found")
        sys.exit(1)

    accept_list = load_json(ACCEPT_PATH)

    print(f"\n  Accept entries: {len(accept_list)}")

    # ── Registry 로드 ──
    if not REGISTRY_PATH.exists():
        print(f"  FAIL: {REGISTRY_PATH} not found")
        sys.exit(1)

    registry = load_json(REGISTRY_PATH)

    rules = registry["rules"]

    # ── BEFORE 지표 (Δ 산출용) ──
    before_ucids = set(r["use_case_id"] for r in rules.values())
    before_ucid_count = len(before_ucids)

    # usecases_by_fulltype에서 변경 전 라인 수 (있으면)
    before_entry_count = None
    if USECASES_PATH.exists():
        uc_data = load_json(USECASES_PATH)
        before_entry_count = sum(
            len(ft_data.get("use_cases", []))
            for ft_data in uc_data.get("fulltypes", {}).values()
        )

    # ══════════════════════════════════════════════════════════════
    #  FAIL-LOUD 검증
    # ══════════════════════════════════════════════════════════════

    # 1) 모든 rule_id가 registry에 존재하는지
    all_accept_rule_ids = []
    for entry in accept_list:
        for rid in entry["merge_rule_ids"]:
            if rid not in rules:
                print(f"  FAIL-LOUD: rule_id '{rid}' not found in registry")
                sys.exit(1)
            all_accept_rule_ids.append(rid)

    # 2) target_use_case_id가 기존에 존재하는 ID인지 (신규 생성 금지)
    existing_ucids = set(r["use_case_id"] for r in rules.values())
    for entry in accept_list:
        target = entry["target_use_case_id"]
        if target not in existing_ucids:
            print(f"  FAIL-LOUD: target_use_case_id '{target}' does not exist in registry (신규 생성 금지)")
            sys.exit(1)

    # 3) 한 rule_id가 여러 merge 그룹에 포함되면 FAIL
    seen_rule_ids: dict[str, int] = {}
    for i, entry in enumerate(accept_list):
        for rid in entry["merge_rule_ids"]:
            if rid in seen_rule_ids:
                print(f"  FAIL-LOUD: rule_id '{rid}' appears in entries [{seen_rule_ids[rid]}] and [{i}]")
                sys.exit(1)
            seen_rule_ids[rid] = i

    print("  FAIL-LOUD checks: ALL PASSED")

    # ══════════════════════════════════════════════════════════════
    #  적용
    # ══════════════════════════════════════════════════════════════
    changes = []

    for entry in accept_list:
        merge_rule_ids = entry["merge_rule_ids"]
        target_ucid = entry["target_use_case_id"]

        for rule_id in merge_rule_ids:
            old_ucid = rules[rule_id]["use_case_id"]
            if old_ucid == target_ucid:
                continue

            rules[rule_id]["use_case_id"] = target_ucid
            changes.append({
                "rule_id": rule_id,
                "old_use_case_id": old_ucid,
                "new_use_case_id": target_ucid,
            })

    # ── 변경 요약 ──
    if not changes:
        print("\n  No changes needed (already converged or no matching rules)")
        print("=" * 60)
        return

    print(f"\n  Changes applied: {len(changes)}")
    for c in changes:
        print(f"    {c['rule_id']}: {c['old_use_case_id']} -> {c['new_use_case_id']}")

    # ── Registry 저장 ──
    write_json(REGISTRY_PATH, registry, indent=4, trailing_newline=False)

    print(f"\n  Written: {REGISTRY_PATH}")

    # ══════════════════════════════════════════════════════════════
    #  Δ 지표 산출
    # ══════════════════════════════════════════════════════════════
    after_ucids = set(r["use_case_id"] for r in rules.values())
    after_ucid_count = len(after_ucids)

    absorbed_ucids = before_ucids - after_ucids
    orphaned = set(c["old_use_case_id"] for c in changes) - after_ucids

    print(f"\n  ── Δ Metrics ──")
    print(f"  distinct_use_case_id: {before_ucid_count} -> {after_ucid_count} (Δ={after_ucid_count - before_ucid_count})")
    if before_entry_count is not None:
        print(f"  use_case_entry_count (before rebuild): {before_entry_count} (will change after rebuild)")
    if absorbed_ucids:
        print(f"  absorbed use_case_ids: {sorted(absorbed_ucids)}")
    if orphaned:
        print(f"  orphaned use_case_ids (no longer in registry): {sorted(orphaned)}")
        print("  -> These will become 'extra' in label_map (warning only)")

    print("\n  NEXT STEPS (manual):")
    print("    1. python build/use_case_integrator.py")
    print("    2. python build/description_generator.py")
    print("    3. python build/convert_descriptions_to_lua.py")
    print("    4. python build/convert_labelmap_to_lua.py")
    print("    5. python build/tests/test_description_generator.py")

    print("\n" + "=" * 60)
    print("SUCCESS: Registry merge applied (Round 2)")
    print("=" * 60)


if __name__ == "__main__":
    main()
