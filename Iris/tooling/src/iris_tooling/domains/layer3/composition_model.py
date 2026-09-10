"""Stable, locale-neutral contract for Layer 3 semantic composition."""
from __future__ import annotations

from collections import Counter
import hashlib
import json


SCHEMA = "iris-layer3-composition-v1"
CONTRACT_VERSION = 1
QUALIFIER_KINDS = frozenset({"condition", "constraint"})
BLOCK_CLASSES = frozenset({"semantic", "acquisition"})
QUALIFIER_SCOPES = frozenset({"block_common", "branch_local", "scope_unresolved"})


class CompositionError(ValueError):
    """The composition handoff violates its consumer contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CompositionError(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def stable_id(prefix: str, value: object) -> str:
    return f"{prefix}:{hashlib.sha256(canonical(value)).hexdigest()}"


def branch_identity(item_id: str, block_class: str, fact_refs: list[str]) -> str:
    return stable_id("branch", {"item_id": item_id, "class": block_class,
                                "fact_refs": sorted(fact_refs)})


def block_identity(item_id: str, block_class: str, fact_refs: list[str]) -> str:
    return stable_id("block", {"item_id": item_id, "class": block_class,
                               "fact_refs": sorted(fact_refs)})


def relation_identity(item_id: str, relation: dict) -> str:
    body = {key: relation[key] for key in sorted(relation) if key != "relation_id"}
    return stable_id("relation", {"item_id": item_id, **body})


def qualifier_identity(item_id: str, fact_refs: list[str]) -> str:
    return stable_id("qualifier", {"item_id": item_id, "fact_refs": sorted(fact_refs)})


def _validate_fact_node(node: dict, item_id: str) -> str:
    ref = node.get("fact_ref")
    require(isinstance(ref, str) and ref.startswith("fact:"), "invalid fact reference")
    require(node.get("item_id") == item_id and node.get("fact_kind")
            and isinstance(node.get("payload"), dict), "incomplete fact meaning")
    provenance = node.get("provenance_refs")
    require(isinstance(provenance, list) and provenance == sorted(set(provenance)) and provenance,
            "invalid fact provenance")
    require(isinstance(node.get("admission_rule_ref"), str), "missing admission rule")
    return ref


def validate_result(result: dict) -> dict:
    """Fail closed on the structure Problem 2 is allowed to consume."""
    require(result.get("schema") == SCHEMA and result.get("contract_version") == CONTRACT_VERSION,
            "unknown composition schema")
    source = result.get("source", {})
    adoption = source.get("adoption", {})
    require(adoption.get("path", "").endswith("/adoption.json")
            and isinstance(adoption.get("sha256"), str), "missing adopted input identity")
    expected_counts = source.get("fact_counts", {})
    require(set(expected_counts) == {"semantic", "acquisition"}
            and all(isinstance(value, int) and value >= 0 for value in expected_counts.values()),
            "invalid input fact counts")

    items = result.get("items")
    require(isinstance(items, list), "missing composition items")
    require([row.get("item_id") for row in items] == sorted({row.get("item_id") for row in items}),
            "duplicate or unsorted item")
    seen_facts: dict[str, str] = {}
    seen_blocks: set[str] = set()
    relation_counts = Counter()
    qualifier_counts = Counter()
    for item in items:
        item_id = item["item_id"]
        blocks = item.get("blocks")
        require(isinstance(blocks, list), "invalid composition block collection")
        require([block.get("block_id") for block in blocks]
                == sorted(block.get("block_id") for block in blocks), "unsorted blocks")
        item_anchor_refs: set[str] = set()
        item_block_refs: set[str] = set()
        branch_to_block: dict[str, str] = {}
        block_branches: dict[str, set[str]] = {}
        for block in blocks:
            block_class = block.get("class")
            require(block_class in BLOCK_CLASSES, "unknown block class")
            branches = block.get("branches")
            require(isinstance(branches, list) and branches, "block has no branch")
            require([branch.get("branch_id") for branch in branches]
                    == sorted(branch.get("branch_id") for branch in branches), "unsorted branches")
            block_fact_refs: set[str] = set()
            branch_refs: set[str] = set()
            for branch in branches:
                nodes = branch.get("facts")
                require(isinstance(nodes, list) and nodes, "branch has no facts")
                refs = [_validate_fact_node(node, item_id) for node in nodes]
                require(refs == sorted(set(refs)), "duplicate or unsorted branch fact")
                require(branch.get("branch_id") == branch_identity(item_id, block_class, refs),
                        "branch identity drift")
                branch_refs.add(branch["branch_id"])
                branch_to_block[branch["branch_id"]] = block.get("block_id")
                block_fact_refs.update(refs)
            require(block.get("block_id") == block_identity(item_id, block_class,
                                                              sorted(block_fact_refs)),
                    "block identity drift")
            require(block["block_id"] not in seen_blocks, "duplicate block identity")
            seen_blocks.add(block["block_id"])
            item_block_refs.add(block["block_id"])
            block_branches[block["block_id"]] = branch_refs
            for ref in block_fact_refs:
                require(ref not in seen_facts, "fact has more than one disposition")
                seen_facts[ref] = block["block_id"]
            item_anchor_refs.update(block_fact_refs)
            for relation in block.get("relations", []):
                require(relation.get("relation_id") == relation_identity(item_id, relation),
                        "relation identity drift")
                require(set(relation.get("branch_refs", [])) <= branch_refs, "dangling branch relation")
                require(set(relation.get("fact_refs", [])) <= block_fact_refs, "dangling fact relation")
                require(relation.get("basis"), "relation lacks basis")
                direction = relation.get("direction")
                if direction:
                    require(set(direction.values()) <= branch_refs | block_fact_refs,
                            "relation direction escapes block")
                relation_counts[relation.get("kind")] += 1

        qualifiers = item.get("qualifiers", [])
        require(isinstance(qualifiers, list)
                and [row.get("qualifier_id") for row in qualifiers]
                == sorted(row.get("qualifier_id") for row in qualifiers), "unsorted qualifiers")
        for qualifier in qualifiers:
            refs = qualifier.get("fact_refs")
            applies = qualifier.get("applies_to_fact_refs")
            branches = qualifier.get("branch_refs")
            qualifier_blocks = qualifier.get("block_refs")
            require(qualifier.get("qualifier_id") == qualifier_identity(item_id, refs or []),
                    "qualifier identity drift")
            require(qualifier.get("fact_kind") in QUALIFIER_KINDS
                    and isinstance(qualifier.get("payload"), dict), "invalid qualifier")
            require(isinstance(refs, list) and refs == sorted(set(refs)) and refs,
                    "invalid qualifier fact refs")
            require(isinstance(applies, list) and applies == sorted(set(applies)) and applies
                    and set(applies) <= item_anchor_refs, "invalid qualifier application")
            require(isinstance(branches, list) and branches == sorted(set(branches)) and branches
                    and set(branches) <= branch_to_block.keys(), "invalid qualifier branch scope")
            require(isinstance(qualifier_blocks, list)
                    and qualifier_blocks == sorted({branch_to_block[ref] for ref in branches}),
                    "invalid qualifier block scope")
            expected_scope = ("block_common" if len(qualifier_blocks) == 1
                              and set(branches) == block_branches[qualifier_blocks[0]]
                              else "branch_local")
            require(qualifier.get("scope") == expected_scope, "qualifier scope drift")
            provenance = qualifier.get("provenance_refs")
            require(isinstance(provenance, list) and provenance == sorted(set(provenance))
                    and provenance, "invalid qualifier provenance")
            require(qualifier.get("basis"), "qualifier lacks basis")
            for ref in refs:
                require(ref not in seen_facts, "fact has more than one disposition")
                seen_facts[ref] = qualifier["qualifier_id"]
            qualifier_counts[qualifier["scope"]] += 1
            if len(refs) > 1:
                relation_counts["equivalent"] += 1

        require(item.get("separate_block_refs") == sorted(item_block_refs),
                "separate block inventory drift")
        for relation in item.get("unresolved_relations", []):
            require(relation.get("relation_id") == relation_identity(item_id, relation),
                    "unresolved relation identity drift")
            refs = relation.get("block_refs", [])
            require(len(refs) == 2 and refs == sorted(set(refs)) and set(refs) <= item_block_refs,
                    "invalid unresolved block relation")
            require(set(relation.get("fact_refs", [])) <= item_anchor_refs,
                    "dangling unresolved fact relation")
            require(relation.get("kind") == "undetermined" and relation.get("reason")
                    and relation.get("consumer_effect"), "unexplained unresolved relation")
            relation_counts["undetermined"] += 1

    summary = result.get("summary", {})
    require(summary.get("targets") == len(items), "target count drift")
    require(summary.get("blocks") == len(seen_blocks), "block count drift")
    require(summary.get("input_facts") == sum(expected_counts.values()) == len(seen_facts),
            "input fact conservation failure")
    require(summary.get("dispositions") == {"represented": len(seen_facts), "residual": 0,
                                             "non_public": 0}, "fact disposition drift")
    require(summary.get("relation_kinds") == dict(sorted(relation_counts.items())),
            "relation summary drift")
    require(summary.get("qualifier_scopes") == dict(sorted(qualifier_counts.items())),
            "qualifier summary drift")
    return result
