"""
Quality Gates v2.5 — Auto-Only 품질 게이트
==========================================
Gate Q1: PASS 무결성 (prove unknown → FAIL)
Gate Q2: Strong 무결성 (uniqueness 불일치 → FAIL)
Gate Q3: Anchor role 완전성 (rule별 profile 미충족 → FAIL)
Gate Q4: 결정성 (canonical JSON SHA 스냅샷 기반)
Gate Q5: 회귀 diff 통제 (expected_diff.json 기반)

Usage:
    python build/quality_gates.py              # Q1~Q5 모두 실행
    python build/quality_gates.py --update-sha # Q1~Q3+Q5 PASS 후 frozen SHA 갱신
"""
import sys
from pathlib import Path

# ── Path bootstrap (Iris/build on sys.path for tools.common + quality.*) ──
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from tools.common.io import load_json, write_json
from quality.config import (
    BUILD_REPORT_JSON,
    BUILD_REPORT_MD,
    BUILD_VERSION,
    CANDIDATES_PATH,
    DATA_DIR,
    DECISIONS_PATH,
    EXPECTED_DIFF_PATH,
    FROZEN_SHA_PATH,
    OUTPUT_DIR,
    OVERLAY_PATH,
    QUALITY_GATES_VERSION,
    ROLE_PROFILE_PATH,
    USECASES_PATH,
)
from quality.q1_pass_integrity import gate_q1
from quality.q2_strong_integrity import gate_q2
from quality.q3_anchor_completeness import gate_q3
from quality.q4_determinism import gate_q4, update_frozen_sha
from quality.q5_regression_diff import gate_q5
from quality.reporting import generate_build_report, generate_build_report_md


