"""
Right-click Evidence Pipeline v2.4
=========================================
Phase S: 입력 로딩 & 검증
Phase C: Candidate 생성  (evidence_candidates.json)
Phase D: Candidate 병합 + Decision  (evidence_decisions.json)
Phase U: Uniqueness Overlay 계산  (uniqueness_overlay.v2.4.json)
Phase F: Track routing + Field Registry  (field_registry.json + review_queue.json)

계약 문서:
  - rightclick_evidence_source_allowlist_v2.md
  - rightclick_fail_conditions_v2.md
  - rightclick_resolution_rules_v2.md
  - rightclick_field_registry_v2.md
  - rightclick_track_boundaries_v2.md

이 successor는 v2.4 schema만 지원하며 predecessor mode flag를 제공하지 않는다.
"""
import json
import hashlib
import re
import copy
import argparse
from pathlib import Path
from collections import OrderedDict

from iris_tooling.build.repository_context import require_repository_context
from .infra import StageRunner, load_json, output_root, pipeline_banner

_repository_context = require_repository_context()
IRIS_DIR = _repository_context.iris_root
INPUT_DIR = IRIS_DIR / 'input'
ITEMS_PATH = INPUT_DIR / 'items_itemscript.json'
SOURCE_INDEX_V24_PATH = INPUT_DIR / 'rightclick_source_index.v2.4.json'
RECIPE_PROVENANCE_KEYWORDS = ['recipes.txt', 'recipecode.lua', 'RecipeManager']
ALLOWED_MATCH_TYPES = {'type', 'tag', 'property', 'category', 'display_category', 'script_type'}
TRUTHY_VALUES = {True, 'true', 'TRUE', '1', 1}
DETERMINISTIC_EXCLUSIONS = {'recipe', 'consumption', 'equip', 'passive', 'auto', 'input_material'}
BLOCK_TOOLDEF_PARSE_FAIL = 'BLOCK_TOOLDEF_PARSE_FAIL'
BLOCK_TOOLDEF_NO_DETERMINISTIC_CRITERIA = 'BLOCK_TOOLDEF_NO_DETERMINISTIC_CRITERIA'
BLOCK_ANCHOR_MISSING = 'BLOCK_ANCHOR_MISSING'
BLOCK_MULTI_ANCHOR_CONFLICT = 'BLOCK_MULTI_ANCHOR_CONFLICT'
FORBIDDEN_SOURCE_PATTERNS = ['DisplayName', 'displayname', 'tooltip', 'description', 'meaning', 'menu_label', 'addOption']

class PipelineLogger:

    def __init__(self):
        self.logs = []
        self.fail_count = 0

    def log(self, level, phase, msg, **kwargs):
        entry = {'level': level, 'phase': phase, 'message': msg, **kwargs}
        self.logs.append(entry)
        prefix = {'FAIL': '❌', 'REVIEW': '⚠️', 'NO': '🚫', 'INFO': 'ℹ️', 'PASS': '✅'}.get(level, '  ')
        print(f'  {prefix} [{level}] Phase={phase} {msg}')
        if level == 'FAIL':
            self.fail_count += 1

    def has_fails(self):
        return self.fail_count > 0
logger = PipelineLogger()

def parse_fulltype_item_type(full_type: str) -> str:
    """Extract ItemType from 'Module.ItemType' format."""
    parts = full_type.split('.', 1)
    return parts[1] if len(parts) == 2 else full_type

def parse_semicolon_list(value) -> set:
    """Parse semicolon-delimited string into a set of stripped values."""
    if not value or not isinstance(value, str):
        return set()
    return {v.strip() for v in value.split(';') if v.strip()}

def is_truthy(value) -> bool:
    """Check if value is truthy per v2 contract: {true, 'true', 'TRUE', '1', 1}."""
    return value in TRUTHY_VALUES

def normalize_slug(ref: str) -> str:
    """
    Generate slug from anchor.ref per field_registry_v2.md 4절:
    파일 확장자 제거 → 구분자를 _ 로 치환 → 소문자 변환
    """
    slug = re.sub('\\.[a-zA-Z]+(?=[:/_\\-]|$)', '', ref)
    slug = re.sub('[/\\\\:.\\-;=\\s]+', '_', slug)
    slug = slug.strip('_')
    return slug.lower()

def compute_sha256(data: dict) -> str:
    """Compute SHA256 hash of JSON data for determinism check."""
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def merge_prove_value(existing, incoming, field_name, full_type, logger_ref):
    """
    Merge prove values per v2 contract:
      true + false = FAIL
      true + unknown = true
      unknown + unknown = unknown
    """
    if existing == incoming:
        return (existing, False)
    pair = {existing, incoming}
    if True in pair and False in pair:
        logger_ref.log('FAIL', 'D', f'prove.{field_name} conflict: true+false', fulltype=full_type)
        return (None, True)
    if True in pair and 'unknown' in pair:
        return (True, False)
    if False in pair and 'unknown' in pair:
        return (False, False)
    return (existing, False)

