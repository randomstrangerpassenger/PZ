"""
build_dvf_3_3_compose.py — DVF 3-3 facts + decisions + gaps 생성기

입력:
- dvf_3_3_compose_input.jsonl (1050건 compose 대상)
- identity_category_ko.json (카테고리 → 한국어 매핑)
- identity_hint_overrides.jsonl (아이템 단위 override)
- compose_profiles.json (프로파일 정의, max_length_chars 참조)

출력:
- dvf_3_3_facts.jsonl
- dvf_3_3_decisions.jsonl
- dvf_3_3_gaps.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


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


def write_json(path: Path, data, *, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def sha256_hex(payload) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# identity_hint 생성
# ---------------------------------------------------------------------------

IDENTITY_HINT_MAX_CHARS = 30


def build_identity_hint(
    fulltype: str,
    display_category: str,
    type_value: str,
    category_map: dict[str, str],
    overrides: dict[str, str],
) -> tuple[str, str]:
    """
    identity_hint 생성.
    Returns: (hint_text, origin)  origin = "override" | "category_rule"
    Raises: ValueError if key miss.
    """
    # 1. override 우선
    if fulltype in overrides:
        return overrides[fulltype], "override"

    # 2. 카테고리 매핑
    key = f"{display_category}|{type_value}"
    if key in category_map:
        return category_map[key], "category_rule"

    # 3. 키 미스 → FAIL
    raise ValueError(
        f"identity_hint 키 미스: fulltype={fulltype}, key={key}. "
        "identity_category_ko.json에 해당 조합이 없습니다."
    )


# ---------------------------------------------------------------------------
# 메인 빌드 함수
# ---------------------------------------------------------------------------

def build_dvf_3_3(
    compose_input: list[dict],
    category_map: dict[str, str],
    overrides: dict[str, str],
    profiles: dict,
    *,
    sync_queue_sha: str | None = None,
    candidate_state_sha: str | None = None,
) -> dict:
    """
    facts + decisions + gaps 생성.

    Returns: {
        "facts": [...],
        "decisions": [...],
        "gaps": [...],
        "errors": [...],
        "stats": {...},
    }
    """
    facts_rows: list[dict] = []
    decisions_rows: list[dict] = []
    gaps: list[dict] = []
    errors: list[str] = []

    for row in compose_input:
        fulltype = row["fulltype"]
        prefix = f"[{fulltype}]"
        dvf_profile = row["dvf_compose_profile"]

        # identity_hint 생성
        try:
            identity_hint, identity_origin = build_identity_hint(
                fulltype,
                row["display_category"],
                row["type_value"],
                category_map,
                overrides,
            )
        except ValueError as e:
            errors.append(f"{prefix} {e}")
            continue

        # identity_hint 길이 검사
        if len(identity_hint) > IDENTITY_HINT_MAX_CHARS:
            errors.append(
                f"{prefix} identity_hint 길이 초과: {len(identity_hint)}자 > {IDENTITY_HINT_MAX_CHARS}자 "
                f"(값: '{identity_hint}')"
            )
            continue

        acquisition_hint = row.get("acquisition_hint")
        acquisition_null_reason = row.get("acquisition_null_reason")

        # 프로파일에서 max_length 조회
        profile_def = profiles.get(dvf_profile)
        if not profile_def:
            errors.append(f"{prefix} 프로파일 정의 없음: {dvf_profile}")
            continue
        max_length = profile_def["max_length_chars"]

        # 전체 길이 사전 검사
        # 조합 결과: "{identity_hint}. {acquisition_hint}."
        if acquisition_hint:
            composed_text = f"{identity_hint}. {acquisition_hint}."
        else:
            composed_text = f"{identity_hint}."

        total_length = len(composed_text)

        if total_length > max_length:
            gaps.append({
                "fulltype": fulltype,
                "dvf_compose_profile": dvf_profile,
                "total_length": total_length,
                "max_length_chars": max_length,
                "cause": "LENGTH_OVERFLOW",
                "identity_hint": identity_hint,
                "acquisition_hint": acquisition_hint,
            })
            continue

        # facts 행 생성
        fact_row = {
            "item_id": fulltype,
            "identity_hint": identity_hint,
            "acquisition_hint": acquisition_hint,
            "primary_use": None,
            "secondary_use": None,
            "processing_hint": None,
            "special_context": None,
            "limitation_hint": None,
            "notes": None,
            "slot_meta": {
                "acquisition_hint": {
                    "mode": "location" if dvf_profile == "acq_location" else "method",
                },
            },
            "fact_origin": {
                "identity_hint": [identity_origin],
                "acquisition_hint": ["phase2_reviewed"],
            },
        }
        facts_rows.append(fact_row)

        # decisions 행 생성
        decision_row = {
            "item_id": fulltype,
            "state": "active",
            "reason_code": "HAS_NON_TRIVIAL_ACQUISITION_CONTEXT",
            "compose_profile": dvf_profile,
            "facts_ref": fulltype,
            "override_mode": "none",
            "manual_override_text_ko": None,
            "acquisition_null_reason": acquisition_null_reason,
            "approval_state_snapshot": row.get("approval_state"),
            "phase3_sync_source_hash": sync_queue_sha,
            "phase3_candidate_source_hash": candidate_state_sha,
        }
        decisions_rows.append(decision_row)

    # 정렬
    facts_rows.sort(key=lambda r: r["item_id"])
    decisions_rows.sort(key=lambda r: r["item_id"])
    gaps.sort(key=lambda r: r["fulltype"])

    stats = {
        "compose_input_count": len(compose_input),
        "facts_count": len(facts_rows),
        "decisions_count": len(decisions_rows),
        "gap_count": len(gaps),
        "error_count": len(errors),
        "identity_equation_check": (
            len(facts_rows) == len(decisions_rows)
            and len(facts_rows) + len(gaps) + len(errors) == len(compose_input)
        ),
    }

    return {
        "facts": facts_rows,
        "decisions": decisions_rows,
        "gaps": gaps,
        "errors": errors,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# worktree 경로 해석
# ---------------------------------------------------------------------------

def find_main_repo_v2() -> Path:
    """worktree 또는 main repo에서 v2 루트를 찾는다."""
    script_v2 = Path(__file__).resolve().parent.parent.parent
    staging_candidate = script_v2 / "staging" / "phase3" / "phase3_sync_queue.jsonl"
    if staging_candidate.exists():
        return script_v2

    for parent in script_v2.parents:
        candidate = parent / "Iris" / "build" / "description" / "v2"
        check = candidate / "staging" / "phase3" / "phase3_sync_queue.jsonl"
        if check.exists() and candidate != script_v2:
            return candidate

    raise FileNotFoundError("staging/phase3/phase3_sync_queue.jsonl을 찾을 수 없음")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="DVF 3-3 facts/decisions/gaps 생성")
    parser.add_argument("buckets", nargs="*", help="버킷 필터 (생략 시 전량)")
    args = parser.parse_args()

    v2_root = find_main_repo_v2()
    data_dir = v2_root / "data"
    phase3_dir = v2_root / "staging" / "phase3"

    # 입력 로드
    compose_input_path = phase3_dir / "dvf_3_3_compose_input.jsonl"
    category_map_path = data_dir / "identity_category_ko.json"
    overrides_path = data_dir / "identity_hint_overrides.jsonl"
    profiles_path = data_dir / "compose_profiles.json"

    for p in [compose_input_path, category_map_path, profiles_path]:
        if not p.exists():
            print(f"FATAL: 파일 없음: {p}")
            sys.exit(1)

    compose_input = load_jsonl(compose_input_path)
    category_map = load_json(category_map_path)
    profiles = load_json(profiles_path)

    # overrides 로드 (없거나 비어있으면 빈 dict)
    overrides: dict[str, str] = {}
    if overrides_path.exists():
        for row in load_jsonl(overrides_path):
            ft = row.get("fulltype")
            hint = row.get("identity_hint_override")
            if ft and hint:
                overrides[ft] = hint

    # 버킷 필터
    if args.buckets:
        bucket_filter = set(args.buckets)
        compose_input = [r for r in compose_input if r.get("bucket_id") in bucket_filter]
        print(f"Bucket filter: {sorted(bucket_filter)} → {len(compose_input)}건")

    # provenance SHA
    sync_queue_path = phase3_dir / "phase3_sync_queue.jsonl"
    candidate_path = phase3_dir / "candidate_state_phase3.review.jsonl"
    sync_sha = sha256_hex(load_jsonl(sync_queue_path)) if sync_queue_path.exists() else None
    candidate_sha = sha256_hex(load_jsonl(candidate_path)) if candidate_path.exists() else None

    # 빌드
    result = build_dvf_3_3(
        compose_input,
        category_map,
        overrides,
        profiles,
        sync_queue_sha=sync_sha,
        candidate_state_sha=candidate_sha,
    )

    if result["errors"]:
        print(f"ERRORS ({len(result['errors'])}):")
        for e in result["errors"]:
            print(f"  ✗ {e}")
        sys.exit(1)

    # 출력
    facts_path = data_dir / "dvf_3_3_facts.jsonl"
    decisions_path = data_dir / "dvf_3_3_decisions.jsonl"
    gaps_path = v2_root / "output" / "dvf_3_3_gaps.json"

    write_jsonl(facts_path, result["facts"])
    write_jsonl(decisions_path, result["decisions"])
    write_json(gaps_path, result["gaps"])

    stats = result["stats"]
    print(f"=== DVF 3-3 Build ===")
    print(f"  Facts: {stats['facts_count']}")
    print(f"  Decisions: {stats['decisions_count']}")
    print(f"  Gaps: {stats['gap_count']}")
    print(f"  Identity equation: {'PASS' if stats['identity_equation_check'] else 'FAIL'}")
    print(f"  Output facts: {facts_path}")
    print(f"  Output decisions: {decisions_path}")
    print(f"  Output gaps: {gaps_path}")

    if stats["gap_count"] > 0:
        print(f"\n  ⚠ gap_count = {stats['gap_count']} (초기 배치 기준 FAIL)")
        sys.exit(1)

    print(f"  ✅ PASS")


if __name__ == "__main__":
    main()
