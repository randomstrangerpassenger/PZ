from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools" / "build"
sys.path.insert(0, str(TOOLS))

import validated_naturalization_runtime_adoption as adoption


class ValidatedNaturalizationRuntimeAdoptionTest(unittest.TestCase):
    def _adoption_fixture(self, root: Path) -> tuple[Path, Path, Path, Path, Path]:
        candidate = root / "candidate.json"
        facts = root / "facts.jsonl"
        manifest = root / "input_manifest.json"
        parent = root / "adoption-owned"
        parent.mkdir()
        output = parent / "generation"
        candidate.write_text(json.dumps({
            "meta": {"facts_sha256": "fixture"},
            "entries": {
                "Base.Adopted": {"source": "korean_prose_candidate_v1", "text_ko": "개선 문안"},
                "Base.Unadopted": {"source": "unadopted", "text_ko": None},
            },
        }), encoding="utf-8")
        facts.write_text('{"item_id":"Base.Adopted"}\n{"item_id":"Base.Unadopted"}\n', encoding="utf-8")
        manifest.write_text('{"schema_version":"fixture-v1"}\n', encoding="utf-8")
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        contract = {
            "schema_version": "validated-naturalization-adoption-generation-contract-v1",
            "authority_effect": "none",
            "bridge_context": "staging",
            "candidate_path": str(candidate.resolve()),
            "candidate_sha256": digest(candidate),
            "facts_path": str(facts.resolve()),
            "facts_sha256": digest(facts),
            "input_manifest_path": str(manifest.resolve()),
            "input_manifest_sha256": digest(manifest),
            "adoption_owned_parent_root": str(parent.resolve()),
            "output_root": str(output.resolve()),
            "expected_shape": {"total": 2, "adopted_public": 1, "unadopted": 1, "public_text": 1},
        }
        contract_path = root / "adoption_contract.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return candidate, facts, manifest, output, contract_path

    def _run_export(self, candidate: Path, output: Path, contract: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        exporter = TOOLS / "export_dvf_3_3_lua_bridge.py"
        return subprocess.run([
            sys.executable, "-B", str(exporter),
            "--rendered-path", str(candidate),
            "--bridge-context", "staging",
            "--format", "chunk",
            "--output-root", str(output),
            "--report-path", str(output / "bridge_export_report.json"),
            "--adoption-generation",
            "--adoption-generation-contract", str(contract),
            *extra,
        ], capture_output=True, text=True, check=False)

    def test_declared_anchors_are_full_lowercase_sha256(self) -> None:
        self.assertTrue(adoption.ANCHORS)
        self.assertTrue(all(adoption.SHA256_RE.fullmatch(value) for value in adoption.ANCHORS.values()))

    def test_candidate_working_and_git_domains_decode_to_same_payload(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        self.assertEqual(
            adoption.load_json_bytes(adoption.git_bytes(repo, adoption.CANDIDATE_PATH)),
            adoption.load_json_bytes(adoption.working_bytes(repo, adoption.CANDIDATE_PATH)),
        )

    def test_adoption_generation_requires_contract_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate, _, _, output, contract = self._adoption_fixture(Path(temporary))
            contract.unlink()
            result = self._run_export(candidate, output, contract)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())

    def test_adoption_generation_rejects_each_input_hash_drift(self) -> None:
        for field in ("candidate_sha256", "facts_sha256", "input_manifest_sha256"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                candidate, _, _, output, contract_path = self._adoption_fixture(Path(temporary))
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                contract[field] = "0" * 64
                contract_path.write_text(json.dumps(contract), encoding="utf-8")
                result = self._run_export(candidate, output, contract_path)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(field.removesuffix("_sha256") + "_hash_mismatch", result.stderr)
                self.assertFalse(output.exists())

    def test_adoption_generation_rejects_output_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate, _, _, output, contract_path = self._adoption_fixture(Path(temporary))
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            escaped = Path(temporary) / "escaped"
            contract["output_root"] = str(escaped.resolve())
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            result = self._run_export(candidate, escaped, contract_path)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("adoption_output_root_escape", result.stderr)
            self.assertFalse(escaped.exists())

    def test_adoption_generation_rejects_bridge_context_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate, _, _, output, contract_path = self._adoption_fixture(Path(temporary))
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["bridge_context"] = "diagnostic"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            result = self._run_export(candidate, output, contract_path)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("adoption_bridge_context_invalid", result.stderr)
            self.assertFalse(output.exists())

    def test_adoption_generation_rejects_mixed_legacy_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate, _, _, output, contract_path = self._adoption_fixture(Path(temporary))
            result = self._run_export(
                candidate, output, contract_path,
                "--registry-compatibility-context", "candidate",
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("adoption_generation_mode_mixed", result.stderr)
            self.assertFalse(output.exists())

    def test_adoption_generation_rejects_outside_report_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate, _, _, output, contract_path = self._adoption_fixture(Path(temporary))
            outside_report = Path(temporary) / "live-or-package" / "report.json"
            result = self._run_export(
                candidate, output, contract_path, "--report-path", str(outside_report)
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("adoption_report_path_invalid", result.stderr)
            self.assertFalse(output.exists())
            self.assertFalse(outside_report.exists())

    def test_candidate_manifest_binds_candidate_and_input_manifest(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        manifest_path = repo / adoption.CANDIDATE_MANIFEST_PATH
        result = adoption.validate_candidate_manifest_binding(
            manifest_path,
            expected_candidate_sha256=adoption.CANDIDATE_SHA256,
            expected_input_manifest_sha256=adoption.INPUT_MANIFEST_SHA256,
        )
        self.assertEqual("PASS", result["status"])
        with tempfile.TemporaryDirectory() as temporary:
            drifted = Path(temporary) / "candidate_manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["source_manifest_hash"] = "0" * 64
            drifted.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "candidate_manifest_input_manifest_mismatch"):
                adoption.validate_candidate_manifest_binding(
                    drifted,
                    expected_candidate_sha256=adoption.CANDIDATE_SHA256,
                    expected_input_manifest_sha256=adoption.INPUT_MANIFEST_SHA256,
                )

    def test_adoption_generation_exports_off_live_without_default_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate, _, _, output, contract_path = self._adoption_fixture(Path(temporary))
            result = self._run_export(candidate, output, contract_path)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((output / "IrisLayer3DataChunks.lua").is_file())
            self.assertTrue(any((output / "IrisLayer3DataChunks").glob("Chunk*.lua")))
            report = json.loads((output / "bridge_export_report.json").read_text(encoding="utf-8"))
            self.assertEqual("adoption_generation", report["validation_mode"])
            self.assertEqual("none", report["authority_effect"])
            self.assertNotIn("registry_compatibility", report)

    def test_materializer_uses_adoption_generation_contract(self) -> None:
        repo = Path(__file__).resolve().parents[5]
        with tempfile.TemporaryDirectory() as temporary:
            result = adoption.run_prepare_and_materialize(repo, Path(temporary) / "attempt")
            self.assertEqual("PASS", result["phase3"])
            next_generation = Path(result["next_generation"])
            report = json.loads((next_generation / "bridge_export_report.json").read_text(encoding="utf-8"))
            self.assertEqual("adoption_generation", report["validation_mode"])
            self.assertNotIn("registry_compatibility", report)
            parity = json.loads((next_generation / "full_parity_report.json").read_text(encoding="utf-8"))
            self.assertEqual("PASS", parity["status"])
            self.assertEqual(2084, parity["public_text_match_count"])
            self.assertEqual(21, parity["unadopted_without_text_count"])
            repeat = json.loads((next_generation.parent / "regeneration_identity_report.json").read_text(encoding="utf-8"))
            self.assertEqual("PASS", repeat["status"])
            self.assertTrue(repeat["byte_identical"])


if __name__ == "__main__":
    unittest.main()
