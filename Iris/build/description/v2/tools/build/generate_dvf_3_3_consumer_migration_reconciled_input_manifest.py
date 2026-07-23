from __future__ import annotations

from dvf_3_3_consumer_migration_normalization_common import phase_path, read_json, write_phase6


def main() -> int:
    write_phase6()
    manifest = read_json(phase_path("phase6", "consumer_migration_reconciled_input_manifest.json"))
    validation = read_json(phase_path("phase6", "reconciled_input_manifest_validation_report.json"))
    return 0 if manifest.get("verdict") == "PASS" and validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
