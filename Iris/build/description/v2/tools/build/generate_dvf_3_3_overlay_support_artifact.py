from __future__ import annotations

from dvf_3_3_cutover_tooling_readiness_common import write_overlay_support


def main() -> int:
    report = write_overlay_support()
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
