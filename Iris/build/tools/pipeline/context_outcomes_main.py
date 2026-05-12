"""
Iris Context Outcome Build Main (v2)
====================================
Context Outcome 정적 추출 메인 엔트리포인트

파이프라인 구조 (v2 리팩터링):
1. [MAIN] ItemScript 파싱 → Outcome 추출 (단일 소스)
2. [DIAGNOSTIC] Lua 스캐너 (진단 전용, Outcome 생성 안 함)
3. Option B 수동 주입 (smoke_item)
4. 검증 (Fail-loud 3종)
5. 출력 생성 (JSON + Lua)
"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# v2: ItemScript 기반 메인
from build.phase1_extraction.itemscript_outcome_extractor import (
    parse_item_scripts,
    extract_outcomes_from_scripts
)

# v2: Lua 스캐너는 진단 전용
from build.phase1_extraction.context_outcome_scanner import scan_directory, ScanDiagnostic

# 나머지는 그대로
from build.phase2_rules.manual_injector import inject_option_b_outcomes
from build.phase3_output.validators import validate_all, write_diagnostics
from build.phase3_output.context_outcomes_generator import (
    generate_context_outcomes_json,
    generate_context_outcomes_lua
)


def run_context_outcome_pipeline(
    scripts_dir: Path | None = None,
    lua_input_dir: Path | None = None,
    output_dir: Path | None = None,
    data_dir: Path | None = None,
    skip_lua_scan: bool = False,
) -> tuple[str, list[str]]:
    """
    Context Outcome 전체 파이프라인 실행 (v2)
    
    Args:
        scripts_dir: ItemScript 폴더 (media/scripts)
        lua_input_dir: Lua 소스 폴더 (진단 전용)
        output_dir: 출력 폴더
        data_dir: 데이터 폴더 (smoke_items.json)
        skip_lua_scan: Lua 스캔 생략 여부
    
    Returns:
        (SHA-256 해시, 진단 목록)
    """
    # 기본 경로 설정
    iris_root = Path(__file__).resolve().parents[3]
    pz_root = iris_root.parent  # Iris의 부모 = PZ 루트
    
    if scripts_dir is None:
        scripts_dir = pz_root / "scripts"
    
    if lua_input_dir is None:
        lua_input_dir = pz_root / "lua"
    
    if output_dir is None:
        output_dir = iris_root / "output"
    
    if data_dir is None:
        data_dir = iris_root / "build" / "data"
    
    all_diagnostics: list[str] = []
    
    print("=" * 60)
    print("Iris Context Outcome Build Pipeline (v2)")
    print("=" * 60)
    
    # ========================================
    # Phase 1: ItemScript 파싱 (MAIN SOURCE)
    # ========================================
    print("\n[Phase 1] Parsing ItemScripts (PRIMARY)...")
    
    if not scripts_dir.exists():
        print(f"  ❌ Scripts directory not found: {scripts_dir}")
        raise FileNotFoundError(f"Scripts directory required: {scripts_dir}")
    
    items = parse_item_scripts(scripts_dir)
    print(f"  Parsed {len(items)} items from scripts")
    
    # Phase 2: 필드 → Outcome 매핑
    print("\n[Phase 2] Extracting outcomes from fields...")
    context_outcomes = extract_outcomes_from_scripts(items)
    print(f"  Extracted outcomes for {len(context_outcomes)} items")
    
    # ========================================
    # Phase 1.5: Lua 스캐너 (DIAGNOSTIC ONLY)
    # ========================================
    if not skip_lua_scan and lua_input_dir.exists():
        print("\n[Phase 1.5] Lua Scanner (DIAGNOSTIC ONLY)...")
        try:
            signal_records, scan_diagnostics = scan_directory(lua_input_dir)
            print(f"  Scanned {len(signal_records)} files")
            print(f"  Diagnostics: {len(scan_diagnostics)}")
            
            # 진단 기록만 (Outcome 생성 안 함!)
            for d in scan_diagnostics:
                all_diagnostics.append(f"[LUA-SCAN] {d.token} at {d.file}:{d.line}")
            
            # 커버리지 힌트: Lua에서 발견되었지만 ItemScript에 없는 패턴
            lua_fulltype_hints = set()
            for file_key, record in signal_records.items():
                # 파일 기반 힌트만 기록 (실제 아이템 추출은 불가)
                if record.signals:
                    lua_fulltype_hints.add(file_key)
            
            if lua_fulltype_hints:
                all_diagnostics.append(
                    f"[COVERAGE-HINT] {len(lua_fulltype_hints)} Lua files contain signals "
                    f"(not used for outcome generation)"
                )
        except Exception as e:
            all_diagnostics.append(f"[LUA-SCAN] Error: {e}")
            print(f"  ⚠️ Lua scan error (non-fatal): {e}")
    else:
        print("\n[Phase 1.5] Lua Scanner skipped")
    
    # ========================================
    # Phase 3: Option B 수동 주입
    # ========================================
    print("\n[Phase 3] Injecting Option B (smoke_item)...")
    context_outcomes, inject_diagnostics = inject_option_b_outcomes(
        context_outcomes, data_dir
    )
    all_diagnostics.extend(inject_diagnostics)
    
    # ========================================
    # Phase 4: 출력 생성
    # ========================================
    print("\n[Phase 4] Generating outputs...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / "context_outcomes.json"
    lua_path = output_dir / "context_outcomes.lua"
    
    sha256 = generate_context_outcomes_json(context_outcomes, json_path)
    print(f"  JSON: {json_path}")
    print(f"  SHA-256: {sha256}")
    
    generate_context_outcomes_lua(context_outcomes, lua_path)
    print(f"  Lua: {lua_path}")
    
    # ========================================
    # Phase 5: Fail-loud 3종 검증 (입력 계약 Gate)
    # ⚠️ 검증 실패 시 Phase 6 실행 안 됨 = 복사/커밋 차단
    # ========================================
    print("\n[Phase 5] Running Fail-loud validations...")
    try:
        validate_all(json_path)  # expected_sha 없이 실행 (첫 실행이므로)
        print("  ✅ All validations passed")
        validation_passed = True
    except ValueError as e:
        print(f"  ❌ Validation failed: {e}")
        print("  ⚠️ Phase 6 (복사) will NOT execute due to validation failure")
        raise
    
    # ========================================
    # Phase 6: Iris Data 폴더에 복사
    # ========================================
    print("\n[Phase 6] Copying to Iris Data folder...")
    iris_data_dir = iris_root / "media" / "lua" / "client" / "Iris" / "Data"
    if iris_data_dir.exists():
        import shutil
        target_lua = iris_data_dir / "IrisContextOutcomes.lua"
        shutil.copy2(lua_path, target_lua)
        print(f"  ✅ Copied to: {target_lua}")
    else:
        print(f"  ⚠️ Iris Data directory not found: {iris_data_dir}")
        all_diagnostics.append(f"[COPY] Iris Data directory not found: {iris_data_dir}")
    
    # 진단 출력
    if all_diagnostics:
        print(f"\n[Diagnostics] {len(all_diagnostics)} items")
        write_diagnostics(all_diagnostics, output_dir)
        print(f"  Written to: {output_dir / 'diagnostics.json'}")
    
    # 통계 출력
    outcome_counts: dict[str, int] = {}
    for outcomes in context_outcomes.values():
        for o in outcomes:
            outcome_counts[o] = outcome_counts.get(o, 0) + 1
    
    print("\n[Statistics] Outcome distribution:")
    for outcome, count in sorted(outcome_counts.items()):
        print(f"  {outcome}: {count}")
    
    print("\n" + "=" * 60)
    print("✅ Context Outcome pipeline completed successfully")
    print("=" * 60)
    
    return sha256, all_diagnostics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Iris Context Outcome Build (v2)")
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        help="ItemScript directory (media/scripts)"
    )
    parser.add_argument(
        "--lua-dir",
        type=Path,
        help="Lua source directory (diagnostic only)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Data directory (contains smoke_items.json)"
    )
    parser.add_argument(
        "--skip-lua-scan",
        action="store_true",
        help="Skip Lua scanning (diagnostics only anyway)"
    )
    
    args = parser.parse_args()
    
    try:
        sha, diagnostics = run_context_outcome_pipeline(
            scripts_dir=args.scripts_dir,
            lua_input_dir=args.lua_dir,
            output_dir=args.output_dir,
            data_dir=args.data_dir,
            skip_lua_scan=args.skip_lua_scan,
        )
        print(f"\nFinal SHA-256: {sha}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