def main():
    import argparse
    parser = argparse.ArgumentParser(description=f"Quality Gates {QUALITY_GATES_VERSION}")
    parser.add_argument("--update-sha", action="store_true",
                        help="Q1~Q3+Q5 PASS 확인 후 frozen SHA 갱신")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  Quality Gates {QUALITY_GATES_VERSION} (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # ── Load data ──
    if not DECISIONS_PATH.exists():
        print(f"\n❌ Decisions file not found: {DECISIONS_PATH}")
        print(f"  Run the pipeline first: python build/rightclick_evidence_pipeline.py --{BUILD_VERSION.replace('.', '')}")
        return 1

    decisions = load_json(DECISIONS_PATH)
    candidates = load_json(CANDIDATES_PATH) if CANDIDATES_PATH.exists() else {}
    overlay = load_json(OVERLAY_PATH) if OVERLAY_PATH.exists() else {}

    gates = {}

    # ── Q1: PASS Integrity ──
    print("\n── Gate Q1: PASS Integrity ──")
    usecases_data = load_json(USECASES_PATH) if USECASES_PATH.exists() else None
    registry_path = DATA_DIR / f"use_case_registry.{BUILD_VERSION}.json"
    registry_data = load_json(registry_path) if registry_path.exists() else None
    
    gates["Q1_pass_integrity"] = gate_q1(decisions, usecases=usecases_data, registry=registry_data)
    q1 = gates["Q1_pass_integrity"]
    print(f"  Checked: {q1['checked']} PASS items")
    print(f"  Status: {q1['status']} (violations={q1['violations']})")
    if q1["details"]:
        for d in q1["details"]:
            print(f"  ❌ {d}")

    # ── Q2: Strong Integrity ──
    print("\n── Gate Q2: Strong Integrity ──")
    gates["Q2_strong_integrity"] = gate_q2(overlay)
    q2 = gates["Q2_strong_integrity"]
    print(f"  Checked: {q2['checked']} rules with uniqueness")
    print(f"  Status: {q2['status']} (violations={q2['violations']})")
    if q2["details"]:
        for d in q2["details"]:
            print(f"  ❌ {d}")

    # ── Q3: Anchor Role Completeness ──
    print("\n── Gate Q3: Anchor Role Completeness ──")
    if ROLE_PROFILE_PATH.exists():
        role_profiles = load_json(ROLE_PROFILE_PATH)
        # Remove metadata keys
        role_profiles = {k: v for k, v in role_profiles.items()
                        if not k.startswith("_")}
        gates["Q3_anchor_completeness"] = gate_q3(
            decisions, candidates, role_profiles
        )
        q3 = gates["Q3_anchor_completeness"]
        print(f"  Profiles loaded: {len(role_profiles)} rules")
        print(f"  Checked: {q3['checked']} PASS items")
        print(f"  Status: {q3['status']} (violations={q3['violations']})")
        if q3["details"]:
            for d in q3["details"]:
                print(f"  ❌ {d}")
    else:
        print(f"  ⚠️ Profile not found: {ROLE_PROFILE_PATH}")
        gates["Q3_anchor_completeness"] = {
            "status": "FAIL",
            "checked": 0,
            "violations": 1,
            "details": ["role_profile_by_rule_id.json not found"],
        }

    # ── Q4: Determinism (SHA snapshot) ──
    print("\n── Gate Q4: Determinism (SHA snapshot) ──")
    if FROZEN_SHA_PATH.exists():
        frozen_sha = load_json(FROZEN_SHA_PATH)
        gates["Q4_determinism"] = gate_q4(frozen_sha)
        q4 = gates["Q4_determinism"]
        print(f"  Files checked: {q4['files_checked']}")
        print(f"  Status: {q4['status']} (mismatches={q4['mismatches']})")
        if q4["details"]:
            for d in q4["details"]:
                print(f"  ❌ {d}")
    else:
        print(f"  ⚠️ frozen_sha not found: {FROZEN_SHA_PATH}")
        gates["Q4_determinism"] = {
            "status": "FAIL",
            "files_checked": 0,
            "mismatches": 1,
            "details": [f"frozen_sha.{BUILD_VERSION}.json not found"],
        }

    # ── Q5: Regression Diff ──
    print("\n── Gate Q5: Regression Diff ──")
    if EXPECTED_DIFF_PATH.exists():
        expected_diff = load_json(EXPECTED_DIFF_PATH)
        gates["Q5_regression_diff"] = gate_q5(decisions, expected_diff)
        q5 = gates["Q5_regression_diff"]
        print(f"  Status: {q5['status']} (unexpected={q5['unexpected_changes']}, "
              f"pending={q5['pending_allowed']})")
        if q5["details"]:
            for d in q5["details"]:
                print(f"  ❌ {d}")
        if q5.get("warnings"):
            for w in q5["warnings"]:
                print(f"  ⚠️ {w}")
    else:
        print(f"  ⚠️ expected_diff.json not found: {EXPECTED_DIFF_PATH}")
        gates["Q5_regression_diff"] = {
            "status": "FAIL",
            "unexpected_changes": 1,
            "pending_allowed": 0,
            "details": ["expected_diff.json not found"],
        }

    # ── --update-sha: Q1~Q3+Q5 PASS guard ──
    if args.update_sha:
        # Q4 is excluded from the guard (it's what we're updating)
        guard_gates = {k: v for k, v in gates.items() if k != "Q4_determinism"}
        guard_pass = all(g["status"] == "PASS" for g in guard_gates.values())

        if not guard_pass:
            failed = [k for k, g in guard_gates.items() if g["status"] != "PASS"]
            print(f"\n❌ --update-sha 거부: {failed} FAIL 상태에서 SHA 갱신 불가")
            print("  PASS 사람 임의조정 금지 — 먼저 게이트를 통과시키세요.")
            return 1

        updated = update_frozen_sha()
        print(f"\n  ✅ frozen SHA 갱신 완료: {FROZEN_SHA_PATH}")
        for fname, sha in updated["files"].items():
            print(f"    {fname}: {sha[:24]}...")

        # Ratchet legacy_count_baseline to current value
        legacy_inv_path = OUTPUT_DIR / f"legacy_inventory.{BUILD_VERSION}.json"
        if EXPECTED_DIFF_PATH.exists():
            ed = load_json(EXPECTED_DIFF_PATH)
            policy = ed.get("legacy_count_policy", "freeze")
            has_update = False
            
            if policy == "decrease_only" and legacy_inv_path.exists():
                legacy_data = load_json(legacy_inv_path)
                new_baseline = legacy_data.get("legacy_count", 0)
                old_baseline = ed.get("legacy_count_baseline", 0)
                if new_baseline != old_baseline:
                    ed["legacy_count_baseline"] = new_baseline
                    print(f"  ✅ legacy_count_baseline 래칫: {old_baseline}→{new_baseline}")
                    has_update = True
                    
            # Update separated metrics in expected_diff
            q5_metrics = gates.get("Q5_regression_diff", {}).get("new_metrics", {})
            for k, v in q5_metrics.items():
                old_val = ed.get(f"frozen_{k}", -1)
                if old_val != v:
                    ed[f"frozen_{k}"] = v
                    print(f"  ✅ {k} 갱신: {old_val}→{v}")
                    has_update = True
            
            if has_update:
                write_json(EXPECTED_DIFF_PATH, ed, indent=4)

        # Re-run Q4 with updated SHA
        gates["Q4_determinism"] = gate_q4(updated)
        q4 = gates["Q4_determinism"]
        print(f"  Q4 re-check: {q4['status']}")

    # ── Generate report ──
    report = generate_build_report(gates, decisions, overlay)

    # Save JSON report
    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(BUILD_REPORT_JSON, report, indent=2, trailing_newline=False)
    print(f"\n  Saved: {BUILD_REPORT_JSON}")

    # Save Markdown report
    md = generate_build_report_md(report)
    with open(BUILD_REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  Saved: {BUILD_REPORT_MD}")

    # ── Final ──
    overall = report["overall"]
    print(f"\n{'=' * 60}")
    if overall == "PASS":
        print("  ✅ All Quality Gates PASSED")
    else:
        print("  ❌ Quality Gates FAILED")
    print(f"{'=' * 60}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
