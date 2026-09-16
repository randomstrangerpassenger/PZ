"""Medical purpose frames; selection and consumption stay with the assembly."""
from .description_composition_frame_rules import (
    en,
    lex,
    purpose_tokens,
)


def render(state):
    compact = state.compact
    emit = state.emit
    locale = state.locale
    plan = state.plan
    select = state.select
    units = state.units
    used = state.used
    bandaging = select({'apply_bandage'})
    if bandaging:
        preparation = [u for u in units if not used & set(u['fact_refs']) and 'bandaging_material_preparation' in purpose_tokens(u)
                       and {r['item_id'] for rel in u.get('recipe_targets', []) for r in rel['results']} <= {'Base.AlcoholBandage', 'Base.AlcoholRippedSheets'}
                       and u.get('recipe_targets')]
        infection = [u for u in units if not used & set(u['fact_refs'])
                     and all(f['payload'].get('property') == 'bandage_patient_infection' for f in u['facts'])
                     and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.BANDAGE_INFECTION}]
        text = '상처를 덮어 처치할 수 있다' if locale == 'ko' else 'It can be used to cover and dress wounds'
        if preparation:
            text += '. 소독해서 쓸 수도 있다' if locale == 'ko' else '. It can also be disinfected before use'
        if infection and not compact:
            text += ('. 감염된 재료를 쓰면 상처가 감염될 수 있다' if locale == 'ko'
                     else '. Infected material can cause wound infection')
        emit(bandaging + preparation + infection, text)

    if compact:
        medical = select({'apply_bandage', 'apply_splint', 'clean_burn'})
        if medical:
            functions = {f['payload'].get('function') for u in medical for f in u['facts']}
            labels = [lex.pair(pair, locale) for fn, pair in (
                ('apply_bandage', ('붕대', 'bandaging')), ('clean_burn', ('화상 세척', 'cleaning burns')),
                ('apply_splint', ('골절 고정', 'splinting fractures'))) if fn in functions]
            consequences = [u for u in units if not used & set(u['fact_refs'])
                and all(f['fact_kind'] == 'effect' and f['payload'].get('property') in {
                    'burn_wash_requirement', 'additional_pain', 'bandage_patient_infection', 'applied_bandage_life', 'splint_factor'} for f in u['facts'])]
            emit(medical + consequences, ', '.join(labels) + '에 쓸 수 있다' if locale == 'ko'
                 else 'It can be used for ' + en.join(labels))
        patch = select({'apply_garment_patch'})
        emit(patch, '의류의 구멍을 덧대거나 패딩을 추가할 수 있다' if locale == 'ko'
             else 'It can be used to patch garment holes or add padding')

    burns = select({'clean_burn'})
    if burns:
        consequences = [u for u in units if not used & set(u['fact_refs'])
            and all(f['fact_kind'] == 'effect' and f['payload'].get('property') in {'burn_wash_requirement', 'additional_pain'} for f in u['facts'])
            and {plan['qualifiers'][q]['payload']['predicate'] for q in u['qualifier_refs']} == {lex.source.BURN_CLEANING}]
        emit(burns + consequences, '화상을 씻는 데 쓸 수 있다' if locale == 'ko'
             else 'It can be used to clean burns')

