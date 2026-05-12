"""7개 소분류를 일괄 silent로 등록한다."""
import json
from pathlib import Path

IRIS = Path("c:/Users/MW/Downloads/coding/PZ/Iris")
tags_data = json.loads((IRIS / "output/tags_by_fulltype.json").read_text("utf-8")).get("items", {})
unreg = [l.strip() for l in (IRIS / "output/layer3_unregistered.txt").read_text("utf-8").splitlines() if l.strip()]

reg_path = IRIS / "build/data/description/layer3_registry.json"
reg = json.loads(reg_path.read_text("utf-8"))
existing = {e["fulltype"] for e in reg["entries"]}

TARGETS = ["Combat.2-K", "Consumable.3-D", "Tool.1-D", "Vehicle.8-A", "Vehicle.8-B", "Wearable.6-D", "Wearable.6-E"]

added = 0
per_tag = {t: 0 for t in TARGETS}

for ft in sorted(unreg):
    ft_tags = tags_data.get(ft, [])
    if ft_tags and ft_tags[0] in TARGETS and ft not in existing:
        reg["entries"].append({
            "fulltype": ft,
            "status": "silent",
            "kind": None,
            "text_ko": None,
            "anchors": [],
            "notes": "소분류 일괄 silent: " + ft_tags[0]
        })
        added += 1
        per_tag[ft_tags[0]] += 1

json.dump(reg, open(reg_path, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

total = len(reg["entries"])
print("추가된 silent: " + str(added) + "개")
print("총 엔트리: " + str(total) + "개")
for t in TARGETS:
    print("  " + t + ": " + str(per_tag[t]) + "개")
