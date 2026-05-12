"""
DVF Layer 3 Pipeline — 고정 테스트
===================================
FAIL 케이스 고정: 각 T-Gate가 의도대로 FAIL/WARN을 생성하는지 검증.
결정론 검증: 2-run SHA 비교.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

# 경로 설정
BUILD_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD_DIR))

from pipeline.description.gate.t1_structural import run_t1
from pipeline.description.gate.t2_contract import run_t2
from pipeline.description.gate.t3_language import run_t3
from pipeline.description.gate.t4_independence import run_t4
from pipeline.description.gate.run_tgates import run_all_gates

# ── 기본 픽스처 ──

PROFILE = json.loads(
    (BUILD_DIR / "data" / "description" / "profiles" / "layer3.profile.json")
    .read_text("utf-8")
)

VALID_ENTRY = {
    "fulltype": "Base.TinOpener",
    "status": "active",
    "kind": "distinct_use",
    "text_ko": "소지하고 있으면 통조림을 열 수 있다.",
    "anchors": [],
    "notes": "",
}

ALL_FULLTYPES = {"Base.TinOpener", "Base.Hammer", "Base.Axe"}


def make_registry(*entries):
    return {"version": 1, "entries": list(entries)}


# ══════════════════════════════════════
# T1 Tests
# ══════════════════════════════════════

def test_t1_unknown_fulltype():
    """존재하지 않는 fulltype → T1 FAIL."""
    entry = {**VALID_ENTRY, "fulltype": "Base.DoesNotExist"}
    result = run_t1(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "unknown fulltype should FAIL"
    assert any("부재" in e or "없음" in e for e in result["errors"])
    print("  ✅ test_t1_unknown_fulltype")


def test_t1_active_empty_text():
    """active + empty text_ko → T1 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": ""}
    result = run_t1(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "active with empty text should FAIL"
    assert any("비어" in e for e in result["errors"])
    print("  ✅ test_t1_active_empty_text")


def test_t1_active_null_text():
    """active + null text_ko → T1 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": None}
    result = run_t1(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "active with null text should FAIL"
    print("  ✅ test_t1_active_null_text")


def test_t1_silent_kind_not_null():
    """silent + kind≠null → T1 FAIL."""
    entry = {
        "fulltype": "Base.Hammer",
        "status": "silent",
        "kind": "distinct_use",  # 위반
        "text_ko": None,
        "anchors": [],
        "notes": "",
    }
    result = run_t1(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "silent with kind should FAIL"
    assert any("kind" in e for e in result["errors"])
    print("  ✅ test_t1_silent_kind_not_null")


def test_t1_silent_text_not_null():
    """silent + text_ko≠null → T1 FAIL."""
    entry = {
        "fulltype": "Base.Hammer",
        "status": "silent",
        "kind": None,
        "text_ko": "이것은 있으면 안 됨.",
        "anchors": [],
        "notes": "",
    }
    result = run_t1(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "silent with text should FAIL"
    print("  ✅ test_t1_silent_text_not_null")


def test_t1_duplicate_fulltype():
    """fulltype 중복 → T1 FAIL."""
    e1 = {**VALID_ENTRY}
    e2 = {**VALID_ENTRY, "text_ko": "다른 문장."}
    result = run_t1(make_registry(e1, e2), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "duplicate fulltype should FAIL"
    assert any("중복" in e for e in result["errors"])
    print("  ✅ test_t1_duplicate_fulltype")


def test_t1_invalid_kind():
    """잘못된 kind → T1 FAIL."""
    entry = {**VALID_ENTRY, "kind": "invalid_kind_value"}
    result = run_t1(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert not result["passed"], "invalid kind should FAIL"
    print("  ✅ test_t1_invalid_kind")


def test_t1_valid():
    """정상 엔트리 → T1 PASS."""
    result = run_t1(make_registry(VALID_ENTRY), PROFILE, ALL_FULLTYPES)
    assert result["passed"], f"valid entry should PASS: {result['errors']}"
    print("  ✅ test_t1_valid")


# ══════════════════════════════════════
# T2 Tests
# ══════════════════════════════════════

def test_t2_newline():
    """줄바꿈 포함 → T2 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "첫째 줄.\n둘째 줄."}
    result = run_t2(make_registry(entry), PROFILE)
    assert not result["passed"], "newline should FAIL"
    print("  ✅ test_t2_newline")


def test_t2_index_header():
    """색인 헤더 패턴 → T2 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "관련 레시피: 나무판자 만들기."}
    result = run_t2(make_registry(entry), PROFILE)
    assert not result["passed"], "index header should FAIL"
    print("  ✅ test_t2_index_header")


def test_t2_comparison():
    """비교급 → T2 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "이것이 가장 좋은 도구다."}
    result = run_t2(make_registry(entry), PROFILE)
    assert not result["passed"], "comparison should FAIL"
    print("  ✅ test_t2_comparison")


