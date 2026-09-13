"""Korean morphology and parallel predicates, applied to planned meanings."""
from . import description_composition_lexicon as lex


def instrumental(noun):
    final = (ord(noun[-1]) - ord("가")) % 28 if "가" <= noun[-1] <= "힣" else 0
    return noun + ("로" if final in {0, 8} else "으로")


def role(activities, roles, compact=False):
    activities = list(activities)
    # Sharing grammar must not move purposes to collect matching suffixes.
    names = "·".join(activities)
    if roles == ["repair_target"]:
        return "수리 대상이 되는 물품이다"
    if roles == ["transformation_target"] and len(activities) == 1:
        transformations = {
            "창 부착물 회수": "창의 부착물을 회수할 수 있다",
            "산탄총 총신 단축": "산탄총의 총신을 줄일 수 있다",
        }
        if activities[0] in transformations:
            return transformations[activities[0]]
    nouns = "·".join(lex.pair(lex.ROLES[r], "ko") for r in roles)
    if roles == ["tool"]:
        return f"{names}에 사용할 수 있다"
    return f"{names}에 {instrumental(nouns)} 사용할 수 있다"


def parallel(clauses):
    """Elide only a shared syntactic ending, never a repeated meaning."""
    if len(clauses) == 1:
        return clauses[0] + "."
    for ending in ("할 수 있다", "쓸 수 있다", "쓰인다"):
        if all(c.endswith(ending) and "." not in c for c in clauses):
            if ending == "할 수 있다":
                return ", ".join(c.removesuffix("할 수 있다").rstrip() + "하거나" for c in clauses[:-1]) + " " + clauses[-1] + "."
            if ending == "쓸 수 있다":
                return ", ".join(c.removesuffix(ending).rstrip() for c in clauses) + " 쓸 수 있다."
            return ", ".join(c.removesuffix(ending).rstrip() for c in clauses) + " 쓰인다."
    return " ".join(c.rstrip(".") + "." for c in clauses)


def qualified(clauses, conditions):
    text = parallel(clauses)
    if conditions:
        text += " 이때 " + " ".join(c.rstrip(".") + "." for c in conditions)
    return text
