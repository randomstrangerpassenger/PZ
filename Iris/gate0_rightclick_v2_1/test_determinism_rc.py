"""Full verification for Gate-0 v2 + candidate-only expansion."""
import json
import subprocess
import hashlib
import sys
from collections import Counter
from pathlib import Path

IRIS_DIR = Path(__file__).parent.parent
OUTPUT_DIR = IRIS_DIR / "output"
PIPELINE = Path(__file__).parent / "rightclick_evidence_pipeline.py"
ITEMS_PATH = IRIS_DIR / "input" / "items_itemscript.json"

FILES = [
    "evidence_candidates.json",
    "evidence_decisions.json",
    "field_registry.json",
    "review_queue.json",
]

ok_all = True

# ── 1. Determinism ──
print("=== 1. Determinism Test ===")
def get_hashes():
    return {f: hashlib.sha256((OUTPUT_DIR / f).read_bytes()).hexdigest()[:16] for f in FILES}

subprocess.run([sys.executable, str(PIPELINE)], capture_output=True, cwd=str(IRIS_DIR))
h1 = get_hashes()
subprocess.run([sys.executable, str(PIPELINE)], capture_output=True, cwd=str(IRIS_DIR))
h2 = get_hashes()

for f in FILES:
    match = h1[f] == h2[f]
    print(f"  {f}: {'MATCH' if match else 'MISMATCH'}")
    if not match: ok_all = False
print()

# ── 2. Regression: STRONG/WEAK frozen set equality ──
print("=== 2. Regression: STRONG/WEAK (frozen set equality) ===")
decisions = json.loads((OUTPUT_DIR / "evidence_decisions.json").read_text("utf-8"))
items = json.loads(ITEMS_PATH.read_text("utf-8"))
candidates = json.loads((OUTPUT_DIR / "evidence_candidates.json").read_text("utf-8"))

FROZEN_STRONG = {
    "Base.Needle", "Base.SutureNeedle", "Base.SutureNeedleHolder",
    "Base.Thread", "Base.Tweezers",
}
FROZEN_WEAK = {
    "Base.BeerEmpty", "Base.BeerWaterFull", "Base.BleachEmpty",
    "Base.Bowl", "Base.BucketEmpty", "Base.BucketWaterFull",
    "Base.Dirtbag", "Base.Extinguisher", "Base.FullKettle",
    "Base.GlassTumbler", "Base.GlassTumblerWater", "Base.GlassWine",
    "Base.Gravelbag", "Base.Kettle", "Base.MugRed", "Base.MugSpiffo",
    "Base.MugWhite", "Base.Mugl", "Base.PlasticCup",
    "Base.PlasticCupWater", "Base.PopBottleEmpty", "Base.Pot",
    "Base.Sandbag", "Base.Saucepan", "Base.Teacup",
    "Base.WaterBleachBottle", "Base.WaterBottleEmpty",
    "Base.WaterBottleFull", "Base.WaterBowl", "Base.WaterMug",
    "Base.WaterMugRed", "Base.WaterMugSpiffo", "Base.WaterMugWhite",
    "Base.WaterPaintbucket", "Base.WaterPopBottle", "Base.WaterPot",
    "Base.WaterSaucepan", "Base.WaterTeacup", "Base.WhiskeyEmpty",
    "Base.WhiskeyWaterFull", "Base.WineEmpty", "Base.WineEmpty2",
    "Base.WineWaterFull",
    "farming.GardeningSprayEmpty", "farming.GardeningSprayFull",
    "farming.MayonnaiseEmpty", "farming.MayonnaiseWaterFull",
    "farming.RemouladeEmpty", "farming.RemouladeWaterFull",
    "farming.WateredCan", "farming.WateredCanFull",
}

actual_strong = {ft for ft, d in decisions.items() if d["decision"] == "STRONG"}
actual_weak = {ft for ft, d in decisions.items() if d["decision"] == "WEAK"}

stats = Counter(d["decision"] for d in decisions.values())
print(f"  STRONG={stats['STRONG']}, WEAK={stats['WEAK']}, NO={stats['NO']}, REVIEW={stats['REVIEW']}")

if actual_strong == FROZEN_STRONG:
    print(f"  OK: STRONG set matches ({len(actual_strong)} items)")
