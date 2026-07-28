from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_weak_active_cleanup_w2_existing_cluster_absorption import (
    dump_json,
    dump_text,
    load_json,
)
from tools.build.report_weak_active_cleanup_w6_aggregate import (
    BACKLOG_PATH as W6_BACKLOG_PATH,
    FULL_CLASSIFICATION_PATH as W6_FULL_CLASSIFICATION_PATH,
    MATRIX_PATH as W6_MATRIX_PATH,
    POST_CLEANUP_FACTS_PATH as W6_POST_CLEANUP_FACTS_PATH,
    STATUS_MODEL_PATH as W6_STATUS_MODEL_PATH,
    SUMMARY_PATH as W6_SUMMARY_PATH,
)


OUTPUT_DIR = ROOT / "staging" / "post_cleanup_integrated_roadmap" / "phase0_input_freeze"
BASELINE_MANIFEST_PATH = OUTPUT_DIR / "post_cleanup_baseline_manifest.json"
INPUT_NOTE_PATH = OUTPUT_DIR / "post_cleanup_input_note.md"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_manifest(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
    }


def render_input_note(*, summary: dict[str, Any], manifest: dict[str, Any]) -> str:
    semantic = summary["semantic_status_counts"]
    runtime_semantic = summary["runtime_semantic_status_counts"]
    full_runtime = summary["full_runtime_semantic_status_counts"]
    return "\n".join(
        [
            "# Post-Cleanup Input Freeze Note",
            "",
            "## Authority",
            "",
            "- baseline authority is the W-6 aggregate output set",
            "- cleanup disposition authority: `weak_active_disposition_matrix.json`",
            "- status-model input authority: `status_model_input_from_weak_cleanup.json`",
            "- runtime-wide semantic split authority: `full_runtime_fourway_classification.json`",
            "- candidate facts remain candidate-only until runtime adoption explicitly replaces the official runtime inputs",
            "",
            "## Frozen counts",
            "",
            f"- cleanup scope rows: `{summary['matrix_row_count']}`",
            f"- full runtime rows: `{summary['full_runtime_row_count']}`",
            f"- backlog rows: `{summary['backlog_row_count']}`",
            f"- cleanup semantic split: `strong {semantic['semantic-strong']} / adequate {semantic['semantic-adequate']} / weak {semantic['semantic-weak']}`",
            f"- cleanup runtime-semantic split: `generated::strong {runtime_semantic['generated::semantic-strong']} / generated::adequate {runtime_semantic['generated::semantic-adequate']} / generated::weak {runtime_semantic['generated::semantic-weak']} / missing::strong {runtime_semantic['missing::semantic-strong']} / missing::adequate {runtime_semantic['missing::semantic-adequate']} / missing::weak {runtime_semantic['missing::semantic-weak']}`",
            f"- full runtime semantic split: `strong {full_runtime['semantic-strong']} / adequate {full_runtime['semantic-adequate']} / weak {full_runtime['semantic-weak']}`",
            "",
            "## Operational consequence",
            "",
            "All Phase 1/2/3 design work must reuse these counts and these exact artifacts as the frozen post-cleanup input set.",
            "If later discussion or implementation changes the cleanup classification, that is a new cleanup round rather than a Phase 1 status-model action.",
            "",
            "## Candidate facts rule",
            "",
            f"- candidate facts path: `{manifest['inputs']['post_cleanup_candidate_facts']['path']}`",
            "- this file is not the current runtime truth source",
            "- runtime adoption must explicitly choose which candidate rows replace the current official integrated facts",
            "",
        ]
    )


def build_post_cleanup_phase0_input_freeze(
    *,
    w6_summary_path: Path = W6_SUMMARY_PATH,
    w6_matrix_path: Path = W6_MATRIX_PATH,
    w6_status_model_path: Path = W6_STATUS_MODEL_PATH,
    w6_full_classification_path: Path = W6_FULL_CLASSIFICATION_PATH,
    w6_backlog_path: Path = W6_BACKLOG_PATH,
    w6_post_cleanup_facts_path: Path = W6_POST_CLEANUP_FACTS_PATH,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    summary = load_json(w6_summary_path)

    manifest = {
        "schema_version": "post-cleanup-phase0-input-freeze-v0",
        "source_authority": "weak-active-cleanup-w6-aggregate",
        "inputs": {
            "w6_summary": file_manifest(w6_summary_path),
            "disposition_matrix": file_manifest(w6_matrix_path),
            "status_model_input": file_manifest(w6_status_model_path),
            "full_runtime_classification": file_manifest(w6_full_classification_path),
            "backlog_map": file_manifest(w6_backlog_path),
            "post_cleanup_candidate_facts": file_manifest(w6_post_cleanup_facts_path),
        },
        "frozen_counts": {
            "cleanup_scope_row_count": summary["matrix_row_count"],
            "status_model_row_count": summary["status_model_row_count"],
            "backlog_row_count": summary["backlog_row_count"],
            "full_runtime_row_count": summary["full_runtime_row_count"],
            "semantic_status_counts": summary["semantic_status_counts"],
            "runtime_semantic_status_counts": summary["runtime_semantic_status_counts"],
            "full_runtime_semantic_status_counts": summary["full_runtime_semantic_status_counts"],
            "silent_review_row_count": summary["silent_review_row_count"],
            "silent_review_disposition_counts": summary["silent_review_disposition_counts"],
            "silent_review_semantic_counts": summary["silent_review_semantic_counts"],
        },
        "candidate_facts_contract": {
            "artifact_role": "candidate_only",
            "runtime_status": "not_adopted",
            "official_runtime_replacement_requires_phase2_adoption": True,
        },
        "output_paths": {
            "baseline_manifest": str(output_dir / BASELINE_MANIFEST_PATH.name),
            "input_note": str(output_dir / INPUT_NOTE_PATH.name),
        },
    }

    dump_json(output_dir / BASELINE_MANIFEST_PATH.name, manifest)
    dump_text(output_dir / INPUT_NOTE_PATH.name, render_input_note(summary=summary, manifest=manifest))
    return manifest


def main() -> int:
    manifest = build_post_cleanup_phase0_input_freeze()
    print("post-cleanup Phase 0 input freeze generated")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
