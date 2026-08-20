from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.dvf_3_3_generation_contract import (
        DESCRIPTOR_NAME,
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
        sha256_file,
    )
    from tools.build.validate_dvf_3_3_complete_generation import (
        validate_complete_generation,
    )
else:
    from .dvf_3_3_generation_contract import (
        DESCRIPTOR_NAME,
        RENDERED_NAME,
        RUNTIME_MANIFEST_NAME,
        sha256_file,
    )
    from .validate_dvf_3_3_complete_generation import validate_complete_generation


LIVE_DATA_RELATIVE = "Iris/media/lua/client/Iris/Data"
LIVE_MANIFEST_RELATIVE = f"{LIVE_DATA_RELATIVE}/IrisLayer3DataChunks.lua"
LIVE_GENERATIONS_RELATIVE = f"{LIVE_DATA_RELATIVE}/IrisLayer3Generations"
LEGACY_DESCRIPTOR_RELATIVE = (
    "Iris/_docs/round3/validated_naturalization_current_runtime_adoption/"
    "current_generation_descriptor.json"
)
DEFAULT_R2_DECISION_RELATIVE = (
    "Iris/_docs/round3/iar_stateful_architecture_retirement/"
    "r2_runtime_layout_owner_decision.json"
)
GENERATION_MODULE_RE = re.compile(
    r"Iris/Data/IrisLayer3Generations/(?P<generation>dvf33-[0-9a-f]{64})/Chunks/"
)
FAILURE_STEPS = {
    "none",
    "candidate_copy",
    "generation_publish",
    "before_visibility_switch",
    "visibility_switch",
    "after_visibility_switch",
}


class GenerationInstallError(RuntimeError):
    def __init__(self, code: str, details: Any = None):
        message = code if details is None else f"{code}: {details}"
        super().__init__(message)
        self.code = code
        self.details = details


def _contained(repository_root: Path, relative: str) -> Path:
    path = (repository_root / relative).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise GenerationInstallError("INSTALL_PATH_ESCAPE", relative) from exc
    return path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_r2_decision(repository_root: Path, decision_path: Path) -> dict[str, Any]:
    decision_path = decision_path.resolve()
    decision = _load_json(decision_path)
    if decision.get("schema_version") != "iris-iar-retirement-r2-owner-decision-v1":
        raise GenerationInstallError("R2_DECISION_SCHEMA_INVALID")
    if decision.get("selection") != "A":
        raise GenerationInstallError("R2_DECISION_SELECTION_NOT_A")
    subject = decision.get("exact_subject", {})
    if not subject.get("commit") or not subject.get("tree"):
        raise GenerationInstallError("R2_DECISION_SUBJECT_MISSING")
    for record in subject.get("implementation_files", []):
        path = _contained(repository_root, record["path"])
        if not path.is_file() or sha256_file(path) != record.get("raw_byte_sha256"):
            raise GenerationInstallError(
                "R2_DECISION_IMPLEMENTATION_DRIFT",
                record["path"],
            )
    return {
        "selection": "A",
        "path": decision_path.as_posix(),
        "raw_byte_sha256": sha256_file(decision_path),
        "subject_commit": subject["commit"],
        "subject_tree": subject["tree"],
    }


def _manifest_generation_id(manifest_bytes: bytes) -> str | None:
    match = GENERATION_MODULE_RE.search(manifest_bytes.decode("utf-8"))
    return match.group("generation") if match else None


def current_generation_id(repository_root: Path) -> str:
    manifest = _contained(repository_root, LIVE_MANIFEST_RELATIVE)
    if not manifest.is_file():
        return "absent"
    generation_id = _manifest_generation_id(manifest.read_bytes())
    if generation_id:
        return generation_id
    legacy_descriptor = _contained(repository_root, LEGACY_DESCRIPTOR_RELATIVE)
    if legacy_descriptor.is_file():
        payload = _load_json(legacy_descriptor)
        identity = payload.get("transaction_id") or payload.get("schema_version")
        if identity:
            return f"legacy:{identity}"
    return f"legacy-manifest:{sha256_file(manifest)}"


