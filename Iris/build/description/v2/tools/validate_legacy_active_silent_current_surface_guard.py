from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fnmatch import fnmatchcase
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable


LEGACY_TOKENS = {"active", "silent"}
CURRENT_SURFACE_ERROR_CODE = "CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL"
UNALLOWLISTED_ERROR_CODE = "UNALLOWLISTED_LEGACY_ACTIVE_SILENT_OCCURRENCE"
ALLOWLIST_TOO_BROAD_ERROR_CODE = "ALLOWLIST_RULE_TOO_BROAD"
DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE = "DIAGNOSTIC_ALIAS_USED_OUTSIDE_EXPLICIT_DIAGNOSTIC_SURFACE"
LEGACY_METRIC_RENDERED_ERROR_CODE = "LEGACY_METRIC_KEY_RENDERED_AS_CURRENT_LABEL"
DEFAULT_RUNTIME_STATE_ERROR_CODE = "DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM"
DEFAULT_RESOLVER_COMPAT_ERROR_CODE = "DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL"

ERROR_CATALOG = {
    CURRENT_SURFACE_ERROR_CODE: (
        "Legacy active/silent appeared as a current generated/operator, writer, or packaged Lua label."
    ),
    UNALLOWLISTED_ERROR_CODE: "Legacy active/silent occurrence did not match a hard-fail or allow rule.",
    ALLOWLIST_TOO_BROAD_ERROR_CODE: "A manifest allow rule can cover current output too broadly.",
    DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE: (
        "A diagnostic/import alias occurrence appeared outside an explicit diagnostic/import surface."
    ),
    LEGACY_METRIC_RENDERED_ERROR_CODE: "A legacy metric key was rendered as a current label.",
    DEFAULT_RUNTIME_STATE_ERROR_CODE: (
        "Existing runtime_state guard owns default-path active/silent runtime enum rejection."
    ),
    DEFAULT_RESOLVER_COMPAT_ERROR_CODE: (
        "Existing resolver guard owns legacy compatibility compose_profile fallback rejection."
    ),
}

TEXT_SUFFIXES = {".json", ".jsonl", ".lua", ".md", ".py", ".txt"}
SKIP_DIR_NAMES = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache"}
DEFAULT_SCAN_ROOTS = ("Iris", "docs")
SCAN_BACKENDS = {"rg", "python"}
SCAN_BACKEND_UNAVAILABLE_ERROR_CODE = "scan_backend_unavailable"
OCCURRENCE_STREAM_SCHEMA = "legacy-active-silent-occurrence-stream-reference-v1"
OCCURRENCE_STREAM_LOGICAL_ID = "legacy-active-silent-current-surface-occurrences"
OCCURRENCE_STREAM_MEDIA_TYPE = "application/x-ndjson"
OCCURRENCE_PRODUCER_VERSION = "legacy-active-silent-current-surface-guard-v1"
SUCCESSOR_OUTPUT_POLICY_RELATIVE = Path(
    "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
)
AUTHORIZED_RESULT_SUBROOTS = ["objects", "phases", "logs", "package"]
AUTHORIZED_LIFECYCLE_ROLES = {
    "retained_current_required",
    "retained_historical_reproduction",
    "archived",
    "disposable",
    "delete_eligible",
}
V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
DEFAULT_MANIFEST = (
    V2_ROOT
    / "staging"
    / "compose_contract_migration"
    / "legacy_active_silent_current_surface_guard_round"
    / "phase1_manifest"
    / "current_surface_guard_referent_manifest.json"
)
TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])(active|silent)(?=_count\b|\b)", re.IGNORECASE)
RUNTIME_STATE_VALUE_RE = re.compile(
    r'"(?:state|runtime_state)"\s*:\s*"(active|silent)"',
    re.IGNORECASE,
)
SOURCE_JSON_VALUE_RE = re.compile(r'"source"\s*:\s*"(active|silent)"', re.IGNORECASE)
SOURCE_LUA_VALUE_RE = re.compile(
    r'(?:\["source"\]|source)\s*=\s*["\'](active|silent)["\']',
    re.IGNORECASE,
)
LABEL_VALUE_RE = re.compile(
    r'"(?:operator_label|current_report_label|writer_output_label|runtime_label|label)"\s*:\s*"(active|silent)"',
    re.IGNORECASE,
)
LEGACY_METRIC_KEY_RE = re.compile(r"\b(?:active_count|silent_count)\b", re.IGNORECASE)
LEGACY_METRIC_RENDERED_RE = re.compile(
    r'"(?:label|current_label|display_label|operator_label|writer_output_label)"\s*:\s*"(?:active_count|silent_count)"',
    re.IGNORECASE,
)
LEGACY_COMPAT_LABEL_RE = re.compile(
    r'"compose_profile"\s*:\s*"(interaction_(?:tool|component|output)[^"]*)"',
    re.IGNORECASE,
)
CODE_IDENTIFIER_RE = re.compile(
    r"\b(?:activeView|isActive|setActive|getActive|active_count|silent_count)\b"
)
PLAIN_TEXT_ALLOWED_RE = re.compile(
    r"\b(?:active/silent|active / silent|silent failure|not active|active voice)\b",
    re.IGNORECASE,
)
DIAGNOSTIC_ALIAS_RE = re.compile(
    r"\b(?:diagnostic|import|alias|historical|read-only|read only|legacy)\b",
    re.IGNORECASE,
)

CURRENT_LABEL_KINDS = {
    "runtime_state_value",
    "source_value",
    "operator_label_value",
    "current_report_label_value",
    "writer_output_label_value",
}

BROAD_ALLOW_GLOBS = {
    "**/*",
    "**/*.json",
    "**/*.jsonl",
    "**/*.lua",
    "Iris/**",
    "Iris/build/**",
    "Iris/build/description/**",
    "Iris/media/**",
    "docs/**",
}


@dataclass(frozen=True)
class Occurrence:
    path: str
    line: int
    column: int
    token: str
    nearby_key: str | None
    occurrence_kind: str
    surface_class: str
    allow_rule_id: str | None
    current_label_candidate: bool
    disposition: str
    error_code: str | None
    line_excerpt: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "token": self.token.lower(),
            "nearby_key": self.nearby_key,
            "occurrence_kind": self.occurrence_kind,
            "surface_class": self.surface_class,
            "allow_rule_id": self.allow_rule_id,
            "current_label_candidate": self.current_label_candidate,
            "disposition": self.disposition,
            "error_code": self.error_code,
            "line_excerpt": self.line_excerpt,
        }


