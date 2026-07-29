from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import public_text_quality_foundation_rebind as base


FoundationRebindError = base.FoundationRebindError

REBIND_ID = "correction-0003"
SCHEMA_VERSION = "public_text_quality_foundation_current_input_rebind_v3"
START_COMMIT = "00e23806c5dd6d220982604128ad50fadca3372c"
START_TREE = "f1acec6b1795a1a91e904a12893a9cb2b8adbd8d"
PREDECESSOR_REBIND_COMMIT = "e61a65322dabb0fd98f8e66f1a2b376cecc57eda"
PREDECESSOR_REBIND_SHA256 = (
    "c362c44b01cabc0937cbddc3843ca89e994ace0fbcacac8f75e61bfb604e8cc2"
)
CURRENT_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
CURRENT_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
ADOPTION_COMMIT = "e56c2e0c94aed8f31a61cb27cd6e37f0037451c8"
ADOPTION_TREE = "c5123b318267f0d3f47933422b292aec864b481d"
CORRECTION_RECEIPT_SHA256 = (
    "312c9b8744e1925b120129402b4ff6834d551960c284af8e91dbdbca091a56b0"
)
CURRENT_IDENTITY_REPORT_SHA256 = (
    "bdaf9a2cb3873bd33fe5517ecce410d3e243ff6d9765ac8ca37b4b4073d650d1"
)
TERMINAL_CORRECTION_SEAL_SHA256 = (
    "03dea1902f1d219b227b2b69cb88742f1005e3620cdcdee2b72ba811d1bd20fb"
)
NATURALIZATION_HANDOFF_SHA256 = (
    "bfa14583f524f99a75e88d4b6eaddfa146544cba9124cf09214a13a38c7d7750"
)

TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
PREDECESSOR_REBIND = (
    base.FOUNDATION_ROOT
    / "readiness_successors"
    / "correction-0002"
    / "public_text_quality_development_readiness_current_input_rebind.json"
)
SUCCESSOR_ROOT = base.FOUNDATION_ROOT / "readiness_successors" / REBIND_ID
SUCCESSOR_PATH = (
    SUCCESSOR_ROOT
    / "public_text_quality_development_readiness_current_input_rebind.json"
)
G3_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0012"
)
CORRECTION_RECEIPT = (
    G3_ATTEMPT_ROOT / "closeout" / "registry_correction_adoption_receipt.json"
)
CURRENT_IDENTITY_REPORT = (
    G3_ATTEMPT_ROOT / "closeout" / "current_correction_identity_report.json"
)
TERMINAL_CORRECTION_SEAL = (
    G3_ATTEMPT_ROOT / "closeout" / "terminal_correction_hash_seal.json"
)
NATURALIZATION_HANDOFF = (
    G3_ATTEMPT_ROOT / "handoff" / "naturalization_current_input_handoff.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
IMPLEMENTATION_FILES = (
    TOOLS_DIR / "public_text_quality_foundation_rebind.py",
    TOOLS_DIR / "public_text_quality_foundation_rebind_correction_0003.py",
    TOOLS_DIR / "run_public_text_quality_foundation_rebind_correction_0003.py",
    TOOLS_DIR / "validate_public_text_quality_foundation_rebind_correction_0003.py",
)


def _validate_start_readpoint(*, require_exact_head: bool) -> dict[str, Any]:
    actual_tree = base._git(
        "show", "-s", "--format=%T", START_COMMIT
    ).stdout.strip()
    if actual_tree != START_TREE:
        raise FoundationRebindError("correction-0003 start commit/tree mismatch")
    head = base._git("rev-parse", "HEAD").stdout.strip()
    if require_exact_head:
        if head != START_COMMIT:
            raise FoundationRebindError(
                "correction-0003 rebind build must start at the exact closeout commit"
            )
    else:
        base._require_ancestor(START_COMMIT, head)
    return {
        "commit": START_COMMIT,
        "tree": START_TREE,
        "exact_head_required_for_build": True,
        "start_commit_is_ancestor_of_validation_head": True,
    }


def _validate_predecessor_rebind() -> dict[str, Any]:
    base._require_ancestor(PREDECESSOR_REBIND_COMMIT, START_COMMIT)
    record = base._raw_tracked_record(
        PREDECESSOR_REBIND, PREDECESSOR_REBIND_SHA256
    )
    predecessor = base._load_json(PREDECESSOR_REBIND)
    immutable = predecessor.get("immutable_foundation", {})
    registry = predecessor.get("registry_correction_adoption", {})
    if (
        predecessor.get("schema_version")
        != "public_text_quality_foundation_current_input_rebind_v2"
        or predecessor.get("status") != "PASS"
        or predecessor.get("rebind_id") != "correction-0002"
        or predecessor.get("authority_effect") != "none"
        or predecessor.get("foundation_contract_semantics_changed") is not False
        or immutable.get("foundation_contract", {}).get("sha256")
        != base.FOUNDATION_CONTRACT_SHA256
        or registry.get("current_facts", {}).get("sha256")
        != "37db2595eff9b58f7b08e59221e950cb529453bd96733fb29171d458e46118f6"
        or registry.get("current_manifest", {}).get("sha256")
        != "a105e3790896b30bc25e95839ceb0ee4c88357fed98ec9fa4258790bf0733a1f"
    ):
        raise FoundationRebindError(
            "correction-0002 readiness predecessor is invalid"
        )
    return {
        **record,
        "rebind_id": "correction-0002",
        "rebind_commit": PREDECESSOR_REBIND_COMMIT,
        "append_only_successor_required": True,
        "predecessor_mutated": False,
    }


def _validate_registry_correction() -> dict[str, Any]:
    receipt_record = base._raw_tracked_record(
        CORRECTION_RECEIPT, CORRECTION_RECEIPT_SHA256
    )
    identity_record = base._raw_tracked_record(
        CURRENT_IDENTITY_REPORT, CURRENT_IDENTITY_REPORT_SHA256
    )
    terminal_record = base._raw_tracked_record(
        TERMINAL_CORRECTION_SEAL, TERMINAL_CORRECTION_SEAL_SHA256
    )
    handoff_record = base._raw_tracked_record(
        NATURALIZATION_HANDOFF, NATURALIZATION_HANDOFF_SHA256
    )
    facts_record = base._raw_tracked_record(CURRENT_FACTS, CURRENT_FACTS_SHA256)
    manifest_record = base._raw_tracked_record(
        CURRENT_MANIFEST, CURRENT_MANIFEST_SHA256
    )
    receipt = base._load_json(CORRECTION_RECEIPT)
    identity = base._load_json(CURRENT_IDENTITY_REPORT)
    terminal = base._load_json(TERMINAL_CORRECTION_SEAL)
    handoff = base._load_json(NATURALIZATION_HANDOFF)
    manifest = base._load_json(CURRENT_MANIFEST)
    actual_adoption_tree = base._git(
        "show", "-s", "--format=%T", ADOPTION_COMMIT
    ).stdout.strip()
    base._require_ancestor(ADOPTION_COMMIT, START_COMMIT)
    correction_binding = (
        manifest.get("source_promotion", {})
        .get("current_facts_correction_adoption_0003_binding", {})
    )
    food_authority = manifest.get("food_semantic_authority", {})
    invalid = (
        actual_adoption_tree != ADOPTION_TREE
        or receipt.get("schema_version")
        != "dvf-3-3-registry-correction-adoption-receipt-v3"
        or receipt.get("status") != "PASS"
        or receipt.get("attempt_id") != "attempt-0012"
        or receipt.get("successor_id") != REBIND_ID
        or receipt.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or receipt.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or receipt.get("previous_correction_receipt_sha256")
        != "475239fba798104371d2c9f4fb166c46ceab15bb462015493238a4aff4656f7f"
        or receipt.get("forbidden_scope_execution_count") != 0
        or identity.get("schema_version")
        != "dvf-3-3-current-correction-identity-report-v3"
        or identity.get("status") != "PASS"
        or identity.get("attempt_id") != "attempt-0012"
        or identity.get("adoption_commit") != ADOPTION_COMMIT
        or identity.get("adoption_tree") != ADOPTION_TREE
        or identity.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or identity.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or identity.get("single_current_identity") is not True
        or identity.get("partial_current_count") != 0
        or identity.get("dual_current_count") != 0
        or terminal.get("schema_version")
        != "dvf-3-3-terminal-correction-hash-seal-v3"
        or terminal.get("status") != "PASS"
        or terminal.get("attempt_id") != "attempt-0012"
        or terminal.get("successor_id") != REBIND_ID
        or terminal.get("adoption_commit") != ADOPTION_COMMIT
        or terminal.get("adoption_tree") != ADOPTION_TREE
        or terminal.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or terminal.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or terminal.get("registry_correction_adoption_receipt_sha256")
        != CORRECTION_RECEIPT_SHA256
        or terminal.get("current_identity_report_sha256")
        != CURRENT_IDENTITY_REPORT_SHA256
        or terminal.get("naturalization_current_input_handoff_sha256")
        != NATURALIZATION_HANDOFF_SHA256
        or terminal.get("forbidden_scope_execution_count") != 0
        or handoff.get("schema_version")
        != "dvf-3-3-naturalization-current-input-handoff-v3"
        or handoff.get("status") != "READY_FOR_FOUNDATION_REBIND"
        or handoff.get("attempt_id") != "attempt-0012"
        or handoff.get("required_next_stage")
        != "G4_Foundation_current_input_rebind"
        or handoff.get("registry_adoption_commit") != ADOPTION_COMMIT
        or handoff.get("registry_adoption_tree") != ADOPTION_TREE
        or handoff.get("registry_correction_adoption_receipt_sha256")
        != CORRECTION_RECEIPT_SHA256
        or handoff.get("current_facts_sha256") != CURRENT_FACTS_SHA256
        or handoff.get("current_manifest_sha256") != CURRENT_MANIFEST_SHA256
        or handoff.get("naturalization_attempt_started") is not False
        or handoff.get("official_publish_started") is not False
        or handoff.get("rtc_executed") is not False
        or manifest.get("facts", {}).get("sha256") != CURRENT_FACTS_SHA256
        or food_authority.get("registry_cutover_attempt_id") != "attempt-0012"
        or food_authority.get("registry_adoption_state")
        != "current_correction_0003"
        or correction_binding.get("append_only") is not True
        or correction_binding.get("successor_id") != REBIND_ID
        or correction_binding.get("successor_facts_sha256")
        != CURRENT_FACTS_SHA256
        or correction_binding.get("registry_cutover_attempt_id")
        != "attempt-0012"
        or correction_binding.get("previous_terminal_correction_seal_sha256")
        != "b54cca40e1dcbf4d279d878a6fba42e244311b33691eb27054d0881ff4682a52"
    )
    if invalid:
        raise FoundationRebindError(
            "correction-0003 G3/current-input evidence binding is invalid"
        )
    return {
        "successor_id": REBIND_ID,
        "registry_cutover_attempt_id": "attempt-0012",
        "adoption_commit": ADOPTION_COMMIT,
        "adoption_tree": ADOPTION_TREE,
        "adoption_tree_matches_commit": True,
        "correction_adoption_receipt": receipt_record,
        "current_identity_report": identity_record,
        "terminal_correction_seal": terminal_record,
        "naturalization_current_input_handoff": handoff_record,
        "current_facts": facts_record,
        "current_manifest": manifest_record,
        "current_identity_ambiguity_count": 0,
        "partial_or_dual_current_count": 0,
        "forbidden_scope_execution_count": 0,
    }


def _protected_paths() -> list[Path]:
    protected = set(base._protected_paths())
    protected.add(PREDECESSOR_REBIND)
    if G3_ATTEMPT_ROOT.is_dir():
        protected.update(
            path for path in G3_ATTEMPT_ROOT.rglob("*") if path.is_file()
        )
    protected.discard(SUCCESSOR_PATH)
    return sorted(protected, key=base._repo_relative)


def protected_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_paths():
        present = path.is_file()
        rows.append(
            {
                "path": base._repo_relative(path),
                "present": present,
                "raw_sha256": base._sha256_file(path) if present else None,
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": "public_text_quality_foundation_rebind_no_write_snapshot_v1",
        "surface_count": len(rows),
        "surface_hash": base._canonical_hash(rows),
        "surfaces": rows,
    }


def _implementation_hashes() -> list[dict[str, Any]]:
    rows = []
    for path in IMPLEMENTATION_FILES:
        if not path.is_file():
            raise FoundationRebindError(
                f"correction-0003 rebind implementation missing: {path}"
            )
        rows.append(
            {
                "path": base._repo_relative(path),
                "hash_algorithm": "sha256_utf8_lf_normalized_v1",
                "sha256": base._sha256_lf(path),
            }
        )
    return rows


def build_successor_projection(
    *,
    require_exact_start_head: bool,
    no_write_guard: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "rebind_id": REBIND_ID,
        "rebind_kind": "append_only_current_input_readiness_successor",
        "purpose": (
            "Bind immutable G4 Foundation readiness to correction-0003 current "
            "inputs without changing Foundation contract or evaluation semantics."
        ),
        "execution_start_readpoint": _validate_start_readpoint(
            require_exact_head=require_exact_start_head
        ),
        "immutable_foundation": base._validate_immutable_foundation(),
        "predecessor_readiness_rebind": _validate_predecessor_rebind(),
        "registry_correction_adoption": _validate_registry_correction(),
        "rebind_implementation_hashes": _implementation_hashes(),
        "protected_no_write_guard": no_write_guard,
        "naturalization_prerequisites": {
            "g4_development_readiness_rebound": True,
            "fresh_naturalization_attempt_must_start_at_phase": 0,
            "naturalization_attempt_created": False,
            "naturalization_phase2_through_phase8_executed": False,
            "current_input_handoff_consumed_as_identity_only": True,
        },
        "publish_boundary": {
            "official_publish_attempt_created": False,
            "public_text_candidate_evaluated": False,
            "live_publish_gate_mutated": False,
            "policy_ratified": False,
        },
        "runtime_boundary": {
            "rtc_executed": False,
            "runtime_mutated": False,
            "package_mutated": False,
            "runtime_package_publication_claim_effect": (
                "none_fail_closed_out_of_scope"
            ),
        },
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "foundation_contract_semantics_changed": False,
        "foundation_validator_semantics_changed": False,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "next_stage": "fresh_naturalization_attempt_phase0",
    }


def _validate_rebind_id(rebind_id: str) -> None:
    if rebind_id != REBIND_ID:
        raise FoundationRebindError(
            f"only the exact append-only rebind ID {REBIND_ID} is allowed"
        )


def build_rebind(rebind_id: str) -> dict[str, Any]:
    _validate_rebind_id(rebind_id)
    if SUCCESSOR_PATH.exists():
        raise FoundationRebindError(
            f"append-only readiness successor already exists: "
            f"{base._repo_relative(SUCCESSOR_PATH)}"
        )
    protected_before = protected_snapshot()
    protected_after_projection = protected_snapshot()
    guard = base._no_write_guard(protected_before, protected_after_projection)
    successor = build_successor_projection(
        require_exact_start_head=True,
        no_write_guard=guard,
    )
    SUCCESSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUCCESSOR_PATH.write_bytes(base._pretty_json_bytes(successor))
    protected_final = protected_snapshot()
    base._no_write_guard(protected_before, protected_final)
    return {
        "status": "PASS",
        "rebind_id": REBIND_ID,
        "readiness_successor_path": base._repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": base._sha256_file(SUCCESSOR_PATH),
        "foundation_contract_sha256": base.FOUNDATION_CONTRACT_SHA256,
        "protected_surface_mutation_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }


def _require_successor_vcs_state() -> dict[str, Any]:
    if not SUCCESSOR_PATH.is_file() or not base._is_tracked(SUCCESSOR_PATH):
        raise FoundationRebindError(
            "correction-0003 readiness successor must be present and tracked"
        )
    if base._is_ignored(SUCCESSOR_PATH):
        raise FoundationRebindError(
            "correction-0003 readiness successor must not be ignored"
        )
    relative = base._repo_relative(SUCCESSOR_PATH)
    staged_or_head_blob = base._git("rev-parse", f":{relative}", check=False)
    if staged_or_head_blob.returncode != 0:
        staged_or_head_blob = base._git(
            "rev-parse", f"HEAD:{relative}", check=False
        )
    if staged_or_head_blob.returncode != 0:
        raise FoundationRebindError("cannot resolve successor Git blob")
    blob_id = staged_or_head_blob.stdout.strip()
    working_raw_blob_id = base._git(
        "hash-object", "--no-filters", "--", relative
    ).stdout.strip()
    if blob_id != working_raw_blob_id:
        raise FoundationRebindError(
            "successor staged/working raw-byte identity mismatch"
        )
    attr = base._git("check-attr", "text", "--", relative).stdout.strip()
    if not attr.endswith(": text: unset"):
        raise FoundationRebindError(
            "successor must have an exact -text attribute"
        )
    return {
        "tracked": True,
        "ignored": False,
        "text_attribute": "unset",
        "git_blob_id": blob_id,
        "working_raw_blob_id": working_raw_blob_id,
        "git_blob_working_byte_identity": True,
    }


def validate_rebind(rebind_id: str) -> dict[str, Any]:
    _validate_rebind_id(rebind_id)
    if not SUCCESSOR_PATH.is_file():
        raise FoundationRebindError("correction-0003 readiness successor is missing")
    successor_bytes_before = SUCCESSOR_PATH.read_bytes()
    successor = base._load_json(SUCCESSOR_PATH)
    protected_before = protected_snapshot()
    protected_after_projection = protected_snapshot()
    guard = base._no_write_guard(protected_before, protected_after_projection)
    expected = build_successor_projection(
        require_exact_start_head=False,
        no_write_guard=guard,
    )
    if successor != expected:
        raise FoundationRebindError(
            "correction-0003 successor differs from exact projection"
        )
    vcs_state = _require_successor_vcs_state()
    if SUCCESSOR_PATH.read_bytes() != successor_bytes_before:
        raise FoundationRebindError("no-write validator changed successor bytes")
    protected_final = protected_snapshot()
    base._no_write_guard(protected_before, protected_final)
    return {
        "status": "PASS",
        "rebind_id": REBIND_ID,
        "readiness_successor_path": base._repo_relative(SUCCESSOR_PATH),
        "readiness_successor_raw_sha256": base._sha256_file(SUCCESSOR_PATH),
        "foundation_contract_sha256": base.FOUNDATION_CONTRACT_SHA256,
        "current_facts_sha256": CURRENT_FACTS_SHA256,
        "current_manifest_sha256": CURRENT_MANIFEST_SHA256,
        "correction_adoption_receipt_sha256": CORRECTION_RECEIPT_SHA256,
        "terminal_correction_seal_sha256": TERMINAL_CORRECTION_SEAL_SHA256,
        "naturalization_current_input_handoff_sha256": (
            NATURALIZATION_HANDOFF_SHA256
        ),
        "vcs_state": vcs_state,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
