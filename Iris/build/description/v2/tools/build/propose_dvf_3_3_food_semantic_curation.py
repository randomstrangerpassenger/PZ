from __future__ import annotations

import argparse
import json
from pathlib import Path

from dvf_3_3_food_semantic.contracts import repo_root
from dvf_3_3_food_semantic.curation_proposals import (
    write_curation_proposal_bundle,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Build non-authoritative AI-assisted curation review packets."
    )
    result.add_argument("--attempt-id", default="attempt-0007")
    result.add_argument(
        "--output-root",
        type=Path,
        default=Path(
            "Iris/build/description/v2/owner_inputs/"
            "dvf_3_3_food_semantic_facts_authority/curation_proposals"
        ),
    )
    return result


def main() -> int:
    args = parser().parse_args()
    root = repo_root()
    attempt_root = (
        root
        / "Iris/build/description/v2/staging/"
        "dvf_3_3_food_semantic_facts_authority/attempts"
        / args.attempt_id
    )
    output_root = args.output_root
    if not output_root.is_absolute():
        output_root = root / output_root
    report = write_curation_proposal_bundle(root, attempt_root, output_root)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
