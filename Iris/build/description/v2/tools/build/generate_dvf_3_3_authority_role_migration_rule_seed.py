from __future__ import annotations

from dvf_3_3_consumer_migration_normalization_common import phase_path, read_json, write_phase4


def main() -> int:
    write_phase4()
    summary = read_json(phase_path("phase4", "authority_role_rule_seed_summary.json"))
    coverage = read_json(phase_path("phase4", "rule_seed_coverage.json"))
    return 0 if summary.get("status") == "PASS" and coverage.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