def phase_s_load_and_validate():
    """Load inputs and perform Gate-S validation."""
    print('\n' + '=' * 70)
    print('  Phase S: 입력 로딩 & 검증')
    print('=' * 70)
    if not ITEMS_PATH.exists():
        logger.log('FAIL', 'S', f'File not found: {ITEMS_PATH}')
        return (None, None)
    items = load_json(ITEMS_PATH)
    logger.log('INFO', 'S', f'items_itemscript.json loaded: {len(items)} items')
    if not SOURCE_INDEX_V24_PATH.exists():
        logger.log('FAIL', 'S', f'File not found: {SOURCE_INDEX_V24_PATH}')
        return (None, None)
    source_index = load_json(SOURCE_INDEX_V24_PATH)
    meta = source_index.get('meta', {})
    expected_version = 'v2.4'
    if meta.get('version') != expected_version:
        logger.log('FAIL', 'S', f"source_index meta.version is '{meta.get('version')}', expected '{expected_version}'")
        return (None, None)
    rules = source_index.get('rules', [])
    disabled_rules = [r for r in rules if r.get('disabled')]
    rules = [r for r in rules if not r.get('disabled')]
    schema = source_index.get('schema', {})
    ref_formats = schema.get('anchor', {}).get('ref_format_by_kind', {})
    logger.log('INFO', 'S', f'source_index loaded: {len(rules)} rules active, {len(disabled_rules)} disabled (v2)')
    for rule in rules:
        rule_id = rule.get('rule_id', 'UNKNOWN')
        anchor = rule.get('anchor', {})
        extract = rule.get('extract', {})
        matchers = extract.get('matchers', [])
        kind = anchor.get('kind', '')
        ref = anchor.get('ref', '')
        if kind in ref_formats:
            expected_pattern = ref_formats[kind]
            if '::' not in ref and '::' in expected_pattern:
                logger.log('FAIL', 'S', f"Anchor ref format violation: rule={rule_id}, kind={kind}, ref='{ref}', expected pattern='{expected_pattern}'")
                return (None, None)
        for m in matchers:
            mt = m.get('match_type', '')
            if mt not in ALLOWED_MATCH_TYPES:
                logger.log('FAIL', 'S', f"Invalid match_type: rule={rule_id}, match_type='{mt}'")
                return (None, None)
        runtime_cond = extract.get('runtime_condition')
        if runtime_cond:
            for m in matchers:
                if m.get('value') == runtime_cond:
                    logger.log('FAIL', 'S', f'runtime_condition used as matcher: rule={rule_id}')
                    return (None, None)
        for m in matchers:
            val = m.get('value', '')
            mt = m.get('match_type', '')
            for forbidden in FORBIDDEN_SOURCE_PATTERNS:
                if forbidden.lower() in val.lower() and mt != 'tag':
                    logger.log('FAIL', 'S', f"Forbidden source in matcher: rule={rule_id}, value='{val}', forbidden='{forbidden}'")
                    return (None, None)
    logger.log('PASS', 'S', 'Gate-S validation passed')
    return (items, rules)

def match_item(item_data: dict, full_type: str, matcher: dict) -> bool:
    """Check if a single item matches a single matcher."""
    mt = matcher.get('match_type', '')
    value = matcher.get('value', '')
    if mt == 'type':
        item_type = parse_fulltype_item_type(full_type)
        return item_type == value
    elif mt == 'tag':
        tags = parse_semicolon_list(item_data.get('Tags', ''))
        return value in tags
    elif mt == 'property':
        if value in item_data:
            return is_truthy(item_data[value])
        return False
    elif mt == 'category':
        categories = parse_semicolon_list(item_data.get('Categories', ''))
        return value in categories
    elif mt == 'display_category':
        return item_data.get('DisplayCategory', '') == value
    elif mt == 'script_type':
        return item_data.get('Type', '') == value
    return False

