from __future__ import annotations

from Iris.validation.test_workflow_consolidation.validate_workflow_closeout_carrier import (
    ALLOWED_EVIDENCE_ROLES,
    EVIDENCE_ROOT,
    MANIFEST_PATH,
    POINTER_PATH,
    validate_carrier,
)


def _pointer(**extra: object) -> dict[str, object]:
    return {
        "schema_version": "iris_test_workflow_terminal_evidence_pointer_v1",
        "terminal_subject_commit": "terminal",
        "terminal_subject_tree": "terminal-tree",
        "retrieval_mode": "fresh-root-terminal-replay-v1",
        "external_retrieval_key": "bundle",
        "expected_terminal_filenames": [
            "terminal_validation_manifest.json",
            "accepted_paired_measurement_summary.json",
            "measurement_comparability_report.json",
            "independent_review.json",
            "owner_seal.json",
        ],
        **extra,
    }


def _manifest_entries() -> list[dict[str, str]]:
    return [
        {
            "path": EVIDENCE_ROOT + f"{role}.json",
            "role": role,
            "git_blob_id": "blob",
        }
        for role in ALLOWED_EVIDENCE_ROLES
    ] + [
        {
            "path": POINTER_PATH,
            "role": "terminal_evidence_pointer",
            "git_blob_id": "blob",
        }
    ]


def _fake_git(changed: list[str]):
    def run(_repo, *args):
        if args == ("rev-parse", "HEAD"):
            return "carrier"
        if args == ("rev-parse", "terminal"):
            return "terminal"
        if args == ("rev-parse", "terminal^{tree}"):
            return "terminal-tree"
        if args == ("rev-list", "--parents", "-n", "1", "carrier"):
            return "carrier terminal"
        if args == ("diff", "--name-only", "terminal", "carrier"):
            return "\n".join(changed)
        if len(args) == 2 and args[0] == "rev-parse" and args[1].startswith("carrier:"):
            return "blob"
        raise AssertionError(args)

    return run


def test_pointer_self_reference_is_rejected(monkeypatch, tmp_path) -> None:
    changed = [row["path"] for row in _manifest_entries()] + [MANIFEST_PATH]
    monkeypatch.setattr(
        "Iris.validation.test_workflow_consolidation.validate_workflow_closeout_carrier.git",
        _fake_git(changed),
    )
    report = validate_carrier(
        tmp_path,
        "terminal",
        _pointer(carrier_commit="carrier"),
        {
            "schema_version": "iris_test_workflow_closeout_carrier_manifest_v1",
            "entries": _manifest_entries(),
        },
    )
    assert report["status"] == "FAIL"


def test_manifest_cannot_allowlist_a_test_or_authority_path(monkeypatch, tmp_path) -> None:
    malicious = "Iris/build/description/v2/tests/test_malicious.py"
    entries = _manifest_entries() + [
        {"path": malicious, "role": "independent_review", "git_blob_id": "blob"}
    ]
    changed = [row["path"] for row in entries] + [MANIFEST_PATH]
    monkeypatch.setattr(
        "Iris.validation.test_workflow_consolidation.validate_workflow_closeout_carrier.git",
        _fake_git(changed),
    )
    report = validate_carrier(
        tmp_path,
        "terminal",
        _pointer(),
        {
            "schema_version": "iris_test_workflow_closeout_carrier_manifest_v1",
            "entries": entries,
        },
    )
    assert report["status"] == "FAIL"
    assert malicious in report["forbidden_paths"]


def test_manifest_entry_must_bind_the_committed_blob(monkeypatch, tmp_path) -> None:
    entries = _manifest_entries()
    entries[0]["git_blob_id"] = "stale"
    changed = [row["path"] for row in entries] + [MANIFEST_PATH]
    monkeypatch.setattr(
        "Iris.validation.test_workflow_consolidation.validate_workflow_closeout_carrier.git",
        _fake_git(changed),
    )
    report = validate_carrier(
        tmp_path,
        "terminal",
        _pointer(),
        {
            "schema_version": "iris_test_workflow_closeout_carrier_manifest_v1",
            "entries": entries,
        },
    )
    assert report["status"] == "FAIL"
    assert report["checks"]["manifest_entries_bind_committed_blobs"] is False
