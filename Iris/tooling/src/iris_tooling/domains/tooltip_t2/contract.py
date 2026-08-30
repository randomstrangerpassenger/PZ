from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from iris_tooling.domains.tooltip_t1.contract import (
    CONTRACT_FILES, DECISION_CONTRACT, canonical_bytes, fulltype_set_sha256,
    git_subject, sha256_bytes, validate_execution_subject,
)
from iris_tooling.domains.tooltip_t1.models import TooltipContractError, validate_handoff_row

AUTHORITY = Path("Iris/_docs/authority/tooltip_t2")
CONTRACT = AUTHORITY / "tooltip_t2_static_projection_contract.json"
MANIFEST_SCHEMA = AUTHORITY / "tooltip_t2_projection_manifest.schema.json"
ROUTE = Path("Iris/_docs/authority/iris_current_route_index.json")
HANDOFF_FILES = ("subject_binding.json", "t2_handoff_input.jsonl", "t2_handoff_manifest.json")
CLOSEOUT = "axis_separated_final_closeout_record.json"
S1_TEMPLATE = "[{category_surface} - {primary_subcategory_surface}]"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TooltipContractError(message)


def decode_object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
        require(isinstance(value, dict), f"{label}: expected object")
        require(canonical_bytes(value) == raw, f"{label}: noncanonical JSON or invalid encoding")
        return value
    except (UnicodeError, ValueError) as exc:
        raise TooltipContractError(f"{label}: invalid encoding/JSON") from exc


def read_object(path: Path) -> dict[str, Any]:
    return decode_object(path.read_bytes(), str(path))


def external_path(repository_root: Path, path: Path) -> Path:
    resolved = path.resolve()
    # Reject the selected checkout and any other checkout of this repository.
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            cwd=repository_root, capture_output=True, text=True, check=True)
    roots = (repository_root.resolve(), Path(common.stdout.strip()).parent.resolve())
    require(not any(resolved == root or resolved.is_relative_to(root) for root in roots),
            "output/input root must be repository-external")
    lowered = [part.lower() for part in resolved.parts]
    require("zomboid" not in lowered and "projectzomboid" not in lowered
            and not any(lowered[i:i + 2] in (["media", "lua"], ["build", "package"])
                        for i in range(len(lowered) - 1)), "PZ auto-load/runtime/package root forbidden")
    return resolved


def empty_output(repository_root: Path, path: Path) -> Path:
    root = external_path(repository_root, path)
    require(not root.exists() or (root.is_dir() and not any(root.iterdir())),
            "output root must be new or empty")
    return root


def machine_subject(repository_root: Path) -> dict[str, str]:
    subject = git_subject(repository_root)
    validate_execution_subject(subject)
    return {key: subject[key] for key in ("commit", "tree")}


def load_contract(repository_root: Path) -> tuple[dict[str, Any], str]:
    value = json.loads((repository_root / CONTRACT).read_text(encoding="utf-8"))
    require(value.get("schema_version") == "iris-tooltip-t2-static-projection-v1", "T2 contract version mismatch")
    return value, sha256_bytes(canonical_bytes(value))


@dataclass(frozen=True)
class AcceptedInput:
    rows: tuple[dict[str, Any], ...]
    binding: dict[str, Any]


