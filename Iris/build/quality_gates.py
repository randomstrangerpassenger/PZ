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
import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

# ── Paths ──
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

IRIS_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json, write_json
from tools.common.versions import (
    BUILD_VERSION,
    QUALITY_GATES_VERSION,
    REQUIRE_FIELDS_VERSION,
    versioned_name,
)

DATA_DIR = SCRIPT_DIR / "data" / BUILD_VERSION
BUILD_DATA_PREFIX = f"build/data/{BUILD_VERSION}"

DECISIONS_PATH = OUTPUT_DIR / f"evidence_decisions.{BUILD_VERSION}.json"
CANDIDATES_PATH = OUTPUT_DIR / f"evidence_candidates.{BUILD_VERSION}.json"
OVERLAY_PATH = OUTPUT_DIR / f"uniqueness_overlay.{BUILD_VERSION}.json"
USECASES_PATH = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"
DESCRIPTIONS_PATH = OUTPUT_DIR / f"descriptions_by_fulltype.{BUILD_VERSION}.json"
ROLE_PROFILE_PATH = DATA_DIR / "role_profile_by_rule_id.json"
EXPECTED_DIFF_PATH = DATA_DIR / "expected_diff.json"
FROZEN_SHA_PATH = DATA_DIR / f"frozen_sha.{BUILD_VERSION}.json"

# ── Output files produced by this script ──
BUILD_REPORT_JSON = OUTPUT_DIR / "build_report.json"
BUILD_REPORT_MD = OUTPUT_DIR / "build_report.md"

# ── Q4 determinism target files (1군) ──
DETERMINISM_FILES = [
    f"evidence_decisions.{BUILD_VERSION}.json",
    f"evidence_candidates.{BUILD_VERSION}.json",
    f"review_queue.{BUILD_VERSION}.json",
    f"uniqueness_overlay.{BUILD_VERSION}.json",
    f"usecases_by_fulltype.{BUILD_VERSION}.json",
    f"recipe_evidence_decisions.{BUILD_VERSION}.json",
    f"recipe_review_queue.{BUILD_VERSION}.json",
    f"descriptions_by_fulltype.{BUILD_VERSION}.json",
    f"requirements_by_fulltype.{BUILD_VERSION}.json",
    f"legacy_inventory.{BUILD_VERSION}.json",
    f"legacy_upgrade_candidates.{BUILD_VERSION}.json",
    versioned_name("recipe_require_fields", REQUIRE_FIELDS_VERSION),
    f"action_requirement_index.{BUILD_VERSION}.json",
    f"action_evidence_classification.{BUILD_VERSION}.json",
    f"recipe_nav_registry.{BUILD_VERSION}.json",
    f"recipe_requirements_index.{BUILD_VERSION}.json",
]

# ── Q4 determinism target files (2군: build/ 정책 파일) ──
DETERMINISM_BUILD_FILES = [
    f"use_case_id_alias_map.{BUILD_VERSION}.json",
]

VALID_DECISIONS = {"PASS", "NO", "REVIEW"}

# ── Q3 exempt 허용 enum ──
ALLOWED_EXEMPT_REASONS = {"single_anchor_missing_roles"}
ALLOWED_MIGRATION_TARGETS = {"multi_anchor"}


# ══════════════════════════════════════════════════════════════════════════
#  GATE Q1: PASS 무결성
# ══════════════════════════════════════════════════════════════════════════

