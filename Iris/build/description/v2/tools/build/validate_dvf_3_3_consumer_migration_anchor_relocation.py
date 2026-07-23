from __future__ import annotations

from dvf_3_3_consumer_migration_normalization_common import phase_path, read_json, write_phase3


def main() -> int:
    write_phase3()
    report = read_json(phase_path("phase3", "anchor_relocation_validation_report.json"))
    freshness = read_json(phase_path("phase3", "anchor_freshness_binding_report.json"))
    return 0 if report.get("status") == "PASS" and freshness.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
