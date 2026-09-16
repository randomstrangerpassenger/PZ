"""Disposable checkout materialization and output seed lifecycle."""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
from pathlib import Path
from typing import Any

from Iris.validation.execution.checkout_environment import (
    CleanCheckoutError,
    canonical_json_bytes,
    ensure_external_root,
    sha256_bytes,
    sha256_file,
    tracked_paths,
)


from Iris.validation.execution.process_results import _raise_process_failure, _run_subprocess


def _require_disjoint_external_roots(
    repo: Path,
    work_root: Path,
    result_root: Path,
) -> None:
    ensure_external_root(repo, work_root)
    ensure_external_root(repo, result_root)
    for left, right in ((work_root, result_root), (result_root, work_root)):
        try:
            left.relative_to(right)
        except ValueError:
            continue
        raise CleanCheckoutError(
            f"work and result roots must be disjoint: {work_root}, {result_root}"
        )


def _require_empty_directory(path: Path, role: str) -> None:
    if any(path.iterdir()):
        raise CleanCheckoutError(f"{role} must be empty before execution: {path}")


def _safe_checkout_target(checkout: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise CleanCheckoutError(
            f"unsafe repository-relative materialization target: {relative_path}"
        )
    target = (checkout / relative).resolve()
    try:
        target.relative_to(checkout)
    except ValueError as exc:
        raise CleanCheckoutError(
            f"materialization target escapes checkout: {relative_path}"
        ) from exc
    return target


def _materialize_frozen_predecessor_fixture(
    checkout: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    fixture_contract = contract["bootstrap"][
        "frozen_predecessor_fixture"
    ]
    manifest_path = _safe_checkout_target(
        checkout, fixture_contract["manifest_path"]
    )
    if sha256_file(manifest_path) != fixture_contract["manifest_sha256"]:
        raise CleanCheckoutError("frozen predecessor fixture manifest hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version")
        != (
            "dvf-3-3-registry-authority-canonical-closure-"
            "frozen-predecessor-fixture-v1"
        )
        or manifest.get("status") != "PASS"
        or manifest.get("authority_claimed") is not False
        or manifest.get("current_route_authority_claimed") is not False
        or manifest.get("candidate_discard_required") is not True
    ):
        raise CleanCheckoutError(
            "frozen predecessor fixture authority boundary is invalid"
        )
    partition_name = fixture_contract["materialized_partition"]
    payload_paths = manifest.get(partition_name)
    if not isinstance(payload_paths, list) or not payload_paths:
        raise CleanCheckoutError(
            f"frozen predecessor partition is empty: {partition_name}"
        )
    rows_by_payload = {
        row["payload_path"]: row
        for row in manifest.get("rows", [])
        if isinstance(row, dict) and isinstance(row.get("payload_path"), str)
    }
    if set(payload_paths) - set(rows_by_payload):
        raise CleanCheckoutError(
            "frozen predecessor partition references an unknown payload"
        )
    fixture_root = manifest_path.parent
    materialized_rows: list[dict[str, Any]] = []
    for payload_relative in payload_paths:
        row = rows_by_payload[payload_relative]
        if (
            row.get("role") != "frozen_predecessor_input"
            or row.get("isolated_candidate_only") is not True
            or row.get("live_materialization_allowed") is not False
        ):
            raise CleanCheckoutError(
                f"invalid frozen predecessor row: {payload_relative}"
            )
        payload = _safe_checkout_target(
            fixture_root, payload_relative
        )
        if (
            not payload.is_file()
            or sha256_file(payload) != row.get("sha256")
            or payload.stat().st_size != row.get("byte_length")
        ):
            raise CleanCheckoutError(
                f"frozen predecessor payload mismatch: {payload_relative}"
            )
        target = _safe_checkout_target(checkout, row["target_path"])
        previous_sha256 = sha256_file(target) if target.is_file() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(payload, target)
        if sha256_file(target) != row["sha256"]:
            raise CleanCheckoutError(
                f"frozen predecessor copy mismatch: {row['target_path']}"
            )
        materialized_rows.append(
            {
                "target_path": row["target_path"],
                "sha256": row["sha256"],
                "byte_length": row["byte_length"],
                "preexisting_sha256": previous_sha256,
                "authority_class": fixture_contract["authority_class"],
                "producer": (
                    "tracked_hash_bound_frozen_predecessor_fixture"
                ),
            }
        )
    return {
        "status": "PASS",
        "manifest_path": fixture_contract["manifest_path"],
        "manifest_sha256": fixture_contract["manifest_sha256"],
        "partition": partition_name,
        "materialized_file_count": len(materialized_rows),
        "rows": materialized_rows,
    }


def _materialize_menu_inputs(source: Path, checkout: Path, contract: dict, environment: dict, result_root: Path) -> None:
    """Provide the declared local ZIP; explicit candidate refs remain opt-in."""
    inputs = contract["bootstrap"].get("menu_inputs")
    if inputs is None:
        return
    import zipfile

    for name in ("IRIS_REFACTOR_MENU_INPUTS", "IRIS_MENU_TOOLTIP_CANDIDATE",
                 "IRIS_MENU_TOOLTIP_BINDING", "IRIS_SHARED_MENU_VALIDATION",
                 "IRIS_MENU_RESUME_PACKAGE"):
        environment.pop(name, None)
    if set(inputs) not in ({"tooltip"}, {"tooltip", "description", "blocks"}):
        raise CleanCheckoutError("invalid Menu bootstrap input set")
    for role, ref in inputs.items():
        if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
            raise CleanCheckoutError(f"invalid Menu bootstrap ref: {role}")
        path = _safe_checkout_target(source, ref["path"])
        if not path.is_file() or sha256_file(path) != ref["sha256"]:
            raise CleanCheckoutError(f"Menu bootstrap input hash mismatch: {role}")
        target = _safe_checkout_target(checkout, ref["path"])
        if role == "tooltip":
            if not ref["path"].startswith(".tmp/") or target.exists():
                raise CleanCheckoutError("Menu ZIP requires an absent local fixture target")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        if not target.is_file() or sha256_file(target) != ref["sha256"]:
            raise CleanCheckoutError(f"Menu bootstrap checkout mismatch: {role}")
    if "description" in inputs:
        refs = {role: inputs[role] for role in ("description", "blocks")}
        refs_path = result_root / "menu_inputs.json"
        with refs_path.open("x", encoding="utf-8") as handle:
            json.dump(refs, handle, ensure_ascii=False)
        with zipfile.ZipFile(_safe_checkout_target(checkout, inputs["tooltip"]["path"])) as archive:
            owner = json.loads(archive.read("Iris/media/lua/client/Iris/Data/IrisTooltipOwner.json"))
        environment["IRIS_REFACTOR_MENU_INPUTS"] = str(refs_path)
        environment["IRIS_MENU_TOOLTIP_CANDIDATE"] = inputs["tooltip"]["path"]
        environment["IRIS_MENU_TOOLTIP_BINDING"] = json.dumps({
            "repository": str(checkout), "description": inputs["description"],
            "tooltip": inputs["tooltip"], "owner": owner["product_id"],
        }, ensure_ascii=False)


def _materialize_package_runtime_mirror(
    source_repo: Path,
    commit: str,
    checkout: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    mirror = contract["bootstrap"]["package_runtime_mirror"]
    source_pointer_relative = mirror["source_pointer"]
    source_pointer = _safe_checkout_target(checkout, source_pointer_relative)
    if not source_pointer.is_file():
        raise CleanCheckoutError("tracked package mirror pointer is missing")
    pointer_text = source_pointer.read_text(encoding="utf-8")
    generation_matches = re.findall(
        r'generation_id\s*=\s*"(dvf33-[0-9a-f]{64})"',
        pointer_text,
    )
    referenced_generations = sorted(
        set(re.findall(r"dvf33-[0-9a-f]{64}", pointer_text))
    )
    if (
        len(generation_matches) != 1
        or referenced_generations != generation_matches
    ):
        raise CleanCheckoutError("package mirror current pointer is invalid")
    generation_id = generation_matches[0]
    source_directory_relative = mirror["source_directory"].replace(
        "<generation_id>", generation_id
    )
    source_directory = _safe_checkout_target(
        checkout, source_directory_relative
    )
    if not source_directory.is_dir():
        raise CleanCheckoutError("tracked package mirror generation is missing")
    source_files = [source_pointer, *sorted(source_directory.rglob("*"))]
    source_files = [path for path in source_files if path.is_file()]
    tracked = set(tracked_paths(source_repo, commit))
    source_relatives = [
        path.relative_to(checkout).as_posix() for path in source_files
    ]
    untracked_sources = sorted(set(source_relatives) - tracked)
    if untracked_sources:
        raise CleanCheckoutError(
            "package mirror source is not tracked at the subject commit: "
            + ", ".join(untracked_sources)
        )

    target_pointer = _safe_checkout_target(
        checkout, mirror["target_pointer"]
    )
    target_directory_relative = mirror["target_directory"].replace(
        "<generation_id>", generation_id
    )
    target_directory = _safe_checkout_target(
        checkout, target_directory_relative
    )
    target_pointer.parent.mkdir(parents=True, exist_ok=True)
    target_directory.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    destinations = [
        target_pointer,
        *[
            target_directory / path.relative_to(source_directory)
            for path in source_files[1:]
        ],
    ]
    for source, target in zip(source_files, destinations, strict=True):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        source_hash = sha256_file(source)
        if sha256_file(target) != source_hash:
            raise CleanCheckoutError(
                f"package mirror copy mismatch: {target}"
            )
        rows.append(
            {
                "source_path": source.relative_to(checkout).as_posix(),
                "target_path": target.relative_to(checkout).as_posix(),
                "sha256": source_hash,
                "byte_length": source.stat().st_size,
                "authority_class": mirror["authority_class"],
                "producer": mirror["producer"],
            }
        )
    return {
        "status": "PASS",
        "generation_id": generation_id,
        "materialized_file_count": len(rows),
        "rows": rows,
    }


def _remove_disposable_checkout(path: Path) -> None:
    removal_path: str | Path = path
    if os.name == "nt":
        resolved = str(path.resolve())
        if resolved.startswith("\\\\"):
            removal_path = "\\\\?\\UNC\\" + resolved[2:]
        else:
            removal_path = "\\\\?\\" + resolved

    def make_writable_and_retry(
        function: Any,
        target: str,
        _: Any,
    ) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    shutil.rmtree(removal_path, onerror=make_writable_and_retry)


def _materialize_current_output_seed(
    checkout: Path,
    output_root: Path,
    python_executable: Path,
    environment: dict[str, str],
    baseline_seed_files: list[dict[str, Any]],
) -> dict[str, Any]:
    if output_root.exists():
        raise CleanCheckoutError(f"current output seed root already exists: {output_root}")
    output_root.mkdir(parents=True)
    if not baseline_seed_files:
        raise CleanCheckoutError("current output baseline seed set is empty")
    baseline_root = checkout / "Iris/build/baseline/current_output_seed_v1"
    expected_sources = {str(row["source"]) for row in baseline_seed_files}
    actual_sources = {
        path.relative_to(checkout).as_posix()
        for path in baseline_root.iterdir()
        if path.is_file()
    }
    if actual_sources != expected_sources:
        raise CleanCheckoutError("current output baseline seed exact set mismatch")
    destinations: set[str] = set()
    for row in baseline_seed_files:
        source = checkout / str(row["source"])
        destination = str(row["destination"])
        if (
            destination != Path(destination).name
            or destination in destinations
            or not source.is_file()
            or source.stat().st_size != row["bytes"]
            or sha256_file(source) != row["sha256"]
        ):
            raise CleanCheckoutError(
                f"current output baseline seed binding mismatch: {destination}"
            )
        destinations.add(destination)
        shutil.copyfile(source, output_root / destination)
    seed_environment = dict(environment)
    seed_environment["IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"] = str(output_root)
    commands = [
        [
            str(python_executable),
            "-B",
            "-m",
            "iris_tooling",
            "--repository-root",
            str(checkout),
            "rightclick",
        ],
        [str(python_executable), "-B", "Iris/build/recipe_evidence_pipeline.py"],
        [
            str(python_executable),
            "-B",
            "Iris/build/tools/pipeline/build_usecases_by_fulltype.py",
        ],
    ]
    for command in commands:
        completed = _run_subprocess(command, cwd=checkout, environment=seed_environment)
        _raise_process_failure("current output seed producer", command, completed)

    rows = [
        {
            "path": path.relative_to(output_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(output_root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    if {row["destination"] for row in baseline_seed_files} - {
        row["path"] for row in rows
    }:
        raise CleanCheckoutError("current output seed is incomplete after producers")
    identity_bytes = canonical_json_bytes(rows)
    return {
        "schema_version": "iris-clean-checkout-current-output-seed-v1",
        "file_count": len(rows),
        "content_identity_sha256": sha256_bytes(identity_bytes),
        "producer_invocation_count": len(commands),
        "rows": rows,
    }


def _publish_current_output_seed(
    checkout: Path,
    final_root: Path,
    python_executable: Path,
    environment: dict[str, str],
    baseline_seed_files: list[dict[str, Any]],
) -> dict[str, Any]:
    staging_root = final_root.with_name(final_root.name + ".staging")
    if staging_root.exists() or final_root.exists():
        raise CleanCheckoutError("current output seed staging/final root already exists")
    identity = _materialize_current_output_seed(
        checkout,
        staging_root,
        python_executable,
        environment,
        baseline_seed_files,
    )
    staging_root.replace(final_root)
    published_rows = [
        {
            "path": path.relative_to(final_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(final_root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    if sha256_bytes(canonical_json_bytes(published_rows)) != identity[
        "content_identity_sha256"
    ]:
        raise CleanCheckoutError("published current output seed identity mismatch")
    return identity


def _clone_current_output_seed(
    final_root: Path,
    destination: Path,
    expected_identity_sha256: str,
) -> None:
    if destination.exists():
        raise CleanCheckoutError(f"current output seed clone already exists: {destination}")
    shutil.copytree(final_root, destination)
    rows = [
        {
            "path": path.relative_to(destination).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(destination.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    if sha256_bytes(canonical_json_bytes(rows)) != expected_identity_sha256:
        raise CleanCheckoutError("case-local current output seed clone identity mismatch")
