import json

tags = json.load(open("c:/Users/MW/Downloads/coding/PZ/Iris/output/tags_by_fulltype.json", encoding="utf-8")).get("items", {})
items = json.load(open("c:/Users/MW/Downloads/coding/PZ/Iris/input/items_itemscript.json", encoding="utf-8"))

search = ["Scissors", "Can Opener", "Chipped Stone", "Wrench", "Hammer",
          "Kitchen Knife", "Hunting Knife", "Shovel", "Crowbar", "Screwdriver", "Pipe Wrench"]

dn_to_ft = {}
for ft, data in items.items():
    dn = data.get("DisplayName", "")
    if dn not in dn_to_ft:
        dn_to_ft[dn] = []
    dn_to_ft[dn].append(ft)

out = open("c:/Users/MW/Downloads/coding/PZ/Iris/build/trace_1b_result.txt", "w", encoding="utf-8")
for name in search:
    fts = dn_to_ft.get(name, [])
    if fts:
        for ft in fts:
            tag = tags.get(ft, ["(태그없음)"])
            line = "{:20s} -> {:30s} -> {}".format(name, ft, tag)
            print(line)
            out.write(line + "\n")
    else:
        line = "{:20s} -> (items_itemscript.json에 없음)".format(name)
        print(line)
        out.write(line + "\n")
out.close()
