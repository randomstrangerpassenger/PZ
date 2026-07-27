from __future__ import annotations

import json
from pathlib import Path
import sys


V2_ROOT = Path(__file__).resolve().parents[2]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.authority_phase11 import (
    run_authority_phase11,
)
from tools.build.dvf_3_3_food_semantic.contracts import FoodSemanticError


def main() -> int:
    try:
        result = run_authority_phase11()
    except (FoodSemanticError, OSError, ValueError, KeyError) as exc:
        print(
            json.dumps(
                {
                    "schema_version": (
                        "food-semantic-authority-phase11-runner-v1"
                    ),
                    "status": "BLOCKED",
                    "error": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
