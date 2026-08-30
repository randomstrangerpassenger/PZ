from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from iris_tooling.build.repository_context import require_repository_context
from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, fulltype_set_sha256, sha256_bytes
from iris_tooling.domains.tooltip_t1.models import TooltipContractError
from .contract import (
    MANIFEST_SCHEMA, ROUTE, admit, empty_output, external_path, load_contract,
    machine_subject, read_object, require,
)
from .projection import project
from .serialization import (
    FINAL_CLOSEOUT, LUA_NAME, MANIFEST_NAME, RUN_RECEIPT,
    artifact_binding, lua_bytes, manifest_bytes,
)


def implementation_binding(repository_root: Path) -> dict:
    contract, contract_hash = load_contract(repository_root)
    return {
        "subject": machine_subject(repository_root),
        "generator_version": contract["generator_version"],
        "projection_contract_sha256": contract_hash,
        "manifest_schema_sha256": sha256_bytes(canonical_bytes(json.loads(
            (repository_root / MANIFEST_SCHEMA).read_text(encoding="utf-8")))),
    }


def build(repository_root: Path, handoff_root: Path, output_root: Path) -> dict:
    output = empty_output(repository_root, output_root)
    implementation = implementation_binding(repository_root)
    contract, contract_hash = load_contract(repository_root)
    accepted = admit(repository_root, handoff_root, contract)
    data, provenance, summary = project(accepted, contract)
    lua = lua_bytes(data)
    manifest = manifest_bytes(accepted.binding, contract_hash, contract, lua, provenance, summary)
    artifacts = {LUA_NAME: lua, MANIFEST_NAME: manifest}
    receipt = {
        "schema_version": "iris-tooltip-t2-run-receipt-v1", "state": "generated",
        "implementation": implementation, "t1_input": accepted.binding,
        "artifacts": {name: artifact_binding(value) for name, value in artifacts.items()},
    }
    # Prepare everything before creating output. The completion marker is last.
    output.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        with (output / name).open("xb") as stream:
            stream.write(value)
    with (output / RUN_RECEIPT).open("xb") as stream:
        stream.write(canonical_bytes(receipt))
    return receipt


