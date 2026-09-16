"""Media purpose frames; selection and consumption stay with the assembly."""
from .description_composition_frame_rules import (
    en,
    lex,
)


def render(state):
    compact = state.compact
    emit = state.emit
    functions = state.functions
    locale = state.locale
    plan = state.plan
    select = state.select
    units = state.units
    used = state.used
    transmission = select({'toggle_radio_microphone'})
    if transmission:
        emit(transmission, lex.pair(('무전으로 말을 송신할 수 있다' if compact else
             '전원을 켜고 마이크 음소거를 해제하면 말을 송신할 수 있다. 같은 주파수에 맞춘 통신 범위 안의 무전기로 받을 수 있다',
             'It can transmit speech by radio' if compact else
             'When powered on with its microphone unmuted, it can transmit speech to radios tuned to the same frequency within range'), locale))
    media = select({'control_device_media', 'tune_radio', 'select_tv_channel'})
    if media:
        media_functions = {f['payload'].get('function') for u in media for f in u['facts']}
        media_type = plan.get('source_traits', {}).get('AcceptMediaType')
        actions = [('control_device_media', ('기록 매체 재생', 'playing CDs' if media_type == '0' else 'playing VHS tapes' if media_type == '1' else 'playing compatible recordings')),
                   ('tune_radio', ('라디오 방송 청취', 'listening to radio broadcasts')),
                   ('select_tv_channel', ('TV 방송 시청', 'watching television broadcasts'))]
        labels = [lex.pair(pair, locale) for fn, pair in actions if fn in media_functions]
        text = ('' + '·'.join(labels) + '에 쓸 수 있다') if locale == 'ko' else ('It can be used for ' + en.join(labels))
        if locale == 'ko':
            verbs = []
            if 'control_device_media' in media_functions:
                media_type = plan.get('source_traits', {}).get('AcceptMediaType')
                verbs.append('CD에 담긴 소리를 재생' if media_type == '0' else 'VHS 테이프에 담긴 영상을 재생' if media_type == '1' else '기록된 내용을 재생')
            if 'tune_radio' in media_functions:
                verbs.append('라디오 방송을 청취')
            if 'select_tv_channel' in media_functions:
                verbs.append('TV 방송을 시청')
            text = '' + '하거나 '.join(verbs) + '할 수 있다'
        outcomes = [u for u in units if not used & set(u['fact_refs']) and all(
            f['payload'].get('property') == 'delivered_media_code_outcome' for f in u['facts'])]
        if outcomes:
            text += ('. 내용에 따라 능력치·경험치·제작법 학습 효과를 얻을 수 있다' if locale == 'ko'
                     else '. Depending on the content, it can affect stats, XP or recipe knowledge')
        emit(media + outcomes, text)

    recordings = select({'insert_recorded_media'})
    if recordings:
        outcomes = [u for u in units if not used & set(u['fact_refs']) and all(
            f['payload'].get('property') == 'delivered_media_code_outcome' for f in u['facts'])]
        category = plan.get('source_traits', {}).get('MediaCategory')
        if category == 'CDs':
            text = ('CD 플레이어로 녹음된 소리를 들을 수 있다' if locale == 'ko' else 'Its recorded audio can be heard with a CD player')
        elif category in {'Home-VHS', 'Retail-VHS'}:
            text = ('VHS 재생 기능이 있는 TV로 녹화된 영상을 볼 수 있다' if locale == 'ko' else 'Its recorded video can be watched on a TV that supports VHS playback')
        else:
            text = ('호환 기기로 녹음·녹화된 내용을 감상할 수 있다' if locale == 'ko' else 'Its recording can be enjoyed with a compatible player')
        if outcomes:
            text += ('. 내용에 따라 능력치·경험치·제작법 학습 효과를 얻을 수 있다' if locale == 'ko'
                     else '. Depending on the content, it can affect stats, XP or recipe knowledge')
        content = select({fn for fn in functions if fn and fn.startswith('recorded_content_')})
        content_fns = {f['payload']['function'].removeprefix('recorded_content_') for u in content for f in u['facts']}
        positive = []
        if 'boredom' in content_fns:
            positive.append(('지루함을 달래', 'relieve boredom'))
        if {'skills', 'recipes'} <= content_fns:
            positive.append(('기술과 제작법을 배우', 'learn skills and recipes'))
        elif 'skills' in content_fns:
            positive.append(('기술을 익히', 'develop skills'))
        elif 'recipes' in content_fns:
            positive.append(('제작법을 배우', 'learn recipes'))
        if positive:
            text += ('. 내용에 따라 ' + '거나 '.join(v[0] for v in positive) + '는 데도 쓸 수 있다') if locale == 'ko' else '. Depending on the recording, it can also help you ' + ' or '.join(v[1] for v in positive)
            if compact and category in {'Home-VHS', 'Retail-VHS'} and not outcomes:
                endings = {'지루함을 달래': '지루함을 달랠', '기술과 제작법을 배우': '기술과 제작법을 배울',
                           '기술을 익히': '기술을 익힐', '제작법을 배우': '제작법을 배울'}
                ability = '거나 '.join([v[0] for v in positive[:-1]] + [endings[positive[-1][0]]])
                text = ('녹화 영상을 감상하고, 내용에 따라 ' + ability + ' 수 있다') if locale == 'ko' else ('Its video can be enjoyed and, depending on the recording, help you ' + ' or '.join(v[1] for v in positive))
        if not compact and {'stress', 'panic'} <= content_fns:
            text += lex.pair(('. 일부 내용은 스트레스나 공포를 느끼게 할 수 있다', '. Some recordings can also cause stress or panic'), locale)
        elif not compact and 'stress' in content_fns:
            text += lex.pair(('. 일부 내용은 스트레스를 느끼게 할 수 있다', '. Some recordings can also cause stress'), locale)
        emit(recordings + outcomes + content, text)

    alarms = select({'set_alarm', 'stop_alarm'})
    if {f['payload'].get('function') for u in alarms for f in u['facts']} == {'set_alarm', 'stop_alarm'}:
        emit(alarms, '원하는 시각에 알람이 울리도록 맞추거나 알람을 끌 수 있다' if locale == 'ko'
             else 'Its alarm can be set to ring at a chosen time or switched off')

    dismantled = select({'dismantle_electronics'})
    salvage_targets = [u for u in units if not used & set(u['fact_refs'])
        and any(f['payload'].get('activity') in {'electronic_salvage', 'radio_salvage'} for f in u['facts'])
        and any(f['payload'].get('role') == 'transformation_target' for f in u['facts'])]
    if dismantled and salvage_targets:
        text = '드라이버로 분해해 전자 부품을 얻을 수 있다' if locale == 'ko' else 'It can be dismantled with a screwdriver to recover electronic parts'
        emit(dismantled + salvage_targets, text)

