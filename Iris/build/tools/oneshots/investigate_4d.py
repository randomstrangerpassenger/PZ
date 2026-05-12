"""Resource.4-D 심층 조사 보고서 생성"""
import json
from pathlib import Path

IRIS = Path("c:/Users/MW/Downloads/coding/PZ/Iris")
ARTIFACT = Path("C:/Users/MW/.gemini/antigravity/brain/c67a6897-eaad-40f1-862a-06431feeec1c")

tags = json.loads((IRIS / "output/tags_by_fulltype.json").read_text("utf-8")).get("items", {})
items = json.loads((IRIS / "input/items_itemscript.json").read_text("utf-8"))
uc = json.loads((IRIS / "output/usecases_by_fulltype.v2.4.json").read_text("utf-8"))
recipes = json.loads((IRIS / "output/recipes_by_fulltype.v2.4.json").read_text("utf-8"))
descs = json.loads((IRIS / "output/descriptions_by_fulltype.v2.4.json").read_text("utf-8"))

targets = sorted([ft for ft, t in tags.items() if t and t[0] == "Resource.4-D"])

out = ARTIFACT / "resource_4d_analysis.txt"
with out.open("w", encoding="utf-8") as f:
    f.write("Resource.4-D (농업·원예 자재) — 심층 조사 보고서\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"대상: {len(targets)}개\n\n")

    for ft in targets:
        item = items.get(ft, {})
        dn = item.get("DisplayName", "?")
        f.write("=" * 60 + "\n")
        f.write(f"■ {ft} — {dn}\n")
        f.write("=" * 60 + "\n\n")

        f.write("  [전체 속성]\n")
        for k, v in sorted(item.items()):
            if k != "FullType":
                f.write(f"    {k} = {v}\n")

        f.write(f"\n  [분류 태그]: {tags.get(ft, [])}\n")

        uc_lines = uc.get(ft, {}).get("lines", [])
        f.write(f"\n  [2계층 UseCase]: {len(uc_lines)}건\n")
        for line in uc_lines:
            f.write(f"    - {line.get('display_text', '?')}\n")

        rec = recipes.get(ft, [])
        f.write(f"\n  [4계층 레시피]: {len(rec)}건\n")
        for r in rec[:5]:
            if isinstance(r, dict):
                f.write(f"    - {r.get('name', '?')}\n")

        desc_lines = descs.get(ft, {}).get("use_case_block", {}).get("lines", [])
        f.write(f"\n  [기존 빌드 설명]: {len(desc_lines)}건\n")
        for line in desc_lines:
            f.write(f"    - {line.get('display_text', '?')}\n")

        f.write("\n  [3계층 판정 포인트]\n")
        f.write("    Q1. 고유 상호작용이 있는가?\n")
        f.write("    Q2. 1·2계층에서 이미 설명되는가?\n")
        f.write("    Q3. 4·5계층으로 처리되는 정보인가?\n")
        f.write("    Q4. 같은 군 내 개별성이 있는가?\n\n")

    # 군 전체 비교
    f.write("=" * 60 + "\n")
    f.write("■ 군 전체 비교\n")
    f.write("=" * 60 + "\n\n")
    for ft in targets:
        item = items.get(ft, {})
        dn = item.get("DisplayName", "?")
        dc = item.get("DisplayCategory", "?")
        tp = item.get("Type", "?")
        w = item.get("Weight", "?")
        tg = item.get("Tags", "")
        uc_cnt = len(uc.get(ft, {}).get("lines", []))
        rec_cnt = len(recipes.get(ft, []))
        f.write(f"  {ft:30s}  {dn:25s}  DC={dc:20s}  T={tp:10s}  Tags={tg}\n")

print(f"완료: {out}")
print(f"대상: {len(targets)}개")