def _candidate_mapping(
    generation_root: Path,
    live_generation_root: Path,
    generation_id: str,
) -> list[tuple[Path, Path]]:
    descriptor = _load_json(generation_root / DESCRIPTOR_NAME)
    mappings: list[tuple[Path, Path]] = []
    chunk_prefix = f"runtime/IrisLayer3Generations/{generation_id}/Chunks/"
    for record in descriptor["outputs"]:
        relative = record["path"]
        source = generation_root / relative
        if relative == RENDERED_NAME:
            target = live_generation_root / RENDERED_NAME
        elif relative == RUNTIME_MANIFEST_NAME:
            continue
        elif relative == "runtime/IrisLayer3DataChunkIndex.lua":
            target = live_generation_root / "IrisLayer3DataChunkIndex.lua"
        elif relative.startswith(chunk_prefix):
            target = live_generation_root / "Chunks" / relative.removeprefix(
                chunk_prefix
            )
        else:
            raise GenerationInstallError(
                "INSTALL_OUTPUT_MAPPING_UNSUPPORTED",
                relative,
            )
        mappings.append((source, target))
    mappings.append(
        (generation_root / DESCRIPTOR_NAME, live_generation_root / DESCRIPTOR_NAME)
    )
    return mappings


def _copy_generation(
    mappings: list[tuple[Path, Path]],
    stage_root: Path,
    live_generation_root: Path,
) -> None:
    for source, final_target in mappings:
        relative = final_target.relative_to(live_generation_root)
        target = stage_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if sha256_file(source) != sha256_file(target):
            raise GenerationInstallError(
                "INSTALL_CANDIDATE_COPY_HASH_MISMATCH",
                relative.as_posix(),
            )


def _validate_existing_generation(
    mappings: list[tuple[Path, Path]],
) -> None:
    for source, target in mappings:
        if not target.is_file():
            raise GenerationInstallError(
                "LIVE_GENERATION_FILE_MISSING",
                str(target),
            )
        if sha256_file(source) != sha256_file(target):
            raise GenerationInstallError(
                "LIVE_GENERATION_FILE_HASH_MISMATCH",
                str(target),
            )


