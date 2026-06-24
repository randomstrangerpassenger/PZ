from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROUND3 = ROOT / "Iris" / "_docs" / "round3"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def signal_summary(signals: dict[str, object]) -> list[str]:
    names: list[str] = []
    if signals.get("in_current_closure"):
        names.append("current_closure")
    if signals.get("imported_by_non_current_tests_count", 0):
        names.append("non_current_test_import")
    if signals.get("imported_by_peer_scripts_count", 0):
        names.append("peer_import")
    if signals.get("doc_or_path_reference_count", 0):
        names.append("doc_or_path_reference")
    if signals.get("dynamic_import_signal"):
        names.append("dynamic_or_path_execution")
    if signals.get("artifact_path_signal"):
        names.append("artifact_path")
    return names


def disposition_for(row: dict[str, object]) -> tuple[str, str]:
    owner_class = str(row["owner_class"])
    signals = row["signals"]
    blockers = signal_summary(signals)  # type: ignore[arg-type]

    if owner_class == "current_build_core":
        return (
            "keep_current_core",
            "D2 limited approval: active current closure member; archive/delete forbidden.",
        )
    if owner_class == "historical_reproduction":
        return (
            "keep_historical_reproduction",
            "D2 limited approval: historical reproduction surface retained; "
            f"blocking signals={','.join(blockers) or 'none'}.",
        )
    if owner_class == "diagnostic_advisory":
        return (
            "keep_diagnostic_advisory",
            "D2 limited approval: diagnostic/advisory surface retained outside default "
            f"current route; blocking signals={','.join(blockers) or 'none'}.",
        )
    if owner_class == "manifest_only_candidate":
        return (
            "keep_manifest_only",
            "D2 limited approval: artifact-path-only candidate retained as manifest-only; "
            "not archive/delete eligible without separate proof.",
        )
    return (
        "keep_unresolved",
        "D2 limited approval: unresolved row retained; archive/delete forbidden.",
    )


