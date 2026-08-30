from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
REPORTER = REPO / "Iris/validation/artifacts/inventory_artifact_lifecycle.py"
PROMOTER = REPO / "Iris/validation/artifacts/promote_lifecycle_evidence.py"
EXECUTOR = REPO / "Iris/validation/artifacts/archive_and_prune_artifacts.py"
AUDITOR = REPO / "Iris/validation/execution/audit_test_output_isolation.py"
SUCCESSOR_POLICY = (
    REPO
    / "Iris/validation/execution/contracts/isolated_command_output_policy.json"
)
GUARD_REFERENCE_POLICY = (
    REPO
    / "Iris/_docs/refactor/repository_runtime_lightweighting/current_surface_guard_successor_manifest.json"
)
DURABLE = Path("Iris/_docs/refactor/repository_runtime_lightweighting")
CANDIDATE = Path(
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
    "phase2_inventory/allowed_occurrence_inventory.json"
)
GIANT_RELATIVES = (
    CANDIDATE,
    Path(
        "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
        "phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl"
    ),
    Path(
        "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
        "phase3_adjudication/occurrence_adjudication_report.json"
    ),
    Path(
        "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/"
        "phase5_guard/current_surface_guard_report.json"
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_id(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def invoke(script: Path, *args: object, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(script), *map(str, args)],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def create_directory_junction(link: Path, target: Path) -> None:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise AssertionError("Windows PowerShell is required for the junction fixture")
    completed = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-Command",
            "& { param($link, $target) New-Item -ItemType Junction -Path $link -Target $target -ErrorAction Stop | Out-Null }",
            str(link),
            str(target),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)


def build_fixture(root: Path) -> tuple[Path, Path, dict[str, object]]:
    repo = (root / "checkout").resolve()
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "iris-tests@example.invalid")
    git(repo, "config", "user.name", "Iris Tests")
    (repo / ".gitattributes").write_text(
        "* text eol=lf\n",
        encoding="utf-8",
        newline="\n",
    )
    (repo / ".gitignore").write_text(
        "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/\n",
        encoding="utf-8",
    )
    for index, relative in enumerate(GIANT_RELATIVES, start=1):
        candidate = repo / relative
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(json.dumps({"candidate": index}) + "\n", encoding="utf-8")
    write_json(
        repo / "Iris/build/description/v2/staging/historical/legacy_guard_reference.json",
        {"path": CANDIDATE.as_posix()},
    )
    write_json(
        repo / "Iris/_archive/staging/legacy_guard_reference.json",
        {"path": CANDIDATE.as_posix()},
    )
    taxonomy = repo / "Iris/_docs/round3/round3_test_taxonomy.json"
    required = repo / "Iris/validation/execution/required_validations.json"
    fixture_test_id = "test_fixture.CurrentRouteFixture.test_passes"
    fixture_test = repo / "Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py"
    fixture_test.parent.mkdir(parents=True, exist_ok=True)
    fixture_test.write_text(
        (
            "GIANT_FIXTURE = 'allowed_occurrence_inventory.json'\n\n"
            "class CurrentRouteFixture:\n"
            "    def test_passes(self):\n"
            "        return None\n"
        ),
        encoding="utf-8",
    )
    write_json(
        taxonomy,
        {
            "rows": [
                {
                    "test_id": fixture_test_id,
                    "contract_class": "current",
                    "state": "ok",
                    "source_file": fixture_test.relative_to(repo).as_posix(),
                    "imported_build_modules": [],
                }
            ]
        },
    )
    write_json(required, {"required_tests": [{"test_id": fixture_test_id, "role": "fixture"}]})
    closure = repo / "Iris/_docs/round3/round3_active_core_closure.json"
    write_json(closure, {"schema_version": "fixture", "active_core": []})
    runner = repo / "Iris/validation/execution/run_required_contract_tests.py"
    runner.write_text("raise SystemExit(0)\n", encoding="utf-8")
    audit_script = repo / "Iris/validation/execution/audit_test_output_isolation.py"
    audit_script.parent.mkdir(parents=True, exist_ok=True)
    audit_script.write_bytes(AUDITOR.read_bytes())
    successor_policy = (
        repo
        / "Iris/validation/execution/contracts/isolated_command_output_policy.json"
    )
    successor_policy.parent.mkdir(parents=True, exist_ok=True)
    successor_policy.write_bytes(SUCCESSOR_POLICY.read_bytes())
    environment_authority = (
        repo / "Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json"
    )
    write_json(environment_authority, {"fixture": "immutable-environment-authority"})
    checkpoint_manifest = repo / DURABLE / "validation_checkpoint_manifest.json"
    write_json(
        checkpoint_manifest,
        {
            "schema_version": "iris_repository_runtime_lightweighting_validation_checkpoint_manifest_v1",
            "checkpoints": [],
        },
    )
    write_json(
        repo / DURABLE / "pre_delete_current_route_receipt.json",
        {
            "schema_version": "iris_repository_runtime_lightweighting_pre_delete_current_route_receipt_v1",
            "receipt_kind": "pre_delete_current_route",
            "status": "SUPERSEDED",
        },
    )
    write_json(
        repo / DURABLE / "protected_surface_successor_manifest.json",
        {
            "schema_version": "iris_repository_runtime_lightweighting_protected_surface_successor_v1",
            "authority": "repository_owner_user",
            "authorization_basis": "fixture owner authority",
            "predecessor": {"fixture": True},
            "revisions": [
                {
                    "revision_id": "fixture_predecessor_v1",
                    "track": "common",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "predecessor_commit": "fixture-predecessor",
                    "reason": "Fixture predecessor revision.",
                    "approved_activation_deltas": [],
                    "added_protected_rows": [],
                }
            ],
        },
    )
    git(repo, "add", ".")
    git(repo, "commit", "-m", "physical fixture")

    external = (root / "external").resolve()
    inventory = external / "inventory"
    subject = inventory / "subject.json"
    produced = invoke(
        REPORTER,
        "--repo",
        repo,
        "--subject-kind",
        "physical_capacity_subject",
        "--out",
        inventory / "artifact_role_manifest.jsonl",
        "--summary-out",
        inventory / "baseline_inventory.json",
        "--subject-receipt-out",
        subject,
        cwd=repo,
    )
    if produced.returncode != 0:
        raise AssertionError(produced.stderr)
    promoted = invoke(
        PROMOTER,
        "baseline",
        "--repo",
        repo,
        "--source-manifest",
        inventory / "artifact_role_manifest.jsonl",
        "--source-summary",
        inventory / "baseline_inventory.json",
        "--subject-receipt",
        subject,
        "--destination-root",
        repo / DURABLE,
        "--receipt-out",
        external / "promotion/baseline.json",
        cwd=repo,
    )
    if promoted.returncode != 0:
        raise AssertionError(promoted.stderr)
    git(repo, "add", DURABLE.as_posix())
    git(repo, "commit", "-m", "adopt baseline")

    taxonomy_payload = json.loads(taxonomy.read_text(encoding="utf-8"))
    taxonomy_payload["common_candidate_revision"] = "fixture-v1"
    write_json(taxonomy, taxonomy_payload)
    fixture_test.write_text(
        fixture_test.read_text(encoding="utf-8")
        + "\n# validated Common candidate fixture\n",
        encoding="utf-8",
        newline="\n",
    )
    successor_manifest = (
        repo
        / DURABLE
        / "current_surface_guard_successor_manifest.json"
    )
    successor_manifest.write_bytes(GUARD_REFERENCE_POLICY.read_bytes())
    git(repo, "add", taxonomy.relative_to(repo).as_posix())
    git(repo, "add", fixture_test.relative_to(repo).as_posix())
    git(repo, "add", successor_manifest.relative_to(repo).as_posix())
    git(repo, "commit", "-m", "adopt validated Common candidate delta")

    validation = (root / "validation-checkout").resolve()
    subprocess.run(
        ["git", "clone", "-q", str(repo), str(validation)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    validation_commit = git(validation, "rev-parse", "HEAD")
    validation_tree = git(validation, "rev-parse", "HEAD^{tree}")
    validation_runner = validation / "Iris/validation/execution/run_required_contract_tests.py"
    validation_taxonomy = validation / "Iris/_docs/round3/round3_test_taxonomy.json"
    validation_required = validation / "Iris/validation/execution/required_validations.json"
    validation_closure = validation / "Iris/_docs/round3/round3_active_core_closure.json"
    validation_auditor = (
        validation / "Iris/validation/execution/audit_test_output_isolation.py"
    )
    validation_environment_authority = (
        validation / "Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json"
    )
    audit_checkout = (root / "output-isolation-audit-checkout").resolve()
    subprocess.run(
        ["git", "clone", "-q", str(repo), str(audit_checkout)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    audit_commit = git(audit_checkout, "rev-parse", "HEAD")
    audit_tree = git(audit_checkout, "rev-parse", "HEAD^{tree}")
    if (audit_commit, audit_tree) != (validation_commit, validation_tree):
        raise AssertionError("audit and pre-delete validation clones differ")
    audit_runner = audit_checkout / "Iris/validation/execution/run_required_contract_tests.py"
    audit_auditor = (
        audit_checkout / "Iris/validation/execution/audit_test_output_isolation.py"
    )
    audit_successor_policy = (
        audit_checkout
        / "Iris/validation/execution/contracts/isolated_command_output_policy.json"
    )
    validation_subject = external / "pre-delete-subject.json"
    write_json(
        validation_subject,
        {
            "subject_kind": "common_pre_delete_validation_subject",
            "claim_id": "pre-delete-fixture",
            "commit": validation_commit,
            "tree": validation_tree,
            "repository_root": validation.as_posix(),
        },
    )
    audit_subject = external / "output-isolation-audit-subject.json"
    write_json(
        audit_subject,
        {
            "subject_kind": "current_route_output_isolation_audit_subject",
            "claim_id": "output-isolation-audit-fixture",
            "commit": audit_commit,
            "tree": audit_tree,
            "repository_root": audit_checkout.as_posix(),
        },
    )
    audit_root = external / "output-isolation-audit"
    static_inventory = audit_root / "static_inventory.json"
    inventory_result = invoke(
        audit_auditor,
        "inventory",
        "--repo", audit_checkout,
        "--taxonomy", "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations", "Iris/validation/execution/required_validations.json",
        "--out", static_inventory,
        cwd=audit_checkout,
    )
    if inventory_result.returncode != 0:
        raise AssertionError(inventory_result.stderr)
    audit_route_result = audit_root / "current_route.json"
    write_json(audit_route_result, {"status": "PASS", "summary": {"failed": 0, "errors": 0}})
    audit_command_root = external / "audit-commands"
    audit_command_root.mkdir(parents=True)
    dynamic_command = audit_command_root / "001-route-audit-dynamic-current.json"
    dynamic_spec = audit_command_root / "001-route-audit-dynamic-current.command.json"
    dynamic_argv = [
        "-B",
        "Iris/validation/execution/run_required_contract_tests.py",
        "--class",
        "current",
        "--enforce-current-build-closure",
        "--out",
        audit_route_result.as_posix(),
    ]
    write_json(
        dynamic_spec,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
            "executable": str(Path(sys.executable).resolve()),
            "argv": dynamic_argv,
            "working_directory": audit_checkout.as_posix(),
            "subject_receipt": audit_subject.as_posix(),
            "claim_id": "output-isolation-audit-fixture",
            "command_id": "001-route-audit-dynamic-current",
            "command_receipt": dynamic_command.as_posix(),
            "output_assertion": "checkout_unchanged",
        },
    )
    runner_blob = git(
        audit_checkout,
        "rev-parse",
        f"{audit_commit}:Iris/validation/execution/run_required_contract_tests.py",
    )
    write_json(
        dynamic_command,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_receipt_v1",
            "command_id": "001-route-audit-dynamic-current",
            "terminal_status": "pass",
            "native_exit_code": 0,
            "semantic_exit_code": 0,
            "claim_id": "output-isolation-audit-fixture",
            "working_directory": audit_checkout.as_posix(),
            "executable": str(Path(sys.executable).resolve()),
            "decoded_argv": dynamic_argv,
            "command_spec": {"path": dynamic_spec.as_posix(), "sha256": sha256(dynamic_spec)},
            "subject_receipt": {
                "path": audit_subject.as_posix(),
                "sha256": sha256(audit_subject),
                "execution_commit": audit_commit,
                "execution_tree": audit_tree,
            },
            "successor_policy": {
                "path": audit_successor_policy.resolve().as_posix(),
                "sha256": sha256(audit_successor_policy),
            },
            "invoked_repository_files": [
                {
                    "logical_path": "Iris/validation/execution/run_required_contract_tests.py",
                    "actual_path": audit_runner.resolve().as_posix(),
                    "execution_commit": audit_commit,
                    "git_blob_id": runner_blob,
                    "working_sha256": sha256(audit_runner),
                }
            ],
            "output_assertion": {
                "kind": "checkout_unchanged",
                "status": "pass",
                "delta": {
                    "changed_count": 0,
                    "tracked_delta_count": 0,
                    "untracked_delta_count": 0,
                    "ignored_delta_count": 0,
                    "unreadable_count": 0,
                },
            },
        },
    )
    audit_receipt = audit_root / "current_route_output_isolation_audit_receipt.json"
    seal_result = invoke(
        audit_auditor,
        "seal",
        "--repo", audit_checkout,
        "--static-inventory", static_inventory,
        "--route-result", audit_route_result,
        "--command-receipt-root", audit_command_root,
        "--out", audit_receipt,
        cwd=audit_checkout,
    )
    if seal_result.returncode != 0:
        raise AssertionError(seal_result.stderr)

    audit_verify_command = external / "commands/000-verify-current-route-output-isolation.json"
    audit_verify_command.parent.mkdir(parents=True, exist_ok=True)
    audit_verify_spec = external / "commands/000-verify-current-route-output-isolation.command.json"
    audit_verify_argv = [
        "-B",
        validation_auditor.resolve().as_posix(),
        "verify",
        "--repo",
        validation.as_posix(),
        "--taxonomy",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations",
        "Iris/validation/execution/required_validations.json",
        "--receipt",
        audit_receipt.as_posix(),
    ]
    write_json(
        audit_verify_spec,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
            "executable": str(Path(sys.executable).resolve()),
            "argv": audit_verify_argv,
            "working_directory": validation.as_posix(),
            "subject_receipt": validation_subject.as_posix(),
            "claim_id": "pre-delete-fixture",
            "command_id": "000-verify-current-route-output-isolation",
            "command_receipt": audit_verify_command.as_posix(),
            "output_assertion": "checkout_unchanged",
        },
    )
    audit_blob = git(
        validation,
        "rev-parse",
        f"{validation_commit}:Iris/validation/execution/audit_test_output_isolation.py",
    )
    write_json(
        audit_verify_command,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_receipt_v1",
            "command_id": "000-verify-current-route-output-isolation",
            "terminal_status": "pass",
            "native_exit_code": 0,
            "semantic_exit_code": 0,
            "claim_id": "pre-delete-fixture",
            "working_directory": validation.as_posix(),
            "executable": str(Path(sys.executable).resolve()),
            "decoded_argv": audit_verify_argv,
            "command_spec": {
                "path": audit_verify_spec.as_posix(),
                "sha256": sha256(audit_verify_spec),
            },
            "subject_receipt": {
                "path": validation_subject.as_posix(),
                "sha256": sha256(validation_subject),
                "execution_commit": validation_commit,
                "execution_tree": validation_tree,
            },
            "environment_authority": {
                "path": validation_environment_authority.resolve().as_posix(),
                "sha256": sha256(validation_environment_authority),
            },
            "invoked_repository_files": [
                {
                    "logical_path": "Iris/validation/execution/audit_test_output_isolation.py",
                    "actual_path": validation_auditor.resolve().as_posix(),
                    "execution_commit": validation_commit,
                    "git_blob_id": audit_blob,
                    "working_sha256": sha256(validation_auditor),
                }
            ],
            "output_assertion": {
                "kind": "checkout_unchanged",
                "status": "pass",
                "delta": {
                    "changed_count": 0,
                    "tracked_delta_count": 0,
                    "untracked_delta_count": 0,
                    "ignored_delta_count": 0,
                    "unreadable_count": 0,
                },
            },
        },
    )
    command = external / "commands/001-pre-delete-current-route.json"
    command.parent.mkdir(parents=True, exist_ok=True)
    route_result = external / "commands/pre-delete-current-route-result.json"
    write_json(route_result, {"status": "PASS", "summary": {"failed": 0, "errors": 0}})
    spec = external / "commands/001-pre-delete-current-route.command.json"
    argv = [
        "-B",
        "Iris/validation/execution/run_required_contract_tests.py",
        "--class",
        "current",
        "--enforce-current-build-closure",
        "--out",
        route_result.as_posix(),
    ]
    write_json(
        spec,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
            "executable": str(Path(sys.executable).resolve()),
            "argv": argv,
            "working_directory": validation.as_posix(),
            "subject_receipt": validation_subject.as_posix(),
            "claim_id": "pre-delete-fixture",
            "command_id": "001-pre-delete-current-route",
            "command_receipt": command.as_posix(),
            "output_assertion": "checkout_unchanged",
        },
    )
    write_json(
        command,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_receipt_v1",
            "command_id": "001-pre-delete-current-route",
            "terminal_status": "pass",
            "native_exit_code": 0,
            "semantic_exit_code": 0,
            "claim_id": "pre-delete-fixture",
            "working_directory": validation.as_posix(),
            "executable": str(Path(sys.executable).resolve()),
            "decoded_argv": argv,
            "command_spec": {"path": spec.as_posix(), "sha256": sha256(spec)},
            "subject_receipt": {
                "path": validation_subject.as_posix(),
                "sha256": sha256(validation_subject),
                "execution_commit": validation_commit,
                "execution_tree": validation_tree,
            },
            "invoked_repository_files": [
                {
                    "logical_path": "Iris/validation/execution/run_required_contract_tests.py",
                    "actual_path": validation_runner.resolve().as_posix(),
                    "execution_commit": validation_commit,
                    "git_blob_id": runner_blob,
                    "working_sha256": sha256(validation_runner),
                }
            ],
            "environment_authority": {
                "path": validation_environment_authority.resolve().as_posix(),
                "sha256": sha256(validation_environment_authority),
            },
            "output_assertion": {
                "kind": "checkout_unchanged",
                "status": "pass",
                "delta": {
                    "changed_count": 0,
                    "tracked_delta_count": 0,
                    "untracked_delta_count": 0,
                    "ignored_delta_count": 0,
                    "unreadable_count": 0,
                },
            },
        },
    )
    command_set = [
        {
            "command_id": "000-verify-current-route-output-isolation",
            "path": audit_verify_command.as_posix(),
            "sha256": sha256(audit_verify_command),
        },
        {
            "command_id": "001-pre-delete-current-route",
            "path": command.as_posix(),
            "sha256": sha256(command),
        }
    ]
    pre_delete = repo / DURABLE / "pre_delete_current_route_receipt.json"
    write_json(
        pre_delete,
        {
            "schema_version": "iris_repository_runtime_lightweighting_pre_delete_current_route_receipt_v1",
            "receipt_kind": "pre_delete_current_route",
            "status": "PASS",
            "protected_surface_revision_id": "pre_delete_fixture_revision_v1",
            "validated_subject": {
                "subject_kind": "common_pre_delete_validation_subject",
                "claim_id": "pre-delete-fixture",
                "commit": validation_commit,
                "tree": validation_tree,
                "repository_root": validation.as_posix(),
                "subject_receipt_path": validation_subject.as_posix(),
                "subject_receipt_sha256": sha256(validation_subject),
            },
            "taxonomy": {
                "path": validation_taxonomy.resolve().as_posix(),
                "sha256": sha256(validation_taxonomy),
            },
            "required_validations": {
                "path": validation_required.resolve().as_posix(),
                "sha256": sha256(validation_required),
            },
            "active_core_closure": {
                "path": validation_closure.resolve().as_posix(),
                "sha256": sha256(validation_closure),
            },
            "environment_authority": {
                "path": validation_environment_authority.resolve().as_posix(),
                "sha256": sha256(validation_environment_authority),
            },
            "output_isolation_audit": {
                "path": audit_receipt.as_posix(),
                "sha256": sha256(audit_receipt),
            },
            "command_receipts": [
                {"path": audit_verify_command.as_posix(), "sha256": sha256(audit_verify_command)},
                {"path": command.as_posix(), "sha256": sha256(command)},
            ],
            "command_receipt_set_sha256": hashlib.sha256(canonical_bytes(command_set)).hexdigest(),
            "current_route_result": {
                "path": route_result.as_posix(),
                "sha256": sha256(route_result),
            },
            "checkout_clean_before": True,
            "checkout_clean_after": True,
        },
    )
    checkpoint = json.loads(checkpoint_manifest.read_text(encoding="utf-8"))
    checkpoint["checkpoints"].append(
        {
            "checkpoint_id": "common_pre_delete",
            "subject_kind": "common_pre_delete_validation_subject",
            "claim_id": "pre-delete-fixture",
            "commit": validation_commit,
            "tree": validation_tree,
            "clean_checkout_receipt": {
                "path": validation_subject.as_posix(),
                "sha256": sha256(validation_subject),
            },
            "required_receipt": {
                "path": (DURABLE / "pre_delete_current_route_receipt.json").as_posix(),
                "sha256": sha256(pre_delete),
            },
            "taxonomy": {
                "path": "Iris/_docs/round3/round3_test_taxonomy.json",
                "sha256": sha256(validation_taxonomy),
            },
            "required_validations": {
                "path": "Iris/validation/execution/required_validations.json",
                "sha256": sha256(validation_required),
            },
            "active_core_closure": {
                "path": "Iris/_docs/round3/round3_active_core_closure.json",
                "sha256": sha256(validation_closure),
            },
            "environment_authority": {
                "path": "Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json",
                "sha256": sha256(validation_environment_authority),
            },
            "output_isolation_audit": {
                "path": audit_receipt.as_posix(),
                "sha256": sha256(audit_receipt),
            },
            "command_receipt_set_sha256": hashlib.sha256(canonical_bytes(command_set)).hexdigest(),
        }
    )
    write_json(checkpoint_manifest, checkpoint)
    protected_manifest = repo / DURABLE / "protected_surface_successor_manifest.json"
    protected = json.loads(protected_manifest.read_text(encoding="utf-8"))
    protected["revisions"].append(
        {
            "revision_id": "pre_delete_fixture_revision_v1",
            "track": "common",
            "owner": "repository_owner_user",
            "approved": True,
            "predecessor_commit": validation_commit,
            "reason": "Bind the fixture STEP 8 receipt and checkpoint successor.",
            "approved_activation_deltas": [],
            "added_protected_rows": [
                {
                    "path": pre_delete.relative_to(repo).as_posix(),
                    "before_git_blob_id": git(
                        validation,
                        "rev-parse",
                        f"HEAD:{pre_delete.relative_to(repo).as_posix()}",
                    ),
                    "before_sha256_lf": sha256(validation / pre_delete.relative_to(repo)),
                    "expected_git_blob_id": git_blob_id(pre_delete.read_bytes()),
                    "after_sha256_lf": sha256(pre_delete),
                    "role": "common_track_pre_delete_current_route_evidence",
                    "writer": "repository_runtime_lightweighting_step8_checkpoint_writer",
                    "consumers": [
                        "archive_operation",
                        "delete_prerequisite_gate",
                        "terminal_closeout",
                        "repository_maintainers",
                    ],
                    "owner": "repository_owner_user",
                    "reason": "Protect the refreshed fixture STEP 8 receipt.",
                },
                {
                    "path": checkpoint_manifest.relative_to(repo).as_posix(),
                    "before_git_blob_id": git(
                        validation,
                        "rev-parse",
                        f"HEAD:{checkpoint_manifest.relative_to(repo).as_posix()}",
                    ),
                    "before_sha256_lf": sha256(validation / checkpoint_manifest.relative_to(repo)),
                    "expected_git_blob_id": git_blob_id(checkpoint_manifest.read_bytes()),
                    "after_sha256_lf": sha256(checkpoint_manifest),
                    "role": "common_track_validation_checkpoint_manifest",
                    "writer": "repository_runtime_lightweighting_step8_checkpoint_writer",
                    "consumers": [
                        "archive_operation",
                        "delete_prerequisite_gate",
                        "selected_track_validation",
                        "terminal_closeout",
                        "repository_maintainers",
                    ],
                    "owner": "repository_owner_user",
                    "reason": "Protect the appended fixture STEP 8 checkpoint.",
                },
            ],
        }
    )
    write_json(protected_manifest, protected)
    git(
        repo,
        "add",
        pre_delete.relative_to(repo).as_posix(),
        checkpoint_manifest.relative_to(repo).as_posix(),
        protected_manifest.relative_to(repo).as_posix(),
    )
    git(repo, "commit", "-m", "seal pre-delete route")

    rows = [
        json.loads(line)
        for line in (repo / DURABLE / "artifact_role_manifest.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    candidate_row = next(row for row in rows if row["path"] == CANDIDATE.as_posix())
    return repo, external, candidate_row
