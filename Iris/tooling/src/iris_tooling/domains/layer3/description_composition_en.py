"""English coordination without translating the Korean realization."""
from . import description_composition_lexicon as lex


def join(values):
    return values[0] if len(values) == 1 else (" and ".join(values) if len(values) == 2
                                             else ", ".join(values[:-1]) + ", and " + values[-1])


def role(activities, roles, compact=False):
    if roles == ["repair_target"]:
        return "It is an item to be repaired"
    activities = list(activities)
    for suffix in (" crafting", " forging", " preparation"):
        peers = [a.removesuffix(suffix) for a in activities if a.endswith(suffix)]
        if len(peers) > 1 and all(" and " not in p for p in peers):
            activities = [a for a in activities if not a.endswith(suffix)] + [join(peers) + suffix]
    return ("It is " if compact else "It serves as ") + join([lex.pair(lex.ROLES[r], "en") for r in roles]) + " for " + join(activities)


def parallel(clauses):
    if len(clauses) > 1:
        for prefix in ("It can be consumed as ", "It can be used to ", "It can be used for ", "It can ", "It "):
            if all(c.startswith(prefix) and "." not in c for c in clauses):
                return prefix + join([c.removeprefix(prefix) for c in clauses]) + "."
    return " ".join(c.rstrip(".") + "." for c in clauses)


def qualified(clauses, conditions):
    text = parallel(clauses)
    if conditions:
        text += " " + " ".join(c.rstrip(".") + "." for c in conditions)
    return text
