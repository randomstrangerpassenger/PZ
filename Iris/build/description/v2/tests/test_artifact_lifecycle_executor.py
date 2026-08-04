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
REPORTER = REPO / "Iris/validation/residual_refactor/report_artifact_lifecycle.py"
PROMOTER = REPO / "Iris/validation/residual_refactor/promote_artifact_lifecycle_evidence.py"
EXECUTOR = REPO / "Iris/validation/residual_refactor/execute_artifact_lifecycle.py"
AUDITOR = REPO / "Iris/validation/clean_checkout/audit_current_route_output_isolation.py"
SUCCESSOR_POLICY = (
    REPO
    / "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
)
DURABLE = Path("Iris/_docs/refactor/repository_runtime_lightweighting")
CANDIDATE = Path(
    "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/"
    "phase2_inventory/allowed_occurrence_inventory.json"
)
GIANT_RELATIVES = (
    CANDIDATE,
    Path(
        "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/"
        "phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl"
    ),
    Path(
        "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/"
        "phase3_adjudication/occurrence_adjudication_report.json"
    ),
    Path(
        "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/"
        "phase5_guard/current_surface_guard_report.json"
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def create_file_symlink(link: Path, target: Path) -> None:
    powershell = shutil.which("powershell")
    if powershell is None:
        raise AssertionError("Windows PowerShell is required for the file-symlink fixture")
    completed = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-Command",
            "& { param($link, $target) New-Item -ItemType SymbolicLink -Path $link -Target $target -ErrorAction Stop | Out-Null }",
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
        "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/\n",
        encoding="utf-8",
    )
    for index, relative in enumerate(GIANT_RELATIVES, start=1):
        candidate = repo / relative
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(json.dumps({"candidate": index}) + "\n", encoding="utf-8")
    taxonomy = repo / "Iris/_docs/round3/round3_test_taxonomy.json"
    required = repo / "Iris/_docs/round3/current_route_required_validations.json"
    fixture_test_id = "test_fixture.CurrentRouteFixture.test_passes"
    fixture_test = repo / "Iris/build/description/v2/tests/test_fixture.py"
    fixture_test.parent.mkdir(parents=True, exist_ok=True)
    fixture_test.write_text(
        "class CurrentRouteFixture:\n    def test_passes(self):\n        return None\n",
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
    runner = repo / "Iris/_docs/round3/round3_run_contract_tests.py"
    runner.write_text("raise SystemExit(0)\n", encoding="utf-8")
    audit_script = repo / "Iris/validation/clean_checkout/audit_current_route_output_isolation.py"
    audit_script.parent.mkdir(parents=True, exist_ok=True)
    audit_script.write_bytes(AUDITOR.read_bytes())
    successor_policy = (
        repo
        / "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
    )
    successor_policy.parent.mkdir(parents=True, exist_ok=True)
    successor_policy.write_bytes(SUCCESSOR_POLICY.read_bytes())
    environment_authority = (
        repo / "Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json"
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
    write_json(
        successor_manifest,
        {
            "schema_version": (
                "iris_repository_runtime_lightweighting_"
                "current_surface_guard_successor_v1"
            ),
            "fixture": "validated Common candidate addition",
        },
    )
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
    validation_runner = validation / "Iris/_docs/round3/round3_run_contract_tests.py"
    validation_taxonomy = validation / "Iris/_docs/round3/round3_test_taxonomy.json"
    validation_required = validation / "Iris/_docs/round3/current_route_required_validations.json"
    validation_closure = validation / "Iris/_docs/round3/round3_active_core_closure.json"
    validation_auditor = (
        validation / "Iris/validation/clean_checkout/audit_current_route_output_isolation.py"
    )
    validation_environment_authority = (
        validation / "Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json"
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
    audit_runner = audit_checkout / "Iris/_docs/round3/round3_run_contract_tests.py"
    audit_auditor = (
        audit_checkout / "Iris/validation/clean_checkout/audit_current_route_output_isolation.py"
    )
    audit_successor_policy = (
        audit_checkout
        / "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
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
        "--required-validations", "Iris/_docs/round3/current_route_required_validations.json",
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
        "Iris/_docs/round3/round3_run_contract_tests.py",
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
        f"{audit_commit}:Iris/_docs/round3/round3_run_contract_tests.py",
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
                    "logical_path": "Iris/_docs/round3/round3_run_contract_tests.py",
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
        "Iris/_docs/round3/current_route_required_validations.json",
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
        f"{validation_commit}:Iris/validation/clean_checkout/audit_current_route_output_isolation.py",
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
                    "logical_path": "Iris/validation/clean_checkout/audit_current_route_output_isolation.py",
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
        "Iris/_docs/round3/round3_run_contract_tests.py",
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
                    "logical_path": "Iris/_docs/round3/round3_run_contract_tests.py",
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
                "path": "Iris/_docs/round3/current_route_required_validations.json",
                "sha256": sha256(validation_required),
            },
            "active_core_closure": {
                "path": "Iris/_docs/round3/round3_active_core_closure.json",
                "sha256": sha256(validation_closure),
            },
            "environment_authority": {
                "path": "Iris/validation/clean_checkout/authority/phase0_ratification_attempt_0002.json",
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
    git(repo, "add", pre_delete.relative_to(repo).as_posix(), checkpoint_manifest.relative_to(repo).as_posix())
    git(repo, "commit", "-m", "seal pre-delete route")

    rows = [
        json.loads(line)
        for line in (repo / DURABLE / "artifact_role_manifest.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    candidate_row = next(row for row in rows if row["path"] == CANDIDATE.as_posix())
    return repo, external, candidate_row


class ArtifactLifecycleExecutorTest(unittest.TestCase):
    def test_full_chain_is_receipt_bound_and_exact_leaf_delete_is_recoverable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-executor-") as temporary:
            root = Path(temporary)
            repo, external, candidate = build_fixture(root)
            durable = repo / DURABLE
            pre_delete = durable / "pre_delete_current_route_receipt.json"
            selection = external / "owner-selection.json"
            baseline_promotion = durable / "baseline_promotion_receipt.json"
            write_json(
                selection,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_exact_archive_selection_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "physical_resolved_root": repo.as_posix(),
                    "baseline_run_identity": json.loads(
                        (durable / "baseline_inventory.json").read_text(encoding="utf-8")
                    )["run_identity"],
                    "baseline_promotion_receipt_sha256": sha256(baseline_promotion),
                    "pre_delete_current_route_receipt_sha256": sha256(pre_delete),
                    "rows": [
                        {
                            "logical_artifact_id": candidate["logical_artifact_id"],
                            "path": candidate["path"],
                            "sha256": candidate["sha256"],
                            "size_bytes": candidate["size_bytes"],
                        }
                    ],
                },
            )

            checkpoint_manifest = durable / "validation_checkpoint_manifest.json"
            audit_receipt_path = external / "output-isolation-audit/current_route_output_isolation_audit_receipt.json"
            audit_receipt_bytes = audit_receipt_path.read_bytes()
            tampered_audit = json.loads(audit_receipt_bytes.decode("utf-8"))
            tampered_audit["status"] = "FAIL"
            write_json(audit_receipt_path, tampered_audit)
            rejected_audit_receipt = invoke(
                EXECUTOR,
                "dry-run",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--promotion-receipt", baseline_promotion,
                "--pre-delete-route-receipt", pre_delete,
                "--selection", selection,
                "--manifest-out", external / "rejected-audit-receipt/operation.json",
                "--receipt-out", external / "rejected-audit-receipt/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_audit_receipt.returncode, 0)
            self.assertIn("output-isolation audit identity", rejected_audit_receipt.stderr)
            audit_receipt_path.write_bytes(audit_receipt_bytes)

            pre_delete_bytes = pre_delete.read_bytes()
            checkpoint_bytes = checkpoint_manifest.read_bytes()
            omitted = json.loads(pre_delete_bytes.decode("utf-8"))
            omitted["command_receipts"] = [
                row
                for row in omitted["command_receipts"]
                if not str(row["path"]).endswith("verify-current-route-output-isolation.json")
            ]
            omitted_command_set = []
            for row in omitted["command_receipts"]:
                payload = json.loads(Path(row["path"]).read_text(encoding="utf-8"))
                omitted_command_set.append(
                    {
                        "command_id": payload["command_id"],
                        "path": Path(row["path"]).resolve().as_posix(),
                        "sha256": row["sha256"],
                    }
                )
            omitted_command_set.sort(key=lambda row: row["command_id"])
            omitted["command_receipt_set_sha256"] = hashlib.sha256(
                canonical_bytes(omitted_command_set)
            ).hexdigest()
            write_json(pre_delete, omitted)
            omitted_checkpoint = json.loads(checkpoint_bytes.decode("utf-8"))
            omitted_checkpoint["checkpoints"][-1]["command_receipt_set_sha256"] = omitted[
                "command_receipt_set_sha256"
            ]
            omitted_checkpoint["checkpoints"][-1]["required_receipt"]["sha256"] = sha256(
                pre_delete
            )
            write_json(checkpoint_manifest, omitted_checkpoint)
            git(
                repo,
                "add",
                pre_delete.relative_to(repo).as_posix(),
                checkpoint_manifest.relative_to(repo).as_posix(),
            )
            git(repo, "commit", "-m", "tamper pre-delete audit command omission")
            rejected_audit_omission = invoke(
                EXECUTOR,
                "dry-run",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--promotion-receipt", baseline_promotion,
                "--pre-delete-route-receipt", pre_delete,
                "--selection", selection,
                "--manifest-out", external / "rejected-audit-omission/operation.json",
                "--receipt-out", external / "rejected-audit-omission/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_audit_omission.returncode, 0)
            self.assertIn("output-isolation mismatch", rejected_audit_omission.stderr)
            pre_delete.write_bytes(pre_delete_bytes)
            checkpoint_manifest.write_bytes(checkpoint_bytes)
            git(
                repo,
                "add",
                pre_delete.relative_to(repo).as_posix(),
                checkpoint_manifest.relative_to(repo).as_posix(),
            )
            git(repo, "commit", "-m", "restore exact pre-delete audit command")

            current_command = external / "commands/001-pre-delete-current-route.json"
            current_spec = external / "commands/001-pre-delete-current-route.command.json"
            current_command_bytes = current_command.read_bytes()
            current_spec_bytes = current_spec.read_bytes()
            canonical_current_argv = json.loads(current_spec_bytes.decode("utf-8"))["argv"]

            def assert_rejected_current_argv(label: str, mutated_argv: list[str]) -> None:
                spec_payload = json.loads(current_spec_bytes.decode("utf-8"))
                spec_payload["argv"] = mutated_argv
                write_json(current_spec, spec_payload)
                command_payload = json.loads(current_command_bytes.decode("utf-8"))
                command_payload["decoded_argv"] = mutated_argv
                command_payload["command_spec"]["sha256"] = sha256(current_spec)
                write_json(current_command, command_payload)
                receipt_payload = json.loads(pre_delete_bytes.decode("utf-8"))
                for row in receipt_payload["command_receipts"]:
                    if Path(row["path"]).resolve() == current_command.resolve():
                        row["sha256"] = sha256(current_command)
                command_set = []
                for row in receipt_payload["command_receipts"]:
                    payload = json.loads(Path(row["path"]).read_text(encoding="utf-8"))
                    command_set.append(
                        {
                            "command_id": payload["command_id"],
                            "path": Path(row["path"]).resolve().as_posix(),
                            "sha256": row["sha256"],
                        }
                    )
                command_set.sort(key=lambda row: row["command_id"])
                receipt_payload["command_receipt_set_sha256"] = hashlib.sha256(
                    canonical_bytes(command_set)
                ).hexdigest()
                write_json(pre_delete, receipt_payload)
                checkpoint_payload = json.loads(checkpoint_bytes.decode("utf-8"))
                checkpoint_payload["checkpoints"][-1]["command_receipt_set_sha256"] = receipt_payload[
                    "command_receipt_set_sha256"
                ]
                checkpoint_payload["checkpoints"][-1]["required_receipt"]["sha256"] = sha256(
                    pre_delete
                )
                write_json(checkpoint_manifest, checkpoint_payload)
                git(
                    repo,
                    "add",
                    pre_delete.relative_to(repo).as_posix(),
                    checkpoint_manifest.relative_to(repo).as_posix(),
                )
                git(repo, "commit", "-m", f"tamper current-route argv {label}")
                rejected = invoke(
                    EXECUTOR,
                    "dry-run",
                    "--repo", repo,
                    "--baseline", durable / "baseline_inventory.json",
                    "--promotion-receipt", baseline_promotion,
                    "--pre-delete-route-receipt", pre_delete,
                    "--selection", selection,
                    "--manifest-out", external / f"rejected-{label}/operation.json",
                    "--receipt-out", external / f"rejected-{label}/receipt.json",
                    cwd=repo,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("exact canonical invocation", rejected.stderr)
                current_spec.write_bytes(current_spec_bytes)
                current_command.write_bytes(current_command_bytes)
                pre_delete.write_bytes(pre_delete_bytes)
                checkpoint_manifest.write_bytes(checkpoint_bytes)
                git(
                    repo,
                    "add",
                    pre_delete.relative_to(repo).as_posix(),
                    checkpoint_manifest.relative_to(repo).as_posix(),
                )
                git(repo, "commit", "-m", f"restore current-route argv after {label}")

            assert_rejected_current_argv(
                "alternate-taxonomy",
                canonical_current_argv
                + [
                    "--taxonomy",
                    "Iris/_docs/round3/current_route_required_validations.json",
                ],
            )
            alternate_route_result = external / "commands/alternate-current-route-result.json"
            write_json(
                alternate_route_result,
                {"status": "PASS", "summary": {"failed": 0, "errors": 0}},
            )
            assert_rejected_current_argv(
                "duplicate-out",
                canonical_current_argv + ["--out", alternate_route_result.as_posix()],
            )

            archive_root = external / "archive"
            restore_root = external / "restore"
            archive_root.mkdir(parents=True)
            restore_root.mkdir(parents=True)
            operation = archive_root / "archive_operation_manifest.json"
            dry = archive_root / "dry_run_receipt.json"
            archive_receipt = archive_root / "archive_receipt.json"
            verify = archive_root / "archive_verify_receipt.json"
            restore = archive_root / "restore_verify_receipt.json"
            commands = [
                (
                    "dry-run",
                    "--repo", repo,
                    "--baseline", durable / "baseline_inventory.json",
                    "--promotion-receipt", baseline_promotion,
                    "--pre-delete-route-receipt", pre_delete,
                    "--selection", selection,
                    "--manifest-out", operation,
                    "--receipt-out", dry,
                ),
                (
                    "archive",
                    "--repo", repo,
                    "--operation-manifest", operation,
                    "--prior-receipt", dry,
                    "--archive-root", archive_root,
                    "--receipt-out", archive_receipt,
                ),
                (
                    "verify",
                    "--operation-manifest", operation,
                    "--prior-receipt", archive_receipt,
                    "--receipt-out", verify,
                ),
                (
                    "restore-verify",
                    "--operation-manifest", operation,
                    "--prior-receipt", verify,
                    "--restore-root", restore_root,
                    "--receipt-out", restore,
                ),
            ]
            for command in commands[:2]:
                result = invoke(EXECUTOR, *command, cwd=repo)
                self.assertEqual(result.returncode, 0, result.stderr)

            archive_receipt_bytes = archive_receipt.read_bytes()
            archive_receipt_payload = json.loads(archive_receipt_bytes.decode("utf-8"))
            archive_path = Path(archive_receipt_payload["archive_path"])
            archive_bytes = archive_path.read_bytes()
            with zipfile.ZipFile(archive_path, "r") as source_bundle:
                member_payloads = [
                    (info.filename, source_bundle.read(info.filename))
                    for info in source_bundle.infolist()
                ]
            with zipfile.ZipFile(
                archive_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
                allowZip64=True,
            ) as tampered_bundle:
                for name, payload in member_payloads:
                    tampered_bundle.writestr(
                        name,
                        b'{"tampered":true}\n'
                        if name == "_iris_archive_operation_manifest.json"
                        else payload,
                    )
            archive_receipt_payload["archive_sha256"] = sha256(archive_path)
            archive_receipt_payload["archive_bytes"] = archive_path.stat().st_size
            write_json(archive_receipt, archive_receipt_payload)
            rejected_embedded_manifest = invoke(
                EXECUTOR,
                "verify",
                "--operation-manifest", operation,
                "--prior-receipt", archive_receipt,
                "--receipt-out", archive_root / "rejected_embedded_manifest.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_embedded_manifest.returncode, 0)
            self.assertIn("embedded archive operation manifest byte identity", rejected_embedded_manifest.stderr)
            self.assertFalse((archive_root / "rejected_embedded_manifest.json").exists())
            archive_path.write_bytes(archive_bytes)
            archive_receipt.write_bytes(archive_receipt_bytes)

            for command in commands[2:]:
                result = invoke(EXECUTOR, *command, cwd=repo)
                self.assertEqual(result.returncode, 0, result.stderr)
            archive_promotion_external = external / "promotion/archive.json"
            promotion = invoke(
                PROMOTER,
                "archive",
                "--repo", repo,
                "--source-operation-manifest", operation,
                "--source-archive-receipt", archive_receipt,
                "--source-verify-receipt", verify,
                "--source-restore-receipt", restore,
                "--destination-root", durable,
                "--receipt-out", archive_promotion_external,
                cwd=repo,
            )
            self.assertEqual(promotion.returncode, 0, promotion.stderr)
            durable_operation = durable / "archive_operation_manifest.json"
            durable_restore = durable / "archive_restore_receipt.json"
            durable_promotion = durable / "archive_promotion_receipt.json"
            durable_archive_bytes = {
                path: path.read_bytes()
                for path in (durable_operation, durable_restore, durable_promotion)
            }
            physical_branch = git(repo, "branch", "--show-current")
            git(repo, "switch", "-c", "side-archive-evidence")
            git(repo, "add", DURABLE.as_posix())
            git(repo, "commit", "-m", "side-branch archive evidence")
            side_archive_commit = git(repo, "rev-parse", "HEAD")
            side_approval = external / "side-delete-approval.json"
            write_json(
                side_approval,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_post_archive_delete_approval_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "archive_evidence_commit": side_archive_commit,
                    "operation_id": json.loads(durable_operation.read_text(encoding="utf-8"))["operation_id"],
                    "exact_paths": [CANDIDATE.as_posix()],
                    "archive_operation_manifest_sha256": sha256(durable_operation),
                    "archive_restore_receipt_sha256": sha256(durable_restore),
                    "archive_promotion_receipt_sha256": sha256(durable_promotion),
                    "pre_delete_current_route_receipt_sha256": sha256(pre_delete),
                },
            )
            git(repo, "switch", physical_branch)
            for path, payload in durable_archive_bytes.items():
                path.write_bytes(payload)
            rejected_side_branch = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", side_archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", side_approval,
                "--out", external / "archive/rejected-side-branch-evidence.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_side_branch.returncode, 0)
            self.assertIn("ancestor of physical HEAD", rejected_side_branch.stderr)
            self.assertFalse((external / "archive/rejected-side-branch-evidence.json").exists())
            physical_runner = repo / "Iris/_docs/round3/round3_run_contract_tests.py"
            validated_runner_bytes = physical_runner.read_bytes()
            physical_runner.write_text("raise SystemExit('changed after validation')\n", encoding="utf-8")
            git(repo, "add", DURABLE.as_posix(), physical_runner.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "adopt archive evidence with stale candidate change")
            archive_commit = git(repo, "rev-parse", "HEAD")
            approval = external / "delete-approval.json"
            write_json(
                approval,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_post_archive_delete_approval_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "archive_evidence_commit": archive_commit,
                    "operation_id": json.loads(durable_operation.read_text(encoding="utf-8"))["operation_id"],
                    "exact_paths": [CANDIDATE.as_posix()],
                    "archive_operation_manifest_sha256": sha256(durable_operation),
                    "archive_restore_receipt_sha256": sha256(durable_restore),
                    "archive_promotion_receipt_sha256": sha256(durable_promotion),
                    "pre_delete_current_route_receipt_sha256": sha256(pre_delete),
                },
            )
            rejected_stale = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-stale-candidate.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_stale.returncode, 0)
            self.assertIn("validated Common candidate", rejected_stale.stderr)
            self.assertFalse((external / "archive/rejected-stale-candidate.json").exists())
            physical_runner.write_bytes(validated_runner_bytes)
            git(repo, "add", physical_runner.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "restore exact validated Common candidate")

            selection_bytes = selection.read_bytes()
            rejected_selection = json.loads(selection_bytes.decode("utf-8"))
            rejected_selection["approved"] = False
            write_json(selection, rejected_selection)
            rejected_owner = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-owner-selection.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_owner.returncode, 0)
            self.assertIn("owner-selection", rejected_owner.stderr)
            self.assertFalse((external / "archive/rejected-owner-selection.json").exists())
            selection.write_bytes(selection_bytes)

            baseline_path = durable / "baseline_inventory.json"
            baseline_bytes = baseline_path.read_bytes()
            rejected_baseline = json.loads(baseline_bytes.decode("utf-8"))
            rejected_baseline["physical_bytes"] = int(rejected_baseline["physical_bytes"]) + 1
            write_json(baseline_path, rejected_baseline)
            rejected_promoted_baseline = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", baseline_path,
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-promoted-baseline.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_promoted_baseline.returncode, 0)
            self.assertIn("baseline", rejected_promoted_baseline.stderr)
            self.assertFalse((external / "archive/rejected-promoted-baseline.json").exists())
            baseline_path.write_bytes(baseline_bytes)

            prerequisite = external / "archive/delete-prerequisite.json"
            validated = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", prerequisite,
                cwd=repo,
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)
            delete_receipt = external / "archive/delete.json"
            candidate_path = repo / CANDIDATE
            candidate_bytes = candidate_path.read_bytes()
            same_content_target = repo / "same-content-delete-target.json"
            same_content_target.write_bytes(candidate_bytes)
            candidate_path.unlink()
            create_file_symlink(candidate_path, same_content_target)
            rejected_symlink = invoke(
                EXECUTOR,
                "delete",
                "--repo", repo,
                "--operation-manifest", durable_operation,
                "--prerequisite-receipt", prerequisite,
                "--receipt-out", external / "archive/rejected-symlink-delete.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_symlink.returncode, 0)
            self.assertIn("symlink or reparse point", rejected_symlink.stderr)
            self.assertTrue(candidate_path.is_symlink())
            self.assertEqual(same_content_target.read_bytes(), candidate_bytes)
            self.assertFalse((external / "archive/rejected-symlink-delete.json").exists())
            candidate_path.unlink()
            candidate_path.write_bytes(candidate_bytes)
            deleted = invoke(
                EXECUTOR,
                "delete",
                "--repo", repo,
                "--operation-manifest", durable_operation,
                "--prerequisite-receipt", prerequisite,
                "--receipt-out", delete_receipt,
                cwd=repo,
            )
            self.assertEqual(deleted.returncode, 0, deleted.stderr)
            self.assertFalse((repo / CANDIDATE).exists())
            self.assertEqual(same_content_target.read_bytes(), candidate_bytes)
            self.assertTrue(Path(json.loads(archive_receipt.read_text(encoding="utf-8"))["archive_path"]).is_file())
            durable_restore_bytes = durable_restore.read_bytes()
            durable_restore.unlink()
            rejected_missing_evidence = invoke(
                EXECUTOR,
                "post-delete-census",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--prior-receipt", delete_receipt,
                "--receipt-out", external / "archive/rejected-missing-evidence.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_missing_evidence.returncode, 0)
            self.assertIn("durable evidence binding mismatch", rejected_missing_evidence.stderr)
            self.assertFalse((external / "archive/rejected-missing-evidence.json").exists())
            durable_restore.write_bytes(durable_restore_bytes)
            post = invoke(
                EXECUTOR,
                "post-delete-census",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--prior-receipt", delete_receipt,
                "--receipt-out", external / "archive/post-delete.json",
                cwd=repo,
            )
            self.assertEqual(post.returncode, 0, post.stderr)
            post_receipt = json.loads(
                (external / "archive/post-delete.json").read_text(encoding="utf-8")
            )
            approved_paths = {
                row["path"]
                for row in (
                    post_receipt["approved_durable_additions"]
                    + post_receipt["approved_durable_changes"]
                )
            }
            self.assertTrue(
                {
                    "Iris/_docs/round3/round3_test_taxonomy.json",
                    "Iris/build/description/v2/tests/test_fixture.py",
                    (
                        "Iris/_docs/refactor/repository_runtime_lightweighting/"
                        "current_surface_guard_successor_manifest.json"
                    ),
                }.issubset(approved_paths)
            )
            self.assertGreater(
                post_receipt["validated_candidate_delta_allowset"][
                    "bound_path_count"
                ],
                0,
            )

    def test_selection_outside_baseline_is_rejected_without_source_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-selection-") as temporary:
            root = Path(temporary)
            repo, external, candidate = build_fixture(root)
            durable = repo / DURABLE
            selection = external / "bad-selection.json"
            baseline = json.loads((durable / "baseline_inventory.json").read_text(encoding="utf-8"))
            write_json(
                selection,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_exact_archive_selection_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "physical_resolved_root": repo.as_posix(),
                    "baseline_run_identity": baseline["run_identity"],
                    "baseline_promotion_receipt_sha256": sha256(durable / "baseline_promotion_receipt.json"),
                    "pre_delete_current_route_receipt_sha256": sha256(
                        durable / "pre_delete_current_route_receipt.json"
                    ),
                    "rows": [
                        {
                            "logical_artifact_id": candidate["logical_artifact_id"],
                            "path": CANDIDATE.parent.as_posix(),
                            "sha256": candidate["sha256"],
                            "size_bytes": candidate["size_bytes"],
                        }
                    ],
                },
            )
            result = invoke(
                EXECUTOR,
                "dry-run",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--promotion-receipt", durable / "baseline_promotion_receipt.json",
                "--pre-delete-route-receipt", durable / "pre_delete_current_route_receipt.json",
                "--selection", selection,
                "--manifest-out", external / "bad/operation.json",
                "--receipt-out", external / "bad/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside promoted baseline", result.stderr)
            self.assertTrue((repo / CANDIDATE).is_file())


if __name__ == "__main__":
    unittest.main()
