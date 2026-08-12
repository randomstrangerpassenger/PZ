from __future__ import annotations

from pathlib import Path

from Iris.validation.test_workflow_consolidation._common import sha256_bytes, write_jsonl
from Iris.validation.test_workflow_consolidation.validate_measurement_comparability import (
    allowed_path,
    classify_changed_rows,
    contract_map_valid,
)


def test_touch_surface_is_fail_closed() -> None:
    surface = {
        "entries": [
            {"kind": "exact", "path": "docs/plan.md", "role": "plan_infrastructure"},
            {"kind": "prefix", "path": "Iris/validation/successor", "role": "application"},
        ]
    }
    assert allowed_path("docs/plan.md", surface) == (True, "plan_infrastructure")
    assert allowed_path("Iris/validation/successor/tool.py", surface) == (True, "application")
    assert allowed_path("Iris/media/lua/client/Iris/IrisMain.lua", surface) == (False, None)
    rename = classify_changed_rows(
        [
            {
                "status": "R100",
                "source_path": "Iris/media/lua/client/Iris/IrisMain.lua",
                "path": "Iris/validation/successor/IrisMain.lua",
            }
        ],
        surface,
    )
    assert rename[0]["allowed"] is False


def test_contract_map_requires_localization_and_successor_probe(tmp_path: Path) -> None:
    path = tmp_path / "mapping.jsonl"
    write_jsonl(
        path,
        [
            {
                "record_type": "manifest",
                "expected_predecessor_count": 1,
                "predecessor_id_sha256": sha256_bytes(b"old.test\n"),
            },
            {
                "record_type": "mapping",
                "predecessor_test_id": "old.test",
                "successor_probe_ids": ["probe"],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            }
        ],
    )
    assert contract_map_valid(path)
    write_jsonl(
        path,
        [
            {
                "record_type": "manifest",
                "expected_predecessor_count": 1,
                "predecessor_id_sha256": sha256_bytes(b"old.test\n"),
            },
            {
                "record_type": "mapping",
                "predecessor_test_id": "old.test",
                "successor_probe_ids": [],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            }
        ],
    )
    assert not contract_map_valid(path)


def test_contract_map_rejects_incomplete_denominator_manifest(tmp_path: Path) -> None:
    path = tmp_path / "mapping.jsonl"
    write_jsonl(
        path,
        [
            {
                "record_type": "manifest",
                "expected_predecessor_count": 2,
                "predecessor_id_sha256": sha256_bytes(b"old.test\nother.test\n"),
            },
            {
                "record_type": "mapping",
                "predecessor_test_id": "old.test",
                "successor_probe_ids": ["probe"],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            },
        ],
    )
    assert not contract_map_valid(path)
