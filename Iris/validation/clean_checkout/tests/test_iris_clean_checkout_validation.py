from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from collections.abc import Callable
from pathlib import Path

import pytest

from Iris.build.tools.common.io import repository_external_output_root
from Iris.validation.clean_checkout.iris_clean_checkout_validation_common import (
    CleanCheckoutError,
    canonical_compact_json_bytes,
    canonical_json_bytes,
    ensure_external_root,
    validate_external_environment,
    write_json_external,
)
from Iris.validation.clean_checkout.inventory_iris_offline_tooling import (
    build_inventory,
)
from Iris.validation.clean_checkout.run_iris_clean_checkout_validation import (
    _classify_full_test_source,
    _full_required_source_roles,
    _ignored_status_snapshot,
    _normalized_test_id,
    _safe_checkout_target,
    _validate_g5_compiler_identity_transition,
    _validate_explicit_required_dependencies,
    _validate_explicit_current_required_classifications,
    _validate_explicit_tool_dispositions,
)
from Iris.validation.clean_checkout.validate_iris_clean_checkout_validation import (
    validate_result_pair,
)


def _fake_repo(path: Path) -> Path:
    repo = path / "repo"
    (repo / ".git").mkdir(parents=True)
    return repo.resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _git_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _schema_accepts(
    instance: object,
    schema: dict[str, object],
    root: dict[str, object],
) -> bool:
    reference = schema.get("$ref")
    if isinstance(reference, str):
        if not reference.startswith("#/"):
            return False
        target: object = root
        for token in reference[2:].split("/"):
            if not isinstance(target, dict) or token not in target:
                return False
            target = target[token]
        return isinstance(target, dict) and _schema_accepts(instance, target, root)
    one_of = schema.get("oneOf")
    if isinstance(one_of, list):
        return (
            sum(
                isinstance(candidate, dict)
                and _schema_accepts(instance, candidate, root)
                for candidate in one_of
            )
            == 1
        )
    all_of = schema.get("allOf")
    if isinstance(all_of, list) and not all(
        isinstance(candidate, dict)
        and _schema_accepts(instance, candidate, root)
        for candidate in all_of
    ):
        return False
    conditional = schema.get("if")
    consequent = schema.get("then")
    if (
        isinstance(conditional, dict)
        and isinstance(consequent, dict)
        and _schema_accepts(instance, conditional, root)
        and not _schema_accepts(instance, consequent, root)
    ):
        return False
    if "const" in schema and instance != schema["const"]:
        return False
    enum = schema.get("enum")
    if isinstance(enum, list) and instance not in enum:
        return False
    declared_type = schema.get("type")
    if isinstance(declared_type, str):
        declared_types = [declared_type]
    elif isinstance(declared_type, list):
        declared_types = declared_type
    else:
        declared_types = []
    if declared_types:
        matches = {
            "null": instance is None,
            "object": isinstance(instance, dict),
            "array": isinstance(instance, list),
            "string": isinstance(instance, str),
            "integer": isinstance(instance, int) and not isinstance(instance, bool),
            "boolean": isinstance(instance, bool),
        }
        if not any(matches.get(str(name), False) for name in declared_types):
            return False
    if isinstance(instance, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(instance) < minimum:
            return False
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            return False
    if isinstance(instance, dict):
        required = schema.get("required")
        if isinstance(required, list) and any(
            key not in instance for key in required
        ):
            return False
        properties = schema.get("properties")
        if isinstance(properties, dict):
            for key, child_schema in properties.items():
                if (
                    key in instance
                    and isinstance(child_schema, dict)
                    and not _schema_accepts(instance[key], child_schema, root)
                ):
                    return False
    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict) and any(
            not _schema_accepts(item, items, root) for item in instance
        ):
            return False
    excluded = schema.get("not")
    if (
        isinstance(excluded, dict)
        and _schema_accepts(instance, excluded, root)
    ):
        return False
    return True


def _assert_matches_schema(name: str, payload: object) -> None:
    schema_path = Path(__file__).resolve().parents[1] / "contracts" / name
    schema = json.loads(schema_path.read_bytes())
    assert _schema_accepts(payload, schema, schema), (
        f"payload does not match {name}"
    )


