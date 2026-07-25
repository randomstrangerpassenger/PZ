#!/usr/bin/env python3
"""Export lossless Registry Runtime Compatibility records for Windows Route C."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence


V2_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[6]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc
from tools.build import validate_dvf_3_3_registry_runtime_compatibility as validator


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise rtc.CompatibilityError(
            "record_export_input_not_object",
            f"Expected JSON object: {path}",
        )
    return value


def surface_records(manifest: dict[str, Any]) -> dict[str, list[rtc.SurfaceRecord]]:
    source_row = manifest["source"]
    source, _ = rtc.load_jsonl_surface(
        {
            component: Path(source_row[component]).resolve()
            for component in ("facts", "decisions", "overlay")
        },
        repo=REPO_ROOT,
    )
    rendered = rtc.load_rendered_surface(
        Path(manifest["rendered"]["path"]).resolve(),
        repo=REPO_ROOT,
    )
    runtime, _ = rtc.load_lua_surface(
        surface="runtime",
        manifest_path=Path(manifest["runtime"]["manifest"]).resolve(),
        chunk_dir=Path(manifest["runtime"]["chunks"]).resolve(),
        repo=REPO_ROOT,
    )
    package, _ = rtc.load_lua_surface(
        surface="package",
        manifest_path=Path(manifest["package"]["manifest"]).resolve(),
        chunk_dir=Path(manifest["package"]["chunks"]).resolve(),
        repo=REPO_ROOT,
    )
    return {
        "source": source,
        "rendered": rendered,
        "runtime": runtime,
        "package": package,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface-input-manifest", required=True)
    parser.add_argument(
        "--policy-context",
        choices=("candidate", "canonical_durable"),
        required=True,
    )
    parser.add_argument("--policy", required=True)
    parser.add_argument("--disposition", required=True)
    parser.add_argument("--binding-manifest", required=True)
    parser.add_argument("--records-out", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)
    try:
        manifest_path = Path(args.surface_input_manifest).resolve()
        manifest = read_json(manifest_path)
        binding = validator.validate_binding_contract(
            policy_context=args.policy_context,
            policy_path=Path(args.policy).resolve(),
            disposition_path=Path(args.disposition).resolve(),
            binding_path=Path(args.binding_manifest).resolve(),
        )
        if manifest.get("binding_manifest_sha256") != binding[
            "binding_manifest_sha256"
        ]:
            raise rtc.CompatibilityError(
                "record_export_binding_hash_mismatch",
                "Surface manifest and selected binding differ",
            )
        surfaces = surface_records(manifest)
        records_path = Path(args.records_out).resolve()
        records_path.parent.mkdir(parents=True, exist_ok=True)
        with records_path.open("wb") as handle:
            for surface in ("source", "rendered", "runtime", "package"):
                for record in surfaces[surface]:
                    projection = rtc.identity_projection(record)
                    projection["payload_sha256"] = rtc.payload_hash(record.payload)
                    handle.write(rtc.canonical_json_bytes(projection))
        report = {
            "schema_version": "rtc-windows-record-export-report-v1",
            "round_id": rtc.ROUND_ID,
            "status": "PASS",
            "route": "windows_record_sidecar",
            "algorithm_authority": "canonical_analyzer",
            "surface_input_manifest_sha256": rtc.sha256_file(manifest_path),
            "binding_manifest_sha256": binding["binding_manifest_sha256"],
            "surface_record_counts": {
                surface: len(rows) for surface, rows in surfaces.items()
            },
            "record_count": sum(len(rows) for rows in surfaces.values()),
            "records_path": str(records_path),
            "records_sha256": rtc.sha256_file(records_path),
            "records_byte_count": records_path.stat().st_size,
        }
        rtc.write_json(Path(args.report_out).resolve(), report)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    except rtc.CompatibilityError as exc:
        print(
            json.dumps(
                {
                    "schema_version": "rtc-windows-record-export-failure-v1",
                    "round_id": rtc.ROUND_ID,
                    "status": "BLOCKED",
                    "failure_code": exc.code,
                    "message": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