def phase_c_generate_candidates(items: dict, rules: list):
    """
    Generate evidence candidates by applying extraction rules to items.
    Output: evidence_candidates.json
    """
    print('\n' + '=' * 70)
    print('  Phase C: Candidate 생성')
    print('=' * 70)
    candidates_raw = {}
    review_entries = []
    forbidden_detected = False
    for rule in rules:
        rule_id = rule.get('rule_id', 'UNKNOWN')
        anchor = rule.get('anchor', {})
        anchors_list = rule.get('anchors', [])
        extract = rule.get('extract', {})
        prove = rule.get('prove', {})
        exclusions = rule.get('exclusions', {})
        if True and anchors_list:
            roles = {a.get('role') for a in anchors_list if a.get('role')}
            target_predicate_valid = False
            if 'target_predicate' in roles and True:
                tp_anchor = next((a for a in anchors_list if a.get('role') == 'target_predicate'), None)
                tc = tp_anchor.get('target_criteria', {}) if tp_anchor else {}
                tc_values = tc.get('values', [])
                tc_matched = [v for v in tc_values if v in items]
                if len(tc_matched) >= 1:
                    target_predicate_valid = True
                    logger.log('INFO', 'C', f'rule={rule_id}: target_criteria validated ({len(tc_matched)}/{len(tc_values)} fulltypes matched)')
                else:
                    logger.log('REVIEW', 'C', f'rule={rule_id}: target_criteria_empty (0/{len(tc_values)} fulltypes matched, B forced unknown)')
                    review_entries.append({'kind': 'target_criteria_empty', 'rule_id': rule_id, 'blocked_reason': 'target_criteria_empty'})
            elif 'target_predicate' in roles:
                target_predicate_valid = True
            role_prove = {'executing_tool': True if 'tool_predicate' in roles else 'unknown', 'external_target': True if target_predicate_valid else 'unknown', 'persistent_change': True if 'outcome_change' in roles else 'unknown'}
            explicit_prove = rule.get('prove', {})
            prove = {}
            for pkey in ['executing_tool', 'external_target', 'persistent_change']:
                role_val = role_prove[pkey]
                expl_val = explicit_prove.get(pkey, 'unknown')
                if role_val is True:
                    prove[pkey] = True
                elif expl_val is True or expl_val is False:
                    prove[pkey] = expl_val
                else:
                    prove[pkey] = role_val
        matchers = extract.get('matchers', [])
        excluded_matchers = extract.get('excluded_matchers', [])
        blocked_reason = extract.get('extract_blocked_reason')
        secondary_confirm = extract.get('secondary_confirm_fields', [])
        if not matchers or blocked_reason:
            reason = blocked_reason or 'matchers is empty'
            review_entries.append({'kind': 'rule_blocked', 'rule_id': rule_id, 'blocked_reason': reason})
            logger.log('REVIEW', 'C', f"Rule blocked (no deterministic extraction): rule={rule_id}, reason='{reason}'")
            continue
        matcher_logic = extract.get('matcher_logic', 'OR').upper()
        matched_fulltypes = set()
        for full_type, item_data in items.items():
            if matcher_logic == 'AND':
                if all((match_item(item_data, full_type, m) for m in matchers)):
                    matched_fulltypes.add(full_type)
            else:
                for m in matchers:
                    if match_item(item_data, full_type, m):
                        matched_fulltypes.add(full_type)
                        break
        logger.log('INFO', 'C', f'rule={rule_id}: {len(matched_fulltypes)} candidates from matchers')
        if secondary_confirm and matched_fulltypes:
            confirmed = set()
            for ft in matched_fulltypes:
                item_data = items[ft]
                if any((cf in item_data for cf in secondary_confirm)):
                    confirmed.add(ft)
            dropped = len(matched_fulltypes) - len(confirmed)
            if dropped > 0:
                logger.log('INFO', 'C', f'rule={rule_id}: {dropped} items dropped (secondary_confirm_fields not present), {len(confirmed)} confirmed')
            matched_fulltypes = confirmed
        excluded_fulltypes = set()
        if excluded_matchers:
            static_excluded_matchers = []
            for em in excluded_matchers:
                em_type = em.get('match_type', '')
                em_value = em.get('value', '')
                em_reason = em.get('exclusion_reason', 'excluded_matcher')
                if em_type == 'property' and em_value.endswith('()'):
                    review_entries.append({'kind': 'excluded_matcher', 'rule_id': rule_id, 'match_type': em_type, 'value': em_value, 'review_reason': em_reason})
                else:
                    static_excluded_matchers.append(em)
            for full_type, item_data in items.items():
                for em in static_excluded_matchers:
                    em_value = em.get('value', '')
                    em_reason = em.get('exclusion_reason', 'excluded_matcher')
                    dummy_matcher = {'match_type': em.get('match_type', ''), 'value': em_value}
                    if match_item(item_data, full_type, dummy_matcher):
                        excluded_fulltypes.add(full_type)
                        review_entries.append({'kind': 'excluded_matcher_item', 'rule_id': rule_id, 'fulltype': full_type, 'review_reason': f'excluded_matcher: {em_value} ({em_reason})'})
        for ft in matched_fulltypes:
            if ft not in candidates_raw:
                candidates_raw[ft] = {'anchors': [], 'prove': {'executing_tool': 'unknown', 'external_target': 'unknown', 'persistent_change': 'unknown'}, 'exclusions': {'recipe': False, 'consumption': False, 'equip': False, 'passive': False, 'auto': False, 'input_material': False, 'property_based': False}, 'rule_ids': [], 'forbidden_source_detected': False}
            entry = candidates_raw[ft]
            if True and anchors_list:
                for anch in anchors_list:
                    entry['anchors'].append({'kind': anch.get('kind', ''), 'ref': anch.get('ref', ''), 'version': anch.get('version', ''), 'role': anch.get('role')})
            else:
                entry['anchors'].append({'kind': anchor.get('kind', ''), 'ref': anchor.get('ref', ''), 'version': anchor.get('version', '')})
            for pkey in ['executing_tool', 'external_target', 'persistent_change']:
                new_val = prove.get(pkey, 'unknown')
                entry['prove'][pkey] = new_val
            for ekey in entry['exclusions']:
                if ekey == 'forbidden_source_detected':
                    continue
                if exclusions.get(ekey, False):
                    entry['exclusions'][ekey] = True
            entry['rule_ids'].append(rule_id)
    sorted_candidates = OrderedDict()
    for ft in sorted(candidates_raw.keys()):
        entry = candidates_raw[ft]
        seen_anchors = {}
        for a in entry['anchors']:
            key = (a['kind'], a['ref'])
            if key not in seen_anchors:
                seen_anchors[key] = a
            elif a.get('version', '') > seen_anchors[key].get('version', ''):
                seen_anchors[key] = a
        entry['anchors'] = sorted(seen_anchors.values(), key=lambda a: a['ref'])
        entry.pop('forbidden_source_detected', None)
        sorted_candidates[ft] = entry
    if forbidden_detected:
        logger.log('FAIL', 'C', '[FAIL:FORBIDDEN_SOURCE] forbidden_source_detected=true')
        return (None, None)
    logger.log('PASS', 'C', f'Candidate generation complete: {len(sorted_candidates)} FullTypes')
    return (sorted_candidates, review_entries)