else:
    added = actual_strong - FROZEN_STRONG
    missing = FROZEN_STRONG - actual_strong
    print(f"  FAIL: STRONG mismatch (added={added}, missing={missing})")
    ok_all = False

if actual_weak == FROZEN_WEAK:
    print(f"  OK: WEAK set matches ({len(actual_weak)} items)")
else:
    added = actual_weak - FROZEN_WEAK
    missing = FROZEN_WEAK - actual_weak
    print(f"  FAIL: WEAK mismatch (added={added}, missing={missing})")
    ok_all = False
print()

# ── 3. excluded_matcher=0 ──
print("=== 3. review_queue excluded_matcher check ===")
review_queue = json.loads((OUTPUT_DIR / "review_queue.json").read_text("utf-8"))
excluded_matchers = [r for r in review_queue if r.get("kind") == "excluded_matcher"]
print(f"  Total review_queue entries: {len(review_queue)}")
print(f"  excluded_matcher entries: {len(excluded_matchers)}")
if len(excluded_matchers) == 0:
    print("  OK: excluded_matcher=0")
else:
    print(f"  FAIL: excluded_matcher should be 0, got {len(excluded_matchers)}")
    ok_all = False
print()

# ── 4. firefighting extract candidate count ≤53 ──
print("=== 4. firefighting extract candidate count (guardrail ≤53) ===")
ff_cands = [
    ft for ft, c in candidates.items()
    if "rule_firefighting_isextinguisher" in c.get("rule_ids", [])
]
print(f"  rule_firefighting_isextinguisher candidates: {len(ff_cands)}")
if len(ff_cands) <= 53:
    print(f"  OK: {len(ff_cands)} <= 53")
else:
    print(f"  FAIL: {len(ff_cands)} > 53")
    ok_all = False
print()

# ── 5. REVIEW delta observation (no pass/fail, observation only) ──
print("=== 5. REVIEW delta observation (no judgment) ===")
REVIEW_BEFORE = 6  # Gate-0 v2 frozen value
review_after = stats["REVIEW"]
delta = review_after - REVIEW_BEFORE
print(f"  REVIEW_before (Gate-0 v2): {REVIEW_BEFORE}")
print(f"  REVIEW_after: {review_after}")
print(f"  REVIEW delta: +{delta}")
print()

# ── 6. Per-rule candidate match counts (observation only) ──
print("=== 6. Per-rule candidate match counts ===")
candidate_rules = [
    "rule_candidate_moveable_furniture",
    "rule_candidate_vehiclemaintenance",
    "rule_candidate_junk",
]
for rule_id in candidate_rules:
    count = sum(1 for ft, c in candidates.items() if rule_id in c.get("rule_ids", []))
    print(f"  {rule_id}: {count} items")
print()

# ── 7. NO items NOT in field_registry ──
print("=== 7. NO items not in field_registry ===")
registry = json.loads((OUTPUT_DIR / "field_registry.json").read_text("utf-8"))
field_items = set()
for fentry in registry.values():
    for item in fentry["items"]:
        field_items.add(item["fulltype"])

no_in_registry = [ft for ft, d in decisions.items() if d["decision"] == "NO" and ft in field_items]
if no_in_registry:
    print(f"  FAIL: {len(no_in_registry)} NO items in field_registry")
    ok_all = False
else:
    print("  OK: no NO items in field_registry")
print()

# ── 8. Guard items still preserved ──
print("=== 8. Material guard items ===")
guard_items = {
    "Base.Thread": "STRONG",
    "Base.Dirtbag": "WEAK",
    "Base.Gravelbag": "WEAK",
    "Base.Sandbag": "WEAK",
}
for ft, expected in guard_items.items():
    actual = decisions.get(ft, {}).get("decision", "MISSING")
    if actual == expected:
        print(f"  OK: guard {ft}={actual}")
    else:
        print(f"  FAIL: guard {ft} expected={expected} actual={actual}")
        ok_all = False
print()

# ── Final ──
print(f"{'=' * 50}")
print(f"FINAL RESULT: {'ALL PASSED' if ok_all else 'FAILURES DETECTED'}")
sys.exit(0 if ok_all else 1)