def _build_fake_launcher_repository(
    tmp_path: Path,
    *,
    native_exit_code: int = 0,
    interpreter_hash_override: str | None = None,
) -> tuple[Path, str, Path]:
    repo = (tmp_path / "subject-repo").resolve()
    clean_checkout_root = repo / "Iris" / "validation" / "clean_checkout"
    contracts = clean_checkout_root / "contracts"
    authority = clean_checkout_root / "authority"
    contracts.mkdir(parents=True)
    authority.mkdir(parents=True)
    fixture_json_paths = (
        "Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json",
        "Iris/validation/clean_checkout/contracts/full_repository_gate.json",
        "Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json",
        "Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json",
        "Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "Iris/_docs/round3/current_route_required_validations.json",
    )
    for relative in fixture_json_paths:
        fixture_path = repo / relative
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_bytes(canonical_json_bytes({"fixture": True}))
    allocator_fixture = (
        clean_checkout_root
        / "allocate_repository_runtime_lightweighting_roots.ps1"
    )
    allocator_fixture.write_text("# fixture\n", encoding="utf-8", newline="\n")
    launcher_source = Path(__file__).resolve().parents[1] / (
        "invoke_receipt_bound_full_gate.ps1"
    )
    (clean_checkout_root / launcher_source.name).write_bytes(
        launcher_source.read_bytes()
    )
    compare_source = Path(__file__).resolve().parents[1] / (
        "invoke_deterministic_compare.ps1"
    )
    (clean_checkout_root / compare_source.name).write_bytes(
        compare_source.read_bytes()
    )
    (clean_checkout_root / "iris_clean_checkout_validation_common.py").write_text(
        "FAKE_COMMON_MARKER = 'actual-import-fixture'\n",
        encoding="utf-8",
    )
    runner = clean_checkout_root / "run_iris_clean_checkout_validation.py"
    runner.write_text(
        textwrap.dedent(
            r'''
            from __future__ import annotations

            import argparse
            import hashlib
            import json
            import os
            import subprocess
            import sys
            from pathlib import Path

            import iris_clean_checkout_validation_common as imported_common


            def sha256(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()


            def git(repo: Path, *args: str) -> str:
                return subprocess.run(
                    ["git", "-C", str(repo), *args],
                    check=True,
                    stdout=subprocess.PIPE,
                    text=True,
                ).stdout.strip()


            def write_json(path: Path, payload: object) -> str:
                path.parent.mkdir(parents=True, exist_ok=True)
                encoded = (
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n"
                ).encode("utf-8")
                path.write_bytes(encoded)
                return hashlib.sha256(encoded).hexdigest()


            parser = argparse.ArgumentParser()
            parser.add_argument("command")
            parser.add_argument("--repo", required=True)
            parser.add_argument("--commit", required=True)
            parser.add_argument("--python", required=True)
            parser.add_argument("--environment-receipt", required=True)
            parser.add_argument("--work-root", required=True)
            parser.add_argument("--result-root", required=True)
            parser.add_argument(
                "--execution-context", default="standalone_full_gate"
            )
            parser.add_argument("--predecessor-stage-receipt-set-sha256")
            parser.add_argument("--qualification-contract-sha256")
            parser.add_argument("--predecessor-stage-receipt-set")
            parser.add_argument("--qualification-contract")
            args = parser.parse_args()

            sys.stdout.buffer.write(b"fake stdout: \x00\xff\n")
            sys.stdout.buffer.flush()
            sys.stderr.buffer.write(b"fake stderr: \xfe\x00\r\n")
            sys.stderr.buffer.flush()
            forced_exit = int(os.environ["IRIS_FAKE_NATIVE_EXIT"])
            if forced_exit:
                raise SystemExit(forced_exit)

            repo = Path(args.repo).resolve()
            result_root = Path(args.result_root).resolve()
            if result_root.exists() and any(result_root.iterdir()):
                raise SystemExit("fixture result root is not empty")
            result_root.mkdir(parents=True, exist_ok=True)
            subject = {
                "commit": git(repo, "rev-parse", args.commit + "^{commit}"),
                "tree": git(repo, "rev-parse", args.commit + "^{tree}"),
            }
            runner_path = Path(__file__).resolve()
            common_path = Path(imported_common.__file__).resolve()
            runner_relative = (
                "Iris/validation/clean_checkout/"
                "run_iris_clean_checkout_validation.py"
            )
            common_relative = (
                "Iris/validation/clean_checkout/"
                "iris_clean_checkout_validation_common.py"
            )
            canonical_path = result_root / "canonical_full_result.json"
            canonical_hash = write_json(
                canonical_path,
                {
                    "schema_version": (
                        "iris-clean-checkout-canonical-full-result-v1"
                    ),
                    "status": "PASS",
                    "subject": subject,
                    "test_identity_count": 1,
                    "test_inventory_sha256": "3" * 64,
                },
            )
            inner = {
                "schema_version": "iris-clean-checkout-full-run-receipt-v1",
                "status": "PASS",
                "subject": subject,
                "execution_context": args.execution_context,
                "predecessor_stage_receipt_set_sha256": (
                    args.predecessor_stage_receipt_set_sha256
                ),
                "qualification_contract_sha256": (
                    args.qualification_contract_sha256
                ),
                "python_executable_path": Path(sys.executable).resolve().as_posix(),
                "environment_receipt_path": Path(
                    args.environment_receipt
                ).resolve().as_posix(),
                "implementation_identity": {
                    "runner": {
                        "logical_path": runner_relative,
                        "actual_path": runner_path.as_posix(),
                        "git_blob_id": git(
                            repo, "rev-parse", args.commit + ":" + runner_relative
                        ),
                        "working_sha256": sha256(runner_path),
                    },
                    "imported_common": {
                        "logical_path": common_relative,
                        "actual_path": common_path.as_posix(),
                        "module_file": common_path.as_posix(),
                        "git_blob_id": git(
                            repo, "rev-parse", args.commit + ":" + common_relative
                        ),
                        "working_sha256": sha256(common_path),
                    },
                },
                "canonical_result": {
                    "path": canonical_path.as_posix(),
                    "sha256": canonical_hash,
                },
            }
            write_json(result_root / "full_run_receipt.json", inner)
            '''
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    validator = (
        clean_checkout_root / "validate_iris_clean_checkout_validation.py"
    )
    validator.write_text(
        textwrap.dedent(
            r'''
            from __future__ import annotations

            import argparse
            import hashlib
            import json
            import subprocess
            import sys
            from pathlib import Path

            import iris_clean_checkout_validation_common as imported_common


            def sha256(path: Path) -> str:
                return hashlib.sha256(path.read_bytes()).hexdigest()


            def git(repo: Path, *args: str) -> str:
                return subprocess.run(
                    ["git", "-C", str(repo), *args],
                    check=True,
                    stdout=subprocess.PIPE,
                    text=True,
                ).stdout.strip()


            parser = argparse.ArgumentParser()
            parser.add_argument("command")
            parser.add_argument("--run-a", required=True)
            parser.add_argument("--run-b", required=True)
            parser.add_argument("--repo", required=True)
            parser.add_argument("--commit", required=True)
            args = parser.parse_args()
            run_a = Path(args.run_a).read_bytes()
            run_b = Path(args.run_b).read_bytes()
            if run_a != run_b:
                raise SystemExit(3)
            repo = Path(args.repo).resolve()
            validator_path = Path(__file__).resolve()
            common_path = Path(imported_common.__file__).resolve()
            validator_relative = (
                "Iris/validation/clean_checkout/"
                "validate_iris_clean_checkout_validation.py"
            )
            common_relative = (
                "Iris/validation/clean_checkout/"
                "iris_clean_checkout_validation_common.py"
            )
            payload = {
                "schema_version": "iris-clean-checkout-result-comparison-v1",
                "status": "PASS",
                "subject": {
                    "commit": git(repo, "rev-parse", args.commit + "^{commit}"),
                    "tree": git(repo, "rev-parse", args.commit + "^{tree}"),
                },
                "canonical_result_raw_bytes_equal": True,
                "canonical_results_equal": True,
                "implementation_identity": {
                    "validator": {
                        "logical_path": validator_relative,
                        "actual_path": validator_path.as_posix(),
                        "git_blob_id": git(
                            repo,
                            "rev-parse",
                            args.commit + ":" + validator_relative,
                        ),
                        "working_sha256": sha256(validator_path),
                    },
                    "imported_common": {
                        "logical_path": common_relative,
                        "actual_path": common_path.as_posix(),
                        "module_file": common_path.as_posix(),
                        "git_blob_id": git(
                            repo,
                            "rev-parse",
                            args.commit + ":" + common_relative,
                        ),
                        "working_sha256": sha256(common_path),
                    },
                },
            }
            sys.stdout.buffer.write(
                (
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n"
                ).encode("utf-8")
            )
            '''
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    python_path = Path(sys.executable).resolve()
    environment_receipt = (tmp_path / "environment-receipt.json").resolve()
    environment_receipt.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": "fake-environment-receipt-v1",
                "interpreter": {"path": python_path.as_posix()},
            }
        )
    )
    interpreter_hash = interpreter_hash_override or _sha256(python_path)
    (contracts / "output_policy.json").write_bytes(
        canonical_json_bytes(
            {
                "required_environment": {
                    "IRIS_ENV_ABSENT": "applied-absent",
                    "IRIS_ENV_EMPTY": "applied-empty",
                    "IRIS_ENV_VALUE": "applied-value",
                    "IRIS_FAKE_NATIVE_EXIT": str(native_exit_code),
                },
                "cleared_ambient_environment": ["IRIS_ENV_CLEAR"],
            }
        )
    )
    (contracts / "repository_runtime_lightweighting_output_policy.json").write_bytes(
        canonical_json_bytes(
            {
                "schema_version": (
                    "iris_repository_runtime_lightweighting_output_policy_v1"
                ),
                "required_environment": {
                    "IRIS_ENV_ABSENT": "applied-absent",
                    "IRIS_ENV_EMPTY": "applied-empty",
                    "IRIS_ENV_VALUE": "applied-value",
                    "IRIS_FAKE_NATIVE_EXIT": str(native_exit_code),
                },
                "cleared_ambient_environment": ["IRIS_ENV_CLEAR"],
            }
        )
    )
    environment_record = authority / "responsibility_refactor_environment_fixture_v1.json"
    environment_record.write_bytes(
        canonical_json_bytes(
            {
                "schema_version": "iris-responsibility-refactor-environment-authority-v1",
                "environment_contract": {
                    "external_environment_root": Path(sys.prefix).resolve().as_posix(),
                    "immutable_environment_receipt_path": environment_receipt.as_posix(),
                    "immutable_environment_receipt_sha256": _sha256(environment_receipt),
                    "interpreter_sha256": interpreter_hash,
                },
            }
        )
    )
    (authority / "responsibility_refactor_environment_current.json").write_bytes(
        canonical_json_bytes(
            {
                "schema_version": "iris-responsibility-refactor-environment-locator-v1",
                "record_path": (
                    "Iris/validation/clean_checkout/authority/"
                    "responsibility_refactor_environment_fixture_v1.json"
                ),
                "record_sha256": _sha256(environment_record),
            }
        )
    )
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _git(repo, "add", ".")
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Codex Fixture",
            "-c",
            "user.email=codex-fixture@example.invalid",
            "commit",
            "-q",
            "-m",
            "fixture",
        ],
        check=True,
    )
    return repo, _git(repo, "rev-parse", "HEAD"), environment_receipt


