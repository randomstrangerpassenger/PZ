from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_food_semantic_registry_cutover as cutover


ATTEMPT_ROOT = cutover.ATTEMPTS_ROOT / "attempt-0004"


class FoodSemanticRegistryCutoverTest(unittest.TestCase):
    def test_current_authority_is_exact_closed_successor_projection(self) -> None:
        self.assertEqual(
            cutover.sha256_file(cutover.CURRENT_FACTS),
            cutover.SUCCESSOR_FACTS_SHA256,
        )
        self.assertEqual(
            cutover.CURRENT_FACTS.read_bytes(),
            cutover.G2_SUCCESSOR_FACTS.read_bytes(),
        )
        successor = cutover.read_json(cutover.G2_SUCCESSOR_MANIFEST)
        current = cutover.read_json(cutover.CURRENT_MANIFEST)
        differences = cutover.validate_projection(
            successor,
            current,
            ATTEMPT_ROOT.name,
        )
        self.assertEqual(
            {row["path"] for row in differences},
            cutover.PROJECTION_ALLOWED_PATHS,
        )
        self.assertEqual(current["facts"]["sha256"], cutover.SUCCESSOR_FACTS_SHA256)
        self.assertEqual(
            current["food_semantic_authority"][
                "source_successor_manifest_sha256"
            ],
            cutover.SUCCESSOR_MANIFEST_SHA256,
        )

    def test_adoption_evidence_and_committed_identity_are_closed(self) -> None:
        artifact = cutover.artifact_validation(ATTEMPT_ROOT.name)
        self.assertEqual(artifact["status"], "PASS")
        self.assertEqual(artifact["current_facts_row_count"], 2105)
        self.assertEqual(artifact["food_target_member_count"], 317)
        self.assertEqual(artifact["proposition_count"], 718)
        receipt = cutover.read_json(
            ATTEMPT_ROOT / "closeout" / "registry_adoption_receipt.json"
        )
        self.assertEqual(
            receipt["food_semantic_registry_adoption"],
            "current_adoption_complete",
        )
        self.assertEqual(receipt["current_identity_ambiguity_count"], 0)
        self.assertEqual(receipt["partial_or_dual_current_count"], 0)
        self.assertEqual(
            receipt["registry_runtime_compatibility_current_source_alignment"],
            "stale_requires_successor_rtc",
        )
        identity = cutover.read_json(
            ATTEMPT_ROOT / "closeout" / "current_identity_report.json"
        )
        self.assertTrue(identity["facts"]["byte_identity"])
        self.assertTrue(identity["manifest"]["byte_identity"])
        self.assertTrue(identity["canonical_adoption_readpoint"])

    def test_exact_tracking_and_current_source_staleness_contracts(self) -> None:
        attributes = (cutover.REPO_ROOT / ".gitattributes").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"{cutover.CURRENT_FACTS_REL} -text", attributes)
        self.assertIn(f"{cutover.CURRENT_MANIFEST_REL} -text", attributes)
        ignore = (cutover.REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for token in (
            "!Iris/build/description/v2/tools/build/"
            "dvf_3_3_food_semantic_registry_cutover.py",
            "!Iris/build/description/v2/tests/"
            "test_dvf_3_3_food_semantic_registry_cutover.py",
            "!Iris/build/description/v2/staging/"
            "dvf_3_3_food_semantic_registry_operational_cutover/",
            "!Iris/build/description/v2/staging/"
            "dvf_3_3_food_semantic_registry_operational_cutover/**",
        ):
            self.assertIn(token, ignore)
        cutover.validate_contracts_and_marker()
        collision = cutover.validate_successor_rows(
            ATTEMPT_ROOT / "transaction" / "rollback_current_facts.jsonl"
        )
        self.assertTrue(collision["predecessor_source_payload_equivalence"])
        self.assertFalse(collision["successor_source_payload_equivalence"])
        self.assertEqual(collision["exact_member_count"], 2)
        self.assertEqual(collision["comparison_collision_group_count"], 1)

    def test_authorization_fixtures_fail_before_target_write(self) -> None:
        expected = {
            "verdict": "PASS",
            "cutover_attempt_id": "attempt-9999",
            "allowed_target_paths": list(cutover.ALLOWED_TARGET_PATHS),
            "current_facts_preimage_sha256": "a" * 64,
        }
        valid = {
            **expected,
            "authorization_nonce": "owner-nonce-0000000001",
            "approver_identity": "repository_owner",
            "approval_time": "2026-07-29T00:00:00+00:00",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.bin"
            target.write_bytes(b"unchanged")
            nonce_path = root / "nonce.json"
            fixtures: list[tuple[str, dict[str, object], bool]] = []
            missing = copy.deepcopy(valid)
            missing.pop("verdict")
            fixtures.append(("missing", missing, False))
            forged = copy.deepcopy(valid)
            forged["verdict"] = "FAIL"
            fixtures.append(("forged", forged, False))
            wrong_path = copy.deepcopy(valid)
            wrong_path["allowed_target_paths"] = ["wrong/path"]
            fixtures.append(("wrong_path", wrong_path, False))
            wrong_preimage = copy.deepcopy(valid)
            wrong_preimage["current_facts_preimage_sha256"] = "b" * 64
            fixtures.append(("wrong_preimage", wrong_preimage, False))
            fixtures.append(("replayed", copy.deepcopy(valid), True))
            for fixture_name, payload, replayed in fixtures:
                with self.subTest(fixture=fixture_name):
                    if replayed:
                        nonce_path.write_text("consumed", encoding="utf-8")
                    elif nonce_path.exists():
                        nonce_path.unlink()
                    before = target.read_bytes()
                    with self.assertRaises(cutover.CutoverError):
                        cutover.validate_authorization_payload(
                            payload,
                            expected,
                            nonce_path,
                        )
                    self.assertEqual(target.read_bytes(), before)

    def test_second_replace_failure_restores_both_preimages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "attempt-9998"
            facts = root / "live" / "facts.jsonl"
            manifest = root / "live" / "manifest.json"
            candidate_facts = root / "candidate" / "facts.jsonl"
            candidate_manifest = root / "candidate" / "manifest.json"
            facts.parent.mkdir(parents=True)
            candidate_facts.parent.mkdir(parents=True)
            facts.write_bytes(b"old facts\n")
            manifest.write_bytes(b'{"state":"old"}\n')
            candidate_facts.write_bytes(b"new facts\n")
            candidate_manifest.write_bytes(b'{"state":"new"}\n')
            preimages = {
                "facts": cutover.sha256_file(facts),
                "manifest": cutover.sha256_file(manifest),
            }
            candidates = {
                "facts": cutover.sha256_file(candidate_facts),
                "manifest": cutover.sha256_file(candidate_manifest),
            }
            with self.assertRaisesRegex(
                cutover.CutoverError,
                "injected_second_replace_failure",
            ):
                cutover.execute_pair_transaction(
                    root=root,
                    facts_target=facts,
                    manifest_target=manifest,
                    facts_candidate=candidate_facts,
                    manifest_candidate=candidate_manifest,
                    expected_preimages=preimages,
                    expected_candidates=candidates,
                    inject_failure="second_replace",
                )
            self.assertEqual(cutover.sha256_file(facts), preimages["facts"])
            self.assertEqual(cutover.sha256_file(manifest), preimages["manifest"])
            failure = cutover.read_json(
                root / "transaction" / "transaction_failure.json"
            )
            self.assertEqual(failure["rollback"]["status"], "PASS")
            self.assertFalse(failure["same_attempt_retry_allowed"])

    def test_lock_is_retained_until_error_release_guard_confirms_safety(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            lock_path = Path(temporary) / "transaction.lock"
            with self.assertRaisesRegex(RuntimeError, "retain"):
                with cutover.transaction_lock(
                    {"mode": "fixture", "attempt_id": "attempt-9996"},
                    error_release_guard=lambda: False,
                    lock_path=lock_path,
                ):
                    raise RuntimeError("retain")
            self.assertTrue(lock_path.is_file())
            lock_path.unlink()
            with self.assertRaisesRegex(RuntimeError, "release"):
                with cutover.transaction_lock(
                    {"mode": "fixture", "attempt_id": "attempt-9996"},
                    error_release_guard=lambda: True,
                    lock_path=lock_path,
                ):
                    raise RuntimeError("release")
            self.assertFalse(lock_path.exists())
            with self.assertRaisesRegex(RuntimeError, "guard-error"):
                with cutover.transaction_lock(
                    {"mode": "fixture", "attempt_id": "attempt-9996"},
                    error_release_guard=lambda: (_ for _ in ()).throw(
                        RuntimeError("guard")
                    ),
                    lock_path=lock_path,
                ):
                    raise RuntimeError("guard-error")
            self.assertTrue(lock_path.is_file())

    def test_startup_recovery_closes_every_journal_transition(self) -> None:
        for transition in (
            "prepared",
            "facts_replaced",
            "manifest_replaced",
            "verified",
        ):
            with self.subTest(transition=transition):
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary) / "attempt-9997"
                    facts = root / "live" / "facts.jsonl"
                    manifest = root / "live" / "manifest.json"
                    candidate_facts = root / "candidate" / "facts.jsonl"
                    candidate_manifest = root / "candidate" / "manifest.json"
                    facts.parent.mkdir(parents=True)
                    candidate_facts.parent.mkdir(parents=True)
                    facts.write_bytes(b"old facts\n")
                    manifest.write_bytes(b'{"state":"old"}\n')
                    candidate_facts.write_bytes(b"new facts\n")
                    candidate_manifest.write_bytes(b'{"state":"new"}\n')
                    preimages = {
                        "facts": cutover.sha256_file(facts),
                        "manifest": cutover.sha256_file(manifest),
                    }
                    candidates = {
                        "facts": cutover.sha256_file(candidate_facts),
                        "manifest": cutover.sha256_file(candidate_manifest),
                    }
                    cutover.create_rollback_snapshots(
                        root,
                        facts,
                        manifest,
                        preimages,
                    )
                    cutover.update_journal(
                        root,
                        state="prepared",
                        previous_state=None,
                    )
                    if transition in {
                        "facts_replaced",
                        "manifest_replaced",
                        "verified",
                    }:
                        cutover.atomic_write_bytes(
                            facts,
                            candidate_facts.read_bytes(),
                        )
                        cutover.update_journal(
                            root,
                            state="facts_replaced",
                            previous_state="prepared",
                        )
                    if transition in {"manifest_replaced", "verified"}:
                        cutover.atomic_write_bytes(
                            manifest,
                            candidate_manifest.read_bytes(),
                        )
                        cutover.update_journal(
                            root,
                            state="manifest_replaced",
                            previous_state="facts_replaced",
                        )
                    if transition == "verified":
                        cutover.update_journal(
                            root,
                            state="verified",
                            previous_state="manifest_replaced",
                        )
                    callbacks: list[str] = []
                    result = cutover.recover_pair_state(
                        root=root,
                        facts_target=facts,
                        manifest_target=manifest,
                        expected_preimages=preimages,
                        expected_candidates=candidates,
                        commit_verified_callback=lambda: callbacks.append(
                            "committed"
                        ),
                    )
                    if transition == "verified":
                        self.assertEqual(
                            result["resolution"],
                            "verified_candidates_committed",
                        )
                        self.assertEqual(callbacks, ["committed"])
                        self.assertEqual(
                            cutover.read_json(cutover.journal_path(root))["state"],
                            "committed",
                        )
                        self.assertEqual(
                            cutover.sha256_file(facts),
                            candidates["facts"],
                        )
                        self.assertEqual(
                            cutover.sha256_file(manifest),
                            candidates["manifest"],
                        )
                    else:
                        self.assertEqual(
                            result["resolution"],
                            "both_preimages_restored",
                        )
                        self.assertEqual(callbacks, [])
                        self.assertEqual(
                            cutover.sha256_file(facts),
                            preimages["facts"],
                        )
                        self.assertEqual(
                            cutover.sha256_file(manifest),
                            preimages["manifest"],
                        )


if __name__ == "__main__":
    unittest.main()
