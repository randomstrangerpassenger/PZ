from __future__ import annotations

from dvf_3_3_cutover_tooling_readiness_common import write_row_level_ledger_generation_report


def main() -> int:
    report = write_row_level_ledger_generation_report()
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
