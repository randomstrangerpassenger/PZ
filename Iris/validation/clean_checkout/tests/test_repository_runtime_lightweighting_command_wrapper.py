from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[4]
WRAPPER = REPO / "Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1"
REQUIRED_ENVIRONMENT = {
    "GIT_OPTIONAL_LOCKS": "0",
    "PIP_NO_INDEX": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONNOUSERSITE": "1",
}
CLEARED_ENVIRONMENT = ["PYTHONHOME", "PYTHONPATH", "PYTEST_ADDOPTS"]
LONG_PATH_PARENT = Path("long-path-fixture").joinpath(
    *(f"segment-{index}-" + ("x" * 54) for index in range(4))
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extended_windows_path(path: Path) -> str:
    absolute = str(path.absolute())
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def powershell() -> str:
    executable = shutil.which("powershell")
    if executable is None:
        pytest.fail("Windows PowerShell 5.1 is required by the wrapper contract")
    return executable


def create_junction(link: Path, target: Path) -> None:
    completed = subprocess.run(
        [
            powershell(),
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
    assert completed.returncode == 0, completed.stderr


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def fixture_checkout(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    repo = tmp_path / "checkout"
    contracts = repo / "Iris/validation/clean_checkout/contracts"
    authority = repo / "Iris/validation/clean_checkout/authority"
    contracts.mkdir(parents=True)
    authority.mkdir(parents=True)
    fixture_wrapper = repo / "Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1"
    fixture_wrapper.write_bytes(WRAPPER.read_bytes())
    git(repo, "init")
    git(repo, "config", "user.email", "iris-tests@example.invalid")
    git(repo, "config", "user.name", "Iris Tests")
    git(repo, "config", "core.longpaths", "true")

    external = tmp_path / "external"
    external.mkdir()
    environment_receipt = external / "environment.json"
    write_json(environment_receipt, {"interpreter": {"path": str(Path(sys.executable).resolve())}})
    environment_record = authority / "responsibility_refactor_environment_fixture_v1.json"
    write_json(
        environment_record,
        {
            "schema_version": "iris-responsibility-refactor-environment-authority-v1",
            "environment_contract": {
                "external_environment_root": str(Path(sys.prefix).resolve()),
                "immutable_environment_receipt_path": str(environment_receipt.resolve()),
                "immutable_environment_receipt_sha256": sha256(environment_receipt),
                "interpreter_sha256": sha256(Path(sys.executable).resolve()),
            },
        },
    )
    write_json(
        authority / "current_environment.json",
        {
            "schema_version": "iris-responsibility-refactor-environment-locator-v1",
            "record_path": (
                "Iris/validation/clean_checkout/authority/"
                "responsibility_refactor_environment_fixture_v1.json"
            ),
            "record_sha256": sha256(environment_record),
        },
    )
    write_json(
        contracts / "repository_runtime_lightweighting_output_policy.json",
        {
            "schema_version": "iris_repository_runtime_lightweighting_output_policy_v1",
            "required_environment": REQUIRED_ENVIRONMENT,
            "cleared_ambient_environment": CLEARED_ENVIRONMENT,
        },
    )
    delta = external / "delta.json"
    write_json(
        delta,
        {
            "schema_version": "iris_repository_runtime_lightweighting_environment_delta_v1",
            "set": REQUIRED_ENVIRONMENT,
            "clear": CLEARED_ENVIRONMENT,
        },
    )
    (repo / ".gitignore").write_text(
        "ignored-write.txt\nignored-empty-directory/\n",
        encoding="utf-8",
    )
    long_parent = repo / LONG_PATH_PARENT
    long_parent_extended = Path(extended_windows_path(long_parent))
    long_parent_extended.mkdir(parents=True)
    (long_parent_extended / "tracked.txt").write_text(
        "long-path-census\n", encoding="utf-8"
    )
    assert len(str(long_parent.absolute())) > 260
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    commit, tree = completed.stdout.splitlines()
    subject = external / "subject.json"
    write_json(
        subject,
        {
            "schema_version": "fixture-subject-v1",
            "subject_kind": "bootstrap_validation_subject",
            "claim_id": "fixture-claim",
            "commit": commit,
            "tree": tree,
        },
    )
    return repo.resolve(), external.resolve(), subject.resolve(), delta.resolve()


def run_wrapper(
    repo: Path,
    external: Path,
    subject: Path,
    delta: Path,
    *,
    command_id: str,
    argv: list[str],
    output_assertion: str = "none",
    prior: list[Path] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, object], Path]:
    receipt = external / "receipts" / f"{command_id}.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    spec = external / "specs" / f"{command_id}.json"
    payload: dict[str, object] = {
        "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
        "executable": str(Path(sys.executable).resolve()),
        "argv": argv,
        "working_directory": str(repo),
        "subject_receipt": str(subject),
        "environment_receipt": str(external / "environment.json"),
        "environment_delta": str(delta),
        "claim_id": "fixture-claim",
        "command_id": command_id,
        "command_receipt": str(receipt),
        "output_assertion": output_assertion,
    }
    if prior is not None:
        payload["prior_command_receipts"] = [str(path) for path in prior]
    write_json(spec, payload)
    completed = subprocess.run(
        [
            powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repo / "Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1"),
            "-CommandSpec",
            str(spec),
        ],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert receipt.is_file(), completed.stderr
    return completed, json.loads(receipt.read_text(encoding="utf-8")), receipt


def test_scalar_command_spec_preserves_windows_argv_and_streams(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    observed = external / "observed.json"
    corpus = [
        "",
        "white space",
        'embedded"quote',
        'backslash-before-\\"quote',
        "trailing\\",
        "한글-경로",
        "-leading-dash",
        "semi;colon",
        "wild*card?",
    ]
    code = (
        "import json,sys; "
        "open(sys.argv[1], 'w', encoding='utf-8').write(json.dumps(sys.argv[2:], ensure_ascii=False)); "
        "print('stdout-marker'); print('stderr-marker', file=sys.stderr)"
    )
    completed, receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="argv-round-trip",
        argv=["-B", "-c", code, str(observed), *corpus],
        output_assertion="checkout_unchanged",
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(observed.read_text(encoding="utf-8")) == corpus
    assert receipt["decoded_argv"] == ["-B", "-c", code, str(observed), *corpus]
    assert receipt["terminal_status"] == "pass"
    assert receipt["output_assertion"]["status"] == "pass"
    assert Path(receipt["stdout"]["path"]).read_bytes() == b"stdout-marker\r\n"
    assert Path(receipt["stderr"]["path"]).read_bytes() == b"stderr-marker\r\n"
    assert receipt["successor_policy"]["sha256"] == sha256(
        repo / "Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json"
    )


def test_checkout_unchanged_detects_ignored_write(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    code = "from pathlib import Path; Path('ignored-write.txt').write_text('changed', encoding='utf-8')"
    completed, receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="ignored-write",
        argv=["-B", "-c", code],
        output_assertion="checkout_unchanged",
    )
    assert completed.returncode != 0
    assert receipt["native_exit_code"] == 0
    assert receipt["semantic_exit_code"] != 0
    assert receipt["output_assertion"]["delta"]["ignored_delta_count"] == 1


def test_checkout_unchanged_detects_empty_ignored_directory(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    ignored_directory = LONG_PATH_PARENT / "ignored-empty-directory"
    ignored_directory_extended = extended_windows_path(repo / ignored_directory)
    code = f"from pathlib import Path; Path({ignored_directory_extended!r}).mkdir()"
    completed, receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="ignored-empty-directory",
        argv=["-B", "-c", code],
        output_assertion="checkout_unchanged",
    )
    assert completed.returncode != 0
    assert receipt["native_exit_code"] == 0
    assert receipt["semantic_exit_code"] != 0
    rows = receipt["output_assertion"]["delta"]["rows"]
    assert receipt["output_assertion"]["delta"]["unreadable_count"] == 0
    assert any(
        row["path"] == ignored_directory.as_posix()
        and row["change"] == "added"
        and row["after"]["entry_kind"] == "directory"
        for row in rows
    )


def test_junction_receipt_parent_targeting_checkout_is_rejected_before_any_write(
    tmp_path: Path,
) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    repository_target = repo / "junction-output-target"
    repository_target.mkdir()
    receipt_alias = external / "junction-receipts"
    create_junction(receipt_alias, repository_target)
    receipt = receipt_alias / "junction-receipt.json"
    spec = external / "specs/junction-receipt.json"
    write_json(
        spec,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
            "executable": str(Path(sys.executable).resolve()),
            "argv": [
                "-B",
                "-c",
                "from pathlib import Path; Path('must-not-run.txt').write_text('ran')",
            ],
            "working_directory": str(repo),
            "subject_receipt": str(subject),
            "environment_receipt": str(external / "environment.json"),
            "environment_delta": str(delta),
            "claim_id": "fixture-claim",
            "command_id": "junction-receipt",
            "command_receipt": str(receipt),
            "output_assertion": "none",
        },
    )
    completed = subprocess.run(
        [
            powershell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repo / "Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1"),
            "-CommandSpec",
            str(spec),
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert completed.returncode != 0
    assert "reparse point" in completed.stderr.lower()
    assert not receipt.exists()
    assert not (repo / "must-not-run.txt").exists()
    assert not any(repository_target.iterdir())


def test_prior_failure_prevents_later_native_command(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    failed, failed_receipt, failed_path = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="current-route-failure",
        argv=["-B", "-c", "raise SystemExit(7)"],
    )
    assert failed.returncode == 7
    assert failed_receipt["terminal_status"] == "fail"

    marker = external / "must-not-exist.txt"
    later, later_receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="historical-success",
        argv=["-B", "-c", f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"],
        prior=[failed_path],
    )
    assert later.returncode != 0
    assert later_receipt["terminal_status"] == "not_run_due_to_prior_failure"
    assert later_receipt["disposition"] == "not_run_due_to_prior_failure"
    assert later_receipt["native_exit_code"] is None
    assert not marker.exists()


def test_claim_and_environment_authority_mismatches_fail_closed(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    original = json.loads(subject.read_text(encoding="utf-8"))
    write_json(subject, {**original, "claim_id": "other"})
    completed, receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="claim-mismatch",
        argv=["-B", "-c", "print('must not run')"],
    )
    assert completed.returncode != 0
    assert receipt["native_exit_code"] is None
    assert receipt["failure"]["kind"] == "exception"


def test_json_scalar_argv_is_rejected_without_execution(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    receipt = external / "receipts/scalar-argv.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    spec = external / "specs/scalar-argv.json"
    write_json(
        spec,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
            "executable": str(Path(sys.executable).resolve()),
            "argv": "-B",
            "working_directory": str(repo),
            "subject_receipt": str(subject),
            "environment_receipt": str(external / "environment.json"),
            "environment_delta": str(delta),
            "claim_id": "fixture-claim",
            "command_id": "scalar-argv",
            "command_receipt": str(receipt),
            "output_assertion": "none",
        },
    )
    completed = subprocess.run(
        [powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(repo / "Iris/validation/clean_checkout/invoke_repository_runtime_lightweighting_command.ps1"), "-CommandSpec", str(spec)],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert completed.returncode != 0
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["native_exit_code"] is None
    assert payload["failure"]["exception_message"] == "command spec argv must remain a JSON array"


def test_invoked_repository_script_is_bound_to_exact_execution_commit(tmp_path: Path) -> None:
    repo, external, subject, delta = fixture_checkout(tmp_path)
    script = repo / "probe.py"
    script.write_text("print('bound')\n", encoding="utf-8", newline="\n")
    git(repo, "add", "probe.py")
    git(repo, "commit", "-m", "add probe")
    completed_identity = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    commit, tree = completed_identity.stdout.splitlines()
    subject_payload = json.loads(subject.read_text(encoding="utf-8"))
    write_json(subject, {**subject_payload, "commit": commit, "tree": tree})

    completed, receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="bound-script",
        argv=["-B", "probe.py"],
    )
    assert completed.returncode == 0, completed.stderr
    assert receipt["subject_receipt"]["execution_commit"] == commit
    assert receipt["subject_receipt"]["execution_tree"] == tree
    assert receipt["invoked_repository_files"] == [
        {
            "logical_path": "probe.py",
            "actual_path": script.as_posix(),
            "execution_commit": commit,
            "git_blob_id": subprocess.run(
                ["git", "-C", str(repo), "rev-parse", f"{commit}:probe.py"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.strip(),
            "working_sha256": sha256(script),
        }
    ]

    script.write_text("print('tampered')\n", encoding="utf-8", newline="\n")
    rejected, rejected_receipt, _ = run_wrapper(
        repo,
        external,
        subject,
        delta,
        command_id="tampered-script",
        argv=["-B", "probe.py"],
    )
    assert rejected.returncode != 0
    assert rejected_receipt["native_exit_code"] is None
    assert "differs from exact execution commit" in rejected_receipt["failure"]["exception_message"]
