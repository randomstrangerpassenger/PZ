"""Combat.2-J (폭발물) 심층 조사 보고서 생성"""
import json
from pathlib import Path

IRIS = Path("c:/Users/MW/Downloads/coding/PZ/Iris")
OUT = Path("C:/Users/MW/.gemini/antigravity/brain/c67a6897-eaad-40f1-862a-06431feeec1c/combat_2j_analysis.txt")

items = json.loads((IRIS / "input/items_itemscript.json").read_text("utf-8"))
tags = json.loads((IRIS / "output/tags_by_fulltype.json").read_text("utf-8")).get("items", {})
uc = json.loads((IRIS / "output/usecases_by_fulltype.v2.4.json").read_text("utf-8"))
recipes = json.loads((IRIS / "output/recipes_by_fulltype.v2.4.json").read_text("utf-8"))
descs = json.loads((IRIS / "output/descriptions_by_fulltype.v2.4.json").read_text("utf-8"))
evidence = json.loads((IRIS / "output/evidence_decisions.v2.4.json").read_text("utf-8"))

targets = sorted([ft for ft, t in tags.items() if t and t[0] == "Combat.2-J"])

with OUT.open("w", encoding="utf-8") as f:
    f.write("Combat.2-J (폭발물) — 심층 조사 보고서\n")
    f.write("=" * 60 + "\n\n")
    f.write("조사 항목: 실제 사용처, 실제 상호작용, 실제 효과,\n")
    f.write("          변형이 의미를 바꾸는지, 4·5계층 처리 여부\n")
    f.write(f"대상 아이템: {len(targets)}개\n\n")

    for ft in targets:
        f.write("=" * 60 + "\n")
        f.write(f"■ {ft}\n")
        f.write("=" * 60 + "\n\n")

        item = items.get(ft, {})
        dn = item.get("DisplayName", "?")
        f.write(f"  표시명: {dn}\n")
        f.write(f"  DisplayCategory: {item.get('DisplayCategory', '?')}\n")
        f.write(f"  Type: {item.get('Type', '?')}\n")
        f.write(f"  Weight: {item.get('Weight', '?')}\n")

        # 전체 속성
        f.write("\n  [전체 속성]\n")
        for k, v in sorted(item.items()):
            if k not in ("DisplayName", "DisplayCategory", "Type", "Weight", "FullType"):
                f.write(f"    {k} = {v}\n")

        # 분류 태그
        f.write(f"\n  [분류 태그]: {tags.get(ft, [])}\n")

        # UseCase (2계층 — 이미 처리되는 정보)
        uc_data = uc.get(ft, {})
        uc_lines = uc_data.get("lines", [])
        f.write(f"\n  [2계층 UseCase]: {len(uc_lines)}건\n")
        for line in uc_lines:
            dt = line.get("display_text", line.get("label_key", "?"))
            strength = line.get("strength", "")
            surface = line.get("surface", "")
            f.write(f"    - {dt}")
            if strength:
                f.write(f" (strength={strength})")
            if surface:
                f.write(f" [surface={surface}]")
            f.write("\n")

        # Evidence (판정 근거)
        ev = evidence.get(ft, {})
        if ev:
            ev_decisions = ev.get("decisions", [])
            f.write(f"\n  [Evidence 판정]: {len(ev_decisions)}건\n")
            for d in ev_decisions[:10]:
                f.write(f"    - {d.get('label_key', '?')}: {d.get('decision', '?')} ({d.get('reason', '')})\n")

        # 레시피 (4계층)
        rec = recipes.get(ft, [])
        f.write(f"\n  [4계층 레시피]: {len(rec)}건\n")
        for r in rec[:10]:
            if isinstance(r, dict):
                f.write(f"    - {r.get('name', '?')}\n")
            else:
                f.write(f"    - {r}\n")

        # 기존 설명 (descriptions_by_fulltype)
        desc = descs.get(ft, {})
        desc_uc = desc.get("use_case_block", {})
        desc_lines = desc_uc.get("lines", [])
        f.write(f"\n  [기존 빌드 설명]: {len(desc_lines)}건\n")
        for line in desc_lines:
            dt = line.get("display_text", "")
            f.write(f"    - {dt}\n")

        # 3계층 판정 포인트
        f.write("\n  [3계층 판정 포인트]\n")
        f.write("    Q1. 고유 상호작용이 있는가?\n")
        f.write("    Q2. 1·2계층에서 이미 설명되는가?\n")
        f.write("    Q3. 4·5계층으로 처리되는 정보인가?\n")
        f.write("    Q4. 같은 군 내 개별성이 있는가?\n")
        f.write("\n")

    # 군 전체 비교
    f.write("=" * 60 + "\n")
    f.write("■ 군 전체 비교\n")
    f.write("=" * 60 + "\n\n")
    for ft in targets:
        item = items.get(ft, {})
        dn = item.get("DisplayName", "?")
        t = item.get("Type", "?")
        w = item.get("Weight", "?")
        uc_cnt = len(uc.get(ft, {}).get("lines", []))
        rec_cnt = len(recipes.get(ft, []))
        f.write(f"  {ft:30s}  {dn:20s}  Type={t:10s}  W={w}  UC={uc_cnt}  Recipes={rec_cnt}\n")

print("완료:", OUT)
