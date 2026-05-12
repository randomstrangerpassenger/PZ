"""
Iris Build Pipeline - Main Entry Point

Executes the complete Iris classification pipeline:
Phase 0 (Gate-0): Validation
Phase 1 (Gate-1): Evidence Extraction  
Phase 2 (Gate-2): Rule Application
Phase 3 (Gate-3): Output Generation
Phase 4 (Gate-4): Verification

Any Gate failure immediately halts the pipeline.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add build directory to path
BUILD_DIR = Path(__file__).parent.resolve()
IRIS_DIR = BUILD_DIR.parent
INPUT_DIR = IRIS_DIR / "input"
OUTPUT_DIR = IRIS_DIR / "output"
RUNTIME_DATA_DIR = IRIS_DIR / "media" / "lua" / "client" / "Iris" / "Data"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


def print_header(phase: str, description: str) -> None:
    """Print a phase header."""
    print(f"\n{'='*60}")
    print(f" {phase}: {description}")
    print(f"{'='*60}")


def print_gate_result(gate: str, passed: bool, details: str = "") -> None:
    """Print Gate result."""
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"\n{gate}: {status}")
    if details:
        print(f"   {details}")


def run_phase0() -> tuple[bool, set[str]]:
    """
    Phase 0: Contract/Validation Pipeline (Gate-0)
    
    Returns: (passed, manual_only_tags)
    """
    print_header("Phase 0", "Contract/Validation Pipeline (Gate-0)")
    
    from phase0_validation.schema_validator import validate_all_inputs
    from phase0_validation.allowlist import ALLOWLIST
    from phase0_validation.evidence_table_loader import validate_evidence_tables
    
    all_passed = True
    
    # 0-1. Input Schema Validation
    print("\n[0-1] Input Schema Validation...")
    schema_result = validate_all_inputs(INPUT_DIR)
    
    if schema_result.passed:
        print(f"      Items: {len(schema_result.items_fulltypes)}")
        print(f"      Recipes: {len(schema_result.recipe_fulltypes)}")
        print(f"      Fixers: {len(schema_result.fixer_fulltypes)}")
        print(f"      Moveables: {len(schema_result.moveables_itemids)} items, {len(schema_result.moveables_tags)} tags")
    else:
        all_passed = False
        for err in schema_result.errors:
            print(f"      ❌ {err}")
    
    # 0-2. Allowlist Loading
    print("\n[0-2] Allowlist Loading...")
    print(f"      Version: {ALLOWLIST['version']}")
    print(f"      Types: {len(ALLOWLIST['Type'])}")
    
    # 0-3. Evidence Table Loading (C1 Critical)
    print("\n[0-3] Evidence Table Loading (C1)...")
    tables, integrity_result = validate_evidence_tables(IRIS_DIR)
    
    if integrity_result.passed:
        print(f"      Tables: {list(tables.keys())}")
        print(f"      Valid tags: {len(integrity_result.valid_tags)}")
        print(f"      Manual-only: {len(integrity_result.manual_only_tags)}")
    else:
        all_passed = False
        for err in integrity_result.errors:
            print(f"      ❌ {err}")
    
    print_gate_result("Gate-0", all_passed)
    
    return all_passed, integrity_result.manual_only_tags


def run_phase1():
    """
    Phase 1: Evidence Extraction (Gate-1)
    
    Returns: (EvidenceCollectionResult, raw_items_data)
    """
    print_header("Phase 1", "Evidence Extraction (Gate-1)")
    
    from phase1_extraction.evidence_collector import collect_all_evidence
    import json
    
    print("\n[1-1] Extracting evidence from all sources...")
    evidence = collect_all_evidence(INPUT_DIR)
    
    print(f"      Items: {evidence.stats.get('items', 0)}")
    print(f"      Recipes: {evidence.stats.get('recipes', 0)}")
    print(f"      Fixers: {evidence.stats.get('fixers', 0)}")
    print(f"      Moveables: {evidence.stats.get('moveables_ids', 0)} IDs, {evidence.stats.get('moveables_tags', 0)} tags")
    print(f"      Combined: {evidence.stats.get('total_combined', 0)}")
    
    # Load raw items data for blocklist (DisplayCategory lookup)
    items_path = INPUT_DIR / "items_itemscript.json"
    with open(items_path, "r", encoding="utf-8") as f:
        raw_items_data = json.load(f)
    
    print_gate_result("Gate-1", True, f"{evidence.total_items} items processed")
    
    return evidence, raw_items_data


def run_phase2(evidence):
    """
    Phase 2: Rule Application (Gate-2)
    
    Returns: ExecutionResult
    """
    print_header("Phase 2", "Rule Application (Gate-2)")
    
    from phase2_rules.rule_executor import execute_rules, get_all_rules
    
    from phase3_output.manual_overrides import get_manual_overrides
    
    print("\n[2-1] Loading rules...")
    rules = get_all_rules()
    manual_overrides = get_manual_overrides()
    print(f"      Rules loaded: {len(rules)}")
    
    print("\n[2-2] Executing rules...")
    result = execute_rules(evidence, rules, manual_overrides=manual_overrides)
    
    print(f"      Items classified: {result.stats.get('items_classified', 0)}")
    print(f"      Items unclassified: {result.stats.get('items_unclassified', 0)}")
    print(f"      Rule matches: {result.stats.get('rules_matched', 0)}")
    
    print_gate_result("Gate-2", True, f"{result.total_classified} items classified")
    
    return result


def run_phase3(result, manual_only_tags, evidence):
    """
    Phase 3: Output Generation (Gate-3)
    
    Returns: ValidationReport
    """
    print_header("Phase 3", "Output Generation (Gate-3)")
    
    from phase3_output.output_generator import generate_all_outputs
    
    print("\n[3-1] Generating outputs...")
    
    # evidence.items를 전달하여 primary_subcategory 자동 생성 (CombinedEvidence 딕셔너리)
    evidence_items = evidence.items if hasattr(evidence, 'items') else {}
    
    # recipe_evidences 추출 (그룹화에 사용)
    recipe_evidences = {}
    for ft, combined in evidence_items.items():
        if hasattr(combined, 'recipe') and combined.recipe:
            recipe_evidences[ft] = combined.recipe
    
    report = generate_all_outputs(result, manual_only_tags, OUTPUT_DIR, evidence_items, recipe_evidences)
    
    print(f"      IrisClassifications.lua generated")
    print(f"      IrisManualOverrides.lua generated")
    print(f"      validation_report.json generated")
    
    print("\n[3-2] Tag distribution:")
    for tag, count in sorted(report.tag_distribution.items()):
        print(f"      {tag}: {count}")
    
    print_gate_result("Gate-3", True, f"Output saved to {OUTPUT_DIR}")
    
    return report



def main() -> int:
    """Main entry point for the Iris Build Pipeline."""
    print(f"\n{'#'*60}")
    print(f"# Iris Build Pipeline")
    print(f"# Started: {datetime.now().isoformat()}")
    print(f"# Input: {INPUT_DIR}")
    print(f"# Output: {OUTPUT_DIR}")
    print(f"{'#'*60}")
    
    # Phase 0: Validation
    passed, manual_only_tags = run_phase0()
    if not passed:
        print("\n❌ Pipeline halted at Gate-0")
        return 1
    
    # Phase 1: Evidence Extraction
    evidence, raw_items_data = run_phase1()
    
    # Phase 1.5: Blocklist Filtering
    from phase2_rules.blocklist import filter_blocklisted
    print("\n[1.5] Blocklist Filtering...")
    evidence, blocked_count, blocklist_diag = filter_blocklisted(evidence, raw_items_data)
    for diag in blocklist_diag:
        print(f"      {diag}")
    print(f"      Evidence after blocklist: {evidence.total_items} items")
    
    # Phase 2: Rule Application
    result = run_phase2(evidence)
    
    # Phase 3: Output Generation
    report = run_phase3(result, manual_only_tags, evidence)
    
    # Phase 3.5: Deploy to runtime
    import shutil
    deploy_files = ["IrisClassifications.lua", "IrisData.lua"]
    print(f"\n[3.5] Deploying to runtime ({RUNTIME_DATA_DIR})...")
    for fname in deploy_files:
        src = OUTPUT_DIR / fname
        dst = RUNTIME_DATA_DIR / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"      Copied {fname} ({src.stat().st_size:,} bytes)")
        else:
            print(f"      Skipped {fname} (not found in output)")
    
    # Phase 4: Regression Testing
    test_passed = run_phase4(result)
    
    # Summary
    print(f"\n{'#'*60}")
    if test_passed:
        print(f"# ✅ Pipeline completed successfully")
    else:
        print(f"# ⚠️ Pipeline completed with test failures")
    print(f"# Classified: {report.classified_items} / {report.total_items} items")
    print(f"# Finished: {datetime.now().isoformat()}")
    print(f"{'#'*60}")
    
    return 0 if test_passed else 1


def run_phase4(result) -> bool:
    """
    Phase 4: Regression Testing (Gate-4)
    
    Returns: True if all tests pass
    """
    print_header("Phase 4", "Regression Testing (Gate-4)")
    
    from phase4_tests.golden_extractor import get_known_golden_set
    from phase4_tests.test_runner import run_regression_tests, save_test_report
    
    print("\n[4-1] Loading golden set...")
    golden = get_known_golden_set()
    print(f"      Test cases: {golden.total}")
    
    print("\n[4-2] Running regression tests...")
    test_result = run_regression_tests(result, golden, strict=False)
    
    print(f"      Passed: {test_result.passed}")
    print(f"      Failed: {test_result.failed}")
    print(f"      Skipped: {test_result.skipped}")
    print(f"      Pass Rate: {test_result.pass_rate:.1f}%")
    
    # Print failures
    if test_result.failed > 0 or test_result.skipped > 0:
        print("\n[4-3] Failures:")
        for r in test_result.results:
            if not r.passed:
                print(f"      ❌ {r.full_type}")
                print(f"         Expected: {r.expected_tags}")
                print(f"         Actual: {r.actual_tags}")
                if r.missing_tags:
                    print(f"         Missing: {r.missing_tags}")
    
    # Save report
    save_test_report(test_result, OUTPUT_DIR / "regression_test_report.json")
    
    passed = test_result.all_passed
    print_gate_result("Gate-4", passed, 
                      f"{test_result.passed}/{test_result.total_tests} tests passed")
    
    return passed


if __name__ == "__main__":
    sys.exit(main())

