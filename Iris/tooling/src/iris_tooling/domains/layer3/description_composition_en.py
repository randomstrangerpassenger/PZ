"""English coordination without translating the Korean realization."""
import re

from . import description_composition_lexicon as lex


def article(noun):
    """An indefinite singular phrase for an explicitly named crafted object."""
    noun = noun[:1].lower() + noun[1:]
    return ('an ' if noun[:1] in 'aeiou' else 'a ') + noun


def object_phrase(record):
    """Realize a result noun; display labels remain separate in evidence."""
    noun = record['names']['en'].lower()
    mass = {'electronic scrap', 'electronics scrap', 'scrap metal', 'gunpowder', 'meat', 'frog meat', 'wire', 'thread', 'twine', 'rope', 'sheet rope', 'plaster', 'dough', 'bread', 'rice', 'pasta', 'tuna'}
    if record.get('declared_traits', {}).get('DisplayCategory') == 'Ammo':
        return noun if noun.endswith(('ammo', 'ammunition', 'rounds', 'shells', 'bullets')) else noun + ' rounds'
    if noun in mass or noun.endswith((' ammo', ' ammunition', ' gunpowder')) or (noun.endswith('s') and not noun.endswith('ss')):
        return noun
    if str(record.get('count', '')).isdigit() and int(record['count']) > 1:
        return noun[:-1] + 'ies' if noun.endswith('y') and noun[-2:-1] not in 'aeiou' else noun + 's'
    return article(noun)


def coordinated_actions(actions):
    result = []
    for action in actions:
        if result and action.startswith('repairing ') and result[-1].startswith('repairing '):
            result[-1] += ' and ' + action.removeprefix('repairing ')
        else:
            result.append(action)
    return join(result)


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


def package_identifies_results(subject, results):
    """Elide only redundant English label words; missing words keep the result.

    This is presentation redundancy, not an inference of a package's contents.
    The declared result relation remains the authority for that identity.
    """
    def words(label):
        packaging = {'opened', 'canned', 'tin', 'jar', 'of'}
        def singular(word):
            if word.endswith('ies'): return word[:-3] + 'y'
            if word.endswith(('oes', 'shes', 'ches')): return word[:-2]
            return word[:-1] if word.endswith('s') and not word.endswith('ss') else word
        return {singular(w) for w in re.findall(r"[a-z0-9]+", label.lower()) if w not in packaging}
    known = words(subject)
    return bool(results) and all(words(r['names']['en']) and words(r['names']['en']) <= known for r in results)
