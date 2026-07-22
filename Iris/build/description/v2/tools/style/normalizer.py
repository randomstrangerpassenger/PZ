from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from postproc_ko import postprocess_ko


RULES_DIR = Path(__file__).resolve().parent / "rules"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_primary_use_fact_origin(facts: dict[str, Any]) -> str | None:
    fact_origin = facts.get("fact_origin")
    if not isinstance(fact_origin, dict):
        return None
    primary_use = fact_origin.get("primary_use")
    if isinstance(primary_use, list) and primary_use:
        return str(primary_use[0])
    if isinstance(primary_use, str) and primary_use.strip():
        return primary_use
    return None


def matches_selected_cluster_contains(
    selected_cluster: str | None,
    selected_cluster_contains: list[str] | str | None,
) -> bool:
    if not selected_cluster_contains:
        return False
    haystack = (selected_cluster or "unknown").lower()
    needles = selected_cluster_contains
    if isinstance(needles, str):
        needles = [needles]
    return any(needle.lower() in haystack for needle in needles)


@dataclass
class NormalizationResult:
    normalized_text: str
    log_entry: dict[str, Any]


class StyleNormalizer:
    def __init__(
        self,
        rules_dir: Path = RULES_DIR,
        *,
        activate_rule_ids: set[str] | None = None,
    ) -> None:
        self.rules_dir = rules_dir
        self.global_rules_doc = load_json(self.rules_dir / "global_rules.json")
        self.family_rules_doc = load_json(self.rules_dir / "family_rules.json")
        self.activate_rule_ids = activate_rule_ids
        self.rule_version = self._build_rule_version()

    def _build_rule_version(self) -> str:
        global_version = self.global_rules_doc.get("version", "unknown")
        family_version = self.family_rules_doc.get("version", "unknown")
        return f"global:{global_version};family:{family_version};postproc:v1"

    def _iter_active_global_rules(self) -> list[dict[str, Any]]:
        return [
            rule
            for rule in self.global_rules_doc.get("rules", [])
            if self._is_rule_active(rule)
        ]

    def _is_rule_active(self, rule: dict[str, Any]) -> bool:
        if self.activate_rule_ids is not None:
            return rule.get("id") in self.activate_rule_ids
        return bool(rule.get("active"))

    def _iter_matching_family_rules(
        self,
        *,
        fact_origin: str | None,
        selected_cluster: str | None,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for rule in self.family_rules_doc.get("rules", []):
            if not self._is_rule_active(rule):
                continue
            condition = rule.get("condition", {})
            if condition.get("fact_origin") and condition.get("fact_origin") != fact_origin:
                continue
            cluster_condition = condition.get("selected_cluster_contains")
            if cluster_condition and not matches_selected_cluster_contains(
                selected_cluster,
                cluster_condition,
            ):
                continue
            matches.append(rule)
        return matches

    def _apply_rule(self, text: str, rule: dict[str, Any]) -> tuple[str, bool]:
        match_type = rule.get("type", "literal")
        match = rule["match"]
        replace = rule["replace"]
        if match_type == "literal":
            updated = text.replace(match, replace)
        elif match_type == "regex":
            updated = re.sub(match, replace, text)
        else:
            raise ValueError(f"Unsupported rule type '{match_type}'")
        return updated, updated != text

    def normalize(
        self,
        *,
        item_id: str,
        text: str,
        fact_origin: str | None = None,
        selected_cluster: str | None = None,
        manual_override: bool = False,
    ) -> NormalizationResult:
        original = text
        working = text
        applied_rules: list[str] = []

        if not manual_override:
            for rule in self._iter_active_global_rules():
                working, changed = self._apply_rule(working, rule)
                if changed:
                    applied_rules.append(rule["id"])

            for rule in self._iter_matching_family_rules(
                fact_origin=fact_origin,
                selected_cluster=selected_cluster,
            ):
                working, changed = self._apply_rule(working, rule)
                if changed:
                    applied_rules.append(rule["id"])

        normalized = postprocess_ko(working)
        log_entry = {
            "item_id": item_id,
            "original": original,
            "normalized": normalized,
            "applied_rules": applied_rules,
            "rule_version": self.rule_version,
            "changed": normalized != original,
            "fact_origin": fact_origin,
            "selected_cluster": selected_cluster,
            "manual_override": manual_override,
            "style_rules_skipped": manual_override,
            "legacy_postproc_applied": True,
        }
        return NormalizationResult(normalized_text=normalized, log_entry=log_entry)
