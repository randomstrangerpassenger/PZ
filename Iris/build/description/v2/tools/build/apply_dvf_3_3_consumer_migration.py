from __future__ import annotations

from dvf_3_3_cutover_tooling_readiness_common import write_consumer_migration_readiness, read_json, phase_path


def main() -> int:
    write_consumer_migration_readiness()
    report = read_json(phase_path("phase3", "consumer_migration_actual_report.json"))
    preflight = read_json(phase_path("phase3", "consumer_migration_materialization_preflight_report.json"))
    return 0 if report.get("status") == "PASS" and preflight.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
