from __future__ import annotations

from dvf_3_3_consumer_migration_normalization_common import phase_path, read_json, write_phase1


def main() -> int:
    write_phase1()
    summary = read_json(phase_path("phase1", "eligibility_matrix_summary.json"))
    return 0 if summary.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
