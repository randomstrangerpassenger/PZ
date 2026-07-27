from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


V2_ROOT = Path(__file__).resolve().parents[2]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.authority_phase9_10 import (
    run_authority_phase9_10,
)
from tools.build.dvf_3_3_food_semantic.contracts import (
    FoodSemanticError,
    repo_root,
)


ATTEMPT_ROOT = Path(
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0007"
)
AUTHORITY_ROOT = ATTEMPT_ROOT / (
    "post_implementation_authority/authority-execution-0002"
)
def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Execute reviewed DVF 3.3 food semantic Phase 9 coverage and "
            "Phase 10 attempt-local authority candidate generation."
        )
    )
    parser.add_argument(
        "--authority-root",
        type=Path,
        default=AUTHORITY_ROOT,
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=AUTHORITY_ROOT,
    )
    args = parser.parse_args()
    root = repo_root()
    attempt_root = root / ATTEMPT_ROOT
    try:
        report = run_authority_phase9_10(
            root,
            attempt_root,
            _resolve(root, args.authority_root),
            output_root=_resolve(root, args.output_root),
        )
    except (FoodSemanticError, FileNotFoundError, KeyError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "BLOCKED", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
