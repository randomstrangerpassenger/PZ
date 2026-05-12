"""TAG_NAMES vs Iris_ko.txt 정합성 검증"""
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

iris_names = {}
with open("c:/Users/MW/Downloads/coding/PZ/Iris/media/lua/shared/translate/ko/Iris_ko.txt", encoding="utf-8") as f:
    for line in f:
        m = re.match(r'\s*Iris_Sub_(\d+)([A-Z])\s*=\s*"(.+?)"', line)
        if m:
            cat_num, sub_letter, name = m.groups()
            cat_map = {"1": "Tool", "2": "Combat", "3": "Consumable", "4": "Resource",
                       "5": "Literature", "6": "Wearable", "7": "Furniture", "8": "Vehicle", "9": "Misc"}
            cat = cat_map.get(cat_num, cat_num)
            tag = f"{cat}.{cat_num}-{sub_letter}"
            iris_names[tag] = name

tag_names = {}
with open(SCRIPT_DIR / "analyze_subcategory_groups.py", encoding="utf-8") as f:
    for line in f:
        for m in re.finditer(r'"([A-Z][a-z]+\.\d+-[A-Z])":\s*"([^"]+)"', line):
            tag_names[m.group(1)] = m.group(2)

print("=== Iris_ko.txt vs TAG_NAMES 비교 ===\n")
mismatches = []
for tag in sorted(set(list(iris_names.keys()) + list(tag_names.keys()))):
    iris = iris_names.get(tag, "(없음)")
    code = tag_names.get(tag, "(없음)")
    if iris != code:
        mismatches.append((tag, iris, code))

if not mismatches:
    print(f"전체 일치! {len(iris_names)}개 소분류 모두 Iris_ko.txt와 동일합니다.")
else:
    for tag, iris, code in mismatches:
        print(f"X {tag:20s}  Iris_ko: \"{iris}\"  vs  TAG_NAMES: \"{code}\"")
    print(f"\n불일치: {len(mismatches)}개 / 전체: {len(iris_names)}개")
