"""Korean morphology and parallel predicates, applied to planned meanings."""
from . import description_composition_lexicon as lex
import re


def final_consonant(noun):
    spoken = re.sub(r'\s*\([^()]*\)\s*$', '', noun).rstrip() or noun.rstrip(')]} ')
    return (ord(spoken[-1]) - ord('가')) % 28 if '가' <= spoken[-1] <= '힣' else 0


def object_name(noun):
    return noun + ('을' if final_consonant(noun) else '를')


def instrumental(noun):
    final = final_consonant(noun)
    return noun + ("로" if final in {0, 8} else "으로")


def alternatives(nouns):
    """Coordinate alternative targets without spreading a later predicate."""
    nouns = list(nouns)
    parts = []
    for noun in nouns[:-1]:
        final = final_consonant(noun)
        parts.append(noun + ('이나' if final else '나'))
    return ' '.join(parts + nouns[-1:])


def role(activities, roles, compact=False):
    activities = list(activities)
    if len(activities) > 1:
        return ". ".join(role([activity], roles, compact) for activity in activities)
    # Sharing grammar must not move purposes to collect matching suffixes.
    names = "·".join(activities)
    if roles == ["repair_target"]:
        return "수리 대상이 되는 물품이다"
    if roles == ["transformation_target"] and len(activities) == 1:
        transformations = {
            "창 부착물 회수": "창의 부착물을 회수할 수 있다",
            "산탄총 총신 단축": "총신을 짧게 개조할 수 있다",
        }
        if activities[0] in transformations:
            return transformations[activities[0]]
    nouns = "·".join(lex.pair(lex.ROLES[r], "ko") for r in roles)
    if roles == ["tool"] and activities == ["산탄총 총신 단축"]:
        return "산탄총의 총신을 줄이는 도구로 쓸 수 있다"
    if roles == ["tool"] and names.endswith('는 데'):
        return names + ' 쓸 수 있다'
    actions = {'음식 나누기': '음식을 나누는', '수박 쪼개기': '수박을 쪼개는',
               '석고 혼합': '석고를 섞는', '목공 작업': '목재를 가공하는', '목공': '목재를 가공하는',
               '금속 부품 용접': '금속 부품을 용접하는', '금속 단조': '금속을 단조하는', '금속 가공': '금속을 가공하는', '금속 용접 건축': '금속을 용접해 건축하는', '건축 작업': '건축에 쓰는'}
    def action(label):
        if label in actions:
            return actions[label]
        for ending, verb in ((' 제작', '만드는'), (' 만들기', '만드는'), (' 혼합', '섞는'), (' 준비', '준비하는')):
            if label.endswith(ending):
                noun = label.removesuffix(ending)
                return object_name(noun) + ' ' + verb
        return label + '에 쓰는'
    if len(activities) == 1 and (activities[0] in actions or activities[0].endswith((' 제작', ' 만들기', ' 혼합', ' 준비'))):
        phrase = action(activities[0])
        if roles == ['tool']:
            return phrase + ' 데 쓸 수 있다'
        if roles == ['material']:
            if phrase == '건축에 쓰는':
                return '건축 재료로 쓸 수 있다'
            for ending, temporal in (('만드는', '만들 때'), ('섞는', '섞을 때'), ('가공하는', '가공할 때'), ('용접하는', '용접할 때'), ('단조하는', '단조할 때'), ('건축하는', '건축할 때'), ('준비하는', '준비할 때'), ('나누는', '나눌 때'), ('쪼개는', '쪼갤 때')):
                if phrase.endswith(ending):
                    return phrase.removesuffix(ending) + temporal + ' 재료로 쓸 수 있다'
        return phrase + ' ' + instrumental(nouns) + ' 쓸 수 있다'
    if roles == ["tool"]:
        return f"{names}에 사용할 수 있다"
    return f"{names}에 {instrumental(nouns)} 사용할 수 있다"



def parallel(clauses):
    """Independent clauses keep predicates; a shared ending is not a relation.

    Grounded same-purpose grouping happens in the semantic frames, before this
    fallback receives text. It must not extend a result across another use.
    """
    return " ".join(c.rstrip(".") + "." for c in clauses)


def qualified(clauses, conditions):
    text = parallel(clauses)
    if conditions:
        text += " 이때 " + " ".join(c.rstrip(".") + "." for c in conditions)
    return text
