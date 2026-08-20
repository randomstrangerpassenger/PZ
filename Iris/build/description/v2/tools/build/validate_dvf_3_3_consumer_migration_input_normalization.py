from __future__ import annotations

import argparse
import json

from dvf_3_3_consumer_migration_normalization_common import (
    anchor_relocation_for_text,
    registry_responsibility_axis_anchor,
    terminal_disposition_for,
    write_phase7_and_phase8,
)


def negative_helper_probe_payload() -> dict:
    disposition, blocked_class, blocked_reason = terminal_disposition_for(
        {
            "migration_disposition": "unexpected",
            "disposition": "unknown",
            "consumer_type": "validator-gate",
        }
    )
    ambiguous = anchor_relocation_for_text(
        ["x 21", "middle", "y 21"],
        2,
        "21",
        allow_tie_break=False,
    )
    deterministic = anchor_relocation_for_text(
        ["x 21", "middle", "y 21"],
        2,
        "21",
    )
    architecture_responsibility = registry_responsibility_axis_anchor(
        [
            "header",
            "* Source authority 변경은 reviewed Git-authored source diff와 해당 owner 경계가 담당한다. Derived Layer 3 runtime은 stateless complete-generation contract가 생산·검증하며 descriptor 자체는 authority/adoption token이 아니다.",
        ],
        {
            "path": "docs/ARCHITECTURE.md",
            "token": "2105",
            "referent": "current-readpoint-triple",
            "authority_role_target": "successor_baseline_manifest_authority",
        },
    )
    roadmap_responsibility = registry_responsibility_axis_anchor(
        [
            "header",
            "* Iris Artifact Registry는 source / rendered / runtime / package identity와 artifact lifecycle, validation, seal, cutover, stale reentry guard, runtime compatibility를 관리한다.",
        ],
        {
            "path": "docs/ROADMAP.md",
            "token": "2084",
            "referent": "current-readpoint-triple",
            "authority_role_target": "successor_baseline_manifest_authority",
        },
    )
    architecture_line = "* Source authority 변경은 reviewed Git-authored source diff와 해당 owner 경계가 담당한다. Derived Layer 3 runtime은 stateless complete-generation contract가 생산·검증하며 descriptor 자체는 authority/adoption token이 아니다."
    responsibility_negative_anchors = {
        "cross_pair": registry_responsibility_axis_anchor(
            [architecture_line],
            {"path": "docs/ARCHITECTURE.md", "token": "2084", "referent": "current-readpoint-triple", "authority_role_target": "successor_baseline_manifest_authority"},
        ),
        "wrong_path": registry_responsibility_axis_anchor(
            [architecture_line],
            {"path": "docs/DECISIONS.md", "token": "2105", "referent": "current-readpoint-triple", "authority_role_target": "successor_baseline_manifest_authority"},
        ),
        "wrong_token": registry_responsibility_axis_anchor(
            [architecture_line],
            {"path": "docs/ARCHITECTURE.md", "token": "9999", "referent": "current-readpoint-triple", "authority_role_target": "successor_baseline_manifest_authority"},
        ),
        "wrong_referent": registry_responsibility_axis_anchor(
            [architecture_line],
            {"path": "docs/ARCHITECTURE.md", "token": "2105", "referent": "other", "authority_role_target": "successor_baseline_manifest_authority"},
        ),
        "wrong_role": registry_responsibility_axis_anchor(
            [architecture_line],
            {"path": "docs/ARCHITECTURE.md", "token": "2105", "referent": "current-readpoint-triple", "authority_role_target": "other"},
        ),
        "duplicate_sentence": registry_responsibility_axis_anchor(
            [architecture_line, architecture_line],
            {"path": "docs/ARCHITECTURE.md", "token": "2105", "referent": "current-readpoint-triple", "authority_role_target": "successor_baseline_manifest_authority"},
        ),
        "semantic_mutation": registry_responsibility_axis_anchor(
            ["* Source authority 변경은 unreviewed input이 담당한다. Derived Layer 3 runtime은 descriptor authority가 생산한다."],
            {"path": "docs/ARCHITECTURE.md", "token": "2105", "referent": "current-readpoint-triple", "authority_role_target": "successor_baseline_manifest_authority"},
        ),
    }
    status = (
        "PASS"
        if (
            disposition == "blocked"
            and blocked_class == "blocked_non_apply"
            and blocked_reason == "unknown_terminal_disposition"
            and ambiguous.get("result") == "ambiguous"
            and deterministic.get("result") == "relocated_deterministically"
            and deterministic.get("basis")
            == "nearest_tie_lowest_line_deterministic"
            and architecture_responsibility
            == {
                "result": "relocated_deterministically",
                "candidate_count": 1,
                "anchor_line": 2,
                "basis": "successor_registry_responsibility_axis_replaces_stale_numeric_anchor",
            }
            and roadmap_responsibility
            == {
                "result": "relocated_deterministically",
                "candidate_count": 1,
                "anchor_line": 2,
                "basis": "successor_registry_responsibility_axis_replaces_stale_numeric_anchor",
            }
            and all(value is None for value in responsibility_negative_anchors.values())
        )
        else "FAIL"
    )
    return {
        "schema_version": "dvf-3-3-consumer-migration-negative-helper-probe-v1",
        "status": status,
        "terminal_disposition": disposition,
        "blocked_class": blocked_class,
        "blocked_reason": blocked_reason,
        "ambiguous_anchor": ambiguous,
        "deterministic_anchor": deterministic,
        "architecture_responsibility_anchor": architecture_responsibility,
        "roadmap_responsibility_anchor": roadmap_responsibility,
        "responsibility_negative_anchors": responsibility_negative_anchors,
        "writes_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-negative-helpers", action="store_true")
    args = parser.parse_args(argv)
    if args.probe_negative_helpers:
        payload = negative_helper_probe_payload()
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1
    report = write_phase7_and_phase8()
    return 0 if report.get("machine_contract_status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
