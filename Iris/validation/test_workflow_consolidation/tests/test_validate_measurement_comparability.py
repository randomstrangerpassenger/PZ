from __future__ import annotations

from pathlib import Path

from Iris.validation.test_workflow_consolidation._common import write_jsonl
from Iris.validation.test_workflow_consolidation.validate_measurement_comparability import (
    allowed_path,
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


def test_contract_map_requires_localization_and_successor_probe(tmp_path: Path) -> None:
    path = tmp_path / "mapping.jsonl"
    write_jsonl(
        path,
        [
            {
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
                "predecessor_test_id": "old.test",
                "successor_probe_ids": [],
                "mapping_status": "preserved",
                "failure_localization_preserved": True,
            }
        ],
    )
    assert not contract_map_valid(path)