def phase_d_merge_and_decide(candidates: dict):
    """
    Merge candidates per FullType and produce decisions.
    Output: evidence_decisions.json
    """
    print('\n' + '=' * 70)
    print('  Phase D: Candidate 병합 + Decision')
    print('=' * 70)
    merged = OrderedDict()
    for ft in sorted(candidates.keys()):
        entry = candidates[ft]
        merged[ft] = copy.deepcopy(entry)
    decisions = OrderedDict()
    for ft in sorted(merged.keys()):
        entry = merged[ft]
        prove = entry['prove']
        exclusions = entry['exclusions']
        anchors = entry['anchors']
        rule_ids = entry['rule_ids']
        exclusion_hit = None
        anchor_refs = [a.get('ref', '') for a in anchors]
        has_recipe_ref = any((kw in ref for ref in anchor_refs for kw in RECIPE_PROVENANCE_KEYWORDS))
        if not anchor_refs:
            mechanism_type = 'unknown'
        elif has_recipe_ref:
            mechanism_type = 'recipe'
        else:
            mechanism_type = 'non_recipe'
        has_menu_gen = any((a.get('role') == 'menu_generation' for a in anchors))
        if mechanism_type == 'unknown':
            decisions[ft] = {'decision': 'REVIEW', 'proof': {'A_static_source': prove.get('executing_tool', 'unknown'), 'B_external_target': prove.get('external_target', 'unknown'), 'C_persistent_change': prove.get('persistent_change', 'unknown')}, 'exclusion_reason': None, 'review_reason': 'mechanism_type=unknown (fail-safe)', 'anchors': anchors, 'rule_ids': rule_ids, 'surface_type': 'context_menu' if has_menu_gen else None, 'mechanism_type': mechanism_type, 'recipe_ui_only': None}
            logger.log('REVIEW', 'D', f"fulltype='{ft}', mechanism_type=unknown (fail-safe)")
            continue
        recipe_ui_only = not has_menu_gen and mechanism_type == 'recipe'
        if recipe_ui_only:
            exclusion_hit = 'recipe_ui_only'
        if not exclusion_hit:
            for ex_flag in ['consumption', 'equip', 'passive', 'auto', 'input_material']:
                if exclusions.get(ex_flag, False):
                    exclusion_hit = ex_flag
                    break
        surface_type = 'context_menu' if has_menu_gen else None
        if exclusion_hit:
            decisions[ft] = {'decision': 'NO', 'proof': {'A_static_source': prove.get('executing_tool', 'unknown'), 'B_external_target': prove.get('external_target', 'unknown'), 'C_persistent_change': prove.get('persistent_change', 'unknown')}, 'exclusion_reason': exclusion_hit, 'review_reason': None, 'anchors': anchors, 'rule_ids': rule_ids}
            decisions[ft]['surface_type'] = surface_type
            decisions[ft]['mechanism_type'] = mechanism_type
            decisions[ft]['recipe_ui_only'] = recipe_ui_only
            logger.log('NO', 'D', f"fulltype='{ft}', exclusion='{exclusion_hit}', rule_ids={rule_ids}")
            continue
        if exclusions.get('property_based', False):
            decisions[ft] = {'decision': 'REVIEW', 'proof': {'A_static_source': prove.get('executing_tool', 'unknown'), 'B_external_target': prove.get('external_target', 'unknown'), 'C_persistent_change': prove.get('persistent_change', 'unknown')}, 'exclusion_reason': None, 'review_reason': 'property_based exclusion (auto conclusion forbidden)', 'anchors': anchors, 'rule_ids': rule_ids}
            decisions[ft]['surface_type'] = surface_type
            decisions[ft]['mechanism_type'] = mechanism_type
            decisions[ft]['recipe_ui_only'] = recipe_ui_only
            logger.log('REVIEW', 'D', f"fulltype='{ft}', reason='property_based'")
            continue
        has_unknown = any((prove.get(k) == 'unknown' for k in ['executing_tool', 'external_target', 'persistent_change']))
        if has_unknown:
            unknown_fields = [k for k in ['executing_tool', 'external_target', 'persistent_change'] if prove.get(k) == 'unknown']
            decisions[ft] = {'decision': 'REVIEW', 'proof': {'A_static_source': prove.get('executing_tool', 'unknown'), 'B_external_target': prove.get('external_target', 'unknown'), 'C_persistent_change': prove.get('persistent_change', 'unknown')}, 'exclusion_reason': None, 'review_reason': f"prove unknown: {', '.join(unknown_fields)}", 'anchors': anchors, 'rule_ids': rule_ids}
            decisions[ft]['surface_type'] = surface_type
            decisions[ft]['mechanism_type'] = mechanism_type
            decisions[ft]['recipe_ui_only'] = recipe_ui_only
            logger.log('REVIEW', 'D', f"fulltype='{ft}', reason='prove unknown: {unknown_fields}'")
            continue
        a_met = prove.get('executing_tool') is True
        b_met = prove.get('external_target') is True
        c_met = prove.get('persistent_change') is True
        all_excl_false = not any((exclusions.get(k, False) for k in exclusions))
        if a_met and b_met and c_met and all_excl_false:
            if not rule_ids:
                logger.log('FAIL', 'D', f'PASS item with empty rule_ids: {ft} (pipeline defect — PASS requires evidence)')
                return None
            decisions[ft] = {'decision': 'PASS', 'proof': {'A_static_source': True, 'B_external_target': True, 'C_persistent_change': True}, 'exclusion_reason': None, 'review_reason': None, 'anchors': anchors, 'rule_ids': rule_ids}
            decisions[ft]['surface_type'] = surface_type
            decisions[ft]['mechanism_type'] = mechanism_type
            decisions[ft]['recipe_ui_only'] = recipe_ui_only
            logger.log('PASS', 'D', f"fulltype='{ft}', rule_ids={rule_ids}")
        else:
            decisions[ft] = {'decision': 'REVIEW', 'proof': {'A_static_source': prove.get('executing_tool', 'unknown'), 'B_external_target': prove.get('external_target', 'unknown'), 'C_persistent_change': prove.get('persistent_change', 'unknown')}, 'exclusion_reason': None, 'review_reason': 'A/B/C not all true but no unknown (unexpected state)', 'anchors': anchors, 'rule_ids': rule_ids}
            decisions[ft]['surface_type'] = surface_type
            decisions[ft]['mechanism_type'] = mechanism_type
            decisions[ft]['recipe_ui_only'] = recipe_ui_only
            logger.log('REVIEW', 'D', f"fulltype='{ft}', reason='unexpected prove state'")
    logger.log('PASS', 'D', f'Decision complete: {len(decisions)} FullTypes')
    stats = {'PASS': 0, 'NO': 0, 'REVIEW': 0}
    for d in decisions.values():
        stats[d['decision']] = stats.get(d['decision'], 0) + 1
    logger.log('INFO', 'D', f'Decision summary: {stats}')
    return decisions