def gate_q1(decisions: dict, usecases: dict = None, registry: dict = None) -> dict:
    """PASS인 FullType의 prove 중 하나라도 unknown이면 FAIL.
       추가로 usecases 데이터의 line_kind 검증 (Prefix 규칙 부합 및 생략 여부)."""
    violations = []
    checked = 0

    for ft, dec in decisions.items():
        if dec["decision"] != "PASS":
            continue
        checked += 1
        proof = dec.get("proof", {})
        for key in ["A_static_source", "B_external_target", "C_persistent_change"]:
            if proof.get(key) == "unknown":
                violations.append(f"{ft}: {key}=unknown")

    # line_kind 검증
    if usecases:
        for ft, entry in usecases.get("fulltypes", {}).items():
            for uc in entry.get("use_cases", []):
                line_kind = uc.get("line_kind")
                if line_kind not in {"evidence", "exclusion"}:
                    violations.append(f"{ft}: invalid line_kind='{line_kind}' for {uc['use_case_id']}")
                # Step 2(현재는 unknown_prefix 배제하므로 여기 도달하는 uc들은 모두 evidence/exclusion임이 보장됨.
                # 그러나 만약 uc.exclusion.* 인데 evidence로 배정됐다면 FAIL.
                ucid = uc.get("use_case_id", "")
                if ucid.startswith("uc.exclusion.") and line_kind != "exclusion":
                    violations.append(f"{ft}: {ucid} must be line_kind='exclusion'")

                # evidence_strength 검증 (uc.action.* 라인 전용)
                ev_strength = uc.get("evidence_strength")
                if ev_strength is not None:
                    if ev_strength not in {"strong", "weak", "exclude"}:
                        violations.append(
                            f"{ft}: {ucid} invalid evidence_strength='{ev_strength}'"
                        )
                    if ev_strength == "exclude" and not uc.get("reason_code"):
                        violations.append(
                            f"{ft}: {ucid} evidence_strength=exclude but missing reason_code"
                        )

    # Alias 검증 (Q1 구조 보장)
    if registry:
        rules = registry.get("rules", {})
        for rid, props in rules.items():
            alias_of = props.get("alias_of")
            if alias_of:
                # 1. Missing target 방지 (alias_of를 use_case_id로 가지는 노드가 존재해야 함)
                target_exists = any(r.get("use_case_id") == alias_of for r in rules.values())
                if not target_exists:
                    violations.append(f"Registry Rule '{rid}': alias_of target '{alias_of}' is explicitly missing from registry")
                
                # 2. 순환 참조 검증
                visited = set()
                curr_alias = alias_of
                while curr_alias:
                    if curr_alias in visited:
                        violations.append(f"Registry Rule '{rid}': circular alias detected -> {curr_alias}")
                        break
                    visited.add(curr_alias)
                    target_rule = next((r for r in rules.values() if r.get("use_case_id") == curr_alias), None)
                    curr_alias = target_rule.get("alias_of") if target_rule else None

                # 3. 체인 금지: alias_of target 노드는 자체 alias_of를 가지면 안 됨
                # (virtual.rule 포함 target 규칙 전체 참조)
                visited = set()
                curr_alias = alias_of
                while curr_alias:
                    if curr_alias in visited:
                        break # circular alias logic handles this
                    visited.add(curr_alias)
                    target_rule = next((r for r in rules.values() if r.get("use_case_id") == curr_alias), None)
                    if target_rule and target_rule.get("alias_of"):
                        violations.append(
                            f"Registry Rule '{rid}': alias chain detected — "
                            f"target '{curr_alias}' itself has alias_of='{target_rule['alias_of']}'"
                        )
                        break
                    curr_alias = None

            # 4. Registry Oeverride 검증 (A안 규칙)
            decision = props.get("decision")
            strength = props.get("strength")
            reason_code = props.get("override_reason_code")
            
            if decision or strength:
                ucid = props.get("use_case_id", "")
                if props.get("alias_of"):
                    ucid = props["alias_of"] # Target ID 기준

                if not ucid.startswith("uc.action."):
                    violations.append(f"Registry Rule '{rid}': override is only allowed for 'uc.action.*' (found '{ucid}')")
                
                if decision not in {"PASS", "REVIEW"}:
                    violations.append(f"Registry Rule '{rid}': invalid decision override '{decision}'")
                
                if strength not in {"STRONG", "WEAK", "EXCLUDE"}:
                    violations.append(f"Registry Rule '{rid}': invalid strength override '{strength}' (must be uppercase STRONG/WEAK/EXCLUDE)")
                
                if not reason_code:
                    violations.append(f"Registry Rule '{rid}': override requires 'override_reason_code'")

    # Old capability ID 잔존 검증 (리네이밍 대상 old ID가 출력에 남아있으면 FAIL)
    alias_map_path = DATA_DIR / f"use_case_id_alias_map.{BUILD_VERSION}.json"
    if usecases and alias_map_path.exists():
        alias_map = load_json(alias_map_path)
        old_ids = set(alias_map.get("map", {}).keys())
        for ft, entry in usecases.get("fulltypes", {}).items():
            for uc in entry.get("use_cases", []):
                ucid = uc.get("use_case_id", "")
                if ucid in old_ids:
                    violations.append(
                        f"{ft}: old capability ID '{ucid}' still present in output "
                        f"(should be '{alias_map['map'][ucid]}')"
                    )

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "checked": checked,
        "violations": len(violations),
        "details": violations[:10] if violations else [],
    }


# ══════════════════════════════════════════════════════════════════════════
#  GATE Q2: Strong 무결성
# ══════════════════════════════════════════════════════════════════════════

def gate_q2(overlay: dict) -> dict:
    """Strong/Weak 분류와 matched_fulltypes 카운트 정합성 검증."""
    violations = []
    checked = 0
    by_rule = overlay.get("by_rule_id", {})

    for rid, entry in by_rule.items():
        uniqueness = entry.get("uniqueness")
        if uniqueness is None:
            continue  # NO-only rule, skip
        checked += 1
        pass_count = entry.get("pass_count", 0)

        if uniqueness == "STRONG" and pass_count != 1:
            violations.append(
                f"{rid}: STRONG but pass_count={pass_count} (expected 1)"
            )
        elif uniqueness == "WEAK" and pass_count == 1:
            violations.append(
                f"{rid}: WEAK but pass_count=1 (should be STRONG)"
            )

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "checked": checked,
        "violations": len(violations),
        "details": violations[:10] if violations else [],
    }


# ══════════════════════════════════════════════════════════════════════════
#  GATE Q3: Anchor role 완전성
# ══════════════════════════════════════════════════════════════════════════

def gate_q3(decisions: dict, candidates: dict, role_profiles: dict) -> dict:
    """
    PASS인 각 FullType의 rule_ids가 role profile을 충족하는지 검증.

    FAIL 조건:
    1. profile 미등록 rule_id가 PASS에 등장
    2. legacy=true인데 q3_exempt 필드 없음 (불완전 프로파일)
    3. q3_exempt=true인데 exempt_reason ∉ 허용 enum
    4. q3_exempt=true인데 legacy≠true (면제 남발 차단)
    5. required_roles 미충족 (non-exempt rules only)

    Evidence directionality: roles come from anchors only, never from prove.
    """
    violations = []
    checked = 0

    # ── Profile-level validation (한 번만 수행) ──
    for rid, profile in role_profiles.items():
        is_legacy = profile.get("legacy", False)
        q3_exempt = profile.get("q3_exempt")
        exempt_reason = profile.get("exempt_reason")

        # FAIL #2: legacy=true but q3_exempt missing
        if is_legacy and q3_exempt is None:
            violations.append(
                f"profile '{rid}': legacy=true but q3_exempt field missing"
            )

        # FAIL #4: q3_exempt=true but legacy!=true
        if q3_exempt is True and not is_legacy:
            violations.append(
                f"profile '{rid}': q3_exempt=true but legacy!=true"
            )

        # FAIL #3: q3_exempt=true but exempt_reason not in allowed enum
        if q3_exempt is True and exempt_reason not in ALLOWED_EXEMPT_REASONS:
            violations.append(
                f"profile '{rid}': exempt_reason='{exempt_reason}' "
                f"not in {sorted(ALLOWED_EXEMPT_REASONS)}"
            )

    # ── Per-item role validation ──
    for ft, dec in decisions.items():
        if dec["decision"] != "PASS":
            continue
        checked += 1

        rule_ids = dec.get("rule_ids", [])

        # ── Collect actual anchor roles (only from real anchor objects) ──
        actual_roles = set()
        cand = candidates.get(ft, {})
        for anchor in cand.get("anchors", []):
            role = anchor.get("role")
            if role:
                actual_roles.add(role)
        for anchor in dec.get("anchors", []):
            role = anchor.get("role")
            if role:
                actual_roles.add(role)

        for rid in rule_ids:
            # FAIL #1: unregistered rule
            if rid not in role_profiles:
                violations.append(
                    f"{ft}: rule_id '{rid}' not registered in "
                    f"role_profile_by_rule_id.json"
                )
                continue

            profile = role_profiles[rid]

            # Skip role check for exempt profiles
            if profile.get("q3_exempt") is True:
                continue

            required = set(profile.get("required_roles", []))
            missing = required - actual_roles

            if missing:
                violations.append(
                    f"{ft}: rule={rid} missing roles {sorted(missing)}"
                )

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "checked": checked,
        "violations": len(violations),
        "details": violations[:10] if violations else [],
    }


