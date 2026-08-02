from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from importlib.machinery import PathFinder
from pathlib import Path
from unittest import mock

from clean_checkout_test_paths import external_test_root


REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())
ROOT = REPO / "Iris/_docs/refactor/core_refactor"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_candidates(path: Path) -> set[str]:
    data = path.read_bytes()
    candidates = {hashlib.sha256(data).hexdigest()}
    if path.suffix.lower() != ".zip":
        normalized = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        candidates.add(hashlib.sha256(normalized).hexdigest())
    return candidates


def load_round3_runner():
    runner_path = REPO / "Iris/_docs/round3/round3_run_contract_tests.py"
    spec = importlib.util.spec_from_file_location("iris_round3_contract_runner", runner_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Round 3 contract runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IrisCoreRefactorCloseoutTest(unittest.TestCase):
    def test_historical_reproduction_corpus_is_exact_and_fail_closed(self) -> None:
        runner = load_round3_runner()
        manifest_path = ROOT / "historical_reproduction_corpus.json"
        manifest = load_json(manifest_path)
        archive = REPO / manifest["archive_path"]

        with tempfile.TemporaryDirectory(
            prefix="hc-", dir=external_test_root()
        ) as temp:
            overlay_root = Path(temp)
            taxonomy = runner.load_json(runner.DEFAULT_TAXONOMY)
            report = runner.materialize_historical_reproduction_overlay(
                overlay_root, taxonomy
            )
            self.assertEqual(manifest["row_count"], report["row_count"])
            self.assertEqual(manifest["archive_sha256"], report["archive_sha256"])
            import_paths = runner.reproduction_overlay_import_paths(overlay_root)
            self.assertEqual(
                ["tests", "build", "tools", "v2"],
                [Path(path).name for path in import_paths],
            )
            spec = PathFinder.find_spec("test_browser_common_base_contract", import_paths)
            self.assertIsNotNone(spec)
            self.assertTrue(str(spec.origin).startswith(str(overlay_root.resolve())))

        self.assertEqual(manifest["archive_sha256"], hashlib.sha256(archive.read_bytes()).hexdigest())
        paths = [row["path"] for row in manifest["rows"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(
            manifest["expected_entry_paths_sha256"],
            hashlib.sha256("\n".join(paths).encode("utf-8")).hexdigest(),
        )

        def assert_rejected(mutated: dict) -> None:
            with tempfile.TemporaryDirectory(
                prefix="hn-", dir=external_test_root()
            ) as temp:
                temp_root = Path(temp)
                candidate = temp_root / "manifest.json"
                candidate.write_text(json.dumps(mutated), encoding="utf-8")
                with mock.patch.object(runner, "HISTORICAL_REPRODUCTION_MANIFEST", candidate):
                    with self.assertRaises(ValueError):
                        runner.materialize_historical_reproduction_overlay(
                            temp_root / "out", taxonomy
                        )

        traversal = copy.deepcopy(manifest)
        traversal["rows"][0]["path"] = "../escape.py"
        assert_rejected(traversal)

        duplicate = copy.deepcopy(manifest)
        duplicate["rows"][1]["path"] = duplicate["rows"][0]["path"]
        assert_rejected(duplicate)

        removed = copy.deepcopy(manifest)
        removed["rows"].pop(0)
        removed["row_count"] -= 1
        removed_paths = [row["path"] for row in removed["rows"]]
        removed["expected_entry_paths_sha256"] = hashlib.sha256(
            "\n".join(removed_paths).encode("utf-8")
        ).hexdigest()
        removed_route_paths = [
            row["path"] for row in removed["rows"] if row["entry_kind"] == "route_test"
        ]
        removed["expected_route_test_paths_sha256"] = hashlib.sha256(
            "\n".join(removed_route_paths).encode("utf-8")
        ).hexdigest()
        assert_rejected(removed)

        support_removed = copy.deepcopy(manifest)
        support_index = next(
            index
            for index, row in enumerate(support_removed["rows"])
            if row["entry_kind"] == "build_support"
        )
        support_removed["rows"].pop(support_index)
        support_removed["row_count"] -= 1
        support_removed["build_support_count"] -= 1
        support_paths = [row["path"] for row in support_removed["rows"]]
        support_removed["expected_entry_paths_sha256"] = hashlib.sha256(
            "\n".join(support_paths).encode("utf-8")
        ).hexdigest()
        assert_rejected(support_removed)

        hash_mismatch = copy.deepcopy(manifest)
        hash_mismatch["rows"][0]["sha256"] = "0" * 64
        assert_rejected(hash_mismatch)

    def test_final_manifest_is_exact_and_fail_closed(self) -> None:
        manifest = load_json(ROOT / "phase1_validation_asset_manifest.json")
        self.assertEqual(7, manifest["generation"])
        self.assertEqual(
            "73e8fcf8c0c3b025e5412df98597aa8924a6d11a1a0abf993f590503a405a920",
            manifest["previous_manifest_sha256_or_null"],
        )
        self.assertFalse(manifest["sealed"])
        self.assertEqual(0, manifest["reserved_future_count"])
        assets = manifest["assets"]
        self.assertTrue(assets)
        self.assertTrue(all(row["required"] for row in assets))
        self.assertTrue(all(row["lifecycle_state"] == "required_active" for row in assets))
        ids = sorted(row["asset_id"] for row in assets)
        self.assertEqual(manifest["expected_required_count"], len(ids))
        self.assertEqual(manifest["expected_required_asset_ids"], ids)
        identity = hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
        self.assertEqual(manifest["expected_required_asset_ids_sha256"], identity)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(assets), len({row["path"].lower() for row in assets}))

    def test_protected_surface_has_no_mutation(self) -> None:
        report = load_json(ROOT / "protected_surface_no_mutation_report.json")
        self.assertEqual("validated", report["axis_status"])
        self.assertEqual(1, report["changed_count"])
        self.assertEqual(1, report["approved_changed_count"])
        self.assertEqual(0, report["unauthorized_changed_count"])
        self.assertFalse(report["before_after_equal"])
        self.assertEqual(
            "dd732e1fb7f529da40befdd3b658571aa898031f",
            report["approval_authority"]["commit"],
        )
        self.assertEqual("pinned_ancestor_blob", report["approval_authority"]["trust_model"])
        for row in report["rows"]:
            path = REPO / row["path"]
            if row["policy"] == "read_only_pre_post" and not path.exists():
                # The existing package peer is intentionally ignored and absent
                # from a fresh committed checkout; its identity is checked by
                # the source-side disposable package validator and receipt.
                continue
            self.assertTrue(path.is_file(), row["path"])
            if row.get("approved_change"):
                self.assertNotEqual(row["before_sha256"], row["after_sha256"])
            else:
                self.assertEqual(row["before_sha256"], row["after_sha256"])
            self.assertIn(row["after_sha256"], sha256_candidates(path))

    def test_supported_api_boundary_remains_compatible(self) -> None:
        supported = load_json(ROOT / "phase0_supported_api_manifest.json")
        report = load_json(ROOT / "final_supported_api_compatibility_report.json")
        self.assertEqual("listed_surfaces_only", report["claim_boundary"])
        self.assertEqual("validated", report["axis_status"])
        declared = {row["symbol"] for row in supported["surfaces"]}
        checked = {row["symbol"] for row in report["surfaces"]}
        self.assertEqual(declared, checked)
        self.assertEqual(len(declared), report["surface_count"])
        self.assertTrue(all(row["status"] == "compatible" for row in report["surfaces"]))

        api = (REPO / "Iris/media/lua/client/Iris/IrisAPI.lua").read_text(encoding="utf-8")
        description = (REPO / "Iris/media/lua/client/Iris/API/Description.lua").read_text(encoding="utf-8")
        browser_data = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua").read_text(encoding="utf-8")
        browser = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua").read_text(encoding="utf-8")
        wiki = (REPO / "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua").read_text(encoding="utf-8")
        self.assertIn("function IrisAPI.getDescriptionBlocks", api)
        self.assertIn("function IrisAPI.getDescription", api)
        self.assertIn("function Description.getDescriptionBlocks", description)
        self.assertIn("function Description.getDescription", description)
        self.assertIn("function IrisBrowserData.getGroupVariants", browser_data)
        self.assertIn("function IrisBrowserData.build", browser_data)
        self.assertIn("function IrisBrowser.openSearch", browser)
        self.assertIn("function IrisBrowser.openForItem", browser)
        self.assertIn("function IrisWikiSections.getAllSections", wiki)

    def test_hard_authority_and_ui_reentry_guards(self) -> None:
        renderer = (REPO / "Iris/media/lua/client/Iris/Data/layer3_renderer.lua").read_text(encoding="utf-8")
        self.assertIn('safeRequire("Iris/Data/IrisLayer3DataChunks")', renderer)
        self.assertNotIn('safeRequire("Iris/Data/IrisLayer3Data")', renderer)
        for forbidden in ("dvf_3_3_facts.jsonl", "dvf_3_3_decisions.jsonl", "dvf_3_3_rendered.json"):
            self.assertNotIn(forbidden, renderer)

        model = (REPO / "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua").read_text(encoding="utf-8")
        for forbidden in ("recommendation =", "compareScore =", "qualityScore =", "priorityScore ="):
            self.assertNotIn(forbidden, model)

        detail = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua").read_text(encoding="utf-8")
        wheel = detail.split("function IrisBrowser:onDetailMouseWheel", 1)[1].split(
            "function IrisBrowser:onToggleRecipeSection", 1
        )[0]
        self.assertNotIn("showDetail", wheel)
        self.assertNotIn("rebuildDetailContent", wheel)
        self.assertIn("applyDetailScrollOffset", wheel)

        query = (REPO / "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserQuery.lua").read_text(encoding="utf-8")
        self.assertNotIn("IrisData", query)
        package_validator = (REPO / "Iris/test/validate_disposable_package.ps1").read_text(encoding="utf-8")
        self.assertIn("IrisLayer3Data.lua", package_validator)
        self.assertIn("'build', '_dev', 'staging', 'probe'", package_validator)
        asset_validator = (REPO / "Iris/test/validate_validation_assets.ps1").read_text(encoding="utf-8")
        self.assertIn("dd732e1fb7f529da40befdd3b658571aa898031f", asset_validator)
        self.assertIn("Get-PinnedProtectedApproval", asset_validator)
        self.assertNotIn("approvalReport.approved_changes", asset_validator)

    def test_validation_axes_and_ceiling_close_without_overclaim(self) -> None:
        matrix = load_json(ROOT / "final_validation_matrix.json")
        mandatory = [row for row in matrix["axes"] if row["mandatory"]]
        self.assertTrue(mandatory)
        unresolved = [row for row in mandatory if row["axis_status"] == "unvalidated_but_in_scope"]
        self.assertTrue(unresolved)
        self.assertTrue(
            all(
                row["axis_status"] in {"validated", "out_of_scope", "unvalidated_but_in_scope"}
                for row in matrix["axes"]
            )
        )
        self.assertEqual(len(unresolved), matrix["mandatory_unvalidated_axis_count"])

        ceiling = load_json(ROOT / "phase1_validation_ceiling.json")
        self.assertEqual(7, ceiling["generation"])
        self.assertEqual(
            "6f747a9fefd53447c01dd95f28f8531b27e67c61205308003f7682799b00db30",
            ceiling["previous_ceiling_sha256_or_null"],
        )
        self.assertEqual(7, ceiling["manifest_generation"])
        self.assertIsNone(ceiling["sealed_by_change"])
        self.assertFalse(ceiling["sealed"])
        self.assertEqual(len(unresolved), ceiling["mandatory_unvalidated_axis_count"])

        closeout = (ROOT / "final_closeout.md").read_text(encoding="utf-8")
        self.assertIn("Standard closeout state: `blocked`", closeout)
        self.assertIn("blocked_current_route_validation_failed", closeout)


if __name__ == "__main__":
    unittest.main()
