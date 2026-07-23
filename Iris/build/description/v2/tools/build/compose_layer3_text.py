from __future__ import annotations

import argparse
from collections import Counter
import errno
import hashlib
import json
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import sys
import time
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.compose_layer3_io import (
        entries_sha256,
        file_sha256,
        load_json,
        load_jsonl,
        load_optional_jsonl_map,
        write_jsonl,
    )
    from tools.build.compose_layer3_body_profile import (
        DEFAULT_RESOLVER_AUTHORITY_MODE,
        DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
        UNADOPTED_RUNTIME_STATE,
        is_body_plan_profiles_v2,
        load_profile_resolution_rules,
    )
    from tools.build.compose_layer3_render import compose_all_legacy, compose_all_v2
else:
    from .compose_layer3_io import (
        entries_sha256,
        file_sha256,
        load_json,
        load_jsonl,
        load_optional_jsonl_map,
        write_jsonl,
    )
    from .compose_layer3_body_profile import (
        DEFAULT_RESOLVER_AUTHORITY_MODE,
        DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
        UNADOPTED_RUNTIME_STATE,
        is_body_plan_profiles_v2,
        load_profile_resolution_rules,
    )
    from .compose_layer3_render import compose_all_legacy, compose_all_v2
from tools.common.paths import V2_ROOT as ROOT


DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
STAGING_DIR = ROOT / "staging" / "body_role" / "phase2"
EDPAS_DIAGNOSTIC_DIR = ROOT / "staging" / "entrypoint_drift_patch_authority_seal_round" / "diagnostic"
STYLE_LOG_PATH = OUTPUT_DIR / "style_normalization_changes.jsonl"
OVERLAY_PATH = STAGING_DIR / "layer3_role_check_overlay.jsonl"
BODY_SOURCE_OVERLAY_PATH = ROOT / "staging" / "compose_contract_migration" / "layer3_body_source_overlay.jsonl"
CURRENT_OVERLAY_SUPPORT_PATH = DATA_DIR / "dvf_3_3_overlay_support.jsonl"
IDENTITY_RULES_PATH = DATA_DIR / "compose_profile_identity_hint_rules.json"
PRECEDENCE_RULES_PATH = DATA_DIR / "compose_profile_conflict_precedence_rules.json"
BODY_PLAN_PROFILES_PATH = DATA_DIR / "compose_profiles_v2.json"
VNEXT_EXECUTION_DIR = ROOT / "staging" / "dvf_3_3_vnext_execution"
TEST_TMP_ROOT = ROOT / "tests"
BUILD_TMP_ROOT = ROOT / ".tmp_tests"

DEFAULT_MODE = "default"
DIAGNOSTIC_RESOLVER_MODE = "diagnostic_resolver"
CURRENT_COMPOSE_CONTEXT = "current"
STAGING_COMPOSE_CONTEXT = "staging"
HISTORICAL_COMPOSE_CONTEXT = "historical"
DIAGNOSTIC_COMPOSE_CONTEXT = "diagnostic"
COMPOSE_CONTEXTS = (
    CURRENT_COMPOSE_CONTEXT,
    STAGING_COMPOSE_CONTEXT,
    HISTORICAL_COMPOSE_CONTEXT,
    DIAGNOSTIC_COMPOSE_CONTEXT,
)
DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE = "DEFAULT_CURRENT_AUTHORITY_INPUT_REJECTED_NON_DATA_SOURCE"
COMPOSE_CONTEXT_REQUIRED_ERROR_CODE = "COMPOSE_CONTEXT_REQUIRED"
COMPOSE_CONTEXT_OUTPUT_CLASS_ERROR_CODE = "COMPOSE_CONTEXT_OUTPUT_CLASS_REJECTED"
COMPOSE_PROFILE_CLASS_ERROR_CODE = "COMPOSE_PROFILE_CLASS_REJECTED"
COMPOSE_CURRENT_UNLISTED_OUTPUT_ERROR_CODE = "COMPOSE_CURRENT_UNLISTED_OUTPUT_REJECTED"
COMPOSE_INVALID_CONTEXT_ERROR_CODE = "COMPOSE_CONTEXT_INVALID"
REGISTRY_REAL_CURRENT_WRITE_DISABLED_ERROR_CODE = "REGISTRY_REAL_CURRENT_PROTECTED_WRITE_DISABLED"
REGISTRY_FIXTURE_RECEIPT_INVALID_ERROR_CODE = "REGISTRY_FIXTURE_RECEIPT_INVALID"
REGISTRY_FIXTURE_RECEIPT_REPLAY_ERROR_CODE = "REGISTRY_FIXTURE_RECEIPT_REPLAY"
REGISTRY_FIXTURE_RECEIPT_SCHEMA = "dvf-3-3-registry-authority-fixture-current-write-receipt-v1"
REGISTRY_FIXTURE_DECISION_SCHEMA = (
    "dvf-3-3-registry-authority-canonical-closure-wp5-fixture-decision-v1"
)
CURRENT_AUTHORITY_INPUT_KEYS = (
    "facts_path",
    "decisions_path",
    "overlay_path",
    "profiles_path",
    "identity_rules_path",
    "precedence_rules_path",
)
CLOSED_CURRENT_PROTECTED_PATHS = {
    "rendered_output": OUTPUT_DIR / "dvf_3_3_rendered.json",
    "style_log": STYLE_LOG_PATH,
    "requeue_candidates": OUTPUT_DIR / "compose_requeue_candidates.jsonl",
}
REAL_CLOSED_CURRENT_PROTECTED_PATHS = frozenset(
    path.resolve() for path in CLOSED_CURRENT_PROTECTED_PATHS.values()
)
CURRENT_PROTECTED_BASENAMES = frozenset(
    path.name for path in CLOSED_CURRENT_PROTECTED_PATHS.values()
)
ENTRYPOINT_MODES = (
    DEFAULT_MODE,
    DIAGNOSTIC_RESOLVER_MODE,
)


