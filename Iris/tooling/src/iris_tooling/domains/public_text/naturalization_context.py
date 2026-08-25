from __future__ import annotations

from pathlib import Path

from iris_tooling.build.naturalization_compiler_identity import compiler_source_paths
from iris_tooling.build.repository_context import require_repository_context


V2_ROOT = require_repository_context().description_v2_root
REPO_ROOT = require_repository_context().repository_root
TOOLING_PACKAGE_SOURCE_DIR = (
    REPO_ROOT / "Iris" / "tooling" / "src" / "iris_tooling"
)
PUBLIC_TEXT_DOMAIN_DIR = TOOLING_PACKAGE_SOURCE_DIR / "domains" / "public_text"
TOOLS_DIR = TOOLING_PACKAGE_SOURCE_DIR / "build"
ROUND_ID = "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
SYNC_CONTRACT_ID = "dvf3_3_korean_naturalization__publish_boundary_sync_v1"
EVALUATION_SUBJECT_KIND = "dvf_3_3_korean_naturalization_candidate"
DEFAULT_ATTEMPT_PARENT = V2_ROOT / "staging" / ROUND_ID
HISTORICAL_ATTEMPT_ID = "attempt-0014-remediation"
BLOCKED_ATTEMPT_ID = "attempt-0018-g3-reseal-a"
PRESERVED_PREDECESSOR_ATTEMPT_IDS = (
    "attempt-0020-g4-rebind-a",
    "attempt-0020-g4-rebind-b",
    "attempt-0021-g4-rebind-a",
    "attempt-0021-g4-rebind-b",
)
DATA_ROOT = V2_ROOT / "data" / "korean_prose_naturalization"
DURABLE_ROOT = REPO_ROOT / "Iris" / "_docs" / "round3" / ROUND_ID
FOUNDATION_ROOT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "foundation"
)
FOUNDATION_CONTRACT = FOUNDATION_ROOT / "public_text_quality_foundation_contract.json"
FOUNDATION_READINESS = (
    FOUNDATION_ROOT / "public_text_quality_development_readiness_report.json"
)
FOUNDATION_READINESS_CORRECTION_REBIND = (
    FOUNDATION_ROOT
    / "public_text_quality_development_readiness_correction_rebind.json"
)
FOUNDATION_READINESS_CURRENT_INPUT_REBIND = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "correction-0003"
    / "public_text_quality_development_readiness_current_input_rebind.json"
)
REGISTRY_ADOPTION_CONTRACT = (
    DURABLE_ROOT / "food_semantic_registry_adoption_contract.json"
)
INITIAL_REGISTRY_ADOPTION_RECEIPT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0009"
    / "closeout"
    / "registry_adoption_receipt.json"
)
REGISTRY_ADOPTION_RECEIPT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0012"
    / "closeout"
    / "registry_correction_adoption_receipt.json"
)
REGISTRY_CORRECTION_TERMINAL_SEAL = REGISTRY_ADOPTION_RECEIPT.with_name(
    "terminal_correction_hash_seal.json"
)
REGISTRY_NATURALIZATION_HANDOFF = (
    REGISTRY_ADOPTION_RECEIPT.parents[1]
    / "handoff"
    / "naturalization_current_input_handoff.json"
)
FOOD_SEMANTIC_SCHEMA = (
    REPO_ROOT / "Iris" / "_docs" / "authority" / "food_semantic"
    / "food_semantic_schema.json"
)
FOOD_SEMANTIC_LICENSE = (
    REPO_ROOT / "Iris" / "_docs" / "authority" / "food_semantic"
    / "proposition_licensing_contract.json"
)
FACTS_AUTHORITY_ROUTING_CORRECTION = (
    DURABLE_ROOT / "facts_authority_routing_correction_attempt_0014.json"
)
PARTICLE_CORRECTION_PROJECTION_REPORT = (
    DURABLE_ROOT
    / "compiler_particle_adjustment_correction_0001_projection_report.json"
)
INPUT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
FACTS_PATH = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
DECISIONS_PATH = V2_ROOT / "data" / "dvf_3_3_decisions.jsonl"
EXPECTED_CURRENT_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
EXPECTED_CURRENT_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256 = (
    "1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40"
)
EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256 = (
    "d1dea3b7b871fac90fc6a15ec18d95641a52d566cd62d14ffb0114c2bfb0098a"
)
EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256 = (
    "66f9eb59ea2cfec3fb5d647345ce5ab07ae17d0ba70b62c52b6bcaa7e3f32563"
)
EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256 = (
    "60f68c3e06fd148fce55072e1b7420165e10db16fc4e4b132b3fba7ae83e6edd"
)
EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256 = (
    "312c9b8744e1925b120129402b4ff6834d551960c284af8e91dbdbca091a56b0"
)
EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256 = (
    "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
)
EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256 = (
    "475239fba798104371d2c9f4fb166c46ceab15bb462015493238a4aff4656f7f"
)
EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256 = (
    "d4aac650a5d8135e6f14846d47b08f538f63b5ad07aaf714074d7a3f6555aed4"
)
EXPECTED_REGISTRY_CORRECTION_SUCCESSOR_MANIFEST_SHA256 = (
    "da7f6676b899b628c444edca56241ad274f2c64fa1a3448a934abff2f059cbb5"
)
EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256 = (
    "03dea1902f1d219b227b2b69cb88742f1005e3620cdcdee2b72ba811d1bd20fb"
)
EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256 = (
    "bfa14583f524f99a75e88d4b6eaddfa146544cba9124cf09214a13a38c7d7750"
)
EXPECTED_FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
EXPECTED_FOUNDATION_READINESS_SHA256 = (
    "34419a8093970c7ffc68d3d968ff90207f63c512971ae9ada87f90cff7f2d263"
)
EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256 = (
    "bf5916854b7aeb29f603ef42efb64e2b363fc5efb899dca1434b5e5c2744f315"
)
EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256 = (
    "912f28b7869ff92ff7fbd84cbdc31e1fbb22923beebbfcce2c9cc78b72eca9d2"
)
EXPECTED_COMPILER_FIX_COMMIT = "ca851a1e10bd37be71deded1fcc57b0d8462db48"
EXPECTED_PARTICLE_CORRECTION_COMMIT = (
    "55c8df22085b581590624d50fdda804c94930316"
)
EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256 = (
    "7cd0e72c879d5c24a171d5cc85fe00e19657388404fd2b55440769343cd4976f"
)
EXPECTED_START_COMMIT = EXPECTED_PARTICLE_CORRECTION_COMMIT
EXPECTED_START_TREE = "d063e618a3c9cf2fcf8a81c05f39b15c4932e3d8"
POLICY_PATH = DATA_ROOT / "korean_prose_policy.json"
CORPUS_MANIFEST_PATH = DATA_ROOT / "corpus_manifest.json"
PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md"
)
PUBLISH_PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"
)
EXECUTION_CONTRACT_PATH = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
ROADMAP_BINDING_PATH = DURABLE_ROOT / "roadmap_binding.json"
QUALITY_APPROVAL_PATH = DURABLE_ROOT / "quality_standard_approval.json"
GOLD_APPROVAL_PATH = DURABLE_ROOT / "gold_corpus_approval.json"
BODY_PLAN_APPLICABILITY_APPROVAL_PATH = (
    DURABLE_ROOT / "body_plan_applicability_approval.json"
)
HUMAN_REVIEW_DECISION_PATH = (
    DURABLE_ROOT / "attempt_0022_human_review_decision.json"
)
QUALITY_STANDARD_PATH = REPO_ROOT / "docs" / "dvf_3_3_korean_prose_quality_standard.md"
GOLD_CORPUS_PATH = DATA_ROOT / "gold_corpus.jsonl"
EXPECTED_ATTACHMENT_HASHES = {
    "roadmap": "c0c4838352910f8cacbcedfca8b74912d544d4f2ebc1d8d96f5cd34860eb3d1d",
    "plan_review": "dee1b7d3368936e88fffa2bc2dd2b5afdead1a55c8df749db387959c256d989f",
    "cycle2_review": "278daed986a32cc8964b0cfd9c786ae015f8e6fbcaac879a32ec2fea30098848",
}
PROTECTED_PATHS = (
    V2_ROOT / "output" / "dvf_3_3_rendered.json",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua",
    REPO_ROOT
    / "Iris"
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
    / "IrisLayer3DataChunks.lua",
    REPO_ROOT / "Iris" / "build" / "package" / "Iris.zip",
    REPO_ROOT / "Iris" / "build" / "package" / "Iris.package_manifest.sha256.json",
)
COMPILER_IMPLEMENTATION_PATHS = compiler_source_paths(REPO_ROOT)
SOURCE_ROLE_BY_FIELD = {
    "identity_hint": "identity",
    "primary_use": "use",
    "secondary_use": "use",
    "special_context": "context",
    "processing_hint": "context",
    "acquisition_hint": "acquisition",
    "limitation_hint": "limitation",
    "notes": "limitation",
}
TRANSFORMATION_IDS = (
    "reorder",
    "merge_equivalent",
    "suppress_duplicate",
    "pronoun_or_zero_anaphora",
    "particle_adjustment",
    "copula_adjustment",
    "paragraph_merge",
    "lexical_surface_naturalization",
)
FORBIDDEN_TRANSFORMATIONS = (
    "invent_fact",
    "strengthen_modality",
    "drop_qualifier",
    "cross_item_copy",
    "advice_conversion",
)
NOT_APPLICABLE_REASONS = (
    "source_role_not_required",
    "profile_exclusion",
    "body_plan_exclusion",
    "non_emittable_metadata",
)
RUNNER_MODES = (
    "phase0-preflight",
    "phase1-census",
    "phase2-source-inventory",
    "phase3-compiler-evidence",
    "phase4-candidate",
    "phase5-semantic",
    "phase5-adversarial",
    "phase6-raw-detectors",
    "phase7-human-review-sample",
    "phase8-publish-handoff",
)

