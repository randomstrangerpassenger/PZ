"""Tool.1-B 심층 조사 보고서 생성"""
import json
from pathlib import Path

IRIS = Path("c:/Users/MW/Downloads/coding/PZ/Iris")
ARTIFACT = Path("C:/Users/MW/.gemini/antigravity/brain/c67a6897-eaad-40f1-862a-06431feeec1c")

tags = json.loads((IRIS / "output/tags_by_fulltype.json").read_text("utf-8")).get("items", {})
items = json.loads((IRIS / "input/items_itemscript.json").read_text("utf-8"))
uc_data = json.loads((IRIS / "output/usecases_by_fulltype.v2.4.json").read_text("utf-8"))
recipes = json.loads((IRIS / "output/recipes_by_fulltype.v2.4.json").read_text("utf-8"))
descs = json.loads((IRIS / "output/descriptions_by_fulltype.v2.4.json").read_text("utf-8"))

targets = sorted([ft for ft, t in tags.items() if t and t[0] == "Tool.1-B"])

# Also check right-click capabilities
rc_data = {}
rc_path = IRIS / "output" / "rightclick_by_fulltype.v2.4.json"
if rc_path.exists():
    rc_data = json.loads(rc_path.read_text("utf-8"))

out = ARTIFACT / "tool_1b_analysis.txt"
with out.open("w", encoding="utf-8") as f:
    f.write("Tool.1-B (분해/개방) — 심층 조사 보고서\n")
    f.write("=" * 60 + "\n\n")
    f.write("대상: {}개\n\n".format(len(targets)))

    for ft in targets:
        item = items.get(ft, {})
        dn = item.get("DisplayName", "?")
        f.write("=" * 60 + "\n")
        f.write("■ {} — {}\n".format(ft, dn))
        f.write("=" * 60 + "\n\n")

        f.write("  [전체 속성]\n")
        for k, v in sorted(item.items()):
            if k != "FullType":
                f.write("    {} = {}\n".format(k, v))

        # UseCase
        uc_lines = uc_data.get(ft, {}).get("lines", [])
        f.write("\n  [2계층 UseCase]: {}건\n".format(len(uc_lines)))
        for line in uc_lines:
            f.write("    - {}\n".format(line.get("display_text", "?")))

        # Recipes
        rec = recipes.get(ft, [])
        f.write("\n  [4계층 레시피]: {}건\n".format(len(rec)))
        for r in rec[:10]:
            if isinstance(r, dict):
                f.write("    - {}\n".format(r.get("name", "?")))

        # Descriptions
        desc = descs.get(ft, {})
        desc_uc = desc.get("use_case_block", {}).get("lines", [])
        desc_rc = desc.get("right_click_block", {}).get("lines", [])
        f.write("\n  [기존 빌드 설명 UseCase]: {}건\n".format(len(desc_uc)))
        for line in desc_uc:
            f.write("    - {}\n".format(line.get("display_text", "?")))
        f.write("  [기존 빌드 설명 RightClick]: {}건\n".format(len(desc_rc)))
        for line in desc_rc:
            f.write("    - {}\n".format(line.get("display_text", "?")))

        # Right-click capabilities
        rc = rc_data.get(ft, {})
        if rc:
            caps = rc.get("capabilities", [])
            f.write("\n  [우클릭 능력]: {}건\n".format(len(caps)))
            for cap in caps:
                f.write("    - {}\n".format(cap))

        f.write("\n")

    # 비교표
    f.write("=" * 60 + "\n")
    f.write("■ 군 전체 비교\n")
    f.write("=" * 60 + "\n\n")
    for ft in targets:
        item = items.get(ft, {})
        dn = item.get("DisplayName", "?")
        dc = item.get("DisplayCategory", "?")
        tp = item.get("Type", "?")
        tg = item.get("Tags", "")
        w = item.get("Weight", "?")
        f.write("  {} | {} | DC={} | Tags={} | W={}\n".format(ft, dn, dc, tg, w))

print("완료: {}".format(out))
print("대상: {}개".format(len(targets)))
