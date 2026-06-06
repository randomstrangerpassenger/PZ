from __future__ import annotations

import argparse
from dataclasses import dataclass
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
import subprocess
import sys
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


def iter_scan_files(repo_root: Path) -> list[Path]:
    rg_files = iter_scan_files_with_rg(repo_root)
    if rg_files is not None:
        return rg_files

    files: list[Path] = []
    for root_name in ("Iris", "docs"):
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if set(path.parts) & SKIP_DIR_NAMES:
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            files.append(path)
    return sorted(set(files), key=lambda item: repo_rel(item, repo_root))


def iter_scan_files_with_rg(repo_root: Path) -> list[Path] | None:
    command = [
        "rg",
        "-l",
        "-i",
        r"active|silent|active_count|silent_count",
        "--glob",
        "*.json",
        "--glob",
        "*.jsonl",
        "--glob",
        "*.lua",
        "--glob",
        "*.md",
        "--glob",
        "*.py",
        "--glob",
        "*.txt",
        "Iris",
        "docs",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if completed.returncode not in {0, 1}:
        return None
    paths = []
    for line in completed.stdout.splitlines():
        if not line.strip():
            continue
        path = repo_root / line.strip()
        if not path.is_file():
            continue
        if set(path.parts) & SKIP_DIR_NAMES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        paths.append(path)
    return sorted(set(paths), key=lambda item: repo_rel(item, repo_root))


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

    round_root = str(manifest.get("round_root", "")).replace("\\", "/")
    if round_root and normalize_rel(path).startswith(normalize_rel(round_root).rstrip("/") + "/"):
        return "allow"

    if pattern_matches(
        path,
        [
            "docs/**",
            "Iris/_archive/**",
            "Iris/_docs/**",
            "Iris/build/description/v2/staging/**",
            "Iris/output/**",
            "Iris/build/description/v2/tests/**",
            "Iris/build/description/v2/tools/build/**/*.py",
            "Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py",
            "Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py",
        ],
    ):
        return "allow"

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
    if pattern_matches(path, ["Iris/build/description/v2/tools/build/**/*.py"]):
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
                disposition = "ignore_non_label" if not current_label_candidate else "allowed"
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
    return errors


def scan_repo(repo_root: Path, manifest: dict[str, Any]) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    round_root = normalize_rel(str(manifest.get("round_root", ""))).rstrip("/")
    for path in iter_scan_files(repo_root):
        rel_path = repo_rel(path, repo_root)
        if round_root and normalize_rel(rel_path).startswith(round_root + "/"):
            continue
        occurrences.extend(scan_path(path, repo_root, manifest))
    return sorted(occurrences, key=lambda item: (item.path, item.line, item.column, item.token))


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


def validate_repo(repo_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_errors = validate_manifest(manifest)
    occurrences = scan_repo(repo_root, manifest)
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
    return {
        "schema_version": "legacy-active-silent-current-surface-guard-report-v0",
        "status": "pass" if summary["gate_a_pass"] else "fail",
        "error_catalog": ERROR_CATALOG,
        "summary": summary,
        "errors": errors,
        "occurrences": [item.as_dict() for item in occurrences],
    }


def write_inventory_files(report: dict[str, Any], output_root: Path) -> None:
    occurrences = list(report.get("occurrences", []))
    current_candidates = [item for item in occurrences if item.get("current_label_candidate")]
    allowed = [item for item in occurrences if item.get("disposition") in {"allowed", "ignore_non_label"}]
    unclassified = [
        item
        for item in occurrences
        if item.get("disposition") == "blocked_unclassified"
        or item.get("error_code")
        in {
            UNALLOWLISTED_ERROR_CODE,
            DIAGNOSTIC_ALIAS_OUTSIDE_ERROR_CODE,
            LEGACY_METRIC_RENDERED_ERROR_CODE,
        }
    ]
    output_root.mkdir(parents=True, exist_ok=True)
    with (output_root / "legacy_active_silent_occurrence_inventory.jsonl").open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for item in occurrences:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    write_json(output_root / "current_label_candidate_inventory.json", {"occurrences": current_candidates})
    write_json(output_root / "allowed_occurrence_inventory.json", {"occurrences": allowed})
    write_json(output_root / "unclassified_occurrence_inventory.json", {"occurrences": unclassified})


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that legacy active/silent does not re-enter current Iris output surfaces."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--report", default=None)
    parser.add_argument("--inventory-root", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    manifest = read_json(Path(args.manifest).resolve())
    report = validate_repo(repo_root, manifest)
    if args.report:
        write_json(Path(args.report), report)
    if args.inventory_root:
        write_inventory_files(report, Path(args.inventory_root))
    print(json.dumps({"status": report["status"], "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
