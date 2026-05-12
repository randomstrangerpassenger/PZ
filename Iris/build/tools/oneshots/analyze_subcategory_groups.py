"""
소분류별 그룹 분석 — active/silent 판정 보조 자료 생성
=====================================================
각 소분류(Primary Subcategory)의 미등록 아이템들을 게임 데이터 기반으로 분석하여,
사람이 그룹 단위로 active/silent 판정을 내릴 때 참고할 수 있는 요약을 만든다.

**자동 판정은 하지 않는다.** 출력물은 판정용 워크시트다.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Paths
IRIS_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = IRIS_DIR / "output"
INPUT_DIR = IRIS_DIR / "input"
ARTIFACT_DIR = IRIS_DIR / "evidence" / "analysis"

UNREG_FILE = OUTPUT_DIR / "layer3_unregistered.txt"
TAGS_FILE = OUTPUT_DIR / "tags_by_fulltype.json"
ITEMS_FILE = INPUT_DIR / "items_itemscript.json"
REGISTRY_FILE = IRIS_DIR / "build" / "data" / "description" / "layer3_registry.json"

# 태그 한국어 이름
TAG_NAMES = {
    # Tool (도구) — Iris_ko.txt 기준
    "Tool.1-A": "건설/제작", "Tool.1-B": "분해/개방", "Tool.1-C": "정비",
    "Tool.1-D": "요리", "Tool.1-E": "농업/채집", "Tool.1-F": "의료",
    "Tool.1-G": "포획", "Tool.1-H": "광원/점화", "Tool.1-I": "통신",
    "Tool.1-J": "전력", "Tool.1-K": "보안", "Tool.1-L": "보관용기",
    # Combat (전투)
    "Combat.2-A": "도끼류", "Combat.2-B": "장둔기", "Combat.2-C": "단둔기",
    "Combat.2-D": "장검류", "Combat.2-E": "단검류", "Combat.2-F": "창류",
    "Combat.2-G": "권총", "Combat.2-H": "소총", "Combat.2-I": "산탄총",
    "Combat.2-J": "투척/폭발", "Combat.2-K": "탄약", "Combat.2-L": "총기부품",
    # Consumable (소모품)
    "Consumable.3-A": "식품", "Consumable.3-B": "음료", "Consumable.3-C": "의약품",
    "Consumable.3-D": "기호품", "Consumable.3-E": "약초",
    # Resource (자원)
    "Resource.4-A": "건설 재료", "Resource.4-B": "조리 재료",
    "Resource.4-C": "의료 재료", "Resource.4-D": "연료",
    "Resource.4-E": "전자부품", "Resource.4-F": "기타 재료",
    # Literature (문헌)
    "Literature.5-A": "스킬북", "Literature.5-B": "레시피잡지",
    "Literature.5-C": "지도", "Literature.5-D": "일반 서적",
    # Wearable (의류)
    "Wearable.6-A": "모자/헬멧", "Wearable.6-B": "상의", "Wearable.6-C": "하의",
    "Wearable.6-D": "장갑", "Wearable.6-E": "신발", "Wearable.6-F": "배낭",
    "Wearable.6-G": "액세서리",
    # Furniture (가구)
    "Furniture.7-A": "탈착 가구",
    # Vehicle (차량)
    "Vehicle.8-A": "주행계", "Vehicle.8-B": "차체/부속",
    # Misc (기타)
    "Misc.9-A": "잡화",
}


def detect_variant_families(fulltypes: list[str]) -> dict[str, list[str]]:
    """이름 패턴 기반으로 변형군(variant family)을 감지한다."""
    families = defaultdict(list)
    for ft in fulltypes:
        # Base.SomethingRed, Base.SomethingBlue → Base.Something
        # Base.Shirt_FormalWhite → Base.Shirt_Formal
        base = ft
        # 색상 접미사 제거
        base = re.sub(r'(Red|Blue|Green|White|Black|Brown|Grey|Pink|Purple|Orange|Yellow|Beige|Camo|Olive|Tan)$', '', base)
        # 크기/상태 접미사 제거
        base = re.sub(r'(Small|Large|Big|Full|Empty|Open|Dirty|Clean|Burnt|Cooked|Rotten|Frozen|Raw)$', '', base)
        # 숫자 접미사 제거
        base = re.sub(r'\d+$', '', base)
        # 후행 _ 정리
        base = base.rstrip('_')
        families[base].append(ft)
    return {k: v for k, v in families.items() if len(v) > 1}


def analyze_group_properties(fulltypes: list[str], items_data: dict) -> dict:
    """그룹 내 아이템들의 게임 속성 패턴을 요약한다."""
    types = Counter()
    display_cats = Counter()
    has_tags = Counter()
    unique_properties = set()

    for ft in fulltypes:
        item = items_data.get(ft, {})
        types[item.get("Type", "?")] += 1
        dc = item.get("DisplayCategory", "?")
        display_cats[dc] += 1

        tags_str = item.get("Tags", "")
        if tags_str:
            for tag in tags_str.split(";"):
                tag = tag.strip()
                if tag:
                    has_tags[tag] += 1

        # 고유 속성 감지
        for key in item.keys():
            if key not in ("DisplayCategory", "DisplayName", "FullType", "Type", "Weight",
                           "Tags", "Icon", "WorldStaticModel", "StaticModel",
                           "IconsForTexture", "ClothingItem", "BodyLocation"):
                unique_properties.add(key)

    return {
        "types": dict(types.most_common()),
        "display_categories": dict(display_cats.most_common()),
        "top_tags": dict(has_tags.most_common(8)),
        "unique_property_count": len(unique_properties),
        "sample_unique_properties": sorted(unique_properties)[:10],
    }


def main():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    unregistered = [l.strip() for l in UNREG_FILE.read_text("utf-8").splitlines() if l.strip()]
    tags_data = json.loads(TAGS_FILE.read_text("utf-8")).get("items", {})
    items_data = json.loads(ITEMS_FILE.read_text("utf-8"))
    registry = json.loads(REGISTRY_FILE.read_text("utf-8"))

    # 이미 등록된 아이템 집계
    registered_active = set()
    registered_silent = set()
    for entry in registry.get("entries", []):
        ft = entry.get("fulltype", "")
        if entry.get("status") == "active":
            registered_active.add(ft)
        elif entry.get("status") == "silent":
            registered_silent.add(ft)

    # 소분류별 그룹핑 — 전체 태그(1차+2차 모두) 기반
    groups = defaultdict(list)
    no_tag = []
    for ft in unregistered:
        tags = tags_data.get(ft, [])
        if tags:
            for tag in tags:
                groups[tag].append(ft)
        else:
            no_tag.append(ft)

    out_path = ARTIFACT_DIR / "subcategory_analysis.md"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# 소분류별 그룹 분석 — Active/Silent 판정 워크시트\n\n")
        f.write(f"**미등록**: {len(unregistered)}개 | ")
        f.write(f"**기등록 active**: {len(registered_active)}개 | ")
        f.write(f"**기등록 silent**: {len(registered_silent)}개\n\n")
        f.write("---\n\n")
        f.write("> 이 문서는 **판정 보조 자료**입니다. 최종 active/silent 판정은 사람이 내립니다.\n")
        f.write("> 각 소분류별로 아이템군의 특성을 분석하고, 변형군(색상/크기 등)을 감지했습니다.\n\n")

        for tag in sorted(groups.keys()):
            fulltypes = groups[tag]
            tag_name = TAG_NAMES.get(tag, tag)
            f.write(f"## {tag} — {tag_name} ({len(fulltypes)}개)\n\n")

            # 게임 속성 분석
            props = analyze_group_properties(fulltypes, items_data)

            f.write(f"**Type**: {props['types']}  \n")
            f.write(f"**DisplayCategory**: {props['display_categories']}  \n")

            if props["top_tags"]:
                f.write(f"**주요 Tags**: {props['top_tags']}  \n")

            f.write(f"**고유 속성 수**: {props['unique_property_count']}개")
            if props["sample_unique_properties"]:
                f.write(f" — {', '.join(props['sample_unique_properties'][:6])}")
            f.write("\n\n")

            # 변형군 감지
            families = detect_variant_families(fulltypes)
            if families:
                big_families = {k: v for k, v in families.items() if len(v) >= 3}
                if big_families:
                    f.write("**변형군 감지** (3개 이상):\n")
                    for base, members in sorted(big_families.items(), key=lambda x: -len(x[1])):
                        short_base = base.split(".")[-1] if "." in base else base
                        f.write(f"- `{short_base}` × {len(members)}: {', '.join(m.split('.')[-1] for m in members[:5])}")
                        if len(members) > 5:
                            f.write(f" ... +{len(members) - 5}")
                        f.write("\n")
                    f.write("\n")

            # 아이템 목록 (50개 이하면 전체, 초과하면 샘플)
            if len(fulltypes) <= 50:
                f.write("<details><summary>전체 아이템 목록</summary>\n\n")
                for ft in sorted(fulltypes):
                    dn = items_data.get(ft, {}).get("DisplayName", "?")
                    f.write(f"- `{ft}` — {dn}\n")
                f.write("\n</details>\n\n")
            else:
                f.write(f"<details><summary>아이템 목록 (샘플 30/{len(fulltypes)})</summary>\n\n")
                for ft in sorted(fulltypes)[:30]:
                    dn = items_data.get(ft, {}).get("DisplayName", "?")
                    f.write(f"- `{ft}` — {dn}\n")
                f.write(f"\n... +{len(fulltypes) - 30} more\n\n</details>\n\n")

            # 판정 란 (사람이 채우는 공간)
            f.write("**판정**: `[ ]` 전체 silent | `[ ]` 전체 active | `[ ]` 개별 판정 필요\n\n")
            f.write("---\n\n")

        # 태그 없는 아이템
        if no_tag:
            f.write(f"## 미분류 (태그 없음) ({len(no_tag)}개)\n\n")
            for ft in sorted(no_tag):
                dn = items_data.get(ft, {}).get("DisplayName", "?")
                f.write(f"- `{ft}` — {dn}\n")
            f.write("\n**판정**: `[ ]` 전체 silent | `[ ]` 개별 판정 필요\n\n")

    print(f"✅ 분석 완료: {out_path}")
    print(f"   소분류 그룹: {len(groups)}개")
    print(f"   미분류(태그 없음): {len(no_tag)}개")

    # 그룹 크기별 요약
    print("\n   그룹 크기 요약:")
    for tag in sorted(groups.keys()):
        cnt = len(groups[tag])
        name = TAG_NAMES.get(tag, tag)
        bar = "█" * (cnt // 10) + ("▌" if cnt % 10 >= 5 else "")
        print(f"   {tag:20s} ({name:15s}): {cnt:4d} {bar}")


if __name__ == "__main__":
    main()