def phase_u_uniqueness_overlay(decisions: dict, candidates: dict):
    """
    Compute uniqueness overlay based on rule_id unit.
    For each rule_id, count how many PASS FullTypes are matched.
      1 → STRONG, 2+ → WEAK
    Also records matched_fulltypes (all criteria-matched, including NO/REVIEW)
    for denominator transparency.

    Output: uniqueness_overlay dict
    """
    print('\n' + '=' * 70)
    print('  Phase U: Uniqueness Overlay')
    print('=' * 70)
    rule_to_pass = {}
    rule_to_all = {}
    for ft, dec in decisions.items():
        rule_ids = dec.get('rule_ids', [])
        for rid in rule_ids:
            rule_to_all.setdefault(rid, set()).add(ft)
            if dec['decision'] == 'PASS':
                rule_to_pass.setdefault(rid, set()).add(ft)
    by_rule_id = OrderedDict()
    for rid in sorted(rule_to_all.keys()):
        pass_fts = sorted(rule_to_pass.get(rid, []))
        all_fts = sorted(rule_to_all[rid])
        count = len(pass_fts)
        if count == 0:
            uniqueness = None
        elif count == 1:
            uniqueness = 'STRONG'
        else:
            uniqueness = 'WEAK'
        by_rule_id[rid] = {'pass_fulltypes': pass_fts, 'matched_fulltypes': all_fts, 'pass_count': count, 'matched_count': len(all_fts), 'uniqueness': uniqueness}
        if uniqueness:
            logger.log('INFO', 'U', f'rule={rid}, pass={count}, matched={len(all_fts)}, uniqueness={uniqueness}')
    by_fulltype = OrderedDict()
    for ft, dec in sorted(decisions.items()):
        if dec['decision'] != 'PASS':
            continue
        contributing = {}
        for rid in dec.get('rule_ids', []):
            rule_entry = by_rule_id.get(rid)
            if rule_entry and rule_entry['uniqueness']:
                contributing[rid] = rule_entry['uniqueness']
        values = set(contributing.values())
        if values == {'STRONG'}:
            summary = 'STRONG_ONLY'
        elif values == {'WEAK'}:
            summary = 'WEAK_ONLY'
        elif 'STRONG' in values and 'WEAK' in values:
            summary = 'MIXED'
        else:
            summary = 'UNKNOWN'
        by_fulltype[ft] = {'contributing_rules': contributing, 'uniqueness_summary': summary}
    logger.log('PASS', 'U', f'Overlay complete: {len(by_fulltype)} PASS items, {len(by_rule_id)} rules')
    summary_stats = {'STRONG_ONLY': 0, 'WEAK_ONLY': 0, 'MIXED': 0}
    for entry in by_fulltype.values():
        s = entry['uniqueness_summary']
        summary_stats[s] = summary_stats.get(s, 0) + 1
    logger.log('INFO', 'U', f'Uniqueness summary: {summary_stats}')
    overlay = {'by_rule_id': by_rule_id, 'by_fulltype': by_fulltype}
    return overlay

