from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
AUDITOR = REPO / "Iris/validation/execution/audit_test_output_isolation.py"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(*args: object, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(AUDITOR), *map(str, args)],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def fixture_contracts(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    repo = (tmp_path / "checkout").resolve()
    repo.mkdir(parents=True)
    (repo / ".gitattributes").write_text("* text eol=lf\n", encoding="utf-8", newline="\n")
    source = repo / "Iris/build/description/v2/tests/test_selected.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        """\
import json
from pathlib import Path

def test_selected(tmp_path):
    target = tmp_path / "result.json"
    target.write_text(json.dumps({"ok": True}), encoding="utf-8")
""",
        encoding="utf-8",
        newline="\n",
    )
    taxonomy = repo / "Iris/_docs/round3/round3_test_taxonomy.json"
    required = repo / "Iris/validation/execution/required_validations.json"
    write_json(
        taxonomy,
        {
            "rows": [
                {
                    "test_id": "test_selected.test_selected",
                    "source_file": "Iris/build/description/v2/tests/test_selected.py",
                    "contract_class": "current",
                    "state": "ok",
                }
            ]
        },
    )
    write_json(
        required,
        {
            "required_tests": [
                {"test_id": "test_selected.test_selected", "role": "current"},
                {"test_id": "test_optional.test_optional", "role": "historical"},
            ],
            "applicability_overrides": {
                "historical_optional_evidence": {
                    "tests": [{"test_id": "test_optional.test_optional"}]
                }
            },
        },
    )
    runner = repo / "Iris/validation/execution/run_required_contract_tests.py"
    runner.write_text("raise SystemExit(0)\n", encoding="utf-8", newline="\n")
    successor = repo / "Iris/validation/execution/contracts/isolated_command_output_policy.json"
    write_json(successor, {"schema_version": "iris_repository_runtime_lightweighting_output_policy_v1"})
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "core.longpaths", "true"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Iris Tests",
            "-c",
            "user.email=iris-tests@example.invalid",
            "commit",
            "-q",
            "-m",
            "fixture",
        ],
        check=True,
    )
    external = (tmp_path / "external").resolve()
    external.mkdir()
    return repo, external, taxonomy, required


def inventory(repo: Path, external: Path) -> tuple[subprocess.CompletedProcess[str], Path]:
    output = external / "static-inventory.json"
    result = invoke(
        "inventory",
        "--repo",
        repo,
        "--taxonomy",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations",
        "Iris/validation/execution/required_validations.json",
        "--out",
        output,
        cwd=repo,
    )
    return result, output


def test_inventory_maps_every_required_id_source_import_and_write_site(tmp_path: Path) -> None:
    repo, external, _, _ = fixture_contracts(tmp_path)
    completed, output = inventory(repo, external)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["selected_test_count"] == 1
    assert payload["historical_optional_test_count"] == 1
    assert payload["historical_optional_test_ids"] == ["test_optional.test_optional"]
    assert payload["selected_source_count"] == 1
    assert payload["selected_tests"][0]["test_id"] == "test_selected.test_selected"
    selected_source = next(row for row in payload["sources"] if row["source_role"] == "selected_test_module")
    assert selected_source["imports"] == ["json", "pathlib"]
    assert selected_source["write_sites"] == [
        {
            "call": "target.write_text",
            "line": 6,
            "resolved_sink": "bounded_temporary_contract",
            "resolution_status": "resolved",
        }
    ]
    assert payload["unresolved_write_site_count"] == 0
    assert payload["source_census_sha256"]


def test_inventory_recurses_local_imports_and_rejects_nonliteral_dynamic_imports(tmp_path: Path) -> None:
    repo, external, _, _ = fixture_contracts(tmp_path)
    source = repo / "Iris/build/description/v2/tests/test_selected.py"
    helper = source.with_name("selected_helper.py")
    helper.write_text("VALUE = 1\n", encoding="utf-8", newline="\n")
    safe_source = """\
import importlib.util
from pathlib import Path
from selected_helper import VALUE

HELPER = Path(__file__).resolve().parent / f"selected_{'helper'}.py"

def load_module(path):
    spec = importlib.util.spec_from_file_location("selected_dynamic", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_selected():
    assert VALUE == 1
    assert load_module(HELPER).VALUE == 1
"""
    source.write_text(
        safe_source,
        encoding="utf-8",
        newline="\n",
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "local closure"], check=True)
    completed, output = inventory(repo, external)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["closure_source_count"] == 3
    assert any(row["source_file"].endswith("selected_helper.py") for row in payload["sources"])

    output.unlink()
    source.write_text(
        """\
import importlib.util
from pathlib import Path
from selected_helper import VALUE

TOOLS = Path(__file__).resolve().parent

def load_module():
    path = TOOLS / "selected_helper.py"
    spec = importlib.util.spec_from_file_location("selected_dynamic", path)
    return importlib.util.module_from_spec(spec)

def test_selected():
    assert VALUE == 1
    assert load_module().VALUE == 1
""",
        encoding="utf-8",
        newline="\n",
    )
    local_static, output = inventory(repo, external)
    assert local_static.returncode == 0, local_static.stderr
    output.unlink()

    source.write_text(
        """\
import importlib.util
from pathlib import Path

def load_module(runtime_base):
    spec = importlib.util.spec_from_file_location(
        "selected_dynamic", runtime_base / "selected_helper.py"
    )
    return importlib.util.module_from_spec(spec)

def test_selected():
    assert load_module(Path.cwd())
""",
        encoding="utf-8",
        newline="\n",
    )
    unresolved_base, _ = inventory(repo, external)
    assert unresolved_base.returncode != 0
    assert "unresolved local/dynamic imports" in unresolved_base.stderr

    source.write_text(
        safe_source.replace(
            "def test_selected():",
            "loader = load_module\n\ndef test_selected():",
        ).replace("load_module(HELPER)", "loader(HELPER)"),
        encoding="utf-8",
        newline="\n",
    )
    aliased_wrapper, _ = inventory(repo, external)
    assert aliased_wrapper.returncode != 0
    assert "unresolved local/dynamic imports" in aliased_wrapper.stderr

    source.write_text(
        safe_source.replace(
            "    assert VALUE == 1",
            "    HELPER = Path.cwd()\n    assert VALUE == 1",
        ),
        encoding="utf-8",
        newline="\n",
    )
    shadowed_argument, _ = inventory(repo, external)
    assert shadowed_argument.returncode != 0
    assert "unresolved local/dynamic imports" in shadowed_argument.stderr

    source.write_text(
        safe_source.replace(
            "def test_selected():\n    assert VALUE == 1\n    assert load_module(HELPER).VALUE == 1",
            """\
def outer():
    HELPER = Path.cwd()

    def inner():
        return load_module(HELPER)

    return inner()

def test_selected():
    assert VALUE == 1
    assert outer()""",
        ),
        encoding="utf-8",
        newline="\n",
    )
    closure_shadow, _ = inventory(repo, external)
    assert closure_shadow.returncode != 0
    assert "unresolved local/dynamic imports" in closure_shadow.stderr

    source.write_text(safe_source, encoding="utf-8", newline="\n")
    helper.write_text(
        "import importlib\n\ndef load(name):\n    return importlib.import_module(name)\n",
        encoding="utf-8",
        newline="\n",
    )
    rejected, _ = inventory(repo, external)
    assert rejected.returncode != 0
    assert "unresolved local/dynamic imports" in rejected.stderr


def test_inventory_rejects_missing_taxonomy_mapping_and_repository_local_output(tmp_path: Path) -> None:
    repo, external, taxonomy, _ = fixture_contracts(tmp_path)
    write_json(taxonomy, {"rows": []})
    missing, _ = inventory(repo, external)
    assert missing.returncode != 0
    assert "lack taxonomy source rows" in missing.stderr

    write_json(
        taxonomy,
        {
            "rows": [
                {
                    "test_id": "test_selected.test_selected",
                    "source_file": "Iris/build/description/v2/tests/test_selected.py",
                    "contract_class": "current",
                    "state": "ok",
                }
            ]
        },
    )
    local = invoke(
        "inventory",
        "--repo",
        repo,
        "--taxonomy",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations",
        "Iris/validation/execution/required_validations.json",
        "--out",
        repo / "local-output.json",
        cwd=repo,
    )
    assert local.returncode != 0
    assert "must be repository-external" in local.stderr


def write_dynamic_receipt(repo: Path, external: Path, route_result: Path, delta: dict[str, int] | None = None) -> Path:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    commit, tree = completed.stdout.splitlines()
    subject = external / "audit-subject.json"
    write_json(
        subject,
        {
            "subject_kind": "bootstrap_validation_subject",
            "claim_id": "audit-claim",
            "commit": commit,
            "tree": tree,
        },
    )
    receipt_root = external / "command-receipts"
    receipt = receipt_root / "004-route-audit-dynamic-current.json"
    spec = receipt_root / "004-route-audit-dynamic-current.command.json"
    argv = [
        "-B",
        "Iris/validation/execution/run_required_contract_tests.py",
        "--class",
        "current",
        "--enforce-current-build-closure",
        "--out",
        str(route_result),
    ]
    write_json(
        spec,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_spec_v1",
            "executable": str(Path(sys.executable).resolve()),
            "argv": argv,
            "working_directory": str(repo),
            "claim_id": "audit-claim",
            "command_id": "004-route-audit-dynamic-current",
            "subject_receipt": str(subject),
            "command_receipt": str(receipt),
            "output_assertion": "checkout_unchanged",
        },
    )
    clean_delta = {
        "changed_count": 0,
        "tracked_delta_count": 0,
        "untracked_delta_count": 0,
        "ignored_delta_count": 0,
        "unreadable_count": 0,
    }
    if delta:
        clean_delta.update(delta)
    successor = repo / "Iris/validation/execution/contracts/isolated_command_output_policy.json"
    runner = repo / "Iris/validation/execution/run_required_contract_tests.py"
    runner_blob = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"{commit}:Iris/validation/execution/run_required_contract_tests.py"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    write_json(
        receipt,
        {
            "schema_version": "iris_repository_runtime_lightweighting_command_receipt_v1",
            "command_id": "004-route-audit-dynamic-current",
            "command_receipt": str(receipt),
            "terminal_status": "pass",
            "native_exit_code": 0,
            "semantic_exit_code": 0,
            "claim_id": "audit-claim",
            "executable": str(Path(sys.executable).resolve()),
            "working_directory": str(repo),
            "decoded_argv": argv,
            "command_spec": {"path": str(spec), "sha256": sha256(spec)},
            "subject_receipt": {
                "path": str(subject),
                "sha256": sha256(subject),
                "execution_commit": commit,
                "execution_tree": tree,
            },
            "invoked_repository_files": [
                {
                    "logical_path": "Iris/validation/execution/run_required_contract_tests.py",
                    "actual_path": str(runner),
                    "execution_commit": commit,
                    "git_blob_id": runner_blob,
                    "working_sha256": sha256(runner),
                }
            ],
            "successor_policy": {"path": str(successor), "sha256": sha256(successor)},
            "output_assertion": {
                "kind": "checkout_unchanged",
                "status": "pass",
                "delta": clean_delta,
            },
        },
    )
    return receipt_root


def test_seal_requires_dynamic_checkout_unchanged_pass_and_verify_detects_drift(tmp_path: Path) -> None:
    repo, external, taxonomy, required = fixture_contracts(tmp_path)
    completed, static_inventory = inventory(repo, external)
    assert completed.returncode == 0, completed.stderr
    route_result = external / "current-route.json"
    write_json(route_result, {"status": "PASS", "summary": {"failed": 0, "errors": 0}})
    receipt_root = write_dynamic_receipt(repo, external, route_result)
    seal = external / "audit-receipt.json"
    sealed = invoke(
        "seal",
        "--repo",
        repo,
        "--static-inventory",
        static_inventory,
        "--route-result",
        route_result,
        "--command-receipt-root",
        receipt_root,
        "--out",
        seal,
        cwd=repo,
    )
    assert sealed.returncode == 0, sealed.stderr
    receipt = json.loads(seal.read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS"
    assert receipt["taxonomy_sha256"] == sha256(taxonomy)
    assert receipt["required_validations_sha256"] == sha256(required)

    verified = invoke(
        "verify",
        "--repo",
        repo,
        "--taxonomy",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations",
        "Iris/validation/execution/required_validations.json",
        "--receipt",
        seal,
        cwd=repo,
    )
    assert verified.returncode != 0
    assert "separate and disjoint" in verified.stderr

    verification = (tmp_path / "verification-checkout").resolve()
    subprocess.run(
        [
            "git",
            "-c",
            "core.longpaths=true",
            "clone",
            "-q",
            "-c",
            "core.longpaths=true",
            str(repo),
            str(verification),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    portable = invoke(
        "verify",
        "--repo",
        verification,
        "--taxonomy",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations",
        "Iris/validation/execution/required_validations.json",
        "--receipt",
        seal,
        cwd=verification,
    )
    assert portable.returncode == 0, portable.stderr

    source = verification / "Iris/build/description/v2/tests/test_selected.py"
    source.write_text(source.read_text(encoding="utf-8") + "\n# closure drift\n", encoding="utf-8")
    drifted = invoke(
        "verify",
        "--repo",
        verification,
        "--taxonomy",
        "Iris/_docs/round3/round3_test_taxonomy.json",
        "--required-validations",
        "Iris/validation/execution/required_validations.json",
        "--receipt",
        seal,
        cwd=verification,
    )
    assert drifted.returncode != 0
    assert "exact clean subject" in drifted.stderr


def test_seal_rejects_ignored_delta_and_unreadable_census(tmp_path: Path) -> None:
    repo, external, _, _ = fixture_contracts(tmp_path)
    completed, static_inventory = inventory(repo, external)
    assert completed.returncode == 0, completed.stderr
    route_result = external / "current-route.json"
    write_json(route_result, {"success": True})
    receipt_root = write_dynamic_receipt(
        repo,
        external,
        route_result,
        {"changed_count": 1, "ignored_delta_count": 1, "unreadable_count": 1},
    )
    result = invoke(
        "seal",
        "--repo",
        repo,
        "--static-inventory",
        static_inventory,
        "--route-result",
        route_result,
        "--command-receipt-root",
        receipt_root,
        "--out",
        external / "must-not-seal.json",
        cwd=repo,
    )
    assert result.returncode != 0
    assert not (external / "must-not-seal.json").exists()


def test_seal_rejects_canonical_but_tampered_static_inventory(tmp_path: Path) -> None:
    repo, external, _, _ = fixture_contracts(tmp_path)
    completed, static_inventory = inventory(repo, external)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(static_inventory.read_text(encoding="utf-8"))
    payload["selected_test_count"] = 99
    write_json(static_inventory, payload)
    route_result = external / "current-route.json"
    write_json(route_result, {"status": "PASS"})
    receipt_root = write_dynamic_receipt(repo, external, route_result)
    result = invoke(
        "seal",
        "--repo",
        repo,
        "--static-inventory",
        static_inventory,
        "--route-result",
        route_result,
        "--command-receipt-root",
        receipt_root,
        "--out",
        external / "must-not-seal-tampered.json",
        cwd=repo,
    )
    assert result.returncode != 0
    assert "exact regenerated current-route closure" in result.stderr
