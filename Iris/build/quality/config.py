"""Shared constants for the quality gate modules.

Paths, version-derived artifact names, determinism file lists, and validation
enums consumed by ``quality_gates.py`` and the ``quality.*`` gate modules.

Extracted from the former monolithic ``quality_gates.py`` (Change 4 split).
Values are byte-for-byte equivalent to the originals; ``BUILD_DIR`` replaces the
old module-local ``SCRIPT_DIR`` name (which was never imported elsewhere).
"""
import sys
from pathlib import Path

# ── Path bootstrap: keep Iris/build importable (tools.common, quality.*) ──
BUILD_DIR = Path(__file__).resolve().parents[1]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from tools.common.versions import (
    BUILD_VERSION,
    QUALITY_GATES_VERSION,
    REQUIRE_FIELDS_VERSION,
    versioned_name,
)

IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"
DATA_DIR = BUILD_DIR / "data" / BUILD_VERSION
BUILD_DATA_PREFIX = f"build/data/{BUILD_VERSION}"

DECISIONS_PATH = OUTPUT_DIR / f"evidence_decisions.{BUILD_VERSION}.json"
CANDIDATES_PATH = OUTPUT_DIR / f"evidence_candidates.{BUILD_VERSION}.json"
OVERLAY_PATH = OUTPUT_DIR / f"uniqueness_overlay.{BUILD_VERSION}.json"
USECASES_PATH = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"
DESCRIPTIONS_PATH = OUTPUT_DIR / f"descriptions_by_fulltype.{BUILD_VERSION}.json"
ROLE_PROFILE_PATH = DATA_DIR / "role_profile_by_rule_id.json"
EXPECTED_DIFF_PATH = DATA_DIR / "expected_diff.json"
FROZEN_SHA_PATH = DATA_DIR / f"frozen_sha.{BUILD_VERSION}.json"

# ── Output files produced by quality_gates.py ──
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