def phase_f_field_registry(decisions: dict, review_entries_from_c: list):
    """
    Route decisions to tracks and build field_registry.json + review_queue.json.
    """
    print('\n' + '=' * 70)
    print('  Phase F: Track routing + Field Registry')
    print('=' * 70)
    field_registry = {}
    review_queue = []
    for entry in review_entries_from_c:
        review_queue.append(entry)
    for ft, dec in decisions.items():
        decision = dec['decision']
        anchors = dec['anchors']
        if decision == 'NO':
            continue
        elif decision == 'REVIEW':
            review_queue.append({'kind': 'item_review', 'fulltype': ft, 'review_reason': dec.get('review_reason', 'unspecified'), 'rule_ids': dec.get('rule_ids', [])})
            continue
        elif decision == 'PASS':
            if not anchors:
                logger.log('FAIL', 'F', f'PASS item without anchors: {ft}')
                return (None, None)
            rep_anchor = min(anchors, key=lambda a: a['ref'])
            field_id = f"rc.{rep_anchor['kind']}.{normalize_slug(rep_anchor['ref'])}"
            if field_id not in field_registry:
                field_registry[field_id] = {'field_id': field_id, 'representative_anchor': rep_anchor, 'all_anchors': [], 'items': []}
            fentry = field_registry[field_id]
            fentry['items'].append({'fulltype': ft, 'decision': decision, 'rule_ids': dec.get('rule_ids', [])})
            existing_keys = {(a['kind'], a['ref']) for a in fentry['all_anchors']}
            for a in anchors:
                key = (a['kind'], a['ref'])
                if key not in existing_keys:
                    fentry['all_anchors'].append(a)
                    existing_keys.add(key)
    sorted_registry = OrderedDict()
    for fid in sorted(field_registry.keys()):
        entry = field_registry[fid]
        entry['all_anchors'] = sorted(entry['all_anchors'], key=lambda a: a['ref'])
        entry['items'] = sorted(entry['items'], key=lambda i: i['fulltype'])
        sorted_registry[fid] = entry

    def review_sort_key(r):
        if r.get('kind') == 'rule_blocked':
            return ('zzz_rule', r.get('rule_id', ''))
        ft = r.get('fulltype', '')
        return ('aaa_item', ft)
    review_queue.sort(key=review_sort_key)
    logger.log('INFO', 'F', f"Field registry: {len(sorted_registry)} fields, {sum((len(f['items']) for f in sorted_registry.values()))} items")
    logger.log('INFO', 'F', f'Review queue: {len(review_queue)} entries')
    return (sorted_registry, review_queue)