# ══════════════════════════════════════════════════════════════════════════
#  GATE Q4: 결정성 (Determinism)
# ══════════════════════════════════════════════════════════════════════════

def canonical_sha256(data) -> str:
    """Canonical JSON SHA256 (sort_keys, compact separators, utf-8)."""
    canonical = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def gate_q4(frozen_sha: dict) -> dict:
    """현재 산출물 SHA vs frozen_sha 스냅샷 비교."""
    frozen_files = frozen_sha.get("files", {})
    if not frozen_files:
        return {
            "status": "FAIL",
            "files_checked": 0,
            "mismatches": 1,
            "details": ["frozen_sha has no 'files' entries"],
        }

    mismatches = []
    checked = 0

    for fname in DETERMINISM_FILES:
        path = OUTPUT_DIR / fname
        if not path.exists():
            mismatches.append(f"{fname}: FILE_MISSING")
            continue

        data = load_json(path)
        actual = canonical_sha256(data)
        expected = frozen_files.get(fname)
        checked += 1

        if expected is None:
            mismatches.append(f"{fname}: not in frozen_sha")
        elif actual != expected:
            mismatches.append(
                f"{fname}: expected={expected[:16]}... actual={actual[:16]}..."
            )

    # 2군: build/ 정책 파일
    for fname in DETERMINISM_BUILD_FILES:
        path = DATA_DIR / fname
        if not path.exists():
            mismatches.append(f"{BUILD_DATA_PREFIX}/{fname}: FILE_MISSING")
            continue

        data = load_json(path)
        actual = canonical_sha256(data)
        expected = frozen_files.get(f"{BUILD_DATA_PREFIX}/{fname}")
        checked += 1

        if expected is None:
            mismatches.append(f"{BUILD_DATA_PREFIX}/{fname}: not in frozen_sha")
        elif actual != expected:
            mismatches.append(
                f"{BUILD_DATA_PREFIX}/{fname}: expected={expected[:16]}... actual={actual[:16]}..."
            )

    status = "FAIL" if mismatches else "PASS"
    return {
        "status": status,
        "files_checked": checked,
        "mismatches": len(mismatches),
        "details": mismatches if mismatches else [],
    }


def update_frozen_sha() -> dict:
    """현재 산출물로 frozen_sha 파일 갱신. 갱신된 데이터 반환."""
    files = {}
    for fname in DETERMINISM_FILES:
        path = OUTPUT_DIR / fname
        if path.exists():
            data = load_json(path)
            files[fname] = canonical_sha256(data)
        else:
            files[fname] = "FILE_MISSING"

    # 2군: build/ 정책 파일
    for fname in DETERMINISM_BUILD_FILES:
        path = DATA_DIR / fname
        if path.exists():
            data = load_json(path)
            files[f"{BUILD_DATA_PREFIX}/{fname}"] = canonical_sha256(data)
        else:
            files[f"{BUILD_DATA_PREFIX}/{fname}"] = "FILE_MISSING"

    frozen = {
        "_comment": "Q4 전용. canonical JSON SHA256. --update-sha로만 갱신. "
                   "Q1~Q3+Q5 PASS 후에만 갱신 허용.",
        "_canonical_spec": {
            "encoding": "utf-8",
            "newline": "LF",
            "sort_keys": True,
            "separators": [",", ":"],
            "ensure_ascii": False,
        },
        "_version_rule": (
            f"frozen_sha.<build_version>.json — "
            f"tools.common.versions.BUILD_VERSION 상수로 정확히 1개만 선택"
        ),
        "files": files,
    }

    write_json(FROZEN_SHA_PATH, frozen, indent=4, trailing_newline=False)

    return frozen


# ══════════════════════════════════════════════════════════════════════════
#  GATE Q5: 회귀 diff 통제
# ══════════════════════════════════════════════════════════════════════════

def q5_validate_allowed_changes(expected_diff: dict, allowed: list[dict]) -> list[str]:
    """Validate the allowed_changes control surface."""
    violations = []
    seen_fulltypes = set()
    all_frozen = (
        set(expected_diff.get("frozen_pass", []))
        | set(expected_diff.get("frozen_review", []))
    )

    for ac in allowed:
        ft = ac.get("fulltype", "")
        frm = ac.get("from", "")
        to = ac.get("to", "")

        # Uniqueness check
        if ft in seen_fulltypes:
            violations.append(f"allowed_changes: duplicate fulltype '{ft}'")
        seen_fulltypes.add(ft)

        # Value range check
        if frm not in VALID_DECISIONS:
            violations.append(
                f"allowed_changes: '{ft}' has invalid from='{frm}'"
            )
        if to not in VALID_DECISIONS:
            violations.append(
                f"allowed_changes: '{ft}' has invalid to='{to}'"
            )

        # Baseline existence check
        if ft not in all_frozen:
            # Also check if it might be a NO item (not individually listed)
            # For NO items, we only have count/hash, so we can't verify by name
            # Just ensure it's not listed in PASS/REVIEW frozen sets
            pass  # NO items are acceptable in allowed_changes

    return violations