def _invoke_fake_launcher(
    tmp_path: Path,
    repo: Path,
    commit: str,
    environment_receipt: Path,
    *,
    attempt_name: str = "external-attempt",
    failure_injection: str = "none",
    receipt_as_directory: bool = False,
    receipt_inside_result: bool = False,
) -> tuple[subprocess.CompletedProcess[bytes], Path, Path, Path]:
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is required for launcher fixtures")
    attempt = (tmp_path / attempt_name).resolve()
    work_root = attempt / "work"
    result_root = attempt / "result"
    receipt = (
        result_root / "orchestration.json"
        if receipt_inside_result
        else attempt / "orchestration.json"
    )
    if receipt_as_directory:
        receipt.mkdir(parents=True)
    launcher = (
        repo
        / "Iris"
        / "validation"
        / "clean_checkout"
        / "invoke_receipt_bound_full_gate.ps1"
    )
    environment = os.environ.copy()
    # The test explicitly launches Windows PowerShell. Do not pass through a
    # PowerShell 7 module search path from the parent process; bind the child to
    # Windows PowerShell's system modules so built-ins such as Get-FileHash
    # remain discoverable under `uv run`.
    environment["PSModulePath"] = str(Path(powershell).resolve().parent / "Modules")
    environment.pop("IRIS_ENV_ABSENT", None)
    environment["IRIS_ENV_EMPTY"] = ""
    environment["IRIS_ENV_VALUE"] = "outer-value"
    environment["IRIS_ENV_CLEAR"] = "outer-clear"
    completed = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher),
            "-RepositoryRoot",
            str(repo),
            "-Commit",
            commit,
            "-ClaimId",
            "fixture-claim",
            "-EnvironmentReceipt",
            str(environment_receipt),
            "-WorkRoot",
            str(work_root),
            "-ResultRoot",
            str(result_root),
            "-OrchestrationReceipt",
            str(receipt),
            "-FailureInjection",
            failure_injection,
            "-EmptyStateFixtureVariable",
            "IRIS_ENV_EMPTY",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        timeout=30,
    )
    stream_root = attempt / (
        "result.launcher" if receipt_inside_result else ""
    )
    return completed, receipt, stream_root / "full-gate.stdout.bin", (
        stream_root / "full-gate.stderr.bin"
    )


