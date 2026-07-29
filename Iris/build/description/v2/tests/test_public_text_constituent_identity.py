from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import public_text_quality_acceptance as acceptance


RELATIVE_PATH = "Iris/example/constituent.json"
HEAD_BLOB_ID = "1" * 40
NONMATCHING_FILTERED_BLOB_ID = "2" * 40


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
        variants = (
            blob_lf,
            blob_lf.replace(b"\n", b"\r\n"),
            blob_lf.replace(b"\n", b"\r"),
        )
        rows = [
            protected_snapshot_row(
                declared_sha256=sha256(blob_lf),
                head_blob_raw=blob_lf,
                working_raw=variant,
            )
            for variant in variants
        ]
        self.assertEqual(
            rows,
            [
                {
                    "path": RELATIVE_PATH,
                    "present": True,
                    "sha256": sha256(blob_lf),
                }
            ]
            * 3,
        )

    def test_protected_snapshot_declared_sha_must_match_head_raw(self) -> None:
        blob_lf = b'{"value":1}\n'
        declared_crlf = sha256(blob_lf.replace(b"\n", b"\r\n"))
        with self.assertRaises(acceptance.FoundationContractError):
            protected_snapshot_row(
                declared_sha256=declared_crlf,
                head_blob_raw=blob_lf,
                working_raw=blob_lf.replace(b"\n", b"\r\n"),
            )

    def test_protected_snapshot_non_line_ending_one_byte_change_is_stale(
        self,
    ) -> None:
        blob_lf = b'{"value":1}\n'
        with self.assertRaises(acceptance.FoundationContractError):
            protected_snapshot_row(
                declared_sha256=sha256(blob_lf),
                head_blob_raw=blob_lf,
                working_raw=b'{"value":2}\r\n',
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

    def test_protected_snapshot_returns_head_authority_raw_sha(self) -> None:
        blob_lf = b'{"value":1}\n'
        working_crlf = blob_lf.replace(b"\n", b"\r\n")
        row = protected_snapshot_row(
            declared_sha256=sha256(blob_lf),
            head_blob_raw=blob_lf,
            working_raw=working_crlf,
        )
        self.assertNotEqual(sha256(blob_lf), sha256(working_crlf))
        self.assertEqual(
            row["sha256"],
            sha256(blob_lf),
        )
        self.assertNotEqual(
            row["sha256"],
            sha256(working_crlf),
        )


if __name__ == "__main__":
    unittest.main()
