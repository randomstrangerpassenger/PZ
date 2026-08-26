from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


V2_ROOT = Path(__file__).resolve().parents[1]

from iris_tooling.build import public_text_quality_acceptance as acceptance
from iris_tooling.domains.public_text import acceptance_attempt_context


RELATIVE_PATH = "Iris/example/constituent.json"
HEAD_BLOB_ID = "1" * 40
NONMATCHING_FILTERED_BLOB_ID = "2" * 40
NATURALIZATION_ATTEMPT_ROOT = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
    "attempt-0023-compiler-identity-v2-a"
)
PHASE0_ATTEMPT_REQUIRED_PATHS = frozenset(
    {
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase2/body_plan_requirement_inventory.jsonl",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase2/source_proposition_manifest.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase4/candidate_manifest.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase4/candidate_rendered.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase4/protected_surface_after_snapshot.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase5/semantic_preservation_report.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase5/structural_satisfaction_ledger.jsonl",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase6/raw_detector_report.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase7/human_review_sample_manifest.json",
        f"{NATURALIZATION_ATTEMPT_ROOT}/phase8/publish_acceptance_handoff_manifest.json",
    }
)
G5_ATTEMPT_ROOT = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/"
    "attempt-0024-publish-remediation-a"
)
G5_REQUIRED_PATHS = frozenset(
    {
        f"{G5_ATTEMPT_ROOT}/phase2/body_plan_requirement_inventory.jsonl",
        f"{G5_ATTEMPT_ROOT}/phase2/source_proposition_manifest.json",
        f"{G5_ATTEMPT_ROOT}/phase4/candidate_manifest.json",
        f"{G5_ATTEMPT_ROOT}/phase4/candidate_proposition_trace.jsonl",
        f"{G5_ATTEMPT_ROOT}/phase4/candidate_rendered.json",
        f"{G5_ATTEMPT_ROOT}/phase4/protected_surface_after_snapshot.json",
        f"{G5_ATTEMPT_ROOT}/phase5/semantic_preservation_report.json",
        f"{G5_ATTEMPT_ROOT}/phase5/structural_satisfaction_ledger.jsonl",
        f"{G5_ATTEMPT_ROOT}/phase6/raw_detector_report.json",
        f"{G5_ATTEMPT_ROOT}/phase7/human_review_sample_manifest.json",
        f"{G5_ATTEMPT_ROOT}/phase8/phase8_closeout.json",
        f"{G5_ATTEMPT_ROOT}/phase8/publish_acceptance_handoff_manifest.json",
    }
)
PHASE0_IMPLEMENTATION_REQUIRED_PATHS = frozenset(
    {
        "Iris/tooling/src/iris_tooling/build/"
        "run_dvf_3_3_korean_prose_naturalization.py",
        "Iris/tooling/src/iris_tooling/build/"
        "validate_dvf_3_3_korean_prose_naturalization.py",
    }
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(
    *,
    declared_sha256: str,
    head_blob_raw: bytes,
    working_raw: bytes,
) -> dict[str, object]:
    return acceptance.build_text_constituent_identity_from_bytes(
        repo_relative_posix_path=RELATIVE_PATH,
        declared_sha256=declared_sha256,
        head_blob_id=HEAD_BLOB_ID,
        head_blob_raw=head_blob_raw,
        working_raw=working_raw,
        filtered_working_blob_id=NONMATCHING_FILTERED_BLOB_ID,
    )


def protected_identity(
    *,
    declared_sha256: str,
    head_blob_raw: bytes,
    working_raw: bytes,
    text_attribute: str = "unspecified",
) -> dict[str, object]:
    return acceptance.build_protected_snapshot_identity_from_bytes(
        repo_relative_posix_path=RELATIVE_PATH,
        declared_sha256=declared_sha256,
        head_blob_id=HEAD_BLOB_ID,
        head_blob_raw=head_blob_raw,
        working_raw=working_raw,
        filtered_working_blob_id=NONMATCHING_FILTERED_BLOB_ID,
        text_attribute=text_attribute,
    )


def protected_snapshot_row(
    *,
    declared_sha256: str,
    head_blob_raw: bytes,
    working_raw: bytes,
    text_attribute: str = "unspecified",
) -> dict[str, object]:
    return acceptance.build_protected_snapshot_present_row_from_bytes(
        repo_relative_posix_path=RELATIVE_PATH,
        declared_sha256=declared_sha256,
        head_blob_id=HEAD_BLOB_ID,
        head_blob_raw=head_blob_raw,
        working_raw=working_raw,
        filtered_working_blob_id=NONMATCHING_FILTERED_BLOB_ID,
        text_attribute=text_attribute,
    )


class PublicTextConstituentIdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.review_sample = acceptance.load_json_strict(
            acceptance.REPO_ROOT
            / "Iris"
            / "validation"
            / "clean_checkout"
            / "evidence"
            / "current_required_v1"
            / "objects"
            / "99e02cfb47193f3f352c55884a145fb515b92b2f033235f017b13977e06b33f9"
        )
        cls.review_decision = acceptance.load_json_strict(
            acceptance.REPO_ROOT
            / "Iris"
            / "_docs"
            / "round3"
            / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
            / "attempt_0024_human_review_decision.json"
        )

    def test_current_exact_full_review_has_zero_human_review_numerator(
        self,
    ) -> None:
        self.assertEqual(
            acceptance.human_review_blocker_count(
                review_sample=self.review_sample,
                review_decision=self.review_decision,
                required_denominator=2084,
            ),
            0,
        )

    def test_exact_full_review_invalid_variants_are_technical_blockers(
        self,
    ) -> None:
        for case_id in (
            "aggregate_failure",
            "denominator_mismatch",
            "digest_mismatch",
            "blocker_list_mismatch",
            "incomplete_aggregate",
            "unknown_review_schema",
        ):
            with self.subTest(case_id=case_id):
                changed = deepcopy(self.review_decision)
                if case_id == "aggregate_failure":
                    changed["rubric_aggregate"]["readability"] = {
                        "pass": 2083,
                        "fail": 1,
                    }
                elif case_id == "denominator_mismatch":
                    changed["reviewed_denominator"] = 2083
                elif case_id == "digest_mismatch":
                    changed["selected_ordered_digest"] = "0" * 64
                elif case_id == "blocker_list_mismatch":
                    changed["blocker_item_ids"] = ["Base.Axe"]
                elif case_id == "incomplete_aggregate":
                    del changed["rubric_aggregate"]["public_suitability"]
                else:
                    changed["decision_mode"] = "unknown_future_review_schema"
                with self.assertRaisesRegex(
                    acceptance.FoundationContractError,
                    "human review schema technical blocker",
                ):
                    acceptance.human_review_blocker_count(
                        review_sample=self.review_sample,
                        review_decision=changed,
                        required_denominator=2084,
                    )

    def test_sampled_uniform_review_contract_is_preserved(self) -> None:
        sample = {"selected_ordered_digest": "a" * 64}
        decision = {
            "decision_mode": "exact_sample_uniform_owner_approval",
            "status": "approved",
            "selected_ordered_digest": "a" * 64,
            "uniform_review": {
                "readability": "pass",
                "naturalness": "pass",
                "semantic_fidelity": "pass",
                "public_suitability": "pass",
            },
        }
        self.assertEqual(
            acceptance.human_review_blocker_count(
                review_sample=sample,
                review_decision=decision,
                required_denominator=2,
            ),
            0,
        )
        decision["uniform_review"]["naturalness"] = "fail"
        self.assertEqual(
            acceptance.human_review_blocker_count(
                review_sample=sample,
                review_decision=decision,
                required_denominator=2,
            ),
            2,
        )

    def test_lf_crlf_and_lone_cr_are_equivalent(self) -> None:
        blob_lf = b'{\n  "value": 1\n}\n'
        declared_crlf = sha256(blob_lf.replace(b"\n", b"\r\n"))
        variants = (
            blob_lf,
            blob_lf.replace(b"\n", b"\r\n"),
            blob_lf.replace(b"\n", b"\r"),
        )
        rows = [
            identity(
                declared_sha256=declared_crlf,
                head_blob_raw=blob_lf,
                working_raw=variant,
            )
            for variant in variants
        ]
        self.assertTrue(all(row["match"] for row in rows))
        self.assertEqual(
            {row["authority_git_blob_raw_sha256"] for row in rows},
            {sha256(blob_lf)},
        )
        self.assertEqual(
            {row["working_lf_canonical_sha256"] for row in rows},
            {sha256(blob_lf)},
        )
        self.assertTrue(
            all(
                row["json_semantic_normalization_applied"] is False
                for row in rows
            )
        )

    def test_non_line_ending_one_byte_change_is_stale(self) -> None:
        blob_lf = b'{"value":1}\n'
        changed = b'{"value":2}\r\n'
        row = identity(
            declared_sha256=sha256(blob_lf),
            head_blob_raw=blob_lf,
            working_raw=changed,
        )
        self.assertFalse(row["canonical_working_identity"])
        self.assertFalse(row["working_matches_head_authority"])
        self.assertFalse(row["match"])

    def test_checkout_location_does_not_change_identity(self) -> None:
        blob_lf = b'{"value":1}\n'
        declared_lone_cr = sha256(blob_lf.replace(b"\n", b"\r"))
        with tempfile.TemporaryDirectory() as first_root:
            with tempfile.TemporaryDirectory() as second_root:
                first = Path(first_root).joinpath(*Path(RELATIVE_PATH).parts)
                second = Path(second_root).joinpath(*Path(RELATIVE_PATH).parts)
                first.parent.mkdir(parents=True)
                second.parent.mkdir(parents=True)
                first.write_bytes(blob_lf)
                second.write_bytes(blob_lf.replace(b"\n", b"\r\n"))
                first_identity = identity(
                    declared_sha256=declared_lone_cr,
                    head_blob_raw=blob_lf,
                    working_raw=first.read_bytes(),
                )
                second_identity = identity(
                    declared_sha256=declared_lone_cr,
                    head_blob_raw=blob_lf,
                    working_raw=second.read_bytes(),
                )
        self.assertEqual(first_identity, second_identity)
        self.assertNotIn(first_root, str(first_identity))
        self.assertNotIn(second_root, str(second_identity))
        self.assertFalse(
            first_identity["absolute_path_or_host_metadata_in_identity"]
        )

    def test_protected_snapshot_lf_crlf_and_lone_cr_are_equivalent(self) -> None:
        blob_lf = b'{\n  "value": 1\n}\n'
        variants = {
            "lf": blob_lf,
            "crlf": blob_lf.replace(b"\n", b"\r\n"),
            "lone_cr": blob_lf.replace(b"\n", b"\r"),
        }
        for case_id, working_raw in variants.items():
            with self.subTest(case_id=case_id):
                row = protected_snapshot_row(
                    declared_sha256=sha256(blob_lf),
                    head_blob_raw=blob_lf,
                    working_raw=working_raw,
                )
                self.assertEqual(
                    row,
                    {
                        "path": RELATIVE_PATH,
                        "present": True,
                        "sha256": sha256(blob_lf),
                    },
                )
                if case_id == "crlf":
                    self.assertNotEqual(sha256(blob_lf), sha256(working_raw))
                    self.assertNotEqual(row["sha256"], sha256(working_raw))

    def test_protected_snapshot_invalid_text_identities_are_stale(self) -> None:
        blob_lf = b'{"value":1}\n'
        cases = {
            "declared_sha_mismatch": (
                sha256(blob_lf.replace(b"\n", b"\r\n")),
                blob_lf.replace(b"\n", b"\r\n"),
            ),
            "semantic_byte_change": (sha256(blob_lf), b'{"value":2}\r\n'),
        }
        for case_id, (declared_sha256, working_raw) in cases.items():
            with self.subTest(case_id=case_id), self.assertRaises(
                acceptance.FoundationContractError
            ):
                protected_snapshot_row(
                    declared_sha256=declared_sha256,
                    head_blob_raw=blob_lf,
                    working_raw=working_raw,
                )

    def test_protected_snapshot_binary_raw_drift_is_stale(self) -> None:
        blob = b"\x00\x01\r\n\xff"
        row = protected_identity(
            declared_sha256=sha256(blob),
            head_blob_raw=blob,
            working_raw=b"\x00\x01\n\xff",
        )
        self.assertEqual(row["identity_kind"], "raw_bytes")
        self.assertFalse(row["raw_working_identity"])
        self.assertFalse(row["working_matches_head_authority"])
        self.assertFalse(row["match"])
        with self.assertRaises(acceptance.FoundationContractError):
            protected_snapshot_row(
                declared_sha256=sha256(blob),
                head_blob_raw=blob,
                working_raw=b"\x00\x01\n\xff",
            )

    def test_phase0_no_write_and_real_required_path_sets_are_identical(
        self,
    ) -> None:
        handoff = acceptance.REPO_ROOT / (
            f"{NATURALIZATION_ATTEMPT_ROOT}/phase8/"
            "publish_acceptance_handoff_manifest.json"
        )
        validation = {
            "constituents": {
                "candidate": {
                    "path": (
                        f"{NATURALIZATION_ATTEMPT_ROOT}/phase4/"
                        "candidate_rendered.json"
                    )
                }
            }
        }

        def passing_preflight(paths):
            rows = [
                {
                    "path": acceptance.repo_relative(path),
                    "present": True,
                    "tracked": True,
                    "ignored": False,
                    "unstaged_delta": False,
                    "head_git_blob_id": HEAD_BLOB_ID,
                    "filtered_working_blob_id": HEAD_BLOB_ID,
                    "head_working_identity": True,
                }
                for path in paths
            ]
            return {
                "schema_version": (
                    "public_text_quality_vcs_required_surface_preflight_v1"
                ),
                "status": "PASS",
                "required_path_count": len(rows),
                "present_count": len(rows),
                "tracked_count": len(rows),
                "ignored_count": 0,
                "unstaged_delta_count": 0,
                "head_working_identity_count": len(rows),
                "blocker_paths": [],
                "rows": rows,
            }

        with patch.object(
            acceptance_attempt_context,
            "vcs_preflight",
            side_effect=passing_preflight,
        ):
            no_write = acceptance.phase0_required_vcs_preflight(
                subject_handoff=handoff,
                consumer="phase0-no-write-preflight",
                handoff_validation=validation,
            )
            real = acceptance.phase0_required_vcs_preflight(
                subject_handoff=handoff,
                consumer="phase0-binding",
                handoff_validation=validation,
            )
        self.assertEqual(
            no_write["required_path_set"],
            real["required_path_set"],
        )
        self.assertEqual(
            no_write["required_path_set_sha256"],
            real["required_path_set_sha256"],
        )
        self.assertEqual(
            no_write["vcs_preflight"]["required_path_count"],
            real["vcs_preflight"]["required_path_count"],
        )

    def test_phase0_before_and_after_exact_unignore_have_parity(self) -> None:
        handoff = acceptance.REPO_ROOT / (
            f"{NATURALIZATION_ATTEMPT_ROOT}/phase8/"
            "publish_acceptance_handoff_manifest.json"
        )
        blocker = (
            f"{NATURALIZATION_ATTEMPT_ROOT}/phase4/"
            "candidate_rendered.json"
        )
        validation = {
            "constituents": {"candidate": {"path": blocker}}
        }
        ignored_paths = {blocker}

        def stateful_preflight(paths):
            rows = []
            for path in paths:
                relative = acceptance.repo_relative(path)
                ignored = relative in ignored_paths
                rows.append(
                    {
                        "path": relative,
                        "present": True,
                        "tracked": True,
                        "ignored": ignored,
                        "unstaged_delta": False,
                        "head_git_blob_id": HEAD_BLOB_ID,
                        "filtered_working_blob_id": HEAD_BLOB_ID,
                        "head_working_identity": True,
                    }
                )
            blockers = [
                row["path"] for row in rows if row["ignored"]
            ]
            return {
                "schema_version": (
                    "public_text_quality_vcs_required_surface_preflight_v1"
                ),
                "status": "FAIL" if blockers else "PASS",
                "required_path_count": len(rows),
                "present_count": len(rows),
                "tracked_count": len(rows),
                "ignored_count": len(blockers),
                "unstaged_delta_count": 0,
                "head_working_identity_count": len(rows),
                "blocker_paths": blockers,
                "rows": rows,
            }

        with patch.object(
            acceptance_attempt_context,
            "vcs_preflight",
            side_effect=stateful_preflight,
        ):
            before = [
                acceptance.phase0_required_vcs_preflight(
                    subject_handoff=handoff,
                    consumer=consumer,
                    handoff_validation=validation,
                )
                for consumer in sorted(
                    acceptance.PHASE0_REQUIRED_VCS_CONSUMERS
                )
            ]
            ignored_paths.clear()
            after = [
                acceptance.phase0_required_vcs_preflight(
                    subject_handoff=handoff,
                    consumer=consumer,
                    handoff_validation=validation,
                )
                for consumer in sorted(
                    acceptance.PHASE0_REQUIRED_VCS_CONSUMERS
                )
            ]
        self.assertEqual(
            [row["vcs_preflight"]["status"] for row in before],
            ["FAIL", "FAIL"],
        )
        self.assertEqual(
            [row["vcs_preflight"]["blocker_paths"] for row in before],
            [[blocker], [blocker]],
        )
        self.assertEqual(
            [row["vcs_preflight"]["status"] for row in after],
            ["PASS", "PASS"],
        )

    def test_phase0_exact_unignore_contract_has_no_broad_unignore(
        self,
    ) -> None:
        lines = (
            acceptance.REPO_ROOT / ".gitignore"
        ).read_text(encoding="utf-8").splitlines()
        start = lines.index(
            "# Publish Boundary attempt-0004-official: "
            "exact synchronized Naturalization inputs."
        )
        g5_start = lines.index(
            "# G5 clean-checkout and future G4: "
            "exact attempt-0024 required inputs."
        )
        end = lines.index(
            "# Publish Boundary attempt-0004-official: "
            "owner input and implementation."
        )
        block = lines[start:g5_start]
        g5_block = lines[g5_start:end]
        exact_files = {
            line[1:]
            for line in block
            if line.startswith("!") and not line.endswith("/")
        }
        g5_exact_files = {
            line[1:]
            for line in g5_block
            if line.startswith("!") and not line.endswith("/")
        }
        self.assertEqual(exact_files, PHASE0_ATTEMPT_REQUIRED_PATHS)
        self.assertEqual(g5_exact_files, G5_REQUIRED_PATHS)
        self.assertFalse(
            any(line.startswith("!") and "*" in line for line in block)
        )
        self.assertFalse(
            any(line.startswith("!") and "*" in line for line in g5_block)
        )
        self.assertFalse(any("attempt-0022" in line for line in block))
        for relative in (
            PHASE0_ATTEMPT_REQUIRED_PATHS
            | PHASE0_IMPLEMENTATION_REQUIRED_PATHS
            | G5_REQUIRED_PATHS
        ):
            self.assertEqual(lines.count(f"!{relative}"), 1)
            self.assertFalse(
                acceptance.is_ignored(acceptance.REPO_ROOT / relative)
            )

    def test_phase0_tracked_but_ignored_required_input_fails(self) -> None:
        required = acceptance.REPO_ROOT / next(
            iter(PHASE0_IMPLEMENTATION_REQUIRED_PATHS)
        )
        self.assertTrue(acceptance.is_tracked(required))
        with patch.object(
            acceptance_attempt_context,
            "is_ignored",
            return_value=True,
        ):
            report = acceptance_attempt_context.vcs_preflight([required])
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["tracked_count"], 1)
        self.assertEqual(report["ignored_count"], 1)
        self.assertEqual(
            report["blocker_paths"],
            [acceptance.repo_relative(required)],
        )


if __name__ == "__main__":
    unittest.main()