def _invoke_fake_compare(
    tmp_path: Path,
    repo: Path,
    commit: str,
    environment_receipt: Path,
    run_a_receipt: Path,
    run_b_receipt: Path,
    *,
    attempt_name: str,
    failure_injection: str = "none",
) -> tuple[subprocess.CompletedProcess[bytes], Path, Path, Path]:
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is required for compare fixtures")
    attempt = (tmp_path / attempt_name).resolve()
    launcher = (
        repo
        / "Iris"
        / "validation"
        / "clean_checkout"
        / "invoke_deterministic_compare.ps1"
    )
    environment = os.environ.copy()
    # Keep the Windows PowerShell fixture independent of the parent shell's
    # PowerShell-major-version module search path.
    environment["PSModulePath"] = str(Path(powershell).resolve().parent / "Modules")
    environment.pop("IRIS_ENV_ABSENT", None)
    environment["IRIS_ENV_EMPTY"] = ""
    environment["IRIS_ENV_VALUE"] = "outer-value"
    environment["IRIS_ENV_CLEAR"] = "outer-clear"
    completed = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher),
            "-RepositoryRoot",
            str(repo),
            "-Commit",
            commit,
            "-ClaimId",
            "fixture-claim",
            "-EnvironmentReceipt",
            str(environment_receipt),
            "-RunAOrchestrationReceipt",
            str(run_a_receipt),
            "-RunBOrchestrationReceipt",
            str(run_b_receipt),
            "-AttemptRoot",
            str(attempt),
            "-FailureInjection",
            failure_injection,
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        timeout=30,
    )
    return (
        completed,
        attempt / "compare_receipt.json",
        attempt / "compare-results.stdout.bin",
        attempt / "compare-results.stderr.bin",
    )


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_success_binds_inner_identity_and_raw_streams(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(
        tmp_path
    )
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path, repo, commit, environment_receipt
    )
    assert completed.returncode == 0, completed.stderr.decode(
        "utf-8", errors="replace"
    )
    receipt_bytes = receipt_path.read_bytes()
    assert not receipt_bytes.startswith(b"\xef\xbb\xbf")
    receipt = json.loads(receipt_bytes)
    _assert_matches_schema("orchestration_receipt.schema.json", receipt)
    assert receipt["launch_status"] == "succeeded"
    assert receipt["primary_failure"] is None
    assert receipt["native_exit_code"] == 0
    assert receipt["result_receipt"]["exists"] is True
    assert receipt["identity"]["inner_actual_import"]["git_blob_id"] == (
        receipt["identity"]["implementation"]["common"]["git_blob_id"]
    )
    environment = receipt["environment"]
    assert environment["configured"] is True
    assert environment["restored"] is True
    assert environment["before"]["IRIS_ENV_ABSENT"]["state"] == "absent"
    assert environment["before"]["IRIS_ENV_EMPTY"]["state"] == "empty"
    assert environment["before"]["IRIS_ENV_VALUE"] == {
        "state": "value",
        "value": "outer-value",
    }
    assert environment["before"] == environment["after_restore"]
    assert stdout_path.read_bytes() == b"fake stdout: \x00\xff\n"
    assert stderr_path.read_bytes() == b"fake stderr: \xfe\x00\r\n"


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_keeps_nested_result_root_empty_for_gate(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(
        tmp_path
    )
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        receipt_inside_result=True,
    )
    assert completed.returncode == 0, completed.stderr.decode(
        "utf-8", errors="replace"
    )
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["launch_status"] == "succeeded"
    assert receipt["environment"]["restored"] is True
    assert stdout_path.read_bytes() == b"fake stdout: \x00\xff\n"
    assert stderr_path.read_bytes() == b"fake stderr: \xfe\x00\r\n"


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_head_mismatch_has_pre_python_receipt(
    tmp_path: Path,
) -> None:
    repo, _, environment_receipt = _build_fake_launcher_repository(tmp_path)
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path, repo, "0" * 40, environment_receipt
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_bytes())
    _assert_matches_schema("orchestration_receipt.schema.json", receipt)
    assert receipt["primary_failure"]["stage"] == "resolve_head"
    assert receipt["native_exit_code"] is None
    assert receipt["actual_argv"] is None
    assert not stdout_path.exists()
    assert not stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_dirty_failure_has_pre_python_receipt(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    (repo / "untracked-local.txt").write_text("dirty", encoding="utf-8")
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path, repo, commit, environment_receipt
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["primary_failure"]["stage"] == "check_clean"
    assert receipt["native_exit_code"] is None
    assert receipt["actual_argv"] is None
    assert not stdout_path.exists()
    assert not stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_detects_skip_worktree_blob_mismatch(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    runner_relative = (
        "Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py"
    )
    _git(repo, "update-index", "--skip-worktree", runner_relative)
    runner = repo / runner_relative
    runner.write_bytes(runner.read_bytes() + b"\n# subject drift\n")
    assert _git(repo, "status", "--porcelain=v1", "--untracked-files=all") == ""
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path, repo, commit, environment_receipt
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["primary_failure"]["stage"] == "resolve_identity"
    assert "differs from the exact subject blob" in (
        receipt["primary_failure"]["exception_message"]
    )
    assert receipt["native_exit_code"] is None
    assert not stdout_path.exists()
    assert not stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_interpreter_mismatch_is_pre_python(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(
        tmp_path,
        interpreter_hash_override="0" * 64,
    )
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path, repo, commit, environment_receipt
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt["primary_failure"]["stage"] == "resolve_identity"
    assert "interpreter hash differs" in (
        receipt["primary_failure"]["exception_message"]
    )
    assert receipt["native_exit_code"] is None
    assert not stdout_path.exists()
    assert not stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_preserves_native_nonzero_as_primary(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(
        tmp_path,
        native_exit_code=7,
    )
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path, repo, commit, environment_receipt
    )
    assert completed.returncode == 7
    receipt = json.loads(receipt_path.read_bytes())
    _assert_matches_schema("orchestration_receipt.schema.json", receipt)
    assert receipt["primary_failure"] == {
        "kind": "native_gate_exit_nonzero",
        "native_exit_code": 7,
    }
    assert receipt["native_exit_code"] == 7
    assert receipt["launch_status"] == "gate_failed"
    assert receipt["secondary_failures"] == []
    assert stdout_path.read_bytes() == b"fake stdout: \x00\xff\n"
    assert stderr_path.read_bytes() == b"fake stderr: \xfe\x00\r\n"


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_restores_after_partial_environment_apply(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        failure_injection="required_environment_apply",
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_bytes())
    _assert_matches_schema("orchestration_receipt.schema.json", receipt)
    assert receipt["primary_failure"]["stage"] == "configure_environment"
    assert receipt["native_exit_code"] is None
    assert receipt["environment"]["configured"] is False
    assert receipt["environment"]["restored"] is True
    assert receipt["environment"]["before"] == (
        receipt["environment"]["after_restore"]
    )
    assert len(receipt["environment"]["applied"]) >= 1
    assert not stdout_path.exists()
    assert not stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_records_restore_failure_without_success_override(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    completed, receipt_path, stdout_path, stderr_path = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        failure_injection="environment_restore",
    )
    assert completed.returncode == 1
    receipt = json.loads(receipt_path.read_bytes())
    _assert_matches_schema("orchestration_receipt.schema.json", receipt)
    assert receipt["primary_failure"]["kind"] == "environment_restore_failed"
    assert receipt["primary_failure"]["stage"] == "restore_environment"
    assert receipt["launch_status"] == "environment_restore_failed"
    assert receipt["native_exit_code"] == 0
    assert receipt["environment"]["restored"] is False
    failed_name = receipt["primary_failure"]["variable"]
    assert failed_name not in receipt["environment"]["after_restore"]
    assert receipt["result_receipt"]["exists"] is True
    assert stdout_path.read_bytes() == b"fake stdout: \x00\xff\n"
    assert stderr_path.read_bytes() == b"fake stderr: \xfe\x00\r\n"


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_keeps_native_failure_primary_when_restore_fails(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(
        tmp_path,
        native_exit_code=7,
    )
    completed, receipt_path, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        failure_injection="environment_restore",
    )
    assert completed.returncode == 7
    receipt = json.loads(receipt_path.read_bytes())
    _assert_matches_schema("orchestration_receipt.schema.json", receipt)
    assert receipt["primary_failure"] == {
        "kind": "native_gate_exit_nonzero",
        "native_exit_code": 7,
    }
    assert receipt["launch_status"] == "gate_failed"
    assert any(
        row["stage"] == "restore_environment"
        and "injected environment restore failure" in row["exception_message"]
        for row in receipt["secondary_failures"]
    )


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_receipt_bound_launcher_writer_failure_is_operator_visible_and_clean(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    completed, receipt_path, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        receipt_as_directory=True,
    )
    assert completed.returncode == 125
    assert receipt_path.is_dir()
    fallback_rows = [
        json.loads(line)
        for line in completed.stderr.decode("utf-8").splitlines()
        if line.startswith("{")
    ]
    assert len(fallback_rows) == 1
    fallback = fallback_rows[0]
    assert fallback["schema_version"] == (
        "iris-clean-checkout-orchestration-writer-fallback-v1"
    )
    assert fallback["receipt_write_status"] == "failed"
    assert fallback["native_exit_code"] == 0
    assert fallback["primary_failure"] is None
    assert fallback["secondary_failures"] == []
    assert fallback["environment_restored"] is True
    assert fallback["writer_exception_type"]
    assert fallback["writer_exception_message"]
    assert not list(receipt_path.parent.glob(".orchestration.json.*.tmp"))


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_compare_launcher_is_byte_stable_across_independent_attempt_roots(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    run_a, run_a_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="run-a",
    )
    run_b, run_b_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="run-b",
    )
    assert run_a.returncode == run_b.returncode == 0
    attempt_a = _invoke_fake_compare(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        run_a_receipt,
        run_b_receipt,
        attempt_name="compare-a",
    )
    attempt_b = _invoke_fake_compare(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        run_a_receipt,
        run_b_receipt,
        attempt_name="compare-b",
    )
    assert attempt_a[0].returncode == attempt_b[0].returncode == 0
    receipt_a_bytes = attempt_a[1].read_bytes()
    receipt_b_bytes = attempt_b[1].read_bytes()
    assert not receipt_a_bytes.startswith(b"\xef\xbb\xbf")
    assert not receipt_b_bytes.startswith(b"\xef\xbb\xbf")
    receipt_a = json.loads(receipt_a_bytes)
    receipt_b = json.loads(receipt_b_bytes)
    _assert_matches_schema("compare_receipt.schema.json", receipt_a)
    _assert_matches_schema("compare_receipt.schema.json", receipt_b)
    assert receipt_a["status"] == receipt_b["status"] == "succeeded"
    assert receipt_a["canonical_fingerprint_sha256"] == (
        receipt_b["canonical_fingerprint_sha256"]
    )
    assert attempt_a[2].read_bytes() == attempt_b[2].read_bytes()
    assert attempt_a[3].read_bytes() == attempt_b[3].read_bytes()
    assert receipt_a["environment"]["before"] == (
        receipt_a["environment"]["after_restore"]
    )


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
@pytest.mark.parametrize(
    ("failure_injection", "expected_stage", "expected_native_exit"),
    [
        ("required_environment_apply", "configure_environment", None),
        ("environment_restore", "restore_environment", 0),
    ],
)
def test_compare_launcher_environment_failure_receipts(
    tmp_path: Path,
    failure_injection: str,
    expected_stage: str,
    expected_native_exit: int | None,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    run_a, run_a_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="run-a",
    )
    run_b, run_b_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="run-b",
    )
    assert run_a.returncode == run_b.returncode == 0
    completed, compare_receipt, stdout_path, stderr_path = _invoke_fake_compare(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        run_a_receipt,
        run_b_receipt,
        attempt_name=f"compare-{failure_injection}",
        failure_injection=failure_injection,
    )
    assert completed.returncode == 1
    receipt = json.loads(compare_receipt.read_bytes())
    _assert_matches_schema("compare_receipt.schema.json", receipt)
    assert receipt["primary_failure"]["stage"] == expected_stage
    assert receipt["native_exit_code"] == expected_native_exit
    if failure_injection == "required_environment_apply":
        assert receipt["environment"]["restored"] is True
        assert receipt["environment"]["before"] == (
            receipt["environment"]["after_restore"]
        )
        assert not stdout_path.exists()
        assert not stderr_path.exists()
    else:
        assert receipt["status"] == "environment_restore_failed"
        assert receipt["environment"]["restored"] is False
        assert stdout_path.exists()
        assert stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_compare_launcher_rejects_canonical_chain_hash_mismatch_pre_execution(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    run_a, run_a_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="run-a",
    )
    run_b, run_b_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="run-b",
    )
    assert run_a.returncode == run_b.returncode == 0
    run_b_orchestration = json.loads(run_b_receipt.read_bytes())
    inner_path = Path(run_b_orchestration["result_receipt"]["path"])
    inner = json.loads(inner_path.read_bytes())
    canonical_path = Path(inner["canonical_result"]["path"])
    canonical_path.write_bytes(canonical_path.read_bytes() + b"\n")
    completed, compare_receipt, stdout_path, stderr_path = _invoke_fake_compare(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        run_a_receipt,
        run_b_receipt,
        attempt_name="compare-mismatch",
    )
    assert completed.returncode == 1
    receipt = json.loads(compare_receipt.read_bytes())
    _assert_matches_schema("compare_receipt.schema.json", receipt)
    assert receipt["primary_failure"]["stage"] == "bind_run_chains"
    assert "canonical result hash mismatch" in (
        receipt["primary_failure"]["exception_message"]
    )
    assert receipt["native_exit_code"] is None
    assert not stdout_path.exists()
    assert not stderr_path.exists()


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher is Windows-only")
def test_compare_launcher_rejects_same_receipt_reused_as_run_a_and_run_b(
    tmp_path: Path,
) -> None:
    repo, commit, environment_receipt = _build_fake_launcher_repository(tmp_path)
    run, run_receipt, _, _ = _invoke_fake_launcher(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        attempt_name="single-run",
    )
    assert run.returncode == 0
    completed, compare_receipt, stdout_path, stderr_path = _invoke_fake_compare(
        tmp_path,
        repo,
        commit,
        environment_receipt,
        run_receipt,
        run_receipt,
        attempt_name="compare-reused-chain",
    )
    assert completed.returncode == 1
    receipt = json.loads(compare_receipt.read_bytes())
    _assert_matches_schema("compare_receipt.schema.json", receipt)
    assert receipt["primary_failure"]["stage"] == "bind_run_chains"
    assert "distinct orchestration receipt paths" in (
        receipt["primary_failure"]["exception_message"]
    )
    assert receipt["native_exit_code"] is None
    assert not stdout_path.exists()
    assert not stderr_path.exists()


