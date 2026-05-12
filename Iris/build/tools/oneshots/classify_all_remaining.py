"""
전체 미분류 아이템 일괄 분류 스크립트
==================================
- 소분류 태그가 있는 아이템: 모두 silent 처리
- 태그 없는 시스템 아이템(Bandage_, Wound_, ZedDmg_, MakeUp_ 등): silent
- SharpedStone: active (원시 도구 재료 — Tool.1-B 분석 결과)
- TinOpener: 이미 등록됨 (확인만)
- 특수 아이템(Corpse, MetalDrum 등): silent
"""
import json
from pathlib import Path
from collections import Counter

IRIS = Path("c:/Users/MW/Downloads/coding/PZ/Iris")

# === 데이터 로드 ===
tags_data = json.loads((IRIS / "output/tags_by_fulltype.json").read_text("utf-8")).get("items", {})
items_data = json.loads((IRIS / "input/items_itemscript.json").read_text("utf-8"))
unreg_list = [l.strip() for l in (IRIS / "output/layer3_unregistered.txt").read_text("utf-8").splitlines() if l.strip()]
unreg_set = set(unreg_list)

reg_path = IRIS / "build/data/description/layer3_registry.json"
reg = json.loads(reg_path.read_text("utf-8"))
existing = {e["fulltype"] for e in reg["entries"]}

# === Step 1: 분석 — 미등록 아이템의 1차 태그별 분포 ===
tag_count = Counter()
for ft in unreg_list:
    ft_tags = tags_data.get(ft, [])
    primary = ft_tags[0] if ft_tags else "(no tag)"
    tag_count[primary] += 1

print("=== 미등록 아이템 1차 태그별 분포 ===")
for tag, cnt in sorted(tag_count.items(), key=lambda x: -x[1]):
    print(f"  {tag}: {cnt}")
print(f"  ---")
print(f"  총 미등록: {len(unreg_list)}")
print()

# === Step 2: active 등록 대상 ===
ACTIVE_ITEMS = {
    "Base.SharpedStone": {
        "kind": "primitive_crafting",
        "text_ko": "원시 생존 도구의 핵심 재료. 돌칼·돌도끼 제작에 사용하며, 캔 따개 없이 캔 음식을 열 수 있는 대체 도구.",
        "anchors": ["Tool.1-B"],
        "notes": "Tool.1-B 심층 분석 판정: 원시 제작 생태계 핵심 재료"
    }
}

# === Step 3: 전체 소분류 일괄 silent 대상 ===
# 모든 소분류 태그를 포함 — 태그가 있는 미등록 아이템은 모두 silent
# 이미 등록된 아이템은 건너뜀

# === Step 4: 태그 없는 아이템 분류 규칙 ===
# Bandage_* → 시스템 렌더링용 → silent
# Wound_* → 시스템 렌더링용 → silent
# ZedDmg_* → 좀비 데미지 텍스처 → silent
# MakeUp_* → 캐릭터 메이크업 → silent
# *_Hair_Stubble, F_Hair_Stubble → 캐릭터 외모 → silent
# CorpseFemale/Male → 시체 오브젝트 → silent
# MetalDrum, Mirror, Stairs, WaterDrop → 시스템/환경 오브젝트 → silent


# === 등록 실행 ===
added_active = 0
added_silent = 0 
skipped = 0
per_tag = Counter()

for ft in sorted(unreg_list):
    if ft in existing:
        skipped += 1
        continue

    # active 대상 확인
    if ft in ACTIVE_ITEMS:
        info = ACTIVE_ITEMS[ft]
        reg["entries"].append({
            "fulltype": ft,
            "status": "active",
            "kind": info["kind"],
            "text_ko": info["text_ko"],
            "anchors": info["anchors"],
            "notes": info["notes"]
        })
        added_active += 1
        existing.add(ft)
        print(f"  [ACTIVE] {ft}")
        continue

    # 태그가 있는 아이템 → silent
    ft_tags = tags_data.get(ft, [])
    if ft_tags:
        primary = ft_tags[0]
        reg["entries"].append({
            "fulltype": ft,
            "status": "silent",
            "kind": None,
            "text_ko": None,
            "anchors": [],
            "notes": f"소분류 일괄 silent: {primary}"
        })
        added_silent += 1
        per_tag[primary] += 1
        existing.add(ft)
        continue

    # 태그 없는 아이템 → 시스템 패턴 매칭
    basename = ft.split(".")[-1] if "." in ft else ft
    
    system_patterns = [
        "Bandage_", "Wound_", "ZedDmg_", "MakeUp_",
        "Hair_Stubble", "Beard_Stubble"
    ]
    system_exact = [
        "Base.CorpseFemale", "Base.CorpseMale",
        "Base.MetalDrum", "Base.Mirror", "Base.Stairs", "Base.WaterDrop"
    ]
    
    is_system = False
    for pat in system_patterns:
        if pat in basename:
            is_system = True
            break
    if ft in system_exact:
        is_system = True
        
    if is_system:
        reg["entries"].append({
            "fulltype": ft,
            "status": "silent",
            "kind": None,
            "text_ko": None,
            "anchors": [],
            "notes": "시스템/렌더링 전용 아이템 — silent"
        })
        added_silent += 1
        per_tag["(system)"] += 1
        existing.add(ft)
        continue

    # 나머지 — 미분류 (이런 케이스는 수동 확인 필요)
    print(f"  [UNHANDLED] {ft} tags={ft_tags}")

# === 저장 ===
reg_path.write_text(json.dumps(reg, indent=4, ensure_ascii=False), encoding="utf-8")

total = len(reg["entries"])
print()
print("=" * 60)
print(f"추가 active: {added_active}개")
print(f"추가 silent: {added_silent}개")
print(f"건너뜀 (이미 등록): {skipped}개")
print(f"총 엔트리: {total}개")
print()
print("=== 태그별 추가 현황 ===")
for tag, cnt in sorted(per_tag.items(), key=lambda x: -x[1]):
    print(f"  {tag}: {cnt}")