def q5_report_allowed_changes(
    all_changes: list[dict],
    allowed: list[dict],
) -> tuple[list[str], list[str]]:
    """Compare collected Q5 changes against allowed_changes."""
    allowed_map = {}
    for ac in allowed:
        allowed_map[ac["fulltype"]] = ac

    unexpected = []
    for chg in all_changes:
        ft = chg["fulltype"]
        if ft.startswith("_"):
            # System-level changes (NO count/hash, usecase count/hash) — always unexpected
            unexpected.append(f"{ft}: {chg['change']}")
        elif ft in allowed_map:
            # This change was explicitly allowed
            pass
        else:
            unexpected.append(f"{ft}: {chg['change']} (not in allowed_changes)")

    warnings = []
    for ft, ac in allowed_map.items():
        was_changed = any(c["fulltype"] == ft for c in all_changes)
        if not was_changed:
            warnings.append(
                f"allowed_changes: '{ft}' {ac['from']}→{ac['to']} not yet applied"
            )

    return unexpected, warnings


def q5_collect_decision_status_changes(
    decisions: dict,
    expected_diff: dict,
) -> list[dict]:
    """Collect PASS/REVIEW set changes and NO aggregate changes."""
    changes = []

    # Compare PASS sets
    frozen_pass = set(expected_diff.get("frozen_pass", []))
    current_pass = set(
        ft for ft, d in decisions.items() if d["decision"] == "PASS"
    )

    for ft in current_pass - frozen_pass:
        changes.append({"fulltype": ft, "change": "→PASS"})
    for ft in frozen_pass - current_pass:
        changes.append({"fulltype": ft, "change": "PASS→"})

    # Compare REVIEW sets
    frozen_review = set(expected_diff.get("frozen_review", []))
    current_review = set(
        ft for ft, d in decisions.items() if d["decision"] == "REVIEW"
    )

    for ft in current_review - frozen_review:
        changes.append({"fulltype": ft, "change": "→REVIEW"})
    for ft in frozen_review - current_review:
        changes.append({"fulltype": ft, "change": "REVIEW→"})

    # Compare NO count + hash
    frozen_no_count = expected_diff.get("frozen_no_count", 0)
    frozen_no_hash = expected_diff.get("frozen_no_hash", "")

    current_no = sorted(
        ft for ft, d in decisions.items() if d["decision"] == "NO"
    )
    current_no_count = len(current_no)
    current_no_hash = hashlib.sha256(
        json.dumps(current_no).encode("utf-8")
    ).hexdigest()

    if current_no_count != frozen_no_count:
        changes.append({
            "fulltype": "_NO_COUNT",
            "change": f"count {frozen_no_count}→{current_no_count}"
        })
    if frozen_no_hash and current_no_hash != frozen_no_hash:
        changes.append({
            "fulltype": "_NO_HASH",
            "change": "NO set content changed"
        })

    return changes


def q5_collect_usecase_aggregate_changes(
    usecases_data: dict | None,
    expected_diff: dict,
) -> list[dict]:
    """Collect usecase aggregate count/hash changes."""
    if not usecases_data:
        return []

    frozen_uc_count = expected_diff.get("frozen_usecase_count", 0)
    frozen_uc_hash = expected_diff.get("frozen_usecase_hash", "")
    uc_fulltypes = usecases_data.get("fulltypes", {})

    # Build a sorted list of (fulltype, [use_case_ids]) for hashing total
    uc_entries = sorted(
        (ft, sorted(uc["use_case_id"] for uc in info["use_cases"]))
        for ft, info in uc_fulltypes.items()
    )
    current_uc_count = len(uc_entries)
    current_uc_hash = hashlib.sha256(
        json.dumps(uc_entries).encode("utf-8")
    ).hexdigest()

    changes = []
    if current_uc_count != frozen_uc_count:
        changes.append({
            "fulltype": "_USECASE_COUNT",
            "change": f"count {frozen_uc_count}→{current_uc_count}"
        })
    if frozen_uc_hash and current_uc_hash != frozen_uc_hash:
        changes.append({
            "fulltype": "_USECASE_HASH",
            "change": "usecase set content changed"
        })
    return changes


def q5_collect_description_aggregate_changes(expected_diff: dict) -> list[dict]:
    """Collect description block count/hash changes."""
    if not DESCRIPTIONS_PATH.exists():
        return []

    frozen_desc_count = expected_diff.get("frozen_description_count", 0)
    frozen_desc_hash = expected_diff.get("frozen_description_hash", "")

    desc_data = load_json(DESCRIPTIONS_PATH)
    desc_fulltypes = desc_data.get("fulltypes", {})
    # Build a sorted list of (fulltype, items+debug_items) for hashing
    # use_case_block이 없을 수 있으므로 .get으로 안전 처리
    desc_entries = sorted(
        (ft, info.get("use_case_block", {}).get("items", [])
         + info.get("use_case_block", {}).get("debug_items", []))
        for ft, info in desc_fulltypes.items()
    )
    current_desc_count = len(desc_entries)
    current_desc_hash = hashlib.sha256(
        json.dumps(desc_entries).encode("utf-8")
    ).hexdigest()

    changes = []
    if current_desc_count != frozen_desc_count:
        changes.append({
            "fulltype": "_DESCRIPTION_COUNT",
            "change": f"count {frozen_desc_count}→{current_desc_count}"
        })
    if frozen_desc_hash and current_desc_hash != frozen_desc_hash:
        changes.append({
            "fulltype": "_DESCRIPTION_HASH",
            "change": "description set content changed"
        })
    return changes


