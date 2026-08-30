#!/usr/bin/env python
"""Encode and restore artifact inventories using shared rows and lifecycle deltas.

The v2 representation stores repeated strings and consumer relations once,
stores each distinct logical row once, and records the terminal state as a
small delta over the baseline.  It deliberately preserves the v1 JSONL byte
contract: decoding either view produces the original canonical stream.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Literal


DICTIONARY_NAME = "dictionary.json"
NODES_NAME = "nodes.jsonl"
BASELINE_NAME = "baseline.json"
DELTA_NAME = "final_delta.json"
MIGRATION_RECEIPT_NAME = "migration_receipt.json"

DICTIONARY_SCHEMA = "iris_repository_evidence_lifecycle_dictionary_v2"
NODES_SCHEMA = "iris_repository_evidence_lifecycle_node_v2"
BASELINE_SCHEMA = "iris_repository_evidence_lifecycle_baseline_v2"
DELTA_SCHEMA = "iris_repository_evidence_lifecycle_final_delta_v2"

CONSUMER_FIELDS = ("consumer_axes", "direct_consumers", "transitive_consumers")
OP_PRECEDENCE = {"remove": 0, "replace": 1, "add": 2}


class RepositoryEvidenceCodecError(RuntimeError):
    """Raised when an evidence stream is ambiguous or noncanonical."""


@dataclass(frozen=True)
class V1Stream:
    rows: list[dict[str, Any]]
    raw_bytes: bytes


@dataclass(frozen=True)
class DecodedBundle:
    baseline_rows: list[dict[str, Any]]
    final_rows: list[dict[str, Any]]
    baseline_bytes: bytes
    final_bytes: bytes
    shared_rows: int
    added_rows: int
    removed_rows: int
    replaced_rows: int


def canonical_value_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_value_bytes(value) + b"\n"


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) for row in rows)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_value_bytes(value)).hexdigest()


def raw_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _valid_sha256(value: object) -> bool:
    text = str(value)
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _validate_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise RepositoryEvidenceCodecError(f"noncanonical repository path: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or value != pure.as_posix() or any(part in {"", ".", ".."} for part in pure.parts):
        raise RepositoryEvidenceCodecError(f"noncanonical repository path: {value!r}")
    return value


def _validate_rows(rows: list[dict[str, Any]], role: str) -> None:
    paths: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise RepositoryEvidenceCodecError(f"{role} contains a non-object row")
        paths.append(_validate_path(row.get("path")))
        for field in CONSUMER_FIELDS:
            if field not in row:
                raise RepositoryEvidenceCodecError(f"{role} row lacks {field}: {row.get('path')}")
    if len(paths) != len(set(paths)):
        raise RepositoryEvidenceCodecError(f"{role} contains duplicate row paths")
    if paths != sorted(paths):
        raise RepositoryEvidenceCodecError(f"{role} row paths are noncanonical")


def read_v1_stream(path: Path) -> V1Stream:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or not raw.endswith(b"\n") or raw.endswith(b"\n\n") or b"\r" in raw:
        raise RepositoryEvidenceCodecError(f"v1 stream has a noncanonical newline/BOM contract: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line:
            raise RepositoryEvidenceCodecError(f"blank v1 row at {path}:{line_number}")
        try:
            value = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RepositoryEvidenceCodecError(f"invalid v1 JSON at {path}:{line_number}") from error
        if not isinstance(value, dict) or canonical_value_bytes(value) != line:
            raise RepositoryEvidenceCodecError(f"noncanonical v1 JSON at {path}:{line_number}")
        rows.append(value)
    _validate_rows(rows, "v1 stream")
    return V1Stream(rows=rows, raw_bytes=raw)


def _collect_strings(value: Any, strings: set[str]) -> None:
    if isinstance(value, str):
        strings.add(value)
    elif isinstance(value, list):
        for item in value:
            _collect_strings(item, strings)
    elif isinstance(value, dict):
        for item in value.values():
            _collect_strings(item, strings)


def _encode_value(value: Any, string_indexes: dict[str, int]) -> Any:
    if isinstance(value, str):
        return ["s", string_indexes[value]]
    if isinstance(value, list):
        return [_encode_value(item, string_indexes) for item in value]
    if isinstance(value, dict):
        return {key: _encode_value(item, string_indexes) for key, item in value.items()}
    return value


def _decode_value(value: Any, strings: list[str]) -> Any:
    if isinstance(value, list):
        if len(value) == 2 and value[0] == "s":
            index = value[1]
            if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(strings):
                raise RepositoryEvidenceCodecError("unknown string reference")
            return strings[index]
        return [_decode_value(item, strings) for item in value]
    if isinstance(value, dict):
        return {key: _decode_value(item, strings) for key, item in value.items()}
    return value


def _consumer_relations(row: dict[str, Any]) -> list[tuple[str, str]]:
    relations: list[tuple[str, str]] = []
    axes = row.get("consumer_axes")
    if not isinstance(axes, dict):
        raise RepositoryEvidenceCodecError(f"consumer_axes is not an object: {row.get('path')}")
    for axis in sorted(axes):
        consumers = axes[axis]
        if not isinstance(axis, str) or not isinstance(consumers, list) or not all(isinstance(item, str) for item in consumers):
            raise RepositoryEvidenceCodecError(f"malformed consumer axis: {row.get('path')}")
        relations.extend((f"axis:{axis}", consumer) for consumer in consumers)
    for field, relation in (("direct_consumers", "direct"), ("transitive_consumers", "transitive")):
        consumers = row.get(field)
        if not isinstance(consumers, list) or not all(isinstance(item, str) for item in consumers):
            raise RepositoryEvidenceCodecError(f"malformed {field}: {row.get('path')}")
        relations.extend((relation, consumer) for consumer in consumers)
    if len(relations) != len(set(relations)):
        raise RepositoryEvidenceCodecError(f"duplicate consumer relation: {row.get('path')}")
    return relations


def _decode_row(
    entry: dict[str, Any],
    strings: list[str],
    edges: list[tuple[str, str]],
) -> dict[str, Any]:
    body = entry.get("body")
    if not isinstance(body, dict):
        raise RepositoryEvidenceCodecError("node body is not an object")
    decoded = _decode_value(body.get("fields"), strings)
    if not isinstance(decoded, dict):
        raise RepositoryEvidenceCodecError("decoded node fields are not an object")
    path_index = body.get("path")
    edge_indexes = body.get("edges")
    if not isinstance(path_index, int) or isinstance(path_index, bool) or not 0 <= path_index < len(strings):
        raise RepositoryEvidenceCodecError("unknown node path reference")
    if not isinstance(edge_indexes, list) or any(
        not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(edges)
        for index in edge_indexes
    ):
        raise RepositoryEvidenceCodecError("unknown edge reference")
    if len(edge_indexes) != len(set(edge_indexes)):
        raise RepositoryEvidenceCodecError("duplicate edge reference in node")
    decoded["path"] = strings[path_index]
    axes: dict[str, list[str]] = {}
    direct: list[str] = []
    transitive: list[str] = []
    for index in edge_indexes:
        relation, consumer = edges[index]
        if relation.startswith("axis:"):
            axes.setdefault(relation[5:], []).append(consumer)
        elif relation == "direct":
            direct.append(consumer)
        elif relation == "transitive":
            transitive.append(consumer)
        else:
            raise RepositoryEvidenceCodecError(f"unknown consumer relation kind: {relation}")
    decoded["consumer_axes"] = axes
    decoded["direct_consumers"] = direct
    decoded["transitive_consumers"] = transitive
    return decoded


def _load_canonical_object(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or not raw.endswith(b"\n") or raw.endswith(b"\n\n") or b"\r" in raw:
        raise RepositoryEvidenceCodecError(f"noncanonical JSON bytes: {path}")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RepositoryEvidenceCodecError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise RepositoryEvidenceCodecError(f"noncanonical JSON: {path}")
    return value


def _load_canonical_nodes(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or not raw.endswith(b"\n") or raw.endswith(b"\n\n") or b"\r" in raw:
        raise RepositoryEvidenceCodecError(f"noncanonical node JSONL bytes: {path}")
    entries: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        try:
            entry = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RepositoryEvidenceCodecError(f"invalid node JSON at {path}:{line_number}") from error
        if not isinstance(entry, dict) or canonical_value_bytes(entry) != line:
            raise RepositoryEvidenceCodecError(f"noncanonical node JSON at {path}:{line_number}")
        entries.append(entry)
    return entries


def build_v2_payloads(
    baseline_rows: list[dict[str, Any]],
    final_rows: list[dict[str, Any]],
) -> dict[str, bytes]:
    _validate_rows(baseline_rows, "baseline")
    _validate_rows(final_rows, "final")
    all_rows = baseline_rows + final_rows

    strings: set[str] = set()
    relations: set[tuple[str, str]] = set()
    for row in all_rows:
        _collect_strings(row, strings)
        relations.update(_consumer_relations(row))
    for relation, consumer in relations:
        strings.add(relation)
        strings.add(consumer)

    string_entries = sorted(
        ({"id": canonical_sha256(value), "value": value} for value in strings),
        key=lambda entry: entry["id"],
    )
    if len({entry["id"] for entry in string_entries}) != len(string_entries):
        raise RepositoryEvidenceCodecError("string dictionary SHA-256 collision")
    string_indexes = {entry["value"]: index for index, entry in enumerate(string_entries)}

    edge_entries = []
    for relation, consumer in relations:
        identity = {"consumer_identity": consumer, "relation": relation}
        edge_entries.append(
            {
                "consumer": string_indexes[consumer],
                "id": canonical_sha256(identity),
                "relation": string_indexes[relation],
            }
        )
    edge_entries.sort(key=lambda entry: entry["id"])
    if len({entry["id"] for entry in edge_entries}) != len(edge_entries):
        raise RepositoryEvidenceCodecError("consumer-edge SHA-256 collision")
    edge_indexes = {
        (string_entries[entry["relation"]]["value"], string_entries[entry["consumer"]]["value"]): index
        for index, entry in enumerate(edge_entries)
    }

    node_by_id: dict[str, dict[str, Any]] = {}
    for row in all_rows:
        path = str(row["path"])
        fields = {key: value for key, value in row.items() if key not in {"path", *CONSUMER_FIELDS}}
        body = {
            "edges": [edge_indexes[pair] for pair in _consumer_relations(row)],
            "fields": _encode_value(fields, string_indexes),
            "path": string_indexes[path],
        }
        node_id = canonical_sha256(row)
        entry = {"body": body, "id": node_id, "schema_version": NODES_SCHEMA}
        prior = node_by_id.get(node_id)
        if prior is not None and prior != entry:
            raise RepositoryEvidenceCodecError("row-node SHA-256 collision")
        node_by_id[node_id] = entry

    node_entries = sorted(node_by_id.values(), key=lambda entry: entry["id"])
    node_indexes = {entry["id"]: index for index, entry in enumerate(node_entries)}
    baseline_by_path = {str(row["path"]): row for row in baseline_rows}
    final_by_path = {str(row["path"]): row for row in final_rows}

    baseline_refs = [
        [string_indexes[path], node_indexes[canonical_sha256(baseline_by_path[path])]]
        for path in sorted(baseline_by_path)
    ]
    operations: list[dict[str, Any]] = []
    for path in sorted(set(baseline_by_path) | set(final_by_path)):
        before = baseline_by_path.get(path)
        after = final_by_path.get(path)
        if before is None and after is not None:
            operations.append({"node": node_indexes[canonical_sha256(after)], "op": "add", "path": string_indexes[path]})
        elif before is not None and after is None:
            operations.append({"before_sha256": canonical_sha256(before), "op": "remove", "path": string_indexes[path]})
        elif before != after:
            assert before is not None and after is not None
            operations.append(
                {
                    "before_sha256": canonical_sha256(before),
                    "node": node_indexes[canonical_sha256(after)],
                    "op": "replace",
                    "path": string_indexes[path],
                }
            )
    operations.sort(key=lambda item: (string_entries[item["path"]]["value"], OP_PRECEDENCE[item["op"]]))

    dictionary = {
        "edges": edge_entries,
        "schema_version": DICTIONARY_SCHEMA,
        "strings": string_entries,
    }
    baseline = {"rows": baseline_refs, "schema_version": BASELINE_SCHEMA}
    delta = {"operations": operations, "schema_version": DELTA_SCHEMA}
    return {
        DICTIONARY_NAME: canonical_json_bytes(dictionary),
        NODES_NAME: canonical_jsonl_bytes(node_entries),
        BASELINE_NAME: canonical_json_bytes(baseline),
        DELTA_NAME: canonical_json_bytes(delta),
    }


def decode_v2_root(root: Path) -> DecodedBundle:
    dictionary = _load_canonical_object(root / DICTIONARY_NAME)
    baseline = _load_canonical_object(root / BASELINE_NAME)
    delta = _load_canonical_object(root / DELTA_NAME)
    node_entries = _load_canonical_nodes(root / NODES_NAME)
    if dictionary.get("schema_version") != DICTIONARY_SCHEMA:
        raise RepositoryEvidenceCodecError("dictionary schema mismatch")
    if baseline.get("schema_version") != BASELINE_SCHEMA:
        raise RepositoryEvidenceCodecError("baseline schema mismatch")
    if delta.get("schema_version") != DELTA_SCHEMA:
        raise RepositoryEvidenceCodecError("delta schema mismatch")

    string_entries = dictionary.get("strings")
    edge_entries = dictionary.get("edges")
    if not isinstance(string_entries, list) or not isinstance(edge_entries, list):
        raise RepositoryEvidenceCodecError("dictionary tables are malformed")
    if [entry.get("id") for entry in string_entries if isinstance(entry, dict)] != sorted(
        entry.get("id") for entry in string_entries if isinstance(entry, dict)
    ) or len(string_entries) != len({entry.get("id") for entry in string_entries if isinstance(entry, dict)}):
        raise RepositoryEvidenceCodecError("string table is duplicate or noncanonical")
    strings: list[str] = []
    for entry in string_entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("value"), str) or entry.get("id") != canonical_sha256(entry["value"]):
            raise RepositoryEvidenceCodecError("string dictionary identity mismatch")
        strings.append(entry["value"])

    if [entry.get("id") for entry in edge_entries if isinstance(entry, dict)] != sorted(
        entry.get("id") for entry in edge_entries if isinstance(entry, dict)
    ) or len(edge_entries) != len({entry.get("id") for entry in edge_entries if isinstance(entry, dict)}):
        raise RepositoryEvidenceCodecError("edge table is duplicate or noncanonical")
    edges: list[tuple[str, str]] = []
    seen_edges: set[tuple[str, str]] = set()
    for entry in edge_entries:
        if not isinstance(entry, dict):
            raise RepositoryEvidenceCodecError("edge table entry is not an object")
        relation_index, consumer_index = entry.get("relation"), entry.get("consumer")
        if any(
            not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(strings)
            for index in (relation_index, consumer_index)
        ):
            raise RepositoryEvidenceCodecError("edge contains an unknown string reference")
        pair = (strings[relation_index], strings[consumer_index])
        expected = canonical_sha256({"consumer_identity": pair[1], "relation": pair[0]})
        if entry.get("id") != expected or pair in seen_edges:
            raise RepositoryEvidenceCodecError("duplicate edge or edge identity mismatch")
        edges.append(pair)
        seen_edges.add(pair)

    node_ids = [entry.get("id") for entry in node_entries]
    if node_ids != sorted(node_ids) or len(node_ids) != len(set(node_ids)) or any(not _valid_sha256(value) for value in node_ids):
        raise RepositoryEvidenceCodecError("node table is duplicate or noncanonical")
    decoded_nodes: list[dict[str, Any]] = []
    used_edges: set[int] = set()
    used_strings: set[int] = set()
    for entry in node_entries:
        if entry.get("schema_version") != NODES_SCHEMA:
            raise RepositoryEvidenceCodecError("node schema mismatch")
        row = _decode_row(entry, strings, edges)
        if entry.get("id") != canonical_sha256(row):
            raise RepositoryEvidenceCodecError("node identity mismatch")
        decoded_nodes.append(row)
        body = entry["body"]
        used_edges.update(body["edges"])
        used_strings.add(body["path"])

    baseline_refs = baseline.get("rows")
    if not isinstance(baseline_refs, list):
        raise RepositoryEvidenceCodecError("baseline rows are malformed")
    state: dict[str, int] = {}
    ordered_baseline_paths: list[str] = []
    used_nodes: set[int] = set()
    for ref in baseline_refs:
        if not isinstance(ref, list) or len(ref) != 2:
            raise RepositoryEvidenceCodecError("baseline row reference is malformed")
        path_index, node_index = ref
        if any(not isinstance(index, int) or isinstance(index, bool) for index in ref):
            raise RepositoryEvidenceCodecError("baseline row reference is malformed")
        if not 0 <= path_index < len(strings) or not 0 <= node_index < len(decoded_nodes):
            raise RepositoryEvidenceCodecError("baseline contains an unknown reference")
        path = _validate_path(strings[path_index])
        if path in state or decoded_nodes[node_index].get("path") != path:
            raise RepositoryEvidenceCodecError("duplicate/mismatched baseline row reference")
        state[path] = node_index
        ordered_baseline_paths.append(path)
        used_nodes.add(node_index)
        used_strings.add(path_index)
    if ordered_baseline_paths != sorted(ordered_baseline_paths):
        raise RepositoryEvidenceCodecError("baseline row order is noncanonical")

    operations = delta.get("operations")
    if not isinstance(operations, list):
        raise RepositoryEvidenceCodecError("delta operations are malformed")
    operation_keys: list[tuple[str, int]] = []
    seen_paths: set[str] = set()
    added = removed = replaced = 0
    for operation in operations:
        if not isinstance(operation, dict):
            raise RepositoryEvidenceCodecError("delta operation is not an object")
        path_index = operation.get("path")
        op = operation.get("op")
        if not isinstance(path_index, int) or isinstance(path_index, bool) or not 0 <= path_index < len(strings) or op not in OP_PRECEDENCE:
            raise RepositoryEvidenceCodecError("delta operation has an unknown path/op")
        path = _validate_path(strings[path_index])
        key = (path, OP_PRECEDENCE[op])
        operation_keys.append(key)
        if path in seen_paths:
            raise RepositoryEvidenceCodecError("duplicate delta operation path")
        seen_paths.add(path)
        used_strings.add(path_index)
        before_index = state.get(path)
        if op in {"remove", "replace"}:
            if before_index is None or operation.get("before_sha256") != node_ids[before_index]:
                raise RepositoryEvidenceCodecError("delta before hash mismatch")
        elif "before_sha256" in operation:
            raise RepositoryEvidenceCodecError("add operation contains a before hash")
        if op == "remove":
            if set(operation) != {"before_sha256", "op", "path"}:
                raise RepositoryEvidenceCodecError("remove operation is malformed")
            del state[path]
            removed += 1
            continue
        node_index = operation.get("node")
        if not isinstance(node_index, int) or isinstance(node_index, bool) or not 0 <= node_index < len(decoded_nodes):
            raise RepositoryEvidenceCodecError("delta contains an unknown node")
        if decoded_nodes[node_index].get("path") != path:
            raise RepositoryEvidenceCodecError("delta node/path mismatch")
        if op == "add":
            if before_index is not None or set(operation) != {"node", "op", "path"}:
                raise RepositoryEvidenceCodecError("add operation is malformed")
            added += 1
        else:
            if set(operation) != {"before_sha256", "node", "op", "path"}:
                raise RepositoryEvidenceCodecError("replace operation is malformed")
            replaced += 1
        state[path] = node_index
        used_nodes.add(node_index)
    if operation_keys != sorted(operation_keys):
        raise RepositoryEvidenceCodecError("delta operation order is noncanonical")
    if used_nodes != set(range(len(decoded_nodes))):
        raise RepositoryEvidenceCodecError("dangling node in node table")
    if used_edges != set(range(len(edges))):
        raise RepositoryEvidenceCodecError("dangling edge in edge table")

    baseline_rows = [decoded_nodes[baseline_node] for baseline_node in (ref[1] for ref in baseline_refs)]
    final_rows = [decoded_nodes[state[path]] for path in sorted(state)]
    _validate_rows(baseline_rows, "decoded baseline")
    _validate_rows(final_rows, "decoded final")
    baseline_bytes = canonical_jsonl_bytes(baseline_rows)
    final_bytes = canonical_jsonl_bytes(final_rows)
    baseline_map = {str(row["path"]): row for row in baseline_rows}
    final_map = {str(row["path"]): row for row in final_rows}
    shared = sum(baseline_map[path] == final_map[path] for path in baseline_map.keys() & final_map.keys())
    return DecodedBundle(
        baseline_rows=baseline_rows,
        final_rows=final_rows,
        baseline_bytes=baseline_bytes,
        final_bytes=final_bytes,
        shared_rows=shared,
        added_rows=added,
        removed_rows=removed,
        replaced_rows=replaced,
    )


def materialize_manifest(
    source: Path,
    view: Literal["baseline", "final"],
) -> tuple[bytes, list[dict[str, Any]], Literal["v1", "v2"]]:
    if source.is_file():
        stream = read_v1_stream(source)
        return stream.raw_bytes, stream.rows, "v1"
    if source.is_dir():
        bundle = decode_v2_root(source)
        if view == "baseline":
            return bundle.baseline_bytes, bundle.baseline_rows, "v2"
        return bundle.final_bytes, bundle.final_rows, "v2"
    raise RepositoryEvidenceCodecError(f"manifest source does not exist: {source}")
