"""
미작성 아이템 목록 + 주 소분류 매핑 추출 스크립트
"""
import json
import re
from pathlib import Path

# Paths
OUTPUT_DIR = Path("c:/Users/MW/Downloads/coding/PZ/Iris/output")
UNREG_FILE = OUTPUT_DIR / "layer3_unregistered.txt"
TAGS_FILE = OUTPUT_DIR / "tags_by_fulltype.json"
OUT_FILE = Path("C:/Users/MW/.gemini/antigravity/brain/c67a6897-eaad-40f1-862a-06431feeec1c/layer3_unregistered_with_subcat.md")

# 실제 태그 체계 — 접두어.번호 형식 (예: Tool.1-A, Combat.2-B)
TAG_NAMES = {
    "Tool.1-A": "도구·장비 (Tools/Equipment)",
    "Tool.1-B": "절단·연마 도구 (Cutting/Sharpening)",
    "Tool.1-C": "조리·주방 도구 (Cooking Utensils)",
    "Tool.1-D": "용기·그릇 (Containers/Vessels)",
    "Tool.1-E": "필기·문구 (Writing/Stationery)",
    "Tool.1-F": "의료·위생 도구 (Medical/Hygiene Tools)",
    "Tool.1-G": "조명·발화 도구 (Light/Fire Tools)",
    "Tool.1-H": "광원·전기 (Light Sources/Electrical)",
    "Tool.1-I": "통신·전자 (Communication/Electronics)",
    "Tool.1-J": "재봉·수선 (Sewing/Repair)",
    "Tool.1-K": "열쇠·자물쇠 (Keys/Locks)",
    "Tool.1-L": "가방·수납 (Bags/Storage)",

    "Combat.2-A": "도끼류 (Axes)",
    "Combat.2-B": "양손 둔기·장병기 (Two-handed Blunt/Polearms)",
    "Combat.2-C": "한손 둔기 (One-handed Blunt)",
    "Combat.2-D": "장검류 (Long Blades)",
    "Combat.2-E": "단검·소도구 (Short Blades/Small Tools)",
    "Combat.2-F": "창·찌르기 무기 (Spears/Thrusting)",
    "Combat.2-G": "권총 (Pistols)",
    "Combat.2-H": "소총 (Rifles)",
    "Combat.2-I": "산탄총 (Shotguns)",
    "Combat.2-J": "폭발물 (Explosives)",
    "Combat.2-K": "탄약 (Ammunition)",
    "Combat.2-L": "부착물·액세서리 (Attachments/Accessories)",

    "Consumable.3-A": "음식 (Food)",
    "Consumable.3-B": "음료 (Beverages)",
    "Consumable.3-C": "의약품·의료 소모품 (Medical Supplies)",
    "Consumable.3-D": "주류 (Alcohol)",
    "Consumable.3-E": "약초·약용 식물 (Herbs/Medicinal Plants)",

    "Resource.4-A": "건축·공작 자재 (Construction Materials)",
    "Resource.4-B": "조리·식품 가공 용기 (Cooking/Food Containers)",
    "Resource.4-C": "부품·수리 재료 (Parts/Repair Materials)",
    "Resource.4-D": "농업·원예 자재 (Farming/Gardening)",
    "Resource.4-E": "의류·직물 자재 (Clothing/Textile Materials)",
    "Resource.4-F": "전자·기계 부품 (Electronic/Mechanical Parts)",

    "Literature.5-A": "교본·매뉴얼 (Manuals/Guides)",
    "Literature.5-B": "신문·잡지 (Newspapers/Magazines)",
    "Literature.5-C": "소설·만화 (Novels/Comics)",
    "Literature.5-D": "지도·문서 (Maps/Documents)",

    "Wearable.6-A": "상의 (Tops)",
    "Wearable.6-B": "하의 (Bottoms)",
    "Wearable.6-C": "모자·헤드기어 (Hats/Headgear)",
    "Wearable.6-D": "신발 (Footwear)",
    "Wearable.6-E": "장갑 (Gloves)",
    "Wearable.6-F": "안경·고글 (Glasses/Goggles)",
    "Wearable.6-G": "악세서리·기타 착용 (Accessories/Other Wearables)",

    "Furniture.7-A": "가구·설치물 (Furniture/Fixtures)",

    "Vehicle.8-A": "차량 부품 (Vehicle Parts)",
    "Vehicle.8-B": "차량 관련 (Vehicle Related)",

    "Misc.9-A": "기타·잡동사니 (Miscellaneous)",
}


def main():
    if not UNREG_FILE.exists() or not TAGS_FILE.exists():
        print("Missing required files.")
        return

    unregistered = [line.strip() for line in UNREG_FILE.read_text("utf-8").splitlines() if line.strip()]
    tags_data = json.loads(TAGS_FILE.read_text("utf-8")).get("items", {})

    results = []

    for ft in unregistered:
        tags = tags_data.get(ft, [])

        # 첫 번째 태그 = 주 소분류 (primary subcategory)
        if tags:
            primary_tag = tags[0]
        else:
            primary_tag = "Unclassified"

        tag_label = TAG_NAMES.get(primary_tag, primary_tag)
        results.append((primary_tag, ft, tag_label))

    # 태그 기준 정렬, 그 안에서 fulltype 정렬
    results.sort(key=lambda x: (x[0], x[1]))

    with OUT_FILE.open("w", encoding="utf-8") as f:
        f.write("# 미작성 아이템 목록 (소분류 매핑)\n\n")
        f.write(f"총 {len(results)}개의 3계층 설명 미작성 아이템을 주 소분류(Primary Subcategory) 기준으로 정렬한 목록입니다.\n\n")

        current_tag = None
        count_in_group = 0
        for tag, ft, label in results:
            if tag != current_tag:
                if current_tag is not None:
                    f.write(f"\n> {count_in_group}개\n\n")
                f.write(f"## {tag} — {label}\n")
                current_tag = tag
                count_in_group = 0
            f.write(f"- `{ft}`\n")
            count_in_group += 1

        # 마지막 그룹 건수
        if count_in_group > 0:
            f.write(f"\n> {count_in_group}개\n")

    print(f"✅ File created: {OUT_FILE}")
    print(f"   Total items: {len(results)}")

    # 그룹별 건수 요약
    from collections import Counter
    tag_counts = Counter(r[0] for r in results)
    print("\n   그룹별 건수:")
    for tag, cnt in sorted(tag_counts.items()):
        label = TAG_NAMES.get(tag, tag)
        print(f"   {tag} ({label}): {cnt}")


if __name__ == "__main__":
    main()
