"""
run_pipeline.py — 3계층 DVF 파이프라인 진입점

DVF는 3계층 본문 전용 엔진이다.

4단계 오케스트레이션:
[1/4] 입력 검증
[2/4] 조합 실행
[3/4] rendered 검증
[4/4] 결정론 검증
"""

import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parent
TOOLS_DIR = V2_ROOT / 'tools'
BUILD_DIR = TOOLS_DIR / 'build'
DVF_DIR = TOOLS_DIR / 'dvf'

sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(BUILD_DIR))
sys.path.insert(0, str(DVF_DIR))

from compose_layer3_text import load_jsonl, load_json, build_rendered, compose_all
from run_dvf_layer3 import run_dvf


def main():
    data_dir = V2_ROOT / 'data'
    output_dir = V2_ROOT / 'output'

    facts_path = data_dir / 'layer3_facts.jsonl'
    decisions_path = data_dir / 'layer3_decisions.jsonl'
    profiles_path = data_dir / 'compose_profiles.json'
    forbidden_path = data_dir / 'forbidden_patterns.json'
    rendered_path = output_dir / 'layer3_rendered.json'

    for p in [facts_path, decisions_path, profiles_path, forbidden_path]:
        if not p.exists():
            print(f"FATAL: 필수 입력 파일 없음: {p}")
            sys.exit(1)

    facts_list = load_jsonl(facts_path)
    decisions_list = load_jsonl(decisions_path)
    profiles = load_json(profiles_path)
    forbidden = load_json(forbidden_path)

    print(f"=== Iris Layer 3 DVF Pipeline ===")
    print(f"  Facts: {len(facts_list)} items")
    print(f"  Decisions: {len(decisions_list)} items")
    print(f"  Profiles: {len(profiles)} profiles")
    print()

    # [2/4] 조합 실행
    print("[2/4] 조합 실행...")
    try:
        rendered = build_rendered(facts_path, decisions_path, profiles_path, rendered_path)
        print(f"  → {rendered_path} 저장 완료")
    except Exception as e:
        print(f"  FATAL: 조합 실행 실패: {e}")
        sys.exit(1)

    # [1,3,4/4] DVF 통합 검증
    print("[1,3,4/4] DVF 통합 검증...")
    dvf_result = run_dvf(
        facts_list=facts_list,
        decisions_list=decisions_list,
        profiles=profiles,
        forbidden_patterns=forbidden,
        rendered=rendered,
        compose_fn=compose_all,
    )

    print()
    if dvf_result["warnings"]:
        print(f"⚠ WARNINGS ({len(dvf_result['warnings'])}):")
        for w in dvf_result["warnings"]:
            print(f"  - {w}")
        print()

    if dvf_result["pass"]:
        stats = rendered.get('meta', {}).get('stats', {})
        print("✅ PASS")
        print(f"  Total: {stats.get('total', '?')}")
        print(f"  Composed: {stats.get('active_composed', '?')}")
        print(f"  Override: {stats.get('active_override', '?')}")
        print(f"  Silent: {stats.get('silent', '?')}")
        print(f"  Override ratio: {stats.get('override_ratio', '?')}")
        sys.exit(0)
    else:
        print(f"❌ FAIL ({len(dvf_result['errors'])} errors)")
        for e in dvf_result["errors"]:
            print(f"  ✗ {e}")

        report_path = output_dir / 'dvf_error_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(dvf_result, f, ensure_ascii=False, indent=2)
        print(f"\n  에러 리포트: {report_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
