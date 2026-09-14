"""English coordination without translating the Korean realization."""
from . import description_composition_lexicon as lex


def join(values):
    return values[0] if len(values) == 1 else (" and ".join(values) if len(values) == 2
                                             else ", ".join(values[:-1]) + ", and " + values[-1])


def role(activities, roles, compact=False):
    if roles == ["repair_target"]:
        return "It is an item to be repaired"
    activities = list(activities)
    if roles == ["transformation_target"] and len(activities) == 1:
        transformations = {
            "spear-attachment recovery": "Its spear attachment can be recovered",
            "shotgun barrel shortening": "Its shotgun barrel can be shortened",
        }
        if activities[0] in transformations:
            return transformations[activities[0]]
    # Preserve the common semantic traversal; suffix elision used to move
    # crafting/preparation peers across intervening independent purposes.
    nouns = join([lex.pair(lex.ROLES[r], "en") for r in roles])
    if roles == ["tool"] and activities == ["shotgun barrel shortening"]:
        return "It can be used to shorten shotgun barrels"
    if roles == ["tool"]:
        return "It can be used for " + join(activities)
    return "It can be used as " + nouns + " for " + join(activities)


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
