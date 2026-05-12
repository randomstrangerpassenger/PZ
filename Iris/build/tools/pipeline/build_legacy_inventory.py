"""
build_legacy_inventory.py — Legacy Rule Inventory 자동 산출
============================================================
role_profile_by_rule_id.json + evidence_decisions + evidence_candidates
→ legacy_inventory.v2.4.json

운영 규칙:
  - 추론/판정 없음 — 데이터 진단 리포트만 산출
  - diagnosis는 배열 (복수 사유 동시 허용)
  - support는 계약 정의: pass_count/candidate_count
  - legacy_count가 Q5 frozen_legacy_count와 일치해야 함
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

ROLE_PROFILE_PATH = DATA_DIR / "role_profile_by_rule_id.json"
DECISIONS_PATH = OUTPUT_DIR / f"evidence_decisions.{BUILD_VERSION}.json"
CANDIDATES_PATH = OUTPUT_DIR / f"evidence_candidates.{BUILD_VERSION}.json"
INVENTORY_PATH = OUTPUT_DIR / f"legacy_inventory.{BUILD_VERSION}.json"


def compute_support(
    rule_id: str,
    decisions: dict,
    candidates: dict,
) -> dict:
    """
    support 계산 (계약 정의):
    - pass_count: evidence_decisions에서 해당 rule_id로 PASS된 fulltype 수
    - candidate_count: evidence_candidates에서 해당 rule_id를 포함하는 fulltype 수
    """
    pass_count = sum(
        1
        for ft, dec in decisions.items()
        if rule_id in dec.get("rule_ids", []) and dec["decision"] == "PASS"
    )
    candidate_count = sum(
        1
        for ft, cand in candidates.items()
        if rule_id in cand.get("rule_ids", [])
    )
    return {"pass_count": pass_count, "candidate_count": candidate_count}


def diagnose(profile: dict) -> list[str]:
    """
    legacy rule의 사유를 자동 진단. 복수 사유 허용 (배열).
    """
    reasons = []

    # missing_required_roles: required_roles가 비어있음
    required_roles = profile.get("required_roles", [])
    if not required_roles:
        reasons.append("missing_required_roles")

    # single_anchor_only: migration_target이 multi_anchor인 경우
    # (= 현재 single anchor만 있다는 뜻)
    if profile.get("migration_target") == "multi_anchor":
        reasons.append("single_anchor_only")

    # unknown_role_binding: exempt_reason이 없거나 알 수 없는 값
    exempt_reason = profile.get("exempt_reason", "")
    known_reasons = {"single_anchor_missing_roles"}
    if exempt_reason and exempt_reason not in known_reasons:
        reasons.append("unknown_role_binding")

    if not reasons:
        reasons.append("unknown_role_binding")

    return reasons


def build_inventory(
    role_profiles: dict,
    decisions_data: dict,
    candidates_data: dict,
) -> dict:
    """
    legacy=true인 rule을 수집하여 inventory 산출.
    계약: evidence_decisions/candidates는 flat dict (FullType → entry).
    nested format 금지 — 파이프라인 출력이 항상 flat.
    """
    decisions = decisions_data
    candidates = candidates_data

    legacy_rules = {}
    for rule_id, profile in sorted(role_profiles.items()):
        # 메타 키(_로 시작) 건너뛰기
        if rule_id.startswith("_"):
            continue
        if not profile.get("legacy", False):
            continue

        support = compute_support(rule_id, decisions, candidates)
        diagnosis = diagnose(profile)

        # support가 0이면 집계 소스 경로/키 확인 필요 플래그
        if support["pass_count"] == 0 and support["candidate_count"] == 0:
            support_status = "unresolved"
        else:
            support_status = "resolved"

        legacy_rules[rule_id] = {
            "exempt_reason": profile.get("exempt_reason", ""),
            "migration_target": profile.get("migration_target", ""),
            "required_roles": profile.get("required_roles", []),
            "support": support,
            "support_status": support_status,
            "diagnosis": diagnosis,
        }

    return {
        "version": BUILD_VERSION,
        "legacy_count": len(legacy_rules),
        "_support_definition": {
            "pass_count": "evidence_decisions에서 해당 rule_id로 PASS된 fulltype 수",
            "candidate_count": "evidence_candidates에서 해당 rule_id를 포함하는 fulltype 수",
        },
        "rules": legacy_rules,
    }


def main():
    print("=" * 60)
    print(f"  Build Legacy Inventory (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # Check prerequisites
    for path, label in [
        (ROLE_PROFILE_PATH, "role_profile_by_rule_id"),
        (DECISIONS_PATH, "evidence_decisions"),
        (CANDIDATES_PATH, "evidence_candidates"),
    ]:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return 1

    print(f"  Loading: {ROLE_PROFILE_PATH.name}")
    role_profiles = load_json(ROLE_PROFILE_PATH)

    print(f"  Loading: {DECISIONS_PATH.name}")
    decisions_data = load_json(DECISIONS_PATH)

    print(f"  Loading: {CANDIDATES_PATH.name}")
    candidates_data = load_json(CANDIDATES_PATH)

    print("  Building legacy inventory...")
    inventory = build_inventory(role_profiles, decisions_data, candidates_data)

    legacy_count = inventory["legacy_count"]
    print(f"  ✅ Legacy rules found: {legacy_count}")

    for rule_id, info in inventory["rules"].items():
        sup = info["support"]
        diag = ", ".join(info["diagnosis"])
        status = info["support_status"]
        print(f"     {rule_id}: pass={sup['pass_count']}, "
              f"cand={sup['candidate_count']}, status={status}, diag=[{diag}]")

    # unresolved 경고
    unresolved = sum(
        1 for info in inventory["rules"].values()
        if info["support_status"] == "unresolved"
    )
    if unresolved:
        print(f"  ⚠️  {unresolved}/{legacy_count} rules have support_status=unresolved")
        print(f"     → 집계 소스 경로/키 확인 필요 (L2 우선순위 정렬에 영향)")

    # Save
    save_json(INVENTORY_PATH, inventory)
    print(f"  ✅ Saved: {INVENTORY_PATH.relative_to(IRIS_DIR)}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
