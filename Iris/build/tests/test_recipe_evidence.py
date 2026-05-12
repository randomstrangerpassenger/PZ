"""
2-run determinism + sample verification for recipe evidence pipeline.
"""
import json
import subprocess
import hashlib
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parents[1]
IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"
PIPELINE = BUILD_DIR / "recipe_evidence_pipeline.py"
INTEGRATOR = BUILD_DIR / "tools" / "pipeline" / "build_usecases_by_fulltype.py"

FILES = [
    "recipe_evidence_decisions.v2.4.json",
    "recipe_review_queue.v2.4.json",
    "recipe_index.v2.4.json",
    "recipes_by_fulltype.v2.4.json",
]

ok_all = True

# ── 1. Determinism (2-run SHA comparison) ──
print("=== 1. Determinism Test (2-run) ===")

def get_hashes():
    return {f: hashlib.sha256((OUTPUT_DIR / f).read_bytes()).hexdigest()[:16] for f in FILES}

subprocess.run([sys.executable, str(PIPELINE)], capture_output=True, cwd=str(IRIS_DIR))
h1 = get_hashes()
subprocess.run([sys.executable, str(PIPELINE)], capture_output=True, cwd=str(IRIS_DIR))
h2 = get_hashes()

for f in FILES:
    match = h1[f] == h2[f]
    print(f"  {f}: {'MATCH' if match else 'MISMATCH'}")
    if not match:
        ok_all = False
print()

# ── 2. Decisions sanity check ──
print("=== 2. Decisions Sanity ===")
dec = json.loads((OUTPUT_DIR / "recipe_evidence_decisions.v2.4.json").read_text("utf-8"))
stats = dec["stats"]
print(f"  PASS={stats['pass_rules']}, NO={stats['no_rules']}, REVIEW={stats['review_rules']}")
print(f"  Total rules: {stats['total_rules']}")
print(f"  PASS fulltypes: {stats['pass_fulltypes']}")

if stats["pass_rules"] == 0:
    print("  FAIL: No PASS rules found")
    ok_all = False
else:
    print("  OK: PASS rules exist")
print()

# ── 3. Rule structure validation ──
print("=== 3. Rule Structure ===")
for rule_id, rule in list(dec["rules"].items())[:3]:
    assert rule_id.startswith("rp.recipe."), f"Bad rule_id prefix: {rule_id}"
    assert "decision" in rule, f"Missing decision: {rule_id}"
    assert "matched_fulltypes" in rule, f"Missing matched_fulltypes: {rule_id}"
    assert "recipe_id" in rule, f"Missing recipe_id: {rule_id}"
print("  OK: All sampled rules have correct structure")

# Verify by_fulltype has rule_ids with {rule_id, role} structure
for ft, entry in list(dec["by_fulltype"].items())[:3]:
    assert "rule_ids" in entry, f"Missing rule_ids in by_fulltype: {ft}"
    assert "decision" not in entry, f"by_fulltype should NOT have decision: {ft}"
    for rid_entry in entry["rule_ids"]:
        assert "rule_id" in rid_entry, f"Missing rule_id in by_fulltype entry: {ft}"
        assert "role" in rid_entry, f"Missing role in by_fulltype entry: {ft}"
        assert rid_entry["role"] in ("consume", "keep"), f"Invalid role: {rid_entry['role']}"
print("  OK: by_fulltype has rule_ids with {rule_id, role} structure")
print()

# ── 4. keep-only fulltypes are included with role="keep" ──
print("=== 4. Keep-only inclusion ===")
rbf = json.loads((OUTPUT_DIR / "recipes_by_fulltype.v2.4.json").read_text("utf-8"))
keep_only = [
    ft for ft, entry in rbf["fulltypes"].items()
    if entry["as_keep"] and not entry["as_input"]
]
# Keep-only fulltypes MUST appear in by_fulltype with role="keep" (전량 검사)
missing_keep = []
bad_role = []
for ft in keep_only:
    if ft not in dec["by_fulltype"]:
        missing_keep.append(ft)
    else:
        roles = {e["role"] for e in dec["by_fulltype"][ft]["rule_ids"]}
        if "keep" not in roles:
            bad_role.append(ft)
if missing_keep or bad_role:
    print(f"  FAIL: {len(missing_keep)} missing, {len(bad_role)} wrong role")
    for ft in missing_keep[:5]:
        print(f"    missing: {ft}")
    for ft in bad_role[:5]:
        print(f"    bad_role: {ft}")
    ok_all = False
else:
    print(f"  OK: {len(keep_only)} keep-only FTs correctly included with role='keep'")

# keep stats validation
assert stats.get("keep_unresolved_count") == 0, \
    f"keep_unresolved_count={stats.get('keep_unresolved_count')} (must be 0)"
assert stats.get("recipe_keep_link_count", 0) > 0, \
    f"recipe_keep_link_count={stats.get('recipe_keep_link_count')} (must be > 0)"
print(f"  OK: keep_unresolved_count=0, recipe_keep_link_count={stats['recipe_keep_link_count']}")
print()

