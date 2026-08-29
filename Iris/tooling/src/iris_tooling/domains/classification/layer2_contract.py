from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

PREDECESSOR_COMMIT = "6b7118dc229bf8138302696e1aa5e5b7454589dc"
PREDECESSOR_TREE = "4eae6fbdb3d0b2cb532f875b96137335a403f2fc"
SUPPORT_PREDICATE = "current-owner-fulltype-union-v1"

CLASSIFICATIONS = Path("Iris/media/lua/client/Iris/Data/IrisClassifications.lua")
CATEGORY_INDEX = Path("Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua")
KO_TRANSLATION = Path("Iris/media/lua/shared/translate/ko/Iris_ko.txt")
EN_TRANSLATION = Path("Iris/media/lua/shared/translate/en/Iris_en.txt")
L3_POINTER = Path("Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua")
L3_GENERATIONS = Path("Iris/media/lua/client/Iris/Data/IrisLayer3Generations")
L4_OWNER_INPUT = Path("Iris/build/description/v2/data/upstream_usecases_by_fulltype.json")

AUTHORITY_ROOT = Path("Iris/_docs/authority/classification_layer2")
RESOLUTION_CONTRACT = AUTHORITY_ROOT / "classification_layer2_resolution_contract.json"
OUTPUT_SCHEMA = AUTHORITY_ROOT / "classification_layer2_owner_output.schema.json"
ABSENCE_REGISTRY = AUTHORITY_ROOT / "classification_layer2_absence_reason_registry.json"
MENU_DISPOSITION = AUTHORITY_ROOT / "classification_layer2_menu_convergence_disposition.json"
DATA_ROOT = Path("Iris/build/classification/data")
RESOLUTION_REGISTRY = DATA_ROOT / "classification_layer2_resolution_registry.json"
SURFACE_CATALOG = DATA_ROOT / "classification_layer2_surface_catalog.json"
OWNER_OUTPUT = DATA_ROOT / "classification_layer2_owner_output.json"


class Layer2ContractError(ValueError):
    """Raised when the Classification-owned Layer 2 relation is malformed."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Layer2ContractError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Layer2ContractError(f"{path}: expected JSON object")
    return value


def git_identity(repository_root: Path) -> dict[str, str]:
    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=repository_root, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if completed.returncode:
            raise Layer2ContractError(completed.stderr.strip() or "git identity query failed")
        return completed.stdout.strip()

    return {
        "commit": git("rev-parse", "HEAD"),
        "tree": git("show", "-s", "--format=%T", "HEAD"),
    }


_PRIMARY_START = re.compile(r"^IrisPrimarySubcategory\s*=\s*\{")
_PRIMARY_ROW = re.compile(r'^\s*\["([^"]+)"\]\s*=\s*"([^"]+)",\s*$')
_CLASSIFICATION_ROW = re.compile(r'^\s*\["([^"]+)"\]\s*=\s*\{\s*((?:"[^"]+"\s*,?\s*)+)\},\s*$')
_QUOTED = re.compile(r'"([^"]+)"')


def parse_classifications(path: Path) -> dict[str, tuple[str, ...]]:
    rows: dict[str, tuple[str, ...]] = {}
    in_primary = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if _PRIMARY_START.match(line):
            in_primary = True
        if in_primary:
            continue
        match = _CLASSIFICATION_ROW.match(line)
        if not match:
            continue
        full_type = match.group(1)
        if full_type in rows:
            raise Layer2ContractError(f"duplicate classification FullType: {full_type}")
        rows[full_type] = tuple(_QUOTED.findall(match.group(2)))
    if not rows:
        raise Layer2ContractError("classification census is empty")
    return rows


def parse_primary_overrides(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if _PRIMARY_START.match(line):
            active = True
            continue
        if active and line.strip() == "}":
            break
        if not active:
            continue
        match = _PRIMARY_ROW.match(line)
        if match:
            full_type, primary = match.groups()
            if full_type in rows:
                raise Layer2ContractError(f"duplicate primary override: {full_type}")
            rows[full_type] = primary
    return rows


_POINTER = re.compile(r'generation_id\s*=\s*"([^"]+)"')


def current_layer3_entries(repository_root: Path) -> dict[str, Any]:
    pointer = (repository_root / L3_POINTER).read_text(encoding="utf-8")
    match = _POINTER.search(pointer)
    if not match:
        raise Layer2ContractError("current Layer 3 generation pointer is malformed")
    rendered = load_json_object(repository_root / L3_GENERATIONS / match.group(1) / "dvf_3_3_rendered.json")
    entries = rendered.get("entries")
    if not isinstance(entries, dict):
        raise Layer2ContractError("current Layer 3 entries are missing")
    return entries


def current_layer4_entries(repository_root: Path) -> dict[str, Any]:
    value = load_json_object(repository_root / L4_OWNER_INPUT)
    entries = value.get("fulltypes")
    if not isinstance(entries, dict):
        raise Layer2ContractError("current Layer 4 owner rows are missing")
    return entries


def support_universe(repository_root: Path) -> tuple[str, ...]:
    classifications = parse_classifications(repository_root / CLASSIFICATIONS)
    layer3 = current_layer3_entries(repository_root)
    layer4 = current_layer4_entries(repository_root)
    support = set(classifications) | set(layer3) | set(layer4)
    if not support or not all(isinstance(row, str) and row for row in support):
        raise Layer2ContractError("support universe is empty or malformed")
    return tuple(sorted(support, key=lambda value: value.encode("utf-8")))


def support_sha256(support: tuple[str, ...]) -> str:
    return sha256_bytes(b"".join(value.encode("utf-8") + b"\n" for value in support))


_CATEGORY_ROW = re.compile(r'^\s*name\s*=\s*"([^"]+)"')
_CATEGORY_KEY = re.compile(r'^\s*key\s*=\s*"(Iris_Cat_[^"]+)"')
_SUBCATEGORY_ROW = re.compile(
    r'^\s*\["([1-9]-[A-Z])"\]\s*=\s*\{\s*key\s*=\s*"(Iris_Sub_[^"]+)"'
)
_TRANSLATION_ROW = re.compile(r'^\s*(Iris_(?:Cat|Sub)_[A-Za-z0-9]+)\s*=\s*"([^"]*)",\s*$')


def parse_taxonomy(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    categories: dict[str, str] = {}
    subcategories: dict[str, str] = {}
    pending_category: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        category = _CATEGORY_ROW.match(line)
        if category:
            pending_category = category.group(1)
            continue
        category_key = _CATEGORY_KEY.match(line)
        if category_key and pending_category is not None:
            categories[pending_category] = category_key.group(1)
            pending_category = None
            continue
        subcategory = _SUBCATEGORY_ROW.match(line)
        if subcategory:
            subcategories[subcategory.group(1)] = subcategory.group(2)
    if len(categories) != 9 or len(subcategories) != 50:
        raise Layer2ContractError(
            f"taxonomy census mismatch: categories={len(categories)} subcategories={len(subcategories)}"
        )
    return categories, subcategories


def parse_translation(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _TRANSLATION_ROW.match(line)
        if not match:
            continue
        key, text = match.groups()
        if key in result:
            raise Layer2ContractError(f"duplicate locale key in {path}: {key}")
        result[key] = text
    return result