def read_handoff(root: Path, locator: dict[str, Any], *, support_count: int,
                 support_sha256: str) -> AcceptedInput:
    """Shared production/fixture decoder. Production always supplies the current locator."""
    require(all(locator.get(key) == expected for key, expected in {
        "adoption_state": "adopted", "contract_and_audit_axis": "complete",
        "formal_closeout_state": "complete", "T2_FULL_DATA_PROGRESSION": "OPEN",
        "production_t2_handoff": "present",
    }.items()), "current T1 handoff state is not adopted/complete/OPEN/present")
    require(root.resolve() == Path(locator["final_root"]).resolve(), "current handoff root mismatch")
    hashes = locator["artifact_sha256"]
    raw = {name: (root / name).read_bytes() for name in (*HANDOFF_FILES, CLOSEOUT)}
    require(all(sha256_bytes(data) == hashes.get(name) for name, data in raw.items()), "current handoff artifact hash mismatch")
    subject = decode_object(raw[HANDOFF_FILES[0]], "T1 subject")
    manifest = decode_object(raw[HANDOFF_FILES[2]], "T1 manifest")
    closeout = decode_object(raw[CLOSEOUT], "T1 closeout")
    expected_subject = locator["machine_subject"]
    require(set(expected_subject) == {"commit", "tree"}
            and all(re.fullmatch("[0-9a-f]{40}", str(value)) for value in expected_subject.values()), "T1 subject identity malformed")
    require({key: subject.get(key) for key in expected_subject} == expected_subject
            and manifest.get("subject") == expected_subject
            and closeout.get("subject") == expected_subject
            and subject.get("working_tree_clean") is True, "T1 subject binding mismatch")
    require(all(closeout.get(key) == locator[key] for key in (
        "contract_and_audit_axis", "formal_closeout_state", "T2_FULL_DATA_PROGRESSION", "production_t2_handoff")), "T1 final closeout state mismatch")
    fields = {"schema_version", "subject", "support_count", "support_sha256", "handoff_row_count",
              "handoff_fulltype_sha256", "handoff_input_sha256", "authority_contract_bundle_sha256", "candidate_run_receipt_sha256"}
    require(set(manifest) == fields and manifest["schema_version"] == "iris-tooltip-t2-handoff-manifest-v1", "T1 manifest schema mismatch")
    require(subject.get("schema_version") == "iris-tooltip-t1-subject-binding-v1", "T1 subject schema mismatch")
    identity_keys = ("commit", "tree", "generation_id", "input_sha256", "contract_sha256",
                     "layer2_menu_relation_sha256", "layer2_menu_relation_receipt_sha256")
    identity = {key: subject[key] for key in identity_keys if key in subject}
    require(subject.get("subject_identity_sha256") == sha256_bytes(canonical_bytes(identity)), "T1 subject identity hash mismatch")
    require(manifest["authority_contract_bundle_sha256"] == subject["contract_sha256"].get("authority_contract_bundle_sha256"), "T1 contract bundle mismatch")
    require(closeout.get("candidate_run_receipt", {}).get("sha256") == manifest["candidate_run_receipt_sha256"], "T1 candidate receipt binding mismatch")
    strict = closeout.get("strict_t2_handoff", {})
    require(strict.get("candidate_final_bytes_equal") is True
            and strict.get("artifact_sha256") == {name: hashes[name] for name in HANDOFF_FILES}, "T1 final artifact binding mismatch")
    data = raw["t2_handoff_input.jsonl"]
    rows = []
    for line in data.splitlines(keepends=True):
        row = decode_object(line, "handoff row")
        validate_handoff_row(row)
        require(row["subject_binding_ref"] == "subject_binding.json", "handoff subject reference mismatch")
        for slot in row["slots"]:
            for surface in slot["localized_surfaces"].values():
                require(bool(surface.strip()), "whitespace-only surface")
        rows.append(row)
    fulltypes = [row["full_type"] for row in rows]
    require(len(fulltypes) == support_count and len(set(fulltypes)) == support_count
            and fulltype_set_sha256(fulltypes) == support_sha256, "handoff exact-set/case/duplicate mismatch")
    require(manifest["support_count"] == manifest["handoff_row_count"] == strict.get("support_count") == strict.get("handoff_row_count") == support_count
            and manifest["support_sha256"] == manifest["handoff_fulltype_sha256"] == strict.get("support_sha256") == support_sha256
            and manifest["handoff_input_sha256"] == hashes["t2_handoff_input.jsonl"], "handoff count/hash mismatch")
    return AcceptedInput(tuple(sorted(rows, key=lambda row: row["full_type"])), {
        "subject": expected_subject, "artifact_sha256": {name: hashes[name] for name in HANDOFF_FILES},
        "authority_contract_bundle_sha256": manifest["authority_contract_bundle_sha256"],
        "support_count": support_count, "support_sha256": support_sha256,
    })


def admit(repository_root: Path, handoff_root: Path, contract: dict[str, Any]) -> AcceptedInput:
    root = external_path(repository_root, handoff_root)
    locator = json.loads((repository_root / ROUTE).read_text(encoding="utf-8"))["tooltip_t1_production_handoff"]
    accepted = read_handoff(root, locator, support_count=contract["support_count"], support_sha256=contract["support_sha256"])
    subject = read_object(root / "subject_binding.json")
    commit = accepted.binding["subject"]["commit"]
    def git(*args: str) -> bytes:
        result = subprocess.run(["git", *args], cwd=repository_root, capture_output=True, check=False)
        require(result.returncode == 0, "T1 successor Git binding unavailable")
        return result.stdout
    require(git("rev-parse", f"{commit}^{{tree}}").decode().strip() == accepted.binding["subject"]["tree"], "T1 Git tree mismatch")
    git("merge-base", "--is-ancestor", commit, "HEAD")
    bundle = []
    for path in CONTRACT_FILES:
        data = git("show", f"{commit}:{path.as_posix()}")
        value = json.loads(data.decode("utf-8"))
        # The accepted subject binds historical physical bytes, which can have
        # mixed line endings. Git cannot reconstruct those bytes. Verify the
        # committed contract through the T1 canonical bundle below, while the
        # locator and subject identity bind the original physical hash record.
        require(re.fullmatch("[0-9a-f]{64}", str(subject["contract_sha256"].get(path.as_posix()))) is not None,
                "T1 subject contract hash malformed")
        if path.name in {"tooltip_display_contract.json", "layer2_tooltip_input_contract.json"}:
            require(value.get("s1_surface_template") == S1_TEMPLATE, "T1 S1 category-title successor required")
        if path != DECISION_CONTRACT:
            bundle.append(f"{path.name}={sha256_bytes(canonical_bytes(value))}\n")
    require(sha256_bytes("".join(bundle).encode()) == accepted.binding["authority_contract_bundle_sha256"], "T1 successor contract bundle mismatch")
    return accepted


def check_surface(text: str, locale: str, contract: dict[str, Any], label: str) -> None:
    require(isinstance(text, str) and bool(text.strip()) and "\r" not in text and "\n" not in text, f"{label}: invalid logical line")
    try:
        text.encode("utf-8")
    except UnicodeError as exc:
        raise TooltipContractError(f"{label}: invalid UTF-8 surface") from exc
    rules = contract["lexical_guard"]
    comparable = text if locale == "ko" else text.lower()
    for literal in rules[locale + "_substring"]:
        require(literal not in comparable, f"{label}: forbidden rule {literal}")
    if locale == "en":
        for literal in rules["en_word_boundary"]:
            require(re.search(r"\b" + re.escape(literal) + r"\b", text, re.IGNORECASE) is None,
                    f"{label}: forbidden rule {literal}")
