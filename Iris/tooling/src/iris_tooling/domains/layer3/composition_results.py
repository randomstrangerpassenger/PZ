"""Production and strict readback of the DVF semantic-composition handoff."""
from __future__ import annotations

import json
from pathlib import Path

from . import composition_model as model
from . import composition_rules as rules
from . import recovery
from . import recovery_relations
from . import recovery_sources


ADOPTION_REF = {
    "path": "Iris/_docs/authority/dvf/layer3_expression/successors/r6/adoption.json",
    "sha256": "7dded22fad93b7eeff8debf56205cb9ee84220758d53ecb41396889fb49bd799",
}
DEFAULT_OUTPUT = "Iris/build/description/composition/blocks.json"


def source_identity(loaded: dict) -> dict:
    payloads = loaded["payloads"]
    return {"adoption": ADOPTION_REF,
            "manifest": loaded["adoption"]["manifest"],
            "semantic_authority_id": payloads["semantic"]["authority_id"],
            "acquisition_authority_id": payloads["acquisition"]["authority_id"],
            "fact_counts": {"semantic": len(payloads["semantic"]["facts"]),
                            "acquisition": len(payloads["acquisition"]["facts"])}}


def produce(root: Path) -> tuple[dict, dict]:
    """Load the adopted input once and return both source and composed result."""
    root = Path(root).resolve()
    loaded = recovery.load_adopted(root, ADOPTION_REF)
    payloads = loaded["payloads"]
    delta = recovery_sources.supplement_player_uses(root, payloads['semantic'])
    semantic = dict(payloads['semantic'],
        facts=payloads['semantic']['facts'] + delta['facts'],
        observations={**payloads['semantic']['observations'], **delta['observations']},
        provenance={**payloads['semantic']['provenance'], **delta['provenance']})
    source = source_identity(loaded)
    source['semantic_correction'] = delta
    source['fact_counts']['semantic'] = len(semantic['facts'])
    result = rules.compose(semantic, payloads['acquisition'], source)
    recovery_relations.enrich(root, semantic, result)
    loaded = dict(loaded, composition_semantic=semantic)
    return loaded, result


def write_result(root: Path, result: dict, path: str = DEFAULT_OUTPUT, *, replace: bool = False) -> Path:
    root = Path(root).resolve()
    target = (root / path).resolve()
    allowed = (root / "Iris/build/description/composition").resolve()
    model.require(target.is_relative_to(allowed), "composition output must stay in its build directory")
    model.validate_result(result)
    target.parent.mkdir(parents=True, exist_ok=True)
    model.require(replace or not target.exists(), "composition result already exists")
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(model.canonical(result))
    temporary.replace(target)
    return target


def read_result(root: Path, path: str = DEFAULT_OUTPUT) -> dict:
    root = Path(root).resolve()
    target = (root / path).resolve()
    allowed = (root / "Iris/build/description/composition").resolve()
    model.require(target.is_relative_to(allowed), "composition input must stay in its build directory")
    return model.validate_result(json.loads(target.read_text(encoding="utf-8")))