class ScanBackendUnavailable(RuntimeError):
    def __init__(self, backend: str, disposition: str, detail: str) -> None:
        super().__init__(f"{SCAN_BACKEND_UNAVAILABLE_ERROR_CODE}: {backend}: {disposition}: {detail}")
        self.backend = backend
        self.disposition = disposition
        self.detail = detail


@dataclass(frozen=True)
class ScanCensus:
    files: tuple[Path, ...]
    receipt: dict[str, Any]


def repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def normalize_rel(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _manifest_scan_surfaces(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    configured = manifest.get("scan_surfaces")
    if isinstance(configured, list) and configured:
        return [dict(item) for item in configured]

    surfaces: list[dict[str, Any]] = []
    for index, rule in enumerate(
        [*manifest.get("hard_fail_surfaces", []), *manifest.get("allow_surfaces", [])]
    ):
        globs = [str(value) for value in rule.get("path_globs", [])]
        if globs:
            surfaces.append(
                {
                    "id": str(rule.get("id", f"legacy_surface_{index}")),
                    "role": "legacy_manifest_surface",
                    "path_globs": globs,
                }
            )
    return surfaces


def _manifest_scan_exclusions(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    exclusions = manifest.get("scan_exclusions", [])
    if not isinstance(exclusions, list):
        raise ValueError("scan_exclusions must be a list")
    result = [dict(item) for item in exclusions]
    round_root = normalize_rel(str(manifest.get("round_root", ""))).rstrip("/")
    if round_root:
        result.append(
            {
                "id": "mandatory_current_round_output",
                "role": "current_guard_run_output",
                "path_globs": [round_root + "/**"],
            }
        )
    result.extend(
        [
            {
                "id": "mandatory_report_only_staging",
                "role": "report_only_staging_residue",
                "path_globs": ["Iris/build/description/v2/staging/**"],
            },
            {
                "id": "mandatory_cold_archive",
                "role": "cold_archive_payload",
                "path_globs": ["Iris/_archive/**"],
            },
        ]
    )
    return result


def write_json_create_new(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".partial", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_path, path)
        except FileExistsError as exc:
            raise FileExistsError(f"refusing to replace existing output: {path}") from exc
        temp_path.unlink(missing_ok=True)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def _enumerate_python_files(repo_root: Path) -> tuple[list[Path], str]:
    paths: list[Path] = []
    for root_name in DEFAULT_SCAN_ROOTS:
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                paths.append(path)
    return paths, sys.version.split()[0]


def _run_rg(command: list[str], repo_root: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="strict",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise ScanBackendUnavailable("rg", "missing", str(exc)) from exc
    except subprocess.TimeoutExpired as exc:
        raise ScanBackendUnavailable("rg", "timeout", f"timeout_seconds={timeout}") from exc
    except UnicodeError as exc:
        raise ScanBackendUnavailable("rg", "unreadable_output", str(exc)) from exc


def _enumerate_rg_files(repo_root: Path, timeout: int) -> tuple[list[Path], str]:
    version_result = _run_rg(["rg", "--version"], repo_root, timeout)
    if version_result.returncode != 0:
        raise ScanBackendUnavailable(
            "rg", "abnormal_exit", f"version_exit={version_result.returncode}: {version_result.stderr.strip()}"
        )
    roots = [root_name for root_name in DEFAULT_SCAN_ROOTS if (repo_root / root_name).exists()]
    if not roots:
        return [], version_result.stdout.splitlines()[0].strip()
    result = _run_rg(["rg", "--files", "--hidden", "--no-ignore", *roots], repo_root, timeout)
    if result.returncode != 0:
        raise ScanBackendUnavailable(
            "rg", "abnormal_exit", f"files_exit={result.returncode}: {result.stderr.strip()}"
        )
    paths = [repo_root / line for line in result.stdout.splitlines() if line.strip()]
    return paths, version_result.stdout.splitlines()[0].strip()


def _matched_role(rel_path: str, rules: Iterable[dict[str, Any]]) -> str | None:
    for rule in rules:
        if pattern_matches(rel_path, [str(value) for value in rule.get("path_globs", [])]):
            return str(rule.get("role") or rule.get("id") or "unspecified")
    return None


def _contains_guard_token(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"unreadable scan input: {path}: {exc}") from exc
    return TOKEN_RE.search(text) is not None


def iter_scan_files(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    scan_backend: str = "rg",
    timeout: int = 60,
    additional_excluded_paths: Iterable[Path] = (),
) -> ScanCensus:
    if scan_backend not in SCAN_BACKENDS:
        raise ValueError(f"unsupported scan backend: {scan_backend}")
    resolved_repo = repo_root.resolve()
    if scan_backend == "rg":
        enumerated, backend_version = _enumerate_rg_files(resolved_repo, timeout)
    else:
        enumerated, backend_version = _enumerate_python_files(resolved_repo)

    scan_surfaces = _manifest_scan_surfaces(manifest)
    scan_exclusions = _manifest_scan_exclusions(manifest)
    exact_exclusions = {path.resolve() for path in additional_excluded_paths}
    included: list[Path] = []
    excluded_counts: Counter[str] = Counter()
    unreadable: list[str] = []
    seen: set[str] = set()
    for candidate in enumerated:
        try:
            path = candidate.resolve(strict=True)
        except OSError as exc:
            unreadable.append(f"{candidate}: {exc}")
            continue
        if path != resolved_repo and resolved_repo not in path.parents:
            unreadable.append(f"scan input resolves outside repository: {candidate} -> {path}")
            continue
        rel_path = repo_rel(path, resolved_repo)
        if rel_path in seen:
            continue
        seen.add(rel_path)
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIR_NAMES for part in Path(rel_path).parts):
            excluded_counts["tool_cache_or_vcs"] += 1
            continue
        if path in exact_exclusions:
            excluded_counts["current_run_exact_output"] += 1
            continue
        exclusion_role = _matched_role(rel_path, scan_exclusions)
        if exclusion_role is not None:
            excluded_counts[exclusion_role] += 1
            continue
        surface_role = _matched_role(rel_path, scan_surfaces)
        if surface_role is None:
            excluded_counts["outside_manifest_scan_surface"] += 1
            continue
        try:
            token_match = _contains_guard_token(path)
        except RuntimeError as exc:
            unreadable.append(str(exc))
            continue
        if not token_match:
            excluded_counts["no_guard_token"] += 1
            continue
        included.append(path)

    if unreadable:
        raise RuntimeError("scan census contains unreadable entries: " + " | ".join(sorted(unreadable)))
    files = tuple(sorted(set(included), key=lambda item: repo_rel(item, resolved_repo)))
    path_rows = [repo_rel(path, resolved_repo) for path in files]
    census_rows = [
        {
            "path": repo_rel(path, resolved_repo),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in files
    ]
    receipt = {
        "schema_version": "legacy-active-silent-scan-census-v1",
        "selected_backend": scan_backend,
        "backend_version": backend_version,
        "backend_available": True,
        "backend_timeout_seconds": timeout if scan_backend == "rg" else None,
        "backend_error_disposition": "none",
        "canonical_path_list_sha256": _sha256_bytes(_canonical_json_bytes(path_rows)),
        "input_census_sha256": _sha256_bytes(_canonical_json_bytes(census_rows)),
        "denominator_count": len(files),
        "excluded_role_counts": dict(sorted(excluded_counts.items())),
    }
    return ScanCensus(files=files, receipt=receipt)


def pattern_matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = normalize_rel(path)
    for pattern in patterns:
        normalized_pattern = normalize_rel(pattern)
        if fnmatchcase(normalized, normalized_pattern):
            return True
        if "/**/" in normalized_pattern:
            direct_pattern = normalized_pattern.replace("/**/", "/")
            if fnmatchcase(normalized, direct_pattern):
                return True
    return False


def match_rule(path: str, occurrence_kind: str, rules: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    for rule in rules:
        path_globs = [str(value) for value in rule.get("path_globs", [])]
        kinds = [str(value) for value in rule.get("occurrence_kinds", [])]
        if pattern_matches(path, path_globs) and (occurrence_kind in kinds or "*" in kinds):
            return rule
    return None


def classify_surface(path: str, manifest: dict[str, Any]) -> str:
    allow_rules = list(manifest.get("allow_surfaces", []))
    hard_rules = list(manifest.get("hard_fail_surfaces", []))

    if any(pattern_matches(path, rule.get("path_globs", [])) for rule in hard_rules):
        return "hard_fail"
    if any(pattern_matches(path, rule.get("path_globs", [])) for rule in allow_rules):
        return "allow"
    return "unclassified"


def infer_nearby_key(line: str) -> str | None:
    for key in (
        "runtime_state",
        "state",
        "source",
        "operator_label",
        "current_report_label",
        "writer_output_label",
        "label",
        "compose_profile",
    ):
        if key in line:
            return key
    return None


def infer_occurrence_kind(path: str, line: str, token: str) -> str:
    if pattern_matches(path, ["Iris/build/description/v2/tests/**"]):
        return "explicit_legacy_test_fixture"
    if pattern_matches(
        path,
        [
            "docs/**",
            "Iris/_docs/**",
            "Iris/_archive/**",
            "Iris/build/description/v2/staging/**",
        ],
    ):
        return "historical_quote"
    if pattern_matches(
        path,
        [
            "Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py",
            "Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py",
        ],
    ):
        return "diagnostic_alias" if DIAGNOSTIC_ALIAS_RE.search(line) else "code_identifier"
    if LEGACY_METRIC_RENDERED_RE.search(line):
        return "legacy_metric_key_rendered_label"
    if RUNTIME_STATE_VALUE_RE.search(line):
        return "runtime_state_value"
    if SOURCE_JSON_VALUE_RE.search(line) or SOURCE_LUA_VALUE_RE.search(line):
        return "source_value"
    if LABEL_VALUE_RE.search(line):
        if "operator_label" in line:
            return "operator_label_value"
        if "current_report_label" in line or "label" in line:
            return "current_report_label_value"
        return "writer_output_label_value"
    if LEGACY_METRIC_KEY_RE.search(line):
        return "legacy_metric_key"
    if LEGACY_COMPAT_LABEL_RE.search(line):
        return "diagnostic_alias"
    if pattern_matches(path, ["Iris/build/description/v2/tools/build/**/*.py"]):
        return "diagnostic_alias" if DIAGNOSTIC_ALIAS_RE.search(line) else "code_identifier"
    if pattern_matches(path, ["docs/**", "Iris/_archive/**", "Iris/_docs/**", "Iris/build/description/v2/staging/**"]):
        return "historical_quote"
    if DIAGNOSTIC_ALIAS_RE.search(line):
        return "diagnostic_alias"
    if CODE_IDENTIFIER_RE.search(line):
        return "code_identifier"
    if PLAIN_TEXT_ALLOWED_RE.search(line):
        return "plain_text"
    return "plain_text"


def primary_error_code(occurrence_kind: str, surface_class: str) -> str | None:
    if occurrence_kind == "runtime_state_value" and surface_class != "allow":
        return DEFAULT_RUNTIME_STATE_ERROR_CODE
    if occurrence_kind == "legacy_metric_key_rendered_label":
        return LEGACY_METRIC_RENDERED_ERROR_CODE
    if occurrence_kind in CURRENT_LABEL_KINDS and surface_class == "hard_fail":
        return CURRENT_SURFACE_ERROR_CODE
    if occurrence_kind == "diagnostic_alias" and surface_class != "allow":
        return DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE
    return None


def scan_path(path: Path, repo_root: Path, manifest: dict[str, Any]) -> list[Occurrence]:
    rel_path = repo_rel(path, repo_root)
    surface_class = classify_surface(rel_path, manifest)
    allow_rules = list(manifest.get("allow_surfaces", []))
    hard_rules = list(manifest.get("hard_fail_surfaces", []))
    occurrences: list[Occurrence] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in TOKEN_RE.finditer(line):
            token = match.group(1).lower()
            kind = infer_occurrence_kind(rel_path, line, token)
            allow_rule = match_rule(rel_path, kind, allow_rules)
            hard_rule = match_rule(rel_path, kind, hard_rules)
            current_label_candidate = kind in CURRENT_LABEL_KINDS or kind == "legacy_metric_key_rendered_label"
            error_code = primary_error_code(kind, surface_class)

            if error_code == DEFAULT_RUNTIME_STATE_ERROR_CODE:
                disposition = "covered_by_existing_guard"
            elif error_code is not None:
                disposition = "rewrite_required" if error_code == CURRENT_SURFACE_ERROR_CODE else "blocked_unclassified"
            elif allow_rule is not None:
                disposition = "allowed"
            elif hard_rule is not None and current_label_candidate:
                error_code = CURRENT_SURFACE_ERROR_CODE
                disposition = "rewrite_required"
            elif surface_class == "allow":
                if current_label_candidate:
                    error_code = UNALLOWLISTED_ERROR_CODE
                    disposition = "blocked_unclassified"
                else:
                    disposition = "ignore_non_label"
            elif current_label_candidate:
                error_code = UNALLOWLISTED_ERROR_CODE
                disposition = "blocked_unclassified"
            else:
                disposition = "ignore_non_label"

            occurrences.append(
                Occurrence(
                    path=rel_path,
                    line=line_number,
                    column=match.start(1) + 1,
                    token=token,
                    nearby_key=infer_nearby_key(line),
                    occurrence_kind=kind,
                    surface_class=surface_class,
                    allow_rule_id=str(allow_rule.get("id")) if allow_rule else None,
                    current_label_candidate=current_label_candidate,
                    disposition=disposition,
                    error_code=error_code,
                    line_excerpt=line.strip(),
                )
            )
    return occurrences


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for rule in manifest.get("allow_surfaces", []):
        rule_id = str(rule.get("id", "<missing>"))
        path_globs = {normalize_rel(str(value)) for value in rule.get("path_globs", [])}
        occurrence_kinds = {str(value) for value in rule.get("occurrence_kinds", [])}
        must_not_be_current_output = bool(rule.get("must_not_be_current_output"))
        if not rule.get("reason"):
            errors.append(
                {
                    "code": ALLOWLIST_TOO_BROAD_ERROR_CODE,
                    "rule_id": rule_id,
                    "message": "Allow rule lacks reason.",
                }
            )
        if not must_not_be_current_output:
            errors.append(
                {
                    "code": ALLOWLIST_TOO_BROAD_ERROR_CODE,
                    "rule_id": rule_id,
                    "message": "Allow rule must declare must_not_be_current_output = true.",
                }
            )
        if path_globs & BROAD_ALLOW_GLOBS:
            errors.append(
                {
                    "code": ALLOWLIST_TOO_BROAD_ERROR_CODE,
                    "rule_id": rule_id,
                    "message": "Allow rule uses a broad path glob.",
                }
            )
        forbidden_current_kinds = CURRENT_LABEL_KINDS | {"legacy_metric_key_rendered_label"}
        if occurrence_kinds & forbidden_current_kinds:
            errors.append(
                {
                    "code": ALLOWLIST_TOO_BROAD_ERROR_CODE,
                    "rule_id": rule_id,
                    "message": "Allow rule admits a current-label occurrence kind.",
                }
            )
    return errors


def scan_repo(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    scan_backend: str = "rg",
    scan_timeout: int = 60,
    additional_excluded_paths: Iterable[Path] = (),
) -> tuple[list[Occurrence], dict[str, Any]]:
    occurrences: list[Occurrence] = []
    census = iter_scan_files(
        repo_root,
        manifest,
        scan_backend=scan_backend,
        timeout=scan_timeout,
        additional_excluded_paths=additional_excluded_paths,
    )
    for path in census.files:
        occurrences.extend(scan_path(path, repo_root, manifest))
    return (
        sorted(occurrences, key=lambda item: (item.path, item.line, item.column, item.token)),
        census.receipt,
    )


def summarize(occurrences: list[Occurrence], manifest_errors: list[dict[str, Any]]) -> dict[str, Any]:
    hard_fail_residue = [
        item
        for item in occurrences
        if item.error_code == CURRENT_SURFACE_ERROR_CODE or item.error_code == DEFAULT_RUNTIME_STATE_ERROR_CODE
    ]
    unclassified = [
        item
        for item in occurrences
        if item.error_code
        in {
            UNALLOWLISTED_ERROR_CODE,
            DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE,
            LEGACY_METRIC_RENDERED_ERROR_CODE,
        }
        or item.disposition == "blocked_unclassified"
    ]
    negative_fixture_reach = {
        "runtime_state_default_guard": any(
            item.error_code == DEFAULT_RUNTIME_STATE_ERROR_CODE for item in occurrences
        ),
        "current_surface_guard": any(item.error_code == CURRENT_SURFACE_ERROR_CODE for item in occurrences),
        "legacy_metric_rendered_guard": any(
            item.error_code == LEGACY_METRIC_RENDERED_ERROR_CODE for item in occurrences
        ),
    }
    return {
        "manifest_error_count": len(manifest_errors),
        "occurrence_count": len(occurrences),
        "hard_fail_current_label_occurrence_count": len(hard_fail_residue),
        "unclassified_occurrence_count": len(unclassified),
        "allowed_occurrence_count": sum(1 for item in occurrences if item.disposition == "allowed"),
        "non_label_occurrence_count": sum(1 for item in occurrences if item.disposition == "ignore_non_label"),
        "covered_by_existing_guard_count": sum(
            1 for item in occurrences if item.disposition == "covered_by_existing_guard"
        ),
        "gate_a_pass": len(manifest_errors) == 0 and len(hard_fail_residue) == 0 and len(unclassified) == 0,
        "negative_fixture_reach": negative_fixture_reach,
    }


def _occurrence_stream_bytes(occurrences: Iterable[Occurrence | dict[str, Any]]) -> bytes:
    chunks: list[bytes] = []
    for occurrence in occurrences:
        row = occurrence.as_dict() if isinstance(occurrence, Occurrence) else dict(occurrence)
        chunks.append(_canonical_json_bytes(row))
    return b"".join(chunks)


def _atomic_store_object(result_root: Path, payload: bytes) -> dict[str, Any]:
    digest = _sha256_bytes(payload)
    relative_path = Path("objects") / "sha256" / digest[:2] / digest
    object_path = result_root / relative_path
    object_path.parent.mkdir(parents=True, exist_ok=True)
    if object_path.exists():
        if (
            not object_path.is_file()
            or object_path.stat().st_size != len(payload)
            or _sha256_file(object_path) != digest
        ):
            raise RuntimeError(f"canonical object collision or corruption: {object_path}")
    else:
        fd, temp_name = tempfile.mkstemp(prefix=f".{digest}.", suffix=".partial", dir=object_path.parent)
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if _sha256_file(temp_path) != digest:
                raise RuntimeError("temporary occurrence object hash mismatch")
            try:
                os.link(temp_path, object_path)
            except FileExistsError:
                if object_path.stat().st_size != len(payload) or _sha256_file(object_path) != digest:
                    raise RuntimeError(f"canonical object collision or corruption: {object_path}")
            temp_path.unlink(missing_ok=True)
        except BaseException:
            temp_path.unlink(missing_ok=True)
            raise
    return {
        "schema_version": OCCURRENCE_STREAM_SCHEMA,
        "logical_id": OCCURRENCE_STREAM_LOGICAL_ID,
        "sha256": digest,
        "bytes": len(payload),
        "media_type": OCCURRENCE_STREAM_MEDIA_TYPE,
        "producer_version": OCCURRENCE_PRODUCER_VERSION,
        "object": {
            "algorithm": "sha256",
            "relative_path": relative_path.as_posix(),
            "lifecycle_role": "retained_current_required",
        },
    }


def store_occurrence_stream(
    occurrences: list[Occurrence], result_root: Path
) -> dict[str, Any]:
    resolved_result = result_root.resolve()
    temporary_parent = resolved_result / "objects" / "sha256"
    temporary_parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".occurrences.", suffix=".partial", dir=temporary_parent)
    temp_path = Path(temp_name)
    digest = hashlib.sha256()
    byte_count = 0
    try:
        with os.fdopen(fd, "wb") as handle:
            for occurrence in occurrences:
                row = _canonical_json_bytes(occurrence.as_dict())
                handle.write(row)
                digest.update(row)
                byte_count += len(row)
            handle.flush()
            os.fsync(handle.fileno())
        sha256 = digest.hexdigest()
        object_path = temporary_parent / sha256[:2] / sha256
        object_path.parent.mkdir(parents=True, exist_ok=True)
        if object_path.exists():
            if object_path.stat().st_size != byte_count or _sha256_file(object_path) != sha256:
                raise RuntimeError(f"canonical object collision or corruption: {object_path}")
        else:
            try:
                os.link(temp_path, object_path)
            except FileExistsError:
                if object_path.stat().st_size != byte_count or _sha256_file(object_path) != sha256:
                    raise RuntimeError(f"canonical object collision or corruption: {object_path}")
        temp_path.unlink(missing_ok=True)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    reference = {
        "schema_version": OCCURRENCE_STREAM_SCHEMA,
        "logical_id": OCCURRENCE_STREAM_LOGICAL_ID,
        "sha256": sha256,
        "bytes": byte_count,
        "media_type": OCCURRENCE_STREAM_MEDIA_TYPE,
        "producer_version": OCCURRENCE_PRODUCER_VERSION,
        "object": {
            "algorithm": "sha256",
            "relative_path": (Path("objects") / "sha256" / sha256[:2] / sha256).as_posix(),
            "lifecycle_role": "retained_current_required",
        },
    }
    counts = Counter(item.disposition for item in occurrences)
    error_counts = Counter(item.error_code for item in occurrences if item.error_code is not None)
    return {
        **reference,
        "row_count": len(occurrences),
        "disposition_counts": dict(sorted(counts.items())),
        "error_code_counts": dict(sorted(error_counts.items())),
    }


def load_occurrence_stream(reference: dict[str, Any], result_root: Path) -> list[dict[str, Any]]:
    verification = verify_occurrence_stream_reference(reference, result_root)
    object_path = Path(verification["path"])
    rows: list[dict[str, Any]] = []
    with object_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def verify_occurrence_stream_reference(reference: dict[str, Any], result_root: Path) -> dict[str, Any]:
    if reference.get("schema_version") != OCCURRENCE_STREAM_SCHEMA:
        raise ValueError("unsupported occurrence stream reference schema")
    if reference.get("logical_id") != OCCURRENCE_STREAM_LOGICAL_ID:
        raise ValueError("occurrence stream logical id mismatch")
    if reference.get("media_type") != OCCURRENCE_STREAM_MEDIA_TYPE:
        raise ValueError("occurrence stream media type mismatch")
    if reference.get("producer_version") != OCCURRENCE_PRODUCER_VERSION:
        raise ValueError("occurrence stream producer version mismatch")
    object_descriptor = reference.get("object", {})
    if (
        object_descriptor.get("algorithm") != "sha256"
        or object_descriptor.get("lifecycle_role") != "retained_current_required"
    ):
        raise ValueError("occurrence stream object descriptor mismatch")
    digest = str(reference.get("sha256", ""))
    expected_relative = Path("objects") / "sha256" / digest[:2] / digest
    recorded_relative = Path(str(object_descriptor.get("relative_path", "")))
    if recorded_relative.as_posix() != expected_relative.as_posix():
        raise ValueError("occurrence stream object path does not match its SHA-256")
    object_path = result_root.resolve() / recorded_relative
    if not object_path.is_file():
        raise FileNotFoundError(f"missing occurrence stream object: {object_path}")
    if object_path.stat().st_size != int(reference.get("bytes", -1)) or _sha256_file(object_path) != digest:
        raise ValueError("occurrence stream object identity mismatch")
    row_count = 0
    disposition_counts: Counter[str] = Counter()
    error_code_counts: Counter[str] = Counter()
    hard_fail_count = 0
    unclassified_count = 0
    with object_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            row_count += 1
            disposition = str(row.get("disposition"))
            disposition_counts[disposition] += 1
            error_code = row.get("error_code")
            if error_code is not None:
                error_code_counts[str(error_code)] += 1
            if error_code in {CURRENT_SURFACE_ERROR_CODE, DEFAULT_RUNTIME_STATE_ERROR_CODE}:
                hard_fail_count += 1
            if (
                error_code
                in {
                    UNALLOWLISTED_ERROR_CODE,
                    DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE,
                    LEGACY_METRIC_RENDERED_ERROR_CODE,
                }
                or disposition == "blocked_unclassified"
            ):
                unclassified_count += 1
    if row_count != int(reference.get("row_count", -1)):
        raise ValueError("occurrence stream row count mismatch")
    recorded_dispositions = {
        str(key): int(value) for key, value in dict(reference.get("disposition_counts", {})).items()
    }
    recorded_errors = {
        str(key): int(value) for key, value in dict(reference.get("error_code_counts", {})).items()
    }
    if dict(sorted(disposition_counts.items())) != dict(sorted(recorded_dispositions.items())):
        raise ValueError("occurrence stream disposition counts mismatch")
    if dict(sorted(error_code_counts.items())) != dict(sorted(recorded_errors.items())):
        raise ValueError("occurrence stream error-code counts mismatch")
    return {
        "path": str(object_path),
        "row_count": row_count,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "error_code_counts": dict(sorted(error_code_counts.items())),
        "hard_fail_current_label_occurrence_count": hard_fail_count,
        "unclassified_occurrence_count": unclassified_count,
    }


def _assert_no_reparse_ancestor(path: Path, label: str) -> None:
    cursor = Path(os.path.abspath(path))
    while True:
        if cursor.exists():
            attributes = int(getattr(cursor.stat(), "st_file_attributes", 0))
            if cursor.is_symlink() or bool(attributes & 0x400):
                raise ValueError(f"{label} has a symlink/reparse ancestor: {cursor}")
        parent = cursor.parent
        if parent == cursor:
            break
        cursor = parent


def validate_external_run_roots(repo_root: Path, work_root: Path, result_root: Path) -> tuple[Path, Path]:
    _assert_no_reparse_ancestor(repo_root, "repository root")
    _assert_no_reparse_ancestor(work_root, "work_root")
    _assert_no_reparse_ancestor(result_root, "result_root")
    repo = repo_root.resolve()
    work = work_root.resolve()
    result = result_root.resolve()
    for label, root in (("work_root", work), ("result_root", result)):
        if root == repo or repo in root.parents:
            raise ValueError(f"{label} must be external to the repository: {root}")
        if not root.is_dir():
            raise ValueError(f"{label} must be a pre-allocated directory: {root}")
        if any(root.iterdir()):
            raise ValueError(f"{label} must be empty at producer entry: {root}")
    if work == result or work in result.parents or result in work.parents:
        raise ValueError("work_root and result_root must be disjoint")
    return work, result


def validate_allocation_receipt(
    repo_root: Path,
    allocation_receipt_path: Path,
    work_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    receipt = read_json(allocation_receipt_path)
    if not isinstance(receipt, dict):
        raise ValueError("allocation receipt must be a JSON object")
    if receipt.get("schema_version") != "iris_repository_runtime_lightweighting_allocation_receipt_v1":
        raise ValueError("unsupported allocation receipt schema")
    if receipt.get("status") != "PASS":
        raise ValueError("allocation receipt is not PASS")
    for field in ("claim_id", "attempt_id", "run_id", "allocation_profile"):
        if not isinstance(receipt.get(field), str) or not str(receipt[field]).strip():
            raise ValueError(f"allocation receipt lacks non-empty {field}")
    if receipt["allocation_profile"] not in {"checkpoint", "terminal-run-a", "terminal-run-b"}:
        raise ValueError("allocation receipt profile cannot authorize persistent guard output")
    for proof_name, count_name in (
        ("pre_create_existence", "existing_count"),
        ("ledger_reuse", "match_count"),
        ("post_create_empty", "nonempty_count"),
    ):
        proof = receipt.get(proof_name, {})
        if proof.get("checked") is not True or int(proof.get(count_name, -1)) != 0:
            raise ValueError(f"allocation receipt proof is not zero-PASS: {proof_name}")
    roots = receipt.get("roots", {})
    if (
        Path(str(roots.get("work", ""))).resolve() != work_root
        or Path(str(roots.get("result", ""))).resolve() != result_root
    ):
        raise ValueError("allocation receipt does not bind producer roots")
    ledger = receipt.get("allocation_ledger", {})
    required_ledger_fields = {
        "path",
        "sha256_after_append",
        "appended_entry_sha256",
        "append_offset_bytes",
        "reservation_ledger_sha256_after_append",
        "reservation_entry_sha256",
        "reservation_append_offset_bytes",
    }
    if not isinstance(ledger, dict) or not required_ledger_fields.issubset(ledger):
        raise ValueError("allocation receipt lacks ledger identity")
    ledger_path = Path(str(ledger["path"])).resolve()
    resolved_repo = repo_root.resolve()
    if not ledger_path.is_file() or resolved_repo in ledger_path.parents:
        raise ValueError("allocation ledger must be a readable repository-external file")
    ledger_bytes = ledger_path.read_bytes()
    reservation_offset = int(ledger["reservation_append_offset_bytes"])
    if reservation_offset < 0 or reservation_offset >= len(ledger_bytes):
        raise ValueError("allocation ledger reservation offset is outside the ledger")
    reservation_newline = ledger_bytes.find(b"\n", reservation_offset)
    if reservation_newline < 0:
        raise ValueError("allocation ledger reservation entry is not newline terminated")
    reservation_bytes = ledger_bytes[reservation_offset : reservation_newline + 1]
    if _sha256_bytes(reservation_bytes) != str(ledger["reservation_entry_sha256"]).lower():
        raise ValueError("allocation ledger reservation entry identity mismatch")
    if _sha256_bytes(ledger_bytes[: reservation_newline + 1]) != str(
        ledger["reservation_ledger_sha256_after_append"]
    ).lower():
        raise ValueError("allocation ledger reservation prefix identity mismatch")
    offset = int(ledger["append_offset_bytes"])
    if offset < 0 or offset >= len(ledger_bytes):
        raise ValueError("allocation ledger append offset is outside the ledger")
    newline = ledger_bytes.find(b"\n", offset)
    if newline < 0:
        raise ValueError("allocation ledger appended entry is not newline terminated")
    entry_bytes = ledger_bytes[offset : newline + 1]
    if _sha256_bytes(entry_bytes) != str(ledger["appended_entry_sha256"]).lower():
        raise ValueError("allocation ledger appended entry identity mismatch")
    if _sha256_bytes(ledger_bytes[: newline + 1]) != str(ledger["sha256_after_append"]).lower():
        raise ValueError("allocation ledger prefix identity mismatch")
    if offset != reservation_newline + 1:
        raise ValueError("allocation ledger commit does not immediately follow its reservation")
    reservation_entry = json.loads(reservation_bytes.decode("utf-8"))
    ledger_entry = json.loads(entry_bytes.decode("utf-8"))
    if (
        reservation_entry.get("schema_version")
        != "iris_repository_runtime_lightweighting_allocation_ledger_v2"
        or reservation_entry.get("state") != "reserved"
    ):
        raise ValueError("allocation ledger reservation state is invalid")
    if (
        ledger_entry.get("schema_version")
        != "iris_repository_runtime_lightweighting_allocation_ledger_v2"
        or ledger_entry.get("state") != "committed"
    ):
        raise ValueError("allocation ledger commit state is invalid")
    if (
        ledger_entry.get("reservation_entry_sha256")
        != str(ledger["reservation_entry_sha256"]).lower()
        or int(ledger_entry.get("reservation_append_offset_bytes", -1)) != reservation_offset
    ):
        raise ValueError("allocation ledger commit does not bind its reservation")
    for field in ("claim_id", "attempt_id", "run_id", "allocation_profile"):
        if ledger_entry.get(field) != receipt.get(field) or reservation_entry.get(field) != receipt.get(field):
            raise ValueError(f"allocation ledger entry does not bind receipt {field}")
    ledger_paths = {Path(str(value)).resolve() for value in ledger_entry.get("paths", [])}
    reservation_paths = {Path(str(value)).resolve() for value in reservation_entry.get("paths", [])}
    if reservation_paths != ledger_paths:
        raise ValueError("allocation ledger reservation and commit paths differ")
    if work_root not in ledger_paths or result_root not in ledger_paths:
        raise ValueError("allocation ledger entry does not bind producer roots")
    return receipt


def validate_successor_output_policy(repo_root: Path, policy_path: Path) -> dict[str, Any]:
    expected_path = (repo_root.resolve() / SUCCESSOR_OUTPUT_POLICY_RELATIVE).resolve()
    resolved_path = policy_path.resolve()
    if resolved_path != expected_path or not resolved_path.is_file():
        raise ValueError("successor output policy must be the repository-owned canonical file")
    policy = read_json(resolved_path)
    if policy.get("schema_version") != "iris_repository_runtime_lightweighting_output_policy_v1":
        raise ValueError("unsupported successor output policy schema")
    if policy.get("approval", {}).get("approved") is not True:
        raise ValueError("successor output policy is not approved")
    if policy.get("external_subroots") != AUTHORIZED_RESULT_SUBROOTS:
        raise ValueError("successor output policy external subroots mismatch")
    if set(policy.get("lifecycle_roles", [])) != AUTHORIZED_LIFECYCLE_ROLES:
        raise ValueError("successor output policy lifecycle vocabulary mismatch")
    if policy.get("canonical_object_layout") != "objects/sha256/<prefix>/<sha256>":
        raise ValueError("successor output policy object layout mismatch")
    if policy.get("dangling_reference_allowed") is not False:
        raise ValueError("successor output policy must reject dangling references")
    production = policy.get("production_contract", {})
    required_true = {
        "atomic_object_promotion_required",
        "external_work_root_required",
        "manifest_owned_cleanup_only",
        "newly_allocated_existing_empty_roots_required",
        "result_root_required",
    }
    if any(production.get(field) is not True for field in required_true):
        raise ValueError("successor output policy production contract is incomplete")
    if production.get("repository_local_large_output_allowed") is not False:
        raise ValueError("successor output policy permits repository-local large output")
    if production.get("run_root_reuse_allowed") is not False:
        raise ValueError("successor output policy permits run-root reuse")
    return policy


def _authorized_output_path(result_root: Path, output: Path, *, allowed_subroots: set[str]) -> Path:
    resolved_result = result_root.resolve()
    resolved_output = output.resolve()
    if resolved_output == resolved_result or resolved_result not in resolved_output.parents:
        raise ValueError(f"persistent output escapes authorized result root: {resolved_output}")
    relative = resolved_output.relative_to(resolved_result)
    if not relative.parts or relative.parts[0] not in allowed_subroots:
        raise ValueError(f"persistent output uses unauthorized result subroot: {resolved_output}")
    if resolved_output.exists():
        raise FileExistsError(f"persistent output already exists: {resolved_output}")
    cursor = resolved_output.parent
    while cursor != resolved_result:
        if cursor.exists() and (
            cursor.is_symlink()
            or bool(getattr(cursor.stat(), "st_file_attributes", 0) & 0x400)
        ):
            raise ValueError(f"persistent output has a reparse ancestor: {cursor}")
        cursor = cursor.parent
    return resolved_output


def validate_repo(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    scan_backend: str = "rg",
    scan_timeout: int = 60,
    result_root: Path | None = None,
    additional_excluded_paths: Iterable[Path] = (),
) -> dict[str, Any]:
    manifest_errors = validate_manifest(manifest)
    occurrences, scan_receipt = scan_repo(
        repo_root,
        manifest,
        scan_backend=scan_backend,
        scan_timeout=scan_timeout,
        additional_excluded_paths=additional_excluded_paths,
    )
    errors = list(manifest_errors)
    for occurrence in occurrences:
        if occurrence.error_code is not None:
            errors.append(
                {
                    "code": occurrence.error_code,
                    "path": occurrence.path,
                    "line": occurrence.line,
                    "column": occurrence.column,
                    "occurrence_kind": occurrence.occurrence_kind,
                    "surface_class": occurrence.surface_class,
                    "message": occurrence.line_excerpt,
                }
            )
    summary = summarize(occurrences, manifest_errors)
    ephemeral_stream_payload = _occurrence_stream_bytes(occurrences) if result_root is None else None
    occurrence_stream = (
        store_occurrence_stream(occurrences, result_root)
        if result_root is not None
        else {
            "schema_version": OCCURRENCE_STREAM_SCHEMA,
            "logical_id": OCCURRENCE_STREAM_LOGICAL_ID,
            "sha256": _sha256_bytes(ephemeral_stream_payload or b""),
            "bytes": len(ephemeral_stream_payload or b""),
            "row_count": len(occurrences),
            "media_type": OCCURRENCE_STREAM_MEDIA_TYPE,
            "producer_version": OCCURRENCE_PRODUCER_VERSION,
            "materialized": False,
            "disposition_counts": dict(sorted(Counter(item.disposition for item in occurrences).items())),
            "error_code_counts": dict(
                sorted(Counter(item.error_code for item in occurrences if item.error_code is not None).items())
            ),
        }
    )
    return {
        "schema_version": "legacy-active-silent-current-surface-guard-report-v1",
        "status": "pass" if summary["gate_a_pass"] else "fail",
        "error_catalog": ERROR_CATALOG,
        "summary": summary,
        "errors": errors,
        "error_summary": {
            "count": len(errors),
            "code_counts": dict(sorted(Counter(str(item.get("code")) for item in errors).items())),
        },
        "occurrence_stream": occurrence_stream,
        "scan_receipt": scan_receipt,
    }


def compact_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in report.items()
        if key not in {"errors", "error_catalog"}
    } | {
        "error_catalog_sha256": _sha256_bytes(_canonical_json_bytes(ERROR_CATALOG)),
    }


def write_inventory_files(
    report: dict[str, Any],
    output_root: Path,
    result_root: Path | None = None,
    *,
    create_new: bool = False,
) -> None:
    verification: dict[str, Any] | None = None
    if result_root is not None:
        verification = verify_occurrence_stream_reference(report["occurrence_stream"], result_root)
        summary = report["summary"]
        expected_summary = {
            "occurrence_count": verification["row_count"],
            "hard_fail_current_label_occurrence_count": verification[
                "hard_fail_current_label_occurrence_count"
            ],
            "unclassified_occurrence_count": verification["unclassified_occurrence_count"],
            "allowed_occurrence_count": verification["disposition_counts"].get("allowed", 0),
            "non_label_occurrence_count": verification["disposition_counts"].get("ignore_non_label", 0),
            "covered_by_existing_guard_count": verification["disposition_counts"].get(
                "covered_by_existing_guard", 0
            ),
        }
        for key, expected in expected_summary.items():
            if int(summary.get(key, -1)) != expected:
                raise ValueError(f"occurrence stream summary mismatch: {key}")
        expected_gate = (
            int(summary.get("manifest_error_count", -1)) == 0
            and verification["hard_fail_current_label_occurrence_count"] == 0
            and verification["unclassified_occurrence_count"] == 0
        )
        if bool(summary.get("gate_a_pass")) != expected_gate:
            raise ValueError("occurrence stream summary mismatch: gate_a_pass")
    output_root.mkdir(parents=True, exist_ok=True)
    writer = write_json_create_new if create_new else write_json
    writer(output_root / "occurrence_stream_reference.json", report["occurrence_stream"])
    writer(
        output_root / "occurrence_inventory_summary.json",
        {
            "schema_version": "legacy-active-silent-occurrence-inventory-summary-v1",
            "status": report["status"],
            "summary": report["summary"],
            "error_summary": report["error_summary"],
            "occurrence_stream": report["occurrence_stream"],
            "scan_receipt": report["scan_receipt"],
        },
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that legacy active/silent does not re-enter current Iris output surfaces."
    )
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--report", default=None)
    parser.add_argument("--inventory-root", default=None)
    parser.add_argument("--result-root", default=None)
    parser.add_argument("--work-root", default=None)
    parser.add_argument("--allocation-receipt", default=None)
    parser.add_argument("--output-policy", default=None)
    parser.add_argument("--scan-backend", choices=sorted(SCAN_BACKENDS), default="rg")
    parser.add_argument("--scan-timeout", type=int, default=60)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else DEFAULT_MANIFEST
    if not manifest_path.exists():
        print(
            f"default manifest not found: {manifest_path}. "
            "Generate the guard round first or pass --manifest.",
            file=sys.stderr,
        )
        return 2
    manifest = read_json(manifest_path.resolve())
    result_root = Path(args.result_root).resolve() if args.result_root else None
    persistent_output = bool(args.report or args.inventory_root or args.result_root)
    if args.result_root and not (args.report or args.inventory_root):
        print("--result-root requires --report or --inventory-root so the object cannot become dangling", file=sys.stderr)
        return 2
    if persistent_output and not (
        args.work_root and args.result_root and args.allocation_receipt and args.output_policy
    ):
        print(
            "--work-root, --result-root, --allocation-receipt, and --output-policy are required for persistent output",
            file=sys.stderr,
        )
        return 2
    if persistent_output:
        try:
            work_root, result_root = validate_external_run_roots(
                repo_root,
                Path(args.work_root),
                Path(args.result_root),
            )
            validate_allocation_receipt(
                repo_root,
                Path(args.allocation_receipt).resolve(),
                work_root,
                result_root,
            )
            validate_successor_output_policy(repo_root, Path(args.output_policy))
            report_path = (
                _authorized_output_path(result_root, Path(args.report), allowed_subroots={"logs"})
                if args.report
                else None
            )
            inventory_root = (
                _authorized_output_path(result_root, Path(args.inventory_root), allowed_subroots={"phases"})
                if args.inventory_root
                else None
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"persistent output authorization failed: {exc}", file=sys.stderr)
            return 2
    else:
        report_path = None
        inventory_root = None
    additional_excluded_paths = [path for path in (report_path, inventory_root) if path is not None]
    try:
        report = validate_repo(
            repo_root,
            manifest,
            scan_backend=args.scan_backend,
            scan_timeout=args.scan_timeout,
            result_root=result_root,
            additional_excluded_paths=additional_excluded_paths,
        )
        if persistent_output:
            policy_path = Path(args.output_policy).resolve()
            report["output_policy"] = {
                "path": repo_rel(policy_path, repo_root),
                "sha256": _sha256_file(policy_path),
            }
    except ScanBackendUnavailable as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "error_code": SCAN_BACKEND_UNAVAILABLE_ERROR_CODE,
                    "selected_backend": exc.backend,
                    "disposition": exc.disposition,
                    "detail": exc.detail,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    if report_path is not None:
        write_json_create_new(report_path, compact_report(report))
    if inventory_root is not None:
        write_inventory_files(report, inventory_root, result_root, create_new=True)
    print(json.dumps({"status": report["status"], "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
