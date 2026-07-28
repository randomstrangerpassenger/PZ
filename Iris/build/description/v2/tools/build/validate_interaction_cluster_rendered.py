from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from postproc_ko import detect_ending_repetition, detect_josa_tokens


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"

DECISIONS_PATH = DATA_DIR / "dvf_3_3_decisions.jsonl"
RENDERED_PATH = OUTPUT_DIR / "dvf_3_3_rendered.json"
REPORT_PATH = OUTPUT_DIR / "interaction_cluster_validation_report.json"
FORBIDDEN_SUBSTRINGS = [": ", "· ", "1. ", "우클릭", "관련 레시피", "필요 재료"]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict]:
    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def validate_rendered(
    *,
    decisions_path: Path = DECISIONS_PATH,
    rendered_path: Path = RENDERED_PATH,
    report_path: Path = REPORT_PATH,
) -> dict:
    rendered = load_json(rendered_path)
    decisions = {entry["item_id"]: entry for entry in load_jsonl(decisions_path)}

    hard_fail_rows: list[str] = []
    warn_rows: list[str] = []
    rows: list[dict] = []

    for item_id, entry in rendered["entries"].items():
        text = entry["text_ko"]
        if text is None:
            continue

        hard_fail_reasons = [reason for reason in decisions[item_id].get("hard_fail_codes", [])]
        for forbidden in FORBIDDEN_SUBSTRINGS:
            if forbidden in text:
                hard_fail_reasons.append(f"forbidden_substring:{forbidden}")

        warnings: list[str] = []
        if decisions[item_id].get("v9_warn"):
            warnings.append("v9_warn")
        warnings.extend(detect_ending_repetition(text))
        warnings.extend(detect_josa_tokens(text))

        if hard_fail_reasons:
            hard_fail_rows.append(item_id)
        if warnings:
            warn_rows.append(item_id)

        rows.append({
            "item_id": item_id,
            "text_ko": text,
            "hard_fail_reasons": hard_fail_reasons,
            "warnings": warnings
        })

    payload = {
        "schema_version": "interaction-cluster-validation-report-v0",
        "hard_fail_count": len(hard_fail_rows),
        "warn_count": len(warn_rows),
        "hard_fail_rows": hard_fail_rows,
        "warn_rows": warn_rows,
        "rows": rows
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate rendered DVF 3-3 text output.")
    parser.add_argument("--decisions-path", type=Path, default=DECISIONS_PATH)
    parser.add_argument("--rendered-path", type=Path, default=RENDERED_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = validate_rendered(
        decisions_path=args.decisions_path,
        rendered_path=args.rendered_path,
        report_path=args.report_path,
    )

    if payload["hard_fail_rows"]:
        print("interaction cluster rendered validation FAILED", file=sys.stderr)
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print("interaction cluster rendered validation OK")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