def make_markdown(
    *,
    generated_at: str,
    rows: list[dict[str, object]],
    retained_rows: list[dict[str, object]],
    historical_run: dict[str, object],
    diagnostic_run: dict[str, object],
    current_run: dict[str, object],
    boundary_guard: dict[str, object],
) -> str:
    owner_counts = Counter(str(row["owner_class"]) for row in rows)
    disposition_counts = Counter(str(row["final_disposition"]) for row in rows)
    manifest_only = [
        row for row in rows if row["final_disposition"] == "keep_manifest_only"
    ]
    archive_count = sum(1 for row in rows if row["archive_eligible"])
    delete_count = sum(1 for row in rows if row["delete_eligible"])

    owner_lines = "\n".join(
        f"| {name} | {owner_counts[name]} |" for name in sorted(owner_counts)
    )
    disposition_lines = "\n".join(
        f"| {name} | {disposition_counts[name]} |"
        for name in sorted(disposition_counts)
    )
    manifest_lines = "\n".join(
        f"| `{row['path']}` | {row['reason']} |" for row in manifest_only
    )
    if not manifest_lines:
        manifest_lines = "| n/a | n/a |"

    return f"""# Round 3 Disposition Log

Generated: `{generated_at}`

## D2 Decision

```text
gate_id: D2
decision: approved_limited_non_destructive
approved_by: user in current Codex chat
timestamp: {generated_at}
allowed_scope: Change 5 disposition manifest/log/ledger only; keep/current/historical/diagnostic/manifest-only classification
blocked_scope: physical archive; delete; relocation; .gitignore edits; filename-glob cleanup
evidence_artifact: Iris/_docs/round3/round3_disposition_log.md
status: approved_limited
```

## Summary

| Metric | Count |
|---|---:|
| disposition rows | {len(rows)} |
| retained non-current rows | {len(retained_rows)} |
| archive eligible | {archive_count} |
| delete eligible | {delete_count} |
| archive/delete actions executed | 0 |

Owner classes:

| Owner Class | Count |
|---|---:|
{owner_lines}

Final dispositions:

| Final Disposition | Count |
|---|---:|
{disposition_lines}

Manifest-only retained rows:

| Path | Reason |
|---|---|
{manifest_lines}

## Route Evidence

| Route | Count | Success | Report |
|---|---:|---|---|
| current | {current_run.get('test_count')} | {current_run.get('success')} | `Iris/_docs/round3/round3_current_test_run.json` |
| historical | {historical_run.get('test_count')} | {historical_run.get('success')} | `Iris/_docs/round3/round3_historical_test_run.json` |
| diagnostic | {diagnostic_run.get('test_count')} | {diagnostic_run.get('success')} | `Iris/_docs/round3/round3_diagnostic_test_run.json` |
| boundary guard | n/a | {boundary_guard.get('success')} | `Iris/_docs/round3/round3_boundary_guard_report.json` |

## Invariant Result

No row is archive/delete eligible under D2. Every current-closure,
historical, diagnostic, doc/path-reference, artifact-path, peer-import,
test-import, dynamic/path-execution, or unresolved signal is retained.

Actual file movement, archive output, delete, or `.gitignore` disposition edit
is intentionally absent from this round.
"""


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    candidates = load_json(ROUND3 / "round3_disposition_candidates.json")
    artifact_manifest = load_json(ROUND3 / "round3_artifact_dependency_manifest.json")
    current_run = load_json(ROUND3 / "round3_current_test_run.json")
    historical_run = load_json(ROUND3 / "round3_historical_test_run.json")
    diagnostic_run = load_json(ROUND3 / "round3_diagnostic_test_run.json")
    boundary_guard = load_json(ROUND3 / "round3_boundary_guard_report.json")

    rows: list[dict[str, object]] = []
    for row in candidates["rows"]:  # type: ignore[index]
        updated = dict(row)
        final_disposition, reason = disposition_for(updated)
        updated["recommended_disposition"] = final_disposition
        updated["final_disposition"] = final_disposition
        updated["reason"] = reason
        updated["archive_eligible"] = False
        updated["delete_eligible"] = False
        rows.append(updated)

    retained_rows = [
        row for row in rows if row["final_disposition"] != "keep_current_core"
    ]
    archive_rows = [row for row in rows if row["archive_eligible"]]
    delete_rows = [row for row in rows if row["delete_eligible"]]
    artifact_by_path = {
        row["path"]: row for row in artifact_manifest["rows"]  # type: ignore[index]
    }

    disposition_manifest = {
        "schema_version": "round3-disposition-manifest-v1",
        "generated_at": generated_at,
        "d2_decision": "approved_limited_non_destructive",
        "approval_source": "user in current Codex chat",
        "allowed_scope": (
            "Change 5 disposition manifest/log/ledger only; no physical archive, "
            "delete, relocation, or .gitignore edits"
        ),
        "rows": rows,
    }
    updated_candidates = {
        **candidates,  # type: ignore[arg-type]
        "generated_at": generated_at,
        "d2_status": "approved_limited_non_destructive",
        "rows": rows,
        "invariants": {
            "archive_or_delete_executed": False,
            "filename_glob_archive_delete_used": False,
            "unresolved_marked_archive_or_delete": False,
            "archive_eligible_count": len(archive_rows),
            "delete_eligible_count": len(delete_rows),
        },
    }
    retained_manifest = {
        "schema_version": "round3-retained-script-manifest-v1",
        "generated_at": generated_at,
        "retained_non_current_count": len(retained_rows),
        "rows": [
            {
                "module": row["module"],
                "path": row["path"],
                "owner_class": row["owner_class"],
                "final_disposition": row["final_disposition"],
                "signals": row["signals"],
                "artifact_dependency": artifact_by_path.get(row["path"], {}),
            }
            for row in retained_rows
        ],
    }
    archive_ledger = {
        "schema_version": "round3-archive-ledger-v1",
        "generated_at": generated_at,
        "archive_or_delete_executed": False,
        "archive_actions": [],
        "delete_actions": [],
        "restore_instructions": (
            "No archive/delete action executed in Round 3 Change 5. "
            "Restore is not required."
        ),
    }
    invariant_report = {
        "schema_version": "round3-d2-invariant-report-v1",
        "generated_at": generated_at,
        "success": True,
        "row_count": len(rows),
        "retained_non_current_count": len(retained_rows),
        "archive_eligible_count": len(archive_rows),
        "delete_eligible_count": len(delete_rows),
        "violations": [],
        "route_evidence": {
            "current": current_run,
            "historical": historical_run,
            "diagnostic": diagnostic_run,
            "boundary_guard": boundary_guard,
        },
    }

    write_json(ROUND3 / "round3_disposition_candidates.json", updated_candidates)
    write_json(ROUND3 / "round3_disposition_manifest.json", disposition_manifest)
    write_json(ROUND3 / "round3_retained_historical_manifest.json", retained_manifest)
    write_json(ROUND3 / "round3_archive_ledger.json", archive_ledger)
    write_json(ROUND3 / "round3_d2_invariant_report.json", invariant_report)
    (ROUND3 / "round3_disposition_log.md").write_text(
        make_markdown(
            generated_at=generated_at,
            rows=rows,
            retained_rows=retained_rows,
            historical_run=historical_run,  # type: ignore[arg-type]
            diagnostic_run=diagnostic_run,  # type: ignore[arg-type]
            current_run=current_run,  # type: ignore[arg-type]
            boundary_guard=boundary_guard,  # type: ignore[arg-type]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "row_count": len(rows),
                "retained_non_current_count": len(retained_rows),
                "archive_eligible_count": len(archive_rows),
                "delete_eligible_count": len(delete_rows),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