def cross_phase_validation(candidates, decisions, field_registry, review_queue):
    """
    Cross-phase consistency checks per fail_conditions_v2.md 3-D.
    """
    print('\n' + '=' * 70)
    print('  Cross-Phase Validation')
    print('=' * 70)
    passed = True
    field_items = set()
    for fentry in field_registry.values():
        for item in fentry['items']:
            ft = item['fulltype']
            if ft in field_items:
                logger.log('FAIL', 'CROSS', f'Duplicate item in field_registry: {ft}')
                passed = False
            field_items.add(ft)
    review_fulltypes = set()
    for r in review_queue:
        if r.get('kind') in ('item_review', 'excluded_matcher_item'):
            review_fulltypes.add(r.get('fulltype', ''))
    for ft, dec in decisions.items():
        decision = dec['decision']
        cand = candidates.get(ft, {})
        cand_exclusions = cand.get('exclusions', {})
        cand_prove = cand.get('prove', {})
        if decision == 'PASS':
            for ex_key in DETERMINISTIC_EXCLUSIONS:
                if cand_exclusions.get(ex_key, False):
                    logger.log('FAIL', 'CROSS', f'Exclusion ignored: {ft} has exclusions.{ex_key}=true but decision={decision}')
                    passed = False
        if decision == 'PASS':
            proof = dec.get('proof', {})
            prove_map = {'A_static_source': 'executing_tool', 'B_external_target': 'external_target', 'C_persistent_change': 'persistent_change'}
            for proof_key, cand_key in prove_map.items():
                if cand_prove.get(cand_key) == 'unknown' and proof.get(proof_key) is True:
                    logger.log('FAIL', 'CROSS', f'Unknown confirmed: {ft} prove.{cand_key}=unknown but {proof_key}=true in decision')
                    passed = False
        if decision == 'REVIEW' and ft not in review_fulltypes:
            found = any((r.get('fulltype') == ft for r in review_queue if r.get('kind') in ('item_review', 'excluded_matcher_item')))
            if not found:
                logger.log('FAIL', 'CROSS', f'REVIEW missing from review_queue: {ft}')
                passed = False
        if decision == 'NO' and ft in field_items:
            logger.log('FAIL', 'CROSS', f'NO item registered in field_registry: {ft}')
            passed = False
    dec_keys = list(decisions.keys())
    if dec_keys != sorted(dec_keys):
        logger.log('FAIL', 'CROSS', 'evidence_decisions.json not sorted by FullType')
        passed = False
    reg_keys = list(field_registry.keys())
    if reg_keys != sorted(reg_keys):
        logger.log('FAIL', 'CROSS', 'field_registry.json not sorted by Field ID')
        passed = False
    if passed:
        logger.log('PASS', 'CROSS', 'All cross-phase validations passed')
    else:
        logger.log('FAIL', 'CROSS', 'Cross-phase validation FAILED')
    return passed

def save_outputs(candidates, decisions, field_registry, review_queue, output_directory, uniqueness_overlay=None, property_based_items=None, runner=None):
    """Save all output files."""
    print('\n' + '=' * 70)
    print('  Saving Outputs')
    print('=' * 70)
    runner = runner or StageRunner()
    suffix = '.v2.4'
    outputs = {f'evidence_candidates{suffix}.json': candidates, f'evidence_decisions{suffix}.json': decisions, f'field_registry{suffix}.json': field_registry, f'review_queue{suffix}.json': review_queue}
    if uniqueness_overlay is not None:
        outputs[f'uniqueness_overlay{suffix}.json'] = uniqueness_overlay
    if property_based_items is not None:
        outputs[f'property_based_items{suffix}.json'] = property_based_items
    for filename, data in outputs.items():
        path = output_directory / filename
        runner.save_json(path, data, on_saved=lambda saved_path: logger.log('INFO', 'OUT', f'Saved: {saved_path} ({saved_path.stat().st_size} bytes)'))