def test_t2_classification():
    """내부 분류 노출 → T2 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "이 아이템의 분류는 도구다."}
    result = run_t2(make_registry(entry), PROFILE)
    assert not result["passed"], "classification leak should FAIL"
    print("  ✅ test_t2_classification")


# ══════════════════════════════════════
# T3 Tests
# ══════════════════════════════════════

def test_t3_no_ending():
    """종결 부호 없음 → T3 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "소지하고 있으면 통조림을 열 수 있다"}
    result = run_t3(make_registry(entry), PROFILE)
    assert not result["passed"], "no ending should FAIL"
    print("  ✅ test_t3_no_ending")


def test_t3_key_leak():
    """내부 키 노출 (Base.) → T3 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "Base.Hammer와 비슷한 도구다."}
    result = run_t3(make_registry(entry), PROFILE)
    assert not result["passed"], "key leak should FAIL"
    print("  ✅ test_t3_key_leak")


def test_t3_banned_phrase():
    """금지 어휘 (추천) → T3 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "추천하는 도구다."}
    result = run_t3(make_registry(entry), PROFILE)
    assert not result["passed"], "banned phrase should FAIL"
    print("  ✅ test_t3_banned_phrase")


def test_t3_valid():
    """정상 → T3 PASS."""
    result = run_t3(make_registry(VALID_ENTRY), PROFILE)
    assert result["passed"], f"valid text should PASS: {result['errors']}"
    print("  ✅ test_t3_valid")


# ══════════════════════════════════════
# T4 Tests
# ══════════════════════════════════════

def test_t4_skip_no_baseline():
    """baseline 없으면 SKIP."""
    result = run_t4(make_registry(VALID_ENTRY), PROFILE)
    assert result["passed"], "T4 should always pass"
    assert result["skipped"], "should skip without baseline"
    print("  ✅ test_t4_skip_no_baseline")


def test_t4_warn_high_similarity():
    """높은 유사도 → WARN + PASS."""
    layer1 = {"Base.TinOpener": "소지하고 있으면 통조림을 열 수 있다."}
    result = run_t4(make_registry(VALID_ENTRY), PROFILE, layer1_texts=layer1)
    assert result["passed"], "T4 should always pass"
    assert not result["skipped"]
    assert len(result["warnings"]) > 0, "high similarity should produce a WARN"
    print("  ✅ test_t4_warn_high_similarity")


# ══════════════════════════════════════
# Integration: run_all_gates
# ══════════════════════════════════════

def test_all_gates_pass():
    """정상 데이터 → 전체 PASS."""
    result = run_all_gates(make_registry(VALID_ENTRY), PROFILE, ALL_FULLTYPES)
    assert result["status"] == "pass", f"should pass: {result}"
    print("  ✅ test_all_gates_pass")


def test_all_gates_fail_at_t1():
    """T1 FAIL → T2/T3 건너뜀."""
    entry = {**VALID_ENTRY, "text_ko": ""}
    result = run_all_gates(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert result["status"] == "fail"
    assert result["stopped_at"] == "T1"
    assert result["t2_contract"] is None
    print("  ✅ test_all_gates_fail_at_t1")


def test_all_gates_fail_at_t2():
    """T1 PASS, T2 FAIL."""
    entry = {**VALID_ENTRY, "text_ko": "관련 레시피: 무언가."}
    result = run_all_gates(make_registry(entry), PROFILE, ALL_FULLTYPES)
    assert result["status"] == "fail"
    assert result["stopped_at"] == "T2"
    print("  ✅ test_all_gates_fail_at_t2")


# ══════════════════════════════════════
# Determinism
# ══════════════════════════════════════

def test_determinism():
    """동일 입력 → 동일 SHA."""
    from pipeline.description.build_layer3 import canonical_sha

    data = {"Base.A": {"kind": "identity", "text_ko": "테스트."}}
    sha1 = canonical_sha(data)
    sha2 = canonical_sha(data)
    assert sha1 == sha2, "canonical_sha must be deterministic"
    print("  ✅ test_determinism")


# ══════════════════════════════════════
# Runner
# ══════════════════════════════════════

ALL_TESTS = [
    # T1
    test_t1_unknown_fulltype,
    test_t1_active_empty_text,
    test_t1_active_null_text,
    test_t1_silent_kind_not_null,
    test_t1_silent_text_not_null,
    test_t1_duplicate_fulltype,
    test_t1_invalid_kind,
    test_t1_valid,
    # T2
    test_t2_newline,
    test_t2_index_header,
    test_t2_comparison,
    test_t2_classification,
    # T3
    test_t3_no_ending,
    test_t3_key_leak,
    test_t3_banned_phrase,
    test_t3_valid,
    # T4
    test_t4_skip_no_baseline,
    test_t4_warn_high_similarity,
    # Integration
    test_all_gates_pass,
    test_all_gates_fail_at_t1,
    test_all_gates_fail_at_t2,
    # Determinism
    test_determinism,
]


def main():
    print("=" * 50)
    print("  DVF Layer 3 Pipeline Tests")
    print("=" * 50)

    passed = 0
    failed = 0
    errors = []

    for test_fn in ALL_TESTS:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"  ❌ {test_fn.__name__}: {e}")
        except Exception as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"  ❌ {test_fn.__name__}: {type(e).__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"  결과: {passed} passed, {failed} failed / {len(ALL_TESTS)} total")
    print(f"{'=' * 50}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
