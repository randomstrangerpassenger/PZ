from __future__ import annotations

import sys
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools" / "build"
sys.path.insert(0, str(TOOLS))

import validated_naturalization_runtime_adoption as adoption


class ValidatedNaturalizationRuntimeAdoptionTest(unittest.TestCase):
    def _candidate_probe_fixture(self, root: Path) -> tuple[dict, Path, Path, list[str]]:
        disposable_parent = root / "disposable"
        disposable_parent.mkdir()
        output_root = disposable_parent / "package"
        inputs = root / "inputs"
        inputs.mkdir()
        descriptor = inputs / "materialized_generation_descriptor.json"
        policy = inputs / "candidate_registry_compatibility_policy.json"
        disposition = inputs / "candidate_collision_disposition.json"
        binding = inputs / "candidate_contract_binding_manifest.json"
        for path, payload in (
            (descriptor, {"schema_version": "validated-naturalization-materialized-generation-v1"}),
            (policy, {"schema_version": "rtc-policy-v1"}),
            (disposition, {"schema_version": "rtc-disposition-v1"}),
            (binding, {"schema_version": "rtc-candidate-contract-binding-manifest-v1"}),
        ):
            path.write_text(json.dumps(payload), encoding="utf-8")
        package_script = root / "package_iris.ps1"
        package_script.write_text("param()\n", encoding="utf-8")
        contract_path = root / "package_candidate_probe_contract.json"
        argv = [
            "powershell", "-ExecutionPolicy", "Bypass", "-File", str(package_script),
            "-OutputRoot", str(output_root), "-RegistryCompatibilityContext", "candidate",
            "-RegistryCompatibilityProbe", "-RegistryCompatibilityRequiredGateState", "not_adopted",
            "-ValidatedNaturalizationCandidateProbeContract", str(contract_path),
        ]
        contract = {
            "schema_version": "validated-naturalization-package-candidate-probe-contract-v1",
            "authority_effect": "none",
            "subject_kind": "validated_naturalization_generation",
            "candidate_sha256": adoption.CANDIDATE_SHA256,
            "source_facts_sha256": adoption.FACTS_SHA256,
            "source_manifest_sha256": adoption.INPUT_MANIFEST_SHA256,
            "materialized_generation_descriptor_path": str(descriptor),
            "materialized_generation_descriptor_sha256": adoption.sha256(descriptor.read_bytes()),
            "registry_policy_path": str(policy),
            "registry_policy_sha256": adoption.sha256(policy.read_bytes()),
            "collision_disposition_path": str(disposition),
            "collision_disposition_sha256": adoption.sha256(disposition.read_bytes()),
            "binding_manifest_path": str(binding),
            "binding_manifest_sha256": adoption.sha256(binding.read_bytes()),
            "package_script_git_blob_sha256": adoption.sha256(package_script.read_bytes()),
            "disposable_parent_root": str(disposable_parent),
            "output_root": str(output_root),
            "allowed_argv_sha256": adoption.sha256(adoption.canonical_json(argv)),
            "zip_allowed": False,
        }
        contract["contract_binding_sha256"] = adoption.package_probe_contract_binding_sha256(contract)
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return contract, contract_path, package_script, argv

    def test_declared_anchors_are_full_lowercase_sha256(self) -> None:
        self.assertTrue(adoption.ANCHORS)
        self.assertTrue(all(adoption.SHA256_RE.fullmatch(value) for value in adoption.ANCHORS.values()))

    def test_phase0_census_is_read_only_and_anchor_exact(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        records = adoption.census(repo, adoption.PROTECTED_PATHS)
        by_path = {record["path"]: record for record in records}
        for path in adoption.ANCHORS:
            self.assertTrue(by_path[path]["git_tracked"])
            self.assertTrue(by_path[path]["declared_identity_matches"])

    def test_windows_candidate_anchor_preserves_named_identity_domain(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        record = adoption.path_record(repo, adoption.CANDIDATE_PATH, adoption.CANDIDATE_SHA256)
        self.assertEqual("working_raw_bytes", record["declared_match_domain"])
        self.assertNotEqual(record["git_blob_sha256"], record["working"]["raw_sha256"])

    def test_current_source_pair_roles_are_coherent(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        manifest = adoption.load_json_from_git(repo, adoption.INPUT_MANIFEST_PATH)
        self.assertEqual("successor_current_source_authority", manifest["authority_role"])
        self.assertEqual("current_source_authority", manifest["facts"]["role"])
        self.assertEqual(adoption.FACTS_SHA256, manifest["facts"]["sha256"])

    def test_candidate_source_vocabulary_counts_unadopted_without_state_field(self) -> None:
        payload = {
            "entries": {
                "Base.Adopted": {"source": "korean_prose_candidate_v1", "text_ko": "본문"},
                "Base.Unadopted": {"source": "unadopted", "text_ko": None},
            }
        }
        shape = adoption.public_shape(payload)
        self.assertEqual(1, shape["adopted_public"])
        self.assertEqual(1, shape["unadopted"])

    def test_facts_key_set_rejects_duplicates(self) -> None:
        with self.assertRaisesRegex(ValueError, "facts_item_id_missing_or_duplicate"):
            adoption.facts_key_set(b'{"item_id":"Base.A"}\n{"item_id":"Base.A"}\n')

    def test_candidate_working_and_git_domains_decode_to_same_payload(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        git_data = adoption.git_bytes(repo, adoption.CANDIDATE_PATH)
        working_data = adoption.working_bytes(repo, adoption.CANDIDATE_PATH)
        self.assertIsNotNone(git_data)
        self.assertIsNotNone(working_data)
        self.assertEqual(adoption.load_json_bytes(git_data), adoption.load_json_bytes(working_data))

    def test_candidate_probe_contract_accepts_fresh_contained_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            contract, contract_path, package_script, argv = self._candidate_probe_fixture(Path(temporary))
            result = adoption.validate_package_probe_contract(
                contract_path=contract_path,
                output_root=Path(contract["output_root"]),
                package_script_path=package_script,
                actual_argv=argv,
                package_script_bytes=package_script.read_bytes(),
            )
            self.assertEqual("PASS", result["status"])
            self.assertEqual("none", result["authority_effect"])

    def test_candidate_probe_contract_rejects_hash_drift_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            contract, contract_path, package_script, argv = self._candidate_probe_fixture(Path(temporary))
            Path(contract["registry_policy_path"]).write_text("drift", encoding="utf-8")
            with self.assertRaisesRegex(adoption.CandidateProbeContractError, "registry_policy_hash_mismatch"):
                adoption.validate_package_probe_contract(
                    contract_path=contract_path,
                    output_root=Path(contract["output_root"]),
                    package_script_path=package_script,
                    actual_argv=argv,
                    package_script_bytes=package_script.read_bytes(),
                )
            self.assertFalse(Path(contract["output_root"]).exists())

    def test_candidate_probe_contract_rejects_root_escape_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            contract, contract_path, package_script, argv = self._candidate_probe_fixture(Path(temporary))
            escaped = Path(temporary) / "escaped"
            contract["output_root"] = str(escaped)
            contract["contract_binding_sha256"] = adoption.package_probe_contract_binding_sha256(contract)
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            argv[argv.index("-OutputRoot") + 1] = str(escaped)
            contract["allowed_argv_sha256"] = adoption.sha256(adoption.canonical_json(argv))
            contract["contract_binding_sha256"] = adoption.package_probe_contract_binding_sha256(contract)
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(adoption.CandidateProbeContractError, "output_root_escape"):
                adoption.validate_package_probe_contract(
                    contract_path=contract_path,
                    output_root=escaped,
                    package_script_path=package_script,
                    actual_argv=argv,
                    package_script_bytes=package_script.read_bytes(),
                )
            self.assertFalse(escaped.exists())

    def test_candidate_probe_contract_rejects_zip_and_authority_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            contract, contract_path, package_script, argv = self._candidate_probe_fixture(Path(temporary))
            contract["authority_effect"] = "package_authority"
            contract["contract_binding_sha256"] = adoption.package_probe_contract_binding_sha256(contract)
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(adoption.CandidateProbeContractError, "authority_effect_forbidden"):
                adoption.validate_package_probe_contract(
                    contract_path=contract_path,
                    output_root=Path(contract["output_root"]),
                    package_script_path=package_script,
                    actual_argv=argv + ["-Zip"],
                    package_script_bytes=package_script.read_bytes(),
                )

    def test_candidate_probe_contract_rejects_argv_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            contract, contract_path, package_script, argv = self._candidate_probe_fixture(Path(temporary))
            with self.assertRaisesRegex(adoption.CandidateProbeContractError, "argv_hash_mismatch"):
                adoption.validate_package_probe_contract(
                    contract_path=contract_path,
                    output_root=Path(contract["output_root"]),
                    package_script_path=package_script,
                    actual_argv=argv + ["-Clean"],
                    package_script_bytes=package_script.read_bytes(),
                )

    def test_candidate_probe_contract_rejects_reparse_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external:
            root = Path(temporary)
            link = root / "linked-parent"
            try:
                link.symlink_to(Path(external), target_is_directory=True)
            except OSError:
                junction = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(link), str(Path(external))],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if junction.returncode != 0:
                    self.fail(f"test_requires_directory_junction_support: {junction.stderr}")
            contract, contract_path, package_script, argv = self._candidate_probe_fixture(root)
            linked_parent = link / "disposable"
            linked_parent.mkdir()
            linked_output = linked_parent / "package"
            contract["disposable_parent_root"] = str(linked_parent)
            contract["output_root"] = str(linked_output)
            argv[argv.index("-OutputRoot") + 1] = str(linked_output)
            contract["allowed_argv_sha256"] = adoption.sha256(adoption.canonical_json(argv))
            contract["contract_binding_sha256"] = adoption.package_probe_contract_binding_sha256(contract)
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(adoption.CandidateProbeContractError, "reparse_escape"):
                adoption.validate_package_probe_contract(
                    contract_path=contract_path,
                    output_root=linked_output,
                    package_script_path=package_script,
                    actual_argv=argv,
                    package_script_bytes=package_script.read_bytes(),
                )
            self.assertFalse(linked_output.exists())

    def test_package_script_rejects_missing_adoption_contract_before_output(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        package_script = repo / "Iris" / "tools" / "package_iris.ps1"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "package"
            missing = root / "missing.json"
            completed = subprocess.run(
                [
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(package_script),
                    "-OutputRoot", str(output),
                    "-RegistryCompatibilityContext", "candidate",
                    "-RegistryCompatibilityPolicy", str(root / "policy.json"),
                    "-RegistryCompatibilityDisposition", str(root / "disposition.json"),
                    "-RegistryCompatibilityBindingManifest", str(root / "binding.json"),
                    "-RegistryCompatibilityRequiredGateState", "not_adopted",
                    "-RegistryCompatibilityProbe",
                    "-ValidatedNaturalizationCandidateProbeContract", str(missing),
                ],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("candidate_probe_contract_validation_failed", completed.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
