from __future__ import annotations

import argparse
import json

import public_text_quality_acceptance_official_0005_phase7_long_path_writer as correction


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()
    result = correction.run_self_test()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
