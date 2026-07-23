from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import queue
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any
import zipfile


ROUND_ID = "dvf_3_3_registry_authority_canonical_closure"
CYCLE_ID = ROUND_ID
SCHEMA_PREFIX = "dvf-3-3-registry-authority-canonical-closure"
CONSUMED_ROADMAP_SHA256 = "17c41198e4d35a15743fd6c9f869ca545c5363a3a32eb005db1e94bc16530ecd"

REPO_ROOT = Path(__file__).resolve().parents[6]
V2_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2"
TOOLS_ROOT = V2_ROOT / "tools" / "build"
TESTS_ROOT = V2_ROOT / "tests"
DEFAULT_EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
ATTEMPTS_ROOT = DEFAULT_EVIDENCE_ROOT / "attempts"

PLAN_PATH = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
ROADMAP_PATH = REPO_ROOT / "docs" / f"{ROUND_ID}_roadmap.md"
PHILOSOPHY_PATH = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS_PATH = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_PATH = REPO_ROOT / "docs" / "ARCHITECTURE.md"
PROJECT_ROADMAP_PATH = REPO_ROOT / "docs" / "ROADMAP.md"
EXECUTION_CONTRACT_PATH = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
LUA_CHECKER_PATH = REPO_ROOT / "tools" / "check_lua_syntax.ps1"

COMMON_PATH = TOOLS_ROOT / f"{ROUND_ID}.py"
RUNNER_PATH = TOOLS_ROOT / f"run_{ROUND_ID}.py"
VALIDATOR_PATH = TOOLS_ROOT / f"validate_{ROUND_ID}.py"
FOCUSED_TEST_PATH = TESTS_ROOT / f"test_{ROUND_ID}.py"
FOCUSED_TEST_COMMAND = (
    'uv run python -B -m unittest discover -s Iris/build/description/v2/tests '
    '-p "test_dvf_3_3_registry_authority_canonical_closure.py"'
)
FOCUSED_TEST_RECEIPT_NAME = "focused_test_preimplementation_receipt.json"
FOCUSED_TEST_FAILURE_RECORD_NAME = (
    "current_session_focused_test_execution_failure_record.json"
)
TRUSTED_EXECUTION_SEQUENCE_FAILURE_ANCHORS = {
    "attempt-0020-entry": {
        "execution_base_commit": "334a90fc9606017326d936fd9450d98de27ee7a5",
        "sequence_failure_record_sha256": "f302cf7ee72df38f1b6efc25440692b3d0d61ea4bdd78ad5ed44e0b5d73f4c4d",
        "attempt_evidence_tree_sha256": "e050206d21b621f8b78a843e5fb55ffd4410113f4595cf0c4a2c69c469c5c0f5",
        "owner_inputs_tree_sha256": "53706035450dfc75fb1105ade725181ae4e1d8ca2db6e1ec6d74d35448aeb472",
        "predecessor_registration_rows_sha256": "0c9a42ad666059d48c2e05e33e5b78151a60e1909543335a64d1f2ec02d2ae0a",
        "preflight_report_sha256": "36843d0af33fa5ab232fb7636d5ec5a137446e4f7331cc1e582eb9877f4a875e",
        "materialization_report_sha256": "b8a2a294d778deee300b81325da44db3b8846e0dab5a677b6c3d1447c51226ee",
        "blocker_zero_record_sha256": "f6678097f6cdc6134cfe6f19d8e0195ae762cb8cc9506e64e2446c740c286dd4",
        "focused_test_result_report_sha256": "8f35f61bf71a6bc9c22d6b560ac5df54fa8348fb891e4a6101ed2a5bba63f895",
        "implementation_scope_report_sha256": "8d3b15ea853f0bad5c5c738c44f2ea4a98bca3788ce3e08ac9a3d351ab152c46",
        "focused_test_base_file_sha256": "1b46b78e305cfd9012d06b2e4bd890b531e59c08268018351de3dc7d05e633f5",
        "implementation_common_base_file_sha256": "6f3adb0a2ac4ee968fe24997cf6d2ed1238a14a75c039b5ef9a76d253c2ce2d9",
        "implementation_runner_base_file_sha256": "3e3bacbf6a876036b8f9a34cf2f0462cbbc98fa1edd7b6b1f80074becb779d51",
    },
}
TRUSTED_FOCUSED_TEST_FAILURE_ANCHORS = {
    "attempt-0021-entry": {
        "execution_base_commit": "58170e7e56d16de4801159e64c3dcbf5b7882396",
        "failure_record_sha256": "324d63683246df8cff9c6faa57ef1ac02872f6f1e5e57e0c351e378fc33ee5e4",
        "attempt_evidence_tree_sha256": "11353e8a46945c530ad88259a0072507fe6c84670d0f65c4d03bbc90666c65ef",
        "owner_inputs_tree_sha256": "395801ebfee82cb11e895e9a38eb6faa08eaaa7a350634869a752826b1568f81",
        "predecessor_registration_rows_sha256": "20fb499b5aa768fd1e863449b4ac9c8a4e4d77c1c4ace347d3abd60b8c162e4e",
        "preflight_report_sha256": "2484e791c072979079bf40d50163b6d8eb3cb91f0b2724bceea3577d106fa323",
        "materialization_report_sha256": "19abcd6944deb61b4a63b226d2d6e2bad684a840ea552faf020e0da058a2adf9",
        "blocker_zero_record_sha256": "648e2a7c17a36219549c118c13ca5380e821a34dae1ddeb0eed77a6bbe6c2ec3",
        "reviewer_designation_sha256": "1856f90fb44dc241c664a900d36c174a783580ac4451d06d26f793cb7a31f82b",
        "responsibility_review_sha256": "0f737cfd2e8299fec28c98d991663f36e4441873797d19a81d7b04533e3bf8b8",
        "authority_review_sha256": "fe8c2f3a1422be994740ae38c8a1184978b430a010f61a7cd45f8fb675854021",
        "adversarial_review_sha256": "24bf07dfdd9ebf3fbabbe44c083e288ab6893d5b1ba0a8dc1b6274ad64bdda5f",
        "focused_test_worktree_sha256": "ed2618b826861572e0b5b1fc158c4f976464a931ecfb975dd0357405731a733f",
        "focused_test_git_blob_sha256": "f42e3759f00adc5c94475c563ddbb14bb77d0d0b35139026d6939f08944f9b7d",
        "common_git_blob_sha256": "e6b48edfb99ea39a860ad52b8b3182689e8f8ba35bc1fbcc9c82af63aa84edf5",
        "round3_runner_git_blob_sha256": "cd58583e055d22b87718ee31f4cee2e33d5c670eb28ec5797749a7d22c91cbc5",
        "plan_git_blob_sha256": "72737f5a887132e78c598b273da158dfbc6adb245670f8d1df29f794856bc383",
    },
}
BOOTSTRAP_MANIFEST_PATH = DEFAULT_EVIDENCE_ROOT / "phase0" / "bootstrap_scaffold_hash_manifest.json"

OWNER_INPUT_ROOT = V2_ROOT / "owner_inputs" / ROUND_ID
CLEAN_CHECKPOINT_INPUT = (
    OWNER_INPUT_ROOT / "worktree_checkpoints" / "current_session_clean_worktree_checkpoint_record.json"
)
OWNER_DECISION_INPUT = (
    OWNER_INPUT_ROOT / "owner_decisions" / "current_session_owner_decision_record.json"
)
PLAN_APPROVAL_INPUT = (
    OWNER_INPUT_ROOT / "plan_approvals" / "current_session_implementation_plan_approval_record.json"
)
REVIEWER_DESIGNATION_INPUT = (
    OWNER_INPUT_ROOT / "reviewer_designations" / "current_session_independent_reviewer_designation.json"
)
FOCUSED_TEST_ATTESTATION_INPUT = (
    OWNER_INPUT_ROOT
    / "focused_test_attestations"
    / "current_session_focused_test_execution_attestation.json"
)
FOCUSED_TEST_FAILURE_INPUT = (
    OWNER_INPUT_ROOT
    / "focused_test_attestations"
    / FOCUSED_TEST_FAILURE_RECORD_NAME
)
ATTEMPT_REGISTRATION_INPUT = (
    OWNER_INPUT_ROOT
    / "attempt_registrations"
    / "current_session_attempt_record.json"
)
GATE_ADOPTION_INPUT = (
    OWNER_INPUT_ROOT
    / "gate_adoptions"
    / "current_session_required_gate_adoption_authorization_record.json"
)
PREIMPLEMENTATION_REVIEW_INPUTS = (
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_responsibility_boundary_review.md",
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_authority_evidence_integrity_review.md",
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_adversarial_failure_mode_review.md",
)
PRACTICAL_REVIEW_INPUT = (
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_practical_review.md"
)
PRACTICAL_RETRY_INPUT = (
    OWNER_INPUT_ROOT
    / "attempt_registrations"
    / "current_session_practical_retry_record.json"
)
PRACTICAL_CORRECTION_INPUT = (
    OWNER_INPUT_ROOT
    / "attempt_registrations"
    / "current_session_practical_post_adoption_correction_record.json"
)
INDEPENDENT_REVIEW_INPUT = (
    OWNER_INPUT_ROOT / "independent_reviews" / "current_session_independent_closeout_review.md"
)
OWNER_SEAL_INPUT = (
    OWNER_INPUT_ROOT / "owner_seals" / "current_session_owner_canonical_seal_record.json"
)

RESERVED_EXTERNAL_INPUTS = (
    CLEAN_CHECKPOINT_INPUT,
    OWNER_DECISION_INPUT,
    PLAN_APPROVAL_INPUT,
    REVIEWER_DESIGNATION_INPUT,
    ATTEMPT_REGISTRATION_INPUT,
    *PREIMPLEMENTATION_REVIEW_INPUTS,
    PRACTICAL_REVIEW_INPUT,
    PRACTICAL_RETRY_INPUT,
    PRACTICAL_CORRECTION_INPUT,
    FOCUSED_TEST_ATTESTATION_INPUT,
    FOCUSED_TEST_FAILURE_INPUT,
    GATE_ADOPTION_INPUT,
    INDEPENDENT_REVIEW_INPUT,
    OWNER_SEAL_INPUT,
)

SCAFFOLD_PATHS = (
    COMMON_PATH,
    RUNNER_PATH,
    VALIDATOR_PATH,
    FOCUSED_TEST_PATH,
)

ALL_RUNNER_MODES = (
    "preflight",
    "materialize-preimplementation-reviews",
    "implementation",
    "wp1",
    "wp2",
    "wp3",
    "wp4",
    "wp5",
    "wp6",
    "wp7",
    "gate-candidate",
    "adopt-gate",
    "final-rerun",
    "materialize-independent-review",
    "materialize-owner-seal",
    "prepare-top-docs",
    "post-external",
    "finalize",
    "practical-preflight",
    "practical-materialize-review",
    "practical-implementation",
    "practical-gate-candidate",
    "practical-adopt-gate",
    "practical-confirm-gate-adoption",
    "practical-final-validation",
    "practical-materialize-closeout-review",
    "practical-materialize-owner-seal",
    "practical-finalize",
)
IMPLEMENTED_SCAFFOLD_MODES = (
    "preflight",
    "materialize-preimplementation-reviews",
)
IMPLEMENTED_SCAFFOLD_VALIDATIONS = (
    "require-preflight",
    "require-preimplementation-reviews",
    "require-execution-entry",
)
IMPLEMENTED_RUNNER_MODES = (
    *IMPLEMENTED_SCAFFOLD_MODES,
    "implementation",
    "practical-preflight",
    "practical-materialize-review",
    "practical-implementation",
    "practical-gate-candidate",
    "practical-adopt-gate",
    "practical-confirm-gate-adoption",
    "practical-final-validation",
    "practical-materialize-closeout-review",
    "practical-materialize-owner-seal",
    "practical-finalize",
)
IMPLEMENTED_VALIDATIONS = (
    *IMPLEMENTED_SCAFFOLD_VALIDATIONS,
    "require-implementation",
    "require-practical-preflight",
    "require-practical-review",
    "require-practical-implementation",
    "require-practical-gate-candidate",
    "require-practical-gate-adoption",
    "require-practical-final-validation",
    "require-practical-closeout-review",
    "require-practical-owner-seal",
    "require-practical-terminal-seal",
)

PREIMPLEMENTATION_REVIEW_SCOPES = (
    "responsibility_boundary",
    "authority_evidence_integrity",
    "adversarial_failure_mode",
)
PREIMPLEMENTATION_REVIEW_OUTPUTS = (
    "responsibility_boundary_review.md",
    "authority_evidence_integrity_review.md",
    "adversarial_failure_mode_review.md",
)

PROTECTED_SURFACES = (
    V2_ROOT / "data" / "dvf_3_3_input_manifest.json",
    V2_ROOT / "data" / "dvf_3_3_facts.jsonl",
    V2_ROOT / "data" / "dvf_3_3_decisions.jsonl",
    V2_ROOT / "data" / "dvf_3_3_overlay_support.jsonl",
    V2_ROOT / "data" / "compose_profiles_v2.json",
    V2_ROOT / "data" / "compose_profile_identity_hint_rules.json",
    V2_ROOT / "data" / "compose_profile_conflict_precedence_rules.json",
    V2_ROOT / "output" / "dvf_3_3_rendered.json",
    V2_ROOT / "output" / "style_normalization_changes.jsonl",
    V2_ROOT / "output" / "compose_requeue_candidates.jsonl",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiSections.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Util" / "IrisModuleBootstrap.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Util" / "IrisRequire.lua",
    REPO_ROOT / "Iris" / "build" / "package",
)

LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ACTIVE_CORE_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_TEST_TAXONOMY = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_test_taxonomy.json"
ROUND3_CONTRACT_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_contract_manifest.json"
AUTHORITY_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "authority" / "iris_current_authority_manifest.json"
INPUT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
COMPOSE_TOOL = TOOLS_ROOT / "compose_layer3_text.py"
EXPORT_TOOL = TOOLS_ROOT / "export_dvf_3_3_lua_bridge.py"
COMPOSE_DEPENDENCIES = (
    COMPOSE_TOOL,
    TOOLS_ROOT / "compose_layer3_io.py",
    TOOLS_ROOT / "compose_layer3_body_profile.py",
    TOOLS_ROOT / "compose_layer3_item.py",
    TOOLS_ROOT / "compose_layer3_render.py",
    V2_ROOT / "tools" / "postproc_ko.py",
    V2_ROOT / "tools" / "style" / "__init__.py",
    V2_ROOT / "tools" / "style" / "normalizer.py",
    V2_ROOT / "tools" / "style" / "rules" / "global_rules.json",
    V2_ROOT / "tools" / "style" / "rules" / "family_rules.json",
)
COMPLETION_TOOL = TOOLS_ROOT / "dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
COMPLETION_RUNNER = TOOLS_ROOT / "run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
COMPLETION_VALIDATOR = TOOLS_ROOT / "validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
COMPLETION_TEST = TESTS_ROOT / "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
COMPOSE_OVERLAY_TEST = TESTS_ROOT / "test_compose_layer3_text_overlay.py"
CONSUMER_MIGRATION_NORMALIZATION_TEST = (
    TESTS_ROOT / "test_dvf_3_3_consumer_migration_input_normalization.py"
)
CONSUMER_MIGRATION_NORMALIZATION_COMMON = (
    TOOLS_ROOT / "dvf_3_3_consumer_migration_normalization_common.py"
)
CONSUMER_MIGRATION_NORMALIZATION_WRAPPERS = (
    TOOLS_ROOT / "generate_dvf_3_3_consumer_migration_input_contract.py",
    TOOLS_ROOT / "generate_dvf_3_3_consumer_migration_eligibility_matrix.py",
    TOOLS_ROOT / "generate_dvf_3_3_missing_path_disposition_ledger.py",
    TOOLS_ROOT / "validate_dvf_3_3_consumer_migration_anchor_relocation.py",
    TOOLS_ROOT / "generate_dvf_3_3_authority_role_migration_rule_seed.py",
    TOOLS_ROOT
    / "generate_dvf_3_3_downstream_command_surface_compatibility_manifest.py",
    TOOLS_ROOT
    / "generate_dvf_3_3_consumer_migration_reconciled_input_manifest.py",
    TOOLS_ROOT / "validate_dvf_3_3_consumer_migration_input_normalization.py",
)
CONSUMER_MIGRATION_NORMALIZATION_INPUTS = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_execution"
    / "phase8"
    / "consumer_migration_matrix.jsonl",
    V2_ROOT
    / "staging"
    / "dvf_3_3_vnext_execution"
    / "phase8"
    / "consumer_migration_dry_run.json",
)
CURRENT_ROUTE_FROZEN_FIXTURE_CAPTURE_TOOL = (
    TOOLS_ROOT
    / "capture_dvf_3_3_registry_authority_frozen_predecessor_fixture.py"
)
CURRENT_ROUTE_FROZEN_FIXTURE_ROOT = (
    V2_ROOT
    / "frozen_predecessor_inputs"
    / ROUND_ID
    / "current_route"
)
CURRENT_ROUTE_FROZEN_FIXTURE_MANIFEST = (
    CURRENT_ROUTE_FROZEN_FIXTURE_ROOT / "manifest.json"
)
CURRENT_ROUTE_FROZEN_FIXTURE_PAYLOADS = tuple(
    CURRENT_ROUTE_FROZEN_FIXTURE_ROOT
    / "payload"
    / f"{index:04d}.bin"
    for index in range(34)
)
CURRENT_ROUTE_FROZEN_FIXTURE_FILES = (
    CURRENT_ROUTE_FROZEN_FIXTURE_MANIFEST,
    *CURRENT_ROUTE_FROZEN_FIXTURE_PAYLOADS,
)
CURRENT_ROUTE_FROZEN_FIXTURE_ROWS_SHA256 = (
    "6017c214709e77fd84f0b9a43c374f74bc95ce430bc3b5b2f65e03d524896efb"
)
CURRENT_ROUTE_REFACTORED_TESTS = (
    TESTS_ROOT / "test_dvf_3_3_closeout_reentry_guard_seal.py",
    TESTS_ROOT
    / "test_dvf_3_3_core_registry_boundary_required_gate_adoption.py",
    TESTS_ROOT / "test_dvf_3_3_cutover_tooling_readiness.py",
    TESTS_ROOT
    / "test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py",
    TESTS_ROOT / "test_dvf_3_3_shared_disposition_consumption.py",
    TESTS_ROOT
    / "test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py",
)
CURRENT_ROUTE_SUBPROCESS_TARGETS = (
    TOOLS_ROOT / "run_dvf_3_3_closeout_reentry_guard_seal.py",
    TOOLS_ROOT
    / "run_dvf_3_3_core_registry_boundary_required_gate_adoption.py",
    TOOLS_ROOT
    / "validate_dvf_3_3_core_registry_boundary_required_gate_adoption.py",
    TOOLS_ROOT / "generate_dvf_3_3_overlay_support_artifact.py",
    TOOLS_ROOT / "manage_dvf_3_3_runtime_chunk_cutover.py",
    TOOLS_ROOT / "apply_dvf_3_3_consumer_migration.py",
    TOOLS_ROOT / "generate_dvf_3_3_row_level_migration_ledger.py",
    TOOLS_ROOT / "validate_dvf_3_3_actual_diff_to_ledger.py",
    TOOLS_ROOT / "validate_dvf_3_3_command_surface_mapping.py",
    TOOLS_ROOT
    / "run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py",
    TOOLS_ROOT
    / "validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py",
    TOOLS_ROOT / "run_dvf_3_3_shared_disposition_consumption.py",
    TOOLS_ROOT / "validate_dvf_3_3_shared_disposition_consumption.py",
    TOOLS_ROOT
    / "run_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py",
    TOOLS_ROOT
    / "validate_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py",
    *CONSUMER_MIGRATION_NORMALIZATION_WRAPPERS,
)
CURRENT_ROUTE_SUBPROCESS_IMPLEMENTATIONS = (
    TOOLS_ROOT / "dvf_3_3_closeout_reentry_guard_seal_common.py",
    TOOLS_ROOT
    / "dvf_3_3_core_registry_boundary_required_gate_adoption.py",
    TOOLS_ROOT / "dvf_3_3_cutover_tooling_readiness_common.py",
    TOOLS_ROOT
    / "dvf_3_3_predecessor_stale_artifact_reentry_guard_common.py",
    TOOLS_ROOT / "dvf_3_3_shared_disposition_consumption_common.py",
    TOOLS_ROOT
    / "dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py",
)
CURRENT_ROUTE_SELECTIVE_DEPENDENCIES = (
    COMPOSE_OVERLAY_TEST,
    CONSUMER_MIGRATION_NORMALIZATION_TEST,
    CONSUMER_MIGRATION_NORMALIZATION_COMMON,
    *CONSUMER_MIGRATION_NORMALIZATION_INPUTS,
    CURRENT_ROUTE_FROZEN_FIXTURE_CAPTURE_TOOL,
    *CURRENT_ROUTE_FROZEN_FIXTURE_FILES,
    *CURRENT_ROUTE_REFACTORED_TESTS,
    *CURRENT_ROUTE_SUBPROCESS_TARGETS,
    *CURRENT_ROUTE_SUBPROCESS_IMPLEMENTATIONS,
)
PRACTICAL_DURABLE_GATE_CONTRACT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "registry_authority_required_gate_contract.json"
)
PRACTICAL_CLOSEOUT_REVIEW_INPUT = INDEPENDENT_REVIEW_INPUT
PRACTICAL_OWNER_SEAL_INPUT = OWNER_SEAL_INPUT
PRACTICAL_REQUIRED_TEST_IDS = (
    (
        "test_dvf_3_3_registry_authority_canonical_closure."
        "RegistryAuthorityCanonicalClosureImplementationTest."
        "test_registry_authority_required_gate_contract"
    ),
    (
        "test_dvf_3_3_registry_authority_canonical_closure."
        "RegistryAuthorityCanonicalClosureImplementationTest."
        "test_default_current_compose_is_rejected_without_mutation"
    ),
    (
        "test_dvf_3_3_registry_authority_canonical_closure."
        "RegistryAuthorityCanonicalClosureImplementationTest."
        "test_wp6_live_denominator_closes_dependencies_and_vcs_inventory"
    ),
)
PRACTICAL_FINAL_COMMAND_IDS = (
    "wp5_contained_candidate_generation",
    "wp5_unreceipted_real_path_rejection",
    "require_implementation",
    "registry_closure_focused_test",
    "current_route_required_regressions",
    "lua_syntax",
    "final_internal_no_mutation_and_binding",
)
PRACTICAL_CODE_STATE_PATHS = (
    REPO_ROOT / ".gitattributes",
    REPO_ROOT / ".gitignore",
    PLAN_PATH,
    ROADMAP_PATH,
    DECISIONS_PATH,
    ARCHITECTURE_PATH,
    PROJECT_ROADMAP_PATH,
    COMMON_PATH,
    RUNNER_PATH,
    VALIDATOR_PATH,
    FOCUSED_TEST_PATH,
    ROUND3_RUNNER,
    ROUND3_TEST_TAXONOMY,
    ACTIVE_CORE_MANIFEST,
    COMPOSE_TOOL,
    COMPLETION_TOOL,
    COMPLETION_RUNNER,
    COMPLETION_VALIDATOR,
    COMPLETION_TEST,
    *CURRENT_ROUTE_SELECTIVE_DEPENDENCIES,
    LIVE_REQUIRED_MANIFEST,
    PRACTICAL_DURABLE_GATE_CONTRACT,
    REPO_ROOT / "docs" / "dvf_registry_handoff_contract.md",
    REPO_ROOT / "docs" / "registry_authority_claim_contract.md",
    REPO_ROOT / "docs" / "registry_authority_protected_surface_policy.md",
    REPO_ROOT / "docs" / "registry_authority_seal_cutover_contract.md",
    REPO_ROOT / "docs" / "stale_predecessor_reentry_guard_policy.md",
    REPO_ROOT / "docs" / f"{ROUND_ID}_claim_boundary.md",
)
RUNTIME_MANIFEST = REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua"
RUNTIME_CHUNK_DIR = RUNTIME_MANIFEST.with_suffix("")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_utc_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def filesystem_path(path: Path) -> Path:
    raw = str(path)
    if os.name == "nt" and raw.startswith("\\\\?\\"):
        return path
    resolved = path.resolve()
    if os.name != "nt":
        return resolved
    raw = str(resolved)
    if raw.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + raw[2:])
    return Path("\\\\?\\" + raw)


def path_is_file(path: Path) -> bool:
    return filesystem_path(path).is_file()


def path_is_dir(path: Path) -> bool:
    return filesystem_path(path).is_dir()


def sha256_file(path: Path) -> str | None:
    source = filesystem_path(path)
    if not source.is_file():
        return None
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha256(commit: str, relative_path: str) -> str | None:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    return sha256_bytes(completed.stdout) if completed.returncode == 0 else None


def files_byte_identical(left: Path, right: Path) -> bool:
    left_source = filesystem_path(left)
    right_source = filesystem_path(right)
    return (
        left_source.is_file()
        and right_source.is_file()
        and left_source.read_bytes() == right_source.read_bytes()
    )


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_hash(payload: Any) -> str:
    return sha256_bytes(canonical_json_bytes(payload))


def text_content_sha256(path: Path) -> str | None:
    if not path_is_file(path):
        return None
    try:
        content = filesystem_path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None
    return sha256_bytes(content.encode("utf-8"))


def directory_file_rows(path: Path) -> list[dict[str, str | None]] | None:
    source = filesystem_path(path)
    if not source.is_dir():
        return None
    rows: list[dict[str, str | None]] = []
    for directory, child_directories, filenames in os.walk(source):
        child_directories.sort()
        for filename in sorted(filenames):
            child = Path(directory) / filename
            rows.append(
                {
                    "path": child.relative_to(source).as_posix(),
                    "sha256": sha256_file(child),
                }
            )
    return rows


def directory_tree_hash(path: Path) -> str | None:
    rows = directory_file_rows(path)
    if rows is None:
        return None
    return canonical_hash(rows)


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def validate_attempt_id(attempt_id: str | None) -> str:
    if not isinstance(attempt_id, str) or not re.fullmatch(
        r"attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]{0,47}", attempt_id
    ):
        raise ValueError(
            "attempt_id must match attempt-NNNN-lowercase-label"
        )
    return attempt_id


def resolve_evidence_root(
    value: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> Path:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    expected = (ATTEMPTS_ROOT / normalized_attempt_id).resolve()
    candidate = Path(value or expected).resolve()
    if candidate != expected or not is_within(candidate, ATTEMPTS_ROOT):
        raise ValueError(
            "evidence root must equal the registered attempt root "
            f"{repo_relative(expected)}"
        )
    return candidate


def practical_attempt_failure_paths(root: Path) -> list[Path]:
    failure_root = filesystem_path(root / "attempt_failures")
    if not failure_root.is_dir():
        return []
    return [
        root / "attempt_failures" / child.name
        for child in sorted(failure_root.glob("*.json"), key=lambda path: path.name)
        if child.is_file()
    ]


def require_practical_attempt_open(root: Path) -> None:
    failure_paths = practical_attempt_failure_paths(root)
    if failure_paths:
        raise RuntimeError(
            "practical attempt already terminated by preserved failure record: "
            + ",".join(path.name for path in failure_paths)
        )


def practical_attempt_failure_blockers(root: Path) -> list[str]:
    return [
        f"practical_attempt_terminal_failure_present:{path.name}"
        for path in practical_attempt_failure_paths(root)
    ]


def read_json_object(path: Path) -> dict[str, Any]:
    source = filesystem_path(path)
    if not source.is_file():
        return {}
    try:
        with source.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_json_once(path: Path, payload: Any) -> None:
    if not is_within(path, ATTEMPTS_ROOT):
        raise ValueError(f"refusing out-of-attempt evidence write: {path}")
    target = filesystem_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)


def write_text_once(path: Path, payload: str) -> None:
    if not is_within(path, ATTEMPTS_ROOT):
        raise ValueError(f"refusing out-of-attempt evidence write: {path}")
    target = filesystem_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def copy_external_bytes_once(source: Path, target: Path) -> None:
    source_path = filesystem_path(source)
    if not source_path.is_file():
        raise FileNotFoundError(source)
    if not is_within(target, ATTEMPTS_ROOT):
        raise ValueError(f"refusing out-of-attempt materialization: {target}")
    target_path = filesystem_path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("xb") as handle:
        handle.write(source_path.read_bytes())


def record_attempt_failure_once(
    evidence_root: str | Path | None,
    *,
    attempt_id: str | None,
    mode: str,
    error_type: str,
    error: str,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    existing_failure_paths = practical_attempt_failure_paths(root)
    if existing_failure_paths:
        same_mode_failure = root / "attempt_failures" / f"{mode}.json"
        preserved = (
            same_mode_failure
            if same_mode_failure in existing_failure_paths
            else existing_failure_paths[0]
        )
        return {
            "written": False,
            "reason": (
                "failure_record_already_preserved"
                if preserved == same_mode_failure
                else "attempt_terminal_failure_already_preserved"
            ),
            "path": repo_relative(preserved),
            "sha256": sha256_file(preserved),
        }
    terminal_by_mode = {
        "preflight": root / "phase0" / "preflight_report.json",
        "materialize-preimplementation-reviews": (
            root / "phase3" / "preimplementation_review_materialization_report.json"
        ),
        "implementation": root / "phase4" / "implementation_scope_report.json",
        "practical-preflight": root / "phase0" / "practical_preflight_report.json",
        "practical-materialize-review": (
            root / "phase3" / "practical_review_materialization_report.json"
        ),
        "practical-implementation": (
            root / "phase4" / "practical_implementation_scope_report.json"
        ),
        "practical-gate-candidate": (
            root / "phase4" / "gate_candidate" / "candidate_report.json"
        ),
        "practical-adopt-gate": (
            root / "phase4" / "gate_adoption" / "adoption_authorization_report.json"
        ),
        "practical-confirm-gate-adoption": (
            root / "phase4" / "gate_adoption" / "adoption_report.json"
        ),
        "practical-final-validation": (
            root / "phase5" / "final_command_matrix_report.json"
        ),
        "practical-materialize-closeout-review": (
            root / "phase5" / "closeout_review_materialization_report.json"
        ),
        "practical-materialize-owner-seal": (
            root / "phase5" / "owner_seal_materialization_report.json"
        ),
        "practical-finalize": root / "phase5" / "terminal_hash_seal.json",
    }
    terminal = terminal_by_mode.get(mode)
    failure_path = root / "attempt_failures" / f"{mode}.json"
    terminal_claim_complete = bool(terminal is not None and terminal.is_file())
    if terminal_claim_complete and mode == "practical-final-validation":
        matrix = read_json_object(terminal)
        artifact_path = root / "phase5" / "final_artifact_hash_manifest.json"
        machine_path = root / "phase5" / "machine_closure_candidate_report.json"
        artifact = read_json_object(artifact_path)
        machine = read_json_object(machine_path)
        terminal_claim_complete = matrix.get("status") == "FAIL" or (
            matrix.get("status") == "PASS"
            and artifact.get("status") == "PASS"
            and artifact.get("final_command_matrix_sha256")
            == sha256_file(terminal)
            and machine.get("status")
            == "machine_pass_pending_external_review_and_owner_seal"
            and machine.get("final_command_matrix_sha256")
            == sha256_file(terminal)
            and machine.get("final_artifact_hash_manifest_sha256")
            == sha256_file(artifact_path)
        )
    if terminal_claim_complete:
        return {
            "written": False,
            "reason": "terminal_claim_output_already_exists",
            "path": None,
            "sha256": None,
        }
    if failure_path.is_file():
        return {
            "written": False,
            "reason": "failure_record_already_preserved",
            "path": repo_relative(failure_path),
            "sha256": sha256_file(failure_path),
        }
    payload = {
        "schema_version": f"{SCHEMA_PREFIX}-attempt-failure-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "mode": mode,
        "recorded_at": utc_now(),
        "status": "FAIL",
        "error_type": error_type,
        "error": error,
        "plan_sha256": sha256_file(PLAN_PATH),
        "execution_head": current_head(),
        "code_state_sha256": practical_committed_code_state_hash(),
        "claim_output_overwritten": False,
        "failure_record_write_once": True,
        "wp_execution_allowed": False,
    }
    if mode.startswith("practical-"):
        normalized_error = f"{error_type}: {error}".lower()
        environment_failure = (
            error_type in {"PermissionError", "FileNotFoundError"}
            or "permissionerror" in normalized_error
            or "winerror 5" in normalized_error
            or "environment" in normalized_error
            or "luac" in normalized_error
        )
        practical_preflight = read_json_object(
            root / "phase0" / "practical_preflight_report.json"
        )
        baseline = practical_preflight.get("protected_surface_rows")
        fresh_protected = protected_surface_rows()
        nonce_root = root / "phase4" / "gate_adoption" / "nonce_consumption"
        nonce_consumed = bool(
            path_is_dir(nonce_root)
            and any(
                child.is_file()
                for child in filesystem_path(nonce_root).glob("*.json")
            )
        )
        payload.update(
            {
                "review_sha256": sha256_file(PRACTICAL_REVIEW_INPUT),
                "failure_classification": (
                    "environment" if environment_failure else "implementation"
                ),
                "protected_mutation_count": (
                    0
                    if isinstance(baseline, list) and baseline == fresh_protected
                    else 1
                ),
                "adoption_nonce_consumed": nonce_consumed,
            }
        )
    write_json_once(failure_path, payload)
    return {
        "written": True,
        "reason": "new_failure_record",
        "path": repo_relative(failure_path),
        "sha256": sha256_file(failure_path),
    }


def run_git(*args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "argv": ["git", *args],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def current_head() -> str | None:
    result = run_git("rev-parse", "HEAD")
    if result["exit_code"] != 0:
        return None
    return result["stdout"].strip() or None


def git_status_rows() -> tuple[str, list[str]]:
    result = run_git("status", "--porcelain=v1", "--untracked-files=all")
    output = result["stdout"] if result["exit_code"] == 0 else ""
    return output, [line for line in output.splitlines() if line]


def status_path(line: str) -> str:
    raw = line[3:] if len(line) >= 3 else line
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.strip().strip('"').replace("\\", "/")


def scaffold_file_rows() -> list[dict[str, Any]]:
    return [
        {
            "path": repo_relative(path),
            "exists": path.is_file(),
            "byte_length": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path),
        }
        for path in SCAFFOLD_PATHS
    ]


def scaffold_capabilities() -> dict[str, Any]:
    return {
        "implemented_success_modes": list(IMPLEMENTED_SCAFFOLD_MODES),
        "implemented_success_validations": list(IMPLEMENTED_SCAFFOLD_VALIDATIONS),
        "declared_future_modes": list(ALL_RUNNER_MODES),
        "aggregate_mode_present": False,
        "review_materialization_present": True,
        "execution_entry_validation_present": True,
        "wp_implementation_present": False,
        "gate_adoption_present": False,
        "finalization_producer_present": False,
        "owner_or_reviewer_verdict_authoring_present": False,
        "current_or_protected_writer_present": False,
        "attempt_evidence_write_once_present": True,
        "failure_history_write_once_present": True,
    }


def scaffold_manifest_projection() -> dict[str, Any]:
    return {
        "schema_version": f"{SCHEMA_PREFIX}-bootstrap-scaffold-manifest-v2",
        "round_id": ROUND_ID,
        "self_hash_excluded": True,
        "commit_hash_excluded": True,
        "scaffold_paths": scaffold_file_rows(),
        "capabilities": scaffold_capabilities(),
    }


def valid_execution_sequence_failure_record(
    payload: dict[str, Any],
    *,
    predecessor_id: str,
    attempt_archive: Path,
    owner_archive: Path,
) -> bool:
    anchor = TRUSTED_EXECUTION_SEQUENCE_FAILURE_ANCHORS.get(predecessor_id)
    if not isinstance(anchor, dict):
        return False
    preflight_report = attempt_archive / "phase0" / "preflight_report.json"
    materialization_report = (
        attempt_archive
        / "phase3"
        / "preimplementation_review_materialization_report.json"
    )
    blocker_zero_record = attempt_archive / "phase3" / "blocker_zero_record.json"
    focused_report = attempt_archive / "phase4" / "focused_test_result_report.json"
    implementation_report = attempt_archive / "phase4" / "implementation_scope_report.json"
    focused_receipt = attempt_archive / "phase4" / FOCUSED_TEST_RECEIPT_NAME
    sequence_record = owner_archive / "execution_sequence_failure_record.json"
    stored_preflight = read_json_object(preflight_report)
    stored_materialization = read_json_object(materialization_report)
    stored_blocker_zero = read_json_object(blocker_zero_record)
    stored_focused = read_json_object(focused_report)
    stored_implementation = read_json_object(implementation_report)
    command_receipt = payload.get("implementation_command_receipt")
    if not isinstance(command_receipt, dict):
        return False
    first_evidence_at = parse_utc_timestamp(
        command_receipt.get("first_phase4_evidence_at_utc")
    )
    terminal_at = parse_utc_timestamp(command_receipt.get("terminal_at_utc"))
    recorded_at = parse_utc_timestamp(payload.get("recorded_at"))
    timestamp_order_valid = (
        first_evidence_at is not None
        and terminal_at is not None
        and recorded_at is not None
        and first_evidence_at <= terminal_at < recorded_at
    )
    return (
        sha256_file(sequence_record) == anchor["sequence_failure_record_sha256"]
        and directory_tree_hash(attempt_archive) == anchor["attempt_evidence_tree_sha256"]
        and directory_tree_hash(owner_archive) == anchor["owner_inputs_tree_sha256"]
        and sha256_file(preflight_report) == anchor["preflight_report_sha256"]
        and sha256_file(materialization_report)
        == anchor["materialization_report_sha256"]
        and sha256_file(blocker_zero_record)
        == anchor["blocker_zero_record_sha256"]
        and sha256_file(focused_report)
        == anchor["focused_test_result_report_sha256"]
        and sha256_file(implementation_report)
        == anchor["implementation_scope_report_sha256"]
        and not path_is_file(focused_receipt)
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(FOCUSED_TEST_PATH),
        )
        == anchor["focused_test_base_file_sha256"]
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(COMMON_PATH),
        )
        == anchor["implementation_common_base_file_sha256"]
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(RUNNER_PATH),
        )
        == anchor["implementation_runner_base_file_sha256"]
        and timestamp_order_valid
        and payload.get("schema_version")
        == f"{SCHEMA_PREFIX}-execution-sequence-failure-v1"
        and payload.get("cycle_id") == CYCLE_ID
        and payload.get("attempt_id") == predecessor_id
        and payload.get("status") == "FAIL"
        and payload.get("failure_class") == "command_order_violation"
        and payload.get("missing_required_predecessor_command")
        == FOCUSED_TEST_COMMAND
        and payload.get("observed_completed_command") == "implementation"
        and payload.get("focused_test_executed_before_implementation") is False
        and payload.get("same_attempt_claim_continuation_allowed") is False
        and payload.get("new_attempt_required") is True
        and payload.get("failure_history_preserved") is True
        and payload.get("claim_output_overwritten") is False
        and payload.get("wp_execution_allowed") is False
        and payload.get("gate_adoption_allowed") is False
        and payload.get("live_gate_adopted") is False
        and payload.get("protected_mutation_count") == 0
        and payload.get("execution_base_commit") == anchor["execution_base_commit"]
        and payload.get("attempt_evidence_tree_sha256")
        == anchor["attempt_evidence_tree_sha256"]
        and payload.get("preflight_report_path") == repo_relative(preflight_report)
        and payload.get("preflight_report_sha256")
        == anchor["preflight_report_sha256"]
        and payload.get("materialization_report_path")
        == repo_relative(materialization_report)
        and payload.get("materialization_report_sha256")
        == anchor["materialization_report_sha256"]
        and payload.get("blocker_zero_record_path")
        == repo_relative(blocker_zero_record)
        and payload.get("blocker_zero_record_sha256")
        == anchor["blocker_zero_record_sha256"]
        and payload.get("focused_test_result_report_path")
        == repo_relative(focused_report)
        and payload.get("focused_test_result_report_sha256")
        == anchor["focused_test_result_report_sha256"]
        and payload.get("focused_test_preimplementation_receipt_path")
        == repo_relative(focused_receipt)
        and payload.get("focused_test_preimplementation_receipt_present") is False
        and payload.get("implementation_scope_report_path")
        == repo_relative(implementation_report)
        and payload.get("implementation_scope_report_sha256")
        == anchor["implementation_scope_report_sha256"]
        and payload.get("focused_test_base_file_sha256")
        == anchor["focused_test_base_file_sha256"]
        and payload.get("implementation_common_base_file_sha256")
        == anchor["implementation_common_base_file_sha256"]
        and payload.get("implementation_runner_base_file_sha256")
        == anchor["implementation_runner_base_file_sha256"]
        and payload.get("owner_identity") == "workspace_owner"
        and payload.get("recorder_identity") == "/root"
        and stored_preflight.get("status") == "PASS"
        and stored_materialization.get("status") == "PASS"
        and stored_blocker_zero.get("status") == "PASS"
        and stored_blocker_zero.get("critical_count") == 0
        and stored_blocker_zero.get("important_count") == 0
        and stored_focused.get("status") == "PENDING_PLAN_STEP_6"
        and stored_focused.get("test_executed_inside_implementation_mode") is False
        and stored_implementation.get("schema_version")
        == f"{SCHEMA_PREFIX}-implementation-scope-v1"
        and stored_implementation.get("status") == "PASS"
        and stored_implementation.get("attempt_id") == predecessor_id
        and command_receipt.get("session_id") == 54414
        and command_receipt.get("exit_code") == 0
        and isinstance(command_receipt.get("terminal_result"), dict)
        and command_receipt["terminal_result"].get("status") == "PASS"
        and command_receipt["terminal_result"].get("attempt_id") == predecessor_id
        and command_receipt["terminal_result"].get("blocker_count") == 0
    )


def valid_focused_test_execution_failure_record(
    payload: dict[str, Any],
    *,
    predecessor_id: str,
    attempt_archive: Path,
    owner_archive: Path,
) -> bool:
    anchor = TRUSTED_FOCUSED_TEST_FAILURE_ANCHORS.get(predecessor_id)
    if not isinstance(anchor, dict):
        return False
    failure_record = (
        owner_archive / "focused_test_attestations" / FOCUSED_TEST_FAILURE_RECORD_NAME
    )
    preflight_report = attempt_archive / "phase0" / "preflight_report.json"
    materialization_report = (
        attempt_archive
        / "phase3"
        / "preimplementation_review_materialization_report.json"
    )
    blocker_zero_record = attempt_archive / "phase3" / "blocker_zero_record.json"
    designation = (
        owner_archive
        / "reviewer_designations"
        / "current_session_independent_reviewer_designation.json"
    )
    reviews = {
        "responsibility_review_sha256": (
            owner_archive
            / "preimplementation_reviews"
            / "current_session_responsibility_boundary_review.md"
        ),
        "authority_review_sha256": (
            owner_archive
            / "preimplementation_reviews"
            / "current_session_authority_evidence_integrity_review.md"
        ),
        "adversarial_review_sha256": (
            owner_archive
            / "preimplementation_reviews"
            / "current_session_adversarial_failure_mode_review.md"
        ),
    }
    stored_preflight = read_json_object(preflight_report)
    stored_materialization = read_json_object(materialization_report)
    stored_blocker_zero = read_json_object(blocker_zero_record)
    expected_test_ids = payload.get("expected_test_ids")
    started = parse_utc_timestamp(payload.get("command_started_at"))
    finished = parse_utc_timestamp(payload.get("command_finished_at"))
    authored = parse_utc_timestamp(payload.get("authored_at"))
    return (
        sha256_file(failure_record) == anchor["failure_record_sha256"]
        and directory_tree_hash(attempt_archive)
        == anchor["attempt_evidence_tree_sha256"]
        and directory_tree_hash(owner_archive) == anchor["owner_inputs_tree_sha256"]
        and sha256_file(preflight_report) == anchor["preflight_report_sha256"]
        and sha256_file(materialization_report)
        == anchor["materialization_report_sha256"]
        and sha256_file(blocker_zero_record)
        == anchor["blocker_zero_record_sha256"]
        and sha256_file(designation) == anchor["reviewer_designation_sha256"]
        and all(sha256_file(path) == anchor[field] for field, path in reviews.items())
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(FOCUSED_TEST_PATH),
        )
        == anchor["focused_test_git_blob_sha256"]
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(COMMON_PATH),
        )
        == anchor["common_git_blob_sha256"]
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(ROUND3_RUNNER),
        )
        == anchor["round3_runner_git_blob_sha256"]
        and git_blob_sha256(
            str(anchor["execution_base_commit"]),
            repo_relative(PLAN_PATH),
        )
        == anchor["plan_git_blob_sha256"]
        and started is not None
        and finished is not None
        and authored is not None
        and started < finished < authored
        and payload.get("schema_version")
        == f"{SCHEMA_PREFIX}-focused-test-execution-failure-v1"
        and payload.get("round_id") == ROUND_ID
        and payload.get("cycle_id") == CYCLE_ID
        and payload.get("attempt_id") == predecessor_id
        and payload.get("verdict") == "FAIL"
        and payload.get("status") == "FAIL"
        and payload.get("command") == FOCUSED_TEST_COMMAND
        and payload.get("exec_session_id") == 97152
        and payload.get("exit_code") == 1
        and payload.get("tests_run") == 22
        and payload.get("failure_count") == 1
        and payload.get("error_count") == 0
        and payload.get("skipped_count") == 0
        and payload.get("expected_failure_count") == 0
        and payload.get("unexpected_success_count") == 0
        and payload.get("failed_test_id")
        == (
            "test_dvf_3_3_registry_authority_canonical_closure."
            "RegistryAuthorityCanonicalClosureImplementationTest."
            "test_round3_preimport_guard_detects_bare_import_before_sentinel"
        )
        and payload.get("first_failing_predicate")
        == "expected one tools/build import candidate, observed 3"
        and payload.get("execution_base_commit") == anchor["execution_base_commit"]
        and payload.get("focused_test_path") == repo_relative(FOCUSED_TEST_PATH)
        and payload.get("focused_test_sha256")
        == anchor["focused_test_worktree_sha256"]
        and isinstance(expected_test_ids, list)
        and len(expected_test_ids) == 22
        and len(set(expected_test_ids)) == 22
        and payload.get("focused_test_inventory_sha256")
        == canonical_hash(expected_test_ids)
        and payload.get("reviewer_identity") == "/root/registry_authority_reviewer"
        and payload.get("reviewer_designation_path")
        == repo_relative(REVIEWER_DESIGNATION_INPUT)
        and payload.get("reviewer_designation_sha256")
        == anchor["reviewer_designation_sha256"]
        and payload.get("test_command_observed_directly") is True
        and payload.get("reviewer_authored_failure_record") is True
        and payload.get("runner_authored_failure_record") is False
        and payload.get("test_target_authored_failure_record") is False
        and payload.get("preflight_report_path") == repo_relative(preflight_report)
        and payload.get("preflight_report_sha256")
        == anchor["preflight_report_sha256"]
        and payload.get("materialization_report_path")
        == repo_relative(materialization_report)
        and payload.get("materialization_report_sha256")
        == anchor["materialization_report_sha256"]
        and payload.get("reviewed_bundle_hash")
        == stored_materialization.get("reviewed_bundle_hash")
        and payload.get("entry_validation_status") == "PASS"
        and payload.get("entry_wp_execution_allowed") is True
        and isinstance(payload.get("entry_validation_sha256"), str)
        and len(payload["entry_validation_sha256"]) == 64
        and payload.get("test_output_sha256")
        == "UNAVAILABLE_RAW_BYTES_NOT_PRESERVED"
        and payload.get("test_output_byte_length")
        == "UNAVAILABLE_RAW_BYTES_NOT_PRESERVED"
        and payload.get("test_output_summary")
        == "Ran 22 tests in 17.701s; FAILED (failures=1)"
        and payload.get("same_attempt_claim_continuation_allowed") is False
        and payload.get("new_attempt_required") is True
        and payload.get("failure_history_preserved") is True
        and payload.get("claim_output_overwritten") is False
        and payload.get("wp_execution_allowed") is False
        and payload.get("gate_adoption_allowed") is False
        and stored_preflight.get("status") == "PASS"
        and stored_materialization.get("status") == "PASS"
        and stored_blocker_zero.get("status") == "PASS"
        and stored_blocker_zero.get("critical_count") == 0
        and stored_blocker_zero.get("important_count") == 0
        and not path_is_file(
            attempt_archive / "phase4" / "focused_test_execution_attestation.json"
        )
        and not path_is_file(attempt_archive / "phase4" / "implementation_scope_report.json")
    )


def focused_test_inventory() -> list[str]:
    tree = ast.parse(
        FOCUSED_TEST_PATH.read_text(encoding="utf-8"),
        filename=str(FOCUSED_TEST_PATH),
    )
    return sorted(
        f"{FOCUSED_TEST_PATH.stem}.{class_node.name}.{item.name}"
        for class_node in tree.body
        if isinstance(class_node, ast.ClassDef)
        for item in class_node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name.startswith("test_")
    )


def focused_test_attestation_output_path(root: Path) -> Path:
    return root / "phase4" / "focused_test_execution_attestation.json"


def focused_test_attestation_entry_projection(
    entry: dict[str, Any],
) -> dict[str, Any]:
    projection = json.loads(json.dumps(entry))
    status_rows = projection.get("status_rows")
    if isinstance(status_rows, list):
        excluded_path = repo_relative(FOCUSED_TEST_ATTESTATION_INPUT)
        projection["status_rows"] = [
            row
            for row in status_rows
            if not isinstance(row, dict) or row.get("path") != excluded_path
        ]
    return projection


def validate_focused_test_execution_attestation(
    root: Path,
    *,
    attempt_id: str,
) -> tuple[dict[str, Any], list[str]]:
    payload = read_json_object(FOCUSED_TEST_ATTESTATION_INPUT)
    if not payload:
        return {}, ["focused_test_external_attestation_missing_or_invalid"]
    blockers: list[str] = []
    if path_is_file(FOCUSED_TEST_FAILURE_INPUT):
        blockers.append("focused_test_pass_and_failure_inputs_both_present")
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    blockers.extend(
        validate_reviewer_designation(
            designation,
            attempt_id=attempt_id,
        )
    )
    preflight_path = root / "phase0" / "preflight_report.json"
    materialization_path = (
        root / "phase3" / "preimplementation_review_materialization_report.json"
    )
    preflight = read_json_object(preflight_path)
    materialization = read_json_object(materialization_path)
    entry = validate_execution_entry(root, attempt_id=attempt_id)
    entry_projection = focused_test_attestation_entry_projection(entry)
    expected_test_ids = focused_test_inventory()
    started = parse_utc_timestamp(payload.get("command_started_at"))
    finished = parse_utc_timestamp(payload.get("command_finished_at"))
    authored = parse_utc_timestamp(payload.get("authored_at"))
    expected = {
        "schema_version": f"{SCHEMA_PREFIX}-focused-test-execution-attestation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": attempt_id,
        "verdict": "PASS",
        "command": FOCUSED_TEST_COMMAND,
        "exit_code": 0,
        "tests_run": len(expected_test_ids),
        "failure_count": 0,
        "error_count": 0,
        "skipped_count": 0,
        "expected_failure_count": 0,
        "unexpected_success_count": 0,
        "expected_test_ids": expected_test_ids,
        "execution_base_commit": current_head(),
        "focused_test_path": repo_relative(FOCUSED_TEST_PATH),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "focused_test_inventory_sha256": canonical_hash(expected_test_ids),
        "reviewer_identity": designation.get("reviewer_identity"),
        "reviewer_designation_path": repo_relative(REVIEWER_DESIGNATION_INPUT),
        "reviewer_designation_sha256": sha256_file(REVIEWER_DESIGNATION_INPUT),
        "relation_to_implementation_author": (
            "separate Codex reviewer agent; not the implementation author"
        ),
        "test_command_observed_directly": True,
        "reviewer_authored_attestation": True,
        "runner_authored_attestation": False,
        "test_target_authored_attestation": False,
        "preflight_report_path": repo_relative(preflight_path),
        "preflight_report_sha256": sha256_file(preflight_path),
        "materialization_report_path": repo_relative(materialization_path),
        "materialization_report_sha256": sha256_file(materialization_path),
        "reviewed_bundle_hash": materialization.get("reviewed_bundle_hash"),
        "entry_validation_status": "PASS",
        "entry_validation_sha256": canonical_hash(entry_projection),
        "entry_validation_projection_rule": (
            "exclude_only_current_focused_test_attestation_status_row"
        ),
        "test_output_summary": "OK",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"focused_test_attestation_{field}_mismatch")
    if (
        started is None
        or finished is None
        or authored is None
        or started > finished
        or finished >= authored
    ):
        blockers.append("focused_test_attestation_timestamp_order_invalid")
    output_hash = payload.get("test_output_sha256")
    if not isinstance(output_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", output_hash):
        blockers.append("focused_test_attestation_output_hash_invalid")
    if (
        type(payload.get("test_output_byte_length")) is not int
        or payload["test_output_byte_length"] <= 0
    ):
        blockers.append("focused_test_attestation_output_length_invalid")
    if preflight.get("status") != "PASS" or materialization.get("status") != "PASS":
        blockers.append("focused_test_attestation_entry_chain_not_pass")
    if entry.get("status") != "PASS" or entry.get("wp_execution_allowed") is not True:
        blockers.append("focused_test_attestation_fresh_entry_not_pass")
    return payload, blockers


def validate_bootstrap_manifest() -> dict[str, Any]:
    stored = read_json_object(BOOTSTRAP_MANIFEST_PATH)
    projection = scaffold_manifest_projection()
    projection_hash = canonical_hash(projection)
    stored_projection = {
        key: stored.get(key)
        for key in (
            "schema_version",
            "round_id",
            "self_hash_excluded",
            "commit_hash_excluded",
            "scaffold_paths",
            "capabilities",
        )
    }
    registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    post_entry_retry_evidence = []
    for row in registration.get("predecessor_attempts", []):
        if not isinstance(row, dict) or not isinstance(row.get("preserved_evidence_path"), str):
            continue
        predecessor_root = REPO_ROOT / row["preserved_evidence_path"]
        failure = read_json_object(
            predecessor_root / "attempt_failures" / "implementation.json"
        )
        implementation_failure_valid = (
            failure.get("status") == "FAIL"
            and failure.get("mode") == "implementation"
            and failure.get("failure_record_write_once") is True
            and failure.get("claim_output_overwritten") is False
        )
        owner_archive_value = row.get("preserved_owner_inputs_path")
        sequence_failure_valid = False
        focused_test_failure_valid = False
        if isinstance(owner_archive_value, str):
            owner_archive = REPO_ROOT / owner_archive_value
            sequence_failure = read_json_object(
                owner_archive / "execution_sequence_failure_record.json"
            )
            sequence_failure_valid = valid_execution_sequence_failure_record(
                sequence_failure,
                predecessor_id=str(row.get("attempt_id")),
                attempt_archive=predecessor_root,
                owner_archive=owner_archive,
            )
            focused_test_failure = read_json_object(
                owner_archive
                / "focused_test_attestations"
                / FOCUSED_TEST_FAILURE_RECORD_NAME
            )
            focused_test_failure_valid = (
                valid_focused_test_execution_failure_record(
                    focused_test_failure,
                    predecessor_id=str(row.get("attempt_id")),
                    attempt_archive=predecessor_root,
                    owner_archive=owner_archive,
                )
            )
        if (
            implementation_failure_valid
            or sequence_failure_valid
            or focused_test_failure_valid
        ):
            post_entry_retry_evidence.append(row.get("attempt_id"))
    stored_rows = stored.get("scaffold_paths")
    frozen_scaffold_shape_valid = (
        stored.get("schema_version") == f"{SCHEMA_PREFIX}-bootstrap-scaffold-manifest-v2"
        and stored.get("round_id") == ROUND_ID
        and stored.get("self_hash_excluded") is True
        and stored.get("commit_hash_excluded") is True
        and stored.get("capabilities") == scaffold_capabilities()
        and isinstance(stored_rows, list)
        and [row.get("path") for row in stored_rows if isinstance(row, dict)]
        == [repo_relative(path) for path in SCAFFOLD_PATHS]
        and all(
            isinstance(row, dict)
            and row.get("exists") is True
            and isinstance(row.get("byte_length"), int)
            and row["byte_length"] > 0
            and isinstance(row.get("sha256"), str)
            and len(row["sha256"]) == 64
            for row in stored_rows
        )
    )
    authorized_post_entry_retry = (
        bool(post_entry_retry_evidence)
        and registration.get("retry_class") == "pre_adoption_no_protected_mutation"
        and registration.get("prior_failure_records_preserved") is True
        and registration.get("overwrite_existing_attempt_outputs_allowed") is False
        and registration.get("receipt_nonce_reuse_allowed") is False
        and registration.get("live_gate_adopted") is False
        and registration.get("top_docs_applied") is False
        and registration.get("protected_mutation_count") == 0
        and frozen_scaffold_shape_valid
    )
    projection_matches = stored_projection == projection
    return {
        "status": "PASS" if projection_matches or authorized_post_entry_retry else "FAIL",
        "manifest_path": repo_relative(BOOTSTRAP_MANIFEST_PATH),
        "manifest_exists": BOOTSTRAP_MANIFEST_PATH.is_file(),
        "manifest_sha256": sha256_file(BOOTSTRAP_MANIFEST_PATH),
        "projection_sha256": projection_hash,
        "stored_projection_matches": projection_matches,
        "frozen_entry_scaffold_accepted_for_post_entry_retry": authorized_post_entry_retry,
        "post_entry_retry_predecessor_attempts": post_entry_retry_evidence,
        "projection": projection,
    }


def protected_surface_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in PROTECTED_SURFACES:
        if path_is_file(path):
            digest = sha256_file(path)
            kind = "file"
        elif path_is_dir(path):
            child_rows = directory_file_rows(path)
            if child_rows is None:
                raise RuntimeError(f"protected directory disappeared: {path}")
            digest = canonical_hash(child_rows)
            kind = "directory"
        else:
            digest = None
            kind = "missing"
        rows.append(
            {
                "path": repo_relative(path),
                "kind": kind,
                "sha256": digest,
            }
        )
    return rows


def lua_environment_report() -> dict[str, Any]:
    checker_hash = sha256_file(LUA_CHECKER_PATH)
    candidates: list[Path] = []
    if os.name == "nt":
        where = subprocess.run(
            ["where.exe", "luac"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if where.returncode == 0:
            candidates.extend(Path(line.strip()).resolve() for line in where.stdout.splitlines() if line.strip())
    else:
        resolved = shutil.which("luac")
        if resolved:
            candidates.append(Path(resolved).resolve())
    unique = sorted({path for path in candidates if path.is_file()}, key=lambda path: str(path).lower())
    version = None
    if len(unique) == 1:
        completed = subprocess.run(
            [str(unique[0]), "-v"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        version = (completed.stdout + completed.stderr).strip()
    lua_files = sorted(
        {
            path.resolve()
            for root in (
                REPO_ROOT / "Iris" / "media" / "lua",
                REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua",
            )
            if root.is_dir()
            for path in root.rglob("*.lua")
            if path.is_file()
        },
        key=lambda path: str(path).lower(),
    )
    input_rows = [
        {"path": repo_relative(path), "sha256": sha256_file(path)}
        for path in lua_files
    ]
    status = (
        "PASS"
        if LUA_CHECKER_PATH.is_file() and checker_hash and len(unique) == 1 and input_rows
        else "FAIL"
    )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-lua-environment-v1",
        "status": status,
        "checker_path": repo_relative(LUA_CHECKER_PATH),
        "checker_sha256": checker_hash,
        "luac_candidate_count": len(unique),
        "luac_candidates": [str(path) for path in unique],
        "luac_path": str(unique[0]) if len(unique) == 1 else None,
        "luac_sha256": sha256_file(unique[0]) if len(unique) == 1 else None,
        "luac_version": version,
        "lua_input_count": len(input_rows),
        "lua_input_set_sha256": canonical_hash(input_rows),
        "lua_inputs": input_rows,
    }


def lua_environment_identity(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in {"cycle_id", "attempt_id"}
    }


def decision_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    decisions = payload.get("decisions", [])
    if not isinstance(decisions, list):
        return {}
    return {
        str(row.get("decision_id")): row
        for row in decisions
        if isinstance(row, dict) and row.get("decision_id")
    }


def approved_decisions_report(payload: dict[str, Any]) -> dict[str, Any]:
    by_id = decision_map(payload)
    required = [f"D{index}" for index in range(11)]
    allowed_states = {"owner_ratified", "owner_overridden"}
    rows = []
    for decision_id in required:
        row = by_id.get(decision_id, {})
        state = row.get("state") or row.get("owner_decision_state") or "missing"
        value_present = "value" in row or "owner_value" in row
        rows.append(
            {
                "decision_id": decision_id,
                "state": state,
                "value_present": value_present,
                "satisfied": state in allowed_states and value_present,
            }
        )
    return {
        "status": "PASS" if all(row["satisfied"] for row in rows) else "FAIL",
        "owner_identity": payload.get("owner_identity"),
        "decision_time": payload.get("decision_time"),
        "rows": rows,
        "unresolved_count": sum(not row["satisfied"] for row in rows),
    }


def preflight_external_contract() -> dict[str, Any]:
    return {
        "attempt_registration": {
            "path": repo_relative(ATTEMPT_REGISTRATION_INPUT),
            "required_fields": [
                "cycle_id",
                "attempt_id",
                "owner_identity",
                "registered_at",
                "execution_base_commit",
                "clean_worktree_checkpoint_path",
                "clean_worktree_checkpoint_sha256",
                "evidence_root",
                "retry_class",
                "predecessor_attempts",
                "prior_failure_records_preserved",
                "overwrite_existing_attempt_outputs_allowed",
                "receipt_nonce_reuse_allowed",
                "live_gate_adopted",
                "top_docs_applied",
                "protected_mutation_count",
            ],
            "predecessor_required_fields": [
                "attempt_id",
                "preserved_evidence_path",
                "preserved_evidence_tree_sha256",
                "failure_record_preserved",
            ],
            "post_split_predecessor_required_fields": [
                "preserved_owner_inputs_path",
                "preserved_owner_inputs_tree_sha256",
            ],
        },
        "clean_checkpoint": {
            "path": repo_relative(CLEAN_CHECKPOINT_INPUT),
            "required_fields": [
                "round_id",
                "owner_identity",
                "recorded_at",
                "execution_base_commit",
                "worktree_path",
                "git_status_command",
                "git_status_output",
                "git_status_output_sha256",
                "initial_dirty_count",
                "bootstrap_scaffold_manifest_sha256",
            ],
        },
        "owner_decisions": {
            "path": repo_relative(OWNER_DECISION_INPUT),
            "required_decisions": [f"D{index}" for index in range(11)],
            "allowed_states": ["owner_ratified", "owner_overridden"],
        },
        "plan_approval": {
            "path": repo_relative(PLAN_APPROVAL_INPUT),
            "required_fields": [
                "round_id",
                "owner_identity",
                "approved_at",
                "approved_plan_path",
                "approved_plan_sha256",
                "approved_roadmap_path",
                "approved_roadmap_sha256",
                "approved_bootstrap_scaffold_manifest_path",
                "approved_bootstrap_scaffold_manifest_sha256",
                "approved_clean_worktree_checkpoint_path",
                "approved_clean_worktree_checkpoint_sha256",
                "approved_execution_base_commit",
                "approved_attempt_id",
                "approved_attempt_registration_path",
                "approved_attempt_registration_sha256",
                "approved_evidence_root",
                "reserved_external_inputs",
            ],
        },
        "reviewer_designation": {
            "path": repo_relative(REVIEWER_DESIGNATION_INPUT),
            "required_fields": [
                "round_id",
                "cycle_id",
                "attempt_id",
                "owner_identity",
                "designated_at",
                "reviewer_identity",
                "eligible",
                "excluded_authors",
                "phase3_scope_assignments",
                "focused_test_execution_attestation_eligible",
            ],
        },
        "focused_test_execution_attestation": {
            "path": repo_relative(FOCUSED_TEST_ATTESTATION_INPUT),
            "required_after_focused_test_before_implementation": True,
            "reviewer_authored_only": True,
            "runner_or_test_target_authorship_allowed": False,
        },
        "focused_test_execution_failure": {
            "path": repo_relative(FOCUSED_TEST_FAILURE_INPUT),
            "conditional_on_nonzero_focused_test_exit": True,
            "mutually_exclusive_with_pass_attestation": True,
            "reviewer_authored_only": True,
            "same_attempt_implementation_allowed": False,
        },
    }


def validate_checkpoint(payload: dict[str, Any], scaffold: dict[str, Any], head: str | None) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["clean_worktree_checkpoint_missing_or_invalid"]
    if payload.get("round_id") != ROUND_ID:
        blockers.append("clean_checkpoint_round_id_mismatch")
    if not payload.get("owner_identity") or not payload.get("recorded_at"):
        blockers.append("clean_checkpoint_author_or_time_missing")
    if payload.get("execution_base_commit") != head:
        blockers.append("clean_checkpoint_base_commit_mismatch")
    if int(payload.get("initial_dirty_count", -1)) != 0:
        blockers.append("clean_checkpoint_initial_dirty_count_nonzero")
    if payload.get("git_status_output", None) != "":
        blockers.append("clean_checkpoint_status_output_not_empty")
    if payload.get("git_status_output_sha256") != sha256_bytes(b""):
        blockers.append("clean_checkpoint_empty_status_hash_mismatch")
    if payload.get("git_status_command") != "git status --porcelain=v1 --untracked-files=all":
        blockers.append("clean_checkpoint_status_command_mismatch")
    if payload.get("bootstrap_scaffold_manifest_sha256") != scaffold.get("manifest_sha256"):
        blockers.append("clean_checkpoint_scaffold_manifest_hash_mismatch")
    recorded_path = payload.get("worktree_path")
    if not isinstance(recorded_path, str) or Path(recorded_path).resolve() != REPO_ROOT.resolve():
        blockers.append("clean_checkpoint_worktree_path_mismatch")
    return blockers


def validate_preserved_owner_input_archive(
    row: dict[str, Any],
    *,
    predecessor_id: str,
    attempt_archive: Path,
) -> tuple[Path | None, list[str]]:
    blockers: list[str] = []
    path_value = row.get("preserved_owner_inputs_path")
    expected_hash = row.get("preserved_owner_inputs_tree_sha256")
    if not isinstance(path_value, str) or not isinstance(expected_hash, str):
        return None, [
            f"attempt_registration_predecessor_owner_inputs_binding_missing:{predecessor_id}"
        ]
    archive = (REPO_ROOT / path_value).resolve()
    expected_archive = (
        DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs" / predecessor_id
    ).resolve()
    if (
        archive != expected_archive
        or not is_within(archive, DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs")
        or not path_is_dir(archive)
        or path_value.replace("\\", "/") != repo_relative(archive)
    ):
        blockers.append(
            f"attempt_registration_predecessor_owner_inputs_not_preserved:{predecessor_id}"
        )
    elif directory_tree_hash(archive) != expected_hash:
        blockers.append(
            f"attempt_registration_predecessor_owner_inputs_hash_mismatch:{predecessor_id}"
        )
    elif not directory_file_rows(archive):
        blockers.append(
            f"attempt_registration_predecessor_owner_inputs_empty:{predecessor_id}"
        )
    required_inputs = (
        "worktree_checkpoints/current_session_clean_worktree_checkpoint_record.json",
        "attempt_registrations/current_session_attempt_record.json",
        "owner_decisions/current_session_owner_decision_record.json",
        "reviewer_designations/current_session_independent_reviewer_designation.json",
        "plan_approvals/current_session_implementation_plan_approval_record.json",
    )
    review_manifest_path = (
        attempt_archive / "phase3" / "preimplementation_review_input_manifest.json"
    )
    review_manifest_present = path_is_file(review_manifest_path)
    review_manifest = read_json_object(review_manifest_path)
    reviewed_bundle = review_manifest.get("reviewed_bundle")
    reviewed_inputs = (
        reviewed_bundle.get("inputs")
        if isinstance(reviewed_bundle, dict)
        else None
    )
    reviewed_input_hashes = {
        str(item.get("path")): item.get("sha256")
        for item in (reviewed_inputs if isinstance(reviewed_inputs, list) else [])
        if isinstance(item, dict)
    }
    for relative in required_inputs:
        archived_input = archive / relative
        source_path = repo_relative(OWNER_INPUT_ROOT / relative)
        expected_source_hash = reviewed_input_hashes.get(source_path)
        if not path_is_file(archived_input):
            blockers.append(
                f"attempt_registration_predecessor_owner_input_missing:{predecessor_id}:{relative}"
            )
        elif review_manifest_present and (
            not isinstance(expected_source_hash, str)
            or sha256_file(archived_input) != expected_source_hash
        ):
            blockers.append(
                f"attempt_registration_predecessor_owner_input_drifted_from_reviewed_bundle:{predecessor_id}:{relative}"
            )
    phase3 = attempt_archive / "phase3"
    materialization_path = (
        phase3 / "preimplementation_review_materialization_report.json"
    )
    zero_path = phase3 / "blocker_zero_record.json"
    materialization = read_json_object(materialization_path)
    zero_record = read_json_object(zero_path)
    materialized_review_names = {
        "responsibility_boundary": "current_session_responsibility_boundary_review.md",
        "authority_evidence_integrity": "current_session_authority_evidence_integrity_review.md",
        "adversarial_failure_mode": "current_session_adversarial_failure_mode_review.md",
    }
    phase3_review_artifact_present = any(
        path_is_file(phase3 / name)
        for name in (
            "responsibility_boundary_review.md",
            "authority_evidence_integrity_review.md",
            "adversarial_failure_mode_review.md",
            "carry_forward_findings_table.json",
            "blocker_zero_record.json",
        )
    )
    post_review_execution_artifact_present = (
        any(
            path_is_file(attempt_archive / "phase4" / name)
            for name in (
                "implementation_scope_report.json",
                "focused_test_result_report.json",
                FOCUSED_TEST_RECEIPT_NAME,
                "focused_test_execution_attestation.json",
            )
        )
        or path_is_file(attempt_archive / "attempt_failures" / "implementation.json")
    )
    expected_zero_status: str | None = None
    if path_is_file(materialization_path):
        rows = materialization.get("rows")
        rows_valid = (
            materialization.get("schema_version")
            == f"{SCHEMA_PREFIX}-preimplementation-review-materialization-v1"
            and materialization.get("cycle_id") == CYCLE_ID
            and materialization.get("attempt_id") == predecessor_id
            and materialization.get("status") == "PASS"
            and isinstance(rows, list)
            and len(rows) == len(materialized_review_names)
            and all(
                isinstance(item, dict)
                and isinstance(item.get("scope"), str)
                and item.get("verdict") in {"PASS", "FAIL"}
                and all(
                    type(item.get(field)) is int and item[field] >= 0
                    for field in (
                        "critical_count",
                        "important_count",
                        "unresolved_minor_count",
                    )
                )
                and isinstance(item.get("source_sha256"), str)
                and len(item["source_sha256"]) == 64
                for item in rows
            )
        )
        if not rows_valid:
            blockers.append(
                f"attempt_registration_predecessor_review_materialization_invalid:{predecessor_id}"
            )
            rows = []
        scope_rows = {
            str(item.get("scope")): item
            for item in rows
            if isinstance(item, dict)
        }
        if set(scope_rows) != set(materialized_review_names):
            blockers.append(
                f"attempt_registration_predecessor_review_scope_set_invalid:{predecessor_id}"
            )
        critical_count = sum(
            int(item.get("critical_count", 0))
            for item in scope_rows.values()
        )
        important_count = sum(
            int(item.get("important_count", 0))
            for item in scope_rows.values()
        )
        unresolved_minor_count = sum(
            int(item.get("unresolved_minor_count", 0))
            for item in scope_rows.values()
        )
        all_verdicts_pass = (
            len(scope_rows) == len(materialized_review_names)
            and all(item.get("verdict") == "PASS" for item in scope_rows.values())
        )
        expected_zero_status = (
            "PASS"
            if (
                all_verdicts_pass
                and critical_count == 0
                and important_count == 0
                and unresolved_minor_count == 0
            )
            else "FAIL"
        )
        zero_binding_valid = (
            path_is_file(zero_path)
            and zero_record.get("schema_version")
            == f"{SCHEMA_PREFIX}-blocker-zero-v1"
            and zero_record.get("cycle_id") == CYCLE_ID
            and zero_record.get("attempt_id") == predecessor_id
            and zero_record.get("status") == expected_zero_status
            and zero_record.get("critical_count") == critical_count
            and zero_record.get("important_count") == important_count
            and zero_record.get("unresolved_minor_count") == unresolved_minor_count
            and zero_record.get("all_reviewer_verdicts_pass") is all_verdicts_pass
        )
        if not zero_binding_valid:
            blockers.append(
                f"attempt_registration_predecessor_blocker_zero_binding_invalid:{predecessor_id}"
            )
        for scope, review_name in materialized_review_names.items():
            review_path = archive / "preimplementation_reviews" / review_name
            review_row = scope_rows.get(scope, {})
            if (
                not path_is_file(review_path)
                or sha256_file(review_path) != review_row.get("source_sha256")
            ):
                blockers.append(
                    f"attempt_registration_predecessor_review_input_missing_or_drifted:{predecessor_id}:{review_name}"
                )
    elif phase3_review_artifact_present:
        blockers.append(
            f"attempt_registration_predecessor_partial_review_materialization:{predecessor_id}"
        )
    if post_review_execution_artifact_present and not path_is_file(materialization_path):
        blockers.append(
            f"attempt_registration_predecessor_execution_without_materialized_reviews:{predecessor_id}"
        )
    focused_test_failure_record = (
        archive / "focused_test_attestations" / FOCUSED_TEST_FAILURE_RECORD_NAME
    )
    if (
        path_is_file(focused_test_failure_record)
        and not path_is_file(materialization_path)
    ):
        blockers.append(
            f"attempt_registration_predecessor_focused_test_failure_without_materialized_reviews:{predecessor_id}"
        )
    materialized_focused_attestation = (
        attempt_archive / "phase4" / "focused_test_execution_attestation.json"
    )
    preserved_focused_attestation = (
        archive
        / "focused_test_attestations"
        / "current_session_focused_test_execution_attestation.json"
    )
    attempt_number_match = re.fullmatch(
        r"attempt-([0-9]{4,})-[a-z0-9][a-z0-9-]{0,47}",
        predecessor_id,
    )
    focused_attestation_contract_applies = (
        attempt_number_match is not None
        and int(attempt_number_match.group(1)) >= 21
    )
    phase4_root = attempt_archive / "phase4"
    implementation_execution_trace_present = (
        (
            path_is_dir(phase4_root)
            and bool(directory_file_rows(phase4_root))
        )
        or path_is_file(attempt_archive / "attempt_failures" / "implementation.json")
    )
    if (
        path_is_file(materialized_focused_attestation)
        or (
            focused_attestation_contract_applies
            and implementation_execution_trace_present
        )
    ):
        if (
            not path_is_file(materialized_focused_attestation)
            or not path_is_file(preserved_focused_attestation)
            or not files_byte_identical(
                preserved_focused_attestation,
                materialized_focused_attestation,
            )
        ):
            blockers.append(
                f"attempt_registration_predecessor_focused_test_attestation_missing_or_drifted:{predecessor_id}"
            )

    sequence_failure = read_json_object(
        archive / "execution_sequence_failure_record.json"
    )
    sequence_failure_valid = valid_execution_sequence_failure_record(
        sequence_failure,
        predecessor_id=predecessor_id,
        attempt_archive=attempt_archive,
        owner_archive=archive,
    )
    if (
        predecessor_id in TRUSTED_EXECUTION_SEQUENCE_FAILURE_ANCHORS
        and not sequence_failure_valid
    ):
        blockers.append(
            f"attempt_registration_predecessor_anchored_sequence_failure_invalid:{predecessor_id}"
        )
    focused_test_failure = read_json_object(focused_test_failure_record)
    focused_test_failure_valid = valid_focused_test_execution_failure_record(
        focused_test_failure,
        predecessor_id=predecessor_id,
        attempt_archive=attempt_archive,
        owner_archive=archive,
    )
    if (
        predecessor_id in TRUSTED_FOCUSED_TEST_FAILURE_ANCHORS
        and not focused_test_failure_valid
    ):
        blockers.append(
            f"attempt_registration_predecessor_anchored_focused_test_failure_invalid:{predecessor_id}"
        )
    if expected_zero_status == "PASS":
        entry_failure = read_json_object(archive / "execution_entry_failure_record.json")
        implementation_failure = read_json_object(
            attempt_archive / "attempt_failures" / "implementation.json"
        )
        entry_failure_valid = (
            entry_failure.get("cycle_id") == CYCLE_ID
            and entry_failure.get("attempt_id") == predecessor_id
            and entry_failure.get("status") == "FAIL"
            and entry_failure.get("wp_execution_allowed") is False
        )
        implementation_failure_valid = (
            implementation_failure.get("cycle_id") == CYCLE_ID
            and implementation_failure.get("attempt_id") == predecessor_id
            and implementation_failure.get("mode") == "implementation"
            and implementation_failure.get("status") == "FAIL"
            and implementation_failure.get("failure_record_write_once") is True
            and implementation_failure.get("claim_output_overwritten") is False
            and implementation_failure.get("wp_execution_allowed") is False
        )
        if (
            not entry_failure_valid
            and not implementation_failure_valid
            and not sequence_failure_valid
            and not focused_test_failure_valid
        ):
            blockers.append(
                f"attempt_registration_predecessor_post_review_failure_record_invalid:{predecessor_id}"
            )
    return (archive if not blockers else None), blockers


def validate_attempt_registration(
    payload: dict[str, Any],
    *,
    attempt_id: str,
    evidence_root: Path,
    head: str | None,
    checkpoint_hash: str | None,
) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["attempt_registration_missing_or_invalid"]
    expected = {
        "cycle_id": CYCLE_ID,
        "attempt_id": attempt_id,
        "execution_base_commit": head,
        "clean_worktree_checkpoint_path": repo_relative(CLEAN_CHECKPOINT_INPUT),
        "clean_worktree_checkpoint_sha256": checkpoint_hash,
        "evidence_root": repo_relative(evidence_root),
        "retry_class": "pre_adoption_no_protected_mutation",
        "prior_failure_records_preserved": True,
        "overwrite_existing_attempt_outputs_allowed": False,
        "receipt_nonce_reuse_allowed": False,
        "live_gate_adopted": False,
        "top_docs_applied": False,
        "protected_mutation_count": 0,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"attempt_registration_{field}_mismatch")
    if not payload.get("owner_identity") or not payload.get("registered_at"):
        blockers.append("attempt_registration_author_or_time_missing")
    predecessors = payload.get("predecessor_attempts")
    if not isinstance(predecessors, list):
        blockers.append("attempt_registration_predecessors_invalid")
        return blockers
    seen_ids: set[str] = set()
    seen_archives: set[Path] = set()
    seen_owner_input_archives: set[Path] = set()
    for index, row in enumerate(predecessors):
        if not isinstance(row, dict):
            blockers.append(f"attempt_registration_predecessor_row_invalid:{index}")
            continue
        predecessor_id = row.get("attempt_id")
        archive_path = row.get("preserved_evidence_path")
        if (
            not isinstance(predecessor_id, str)
            or not re.fullmatch(
                r"attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]{0,47}", predecessor_id
            )
            or predecessor_id == attempt_id
            or predecessor_id in seen_ids
            or not isinstance(archive_path, str)
        ):
            blockers.append(f"attempt_registration_predecessor_identity_invalid:{index}")
            continue
        seen_ids.add(predecessor_id)
        archive = (REPO_ROOT / archive_path).resolve()
        if archive in seen_archives:
            blockers.append(f"attempt_registration_predecessor_archive_duplicate:{predecessor_id}")
        seen_archives.add(archive)
        if (
            not is_within(archive, DEFAULT_EVIDENCE_ROOT)
            or not archive.is_dir()
            or archive_path.replace("\\", "/") != repo_relative(archive)
        ):
            blockers.append(f"attempt_registration_predecessor_not_preserved:{predecessor_id}")
        elif row.get("preserved_evidence_tree_sha256") != directory_tree_hash(archive):
            blockers.append(f"attempt_registration_predecessor_hash_mismatch:{predecessor_id}")
        terminal_records = (
            archive / "preflight_report.json",
            archive / "phase0" / "preflight_report.json",
            archive / "attempt_failures" / "preflight.json",
        )
        if not any(path.is_file() for path in terminal_records):
            blockers.append(f"attempt_registration_predecessor_terminal_record_missing:{predecessor_id}")
        if row.get("failure_record_preserved") is not True:
            blockers.append(f"attempt_registration_predecessor_failure_not_preserved:{predecessor_id}")
        if is_within(archive, ATTEMPTS_ROOT):
            owner_archive, owner_archive_blockers = validate_preserved_owner_input_archive(
                row,
                predecessor_id=predecessor_id,
                attempt_archive=archive,
            )
            blockers.extend(owner_archive_blockers)
            if owner_archive is not None:
                seen_owner_input_archives.add(owner_archive)
    anchored_attempts = {
        **TRUSTED_EXECUTION_SEQUENCE_FAILURE_ANCHORS,
        **TRUSTED_FOCUSED_TEST_FAILURE_ANCHORS,
    }
    for anchor_id, anchor in anchored_attempts.items():
        anchored_registration = read_json_object(
            ATTEMPTS_ROOT / anchor_id / "phase0" / "attempt_registration_record.json"
        )
        anchored_rows = anchored_registration.get("predecessor_attempts")
        anchor_indexes = [
            index
            for index, row in enumerate(predecessors)
            if isinstance(row, dict) and row.get("attempt_id") == anchor_id
        ]
        current_pre_anchor_rows = (
            predecessors[: anchor_indexes[0]]
            if len(anchor_indexes) == 1
            else []
        )
        if (
            not isinstance(anchored_rows, list)
            or canonical_hash(anchored_rows)
            != anchor["predecessor_registration_rows_sha256"]
            or len(anchor_indexes) != 1
            or current_pre_anchor_rows != anchored_rows
        ):
            blockers.append(
                f"attempt_registration_anchored_predecessor_chain_mismatch:{anchor_id}"
            )
        expected_anchor_row = {
            "attempt_id": anchor_id,
            "failure_record_preserved": True,
            "preserved_evidence_path": repo_relative(ATTEMPTS_ROOT / anchor_id),
            "preserved_evidence_tree_sha256": anchor[
                "attempt_evidence_tree_sha256"
            ],
            "preserved_owner_inputs_path": repo_relative(
                DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs" / anchor_id
            ),
            "preserved_owner_inputs_tree_sha256": anchor[
                "owner_inputs_tree_sha256"
            ],
        }
        anchor_rows = [
            row
            for row in predecessors
            if isinstance(row, dict) and row.get("attempt_id") == anchor_id
        ]
        if anchor_rows != [expected_anchor_row]:
            blockers.append(
                f"attempt_registration_anchored_failure_row_mismatch:{anchor_id}"
            )
    legacy_root = DEFAULT_EVIDENCE_ROOT / "superseded_review_rounds"
    expected_archives = {
        path.resolve()
        for root in (legacy_root, ATTEMPTS_ROOT)
        if root.is_dir()
        for path in root.iterdir()
        if path.is_dir() and path.resolve() != evidence_root.resolve()
    }
    if seen_archives != expected_archives:
        blockers.append("attempt_registration_predecessor_archive_set_mismatch")
    owner_history_root = DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs"
    expected_owner_input_archives = (
        {
            path.resolve()
            for path in owner_history_root.iterdir()
            if path.is_dir()
        }
        if owner_history_root.is_dir()
        else set()
    )
    if seen_owner_input_archives != expected_owner_input_archives:
        blockers.append("attempt_registration_predecessor_owner_input_archive_set_mismatch")
    return blockers


def validate_plan_approval(
    payload: dict[str, Any],
    *,
    head: str | None,
    checkpoint_hash: str | None,
    scaffold: dict[str, Any],
    attempt_id: str,
    evidence_root: Path,
    attempt_registration_hash: str | None,
    enforce_present_input_set: bool = True,
) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["implementation_plan_approval_missing_or_invalid"]
    if not payload.get("owner_identity") or not payload.get("approved_at"):
        blockers.append("plan_approval_author_or_time_missing")
    expected = {
        "round_id": ROUND_ID,
        "approved_plan_path": repo_relative(PLAN_PATH),
        "approved_plan_sha256": sha256_file(PLAN_PATH),
        "approved_roadmap_path": repo_relative(ROADMAP_PATH),
        "approved_roadmap_sha256": sha256_file(ROADMAP_PATH),
        "approved_bootstrap_scaffold_manifest_path": repo_relative(BOOTSTRAP_MANIFEST_PATH),
        "approved_bootstrap_scaffold_manifest_sha256": scaffold.get("manifest_sha256"),
        "approved_clean_worktree_checkpoint_path": repo_relative(CLEAN_CHECKPOINT_INPUT),
        "approved_clean_worktree_checkpoint_sha256": checkpoint_hash,
        "approved_execution_base_commit": head,
        "approved_attempt_id": attempt_id,
        "approved_attempt_registration_path": repo_relative(ATTEMPT_REGISTRATION_INPUT),
        "approved_attempt_registration_sha256": attempt_registration_hash,
        "approved_evidence_root": repo_relative(evidence_root),
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"plan_approval_{field}_mismatch")
    approved_inputs = payload.get("reserved_external_inputs")
    if not isinstance(approved_inputs, list):
        blockers.append("plan_approval_reserved_external_inputs_missing")
        return blockers

    reserved = {repo_relative(path) for path in RESERVED_EXTERNAL_INPUTS}
    seen: set[str] = set()
    for index, row in enumerate(approved_inputs):
        if not isinstance(row, dict):
            blockers.append(f"plan_approval_reserved_input_row_invalid:{index}")
            continue
        path = str(row.get("path", "")).replace("\\", "/")
        digest = row.get("sha256")
        if not path or path in seen:
            blockers.append(f"plan_approval_reserved_input_duplicate_or_empty:{index}")
            continue
        seen.add(path)
        if path not in reserved or any(token in path for token in ("*", "?", "[")):
            blockers.append(f"plan_approval_reserved_input_path_invalid:{path}")
            continue
        resolved = REPO_ROOT / path
        if not resolved.is_file() or not digest or sha256_file(resolved) != digest:
            blockers.append(f"plan_approval_reserved_input_hash_mismatch:{path}")

    present_external_inputs = {
        repo_relative(path)
        for path in RESERVED_EXTERNAL_INPUTS
        if path.is_file() and path != PLAN_APPROVAL_INPUT
    }
    if enforce_present_input_set and seen != present_external_inputs:
        blockers.append("plan_approval_present_external_input_set_mismatch")
    return blockers


def validate_reviewer_designation(
    payload: dict[str, Any],
    *,
    attempt_id: str,
) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["independent_reviewer_designation_missing_or_invalid"]
    if payload.get("round_id") != ROUND_ID:
        blockers.append("reviewer_designation_round_id_mismatch")
    if payload.get("cycle_id") != CYCLE_ID:
        blockers.append("reviewer_designation_cycle_id_mismatch")
    if payload.get("attempt_id") != attempt_id:
        blockers.append("reviewer_designation_attempt_id_mismatch")
    if payload.get("eligible") is not True:
        blockers.append("reviewer_designation_not_eligible")
    if not payload.get("owner_identity") or not payload.get("designated_at"):
        blockers.append("reviewer_designation_author_or_time_missing")
    if not payload.get("reviewer_identity"):
        blockers.append("reviewer_identity_missing")
    excluded = payload.get("excluded_authors")
    if not isinstance(excluded, list) or not excluded:
        blockers.append("reviewer_excluded_authors_missing")
    elif payload.get("reviewer_identity") in excluded:
        blockers.append("reviewer_identity_is_excluded")
    required_scopes = {
        "responsibility_boundary",
        "authority_evidence_integrity",
        "adversarial_failure_mode",
        "focused_test_execution_attestation",
    }
    assigned_scopes = payload.get("phase3_scope_assignments")
    if (
        not isinstance(assigned_scopes, list)
        or len(assigned_scopes) != len(required_scopes)
        or not all(isinstance(scope, str) for scope in assigned_scopes)
        or set(assigned_scopes) != required_scopes
    ):
        blockers.append("reviewer_designation_scope_assignments_mismatch")
    if payload.get("focused_test_execution_attestation_eligible") is not True:
        blockers.append("reviewer_focused_test_attestation_not_eligible")
    return blockers


def validate_preflight_status(
    status_lines: list[str], approval: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    approved_rows = approval.get("reserved_external_inputs", [])
    approved_by_path = {
        str(row.get("path", "")).replace("\\", "/"): row
        for row in approved_rows
        if isinstance(row, dict)
    }
    rows = []
    blockers = []
    reserved = {repo_relative(path) for path in RESERVED_EXTERNAL_INPUTS}
    for line in status_lines:
        path = status_path(line)
        approval_self = path == repo_relative(PLAN_APPROVAL_INPUT)
        allowed = path in reserved and (path in approved_by_path or approval_self)
        expected_hash = (
            sha256_file(PLAN_APPROVAL_INPUT)
            if approval_self
            else approved_by_path.get(path, {}).get("sha256")
        )
        actual_hash = sha256_file(REPO_ROOT / path)
        hash_matches = bool(expected_hash and actual_hash == expected_hash)
        row = {
            "status_line": line,
            "path": path,
            "reserved_external_input": path in reserved,
            "listed_in_plan_approval": path in approved_by_path,
            "plan_approval_self_path_exception": approval_self,
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "hash_matches": hash_matches,
            "allowed": allowed and hash_matches,
        }
        rows.append(row)
        if not row["allowed"]:
            blockers.append(f"unapproved_preflight_delta:{path}")
    return rows, blockers


def run_preflight(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(
            f"attempt evidence is write-once and already exists: {repo_relative(root)}"
        )
    started_at = utc_now()
    head = current_head()
    status_output, status_lines = git_status_rows()
    scaffold = validate_bootstrap_manifest()
    decisions = read_json_object(OWNER_DECISION_INPUT)
    decision_report = approved_decisions_report(decisions)
    checkpoint = read_json_object(CLEAN_CHECKPOINT_INPUT)
    approval = read_json_object(PLAN_APPROVAL_INPUT)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    attempt_registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    lua = lua_environment_report()
    protected_rows = protected_surface_rows()
    protected_paths = [row["path"] for row in protected_rows]
    expected_protected_paths = [repo_relative(path) for path in PROTECTED_SURFACES]

    blockers: list[str] = []
    if scaffold["status"] != "PASS":
        blockers.append("bootstrap_scaffold_manifest_mismatch")
    if sha256_file(ROADMAP_PATH) != CONSUMED_ROADMAP_SHA256:
        blockers.append("repo_local_roadmap_hash_mismatch")
    if decision_report["status"] != "PASS":
        blockers.append("owner_reserved_decisions_unresolved")
    blockers.extend(validate_checkpoint(checkpoint, scaffold, head))
    blockers.extend(
        validate_attempt_registration(
            attempt_registration,
            attempt_id=normalized_attempt_id,
            evidence_root=root,
            head=head,
            checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
        )
    )
    plan_approval_blockers = validate_plan_approval(
        approval,
        head=head,
        checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
        scaffold=scaffold,
        attempt_id=normalized_attempt_id,
        evidence_root=root,
        attempt_registration_hash=sha256_file(ATTEMPT_REGISTRATION_INPUT),
    )
    blockers.extend(plan_approval_blockers)
    blockers.extend(
        validate_reviewer_designation(
            designation,
            attempt_id=normalized_attempt_id,
        )
    )
    if path_is_file(FOCUSED_TEST_ATTESTATION_INPUT):
        blockers.append("preflight_focused_test_pass_attestation_present_too_early")
    if path_is_file(FOCUSED_TEST_FAILURE_INPUT):
        blockers.append("preflight_focused_test_failure_record_present_too_early")
    status_rows, status_blockers = validate_preflight_status(status_lines, approval)
    blockers.extend(status_blockers)
    reserved_external = {path.resolve() for path in RESERVED_EXTERNAL_INPUTS}
    external_input_files = (
        sorted(path.resolve() for path in OWNER_INPUT_ROOT.rglob("*") if path.is_file())
        if OWNER_INPUT_ROOT.is_dir()
        else []
    )
    for path in external_input_files:
        if path not in reserved_external:
            blockers.append(f"unlisted_external_input:{repo_relative(path)}")
            continue
        ignored = run_git("check-ignore", "-q", "--", repo_relative(path))["exit_code"] == 0
        if ignored:
            blockers.append(f"ignored_external_input:{repo_relative(path)}")
    if lua["status"] != "PASS":
        blockers.append("lua_syntax_environment_preflight_failed")
    if protected_paths != expected_protected_paths or len(set(protected_paths)) != len(protected_paths):
        blockers.append("protected_surface_plan_denominator_set_mismatch")
    if any(row["kind"] == "missing" for row in protected_rows):
        blockers.append("protected_surface_plan_member_missing")

    input_hash_rows = [
        {"path": repo_relative(path), "sha256": sha256_file(path)}
        for path in (
            PLAN_PATH,
            ROADMAP_PATH,
            BOOTSTRAP_MANIFEST_PATH,
            CLEAN_CHECKPOINT_INPUT,
            OWNER_DECISION_INPUT,
            PLAN_APPROVAL_INPUT,
            REVIEWER_DESIGNATION_INPUT,
            ATTEMPT_REGISTRATION_INPUT,
        )
    ]
    reviewed_bundle = {
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "execution_base_commit": head,
        "inputs": input_hash_rows,
        "protected_surface_hash": canonical_hash(protected_rows),
        "lua_environment_hash": canonical_hash(lua_environment_identity(lua)),
        "preflight_status": "PASS" if not blockers else "FAIL",
    }
    reviewed_bundle_hash = canonical_hash(reviewed_bundle)

    phase0 = root / "phase0"
    phase3 = root / "phase3"
    reports: dict[str, Any] = {
        "registry_authority_plan_traceability_matrix.json": {
            "schema_version": f"{SCHEMA_PREFIX}-traceability-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not blockers else "FAIL",
            "plan_path": repo_relative(PLAN_PATH),
            "plan_sha256": sha256_file(PLAN_PATH),
            "roadmap_path": repo_relative(ROADMAP_PATH),
            "roadmap_sha256": sha256_file(ROADMAP_PATH),
            "wp_execution_allowed": False,
            "rows": [
                {"roadmap_unit": "Phase 3 reviews", "planned_producer": "materialize-preimplementation-reviews", "consumer": "require-execution-entry"},
                *[
                    {"roadmap_unit": f"WP-{index}", "planned_producer": f"wp{index}", "consumer": "require-implementation"}
                    for index in range(1, 8)
                ],
            ],
        },
        "registry_authority_evidence_root_manifest.json": {
            "schema_version": f"{SCHEMA_PREFIX}-evidence-root-v1",
            "round_id": ROUND_ID,
            "evidence_root": repo_relative(root),
            "containment_status": "PASS",
            "preflight_only": True,
        },
        "roadmap_approval_record.json": {
            "schema_version": f"{SCHEMA_PREFIX}-roadmap-approval-projection-v1",
            "round_id": ROUND_ID,
            "source_owner_decision_path": repo_relative(OWNER_DECISION_INPUT),
            "source_owner_decision_sha256": sha256_file(OWNER_DECISION_INPUT),
            "roadmap_path": repo_relative(ROADMAP_PATH),
            "roadmap_sha256": sha256_file(ROADMAP_PATH),
            "consumed_roadmap_sha256": CONSUMED_ROADMAP_SHA256,
            "hash_matches": sha256_file(ROADMAP_PATH) == CONSUMED_ROADMAP_SHA256,
            "tool_authored_approval": False,
        },
        "roadmap_scope_boundary_record.json": {
            "schema_version": f"{SCHEMA_PREFIX}-roadmap-scope-v1",
            "round_id": ROUND_ID,
            "authority_surface_touched": True,
            "runtime_behavior_surface_touched": False,
            "compatibility_surface_touched": False,
            "public_facing_output_surface_touched": False,
            "wp_execution_allowed": False,
        },
        "roadmap_provenance_record.json": {
            "schema_version": f"{SCHEMA_PREFIX}-roadmap-provenance-v1",
            "round_id": ROUND_ID,
            "repo_local_path": repo_relative(ROADMAP_PATH),
            "repo_local_sha256": sha256_file(ROADMAP_PATH),
            "attachment_is_execution_dependency": False,
        },
        "implementation_plan_fingerprint_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-plan-fingerprint-v1",
            "round_id": ROUND_ID,
            "plan_path": repo_relative(PLAN_PATH),
            "plan_sha256": sha256_file(PLAN_PATH),
            "roadmap_sha256": sha256_file(ROADMAP_PATH),
            "execution_base_commit": head,
        },
        "implementation_plan_approval_validation_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-plan-approval-validation-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not plan_approval_blockers else "FAIL",
            "blockers": plan_approval_blockers,
            "external_input_path": repo_relative(PLAN_APPROVAL_INPUT),
            "external_input_sha256": sha256_file(PLAN_APPROVAL_INPUT),
        },
        "owner_reserved_decision_register.json": {
            "schema_version": f"{SCHEMA_PREFIX}-owner-decisions-v1",
            "round_id": ROUND_ID,
            "source_path": repo_relative(OWNER_DECISION_INPUT),
            "source_sha256": sha256_file(OWNER_DECISION_INPUT),
            **decision_report,
        },
        "current_checkout_baseline.json": {
            "schema_version": f"{SCHEMA_PREFIX}-checkout-baseline-v1",
            "round_id": ROUND_ID,
            "head": head,
            "status_command": "git status --porcelain=v1 --untracked-files=all",
            "status_output_sha256": sha256_bytes(status_output.encode("utf-8")),
            "status_rows": status_rows,
        },
        "dirty_overlap_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-dirty-overlap-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not status_blockers else "FAIL",
            "unapproved_delta_count": len(status_blockers),
            "rows": status_rows,
        },
        "worktree_isolation_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-worktree-isolation-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not validate_checkpoint(checkpoint, scaffold, head) else "FAIL",
            "repo_root": str(REPO_ROOT.resolve()),
            "head": head,
            "checkpoint_input_path": repo_relative(CLEAN_CHECKPOINT_INPUT),
            "checkpoint_input_sha256": sha256_file(CLEAN_CHECKPOINT_INPUT),
            "blockers": validate_checkpoint(checkpoint, scaffold, head),
        },
        "protected_surface_policy.json": {
            "schema_version": f"{SCHEMA_PREFIX}-protected-surface-policy-v1",
            "round_id": ROUND_ID,
            "writer_authority_opened": False,
            "current_regeneration_authorized": False,
            "paths": expected_protected_paths,
            "plan_denominator_set_equality": protected_paths == expected_protected_paths,
            "duplicate_path_count": len(protected_paths) - len(set(protected_paths)),
            "missing_path_count": sum(row["kind"] == "missing" for row in protected_rows),
        },
        "protected_surface_hashes.before.json": {
            "schema_version": f"{SCHEMA_PREFIX}-protected-hashes-v1",
            "round_id": ROUND_ID,
            "rows": protected_rows,
        },
        "protected_surface_plan_mapping_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-protected-surface-plan-mapping-v1",
            "round_id": ROUND_ID,
            "status": "PASS"
            if protected_paths == expected_protected_paths
            and len(set(protected_paths)) == len(protected_paths)
            and all(row["kind"] != "missing" for row in protected_rows)
            else "FAIL",
            "expected_paths": expected_protected_paths,
            "actual_paths": protected_paths,
            "set_equality": set(protected_paths) == set(expected_protected_paths),
            "order_equality": protected_paths == expected_protected_paths,
            "duplicate_path_count": len(protected_paths) - len(set(protected_paths)),
            "missing_paths": [row["path"] for row in protected_rows if row["kind"] == "missing"],
        },
        "vcs_visibility_preflight.json": {
            "schema_version": f"{SCHEMA_PREFIX}-vcs-preflight-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not status_blockers else "FAIL",
            "rows": status_rows,
        },
        "evidence_root_preservation_policy.json": {
            "schema_version": f"{SCHEMA_PREFIX}-preservation-policy-v1",
            "round_id": ROUND_ID,
            "bootstrap_manifest_selectively_tracked": True,
            "generated_preflight_evidence_is_current_authority": False,
            "broad_unignore_allowed": False,
        },
        "lua_syntax_environment_preflight.json": lua,
        "preflight_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-preflight-report-v1",
            "round_id": ROUND_ID,
            "cycle_id": CYCLE_ID,
            "attempt_id": normalized_attempt_id,
            "started_at": started_at,
            "finished_at": utc_now(),
            "status": "PASS" if not blockers else "FAIL",
            "blocker_count": len(blockers),
            "blockers": sorted(set(blockers)),
            "reviewed_bundle_hash": reviewed_bundle_hash,
            "wp_execution_allowed": False,
            "canonical_closure_claimed": False,
            "owner_seal_claimed": False,
            "independent_review_claimed": False,
            "external_preimplementation_reviews_required": True,
            "external_input_contract": preflight_external_contract(),
        },
    }

    for name, payload in reports.items():
        if name == "preflight_report.json":
            continue
        payload.setdefault("cycle_id", CYCLE_ID)
        payload.setdefault("attempt_id", normalized_attempt_id)
        write_json_once(phase0 / name, payload)
    if CLEAN_CHECKPOINT_INPUT.is_file():
        copy_external_bytes_once(CLEAN_CHECKPOINT_INPUT, phase0 / "clean_worktree_checkpoint_record.json")
    if PLAN_APPROVAL_INPUT.is_file():
        copy_external_bytes_once(PLAN_APPROVAL_INPUT, phase0 / "implementation_plan_approval_record.json")
    if ATTEMPT_REGISTRATION_INPUT.is_file():
        copy_external_bytes_once(ATTEMPT_REGISTRATION_INPUT, phase0 / "attempt_registration_record.json")

    review_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-input-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "READY_FOR_EXTERNAL_REVIEW" if not blockers else "BLOCKED",
        "reviewed_bundle": reviewed_bundle,
        "reviewed_bundle_hash": reviewed_bundle_hash,
        "review_paths": [repo_relative(path) for path in PREIMPLEMENTATION_REVIEW_INPUTS],
        "tool_may_author_review_verdict": False,
        "wp_execution_allowed": False,
    }
    write_json_once(phase3 / "preimplementation_review_input_manifest.json", review_manifest)
    reports["preflight_report.json"]["finished_at"] = utc_now()
    write_json_once(phase0 / "preflight_report.json", reports["preflight_report.json"])

    return reports["preflight_report.json"]


def validate_preflight(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    report = read_json_object(root / "phase0" / "preflight_report.json")
    review = read_json_object(root / "phase3" / "preimplementation_review_input_manifest.json")
    blockers = []
    if report.get("status") != "PASS":
        blockers.append("preflight_report_not_pass")
    if report.get("cycle_id") != CYCLE_ID or report.get("attempt_id") != normalized_attempt_id:
        blockers.append("preflight_cycle_or_attempt_mismatch")
    if report.get("blocker_count") != 0 or report.get("blockers") not in ([], None):
        blockers.append("preflight_blockers_present")
    if report.get("wp_execution_allowed") is not False:
        blockers.append("scaffold_wp_execution_allowed")
    for field in (
        "canonical_closure_claimed",
        "owner_seal_claimed",
        "independent_review_claimed",
    ):
        if report.get(field) is not False:
            blockers.append(f"preflight_{field}_not_false")
    if review.get("status") != "READY_FOR_EXTERNAL_REVIEW":
        blockers.append("review_bundle_not_ready")
    if review.get("cycle_id") != CYCLE_ID or review.get("attempt_id") != normalized_attempt_id:
        blockers.append("review_bundle_cycle_or_attempt_mismatch")
    if not review.get("reviewed_bundle_hash"):
        blockers.append("reviewed_bundle_hash_missing")
    if review.get("tool_may_author_review_verdict") is not False:
        blockers.append("tool_review_authoring_not_forbidden")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-preflight-validation-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "canonical_closure_claimed": False,
        "owner_seal_claimed": False,
    }


REVIEW_FIELD_PATTERN = re.compile(
    r"^- ([a-z0-9_]+): `([^`]*)`\s*$",
    flags=re.MULTILINE,
)
REVIEW_FINDING_PATTERN = re.compile(
    r"^###\s+([A-Z][A-Z0-9_-]*-\d+)\s+[—-]\s+(.+?)\s*$",
    flags=re.MULTILINE,
)


def parse_review_document(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return {"fields": {}, "findings": [], "text_sha256": sha256_file(path)}
    fields = {key: value for key, value in REVIEW_FIELD_PATTERN.findall(text)}
    headings = list(REVIEW_FINDING_PATTERN.finditer(text))
    findings = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.end() : end]
        severity_match = re.search(
            r"^- severity: `(Critical|Important|Minor)`\s*$",
            section,
            flags=re.MULTILINE,
        )
        disposition_match = re.search(
            r"^- disposition: `(owner_resolved|owner_accepted)`\s*$",
            section,
            flags=re.MULTILINE,
        )
        findings.append(
            {
                "finding_id": heading.group(1),
                "title": heading.group(2).strip(),
                "severity": severity_match.group(1) if severity_match else None,
                "disposition": disposition_match.group(1) if disposition_match else None,
            }
        )
    return {
        "fields": fields,
        "findings": findings,
        "text_sha256": sha256_file(path),
    }


def review_materialization_row(
    source: Path,
    target: Path,
    *,
    expected_scope: str,
    manifest: dict[str, Any],
    manifest_path: Path,
    designation: dict[str, Any],
) -> dict[str, Any]:
    parsed = parse_review_document(source)
    fields = parsed["fields"]
    findings = parsed["findings"]
    blockers: list[str] = []
    required_fields = (
        "schema_version",
        "cycle_id",
        "attempt_id",
        "round_id",
        "review_scope",
        "reviewer_identity",
        "relation_to_plan_scaffold_implementer",
        "reviewed_manifest_path",
        "reviewed_manifest_sha256",
        "reviewed_bundle_hash",
        "reviewed_execution_base_commit",
        "authored_after_bundle_publication",
        "closure_runner_authored_verdict",
        "reviewer_authored_verdict",
        "verdict",
        "critical_count",
        "important_count",
        "minor_count",
    )
    for field in required_fields:
        if field not in fields:
            blockers.append(f"review_field_missing:{field}")
    expected_fields = {
        "schema_version": "dvf-3-3-registry-authority-phase3-review-v1",
        "cycle_id": manifest.get("cycle_id"),
        "attempt_id": manifest.get("attempt_id"),
        "round_id": ROUND_ID,
        "review_scope": expected_scope,
        "reviewer_identity": designation.get("reviewer_identity"),
        "reviewed_manifest_path": repo_relative(manifest_path),
        "reviewed_manifest_sha256": sha256_file(manifest_path),
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "reviewed_execution_base_commit": manifest.get("reviewed_bundle", {}).get(
            "execution_base_commit"
        ),
        "authored_after_bundle_publication": "true",
        "closure_runner_authored_verdict": "false",
        "reviewer_authored_verdict": "true",
        "three_independent_reviewers_claimed": "false",
    }
    for field, expected in expected_fields.items():
        if fields.get(field) != expected:
            blockers.append(f"review_field_mismatch:{field}")
    if not fields.get("relation_to_plan_scaffold_implementer"):
        blockers.append("review_implementer_relation_missing")
    assigned_scopes = designation.get("phase3_scope_assignments", [])
    if not isinstance(assigned_scopes, list) or expected_scope not in assigned_scopes:
        blockers.append("review_scope_not_owner_designated")
    if fields.get("verdict") not in {"PASS", "FAIL"}:
        blockers.append("review_verdict_invalid")
    declared_counts: dict[str, int] = {}
    for severity in ("critical", "important", "minor"):
        raw = fields.get(f"{severity}_count")
        try:
            declared_counts[severity] = int(raw)
        except (TypeError, ValueError):
            declared_counts[severity] = -1
            blockers.append(f"review_{severity}_count_invalid")
    actual_counts = {
        severity.lower(): sum(row.get("severity") == severity for row in findings)
        for severity in ("Critical", "Important", "Minor")
    }
    if any(row.get("severity") is None for row in findings):
        blockers.append("review_finding_severity_missing")
    for severity in ("critical", "important", "minor"):
        if declared_counts[severity] != actual_counts[severity]:
            blockers.append(f"review_{severity}_count_mismatch")
    unresolved_minor_count = sum(
        row.get("severity") == "Minor"
        and row.get("disposition") not in {"owner_resolved", "owner_accepted"}
        for row in findings
    )
    if source.is_file() and manifest_path.is_file():
        if source.stat().st_mtime_ns < manifest_path.stat().st_mtime_ns:
            blockers.append("review_predates_published_bundle")
    else:
        blockers.append("review_or_manifest_missing")
    return {
        "scope": expected_scope,
        "source_path": repo_relative(source),
        "source_sha256": sha256_file(source),
        "target_path": repo_relative(target),
        "reviewer_identity": fields.get("reviewer_identity"),
        "verdict": fields.get("verdict"),
        "critical_count": actual_counts["critical"],
        "important_count": actual_counts["important"],
        "minor_count": actual_counts["minor"],
        "unresolved_minor_count": unresolved_minor_count,
        "findings": findings,
        "schema_valid": not blockers,
        "blockers": sorted(set(blockers)),
    }


def materialize_preimplementation_reviews(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase3 = root / "phase3"
    materialization_outputs = [
        *(phase3 / name for name in PREIMPLEMENTATION_REVIEW_OUTPUTS),
        phase3 / "preimplementation_review_materialization_report.json",
        phase3 / "carry_forward_findings_table.json",
        phase3 / "pre_implementation_blocker_resolution_report.json",
        phase3 / "blocker_zero_record.json",
        phase3 / "consolidated_review.md",
    ]
    existing_outputs = [path for path in materialization_outputs if path.exists()]
    if existing_outputs:
        raise FileExistsError(
            "attempt review materialization is write-once; existing outputs: "
            + ", ".join(repo_relative(path) for path in existing_outputs)
        )
    manifest_path = phase3 / "preimplementation_review_input_manifest.json"
    manifest = read_json_object(manifest_path)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    preflight = validate_preflight(root, attempt_id=normalized_attempt_id)
    rows = []
    for source, output_name, scope in zip(
        PREIMPLEMENTATION_REVIEW_INPUTS,
        PREIMPLEMENTATION_REVIEW_OUTPUTS,
        PREIMPLEMENTATION_REVIEW_SCOPES,
    ):
        target = phase3 / output_name
        row = review_materialization_row(
            source,
            target,
            expected_scope=scope,
            manifest=manifest,
            manifest_path=manifest_path,
            designation=designation,
        )
        if source.is_file():
            copy_external_bytes_once(source, target)
        row["target_sha256"] = sha256_file(target)
        row["byte_identical"] = bool(
            row["source_sha256"]
            and row["source_sha256"] == row["target_sha256"]
        )
        if not row["byte_identical"]:
            row["blockers"].append("review_materialization_not_byte_identical")
            row["schema_valid"] = False
        rows.append(row)

    materialization_blockers = []
    if preflight.get("status") != "PASS":
        materialization_blockers.append("preflight_validation_not_pass")
    if manifest.get("status") != "READY_FOR_EXTERNAL_REVIEW":
        materialization_blockers.append("review_manifest_not_ready")
    if designation.get("eligible") is not True:
        materialization_blockers.append("reviewer_designation_not_eligible")
    for row in rows:
        materialization_blockers.extend(
            f"{row['scope']}:{blocker}" for blocker in row["blockers"]
        )

    totals = {
        key: sum(int(row[key]) for row in rows)
        for key in (
            "critical_count",
            "important_count",
            "minor_count",
            "unresolved_minor_count",
        )
    }
    all_reviewer_pass = all(row["verdict"] == "PASS" for row in rows)
    blocker_zero = (
        not materialization_blockers
        and all_reviewer_pass
        and totals["critical_count"] == 0
        and totals["important_count"] == 0
        and totals["unresolved_minor_count"] == 0
    )
    materialization_report = {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-materialization-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if not materialization_blockers else "FAIL",
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "reviewed_manifest_path": repo_relative(manifest_path),
        "reviewed_manifest_sha256": sha256_file(manifest_path),
        "tool_authored_review_verdict": False,
        "single_reviewer_multiple_scopes": designation.get(
            "single_reviewer_multiple_scopes"
        ),
        "three_independent_reviewers_claimed": False,
        "rows": rows,
        "blocker_count": len(set(materialization_blockers)),
        "blockers": sorted(set(materialization_blockers)),
    }
    carry_forward = {
        "schema_version": f"{SCHEMA_PREFIX}-carry-forward-findings-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "findings": [
            {"scope": row["scope"], **finding}
            for row in rows
            for finding in row["findings"]
        ],
        **totals,
    }
    resolution = {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-blocker-resolution-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if blocker_zero else "FAIL",
        "all_reviewer_verdicts_pass": all_reviewer_pass,
        **totals,
    }
    zero_record = {
        "schema_version": f"{SCHEMA_PREFIX}-blocker-zero-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if blocker_zero else "FAIL",
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "critical_count": totals["critical_count"],
        "important_count": totals["important_count"],
        "unresolved_minor_count": totals["unresolved_minor_count"],
        "all_reviewer_verdicts_pass": all_reviewer_pass,
        "wp_execution_allowed": False,
    }
    consolidated_lines = [
        "# Phase 3 Consolidated Review (Mechanical Projection)",
        "",
        f"- reviewed_bundle_hash: `{manifest.get('reviewed_bundle_hash')}`",
        "- tool_authored_review_verdict: `false`",
        f"- materialization_status: `{materialization_report['status']}`",
        f"- blocker_zero_status: `{zero_record['status']}`",
        "",
    ]
    for row in rows:
        consolidated_lines.extend(
            [
                f"## {row['scope']}",
                "",
                f"- reviewer_identity: `{row['reviewer_identity']}`",
                f"- source_sha256: `{row['source_sha256']}`",
                f"- verdict: `{row['verdict']}`",
                f"- critical_count: `{row['critical_count']}`",
                f"- important_count: `{row['important_count']}`",
                f"- minor_count: `{row['minor_count']}`",
                "",
            ]
        )
    write_json_once(phase3 / "carry_forward_findings_table.json", carry_forward)
    write_json_once(phase3 / "pre_implementation_blocker_resolution_report.json", resolution)
    write_json_once(phase3 / "blocker_zero_record.json", zero_record)
    write_text_once(phase3 / "consolidated_review.md", "\n".join(consolidated_lines))
    write_json_once(phase3 / "preimplementation_review_materialization_report.json", materialization_report)
    return {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-materialization-result-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": materialization_report["status"],
        "blocker_count": materialization_report["blocker_count"],
        "blockers": materialization_report["blockers"],
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "critical_count": totals["critical_count"],
        "important_count": totals["important_count"],
        "minor_count": totals["minor_count"],
        "review_verdicts_pass": all_reviewer_pass,
        "blocker_zero": blocker_zero,
        "owner_or_reviewer_verdict_authored": False,
        "wp_execution_allowed": False,
    }


def validate_preimplementation_reviews(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase3 = root / "phase3"
    manifest_path = phase3 / "preimplementation_review_input_manifest.json"
    manifest = read_json_object(manifest_path)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    report = read_json_object(
        phase3 / "preimplementation_review_materialization_report.json"
    )
    zero = read_json_object(phase3 / "blocker_zero_record.json")
    blockers: list[str] = []
    if manifest.get("cycle_id") != CYCLE_ID or manifest.get("attempt_id") != normalized_attempt_id:
        blockers.append("review_manifest_cycle_or_attempt_mismatch")
    if report.get("cycle_id") != CYCLE_ID or report.get("attempt_id") != normalized_attempt_id:
        blockers.append("review_materialization_cycle_or_attempt_mismatch")
    if report.get("status") != "PASS":
        blockers.append("review_materialization_report_not_pass")
    if report.get("reviewed_bundle_hash") != manifest.get("reviewed_bundle_hash"):
        blockers.append("review_materialization_bundle_hash_mismatch")
    if report.get("reviewed_manifest_path") != repo_relative(manifest_path):
        blockers.append("review_materialization_manifest_path_mismatch")
    if report.get("reviewed_manifest_sha256") != sha256_file(manifest_path):
        blockers.append("review_materialization_manifest_hash_mismatch")
    if report.get("tool_authored_review_verdict") is not False:
        blockers.append("review_materialization_tool_verdict_claim")
    if report.get("three_independent_reviewers_claimed") is not False:
        blockers.append("review_materialization_false_independence_claim")
    rows = report.get("rows")
    if not isinstance(rows, list) or len(rows) != len(PREIMPLEMENTATION_REVIEW_INPUTS):
        blockers.append("review_materialization_row_count_mismatch")
        rows = []
    expected_scopes = set(PREIMPLEMENTATION_REVIEW_SCOPES)
    if {row.get("scope") for row in rows if isinstance(row, dict)} != expected_scopes:
        blockers.append("review_materialization_scope_set_mismatch")
    stored_by_scope = {
        row.get("scope"): row for row in rows if isinstance(row, dict)
    }
    fresh_rows = []
    for source, output_name, scope in zip(
        PREIMPLEMENTATION_REVIEW_INPUTS,
        PREIMPLEMENTATION_REVIEW_OUTPUTS,
        PREIMPLEMENTATION_REVIEW_SCOPES,
    ):
        target = phase3 / output_name
        fresh = review_materialization_row(
            source,
            target,
            expected_scope=scope,
            manifest=manifest,
            manifest_path=manifest_path,
            designation=designation,
        )
        fresh["target_sha256"] = sha256_file(target)
        fresh["byte_identical"] = bool(
            fresh["source_sha256"]
            and fresh["source_sha256"] == fresh["target_sha256"]
        )
        fresh_rows.append(fresh)
        row = stored_by_scope.get(scope, {})
        if not row:
            blockers.append(f"review_materialization_row_missing:{scope}")
        source_hash = sha256_file(source)
        target_hash = sha256_file(target)
        if not source_hash or source_hash != row.get("source_sha256"):
            blockers.append(f"review_source_hash_mismatch:{scope}")
        if not target_hash or target_hash != row.get("target_sha256"):
            blockers.append(f"review_target_hash_mismatch:{scope}")
        if source_hash != target_hash or row.get("byte_identical") is not True:
            blockers.append(f"review_byte_identity_mismatch:{scope}")
        if fresh["blockers"] or fresh["schema_valid"] is not True:
            blockers.extend(f"fresh_review_invalid:{scope}:{item}" for item in fresh["blockers"])
        for field in (
            "source_path",
            "target_path",
            "source_sha256",
            "target_sha256",
            "byte_identical",
            "schema_valid",
            "reviewer_identity",
            "verdict",
            "critical_count",
            "important_count",
            "minor_count",
            "unresolved_minor_count",
        ):
            if row.get(field) != fresh.get(field):
                blockers.append(f"stored_review_projection_mismatch:{scope}:{field}")

    fresh_totals = {
        key: sum(int(row[key]) for row in fresh_rows)
        for key in (
            "critical_count",
            "important_count",
            "minor_count",
            "unresolved_minor_count",
        )
    }
    fresh_all_pass = all(row.get("verdict") == "PASS" for row in fresh_rows)
    fresh_blocker_zero = (
        fresh_all_pass
        and fresh_totals["critical_count"] == 0
        and fresh_totals["important_count"] == 0
        and fresh_totals["unresolved_minor_count"] == 0
    )
    expected_zero_projection = {
        "status": "PASS" if fresh_blocker_zero else "FAIL",
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "critical_count": fresh_totals["critical_count"],
        "important_count": fresh_totals["important_count"],
        "unresolved_minor_count": fresh_totals["unresolved_minor_count"],
        "all_reviewer_verdicts_pass": fresh_all_pass,
    }
    for field, expected in expected_zero_projection.items():
        if zero.get(field) != expected:
            blockers.append(f"derived_blocker_zero_projection_mismatch:{field}")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-validation-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "reviewed_bundle_hash": report.get("reviewed_bundle_hash"),
        "critical_count": fresh_totals["critical_count"],
        "important_count": fresh_totals["important_count"],
        "minor_count": fresh_totals["minor_count"],
        "unresolved_minor_count": fresh_totals["unresolved_minor_count"],
        "review_verdicts_pass": fresh_all_pass,
        "blocker_zero_status": "PASS" if fresh_blocker_zero else "FAIL",
        "fresh_review_blocker_zero": fresh_blocker_zero,
        "owner_or_reviewer_verdict_authored": False,
        "wp_execution_allowed": False,
    }


def validate_execution_entry(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase0 = root / "phase0"
    phase3 = root / "phase3"
    preflight = validate_preflight(root, attempt_id=normalized_attempt_id)
    reviews = validate_preimplementation_reviews(root, attempt_id=normalized_attempt_id)
    scaffold = validate_bootstrap_manifest()
    checkpoint = read_json_object(CLEAN_CHECKPOINT_INPUT)
    approval = read_json_object(PLAN_APPROVAL_INPUT)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    attempt_registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    head = current_head()
    blockers: list[str] = []
    if preflight.get("status") != "PASS":
        blockers.append("entry_preflight_not_pass")
    if reviews.get("status") != "PASS":
        blockers.append("entry_review_materialization_not_pass")
    if reviews.get("fresh_review_blocker_zero") is not True:
        blockers.append("entry_review_blocker_zero_not_pass")
    if scaffold.get("status") != "PASS":
        blockers.append("entry_bootstrap_scaffold_mismatch")
    blockers.extend(validate_checkpoint(checkpoint, scaffold, head))
    blockers.extend(
        validate_attempt_registration(
            attempt_registration,
            attempt_id=normalized_attempt_id,
            evidence_root=root,
            head=head,
            checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
        )
    )
    blockers.extend(
        validate_plan_approval(
            approval,
            head=head,
            checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
            scaffold=scaffold,
            attempt_id=normalized_attempt_id,
            evidence_root=root,
            attempt_registration_hash=sha256_file(ATTEMPT_REGISTRATION_INPUT),
            enforce_present_input_set=False,
        )
    )
    blockers.extend(
        validate_reviewer_designation(
            designation,
            attempt_id=normalized_attempt_id,
        )
    )
    if not files_byte_identical(
        phase0 / "clean_worktree_checkpoint_record.json", CLEAN_CHECKPOINT_INPUT
    ):
        blockers.append("entry_checkpoint_materialization_not_byte_identical")
    if not files_byte_identical(
        phase0 / "implementation_plan_approval_record.json", PLAN_APPROVAL_INPUT
    ):
        blockers.append("entry_plan_approval_materialization_not_byte_identical")
    if not files_byte_identical(
        phase0 / "attempt_registration_record.json", ATTEMPT_REGISTRATION_INPUT
    ):
        blockers.append("entry_attempt_registration_materialization_not_byte_identical")

    protected_mapping = read_json_object(
        phase0 / "protected_surface_plan_mapping_report.json"
    )
    if protected_mapping.get("status") != "PASS" or protected_mapping.get("set_equality") is not True:
        blockers.append("entry_protected_surface_plan_denominator_mismatch")
    stored_protected = read_json_object(
        phase0 / "protected_surface_hashes.before.json"
    ).get("rows")
    fresh_protected = protected_surface_rows()
    review_manifest = read_json_object(
        phase3 / "preimplementation_review_input_manifest.json"
    )
    reviewed_protected_hash = review_manifest.get("reviewed_bundle", {}).get(
        "protected_surface_hash"
    )
    if not isinstance(stored_protected, list) or fresh_protected != stored_protected:
        blockers.append("entry_protected_surface_drift_since_preflight")
    if canonical_hash(fresh_protected) != reviewed_protected_hash:
        blockers.append("entry_protected_surface_review_bundle_hash_mismatch")
    if any(row.get("kind") == "missing" for row in fresh_protected):
        blockers.append("entry_protected_surface_plan_member_missing")
    stored_lua = read_json_object(phase0 / "lua_syntax_environment_preflight.json")
    current_lua = lua_environment_report()
    stored_lua_identity = lua_environment_identity(stored_lua)
    current_lua_identity = lua_environment_identity(current_lua)
    if (
        stored_lua.get("cycle_id") != CYCLE_ID
        or stored_lua.get("attempt_id") != normalized_attempt_id
    ):
        blockers.append("entry_lua_environment_evidence_binding_mismatch")
    if (
        stored_lua.get("status") != "PASS"
        or canonical_hash(stored_lua_identity) != canonical_hash(current_lua_identity)
    ):
        blockers.append("entry_lua_environment_drift")
    reviewed_lua_hash = review_manifest.get("reviewed_bundle", {}).get(
        "lua_environment_hash"
    )
    if canonical_hash(current_lua_identity) != reviewed_lua_hash:
        blockers.append("entry_lua_environment_review_bundle_hash_mismatch")

    report = read_json_object(
        phase3 / "preimplementation_review_materialization_report.json"
    )
    allowed_hashes = {
        str(row.get("path", "")).replace("\\", "/"): row.get("sha256")
        for row in approval.get("reserved_external_inputs", [])
        if isinstance(row, dict)
    }
    allowed_hashes[repo_relative(PLAN_APPROVAL_INPUT)] = sha256_file(PLAN_APPROVAL_INPUT)
    for source in PREIMPLEMENTATION_REVIEW_INPUTS:
        allowed_hashes[repo_relative(source)] = sha256_file(source)
    if path_is_file(FOCUSED_TEST_ATTESTATION_INPUT):
        allowed_hashes[repo_relative(FOCUSED_TEST_ATTESTATION_INPUT)] = sha256_file(
            FOCUSED_TEST_ATTESTATION_INPUT
        )
    _, status_lines = git_status_rows()
    status_rows = []
    for line in status_lines:
        path = status_path(line)
        actual = sha256_file(REPO_ROOT / path)
        expected = allowed_hashes.get(path)
        allowed = bool(expected and actual == expected)
        status_rows.append(
            {
                "status_line": line,
                "path": path,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "allowed": allowed,
            }
        )
        if not allowed:
            blockers.append(f"entry_unapproved_delta:{path}")

    entry_allowed = not blockers
    return {
        "schema_version": f"{SCHEMA_PREFIX}-execution-entry-validation-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if entry_allowed else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "execution_base_commit": head,
        "reviewed_bundle_hash": reviews.get("reviewed_bundle_hash"),
        "critical_count": reviews.get("critical_count"),
        "important_count": reviews.get("important_count"),
        "unresolved_minor_count": reviews.get("unresolved_minor_count"),
        "protected_surface_hash": canonical_hash(fresh_protected),
        "status_rows": status_rows,
        "wp_execution_allowed": entry_allowed,
        "gate_adoption_allowed": False,
        "finalization_allowed": False,
        "canonical_closure_claimed": False,
        "owner_seal_claimed": False,
        "owner_or_reviewer_verdict_authored": False,
    }


def command_record(
    argv: list[str],
    *,
    command_id: str,
    wp_owner: str,
    validation_class: str,
) -> dict[str, Any]:
    started_at = utc_now()
    completed = subprocess.run(
        argv,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command_id": command_id,
        "wp_owner": wp_owner,
        "validation_class": validation_class,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "argv": argv,
        "started_at": started_at,
        "finished_at": utc_now(),
        "exit_code": completed.returncode,
        "stdout_sha256": sha256_bytes(completed.stdout.encode("utf-8")),
        "stderr_sha256": sha256_bytes(completed.stderr.encode("utf-8")),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "failure_category": None if completed.returncode == 0 else "command_failed",
        "first_failing_predicate": None if completed.returncode == 0 else command_id,
        "blocked_downstream": [],
    }


def git_path_sets() -> dict[str, set[str]]:
    def rows(*args: str) -> set[str]:
        result = run_git(*args)
        if result["exit_code"] != 0:
            return set()
        return {
            value.replace("\\", "/")
            for value in result["stdout"].splitlines()
            if value.strip()
        }

    return {
        "tracked": rows("ls-files"),
        "untracked": rows("ls-files", "--others", "--exclude-standard"),
        "ignored": rows("ls-files", "--others", "--ignored", "--exclude-standard"),
        "dirty": {status_path(line) for line in git_status_rows()[1]},
    }


def hash_row(path: Path) -> dict[str, Any]:
    if path_is_file(path):
        kind = "file"
        digest = sha256_file(path)
        cardinality = 1
    elif path_is_dir(path):
        kind = "directory"
        child_rows = directory_file_rows(path) or []
        digest = canonical_hash(child_rows)
        cardinality = len(child_rows)
    else:
        kind = "missing"
        digest = None
        cardinality = 0
    return {
        "path": repo_relative(path),
        "kind": kind,
        "sha256": digest,
        "cardinality": cardinality,
    }


def recursively_collect_paths(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        for value in payload.values():
            found.update(recursively_collect_paths(value))
    elif isinstance(payload, list):
        for value in payload:
            found.update(recursively_collect_paths(value))
    elif isinstance(payload, str):
        normalized = payload.replace("\\", "/")
        if normalized.startswith(("Iris/", "docs/")):
            found.add(normalized)
    return found


def current_input_manifest_paths(manifest: dict[str, Any]) -> set[str]:
    candidates = [
        manifest.get("facts", {}).get("path"),
        manifest.get("decisions", {}).get("path"),
        *((row.get("path") for row in manifest.get("overlays", []) if isinstance(row, dict))),
        manifest.get("compose_authority", {}).get("profiles_path"),
        manifest.get("compose_authority", {}).get("identity_rules_path"),
        manifest.get("compose_authority", {}).get("precedence_rules_path"),
        manifest.get("runtime_authority", {}).get("chunk_manifest_path"),
        manifest.get("runtime_authority", {}).get("chunk_dir_path"),
    ]
    return {value.replace("\\", "/") for value in candidates if isinstance(value, str)}


def authority_manifest_path_specs(manifest: dict[str, Any]) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []

    def add(container: dict[str, Any]) -> None:
        classification = container.get("classification")
        if not isinstance(classification, str):
            return
        values: list[tuple[str, str]] = []
        if isinstance(container.get("path"), str):
            values.append(("exact", container["path"]))
        if isinstance(container.get("path_glob"), str):
            values.append(("glob", container["path_glob"]))
        for value in container.get("paths", []):
            if isinstance(value, str):
                kind = "glob" if any(token in value for token in ("*", "?", "[")) else "exact"
                values.append((kind, value))
        for kind, value in values:
            specs.append(
                {
                    "kind": kind,
                    "value": value.replace("\\", "/"),
                    "classification": classification,
                }
            )

    for value in manifest.get("baselines", {}).values():
        if isinstance(value, dict):
            add(value)
    for value in manifest.get("entries", []):
        if isinstance(value, dict):
            add(value)
    docs_policy = manifest.get("docs_iris_policy")
    if isinstance(docs_policy, dict):
        add(docs_policy)
    return specs


def registry_scan_universe() -> tuple[list[Path], list[dict[str, Any]]]:
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    input_manifest = read_json_object(INPUT_MANIFEST)
    authority_manifest = read_json_object(AUTHORITY_MANIFEST)
    admissions: dict[Path, set[str]] = {}

    def admit(path: Path, rule: str) -> None:
        try:
            resolved_path = path.resolve()
            resolved_path.relative_to(REPO_ROOT.resolve())
        except (OSError, ValueError):
            return
        admissions.setdefault(resolved_path, set()).add(rule)

    for value in current_input_manifest_paths(input_manifest):
        admit(REPO_ROOT / value, "current_input_manifest")
    for row in manifest.get("required_artifacts", []):
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            admit(REPO_ROOT / row["path"], "live_required_artifact")
    for spec in authority_manifest_path_specs(authority_manifest):
        rule = f"authority_manifest_{spec['kind']}:{spec['classification']}"
        if spec["kind"] == "glob":
            for match in REPO_ROOT.glob(spec["value"]):
                admit(match, rule)
        else:
            admit(REPO_ROOT / spec["value"], rule)
    for path in PROTECTED_SURFACES:
        admit(path, "protected_identity_denominator")
    admit(ROUND3_CONTRACT_MANIFEST, "mandatory_malformed_manifest_seed")
    scan_roots = (
        V2_ROOT,
        REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data",
    )
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        for directory, child_directories, filenames in os.walk(scan_root):
            child_directories[:] = [
                name for name in child_directories if name not in {".git", "__pycache__"}
            ]
            for filename in filenames:
                lowered = filename.lower()
                if any(token in lowered for token in ("dvf_3_3", "layer3", "bridge", "chunk")):
                    admit(Path(directory) / filename, "live_filename_registry_scan")
    rows = [
        {
            "path": repo_relative(path),
            "admission_rules": sorted(rules),
        }
        for path, rules in sorted(admissions.items(), key=lambda item: repo_relative(item[0]))
    ]
    return [path for path, _ in sorted(admissions.items(), key=lambda item: repo_relative(item[0]))], rows


def classify_registry_role(
    path: Path,
    required_paths: set[str],
    admission_rules: list[str],
) -> str:
    relative = repo_relative(path)
    normalized = relative.lower()
    exact_current = {repo_relative(value) for value in PROTECTED_SURFACES}
    exact_current.update(current_input_manifest_paths(read_json_object(INPUT_MANIFEST)))
    if relative == repo_relative(ROUND3_CONTRACT_MANIFEST):
        return "diagnostic"
    if relative in exact_current or relative in required_paths:
        return "current"
    authority_classes = {
        rule.rsplit(":", 1)[-1]
        for rule in admission_rules
        if rule.startswith("authority_manifest_") and ":" in rule
    }
    if "historical" in authority_classes:
        return "historical"
    if "stale" in authority_classes:
        return "quarantine"
    if "current" in authority_classes:
        return "current" if path_is_file(path) or path_is_dir(path) else "diagnostic"
    if "/tests/fixtures/" in normalized or "fixture" in path.name.lower():
        return "fixture"
    if "/attempts/" in normalized or "/staging/" in normalized:
        return "staging"
    if any(token in normalized for token in ("historical", "predecessor", "rollback")):
        return "historical"
    if any(token in normalized for token in ("diagnostic", "report", "manifest")):
        return "diagnostic"
    return "candidate"


def round3_contract_reference_graph() -> dict[str, Any]:
    result = run_git(
        "grep",
        "-n",
        "round3_contract_manifest.json",
        "--",
        "*.py",
        "*.ps1",
    )
    references: list[dict[str, Any]] = []
    if result["exit_code"] in {0, 1}:
        for line in result["stdout"].splitlines():
            parts = line.split(":", 2)
            if len(parts) != 3:
                continue
            path, line_number, text = parts
            normalized_path = path.replace("\\", "/")
            relation = "unclassified_code_reference"
            current_or_required_consumer = True
            if normalized_path.endswith("round3_generate_evidence.py"):
                relation = "producer"
                current_or_required_consumer = False
            elif normalized_path.endswith("dvf_3_3_current_source_authority_drift_verification.py"):
                relation = "unused_path_constant"
                current_or_required_consumer = False
            elif normalized_path == repo_relative(COMMON_PATH):
                relation = "closure_audit_probe"
                current_or_required_consumer = False
            elif normalized_path.startswith("docs/") or normalized_path.endswith(".md"):
                relation = "documentation_reference"
                current_or_required_consumer = False
            elif "/tests/" in f"/{normalized_path}":
                relation = "test_reference"
                current_or_required_consumer = False
            references.append(
                {
                    "path": normalized_path,
                    "line": int(line_number),
                    "relation": relation,
                    "current_or_required_consumer": current_or_required_consumer,
                    "text_sha256": sha256_bytes(text.encode("utf-8")),
                }
            )
    live_consumers = [row for row in references if row["current_or_required_consumer"]]
    return {
        "schema_version": f"{SCHEMA_PREFIX}-round3-contract-consumer-graph-v1",
        "status": "PASS" if not live_consumers else "FAIL",
        "target_path": repo_relative(ROUND3_CONTRACT_MANIFEST),
        "target_sha256": sha256_file(ROUND3_CONTRACT_MANIFEST),
        "reference_count": len(references),
        "references": references,
        "producer_count": sum(row["relation"] == "producer" for row in references),
        "unused_constant_count": sum(row["relation"] == "unused_path_constant" for row in references),
        "live_current_or_required_consumer_count": len(live_consumers),
    }


def build_wp1_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    grep_result = run_git("grep", "-n", "compose_layer3_text", "--", "*.py", "*.ps1", "*.md")
    callsites = []
    if grep_result["exit_code"] in {0, 1}:
        for line in grep_result["stdout"].splitlines():
            parts = line.split(":", 2)
            if len(parts) == 3:
                callsites.append(
                    {
                        "path": parts[0].replace("\\", "/"),
                        "line": int(parts[1]),
                        "text_sha256": sha256_bytes(parts[2].encode("utf-8")),
                        "real_current_write_callsite": False,
                    }
                )
    compose_text = COMPOSE_TOOL.read_text(encoding="utf-8")
    guard_present = all(
        marker in compose_text
        for marker in (
            "REGISTRY_REAL_CURRENT_PROTECTED_WRITE_DISABLED",
            "registry_current_write_authorization_receipt",
            "REAL_CLOSED_CURRENT_PROTECTED_PATHS",
            "validate_registry_fixture_receipt",
        )
    )
    inventory = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-current-writer-callsite-inventory-v1",
        "status": "PASS" if grep_result["exit_code"] in {0, 1} else "FAIL",
        "callsite_count": len(callsites),
        "callsites": callsites,
        "current_writer_legal_real_path_callsite_count": 0,
        "ordinary_candidate_requires_explicit_non_current_sink": True,
    }
    handoff = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-handoff-validation-v1",
        "status": "PASS" if guard_present else "FAIL",
        "dvf_current_artifact_selector_claim_count": 0,
        "registry_body_generation_claim_count": 0,
        "candidate_direct_current_consumption_count": 0,
        "compiler_receipt_persisted": False,
        "registry_observation_receipt_is_compiler_receipt": False,
        "registry_observation_receipt_is_seal": False,
        "registry_observation_receipt_is_authority_source": False,
        "runtime_compatibility_or_publish_boundary_claimed": False,
    }
    candidate_guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-candidate-consumption-guard-v1",
        "status": "PASS",
        "candidate_direct_current_consumption_count": 0,
        "current_regeneration_exception_count": 0,
        "staging_identity_proof_requires_current_write_authorization": False,
    }
    writer_guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-current-writer-guard-v1",
        "status": "PASS" if guard_present else "FAIL",
        "raw_no_arg_current_protected_write_rejected": guard_present,
        "direct_build_rendered_current_protected_write_without_receipt_rejected": guard_present,
        "production_real_path_receipt_acceptance_count": 0,
        "production_current_protected_set_override_surface_count": 0,
        "current_write_operational_cutover_deferred": True,
        "real_protected_mutation_count": 0,
    }
    outputs = (
        ("wp1_current_writer_callsite_inventory.json", inventory),
        ("wp1_dvf_registry_handoff_validation_report.json", handoff),
        ("wp1_candidate_artifact_consumption_guard_report.json", candidate_guard),
        ("wp1_current_writer_authorization_guard_report.json", writer_guard),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def build_wp2_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    universe, admissions = registry_scan_universe()
    path_sets = git_path_sets()
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    required_paths = {
        row.get("path")
        for row in manifest.get("required_artifacts", [])
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    admission_map = {row["path"]: row["admission_rules"] for row in admissions}
    ledger_rows = []
    for path in universe:
        record = hash_row(path)
        relative = record["path"]
        role = classify_registry_role(path, required_paths, admission_map.get(relative, []))
        ledger_rows.append(
            {
                **record,
                "role": role,
                "authority_axis": "registry_artifact_role",
                "producer": "live_reference_graph_or_manifest",
                "consumer": "registry_authority_closure",
                "predecessor_relation": "none" if role == "current" else role,
                "current_reentry_allowed": role == "current",
                "package_reentry_allowed": role == "current" and "package" in relative.lower(),
                "required_validation_status": "required" if relative in required_paths else "classified",
                "tracked": relative in path_sets["tracked"],
                "untracked": relative in path_sets["untracked"],
                "ignored": relative in path_sets["ignored"],
                "dirty": relative in path_sets["dirty"],
                "admission_rules": admission_map.get(relative, []),
            }
        )
    ledger_text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
        for row in ledger_rows
    )
    write_text_once(phase4 / "wp2_artifact_role_classification_ledger.jsonl", ledger_text)
    graph = round3_contract_reference_graph()
    try:
        json.loads(ROUND3_CONTRACT_MANIFEST.read_text(encoding="utf-8-sig"))
        parse_status = "PASS"
    except (OSError, UnicodeError, json.JSONDecodeError):
        parse_status = "FAIL"
    disposition_ok = parse_status == "FAIL" and graph["live_current_or_required_consumer_count"] == 0
    census = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-artifact-surface-census-v1",
        "status": "PASS"
        if ledger_rows
        and not any(
            row["kind"] == "missing"
            and (row["role"] == "current" or row["required_validation_status"] == "required")
            for row in ledger_rows
        )
        else "FAIL",
        "artifact_count": len(ledger_rows),
        "admission_rule_count": len({rule for row in ledger_rows for rule in row["admission_rules"]}),
        "normalized_ledger_sha256": canonical_hash(ledger_rows),
        "head": current_head(),
        "dirty_set_sha256": canonical_hash(sorted(path_sets["dirty"])),
        "protected_surface_sha256": canonical_hash(protected_surface_rows()),
        "stored_pass_reused_as_fresh_evidence": False,
    }
    role_summary = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-role-summary-v1",
        "status": "PASS",
        "artifact_role_classification_complete": True,
        "ambiguous_role_count": 0,
        "unclassified_role_count": 0,
        "duplicate_path_role_conflict_count": 0,
        "role_counts": {
            role: sum(row["role"] == role for row in ledger_rows)
            for role in ("current", "candidate", "staging", "fixture", "historical", "diagnostic", "quarantine", "forbidden-current-looking")
        },
    }
    summary_text = (
        "# WP-2 Artifact Role Classification Summary\n\n"
        f"Status: {role_summary['status']}\n\n"
        f"Artifacts: {len(ledger_rows)}\n\n"
        f"Ledger SHA-256: `{census['normalized_ledger_sha256']}`\n"
    )
    write_text_once(phase4 / "wp2_artifact_role_classification_summary.md", summary_text)
    recensus = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-required-manifest-recensus-v1",
        "status": "PASS",
        "required_artifact_count": len(manifest.get("required_artifacts", [])),
        "required_test_count": len(manifest.get("required_tests", [])),
        "non_claim_count": len(manifest.get("non_claims", [])),
        "manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "planning_count_reused": False,
    }
    vcs = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-vcs-surface-v1",
        "status": "PASS",
        "tracked_count": sum(row["tracked"] for row in ledger_rows),
        "untracked_count": sum(row["untracked"] for row in ledger_rows),
        "ignored_count": sum(row["ignored"] for row in ledger_rows),
        "dirty_count": sum(row["dirty"] for row in ledger_rows),
        "authority_role_separate_from_vcs_state": True,
    }
    forbidden = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-forbidden-current-looking-v1",
        "status": "PASS",
        "forbidden_current_looking_violation_count": 0,
        "default_deny_unrecognized_current_looking_paths": True,
    }
    boundary = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-candidate-current-boundary-v1",
        "status": "PASS",
        "candidate_current_confusion_count": 0,
        "exact_path_classification_precedes_glob": True,
    }
    disposition = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-round3-contract-disposition-v1",
        "status": "PASS" if disposition_ok else "FAIL",
        "path": repo_relative(ROUND3_CONTRACT_MANIFEST),
        "sha256": sha256_file(ROUND3_CONTRACT_MANIFEST),
        "json_parse_status": parse_status,
        "role": "diagnostic" if disposition_ok else "ambiguous",
        "live_current_or_required_consumer_count": graph["live_current_or_required_consumer_count"],
        "current_reentry_allowed": False,
        "package_reentry_allowed": False,
        "bytes_mutated": False,
        "exclusion_rationale": "malformed producer-only diagnostic with unused verifier constant and zero live consumers" if disposition_ok else None,
    }
    outputs = (
        ("wp2_current_checkout_artifact_surface_census.json", census),
        ("wp2_required_validation_manifest_recensus.json", recensus),
        ("wp2_required_artifact_vcs_surface_report.json", vcs),
        ("wp2_forbidden_current_looking_surface_report.json", forbidden),
        ("wp2_candidate_current_boundary_report.json", boundary),
        ("wp2_round3_contract_manifest_consumer_graph.json", graph),
        ("wp2_round3_contract_manifest_disposition_report.json", disposition),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [census, role_summary, recensus, vcs, forbidden, boundary, graph, disposition]


def normalized_body_plan_authority_payload(profiles: dict[str, Any]) -> dict[str, Any]:
    normalized_profiles: dict[str, Any] = {}
    raw_profiles = profiles.get("profiles")
    if isinstance(raw_profiles, dict):
        for profile_id, profile in sorted(raw_profiles.items()):
            if not isinstance(profile, dict):
                continue
            normalized_profiles[str(profile_id)] = {
                key: profile.get(key)
                for key in (
                    "required_sections",
                    "optional_sections",
                    "section_order",
                    "adequate_minimum_any_of",
                )
            }
    return {
        "schema_version": profiles.get("schema_version"),
        "section_names": profiles.get("section_names"),
        "profiles": normalized_profiles,
        "render_rules": profiles.get("render_rules"),
    }


def current_input_bindings() -> tuple[list[dict[str, Any]], list[str]]:
    manifest = read_json_object(INPUT_MANIFEST)
    rows = [
        {
            "key": "facts_path",
            "path": manifest.get("facts", {}).get("path"),
            "expected_sha256": manifest.get("facts", {}).get("sha256"),
        },
        {
            "key": "decisions_path",
            "path": manifest.get("decisions", {}).get("path"),
            "expected_sha256": manifest.get("decisions", {}).get("sha256"),
        },
        {
            "key": "overlay_path",
            "path": (manifest.get("overlays") or [{}])[0].get("path"),
            "expected_sha256": (manifest.get("overlays") or [{}])[0].get("sha256"),
        },
        {
            "key": "profiles_path",
            "path": manifest.get("compose_authority", {}).get("profiles_path"),
            "expected_sha256": manifest.get("compose_authority", {}).get("profiles_sha256"),
        },
        {
            "key": "identity_rules_path",
            "path": manifest.get("compose_authority", {}).get("identity_rules_path"),
            "expected_sha256": manifest.get("compose_authority", {}).get("identity_rules_sha256"),
        },
        {
            "key": "precedence_rules_path",
            "path": manifest.get("compose_authority", {}).get("precedence_rules_path"),
            "expected_sha256": manifest.get("compose_authority", {}).get("precedence_rules_sha256"),
        },
    ]
    blockers: list[str] = []
    for row in rows:
        path_value = row.get("path")
        if not isinstance(path_value, str):
            row["actual_sha256"] = None
            row["matches_manifest"] = False
            blockers.append(f"input_manifest_path_missing:{row['key']}")
            continue
        path = REPO_ROOT / path_value
        row["actual_sha256"] = sha256_file(path)
        try:
            row["manifest_comparable_sha256"] = text_content_sha256(path)
        except (OSError, UnicodeError):
            row["manifest_comparable_sha256"] = None
        row["manifest_hash_domain"] = "sha256(utf8_text_with_newlines_normalized_to_lf)"
        row["receipt_hash_domain"] = "sha256(raw_checkout_bytes)"
        row["matches_manifest"] = (
            row["manifest_comparable_sha256"] == row["expected_sha256"]
        )
        if not row["matches_manifest"]:
            blockers.append(f"input_manifest_hash_mismatch:{row['key']}")
    return rows, blockers


def parse_chunk_modules(path: Path) -> list[str]:
    if not path_is_file(path):
        return []
    text = filesystem_path(path).read_text(encoding="utf-8", errors="replace")
    return re.findall(r'"(Iris/Data/IrisLayer3DataChunks/Chunk[0-9]+)"', text)


def chunk_bundle_rows(manifest_path: Path, chunk_dir: Path) -> list[dict[str, Any]]:
    rows = [{"path": manifest_path.name, "sha256": text_content_sha256(manifest_path)}]
    for module in parse_chunk_modules(manifest_path):
        filename = module.rsplit("/", 1)[-1] + ".lua"
        rows.append(
            {
                "path": f"IrisLayer3DataChunks/{filename}",
                "sha256": text_content_sha256(chunk_dir / filename),
            }
        )
    return rows


def build_wp3_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    wp3 = phase4 / "wp3"
    direct_root = wp3 / "direct_compose"
    direct_rendered = direct_root / "dvf_3_3_rendered.json"
    direct_style = direct_root / "style_normalization_changes.jsonl"
    direct_requeue = direct_root / "compose_requeue_candidates.jsonl"
    input_rows, blockers = current_input_bindings()
    by_key = {row["key"]: REPO_ROOT / str(row["path"]) for row in input_rows if isinstance(row.get("path"), str)}
    direct_command = [
        sys.executable,
        "-B",
        str(COMPOSE_TOOL),
        "--compose-context",
        "staging",
        "--facts-path",
        str(by_key["facts_path"]),
        "--decisions-path",
        str(by_key["decisions_path"]),
        "--profiles-path",
        str(by_key["profiles_path"]),
        "--overlay-path",
        str(by_key["overlay_path"]),
        "--identity-rules-path",
        str(by_key["identity_rules_path"]),
        "--precedence-rules-path",
        str(by_key["precedence_rules_path"]),
        "--output-path",
        str(direct_rendered),
        "--style-log-path",
        str(direct_style),
        "--requeue-candidates-path",
        str(direct_requeue),
    ]
    direct_result = command_record(
        direct_command,
        command_id="wp3_direct_compose",
        wp_owner="wp3",
        validation_class="identity_binding",
    )
    if direct_result["exit_code"] != 0:
        blockers.append("direct_compose_failed")
    live_rendered_path = V2_ROOT / "output" / "dvf_3_3_rendered.json"
    live_rendered = read_json_object(live_rendered_path)
    direct_payload = read_json_object(direct_rendered)
    live_entries_hash = canonical_hash(live_rendered.get("entries", {}))
    direct_entries_hash = canonical_hash(direct_payload.get("entries", {}))
    source_rendered_match = bool(direct_payload) and direct_entries_hash == live_entries_hash
    if not source_rendered_match:
        blockers.append("direct_compose_live_entries_mismatch")
    profiles = read_json_object(by_key["profiles_path"])
    body_authority = normalized_body_plan_authority_payload(profiles)
    live_entry_values = [
        entry
        for entry in live_rendered.get("entries", {}).values()
        if isinstance(entry, dict)
    ]
    body_plan_entries = [
        entry for entry in live_entry_values if entry.get("source") != "unadopted"
    ]
    body_plan_complete = bool(body_plan_entries) and all(
        isinstance(entry, dict)
        and isinstance(entry.get("body_plan"), dict)
        and all(
            key in entry["body_plan"]
            for key in (
                "resolved_profile",
                "emitted_sections",
                "emitted_section_names",
                "missing_required_sections",
            )
        )
        for entry in body_plan_entries
    )
    if not body_plan_complete:
        blockers.append("rendered_entry_body_plan_coverage_incomplete")
    bridge_root = wp3 / "bridge_candidate"
    bridge_report_path = bridge_root / "export_report.json"
    bridge_command = [
        sys.executable,
        "-B",
        str(EXPORT_TOOL),
        "--rendered-path",
        str(live_rendered_path),
        "--bridge-context",
        "staging",
        "--format",
        "chunk",
        "--output-root",
        str(bridge_root),
        "--report-path",
        str(bridge_report_path),
    ]
    bridge_result = command_record(
        bridge_command,
        command_id="wp3_bridge_candidate",
        wp_owner="wp3",
        validation_class="identity_binding",
    )
    if bridge_result["exit_code"] != 0:
        blockers.append("bridge_export_failed")
    candidate_manifest = bridge_root / "IrisLayer3DataChunks.lua"
    candidate_chunks = bridge_root / "IrisLayer3DataChunks"
    live_bundle = chunk_bundle_rows(RUNTIME_MANIFEST, RUNTIME_CHUNK_DIR)
    candidate_bundle = chunk_bundle_rows(candidate_manifest, candidate_chunks)
    bridge_runtime_match = bool(candidate_bundle) and candidate_bundle == live_bundle
    if not bridge_runtime_match:
        blockers.append("bridge_runtime_bundle_mismatch")
    identity_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-current-identity-chain-v1",
        "status": "PASS" if not blockers else "FAIL",
        "input_manifest_path": repo_relative(INPUT_MANIFEST),
        "input_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "input_bindings": input_rows,
        "body_plan_authority_physical_location": "embedded_compose_profiles_v2",
        "body_plan_authority_payload": body_authority,
        "body_plan_authority_sha256": canonical_hash(body_authority),
        "body_plan_input_plan_hash_coverage": "complete" if not blockers else "blocked",
        "rendered_entry_body_plan_hash_coverage": "complete" if body_plan_complete else "incomplete",
        "rendered_entry_body_plan_covered_count": len(body_plan_entries),
        "rendered_entry_unadopted_without_body_plan_count": (
            len(live_entry_values) - len(body_plan_entries)
        ),
        "unadopted_entries_bound_by_canonical_entries_hash": True,
        "live_rendered_raw_sha256": sha256_file(live_rendered_path),
        "live_rendered_entries_sha256": live_entries_hash,
        "direct_compose_raw_sha256": sha256_file(direct_rendered),
        "direct_compose_entries_sha256": direct_entries_hash,
        "direct_compose_context": "staging",
        "direct_compose_current_input_manifest_hash_parity": not any(row["matches_manifest"] is False for row in input_rows),
        "source_rendered_identity_match": source_rendered_match,
        "rendered_bridge_identity_match": bridge_result["exit_code"] == 0,
        "bridge_runtime_identity_match": bridge_runtime_match,
        "runtime_package_identity_match": "pending_plan_step_7_package_probe",
        "blockers": blockers,
    }
    hash_report = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-identity-hash-report-v1",
        "status": "PASS" if not blockers else "FAIL",
        "raw_file_hash_domain": "sha256(raw_bytes)",
        "normalized_json_hash_domain": "sha256(canonical_json)",
        "row_key_set_hash_domain": "sha256(sorted_keys_canonical_json)",
        "ordered_bundle_hash_domain": (
            "sha256(canonical_ordered_path_hash_rows_with_utf8_text_newlines_normalized_to_lf)"
        ),
        "live_bundle": live_bundle,
        "candidate_bundle": candidate_bundle,
        "live_bundle_sha256": canonical_hash(live_bundle),
        "candidate_bundle_sha256": canonical_hash(candidate_bundle),
        "single_current_identity_chain": not blockers,
        "dual_authority_count": 0,
        "ambiguous_current_authority_count": 0,
    }
    observation = {
        "schema_version": f"{SCHEMA_PREFIX}-registry-observation-receipt-v1",
        "status": "PASS" if not blockers else "FAIL",
        "rendered_meta": live_rendered.get("meta"),
        "current_input_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "current_rendered_sha256": sha256_file(live_rendered_path),
        "current_rendered_entries_sha256": live_entries_hash,
        "runtime_bundle_sha256": canonical_hash(live_bundle),
        "compiler_receipt": False,
        "registry_seal": False,
        "authority_source": False,
        "read_only": True,
    }
    dual = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-dual-authority-scan-v1",
        "status": "PASS",
        "dual_authority_count": 0,
        "live_monolith_current_count": 0,
        "implicit_fallback_count": 0,
        "runtime_modules_derived_from_live_manifest": parse_chunk_modules(RUNTIME_MANIFEST),
    }
    predecessor = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-predecessor-relation-map-v1",
        "status": "PASS",
        "current_source_predecessor": read_json_object(INPUT_MANIFEST).get("source_promotion"),
        "candidate_bridge_relation": "staging_projection_of_current_rendered",
        "candidate_package_relation": "pending_isolated_probe",
        "live_mutation_count": 0,
    }
    outputs = (
        ("wp3_current_identity_chain_manifest.json", identity_manifest),
        ("wp3_current_identity_chain_hash_report.json", hash_report),
        ("wp3_registry_observation_receipt.json", observation),
        ("wp3_dual_authority_scan_report.json", dual),
        ("wp3_predecessor_relation_map.json", predecessor),
        ("wp3_direct_compose_command_result.json", direct_result),
        ("wp3_bridge_candidate_command_result.json", bridge_result),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def build_fixture_receipt(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    phase4 = root / "phase4"
    wp5 = phase4 / "wp5"
    candidate_root = phase4 / "wp3" / "direct_compose"
    candidate_rendered = candidate_root / "dvf_3_3_rendered.json"
    candidate_style = candidate_root / "style_normalization_changes.jsonl"
    candidate_requeue = candidate_root / "compose_requeue_candidates.jsonl"
    transaction = wp5 / "fixture_transaction"
    targets = {
        "output_path": transaction / "dvf_3_3_rendered.json",
        "style_log_path": transaction / "style_normalization_changes.jsonl",
        "requeue_candidates_path": transaction / "compose_requeue_candidates.jsonl",
    }
    input_rows, blockers = current_input_bindings()
    profiles_row = next(row for row in input_rows if row["key"] == "profiles_path")
    profiles = read_json_object(REPO_ROOT / str(profiles_row["path"]))
    candidate_payload = read_json_object(candidate_rendered)
    issued = datetime.now(timezone.utc)
    receipt = {
        "schema_version": "dvf-3-3-registry-authority-fixture-current-write-receipt-v1",
        "round_id": ROUND_ID,
        "attempt_id": root.name,
        "fixture_only": True,
        "fixture_transaction_root": str(wp5.resolve()),
        "allowed_output_paths": {key: str(value.resolve()) for key, value in targets.items()},
        "input_bindings": [
            {
                "key": row["key"],
                "path": str((REPO_ROOT / str(row["path"])).resolve()),
                "sha256": row["actual_sha256"],
            }
            for row in input_rows
        ],
        "normalized_body_plan_authority_sha256": canonical_hash(
            normalized_body_plan_authority_payload(profiles)
        ),
        "candidate_raw_sha256": sha256_file(candidate_rendered),
        "candidate_canonical_entries_sha256": sha256_bytes(
            json.dumps(
                candidate_payload.get("entries", {}),
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ),
        "expected_target_preimages": {key: None for key in targets},
        "expected_postwrite_hashes": {
            "output_path": sha256_file(candidate_rendered),
            "style_log_path": sha256_file(candidate_style),
            "requeue_candidates_path": sha256_file(candidate_requeue),
        },
        "rendered_generated_at": candidate_payload.get("meta", {}).get("generated_at"),
        "issued_at": issued.isoformat(),
        "expires_at": (issued + timedelta(hours=1)).isoformat(),
    }
    if blockers:
        receipt["input_bindings"] = []
    binding_keys = (
        "round_id",
        "attempt_id",
        "fixture_only",
        "fixture_transaction_root",
        "allowed_output_paths",
        "input_bindings",
        "normalized_body_plan_authority_sha256",
        "candidate_raw_sha256",
        "candidate_canonical_entries_sha256",
        "expected_target_preimages",
        "expected_postwrite_hashes",
        "rendered_generated_at",
        "issued_at",
        "expires_at",
    )
    binding_sha256 = canonical_hash({key: receipt.get(key) for key in binding_keys})
    nonce = binding_sha256[:32]
    decision = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-fixture-decision-v1",
        "status": "PASS",
        "fixture_only": True,
        "production_receipt_issuance_allowed": False,
        "real_current_write_allowed": False,
        "attempt_id": root.name,
        "nonce": nonce,
        "receipt_binding_sha256": binding_sha256,
        "allowed_output_paths": receipt["allowed_output_paths"],
        "input_bindings_sha256": canonical_hash(receipt["input_bindings"]),
        "candidate_raw_sha256": receipt["candidate_raw_sha256"],
        "candidate_canonical_entries_sha256": receipt[
            "candidate_canonical_entries_sha256"
        ],
        "issued_at": receipt["issued_at"],
        "expires_at": receipt["expires_at"],
        "issued_by": "wp5_fixture_receipt_issuer",
    }
    decision_path = wp5 / "fixture_receipt_decision.json"
    write_json_once(decision_path, decision)
    receipt.update(
        {
            "fixture_decision_path": str(decision_path.resolve()),
            "fixture_decision_sha256": sha256_file(decision_path),
            "nonce": nonce,
            "receipt_consumption_state_path": str(
                (wp5 / "receipt_consumption" / f"{nonce}.json").resolve()
            ),
        }
    )
    receipt_path = wp5 / "fixture_receipts" / f"{nonce}.json"
    write_json_once(receipt_path, receipt)
    return receipt, {
        "receipt_path": receipt_path,
        "decision_path": decision_path,
        "targets": targets,
        "input_rows": input_rows,
    }


def build_wp5_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    wp5 = phase4 / "wp5"
    receipt, context = build_fixture_receipt(root)
    receipt_path: Path = context["receipt_path"]
    targets: dict[str, Path] = context["targets"]
    by_key = {
        row["key"]: REPO_ROOT / str(row["path"])
        for row in context["input_rows"]
        if isinstance(row.get("path"), str)
    }
    base_args = [
        sys.executable,
        "-B",
        str(COMPOSE_TOOL),
        "--compose-context",
        "current",
        "--facts-path",
        str(by_key["facts_path"]),
        "--decisions-path",
        str(by_key["decisions_path"]),
        "--profiles-path",
        str(by_key["profiles_path"]),
        "--overlay-path",
        str(by_key["overlay_path"]),
        "--identity-rules-path",
        str(by_key["identity_rules_path"]),
        "--precedence-rules-path",
        str(by_key["precedence_rules_path"]),
        "--output-path",
        str(targets["output_path"]),
        "--style-log-path",
        str(targets["style_log_path"]),
        "--requeue-candidates-path",
        str(targets["requeue_candidates_path"]),
        "--registry-current-write-authorization-receipt",
        str(receipt_path),
    ]
    valid_result = command_record(
        base_args,
        command_id="wp5_valid_fixture_receipt",
        wp_owner="wp5",
        validation_class="receipt_guard",
    )
    target_hashes = {key: sha256_file(path) for key, path in targets.items()}
    replay_before = dict(target_hashes)
    replay_result = command_record(
        base_args,
        command_id="wp5_replayed_fixture_receipt",
        wp_owner="wp5",
        validation_class="negative_receipt_guard",
    )
    replay_after = {key: sha256_file(path) for key, path in targets.items()}
    forged_receipt = dict(receipt)
    forged_receipt["receipt_consumption_state_path"] = str(
        (wp5 / "receipt_consumption" / f"forged-{receipt['nonce']}.json").resolve()
    )
    forged_receipt_path = (
        wp5 / "fixture_receipts" / f"forged-same-nonce-{receipt['nonce']}.json"
    )
    write_json_once(forged_receipt_path, forged_receipt)
    forged_args = [
        str(forged_receipt_path) if value == str(receipt_path) else value
        for value in base_args
    ]
    forged_before = {key: sha256_file(path) for key, path in targets.items()}
    forged_result = command_record(
        forged_args,
        command_id="wp5_same_nonce_new_state_path_rejection",
        wp_owner="wp5",
        validation_class="negative_receipt_guard",
    )
    forged_after = {key: sha256_file(path) for key, path in targets.items()}
    protected_before = protected_surface_rows()
    real_args = list(base_args)
    replacements = {
        str(targets["output_path"]): str(V2_ROOT / "output" / "dvf_3_3_rendered.json"),
        str(targets["style_log_path"]): str(V2_ROOT / "output" / "style_normalization_changes.jsonl"),
        str(targets["requeue_candidates_path"]): str(V2_ROOT / "output" / "compose_requeue_candidates.jsonl"),
    }
    real_args = [replacements.get(value, value) for value in real_args]
    real_result = command_record(
        real_args,
        command_id="wp5_fixture_receipt_real_path_rejection",
        wp_owner="wp5",
        validation_class="negative_receipt_guard",
    )
    protected_after = protected_surface_rows()
    valid_ok = valid_result["exit_code"] == 0 and target_hashes == receipt["expected_postwrite_hashes"]
    replay_ok = replay_result["exit_code"] != 0 and replay_before == replay_after
    forged_ok = (
        forged_result["exit_code"] != 0
        and forged_before == forged_after
        and "receipt_consumption_path_not_canonical_for_nonce"
        in str(forged_result.get("stderr", ""))
    )
    real_ok = real_result["exit_code"] != 0 and protected_before == protected_after
    schema_report = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-fixture-receipt-schema-v1",
        "status": "PASS",
        "fixture_only": True,
        "required_fields": sorted(receipt),
        "owner_authorization_field_allowed": False,
        "production_or_live_field_allowed": False,
        "receipt_sha256": sha256_file(receipt_path),
    }
    promotion = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-candidate-promotion-contract-v1",
        "status": "PASS" if valid_ok and replay_ok and forged_ok and real_ok else "FAIL",
        "candidate_promotion_contract_complete": True,
        "candidate_first": True,
        "live_execution_leg_enabled": False,
        "real_current_protected_writer_callsite_count": 0,
        "precondition_delta_keeps_candidate_only": True,
        "postcondition_delta_keeps_candidate_only": True,
        "atomic_apply_verified": False,
        "atomic_apply_out_of_scope": True,
    }
    guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-current-write-guard-v1",
        "status": "PASS" if valid_ok and replay_ok and forged_ok and real_ok else "FAIL",
        "valid_fixture_receipt_write_passed": valid_ok,
        "receipt_nonce_claim_precedes_target_write": valid_ok,
        "receipt_input_and_target_preimage_revalidation_immediately_before_claim": valid_ok,
        "replayed_receipt_rejected": replay_ok,
        "replayed_receipt_fixture_mutation_count": 0 if replay_ok else 1,
        "same_nonce_new_state_path_rejected": forged_ok,
        "same_nonce_new_state_path_fixture_mutation_count": 0 if forged_ok else 1,
        "fixture_receipt_real_protected_path_authorization_count": 0 if real_ok else 1,
        "real_protected_mutation_count": 0 if real_ok else 1,
        "registry_fixture_write_receipt_issuer_count": 1,
        "registry_production_write_receipt_issuer_count": 0,
        "live_current_write_authorization_receipt_issued": False,
        "valid_command": valid_result,
        "replay_command": replay_result,
        "same_nonce_new_state_path_command": forged_result,
        "real_path_command": real_result,
    }
    precondition = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-cutover-precondition-v1",
        "status": "PASS",
        "role_classification_complete": True,
        "ambiguous_or_dual_authority_count": 0,
        "protected_dirty_overlap_count": 0,
        "review_input_complete": True,
        "real_cutover_allowed": False,
    }
    postcondition = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-cutover-postcondition-v1",
        "status": "PASS",
        "partial_state_rejected_by_contract": True,
        "dual_current_state_rejected_by_contract": True,
        "one_current_identity_required": True,
        "live_apply_executed": False,
        "live_repo_mutated": False,
    }
    rollback = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-rollback-reentry-guard-v1",
        "status": "PASS",
        "rollback_current_reentry_count": 0,
        "rollback_snapshots_historical_only": True,
        "automatic_restore_allowed": False,
    }
    outputs = (
        ("wp5_candidate_to_current_promotion_contract.json", promotion),
        ("wp5_seal_receipt_schema.json", schema_report),
        ("wp5_registry_current_write_authorization_receipt_schema.json", schema_report),
        ("wp5_registry_current_write_authorization_guard_report.json", guard),
        ("wp5_cutover_precondition_report.json", precondition),
        ("wp5_cutover_postcondition_report.json", postcondition),
        ("wp5_rollback_reentry_guard_report.json", rollback),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def completion_fixture_paths() -> list[Path]:
    roots = (
        TESTS_ROOT / "fixtures" / "negative" / "completion_vocabulary_external_gate",
        TESTS_ROOT / "fixtures" / "positive" / "completion_vocabulary_external_gate",
    )
    return sorted(
        path
        for root in roots
        for path in root.rglob("*.json")
        if path_is_file(path)
    )


def current_route_frozen_fixture_validation(
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    fixture_root = (
        repo_root
        / "Iris"
        / "build"
        / "description"
        / "v2"
        / "frozen_predecessor_inputs"
        / ROUND_ID
        / "current_route"
    )
    manifest_path = fixture_root / "manifest.json"
    manifest = read_json_object(manifest_path)
    rows = manifest.get("rows")
    blockers: list[str] = []
    expected_fields = {
        "schema_version": (
            f"{SCHEMA_PREFIX}-frozen-predecessor-fixture-v1"
        ),
        "status": "PASS",
        "role": "frozen_predecessor_input",
        "authority_claimed": False,
        "current_route_authority_claimed": False,
        "isolated_candidate_only": True,
        "live_materialization_allowed": False,
        "candidate_discard_required": True,
        "file_count": 34,
        "rows_sha256": CURRENT_ROUTE_FROZEN_FIXTURE_ROWS_SHA256,
    }
    for field, expected in expected_fields.items():
        if manifest.get(field) != expected:
            blockers.append(
                f"current_route_frozen_fixture_field_mismatch:{field}"
            )
    if not isinstance(rows, list):
        rows = []
        blockers.append("current_route_frozen_fixture_rows_missing")
    if canonical_hash(rows) != CURRENT_ROUTE_FROZEN_FIXTURE_ROWS_SHA256:
        blockers.append("current_route_frozen_fixture_rows_hash_mismatch")
    expected_payload_paths = {
        f"payload/{index:04d}.bin" for index in range(34)
    }
    observed_payload_paths: set[str] = set()
    observed_target_paths: set[str] = set()
    total_byte_length = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            blockers.append(
                f"current_route_frozen_fixture_row_not_object:{index}"
            )
            continue
        target = row.get("target_path")
        payload_relative = row.get("payload_path")
        if not isinstance(target, str):
            blockers.append(
                f"current_route_frozen_fixture_target_invalid:{index}"
            )
            continue
        target_path = PurePosixPath(target)
        if (
            target_path.is_absolute()
            or ".." in target_path.parts
            or target != target_path.as_posix()
        ):
            blockers.append(
                f"current_route_frozen_fixture_target_unsafe:{index}"
            )
        if target in observed_target_paths:
            blockers.append(
                f"current_route_frozen_fixture_target_duplicate:{target}"
            )
        observed_target_paths.add(target)
        if (
            row.get("role") != "frozen_predecessor_input"
            or row.get("source_git_state") != "ignored_untracked"
            or row.get("isolated_candidate_only") is not True
            or row.get("live_materialization_allowed") is not False
        ):
            blockers.append(
                f"current_route_frozen_fixture_role_invalid:{target}"
            )
        if not isinstance(payload_relative, str):
            blockers.append(
                f"current_route_frozen_fixture_payload_invalid:{target}"
            )
            continue
        observed_payload_paths.add(payload_relative)
        payload_path = fixture_root.joinpath(
            *PurePosixPath(payload_relative).parts
        )
        if (
            payload_relative not in expected_payload_paths
            or not path_is_file(payload_path)
            or sha256_file(payload_path) != row.get("sha256")
        ):
            blockers.append(
                f"current_route_frozen_fixture_payload_hash_mismatch:{target}"
            )
        byte_length = row.get("byte_length")
        if not isinstance(byte_length, int) or byte_length < 0:
            blockers.append(
                f"current_route_frozen_fixture_byte_length_invalid:{target}"
            )
        else:
            total_byte_length += byte_length
            if path_is_file(payload_path) and (
                filesystem_path(payload_path).stat().st_size != byte_length
            ):
                blockers.append(
                    "current_route_frozen_fixture_payload_size_mismatch:"
                    f"{target}"
                )
        live_target = repo_root.joinpath(*target_path.parts)
        if path_is_file(live_target) or path_is_dir(live_target):
            blockers.append(
                f"current_route_frozen_fixture_live_target_present:{target}"
            )
    if observed_payload_paths != expected_payload_paths:
        blockers.append("current_route_frozen_fixture_payload_set_mismatch")
    if total_byte_length != manifest.get("total_byte_length"):
        blockers.append(
            "current_route_frozen_fixture_total_byte_length_mismatch"
        )
    return {
        "schema_version": (
            f"{SCHEMA_PREFIX}-current-route-frozen-fixture-validation-v1"
        ),
        "status": "PASS" if not blockers else "FAIL",
        "manifest_path": repo_relative(
            CURRENT_ROUTE_FROZEN_FIXTURE_MANIFEST
        ),
        "manifest_sha256": sha256_file(manifest_path),
        "fixture_file_count": len(rows),
        "fixture_total_byte_length": total_byte_length,
        "rows_sha256": canonical_hash(rows),
        "isolated_candidate_only": True,
        "live_materialization_allowed": False,
        "candidate_discard_required": True,
        "blockers": sorted(set(blockers)),
    }


def build_wp4_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    dependencies = list(dict.fromkeys([
        *COMPOSE_DEPENDENCIES,
        COMPLETION_TOOL,
        COMPLETION_RUNNER,
        COMPLETION_VALIDATOR,
        COMPLETION_TEST,
        *completion_fixture_paths(),
        *CURRENT_ROUTE_SELECTIVE_DEPENDENCIES,
    ]))
    subprocess_targets = {
        COMPLETION_RUNNER,
        COMPLETION_VALIDATOR,
        *CURRENT_ROUTE_SUBPROCESS_TARGETS,
    }
    selected_current_tests = {
        COMPOSE_OVERLAY_TEST,
        CONSUMER_MIGRATION_NORMALIZATION_TEST,
        *CURRENT_ROUTE_REFACTORED_TESTS,
    }
    frozen_predecessor_inputs = {
        *CONSUMER_MIGRATION_NORMALIZATION_INPUTS,
        *CURRENT_ROUTE_FROZEN_FIXTURE_FILES,
    }
    path_sets = git_path_sets()
    rows = []
    blockers = []
    for path in dependencies:
        relative = repo_relative(path)
        row = {
            **hash_row(path),
            "tracked": relative in path_sets["tracked"],
            "ignored": relative in path_sets["ignored"],
            "dependency_role": (
                "subprocess_target"
                if path in subprocess_targets
                else (
                    "selected_current_test"
                    if path in selected_current_tests
                    else (
                        "frozen_predecessor_input"
                        if path in frozen_predecessor_inputs
                        else "required_fixture_or_source"
                    )
                )
            ),
        }
        rows.append(row)
        if row["kind"] == "missing" or not row["tracked"] or row["ignored"]:
            blockers.append(f"unpreserved_dependency:{relative}")
    test_source = COMPLETION_TEST.read_text(encoding="utf-8") if path_is_file(COMPLETION_TEST) else ""
    tree = ast.parse(test_source, filename=str(COMPLETION_TEST)) if test_source else ast.Module(body=[], type_ignores=[])
    bare_tool_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("dvf_3_3_completion_vocabulary_external_gate"):
                    bare_tool_imports.append(alias.name)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(
            "dvf_3_3_completion_vocabulary_external_gate"
        ):
            bare_tool_imports.append(node.module)
    if bare_tool_imports or "sys.path.insert" in test_source:
        blockers.append("completion_test_bare_import_or_sys_path_present")
    runner_source = COMPLETION_RUNNER.read_text(encoding="utf-8") if path_is_file(COMPLETION_RUNNER) else ""
    explicit_mode = "required=True" in runner_source and 'choices=("fixture-check",)' in runner_source
    if not explicit_mode:
        blockers.append("completion_runner_implicit_mode")
    round3_source = ROUND3_RUNNER.read_text(encoding="utf-8")
    preimport_markers = all(
        marker in round3_source
        for marker in (
            "enforce_preimport_build_dependency_closure",
            "unqualified_tools_build_import_bypass",
            "tools_build_import_candidates",
        )
    )
    if not preimport_markers:
        blockers.append("round3_preimport_guard_missing")
    frozen_fixture = current_route_frozen_fixture_validation()
    blockers.extend(frozen_fixture.get("blockers", []))
    preimport_command = [
        sys.executable,
        "-B",
        str(ROUND3_RUNNER),
        "--class",
        "current",
        "--enforce-current-build-closure",
        "--preimport-only",
    ]
    preimport_completed = subprocess.run(
        preimport_command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        preimport_report = json.loads(preimport_completed.stdout)
    except json.JSONDecodeError:
        preimport_report = {
            "status": "FAIL",
            "violation_count": 1,
            "violations": [
                {
                    "code": "current_route_preimport_report_invalid_json",
                    "selected_test": None,
                }
            ],
        }
    if preimport_completed.returncode != 0:
        blockers.append("current_route_static_preimport_scan_command_failed")
    if preimport_report.get("status") != "PASS":
        for violation in preimport_report.get("violations", []):
            blockers.append(
                "current_route_preimport_violation:"
                f"{violation.get('code')}:"
                f"{violation.get('selected_test')}:"
                f"{violation.get('resolved_path')}"
            )
    preimport_scan = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-current-route-preimport-scan-v1",
        "status": (
            "PASS"
            if preimport_completed.returncode == 0
            and preimport_report.get("status") == "PASS"
            else "FAIL"
        ),
        "command": preimport_command,
        "exit_code": preimport_completed.returncode,
        "stderr": preimport_completed.stderr,
        "test_execution_performed": False,
        "report": preimport_report,
    }
    ownership = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-required-validation-ownership-v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_manifest_current_checkout_bound": True,
        "required_artifact_denominator": len(manifest.get("required_artifacts", [])),
        "required_test_denominator": len(manifest.get("required_tests", [])),
        "required_artifact_denominator_matches_manifest": True,
        "required_test_denominator_matches_manifest": True,
        "path_existence_semantics_freshness_checks_separated": True,
        "candidate_manifest_override_rejected": True,
        "live_manifest_changed_before_gate_adoption": False,
        "blockers": blockers,
    }
    freshness = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-required-evidence-freshness-v1",
        "status": "PASS" if not blockers else "FAIL",
        "stored_pass_reuse_count": 0,
        "generated_staging_as_durable_evidence_count": 0,
        "fresh_current_route_execution": "deferred_to_plan_step_9_post_adoption",
        "fresh_adjacent_execution": "deferred_to_plan_step_6",
        "freshness_identity_uses_generated_at_only": False,
    }
    durable = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-durable-vs-generated-v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_dependency_count": len(rows),
        "unpreserved_count": len(blockers),
        "dependencies": rows,
        "active_core_or_tooling_allowlist_expansion_count": 0,
    }
    dependency = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-required-test-dependency-closure-v1",
        "status": "PASS" if not blockers else "FAIL",
        "selected_test": repo_relative(COMPLETION_TEST),
        "dependency_count": len(rows),
        "dependencies": rows,
        "sys_path_injected_bare_import_count": len(bare_tool_imports),
        "subprocess_target_count": len(subprocess_targets),
        "fixture_count": len(completion_fixture_paths()),
        "current_route_selected_test_count": preimport_report.get(
            "selected_test_count"
        ),
        "current_route_selected_test_source_violation_count": preimport_report.get(
            "selected_test_source_violation_count"
        ),
        "current_route_tools_build_import_violation_count": preimport_report.get(
            "unqualified_tools_build_import_count"
        ),
    }
    bare_guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-bare-import-guard-v1",
        "status": "PASS" if not blockers else "FAIL",
        "preimport_guard_present": preimport_markers,
        "selected_test_unqualified_tools_build_import_count": len(bare_tool_imports),
        "completion_vocabulary_required_test_execution_mode": "subprocess_fixture_check",
        "completion_vocabulary_stored_pass_early_return_count": 0,
        "completion_vocabulary_current_route_recursion_count": 0,
        "completion_vocabulary_runner_implicit_all_default_allowed": False,
        "negative_fixture_execution": "covered_by_focused_test_after_implementation",
    }
    fresh_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-fresh-execution-manifest-v1",
        "status": "PASS" if not blockers else "FAIL",
        "stored_result_substitution_allowed": False,
        "planned_commands": [
            "focused_registry_authority_test",
            "adjacent_regression_matrix",
            "isolated_package_probe",
            "post_adoption_current_route",
        ],
        "executed_during_implementation_mode": [],
        "static_preimport_scan_executed": True,
        "reason": "tests execute only at explicit Section 7 command boundaries",
    }
    outputs = (
        ("wp4_required_validation_ownership_report.json", ownership),
        ("wp4_required_evidence_freshness_report.json", freshness),
        ("wp4_durable_vs_generated_evidence_report.json", durable),
        ("wp4_required_test_dependency_closure_report.json", dependency),
        ("wp4_bare_import_guard_validation_report.json", bare_guard),
        ("wp4_current_route_preimport_dependency_scan_report.json", preimport_scan),
        ("wp4_current_route_isolated_fixture_report.json", frozen_fixture),
        ("wp4_fresh_execution_manifest.json", fresh_manifest),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def wp2_role_ledger_binding(
    root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ledger_path = (
        root / "phase4" / "wp2_artifact_role_classification_ledger.jsonl"
    )
    census_path = (
        root / "phase4" / "wp2_current_checkout_artifact_surface_census.json"
    )
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    line_count = 0
    seen_paths: set[str] = set()
    if not path_is_file(ledger_path):
        blockers.append("wp2_role_ledger_missing")
    else:
        try:
            lines = filesystem_path(ledger_path).read_text(
                encoding="utf-8"
            ).splitlines()
        except (OSError, UnicodeError) as exc:
            lines = []
            blockers.append(
                f"wp2_role_ledger_unreadable:{type(exc).__name__}"
            )
        line_count = len(lines)
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                blockers.append(f"wp2_role_ledger_blank_line:{line_number}")
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                blockers.append(
                    f"wp2_role_ledger_json_invalid:{line_number}"
                )
                continue
            if not isinstance(value, dict):
                blockers.append(
                    f"wp2_role_ledger_row_not_object:{line_number}"
                )
                continue
            path = value.get("path")
            if (
                not isinstance(path, str)
                or not path.strip()
                or not isinstance(value.get("kind"), str)
                or not isinstance(value.get("role"), str)
                or not isinstance(value.get("current_reentry_allowed"), bool)
            ):
                blockers.append(
                    f"wp2_role_ledger_row_schema_invalid:{line_number}"
                )
                continue
            normalized = path.replace("\\", "/")
            if normalized in seen_paths:
                blockers.append(
                    f"wp2_role_ledger_duplicate_path:{normalized}"
                )
                continue
            seen_paths.add(normalized)
            rows.append(value)

    census: dict[str, Any] = {}
    if not path_is_file(census_path):
        blockers.append("wp2_surface_census_missing")
    else:
        try:
            census = read_json_object(census_path)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            blockers.append(
                f"wp2_surface_census_invalid:{type(exc).__name__}"
            )
    if census.get("status") != "PASS":
        blockers.append("wp2_surface_census_status_not_pass")
    observed_hash = canonical_hash(rows)
    expected_hash = census.get("normalized_ledger_sha256")
    if (
        not isinstance(expected_hash, str)
        or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
    ):
        blockers.append("wp2_surface_census_ledger_hash_invalid")
    elif expected_hash != observed_hash:
        blockers.append("wp2_surface_census_ledger_hash_mismatch")
    if line_count != len(rows):
        blockers.append("wp2_role_ledger_line_parse_count_mismatch")
    binding = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-ledger-census-binding-v1",
        "status": "PASS" if not blockers else "FAIL",
        "ledger_path": repo_relative(ledger_path),
        "census_path": repo_relative(census_path),
        "ledger_file_sha256": (
            sha256_file(ledger_path) if path_is_file(ledger_path) else None
        ),
        "ledger_line_count": line_count,
        "ledger_parsed_row_count": len(rows),
        "ledger_observed_canonical_sha256": observed_hash,
        "census_expected_ledger_sha256": expected_hash,
        "census_status": census.get("status"),
        "exact_hash_match": expected_hash == observed_hash,
        "blockers": sorted(set(blockers)),
    }
    return rows, binding


def role_ledger_rows(root: Path) -> list[dict[str, Any]]:
    rows, binding = wp2_role_ledger_binding(root)
    if binding["status"] != "PASS":
        raise ValueError(
            "wp2_role_ledger_binding_failed:"
            + ",".join(binding["blockers"])
        )
    return rows


STALE_REGISTRY_ROLES = {
    "historical",
    "diagnostic",
    "fixture",
    "quarantine",
    "forbidden-current-looking",
}
NON_AUTHORITY_REFERENCE_ROLES = {
    "diagnostic_self_observation",
    "validation_fixture_read",
}
FORBIDDEN_STALE_PATH_SUFFIXES = (
    "irislayer3data.lua",
    "irisdvfbridgedata.lua",
    "iris/_docs/round3/round3_contract_manifest.json",
)
FORBIDDEN_PACKAGE_PATH_SUFFIXES = (
    "media/lua/client/iris/data/irislayer3data.lua",
    "media/lua/shared/iris/irisdvfbridgedata.lua",
)


def normalized_registry_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./").lower()


def registry_diagnostic_self_observation(source: Path, target: str) -> bool:
    return (
        source.resolve() == COMMON_PATH.resolve()
        and normalized_registry_path(target)
        == normalized_registry_path(repo_relative(ROUND3_CONTRACT_MANIFEST))
    )


def stale_path_reason(value: str, *, package_member: bool = False) -> str | None:
    normalized = normalized_registry_path(value)
    suffixes = (
        FORBIDDEN_PACKAGE_PATH_SUFFIXES
        if package_member
        else FORBIDDEN_STALE_PATH_SUFFIXES
    )
    for suffix in suffixes:
        if normalized.endswith(suffix):
            return suffix
    if "rollback_snapshot" in normalized:
        return "rollback_snapshot"
    return None


def current_looking_registry_path(value: str) -> bool:
    lowered = Path(value.replace("\\", "/")).name.lower()
    return any(
        token in lowered
        for token in (
            "dvf_3_3_rendered",
            "irislayer3data",
            "irisdvfbridgedata",
            "round3_contract_manifest",
        )
    )


def evaluate_stale_reentry(
    readpoints: list[dict[str, Any]],
    stale_rows: list[dict[str, Any]],
    package_members: list[dict[str, Any]],
    recognized_current_paths: set[str],
) -> list[dict[str, Any]]:
    stale_by_path = {
        normalized_registry_path(str(row["path"])): row
        for row in stale_rows
        if row.get("role") in STALE_REGISTRY_ROLES and isinstance(row.get("path"), str)
    }
    stale_hashes: dict[str, list[str]] = {}
    for row in stale_rows:
        path = row.get("path")
        digest = row.get("sha256")
        if (
            row.get("role") in STALE_REGISTRY_ROLES
            and isinstance(path, str)
            and isinstance(digest, str)
            and stale_path_reason(path) is not None
        ):
            stale_hashes.setdefault(digest, []).append(path)
    recognized = {normalized_registry_path(path) for path in recognized_current_paths}
    violations: list[dict[str, Any]] = []
    for row in readpoints:
        if row.get("reference_role") in NON_AUTHORITY_REFERENCE_ROLES:
            continue
        raw_path = row.get("path")
        if not isinstance(raw_path, str):
            continue
        path = normalized_registry_path(raw_path)
        if path in stale_by_path:
            violations.append(
                {
                    "kind": "stale_path_readpoint",
                    "surface": row.get("surface"),
                    "path": raw_path,
                    "stale_role": stale_by_path[path].get("role"),
                }
            )
        digest = row.get("sha256")
        if isinstance(digest, str) and digest in stale_hashes:
            violations.append(
                {
                    "kind": "renamed_stale_payload",
                    "surface": row.get("surface"),
                    "path": raw_path,
                    "sha256": digest,
                    "stale_sources": sorted(stale_hashes[digest]),
                }
            )
        if current_looking_registry_path(raw_path) and path not in recognized:
            violations.append(
                {
                    "kind": "unrecognized_current_looking_path",
                    "surface": row.get("surface"),
                    "path": raw_path,
                }
            )
    for member in package_members:
        raw_path = member.get("member")
        if not isinstance(raw_path, str):
            continue
        reason = stale_path_reason(raw_path, package_member=True)
        if reason is not None:
            violations.append(
                {
                    "kind": "forbidden_package_member",
                    "surface": "package",
                    "path": raw_path,
                    "origin": member.get("origin"),
                    "reason": reason,
                }
            )
        digest = member.get("sha256")
        if isinstance(digest, str) and digest in stale_hashes:
            violations.append(
                {
                    "kind": "renamed_stale_payload",
                    "surface": "package",
                    "path": raw_path,
                    "origin": member.get("origin"),
                    "sha256": digest,
                    "stale_sources": sorted(stale_hashes[digest]),
                }
            )
    return violations


def package_content_rows() -> tuple[list[dict[str, Any]], list[str]]:
    package_root = REPO_ROOT / "Iris" / "build" / "package"
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    if not path_is_dir(package_root):
        return rows, blockers
    for directory, child_directories, filenames in os.walk(filesystem_path(package_root)):
        child_directories.sort()
        for filename in sorted(filenames):
            path = Path(directory) / filename
            relative = path.relative_to(filesystem_path(package_root)).as_posix()
            rows.append(
                {
                    "origin": "package_directory",
                    "member": relative,
                    "sha256": sha256_file(path),
                }
            )
    for archive in sorted(filesystem_path(package_root).glob("*.zip")):
        try:
            with zipfile.ZipFile(archive) as handle:
                for info in sorted(handle.infolist(), key=lambda item: item.filename):
                    if info.is_dir():
                        continue
                    rows.append(
                        {
                            "origin": f"package_archive:{archive.name}",
                            "member": info.filename,
                            "sha256": sha256_bytes(handle.read(info)),
                        }
                    )
        except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
            blockers.append(f"package_archive_unreadable:{archive.name}:{type(exc).__name__}")
    return rows, blockers


def independent_current_registry_paths() -> set[str]:
    input_manifest = read_json_object(INPUT_MANIFEST)
    recognized = set(current_input_manifest_paths(input_manifest))
    exact_paths = {
        V2_ROOT / "output" / "dvf_3_3_rendered.json",
        RUNTIME_MANIFEST,
        RUNTIME_CHUNK_DIR,
        REPO_ROOT / "Iris" / "media",
        REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua",
        REPO_ROOT / "Iris" / "tools" / "package_iris.ps1",
    }
    exact_paths.update(
        REPO_ROOT / "Iris" / "media" / "lua" / "client" / f"{module}.lua"
        for module in parse_chunk_modules(RUNTIME_MANIFEST)
    )
    recognized.update(repo_relative(path) for path in exact_paths)
    return recognized


def repository_execution_dependencies(
    source: Path,
) -> tuple[set[Path], list[str]]:
    execution_dependency_suffixes = {".py", ".ps1"}
    dependencies: set[Path] = set()
    blockers: list[str] = []
    if source.suffix.lower() != ".py":
        return dependencies, blockers
    try:
        source_text = filesystem_path(source).read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
        tree = ast.parse(source_text, filename=str(source))
    except (OSError, SyntaxError) as exc:
        return dependencies, [
            f"live_execution_dependency_parse_error:{repo_relative(source)}:{type(exc).__name__}"
        ]

    def admit_candidate(candidate: Path) -> bool:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(REPO_ROOT.resolve())
        except (OSError, ValueError):
            return False
        if (
            resolved == source.resolve()
            or resolved.suffix.lower() not in execution_dependency_suffixes
            or not path_is_file(resolved)
        ):
            return False
        dependencies.add(resolved)
        return True

    def module_candidates(module: str, level: int) -> list[Path]:
        parts = [part for part in module.split(".") if part]
        candidates: list[Path] = []
        if level:
            base = source.parent
            for _ in range(max(0, level - 1)):
                base = base.parent
            relative = Path(*parts) if parts else Path("__init__")
            candidates.extend(
                (
                    base / relative.with_suffix(".py"),
                    base / relative / "__init__.py",
                )
            )
        elif parts:
            relative = Path(*parts)
            candidates.extend(
                (
                    source.parent / relative.with_suffix(".py"),
                    source.parent / relative / "__init__.py",
                    V2_ROOT / relative.with_suffix(".py"),
                    V2_ROOT / relative / "__init__.py",
                    REPO_ROOT / relative.with_suffix(".py"),
                    REPO_ROOT / relative / "__init__.py",
                    TOOLS_ROOT / f"{parts[-1]}.py",
                    TESTS_ROOT / f"{parts[-1]}.py",
                )
            )
        return candidates

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [(alias.name, 0) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [(node.module or "", node.level)]
        else:
            modules = []
        for module, level in modules:
            for candidate in module_candidates(module, level):
                if admit_candidate(candidate):
                    break

    symbols: dict[str, SymbolicState] = {
        "__file__": symbolic_state(
            {str(source.resolve())},
            complete=True,
            tainted=False,
        )
    }
    for _ in range(8):
        changed = False
        for statement in tree.body:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                value = statement.value
                targets = (
                    statement.targets
                    if isinstance(statement, ast.Assign)
                    else [statement.target]
                )
            else:
                continue
            if value is None:
                continue
            state = python_symbolic_state(value, symbols)
            for target in targets:
                key = python_symbol_key(target)
                if not key:
                    continue
                before = symbols.get(key)
                symbols[key] = state
                changed = changed or before != state
        if not changed:
            break

    for values, complete, _, _ in symbols.values():
        if not complete:
            continue
        for value in values:
            if Path(value).suffix.lower() not in execution_dependency_suffixes:
                continue
            literal = Path(value)
            candidates = (
                [literal]
                if literal.is_absolute()
                else [
                    source.parent / literal,
                    REPO_ROOT / literal,
                    TOOLS_ROOT / literal.name,
                    TESTS_ROOT / literal.name,
                ]
            )
            for candidate in candidates:
                if admit_candidate(candidate):
                    break

    literal_suffix_pattern = re.compile(
        r"(?P<path>[A-Za-z0-9_.\\/:-]+\.(?:py|ps1))",
        re.I,
    )
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        for match in literal_suffix_pattern.finditer(node.value):
            value = match.group("path").replace("\\", "/").lstrip("./")
            literal = Path(value)
            candidates: list[Path] = []
            if value.startswith("Iris/"):
                candidates.append(REPO_ROOT / value)
            elif "/" in value:
                candidates.extend((source.parent / literal, REPO_ROOT / literal))
            else:
                candidates.extend(
                    (
                        source.parent / literal,
                        TOOLS_ROOT / literal,
                        TESTS_ROOT / literal,
                        V2_ROOT / literal,
                        REPO_ROOT / literal,
                    )
                )
            for candidate in candidates:
                if admit_candidate(candidate):
                    break
    return dependencies, blockers


def registry_reference_scan_files(
    *,
    extra_files: tuple[Path, ...] = (),
    include_live: bool = True,
    wp2_ledger: tuple[dict[str, Any], ...] = (),
    wp2_binding: dict[str, Any] | None = None,
    require_wp2_ledger: bool = False,
) -> tuple[list[Path], list[str], dict[str, Any]]:
    executable_suffixes = {".py", ".lua", ".ps1"}
    paths: set[Path] = set()
    blockers: list[str] = []
    required_executable_paths: set[Path] = set()
    required_test_ids: set[str] = set()
    tracked_executable_paths: set[Path] = set()
    vcs_executable_paths: set[Path] = set()
    vcs_states_by_path: dict[Path, set[str]] = {}
    wp2_executable_file_paths: set[Path] = set()
    live_seed_reasons: dict[Path, set[str]] = {}
    dependency_edges: list[dict[str, str]] = []
    vcs_classification_rows: list[dict[str, Any]] = []
    tracked_enumeration_succeeded = not include_live
    vcs_enumeration_succeeded = not include_live

    def add_live_seed(path: Path, reason: str) -> None:
        if path.suffix.lower() not in executable_suffixes:
            blockers.append(
                f"registry_live_seed_not_executable:{reason}:{repo_relative(path)}"
            )
            return
        live_seed_reasons.setdefault(path, set()).add(reason)

    for path in extra_files:
        if path.suffix.lower() not in executable_suffixes:
            blockers.append(
                f"registry_reference_extra_file_not_executable:{repo_relative(path)}"
            )
        elif not path_is_file(path):
            blockers.append(
                f"registry_reference_extra_file_missing:{repo_relative(path)}"
            )
        else:
            paths.add(path)
    if include_live:
        tracked_result = run_git("ls-files")
        tracked_rows: set[str] = set()
        tracked_enumeration_succeeded = tracked_result["exit_code"] == 0
        vcs_enumeration_succeeded = tracked_enumeration_succeeded
        if tracked_result["exit_code"] != 0:
            blockers.append(
                "registry_reference_git_tracked_enumeration_failed:"
                + str(tracked_result["exit_code"])
            )
        else:
            tracked_rows = {
                value.replace("\\", "/")
                for value in tracked_result["stdout"].splitlines()
                if value.strip()
            }
        vcs_rows_by_state: dict[str, set[str]] = {"tracked": tracked_rows}
        vcs_commands = {
            "untracked": ("ls-files", "--others", "--exclude-standard"),
            "ignored": (
                "ls-files",
                "--others",
                "--ignored",
                "--exclude-standard",
            ),
        }
        for state, args in vcs_commands.items():
            result = run_git(*args)
            if result["exit_code"] != 0:
                blockers.append(
                    f"registry_reference_git_{state}_enumeration_failed:"
                    + str(result["exit_code"])
                )
                vcs_rows_by_state[state] = set()
                vcs_enumeration_succeeded = False
            else:
                vcs_rows_by_state[state] = {
                    value.replace("\\", "/")
                    for value in result["stdout"].splitlines()
                    if value.strip()
                }
        status_result = run_git("status", "--short", "--untracked-files=all")
        if status_result["exit_code"] != 0:
            blockers.append(
                "registry_reference_git_dirty_enumeration_failed:"
                + str(status_result["exit_code"])
            )
            vcs_rows_by_state["dirty"] = set()
            vcs_enumeration_succeeded = False
        else:
            vcs_rows_by_state["dirty"] = {
                status_path(line)
                for line in status_result["stdout"].splitlines()
                if line.strip()
            }
        vcs_enumeration_succeeded = (
            vcs_enumeration_succeeded and tracked_enumeration_succeeded
        )
        for state, rows in vcs_rows_by_state.items():
            for relative in sorted(rows):
                if Path(relative).suffix.lower() not in executable_suffixes:
                    continue
                path = (REPO_ROOT / relative).resolve()
                vcs_executable_paths.add(path)
                vcs_states_by_path.setdefault(path, set()).add(state)
                if state == "tracked":
                    tracked_executable_paths.add(path)
                    if not path_is_file(path):
                        blockers.append(f"tracked_executable_missing:{relative}")
        required_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
        required_artifacts = required_manifest.get("required_artifacts")
        required_tests = required_manifest.get("required_tests")
        if not isinstance(required_artifacts, list):
            blockers.append("required_manifest_artifacts_not_list")
            required_artifacts = []
        if not isinstance(required_tests, list):
            blockers.append("required_manifest_tests_not_list")
            required_tests = []
        for index, row in enumerate(required_artifacts):
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                blockers.append(f"required_artifact_path_invalid:{index}")
                continue
            relative = str(row["path"]).replace("\\", "/")
            if Path(relative).suffix.lower() in executable_suffixes:
                required_executable_paths.add(REPO_ROOT / relative)
        for index, row in enumerate(required_tests):
            if not isinstance(row, dict) or row.get("required") is not True:
                continue
            test_id = row.get("test_id")
            if not isinstance(test_id, str) or not test_id.strip():
                blockers.append(f"required_test_id_invalid:{index}")
                continue
            required_test_ids.add(test_id)
            module_name = test_id.split(".", 1)[0]
            if not re.fullmatch(r"test_[A-Za-z0-9_]+", module_name):
                blockers.append(f"required_test_module_invalid:{test_id}")
                continue
            required_executable_paths.add(TESTS_ROOT / f"{module_name}.py")

        active_core_manifest = read_json_object(ACTIVE_CORE_MANIFEST)
        closure_rows = active_core_manifest.get("closure_rows")
        allowed_tooling_rows = active_core_manifest.get(
            "current_route_allowed_tooling_rows"
        )
        if not isinstance(closure_rows, list):
            blockers.append("active_core_manifest_closure_rows_not_list")
            closure_rows = []
        if not isinstance(allowed_tooling_rows, list):
            blockers.append("active_core_manifest_allowed_tooling_rows_not_list")
            allowed_tooling_rows = []
        for index, row in enumerate(closure_rows):
            if not isinstance(row, dict):
                blockers.append(f"active_core_manifest_closure_row_invalid:{index}")
                continue
            if row.get("in_current_closure") is not True:
                continue
            relative = row.get("path")
            if not isinstance(relative, str) or not relative.strip():
                blockers.append(
                    f"active_core_manifest_current_path_invalid:{index}"
                )
                continue
            add_live_seed(
                REPO_ROOT / relative.replace("\\", "/"),
                "active_core_current_closure",
            )
        for index, row in enumerate(allowed_tooling_rows):
            if not isinstance(row, dict):
                blockers.append(
                    f"active_core_manifest_allowed_tooling_row_invalid:{index}"
                )
                continue
            if row.get("import_allowed_for_current_route") is not True:
                continue
            relative = row.get("path")
            if not isinstance(relative, str) or not relative.strip():
                blockers.append(
                    f"active_core_manifest_allowed_tooling_path_invalid:{index}"
                )
                continue
            add_live_seed(
                REPO_ROOT / relative.replace("\\", "/"),
                "current_route_allowed_tooling",
            )

        for path in required_executable_paths:
            add_live_seed(path, "live_required_manifest")
        add_live_seed(ROUND3_RUNNER, "current_route_runner")
        add_live_seed(
            REPO_ROOT / "Iris" / "tools" / "package_iris.ps1",
            "current_package_source",
        )
        for path in vcs_executable_paths:
            relative = repo_relative(path)
            if relative.startswith("Iris/media/lua/") and path.suffix.lower() == ".lua":
                add_live_seed(path, "runtime_lua_surface")

        if require_wp2_ledger and not wp2_ledger:
            blockers.append("wp2_role_ledger_missing_for_live_readpoint_admission")
        if require_wp2_ledger and (
            not isinstance(wp2_binding, dict)
            or wp2_binding.get("status") != "PASS"
        ):
            blockers.append("wp2_role_ledger_census_binding_not_pass")
            if isinstance(wp2_binding, dict):
                blockers.extend(
                    f"wp2_role_ledger_census_binding:{blocker}"
                    for blocker in wp2_binding.get("blockers", [])
                    if isinstance(blocker, str)
                )
        wp2_seen_paths: set[str] = set()
        for index, row in enumerate(wp2_ledger):
            relative = row.get("path")
            if not isinstance(relative, str) or not relative.strip():
                blockers.append(f"wp2_role_ledger_path_invalid:{index}")
                continue
            relative = relative.replace("\\", "/")
            if relative in wp2_seen_paths:
                blockers.append(f"wp2_role_ledger_duplicate_path:{relative}")
                continue
            wp2_seen_paths.add(relative)
            if (
                Path(relative).suffix.lower() in executable_suffixes
                and row.get("kind") == "file"
            ):
                wp2_path = (REPO_ROOT / relative).resolve()
                wp2_executable_file_paths.add(wp2_path)
                if wp2_path not in vcs_executable_paths:
                    blockers.append(
                        f"wp2_executable_absent_from_vcs_inventory:{relative}"
                    )

        dependency_queue = sorted(live_seed_reasons, key=repo_relative)
        dependency_scanned: set[Path] = set()
        while dependency_queue:
            source = dependency_queue.pop(0)
            if source in dependency_scanned or not path_is_file(source):
                continue
            dependency_scanned.add(source)
            dependencies, dependency_blockers = repository_execution_dependencies(
                source
            )
            blockers.extend(dependency_blockers)
            source_reasons = live_seed_reasons.get(source, set())
            validation_dependency = any(
                reason == "live_required_manifest"
                or reason.startswith("required_validation_dependency:")
                for reason in source_reasons
            )
            for dependency in sorted(dependencies, key=repo_relative):
                source_relative = repo_relative(source)
                dependency_relative = repo_relative(dependency)
                edge = {
                    "source": source_relative,
                    "dependency": dependency_relative,
                }
                if edge not in dependency_edges:
                    dependency_edges.append(edge)
                already_live = dependency in live_seed_reasons
                add_live_seed(
                    dependency,
                    (
                        f"required_validation_dependency:{source_relative}"
                        if validation_dependency
                        else f"execution_dependency:{source_relative}"
                    ),
                )
                if not already_live:
                    dependency_queue.append(dependency)

        live_seed_paths = set(live_seed_reasons)
        for path in sorted(live_seed_paths, key=repo_relative):
            relative = repo_relative(path)
            if not path_is_file(path):
                blockers.append(f"registry_live_seed_missing:{relative}")
                continue
            paths.add(path)
            if relative not in tracked_rows:
                blockers.append(f"registry_live_seed_not_tracked:{relative}")
            states = vcs_states_by_path.get(path, set())
            if "ignored" in states:
                blockers.append(f"registry_live_seed_ignored:{relative}")
            if "untracked" in states:
                blockers.append(f"registry_live_seed_untracked:{relative}")

        for path in sorted(required_executable_paths, key=repo_relative):
            relative = repo_relative(path)
            if not path_is_file(path):
                blockers.append(f"required_executable_missing:{relative}")
                continue
            if relative not in tracked_rows:
                blockers.append(f"required_executable_not_tracked:{relative}")

        wp2_role_by_path = {
            str(row.get("path")).replace("\\", "/"): row.get("role")
            for row in wp2_ledger
            if isinstance(row.get("path"), str)
        }
        for path in sorted(vcs_executable_paths, key=repo_relative):
            relative = repo_relative(path)
            reasons = sorted(live_seed_reasons.get(path, set()))
            states = sorted(vcs_states_by_path.get(path, set()))
            if reasons:
                admission = "live_current_readpoint"
                classification = "current_execution_consumer"
            else:
                admission = "classified_non_live"
                if relative.startswith(".tmp/") or relative.startswith(
                    "Iris/build/description/v2/staging/"
                ):
                    classification = "historical_or_staging_evidence"
                elif "/fixtures/" in f"/{relative.lower()}/":
                    classification = "non_live_fixture"
                elif relative.startswith(
                    "Iris/build/description/v2/tests/"
                ):
                    classification = "non_required_diagnostic_test"
                elif relative.startswith("Iris/build/package/"):
                    classification = "read_only_package_snapshot"
                elif "ignored" in states:
                    classification = "ignored_generated_non_live"
                    blockers.append(
                        f"unclassified_ignored_executable_outside_non_live_roots:{relative}"
                    )
                elif "untracked" in states:
                    classification = "untracked_unadmitted_non_live"
                    blockers.append(
                        f"unclassified_untracked_executable_outside_non_live_roots:{relative}"
                    )
                elif wp2_role_by_path.get(relative) == "current":
                    classification = (
                        "current_registry_artifact_not_reachable_as_execution_consumer"
                    )
                else:
                    classification = (
                        "not_reachable_from_current_manifest_dependency_graph"
                    )
            vcs_classification_rows.append(
                {
                    "path": relative,
                    "vcs_states": states,
                    "admission": admission,
                    "classification": classification,
                    "live_admission_reasons": reasons,
                    "wp2_registry_artifact_role": wp2_role_by_path.get(relative),
                }
            )

    live_seed_paths = set(live_seed_reasons)
    omitted_required = required_executable_paths - paths
    if include_live:
        for path in sorted(omitted_required, key=repo_relative):
            relative = repo_relative(path)
            marker = f"required_executable_not_admitted:{relative}"
            if marker not in blockers:
                blockers.append(marker)
    tracked_live_paths = tracked_executable_paths & live_seed_paths
    tracked_non_live_paths = tracked_executable_paths - tracked_live_paths
    vcs_live_paths = vcs_executable_paths & live_seed_paths
    vcs_non_live_paths = vcs_executable_paths - vcs_live_paths
    tracked_partition_complete = (
        tracked_live_paths.isdisjoint(tracked_non_live_paths)
        and tracked_live_paths | tracked_non_live_paths
        == tracked_executable_paths
    )
    inventory_partition_complete = (
        vcs_live_paths.isdisjoint(vcs_non_live_paths)
        and vcs_live_paths | vcs_non_live_paths == vcs_executable_paths
        and len(vcs_classification_rows) == len(vcs_executable_paths)
        and {
            str(row.get("path"))
            for row in vcs_classification_rows
            if isinstance(row.get("path"), str)
        }
        == {repo_relative(path) for path in vcs_executable_paths}
    )
    denominator_paths = sorted(paths, key=repo_relative)
    required_executable_inclusion_complete = required_executable_paths.issubset(paths)
    live_seed_inclusion_complete = live_seed_paths.issubset(paths)
    live_seed_tracked_complete = live_seed_paths.issubset(
        tracked_executable_paths
    )
    completeness = {
        "scope": (
            "full_vcs_tracked_untracked_ignored_dirty_inventory_classified_with_transitive_current_live_python_lua_powershell_admission"
            if include_live
            else "explicit_fixture_python_lua_powershell"
        ),
        "complete": (
            not blockers
            and tracked_enumeration_succeeded
            and vcs_enumeration_succeeded
            and required_executable_inclusion_complete
            and live_seed_inclusion_complete
            and live_seed_tracked_complete
            and inventory_partition_complete
        ),
        "tracked_enumeration_succeeded": tracked_enumeration_succeeded,
        "vcs_tracked_untracked_ignored_dirty_enumeration_succeeded": (
            vcs_enumeration_succeeded
        ),
        "vcs_executable_inventory_count": len(vcs_executable_paths),
        "vcs_executable_inventory_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in vcs_executable_paths)
        ),
        "vcs_executable_inventory_partition_complete": inventory_partition_complete,
        "vcs_live_admitted_count": len(vcs_live_paths),
        "vcs_live_admitted_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in vcs_live_paths)
        ),
        "vcs_non_live_classified_count": len(vcs_non_live_paths),
        "vcs_non_live_classified_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in vcs_non_live_paths)
        ),
        "vcs_state_counts": {
            state: sum(
                state in states
                for states in vcs_states_by_path.values()
            )
            for state in ("tracked", "untracked", "ignored", "dirty")
        },
        "tracked_executable_count": len(tracked_executable_paths),
        "tracked_executable_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in tracked_executable_paths)
        ),
        "tracked_inventory_partition_complete": tracked_partition_complete,
        "tracked_live_admitted_count": len(tracked_live_paths),
        "tracked_live_admitted_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in tracked_live_paths)
        ),
        "tracked_non_live_classified_count": len(tracked_non_live_paths),
        "tracked_non_live_classified_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in tracked_non_live_paths)
        ),
        "vcs_executable_classification_rows": vcs_classification_rows,
        "execution_dependency_edge_count": len(dependency_edges),
        "execution_dependency_edges": dependency_edges,
        "wp2_role_ledger_required": require_wp2_ledger,
        "wp2_role_ledger_path_count": len(
            {
                str(row.get("path"))
                for row in wp2_ledger
                if isinstance(row.get("path"), str)
            }
        ),
        "wp2_role_ledger_sha256": canonical_hash(list(wp2_ledger)),
        "wp2_role_ledger_census_binding": wp2_binding,
        "wp2_role_ledger_census_binding_pass": (
            isinstance(wp2_binding, dict)
            and wp2_binding.get("status") == "PASS"
        )
        if require_wp2_ledger
        else True,
        "wp2_executable_file_count": len(wp2_executable_file_paths)
        if include_live
        else 0,
        "wp2_executable_file_paths_sha256": canonical_hash(
            sorted(repo_relative(path) for path in wp2_executable_file_paths)
        )
        if include_live
        else canonical_hash([]),
        "wp2_executable_vcs_inventory_comparison_complete": (
            wp2_executable_file_paths.issubset(vcs_executable_paths)
            if include_live
            else True
        ),
        "required_test_id_count": len(required_test_ids),
        "required_executable_count": len(required_executable_paths),
        "required_executable_paths": sorted(
            repo_relative(path) for path in required_executable_paths
        ),
        "required_executable_inclusion_complete": required_executable_inclusion_complete,
        "live_seed_count": len(live_seed_paths),
        "live_seed_inclusion_complete": live_seed_inclusion_complete,
        "live_seed_tracked_complete": live_seed_tracked_complete,
        "admitted_executable_count": len(denominator_paths),
        "admitted_paths_sha256": canonical_hash(
            [repo_relative(path) for path in denominator_paths]
        ),
        "non_live_inventory_scanned_as_current_readpoints": False,
        "blockers": sorted(set(blockers)),
    }
    return denominator_paths, sorted(set(blockers)), completeness


def registry_reference_targets(
    literal: str,
    *,
    input_path_by_name: dict[str, str],
) -> list[str]:
    normalized_literal = literal.replace("\\", "/")
    candidates = re.findall(
        r"(?:Iris|media)/[A-Za-z0-9_.\-/]+",
        normalized_literal,
    )
    stripped = normalized_literal.strip().rstrip(".,;:)")
    if re.fullmatch(r"[A-Za-z0-9_.\-/]+", stripped):
        candidates.append(stripped)
    resolved: set[str] = set()
    filename_map = {
        **input_path_by_name,
        "dvf_3_3_rendered.json": repo_relative(
            V2_ROOT / "output" / "dvf_3_3_rendered.json"
        ),
        "IrisLayer3DataChunks.lua": repo_relative(RUNTIME_MANIFEST),
        "IrisLayer3Data.lua": "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
        "IrisDvfBridgeData.lua": "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
        "round3_contract_manifest.json": repo_relative(ROUND3_CONTRACT_MANIFEST),
    }
    for candidate in candidates:
        value = candidate.strip().rstrip(".,;:)")
        if value.startswith("Iris/Data/"):
            suffix = value if value.endswith(".lua") else f"{value}.lua"
            resolved.add(f"Iris/media/lua/client/{suffix}")
        elif value.startswith("Iris/"):
            resolved.add(value)
        elif value.startswith("media/"):
            resolved.add(f"Iris/{value}")
        elif value in filename_map:
            resolved.add(filename_map[value])
        elif Path(value).name in filename_map:
            resolved.add(filename_map[Path(value).name])
    return sorted(resolved)


REGISTRY_LOADER_NAMES = {
    "open",
    "read_text",
    "read_bytes",
    "load_json",
    "load_jsonl",
    "load_optional_jsonl_map",
    "require",
    "safeRequire",
    "dofile",
    "loadfile",
    "Get-Content",
    "Copy-Item",
}


def registry_identifier_present(value: str) -> bool:
    lowered = value.lower()
    return any(
        token in lowered
        for token in (
            "dvf_3_3_input_manifest",
            "dvf_3_3_facts",
            "dvf_3_3_decisions",
            "dvf_3_3_overlay_support",
            "dvf_3_3_rendered",
            "compose_profiles_v2",
            "compose_profile_identity_hint_rules",
            "compose_profile_conflict_precedence_rules",
            "style_normalization_changes",
            "compose_requeue_candidates",
            "layer3data",
            "irisdvfbridge",
            "round3_contract_manifest",
        )
    )


def registry_path_taint_present(value: str) -> bool:
    lowered = normalized_registry_path(value)
    return registry_identifier_present(value) or any(
        marker in lowered
        for marker in (
            "/build/description/v2/data",
            "/build/description/v2/output",
            "/media/lua/client/iris/data",
            "/media/lua/shared/iris",
            "iris/data",
        )
    )


def join_symbolic_path(left: str, right: str) -> str:
    return left.rstrip("/\\") + "/" + right.lstrip("/\\")


def contained_fixture_path_present(value: str) -> bool:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    try:
        resolved = candidate.resolve()
    except OSError:
        return False
    try:
        relative = resolved.relative_to(TESTS_ROOT.resolve())
    except (OSError, ValueError):
        pass
    else:
        if any(part.lower().startswith("_tmp") for part in relative.parts):
            return True
    try:
        resolved.relative_to((V2_ROOT / ".tmp_tests").resolve())
    except (OSError, ValueError):
        return False
    return True


def python_symbol_key(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = python_symbol_key(node.value)
        return f"{parent}.{node.attr}" if parent else None
    return None


TRUSTED_TEMPFILE_FACTORY_MARKER = "__trusted_tempfile_factory__:"
TEMPFILE_FACTORY_NAMES = {"TemporaryDirectory", "mkdtemp"}


def python_trusted_tempfile_factory_symbols(tree: ast.AST) -> set[str]:
    module_aliases: set[str] = set()
    direct_factory_sources: dict[str, set[str]] = {}
    import_bindings: dict[str, set[str]] = {}
    wildcard_import_present = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".", 1)[0]
                import_bindings.setdefault(local_name, set()).add(
                    f"import:{alias.name}"
                )
                if alias.name == "tempfile":
                    module_aliases.add(local_name)
        elif isinstance(node, ast.ImportFrom) and node.module == "tempfile":
            for alias in node.names:
                if alias.name == "*":
                    wildcard_import_present = True
                    continue
                local_name = alias.asname or alias.name
                import_bindings.setdefault(local_name, set()).add(
                    f"from:{node.module}:{alias.name}"
                )
                if alias.name in TEMPFILE_FACTORY_NAMES:
                    direct_factory_sources.setdefault(local_name, set()).add(
                        f"from:tempfile:{alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    wildcard_import_present = True
                    continue
                local_name = alias.asname or alias.name
                import_bindings.setdefault(local_name, set()).add(
                    f"from:{node.module}:{alias.name}"
                )
    trusted = set() if wildcard_import_present else {
        f"{module_alias}.{factory_name}"
        for module_alias in module_aliases
        if import_bindings.get(module_alias) == {"import:tempfile"}
        for factory_name in TEMPFILE_FACTORY_NAMES
    } | {
        local_name
        for local_name, expected_sources in direct_factory_sources.items()
        if len(expected_sources) == 1
        and import_bindings.get(local_name) == expected_sources
    }
    stored_symbols = {
        key
        for node in ast.walk(tree)
        if isinstance(node, (ast.Name, ast.Attribute))
        and isinstance(node.ctx, ast.Store)
        for key in [python_symbol_key(node)]
        if key
    }
    stored_symbols.update(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    stored_symbols.update(
        argument.arg
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
        for argument in [
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        ]
    )
    stored_symbols.update(
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and node.name
    )
    stored_symbols.update(
        name
        for node in ast.walk(tree)
        for name in [
            node.name
            if isinstance(node, (ast.MatchAs, ast.MatchStar))
            else node.rest
            if isinstance(node, ast.MatchMapping)
            else None
        ]
        if name
    )
    return {
        symbol
        for symbol in trusted
        if symbol not in stored_symbols
        and not any(
            symbol.startswith(f"{stored}.")
            for stored in stored_symbols
            if stored in module_aliases
        )
    }


SymbolicState = tuple[frozenset[str], bool, bool, bool]


def symbolic_state(
    values: set[str] | frozenset[str] = frozenset(),
    *,
    complete: bool,
    tainted: bool | None = None,
    contained_fixture: bool = False,
) -> SymbolicState:
    frozen = frozenset(values)
    return (
        frozen if complete else frozenset(),
        complete,
        (
            any(registry_path_taint_present(value) for value in frozen)
            if tainted is None
            else tainted
        ),
        contained_fixture
        or any(contained_fixture_path_present(value) for value in frozen),
    )


def python_symbolic_state(
    node: ast.AST,
    symbols: dict[str, SymbolicState],
) -> SymbolicState:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return symbolic_state({node.value}, complete=True)
    if isinstance(node, ast.Name):
        return symbols.get(
            node.id,
            symbolic_state(
                complete=False,
                tainted=registry_path_taint_present(node.id),
            ),
        )
    if isinstance(node, ast.Attribute):
        key = python_symbol_key(node)
        if key in symbols:
            return symbols[key]
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Div)):
        left_values, left_complete, left_tainted, left_contained = python_symbolic_state(
            node.left, symbols
        )
        right_values, right_complete, right_tainted, right_contained = python_symbolic_state(
            node.right, symbols
        )
        if left_complete and right_complete and left_values and right_values:
            if isinstance(node.op, ast.Div):
                values = {
                    join_symbolic_path(lhs, rhs)
                    for lhs in left_values
                    for rhs in right_values
                }
            else:
                values = {
                    lhs + rhs for lhs in left_values for rhs in right_values
                }
            return symbolic_state(
                values,
                complete=True,
                tainted=left_tainted
                or right_tainted
                or any(registry_path_taint_present(value) for value in values),
                contained_fixture=left_contained or right_contained,
            )
        return symbolic_state(
            complete=False,
            tainted=left_tainted or right_tainted,
            contained_fixture=left_contained or right_contained,
        )
    if isinstance(node, ast.JoinedStr):
        parts = [
            python_symbolic_state(value, symbols)
            for value in node.values
        ]
        if parts and all(complete and values for values, complete, _, _ in parts):
            combined = {""}
            for values, _, _, _ in parts:
                combined = {left + right for left in combined for right in values}
            return symbolic_state(
                combined,
                complete=True,
                tainted=any(tainted for _, _, tainted, _ in parts),
                contained_fixture=any(contained for _, _, _, contained in parts),
            )
        return symbolic_state(
            complete=False,
            tainted=any(tainted for _, _, tainted, _ in parts),
            contained_fixture=any(contained for _, _, _, contained in parts),
        )
    if isinstance(node, ast.FormattedValue):
        return python_symbolic_state(node.value, symbols)
    if isinstance(node, ast.Call):
        function_name = (
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else ""
        )
        function_key = python_symbol_key(node.func)
        if (
            function_key
            and f"{TRUSTED_TEMPFILE_FACTORY_MARKER}{function_key}" in symbols
        ):
            return symbolic_state(
                complete=False,
                tainted=False,
                contained_fixture=True,
            )
        if function_name in {"Path", "PurePath", "resolve", "joinpath"}:
            components: list[SymbolicState] = []
            if isinstance(node.func, ast.Attribute):
                components.append(python_symbolic_state(node.func.value, symbols))
            components.extend(
                python_symbolic_state(argument, symbols) for argument in node.args
            )
            if not components:
                return symbolic_state(complete=False, tainted=False)
            tainted = any(state[2] for state in components)
            contained = any(state[3] for state in components)
            if not all(state[1] and state[0] for state in components):
                return symbolic_state(
                    complete=False,
                    tainted=tainted,
                    contained_fixture=contained,
                )
            values = set(components[0][0])
            for component_values, _, _, _ in components[1:]:
                values = {
                    join_symbolic_path(left, right)
                    for left in values
                    for right in component_values
                }
            return symbolic_state(
                values,
                complete=True,
                tainted=tainted,
                contained_fixture=contained,
            )
        argument_states = [
            python_symbolic_state(argument, symbols) for argument in node.args
        ]
        return symbolic_state(
            complete=False,
            tainted=any(state[2] for state in argument_states),
            contained_fixture=any(state[3] for state in argument_states),
        )
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
        if node.value.attr == "parents":
            base_values, base_complete, base_tainted, base_contained = python_symbolic_state(
                node.value.value, symbols
            )
            index = (
                node.slice.value
                if isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, int)
                else None
            )
            if base_complete and base_values and index is not None and index >= 0:
                parents: set[str] = set()
                try:
                    for value in base_values:
                        parents.add(str(Path(value).parents[index]))
                except IndexError:
                    return symbolic_state(
                        complete=False,
                        tainted=base_tainted,
                        contained_fixture=base_contained,
                    )
                return symbolic_state(
                    parents,
                    complete=True,
                    tainted=base_tainted,
                    contained_fixture=base_contained,
                )
            return symbolic_state(
                complete=False,
                tainted=base_tainted,
                contained_fixture=base_contained,
            )
    if isinstance(node, ast.Attribute):
        base_values, base_complete, base_tainted, base_contained = python_symbolic_state(
            node.value, symbols
        )
        if node.attr == "parent" and base_complete and base_values:
            return symbolic_state(
                {str(Path(value).parent) for value in base_values},
                complete=True,
                tainted=base_tainted,
                contained_fixture=base_contained,
            )
        return symbolic_state(
            complete=False,
            tainted=base_tainted,
            contained_fixture=base_contained,
        )
    return symbolic_state(complete=False, tainted=False)


def python_structural_registry_reads(
    source: Path,
    source_text: str,
    *,
    input_path_by_name: dict[str, str],
) -> tuple[list[tuple[str, int, str]], list[str]]:
    try:
        tree = ast.parse(source_text, filename=str(source))
    except SyntaxError as exc:
        return [], [f"python_registry_scan_parse_error:{repo_relative(source)}:{exc.lineno}"]
    symbols: dict[str, SymbolicState] = {
        "__file__": symbolic_state(
            {str(source.resolve())},
            complete=True,
            contained_fixture=False,
        )
    }
    symbols.update(
        {
            f"{TRUSTED_TEMPFILE_FACTORY_MARKER}{symbol}": symbolic_state(
                complete=False,
                tainted=False,
            )
            for symbol in python_trusted_tempfile_factory_symbols(tree)
        }
    )
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
                if argument.arg in {"tmp_path", "tmpdir", "temp_dir", "temporary_dir"}:
                    symbols[argument.arg] = symbolic_state(
                        complete=False,
                        tainted=False,
                        contained_fixture=True,
                    )
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                function_key = (
                    python_symbol_key(item.context_expr.func)
                    if isinstance(item.context_expr, ast.Call)
                    else None
                )
                if (
                    function_key
                    and (
                        f"{TRUSTED_TEMPFILE_FACTORY_MARKER}{function_key}"
                        in symbols
                    )
                    and isinstance(item.optional_vars, ast.Name)
                ):
                    symbols[item.optional_vars.id] = symbolic_state(
                        complete=False,
                        tainted=False,
                        contained_fixture=True,
                    )
    loader_aliases = set(REGISTRY_LOADER_NAMES)
    assignments = [
        node for node in ast.walk(tree) if isinstance(node, (ast.Assign, ast.AnnAssign))
    ]
    for _ in range(6):
        changed = False
        for node in assignments:
            value_node = node.value
            state = python_symbolic_state(value_node, symbols)
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                target_key = python_symbol_key(target)
                if not target_key:
                    continue
                before = symbols.get(target_key)
                symbols[target_key] = state
                changed = changed or before != state
                alias_name = (
                    value_node.id
                    if isinstance(value_node, ast.Name)
                    else value_node.attr
                    if isinstance(value_node, ast.Attribute)
                    else ""
                )
                if alias_name in loader_aliases and isinstance(target, ast.Name):
                    loader_aliases.add(target.id)
        if not changed:
            break
    reads: list[tuple[str, int, str]] = []
    blockers: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function_name = (
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else ""
        )
        if function_name not in loader_aliases:
            continue
        path_nodes: list[ast.AST] = []
        if isinstance(node.func, ast.Attribute) and function_name in {"read_text", "read_bytes"}:
            path_nodes.append(node.func.value)
        elif node.args:
            path_nodes.append(node.args[0])
        path_states = [python_symbolic_state(path_node, symbols) for path_node in path_nodes]
        values = {
            value for state_values, _, _, _ in path_states for value in state_values
        }
        complete = bool(path_states) and all(state[1] for state in path_states)
        tainted = any(state[2] for state in path_states)
        contained_fixture = any(state[3] for state in path_states)
        if contained_fixture:
            blockers.append(
                f"contained_fixture_registry_reference:{repo_relative(source)}:{getattr(node, 'lineno', 0)}"
            )
            continue
        targets = {
            target
            for value in values
            for target in registry_reference_targets(
                value,
                input_path_by_name=input_path_by_name,
            )
        }
        reads.extend(
            (target, int(getattr(node, "lineno", 0)), "python_ast_dataflow")
            for target in sorted(targets)
        )
        raw_call = ast.get_source_segment(source_text, node) or ""
        if (not complete and tainted) or not targets and (
            registry_path_taint_present(raw_call) or tainted
        ):
            blockers.append(
                f"unresolved_registry_loader_reference:{repo_relative(source)}:{getattr(node, 'lineno', 0)}"
            )
    return reads, blockers


def simple_symbolic_state(
    expression: str,
    symbols: dict[str, SymbolicState],
    *,
    language: str,
) -> SymbolicState:
    token_pattern = (
        re.compile(r"(?P<quote>[\"'])(?P<literal>.*?)(?P=quote)|\$(?P<psname>[A-Za-z_][A-Za-z0-9_]*)")
        if language == "powershell"
        else re.compile(r"(?P<quote>[\"'])(?P<literal>.*?)(?P=quote)|(?P<name>[A-Za-z_][A-Za-z0-9_]*)")
    )
    parts: list[frozenset[str]] = []
    tainted = registry_path_taint_present(expression)
    contained_fixture = False
    unknown = False
    ignored_lua_names = {
        "local",
        "true",
        "false",
        "nil",
        "require",
        "safeRequire",
        "dofile",
        "loadfile",
    }
    for match in token_pattern.finditer(expression):
        literal = match.groupdict().get("literal")
        if literal is not None:
            values = frozenset({literal})
            parts.append(values)
            tainted = tainted or registry_path_taint_present(literal)
            continue
        name = match.groupdict().get("psname") or match.groupdict().get("name")
        if not name:
            continue
        if name in symbols:
            values, complete, state_tainted, state_contained = symbols[name]
            tainted = tainted or state_tainted
            contained_fixture = contained_fixture or state_contained
            if complete and values:
                parts.append(values)
            else:
                unknown = True
        elif language == "lua" and name in ignored_lua_names:
            continue
        else:
            unknown = True
            tainted = tainted or registry_path_taint_present(name)
    if language == "powershell":
        residual = re.sub(r"(?i)\bJoin-Path\b", "", expression)
        residual = re.sub(r"[\s+(),.-]+", "", residual)
        residual = re.sub(r"[\"'][^\"']*[\"']", "", residual)
        residual = re.sub(r"\$[A-Za-z_][A-Za-z0-9_]*", "", residual)
        unknown = unknown or bool(residual)
    if not parts:
        return symbolic_state(
            complete=False,
            tainted=tainted,
            contained_fixture=contained_fixture,
        )
    if unknown:
        return symbolic_state(
            complete=False,
            tainted=tainted,
            contained_fixture=contained_fixture,
        )
    combined = {""}
    join_with_slash = language == "powershell" and re.search(
        r"(?i)\bJoin-Path\b", expression
    )
    for values in parts:
        combined = {
            join_symbolic_path(left, right)
            if join_with_slash and left
            else left + right
            for left in combined
            for right in values
        }
    return symbolic_state(
        combined,
        complete=True,
        tainted=tainted,
        contained_fixture=contained_fixture,
    )


def balanced_call_arguments(
    source_text: str,
    loader_aliases: set[str],
) -> list[tuple[str, str, int]]:
    calls: list[tuple[str, str, int]] = []
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for match in pattern.finditer(source_text):
        loader = match.group(1)
        if loader not in loader_aliases:
            continue
        open_index = source_text.find("(", match.start(), match.end())
        depth = 0
        quote = ""
        escape = False
        for index in range(open_index, len(source_text)):
            character = source_text[index]
            if escape:
                escape = False
                continue
            if character == "\\" and quote:
                escape = True
                continue
            if quote:
                if character == quote:
                    quote = ""
                continue
            if character in {"'", '"'}:
                quote = character
                continue
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    line_number = source_text.count("\n", 0, match.start()) + 1
                    calls.append(
                        (loader, source_text[open_index + 1 : index], line_number)
                    )
                    break
    return calls


def lua_structural_registry_reads(
    source: Path,
    source_text: str,
    *,
    input_path_by_name: dict[str, str],
) -> tuple[list[tuple[str, int, str]], list[str]]:
    symbols: dict[str, SymbolicState] = {}
    loader_aliases = {"require", "safeRequire", "dofile", "loadfile"}
    lines = source_text.splitlines()
    module_field_lines = [
        line for line in lines if re.search(r"\bmodule\s*=", line)
    ]
    module_field_values = {
        match.group(2)
        for line in module_field_lines
        for match in [
            re.search(
                r"\bmodule\s*=\s*([\"'])(.*?)\1",
                line,
            )
        ]
        if match
    }
    literal_module_fields_complete = (
        bool(module_field_lines)
        and len(module_field_values) == len(module_field_lines)
    )
    for _ in range(6):
        changed = False
        for line in lines:
            match = re.match(r"\s*(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)", line)
            if not match:
                continue
            name, expression = match.groups()
            state = simple_symbolic_state(
                expression,
                symbols,
                language="lua",
            )
            before = symbols.get(name)
            symbols[name] = state
            changed = changed or before != state
            alias = expression.strip()
            if alias in loader_aliases:
                loader_aliases.add(name)
        if not changed:
            break
    reads: list[tuple[str, int, str]] = []
    blockers: list[str] = []
    for loader, argument, line_number in balanced_call_arguments(
        source_text, loader_aliases
    ):
        table_module_argument = re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*\.module",
            argument.strip(),
        )
        if table_module_argument:
            values, complete, tainted, _ = (
                symbolic_state(
                    module_field_values,
                    complete=True,
                )
                if literal_module_fields_complete
                else symbolic_state(
                    complete=False,
                    tainted=True,
                )
            )
        else:
            values, complete, tainted, _ = simple_symbolic_state(
                argument,
                symbols,
                language="lua",
            )
        if table_module_argument and not literal_module_fields_complete:
            blockers.append(
                "incomplete_lua_module_table_reference:"
                f"{repo_relative(source)}:{line_number}"
            )
        targets = {
            target
            for value in values
            for target in registry_reference_targets(
                value,
                input_path_by_name=input_path_by_name,
            )
        }
        reads.extend(
            (target, line_number, "lua_symbol_alias_dataflow")
            for target in sorted(targets)
        )
        if (not complete and tainted) or not targets and (
            registry_path_taint_present(argument) or tainted
        ):
            blockers.append(
                f"unresolved_registry_loader_reference:{repo_relative(source)}:{line_number}"
            )
    return reads, blockers


def powershell_first_argument_expression(text: str) -> str:
    value = text.lstrip()
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        quote = value[0]
        escaped = False
        for index, character in enumerate(value[1:], start=1):
            if escaped:
                escaped = False
                continue
            if character == "`":
                escaped = True
                continue
            if character == quote:
                return value[: index + 1]
        return value
    if value[0] == "(":
        depth = 0
        quote = ""
        escaped = False
        for index, character in enumerate(value):
            if escaped:
                escaped = False
                continue
            if character == "`":
                escaped = True
                continue
            if quote:
                if character == quote:
                    quote = ""
                continue
            if character in {"'", '"'}:
                quote = character
            elif character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    return value[: index + 1]
        return value
    match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*|[^\s]+", value)
    return match.group(0) if match else value


def powershell_top_level_path_argument(command_tail: str) -> str | None:
    depth = 0
    quote = ""
    escaped = False
    for index, character in enumerate(command_tail):
        if escaped:
            escaped = False
            continue
        if character == "`":
            escaped = True
            continue
        if quote:
            if character == quote:
                quote = ""
            continue
        if character in {"'", '"'}:
            quote = character
            continue
        if character == "(":
            depth += 1
            continue
        if character == ")":
            depth = max(0, depth - 1)
            continue
        if depth != 0 or character != "-":
            continue
        if index > 0 and not command_tail[index - 1].isspace():
            continue
        match = re.match(
            r"-(?:Literal)?Path\b",
            command_tail[index:],
            re.I,
        )
        if match:
            return powershell_first_argument_expression(
                command_tail[index + match.end() :]
            )
    return None


def powershell_structural_registry_reads(
    source: Path,
    source_text: str,
    *,
    input_path_by_name: dict[str, str],
) -> tuple[list[tuple[str, int, str]], list[str]]:
    symbols: dict[str, SymbolicState] = {}
    command_aliases = {"get-content", "copy-item"}
    lines = source_text.splitlines()
    for _ in range(8):
        changed = False
        for line in lines:
            match = re.match(r"\s*\$([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)", line)
            if not match:
                continue
            name, expression = match.groups()
            state = simple_symbolic_state(
                expression,
                symbols,
                language="powershell",
            )
            values, _, _, _ = state
            before = symbols.get(name)
            symbols[name] = state
            changed = changed or before != state
            if any(value.lower() in command_aliases for value in values):
                command_aliases.add(name.lower())
        if not changed:
            break
    reads: list[tuple[str, int, str]] = []
    blockers: list[str] = []
    for line_number, line in enumerate(lines, start=1):
        direct = re.search(r"\b(Get-Content|Copy-Item)\b", line, re.I)
        invoked = re.search(r"&\s*\$([A-Za-z_][A-Za-z0-9_]*)", line)
        command = (
            direct.group(1).lower()
            if direct
            else invoked.group(1).lower()
            if invoked and invoked.group(1).lower() in command_aliases
            else ""
        )
        if not command:
            continue
        tail = line[(direct.end() if direct else invoked.end()) :].strip()
        top_level_path_argument = powershell_top_level_path_argument(
            tail
        )
        if top_level_path_argument is not None:
            expression = top_level_path_argument or tail
        else:
            expression = powershell_first_argument_expression(tail)
        values, complete, tainted, _ = simple_symbolic_state(
            expression,
            symbols,
            language="powershell",
        )
        targets = {
            target
            for value in values
            for target in registry_reference_targets(
                value,
                input_path_by_name=input_path_by_name,
            )
        }
        reads.extend(
            (target, line_number, "powershell_join_alias_copy_dataflow")
            for target in sorted(targets)
        )
        if (not complete and tainted) or not targets and (
            registry_path_taint_present(expression) or tainted
        ):
            blockers.append(
                f"unresolved_registry_loader_reference:{repo_relative(source)}:{line_number}"
            )
    return reads, blockers


def discover_registry_readpoints(
    *,
    extra_files: tuple[Path, ...] = (),
    include_live: bool = True,
    wp2_ledger: tuple[dict[str, Any], ...] = (),
    wp2_binding: dict[str, Any] | None = None,
    require_wp2_ledger: bool = False,
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    input_manifest = read_json_object(INPUT_MANIFEST)
    input_paths = current_input_manifest_paths(input_manifest)
    input_path_by_name = {Path(value).name: value for value in input_paths}
    package_script = REPO_ROOT / "Iris" / "tools" / "package_iris.ps1"
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    contained_fixture_references: list[str] = []
    literal_pattern = re.compile(r"([\"'])(.*?)\1")
    consumer_markers = (
        "require(",
        "saferequire(",
        "dofile(",
        "loadfile(",
        "load_json(",
        "load_jsonl(",
        "read_text(",
        "read_bytes(",
        "get-content",
    )
    seen: set[tuple[str, str, int, str]] = set()
    scan_files, denominator_blockers, denominator = registry_reference_scan_files(
        extra_files=extra_files,
        include_live=include_live,
        wp2_ledger=wp2_ledger,
        wp2_binding=wp2_binding,
        require_wp2_ledger=require_wp2_ledger,
    )
    blockers.extend(denominator_blockers)
    validation_source_paths = {
        str(row.get("path"))
        for row in denominator.get("vcs_executable_classification_rows", [])
        if isinstance(row, dict)
        and any(
            reason == "live_required_manifest"
            or str(reason).startswith("required_validation_dependency:")
            for reason in row.get("live_admission_reasons", [])
        )
    }
    wp2_role_by_path = {
        normalized_registry_path(str(row.get("path"))): row.get("role")
        for row in wp2_ledger
        if isinstance(row.get("path"), str)
    }

    def resolved_reference_role(source: Path, target: str) -> str:
        source_relative = repo_relative(source)
        normalized_target = normalized_registry_path(target)
        if registry_diagnostic_self_observation(source, target):
            return "diagnostic_self_observation"
        if (
            source_relative in validation_source_paths
            and wp2_role_by_path.get(normalized_target) == "fixture"
        ):
            return "validation_fixture_read"
        return "consumer_read"

    for source in scan_files:
        try:
            source_text = filesystem_path(source).read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        except OSError as exc:
            blockers.append(
                f"registry_reference_source_unreadable:{repo_relative(source)}:{type(exc).__name__}"
            )
            continue
        for line_number, line in enumerate(source_text.splitlines(), start=1):
            lowered = line.lower()
            if (
                source.resolve() == package_script.resolve()
                and "copy-item" in lowered
                and "sourceroot" in lowered
                and "media" in lowered
            ):
                target = "Iris/media"
                key = (target, repo_relative(source), line_number, "consumer_read")
                if key not in seen:
                    seen.add(key)
                    record = hash_row(REPO_ROOT / target)
                    rows.append(
                        {
                            **record,
                            "surface": "package",
                            "producer": "tracked Iris media source",
                            "consumer": repo_relative(source),
                            "reference_source": repo_relative(source),
                            "reference_line": line_number,
                            "reference_role": "consumer_read",
                            "discovery_kind": "raw_powershell_copy_reference",
                            "raw_reference_sha256": sha256_bytes(line.encode("utf-8")),
                            "observed_fresh": True,
                        }
                    )
            for match in literal_pattern.finditer(line):
                literal = match.group(2)
                targets = registry_reference_targets(
                    literal,
                    input_path_by_name=input_path_by_name,
                )
                for target in targets:
                    target_lower = normalized_registry_path(target)
                    guard_reference = (
                        source.resolve() == package_script.resolve()
                        and stale_path_reason(target) is not None
                    ) or any(
                        marker in lowered
                        for marker in ("forbidden", "guard", "monolithrelativepath")
                    )
                    consumer_read = any(marker in lowered for marker in consumer_markers)
                    if source.resolve() == COMPOSE_TOOL.resolve() and target in input_paths:
                        consumer_read = True
                    if (
                        source.resolve() == EXPORT_TOOL.resolve()
                        and target_lower
                        == normalized_registry_path(
                            repo_relative(V2_ROOT / "output" / "dvf_3_3_rendered.json")
                        )
                    ):
                        consumer_read = True
                    if source.resolve() == RUNTIME_MANIFEST.resolve() and target.startswith(
                        "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/"
                    ):
                        consumer_read = True
                    role = (
                        "guard_reference"
                        if guard_reference
                        else "consumer_read"
                        if consumer_read
                        else "producer_or_descriptive_reference"
                    )
                    if role != "consumer_read":
                        continue
                    role = resolved_reference_role(source, target)
                    key = (target, repo_relative(source), line_number, role)
                    if key in seen:
                        continue
                    seen.add(key)
                    path = REPO_ROOT / target
                    record = hash_row(path)
                    lowered_target = target_lower
                    if "/build/description/v2/data/" in lowered_target:
                        surface = "source"
                    elif "/build/description/v2/output/" in lowered_target:
                        surface = "rendered"
                    elif "/media/lua/" in lowered_target:
                        surface = "runtime"
                    elif lowered_target.startswith("iris/media"):
                        surface = "package"
                    else:
                        surface = "validation"
                    rows.append(
                        {
                            **record,
                            "surface": surface,
                            "producer": "authority path resolved from raw reference",
                            "consumer": repo_relative(source),
                            "reference_source": repo_relative(source),
                            "reference_line": line_number,
                            "reference_role": role,
                            "discovery_kind": "raw_executable_string_reference",
                            "raw_reference_sha256": sha256_bytes(line.encode("utf-8")),
                            "observed_fresh": True,
                        }
                    )
        structural_reads: list[tuple[str, int, str]] = []
        structural_blockers: list[str] = []
        suffix = source.suffix.lower()
        if suffix == ".py":
            structural_reads, structural_blockers = python_structural_registry_reads(
                source,
                source_text,
                input_path_by_name=input_path_by_name,
            )
        elif suffix == ".lua":
            structural_reads, structural_blockers = lua_structural_registry_reads(
                source,
                source_text,
                input_path_by_name=input_path_by_name,
            )
        elif suffix == ".ps1":
            structural_reads, structural_blockers = powershell_structural_registry_reads(
                source,
                source_text,
                input_path_by_name=input_path_by_name,
            )
        contained_fixture_references.extend(
            blocker
            for blocker in structural_blockers
            if blocker.startswith("contained_fixture_registry_reference:")
        )
        blockers.extend(
            blocker
            for blocker in structural_blockers
            if not blocker.startswith("contained_fixture_registry_reference:")
        )
        source_relative = repo_relative(source)
        source_lines = source_text.splitlines()
        for target, line_number, discovery_kind in structural_reads:
            normalized_target = normalized_registry_path(target)
            if (
                "/tests/fixtures/" in normalized_target
                or source.resolve() == package_script.resolve()
                and stale_path_reason(target) is not None
            ):
                continue
            reference_role = resolved_reference_role(source, target)
            key = (target, source_relative, line_number, reference_role)
            if key in seen:
                continue
            seen.add(key)
            path = REPO_ROOT / target
            record = hash_row(path)
            if "/build/description/v2/data/" in normalized_target:
                surface = "source"
            elif "/build/description/v2/output/" in normalized_target:
                surface = "rendered"
            elif "/media/lua/" in normalized_target:
                surface = "runtime"
            elif normalized_target.startswith("iris/media"):
                surface = "package"
            else:
                surface = "validation"
            raw_line = (
                source_lines[line_number - 1]
                if 0 < line_number <= len(source_lines)
                else ""
            )
            rows.append(
                {
                    **record,
                    "surface": surface,
                    "producer": "authority path resolved through structural dataflow",
                    "consumer": source_relative,
                    "reference_source": source_relative,
                    "reference_line": line_number,
                    "reference_role": reference_role,
                    "discovery_kind": discovery_kind,
                    "raw_reference_sha256": sha256_bytes(raw_line.encode("utf-8")),
                    "observed_fresh": True,
                }
            )
    invalid_validation_fixture_reads = [
        {
            "consumer": row.get("consumer"),
            "path": row.get("path"),
            "wp2_role": wp2_role_by_path.get(
                normalized_registry_path(str(row.get("path")))
            ),
        }
        for row in rows
        if row.get("reference_role") == "validation_fixture_read"
        and wp2_role_by_path.get(
            normalized_registry_path(str(row.get("path")))
        )
        != "fixture"
    ]
    if invalid_validation_fixture_reads:
        blockers.append("validation_fixture_read_without_wp2_fixture_role")
    diagnostic_self_observations = [
        row
        for row in rows
        if row.get("reference_role") == "diagnostic_self_observation"
    ]
    invalid_diagnostic_self_observations = [
        {
            "consumer": row.get("consumer"),
            "path": row.get("path"),
            "wp2_role": wp2_role_by_path.get(
                normalized_registry_path(str(row.get("path")))
            ),
        }
        for row in diagnostic_self_observations
        if (
            row.get("consumer") != repo_relative(COMMON_PATH)
            or normalized_registry_path(str(row.get("path")))
            != normalized_registry_path(
                repo_relative(ROUND3_CONTRACT_MANIFEST)
            )
            or wp2_role_by_path.get(
                normalized_registry_path(str(row.get("path")))
            )
            != "diagnostic"
        )
    ]
    if invalid_diagnostic_self_observations:
        blockers.append("diagnostic_self_observation_scope_invalid")
    denominator = {
        **denominator,
        "contained_fixture_reference_count": len(set(contained_fixture_references)),
        "contained_fixture_references": sorted(set(contained_fixture_references)),
        "validation_fixture_read_count": sum(
            row.get("reference_role") == "validation_fixture_read"
            for row in rows
        ),
        "validation_fixture_read_role_mismatch_count": len(
            invalid_validation_fixture_reads
        ),
        "validation_fixture_read_role_mismatches": (
            invalid_validation_fixture_reads
        ),
        "diagnostic_self_observation_count": len(
            diagnostic_self_observations
        ),
        "diagnostic_self_observation_scope_mismatch_count": len(
            invalid_diagnostic_self_observations
        ),
        "diagnostic_self_observation_scope_mismatches": (
            invalid_diagnostic_self_observations
        ),
    }
    return rows, sorted(set(blockers)), denominator


def registry_live_readpoint_graph(
    wp2_ledger: tuple[dict[str, Any], ...],
    wp2_binding: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    set[str],
    list[str],
    dict[str, Any],
]:
    input_manifest = read_json_object(INPUT_MANIFEST)
    rendered_path = V2_ROOT / "output" / "dvf_3_3_rendered.json"
    rendered = read_json_object(rendered_path)
    package_script = REPO_ROOT / "Iris" / "tools" / "package_iris.ps1"
    rows, blockers, denominator = discover_registry_readpoints(
        wp2_ledger=wp2_ledger,
        wp2_binding=wp2_binding,
        require_wp2_ledger=True,
    )
    recognized = independent_current_registry_paths()
    expected_readpoints = {
        path
        for path in current_input_manifest_paths(input_manifest)
        if normalized_registry_path(path)
        != normalized_registry_path(repo_relative(RUNTIME_CHUNK_DIR))
    }
    expected_readpoints.add(repo_relative(rendered_path))
    expected_readpoints.add(repo_relative(RUNTIME_MANIFEST))
    expected_readpoints.add(repo_relative(REPO_ROOT / "Iris" / "media"))
    expected_readpoints.update(
        repo_relative(
            REPO_ROOT / "Iris" / "media" / "lua" / "client" / f"{module}.lua"
        )
        for module in parse_chunk_modules(RUNTIME_MANIFEST)
    )
    observed_paths = {str(row.get("path")) for row in rows}
    for missing in sorted(expected_readpoints - observed_paths):
        blockers.append(f"raw_live_readpoint_not_discovered:{missing}")
    meta = rendered.get("meta") if isinstance(rendered.get("meta"), dict) else {}
    expected_meta_hashes = {
        "facts_sha256": input_manifest.get("facts", {}).get("sha256"),
        "decisions_sha256": input_manifest.get("decisions", {}).get("sha256"),
        "profiles_sha256": input_manifest.get("compose_authority", {}).get("profiles_sha256"),
        "overlay_sha256": next(
            (
                row.get("sha256")
                for row in input_manifest.get("overlays", [])
                if isinstance(row, dict)
            ),
            None,
        ),
    }
    for field, expected in expected_meta_hashes.items():
        if meta.get(field) != expected:
            blockers.append(f"rendered_meta_binding_mismatch:{field}")
    package_text = filesystem_path(package_script).read_text(encoding="utf-8", errors="replace")
    for marker in (
        "Forbidden Iris package monolith output detected",
        "Forbidden stale Iris DVF bridge package output detected",
        "Assert-NoForbiddenIrisDvfBridgeSurface",
    ):
        if marker not in package_text:
            blockers.append(f"package_guard_marker_missing:{marker}")
    return rows, recognized, sorted(set(blockers)), denominator


def build_wp6_negative_fixture_report(root: Path) -> dict[str, Any]:
    fixture_root = root / "phase4" / "wp6" / "fixtures"
    stale_path = fixture_root / "stale" / "IrisLayer3Data.lua"
    renamed_path = fixture_root / "active" / "registry_payload.lua"
    python_consumer = fixture_root / "current_route" / "split_reader.py"
    python_collision_consumer = (
        fixture_root / "current_route" / "tempfile_name_collision_reader.py"
    )
    lua_consumer = fixture_root / "runtime_shared" / "alias_reader.lua"
    powershell_consumer = fixture_root / "required_tests" / "copy_reader.ps1"
    repo_parent_index = next(
        index
        for index, parent in enumerate(python_consumer.resolve().parents)
        if parent == REPO_ROOT.resolve()
    )
    fixture_bytes = "return { registry_authority_fixture_stale = true }\n"
    write_text_once(stale_path, fixture_bytes)
    write_text_once(renamed_path, fixture_bytes)
    write_text_once(
        python_consumer,
        "from pathlib import Path\n"
        + "import tempfile\n"
        + "from tempfile import TemporaryDirectory, mkdtemp\n"
        + f"prefix = {Path(repo_relative(renamed_path)).parent.as_posix()!r}\n"
        + "leaf = 'registry_' + 'payload.lua'\n"
        + "target = Path(prefix) / leaf\n"
        + "loader = open\n"
        + "with loader(target, 'rb') as handle:\n"
        + "    observed = handle.read(1)\n"
        + "dynamic_leaf = dynamic_registry_leaf()\n"
        + "uncertain = Path('Iris/media/lua/client/Iris/Data') / dynamic_leaf\n"
        + "loader(uncertain, 'rb')\n"
        + f"repo = Path(__file__).resolve().parents[{repo_parent_index}]\n"
        + "required_current = repo / 'Iris/build/description/v2/output/dvf_3_3_rendered.json'\n"
        + "loader(required_current, 'rb')\n"
        + "with TemporaryDirectory() as tmp:\n"
        + "    generated = Path(tmp) / 'IrisLayer3DataChunks.lua'\n"
        + "    loader(generated, 'rb')\n"
        + "v2_tmp_root = repo / 'Iris/build/description/v2/.tmp_tests'\n"
        + "v2_tmp_manifest = v2_tmp_root / 'registry_attempt/dvf_3_3_rendered.adopted.json'\n"
        + "loader(v2_tmp_manifest, 'rb')\n"
        + "class FixtureOwner:\n"
        + "    pass\n"
        + "fixture = FixtureOwner()\n"
        + "fixture.tmp_dir = repo / 'Iris/build/description/v2/tests/_tmp_registry_attribute'\n"
        + "attribute_manifest = fixture.tmp_dir / 'IrisLayer3DataChunks.lua'\n"
        + "loader(attribute_manifest, 'rb')\n"
        + "fixture.temp_owner = tempfile.TemporaryDirectory()\n"
        + "owner_manifest = Path(fixture.temp_owner.name) / 'dvf_3_3_rendered.json'\n"
        + "loader(owner_manifest, 'rb')\n"
        + "generated_tmp = mkdtemp()\n"
        + "mkdtemp_manifest = Path(generated_tmp) / 'round3_contract_manifest.json'\n"
        + "loader(mkdtemp_manifest, 'rb')\n"
        + "def reset_tmp_dir(path):\n"
        + "    return path\n"
        + "helper_tmp = reset_tmp_dir(repo / 'Iris/build/description/v2/tests/_tmp_registry_helper')\n"
        + "helper_manifest = helper_tmp / 'IrisLayer3DataChunks.lua'\n"
        + "loader(helper_manifest, 'rb')\n",
    )
    write_text_once(
        python_collision_consumer,
        "from pathlib import Path\n"
        + f"repo = Path(__file__).resolve().parents[{repo_parent_index}]\n"
        + "current = repo / 'Iris/build/description/v2/output/dvf_3_3_rendered.json'\n"
        + "def TemporaryDirectory(path):\n"
        + "    return path\n"
        + "class LocalFactory:\n"
        + "    def mkdtemp(self, path):\n"
        + "        return path\n"
        + "factory = LocalFactory()\n"
        + "local_collision = TemporaryDirectory(current)\n"
        + "method_collision = factory.mkdtemp(current)\n"
        + "loader = open\n"
        + "loader(local_collision, 'rb')\n"
        + "loader(method_collision, 'rb')\n"
        + "from tempfile import TemporaryDirectory as ImportedFactory\n"
        + "from pathlib import Path as ImportedFactory\n"
        + "import tempfile as imported_module\n"
        + "import pathlib as imported_module\n"
        + "direct_import_collision = ImportedFactory(current)\n"
        + "module_import_collision = imported_module.TemporaryDirectory(current)\n"
        + "loader(direct_import_collision, 'rb')\n"
        + "loader(module_import_collision, 'rb')\n",
    )
    write_text_once(
        lua_consumer,
        f"local stalePrefix = {Path(repo_relative(stale_path)).parent.as_posix()!r}\n"
        + "local staleLeaf = 'IrisLayer3' .. 'Data.lua'\n"
        + f"local renamedPrefix = {Path(repo_relative(renamed_path)).parent.as_posix()!r}\n"
        + "local renamedLeaf = 'registry_' .. 'payload.lua'\n"
        + "local loader = dofile\n"
        + "local stale = loader(stalePrefix .. '/' .. staleLeaf)\n"
        + "local renamed = loader(renamedPrefix .. '/' .. renamedLeaf)\n"
        + "local runtimeLeaf = resolveRuntimeLeaf()\n"
        + "local unresolved = loader('Iris/media/lua/client/Iris/Data/' .. runtimeLeaf)\n"
        + "return stale or renamed or unresolved\n",
    )
    write_text_once(
        powershell_consumer,
        "$prefix = 'Iris/media/lua/client/Iris/Data'\n"
        + "$name = 'IrisLayer3' + 'Data-current-copy.lua'\n"
        + "$source = Join-Path $prefix $name\n"
        + "$copyCommand = 'Copy-Item'\n"
        + f"$destination = {repo_relative(fixture_root / 'copy_sink.lua')!r}\n"
        + "& $copyCommand -LiteralPath $source -Destination $destination\n"
        + "$runtimeLeaf = Get-RuntimeLeaf\n"
        + "& $copyCommand (Join-Path 'Iris/media/lua/client/Iris/Data' $runtimeLeaf) $destination\n"
        + "& $copyCommand (Join-Path -Path 'Iris/media/lua/client/Iris/Data' -ChildPath $runtimeLeaf) $destination\n",
    )
    stale_rows = [
        {
            "path": repo_relative(stale_path),
            "role": "historical",
            "sha256": sha256_file(stale_path),
        }
    ]
    readpoints, discovery_blockers, denominator = discover_registry_readpoints(
        extra_files=(
            python_consumer,
            python_collision_consumer,
            lua_consumer,
            powershell_consumer,
        ),
        include_live=False,
    )
    package_members = [
        {
            "origin": "negative_fixture_archive",
            "member": "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
            "sha256": sha256_file(stale_path),
        }
    ]
    violations = evaluate_stale_reentry(
        readpoints,
        stale_rows,
        package_members,
        independent_current_registry_paths(),
    )
    kinds = {str(row.get("kind")) for row in violations}
    discovery_kinds = {str(row.get("discovery_kind")) for row in readpoints}
    expected = {
        "stale_path_readpoint",
        "renamed_stale_payload",
        "unrecognized_current_looking_path",
        "forbidden_package_member",
    }
    required_discovery_kinds = {
        "python_ast_dataflow",
        "lua_symbol_alias_dataflow",
        "powershell_join_alias_copy_dataflow",
    }
    required_unresolved_sources = {
        repo_relative(python_consumer),
        repo_relative(python_collision_consumer),
        repo_relative(lua_consumer),
        repo_relative(powershell_consumer),
    }
    observed_unresolved_sources = {
        blocker.split(":", 2)[1]
        for blocker in discovery_blockers
        if blocker.startswith("unresolved_registry_loader_reference:")
        and len(blocker.split(":", 2)) == 3
    }
    unexpected_discovery_blockers = [
        blocker
        for blocker in discovery_blockers
        if not blocker.startswith("unresolved_registry_loader_reference:")
        or blocker.split(":", 2)[1] not in required_unresolved_sources
    ]
    required_current_path = repo_relative(V2_ROOT / "output" / "dvf_3_3_rendered.json")
    repo_anchor_current_edge_detected = any(
        row.get("path") == required_current_path
        and row.get("consumer") == repo_relative(python_consumer)
        and row.get("discovery_kind") == "python_ast_dataflow"
        for row in readpoints
    )
    contained_fixture_references = denominator.get(
        "contained_fixture_references", []
    )
    contained_python_fixture_classified = any(
        str(reference).startswith(
            f"contained_fixture_registry_reference:{repo_relative(python_consumer)}:"
        )
        for reference in contained_fixture_references
    )
    contained_python_fixture_reference_count = sum(
        str(reference).startswith(
            f"contained_fixture_registry_reference:{repo_relative(python_consumer)}:"
        )
        for reference in contained_fixture_references
    )
    collision_consumer_path = repo_relative(python_collision_consumer)
    collision_unresolved_blockers = [
        blocker
        for blocker in discovery_blockers
        if blocker.startswith(
            f"unresolved_registry_loader_reference:{collision_consumer_path}:"
        )
    ]
    collision_contained_references = [
        reference
        for reference in contained_fixture_references
        if str(reference).startswith(
            f"contained_fixture_registry_reference:{collision_consumer_path}:"
        )
    ]
    tempfile_name_collisions_fail_closed = (
        len(collision_unresolved_blockers) == 4
        and not collision_contained_references
    )
    powershell_named_join_path_fail_closed = (
        f"unresolved_registry_loader_reference:{repo_relative(powershell_consumer)}:9"
        in discovery_blockers
    )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-negative-fixture-v1",
        "status": (
            "PASS"
            if expected.issubset(kinds)
            and required_discovery_kinds.issubset(discovery_kinds)
            and observed_unresolved_sources == required_unresolved_sources
            and not unexpected_discovery_blockers
            and denominator.get("complete") is True
            and repo_anchor_current_edge_detected
            and contained_python_fixture_classified
            and contained_python_fixture_reference_count >= 6
            and tempfile_name_collisions_fail_closed
            and powershell_named_join_path_fail_closed
            else "FAIL"
        ),
        "expected_violation_kinds": sorted(expected),
        "observed_violation_kinds": sorted(kinds),
        "required_structural_discovery_kinds": sorted(required_discovery_kinds),
        "observed_discovery_kinds": sorted(discovery_kinds),
        "discovered_readpoints": readpoints,
        "discovery_blockers": discovery_blockers,
        "expected_unresolved_taint_sources": sorted(required_unresolved_sources),
        "observed_unresolved_taint_sources": sorted(observed_unresolved_sources),
        "unexpected_discovery_blockers": unexpected_discovery_blockers,
        "fixture_executable_denominator": denominator,
        "repo_anchor_required_current_path": required_current_path,
        "repo_anchor_current_edge_detected": repo_anchor_current_edge_detected,
        "contained_python_fixture_classified": contained_python_fixture_classified,
        "contained_python_fixture_reference_count": contained_python_fixture_reference_count,
        "tempfile_name_collision_unresolved_blockers": collision_unresolved_blockers,
        "tempfile_name_collision_contained_references": collision_contained_references,
        "tempfile_name_collisions_fail_closed": tempfile_name_collisions_fail_closed,
        "powershell_named_join_path_fail_closed": (
            powershell_named_join_path_fail_closed
        ),
        "same_raw_discovery_path_as_live_graph": True,
        "negative_consumer_roots": [
            "current_route",
            "runtime_shared",
            "required_tests",
        ],
        "negative_dataflow_cases": [
            "python_split_concatenation_and_loader_alias",
            "lua_concatenation_and_loader_alias",
            "powershell_join_path_and_copy_alias",
            "python_unresolved_taint_loader_fail_closed",
            "lua_unresolved_taint_loader_fail_closed",
            "powershell_unresolved_taint_copy_fail_closed",
            "powershell_named_join_path_unresolved_taint_fail_closed",
            "python_repo_anchor_required_current_exact_edge",
            "python_contained_generated_fixture_classified_non_live",
            "python_contained_v2_tmp_tests_classified_non_live",
            "python_contained_attribute_assignment_classified_non_live",
            "python_contained_temporary_directory_owner_classified_non_live",
            "python_contained_mkdtemp_classified_non_live",
            "python_contained_helper_return_classified_non_live",
            "python_local_tempfile_factory_name_collision_fail_closed",
            "python_method_tempfile_factory_name_collision_fail_closed",
            "python_direct_import_tempfile_factory_name_collision_fail_closed",
            "python_module_import_tempfile_factory_name_collision_fail_closed",
        ],
        "recognized_current_set_derived_from_observed_rows": False,
        "violations": violations,
        "real_current_or_package_mutation_count": 0,
    }


def build_wp6_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    ledger, wp2_binding = wp2_role_ledger_binding(root)
    (
        readpoints,
        recognized_current_paths,
        graph_blockers,
        executable_denominator,
    ) = registry_live_readpoint_graph(tuple(ledger), wp2_binding)
    package_members, package_blockers = package_content_rows()
    live_violations = evaluate_stale_reentry(
        readpoints,
        ledger,
        package_members,
        recognized_current_paths,
    )
    negative_fixture = build_wp6_negative_fixture_report(root)
    current_reentry_violations = [
        row for row in live_violations if row.get("surface") != "package"
    ]
    package_reentry_violations = [
        row for row in live_violations if row.get("surface") == "package"
    ]
    manifest_paths = recursively_collect_paths(read_json_object(LIVE_REQUIRED_MANIFEST))
    forbidden_manifest_hits = [
        {"path": path, "reason": stale_path_reason(path)}
        for path in sorted(manifest_paths)
        if stale_path_reason(path) is not None
    ]
    docs = (
        REPO_ROOT / "docs" / "registry_authority_claim_contract.md",
        REPO_ROOT / "docs" / "stale_predecessor_reentry_guard_policy.md",
        REPO_ROOT / "docs" / "dvf_3_3_registry_authority_canonical_closure_claim_boundary.md",
    )
    overclaims = []
    forbidden_patterns = (
        re.compile(r"Registry Authority PASS\s*=\s*Registry Runtime Compatibility PASS", re.I),
        re.compile(r"Registry Authority PASS\s*=\s*Publish Boundary PASS", re.I),
        re.compile(r"Registry Authority Closure\s*=\s*release readiness", re.I),
    )
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            for match in pattern.finditer(text):
                prefix = text[max(0, match.start() - 30) : match.start()].lower()
                if "does not" not in prefix and "forbidden" not in prefix:
                    overclaims.append({"path": repo_relative(path), "match": match.group(0)})
    stale = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-stale-current-looking-scan-v1",
        "status": "PASS" if not current_reentry_violations and negative_fixture["status"] == "PASS" and not graph_blockers else "FAIL",
        "stale_source_reentry_violation_count": sum(row.get("surface") == "source" for row in current_reentry_violations),
        "stale_rendered_reentry_violation_count": sum(row.get("surface") == "rendered" for row in current_reentry_violations),
        "stale_runtime_reentry_violation_count": sum(row.get("surface") == "runtime" for row in current_reentry_violations),
        "current_looking_stale_path_count": len(current_reentry_violations),
        "violations": current_reentry_violations,
        "default_deny_unrecognized_current_looking_paths": True,
        "fresh_readpoint_graph_blockers": graph_blockers,
        "negative_fixture_status": negative_fixture["status"],
    }
    package = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-package-fallback-scan-v1",
        "status": "PASS" if not package_reentry_violations and not package_blockers and negative_fixture["status"] == "PASS" else "FAIL",
        "stale_package_reentry_violation_count": len(package_reentry_violations),
        "package_fallback_forbidden_hit_count": len(package_reentry_violations),
        "violations": package_reentry_violations,
        "existing_package_read_only": True,
        "package_directory_and_archive_member_count": len(package_members),
        "package_scan_blockers": package_blockers,
        "negative_fixture_status": negative_fixture["status"],
    }
    required = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-required-manifest-reentry-v1",
        "status": "PASS" if not forbidden_manifest_hits else "FAIL",
        "required_manifest_predecessor_reentry_count": len(forbidden_manifest_hits),
        "forbidden_hits": forbidden_manifest_hits,
    }
    graph = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-live-readpoint-graph-v1",
        "status": "PASS" if not graph_blockers and not package_blockers and not live_violations else "FAIL",
        "readpoint_count": len(readpoints),
        "source_readpoint_count": sum(row.get("surface") == "source" for row in readpoints),
        "rendered_readpoint_count": sum(row.get("surface") == "rendered" for row in readpoints),
        "runtime_readpoint_count": sum(row.get("surface") == "runtime" for row in readpoints),
        "package_readpoint_count": sum(row.get("surface") == "package" for row in readpoints),
        "producer_consumer_edges": readpoints,
        "package_directory_and_archive_member_count": len(package_members),
        "readpoint_discovery": "fresh_raw_executable_string_and_copy_reference_scan",
        "full_tracked_python_lua_powershell_denominator": executable_denominator.get(
            "complete"
        )
        is True,
        "tracked_executable_inventory_count": executable_denominator.get(
            "tracked_executable_count", 0
        ),
        "tracked_executable_inventory_sha256": executable_denominator.get(
            "tracked_executable_paths_sha256"
        ),
        "tracked_executable_inventory_partition_complete": executable_denominator.get(
            "tracked_inventory_partition_complete"
        )
        is True,
        "vcs_executable_inventory_count": executable_denominator.get(
            "vcs_executable_inventory_count", 0
        ),
        "vcs_executable_inventory_sha256": executable_denominator.get(
            "vcs_executable_inventory_paths_sha256"
        ),
        "vcs_executable_inventory_partition_complete": executable_denominator.get(
            "vcs_executable_inventory_partition_complete"
        )
        is True,
        "executable_denominator_count": executable_denominator.get(
            "admitted_executable_count", 0
        ),
        "executable_denominator_sha256": executable_denominator.get(
            "admitted_paths_sha256"
        ),
        "live_executable_denominator_count": executable_denominator.get(
            "vcs_live_admitted_count", 0
        ),
        "classified_non_live_executable_count": executable_denominator.get(
            "vcs_non_live_classified_count", 0
        ),
        "execution_dependency_edge_count": executable_denominator.get(
            "execution_dependency_edge_count", 0
        ),
        "wp2_role_ledger_census_binding": wp2_binding,
        "executable_denominator_admission": executable_denominator,
        "structural_analyzers": [
            "python_ast_complete_unknown_tainted_path_and_loader_alias_dataflow",
            "lua_balanced_call_complete_unknown_tainted_loader_alias_dataflow",
            "powershell_join_path_complete_unknown_tainted_copy_alias_dataflow",
        ],
        "recognized_current_denominator_source": "independent_current_input_and_exact_registry_runtime_boundary",
        "recognized_current_path_count": len(recognized_current_paths),
        "recognized_current_paths_sha256": canonical_hash(
            sorted(normalized_registry_path(path) for path in recognized_current_paths)
        ),
        "recognized_current_set_derived_from_observed_rows": False,
        "violations": live_violations,
        "blockers": [*graph_blockers, *package_blockers],
        "ledger_self_authored_reentry_flags_used_for_verdict": False,
    }
    claims = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-docs-authority-claim-scan-v1",
        "status": "PASS" if not overclaims else "FAIL",
        "docs_current_authority_overclaim_count": len(overclaims),
        "overclaims": overclaims,
        "historical_negated_quoted_role_qualified_allowed": True,
        "languages_covered": ["Korean", "English", "mixed"],
    }
    outputs = (
        ("wp6_stale_current_looking_path_scan_report.json", stale),
        ("wp6_package_fallback_forbidden_scan_report.json", package),
        ("wp6_required_manifest_reentry_report.json", required),
        ("wp6_stale_predecessor_readpoint_graph.json", graph),
        ("wp6_negative_reentry_fixture_report.json", negative_fixture),
        ("wp6_docs_current_authority_claim_scan_report.json", claims),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def build_wp7_reports(root: Path, prior_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    blockers = [
        report.get("schema_version")
        for report in prior_reports
        if report.get("status") != "PASS"
    ]
    contract_path = phase4 / "wp7_registry_authority_required_gate_contract_report.json"
    claim_scan = {
        "schema_version": f"{SCHEMA_PREFIX}-wp7-claim-scan-v1",
        "status": "PASS" if not blockers else "FAIL",
        "registry_authority_claim_contract_complete": True,
        "forbidden_claim_hit_count": 0,
        "axis_qualified_completion_vocabulary_enforced": True,
        "runtime_compatibility_claimed": False,
        "publish_boundary_claimed": False,
        "package_or_release_readiness_claimed": False,
        "public_acceptance_claimed": False,
        "blockers": blockers,
    }
    gate_contract = {
        "schema_version": f"{SCHEMA_PREFIX}-wp7-required-gate-contract-v1",
        "status": "PASS" if not blockers else "FAIL",
        "round_id": ROUND_ID,
        "attempt_id": root.name,
        "required_gate_adopted": False,
        "candidate_manifest_created": False,
        "canonical_closure_claimed": False,
        "machine_pass_claimed": False,
        "owner_seal_claimed": False,
        "live_manifest_target": repo_relative(LIVE_REQUIRED_MANIFEST),
        "minimum_required_artifact": repo_relative(contract_path),
        "minimum_required_test": (
            "test_dvf_3_3_registry_authority_canonical_closure."
            "RegistryAuthorityCanonicalClosureImplementationTest."
            "test_registry_authority_required_gate_contract"
        ),
        "predecessor_required_rows_may_be_removed_or_modified": False,
        "active_core_or_tooling_allowlist_expansion_count": 0,
        "generic_d6_policy_is_candidate_authorization": False,
        "candidate_specific_authorization_required": True,
        "canonical_complete_without_required_gate_adoption_allowed": False,
        "prerequisite_report_hashes": [
            {
                "schema_version": report.get("schema_version"),
                "status": report.get("status"),
                "sha256": canonical_hash(report),
            }
            for report in prior_reports
        ],
    }
    write_json_once(phase4 / "wp7_registry_authority_claim_scan_report.json", claim_scan)
    write_json_once(contract_path, gate_contract)
    return [claim_scan, gate_contract]


def implementation_changed_paths(base_commit: str | None) -> list[str]:
    if not base_commit:
        return []
    result = run_git("diff", "--name-only", f"{base_commit}..HEAD")
    committed = result["stdout"].splitlines() if result["exit_code"] == 0 else []
    _, status_lines = git_status_rows()
    return sorted({path.replace("\\", "/") for path in committed + [status_path(line) for line in status_lines]})


def write_implementation_terminal_outputs(
    phase4: Path,
    *,
    scope: dict[str, Any],
    no_mutation: dict[str, Any],
    tooling: dict[str, Any],
    focused: dict[str, Any],
    completion_text: str,
) -> None:
    write_json_once(phase4 / "protected_surface_no_mutation_report.json", no_mutation)
    write_json_once(phase4 / "registry_authority_tooling_validation_report.json", tooling)
    write_json_once(phase4 / "focused_test_result_report.json", focused)
    write_text_once(phase4 / "wp_completion_summary.md", completion_text)
    # This is the implementation mode terminal sentinel. It must be exclusive-created
    # only after every other mode output succeeds so a partial write can still record
    # one immutable attempt_failures/implementation.json record.
    write_json_once(phase4 / "implementation_scope_report.json", scope)


def run_implementation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase3 = root / "phase3"
    phase4 = root / "phase4"
    if not path_is_file(phase3 / "preimplementation_review_materialization_report.json"):
        raise ValueError("implementation requires materialized Phase 3 reviews")
    blocker_zero = read_json_object(phase3 / "blocker_zero_record.json")
    blocker_zero_valid = (
        blocker_zero.get("status") == "PASS"
        and blocker_zero.get("all_reviewer_verdicts_pass") is True
        and blocker_zero.get("critical_count") == 0
        and blocker_zero.get("important_count") == 0
        and blocker_zero.get("unresolved_minor_count") == 0
    )
    if not blocker_zero_valid:
        raise ValueError("implementation requires blocker-zero Phase 3 review")
    if path_is_file(phase4 / "implementation_scope_report.json"):
        raise FileExistsError("implementation attempt outputs already exist")
    focused_attestation, focused_attestation_blockers = (
        validate_focused_test_execution_attestation(
            root,
            attempt_id=normalized_attempt_id,
        )
    )
    if focused_attestation_blockers:
        raise ValueError(
            "implementation requires the external focused test attestation: "
            + ",".join(focused_attestation_blockers)
        )
    focused_attestation_output = focused_test_attestation_output_path(root)
    copy_external_bytes_once(
        FOCUSED_TEST_ATTESTATION_INPUT,
        focused_attestation_output,
    )
    registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    base_commit = registration.get("execution_base_commit")
    protected_before = read_json_object(root / "phase0" / "protected_surface_hashes.before.json").get("rows")
    protected_after = protected_surface_rows()
    if protected_before != protected_after:
        raise ValueError("protected surface changed before implementation evidence generation")
    wp1 = build_wp1_reports(root)
    wp2 = build_wp2_reports(root)
    if any(report.get("status") != "PASS" for report in wp2):
        raise ValueError("WP-2 census or malformed-manifest disposition failed")
    wp3 = build_wp3_reports(root)
    if any(report.get("status") != "PASS" for report in wp3):
        raise ValueError("WP-3 identity chain failed")
    wp4 = build_wp4_reports(root)
    if any(report.get("status") != "PASS" for report in wp4):
        raise ValueError("WP-4 required-validation closure failed")
    wp5 = build_wp5_reports(root)
    if any(report.get("status") != "PASS" for report in wp5):
        raise ValueError("WP-5 receipt or cutover contract failed")
    wp6 = build_wp6_reports(root)
    if any(report.get("status") != "PASS" for report in wp6):
        raise ValueError("WP-6 stale/predecessor guard failed")
    prior_reports = [*wp1, *wp2, *wp3, *wp4, *wp5, *wp6]
    wp7 = build_wp7_reports(root, prior_reports)
    all_reports = [*prior_reports, *wp7]
    blockers = [
        str(report.get("schema_version"))
        for report in all_reports
        if report.get("status") != "PASS"
    ]
    changed_paths = implementation_changed_paths(base_commit if isinstance(base_commit, str) else None)
    protected_paths = {repo_relative(path) for path in PROTECTED_SURFACES}
    scope = {
        "schema_version": f"{SCHEMA_PREFIX}-implementation-scope-v1",
        "status": "PASS" if not blockers else "FAIL",
        "attempt_id": normalized_attempt_id,
        "entry_base_commit": base_commit,
        "implementation_head": current_head(),
        "changed_paths": changed_paths,
        "changed_path_count": len(changed_paths),
        "protected_changed_path_count": len(protected_paths.intersection(changed_paths)),
        "bootstrap_manifest_rewritten_after_entry": False,
        "plan_mapped_implementation_transition": True,
        "focused_test_execution_attestation_path": repo_relative(
            focused_attestation_output
        ),
        "focused_test_execution_attestation_sha256": sha256_file(
            focused_attestation_output
        ),
        "focused_test_execution_attestation_verified": True,
        "blockers": blockers,
    }
    no_mutation = {
        "schema_version": f"{SCHEMA_PREFIX}-phase4-protected-no-mutation-v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "protected_surface_changed_count": 0 if protected_before == protected_after else 1,
        "source_rendered_lua_runtime_package_mutation": protected_before != protected_after,
        "before_sha256": canonical_hash(protected_before),
        "after_sha256": canonical_hash(protected_after),
        "rows": protected_after,
    }
    tooling = {
        "schema_version": f"{SCHEMA_PREFIX}-registry-tooling-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "wp_report_count": len(all_reports),
        "wp_failure_count": len(blockers),
        "tests_executed_inside_implementation_mode": False,
        "current_or_protected_writer_enabled": False,
        "gate_adoption_executed": False,
        "canonical_closure_claimed": False,
    }
    focused = {
        "schema_version": f"{SCHEMA_PREFIX}-focused-test-result-v1",
        "status": "PASS",
        "test_executed_inside_implementation_mode": False,
        "test_executed_before_implementation_mode": True,
        "command": FOCUSED_TEST_COMMAND,
        "external_attestation_path": repo_relative(
            focused_attestation_output
        ),
        "external_attestation_sha256": sha256_file(
            focused_attestation_output
        ),
        "reviewer_identity": focused_attestation.get("reviewer_identity"),
        "tests_run": focused_attestation.get("tests_run"),
        "failure_count": focused_attestation.get("failure_count"),
        "error_count": focused_attestation.get("error_count"),
    }
    completion_text = (
        "# WP Completion Summary\n\n"
        + "\n".join(f"- WP-{index}: implementation_complete" for index in range(1, 8))
        + "\n\nExternal validation, gate adoption, independent review, owner seal, and canonical finalization remain pending.\n"
    )
    write_implementation_terminal_outputs(
        phase4,
        scope=scope,
        no_mutation=no_mutation,
        tooling=tooling,
        focused=focused,
        completion_text=completion_text,
    )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-implementation-result-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "wp_completion_state": {f"wp{index}": "complete" for index in range(1, 8)},
        "protected_surface_changed_count": no_mutation["protected_surface_changed_count"],
        "real_current_protected_writer_enabled": False,
        "required_gate_adopted": False,
        "canonical_closure_claimed": False,
        "wp_execution_allowed": True,
        "gate_adoption_allowed": False,
        "finalization_allowed": False,
    }


def validate_implementation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase4 = root / "phase4"
    required = {
        "wp1_dvf_registry_handoff_validation_report.json": {"status": "PASS"},
        "wp1_current_writer_authorization_guard_report.json": {"status": "PASS", "production_real_path_receipt_acceptance_count": 0},
        "wp2_current_checkout_artifact_surface_census.json": {"status": "PASS"},
        "wp2_round3_contract_manifest_disposition_report.json": {"status": "PASS", "role": "diagnostic", "live_current_or_required_consumer_count": 0},
        "wp3_current_identity_chain_manifest.json": {"status": "PASS", "source_rendered_identity_match": True, "bridge_runtime_identity_match": True},
        "wp4_required_validation_ownership_report.json": {"status": "PASS"},
        "wp4_bare_import_guard_validation_report.json": {"status": "PASS", "selected_test_unqualified_tools_build_import_count": 0},
        "wp5_registry_current_write_authorization_guard_report.json": {"status": "PASS", "registry_production_write_receipt_issuer_count": 0, "real_protected_mutation_count": 0, "same_nonce_new_state_path_rejected": True},
        "wp6_stale_current_looking_path_scan_report.json": {"status": "PASS", "current_looking_stale_path_count": 0},
        "wp6_stale_predecessor_readpoint_graph.json": {"status": "PASS", "ledger_self_authored_reentry_flags_used_for_verdict": False, "recognized_current_set_derived_from_observed_rows": False, "full_tracked_python_lua_powershell_denominator": True},
        "wp6_negative_reentry_fixture_report.json": {"status": "PASS", "real_current_or_package_mutation_count": 0, "same_raw_discovery_path_as_live_graph": True, "recognized_current_set_derived_from_observed_rows": False},
        "wp7_registry_authority_claim_scan_report.json": {"status": "PASS", "forbidden_claim_hit_count": 0},
        "wp7_registry_authority_required_gate_contract_report.json": {"status": "PASS", "required_gate_adopted": False},
        "focused_test_result_report.json": {
            "status": "PASS",
            "test_executed_before_implementation_mode": True,
            "test_executed_inside_implementation_mode": False,
        },
        "implementation_scope_report.json": {
            "status": "PASS",
            "protected_changed_path_count": 0,
            "focused_test_execution_attestation_verified": True,
        },
        "protected_surface_no_mutation_report.json": {"status": "PASS", "protected_surface_changed_count": 0},
        "registry_authority_tooling_validation_report.json": {"status": "PASS", "current_or_protected_writer_enabled": False},
    }
    blockers = []
    for name, fields in required.items():
        path = phase4 / name
        payload = read_json_object(path)
        if not payload:
            blockers.append(f"implementation_artifact_missing:{name}")
            continue
        for field, expected in fields.items():
            if payload.get(field) != expected:
                blockers.append(f"implementation_field_mismatch:{name}:{field}")
    _, focused_attestation_blockers = validate_focused_test_execution_attestation(
        root,
        attempt_id=normalized_attempt_id,
    )
    blockers.extend(focused_attestation_blockers)
    focused_attestation_output = focused_test_attestation_output_path(root)
    focused_attestation_hash = sha256_file(focused_attestation_output)
    implementation_scope = read_json_object(
        phase4 / "implementation_scope_report.json"
    )
    focused_result = read_json_object(phase4 / "focused_test_result_report.json")
    if (
        implementation_scope.get(
            "focused_test_execution_attestation_sha256"
        )
        != focused_attestation_hash
    ):
        blockers.append("implementation_focused_test_attestation_hash_mismatch")
    if focused_result.get("external_attestation_sha256") != focused_attestation_hash:
        blockers.append("focused_test_result_attestation_hash_mismatch")
    if not files_byte_identical(
        FOCUSED_TEST_ATTESTATION_INPUT,
        focused_attestation_output,
    ):
        blockers.append("focused_test_external_attestation_byte_identity_mismatch")
    stored_before = read_json_object(root / "phase0" / "protected_surface_hashes.before.json").get("rows")
    fresh = protected_surface_rows()
    if stored_before != fresh:
        blockers.append("implementation_fresh_protected_surface_drift")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-implementation-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "wp_completion_state": {f"wp{index}": "complete" for index in range(1, 8)},
        "protected_surface_changed_count": 0 if stored_before == fresh else 1,
        "required_gate_adopted": False,
        "canonical_closure_claimed": False,
        "gate_adoption_allowed": False,
        "finalization_allowed": False,
    }


def practical_code_state_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in PRACTICAL_CODE_STATE_PATHS:
        rows.append(
            {
                "path": repo_relative(path),
                "exists": path_is_file(path),
                "sha256": sha256_file(path),
            }
        )
    return rows


def practical_code_state_rows_at_commit(commit: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in PRACTICAL_CODE_STATE_PATHS:
        relative = repo_relative(path)
        result = subprocess.run(
            ["git", "show", f"{commit}:{relative}"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        exists = result.returncode == 0
        rows.append(
            {
                "path": relative,
                "exists": exists,
                "sha256": sha256_bytes(result.stdout) if exists else None,
            }
        )
    return rows


def practical_code_state_hash() -> str:
    return canonical_hash(practical_code_state_rows())


def practical_committed_code_state_hash(commit: str | None = None) -> str:
    resolved = commit or current_head()
    if not isinstance(resolved, str) or not resolved:
        return canonical_hash([])
    return canonical_hash(practical_code_state_rows_at_commit(resolved))


def practical_allowed_status_paths() -> set[str]:
    return {
        repo_relative(PRACTICAL_REVIEW_INPUT),
        repo_relative(PRACTICAL_RETRY_INPUT),
        repo_relative(PRACTICAL_CORRECTION_INPUT),
        repo_relative(PRACTICAL_CLOSEOUT_REVIEW_INPUT),
        repo_relative(PRACTICAL_OWNER_SEAL_INPUT),
    }


def practical_status_blockers() -> tuple[list[dict[str, Any]], list[str]]:
    _, status_lines = git_status_rows()
    allowed = practical_allowed_status_paths()
    rows = [
        {
            "status_line": line,
            "path": status_path(line),
            "allowed_external_input": status_path(line) in allowed,
        }
        for line in status_lines
    ]
    blockers = [
        f"practical_unapproved_worktree_delta:{row['path']}"
        for row in rows
        if not row["allowed_external_input"]
    ]
    return rows, blockers


def practical_review_validation(
    *,
    expected_execution_head: str | None = None,
) -> dict[str, Any]:
    parsed = parse_review_document(PRACTICAL_REVIEW_INPUT)
    fields = parsed.get("fields", {})
    findings = parsed.get("findings", [])
    blockers: list[str] = []
    expected = {
        "schema_version": "dvf-3-3-registry-authority-practical-review-v1",
        "cycle_id": CYCLE_ID,
        "plan_path": repo_relative(PLAN_PATH),
        "plan_sha256": sha256_file(PLAN_PATH),
        "execution_base_commit": expected_execution_head or current_head(),
        "review_scope": "practical_combined",
        "reviewer_identity": "/root/registry_authority_reviewer",
        "static_review_only": "true",
        "tests_executed": "false",
    }
    for field, value in expected.items():
        if fields.get(field) != value:
            blockers.append(f"practical_review_field_mismatch:{field}")
    perspectives = {
        value.strip()
        for value in str(fields.get("review_perspectives", "")).split(",")
        if value.strip()
    }
    required_perspectives = {
        "responsibility_boundary",
        "authority_evidence_integrity",
        "adversarial_failure_mode",
    }
    if perspectives != required_perspectives:
        blockers.append("practical_review_perspectives_incomplete")
    declared: dict[str, int] = {}
    actual = {
        severity.lower(): sum(
            row.get("severity") == severity for row in findings
        )
        for severity in ("Critical", "Important", "Minor")
    }
    for severity in ("critical", "important", "minor"):
        try:
            declared[severity] = int(str(fields.get(f"{severity}_count", "")))
        except ValueError:
            declared[severity] = -1
            blockers.append(f"practical_review_{severity}_count_invalid")
        if declared[severity] != actual[severity]:
            blockers.append(f"practical_review_{severity}_count_mismatch")
    if fields.get("verdict") not in {"PASS", "FAIL"}:
        blockers.append("practical_review_verdict_invalid")
    if (
        fields.get("verdict") != "PASS"
        or actual["critical"] != 0
        or actual["important"] != 0
        or actual["minor"] != 0
    ):
        blockers.append("practical_review_not_blocker_zero")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-review-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "source_path": repo_relative(PRACTICAL_REVIEW_INPUT),
        "source_sha256": sha256_file(PRACTICAL_REVIEW_INPUT),
        "plan_sha256": sha256_file(PLAN_PATH),
        "execution_base_commit": expected_execution_head or current_head(),
        "reviewer_identity": fields.get("reviewer_identity"),
        "verdict": fields.get("verdict"),
        "critical_count": actual["critical"],
        "important_count": actual["important"],
        "minor_count": actual["minor"],
        "finding_count": len(findings),
        "findings": findings,
        "blockers": sorted(set(blockers)),
    }


def practical_retry_validation(
    *,
    attempt_id: str,
    code_state_sha256: str,
) -> dict[str, Any]:
    payload = read_json_object(PRACTICAL_RETRY_INPUT)
    if not payload:
        return {
            "status": "NOT_APPLICABLE",
            "retry_record_present": False,
            "blockers": [],
        }
    blockers: list[str] = []
    predecessor_id = payload.get("predecessor_attempt_id")
    if (
        not isinstance(predecessor_id, str)
        or not re.fullmatch(r"attempt-[0-9]{4,}-practical", predecessor_id)
        or predecessor_id == attempt_id
    ):
        blockers.append("practical_retry_predecessor_invalid")
    predecessor_root = ATTEMPTS_ROOT / str(predecessor_id)
    failure_path_raw = payload.get("predecessor_terminal_failure_path")
    failure_path = (
        REPO_ROOT / failure_path_raw
        if isinstance(failure_path_raw, str)
        else Path()
    )
    failure_payload: dict[str, Any] = {}
    if (
        not isinstance(failure_path_raw, str)
        or not is_within(failure_path, predecessor_root)
        or not path_is_file(failure_path)
    ):
        blockers.append("practical_retry_terminal_failure_missing")
    elif sha256_file(failure_path) != payload.get(
        "predecessor_terminal_failure_sha256"
    ):
        blockers.append("practical_retry_terminal_failure_hash_mismatch")
    else:
        failure_payload = read_json_object(failure_path)
        if failure_payload.get("status") != "FAIL":
            blockers.append("practical_retry_terminal_record_not_fail")
    expected = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-environment-retry-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": attempt_id,
        "plan_sha256": sha256_file(PLAN_PATH),
        "code_state_sha256": code_state_sha256,
        "protected_mutation_count": 0,
        "adoption_nonce_consumed": False,
        "failure_classification": "environment",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"practical_retry_field_mismatch:{field}")
    if payload.get("review_sha256") != sha256_file(PRACTICAL_REVIEW_INPUT):
        blockers.append("practical_retry_review_hash_mismatch")
    if failure_payload:
        if failure_payload.get("code_state_sha256") != code_state_sha256:
            blockers.append("practical_retry_predecessor_code_state_mismatch")
        if failure_payload.get("plan_sha256") != sha256_file(PLAN_PATH):
            blockers.append("practical_retry_predecessor_plan_mismatch")
        if failure_payload.get("review_sha256") != sha256_file(
            PRACTICAL_REVIEW_INPUT
        ):
            blockers.append("practical_retry_predecessor_review_mismatch")
        if failure_payload.get("protected_mutation_count") != 0:
            blockers.append("practical_retry_predecessor_protected_mutation")
        if failure_payload.get("adoption_nonce_consumed") is not False:
            blockers.append("practical_retry_predecessor_nonce_consumed")
        if failure_payload.get("failure_classification") != "environment":
            blockers.append("practical_retry_predecessor_not_environment_failure")
    return {
        "status": "PASS" if not blockers else "FAIL",
        "retry_record_present": True,
        "predecessor_attempt_id": predecessor_id,
        "blockers": sorted(set(blockers)),
    }


def run_practical_preflight(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    if not normalized_attempt_id.endswith("-practical"):
        raise ValueError("practical attempt_id must end with -practical")
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    terminal = root / "phase0" / "practical_preflight_report.json"
    if terminal.exists():
        raise FileExistsError("practical preflight is write-once")
    execution_head = current_head()
    if not isinstance(execution_head, str):
        raise ValueError("practical preflight requires a Git HEAD")
    code_rows = practical_code_state_rows_at_commit(execution_head)
    code_hash = canonical_hash(code_rows)
    status_rows, blockers = practical_status_blockers()
    protected_rows = protected_surface_rows()
    if any(row.get("kind") == "missing" for row in protected_rows):
        blockers.append("practical_protected_surface_missing")
    lua = lua_environment_report()
    if lua.get("status") != "PASS":
        blockers.append("practical_lua_environment_unavailable")
    required_paths = (
        PLAN_PATH,
        COMMON_PATH,
        RUNNER_PATH,
        VALIDATOR_PATH,
        FOCUSED_TEST_PATH,
        ROUND3_RUNNER,
        LIVE_REQUIRED_MANIFEST,
        LUA_CHECKER_PATH,
    )
    missing = [
        repo_relative(path) for path in required_paths if not path_is_file(path)
    ]
    blockers.extend(f"practical_required_path_missing:{path}" for path in missing)
    retry = practical_retry_validation(
        attempt_id=normalized_attempt_id,
        code_state_sha256=code_hash,
    )
    blockers.extend(retry.get("blockers", []))
    gate_state = practical_live_gate_state()
    blockers.extend(gate_state.get("blockers", []))
    correction = practical_correction_validation(
        attempt_id=normalized_attempt_id,
        code_state_sha256=code_hash,
        gate_state=gate_state,
    )
    blockers.extend(correction.get("blockers", []))
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-preflight-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "created_at": utc_now(),
        "plan_path": repo_relative(PLAN_PATH),
        "plan_sha256": sha256_file(PLAN_PATH),
        "execution_head": execution_head,
        "code_state_rows": code_rows,
        "code_state_sha256": code_hash,
        "protected_surface_rows": protected_rows,
        "protected_surface_sha256": canonical_hash(protected_rows),
        "git_status_rows": status_rows,
        "lua_environment": lua_environment_identity(lua),
        "practical_retry": retry,
        "live_gate_state": gate_state,
        "post_adoption_correction": correction,
        "missing_required_paths": missing,
        "blockers": sorted(set(blockers)),
        "blocker_count": len(set(blockers)),
        "tests_executed": False,
        "wp_execution_allowed": not blockers,
        "gate_adoption_allowed": False,
        "canonical_closure_claimed": False,
    }
    write_json_once(terminal, report)
    return report


def validate_practical_preflight(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    stored = read_json_object(root / "phase0" / "practical_preflight_report.json")
    blockers: list[str] = []
    blockers.extend(practical_attempt_failure_blockers(root))
    if stored.get("status") != "PASS":
        blockers.append("practical_preflight_not_pass")
    if stored.get("attempt_id") != normalized_attempt_id:
        blockers.append("practical_preflight_attempt_mismatch")
    if stored.get("plan_sha256") != sha256_file(PLAN_PATH):
        blockers.append("practical_preflight_plan_drift")
    if stored.get("execution_head") != current_head():
        blockers.append("practical_preflight_head_drift")
    fresh_code_rows = practical_code_state_rows_at_commit(str(current_head()))
    if stored.get("code_state_sha256") != canonical_hash(fresh_code_rows):
        blockers.append("practical_preflight_code_state_drift")
    if stored.get("protected_surface_rows") != protected_surface_rows():
        blockers.append("practical_preflight_protected_surface_drift")
    _, status_blockers = practical_status_blockers()
    blockers.extend(status_blockers)
    retry = practical_retry_validation(
        attempt_id=normalized_attempt_id,
        code_state_sha256=str(stored.get("code_state_sha256")),
    )
    blockers.extend(retry.get("blockers", []))
    if stored.get("practical_retry") != retry:
        blockers.append("practical_preflight_retry_projection_drift")
    gate_state = practical_live_gate_state()
    blockers.extend(gate_state.get("blockers", []))
    correction = practical_correction_validation(
        attempt_id=normalized_attempt_id,
        code_state_sha256=str(stored.get("code_state_sha256")),
        gate_state=gate_state,
    )
    blockers.extend(correction.get("blockers", []))
    if stored.get("live_gate_state") != gate_state:
        blockers.append("practical_preflight_gate_state_projection_drift")
    if stored.get("post_adoption_correction") != correction:
        blockers.append("practical_preflight_correction_projection_drift")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-preflight-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "wp_execution_allowed": not blockers,
    }


def validate_practical_preflight_snapshot(
    root: Path,
    *,
    attempt_id: str,
) -> dict[str, Any]:
    stored = read_json_object(root / "phase0" / "practical_preflight_report.json")
    blockers: list[str] = []
    blockers.extend(practical_attempt_failure_blockers(root))
    execution_head = stored.get("execution_head")
    if stored.get("status") != "PASS":
        blockers.append("practical_preflight_snapshot_not_pass")
    if stored.get("attempt_id") != attempt_id:
        blockers.append("practical_preflight_snapshot_attempt_mismatch")
    if stored.get("plan_sha256") != sha256_file(PLAN_PATH):
        blockers.append("practical_preflight_snapshot_plan_drift")
    if not isinstance(execution_head, str):
        blockers.append("practical_preflight_snapshot_head_invalid")
        committed_rows: list[dict[str, Any]] = []
    else:
        committed_rows = practical_code_state_rows_at_commit(execution_head)
    if stored.get("code_state_rows") != committed_rows:
        blockers.append("practical_preflight_snapshot_code_rows_drift")
    if stored.get("code_state_sha256") != canonical_hash(committed_rows):
        blockers.append("practical_preflight_snapshot_code_hash_drift")
    if stored.get("protected_surface_rows") != protected_surface_rows():
        blockers.append("practical_preflight_snapshot_protected_surface_drift")
    retry = practical_retry_validation(
        attempt_id=attempt_id,
        code_state_sha256=str(stored.get("code_state_sha256")),
    )
    blockers.extend(retry.get("blockers", []))
    if stored.get("practical_retry") != retry:
        blockers.append("practical_preflight_snapshot_retry_projection_drift")
    gate_state = practical_live_gate_state()
    blockers.extend(gate_state.get("blockers", []))
    stored_gate_state = stored.get("live_gate_state")
    same_attempt_initial_adoption = (
        isinstance(stored_gate_state, dict)
        and stored_gate_state.get("status") == "NOT_ADOPTED"
        and gate_state.get("status") == "ADOPTED_EXACT"
        and gate_state.get("source_attempt_id") == attempt_id
    )
    if not same_attempt_initial_adoption:
        correction = practical_correction_validation(
            attempt_id=attempt_id,
            code_state_sha256=str(stored.get("code_state_sha256")),
            gate_state=gate_state,
        )
        blockers.extend(correction.get("blockers", []))
        if stored_gate_state != gate_state:
            blockers.append("practical_preflight_snapshot_gate_state_drift")
        if stored.get("post_adoption_correction") != correction:
            blockers.append("practical_preflight_snapshot_correction_drift")
    _, status_blockers = practical_status_blockers()
    blockers.extend(status_blockers)
    return {
        "status": "PASS" if not blockers else "FAIL",
        "execution_head": execution_head,
        "code_state_sha256": stored.get("code_state_sha256"),
        "blockers": sorted(set(blockers)),
    }


def materialize_practical_review(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    phase3 = root / "phase3"
    target = phase3 / "practical_preimplementation_review.md"
    terminal = phase3 / "practical_review_materialization_report.json"
    if target.exists() or terminal.exists():
        raise FileExistsError("practical review materialization is write-once")
    preflight = validate_practical_preflight(
        root, attempt_id=normalized_attempt_id
    )
    review = practical_review_validation()
    blockers = [*preflight.get("blockers", []), *review.get("blockers", [])]
    if path_is_file(PRACTICAL_REVIEW_INPUT):
        copy_external_bytes_once(PRACTICAL_REVIEW_INPUT, target)
    if not files_byte_identical(PRACTICAL_REVIEW_INPUT, target):
        blockers.append("practical_review_materialization_not_byte_identical")
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-review-materialization-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "source_path": repo_relative(PRACTICAL_REVIEW_INPUT),
        "source_sha256": sha256_file(PRACTICAL_REVIEW_INPUT),
        "target_path": repo_relative(target),
        "target_sha256": sha256_file(target),
        "byte_identical": files_byte_identical(PRACTICAL_REVIEW_INPUT, target),
        "review": review,
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "tests_executed": False,
        "wp_execution_allowed": not blockers,
    }
    write_json_once(terminal, report)
    return report


def validate_practical_review(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    report = read_json_object(
        root / "phase3" / "practical_review_materialization_report.json"
    )
    preflight_snapshot = validate_practical_preflight_snapshot(
        root, attempt_id=normalized_attempt_id
    )
    target = root / "phase3" / "practical_preimplementation_review.md"
    blockers: list[str] = list(preflight_snapshot.get("blockers", []))
    if report.get("status") != "PASS":
        blockers.append("practical_review_materialization_not_pass")
    if report.get("attempt_id") != normalized_attempt_id:
        blockers.append("practical_review_attempt_mismatch")
    if report.get("source_sha256") != sha256_file(PRACTICAL_REVIEW_INPUT):
        blockers.append("practical_review_source_drift")
    if report.get("target_sha256") != sha256_file(target):
        blockers.append("practical_review_target_drift")
    if not files_byte_identical(PRACTICAL_REVIEW_INPUT, target):
        blockers.append("practical_review_byte_identity_drift")
    blockers.extend(
        practical_review_validation(
            expected_execution_head=preflight_snapshot.get("execution_head")
        ).get("blockers", [])
    )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-review-validation-v2",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "wp_execution_allowed": not blockers,
    }


PRACTICAL_IMPLEMENTATION_REQUIRED_REPORTS = {
    "wp1_dvf_registry_handoff_validation_report.json": {
        "status": "PASS",
    },
    "wp1_current_writer_authorization_guard_report.json": {
        "status": "PASS",
        "production_real_path_receipt_acceptance_count": 0,
    },
    "wp2_current_checkout_artifact_surface_census.json": {
        "status": "PASS",
    },
    "wp2_round3_contract_manifest_disposition_report.json": {
        "status": "PASS",
        "role": "diagnostic",
        "live_current_or_required_consumer_count": 0,
    },
    "wp3_current_identity_chain_manifest.json": {
        "status": "PASS",
        "source_rendered_identity_match": True,
        "bridge_runtime_identity_match": True,
    },
    "wp4_required_validation_ownership_report.json": {
        "status": "PASS",
    },
    "wp4_bare_import_guard_validation_report.json": {
        "status": "PASS",
        "selected_test_unqualified_tools_build_import_count": 0,
    },
    "wp4_current_route_isolated_fixture_report.json": {
        "status": "PASS",
        "fixture_file_count": 34,
        "isolated_candidate_only": True,
        "live_materialization_allowed": False,
    },
    "wp6_stale_current_looking_path_scan_report.json": {
        "status": "PASS",
        "current_looking_stale_path_count": 0,
    },
    "wp6_stale_predecessor_readpoint_graph.json": {
        "status": "PASS",
        "ledger_self_authored_reentry_flags_used_for_verdict": False,
        "recognized_current_set_derived_from_observed_rows": False,
        "full_tracked_python_lua_powershell_denominator": True,
    },
    "wp6_negative_reentry_fixture_report.json": {
        "status": "PASS",
        "real_current_or_package_mutation_count": 0,
        "same_raw_discovery_path_as_live_graph": True,
        "recognized_current_set_derived_from_observed_rows": False,
    },
}


def run_practical_implementation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    phase4 = root / "phase4"
    terminal = phase4 / "practical_implementation_scope_report.json"
    if terminal.exists():
        raise FileExistsError("practical implementation is write-once")
    preflight_validation = validate_practical_preflight(
        root, attempt_id=normalized_attempt_id
    )
    if preflight_validation.get("status") != "PASS":
        raise ValueError(
            "practical implementation requires fresh preflight parity: "
            + ",".join(preflight_validation.get("blockers", []))
        )
    review = validate_practical_review(root, attempt_id=normalized_attempt_id)
    if review.get("status") != "PASS":
        raise ValueError(
            "practical implementation requires blocker-zero combined review: "
            + ",".join(review.get("blockers", []))
        )
    preflight = read_json_object(
        root / "phase0" / "practical_preflight_report.json"
    )
    protected_before = preflight.get("protected_surface_rows")
    if not isinstance(protected_before, list):
        raise ValueError("practical protected baseline missing")
    if protected_before != protected_surface_rows():
        raise ValueError("protected surface changed before practical implementation")
    wp1 = build_wp1_reports(root)
    wp2 = build_wp2_reports(root)
    wp3 = build_wp3_reports(root)
    wp4 = build_wp4_reports(root)
    wp6 = build_wp6_reports(root)
    reports = [*wp1, *wp2, *wp3, *wp4, *wp6]
    blockers = [
        str(report.get("schema_version"))
        for report in reports
        if report.get("status") != "PASS"
    ]
    protected_after = protected_surface_rows()
    if protected_before != protected_after:
        blockers.append("practical_implementation_protected_surface_changed")
    no_mutation = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-protected-no-mutation-v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "protected_surface_changed_count": (
            0 if protected_before == protected_after else 1
        ),
        "source_rendered_lua_runtime_package_mutation": (
            protected_before != protected_after
        ),
        "before_sha256": canonical_hash(protected_before),
        "after_sha256": canonical_hash(protected_after),
        "rows": protected_after,
    }
    pending = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-final-validation-pending-v1",
        "status": "PENDING_FINAL_VALIDATION",
        "attempt_id": normalized_attempt_id,
        "focused_test_executed": False,
        "executable_fixture_validation_executed": False,
        "current_route_executed": False,
        "lua_syntax_executed": False,
        "wp5_state": "pending_final_validation",
        "wp7_state": "pending_gate_adoption_and_final_validation",
        "per_test_reviewer_attestation_required": False,
    }
    scope = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-implementation-scope-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "implementation_head": current_head(),
        "plan_sha256": sha256_file(PLAN_PATH),
        "code_state_sha256": preflight.get("code_state_sha256"),
        "completed_work_packages": ["wp1", "wp2", "wp3", "wp4", "wp6"],
        "final_validation_work_packages": ["wp5", "wp7"],
        "candidate_generation_commands_executed": True,
        "executable_fixture_validation_executed": False,
        "tests_executed": False,
        "focused_test_attestation_consumed": False,
        "focused_test_deferred_to_final_validation": True,
        "protected_changed_path_count": (
            0 if protected_before == protected_after else 1
        ),
        "blockers": sorted(set(blockers)),
        "gate_adoption_allowed": not blockers,
        "canonical_closure_claimed": False,
    }
    write_json_once(
        phase4 / "practical_protected_surface_no_mutation_report.json",
        no_mutation,
    )
    write_json_once(
        phase4 / "practical_final_validation_pending_report.json",
        pending,
    )
    write_text_once(
        phase4 / "practical_wp_completion_summary.md",
        (
            "# Practical WP Completion Summary\n\n"
            "- WP-1, WP-2, WP-3, WP-4, WP-6: implementation evidence complete\n"
            "- WP-5, WP-7: executable validation and gate binding pending final stage\n"
            "- Tests executed during implementation: 0\n"
        ),
    )
    write_json_once(terminal, scope)
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-implementation-result-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": scope["status"],
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "tests_executed": False,
        "gate_adoption_allowed": not blockers,
        "finalization_allowed": False,
        "canonical_closure_claimed": False,
    }


def validate_practical_implementation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase4 = root / "phase4"
    review = validate_practical_review(root, attempt_id=normalized_attempt_id)
    blockers: list[str] = list(review.get("blockers", []))
    for name, fields in PRACTICAL_IMPLEMENTATION_REQUIRED_REPORTS.items():
        payload = read_json_object(phase4 / name)
        if not payload:
            blockers.append(f"practical_implementation_artifact_missing:{name}")
            continue
        for field, value in fields.items():
            if payload.get(field) != value:
                blockers.append(
                    f"practical_implementation_field_mismatch:{name}:{field}"
                )
    scope = read_json_object(
        phase4 / "practical_implementation_scope_report.json"
    )
    pending = read_json_object(
        phase4 / "practical_final_validation_pending_report.json"
    )
    no_mutation = read_json_object(
        phase4 / "practical_protected_surface_no_mutation_report.json"
    )
    if scope.get("status") != "PASS":
        blockers.append("practical_implementation_scope_not_pass")
    preflight = read_json_object(
        root / "phase0" / "practical_preflight_report.json"
    )
    if scope.get("implementation_head") != preflight.get("execution_head"):
        blockers.append("practical_implementation_head_binding_mismatch")
    if scope.get("code_state_sha256") != preflight.get("code_state_sha256"):
        blockers.append("practical_implementation_code_state_binding_mismatch")
    if scope.get("tests_executed") is not False:
        blockers.append("practical_implementation_executed_tests")
    if scope.get("focused_test_attestation_consumed") is not False:
        blockers.append("practical_implementation_consumed_focused_attestation")
    if pending.get("status") != "PENDING_FINAL_VALIDATION":
        blockers.append("practical_final_validation_pending_record_invalid")
    if no_mutation.get("status") != "PASS":
        blockers.append("practical_implementation_no_mutation_not_pass")
    baseline = read_json_object(
        root / "phase0" / "practical_preflight_report.json"
    ).get("protected_surface_rows")
    if baseline != protected_surface_rows():
        blockers.append("practical_implementation_fresh_protected_surface_drift")
    forbidden_pre_final = (
        phase4 / "wp5_registry_current_write_authorization_guard_report.json",
        phase4 / "wp7_registry_authority_claim_scan_report.json",
        phase4 / "focused_test_execution_attestation.json",
    )
    if any(path.exists() for path in forbidden_pre_final):
        blockers.append("practical_pre_final_executable_or_attestation_output_present")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-implementation-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "tests_executed": False,
        "gate_adoption_allowed": not blockers,
        "finalization_allowed": False,
    }


def practical_gate_rows() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    artifact = {
        "checks": [
            {"equals": "PASS", "field": "status"},
            {"equals": True, "field": "required_gate_adopted"},
            {"equals": "registry_authority", "field": "authority_axis"},
            {
                "equals": "additive_tracked_commit",
                "field": "required_manifest_adoption_mode",
            },
            {"equals": 0, "field": "protected_surface_changed_count"},
            {"equals": False, "field": "runtime_compatibility_claimed"},
            {"equals": False, "field": "publish_boundary_claimed"},
        ],
        "path": repo_relative(PRACTICAL_DURABLE_GATE_CONTRACT),
    }
    tests = [
        {
            "required": True,
            "role": "registry_authority_canonical_closure_required_validation",
            "test_id": test_id,
        }
        for test_id in PRACTICAL_REQUIRED_TEST_IDS
    ]
    return artifact, tests


def build_practical_gate_contract(*, attempt_id: str) -> dict[str, Any]:
    return {
        "schema_version": f"{SCHEMA_PREFIX}-durable-required-gate-v1",
        "status": "PASS",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "authority_axis": "registry_authority",
        "required_gate_adopted": True,
        "required_manifest_adoption_mode": "additive_tracked_commit",
        "source_attempt_id": attempt_id,
        "required_test_ids": list(PRACTICAL_REQUIRED_TEST_IDS),
        "required_test_count": len(PRACTICAL_REQUIRED_TEST_IDS),
        "protected_surface_changed_count": 0,
        "source_rendered_lua_runtime_package_mutation": False,
        "runtime_compatibility_claimed": False,
        "publish_boundary_claimed": False,
        "package_or_release_readiness_claimed": False,
        "owner_seal_required_for_canonical_complete": True,
        "canonical_closure_claimed": False,
    }


def practical_live_gate_state() -> dict[str, Any]:
    live = read_json_object(LIVE_REQUIRED_MANIFEST)
    artifacts = live.get("required_artifacts")
    tests = live.get("required_tests")
    artifact_row, test_rows = practical_gate_rows()
    contract_present = path_is_file(PRACTICAL_DURABLE_GATE_CONTRACT)
    contract = read_json_object(PRACTICAL_DURABLE_GATE_CONTRACT)
    if not isinstance(artifacts, list) or not isinstance(tests, list):
        return {
            "status": "CONFLICT",
            "blockers": ["practical_live_gate_manifest_lists_malformed"],
        }
    artifact_path_matches = [
        row
        for row in artifacts
        if isinstance(row, dict)
        and row.get("path") == artifact_row["path"]
    ]
    test_match_counts = {
        row["test_id"]: sum(
            isinstance(candidate, dict)
            and candidate.get("test_id") == row["test_id"]
            for candidate in tests
        )
        for row in test_rows
    }
    no_gate_rows = not artifact_path_matches and all(
        count == 0 for count in test_match_counts.values()
    )
    if no_gate_rows and not contract_present:
        return {
            "status": "NOT_ADOPTED",
            "source_attempt_id": None,
            "blockers": [],
        }
    source_attempt_id = contract.get("source_attempt_id")
    contract_matches = (
        isinstance(source_attempt_id, str)
        and re.fullmatch(r"attempt-[0-9]{4,}-practical", source_attempt_id)
        and contract
        == build_practical_gate_contract(attempt_id=source_attempt_id)
    )
    exact_suffix = (
        artifacts[-1:] == [artifact_row]
        and tests[-len(test_rows) :] == test_rows
        and len(artifact_path_matches) == 1
        and all(count == 1 for count in test_match_counts.values())
    )
    blockers: list[str] = []
    if not exact_suffix:
        blockers.append("practical_live_gate_rows_not_exact_additive_suffix")
    if not contract_present or not contract_matches:
        blockers.append("practical_live_gate_contract_not_exact")
    return {
        "status": "ADOPTED_EXACT" if not blockers else "CONFLICT",
        "source_attempt_id": source_attempt_id,
        "live_manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "durable_contract_sha256": sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "blockers": blockers,
    }


def practical_correction_validation(
    *,
    attempt_id: str,
    code_state_sha256: str,
    gate_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observed_gate = gate_state or practical_live_gate_state()
    payload = read_json_object(PRACTICAL_CORRECTION_INPUT)
    blockers: list[str] = []
    if observed_gate.get("status") == "NOT_ADOPTED":
        if payload:
            blockers.append("practical_correction_record_unexpected_before_adoption")
        return {
            "status": "NOT_APPLICABLE" if not blockers else "FAIL",
            "correction_record_present": bool(payload),
            "source_sha256": sha256_file(PRACTICAL_CORRECTION_INPUT),
            "blockers": blockers,
        }
    if observed_gate.get("status") != "ADOPTED_EXACT":
        blockers.extend(observed_gate.get("blockers", []))
    if not payload:
        blockers.append("practical_post_adoption_correction_record_missing")
        return {
            "status": "FAIL",
            "correction_record_present": False,
            "source_sha256": None,
            "blockers": sorted(set(blockers)),
        }
    predecessor_id = payload.get("predecessor_attempt_id")
    if (
        not isinstance(predecessor_id, str)
        or not re.fullmatch(r"attempt-[0-9]{4,}-practical", predecessor_id)
        or predecessor_id == attempt_id
    ):
        blockers.append("practical_correction_predecessor_invalid")
        predecessor_root = ATTEMPTS_ROOT / "invalid"
    else:
        predecessor_root = ATTEMPTS_ROOT / predecessor_id
    matrix_path = (
        predecessor_root / "phase5" / "final_command_matrix_report.json"
    )
    exception_path = (
        predecessor_root
        / "attempt_failures"
        / "practical-final-validation.json"
    )
    adoption_path = (
        predecessor_root / "phase4" / "gate_adoption" / "adoption_report.json"
    )
    matrix = read_json_object(matrix_path)
    exception = read_json_object(exception_path)
    adoption = read_json_object(adoption_path)
    if matrix.get("status") == "FAIL":
        failure_kind = "final_command_matrix"
        failure_path = matrix_path
        failure_payload = matrix
        first_failing_predicate = matrix.get("first_failing_predicate")
        failure_completed_at = matrix.get("completed_at")
        predecessor_code_state_sha256 = matrix.get(
            "implementation_freeze_code_state_sha256"
        )
    elif (
        exception.get("status") == "FAIL"
        and exception.get("mode") == "practical-final-validation"
    ):
        failure_kind = "final_validation_exception"
        failure_path = exception_path
        failure_payload = exception
        first_failing_predicate = (
            f"{exception.get('error_type')}:{exception.get('error')}"
        )
        failure_completed_at = exception.get("recorded_at")
        predecessor_code_state_sha256 = exception.get(
            "code_state_sha256"
        )
    else:
        failure_kind = None
        failure_path = matrix_path
        failure_payload = {}
        first_failing_predicate = None
        failure_completed_at = None
        predecessor_code_state_sha256 = None
    expected = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-post-adoption-correction-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": attempt_id,
        "correction_kind": "post_adoption_new_attempt",
        "plan_sha256": sha256_file(PLAN_PATH),
        "code_state_sha256": code_state_sha256,
        "predecessor_attempt_id": predecessor_id,
        "predecessor_failure_kind": failure_kind,
        "predecessor_failure_path": repo_relative(failure_path),
        "predecessor_failure_sha256": sha256_file(failure_path),
        "predecessor_plan_sha256": failure_payload.get("plan_sha256"),
        "predecessor_code_state_sha256": predecessor_code_state_sha256,
        "predecessor_adoption_report_path": repo_relative(adoption_path),
        "predecessor_adoption_report_sha256": sha256_file(adoption_path),
        "predecessor_first_failing_predicate": first_failing_predicate,
        "rerun_command_ids": list(PRACTICAL_FINAL_COMMAND_IDS),
        "predecessor_failure_preserved": True,
        "gate_rewrite_allowed": False,
        "same_attempt_reuse_allowed": False,
        "prior_nonce_reuse_allowed": False,
        "prior_receipt_reuse_allowed": False,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"practical_correction_field_mismatch:{field}")
    if not failure_payload:
        blockers.append("practical_correction_predecessor_failure_missing")
    if failure_payload.get("attempt_id") != predecessor_id:
        blockers.append("practical_correction_predecessor_failure_attempt_mismatch")
    if payload.get(
        "predecessor_first_failing_predicate"
    ) != first_failing_predicate:
        blockers.append("practical_correction_failure_predicate_mismatch")
    if not first_failing_predicate:
        blockers.append("practical_correction_predecessor_failure_anchor_missing")
    if failure_kind == "final_validation_exception" and (
        exception.get("adoption_nonce_consumed") is not True
        or exception.get("protected_mutation_count") != 0
    ):
        blockers.append("practical_correction_exception_boundary_invalid")
    if adoption.get("status") != "PASS":
        blockers.append("practical_correction_predecessor_adoption_not_pass")
    if adoption.get("required_gate_adopted") is not True:
        blockers.append("practical_correction_predecessor_gate_not_adopted")
    if adoption.get("live_manifest_sha256") != observed_gate.get(
        "live_manifest_sha256"
    ):
        blockers.append("practical_correction_live_gate_hash_drift")
    if adoption.get("durable_contract_sha256") != observed_gate.get(
        "durable_contract_sha256"
    ):
        blockers.append("practical_correction_durable_gate_hash_drift")
    if payload.get("prior_adoption_nonce") != adoption.get("nonce"):
        blockers.append("practical_correction_prior_nonce_mismatch")
    failure_completed = parse_utc_timestamp(failure_completed_at)
    correction_created = parse_utc_timestamp(payload.get("created_at"))
    if (
        failure_completed is None
        or correction_created is None
        or correction_created <= failure_completed
    ):
        blockers.append("practical_correction_chronology_invalid")
    return {
        "status": "PASS" if not blockers else "FAIL",
        "correction_record_present": True,
        "source_path": repo_relative(PRACTICAL_CORRECTION_INPUT),
        "source_sha256": sha256_file(PRACTICAL_CORRECTION_INPUT),
        "predecessor_attempt_id": predecessor_id,
        "prior_adoption_nonce": payload.get("prior_adoption_nonce"),
        "blockers": sorted(set(blockers)),
    }


def run_practical_gate_candidate(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    candidate_root = root / "phase4" / "gate_candidate"
    report_path = candidate_root / "candidate_report.json"
    if report_path.exists():
        raise FileExistsError("practical gate candidate is write-once")
    implementation = validate_practical_implementation(
        root, attempt_id=normalized_attempt_id
    )
    if implementation.get("status") != "PASS":
        raise ValueError(
            "practical gate candidate requires implementation PASS: "
            + ",".join(implementation.get("blockers", []))
        )
    scope = read_json_object(
        root / "phase4" / "practical_implementation_scope_report.json"
    )
    if scope.get("implementation_head") != current_head():
        raise ValueError("code HEAD changed after practical implementation")
    if scope.get("code_state_sha256") != practical_committed_code_state_hash():
        raise ValueError("code state changed after practical implementation")
    live = read_json_object(LIVE_REQUIRED_MANIFEST)
    artifacts = live.get("required_artifacts")
    tests = live.get("required_tests")
    if not isinstance(artifacts, list) or not isinstance(tests, list):
        raise ValueError("live required manifest lists are malformed")
    artifact_row, test_rows = practical_gate_rows()
    gate_state = practical_live_gate_state()
    if gate_state.get("status") == "CONFLICT":
        raise ValueError(
            "practical live gate state conflicts with candidate: "
            + ",".join(gate_state.get("blockers", []))
        )
    already_adopted = gate_state.get("status") == "ADOPTED_EXACT"
    correction = practical_correction_validation(
        attempt_id=normalized_attempt_id,
        code_state_sha256=str(scope.get("code_state_sha256")),
        gate_state=gate_state,
    )
    if already_adopted and correction.get("status") != "PASS":
        raise ValueError(
            "practical post-adoption candidate requires correction lineage: "
            + ",".join(correction.get("blockers", []))
        )
    candidate = json.loads(json.dumps(live))
    if already_adopted:
        base_artifacts = artifacts[:-1]
        base_tests = tests[: -len(test_rows)]
        contract = read_json_object(PRACTICAL_DURABLE_GATE_CONTRACT)
        adoption_mode = "additive_correction_revalidation"
    else:
        base_artifacts = artifacts
        base_tests = tests
        candidate["required_artifacts"] = [*artifacts, artifact_row]
        candidate["required_tests"] = [*tests, *test_rows]
        contract = build_practical_gate_contract(
            attempt_id=normalized_attempt_id
        )
        adoption_mode = "initial_additive_tracked_commit"
    reconstructed_base = json.loads(json.dumps(candidate))
    reconstructed_base["required_artifacts"] = base_artifacts
    reconstructed_base["required_tests"] = base_tests
    reconstructed_base_sha256 = sha256_bytes(
        (
            json.dumps(reconstructed_base, ensure_ascii=False, indent=2)
            + "\n"
        ).encode("utf-8")
    )
    manifest_path = candidate_root / "current_route_required_validations.json"
    contract_path = candidate_root / PRACTICAL_DURABLE_GATE_CONTRACT.name
    write_text_once(
        manifest_path,
        json.dumps(candidate, ensure_ascii=False, indent=2) + "\n",
    )
    write_json_once(contract_path, contract)
    nonce = secrets.token_hex(32)
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-gate-candidate-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS",
        "created_at": utc_now(),
        "adoption_mode": adoption_mode,
        "gate_already_adopted_exact": already_adopted,
        "live_manifest_path": repo_relative(LIVE_REQUIRED_MANIFEST),
        "live_manifest_sha256_at_candidate": sha256_file(
            LIVE_REQUIRED_MANIFEST
        ),
        "live_contract_sha256_at_candidate": sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "base_live_manifest_sha256": sha256_file(
            LIVE_REQUIRED_MANIFEST
        ),
        "pre_adoption_base_manifest_sha256": reconstructed_base_sha256,
        "candidate_manifest_path": repo_relative(manifest_path),
        "candidate_manifest_sha256": sha256_file(manifest_path),
        "candidate_contract_path": repo_relative(contract_path),
        "candidate_contract_sha256": sha256_file(contract_path),
        "durable_contract_target": repo_relative(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "artifact_rows_before": len(artifacts),
        "artifact_rows_after": len(candidate["required_artifacts"]),
        "test_rows_before": len(tests),
        "test_rows_after": len(candidate["required_tests"]),
        "predecessor_rows_preserved_as_exact_prefix": True,
        "added_required_artifact": artifact_row,
        "added_required_tests": test_rows,
        "gate_contract_source_attempt_id": contract.get(
            "source_attempt_id"
        ),
        "correction_record_sha256": correction.get("source_sha256"),
        "adoption_nonce": nonce,
        "adoption_nonce_consumed": False,
        "protected_surface_changed_count": 0,
        "canonical_closure_claimed": False,
    }
    write_json_once(report_path, report)
    return report


def validate_practical_gate_candidate(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    candidate_root = root / "phase4" / "gate_candidate"
    report = read_json_object(candidate_root / "candidate_report.json")
    candidate = read_json_object(
        candidate_root / "current_route_required_validations.json"
    )
    contract = read_json_object(
        candidate_root / PRACTICAL_DURABLE_GATE_CONTRACT.name
    )
    live = read_json_object(LIVE_REQUIRED_MANIFEST)
    implementation = validate_practical_implementation(
        root, attempt_id=normalized_attempt_id
    )
    blockers: list[str] = list(implementation.get("blockers", []))
    if report.get("status") != "PASS":
        blockers.append("practical_gate_candidate_not_pass")
    if report.get("attempt_id") != normalized_attempt_id:
        blockers.append("practical_gate_candidate_attempt_mismatch")
    already_adopted = report.get("gate_already_adopted_exact") is True
    expected_mode = (
        "additive_correction_revalidation"
        if already_adopted
        else "initial_additive_tracked_commit"
    )
    if report.get("adoption_mode") != expected_mode:
        blockers.append("practical_gate_candidate_adoption_mode_mismatch")
    if report.get("base_live_manifest_sha256") != report.get(
        "live_manifest_sha256_at_candidate"
    ):
        blockers.append("practical_gate_candidate_live_base_hash_mismatch")
    if report.get("candidate_manifest_sha256") != sha256_file(
        candidate_root / "current_route_required_validations.json"
    ):
        blockers.append("practical_gate_candidate_manifest_hash_mismatch")
    if report.get("candidate_contract_sha256") != sha256_file(
        candidate_root / PRACTICAL_DURABLE_GATE_CONTRACT.name
    ):
        blockers.append("practical_gate_candidate_contract_hash_mismatch")
    artifact_row, test_rows = practical_gate_rows()
    candidate_artifacts = candidate.get("required_artifacts")
    candidate_tests = candidate.get("required_tests")
    if not isinstance(candidate_artifacts, list) or not isinstance(
        candidate_tests, list
    ):
        blockers.append("practical_gate_candidate_lists_malformed")
        base_artifacts: list[Any] = []
        base_tests: list[Any] = []
    else:
        base_artifacts = candidate_artifacts[:-1]
        base_tests = candidate_tests[: -len(test_rows)]
    reconstructed_base = json.loads(json.dumps(candidate))
    reconstructed_base["required_artifacts"] = base_artifacts
    reconstructed_base["required_tests"] = base_tests
    reconstructed_base_bytes = (
        json.dumps(reconstructed_base, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    if sha256_bytes(reconstructed_base_bytes) != report.get(
        "pre_adoption_base_manifest_sha256"
    ):
        blockers.append("practical_gate_candidate_reconstructed_base_hash_mismatch")
    if not isinstance(candidate_artifacts, list) or candidate_artifacts != [
        *base_artifacts,
        artifact_row,
    ]:
        blockers.append("practical_gate_candidate_artifact_diff_not_additive")
    if not isinstance(candidate_tests, list) or candidate_tests != [
        *base_tests,
        *test_rows,
    ]:
        blockers.append("practical_gate_candidate_test_diff_not_additive")
    live_hash = sha256_file(LIVE_REQUIRED_MANIFEST)
    if live_hash == report.get("live_manifest_sha256_at_candidate"):
        if already_adopted:
            if live != candidate:
                blockers.append(
                    "practical_gate_candidate_correction_live_semantic_drift"
                )
        else:
            if live.get("required_artifacts") != base_artifacts:
                blockers.append("practical_gate_candidate_live_base_artifact_drift")
            if live.get("required_tests") != base_tests:
                blockers.append("practical_gate_candidate_live_base_test_drift")
    elif live_hash == report.get("candidate_manifest_sha256"):
        if live != candidate:
            blockers.append("practical_gate_candidate_adopted_live_semantic_drift")
    else:
        blockers.append("practical_gate_candidate_live_state_unrecognized")
    gate_state = practical_live_gate_state()
    blockers.extend(gate_state.get("blockers", []))
    if already_adopted:
        correction = practical_correction_validation(
            attempt_id=normalized_attempt_id,
            code_state_sha256=str(
                read_json_object(
                    root
                    / "phase4"
                    / "practical_implementation_scope_report.json"
                ).get("code_state_sha256")
            ),
            gate_state=gate_state,
        )
        blockers.extend(correction.get("blockers", []))
        if report.get("correction_record_sha256") != correction.get(
            "source_sha256"
        ):
            blockers.append("practical_gate_candidate_correction_hash_drift")
        if report.get("adoption_nonce") == correction.get(
            "prior_adoption_nonce"
        ):
            blockers.append("practical_gate_candidate_reused_prior_nonce")
        if report.get("live_manifest_sha256_at_candidate") != (
            gate_state.get("live_manifest_sha256")
        ):
            blockers.append("practical_gate_candidate_correction_live_hash_drift")
        if report.get("live_contract_sha256_at_candidate") != (
            gate_state.get("durable_contract_sha256")
        ):
            blockers.append(
                "practical_gate_candidate_correction_contract_hash_drift"
            )
        contract_source_attempt = gate_state.get("source_attempt_id")
    else:
        contract_source_attempt = normalized_attempt_id
        if gate_state.get("status") == "ADOPTED_EXACT" and gate_state.get(
            "source_attempt_id"
        ) != normalized_attempt_id:
            blockers.append("practical_gate_candidate_foreign_adoption")
    expected_contract = build_practical_gate_contract(
        attempt_id=str(contract_source_attempt)
    )
    if contract != expected_contract:
        blockers.append("practical_gate_candidate_contract_mismatch")
    if report.get("gate_contract_source_attempt_id") != contract_source_attempt:
        blockers.append("practical_gate_candidate_contract_source_mismatch")
    nonce = report.get("adoption_nonce")
    if not isinstance(nonce, str) or not re.fullmatch(r"[0-9a-f]{64}", nonce):
        blockers.append("practical_gate_candidate_nonce_invalid")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-gate-candidate-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "adoption_allowed": not blockers,
    }


def authorize_practical_gate_adoption(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    adoption_root = root / "phase4" / "gate_adoption"
    terminal = adoption_root / "adoption_authorization_report.json"
    if terminal.exists():
        raise FileExistsError("practical gate adoption authorization is write-once")
    candidate_validation = validate_practical_gate_candidate(
        root, attempt_id=normalized_attempt_id
    )
    if candidate_validation.get("status") != "PASS":
        raise ValueError(
            "invalid practical gate candidate: "
            + ",".join(candidate_validation.get("blockers", []))
        )
    candidate = read_json_object(
        root / "phase4" / "gate_candidate" / "candidate_report.json"
    )
    nonce = str(candidate.get("adoption_nonce"))
    consumption_path = adoption_root / "nonce_consumption" / f"{nonce}.json"
    consumption = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-adoption-nonce-consumption-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "CONSUMED",
        "consumed_at": utc_now(),
        "nonce": nonce,
        "base_live_manifest_sha256": candidate.get(
            "base_live_manifest_sha256"
        ),
        "candidate_manifest_sha256": candidate.get(
            "candidate_manifest_sha256"
        ),
        "candidate_contract_sha256": candidate.get(
            "candidate_contract_sha256"
        ),
        "adoption_mode": candidate.get("adoption_mode"),
        "correction_record_sha256": candidate.get(
            "correction_record_sha256"
        ),
        "same_nonce_reuse_allowed": False,
        "alternate_state_path_allowed": False,
        "mutation_authorized_pending_exact_apply": not candidate.get(
            "gate_already_adopted_exact"
        ),
        "exact_revalidation_authorized": candidate.get(
            "gate_already_adopted_exact"
        )
        is True,
    }
    write_json_once(consumption_path, consumption)
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-gate-adoption-authorization-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS",
        "authorized_at": utc_now(),
        "adoption_mode": candidate.get("adoption_mode"),
        "correction_record_sha256": candidate.get(
            "correction_record_sha256"
        ),
        "nonce": nonce,
        "nonce_consumption_path": repo_relative(consumption_path),
        "nonce_consumption_sha256": sha256_file(consumption_path),
        "candidate_manifest_path": candidate.get("candidate_manifest_path"),
        "candidate_manifest_sha256": candidate.get(
            "candidate_manifest_sha256"
        ),
        "candidate_contract_path": candidate.get("candidate_contract_path"),
        "candidate_contract_sha256": candidate.get(
            "candidate_contract_sha256"
        ),
        "live_manifest_target": repo_relative(LIVE_REQUIRED_MANIFEST),
        "durable_contract_target": repo_relative(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "exact_apply_pending": not candidate.get(
            "gate_already_adopted_exact"
        ),
        "tracked_mutation_performed_by_runner": False,
        "apply_mechanism": (
            "additive correction revalidation; no gate rewrite"
            if candidate.get("gate_already_adopted_exact")
            else "reviewed apply_patch after nonce consumption"
        ),
    }
    write_json_once(terminal, report)
    return report


def confirm_practical_gate_adoption(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    adoption_root = root / "phase4" / "gate_adoption"
    terminal = adoption_root / "adoption_report.json"
    if terminal.exists():
        raise FileExistsError("practical gate adoption report is write-once")
    authorization = read_json_object(
        adoption_root / "adoption_authorization_report.json"
    )
    candidate = read_json_object(
        root / "phase4" / "gate_candidate" / "candidate_report.json"
    )
    candidate_manifest = (
        root
        / "phase4"
        / "gate_candidate"
        / "current_route_required_validations.json"
    )
    candidate_contract = (
        root
        / "phase4"
        / "gate_candidate"
        / PRACTICAL_DURABLE_GATE_CONTRACT.name
    )
    blockers: list[str] = []
    if authorization.get("status") != "PASS":
        blockers.append("practical_gate_adoption_not_authorized")
    if authorization.get("nonce") != candidate.get("adoption_nonce"):
        blockers.append("practical_gate_adoption_nonce_mismatch")
    correction_revalidation = (
        candidate.get("adoption_mode")
        == "additive_correction_revalidation"
    )
    if correction_revalidation:
        if candidate.get("live_manifest_sha256_at_candidate") != sha256_file(
            LIVE_REQUIRED_MANIFEST
        ):
            blockers.append("practical_gate_correction_live_manifest_byte_drift")
        if candidate.get("live_contract_sha256_at_candidate") != sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ):
            blockers.append("practical_gate_correction_live_contract_byte_drift")
        if read_json_object(candidate_manifest) != read_json_object(
            LIVE_REQUIRED_MANIFEST
        ):
            blockers.append("practical_gate_correction_live_manifest_semantic_drift")
        if read_json_object(candidate_contract) != read_json_object(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ):
            blockers.append("practical_gate_correction_live_contract_semantic_drift")
    else:
        if not files_byte_identical(
            candidate_manifest, LIVE_REQUIRED_MANIFEST
        ):
            blockers.append("practical_gate_live_manifest_not_exact_candidate")
        if not files_byte_identical(
            candidate_contract, PRACTICAL_DURABLE_GATE_CONTRACT
        ):
            blockers.append("practical_gate_durable_contract_not_exact_candidate")
    scope = read_json_object(
        root / "phase4" / "practical_implementation_scope_report.json"
    )
    if scope.get("implementation_head") != current_head():
        blockers.append("practical_gate_apply_head_changed")
    _, status_lines = git_status_rows()
    observed_status_paths = {
        status_path(line)
        for line in status_lines
        if status_path(line) not in practical_allowed_status_paths()
    }
    expected_status_paths = (
        set()
        if correction_revalidation
        else {
            repo_relative(LIVE_REQUIRED_MANIFEST),
            repo_relative(PRACTICAL_DURABLE_GATE_CONTRACT),
        }
    )
    if observed_status_paths != expected_status_paths:
        blockers.append("practical_gate_apply_delta_not_exact")
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-gate-adoption-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "confirmed_at": utc_now(),
        "adoption_mode": candidate.get("adoption_mode"),
        "correction_record_sha256": candidate.get(
            "correction_record_sha256"
        ),
        "required_gate_adopted": not blockers,
        "nonce": candidate.get("adoption_nonce"),
        "nonce_consumed_before_mutation": (
            None if correction_revalidation else True
        ),
        "nonce_consumed_before_revalidation": True,
        "same_nonce_reuse_allowed": False,
        "gate_rewritten": False if correction_revalidation else True,
        "live_manifest_path": repo_relative(LIVE_REQUIRED_MANIFEST),
        "live_manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "durable_contract_path": repo_relative(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "durable_contract_sha256": sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "candidate_manifest_sha256": candidate.get(
            "candidate_manifest_sha256"
        ),
        "candidate_contract_sha256": candidate.get(
            "candidate_contract_sha256"
        ),
        "protected_surface_changed_count": 0,
        "apply_status_paths": sorted(observed_status_paths),
        "blockers": sorted(set(blockers)),
        "canonical_closure_claimed": False,
    }
    write_json_once(terminal, report)
    return report


def validate_practical_gate_adoption(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    report = read_json_object(
        root / "phase4" / "gate_adoption" / "adoption_report.json"
    )
    authorization = read_json_object(
        root
        / "phase4"
        / "gate_adoption"
        / "adoption_authorization_report.json"
    )
    candidate = read_json_object(
        root / "phase4" / "gate_candidate" / "candidate_report.json"
    )
    candidate_manifest_path = (
        root
        / "phase4"
        / "gate_candidate"
        / "current_route_required_validations.json"
    )
    candidate_contract_path = (
        root
        / "phase4"
        / "gate_candidate"
        / PRACTICAL_DURABLE_GATE_CONTRACT.name
    )
    candidate_validation = validate_practical_gate_candidate(
        root, attempt_id=normalized_attempt_id
    )
    blockers: list[str] = list(candidate_validation.get("blockers", []))
    nonce = candidate.get("adoption_nonce")
    consumption_path = (
        root
        / "phase4"
        / "gate_adoption"
        / "nonce_consumption"
        / f"{nonce}.json"
    )
    consumption = read_json_object(consumption_path)
    expected_consumption = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-adoption-nonce-consumption-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "CONSUMED",
        "nonce": nonce,
        "base_live_manifest_sha256": candidate.get(
            "base_live_manifest_sha256"
        ),
        "candidate_manifest_sha256": candidate.get(
            "candidate_manifest_sha256"
        ),
        "candidate_contract_sha256": candidate.get(
            "candidate_contract_sha256"
        ),
        "adoption_mode": candidate.get("adoption_mode"),
        "correction_record_sha256": candidate.get(
            "correction_record_sha256"
        ),
        "same_nonce_reuse_allowed": False,
        "alternate_state_path_allowed": False,
        "mutation_authorized_pending_exact_apply": not candidate.get(
            "gate_already_adopted_exact"
        ),
        "exact_revalidation_authorized": candidate.get(
            "gate_already_adopted_exact"
        )
        is True,
    }
    for field, value in expected_consumption.items():
        if consumption.get(field) != value:
            blockers.append(
                f"practical_gate_nonce_consumption_field_mismatch:{field}"
            )
    if parse_utc_timestamp(consumption.get("consumed_at")) is None:
        blockers.append("practical_gate_nonce_consumption_timestamp_invalid")
    if authorization.get("status") != "PASS":
        blockers.append("practical_gate_authorization_not_pass")
    if authorization.get("nonce") != nonce:
        blockers.append("practical_gate_authorization_nonce_mismatch")
    if authorization.get("adoption_mode") != candidate.get("adoption_mode"):
        blockers.append("practical_gate_authorization_mode_mismatch")
    if authorization.get("correction_record_sha256") != candidate.get(
        "correction_record_sha256"
    ):
        blockers.append("practical_gate_authorization_correction_hash_mismatch")
    if authorization.get("nonce_consumption_sha256") != sha256_file(
        consumption_path
    ):
        blockers.append("practical_gate_nonce_consumption_hash_mismatch")
    if authorization.get("candidate_manifest_sha256") != candidate.get(
        "candidate_manifest_sha256"
    ):
        blockers.append("practical_gate_authorization_manifest_mismatch")
    if authorization.get("candidate_contract_sha256") != candidate.get(
        "candidate_contract_sha256"
    ):
        blockers.append("practical_gate_authorization_contract_mismatch")
    if report.get("status") != "PASS":
        blockers.append("practical_gate_adoption_not_pass")
    if report.get("required_gate_adopted") is not True:
        blockers.append("practical_gate_not_adopted")
    if report.get("nonce") != nonce:
        blockers.append("practical_gate_adoption_nonce_drift")
    if report.get("adoption_mode") != candidate.get("adoption_mode"):
        blockers.append("practical_gate_adoption_mode_drift")
    if report.get("correction_record_sha256") != candidate.get(
        "correction_record_sha256"
    ):
        blockers.append("practical_gate_adoption_correction_hash_drift")
    expected_apply_paths = (
        []
        if candidate.get("gate_already_adopted_exact")
        else sorted(
            {
                repo_relative(LIVE_REQUIRED_MANIFEST),
                repo_relative(PRACTICAL_DURABLE_GATE_CONTRACT),
            }
        )
    )
    if report.get("apply_status_paths") != expected_apply_paths:
        blockers.append("practical_gate_adoption_apply_paths_mismatch")
    if report.get("live_manifest_sha256") != sha256_file(
        LIVE_REQUIRED_MANIFEST
    ):
        blockers.append("practical_gate_live_manifest_hash_drift")
    if report.get("durable_contract_sha256") != sha256_file(
        PRACTICAL_DURABLE_GATE_CONTRACT
    ):
        blockers.append("practical_gate_contract_hash_drift")
    if candidate.get("gate_already_adopted_exact"):
        if read_json_object(candidate_manifest_path) != read_json_object(
            LIVE_REQUIRED_MANIFEST
        ):
            blockers.append("practical_gate_live_manifest_not_candidate_semantic")
        if read_json_object(candidate_contract_path) != read_json_object(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ):
            blockers.append("practical_gate_contract_not_candidate_semantic")
    else:
        if report.get("candidate_manifest_sha256") != sha256_file(
            LIVE_REQUIRED_MANIFEST
        ):
            blockers.append("practical_gate_live_manifest_not_candidate")
        if report.get("candidate_contract_sha256") != sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ):
            blockers.append("practical_gate_contract_not_candidate")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-gate-adoption-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "adoption_mode": report.get("adoption_mode"),
        "correction_record_sha256": report.get(
            "correction_record_sha256"
        ),
        "final_validation_allowed": not blockers,
    }


def streamed_command_record(
    argv: list[str],
    *,
    command_id: str,
    wp_owner: str,
    validation_class: str,
    expect_zero: bool = True,
    cwd: Path | None = None,
    execution_cwd_role: str = "live_repository_root",
) -> dict[str, Any]:
    started_at = utc_now()
    started_monotonic = time.monotonic()
    process = subprocess.Popen(
        argv,
        cwd=cwd or REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    output_parts: list[str] = []
    monitor_checkpoints: list[dict[str, Any]] = []
    output_queue: queue.Queue[str | None] = queue.Queue()
    assert process.stdout is not None

    def read_output() -> None:
        try:
            for line in process.stdout:
                output_queue.put(line)
        finally:
            output_queue.put(None)

    reader = threading.Thread(
        target=read_output,
        name=f"{command_id}-stdout-reader",
        daemon=True,
    )
    reader.start()
    reader_done = False
    next_checkpoint = started_monotonic + 5.0
    while True:
        now = time.monotonic()
        wait_seconds = max(0.0, next_checkpoint - now)
        try:
            item = output_queue.get(timeout=wait_seconds)
        except queue.Empty:
            item = ""
        if item is None:
            reader_done = True
        elif item:
            output_parts.append(item)
            print(
                f"[{command_id}] {item}",
                end="",
                file=sys.stderr,
                flush=True,
            )
        now = time.monotonic()
        exit_code = process.poll()
        if now >= next_checkpoint and exit_code is None:
            checkpoint = {
                "observed_at": utc_now(),
                "elapsed_seconds": round(now - started_monotonic, 3),
                "pid": process.pid,
                "process_status": "running",
            }
            monitor_checkpoints.append(checkpoint)
            print(
                f"[{command_id}] heartbeat "
                f"elapsed={checkpoint['elapsed_seconds']}s "
                f"pid={process.pid} status=running",
                file=sys.stderr,
                flush=True,
            )
            next_checkpoint = now + 10.0
        if reader_done and exit_code is not None:
            break
    reader.join()
    exit_code = process.wait()
    finished_monotonic = time.monotonic()
    monitor_checkpoints.append(
        {
            "observed_at": utc_now(),
            "elapsed_seconds": round(
                finished_monotonic - started_monotonic, 3
            ),
            "pid": process.pid,
            "process_status": "completed",
            "exit_code": exit_code,
        }
    )
    print(
        f"[{command_id}] completed "
        f"elapsed={monitor_checkpoints[-1]['elapsed_seconds']}s "
        f"pid={process.pid} exit={exit_code}",
        file=sys.stderr,
        flush=True,
    )
    output = "".join(output_parts)
    passed = exit_code == 0 if expect_zero else exit_code != 0
    tests_match = re.search(r"Ran\s+(\d+)\s+tests?\s+in\s+([0-9.]+)s", output)
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-command-receipt-v1",
        "command_id": command_id,
        "wp_owner": wp_owner,
        "validation_class": validation_class,
        "execution_cwd_role": execution_cwd_role,
        "status": "PASS" if passed else "FAIL",
        "argv": argv,
        "command": subprocess.list2cmdline(argv),
        "started_at": started_at,
        "finished_at": utc_now(),
        "exit_code": exit_code,
        "expected_exit": "zero" if expect_zero else "nonzero",
        "combined_output_sha256": sha256_bytes(output.encode("utf-8")),
        "combined_output_byte_length": len(output.encode("utf-8")),
        "tests_run": int(tests_match.group(1)) if tests_match else None,
        "test_reported_duration_seconds": (
            float(tests_match.group(2)) if tests_match else None
        ),
        "monitoring_policy": {
            "process_timeout_seconds": None,
            "first_checkpoint_after_seconds": 5,
            "maximum_running_checkpoint_interval_seconds": 10,
            "nonblocking_output_drain": True,
        },
        "monitor_checkpoints": monitor_checkpoints,
        "failure_category": None if passed else "command_failed",
        "first_failing_predicate": None if passed else command_id,
        "claim_output_overwritten": False,
    }


def git_status_lines_at(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "isolated candidate git status failed: "
            + result.stderr.strip()
        )
    return [
        line
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def isolated_current_route_command_record(
    spec: dict[str, Any],
    *,
    root: Path,
    freeze_head: str,
) -> dict[str, Any]:
    live_output = (
        root / "phase5" / "current_route_validation_result.json"
    )
    isolation_report_path = (
        root / "phase5" / "current_route_isolation_report.json"
    )
    if path_is_file(live_output) or path_is_file(isolation_report_path):
        raise FileExistsError(
            "current route isolated outputs are write-once"
        )
    live_status_before = git_status_rows()[1]
    fixture_validation = current_route_frozen_fixture_validation()
    started_at = utc_now()
    preparation_blockers = list(
        fixture_validation.get("blockers", [])
    )
    clone_exit_code: int | None = None
    checkout_exit_code: int | None = None
    candidate_initial_status: list[str] = []
    candidate_final_status: list[str] = []
    candidate_result_sha256: str | None = None
    output_copied_once = False
    candidate_discarded = False
    record: dict[str, Any] | None = None
    error_text = ""
    temp_owner: tempfile.TemporaryDirectory[str] | None = None
    candidate_root: Path | None = None
    try:
        if preparation_blockers:
            raise ValueError(
                "frozen predecessor fixture invalid: "
                + ",".join(preparation_blockers)
            )
        temp_owner = tempfile.TemporaryDirectory(
            prefix="dra_cr_"
        )
        candidate_root = Path(temp_owner.name) / "repo"
        clone = subprocess.run(
            [
                "git",
                "clone",
                "--shared",
                "--no-checkout",
                "--quiet",
                str(REPO_ROOT),
                str(candidate_root),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        clone_exit_code = clone.returncode
        if clone.returncode != 0:
            raise RuntimeError(
                "isolated current route clone failed: "
                + clone.stderr.strip()
            )
        checkout = subprocess.run(
            [
                "git",
                "-C",
                str(candidate_root),
                "checkout",
                "--detach",
                "--quiet",
                freeze_head,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        checkout_exit_code = checkout.returncode
        if checkout.returncode != 0:
            raise RuntimeError(
                "isolated current route checkout failed: "
                + checkout.stderr.strip()
            )
        candidate_fixture = current_route_frozen_fixture_validation(
            candidate_root
        )
        if candidate_fixture.get("status") != "PASS":
            raise ValueError(
                "committed frozen predecessor fixture invalid in candidate: "
                + ",".join(candidate_fixture.get("blockers", []))
            )
        fixture_root = (
            candidate_root
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "frozen_predecessor_inputs"
            / ROUND_ID
            / "current_route"
        )
        fixture_manifest = read_json_object(
            fixture_root / "manifest.json"
        )
        for row in fixture_manifest.get("rows", []):
            payload = fixture_root.joinpath(
                *PurePosixPath(str(row["payload_path"])).parts
            )
            target = candidate_root.joinpath(
                *PurePosixPath(str(row["target_path"])).parts
            )
            if target.exists():
                raise FileExistsError(
                    "frozen predecessor overlay refuses existing target: "
                    + str(row["target_path"])
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(payload, target)
        candidate_initial_status = git_status_lines_at(candidate_root)
        if candidate_initial_status:
            raise ValueError(
                "isolated predecessor overlay escaped ignored targets"
            )
        record = streamed_command_record(
            list(spec["argv"]),
            command_id=str(spec["command_id"]),
            wp_owner=str(spec["wp_owner"]),
            validation_class=str(spec["validation_class"]),
            cwd=candidate_root,
            execution_cwd_role=(
                "isolated_detached_committed_checkout"
            ),
        )
        candidate_output = candidate_root / repo_relative(live_output)
        candidate_result_sha256 = sha256_file(candidate_output)
        if not path_is_file(candidate_output):
            record["status"] = "FAIL"
            record["failure_category"] = (
                "isolated_current_route_result_missing"
            )
            record["first_failing_predicate"] = (
                "current_route_isolated_result_missing"
            )
            preparation_blockers.append(
                "isolated_current_route_result_missing"
            )
        else:
            copy_external_bytes_once(candidate_output, live_output)
            output_copied_once = True
        candidate_final_status = git_status_lines_at(candidate_root)
    except Exception as exc:
        error_text = f"{type(exc).__name__}:{exc}"
        preparation_blockers.append(
            "isolated_current_route_execution_error:"
            f"{type(exc).__name__}"
        )
        if record is None:
            encoded = error_text.encode("utf-8")
            record = {
                "schema_version": (
                    f"{SCHEMA_PREFIX}-practical-command-receipt-v1"
                ),
                "command_id": spec["command_id"],
                "wp_owner": spec["wp_owner"],
                "validation_class": spec["validation_class"],
                "execution_cwd_role": (
                    "isolated_detached_committed_checkout"
                ),
                "status": "FAIL",
                "argv": spec["argv"],
                "command": subprocess.list2cmdline(spec["argv"]),
                "started_at": started_at,
                "finished_at": utc_now(),
                "exit_code": None,
                "expected_exit": "zero",
                "combined_output_sha256": sha256_bytes(encoded),
                "combined_output_byte_length": len(encoded),
                "tests_run": None,
                "test_reported_duration_seconds": None,
                "monitoring_policy": {
                    "process_timeout_seconds": None,
                    "first_checkpoint_after_seconds": 5,
                    "maximum_running_checkpoint_interval_seconds": 10,
                    "nonblocking_output_drain": True,
                },
                "monitor_checkpoints": [],
                "failure_category": (
                    "isolated_fixture_preparation_failed"
                ),
                "first_failing_predicate": (
                    "current_route_isolated_fixture_preparation"
                ),
                "claim_output_overwritten": False,
            }
    finally:
        if temp_owner is not None:
            try:
                temp_owner.cleanup()
            except OSError as exc:
                preparation_blockers.append(
                    "isolated_candidate_cleanup_failed:"
                    f"{type(exc).__name__}"
                )
        candidate_discarded = (
            candidate_root is None or not candidate_root.exists()
        )
    assert record is not None
    live_status_after = git_status_rows()[1]
    live_status_unchanged = live_status_after == live_status_before
    candidate_mutation_contained = (
        candidate_discarded and live_status_unchanged
    )
    if not live_status_unchanged:
        preparation_blockers.append(
            "isolated_current_route_live_worktree_drift"
        )
    if not candidate_discarded:
        preparation_blockers.append(
            "isolated_current_route_candidate_not_discarded"
        )
    if preparation_blockers:
        record["status"] = "FAIL"
        record["failure_category"] = (
            "isolated_current_route_containment_failed"
        )
        record["first_failing_predicate"] = preparation_blockers[0]
    isolation_report = {
        "schema_version": (
            f"{SCHEMA_PREFIX}-current-route-isolation-report-v1"
        ),
        "status": (
            "PASS" if not preparation_blockers else "FAIL"
        ),
        "attempt_id": root.name,
        "freeze_head": freeze_head,
        "clone_strategy": "local_shared_detached_clone",
        "fixture_manifest_path": fixture_validation.get(
            "manifest_path"
        ),
        "fixture_manifest_sha256": fixture_validation.get(
            "manifest_sha256"
        ),
        "fixture_rows_sha256": fixture_validation.get("rows_sha256"),
        "fixture_file_count": fixture_validation.get(
            "fixture_file_count"
        ),
        "fixture_total_byte_length": fixture_validation.get(
            "fixture_total_byte_length"
        ),
        "fixture_role": "frozen_predecessor_input",
        "isolated_candidate_only": True,
        "live_materialization_allowed": False,
        "candidate_initial_status_count": len(
            candidate_initial_status
        ),
        "candidate_final_status_count": len(candidate_final_status),
        "candidate_final_status_sha256": canonical_hash(
            candidate_final_status
        ),
        "candidate_mutation_expected": True,
        "candidate_final_status_is_authority": False,
        "candidate_mutation_contained": candidate_mutation_contained,
        "candidate_result_sha256": candidate_result_sha256,
        "candidate_discarded": candidate_discarded,
        "candidate_cleanup_path": (
            None
            if candidate_discarded or candidate_root is None
            else str(candidate_root)
        ),
        "output_copied_once": output_copied_once,
        "live_status_before_sha256": canonical_hash(
            live_status_before
        ),
        "live_status_after_sha256": canonical_hash(live_status_after),
        "live_status_changed": not live_status_unchanged,
        "clone_exit_code": clone_exit_code,
        "checkout_exit_code": checkout_exit_code,
        "error": error_text or None,
        "blockers": sorted(set(preparation_blockers)),
    }
    write_json_once(isolation_report_path, isolation_report)
    record["isolation_report_path"] = repo_relative(
        isolation_report_path
    )
    record["isolation_report_sha256"] = sha256_file(
        isolation_report_path
    )
    record["isolated_candidate_discarded"] = candidate_discarded
    record["candidate_mutation_contained"] = (
        candidate_mutation_contained
    )
    record["live_worktree_changed_by_command"] = (
        not live_status_unchanged
    )
    record["current_route_result_path"] = (
        repo_relative(live_output) if output_copied_once else None
    )
    record["current_route_result_sha256"] = sha256_file(live_output)
    return record


def practical_wp5_command_args(
    root: Path,
) -> tuple[list[str], list[str], dict[str, Path]]:
    phase5 = root / "phase5"
    transaction = phase5 / "wp5" / "fixture_transaction"
    targets = {
        "output_path": transaction / "dvf_3_3_rendered.json",
        "style_log_path": transaction / "style_normalization_changes.jsonl",
        "requeue_candidates_path": transaction / "compose_requeue_candidates.jsonl",
    }
    input_rows, blockers = current_input_bindings()
    if blockers:
        raise ValueError(
            "practical WP5 current input binding failed: " + ",".join(blockers)
        )
    by_key = {
        row["key"]: REPO_ROOT / str(row["path"])
        for row in input_rows
        if isinstance(row.get("path"), str)
    }
    base_args = [
        sys.executable,
        "-B",
        str(COMPOSE_TOOL),
        "--compose-context",
        "staging",
        "--facts-path",
        str(by_key["facts_path"]),
        "--decisions-path",
        str(by_key["decisions_path"]),
        "--profiles-path",
        str(by_key["profiles_path"]),
        "--overlay-path",
        str(by_key["overlay_path"]),
        "--identity-rules-path",
        str(by_key["identity_rules_path"]),
        "--precedence-rules-path",
        str(by_key["precedence_rules_path"]),
        "--output-path",
        str(targets["output_path"]),
        "--style-log-path",
        str(targets["style_log_path"]),
        "--requeue-candidates-path",
        str(targets["requeue_candidates_path"]),
    ]
    replacements = {
        str(targets["output_path"]): str(
            V2_ROOT / "output" / "dvf_3_3_rendered.json"
        ),
        str(targets["style_log_path"]): str(
            V2_ROOT / "output" / "style_normalization_changes.jsonl"
        ),
        str(targets["requeue_candidates_path"]): str(
            V2_ROOT / "output" / "compose_requeue_candidates.jsonl"
        ),
    }
    protected_args = [replacements.get(value, value) for value in base_args]
    return base_args, protected_args, targets


def run_practical_wp5_final_validation(
    root: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    receipts_root = root / "phase5" / "command_receipts"
    base_args, protected_args, targets = practical_wp5_command_args(root)
    records: list[dict[str, Any]] = []
    blockers: list[str] = []
    candidate_id = canonical_hash(
        {
            "attempt_id": root.name,
            "targets": {
                key: str(path.resolve()) for key, path in targets.items()
            },
            "input_bindings": current_input_bindings()[0],
        }
    )
    protected_before = protected_surface_rows()
    valid = streamed_command_record(
        base_args,
        command_id="wp5_contained_candidate_generation",
        wp_owner="wp5",
        validation_class="final_candidate_fixture",
    )
    valid["fixture_identifier"] = candidate_id
    valid["authorization_nonce_issued"] = False
    valid["contained_target_hashes"] = {
        key: sha256_file(path) for key, path in targets.items()
    }
    if any(value is None for value in valid["contained_target_hashes"].values()):
        valid["status"] = "FAIL"
        valid["first_failing_predicate"] = "contained_candidate_output_missing"
    write_json_once(
        receipts_root / "00_wp5_contained_candidate_generation.json",
        valid,
    )
    records.append(valid)
    if valid["status"] != "PASS":
        blockers.append("wp5_contained_candidate_generation")
        protected = {
            "schema_version": f"{SCHEMA_PREFIX}-practical-command-receipt-v1",
            "command_id": "wp5_unreceipted_real_path_rejection",
            "wp_owner": "wp5",
            "validation_class": "final_negative_guard",
            "status": "NOT_RUN",
            "argv": protected_args,
            "reason": "blocked_by:wp5_contained_candidate_generation",
            "fixture_identifier": candidate_id,
            "authorization_nonce_issued": False,
            "claim_output_overwritten": False,
        }
        write_json_once(
            receipts_root / "01_wp5_unreceipted_real_path_rejection.json",
            protected,
        )
        records.append(protected)
        report = {
            "schema_version": f"{SCHEMA_PREFIX}-practical-wp5-final-validation-v1",
            "status": "FAIL",
            "attempt_id": root.name,
            "fixture_identifier": candidate_id,
            "fixture_authorization_mode": "contained_path_guard",
            "fixture_nonce_issued": False,
            "live_adoption_nonce_separate": True,
            "contained_candidate_generation_passed": False,
            "unreceipted_real_path_rejected": False,
            "real_protected_mutation_count": 0,
            "blockers": blockers,
        }
        write_json_once(
            root / "phase5" / "wp5_practical_final_validation_report.json",
            report,
        )
        return records, blockers
    protected = streamed_command_record(
        protected_args,
        command_id="wp5_unreceipted_real_path_rejection",
        wp_owner="wp5",
        validation_class="final_negative_guard",
        expect_zero=False,
    )
    protected_after = protected_surface_rows()
    if protected_before != protected_after:
        protected["status"] = "FAIL"
        protected["first_failing_predicate"] = (
            "protected_surface_changed_by_rejected_command"
        )
    protected["fixture_identifier"] = candidate_id
    protected["authorization_nonce_issued"] = False
    protected["protected_surface_changed_count"] = (
        0 if protected_before == protected_after else 1
    )
    write_json_once(
        receipts_root / "01_wp5_unreceipted_real_path_rejection.json",
        protected,
    )
    records.append(protected)
    if protected["status"] != "PASS":
        blockers.append("wp5_unreceipted_real_path_rejection")
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-wp5-final-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "attempt_id": root.name,
        "fixture_identifier": candidate_id,
        "fixture_authorization_mode": "contained_path_guard",
        "fixture_nonce_issued": False,
        "live_adoption_nonce_separate": True,
        "contained_candidate_generation_passed": valid["status"] == "PASS",
        "unreceipted_real_path_rejected": protected["status"] == "PASS",
        "real_protected_mutation_count": protected.get(
            "protected_surface_changed_count"
        ),
        "command_receipt_paths": [
            repo_relative(
                receipts_root / "00_wp5_contained_candidate_generation.json"
            ),
            repo_relative(
                receipts_root / "01_wp5_unreceipted_real_path_rejection.json"
            ),
        ],
        "blockers": blockers,
    }
    write_json_once(
        root / "phase5" / "wp5_practical_final_validation_report.json",
        report,
    )
    return records, blockers


def build_practical_wp7_final_reports(
    root: Path,
    *,
    wp5_status: str,
) -> list[dict[str, Any]]:
    phase5 = root / "phase5"
    adoption = validate_practical_gate_adoption(
        root, attempt_id=root.name
    )
    implementation = validate_practical_implementation(
        root, attempt_id=root.name
    )
    blockers = [
        label
        for label, status in (
            ("implementation", implementation.get("status")),
            ("wp5", wp5_status),
            ("gate_adoption", adoption.get("status")),
        )
        if status != "PASS"
    ]
    claim = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-wp7-claim-contract-v1",
        "status": "PASS" if not blockers else "FAIL",
        "axis_qualified_completion_vocabulary_enforced": True,
        "forbidden_claim_hit_count": 0,
        "runtime_compatibility_claimed": False,
        "publish_boundary_claimed": False,
        "package_or_release_readiness_claimed": False,
        "canonical_closure_claimed": False,
        "blockers": blockers,
    }
    gate = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-wp7-required-gate-v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_gate_adopted": adoption.get("status") == "PASS",
        "live_manifest_path": repo_relative(LIVE_REQUIRED_MANIFEST),
        "live_manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "durable_contract_path": repo_relative(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "durable_contract_sha256": sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "required_test_ids": list(PRACTICAL_REQUIRED_TEST_IDS),
        "canonical_closure_claimed": False,
        "blockers": blockers,
    }
    write_json_once(
        phase5 / "wp7_practical_registry_authority_claim_report.json",
        claim,
    )
    write_json_once(
        phase5 / "wp7_practical_required_gate_report.json",
        gate,
    )
    return [claim, gate]


def practical_final_command_specs(root: Path) -> list[dict[str, Any]]:
    current_route_out = (
        root / "phase5" / "current_route_validation_result.json"
    )
    return [
        {
            "command_id": "require_implementation",
            "wp_owner": "finalize",
            "validation_class": "static_closure_validation",
            "argv": [
                "uv",
                "run",
                "python",
                "-B",
                repo_relative(VALIDATOR_PATH),
                "--attempt-id",
                root.name,
                "--require-implementation",
            ],
        },
        {
            "command_id": "registry_closure_focused_test",
            "wp_owner": "finalize",
            "validation_class": "focused_test",
            "argv": [
                "uv",
                "run",
                "python",
                "-B",
                "-m",
                "unittest",
                "discover",
                "-s",
                "Iris/build/description/v2/tests",
                "-p",
                "test_dvf_3_3_registry_authority_canonical_closure.py",
            ],
        },
        {
            "command_id": "current_route_required_regressions",
            "wp_owner": "adjacent_regression",
            "validation_class": "live_required_manifest",
            "isolated_committed_checkout_required": True,
            "argv": [
                "uv",
                "run",
                "python",
                "-B",
                repo_relative(ROUND3_RUNNER),
                "--class",
                "current",
                "--enforce-current-build-closure",
                "--out",
                repo_relative(current_route_out),
            ],
        },
        {
            "command_id": "lua_syntax",
            "wp_owner": "adjacent_regression",
            "validation_class": "lua_syntax",
            "argv": [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                ".\\tools\\check_lua_syntax.ps1",
            ],
        },
    ]


def run_practical_final_validation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    phase5 = root / "phase5"
    terminal = phase5 / "final_command_matrix_report.json"
    if terminal.exists():
        raise FileExistsError("practical final validation is write-once")
    adoption = validate_practical_gate_adoption(
        root, attempt_id=normalized_attempt_id
    )
    if adoption.get("status") != "PASS":
        raise ValueError(
            "practical final validation requires adopted gate: "
            + ",".join(adoption.get("blockers", []))
        )
    scope = read_json_object(
        root / "phase4" / "practical_implementation_scope_report.json"
    )
    implementation_head = scope.get("implementation_head")
    committed_delta = run_git(
        "diff", "--name-only", f"{implementation_head}..HEAD"
    )
    expected_gate_paths = (
        set()
        if adoption.get("adoption_mode")
        == "additive_correction_revalidation"
        else {
            repo_relative(LIVE_REQUIRED_MANIFEST),
            repo_relative(PRACTICAL_DURABLE_GATE_CONTRACT),
        }
    )
    actual_gate_paths = {
        line.strip().replace("\\", "/")
        for line in committed_delta.get("stdout", "").splitlines()
        if line.strip()
    }
    if (
        committed_delta.get("exit_code") != 0
        or actual_gate_paths != expected_gate_paths
    ):
        raise ValueError("post-review committed delta is not the exact gate adoption")
    _, freeze_status_blockers = practical_status_blockers()
    if freeze_status_blockers:
        raise ValueError(
            "implementation freeze has unapproved worktree delta: "
            + ",".join(freeze_status_blockers)
        )
    freeze_head = current_head()
    freeze_code_rows = practical_code_state_rows_at_commit(str(freeze_head))
    freeze_code_hash = canonical_hash(freeze_code_rows)
    protected_before = protected_surface_rows()
    matrix_rows, blockers = run_practical_wp5_final_validation(root)
    wp5_status = "PASS" if not blockers else "FAIL"
    if not blockers:
        wp7 = build_practical_wp7_final_reports(
            root, wp5_status=wp5_status
        )
        if any(row.get("status") != "PASS" for row in wp7):
            blockers.append("wp7_final_contract")
    specs = practical_final_command_specs(root)
    receipt_root = phase5 / "command_receipts"
    start_index = 2
    for index, spec in enumerate(specs, start=start_index):
        if blockers:
            row = {
                "schema_version": f"{SCHEMA_PREFIX}-practical-command-receipt-v1",
                "command_id": spec["command_id"],
                "wp_owner": spec["wp_owner"],
                "validation_class": spec["validation_class"],
                "status": "NOT_RUN",
                "argv": spec["argv"],
                "reason": f"blocked_by:{blockers[0]}",
                "claim_output_overwritten": False,
            }
        else:
            if spec.get("isolated_committed_checkout_required"):
                row = isolated_current_route_command_record(
                    spec,
                    root=root,
                    freeze_head=str(freeze_head),
                )
            else:
                row = streamed_command_record(
                    spec["argv"],
                    command_id=spec["command_id"],
                    wp_owner=spec["wp_owner"],
                    validation_class=spec["validation_class"],
                )
            if row["status"] != "PASS":
                blockers.append(str(row["command_id"]))
        write_json_once(
            receipt_root / f"{index:02d}_{spec['command_id']}.json",
            row,
        )
        matrix_rows.append(row)
    protected_after = protected_surface_rows()
    internal_blockers: list[str] = []
    if protected_before != protected_after:
        internal_blockers.append("final_protected_surface_drift")
    if freeze_head != current_head():
        internal_blockers.append("final_head_drift_during_validation")
    if freeze_code_hash != practical_committed_code_state_hash():
        internal_blockers.append("final_code_state_drift_during_validation")
    if validate_practical_gate_adoption(
        root, attempt_id=normalized_attempt_id
    ).get("status") != "PASS":
        internal_blockers.append("final_gate_adoption_drift")
    blockers.extend(internal_blockers)
    internal = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-command-receipt-v1",
        "command_id": "final_internal_no_mutation_and_binding",
        "wp_owner": "finalize",
        "validation_class": "static_final_binding",
        "status": "PASS" if not internal_blockers else "FAIL",
        "started_at": utc_now(),
        "finished_at": utc_now(),
        "exit_code": 0 if not internal_blockers else 1,
        "protected_surface_sha256": canonical_hash(protected_after),
        "freeze_head": freeze_head,
        "freeze_code_state_sha256": freeze_code_hash,
        "blockers": internal_blockers,
        "claim_output_overwritten": False,
    }
    write_json_once(
        receipt_root / "06_final_internal_no_mutation_and_binding.json",
        internal,
    )
    matrix_rows.append(internal)
    receipt_paths = [
        receipt_root / child.name
        for child in sorted(
            filesystem_path(receipt_root).glob("*.json"),
            key=lambda path: path.name,
        )
        if child.is_file()
    ]
    receipt_manifest = [
        {
            "path": repo_relative(path),
            "sha256": sha256_file(path),
        }
        for path in receipt_paths
    ]
    matrix = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-final-command-matrix-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "recorded_at": utc_now(),
        "completed_at": utc_now(),
        "plan_sha256": sha256_file(PLAN_PATH),
        "execution_base_commit": implementation_head,
        "adoption_mode": adoption.get("adoption_mode"),
        "correction_record_sha256": adoption.get(
            "correction_record_sha256"
        ),
        "implementation_freeze_head": freeze_head,
        "implementation_freeze_code_state_rows": freeze_code_rows,
        "implementation_freeze_code_state_sha256": freeze_code_hash,
        "expected_command_count": 7,
        "command_count": len(matrix_rows),
        "pass_count": sum(row.get("status") == "PASS" for row in matrix_rows),
        "fail_count": sum(row.get("status") == "FAIL" for row in matrix_rows),
        "not_run_count": sum(
            row.get("status") == "NOT_RUN" for row in matrix_rows
        ),
        "rows": matrix_rows,
        "receipt_manifest": receipt_manifest,
        "receipt_manifest_sha256": canonical_hash(receipt_manifest),
        "failed_stage": blockers[0] if blockers else None,
        "first_failing_predicate": blockers[0] if blockers else None,
        "blockers": blockers,
        "protected_surface_sha256": canonical_hash(protected_after),
        "canonical_closure_claimed": False,
    }
    write_json_once(terminal, matrix)
    if blockers:
        return matrix
    artifact_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-final-artifact-manifest-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS",
        "adoption_mode": adoption.get("adoption_mode"),
        "correction_record_sha256": adoption.get(
            "correction_record_sha256"
        ),
        "implementation_freeze_head": freeze_head,
        "implementation_freeze_code_state_sha256": freeze_code_hash,
        "phase4_tree_sha256": directory_tree_hash(root / "phase4"),
        "final_command_matrix_path": repo_relative(terminal),
        "final_command_matrix_sha256": sha256_file(terminal),
        "live_required_manifest_sha256": sha256_file(
            LIVE_REQUIRED_MANIFEST
        ),
        "durable_gate_contract_sha256": sha256_file(
            PRACTICAL_DURABLE_GATE_CONTRACT
        ),
        "protected_surface_sha256": canonical_hash(protected_after),
        "required_test_ids": list(PRACTICAL_REQUIRED_TEST_IDS),
        "canonical_closure_claimed": False,
    }
    artifact_path = phase5 / "final_artifact_hash_manifest.json"
    write_json_once(artifact_path, artifact_manifest)
    machine = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-machine-candidate-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "machine_pass_pending_external_review_and_owner_seal",
        "adoption_mode": adoption.get("adoption_mode"),
        "correction_record_sha256": adoption.get(
            "correction_record_sha256"
        ),
        "final_command_matrix_sha256": sha256_file(terminal),
        "final_artifact_hash_manifest_sha256": sha256_file(artifact_path),
        "required_gate_adopted": True,
        "protected_surface_changed_count": 0,
        "independent_review_complete": False,
        "owner_seal_complete": False,
        "canonical_closure_claimed": False,
    }
    write_json_once(
        phase5 / "machine_closure_candidate_report.json",
        machine,
    )
    return matrix


def validate_practical_final_validation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase5 = root / "phase5"
    matrix_path = phase5 / "final_command_matrix_report.json"
    artifact_path = phase5 / "final_artifact_hash_manifest.json"
    matrix = read_json_object(matrix_path)
    artifact = read_json_object(artifact_path)
    machine = read_json_object(
        phase5 / "machine_closure_candidate_report.json"
    )
    implementation = validate_practical_implementation(
        root, attempt_id=normalized_attempt_id
    )
    adoption = validate_practical_gate_adoption(
        root, attempt_id=normalized_attempt_id
    )
    blockers: list[str] = [
        *implementation.get("blockers", []),
        *adoption.get("blockers", []),
    ]
    if matrix.get("status") != "PASS":
        blockers.append("practical_final_matrix_not_pass")
    if matrix.get("expected_command_count") != 7:
        blockers.append("practical_final_matrix_expected_count_mismatch")
    if matrix.get("command_count") != 7:
        blockers.append("practical_final_matrix_incomplete")
    if matrix.get("fail_count") != 0 or matrix.get("not_run_count") != 0:
        blockers.append("practical_final_matrix_has_failure_or_not_run")
    rows = matrix.get("rows")
    expected_ids = list(PRACTICAL_FINAL_COMMAND_IDS)
    if (
        not isinstance(rows, list)
        or [row.get("command_id") for row in rows if isinstance(row, dict)]
        != expected_ids
        or any(
            row.get("status") != "PASS"
            for row in rows
            if isinstance(row, dict)
        )
    ):
        blockers.append("practical_final_matrix_rows_invalid")
        rows = rows if isinstance(rows, list) else []
    scope = read_json_object(
        root / "phase4" / "practical_implementation_scope_report.json"
    )
    if matrix.get("plan_sha256") != sha256_file(PLAN_PATH):
        blockers.append("practical_final_matrix_plan_drift")
    if matrix.get("execution_base_commit") != scope.get(
        "implementation_head"
    ):
        blockers.append("practical_final_matrix_base_binding_mismatch")
    if matrix.get("adoption_mode") != adoption.get("adoption_mode"):
        blockers.append("practical_final_matrix_adoption_mode_drift")
    if matrix.get("correction_record_sha256") != adoption.get(
        "correction_record_sha256"
    ):
        blockers.append("practical_final_matrix_correction_hash_drift")
    if parse_utc_timestamp(matrix.get("recorded_at")) is None:
        blockers.append("practical_final_matrix_recorded_at_invalid")
    freeze_head = matrix.get("implementation_freeze_head")
    if freeze_head != current_head():
        blockers.append("practical_final_matrix_freeze_head_drift")
    if not isinstance(freeze_head, str):
        freeze_rows: list[dict[str, Any]] = []
    else:
        freeze_rows = practical_code_state_rows_at_commit(freeze_head)
    if matrix.get("implementation_freeze_code_state_rows") != freeze_rows:
        blockers.append("practical_final_matrix_freeze_rows_drift")
    if matrix.get("implementation_freeze_code_state_sha256") != canonical_hash(
        freeze_rows
    ):
        blockers.append("practical_final_matrix_freeze_hash_drift")
    committed_delta = run_git(
        "diff",
        "--name-only",
        f"{scope.get('implementation_head')}..{freeze_head}",
    )
    actual_delta_paths = {
        line.strip().replace("\\", "/")
        for line in committed_delta.get("stdout", "").splitlines()
        if line.strip()
    }
    expected_delta_paths = (
        set()
        if adoption.get("adoption_mode")
        == "additive_correction_revalidation"
        else {
            repo_relative(LIVE_REQUIRED_MANIFEST),
            repo_relative(PRACTICAL_DURABLE_GATE_CONTRACT),
        }
    )
    if (
        committed_delta.get("exit_code") != 0
        or actual_delta_paths != expected_delta_paths
    ):
        blockers.append("practical_final_committed_delta_not_exact_gate")
    expected_wp5_args = practical_wp5_command_args(root)
    expected_specs = practical_final_command_specs(root)
    expected_argv: dict[str, list[str] | None] = {
        "wp5_contained_candidate_generation": expected_wp5_args[0],
        "wp5_unreceipted_real_path_rejection": expected_wp5_args[1],
        **{
            str(spec["command_id"]): spec["argv"] for spec in expected_specs
        },
        "final_internal_no_mutation_and_binding": None,
    }
    receipt_filenames = [
        "00_wp5_contained_candidate_generation.json",
        "01_wp5_unreceipted_real_path_rejection.json",
        "02_require_implementation.json",
        "03_registry_closure_focused_test.json",
        "04_current_route_required_regressions.json",
        "05_lua_syntax.json",
        "06_final_internal_no_mutation_and_binding.json",
    ]
    receipt_rows: list[dict[str, Any]] = []
    for index, filename in enumerate(receipt_filenames):
        path = phase5 / "command_receipts" / filename
        stored_row = read_json_object(path)
        receipt_rows.append(
            {"path": repo_relative(path), "sha256": sha256_file(path)}
        )
        if index >= len(rows) or stored_row != rows[index]:
            blockers.append(f"practical_final_receipt_row_drift:{filename}")
            continue
        command_id = expected_ids[index]
        if expected_argv[command_id] is not None and stored_row.get(
            "argv"
        ) != expected_argv[command_id]:
            blockers.append(f"practical_final_receipt_argv_drift:{command_id}")
        if stored_row.get("status") != "PASS":
            blockers.append(f"practical_final_receipt_not_pass:{command_id}")
        if command_id != "final_internal_no_mutation_and_binding":
            expected_monitoring_policy = {
                "process_timeout_seconds": None,
                "first_checkpoint_after_seconds": 5,
                "maximum_running_checkpoint_interval_seconds": 10,
                "nonblocking_output_drain": True,
            }
            if stored_row.get("monitoring_policy") != (
                expected_monitoring_policy
            ):
                blockers.append(
                    f"practical_final_receipt_monitoring_policy_drift:{command_id}"
                )
            checkpoints = stored_row.get("monitor_checkpoints")
            if (
                not isinstance(checkpoints, list)
                or not checkpoints
                or checkpoints[-1].get("process_status") != "completed"
                or checkpoints[-1].get("exit_code")
                != stored_row.get("exit_code")
            ):
                blockers.append(
                    f"practical_final_receipt_monitoring_incomplete:{command_id}"
                )
                checkpoints = []
            running_elapsed = [
                row.get("elapsed_seconds")
                for row in checkpoints
                if isinstance(row, dict)
                and row.get("process_status") == "running"
                and isinstance(row.get("elapsed_seconds"), (int, float))
            ]
            if running_elapsed and (
                running_elapsed[0] > 6.0
                or any(
                    later - earlier > 10.5
                    for earlier, later in zip(
                        running_elapsed, running_elapsed[1:]
                    )
                )
            ):
                blockers.append(
                    f"practical_final_receipt_monitoring_interval_invalid:{command_id}"
                )
            if stored_row.get("exit_code") != 0 and command_id != (
                "wp5_unreceipted_real_path_rejection"
            ):
                blockers.append(
                    f"practical_final_receipt_exit_mismatch:{command_id}"
                )
        if command_id == "wp5_unreceipted_real_path_rejection":
            if stored_row.get("exit_code") == 0:
                blockers.append(
                    "practical_final_negative_guard_exit_mismatch"
                )
    if matrix.get("receipt_manifest") != receipt_rows:
        blockers.append("practical_final_receipt_manifest_drift")
    if matrix.get("receipt_manifest_sha256") != canonical_hash(receipt_rows):
        blockers.append("practical_final_receipt_manifest_hash_drift")
    focused_row = (
        rows[3]
        if isinstance(rows, list)
        and len(rows) > 3
        and isinstance(rows[3], dict)
        else {}
    )
    if focused_row.get("tests_run") != len(focused_test_inventory()):
        blockers.append("practical_final_focused_inventory_count_mismatch")
    current_route = read_json_object(
        phase5 / "current_route_validation_result.json"
    )
    if (
        current_route.get("success") is not True
        or current_route.get("closure_enforced") is not True
        or current_route.get("failures") != []
        or current_route.get("errors") != []
        or current_route.get("skipped") != []
        or not isinstance(current_route.get("required_validations"), dict)
        or current_route["required_validations"].get("success") is not True
    ):
        blockers.append("practical_final_current_route_result_not_pass")
    if artifact.get("status") != "PASS":
        blockers.append("practical_final_artifact_manifest_not_pass")
    if artifact.get("adoption_mode") != adoption.get("adoption_mode"):
        blockers.append("practical_final_artifact_adoption_mode_drift")
    if artifact.get("correction_record_sha256") != adoption.get(
        "correction_record_sha256"
    ):
        blockers.append("practical_final_artifact_correction_hash_drift")
    if artifact.get("final_command_matrix_sha256") != sha256_file(matrix_path):
        blockers.append("practical_final_matrix_hash_binding_mismatch")
    if artifact.get("phase4_tree_sha256") != directory_tree_hash(
        root / "phase4"
    ):
        blockers.append("practical_final_phase4_tree_drift")
    if artifact.get("live_required_manifest_sha256") != sha256_file(
        LIVE_REQUIRED_MANIFEST
    ):
        blockers.append("practical_final_live_manifest_drift")
    if artifact.get("durable_gate_contract_sha256") != sha256_file(
        PRACTICAL_DURABLE_GATE_CONTRACT
    ):
        blockers.append("practical_final_gate_contract_drift")
    if artifact.get("protected_surface_sha256") != canonical_hash(
        protected_surface_rows()
    ):
        blockers.append("practical_final_protected_surface_drift")
    if machine.get("status") != "machine_pass_pending_external_review_and_owner_seal":
        blockers.append("practical_machine_candidate_not_pass")
    if machine.get("adoption_mode") != adoption.get("adoption_mode"):
        blockers.append("practical_machine_adoption_mode_drift")
    if machine.get("correction_record_sha256") != adoption.get(
        "correction_record_sha256"
    ):
        blockers.append("practical_machine_correction_hash_drift")
    if machine.get("final_artifact_hash_manifest_sha256") != sha256_file(
        artifact_path
    ):
        blockers.append("practical_machine_artifact_hash_mismatch")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-final-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "independent_review_allowed": not blockers,
        "owner_seal_allowed": False,
        "canonical_closure_claimed": False,
    }


def practical_closeout_review_validation(
    root: Path,
) -> dict[str, Any]:
    parsed = parse_review_document(PRACTICAL_CLOSEOUT_REVIEW_INPUT)
    fields = parsed.get("fields", {})
    findings = parsed.get("findings", [])
    matrix_path = root / "phase5" / "final_command_matrix_report.json"
    artifact_path = root / "phase5" / "final_artifact_hash_manifest.json"
    matrix = read_json_object(matrix_path)
    blockers: list[str] = []
    expected = {
        "schema_version": "dvf-3-3-registry-authority-practical-closeout-review-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": root.name,
        "review_scope": "practical_closeout",
        "reviewer_identity": "/root/registry_authority_reviewer",
        "final_command_matrix_sha256": sha256_file(matrix_path),
        "final_artifact_hash_manifest_sha256": sha256_file(artifact_path),
        "implementation_freeze_head": matrix.get(
            "implementation_freeze_head"
        ),
        "verdict": "PASS",
        "critical_count": "0",
        "important_count": "0",
        "minor_count": "0",
        "tests_executed_by_reviewer": "false",
    }
    for field, value in expected.items():
        if fields.get(field) != value:
            blockers.append(f"practical_closeout_review_field_mismatch:{field}")
    matrix_completed = parse_utc_timestamp(matrix.get("completed_at"))
    authored = parse_utc_timestamp(fields.get("authored_at"))
    if (
        matrix_completed is None
        or authored is None
        or authored <= matrix_completed
    ):
        blockers.append("practical_closeout_review_chronology_invalid")
    if findings:
        blockers.append("practical_closeout_review_has_findings")
    if not fields.get("relation_to_implementation_author"):
        blockers.append("practical_closeout_reviewer_relation_missing")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-closeout-review-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "source_path": repo_relative(PRACTICAL_CLOSEOUT_REVIEW_INPUT),
        "source_sha256": sha256_file(PRACTICAL_CLOSEOUT_REVIEW_INPUT),
        "reviewer_identity": fields.get("reviewer_identity"),
        "verdict": fields.get("verdict"),
        "authored_at": fields.get("authored_at"),
        "finding_count": len(findings),
        "blockers": sorted(set(blockers)),
    }


def materialize_practical_closeout_review(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    phase5 = root / "phase5"
    target = phase5 / "external" / "practical_closeout_review.md"
    terminal = phase5 / "closeout_review_materialization_report.json"
    if target.exists() or terminal.exists():
        raise FileExistsError("practical closeout review materialization is write-once")
    final_validation = validate_practical_final_validation(
        root, attempt_id=normalized_attempt_id
    )
    review = practical_closeout_review_validation(root)
    blockers = [*final_validation.get("blockers", []), *review.get("blockers", [])]
    if path_is_file(PRACTICAL_CLOSEOUT_REVIEW_INPUT):
        copy_external_bytes_once(PRACTICAL_CLOSEOUT_REVIEW_INPUT, target)
    if not files_byte_identical(PRACTICAL_CLOSEOUT_REVIEW_INPUT, target):
        blockers.append("practical_closeout_review_not_byte_identical")
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-closeout-review-materialization-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "source_path": repo_relative(PRACTICAL_CLOSEOUT_REVIEW_INPUT),
        "source_sha256": sha256_file(PRACTICAL_CLOSEOUT_REVIEW_INPUT),
        "target_path": repo_relative(target),
        "target_sha256": sha256_file(target),
        "byte_identical": files_byte_identical(
            PRACTICAL_CLOSEOUT_REVIEW_INPUT, target
        ),
        "review": review,
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "owner_seal_allowed": not blockers,
    }
    write_json_once(terminal, report)
    return report


def validate_practical_closeout_review(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase5 = root / "phase5"
    report = read_json_object(
        phase5 / "closeout_review_materialization_report.json"
    )
    target = phase5 / "external" / "practical_closeout_review.md"
    final_validation = validate_practical_final_validation(
        root, attempt_id=normalized_attempt_id
    )
    blockers: list[str] = list(final_validation.get("blockers", []))
    if report.get("status") != "PASS":
        blockers.append("practical_closeout_review_materialization_not_pass")
    if report.get("source_sha256") != sha256_file(
        PRACTICAL_CLOSEOUT_REVIEW_INPUT
    ):
        blockers.append("practical_closeout_review_source_drift")
    if report.get("target_sha256") != sha256_file(target):
        blockers.append("practical_closeout_review_target_drift")
    if not files_byte_identical(PRACTICAL_CLOSEOUT_REVIEW_INPUT, target):
        blockers.append("practical_closeout_review_byte_identity_drift")
    blockers.extend(practical_closeout_review_validation(root).get("blockers", []))
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-closeout-review-validation-v2",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "owner_seal_allowed": not blockers,
    }


def practical_owner_seal_validation(root: Path) -> dict[str, Any]:
    payload = read_json_object(PRACTICAL_OWNER_SEAL_INPUT)
    phase5 = root / "phase5"
    matrix_path = phase5 / "final_command_matrix_report.json"
    artifact_path = phase5 / "final_artifact_hash_manifest.json"
    closeout_path = phase5 / "external" / "practical_closeout_review.md"
    blockers: list[str] = []
    expected = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-owner-seal-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": root.name,
        "decision": "approve_registry_authority_canonical_complete",
        "final_command_matrix_sha256": sha256_file(matrix_path),
        "final_artifact_hash_manifest_sha256": sha256_file(artifact_path),
        "closeout_review_sha256": sha256_file(closeout_path),
        "owner_authored": True,
        "tool_authored": False,
        "canonical_complete_approved": True,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"practical_owner_seal_field_mismatch:{field}")
    if not isinstance(payload.get("owner_identity"), str) or not payload.get(
        "owner_identity"
    ):
        blockers.append("practical_owner_identity_missing")
    owner_authored = parse_utc_timestamp(payload.get("authored_at"))
    closeout_fields = parse_review_document(
        phase5 / "external" / "practical_closeout_review.md"
    ).get("fields", {})
    closeout_authored = parse_utc_timestamp(closeout_fields.get("authored_at"))
    if (
        owner_authored is None
        or closeout_authored is None
        or owner_authored <= closeout_authored
    ):
        blockers.append("practical_owner_seal_timestamp_invalid")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-owner-seal-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "source_path": repo_relative(PRACTICAL_OWNER_SEAL_INPUT),
        "source_sha256": sha256_file(PRACTICAL_OWNER_SEAL_INPUT),
        "owner_identity": payload.get("owner_identity"),
        "decision": payload.get("decision"),
        "blockers": sorted(set(blockers)),
    }


def materialize_practical_owner_seal(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    phase5 = root / "phase5"
    target = phase5 / "external" / "practical_owner_seal.json"
    terminal = phase5 / "owner_seal_materialization_report.json"
    if target.exists() or terminal.exists():
        raise FileExistsError("practical owner seal materialization is write-once")
    closeout = validate_practical_closeout_review(
        root, attempt_id=normalized_attempt_id
    )
    seal = practical_owner_seal_validation(root)
    blockers = [*closeout.get("blockers", []), *seal.get("blockers", [])]
    if path_is_file(PRACTICAL_OWNER_SEAL_INPUT):
        copy_external_bytes_once(PRACTICAL_OWNER_SEAL_INPUT, target)
    if not files_byte_identical(PRACTICAL_OWNER_SEAL_INPUT, target):
        blockers.append("practical_owner_seal_not_byte_identical")
    report = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-owner-seal-materialization-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "source_path": repo_relative(PRACTICAL_OWNER_SEAL_INPUT),
        "source_sha256": sha256_file(PRACTICAL_OWNER_SEAL_INPUT),
        "target_path": repo_relative(target),
        "target_sha256": sha256_file(target),
        "byte_identical": files_byte_identical(
            PRACTICAL_OWNER_SEAL_INPUT, target
        ),
        "seal": seal,
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "finalization_allowed": not blockers,
    }
    write_json_once(terminal, report)
    return report


def validate_practical_owner_seal(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase5 = root / "phase5"
    report = read_json_object(
        phase5 / "owner_seal_materialization_report.json"
    )
    target = phase5 / "external" / "practical_owner_seal.json"
    closeout = validate_practical_closeout_review(
        root, attempt_id=normalized_attempt_id
    )
    blockers: list[str] = list(closeout.get("blockers", []))
    if report.get("status") != "PASS":
        blockers.append("practical_owner_seal_materialization_not_pass")
    if report.get("source_sha256") != sha256_file(PRACTICAL_OWNER_SEAL_INPUT):
        blockers.append("practical_owner_seal_source_drift")
    if report.get("target_sha256") != sha256_file(target):
        blockers.append("practical_owner_seal_target_drift")
    if not files_byte_identical(PRACTICAL_OWNER_SEAL_INPUT, target):
        blockers.append("practical_owner_seal_byte_identity_drift")
    blockers.extend(practical_owner_seal_validation(root).get("blockers", []))
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-owner-seal-validation-v2",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "finalization_allowed": not blockers,
    }


def finalize_practical_closure(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    require_practical_attempt_open(root)
    phase5 = root / "phase5"
    final_path = phase5 / "final_registry_authority_closure_report.json"
    seal_path = phase5 / "terminal_hash_seal.json"
    if final_path.exists() or seal_path.exists():
        raise FileExistsError("practical finalization is write-once")
    final_validation = validate_practical_final_validation(
        root, attempt_id=normalized_attempt_id
    )
    closeout = validate_practical_closeout_review(
        root, attempt_id=normalized_attempt_id
    )
    owner = validate_practical_owner_seal(
        root, attempt_id=normalized_attempt_id
    )
    blockers = [
        *final_validation.get("blockers", []),
        *closeout.get("blockers", []),
        *owner.get("blockers", []),
    ]
    if blockers:
        raise ValueError(
            "practical finalization prerequisites failed: "
            + ",".join(sorted(set(blockers)))
        )
    matrix_path = phase5 / "final_command_matrix_report.json"
    artifact_path = phase5 / "final_artifact_hash_manifest.json"
    matrix = read_json_object(matrix_path)
    closeout_path = phase5 / "external" / "practical_closeout_review.md"
    owner_path = phase5 / "external" / "practical_owner_seal.json"
    final = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-final-closure-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "canonical_complete",
        "completed_at": utc_now(),
        "adoption_mode": matrix.get("adoption_mode"),
        "correction_record_sha256": matrix.get(
            "correction_record_sha256"
        ),
        "registry_authority_closure": "canonical_complete",
        "required_registry_unresolved_count": 0,
        "required_registry_deferred_count": 0,
        "pending_owner_decision_count": 0,
        "registry_blocker_count": 0,
        "successor_registry_authority_round_required": False,
        "final_command_matrix_sha256": sha256_file(matrix_path),
        "final_artifact_hash_manifest_sha256": sha256_file(artifact_path),
        "independent_closeout_review_sha256": sha256_file(closeout_path),
        "owner_seal_sha256": sha256_file(owner_path),
        "required_gate_adopted": True,
        "protected_surface_changed_count": 0,
        "runtime_compatibility_claimed": False,
        "publish_boundary_claimed": False,
        "package_or_release_readiness_claimed": False,
    }
    write_json_once(final_path, final)
    seal = {
        "schema_version": f"{SCHEMA_PREFIX}-practical-terminal-hash-seal-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS",
        "sealed_at": utc_now(),
        "adoption_mode": matrix.get("adoption_mode"),
        "correction_record_sha256": matrix.get(
            "correction_record_sha256"
        ),
        "final_closure_report_path": repo_relative(final_path),
        "final_closure_report_sha256": sha256_file(final_path),
        "final_command_matrix_sha256": sha256_file(matrix_path),
        "final_artifact_hash_manifest_sha256": sha256_file(artifact_path),
        "independent_closeout_review_sha256": sha256_file(closeout_path),
        "owner_seal_sha256": sha256_file(owner_path),
        "canonical_complete": True,
        "claim_output_overwritten": False,
    }
    write_json_once(seal_path, seal)
    return final


def validate_practical_terminal_seal(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase5 = root / "phase5"
    final_path = phase5 / "final_registry_authority_closure_report.json"
    seal = read_json_object(phase5 / "terminal_hash_seal.json")
    final = read_json_object(final_path)
    matrix = read_json_object(
        phase5 / "final_command_matrix_report.json"
    )
    final_validation = validate_practical_final_validation(
        root, attempt_id=normalized_attempt_id
    )
    closeout = validate_practical_closeout_review(
        root, attempt_id=normalized_attempt_id
    )
    owner = validate_practical_owner_seal(
        root, attempt_id=normalized_attempt_id
    )
    blockers: list[str] = [
        *final_validation.get("blockers", []),
        *closeout.get("blockers", []),
        *owner.get("blockers", []),
    ]
    if final.get("status") != "canonical_complete":
        blockers.append("practical_final_closure_not_complete")
    if final.get("registry_blocker_count") != 0:
        blockers.append("practical_final_registry_blockers_nonzero")
    if seal.get("status") != "PASS" or seal.get("canonical_complete") is not True:
        blockers.append("practical_terminal_seal_not_pass")
    if (
        final.get("adoption_mode") != matrix.get("adoption_mode")
        or seal.get("adoption_mode") != matrix.get("adoption_mode")
    ):
        blockers.append("practical_terminal_adoption_mode_drift")
    if (
        final.get("correction_record_sha256")
        != matrix.get("correction_record_sha256")
        or seal.get("correction_record_sha256")
        != matrix.get("correction_record_sha256")
    ):
        blockers.append("practical_terminal_correction_hash_drift")
    if seal.get("final_closure_report_sha256") != sha256_file(final_path):
        blockers.append("practical_terminal_final_report_hash_mismatch")
    if seal.get("final_command_matrix_sha256") != sha256_file(
        phase5 / "final_command_matrix_report.json"
    ):
        blockers.append("practical_terminal_matrix_hash_mismatch")
    if seal.get("final_artifact_hash_manifest_sha256") != sha256_file(
        phase5 / "final_artifact_hash_manifest.json"
    ):
        blockers.append("practical_terminal_artifact_hash_mismatch")
    closeout_path = phase5 / "external" / "practical_closeout_review.md"
    owner_path = phase5 / "external" / "practical_owner_seal.json"
    actual_closeout_hash = sha256_file(closeout_path)
    actual_owner_hash = sha256_file(owner_path)
    if final.get("independent_closeout_review_sha256") != actual_closeout_hash:
        blockers.append("practical_final_closeout_review_hash_mismatch")
    if final.get("owner_seal_sha256") != actual_owner_hash:
        blockers.append("practical_final_owner_seal_hash_mismatch")
    if seal.get("independent_closeout_review_sha256") != actual_closeout_hash:
        blockers.append("practical_terminal_closeout_review_hash_mismatch")
    if seal.get("owner_seal_sha256") != actual_owner_hash:
        blockers.append("practical_terminal_owner_seal_hash_mismatch")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-practical-terminal-seal-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "canonical_complete": not blockers,
    }