def determinism_check(items_list):
    """Compute SHA256 for determinism verification.
    items_list: list of (name, data) tuples.
    """
    print('\n' + '=' * 70)
    print('  Determinism Check')
    print('=' * 70)
    hashes = {}
    for name, data in items_list:
        h = compute_sha256(data)
        hashes[name] = h
        print(f'  SHA256({name}): {h[:24]}...')
    return hashes

def collect_property_based_items(decisions: dict) -> dict:
    """Collect property_based items for cross-pipeline routing."""
    items = OrderedDict()
    for ft, dec in sorted(decisions.items()):
        if dec['decision'] == 'REVIEW' and dec.get('review_reason', '').startswith('property_based'):
            items[ft] = {'fulltype': ft, 'rule_ids': dec.get('rule_ids', []), 'review_reason': dec['review_reason']}
    return items

def main(argv: list[str] | None = None):
    """Main entry point for the right-click evidence pipeline."""
    parser = argparse.ArgumentParser(description='Right-click Evidence Pipeline')
    parser.parse_args(argv)
    output_directory = output_root(
        repository_root=_repository_context.repository_root,
    )
    version_label = 'v2.4'
    pipeline_banner(f'Right-click Evidence Pipeline {version_label}', 70)
    runner = StageRunner()
    (items, rules), ok = runner.run(phase_s_load_and_validate, failed=lambda result: result[0] is None or result[1] is None, abort_message='❌ Pipeline aborted at Phase S')
    if not ok:
        return 1
    (candidates, review_entries), ok = runner.run(lambda: phase_c_generate_candidates(items, rules), failed=lambda result: result[0] is None, abort_message='❌ Pipeline aborted at Phase C')
    if not ok:
        return 1
    decisions, ok = runner.run(lambda: phase_d_merge_and_decide(candidates), failed=lambda result: result is None, abort_message='❌ Pipeline aborted at Phase D')
    if not ok:
        return 1
    uniqueness_overlay = None
    uniqueness_overlay, ok = runner.run(lambda: phase_u_uniqueness_overlay(decisions, candidates), failed=lambda result: result is None, abort_message='❌ Pipeline aborted at Phase U')
    if not ok:
        return 1
    (field_registry, review_queue), ok = runner.run(lambda: phase_f_field_registry(decisions, review_entries), failed=lambda result: result[0] is None, abort_message='❌ Pipeline aborted at Phase F')
    if not ok:
        return 1
    if uniqueness_overlay:
        by_ft = uniqueness_overlay.get('by_fulltype', {})
        for fentry in field_registry.values():
            for item in fentry['items']:
                ft = item['fulltype']
                overlay_entry = by_ft.get(ft, {})
                item['uniqueness_summary'] = overlay_entry.get('uniqueness_summary', 'UNKNOWN')
    validation_passed = cross_phase_validation(candidates, decisions, field_registry, review_queue)
    property_based_items = None
    property_based_items = collect_property_based_items(decisions)
    save_outputs(candidates, decisions, field_registry, review_queue, output_directory, uniqueness_overlay=uniqueness_overlay, property_based_items=property_based_items, runner=runner)
    hash_items = [('candidates', candidates), ('decisions', decisions), ('field_registry', field_registry), ('review_queue', review_queue)]
    if uniqueness_overlay:
        hash_items.append(('uniqueness_overlay', uniqueness_overlay))
    hashes = determinism_check(hash_items)
    print('\n' + '=' * 70)
    print(f'  Pipeline Summary ({version_label})')
    print('=' * 70)
    stats = {'PASS': 0, 'NO': 0, 'REVIEW': 0}
    for d in decisions.values():
        stats[d['decision']] = stats.get(d['decision'], 0) + 1
    print(f'  Total candidates: {len(candidates)}')
    print(f"  Decisions: PASS={stats['PASS']}, NO={stats['NO']}, REVIEW={stats['REVIEW']}")
    print(f'  Fields created: {len(field_registry)}')
    print(f'  Review queue entries: {len(review_queue)}')
    if uniqueness_overlay:
        u_stats = {}
        for e in uniqueness_overlay.get('by_fulltype', {}).values():
            s = e.get('uniqueness_summary', 'UNKNOWN')
            u_stats[s] = u_stats.get(s, 0) + 1
        print(f'  Uniqueness: {u_stats}')
    if property_based_items is not None:
        print(f'  Property-based items: {len(property_based_items)}')
    print(f"  Cross-phase validation: {('PASSED' if validation_passed else 'FAILED')}")
    if logger.has_fails():
        print(f'\n❌ Pipeline completed with {logger.fail_count} FAIL(s)')
        return 1
    print('\n✅ Pipeline completed successfully')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
