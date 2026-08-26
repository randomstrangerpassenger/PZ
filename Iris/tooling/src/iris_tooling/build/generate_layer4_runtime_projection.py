"""Generate the complete Layer 4 runtime projection outside the live tree."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_REPOSITORY_ROOT = SCRIPT_PATH.parents[6]
BUILD_ROOT_REL = Path("Iris/build")
DATA_ROOT_REL = Path("Iris/media/lua/client/Iris/Data")
CHUNK_ROOT_REL = DATA_ROOT_REL / "UseCaseDescriptions"
FACADE_REL = DATA_ROOT_REL / "IrisUseCaseDescriptions.lua"
REQUIREMENTS_REL = CHUNK_ROOT_REL / "RequirementsLookup.lua"
CHUNK_INDEX_REL = CHUNK_ROOT_REL / "ChunkIndex.lua"
LINE_COUNT_INDEX_REL = CHUNK_ROOT_REL / "LineCountIndex.lua"


class Layer4GenerationError(RuntimeError):
    pass


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Layer4GenerationError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Layer4GenerationError(f"expected object in {path}")
    return value


def _load_converter(repository_root: Path):
    build_root = repository_root / BUILD_ROOT_REL
    if str(build_root) not in sys.path:
        sys.path.insert(0, str(build_root))
    import convert_descriptions_to_lua as converter

    return converter


def source_paths(repository_root: Path) -> dict[str, Path]:
    raw_output = os.environ.get("IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT")
    if not raw_output:
        raise Layer4GenerationError(
            "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT is required; repository output fallback is unsupported"
        )
    output = Path(raw_output).resolve()
    resolved_repository = repository_root.resolve()
    if output == resolved_repository or resolved_repository in output.parents:
        raise Layer4GenerationError("Layer 4 source projection must be repository-external")
    return {
        "descriptions": output / "descriptions_by_fulltype.v2.4.json",
        "navigation": output / "recipe_nav_registry.v2.4.json",
        "requirements": output / "recipe_requirements_index.v2.4.json",
        "recipe_decisions": output / "recipe_evidence_decisions.v2.4.json",
    }


def _enrich_navigation(
    descriptions: dict, navigation: dict, recipe_decisions: dict
) -> tuple[dict, dict[str, int]]:
    fulltypes = descriptions.get("fulltypes")
    entries = navigation.get("entries")
    rules = recipe_decisions.get("rules")
    if not isinstance(fulltypes, dict) or not isinstance(entries, dict) or not isinstance(rules, dict):
        raise Layer4GenerationError("structured source schema is incomplete")

    enriched = copy.deepcopy(navigation)
    enriched_entries = enriched["entries"]
    positive_count = 0
    recipe_count = 0
    seen_recipe_use_cases: set[str] = set()

    for fulltype in sorted(fulltypes):
        block = fulltypes[fulltype].get("use_case_block", {})
        items = block.get("items", [])
        if not isinstance(items, list):
            raise Layer4GenerationError(f"{fulltype}: items must be a list")
        seen_identities: set[str] = set()
        for item in items:
            identity = item.get("use_case_id")
            if not isinstance(identity, str) or not identity:
                raise Layer4GenerationError(f"{fulltype}: blank interaction identity")
            if identity.startswith("uc.exclusion."):
                continue
            if identity in seen_identities:
                raise Layer4GenerationError(f"{fulltype}: duplicate identity {identity}")
            seen_identities.add(identity)
            surface = item.get("surface")
            if surface not in {"context_menu", "recipe_ui"}:
                raise Layer4GenerationError(
                    f"{fulltype}/{identity}: unsupported positive surface {surface!r}"
                )
            positive_count += 1
            if surface != "recipe_ui":
                continue
            if not identity.startswith("uc.recipe."):
                raise Layer4GenerationError(
                    f"{fulltype}/{identity}: Recipe row lacks structured recipe identity"
                )
            nav_entry = enriched_entries.get(identity)
            if not isinstance(nav_entry, dict) or not nav_entry.get("nav_eligible"):
                raise Layer4GenerationError(f"{fulltype}/{identity}: navigation is unavailable")
            rule_id = "rp.recipe." + identity.removeprefix("uc.recipe.")
            rule = rules.get(rule_id)
            if not isinstance(rule, dict) or rule.get("decision") != "PASS":
                raise Layer4GenerationError(f"{fulltype}/{identity}: missing positive rule {rule_id}")
            stable_recipe_id = rule.get("recipe_id")
            if not isinstance(stable_recipe_id, str) or not stable_recipe_id:
                raise Layer4GenerationError(f"{rule_id}: blank stable recipe_id")
            nav_entry["stable_recipe_id"] = stable_recipe_id
            seen_recipe_use_cases.add(identity)
            recipe_count += 1

    return enriched, {
        "fulltype_count": len(fulltypes),
        "positive_row_count": positive_count,
        "recipe_row_count": recipe_count,
        "unique_recipe_identity_count": len(seen_recipe_use_cases),
    }


def render_projection(repository_root: Path) -> tuple[dict[Path, bytes], dict[str, int]]:
    repository_root = repository_root.resolve()
    paths = source_paths(repository_root)
    descriptions = _load_json(paths["descriptions"])
    navigation = _load_json(paths["navigation"])
    requirements = _load_json(paths["requirements"])
    recipe_decisions = _load_json(paths["recipe_decisions"])
    navigation, metrics = _enrich_navigation(descriptions, navigation, recipe_decisions)

    converter = _load_converter(repository_root)
    (
        facade,
        chunks,
        requirements_lookup,
        fulltype_count,
        _line_count,
        nav_errors,
    ) = converter.convert_to_lua(
        descriptions, navigation, requirements, require_stable_recipe_id=True
    )
    if nav_errors:
        raise Layer4GenerationError("; ".join(nav_errors[:10]))
    structural_errors = converter.structural_validation(
        facade, [content for _index, content, _count in chunks], fulltype_count
    )
    if structural_errors:
        raise Layer4GenerationError("; ".join(structural_errors[:10]))
    if requirements_lookup is None:
        raise Layer4GenerationError("requirements projection was not generated")

    rendered: dict[Path, bytes] = {
        FACADE_REL: facade.encode("utf-8"),
        REQUIREMENTS_REL: requirements_lookup.encode("utf-8"),
        CHUNK_INDEX_REL: converter.build_usecase_chunk_index(descriptions, chunks).encode("utf-8"),
        LINE_COUNT_INDEX_REL: converter.build_usecase_line_count_index(descriptions).encode("utf-8"),
    }
    for index, content, _entry_count in chunks:
        rendered[CHUNK_ROOT_REL / f"Chunk{index:03d}.lua"] = content.encode("utf-8")
    metrics["generated_file_count"] = len(rendered)
    metrics["chunk_count"] = len(chunks)
    return rendered, metrics


def generate_projection(candidate_root: Path, repository_root: Path) -> dict[str, int]:
    candidate_root = candidate_root.resolve()
    repository_root = repository_root.resolve()
    live_data_root = (repository_root / DATA_ROOT_REL).resolve()
    if candidate_root == repository_root or candidate_root == live_data_root or live_data_root in candidate_root.parents:
        raise Layer4GenerationError("candidate root must be outside the live generated tree")
    rendered, metrics = render_projection(repository_root)
    for relative_path, content in rendered.items():
        destination = candidate_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT)
    args = parser.parse_args()
    try:
        metrics = generate_projection(args.candidate_root, args.repository_root)
    except Layer4GenerationError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("PASS: Layer 4 complete candidate generated")
    print(json.dumps(metrics, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
