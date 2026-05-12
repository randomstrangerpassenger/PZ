"""
Use Case Integration — build_usecases_by_fulltype.py
=====================================================
evidence_decisions + uniqueness_overlay + use_case_registry
+ recipe_evidence_decisions
→ usecases_by_fulltype.v2.4.json

Phase 2: RightClick + Recipe(evidence) 통합.
- RightClick  → source_type="rightclick", decision=PASS/NO/REVIEW, strength=overlay
- Recipe      → source_type="recipe_evidence", decision=PASS (input/output 행동 증거)

Surface union:
  - rightclick만 → "context_menu"
  - recipe_evidence만 → "recipe_ui"
  - 둘 다 → "both"

FAIL-LOUD 조건:
  1. decisions + recipe_evidence에 등장하는 모든 rule_id가 registry에 있어야 함
  2. PASS fulltype이 overlay.by_fulltype에 없으면 FAIL (REVIEW/NO는 overlay 미존재 허용)
"""
import sys
from pathlib import Path
from collections import defaultdict

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_DIR = Path(__file__).resolve().parents[2]
for import_path in (BUILD_DIR, SCRIPT_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"

from registry_utils import resolve_use_case_id
from tools.common.io import load_json, write_json
from tools.common.versions import BUILD_VERSION

DATA_DIR = BUILD_DIR / "data" / BUILD_VERSION

DECISIONS_PATH = OUTPUT_DIR / f"evidence_decisions.{BUILD_VERSION}.json"
OVERLAY_PATH = OUTPUT_DIR / f"uniqueness_overlay.{BUILD_VERSION}.json"
RECIPE_DECISIONS_PATH = OUTPUT_DIR / f"recipe_evidence_decisions.{BUILD_VERSION}.json"
ACTION_CLASSIFICATION_PATH = OUTPUT_DIR / f"action_evidence_classification.{BUILD_VERSION}.json"
REGISTRY_PATH = DATA_DIR / f"use_case_registry.{BUILD_VERSION}.json"
OUTPUT_PATH = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"

# ── uniqueness_summary → overlay label 매핑 ──
UNIQUENESS_LABEL = {
    "STRONG_ONLY": "unique",
    "WEAK_ONLY": "shared",
    "MIXED": "shared",
}

# ── RightClick Prefix Boundaries ──
EXCLUSION_PREFIX = ("uc.exclusion.",)
EVIDENCE_PREFIX = ("uc.action.", "uc.capability.")


def build_usecases():
    """Main builder. Returns (output_data, diagnostics, exit_code)."""
    diagnostics = {"unknown_prefix": set()}

    # ── Step 0: Load inputs ──
    print(f"  Loading decisions: {DECISIONS_PATH.name}")
    decisions = load_json(DECISIONS_PATH)

    print(f"  Loading overlay: {OVERLAY_PATH.name}")
    overlay = load_json(OVERLAY_PATH)

    print(f"  Loading registry: {REGISTRY_PATH.name}")
    registry = load_json(REGISTRY_PATH)

    print(f"  Loading recipe evidence decisions: {RECIPE_DECISIONS_PATH.name}")
    recipe_evidence = load_json(RECIPE_DECISIONS_PATH)
    recipe_by_ft = recipe_evidence.get("by_fulltype", {})
    recipe_rules = recipe_evidence.get("rules", {})

    # Load action evidence classification (optional — skip if not present yet)
    action_classifications = {}
    if ACTION_CLASSIFICATION_PATH.exists():
        print(f"  Loading action evidence classification: {ACTION_CLASSIFICATION_PATH.name}")
        action_cls_data = load_json(ACTION_CLASSIFICATION_PATH)
        action_classifications = action_cls_data.get("classifications", {})
        print(f"  ✅ Action classifications loaded: {len(action_classifications)} entries")
    else:
        print(f"  ⚠️  Action classification not found, skipping evidence_strength enrichment")

    registry_rules = registry.get("rules", {})

    # ── Auto-expand registry with recipe rule_ids ──
    # rp.recipe.<id> → uc.recipe.<id> (1:1 자동 매핑)
    recipe_auto_count = 0
    for rule_id in recipe_rules:
        if rule_id not in registry_rules:
            # Extract recipe_id from rule_id: rp.recipe.<recipe_id>
            recipe_id = rule_id.replace("rp.recipe.", "", 1)
            registry_rules[rule_id] = {
                "use_case_id": f"uc.recipe.{recipe_id}",
                "auto_generated": True,
            }
            recipe_auto_count += 1
    if recipe_auto_count:
        print(f"  ℹ️ Registry auto-expanded: {recipe_auto_count} recipe rule_ids")

    overlay_by_rule = overlay.get("by_rule_id", {})
    overlay_by_ft = overlay.get("by_fulltype", {})

    # ── Step 1: Validate registry coverage (FAIL-LOUD #1) ──
    # Collect all rule_ids from BOTH sources
    all_rule_ids = set()

    # RightClick rule_ids
    for ft, entry in decisions.items():
        if not isinstance(entry, dict):
            continue
        for rid in entry.get("rule_ids", []):
            all_rule_ids.add(rid)

    # Recipe evidence rule_ids
    for ft, ft_entry in recipe_by_ft.items():
        for rid_entry in ft_entry.get("rule_ids", []):
            all_rule_ids.add(rid_entry["rule_id"])

    missing_in_registry = all_rule_ids - set(registry_rules.keys())
    if missing_in_registry:
        print(f"\n  ❌ FAIL-LOUD: {len(missing_in_registry)} rule_id(s) "
              f"missing from registry:")
        for rid in sorted(missing_in_registry):
            print(f"    - {rid}")
        return None, diagnostics, 1

    print(f"  ✅ Registry coverage OK: {len(all_rule_ids)} rule_ids, "
          f"all mapped")

    # ── Step 2: Build (fulltype, use_case_id) buckets ──
    buckets = defaultdict(list)
    bucket_decisions = {}  # (ft, ucid) → decision (from rightclick, or None)

    # 2a: RightClick evidence sources
    rc_ft_count = 0
    for ft, entry in decisions.items():
        if not isinstance(entry, dict):
            continue

        decision = entry.get("decision")
        rule_ids = entry.get("rule_ids", [])

        if not rule_ids:
            continue

        rc_ft_count += 1
        for rid in rule_ids:
            rule_props = registry_rules[rid]
            ucid = resolve_use_case_id(rule_props)
            key = (ft, ucid)

            local_decision = decision
            if rule_props.get("decision") == "PASS" and rule_props.get("override_reason_code"):
                local_decision = "PASS"

            # Get strength from overlay.by_rule_id
            rule_overlay = overlay_by_rule.get(rid, {})
            strength = rule_overlay.get("uniqueness")  # "STRONG" | "WEAK" | None

            if rule_props.get("decision") == "PASS" and rule_props.get("strength"):
                strength = rule_props.get("strength")

            evidence_source = {
                "source_type": "rightclick",
                "rule_id": rid,
                "decision": local_decision,
                "strength": strength,
            }
            buckets[key].append(evidence_source)
            bucket_decisions[key] = local_decision

    print(f"  ✅ RightClick: {rc_ft_count} fulltypes loaded")

    # 2b: Recipe evidence sources (PASS fulltypes only)
    recipe_ft_count = 0
    for ft, ft_entry in recipe_by_ft.items():
        recipe_ft_count += 1
        for rid_entry in ft_entry.get("rule_ids", []):
            rid = rid_entry["rule_id"]
            role = rid_entry["role"]  # "consume" | "keep" (필수)
            # Get recipe rule decision from rules section
            rule_decision = recipe_rules.get(rid, {}).get("decision", "PASS")

            rule_props = registry_rules[rid]
            ucid = resolve_use_case_id(rule_props)
            key = (ft, ucid)

            evidence_source = {
                "source_type": "recipe_evidence",
                "rule_id": rid,
                "decision": rule_decision,
                "strength": None,
                "role": role,
            }
            buckets[key].append(evidence_source)
            # Don't overwrite rightclick decision; only set if no rightclick
            if key not in bucket_decisions:
                bucket_decisions[key] = rule_decision

    print(f"  ✅ Recipe evidence: {recipe_ft_count} fulltypes loaded")

    # ── Step 3: Finalize per-fulltype use_case list ──
    fulltypes_output = {}
    fail_loud_missing_ft = []

    # Group buckets by fulltype
    by_fulltype = defaultdict(list)
    for (ft, ucid), sources in buckets.items():
        by_fulltype[ft].append((ucid, sources, bucket_decisions[(ft, ucid)]))

    for ft in sorted(by_fulltype.keys()):
        uc_entries = by_fulltype[ft]
        use_cases = []

        # FAIL-LOUD #2: Check overlay.by_fulltype existence for rightclick PASS only
        # Recipe evidence items legitimately lack overlay entries (overlay is rightclick-only)
        # REVIEW/NO items also legitimately lack overlay entries
        has_rightclick_pass = False
        for _, sources, dec in uc_entries:
            if dec == "PASS" and any(s["source_type"] == "rightclick" for s in sources):
                has_non_override = False
                for s in sources:
                    if s["source_type"] == "rightclick":
                        rid = s["rule_id"]
                        if not registry_rules[rid].get("override_reason_code"):
                            has_non_override = True
                            break
                if has_non_override:
                    has_rightclick_pass = True
                    break

        ft_overlay = overlay_by_ft.get(ft)
        if has_rightclick_pass and ft_overlay is None:
            fail_loud_missing_ft.append(ft)

        for ucid, sources, decision in sorted(uc_entries, key=lambda x: x[0]):
            # Sort evidence_sources deterministically
            # null values → "" for stable sorting
            sorted_sources = sorted(
                sources,
                key=lambda s: (
                    s["source_type"],
                    s["rule_id"],
                    s["decision"] or "",
                    s["strength"] or "",
                ),
            )

            # Surface union: from source_type set
            source_types = set(s["source_type"] for s in sorted_sources)
            has_rc = "rightclick" in source_types
            has_recipe = "recipe_evidence" in source_types
            if has_rc and has_recipe:
                surface = "both"
            elif has_recipe:
                surface = "recipe_ui"
            else:
                surface = "context_menu"

            # display_strength (rightclick overlay only, recipe=null)
            strengths = [s["strength"] for s in sorted_sources if s["strength"]]
            if "STRONG" in strengths:
                display_strength = "STRONG"
            elif "WEAK" in strengths:
                display_strength = "WEAK"
            else:
                display_strength = None

            # Determine line_kind based on strict prefixes
            line_kind = None
            if has_rc:
                if ucid.startswith(EXCLUSION_PREFIX):
                    line_kind = "exclusion"
                elif ucid.startswith(EVIDENCE_PREFIX):
                    line_kind = "evidence"
                else:
                    diagnostics["unknown_prefix"].add(ucid)
                    line_kind = "unknown"
            elif has_recipe:
                # Recipe ONLY is always evidence
                line_kind = "evidence"

            if line_kind == "unknown":
                # Step 1 rollout: filter out unknown prefixes so they don't enter PASS list
                continue

            # uniqueness overlay
            if ft_overlay is not None:
                summary = ft_overlay.get("uniqueness_summary", "")
                overlay_label = UNIQUENESS_LABEL.get(summary, "none")
            else:
                overlay_label = "none"

            use_case = {
                "use_case_id": ucid,
                "surface": surface,
                "display_strength": display_strength,
                "evidence_sources": sorted_sources,
                "uniqueness": {"overlay": overlay_label},
                "line_kind": line_kind,
            }

            # Enrich uc.action.* lines with evidence_strength + reason_code
            # Rule 1.5: per-item consumable check — if this FullType is in
            # excluded_consumables, override to exclude/INPUT_ITEM_CONSUMABLE
            if ucid.startswith("uc.action.") and ucid in action_classifications:
                cls = action_classifications[ucid]
                excluded_consumables = cls.get("excluded_consumables", [])
                if ft in excluded_consumables:
                    use_case["evidence_strength"] = "exclude"
                    use_case["reason_code"] = "INPUT_ITEM_CONSUMABLE"
                    use_case["display_strength"] = "EXCLUDE"
                else:
                    es = cls.get("evidence_strength")
                    use_case["evidence_strength"] = es
                    use_case["reason_code"] = cls.get("reason_code")
                    # Classification의 evidence_strength를 display_strength에 반영
                    # (overlay가 이미 STRONG/WEAK를 잡았으면 그대로 유지,
                    #  overlay가 None이면 classification 결과로 채움)
                    if display_strength is None and es:
                        use_case["display_strength"] = es.upper()

            use_cases.append(use_case)

        # Q4 Determinism sort key
        use_cases.sort(key=lambda uc: (
            "rightclick" if any(s["source_type"] == "rightclick" for s in uc["evidence_sources"]) else "recipe_evidence",
            uc.get("line_kind", ""),
            uc.get("evidence_strength", ""),
            uc["use_case_id"]
        ))

        fulltypes_output[ft] = {"use_cases": use_cases}

    # ── FAIL-LOUD #2 check ──
    if fail_loud_missing_ft:
        print(f"\n  ❌ FAIL-LOUD: {len(fail_loud_missing_ft)} PASS "
              f"fulltype(s) missing from overlay.by_fulltype:")
        for ft in fail_loud_missing_ft[:10]:
            print(f"    - {ft}")
        return None, diagnostics, 1

    # ── Step 4: Write output ──
    output = {
        "version": BUILD_VERSION,
        "fulltypes": fulltypes_output,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    full_output_path = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"
    write_json(full_output_path, output, indent=2)
        
    # Write diagnostics explicitly
    diag_path = OUTPUT_DIR / f"diagnostics.{BUILD_VERSION}.json"
    diag_out = {
        "unknown_prefix": sorted(list(diagnostics["unknown_prefix"]))
    }
    write_json(diag_path, diag_out, indent=2)

    return output, diagnostics, 0


def main():
    print("=" * 60)
    print(f"  Use Case Integration (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # ── Check prerequisites ──
    for path, label in [
        (DECISIONS_PATH, "evidence_decisions"),
        (OVERLAY_PATH, "uniqueness_overlay"),
        (RECIPE_DECISIONS_PATH, "recipe_evidence_decisions"),
        (REGISTRY_PATH, "use_case_registry"),
    ]:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return 1

    output, diagnostics, code = build_usecases()
    if code != 0:
        return code

    ft_count = len(output["fulltypes"])
    uc_total = sum(
        len(v["use_cases"]) for v in output["fulltypes"].values()
    )

    # Surface distribution
    surface_dist = defaultdict(int)
    for ft_data in output["fulltypes"].values():
        for uc in ft_data["use_cases"]:
            surface_dist[uc["surface"]] += 1

    print(f"\n  ✅ Generated usecases_by_fulltype.{BUILD_VERSION}.json")
    print(f"     fulltypes: {ft_count}")
    print(f"     use_case entries: {uc_total}")
    print(f"     surfaces: {dict(surface_dist)}")
    
    if diagnostics["unknown_prefix"]:
        print(f"\n  ⚠️  Diagnostics (2-Step Rollout): {len(diagnostics['unknown_prefix'])} unknown prefix(es) filtered out.")
        for ucid in sorted(diagnostics["unknown_prefix"])[:20]:
            print(f"     - {ucid}")
    
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
