from __future__ import annotations

from dvf_3_3_cutover_tooling_readiness_common import validate_diff_to_ledger


def main() -> int:
    report = validate_diff_to_ledger()
    return 0 if report.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