def _atomic_replace_bytes(target: Path, data: bytes, suffix: str) -> None:
    temporary = target.with_name(f".{target.name}.{suffix}.tmp")
    if temporary.exists():
        raise GenerationInstallError("INSTALL_STALE_TEMP_PRESENT", str(temporary))
    temporary.write_bytes(data)
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def install_complete_generation(
    *,
    repository_root: Path,
    generation_root: Path,
    expected_predecessor_generation_id: str,
    r2_decision_path: Path | None = None,
    inject_failure: str = "none",
) -> dict[str, Any]:
    if inject_failure not in FAILURE_STEPS:
        raise GenerationInstallError("INSTALL_FAILURE_STEP_INVALID", inject_failure)
    repository_root = repository_root.resolve()
    generation_root = generation_root.resolve()
    decision_path = r2_decision_path or _contained(
        repository_root,
        DEFAULT_R2_DECISION_RELATIVE,
    )
    r2 = validate_r2_decision(repository_root, decision_path)
    validation = validate_complete_generation(
        repository_root=repository_root,
        generation_root=generation_root,
    )
    generation_id = validation["generation_id"]
    manifest_source = generation_root / RUNTIME_MANIFEST_NAME
    manifest_bytes = manifest_source.read_bytes()
    if _manifest_generation_id(manifest_bytes) != generation_id:
        raise GenerationInstallError("INSTALL_MANIFEST_GENERATION_MISMATCH")

    live_manifest = _contained(repository_root, LIVE_MANIFEST_RELATIVE)
    generations_root = _contained(repository_root, LIVE_GENERATIONS_RELATIVE)
    live_generation_root = generations_root / generation_id
    mappings = _candidate_mapping(
        generation_root,
        live_generation_root,
        generation_id,
    )
    current = current_generation_id(repository_root)
    if current == generation_id:
        if live_manifest.read_bytes() != manifest_bytes:
            raise GenerationInstallError("ALREADY_CURRENT_MANIFEST_BYTES_MISMATCH")
        _validate_existing_generation(mappings)
        return {
            "status": "NOOP_ALREADY_CURRENT",
            "generation_id": generation_id,
            "predecessor_generation_id": current,
            "protected_current_mutation_count": 0,
            "visibility_switch_count": 0,
            "r2_decision": r2,
        }
    if current != expected_predecessor_generation_id:
        raise GenerationInstallError(
            "EXPECTED_PREDECESSOR_MISMATCH",
            {"expected": expected_predecessor_generation_id, "actual": current},
        )

    generations_root.mkdir(parents=True, exist_ok=True)
    lock_path = generations_root / ".install.lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise GenerationInstallError("CONCURRENT_INSTALL_REJECTED") from exc
    os.write(lock_fd, generation_id.encode("ascii"))
    os.close(lock_fd)

    predecessor_manifest = live_manifest.read_bytes() if live_manifest.is_file() else None
    stage_root = generations_root / f".{generation_id}.stage"
    switched = False
    try:
        if stage_root.exists():
            raise GenerationInstallError("INSTALL_STALE_STAGE_PRESENT", str(stage_root))
        if live_generation_root.exists():
            _validate_existing_generation(mappings)
        else:
            stage_root.mkdir()
            _copy_generation(mappings, stage_root, live_generation_root)
            if inject_failure == "candidate_copy":
                raise GenerationInstallError("INJECTED_FAILURE_CANDIDATE_COPY")
            stage_root.replace(live_generation_root)
            if inject_failure == "generation_publish":
                raise GenerationInstallError("INJECTED_FAILURE_GENERATION_PUBLISH")
        _validate_existing_generation(mappings)
        if inject_failure == "before_visibility_switch":
            raise GenerationInstallError("INJECTED_FAILURE_BEFORE_VISIBILITY_SWITCH")
        if inject_failure == "visibility_switch":
            raise GenerationInstallError("INJECTED_FAILURE_VISIBILITY_SWITCH")
        live_manifest.parent.mkdir(parents=True, exist_ok=True)
        _atomic_replace_bytes(live_manifest, manifest_bytes, generation_id)
        switched = True
        if inject_failure == "after_visibility_switch":
            raise GenerationInstallError("INJECTED_FAILURE_AFTER_VISIBILITY_SWITCH")
        return {
            "status": "INSTALLED",
            "generation_id": generation_id,
            "predecessor_generation_id": current,
            "protected_current_mutation_count": 1,
            "visibility_switch_count": 1,
            "visibility_switch_primitive": "os.replace(single regular file)",
            "linearization_point": LIVE_MANIFEST_RELATIVE,
            "switch_atomicity": "requires_failure_injection_evidence",
            "predecessor_cleanup_performed": False,
            "rollback_available": predecessor_manifest is not None,
            "r2_decision": r2,
        }
    except Exception:
        if switched:
            if predecessor_manifest is None:
                live_manifest.unlink(missing_ok=True)
            else:
                _atomic_replace_bytes(
                    live_manifest,
                    predecessor_manifest,
                    "rollback",
                )
        raise
    finally:
        if stage_root.exists():
            shutil.rmtree(stage_root)
        lock_path.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--generation-root", type=Path, required=True)
    parser.add_argument("--expected-predecessor-generation-id", required=True)
    parser.add_argument("--r2-decision", type=Path)
    parser.add_argument("--inject-failure", choices=sorted(FAILURE_STEPS), default="none")
    args = parser.parse_args(argv)
    result = install_complete_generation(
        repository_root=args.repository_root,
        generation_root=args.generation_root,
        expected_predecessor_generation_id=args.expected_predecessor_generation_id,
        r2_decision_path=args.r2_decision,
        inject_failure=args.inject_failure,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
