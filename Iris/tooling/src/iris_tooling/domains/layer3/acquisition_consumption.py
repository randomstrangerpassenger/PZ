"""L3-05 structured handoff: independent authorities, existing resolver only."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from . import acquisition_results as acquisition
from . import investigation as inv
from . import semantic_model as model
from . import semantic_results as semantic


def consume_payloads(semantic_payload: dict, acquisition_payload: dict, contract: dict,
                     inherited: dict, semantic_binding: dict, acquisition_binding: dict) -> list[dict]:
    """In-memory candidate helper. Adopted authority is exposed only by load()."""
    inv.require(semantic_payload['status'] == acquisition_payload['status'] == 'candidate',
                'adopted consumption requires validated readpoints; mixed result modes')
    model.validate_payload(semantic_payload, contract)
    acquisition.validate_payload(acquisition_payload, contract)
    return _consume(semantic_payload, acquisition_payload, contract, inherited, semantic_binding, acquisition_binding)


def _consume(semantic_payload, acquisition_payload, contract, inherited, semantic_binding, acquisition_binding):
    mode = acquisition_payload['status']
    inv.require(mode == semantic_payload['status'] and mode in {'candidate', 'adopted'}, 'mixed result modes')
    inv.require(semantic_payload['authority_id'] != acquisition_payload['authority_id'], 'authority ID collision')
    inv.require(semantic_payload['target_ids'] == acquisition_payload['target_ids'], 'authority target mismatch')
    facts = {}
    results, bindings = defaultdict(list), defaultdict(list)
    keys = set()
    authorities = {}
    for payload, ref in ((semantic_payload, semantic_binding), (acquisition_payload, acquisition_binding)):
        authorities[payload['authority_id']] = {**payload, 'binding': ref}
        for fact in payload['facts']:
            if fact['fact_id'] in facts:
                inv.require(model.fact_identity(facts[fact['fact_id']]) == model.fact_identity(fact)
                            and facts[fact['fact_id']]['payload'] == fact['payload'], 'semantic ID/content collision')
            facts[fact['fact_id']] = fact
        for row in payload['results']:
            key = model.question_key(row)
            inv.require(key not in keys, 'duplicate question across authorities')
            keys.add(key)
            results[row['item_id']].append(row)
        for relation in payload['fact_question_bindings']:
            bindings[relation['question_key'][0]].append(relation)
    inputs = semantic_payload['application_inputs']
    inv.require(len(inputs) == len(semantic_payload['target_ids'])
                and {r['item_id'] for r in inputs} == set(semantic_payload['target_ids']), 'missing application inputs')
    return [inv.resolve_item(row['item_id'], contract, row['routes'], row['gap'], inherited,
                             results[row['item_id']], authorities,
                             fact_question_bindings=bindings[row['item_id']], result_mode=mode)
            for row in inputs]


def load(root: Path, acquisition_ref: dict, *, mode: str = 'adopted') -> dict:
    manifest, acquisition_payload = acquisition.load_manifest(root, acquisition_ref, mode=mode)
    semantic_ref = manifest['semantic_readpoint']
    _, semantic_payload = semantic.load_manifest(root, semantic_ref, mode=mode)
    contract = inv.read_json(root / inv.ROOT / 'contract.json')
    inherited = inv.inherited_contract(root, contract['inherits'])
    model.validate_payload(semantic_payload, contract)
    applications = _consume(semantic_payload, acquisition_payload, contract, inherited, semantic_ref, acquisition_ref)
    return {'mode': mode, 'definition_revision': contract['revision'],
            'readpoints': {'semantic': semantic_ref, 'acquisition': acquisition_ref},
            'semantic': semantic_payload, 'acquisition': acquisition_payload, 'applications': applications}


def non_acquisition_projection(application: dict) -> dict:
    """Compare exactly the pre-existing resolver projection, excluding only L3-04."""
    return {**{k: application[k] for k in ('item_id', 'registry_revision', 'routing', 'pending_scope_refs',
                                          'first_contact', 'scope_state', 'coverage_gap_state')},
            'required_axes': [r for r in application['required_axes'] if r['axis_id'] != 'acquisition'],
            'blockers': [r for r in application['blockers'] if r.get('axis_id') != 'acquisition'],
            'fact_question_bindings': [r for r in application['fact_question_bindings'] if r['question_key'][1] != 'acquisition']}