def q5_collect_requirements_aggregate_changes(
    expected_diff: dict,
) -> tuple[list[dict], dict | None]:
    """Collect keep-requirements count/hash changes and return requirement data."""
    req_path = OUTPUT_DIR / f"requirements_by_fulltype.{BUILD_VERSION}.json"
    if not req_path.exists():
        return [], None

    frozen_req_count = expected_diff.get("frozen_requirements_count", 0)
    frozen_req_hash = expected_diff.get("frozen_requirements_hash", "")

    req_data = load_json(req_path)
    req_fulltypes = req_data.get("fulltypes", {})
    req_entries = sorted(
        (ft, info.get("requirements", []))
        for ft, info in req_fulltypes.items()
        if info.get("requirements")
    )
    current_req_count = len(req_entries)
    current_req_hash = hashlib.sha256(
        json.dumps(req_entries).encode("utf-8")
    ).hexdigest()

    changes = []
    if current_req_count != frozen_req_count:
        changes.append({
            "fulltype": "_REQUIREMENTS_COUNT",
            "change": f"count {frozen_req_count}→{current_req_count}"
        })
    if frozen_req_hash and current_req_hash != frozen_req_hash:
        changes.append({
            "fulltype": "_REQUIREMENTS_HASH",
            "change": "requirements set content changed"
        })
    return changes, req_fulltypes


def q5_collect_legacy_count_changes(expected_diff: dict) -> list[dict]:
    """Collect legacy inventory count changes according to its policy."""
    legacy_baseline = expected_diff.get("legacy_count_baseline", 0)
    legacy_policy = expected_diff.get("legacy_count_policy", "freeze")
    legacy_inv_path = OUTPUT_DIR / f"legacy_inventory.{BUILD_VERSION}.json"
    if not legacy_inv_path.exists():
        return []

    legacy_data = load_json(legacy_inv_path)
    current_legacy_count = legacy_data.get("legacy_count", 0)
    if legacy_policy == "decrease_only":
        legacy_count_changed = current_legacy_count > legacy_baseline
    else:
        legacy_count_changed = current_legacy_count != legacy_baseline

    if not legacy_count_changed:
        return []

    return [{
        "fulltype": "_LEGACY_COUNT",
        "change": f"count {legacy_baseline}→{current_legacy_count}"
    }]


def q5_collect_require_channel_changes(
    req_fulltypes: dict | None,
    expected_diff: dict,
) -> list[dict]:
    """Collect v2.5 require channel count/hash changes."""
    if req_fulltypes is None:
        return []

    frozen_require_ft_count = expected_diff.get("frozen_require_fulltype_count", 0)
    frozen_require_hash = expected_diff.get("frozen_require_hash", "")
    frozen_require_policy = expected_diff.get("frozen_require_policy", "decrease_only")

    require_entries = sorted(
        (ft, info.get("require", []))
        for ft, info in req_fulltypes.items()
        if info.get("require")
    )
    current_require_ft_count = len(require_entries)
    current_require_hash = hashlib.sha256(
        json.dumps(require_entries).encode("utf-8")
    ).hexdigest()

    if frozen_require_policy == "decrease_only":
        # decrease_only 래칫: 증가만 FAIL, 감소는 허용
        require_count_changed = current_require_ft_count > frozen_require_ft_count
    else:
        require_count_changed = current_require_ft_count != frozen_require_ft_count
    require_hash_changed = (
        frozen_require_hash and current_require_hash != frozen_require_hash
    )

    changes = []
    if require_count_changed:
        changes.append({
            "fulltype": "_REQUIRE_FT_COUNT",
            "change": f"count {frozen_require_ft_count}→{current_require_ft_count}"
        })
    if require_hash_changed:
        changes.append({
            "fulltype": "_REQUIRE_HASH",
            "change": "require set content changed"
        })
    return changes