def write_json_retry(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    last_error: OSError | None = None
    for attempt in range(8):
        target = path if attempt == 0 else path.with_name(f".{path.name}.{os.getpid()}.{attempt}.tmp")
        try:
            target.write_text(serialized, encoding="utf-8")
            if target != path:
                target.replace(path)
            return
        except OSError as exc:
            last_error = exc
            if target != path:
                try:
                    target.unlink(missing_ok=True)
                except OSError:
                    pass
            if exc.errno != errno.EINVAL or attempt == 7:
                raise
            time.sleep(0.05 * (attempt + 1))
    if last_error is not None:
        raise last_error


def write_lines_retry(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(lines)
    last_error: OSError | None = None
    for attempt in range(8):
        target = path if attempt == 0 else path.with_name(f".{path.name}.{os.getpid()}.{attempt}.tmp")
        try:
            target.write_text(text, encoding="utf-8")
            if target != path:
                target.replace(path)
            return
        except OSError as exc:
            last_error = exc
            if target != path:
                try:
                    target.unlink(missing_ok=True)
                except OSError:
                    pass
            if exc.errno != errno.EINVAL or attempt == 7:
                raise
            time.sleep(0.05 * (attempt + 1))
    if last_error is not None:
        raise last_error


def text_mode_write_bytes(text: str) -> bytes:
    if os.linesep != "\n":
        text = text.replace("\n", os.linesep)
    return text.encode("utf-8")


class ComposeEntrypointGuardError(ValueError):
    def __init__(
        self,
        reason: str,
        *,
        compose_context: str | None,
        output_path_class: str | None = None,
        profile_class: str | None = None,
        write_role: str | None = None,
        path: Path | None = None,
    ) -> None:
        details = [
            reason,
            f"compose_context={compose_context or 'missing'}",
        ]
        if output_path_class is not None:
            details.append(f"output_path_class={output_path_class}")
        if profile_class is not None:
            details.append(f"profile_class={profile_class}")
        if write_role is not None:
            details.append(f"write_role={write_role}")
        if path is not None:
            details.append(f"path={path}")
        super().__init__(": ".join([details[0], ", ".join(details[1:])]))
        self.reason = reason
        self.compose_context = compose_context
        self.output_path_class = output_path_class
        self.profile_class = profile_class
        self.write_role = write_role
        self.path = path


def is_under_path(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def resolved(path: Path) -> Path:
    return path.resolve()


def has_test_tmp_segment(path: Path) -> bool:
    path = resolved(path)
    if path == BUILD_TMP_ROOT.resolve() or BUILD_TMP_ROOT.resolve() in path.parents:
        return True
    try:
        relative_parts = path.relative_to(TEST_TMP_ROOT.resolve()).parts
    except ValueError:
        return False
    return any(part.startswith("_tmp") for part in relative_parts)


def is_known_current_protected_path(path: Path) -> bool:
    target = resolved(path)
    return any(target == resolved(protected) for protected in CLOSED_CURRENT_PROTECTED_PATHS.values())


def is_real_current_protected_path(path: Path) -> bool:
    return resolved(path) in REAL_CLOSED_CURRENT_PROTECTED_PATHS


def sha256_path(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalized_body_plan_authority(profiles: dict[str, Any]) -> dict[str, Any]:
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


def read_registry_fixture_receipt(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ComposeEntrypointGuardError(
            f"{REGISTRY_FIXTURE_RECEIPT_INVALID_ERROR_CODE}: unreadable receipt",
            compose_context=CURRENT_COMPOSE_CONTEXT,
            path=path,
        ) from exc
    if not isinstance(payload, dict):
        raise ComposeEntrypointGuardError(
            f"{REGISTRY_FIXTURE_RECEIPT_INVALID_ERROR_CODE}: receipt must be an object",
            compose_context=CURRENT_COMPOSE_CONTEXT,
            path=path,
        )
    return payload


def receipt_fixture_root(payload: dict[str, Any]) -> Path:
    value = payload.get("fixture_transaction_root")
    if not isinstance(value, str):
        raise ValueError("fixture_transaction_root missing")
    root = Path(value).resolve()
    normalized = root.as_posix().lower()
    required_parts = (
        "/staging/dvf_3_3_registry_authority_canonical_closure/attempts/",
        "/phase4/wp5",
    )
    if not all(part in normalized for part in required_parts):
        raise ValueError("fixture transaction root is outside phase4/wp5 attempt evidence")
    return root


def receipt_output_paths(payload: dict[str, Any]) -> dict[str, Path]:
    raw = payload.get("allowed_output_paths")
    if not isinstance(raw, dict) or set(raw) != {
        "output_path",
        "style_log_path",
        "requeue_candidates_path",
    }:
        raise ValueError("allowed_output_paths must name the exact three compose targets")
    if not all(isinstance(value, str) for value in raw.values()):
        raise ValueError("allowed_output_paths values must be strings")
    return {key: Path(value).resolve() for key, value in raw.items()}


def registry_fixture_receipt_binding(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: payload.get(key)
        for key in (
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
    }


def validate_registry_fixture_receipt(
    receipt_path: Path,
    *,
    paths: dict[str, Path | None],
    profiles: dict[str, Any],
    rendered: dict[str, Any] | None = None,
    computed_postwrite_hashes: dict[str, str] | None = None,
    consume: bool = False,
) -> dict[str, Any]:
    payload = read_registry_fixture_receipt(receipt_path)
    required_fields = {
        "schema_version",
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
        "fixture_decision_path",
        "fixture_decision_sha256",
        "issued_at",
        "expires_at",
        "nonce",
        "receipt_consumption_state_path",
    }
    forbidden_fields = {
        "owner_authorization",
        "owner_approved",
        "production",
        "live",
        "live_write_allowed",
    }
    errors: list[str] = []
    if set(payload) != required_fields:
        errors.append("receipt_field_set_mismatch")
    if forbidden_fields.intersection(payload):
        errors.append("receipt_forbidden_authority_field_present")
    if payload.get("schema_version") != REGISTRY_FIXTURE_RECEIPT_SCHEMA:
        errors.append("receipt_schema_mismatch")
    if payload.get("round_id") != "dvf_3_3_registry_authority_canonical_closure":
        errors.append("receipt_round_mismatch")
    if payload.get("fixture_only") is not True:
        errors.append("receipt_not_fixture_only")
    try:
        root = receipt_fixture_root(payload)
        allowed_paths = receipt_output_paths(payload)
    except (TypeError, ValueError) as exc:
        root = Path()
        allowed_paths = {}
        errors.append(str(exc))
    attempt_id = payload.get("attempt_id")
    if (
        not isinstance(attempt_id, str)
        or not re.fullmatch(r"attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]{0,47}", attempt_id)
        or root.parent.parent.name != attempt_id
    ):
        errors.append("receipt_attempt_binding_mismatch")
    actual_paths = {
        key: value.resolve()
        for key, value in paths.items()
        if key in {"output_path", "style_log_path", "requeue_candidates_path"}
        and value is not None
    }
    if allowed_paths != actual_paths:
        errors.append("receipt_target_set_mismatch")
    if any(
        not is_under_path(path, root) or is_real_current_protected_path(path)
        for path in allowed_paths.values()
    ):
        errors.append("receipt_target_outside_fixture_or_real_protected")
    if not is_under_path(receipt_path, root / "fixture_receipts"):
        errors.append("receipt_path_outside_fixture_receipt_root")
    binding_rows = payload.get("input_bindings")
    supplied_bindings: dict[str, dict[str, Any]] = {}
    if isinstance(binding_rows, list):
        for row in binding_rows:
            if not isinstance(row, dict):
                continue
            key = row.get("key")
            path_value = row.get("path")
            if isinstance(key, str) and isinstance(path_value, str):
                supplied_bindings[key] = {
                    "path": str(Path(path_value).resolve()),
                    "sha256": row.get("sha256"),
                }
    observed_bindings = {
        key: {"path": str(value.resolve()), "sha256": sha256_path(value)}
        for key, value in paths.items()
        if key in CURRENT_AUTHORITY_INPUT_KEYS and value is not None
    }
    if supplied_bindings != observed_bindings or len(observed_bindings) != 6:
        errors.append("receipt_input_binding_mismatch")
    if payload.get("normalized_body_plan_authority_sha256") != canonical_sha256(
        normalized_body_plan_authority(profiles)
    ):
        errors.append("receipt_body_plan_authority_mismatch")
    now = datetime.now(timezone.utc)
    try:
        issued = datetime.fromisoformat(str(payload.get("issued_at")).replace("Z", "+00:00"))
        expires = datetime.fromisoformat(str(payload.get("expires_at")).replace("Z", "+00:00"))
        if issued > now or expires <= now or expires <= issued:
            errors.append("receipt_time_window_invalid")
    except ValueError:
        errors.append("receipt_time_invalid")
    nonce = payload.get("nonce")
    binding_sha256 = canonical_sha256(registry_fixture_receipt_binding(payload))
    if not isinstance(nonce, str) or not re.fullmatch(r"[0-9a-f]{32}", nonce):
        errors.append("receipt_nonce_schema_mismatch")
        nonce = "invalid"
    elif nonce != binding_sha256[:32]:
        errors.append("receipt_nonce_binding_mismatch")
    expected_receipt_path = (root / "fixture_receipts" / f"{nonce}.json").resolve()
    if receipt_path.resolve() != expected_receipt_path:
        errors.append("receipt_path_not_canonical_for_nonce")
    decision_value = payload.get("fixture_decision_path")
    decision_path = Path(decision_value).resolve() if isinstance(decision_value, str) else Path()
    expected_decision_path = (root / "fixture_receipt_decision.json").resolve()
    if decision_path != expected_decision_path:
        errors.append("receipt_decision_path_mismatch")
    decision: dict[str, Any] = {}
    if decision_path.is_file():
        try:
            loaded_decision = json.loads(decision_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded_decision, dict):
                decision = loaded_decision
            else:
                errors.append("receipt_decision_not_object")
        except (OSError, UnicodeError, json.JSONDecodeError):
            errors.append("receipt_decision_unreadable")
    else:
        errors.append("receipt_decision_missing")
    if payload.get("fixture_decision_sha256") != sha256_path(decision_path):
        errors.append("receipt_decision_hash_mismatch")
    expected_decision_fields = {
        "schema_version",
        "status",
        "fixture_only",
        "production_receipt_issuance_allowed",
        "real_current_write_allowed",
        "attempt_id",
        "nonce",
        "receipt_binding_sha256",
        "allowed_output_paths",
        "input_bindings_sha256",
        "candidate_raw_sha256",
        "candidate_canonical_entries_sha256",
        "issued_at",
        "expires_at",
        "issued_by",
    }
    if set(decision) != expected_decision_fields:
        errors.append("receipt_decision_field_set_mismatch")
    if any(
        (
            decision.get("schema_version") != REGISTRY_FIXTURE_DECISION_SCHEMA,
            decision.get("status") != "PASS",
            decision.get("fixture_only") is not True,
            decision.get("production_receipt_issuance_allowed") is not False,
            decision.get("real_current_write_allowed") is not False,
            decision.get("attempt_id") != attempt_id,
            decision.get("nonce") != nonce,
            decision.get("receipt_binding_sha256") != binding_sha256,
            decision.get("allowed_output_paths") != payload.get("allowed_output_paths"),
            decision.get("input_bindings_sha256")
            != canonical_sha256(payload.get("input_bindings")),
            decision.get("candidate_raw_sha256") != payload.get("candidate_raw_sha256"),
            decision.get("candidate_canonical_entries_sha256")
            != payload.get("candidate_canonical_entries_sha256"),
            decision.get("issued_at") != payload.get("issued_at"),
            decision.get("expires_at") != payload.get("expires_at"),
            decision.get("issued_by") != "wp5_fixture_receipt_issuer",
        )
    ):
        errors.append("receipt_decision_binding_mismatch")
    preimages = payload.get("expected_target_preimages")
    observed_preimages = {key: sha256_path(path) for key, path in allowed_paths.items()}
    if not isinstance(preimages, dict) or preimages != observed_preimages:
        errors.append("receipt_target_preimage_mismatch")
    state_value = payload.get("receipt_consumption_state_path")
    state_path = Path(state_value).resolve() if isinstance(state_value, str) else Path()
    expected_state_path = (root / "receipt_consumption" / f"{nonce}.json").resolve()
    if state_path != expected_state_path:
        errors.append("receipt_consumption_path_not_canonical_for_nonce")
    if state_path.exists():
        errors.append("receipt_nonce_already_consumed")
    if rendered is not None:
        if payload.get("candidate_canonical_entries_sha256") != entries_sha256(
            rendered.get("entries", {})
        ):
            errors.append("receipt_candidate_entries_mismatch")
        if not isinstance(computed_postwrite_hashes, dict):
            errors.append("receipt_expected_postwrite_hashes_missing")
        elif payload.get("expected_postwrite_hashes") != computed_postwrite_hashes:
            errors.append("receipt_expected_postwrite_hashes_mismatch")
        elif payload.get("candidate_raw_sha256") != computed_postwrite_hashes.get(
            "output_path"
        ):
            errors.append("receipt_candidate_raw_mismatch")
    if errors:
        reason = (
            REGISTRY_FIXTURE_RECEIPT_REPLAY_ERROR_CODE
            if "receipt_nonce_already_consumed" in errors
            else REGISTRY_FIXTURE_RECEIPT_INVALID_ERROR_CODE
        )
        raise ComposeEntrypointGuardError(
            f"{reason}: {','.join(sorted(set(errors)))}",
            compose_context=CURRENT_COMPOSE_CONTEXT,
            path=receipt_path,
        )
    if consume:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with state_path.open("x", encoding="utf-8") as handle:
            json.dump(
                {
                    "schema_version": "dvf-3-3-registry-authority-fixture-receipt-consumption-v1",
                    "nonce": payload.get("nonce"),
                    "receipt_sha256": sha256_path(receipt_path),
                    "consumed_at": datetime.now(timezone.utc).isoformat(),
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )
    return payload


def is_current_equivalent_name(path: Path) -> bool:
    name = path.name
    return (
        name in CURRENT_PROTECTED_BASENAMES
        or name.startswith("dvf_3_3_rendered")
        or name.startswith("style_normalization_changes")
    )


def classify_compose_write_path(path: Path) -> str:
    if has_test_tmp_segment(path) and is_current_equivalent_name(path):
        return "current-equivalent-fixture"
    if is_under_path(path, OUTPUT_DIR):
        return "current-equivalent"
    if is_under_path(path, EDPAS_DIAGNOSTIC_DIR):
        return "diagnostic"
    if is_under_path(path, ROOT / "staging"):
        return "staging"
    if has_test_tmp_segment(path):
        return "test-fixture"
    return "historical"


def contains_legacy_sentence_plan(profiles: dict[str, Any]) -> bool:
    return any(
        isinstance(profile, dict) and "sentence_plan" in profile
        for profile in profiles.values()
    )


def classify_compose_profile(profiles: dict[str, Any]) -> str:
    has_v2_marker = profiles.get("schema_version") == "compose-profiles-v2"
    has_v2_profiles = isinstance(profiles.get("profiles"), dict)
    has_legacy_sentence_plan = contains_legacy_sentence_plan(profiles)
    if has_v2_marker and has_legacy_sentence_plan:
        return "ambiguous"
    if has_v2_marker or has_v2_profiles:
        if not is_body_plan_profiles_v2(profiles):
            return "partial_v2"
        if not isinstance(profiles.get("section_names"), list):
            return "partial_v2"
        if not isinstance(profiles.get("render_rules"), dict):
            return "partial_v2"
        for profile in profiles["profiles"].values():
            if not isinstance(profile, dict):
                return "partial_v2"
            for key in ("required_sections", "section_order", "adequate_minimum_any_of"):
                if key not in profile:
                    return "partial_v2"
        return "v2_current"
    if has_legacy_sentence_plan:
        return "legacy"
    return "unknown"


def require_compose_context(compose_context: str | None) -> None:
    if compose_context is None:
        raise ComposeEntrypointGuardError(
            COMPOSE_CONTEXT_REQUIRED_ERROR_CODE,
            compose_context=compose_context,
        )
    if compose_context not in COMPOSE_CONTEXTS:
        raise ComposeEntrypointGuardError(
            COMPOSE_INVALID_CONTEXT_ERROR_CODE,
            compose_context=compose_context,
        )


def enforce_current_output_known_set(
    *,
    compose_context: str,
    path_records: list[dict[str, Any]],
    profile_class: str,
) -> None:
    for record in path_records:
        if record["path_class"] != "current-equivalent":
            continue
        if not is_known_current_protected_path(record["path"]):
            raise ComposeEntrypointGuardError(
                COMPOSE_CURRENT_UNLISTED_OUTPUT_ERROR_CODE,
                compose_context=compose_context,
                output_path_class=record["path_class"],
                profile_class=profile_class,
                write_role=record["role"],
                path=record["path"],
            )


def enforce_allowed_output_classes(
    *,
    compose_context: str,
    path_records: list[dict[str, Any]],
    profile_class: str,
) -> None:
    allowed_by_context = {
        CURRENT_COMPOSE_CONTEXT: {"current-equivalent", "current-equivalent-fixture"},
        STAGING_COMPOSE_CONTEXT: {"staging", "test-fixture", "current-equivalent-fixture"},
        HISTORICAL_COMPOSE_CONTEXT: {"historical", "test-fixture", "current-equivalent-fixture"},
        DIAGNOSTIC_COMPOSE_CONTEXT: {"diagnostic", "test-fixture", "current-equivalent-fixture"},
    }
    allowed = allowed_by_context[compose_context]
    for record in path_records:
        if record["path_class"] not in allowed:
            raise ComposeEntrypointGuardError(
                COMPOSE_CONTEXT_OUTPUT_CLASS_ERROR_CODE,
                compose_context=compose_context,
                output_path_class=record["path_class"],
                profile_class=profile_class,
                write_role=record["role"],
                path=record["path"],
            )


def enforce_compose_write_contract(
    *,
    compose_context: str | None,
    paths: dict[str, Path | None],
    profiles: dict[str, Any],
    registry_current_write_authorization_receipt: Path | None = None,
) -> None:
    require_compose_context(compose_context)
    assert compose_context is not None
    profile_class = classify_compose_profile(profiles)
    raw_targets = [
        value
        for key, value in paths.items()
        if key in {"output_path", "style_log_path", "requeue_candidates_path"}
        and value is not None
    ]
    fixture_receipt_targets: set[Path] = set()
    if registry_current_write_authorization_receipt is not None:
        receipt = validate_registry_fixture_receipt(
            registry_current_write_authorization_receipt,
            paths=paths,
            profiles=profiles,
        )
        fixture_receipt_targets = set(receipt_output_paths(receipt).values())
    path_records = [
        {
            "role": key,
            "path": value,
            "path_class": (
                "current-equivalent-fixture"
                if value.resolve() in fixture_receipt_targets
                else classify_compose_write_path(value)
            ),
        }
        for key, value in (
            ("output_path", paths["output_path"]),
            ("style_log_path", paths["style_log_path"]),
            ("requeue_candidates_path", paths.get("requeue_candidates_path")),
        )
        if value is not None
    ]
    enforce_allowed_output_classes(
        compose_context=compose_context,
        path_records=path_records,
        profile_class=profile_class,
    )
    if compose_context == CURRENT_COMPOSE_CONTEXT:
        enforce_current_output_known_set(
            compose_context=compose_context,
            path_records=path_records,
            profile_class=profile_class,
        )
        if profile_class != "v2_current":
            raise ComposeEntrypointGuardError(
                COMPOSE_PROFILE_CLASS_ERROR_CODE,
                compose_context=compose_context,
                output_path_class="current-equivalent",
                profile_class=profile_class,
            )
        enforce_current_authority_input_contract(DEFAULT_MODE, paths)
    for target in raw_targets:
        if is_real_current_protected_path(target):
            raise ComposeEntrypointGuardError(
                REGISTRY_REAL_CURRENT_WRITE_DISABLED_ERROR_CODE,
                compose_context=compose_context,
                output_path_class="real-current-protected",
                profile_class=profile_class,
                path=target,
            )


def enforce_resolver_authority_output_contract(
    *,
    resolver_authority_mode: str,
    output_path: Path,
    style_log_path: Path,
    requeue_candidates_path: Path | None,
) -> None:
    if resolver_authority_mode != DIAGNOSTIC_RESOLVER_AUTHORITY_MODE:
        return
    for key, value in (
        ("output_path", output_path),
        ("style_log_path", style_log_path),
        ("requeue_candidates_path", requeue_candidates_path),
    ):
        if value is not None and is_under_path(value, OUTPUT_DIR):
            raise ValueError(f"diagnostic resolver {key} must not write under canonical {OUTPUT_DIR}")


def enforce_current_authority_input_contract(mode: str, paths: dict[str, Path | None]) -> None:
    if mode != DEFAULT_MODE:
        return
    if is_vnext_staging_default_execution(paths):
        return
    for key in CURRENT_AUTHORITY_INPUT_KEYS:
        value = paths.get(key)
        if value is None:
            raise ValueError(f"{DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE}: default mode {key} is required")
        if not is_under_path(value, DATA_DIR):
            raise ValueError(
                f"{DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE}: "
                f"default mode {key} must read current authority input from {DATA_DIR}, got {value}"
            )


def is_vnext_staging_default_execution(paths: dict[str, Path | None]) -> bool:
    facts_path = paths.get("facts_path")
    decisions_path = paths.get("decisions_path")
    output_path = paths.get("output_path")
    style_log_path = paths.get("style_log_path")
    profiles_path = paths.get("profiles_path")
    identity_rules_path = paths.get("identity_rules_path")
    precedence_rules_path = paths.get("precedence_rules_path")
    required_paths = [facts_path, decisions_path, output_path, style_log_path]
    if any(path is None for path in required_paths):
        return False
    assert facts_path is not None
    assert decisions_path is not None
    assert output_path is not None
    assert style_log_path is not None
    return (
        is_under_path(facts_path, VNEXT_EXECUTION_DIR / "phase2")
        and is_under_path(decisions_path, VNEXT_EXECUTION_DIR / "phase2")
        and is_under_path(output_path, VNEXT_EXECUTION_DIR / "phase4")
        and is_under_path(style_log_path, VNEXT_EXECUTION_DIR / "phase4")
        and profiles_path is not None
        and identity_rules_path is not None
        and precedence_rules_path is not None
        and profiles_path.resolve() == BODY_PLAN_PROFILES_PATH.resolve()
        and identity_rules_path.resolve() == IDENTITY_RULES_PATH.resolve()
        and precedence_rules_path.resolve() == PRECEDENCE_RULES_PATH.resolve()
    )


def build_rendered(
    facts_path: Path,
    decisions_path: Path,
    profiles_path: Path,
    output_path: Path,
    overlay_path: Path | None = OVERLAY_PATH,
    style_log_path: Path = STYLE_LOG_PATH,
    requeue_candidates_path: Path | None = None,
    identity_rules_path: Path = IDENTITY_RULES_PATH,
    precedence_rules_path: Path = PRECEDENCE_RULES_PATH,
    resolver_authority_mode: str = DEFAULT_RESOLVER_AUTHORITY_MODE,
    compose_context: str | None = None,
    registry_current_write_authorization_receipt: Path | None = None,
) -> dict[str, Any]:
    require_compose_context(compose_context)
    enforce_resolver_authority_output_contract(
        resolver_authority_mode=resolver_authority_mode,
        output_path=output_path,
        style_log_path=style_log_path,
        requeue_candidates_path=requeue_candidates_path,
    )
    profiles = load_json(profiles_path)
    enforce_compose_write_contract(
        compose_context=compose_context,
        paths={
            "facts_path": facts_path,
            "decisions_path": decisions_path,
            "profiles_path": profiles_path,
            "output_path": output_path,
            "overlay_path": overlay_path,
            "style_log_path": style_log_path,
            "requeue_candidates_path": requeue_candidates_path,
            "identity_rules_path": identity_rules_path,
            "precedence_rules_path": precedence_rules_path,
        },
        profiles=profiles,
        registry_current_write_authorization_receipt=(
            registry_current_write_authorization_receipt
        ),
    )
    facts_list = load_jsonl(facts_path)
    decisions_list = load_jsonl(decisions_path)
    overlay_map = load_optional_jsonl_map(overlay_path)
    is_v2 = is_body_plan_profiles_v2(profiles)

    if is_v2:
        identity_hint_target_map, precedence_rules = load_profile_resolution_rules(
            identity_rules_path=identity_rules_path,
            precedence_rules_path=precedence_rules_path,
        )
        entries, normalization_logs, requeue_candidates = compose_all_v2(
            facts_list,
            decisions_list,
            overlay_map,
            profiles,
            identity_hint_target_map=identity_hint_target_map,
            precedence_rules=precedence_rules,
            resolver_authority_mode=resolver_authority_mode,
        )
    else:
        entries, normalization_logs, requeue_candidates = compose_all_legacy(
            facts_list,
            decisions_list,
            overlay_map,
            profiles,
            allow_legacy_runtime_state=True,
        )

    stats = {
        "total": len(entries),
        "adopted_override": sum(1 for entry in entries.values() if entry["source"] == "override"),
        "unadopted": sum(1 for entry in entries.values() if entry["source"] == UNADOPTED_RUNTIME_STATE),
    }
    if is_v2:
        resolved_profile_counts = Counter(
            entry.get("resolved_profile")
            for entry in entries.values()
            if entry.get("resolved_profile") is not None
        )
        resolution_source_counts = Counter(
            entry.get("resolution_source")
            for entry in entries.values()
            if entry.get("resolution_source") is not None
        )
        coverage_quality_candidate_counts = Counter(
            entry.get("coverage_quality_candidate")
            for entry in entries.values()
            if entry.get("coverage_quality_candidate") is not None
        )
        missing_required_section_counts = Counter()
        for entry in entries.values():
            for section_name in entry.get("body_plan", {}).get("missing_required_sections", []):
                missing_required_section_counts[str(section_name)] += 1
        stats.update(
            {
                "adopted_composed_v2_preview": sum(
                    1 for entry in entries.values() if entry["source"] == "composed_v2_preview"
                ),
                "resolved_profile_counts": dict(resolved_profile_counts),
                "resolution_source_counts": dict(resolution_source_counts),
                "coverage_quality_candidate_counts": dict(coverage_quality_candidate_counts),
                "missing_required_section_counts": dict(missing_required_section_counts),
            }
        )
    else:
        stats.update(
            {
                "adopted_composed": sum(
                    1 for entry in entries.values() if entry["source"] == "composed"
                ),
                "quality_flagged": sum(
                    1 for entry in entries.values() if entry.get("quality_flag") is not None
                ),
                "requeue_candidates": len(requeue_candidates),
            }
        )

    receipt_payload = (
        read_registry_fixture_receipt(registry_current_write_authorization_receipt)
        if registry_current_write_authorization_receipt is not None
        else None
    )
    rendered = {
        "meta": {
            "version": "dvf-3-3-body-plan-v2-preview-v0" if is_v2 else "interaction-cluster-rendered-v0",
            "generated_at": (
                receipt_payload["rendered_generated_at"]
                if receipt_payload is not None
                else datetime.now(timezone.utc).isoformat()
            ),
            "facts_sha256": file_sha256(facts_path),
            "decisions_sha256": file_sha256(decisions_path),
            "profiles_sha256": file_sha256(profiles_path),
            "overlay_path": str(overlay_path) if overlay_path is not None else None,
            "overlay_sha256": file_sha256(overlay_path) if overlay_path is not None and overlay_path.exists() else None,
            "entries_sha256": entries_sha256(entries),
            "stats": stats,
        },
        "entries": entries,
    }

    rendered_text = json.dumps(rendered, ensure_ascii=False, indent=2)
    style_text = "".join(
        json.dumps(log_entry, ensure_ascii=False) + "\n"
        for log_entry in normalization_logs
    )
    requeue_text = "".join(
        json.dumps(row, ensure_ascii=False) + "\n"
        for row in requeue_candidates
    )
    if registry_current_write_authorization_receipt is not None:
        validate_registry_fixture_receipt(
            registry_current_write_authorization_receipt,
            paths={
                "facts_path": facts_path,
                "decisions_path": decisions_path,
                "profiles_path": profiles_path,
                "output_path": output_path,
                "overlay_path": overlay_path,
                "style_log_path": style_log_path,
                "requeue_candidates_path": requeue_candidates_path,
                "identity_rules_path": identity_rules_path,
                "precedence_rules_path": precedence_rules_path,
            },
            profiles=profiles,
            rendered=rendered,
            computed_postwrite_hashes={
                "output_path": hashlib.sha256(
                    text_mode_write_bytes(rendered_text)
                ).hexdigest(),
                "style_log_path": hashlib.sha256(
                    text_mode_write_bytes(style_text)
                ).hexdigest(),
                "requeue_candidates_path": hashlib.sha256(
                    text_mode_write_bytes(requeue_text)
                ).hexdigest(),
            },
            consume=True,
        )

    write_json_retry(output_path, rendered)
    write_lines_retry(
        style_log_path,
        [json.dumps(log_entry, ensure_ascii=False) + "\n" for log_entry in normalization_logs],
    )

    if requeue_candidates_path is not None:
        write_jsonl(requeue_candidates_path, requeue_candidates)
    return rendered


def default_entrypoint_paths(mode: str) -> dict[str, Path | None]:
    if mode == DEFAULT_MODE:
        return {
            "profiles_path": BODY_PLAN_PROFILES_PATH,
            "overlay_path": CURRENT_OVERLAY_SUPPORT_PATH,
            "output_path": OUTPUT_DIR / "dvf_3_3_rendered.json",
            "style_log_path": STYLE_LOG_PATH,
            "requeue_candidates_path": None,
        }
    if mode == DIAGNOSTIC_RESOLVER_MODE:
        return {
            "profiles_path": BODY_PLAN_PROFILES_PATH,
            "overlay_path": BODY_SOURCE_OVERLAY_PATH,
            "output_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_resolver_dvf_3_3_rendered.json",
            "style_log_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_resolver_style_log.jsonl",
            "requeue_candidates_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_resolver_requeue_candidates.jsonl",
        }
    raise ValueError(f"Unknown entrypoint mode: {mode}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose Iris DVF 3-3 layer3 text.")
    parser.add_argument("--mode", choices=ENTRYPOINT_MODES, default=DEFAULT_MODE)
    parser.add_argument("--compose-context", choices=COMPOSE_CONTEXTS, default=None)
    parser.add_argument("--facts-path", type=Path, default=DATA_DIR / "dvf_3_3_facts.jsonl")
    parser.add_argument("--decisions-path", type=Path, default=DATA_DIR / "dvf_3_3_decisions.jsonl")
    parser.add_argument("--profiles-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=None)
    parser.add_argument("--overlay-path", type=Path, default=None)
    parser.add_argument("--style-log-path", type=Path, default=None)
    parser.add_argument("--requeue-candidates-path", type=Path, default=None)
    parser.add_argument("--identity-rules-path", type=Path, default=IDENTITY_RULES_PATH)
    parser.add_argument("--precedence-rules-path", type=Path, default=PRECEDENCE_RULES_PATH)
    parser.add_argument("--registry-current-write-authorization-receipt", type=Path, default=None)
    return parser.parse_args(argv)


def resolve_entrypoint_paths(args: argparse.Namespace) -> dict[str, Path | None]:
    defaults = default_entrypoint_paths(args.mode)
    return {
        "facts_path": args.facts_path,
        "decisions_path": args.decisions_path,
        "profiles_path": args.profiles_path or defaults["profiles_path"],
        "output_path": args.output_path or defaults["output_path"],
        "overlay_path": args.overlay_path or defaults["overlay_path"],
        "style_log_path": args.style_log_path or defaults["style_log_path"],
        "requeue_candidates_path": args.requeue_candidates_path or defaults["requeue_candidates_path"],
        "identity_rules_path": args.identity_rules_path,
        "precedence_rules_path": args.precedence_rules_path,
    }


def explicit_write_path_args_present(args: argparse.Namespace) -> bool:
    return (
        args.output_path is not None
        or args.style_log_path is not None
        or args.requeue_candidates_path is not None
    )


def compose_context_for_entrypoint(args: argparse.Namespace) -> str | None:
    if args.compose_context is not None:
        return args.compose_context
    if args.mode == DIAGNOSTIC_RESOLVER_MODE:
        return DIAGNOSTIC_COMPOSE_CONTEXT
    if args.mode == DEFAULT_MODE and not explicit_write_path_args_present(args):
        return CURRENT_COMPOSE_CONTEXT
    return None


def enforce_entrypoint_mode_contract(
    mode: str,
    paths: dict[str, Path | None],
    *,
    compose_context: str | None,
) -> None:
    profiles_path = paths["profiles_path"]
    if profiles_path is None:
        raise ValueError("profiles_path is required")
    profiles = load_json(profiles_path)
    is_v2 = is_body_plan_profiles_v2(profiles)

    if mode in {DEFAULT_MODE, DIAGNOSTIC_RESOLVER_MODE} and not is_v2:
        raise ValueError(f"{mode} mode requires compose_profiles_v2.json / schema compose-profiles-v2")

    if compose_context == CURRENT_COMPOSE_CONTEXT:
        enforce_current_authority_input_contract(mode, paths)

    if mode == DIAGNOSTIC_RESOLVER_MODE:
        for key in ("output_path", "style_log_path", "requeue_candidates_path"):
            value = paths.get(key)
            if value is not None and not is_under_path(value, EDPAS_DIAGNOSTIC_DIR):
                raise ValueError(f"{mode} {key} must stay under {EDPAS_DIAGNOSTIC_DIR}")


def resolver_authority_mode_for_entrypoint(mode: str) -> str:
    if mode == DIAGNOSTIC_RESOLVER_MODE:
        return DIAGNOSTIC_RESOLVER_AUTHORITY_MODE
    return DEFAULT_RESOLVER_AUTHORITY_MODE


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = resolve_entrypoint_paths(args)
    compose_context = compose_context_for_entrypoint(args)
    enforce_entrypoint_mode_contract(args.mode, paths, compose_context=compose_context)
    build_rendered(
        paths["facts_path"],
        paths["decisions_path"],
        paths["profiles_path"],
        paths["output_path"],
        paths["overlay_path"],
        paths["style_log_path"],
        paths["requeue_candidates_path"],
        paths["identity_rules_path"],
        paths["precedence_rules_path"],
        resolver_authority_mode_for_entrypoint(args.mode),
        compose_context=compose_context,
        registry_current_write_authorization_receipt=(
            args.registry_current_write_authorization_receipt
        ),
    )
    print("rendered written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
