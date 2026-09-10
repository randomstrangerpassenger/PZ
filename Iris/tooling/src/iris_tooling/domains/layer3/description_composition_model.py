"""Offline description records; references are explanatory links, not authority."""
from __future__ import annotations

from collections import Counter

from .composition_model import CompositionError, canonical, require

SCHEMA = "iris-layer3-descriptions-v1"
VERSION = 1
LOCALES = ("ko", "en")
SURFACES = ("compact", "expanded")


def validate_result(result: dict) -> dict:
    require(result.get("schema") == SCHEMA and result.get("version") == VERSION,
            "unknown description schema")
    require(isinstance(result.get("input", {}).get("sha256"), str), "missing input identity")
    require(bool(result.get("producer")), "missing producer identity")
    items = result.get("items")
    require(isinstance(items, list), "missing description items")
    require([i.get("item_id") for i in items] == sorted({i.get("item_id") for i in items}),
            "duplicate or unordered description item")
    for item in items:
        qualifiers = item.get("qualifiers")
        require(isinstance(qualifiers, list), "missing qualifier meanings")
        by_qualifier = {q["qualifier_id"]: q for q in qualifiers}
        require(len(by_qualifier) == len(qualifiers), "duplicate qualifier meaning")
        require(set(item.get("locales", {})) == set(LOCALES), "missing locale")
        for locale, surfaces in item["locales"].items():
            require(set(surfaces) == set(SURFACES), "missing surface")
            for surface, row in surfaces.items():
                require(row.get("item_id") == item["item_id"] and row.get("locale") == locale
                        and row.get("surface") == surface, "description identity drift")
                state, text = row.get("state"), row.get("text")
                require(state in {"present", "absent", "failed"}, "invalid description state")
                require(isinstance(text, str), "invalid description text")
                require(bool(text.strip()) == (state == "present"), "state/text mismatch")
                require(state == "present" or bool(row.get("reason")), "unexplained silence")
                require(isinstance(row.get("segments"), list), "missing text links")
                separator = " " if surface == "compact" else "\n"
                require(text == separator.join(s["text"] for s in row["segments"]), "segment text drift")
                for segment in row["segments"]:
                    require(bool(segment["text"].strip()) and bool(segment["fact_refs"]),
                            "empty segment or meaning")
                    require(bool(segment["block_refs"]) and bool(segment["branch_refs"]),
                            "missing block/branch links")
                    for key in ("block_refs", "branch_refs", "fact_refs", "qualifier_refs", "relation_refs"):
                        refs = segment.get(key)
                        require(isinstance(refs, list) and all(isinstance(ref, str) for ref in refs)
                                and refs == sorted(set(refs)), "invalid segment references")
                    applications = segment.get("qualifier_applications")
                    require(isinstance(applications, list) and
                            [q.get("qualifier_id") for q in applications] == segment["qualifier_refs"],
                            "qualifier application identity drift")
                    for q in applications:
                        require(isinstance(q.get("applies_to_fact_refs"), list)
                                and q["applies_to_fact_refs"] and q["qualifier_id"] in by_qualifier
                                and q["applies_to_fact_refs"] == by_qualifier[q["qualifier_id"]]["applies_to_fact_refs"],
                                "malformed qualifier application")
                if surface == "compact":
                    detail = surfaces["expanded"]
                    require(not row.get("detail_links") or detail["state"] == "present",
                            "detail links point to failed/absent expanded")
                    require(all(type(link["segment"]) is int
                                and 0 <= link["segment"] < len(detail["segments"])
                                for link in row.get("detail_links", [])), "invalid detail link")
                    require(all(link["fact_refs"] == detail["segments"][link["segment"]]["fact_refs"]
                                for link in row.get("detail_links", [])), "detail meaning drift")
    states = Counter(f"{loc}/{surface}/{row['state']}" for item in items
                     for loc, surfaces in item["locales"].items() for surface, row in surfaces.items())
    require(result.get("summary") == {"targets": len(items), "surfaces": sum(states.values()),
                                     "states": dict(sorted(states.items()))}, "description summary drift")
    return result