def q5_compare_metric_changes(
    new_metrics: dict,
    expected_diff: dict,
) -> tuple[list[dict], list[str]]:
    """Compare collected Q5 metrics against frozen policies."""
    changes = []
    violations = []

    for k, current_val in new_metrics.items():
        # override metrics do not have 'frozen_' prefix in expected_diff.json
        if k.startswith("override_"):
            frozen_val = expected_diff.get(k, 0)
        else:
            frozen_val = expected_diff.get(f"frozen_{k}", 0)

        if k == "rightclick_evidence_fulltype_count" and current_val < frozen_val:
            # decrease_only policy
            pass
        elif k == "rightclick_evidence_fulltype_count" and current_val > frozen_val:
            violations.append(
                f"Metric '{k}' increased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Policy for unknown_prefix_line_count (decrease_only)
        if k == "unknown_prefix_line_count" and current_val < frozen_val:
            pass  # Acceptable
        elif k == "unknown_prefix_line_count" and current_val > frozen_val:
            violations.append(
                f"Metric '{k}' increased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Policy for rightclick_strong_fulltype_count (decrease_only)
        if k == "rightclick_strong_fulltype_count" and current_val < frozen_val:
            violations.append(
                f"Metric '{k}' decreased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Policy for rightclick_strong_line_count (decrease_only)
        if k == "rightclick_strong_line_count" and current_val < frozen_val:
            violations.append(
                f"Metric '{k}' decreased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Other metrics allow arbitrary changes without strict FAIL logic for now,
        # but they must be registered in all_changes if they differ.
        if current_val != frozen_val:
            changes.append({
                "fulltype": f"_{k.upper()}",
                "change": f"count {frozen_val}→{current_val}"
            })

    return changes, violations


def q5_collect_usecase_line_metrics(uc_fulltypes: dict) -> dict:
    """Collect right-click/recipe line-kind usecase metrics."""
    rc_ev_ft = 0
    rc_ev_lines = 0
    rc_ex_ft = 0
    rc_ex_lines = 0
    rec_ev_ft = 0

    for ft, info in uc_fulltypes.items():
        ft_has_rc_ev = False
        ft_has_rc_ex = False
        ft_has_rec_ev = False

        for uc in info.get("use_cases", []):
            is_recipe = any(
                s["source_type"] == "recipe_evidence"
                for s in uc.get("evidence_sources", [])
            )
            is_rc = any(
                s["source_type"] == "rightclick"
                for s in uc.get("evidence_sources", [])
            )
            kind = uc.get("line_kind")

            if is_recipe:
                ft_has_rec_ev = True
            if is_rc:
                if kind == "evidence":
                    ft_has_rc_ev = True
                    rc_ev_lines += 1
                elif kind == "exclusion":
                    ft_has_rc_ex = True
                    rc_ex_lines += 1

        if ft_has_rc_ev:
            rc_ev_ft += 1
        if ft_has_rc_ex:
            rc_ex_ft += 1
        if ft_has_rec_ev:
            rec_ev_ft += 1

    return {
        "rightclick_evidence_fulltype_count": rc_ev_ft,
        "rightclick_evidence_line_count": rc_ev_lines,
        "rightclick_exclusion_fulltype_count": rc_ex_ft,
        "rightclick_exclusion_line_count": rc_ex_lines,
        "recipe_evidence_fulltype_count": rec_ev_ft,
    }


def q5_collect_evidence_strength_metrics(uc_fulltypes: dict) -> dict:
    """Collect right-click evidence strength metrics."""
    rc_strong_ft = 0
    rc_strong_lines = 0
    rc_weak_ft = 0
    rc_exclude_lines = 0

    for ft, info in uc_fulltypes.items():
        ft_has_strong = False
        ft_has_weak = False
        for uc in info.get("use_cases", []):
            ev_str = uc.get("evidence_strength")
            if ev_str in ("strong", "STRONG"):
                rc_strong_lines += 1
                ft_has_strong = True
            elif ev_str in ("weak", "WEAK"):
                ft_has_weak = True
            elif ev_str in ("exclude", "EXCLUDE"):
                rc_exclude_lines += 1
        if ft_has_strong:
            rc_strong_ft += 1
        if ft_has_weak:
            rc_weak_ft += 1

    return {
        "rightclick_strong_fulltype_count": rc_strong_ft,
        "rightclick_strong_line_count": rc_strong_lines,
        "rightclick_weak_fulltype_count": rc_weak_ft,
        "rightclick_exclude_line_count": rc_exclude_lines,
    }


def q5_collect_recipe_role_metrics(
    uc_fulltypes: dict,
    expected_diff: dict,
) -> tuple[dict, list[str]]:
    """Validate recipe source roles and collect keep-link metric."""
    valid_recipe_roles = {"consume", "keep"}
    recipe_keep_link_count = 0
    violations = []

    for ft, info in uc_fulltypes.items():
        for uc in info.get("use_cases", []):
            for src in uc.get("evidence_sources", []):
                st = src.get("source_type")
                role = src.get("role")
                if st == "recipe_evidence":
                    # 필수: role이 없으면 FAIL
                    if role is None:
                        violations.append(
                            f"{ft}: recipe_evidence source missing role field "
                            f"(rule_id={src.get('rule_id')})"
                        )
                    elif role not in valid_recipe_roles:
                        violations.append(
                            f"{ft}: invalid role '{role}' "
                            f"(must be {sorted(valid_recipe_roles)})"
                        )
                    if role == "keep":
                        recipe_keep_link_count += 1
                else:
                    # 비-recipe source에 role이 있으면 FAIL (스키마 오염 차단)
                    if role is not None:
                        violations.append(
                            f"{ft}: source_type='{st}' has unexpected role field"
                        )

    frozen_keep_links = expected_diff.get("frozen_recipe_keep_link_count", 0)
    if recipe_keep_link_count < frozen_keep_links:
        violations.append(
            f"recipe_keep_link_count decreased "
            f"{frozen_keep_links}→{recipe_keep_link_count} (decrease_only)"
        )

    return {"recipe_keep_link_count": recipe_keep_link_count}, violations


def q5_validate_keep_unresolved_count() -> list[str]:
    """Validate recipe keep_unresolved_count FAIL-LOUD condition."""
    rec_dec_path = OUTPUT_DIR / f"recipe_evidence_decisions.{BUILD_VERSION}.json"
    if not rec_dec_path.exists():
        return [
            "recipe_evidence_decisions MISSING — cannot verify keep_unresolved_count"
        ]

    rec_stats = load_json(rec_dec_path).get("stats", {})
    keep_unresolved = rec_stats.get("keep_unresolved_count", 0)
    if keep_unresolved > 0:
        return [f"keep_unresolved_count={keep_unresolved} (must be 0)"]
    return []


def q5_collect_registry_override_metrics() -> dict:
    """Collect action override metrics from the use-case registry."""
    override_action_count = 0
    override_strong_count = 0

    registry_path = DATA_DIR / f"use_case_registry.{BUILD_VERSION}.json"
    if registry_path.exists():
        registry_data = load_json(registry_path)
        for props in registry_data.get("rules", {}).values():
            ucid = props.get("use_case_id", "")
            if props.get("alias_of"):
                ucid = props["alias_of"]
            if ucid.startswith("uc.action.") and props.get("decision") == "PASS":
                override_action_count += 1
                if props.get("strength") == "STRONG":
                    override_strong_count += 1

    return {
        "override_action_count": override_action_count,
        "override_strong_count": override_strong_count,
    }


def q5_collect_diagnostic_metrics() -> dict:
    """Collect diagnostic metrics used by Q5."""
    diagnostics_path = OUTPUT_DIR / f"diagnostics.{BUILD_VERSION}.json"
    if diagnostics_path.exists():
        diag_data = load_json(diagnostics_path)
        unknown_prefix_count = len(diag_data.get("unknown_prefix", []))
    else:
        unknown_prefix_count = 0
    return {"unknown_prefix_line_count": unknown_prefix_count}


def q5_collect_recipe_nav_metrics(expected_diff: dict) -> tuple[dict, list[str]]:
    """Validate recipe nav registry stats and collect nav metrics."""
    nav_registry_path = OUTPUT_DIR / f"recipe_nav_registry.{BUILD_VERSION}.json"
    frozen_nav = expected_diff.get("frozen_nav_eligible_count", 0)
    violations = []
    metrics = {}

    if not nav_registry_path.exists():
        if frozen_nav > 0:
            violations.append(
                f"recipe_nav: registry MISSING but frozen_nav_eligible_count={frozen_nav}"
            )
        return metrics, violations

    nav_data = load_json(nav_registry_path)
    nav_stats = nav_data.get("stats", {})

    # FAIL-LOUD: required stats keys
    for req_key in [
        "uid_collision_count",
        "nav_missing_index_count",
        "nav_eligible_count",
        "nav_ineligible_count",
    ]:
        if req_key not in nav_stats:
            violations.append(
                f"recipe_nav: required stats key '{req_key}' missing"
            )

    # FAIL-LOUD: uid_collision must be 0
    uid_collision = nav_stats.get("uid_collision_count", -1)
    if uid_collision != 0:
        violations.append(
            f"recipe_nav: uid_collision_count={uid_collision} (must be 0)"
        )

    # FAIL-LOUD: nav_missing_index must be 0
    nav_missing = nav_stats.get("nav_missing_index_count", -1)
    if nav_missing != 0:
        violations.append(
            f"recipe_nav: nav_missing_index_count={nav_missing} (must be 0)"
        )

    # Ratchet: nav_eligible_count (decrease_only)
    current_nav = nav_stats.get("nav_eligible_count", 0)
    if current_nav < frozen_nav:
        violations.append(
            f"recipe_nav: nav_eligible_count decreased "
            f"{frozen_nav}→{current_nav} (decrease_only)"
        )
    metrics["nav_eligible_count"] = current_nav
    return metrics, violations


def q5_collect_recipe_requirement_index_metrics(
    expected_diff: dict,
) -> tuple[dict, list[str]]:
    """Validate recipe requirements index stats and collect requirement metrics."""
    req_index_path = OUTPUT_DIR / f"recipe_requirements_index.{BUILD_VERSION}.json"
    frozen_req_with = expected_diff.get("frozen_req_with_requirements_count", 0)
    frozen_req_atoms = expected_diff.get("frozen_req_atoms_total", 0)
    metrics = {}
    violations = []

    if not req_index_path.exists():
        if frozen_req_with > 0:
            violations.append(
                "recipe_req: index MISSING but "
                f"frozen_req_with_requirements_count={frozen_req_with}"
            )
        return metrics, violations

    req_data = load_json(req_index_path)
    req_stats = req_data.get("stats", {})

    # FAIL-LOUD: upper bound 0
    for zero_key in [
        "req_missing_index_count",
        "req_uid_collision_count",
        "req_dangling_count",
    ]:
        val = req_stats.get(zero_key, -1)
        if val != 0:
            violations.append(f"recipe_req: {zero_key}={val} (must be 0)")

    # Upper bound: dangling_non_suffixed <= 1
    dns = req_stats.get("req_dangling_non_suffixed_count", -1)
    frozen_dns = expected_diff.get("frozen_req_dangling_non_suffixed_count", 1)
    if dns > frozen_dns:
        violations.append(
            f"recipe_req: req_dangling_non_suffixed_count={dns} "
            f"exceeds frozen {frozen_dns}"
        )

    # decrease_only: with_requirements
    cur_with = req_stats.get("with_requirements", 0)
    if cur_with < frozen_req_with:
        violations.append(
            f"recipe_req: with_requirements decreased "
            f"{frozen_req_with}→{cur_with} (decrease_only)"
        )
    metrics["req_with_requirements_count"] = cur_with

    # decrease_only: atoms_total
    cur_atoms = req_stats.get("atoms_total", 0)
    if cur_atoms < frozen_req_atoms:
        violations.append(
            f"recipe_req: atoms_total decreased "
            f"{frozen_req_atoms}→{cur_atoms} (decrease_only)"
        )
    metrics["req_atoms_total"] = cur_atoms

    # decrease_only: atoms_with_check (C1 — FAIL-LOUD 후조건)
    frozen_req_with_check = expected_diff.get("frozen_req_atoms_with_check", 0)
    cur_with_check = req_stats.get("atoms_with_check", 0)
    if cur_with_check < frozen_req_with_check:
        violations.append(
            f"recipe_req: atoms_with_check decreased "
            f"{frozen_req_with_check}→{cur_with_check} (decrease_only)"
        )
    metrics["req_atoms_with_check"] = cur_with_check

    # upper bound 0: atoms_without_check must be 0 (C1)
    cur_no_check = req_stats.get("atoms_without_check", 0)
    if cur_no_check > 0:
        violations.append(
            f"recipe_req: atoms_without_check={cur_no_check} (must be 0)"
        )

    # Tracking: base_slug_fallback
    metrics["req_base_slug_fallback_count"] = req_stats.get(
        "req_base_slug_fallback_count", 0
    )
    return metrics, violations


def gate_q5(decisions: dict, expected_diff: dict) -> dict:
    """expected_diff.json 기준으로 허용되지 않은 변경 탐지."""
    violations = []

    # ── Step 0: allowed_changes 자체 검증 ──
    allowed = expected_diff.get("allowed_changes", [])
    violations.extend(q5_validate_allowed_changes(expected_diff, allowed))

    if violations:
        return {
            "status": "FAIL",
            "unexpected_changes": len(violations),
            "pending_allowed": 0,
            "details": violations[:10],
            "warnings": [],
        }

    # ── Step 1~3: Compare PASS/REVIEW/NO decision status changes ──
    decision_status_changes = q5_collect_decision_status_changes(
        decisions, expected_diff
    )

    # ── Step 3b: Compare usecases count/hash and derived metrics ──
    usecase_aggregate_changes = []
    new_metrics = {}
    usecases_data = None
    if USECASES_PATH.exists():
        usecases_data = load_json(USECASES_PATH)
        usecase_aggregate_changes = q5_collect_usecase_aggregate_changes(
            usecases_data, expected_diff
        )
        uc_fulltypes = usecases_data.get("fulltypes", {})
        role_metrics, role_violations = q5_collect_recipe_role_metrics(
            uc_fulltypes, expected_diff
        )
        nav_metrics, nav_violations = q5_collect_recipe_nav_metrics(
            expected_diff
        )
        req_index_metrics, req_index_violations = (
            q5_collect_recipe_requirement_index_metrics(expected_diff)
        )

        new_metrics.update(q5_collect_usecase_line_metrics(uc_fulltypes))
        new_metrics.update(q5_collect_evidence_strength_metrics(uc_fulltypes))
        new_metrics.update(role_metrics)
        new_metrics.update(q5_collect_registry_override_metrics())
        new_metrics.update(q5_collect_diagnostic_metrics())
        new_metrics.update(nav_metrics)
        new_metrics.update(req_index_metrics)

        violations.extend(role_violations)
        violations.extend(q5_validate_keep_unresolved_count())
        violations.extend(nav_violations)
        violations.extend(req_index_violations)

    new_metric_changes, metric_violations = q5_compare_metric_changes(
        new_metrics, expected_diff
    )
    violations.extend(metric_violations)

    # ── Step 3c~3f: Compare output aggregate count/hash changes ──
    description_aggregate_changes = q5_collect_description_aggregate_changes(
        expected_diff
    )
    requirements_aggregate_changes, req_fulltypes = (
        q5_collect_requirements_aggregate_changes(expected_diff)
    )
    legacy_count_changes = q5_collect_legacy_count_changes(expected_diff)
    require_channel_changes = q5_collect_require_channel_changes(
        req_fulltypes, expected_diff
    )

    # ── Step 4: Collect all changes ──
    all_changes = []
    all_changes.extend(new_metric_changes)
    all_changes.extend(decision_status_changes)
    all_changes.extend(usecase_aggregate_changes)
    all_changes.extend(description_aggregate_changes)
    all_changes.extend(requirements_aggregate_changes)
    all_changes.extend(legacy_count_changes)
    all_changes.extend(require_channel_changes)

    # ── Step 5~6: Check against allowed_changes and pending allowed ──
    unexpected, warnings = q5_report_allowed_changes(all_changes, allowed)

    status = "FAIL" if unexpected else "PASS"
    return {
        "status": status,
        "unexpected_changes": len(unexpected),
        "pending_allowed": len(warnings),
        "details": unexpected[:10] if unexpected else [],
        "warnings": warnings[:10] if warnings else [],
        "new_metrics": new_metrics,
    }


# ══════════════════════════════════════════════════════════════════════════
#  BUILD REPORT 생성
# ══════════════════════════════════════════════════════════════════════════

def generate_build_report(gates: dict, decisions: dict, overlay: dict) -> dict:
    """Build report JSON 생성."""
    stats = Counter(d["decision"] for d in decisions.values())
    by_ft = overlay.get("by_fulltype", {})
    strong = sum(1 for e in by_ft.values()
                 if e.get("uniqueness_summary") == "STRONG_ONLY")
    weak = sum(1 for e in by_ft.values()
               if e.get("uniqueness_summary") == "WEAK_ONLY")
    mixed = sum(1 for e in by_ft.values()
                if e.get("uniqueness_summary") == "MIXED")

    overall = "PASS" if all(
        g["status"] == "PASS" for g in gates.values()
    ) else "FAIL"

    report = {
        "version": QUALITY_GATES_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gates": gates,
        "statistics": {
            "total_items": len(decisions),
            "PASS": stats.get("PASS", 0),
            "NO": stats.get("NO", 0),
            "REVIEW": stats.get("REVIEW", 0),
            "STRONG": strong,
            "WEAK": weak,
            "MIXED": mixed,
        },
        "overall": overall,
    }
    return report


def generate_build_report_md(report: dict) -> str:
    """Build report Markdown 생성."""
    lines = []
    lines.append(f"# Build Report — Quality Gates {QUALITY_GATES_VERSION}")
    lines.append("")
    lines.append(f"**Timestamp**: {report['timestamp']}")
    lines.append(f"**Overall**: {'✅ PASS' if report['overall'] == 'PASS' else '❌ FAIL'}")
    lines.append("")

    lines.append("## Gate Results")
    lines.append("")
    lines.append("| Gate | Status | Details |")
    lines.append("|------|--------|---------|")

    gate_labels = {
        "Q1_pass_integrity": "Q1: PASS 무결성",
        "Q2_strong_integrity": "Q2: Strong 무결성",
        "Q3_anchor_completeness": "Q3: Anchor 완전성",
        "Q4_determinism": "Q4: 결정성",
        "Q5_regression_diff": "Q5: 회귀 diff",
    }

    for gid, label in gate_labels.items():
        gate = report["gates"].get(gid)
        if gate is None:
            lines.append(f"| {label} | ⏭ SKIP | not run |")
            continue
        icon = "✅" if gate["status"] == "PASS" else "❌"
        # Build detail string
        detail_parts = []
        for k, v in gate.items():
            if k in ("status", "details", "warnings"):
                continue
            detail_parts.append(f"{k}={v}")
        detail_str = ", ".join(detail_parts) if detail_parts else "-"
        lines.append(f"| {label} | {icon} {gate['status']} | {detail_str} |")

    lines.append("")
    lines.append("## Statistics")
    lines.append("")
    stats = report["statistics"]
    lines.append(f"- Total items: {stats['total_items']}")
    lines.append(f"- PASS: {stats['PASS']}, NO: {stats['NO']}, REVIEW: {stats['REVIEW']}")
    lines.append(f"- STRONG: {stats['STRONG']}, WEAK: {stats['WEAK']}, MIXED: {stats['MIXED']}")
    lines.append("")

    # Show violations if any
    any_violations = False
    for gid, gate in report["gates"].items():
        details = gate.get("details", [])
        warnings_list = gate.get("warnings", [])
        if details:
            if not any_violations:
                lines.append("## Violations")
                lines.append("")
                any_violations = True
            lines.append(f"### {gate_labels.get(gid, gid)}")
            lines.append("")
            for d in details:
                lines.append(f"- ❌ {d}")
            lines.append("")
        if warnings_list:
            if not any_violations:
                lines.append("## Warnings")
                lines.append("")
                any_violations = True
            lines.append(f"### {gate_labels.get(gid, gid)} (warnings)")
            lines.append("")
            for w in warnings_list:
                lines.append(f"- ⚠️ {w}")
            lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

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
