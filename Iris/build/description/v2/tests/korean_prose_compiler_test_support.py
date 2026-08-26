from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]

from iris_tooling.build.compose_layer3_identity import (
    apply_identity_zero_anaphora,
    build_candidate_lead_context,
    naturalize_source_fragment,
    render_acquisition_listing,
    render_candidate_lead,
    select_candidate_lead_realization,
)
from iris_tooling.build.compose_layer3_body_profile import (
    build_candidate_body_plan_requirements,
)
from iris_tooling.build.compose_layer3_item import compose_item_candidate
from iris_tooling.build.layer3_current_authority_reconstruction import load_runtime_chunks


def current_rendered_path() -> Path:
    runtime_data = (
        V2_ROOT.parents[2] / "media" / "lua" / "client" / "Iris" / "Data"
    )
    pointer = (runtime_data / "IrisLayer3DataCurrent.lua").read_text(
        encoding="utf-8"
    )
    match = re.search(r"dvf33-[0-9a-f]{64}", pointer)
    if match is None:
        raise ValueError("current Layer3 generation pointer is invalid")
    return (
        runtime_data
        / "IrisLayer3Generations"
        / match.group(0)
        / "dvf_3_3_rendered.json"
    )


def candidate_proposition(
    role: str,
    source_field: str,
    source_value: str,
    semantic_key: str,
) -> dict[str, object]:
    return {
        "item_id": "Base.Test",
        "proposition_id": f"Base.Test#{role}",
        "role": role,
        "source_path": "facts.jsonl",
        "source_field": source_field,
        "source_value": source_value,
        "semantic_key": semantic_key,
        "qualifier": "none",
        "condition": "none",
        "modality": "asserted",
    }


def candidate_requirement(
    section_name: str,
    role: str,
    required: bool,
    optional: bool,
    ordering_index: int,
) -> dict[str, object]:
    return {
        "item_id": "Base.Test",
        "requirement_id": f"Base.Test#{section_name}",
        "resolved_profile": "tool_body",
        "section_name": section_name,
        "role": role,
        "required": required,
        "optional": optional,
        "ordering_index": ordering_index,
        "applicable_proposition_ids": [f"Base.Test#{role}"],
        "emission_eligible": True,
    }
