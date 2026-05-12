"""다중 태그 분류 분석 — 파일 출력"""
import json
from collections import defaultdict

tags = json.load(open("c:/Users/MW/Downloads/coding/PZ/Iris/output/tags_by_fulltype.json", encoding="utf-8")).get("items", {})

primary_count = defaultdict(int)
all_count = defaultdict(int)

for ft, tag_list in tags.items():
    if not tag_list:
        continue
    primary_count[tag_list[0]] += 1
    for tag in tag_list:
        all_count[tag] += 1

out = open("c:/Users/MW/Downloads/coding/PZ/Iris/build/multi_tag_result.txt", "w", encoding="utf-8")

out.write("{:20s} {:>8s} {:>8s} {:>8s}\n".format("소분류", "1차태그", "전체", "누락"))
out.write("=" * 50 + "\n")

mismatches = []
for tag in sorted(all_count.keys()):
    p = primary_count.get(tag, 0)
    a = all_count[tag]
    diff = a - p
    if diff > 0:
        mismatches.append((tag, p, a, diff))
    out.write("{:20s} {:8d} {:8d} {:8d}\n".format(tag, p, a, diff))

out.write("\n불일치 소분류 (누락>0):\n")
for tag, p, a, diff in sorted(mismatches, key=lambda x: -x[3]):
    out.write("  {:20s}: 1차={}, 전체={}, 누락={}\n".format(tag, p, a, diff))

out.close()
print("완료: multi_tag_result.txt")
print("불일치 소분류: {}개".format(len(mismatches)))
