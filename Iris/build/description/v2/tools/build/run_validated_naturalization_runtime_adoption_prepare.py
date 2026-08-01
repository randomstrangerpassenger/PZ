from __future__ import annotations

import argparse
import json
from pathlib import Path

from validated_naturalization_runtime_adoption import run_prepare_and_materialize


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--attempt-root", required=True, type=Path)
    args = parser.parse_args()
    result = run_prepare_and_materialize(args.repo, args.attempt_root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
