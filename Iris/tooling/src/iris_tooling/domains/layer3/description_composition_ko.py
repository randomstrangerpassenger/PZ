"""Korean morphology and parallel predicates, applied to planned meanings."""
from . import description_composition_lexicon as lex


def instrumental(noun):
    final = (ord(noun[-1]) - ord("가")) % 28 if "가" <= noun[-1] <= "힣" else 0
    return noun + ("로" if final in {0, 8} else "으로")


def role(activities, roles, compact=False):
    activities = list(activities)
    for suffix in (" 제작", " 단조", " 준비"):
        peers = [a.removesuffix(suffix) for a in activities if a.endswith(suffix)]
        if len(peers) > 1:
            activities = [a for a in activities if not a.endswith(suffix)] + ["·".join(peers) + suffix]
    names = "·".join(activities)
    if roles == ["repair_target"]:
        return "수리 대상이 되는 물품이다"
    nouns = "·".join(lex.pair(lex.ROLES[r], "ko") for r in roles)
    if compact:
        final = (ord(nouns[-1]) - ord("가")) % 28 if "가" <= nouns[-1] <= "힣" else 0
        return f"{names}에 쓰는 {nouns}" + ("이다" if final else "다")
    return f"{names}에 {instrumental(nouns)} 쓰인다"


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
