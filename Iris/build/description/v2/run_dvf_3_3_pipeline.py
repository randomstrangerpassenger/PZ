"""
run_dvf_3_3_pipeline.py — DVF 3-3 전용 파이프라인 진입점

기존 demo 10건 파이프라인(run_pipeline.py)과 독립 실행.

단계:
[1] build_dvf_3_3_compose → facts/decisions/gaps 생성
[2] compose_layer3_text → rendered 생성
[3] DVF 4단계 검증 (입력/rendered/결정론)
[4] 배치 전용 검증 (validate_dvf_3_3_batch)
[5] 요약 출력
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 경로 설정
# ---------------------------------------------------------------------------


def find_main_repo_v2() -> Path:
    """worktree 또는 main repo에서 v2 루트를 찾는다."""
    script_v2 = Path(__file__).resolve().parent
    staging_candidate = script_v2 / "staging" / "phase3" / "phase3_sync_queue.jsonl"
    if staging_candidate.exists():
        return script_v2

    for parent in script_v2.parents:
        candidate = parent / "Iris" / "build" / "description" / "v2"
        check = candidate / "staging" / "phase3" / "phase3_sync_queue.jsonl"
        if check.exists() and candidate != script_v2:
            return candidate

    raise FileNotFoundError("staging/phase3/phase3_sync_queue.jsonl을 찾을 수 없음")


def setup_paths():
    v2_root = find_main_repo_v2()
    # Also add the worktree v2 root for tools that live there
    script_v2 = Path(__file__).resolve().parent

    for tools_base in [v2_root, script_v2]:
        tools_dir = tools_base / "tools"
        for sub in ["build", "dvf", ""]:
            p = tools_dir / sub if sub else tools_dir
            if p.exists() and str(p) not in sys.path:
                sys.path.insert(0, str(p))

    # Also add v2 root for postproc_ko
    for base in [v2_root, script_v2]:
        if str(base / "tools") not in sys.path:
            sys.path.insert(0, str(base / "tools"))

    return v2_root


V2_ROOT = setup_paths()

from build_dvf_3_3_compose import (
    build_dvf_3_3,
    load_json,
    load_jsonl,
    sha256_hex,
    write_json,
    write_jsonl,
)
from compose_layer3_text import build_rendered, compose_all, entries_sha256
from run_dvf_layer3 import run_dvf
from validate_dvf_3_3_batch import validate_dvf_3_3_batch


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="DVF 3-3 파이프라인")
    parser.add_argument("buckets", nargs="*", help="버킷 필터 (생략 시 전량)")
    args = parser.parse_args()

    data_dir = V2_ROOT / "data"
    phase3_dir = V2_ROOT / "staging" / "phase3"
    output_dir = V2_ROOT / "output"

    # 입력 파일
    compose_input_path = phase3_dir / "dvf_3_3_compose_input.jsonl"
    category_map_path = data_dir / "identity_category_ko.json"
    overrides_path = data_dir / "identity_hint_overrides.jsonl"
    profiles_path = data_dir / "compose_profiles.json"
    forbidden_path = data_dir / "forbidden_patterns.json"
    sync_queue_path = phase3_dir / "phase3_sync_queue.jsonl"
    candidate_path = phase3_dir / "candidate_state_phase3.review.jsonl"

    for p in [compose_input_path, category_map_path, profiles_path, forbidden_path]:
        if not p.exists():
            print(f"FATAL: 파일 없음: {p}")
            sys.exit(1)

    # 로드
    compose_input = load_jsonl(compose_input_path)
    category_map = load_json(category_map_path)
    profiles = load_json(profiles_path)
    forbidden = load_json(forbidden_path)

    overrides: dict[str, str] = {}
    if overrides_path.exists():
        for row in load_jsonl(overrides_path):
            ft = row.get("fulltype")
            hint = row.get("identity_hint_override")
            if ft and hint:
                overrides[ft] = hint

    sync_queue = load_jsonl(sync_queue_path) if sync_queue_path.exists() else None

    # 버킷 필터
    if args.buckets:
        bucket_filter = set(args.buckets)
        compose_input = [r for r in compose_input if r.get("bucket_id") in bucket_filter]
        print(f"Bucket filter: {sorted(bucket_filter)} → {len(compose_input)}건")
    else:
        print(f"전량 모드: {len(compose_input)}건")

    # provenance
    sync_sha = sha256_hex(load_jsonl(sync_queue_path)) if sync_queue_path.exists() else None
    candidate_sha = sha256_hex(load_jsonl(candidate_path)) if candidate_path.exists() else None

    # ===== [1] Build facts/decisions/gaps =====
    print("\n[1/5] facts/decisions/gaps 생성...")
    build_result = build_dvf_3_3(
        compose_input, category_map, overrides, profiles,
        sync_queue_sha=sync_sha,
        candidate_state_sha=candidate_sha,
    )

    if build_result["errors"]:
        print(f"  BUILD ERRORS ({len(build_result['errors'])}):")
        for e in build_result["errors"]:
            print(f"    ✗ {e}")
        sys.exit(1)

    facts_list = build_result["facts"]
    decisions_list = build_result["decisions"]
    gaps = build_result["gaps"]

    print(f"  Facts: {len(facts_list)}, Decisions: {len(decisions_list)}, Gaps: {len(gaps)}")

    # 출력
    facts_path = data_dir / "dvf_3_3_facts.jsonl"
    decisions_path = data_dir / "dvf_3_3_decisions.jsonl"
    gaps_path = output_dir / "dvf_3_3_gaps.json"

    write_jsonl(facts_path, facts_list)
    write_jsonl(decisions_path, decisions_list)
    write_json(gaps_path, gaps)

    # ===== [2] Compose rendered =====
    print("[2/5] 조합 실행...")
    rendered_path = output_dir / "dvf_3_3_rendered.json"
    try:
        rendered = build_rendered(facts_path, decisions_path, profiles_path, rendered_path)
        print(f"  → {rendered_path}")
    except Exception as e:
        print(f"  FATAL: 조합 실패: {e}")
        sys.exit(1)

    # ===== [3] DVF 4단계 검증 =====
    print("[3/5] DVF 4단계 검증...")
    dvf_result = run_dvf(
        facts_list=facts_list,
        decisions_list=decisions_list,
        profiles=profiles,
        forbidden_patterns=forbidden,
        rendered=rendered,
        compose_fn=compose_all,
    )

    if dvf_result["warnings"]:
        print(f"  ⚠ DVF WARNINGS ({len(dvf_result['warnings'])}):")
        for w in dvf_result["warnings"][:10]:
            print(f"    - {w}")

    if not dvf_result["pass"]:
        print(f"  ❌ DVF FAIL ({len(dvf_result['errors'])} errors)")
        for e in dvf_result["errors"][:20]:
            print(f"    ✗ {e}")
        report_path = output_dir / "dvf_3_3_validation_report.json"
        write_json(report_path, dvf_result)
        print(f"  에러 리포트: {report_path}")
        sys.exit(1)

    print("  ✅ DVF PASS")

    # ===== [4] 배치 검증 =====
    print("[4/5] 배치 전용 검증...")
    batch_result = validate_dvf_3_3_batch(
        rendered=rendered,
        compose_input=compose_input,
        gaps=gaps,
        decisions=decisions_list,
        sync_queue=sync_queue,
    )

    if batch_result["warnings"]:
        print(f"  ⚠ BATCH WARNINGS ({len(batch_result['warnings'])}):")
        for w in batch_result["warnings"][:10]:
            print(f"    - {w}")

    if not batch_result["pass"]:
        print(f"  ❌ BATCH FAIL ({len(batch_result['errors'])} errors)")
        for e in batch_result["errors"][:20]:
            print(f"    ✗ {e}")
        report_path = output_dir / "dvf_3_3_validation_report.json"
        write_json(report_path, {
            "dvf": dvf_result,
            "batch": batch_result,
        })
        sys.exit(1)

    print("  ✅ BATCH PASS")

    # ===== [5] 요약 =====
    print("\n[5/5] 요약...")
    stats = rendered.get("meta", {}).get("stats", {})
    summary = {
        "compose_target": len(compose_input),
        "facts_count": len(facts_list),
        "decisions_count": len(decisions_list),
        "rendered_count": stats.get("active_composed", 0),
        "gap_count": len(gaps),
        "dvf_pass": dvf_result["pass"],
        "batch_pass": batch_result["pass"],
        "batch_warnings": len(batch_result["warnings"]),
        "rendered_sha": entries_sha256(rendered.get("entries", {})),
        "build_version": "dvf-3-3-compose-v1",
    }

    summary_path = output_dir / "dvf_3_3_summary.json"
    write_json(summary_path, summary)

    report_path = output_dir / "dvf_3_3_validation_report.json"
    write_json(report_path, {
        "dvf": dvf_result,
        "batch": batch_result,
        "summary": summary,
    })

    print(f"  Compose target: {summary['compose_target']}")
    print(f"  Rendered: {summary['rendered_count']}")
    print(f"  Gaps: {summary['gap_count']}")
    print(f"  DVF: {'PASS' if summary['dvf_pass'] else 'FAIL'}")
    print(f"  Batch: {'PASS' if summary['batch_pass'] else 'FAIL'}")
    print(f"  Warnings: {summary['batch_warnings']}")
    print(f"  SHA: {summary['rendered_sha'][:16]}...")
    print(f"\n  ✅ ALL PASS")


if __name__ == "__main__":
    main()