__all__ = (
    "BLOCKED_ATTEMPT_ID", "BODY_PLAN_APPLICABILITY_APPROVAL_PATH",
    "COMPILER_IMPLEMENTATION_PATHS", "CORPUS_MANIFEST_PATH", "DATA_ROOT",
    "DECISIONS_PATH", "DEFAULT_ATTEMPT_PARENT", "DURABLE_ROOT",
    "EVALUATION_SUBJECT_KIND", "EXECUTION_CONTRACT_PATH",
    "EXPECTED_ATTACHMENT_HASHES", "EXPECTED_COMPILER_FIX_COMMIT",
    "EXPECTED_CURRENT_FACTS_SHA256", "EXPECTED_CURRENT_MANIFEST_SHA256",
    "EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256", "EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256",
    "EXPECTED_FOUNDATION_CONTRACT_SHA256", "EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256",
    "EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256",
    "EXPECTED_FOUNDATION_READINESS_SHA256", "EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256",
    "EXPECTED_PARTICLE_CORRECTION_COMMIT", "EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256",
    "EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256",
    "EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256", "EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256",
    "EXPECTED_REGISTRY_CORRECTION_SUCCESSOR_MANIFEST_SHA256",
    "EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256",
    "EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256",
    "EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256", "EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256",
    "EXPECTED_START_COMMIT", "EXPECTED_START_TREE", "FACTS_AUTHORITY_ROUTING_CORRECTION",
    "FACTS_PATH", "FOOD_SEMANTIC_LICENSE", "FOOD_SEMANTIC_SCHEMA",
    "FORBIDDEN_TRANSFORMATIONS", "FOUNDATION_CONTRACT", "FOUNDATION_READINESS",
    "FOUNDATION_READINESS_CORRECTION_REBIND", "FOUNDATION_READINESS_CURRENT_INPUT_REBIND",
    "FOUNDATION_ROOT", "GOLD_APPROVAL_PATH", "GOLD_CORPUS_PATH",
    "HISTORICAL_ATTEMPT_ID", "HUMAN_REVIEW_DECISION_PATH",
    "INITIAL_REGISTRY_ADOPTION_RECEIPT", "INPUT_MANIFEST", "NOT_APPLICABLE_REASONS",
    "PARTICLE_CORRECTION_PROJECTION_REPORT", "PLAN_PATH", "POLICY_PATH",
    "PRESERVED_PREDECESSOR_ATTEMPT_IDS", "PROTECTED_PATHS",
    "PUBLIC_TEXT_DOMAIN_DIR", "PUBLISH_PLAN_PATH", "QUALITY_APPROVAL_PATH",
    "QUALITY_STANDARD_PATH", "REGISTRY_ADOPTION_CONTRACT", "REGISTRY_ADOPTION_RECEIPT",
    "REGISTRY_CORRECTION_TERMINAL_SEAL", "REGISTRY_NATURALIZATION_HANDOFF", "REPO_ROOT",
    "ROADMAP_BINDING_PATH", "ROUND_ID", "RUNNER_MODES", "SOURCE_ROLE_BY_FIELD",
    "SYNC_CONTRACT_ID", "TOOLING_PACKAGE_SOURCE_DIR",
    "TOOLS_DIR", "TRANSFORMATION_IDS", "V2_ROOT",
)
