from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
CODEC_ROOT = REPO / "Iris/validation/residual_refactor"
sys.path.insert(0, str(CODEC_ROOT))

from repository_evidence_codec import (  # noqa: E402
    BASELINE_NAME,
    DELTA_NAME,
    DICTIONARY_NAME,
    NODES_NAME,
    RepositoryEvidenceCodecError,
    build_v2_payloads,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    decode_v2_root,
    read_v1_stream,
)


def row(path: str, marker: str) -> dict[str, object]:
    consumer = f"consumers/{marker}.py"
    return {
        "authority_role": "historical",
        "consumer_axes": {"python_read": [consumer]},
        "consumer_scan_holds": [],
        "delete_eligible": False,
        "delete_preconditions": ["retain"],
        "direct_consumers": [consumer],
        "evidence_role": "evidence",
        "logical_artifact_id": f"artifact:{marker}",
        "path": path,
        "path_access": "readable",
        "producer": None,
        "regenerable": True,
        "restore_source": "repository",
        "route_class": "historical",
        "schema_version": "fixture-v1",
        "sha256": marker * 64,
        "size_bytes": len(marker),
        "transitive_consumers": [],
        "vcs_state": "tracked",
        "zero_live_consumers": False,
    }


class RepositoryEvidenceCodecTest(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = [row("a.json", "a"), row("b.json", "b")]
        self.final = [row("b.json", "c"), row("c.json", "d")]

    def write_bundle(self, root: Path) -> None:
        root.mkdir()
        for name, payload in build_v2_payloads(self.baseline, self.final).items():
            (root / name).write_bytes(payload)

    def mutate_object(self, root: Path, name: str, update) -> None:
        path = root / name
        value = json.loads(path.read_bytes())
        update(value)
        path.write_bytes(canonical_json_bytes(value))

    def test_round_trip_and_same_input_are_byte_stable(self) -> None:
        first = build_v2_payloads(self.baseline, self.final)
        second = build_v2_payloads(copy.deepcopy(self.baseline), copy.deepcopy(self.final))
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.write_bundle(root)
            decoded = decode_v2_root(root)
        self.assertEqual(decoded.baseline_bytes, canonical_jsonl_bytes(self.baseline))
        self.assertEqual(decoded.final_bytes, canonical_jsonl_bytes(self.final))
        self.assertEqual((decoded.shared_rows, decoded.added_rows, decoded.removed_rows, decoded.replaced_rows), (0, 1, 1, 1))

    def test_v1_rejects_duplicate_path_and_noncanonical_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.jsonl"
            path.write_bytes(canonical_jsonl_bytes([self.baseline[0], self.baseline[0]]))
            with self.assertRaises(RepositoryEvidenceCodecError):
                read_v1_stream(path)
            path.write_text(json.dumps(self.baseline[0], indent=2) + "\n", encoding="utf-8", newline="\n")
            with self.assertRaises(RepositoryEvidenceCodecError):
                read_v1_stream(path)

    def test_duplicate_delta_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.write_bundle(root)
            self.mutate_object(root, DELTA_NAME, lambda value: value["operations"].append(value["operations"][-1]))
            with self.assertRaises(RepositoryEvidenceCodecError):
                decode_v2_root(root)

    def test_wrong_delta_order_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.write_bundle(root)
            self.mutate_object(root, DELTA_NAME, lambda value: value["operations"].reverse())
            with self.assertRaises(RepositoryEvidenceCodecError):
                decode_v2_root(root)

    def test_wrong_before_hash_and_malformed_remove_are_rejected(self) -> None:
        for malformed in ("wrong_hash", "extra_node"):
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bundle"
                self.write_bundle(root)
                def update(value):
                    remove = next(operation for operation in value["operations"] if operation["op"] == "remove")
                    if malformed == "wrong_hash":
                        remove["before_sha256"] = "0" * 64
                    else:
                        remove["node"] = 0
                self.mutate_object(root, DELTA_NAME, update)
                with self.assertRaises(RepositoryEvidenceCodecError):
                    decode_v2_root(root)

    def test_unknown_node_and_dangling_node_are_rejected(self) -> None:
        for malformed in ("unknown", "dangling"):
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bundle"
                self.write_bundle(root)
                def update(value):
                    add = next(operation for operation in value["operations"] if operation["op"] == "add")
                    if malformed == "unknown":
                        add["node"] = 999999
                    else:
                        value["operations"].remove(add)
                self.mutate_object(root, DELTA_NAME, update)
                with self.assertRaises(RepositoryEvidenceCodecError):
                    decode_v2_root(root)

    def test_duplicate_edge_and_unknown_edge_reference_are_rejected(self) -> None:
        for malformed in ("duplicate", "unknown"):
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "bundle"
                self.write_bundle(root)
                if malformed == "duplicate":
                    self.mutate_object(root, DICTIONARY_NAME, lambda value: value["edges"].append(value["edges"][-1]))
                else:
                    node_path = root / NODES_NAME
                    entries = [json.loads(line) for line in node_path.read_text(encoding="utf-8").splitlines()]
                    entries[0]["body"]["edges"][0] = 999999
                    node_path.write_bytes(canonical_jsonl_bytes(entries))
                with self.assertRaises(RepositoryEvidenceCodecError):
                    decode_v2_root(root)

    def test_noncanonical_v2_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bundle"
            self.write_bundle(root)
            value = json.loads((root / BASELINE_NAME).read_bytes())
            (root / BASELINE_NAME).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
            with self.assertRaises(RepositoryEvidenceCodecError):
                decode_v2_root(root)


if __name__ == "__main__":
    unittest.main()

