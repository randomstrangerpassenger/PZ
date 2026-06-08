"""Quality Gate Q4 — Determinism (canonical JSON SHA snapshot)."""
import hashlib
import json

from quality.config import (
    BUILD_DATA_PREFIX,
    DATA_DIR,
    DETERMINISM_BUILD_FILES,
    DETERMINISM_FILES,
    FROZEN_SHA_PATH,
    OUTPUT_DIR,
)
from tools.common.io import load_json, write_json


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
