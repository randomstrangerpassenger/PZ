"""
extract_dvf_3_3_compose_input.py — sync queue에서 APPROVE_SYNC 1050건 추출

3파일 조인:
1. phase3_sync_queue.jsonl  → approval_state == "APPROVE_SYNC" 필터 (canonical truth)
2. candidate_state_phase3.review.jsonl → acquisition_hint, phase2_snapshot_hash 조인
3. staging/reviews/*.acquisition.jsonl → display_name, display_category, type_value 조인

출력:
- dvf_3_3_compose_input.jsonl (1050행)
- dvf_3_3_compose_manifest.json (메타/통계)
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# 프로파일 매핑
# ---------------------------------------------------------------------------

PHASE3_TO_DVF_PROFILE = {
    "ACQ_ONLY_LOCATION": "acq_location",
    "ACQ_ONLY_METHOD": "acq_method",
    "IDENTITY_PLUS_ACQ": "identity_acq",
    "USE_PLUS_ACQ": "use_acq",
}


# ---------------------------------------------------------------------------
# 데이터 로더
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict]:
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    f.close()


def sha256_hex(payload) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def extract_compose_input(
    staging_dir: Path,
    *,
    bucket_filter: set[str] | None = None,
) -> dict:
    """
    1050건 compose 대상 세트 추출.

    Args:
        staging_dir: description/v2/staging 디렉토리
        bucket_filter: None이면 전량, set이면 해당 버킷만

    Returns: {"rows": [...], "manifest": {...}, "errors": [...]}
    """
    phase3_dir = staging_dir / "phase3"
    reviews_dir = staging_dir / "reviews"

    sync_queue_path = phase3_dir / "phase3_sync_queue.jsonl"
    overlay_path = phase3_dir / "candidate_state_phase3.review.jsonl"

    errors: list[str] = []

    # 1. sync queue 로드 + APPROVE_SYNC 필터
    sync_rows = load_jsonl(sync_queue_path)
    approved = [r for r in sync_rows if r.get("approval_state") == "APPROVE_SYNC"]

    if bucket_filter:
        approved = [r for r in approved if r.get("bucket_id") in bucket_filter]

    # 2. phase3 overlay 인덱스 (fulltype → row)
    overlay_rows = load_jsonl(overlay_path)
    overlay_index: dict[str, dict] = {}
    for row in overlay_rows:
        ft = row.get("fulltype")
        if ft:
            overlay_index[ft] = row

    # 3. Phase 2 review 인덱스 (item_id → row)
    phase2_index: dict[str, dict] = {}
    review_files = sorted(reviews_dir.glob("*.acquisition.jsonl"))
    for path in review_files:
        for line in open(path, "r", encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            item_id = row.get("item_id")
            if item_id:
                phase2_index[item_id] = row

    # 4. 조인 + compose input 생성
    compose_rows: list[dict] = []
    seen_fulltypes: set[str] = set()

    for sq_row in approved:
        fulltype = sq_row["fulltype"]
        prefix = f"[{fulltype}]"

        # 중복 체크
        if fulltype in seen_fulltypes:
            errors.append(f"{prefix} fulltype 중복")
            continue
        seen_fulltypes.add(fulltype)

        # overlay 조인
        ov = overlay_index.get(fulltype)
        if not ov:
            errors.append(f"{prefix} phase3 overlay에 없음")
            continue

        # phase2 조인
        p2 = phase2_index.get(fulltype)
        if not p2:
            errors.append(f"{prefix} phase2 review에 없음")
            continue

        # 프로파일 매핑
        phase3_profile = sq_row.get("candidate_compose_profile")
        dvf_profile = PHASE3_TO_DVF_PROFILE.get(phase3_profile)
        if not dvf_profile:
            errors.append(f"{prefix} 알 수 없는 phase3 프로파일: {phase3_profile}")
            continue

        compose_row = {
            "fulltype": fulltype,
            "bucket_id": sq_row.get("bucket_id"),
            "display_name": p2.get("display_name"),
            "display_category": p2.get("display_category"),
            "type_value": p2.get("type_value"),
            "approval_state": sq_row.get("approval_state"),
            "approval_reason_code": sq_row.get("approval_reason_code"),
            "phase3_reason_code": sq_row.get("candidate_reason_code"),
            "phase3_compose_profile": phase3_profile,
            "dvf_compose_profile": dvf_profile,
            "acquisition_hint": ov.get("phase2_acquisition_hint_snapshot"),
            "acquisition_null_reason": ov.get("phase2_null_reason_snapshot"),
            "phase2_snapshot_hash": ov.get("phase2_snapshot_hash"),
            "sync_queue_version": sq_row.get("queue_version"),
        }
        compose_rows.append(compose_row)

    # fulltype 정렬
    compose_rows.sort(key=lambda r: r["fulltype"])

    # 매니페스트
    profile_breakdown = dict(Counter(r["dvf_compose_profile"] for r in compose_rows))
    total_sync = sum(1 for r in sync_rows if r.get("approval_state") == "APPROVE_SYNC")
    total_hold = sum(1 for r in sync_rows if r.get("approval_state") == "HOLD")
    total_silent = len(overlay_rows) - len(sync_rows)

    manifest = {
        "total_compose_target": len(compose_rows),
        "excluded_hold": total_hold,
        "excluded_keep_silent": total_silent,
        "profile_breakdown": dict(sorted(profile_breakdown.items())),
        "source_sync_queue": "phase3_sync_queue.jsonl",
        "source_phase3_determinism_sha": sha256_hex(
            [{"fulltype": r["fulltype"], "bucket_id": r["bucket_id"]}
             for r in sorted(overlay_rows, key=lambda x: x.get("fulltype", ""))]
        ),
        "compose_input_sha": sha256_hex(compose_rows),
        "build_version": "dvf-3-3-compose-v1",
    }

    if bucket_filter:
        manifest["bucket_filter"] = sorted(bucket_filter)

    return {"rows": compose_rows, "manifest": manifest, "errors": errors}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def find_main_repo_v2() -> Path:
    """worktree 또는 main repo에서 v2 루트를 찾는다."""
    # 현재 스크립트 위치 기준
    script_v2 = Path(__file__).resolve().parent.parent.parent
    staging_candidate = script_v2 / "staging" / "phase3" / "phase3_sync_queue.jsonl"
    if staging_candidate.exists():
        return script_v2

    # worktree인 경우 main repo 경로 탐색
    # .claude/worktrees/<name>/Iris/... → main repo는 .claude의 3단계 위
    for parent in script_v2.parents:
        candidate = parent / "Iris" / "build" / "description" / "v2"
        check = candidate / "staging" / "phase3" / "phase3_sync_queue.jsonl"
        if check.exists() and candidate != script_v2:
            return candidate

    raise FileNotFoundError("staging/phase3/phase3_sync_queue.jsonl을 찾을 수 없음")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DVF 3-3 compose input 추출")
    parser.add_argument("buckets", nargs="*", help="버킷 필터 (생략 시 전량)")
    parser.add_argument("--staging-dir", type=Path, default=None,
                        help="staging 디렉토리 경로 (기본: 자동 탐색)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="출력 디렉토리 (기본: staging/phase3/)")
    args = parser.parse_args()

    if args.staging_dir:
        staging_dir = args.staging_dir
    else:
        v2_root = find_main_repo_v2()
        staging_dir = v2_root / "staging"

    phase3_dir = staging_dir / "phase3"
    output_dir = args.output_dir or phase3_dir

    bucket_filter = set(args.buckets) if args.buckets else None
    if bucket_filter:
        print(f"Bucket filter: {sorted(bucket_filter)}")

    result = extract_compose_input(staging_dir, bucket_filter=bucket_filter)

    if result["errors"]:
        print(f"ERRORS ({len(result['errors'])}):")
        for e in result["errors"]:
            print(f"  ✗ {e}")
        sys.exit(1)

    rows = result["rows"]
    manifest = result["manifest"]

    # 출력
    output_jsonl = output_dir / "dvf_3_3_compose_input.jsonl"
    output_manifest = output_dir / "dvf_3_3_compose_manifest.json"

    write_jsonl(output_jsonl, rows)
    write_json(output_manifest, manifest)

    print(f"=== DVF 3-3 Compose Input Extraction ===")
    print(f"  Total compose target: {manifest['total_compose_target']}")
    print(f"  Excluded hold: {manifest['excluded_hold']}")
    print(f"  Excluded keep_silent: {manifest['excluded_keep_silent']}")
    print(f"  Profile breakdown: {manifest['profile_breakdown']}")
    print(f"  Output: {output_jsonl}")
    print(f"  Manifest: {output_manifest}")
    print(f"  ✅ PASS")


if __name__ == "__main__":
    main()
