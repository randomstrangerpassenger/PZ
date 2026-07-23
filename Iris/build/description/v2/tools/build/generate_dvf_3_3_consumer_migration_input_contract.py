from __future__ import annotations

from dvf_3_3_consumer_migration_normalization_common import phase_path, read_json, write_phase0


def main() -> int:
    write_phase0()
    report = read_json(phase_path("phase0", "source_matrix_fingerprint_report.json"))
    membership = read_json(phase_path("phase0", "source_membership_reconciliation.json"))
    return 0 if report.get("status") == "PASS" and membership.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