def finalize(repository_root: Path, run_a_root: Path, run_b_root: Path,
             output_root: Path, completion: dict | None = None) -> dict:
    output = empty_output(repository_root, output_root)
    expected = implementation_binding(repository_root)
    contract, _ = load_contract(repository_root)
    roots = [external_path(repository_root, root) for root in (run_a_root, run_b_root)]
    require(roots[0] != roots[1], "Run A and B must be distinct roots")
    receipts, artifacts = [], []
    for root in roots:
        require({path.name for path in root.iterdir()} == {LUA_NAME, MANIFEST_NAME, RUN_RECEIPT}, "run file set mismatch")
        receipt = read_object(root / RUN_RECEIPT)
        require(receipt.get("schema_version") == "iris-tooltip-t2-run-receipt-v1"
                and receipt.get("state") == "generated" and receipt.get("implementation") == expected,
                "T2 run implementation subject/contract mismatch")
        payload = {name: (root / name).read_bytes() for name in (LUA_NAME, MANIFEST_NAME)}
        require(receipt.get("artifacts") == {name: artifact_binding(value) for name, value in payload.items()}, "run artifact tamper")
        manifest = read_object(root / MANIFEST_NAME)
        require(manifest.get("schema_version") == "iris-tooltip-t2-projection-manifest-v1"
                and manifest.get("projection_contract_sha256") == expected["projection_contract_sha256"]
                and manifest.get("generator_version") == expected["generator_version"]
                and manifest.get("t1_input") == receipt.get("t1_input"), "manifest input/contract binding mismatch")
        require(manifest.get("generation_success_count") == contract["support_count"]
                and len(manifest.get("fulltypes", {})) == contract["support_count"]
                and fulltype_set_sha256(manifest.get("fulltypes", {})) == contract["support_sha256"]
                and all(manifest.get(key) == 0 for key in ("generation_failure_count", "contract_violation_count", "lexical_guard_hit_count")), "manifest coverage/violation mismatch")
        require(manifest.get("lua") == {"file_name": LUA_NAME, **artifact_binding(payload[LUA_NAME])}, "manifest Lua binding mismatch")
        receipts.append(receipt)
        artifacts.append(payload)
    require(receipts[0]["t1_input"] == receipts[1]["t1_input"], "Run A/B T1 input mismatch")
    require(artifacts[0] == artifacts[1], "Run A/B bytes differ")
    locator = json.loads((repository_root / ROUTE).read_text(encoding="utf-8"))["tooltip_t1_production_handoff"]
    accepted = admit(repository_root, Path(locator["final_root"]), contract)
    require(accepted.binding == receipts[0]["t1_input"], "run T1 input is no longer current")
    required_checks = {"focused_tests", "installed_inspect", "lua_syntax", "canonical_full_gate"}
    if completion is not None:
        require(isinstance(completion, dict) and set(completion) == required_checks, "completion metadata checks missing")
        for name, check in completion.items():
            require(isinstance(check, dict) and check.get("exit_code") == 0
                    and check.get("subject") == expected["subject"]
                    and isinstance(check.get("command"), str) and bool(check["command"])
                    and check.get("artifacts") == receipts[0]["artifacts"], f"{name}: completion binding mismatch")
    closeout = {
        "schema_version": "iris-tooltip-t2-closeout-v1",
        "state": "complete" if completion is not None else "artifact_finalized",
        "implementation": expected, "t1_input": accepted.binding,
        "artifacts": receipts[0]["artifacts"], "candidate_final_bytes_equal": True,
        "runs": [{"root": root.as_posix(), "receipt_sha256": sha256_bytes((root / RUN_RECEIPT).read_bytes())} for root in roots],
        "validation": completion or {},
        "validated": ["Run A/B artifact equality", "exact coverage and zero violations", "candidate/final equality", *(sorted(required_checks) if completion is not None else [])],
        "unvalidated_but_in_scope": [] if completion is not None else sorted(required_checks),
        "out_of_scope": ["PZ runtime/load", "visual/Alt/wrapping/performance", "runtime/package adoption", "release/deployment"],
        "validation_ceiling": "offline static staging only; fixed lexical list, not semantic quality certification; no full Menu parity claim",
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts[0].items():
        with (output / name).open("xb") as stream:
            stream.write(value)
        require((output / name).read_bytes() == value, "candidate/final byte mismatch")
    require({path.name for path in output.iterdir()} == {LUA_NAME, MANIFEST_NAME}, "final artifact file set mismatch")
    with (output / FINAL_CLOSEOUT).open("xb") as stream:
        stream.write(canonical_bytes(closeout))
    return closeout


def main(argv=None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    is_final = values[:1] == ["finalize"]
    parser = argparse.ArgumentParser(prog="iris-tooling " + ("finalize" if is_final else "build") + " tooltip-t2")
    parser.add_argument("--output-root", type=Path, required=True)
    if is_final:
        parser.add_argument("--run-a-root", type=Path, required=True)
        parser.add_argument("--run-b-root", type=Path, required=True)
        parser.add_argument("--completion-metadata-json", help="Explicit command/exit/subject/artifact bindings; omission permits artifact finalization only")
    else:
        parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args(values[1:] if is_final else values)
    try:
        repository = require_repository_context().repository_root
        if is_final:
            result = finalize(repository, args.run_a_root, args.run_b_root, args.output_root,
                              json.loads(args.completion_metadata_json) if args.completion_metadata_json else None)
        else:
            result = build(repository, args.handoff_root, args.output_root)
    except (OSError, ValueError, KeyError, TypeError, TooltipContractError) as exc:
        print(f"tooltip-t2 blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({key: result[key] for key in ("state", "implementation", "artifacts")}, sort_keys=True))
    return 0
