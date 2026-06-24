from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import json
import sys
from typing import Any


NAMESPACE_TOKENS = (
    "LAYER4_ABSORPTION_CONFIRMED",
    "layer4_absorption_confirmed",
    "layer_boundary_hard_block_namespace",
)

UNAUTHORIZED_CONSUMPTION_ERROR_CODE = (
    "UNAUTHORIZED_LAYER4_ABSORPTION_CONFIRMED_CURRENT_SURFACE_CONSUMPTION"
)

TEXT_SUFFIXES = {".json", ".jsonl", ".lua", ".md", ".py", ".txt"}
SKIP_DIR_NAMES = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache"}

HARD_FAIL_PREFIXES = (
    "Iris/build/description/v2/data/",
    "Iris/build/description/v2/output/",
    "Iris/build/description/v2/tools/build/",
    "Iris/build/description/v2/tools/style/rules/",
    "Iris/build/package/Iris/media/lua/",
    "Iris/media/lua/client/Iris/Data/",
    "Iris/media/lua/client/Iris/UI/",
)

EXPLICIT_ALLOW_PATHS = {
    "Iris/build/description/v2/tools/build/build_dvf_3_3_round_a_round_b_parallel_execution.py": (
        "historical Round A/Round B predecessor evidence, not current production consumer"
    ),
}


@dataclass(frozen=True)
class Occurrence:
    path: str
    line: int
    column: int
    token: str
    surface_class: str
    disposition: str
    reason: str
    line_excerpt: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "token": self.token,
            "surface_class": self.surface_class,
            "disposition": self.disposition,
            "reason": self.reason,
            "line_excerpt": self.line_excerpt,
        }


def repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def iter_scan_files(repo_root: Path) -> list[Path]:
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
    return sorted(set(files), key=lambda item: repo_rel(item, repo_root).lower())


def classify_surface(rel_path: str) -> tuple[str, str, str]:
    if rel_path in EXPLICIT_ALLOW_PATHS:
        return "allowed_historical", "allowed", EXPLICIT_ALLOW_PATHS[rel_path]
    if rel_path.startswith("docs/"):
        return "governance_docs", "allowed", "governance/reference text is not current runtime or build consumption"
    if rel_path.startswith("Iris/build/description/v2/staging/"):
        return "staging_evidence", "allowed", "round-local and staging evidence is not current runtime or build consumption"
    if rel_path.startswith("Iris/_archive/"):
        return "archive_evidence", "allowed", "archived historical evidence is not current runtime or build consumption"
    if rel_path.startswith("Iris/build/description/v2/tests/"):
        return "test_fixture", "allowed", "tests may name the namespace to guard it"
    if any(rel_path.startswith(prefix) for prefix in HARD_FAIL_PREFIXES):
        return (
            "current_surface",
            "rejected",
            "namespace token entered a source/rendered/runtime/package/build current surface",
        )
    return "non_current_surface", "allowed", "not a guarded current application surface"


def scan_repo(repo_root: Path) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    for path in iter_scan_files(repo_root):
        text = read_text(path)
        if not any(token in text for token in NAMESPACE_TOKENS):
            continue
        rel_path = repo_rel(path, repo_root)
        surface_class, disposition, reason = classify_surface(rel_path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            for token in NAMESPACE_TOKENS:
                start = line.find(token)
                if start == -1:
                    continue
                occurrences.append(
                    Occurrence(
                        path=rel_path,
                        line=line_number,
                        column=start + 1,
                        token=token,
                        surface_class=surface_class,
                        disposition=disposition,
                        reason=reason,
                        line_excerpt=line.strip()[:200],
                    )
                )
    return occurrences


def build_report(repo_root: Path) -> dict[str, Any]:
    occurrences = scan_repo(repo_root)
    rejected = [item for item in occurrences if item.disposition == "rejected"]
    return {
        "schema_version": "layer4-absorption-current-surface-guard-v1",
        "status": "fail" if rejected else "pass",
        "error_code": UNAUTHORIZED_CONSUMPTION_ERROR_CODE if rejected else None,
        "summary": {
            "token_count": len(NAMESPACE_TOKENS),
            "occurrence_count": len(occurrences),
            "rejected_occurrence_count": len(rejected),
            "allowed_occurrence_count": len(occurrences) - len(rejected),
            "hard_fail_prefixes": list(HARD_FAIL_PREFIXES),
            "explicit_allow_path_count": len(EXPLICIT_ALLOW_PATHS),
        },
        "rejected_occurrences": [item.as_dict() for item in rejected],
        "occurrences": [item.as_dict() for item in occurrences],
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Guard against unauthorized LAYER4_ABSORPTION_CONFIRMED consumption "
            "in current source/rendered/runtime/build surfaces."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-json", type=Path)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the full occurrence list to stdout.",
    )
    args = parser.parse_args(argv)

    report = build_report(args.repo_root.resolve())
    if args.output_json is not None:
        write_json(args.output_json, report)
    elif args.verbose:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        summary = {
            "schema_version": report["schema_version"],
            "status": report["status"],
            "error_code": report["error_code"],
            "summary": report["summary"],
            "rejected_occurrences": report["rejected_occurrences"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