# ── 5. Review queue reason validation ──
print("=== 5. Review Queue Validation ===")
rq = json.loads((OUTPUT_DIR / "recipe_review_queue.v2.4.json").read_text("utf-8"))
valid_reasons = {
    "unresolved_token", "parser_unsupported", "unknown_fulltype_ref",
    "unknown_tag_ref", "dynamic_recipe_expr", "missing_output",
    "dynamic_recipe_expr.tag_match_empty",
    "dynamic_recipe_expr.group_def_dynamic",
}
bad_reasons = [i for i in rq["items"] if i["reason"] not in valid_reasons]
if bad_reasons:
    print(f"  FAIL: {len(bad_reasons)} items with invalid reason")
    ok_all = False
else:
    print(f"  OK: All {rq['total']} review items have valid reasons")
print(f"  By reason: {json.dumps(rq.get('by_reason', {}))}")
print()

# ── 5.5 Policy Freeze Validation ──
print("=== 5.5 Policy Freeze Validation ===")
policy_path = OUTPUT_DIR / "dynamic_group_policy.v2.4.json"
if not policy_path.exists():
    print(f"  FAIL: {policy_path.name} not found")
    ok_all = False
else:
    pol = json.loads(policy_path.read_text("utf-8"))

    # frozen_count == 5
    frozen_count = pol.get("frozen_count", 0)
    if frozen_count != 5:
        print(f"  FAIL: frozen_count={frozen_count} (expected 5)")
        ok_all = False
    else:
        print(f"  OK: frozen_count={frozen_count}")

    # policy == PERMANENT_REVIEW
    policy_val = pol.get("policy", "")
    if policy_val != "PERMANENT_REVIEW":
        print(f"  FAIL: policy='{policy_val}' (expected PERMANENT_REVIEW)")
        ok_all = False
    else:
        print(f"  OK: policy={policy_val}")

    # Each group: depends_on non-empty, source_ref pattern
    groups = pol.get("groups", {})
    group_errors = []
    for gname, ginfo in groups.items():
        deps = ginfo.get("depends_on", [])
        if not deps:
            group_errors.append(f"{gname}: depends_on is empty")
        sref = ginfo.get("source_ref", "")
        if "::Recipe.GetItemTypes." not in sref:
            group_errors.append(f"{gname}: source_ref '{sref}' missing '::Recipe.GetItemTypes.' pattern")
    if group_errors:
        for e in group_errors:
            print(f"  FAIL: {e}")
        ok_all = False
    else:
        print(f"  OK: All {len(groups)} groups have valid depends_on and source_ref")
print()

# ── 6. Integrator surface validation ──
print("=== 6. Surface Type Validation ===")
subprocess.run([sys.executable, str(INTEGRATOR)], capture_output=True, cwd=str(IRIS_DIR))
uc = json.loads((OUTPUT_DIR / "usecases_by_fulltype.v2.4.json").read_text("utf-8"))
ucf = uc["fulltypes"]

# Find a recipe_only fulltype
recipe_only = None
both_ft = None
for ft, info in ucf.items():
    source_types = set()
    for uc_entry in info["use_cases"]:
        for src in uc_entry["evidence_sources"]:
            source_types.add(src["source_type"])
    if source_types == {"recipe_evidence"} and recipe_only is None:
        recipe_only = ft
    if "rightclick" in source_types and "recipe_evidence" in source_types and both_ft is None:
        both_ft = ft
    if recipe_only and both_ft:
        break

if recipe_only:
    surface = ucf[recipe_only]["use_cases"][0]["surface"]
    if surface == "recipe_ui":
        print(f"  OK: recipe_only '{recipe_only}' -> surface='recipe_ui'")
    else:
        print(f"  FAIL: recipe_only '{recipe_only}' -> surface='{surface}' (expected 'recipe_ui')")
        ok_all = False
else:
    print("  SKIP: No recipe_only fulltype found")

if both_ft:
    # Check any use_case with both sources
    for uc_entry in ucf[both_ft]["use_cases"]:
        src_types = set(s["source_type"] for s in uc_entry["evidence_sources"])
        if "rightclick" in src_types and "recipe_evidence" in src_types:
            if uc_entry["surface"] == "both":
                print(f"  OK: both '{both_ft}' -> surface='both'")
            else:
                print(f"  FAIL: both '{both_ft}' -> surface='{uc_entry['surface']}' (expected 'both')")
                ok_all = False
            break
else:
    print("  SKIP: No 'both' fulltype found")
print()

# ── 7. Full quality gates ──
print("=== 7. Full Quality Gates ===")
result = subprocess.run(
    [sys.executable, str(BUILD_DIR / "quality_gates.py")],
    capture_output=True, text=True, encoding="utf-8", cwd=str(IRIS_DIR)
)
if result.returncode == 0:
    print("  OK: All quality gates passed")
else:
    print("  FAIL: Quality gates failed")
    ok_all = False
print()

# ── Final ──
print(f"{'=' * 50}")
print(f"FINAL RESULT: {'ALL PASSED' if ok_all else 'FAILURES DETECTED'}")
sys.exit(0 if ok_all else 1)
