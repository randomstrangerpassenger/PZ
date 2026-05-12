"""
build_legacy_candidates.py — Legacy 승격 후보 자동 정렬
======================================================
legacy_inventory.v2.4.json → legacy_upgrade_candidates.v2.4.json

정렬 키 (결정성):
  1. support_status: resolved 우선, unresolved 뒤로
  2. support.candidate_count 내림차순 (영향 큰 것 우선)
  3. support.pass_count 내림차순
  4. diagnosis 길이 오름차순 (문제 적은 것 = 쉬운 것 우선)
  5. rule_id 사전순 (타이브레이크)

운영 규칙:
  - 추론/판정 없음 — 정렬만 수행
  - accept 리스트는 별도 파일(legacy_upgrade_accept.v2.4.json)
"""
import sys
from pathlib import Path

# ── Paths ──
BUILD_DIR = Path(__file__).resolve().parents[2]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json, write_json as save_json
from tools.common.versions import BUILD_VERSION

DATA_DIR = BUILD_DIR / "data" / BUILD_VERSION

INVENTORY_PATH = OUTPUT_DIR / f"legacy_inventory.{BUILD_VERSION}.json"
CANDIDATES_PATH = OUTPUT_DIR / f"legacy_upgrade_candidates.{BUILD_VERSION}.json"
ACCEPT_PATH = DATA_DIR / f"legacy_upgrade_accept.{BUILD_VERSION}.json"


def sort_key(rule_id: str, info: dict) -> tuple:
    """
    정렬 키 (결정성):
    1. support_status: resolved=0, unresolved=1 (resolved 우선)
    2. candidate_count 내림 (큰 것 우선 → 음수)
    3. pass_count 내림
    4. diagnosis 길이 오름 (문제 적은 것 우선)
    5. rule_id 사전순
    """
    status_ord = 0 if info.get("support_status") == "resolved" else 1
    sup = info.get("support", {})
    return (
        status_ord,
        -sup.get("candidate_count", 0),
        -sup.get("pass_count", 0),
        len(info.get("diagnosis", [])),
        rule_id,
    )


def build_candidates(inventory: dict) -> dict:
    """
    inventory에서 legacy rule을 정렬하여 candidates 산출.
    """
    rules = inventory.get("rules", {})

    ranked = []
    for rule_id, info in rules.items():
        ranked.append((rule_id, info))

    ranked.sort(key=lambda x: sort_key(x[0], x[1]))

    candidates = []
    for rank, (rule_id, info) in enumerate(ranked, 1):
        sup = info.get("support", {})
        candidates.append({
            "rank": rank,
            "rule_id": rule_id,
            "support_status": info.get("support_status", "unknown"),
            "pass_count": sup.get("pass_count", 0),
            "candidate_count": sup.get("candidate_count", 0),
            "diagnosis": info.get("diagnosis", []),
            "migration_target": info.get("migration_target", ""),
        })

    return {
        "version": BUILD_VERSION,
        "total": len(candidates),
        "_sort_keys": [
            "support_status (resolved first)",
            "candidate_count desc",
            "pass_count desc",
            "diagnosis length asc",
            "rule_id asc",
        ],
        "candidates": candidates,
    }


def ensure_accept_file() -> dict:
    """
    accept 파일이 없으면 빈 템플릿 생성.
    있으면 기존 내용 로드.
    """
    if ACCEPT_PATH.exists():
        return load_json(ACCEPT_PATH)

    template = {
        "version": BUILD_VERSION,
        "_comment": "이번 라운드에서 승격할 rule_id 목록. candidates에서 선택.",
        "accept": [],
    }
    save_json(ACCEPT_PATH, template)
    return template


def main():
    print("=" * 60)
    print(f"  Build Legacy Upgrade Candidates (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    if not INVENTORY_PATH.exists():
        print(f"\n  ❌ legacy_inventory not found: {INVENTORY_PATH}")
        return 1

    print(f"  Loading: {INVENTORY_PATH.name}")
    inventory = load_json(INVENTORY_PATH)

    print("  Ranking candidates...")
    result = build_candidates(inventory)

    print(f"  ✅ Candidates ranked: {result['total']}")
    for c in result["candidates"]:
        print(f"     #{c['rank']} {c['rule_id']}: "
              f"status={c['support_status']}, "
              f"pass={c['pass_count']}, cand={c['candidate_count']}, "
              f"diag={c['diagnosis']}")

    save_json(CANDIDATES_PATH, result)
    print(f"  ✅ Saved: {CANDIDATES_PATH.relative_to(IRIS_DIR)}")

    # Accept file
    print(f"\n  Checking accept file: {ACCEPT_PATH.name}")
    accept = ensure_accept_file()
    accepted = accept.get("accept", [])
    if accepted:
        print(f"  ✅ Accept list: {len(accepted)} rules")
        for rid in accepted:
            print(f"     - {rid}")
    else:
        print(f"  ℹ️  Accept list is empty (no rules selected for upgrade)")

    # ── Stability check: accepted rules' matched_fulltypes ──
    if accepted:
        print(f"\n  Stability check (accepted rules):")
        rules_in_inv = inventory.get("rules", {})
        for rid in accepted:
            if rid not in rules_in_inv:
                continue
            inv_cand = rules_in_inv[rid].get("support", {}).get("candidate_count", 0)
            # Find in candidates result
            cand_entry = next(
                (c for c in result["candidates"] if c["rule_id"] == rid), None
            )
            cur_cand = cand_entry["candidate_count"] if cand_entry else 0
            if cur_cand != inv_cand:
                print(f"  ⚠️  WARNING: {rid} candidate_count changed "
                      f"({inv_cand}→{cur_cand}). "
                      f"향후 정책 확장 시 FAIL로 전환 가능.")
            else:
                print(f"  ✅ {rid}: candidate_count stable ({cur_cand})")

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
