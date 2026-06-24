from __future__ import annotations

import argparse

from _dvf_3_3_vnext_common import classify_delta, write_json, write_jsonl, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify DVF 3-3 predecessor-to-successor delta.")
    parser.add_argument("--predecessor-manifest", required=True)
    parser.add_argument("--predecessor-chunk-dir", required=True)
    parser.add_argument("--successor-manifest", required=True)
    parser.add_argument("--successor-chunk-dir", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--facts", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--compose-binding", required=True)
    parser.add_argument("--rendered", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary-output", required=True)
    parser.add_argument("--unexplained-output", required=True)
    parser.add_argument("--metrics-output", required=True)
    args = parser.parse_args()

    rows, summary, unexplained_report, metrics, ok = classify_delta(
        args.predecessor_manifest,
        args.predecessor_chunk_dir,
        args.successor_manifest,
        args.successor_chunk_dir,
    )
    write_jsonl(args.output, rows)
    write_json(args.summary_output, summary)
    write_text(args.unexplained_output, unexplained_report)
    write_json(args.metrics_output, metrics)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