def test_external_root_rejects_checkout_descendant(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    with pytest.raises(CleanCheckoutError, match="outside the checkout"):
        ensure_external_root(repo, repo / "result")


def test_external_root_rejects_checkout_ancestor(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    with pytest.raises(CleanCheckoutError, match="must not contain"):
        ensure_external_root(repo, tmp_path)


def test_external_root_accepts_disjoint_sibling(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path / "checkout-parent")
    result = ensure_external_root(repo, tmp_path / "result")
    assert result == (tmp_path / "result").resolve()
    assert result.is_dir()


def test_external_writer_rejects_repository_path(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path)
    with pytest.raises(CleanCheckoutError, match="repository-local"):
        write_json_external(repo, repo / "result.json", {"status": "PASS"})


def test_altered_environment_receipt_fails_before_execution(
    tmp_path: Path,
) -> None:
    receipt = tmp_path / "environment_receipt.json"
    receipt.write_bytes(
        canonical_compact_json_bytes(
            {
                "schema_version": (
                    "iris_clean_checkout_external_environment_receipt_v1"
                )
            }
        )
    )
    with pytest.raises(CleanCheckoutError, match="receipt hash differs"):
        validate_external_environment(
            Path(__file__),
            receipt,
            {
                "immutable_environment_receipt_path": str(receipt),
                "immutable_environment_receipt_sha256": "0" * 64,
                "interpreter_sha256": "0" * 64,
                "external_environment_root": str(tmp_path),
                "environment_content_manifest_sha256": "0" * 64,
                "package_set_sha256": "0" * 64,
            },
        )


def _canonical_result(status: str = "PASS") -> dict[str, object]:
    return {
        "schema_version": "iris-clean-checkout-canonical-result-v2",
        "status": status,
        "subject": {
            "commit": "1" * 40,
            "tree": "2" * 40,
        },
        "test_identity_count": 1,
        "test_inventory_sha256": "3" * 64,
    }


def test_result_pair_rejects_semantic_equal_byte_different_payloads(
    tmp_path: Path,
) -> None:
    run_a = tmp_path / "run-a.json"
    run_b = tmp_path / "run-b.json"
    run_a.write_bytes(canonical_json_bytes(_canonical_result()))
    run_b.write_text(json.dumps(_canonical_result()), encoding="utf-8")
    with pytest.raises(CleanCheckoutError, match="result bytes differ"):
        validate_result_pair(run_a, run_b)


def test_result_pair_accepts_equivalent_passes(tmp_path: Path) -> None:
    run_a = tmp_path / "run-a.json"
    run_b = tmp_path / "run-b.json"
    payload = canonical_json_bytes(_canonical_result())
    run_a.write_bytes(payload)
    run_b.write_bytes(payload)
    result = validate_result_pair(run_a, run_b)
    assert result["status"] == "PASS"
    assert result["canonical_result_raw_bytes_equal"] is True
    assert result["canonical_results_equal"] is True


def test_receipt_and_registry_schemas_are_parseable_and_version_bound() -> None:
    contracts = Path(__file__).resolve().parents[1] / "contracts"
    expected = {
        "orchestration_receipt.schema.json": (
            "iris-clean-checkout-orchestration-receipt-v1"
        ),
        "compare_receipt.schema.json": "iris-clean-checkout-compare-receipt-v1",
        "output_isolation_batch_registry.schema.json": (
            "iris-output-isolation-batch-registry-v1"
        ),
    }
    for name, schema_version in expected.items():
        schema = json.loads((contracts / name).read_bytes())
        assert schema["$schema"] == (
            "https://json-schema.org/draft/2020-12/schema"
        )
        assert schema["properties"]["schema_version"]["const"] == (
            schema_version
        )


@pytest.mark.parametrize(
    ("variant_name", "variant"),
    [
        ("bom", lambda payload: b"\xef\xbb\xbf" + payload),
        ("crlf", lambda payload: payload.replace(b"\n", b"\r\n")),
        ("missing-trailing-newline", lambda payload: payload.rstrip(b"\n")),
        ("extra-trailing-newline", lambda payload: payload + b"\n"),
    ],
)
def test_result_pair_rejects_noncanonical_byte_variants(
    tmp_path: Path,
    variant_name: str,
    variant: Callable[[bytes], bytes],
) -> None:
    del variant_name
    run_a = tmp_path / "run-a.json"
    run_b = tmp_path / "run-b.json"
    canonical = canonical_json_bytes(_canonical_result())
    altered = variant(canonical)
    run_a.write_bytes(altered)
    run_b.write_bytes(altered)
    with pytest.raises(CleanCheckoutError, match="BOM|canonical JSON bytes"):
        validate_result_pair(run_a, run_b)


def test_full_source_policy_classifies_only_declared_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract_path = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "full_repository_gate.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    actual_repository_root = Path(__file__).resolve().parents[4]
    taxonomy = json.loads(
        (
            actual_repository_root
            / "Iris/_docs/round3/round3_test_taxonomy.json"
        ).read_text(encoding="utf-8")
    )
    output_projection = contract["execution_workspace"][
        "standalone_output_projection"
    ]
    assert (
        output_projection["environment_variable"]
        == "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
    )
    assert output_projection["pytest_projection"] is True
    assert output_projection["per_command_isolation"] is True
    assert output_projection["repository_output_write_count"] == 0
    repository_root = tmp_path / "repo"
    repository_root.mkdir()
    external_output = tmp_path / "external-output"
    monkeypatch.setenv(
        "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT",
        str(external_output),
    )
    assert repository_external_output_root(
        environment_variable=(
            "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
        ),
        default_root=repository_root / "Iris" / "output",
        repository_root=repository_root,
    ) == external_output.resolve()
    monkeypatch.setenv(
        "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT",
        str(repository_root / "Iris" / "output"),
    )
    with pytest.raises(ValueError, match="outside the repository"):
        repository_external_output_root(
            environment_variable=(
                "IRIS_CLEAN_CHECKOUT_LEGACY_OUTPUT_ROOT"
            ),
            default_root=repository_root / "Iris" / "output",
            repository_root=repository_root,
        )
    explicit_required_sources = {
        (
            "Iris/build/description/v2/tests/"
            "test_public_text_constituent_identity.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_dvf_3_3_korean_prose_compiler.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_naturalization_compiler_identity.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_iar_public_text_assessment.py"
        ),
    }
    explicit_paths = {
        row["path"]
        for row in contract["source_disposition_policy"][
            "explicit_current_required_sources"
        ]
    }
    assert explicit_required_sources <= explicit_paths
    roles = _full_required_source_roles(contract, taxonomy)
    required_classifications = {
        path: _classify_full_test_source(path, roles)
        for path in explicit_paths
    }
    expected_classification = {
        "execution_role": "required_pytest",
        "authority_class": "required_tracked_source",
        "classification_basis": "explicit_current_required_source",
    }
    assert all(
        required_classifications[path] == expected_classification
        for path in explicit_required_sources
    )
    _validate_explicit_current_required_classifications(
        contract,
        required_classifications,
    )
    validated_direct_dependencies = _validate_explicit_required_dependencies(
        contract,
        {
            row["path"]
            for row in contract["required_test_dependency_policy"][
                "explicit_direct_dependencies"
            ]
        },
        explicit_paths,
    )
    iar_source = (
        "Iris/build/description/v2/tests/"
        "test_iar_public_text_assessment.py"
    )
    direct_dependencies = [
        row
        for row in validated_direct_dependencies
        if row["test_source"] == iar_source
    ]
    assert len(direct_dependencies) == 3
    assert {row["test_source"] for row in direct_dependencies} == {
        iar_source
    }
    assert {row["dependency_role"] for row in direct_dependencies} == {
        "generic_assessment_contract",
        "generic_assessment_runner",
        "generic_assessment_no_write_validator",
    }
    consumer_evidence = contract["consumer_integration_evidence_policy"][
        "explicit_evidence_roles"
    ]
    assert len(consumer_evidence) == 1
    assert consumer_evidence[0]["execution_role"] == "not_required"
    assert (
        consumer_evidence[0]["evidence_role"]
        == "consumer_integration_evidence"
    )
    assert consumer_evidence[0]["path"] not in {
        row["path"] for row in validated_direct_dependencies
    }
    for demoted_source in explicit_required_sources:
        demoted = dict(required_classifications)
        demoted[demoted_source] = {
            "execution_role": "not_required",
            "authority_class": "historical_optional_evidence",
            "classification_basis": "historical heuristic",
        }
        with pytest.raises(
            CleanCheckoutError,
            match="classified as historical/optional",
        ):
            _validate_explicit_current_required_classifications(
                contract,
                demoted,
            )
    tool_paths = {
        row["path"]
        for row in contract["tool_disposition_policy"][
            "explicit_tool_roles"
        ]
    }
    tool_rows = _validate_explicit_tool_dispositions(
        contract,
        tool_paths,
        set(),
    )
    assert len(tool_rows) == 2
    with pytest.raises(
        CleanCheckoutError,
        match="required-test dependency",
    ):
        _validate_explicit_tool_dispositions(
            contract,
            tool_paths,
            {next(iter(tool_paths))},
        )
    dedicated_sources = {
        (
            "Iris/validation/test_workflow_consolidation/tests/"
            "test_public_text_phase7_scenario.py"
        ),
        (
            "Iris/validation/test_workflow_consolidation/tests/"
            "test_scenario_contracts.py"
        ),
        (
            "Iris/validation/test_workflow_consolidation/tests/"
            "test_validate_scenario_report.py"
        ),
    }
    source_policy = contract["source_disposition_policy"]
    dedicated_rows = {
        row["path"]: row
        for row in source_policy["explicit_dedicated_route_sources"]
    }
    assert dedicated_sources <= dedicated_rows.keys()
    for path in dedicated_sources:
        row = dedicated_rows[path]
        assert row["owner_decision"] == "not_applicable_dedicated_route"
        assert row["reason"].strip()
        assert _classify_full_test_source(path, roles) == {
            "execution_role": "not_required",
            "authority_class": "dedicated_route_validation",
            "classification_basis": row["reason"],
        }
    evidence_rows = {
        row["path"]: row
        for row in source_policy["evidence_only_sources"]
    }
    assert set(evidence_rows) == set()
    for path, row in evidence_rows.items():
        assert row["physical_preservation"] == "executable_source"
        assert _classify_full_test_source(path, roles) == {
            "execution_role": "not_required",
            "authority_class": "evidence_only_executable_source",
            "classification_basis": row["reason"],
        }
    disposition_surfaces = (
        "explicit_current_required_sources",
        "explicit_historical_optional_sources",
        "explicit_dedicated_route_sources",
        "hermetic_test_fixture_sources",
        "evidence_only_sources",
        "obsolete_or_misrouted_sources",
    )
    for path in dedicated_sources:
        assert sum(
            row["path"] == path
            for surface in disposition_surfaces
            for row in source_policy[surface]
        ) == 1
    required_selection = contract["required_pytest_selection"]
    current_taxonomy_sources = {
        row["source_file"]
        for row in taxonomy["rows"]
        if row["contract_class"] == required_selection["contract_class"]
        and row["state"] == required_selection["state"]
    }
    required_source_paths = {
        *current_taxonomy_sources,
        *required_selection["additional_source_paths"],
        *(
            node_id.split("::", 1)[0]
            for node_id in required_selection["additional_node_ids"]
        ),
        *(
            row["path"]
            for row in contract["required_standalone_validations"]
        ),
        *(
            row["path"]
            for row in source_policy["explicit_current_required_sources"]
        ),
    }
    assert dedicated_sources.isdisjoint(required_source_paths)
    configured_policy = json.loads(
        (
            actual_repository_root
            / "Iris/_docs/round3/round3_pytest_source_classification.json"
        ).read_text(encoding="utf-8")
    )
    configured_source_paths = {
        row["source_file"]
        for surface in (
            "reviewed_sources",
            "planned_sources",
            "mixed_sources",
            "additional_sources",
            "excluded_sources",
        )
        for row in configured_policy[surface]
    }
    assert dedicated_sources.isdisjoint(configured_source_paths)
    pytest_ini = (actual_repository_root / "pytest.ini").read_text(
        encoding="utf-8"
    )
    testpaths_match = re.search(
        r"(?ms)^testpaths\s*=\s*(.*?)(?=^[^\s#;]|\Z)",
        pytest_ini,
    )
    assert testpaths_match is not None
    configured_roots = {
        (
            actual_repository_root
            / (token.replace("\\", "/").rstrip("/") or ".")
        ).resolve()
        for token in testpaths_match.group(1).split()
    }
    dedicated_source_paths = {
        (actual_repository_root / path).resolve()
        for path in dedicated_sources
    }
    assert all(
        root != path and root not in path.parents
        for path in dedicated_source_paths
        for root in configured_roots
    )
    historical = _classify_full_test_source(
        "Iris/build/description/v2/tests/test_old_authority.py",
        {},
    )
    assert historical["authority_class"] == "historical_optional_evidence"
    with pytest.raises(CleanCheckoutError, match="unclassified"):
        _classify_full_test_source("Iris/test/test_unknown.py", {})


def test_g5_current_capsule_separates_historical_raw_and_current_claim() -> None:
    repository_root = Path(__file__).resolve().parents[4]
    contract_path = (
        repository_root
        / "Iris/validation/clean_checkout/contracts/full_repository_gate.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    g5 = contract["g5_required_evidence"]
    assert g5["claim_id"] == "current_capsule_attestation_v2"
    assert g5["external_archive_dependency_allowed"] is False
    manifest_binding = g5["capsule_manifest"]
    manifest_raw = _git_bytes(
        repository_root,
        "show",
        f"HEAD:{manifest_binding['path']}",
    )
    assert hashlib.sha256(manifest_raw).hexdigest() == manifest_binding[
        "git_blob_raw_sha256"
    ]
    manifest = json.loads(manifest_raw)
    assert manifest["superseded_claim_id"] == "raw_repository_evidence_v1"
    assert manifest["external_archive_is_current_route_dependency"] is False
    assert manifest["direct_row_count"] == 18
    assert manifest["raw_capsule_row_count"] == 14
    assert manifest["digest_capsule_row_count"] == 4
    assert manifest["raw_retained_bytes"] <= 2_359_296

    compiler = g5["compiler_identity"]
    transition_binding = compiler["successor_transition"]
    subject_commit = _git(repository_root, "rev-parse", "HEAD")
    transition_raw = _git_bytes(
        repository_root,
        "show",
        f"{subject_commit}:{transition_binding['path']}",
    )
    transition = json.loads(transition_raw)
    assert hashlib.sha256(transition_raw).hexdigest() == transition_binding[
        "git_blob_raw_sha256"
    ]
    assert transition_binding["path"] in g5["current_required_paths"]
    validated = _validate_g5_compiler_identity_transition(
        repository_root,
        subject_commit,
        compiler,
        transition,
        True,
    )
    assert validated == {
        "algorithm_id": (
            "naturalization_compiler_identity_sha256_lf_normalized_"
            "ordered_paths_v2"
        ),
        "ordered_path_count": 19,
        "historical_attested_aggregate_sha256": (
            "2dcff095b1cc34c8fb6d3ad735ac8f9d0ca2affe259f6bb97870b19e7235cc7f"
        ),
        "current_aggregate_sha256": (
            "3b3aefd5fb21a032a2e677eda61f94023af8604d6abb18b550551f8de2413287"
        ),
        "changed_constituent_count": 19,
        "unchanged_constituent_count": 0,
        "current_basis_validation_mode": "exact_git_object",
    }

    tampered_compiler = copy.deepcopy(compiler)
    tampered_compiler["current_aggregate_sha256"] = "0" * 64
    with pytest.raises(
        CleanCheckoutError, match="contract aggregate split mismatch"
    ):
        _validate_g5_compiler_identity_transition(
            repository_root,
            subject_commit,
            tampered_compiler,
            transition,
            True,
        )

    tampered_changed = copy.deepcopy(transition)
    tampered_changed["changed_rows"][0]["current_sha256_lf"] = "0" * 64
    with pytest.raises(CleanCheckoutError, match="derived changed-row mismatch"):
        _validate_g5_compiler_identity_transition(
            repository_root,
            subject_commit,
            compiler,
            tampered_changed,
            True,
        )

    tampered_provenance = copy.deepcopy(transition)
    tampered_provenance["changed_rows"][0]["current_last_writer_tree"] = (
        "0" * 40
    )
    with pytest.raises(CleanCheckoutError, match="derived changed-row mismatch"):
        _validate_g5_compiler_identity_transition(
            repository_root,
            subject_commit,
            compiler,
            tampered_provenance,
            True,
        )


def test_ignored_status_snapshot_excludes_nonignored_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "Iris.validation.clean_checkout.run_iris_clean_checkout_validation."
        "_status_snapshot",
        lambda repo, include_ignored=True: (
            "1 .M N... tracked.py\n? local.py\n! ignored-output/\n"
        ),
    )
    assert _ignored_status_snapshot(tmp_path) == "! ignored-output/"


def test_full_node_identity_normalization() -> None:
    node_id = (
        "Iris/build/description/v2/tests/test_sample.py::"
        "SampleTest::test_value[param]"
    )
    assert _normalized_test_id(node_id) == (
        "test_sample.SampleTest.test_value"
    )


def test_full_materialization_target_rejects_parent_escape(
    tmp_path: Path,
) -> None:
    checkout = (tmp_path / "checkout").resolve()
    checkout.mkdir()
    with pytest.raises(CleanCheckoutError, match="unsafe"):
        _safe_checkout_target(checkout, "../outside.json")


def test_offline_tool_inventory_keeps_denominator_axes_and_registry_bindings(
    tmp_path: Path,
) -> None:
    repo = (tmp_path / "inventory-repo").resolve()
    tools_root = repo / "Iris" / "build" / "description" / "v2" / "tools" / "build"
    staging_root = repo / "Iris" / "build" / "description" / "v2" / "staging"
    closure_path = (
        repo / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
    )
    schema_path = (
        repo
        / "Iris"
        / "validation"
        / "clean_checkout"
        / "contracts"
        / "output_isolation_batch_registry.schema.json"
    )
    tools_root.mkdir(parents=True)
    staging_root.mkdir(parents=True)
    closure_path.parent.mkdir(parents=True)
    schema_path.parent.mkdir(parents=True)
    (tools_root / "core.py").write_text(
        "import shared_io\n\ndef main():\n    return shared_io.VALUE\n",
        encoding="utf-8",
    )
    (tools_root / "tooling.py").write_text(
        "def validate():\n    return True\n",
        encoding="utf-8",
    )
    (tools_root / "shared_io.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    (tools_root / "mystery.py").write_text(
        "VALUE = 2\n",
        encoding="utf-8",
    )
    (staging_root / "sealed_receipt.json").write_bytes(
        canonical_json_bytes({"status": "SEALED"})
    )
    closure_path.write_bytes(
        canonical_json_bytes(
            {
                "current_closure_modules": ["core"],
                "current_route_allowed_tooling_modules": ["tooling"],
            }
        )
    )
    source_schema = (
        Path(__file__).resolve().parents[1]
        / "contracts"
        / "output_isolation_batch_registry.schema.json"
    )
    schema_path.write_bytes(source_schema.read_bytes())
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _git(repo, "add", ".")
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Codex Fixture",
            "-c",
            "user.email=codex-fixture@example.invalid",
            "commit",
            "-q",
            "-m",
            "inventory fixture",
        ],
        check=True,
    )
    commit = _git(repo, "rev-parse", "HEAD")
    output_a = (tmp_path / "inventory-a").resolve()
    output_b = (tmp_path / "inventory-b").resolve()
    result_a = build_inventory(
        repo,
        commit,
        output_a,
        materialized_root=repo,
        unknown_role_ceiling=1,
    )
    result_b = build_inventory(
        repo,
        commit,
        output_b,
        materialized_root=repo,
        unknown_role_ceiling=1,
    )
    assert result_a["status"] == result_b["status"] == "PASS"
    manifests_a = output_a / "manifests"
    manifests_b = output_b / "manifests"
    stable_manifests = {
        "denominator_registry.json",
        "tool_inventory.json",
        "shared_module_manifest.json",
        "serialization_contract_census.json",
        "tool_role_manifest.json",
        "retention_inventory.json",
        "receipt_migration_batch_registry.json",
    }
    for name in stable_manifests:
        assert (manifests_a / name).read_bytes() == (
            manifests_b / name
        ).read_bytes()
    denominator = json.loads(
        (manifests_a / "denominator_registry.json").read_bytes()
    )
    counts = {
        row["denominator_id"]: row["count"] for row in denominator["rows"]
    }
    assert counts == {
        "allowed_tooling": 1,
        "current_core": 1,
        "tools_build_recursive_physical": 4,
        "tools_build_recursive_tracked": 4,
        "tools_build_root_direct_physical": 4,
        "tools_build_root_direct_tracked": 4,
    }
    roles = json.loads((manifests_a / "tool_role_manifest.json").read_bytes())
    assert roles["total"] == 4
    assert roles["role_axis"]["classified_role"] == 3
    assert roles["role_axis"]["unknown_role"] == 1
    assert sum(roles["owner_axis"].values()) == roles["total"]
    assert sum(roles["caller_axis"].values()) == roles["total"]
    mystery = next(row for row in roles["rows"] if row["path"].endswith("mystery.py"))
    assert mystery["disposition"] == "move_delete_consolidate_forbidden"
    assert mystery["decision_owner"] == "repository_owner"
    shared = json.loads(
        (manifests_a / "shared_module_manifest.json").read_bytes()
    )
    assert {
        "caller": "Iris/build/description/v2/tools/build/core.py",
        "provider": "Iris/build/description/v2/tools/build/shared_io.py",
    } in shared["edges"]
    retention = json.loads(
        (manifests_a / "retention_inventory.json").read_bytes()
    )
    assert retention["tracked_count"] == retention["physical_count"] == 1
    assert retention["rows"][0]["mutation_disposition"] == (
        "move_delete_forbidden"
    )
    registry_path = manifests_a / "output_isolation_batch_registry.json"
    registry = json.loads(registry_path.read_bytes())
    _assert_matches_schema(
        "output_isolation_batch_registry.schema.json", registry
    )
    ratification = json.loads(
        (
            manifests_a
            / "output_isolation_batch_registry.ratification.json"
        ).read_bytes()
    )
    assert registry["selected_rows"] == []
    assert registry["selected_owner_unknown_count"] == 0
    assert registry["selected_unknown_role_count"] == 0
    schema_blob = _git_bytes(
        repo,
        "show",
        (
            f"{commit}:Iris/validation/clean_checkout/contracts/"
            "output_isolation_batch_registry.schema.json"
        ),
    )
    assert registry["schema"]["sha256"] == hashlib.sha256(schema_blob).hexdigest()
    assert ratification["registry"]["sha256"] == _sha256(registry_path)
    assert ratification["source_mutation_authorized"] is False
