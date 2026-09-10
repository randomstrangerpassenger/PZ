"""Single integrated Layer 2 identity gate; no product build or installation."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

import pytest

from iris_tooling.domains.classification import layer2_contract as contract
from iris_tooling.domains.classification import layer2_materializer as materializer
from iris_tooling.domains.classification import layer2_validator as validator
from iris_tooling.domains.layer3 import product_projection


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = contract.load_json_object(ROOT / contract.RESOLUTION_REGISTRY)
OWNER_SHA = "d9267995d04bb84009a8106e81c6935da2190ce26b156eb8beb903f956595d34"


def git_bytes(commit, path):
    return subprocess.run(
        ["git", "show", f"{commit}:{Path(path).as_posix()}"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
    ).stdout


@pytest.fixture(scope="module")
def workspace():
    parent = ROOT / ".tmp"
    parent.mkdir(exist_ok=True)
    assert parent.resolve().is_relative_to(ROOT)
    with TemporaryDirectory(prefix="l2-", dir=parent) as directory:
        yield Path(directory)


@pytest.fixture(scope="module")
def inputs(workspace):
    registry = deepcopy(REGISTRY)
    bindings = registry["input_identities"]
    generation = next(p for p in bindings if p.endswith("/dvf_3_3_rendered.json"))
    # Short fixture generation ID preserves the input graph without duplicating
    # the long content-addressed directory name in a Windows temporary tree.
    short_generation = (contract.L3_GENERATIONS / "g" / "dvf_3_3_rendered.json").as_posix()
    for relative in list(bindings):
        raw = (ROOT / relative).read_bytes()
        target = short_generation if relative == generation else relative
        if relative == contract.L3_POINTER.as_posix():
            raw = raw.replace(Path(generation).parent.name.encode(), b"g")
            bindings[relative]["sha256"] = contract.sha256_bytes(raw)
        path = workspace / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    bindings[short_generation] = bindings.pop(generation)
    return workspace, registry


@contextmanager
def changed(path, raw):
    original = path.read_bytes()
    try:
        path.write_bytes(raw)
        yield
    finally:
        path.write_bytes(original)


def test_uniform_eol_and_locale_projection(inputs):
    root, registry = inputs
    for relative, descriptor in registry["input_identities"].items():
        path = root / relative
        if descriptor["algorithm"] == "eol_lf_sha256":
            lf = path.read_bytes().replace(b"\r\n", b"\n")
            for raw in (lf, lf.replace(b"\n", b"\r\n")):
                with changed(path, raw):
                    contract.admit_registry_inputs(root, registry)
        elif descriptor["algorithm"] == "category_locale_sha256":
            raw = path.read_bytes()
            # Even a value mentioning a category key in an unrelated UI entry
            # must stay outside the referenced declaration projection.
            addition = b'    Iris_UI_IdentityFixture = "Iris_Cat_Tool",\n'
            for variant in (raw.replace(b"}\n", addition + b"}\n"), raw.replace(b"\n", b"\r\n")):
                assert variant != raw
                with changed(path, variant):
                    contract.admit_registry_inputs(root, registry)


def test_source_mutations_fail_closed(inputs):
    root, registry = inputs
    for relative, descriptor in registry["input_identities"].items():
        path = root / relative
        raw = path.read_bytes()
        if descriptor["algorithm"] == "eol_lf_sha256":
            lf = raw.replace(b"\r\n", b"\n")
            variants = (
                lf.replace(b"\n", b"\r\n", 1),  # mixed EOL
                lf.replace(b"\n", b"\r", 1),  # lone CR
                b"\xef\xbb\xbf" + lf,
                lf.rstrip(b"\n"),
                lf.replace(b"\n", b" \n", 1),
                lf + b"-- comment\n",
                lf.replace(b"Iris", b"IRIS", 1) if b"Iris" in lf else lf + b"x",
            )
        elif descriptor["algorithm"] == "category_locale_sha256":
            text = raw.decode("utf-8")
            key = next(iter(contract.referenced_locale_projection(root / contract.CATEGORY_INDEX, path)))
            row = next(line for line in text.splitlines(keepends=True) if re.match(r"\s*" + key + r"\s*=", line))
            variants = tuple(value.encode("utf-8") for value in (
                text.replace(row, ""), text + row,
                text.replace(row, row.replace('= "', '= "changed ', 1)),
                text.replace(row, row.replace('= "', '= malformed "', 1)),
                text + row.replace('= "', '= malformed "', 1),
            ))
        else:
            # Raw boundaries reject EOL-only drift as well as arbitrary bytes.
            variants = (raw + b" ", raw.replace(b"\n", b"\r\n"))
        for mutation in variants:
            assert mutation != raw
            with changed(path, mutation), pytest.raises(contract.Layer2ContractError):
                contract.admit_registry_inputs(root, registry)
    path = root / contract.EN_TRANSLATION
    missing = path.with_suffix(".bak")
    path.rename(missing)
    try:
        with pytest.raises(contract.Layer2ContractError):
            contract.admit_registry_inputs(root, registry)
    finally:
        missing.rename(path)


def test_descriptor_admission_and_historical_raw_semantics(inputs):
    root, registry = inputs
    path = contract.CATEGORY_INDEX.as_posix()
    invalid = []
    for field, value in (("algorithm", "unknown"), ("version", 2), ("version", True),
                         ("scope", "all_text"), ("sha256", "0"), ("sha256", "z" * 64)):
        copy = deepcopy(registry)
        copy["input_identities"][path][field] = value
        invalid.append(copy)
    for field in ("algorithm", "version", "scope", "sha256"):
        copy = deepcopy(registry)
        del copy["input_identities"][path][field]
        invalid.append(copy)
    copy = deepcopy(registry)
    del copy["input_identities"][path]
    invalid.append(copy)
    for update in ({"schema_version": "unknown"}, {"input_sha256": {}},
                   {"input_identities": {}}, {"input_identities": None}):
        invalid.append(dict(registry, **update))
    for copy in invalid:
        with pytest.raises(contract.Layer2ContractError):
            contract.admit_registry_inputs(root, copy)

    v1 = deepcopy(registry)
    v1["schema_version"] = contract.REGISTRY_V1
    v1["input_sha256"] = {p: contract.sha256_file(root / p) for p in v1.pop("input_identities")}
    contract.admit_registry_inputs(root, v1)
    taxonomy = root / path
    with changed(taxonomy, taxonomy.read_bytes().replace(b"\n", b"\r\n")):
        with pytest.raises(contract.Layer2ContractError, match="stale"):
            contract.admit_registry_inputs(root, v1)
    v1["input_identities"] = registry["input_identities"]
    with pytest.raises(contract.Layer2ContractError, match="ambiguous"):
        contract.admit_registry_inputs(root, v1)


def test_predecessor_semantics_and_binding_history(workspace):
    migration = REGISTRY["input_identity_migration"]
    predecessor = migration["predecessor_registry"]
    assert predecessor == json.loads(git_bytes(migration["predecessor_registry_commit"], contract.RESOLUTION_REGISTRY))
    assert REGISTRY["source_subject_binding"] == predecessor["source_subject_binding"]
    assert REGISTRY["approval_identity"] == predecessor["approval_identity"]
    before = workspace / "before"
    taxonomy = workspace / "taxonomy.lua"
    taxonomy.write_bytes(git_bytes(migration["predecessor_registry_commit"], contract.CATEGORY_INDEX))
    assert contract.parse_taxonomy(taxonomy) == contract.parse_taxonomy(ROOT / contract.CATEGORY_INDEX)
    keys = set().union(*(mapping.values() for mapping in contract.parse_taxonomy(taxonomy)))
    assert len(keys) == 59
    for relative, descriptor in REGISTRY["input_identities"].items():
        if descriptor["algorithm"] == "category_locale_sha256":
            raw = git_bytes(migration["locale_raw_binding_commit"], relative)
            assert contract.sha256_bytes(raw) == predecessor["input_sha256"][relative]
            before.write_bytes(raw)
            old = contract.referenced_locale_projection(taxonomy, before)
            current = contract.referenced_locale_projection(ROOT / contract.CATEGORY_INDEX, ROOT / relative)
            assert old == current and set(current) == keys
        elif descriptor["algorithm"] == "eol_lf_sha256":
            raw = git_bytes(migration["predecessor_registry_commit"], relative)
            lf = raw.replace(b"\r\n", b"\n")
            assert predecessor["input_sha256"][relative] in {
                contract.sha256_bytes(lf), contract.sha256_bytes(lf.replace(b"\n", b"\r\n")),
            }
            assert lf == (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
            before.write_bytes(raw)
            if relative == contract.CLASSIFICATIONS.as_posix():
                assert contract.parse_classifications(before) == contract.parse_classifications(ROOT / relative)
                assert contract.parse_primary_overrides(before) == contract.parse_primary_overrides(ROOT / relative)
            elif relative == contract.L4_OWNER_INPUT.as_posix():
                assert json.loads(raw) == contract.load_json_object(ROOT / relative)
        else:
            assert descriptor["sha256"] == predecessor["input_sha256"][relative]


def product_readback():
    data = contract.L3_POINTER.parent
    generation = next(Path(p).parent for p in REGISTRY["input_identities"] if p.endswith("/dvf_3_3_rendered.json"))
    paths = [generation, contract.L3_POINTER, contract.OWNER_OUTPUT,
             data / "IrisLayer3ProductCurrent.lua", data / "IrisLayer3ProductGenerations",
             data / "IrisLayer3Product.lock", data / "IrisTooltipStaticData.lua",
             data / "IrisTooltipRecipeVariants.lua",
             Path("Iris/_docs/authority/iris_current_route_index.json"),
             Path(".tmp/l3-06/candidate"), Path(".tmp/l3-06/source"), Path(".tmp/package/l3-06")]
    result = {}
    for relative in paths:
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT)
        result[relative.as_posix()] = "directory" if path.is_dir() else "file" if path.is_file() else None
        for member in sorted(path.rglob("*")) if path.is_dir() else [path]:
            assert member.resolve().is_relative_to(ROOT)
            if member.is_file():
                result[member.relative_to(ROOT).as_posix()] = contract.sha256_file(member)
    return result


def test_final_owner_and_downstream_prerequisite():
    # The installed tooling must be this final source, with normal conftest.
    for module in (contract, materializer, validator, product_projection):
        source = ROOT / "Iris/tooling/src" / Path(*module.__name__.split(".")).with_suffix(".py")
        installed = Path(module.__file__).resolve()
        assert installed.is_relative_to(ROOT)
        assert installed.read_bytes() == source.read_bytes()
    baseline = product_readback()
    original = (ROOT / contract.OWNER_OUTPUT).read_bytes()
    assert contract.sha256_bytes(original) == OWNER_SHA
    generated = materializer.materialize(ROOT)
    # The current owner is already serialized with CRLF. Admission changes do
    # not authorize reserializing it, even when canonical JSON differs in EOL.
    assert generated == json.loads(original)
    assert product_projection.validate_owner_output is validator.validate_owner_output
    report = product_projection.validate_owner_output(ROOT)
    assert report["status"] == "complete"
    assert (report["frozen_support_count"], report["layer2_applicable_count"],
            report["layer2_display_silence_count"]) == (2280, 1406, 874)
    seal = contract.load_json_object(ROOT / contract.RESOLUTION_CONTRACT)["successor_amendment"]["preserved_resolved_rows_canonical_sha256"]
    assert contract.sha256_bytes(contract.canonical_bytes(generated["rows"])) == seal
    assert (ROOT / contract.OWNER_OUTPUT).read_bytes() == original
    assert product_readback() == baseline
