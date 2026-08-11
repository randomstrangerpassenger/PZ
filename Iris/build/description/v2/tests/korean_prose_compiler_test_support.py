from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.compose_layer3_identity import (
    apply_identity_zero_anaphora,
    build_candidate_lead_context,
    naturalize_source_fragment,
    render_acquisition_listing,
    render_candidate_lead,
    select_candidate_lead_realization,
)
from tools.build.compose_layer3_body_profile import (
    build_candidate_body_plan_requirements,
)
from tools.build.compose_layer3_item import compose_item_candidate
from tools.build.layer3_current_authority_reconstruction import (
    CANONICAL_RENDERED,
    load_runtime_chunks,
)
