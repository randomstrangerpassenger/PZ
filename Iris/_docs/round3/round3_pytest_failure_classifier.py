"""Classify advisory full-suite failures without weakening current ownership."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


PRIORITY = {
    "diagnostic": 1,
    "historical": 2,
    "unknown": 3,
    "excluded-contract-drift": 4,
    "current": 5,
    "modified": 6,
    "mandatory": 7,
}
IN_SCOPE_CLASSES = {"mandatory", "modified", "current", "unknown", "excluded-contract-drift"}
REPO_ROOT = Path(__file__).resolve().parents[3]


def source_from_nodeid(nodeid: str) -> str | None:
    source = nodeid.split("::", 1)[0].replace("\\", "/")
    return source if source.endswith(".py") else None


def classify_failure(
    failure: dict[str, Any],
    *,
    source_classes: dict[str, str],
    mixed_sources: set[str],
    modified_paths: set[str],
    mandatory_test_ids: set[str],
    mandatory_paths: set[str] | None = None,
) -> str:
    return classify_failure_with_basis(
        failure,
        source_classes=source_classes,
        mixed_sources=mixed_sources,
        modified_paths=modified_paths,
        mandatory_test_ids=mandatory_test_ids,
        mandatory_paths=mandatory_paths,
    )[0]


def classify_failure_with_basis(
    failure: dict[str, Any],
    *,
    source_classes: dict[str, str],
    mixed_sources: set[str],
    modified_paths: set[str],
    mandatory_test_ids: set[str],
    mandatory_paths: set[str] | None = None,
) -> tuple[str, dict[str, Any]]:
    nodeid = str(failure.get("nodeid", ""))
    source = str(failure.get("source_file") or source_from_nodeid(nodeid) or "")
    test_id = failure.get("test_id")
    dependency_paths = {
        str(path).replace("\\", "/")
        for path in failure.get("dependency_paths", [])
        if str(path)
    }
    affected_paths = dependency_paths | ({source} if source else set())
    mandatory_path_matches = sorted(affected_paths & set(mandatory_paths or set()))
    modified_path_matches = sorted(affected_paths & modified_paths)
    if test_id in mandatory_test_ids or nodeid in mandatory_test_ids:
        return "mandatory", {
            "rule": "mandatory_test_id",
            "matched_test_ids": [str(test_id or nodeid)],
            "affected_paths": sorted(affected_paths),
        }
    if mandatory_path_matches:
        return "mandatory", {
            "rule": "mandatory_dependency_path",
            "matched_paths": mandatory_path_matches,
            "affected_paths": sorted(affected_paths),
        }
    if modified_path_matches:
        return "modified", {
            "rule": "modified_source_or_dependency_path",
            "matched_paths": modified_path_matches,
            "affected_paths": sorted(affected_paths),
        }
    if failure.get("source_level") and source in mixed_sources:
        return "unknown", {
            "rule": "mixed_source_collection_error",
            "affected_paths": sorted(affected_paths),
        }
    classification = source_classes.get(source)
    if classification == "excluded":
        return "excluded-contract-drift", {
            "rule": "excluded_source_failure",
            "source_file": source,
            "affected_paths": sorted(affected_paths),
        }
    if classification in {"current", "historical", "diagnostic"}:
        return classification, {
            "rule": "source_policy_classification",
            "source_file": source,
            "source_classification": classification,
            "modified_path_matches": [],
            "mandatory_path_matches": [],
            "affected_paths": sorted(affected_paths),
        }
    return "unknown", {
        "rule": "unclassified_source_or_dependency",
        "source_file": source,
        "affected_paths": sorted(affected_paths),
    }


def classify_report(
    failures: Iterable[dict[str, Any]],
    *,
    source_classes: dict[str, str],
    mixed_sources: set[str],
    modified_paths: set[str],
    mandatory_test_ids: set[str],
    mandatory_paths: set[str] | None = None,
    requested_downgrades: dict[str, str] | None = None,
) -> dict[str, Any]:
    rows = []
    for failure in failures:
        classification, basis = classify_failure_with_basis(
            failure,
            source_classes=source_classes,
            mixed_sources=mixed_sources,
            modified_paths=modified_paths,
            mandatory_test_ids=mandatory_test_ids,
            mandatory_paths=mandatory_paths,
        )
        requested = (requested_downgrades or {}).get(str(failure.get("nodeid", "")))
        if requested is not None and PRIORITY.get(requested, -1) < PRIORITY[classification]:
            raise ValueError(
                f"Manual downgrade is forbidden: {classification} -> {requested} "
                f"for {failure.get('nodeid')}"
            )
        if requested is not None and PRIORITY.get(requested, -1) >= PRIORITY[classification]:
            classification = requested
        rows.append({
            **failure,
            "classification": classification,
            "classification_basis": basis,
        })
    blocking = any(row["classification"] in IN_SCOPE_CLASSES for row in rows)
    return {
        "schema_version": "round3-pytest-failure-classification-v1",
        "failures": rows,
        "scoped_status": "unvalidated_but_in_scope" if blocking else "out_of_scope",
        "configured_full_suite_pass": False,
    }


def _run_git(*arguments: str) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Git evidence query failed: "
            + result.stderr.decode("utf-8", errors="replace")
        )
    return result.stdout


def _canonical_repo_path(value: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe repository-relative classifier path: {value}")
    normalized = candidate.as_posix()
    if normalized != value:
        raise ValueError(f"non-canonical classifier path: {value}")
    return normalized


def expand_cli_evidence(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    expanded = dict(payload)
    modified_subject = dict(payload.get("modified_subject", {}))
    base = str(modified_subject.get("base_commit", ""))
    endpoint = str(modified_subject.get("endpoint", ""))
    diff_arguments: tuple[str, ...] | None = None
    if base:
        if endpoint and endpoint != "implementation_worktree":
            diff_arguments = ("diff", "--name-only", base, endpoint, "--")
        else:
            diff_arguments = ("diff", "--name-only", base, "--")
        changed = _run_git(*diff_arguments).decode("utf-8")
        modified_paths = {
            _canonical_repo_path(path)
            for path in changed.splitlines()
            if path
        }
    else:
        modified_paths = set(payload.get("modified_paths", []))
    expanded["modified_paths"] = sorted(modified_paths)

    failures = []
    dependency_bindings = []
    for original in payload.get("failures", []):
        failure = dict(original)
        manifest_path = failure.pop("dependency_manifest", None)
        manifest_commit = failure.pop("dependency_manifest_commit", None)
        if manifest_path is not None:
            path = _canonical_repo_path(str(manifest_path))
            if not manifest_commit:
                raise ValueError(f"dependency manifest commit is required: {path}")
            manifest = json.loads(
                _run_git("show", f"{manifest_commit}:{path}").decode("utf-8")
            )
            artifacts = manifest.get("artifacts", [])
            dependency_paths = [
                _canonical_repo_path(str(row["path"]))
                for row in artifacts
            ]
            failure["dependency_paths"] = dependency_paths
            binding = {
                "path": path,
                "commit": manifest_commit,
                "artifact_count": manifest.get("artifact_count"),
                "aggregate_sha256": manifest.get("aggregate_sha256"),
            }
            failure["dependency_manifest_binding"] = binding
            dependency_bindings.append(binding)
        failures.append(failure)
    expanded["failures"] = failures
    basis = {
        "modified_subject": modified_subject,
        "modified_diff_arguments": list(diff_arguments or ()),
        "modified_path_count": len(modified_paths),
        "mandatory_test_id_count": len(payload.get("mandatory_test_ids", [])),
        "mandatory_path_count": len(payload.get("mandatory_paths", [])),
        "dependency_manifests": dependency_bindings,
        "source_policy": payload.get("source_policy"),
    }
    return expanded, basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    payload, input_basis = expand_cli_evidence(payload)
    result = classify_report(
        payload.get("failures", []),
        source_classes=dict(payload.get("source_classes", {})),
        mixed_sources=set(payload.get("mixed_sources", [])),
        modified_paths=set(payload.get("modified_paths", [])),
        mandatory_test_ids=set(payload.get("mandatory_test_ids", [])),
        mandatory_paths=set(payload.get("mandatory_paths", [])),
        requested_downgrades=dict(payload.get("requested_downgrades", {})),
    )
    result["input_basis"] = input_basis
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
