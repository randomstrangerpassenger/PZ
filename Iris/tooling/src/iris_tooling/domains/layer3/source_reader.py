"""Bounded, non-executing readers. Observations are not semantic facts.

Keep declaration multiplicity and repeated clauses. Lua group expansion accepts
only the reviewed straight-line tag/type union grammar; opaque code stays open.
"""
from __future__ import annotations

from collections import defaultdict
import re

from .investigation import require


def mask(text: str, *, lua: bool = False, strings: bool = False) -> str:
    if not lua:
        output = list(text)
        i = 0
        while i < len(text):
            start = i
            if text[i] == '"':
                quote = text[i]
                i += 1
                while i < len(text):
                    if text[i] == '\\': i += 2
                    elif text[i] == quote:
                        i += 1
                        break
                    else: i += 1
                if not strings: continue
            elif text.startswith('//', i):
                end = text.find('\n', i)
                i = len(text) if end < 0 else end
            elif text.startswith('/*', i):
                depth = 1
                i += 2
                while i < len(text) and depth:
                    if text.startswith('/*', i):
                        depth += 1
                        i += 2
                    elif text.startswith('*/', i):
                        depth -= 1
                        i += 2
                    else: i += 1
                require(depth == 0, 'unterminated script comment')
            else:
                i += 1
                continue
            for j in range(start, min(i, len(text))):
                if output[j] != '\n': output[j] = ' '
        return ''.join(output)
    pattern = (r'--\[\[.*?\]\]|--[^\n]*' if lua else r'/\*.*?\*/|//[^\n]*')
    pattern += r'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' '''.rstrip()
    def replace(match):
        value = match[0]
        if value[:1] in {'"', "'"} and not strings:
            return value
        return ''.join('\n' if c == '\n' else ' ' for c in value)
    return re.sub(pattern, replace, text, flags=re.S)


def clauses(body: str) -> list[str]:
    hidden = mask(body, strings=True)
    start, depth, result = 0, 0, []
    for i, c in enumerate(hidden):
        if c in '[({':
            depth += 1
        elif c in '])}':
            depth -= 1
            require(depth >= 0, "unbalanced clause")
        elif c == ',' and depth == 0:
            if body[start:i].strip():
                result.append(body[start:i].strip())
            start = i + 1
    require(depth == 0, "unclosed clause")
    if body[start:].strip():
        result.append(body[start:].strip())
    return result


def declarations(text: str, path: str) -> list[dict]:
    clean = mask(text)
    hidden = mask(text, strings=True)
    modules = []
    for match in re.finditer(r'\bmodule\s+(\w+)\s*\{', hidden):
        depth, end = 1, match.end()
        while end < len(hidden) and depth:
            depth += (hidden[end] == '{') - (hidden[end] == '}')
            end += 1
        require(depth == 0, f"unterminated module: {path}")
        modules.append((match[1], match.end(), end - 1))
    result = []
    for module, begin, finish in modules:
        region = hidden[begin:finish]
        pattern = r'\b(item|recipe|evolvedrecipe|fixing|multistagebuild)\s+([^{}\r\n]+?)\s*\{'
        for match in re.finditer(pattern, region):
            start = begin + match.start()
            body_start = begin + match.end()
            depth, end = 1, body_start
            while end < finish and depth:
                depth += (hidden[end] == '{') - (hidden[end] == '}')
                end += 1
            require(depth == 0, f"unterminated declaration: {path}:{start}")
            # Names may contain spaces, but never normalize case or FullType.
            name = clean[begin + match.start(2):begin + match.end(2)].strip()
            body = clean[body_start:end - 1]
            result.append({"path": path, "line": text[:start].count('\n') + 1,
                           "end_line": text[:end].count('\n') + 1,
                           "module": module, "kind": match[1], "name": name,
                           "clauses": clauses(body), "raw": text[start:end]})
    return result


def properties(record: dict, separator: str = '=') -> dict[str, list[str]]:
    result = defaultdict(list)
    for clause in record['clauses']:
        match = re.fullmatch(r'\s*(\w+)\s*' + re.escape(separator) + r'\s*(.*?)\s*', clause, re.S)
        if match:
            result[match[1]].append(match[2])
    return dict(result)


def unique_properties(record: dict) -> dict[str, str] | None:
    fields = properties(record)
    if any(len(values) != 1 for values in fields.values()):
        return None
    return {key: values[0] for key, values in fields.items()}


def qualify(module: str, token: str) -> str:
    return token if '.' in token else module + '.' + token


def groups(text: str) -> dict[str, dict]:
    clean = mask(text, lua=True)
    result = {}
    pattern = r'(?m)^function (Recipe\.GetItemTypes\.\w+)\(scriptItems\)(.*?)^end\b'
    for match in re.finditer(pattern, clean, re.S):
        body = match[2]
        tags = re.findall(r'scriptItems:addAll\(getScriptManager\(\):getItemsTag\("([^"]+)"\)\)', body)
        types = re.findall(r'addExistingItemType\(scriptItems,\s*"([^"]+)"\)', body)
        residue = re.sub(r'scriptItems:addAll\(getScriptManager\(\):getItemsTag\("[^"]+"\)\)', '', body)
        residue = re.sub(r'addExistingItemType\(scriptItems,\s*"[^"]+"\)', '', residue)
        result[match[1]] = {"line": clean[:match.start()].count('\n') + 1,
                            "tags": tags, "types": types, "raw": text[match.start():match.end()],
                            "supported": not residue.strip(' \t\r\n;') and bool(tags or types)}
    return result


def expand_structural_groups(definitions: dict, item_fields: dict, clothing_text: str) -> None:
    """Interpret the six reviewed source predicates; do not execute Lua.

    Fabric registry rows and name/type comparisons are snapshot observations.
    Runtime registry additions and loader ambiguity remain outside this expansion.
    """
    clean = mask(clothing_text, lua=True)
    fabrics = set(re.findall(r'ClothingRecipesDefinitions\["FabricType"\]\["([^"]+)"\]\s*=\s*\{', clean))
    blocked = set(re.findall(r'ClothingRecipesDefinitions\["FabricType"\]\["([^"]+)"\]\.noSheetRope\s*=\s*true', clean))
    named = set(re.findall(r'ClothingRecipesDefinitions\["([^"]+)"\]\s*=\s*\{', clean)) - {'FabricType'}
    prefix = 'Recipe.GetItemTypes.'
    for name in ('CraftSheetRope', 'RipClothing_Cotton', 'RipClothing_Denim', 'RipClothing_Leather', 'RipSheets', 'DismantleDigitalWatch'):
        group = definitions.get(prefix + name)
        require(group is not None, 'missing structural group source')
        members = []
        for item_id, fields in item_fields.items():
            if fields is None: continue
            item_name = item_id.split('.', 1)[1]
            fabric, kind = fields.get('FabricType'), fields.get('Type')
            if name == 'CraftSheetRope':
                applicable = (fabric in fabrics and fabric not in blocked) if kind == 'Clothing' and fabric else item_name in named
            elif name.startswith('RipClothing_'):
                required_fabric = name.split('_', 1)[1]
                applicable = required_fabric in fabrics and kind == 'Clothing' and fabric == required_fabric and item_name not in named
            elif name == 'RipSheets':
                applicable = kind != 'Clothing' and item_name in named
            else:
                applicable = kind == 'AlarmClockClothing' and 'Digital' in item_name
            if applicable: members.append(item_id)
        group.update(supported=True, exact_members=sorted(members), interpretation='reviewed structural predicate; snapshot only')


def recipe_participants(record: dict, item_fields: dict, group_defs: dict) -> tuple[list[dict], list[str]]:
    rows, opaque = [], []
    for ordinal, clause in enumerate(record['clauses']):
        if re.match(r'^\w+\s*:', clause):
            if not re.match(r'^Result\s*:', clause):
                continue
            expression, role = clause.split(':', 1)[1].strip(), 'result'
        else:
            match = re.match(r'^(keep|destroy)\s+', clause)
            role = match[1] if match else 'input'
            expression = clause[match.end():] if match else clause
        for token in expression.split('/'):
            group_match = re.fullmatch(r'\[([\w.]+)\](?:=\d+(?:\.\d+)?)?', token.strip())
            ids = set()
            if group_match:
                group = group_defs.get(group_match[1], {})
                if not group.get('supported'):
                    opaque.append(token)
                    continue
                ids.update(group.get('exact_members', []))
                for item_id, fields in item_fields.items():
                    if fields is not None and (set(fields.get('Tags', '').split(';')) & set(group['tags'])
                                               or item_id.split('.', 1)[1] in group['types']):
                        ids.add(item_id)
            else:
                match = re.fullmatch(r'([\w.]+)(?:=\d+(?:\.\d+)?)?', token.strip())
                if not match:
                    opaque.append(expression)
                    continue
                ids.add(qualify(record['module'], match[1]))
            rows.extend({"item_id": item_id, "role": role, "clause": clause,
                         "ordinal": ordinal, "group": group_match[1] if group_match else None}
                        for item_id in sorted(ids))
    return rows, sorted(set(opaque))


def literal_hits(text: str, tokens: set[str]) -> list[dict]:
    """Search seeds only: even a matching string does not prove a predicate."""
    clean = mask(text, lua=True)
    return [{"line": clean[:m.start()].count('\n') + 1, "token": m[1]}
            for m in re.finditer(r'''["']([^"'\r\n]+)["']''', clean) if m[1] in tokens]


def selected_item_predicates(text: str, item: str, fields: dict | None) -> list[dict]:
    """Partially evaluate selected-item predicates, retaining unresolved atoms.

    Only testItem in the inventory selection loop is an established alias for
    this item. Other receivers and live getter values are never substituted.
    """
    clean = mask(text, lua=True)
    result = []
    for line, expression in enumerate(clean.splitlines(), 1):
        if 'testItem:' not in expression or not re.search(r'\b(if|elseif)\b', expression): continue
        atoms = []
        for match in re.finditer(r'testItem:(getType|getFullType|getCategory)\(\)\s*(==|~=)\s*"([^"]+)"', expression):
            value = {'getType': item.split('.', 1)[1], 'getFullType': item,
                     'getCategory': {'Container': 'Container'}.get((fields or {}).get('Type'), (fields or {}).get('Type'))}[match[1]]
            atoms.append({'predicate': match[0], 'value': None if value is None else ((value == match[3]) == (match[2] == '=='))})
        if 'testItem:getScriptItem():isCantEat()' in expression:
            atoms.append({'predicate': 'testItem:getScriptItem():isCantEat()',
                          'value': None if fields is None else fields.get('CantEat', '').lower() == 'true'})
        if 'testItem:canBeWrite()' in expression:
            atoms.append({'predicate': 'testItem:canBeWrite()',
                          'value': None if fields is None else fields.get('CanBeWrite', '').lower() == 'true'})
        result.append({'line': line, 'expression': expression.strip(), 'evaluated_atoms': atoms,
                       'remaining': 'Full boolean branch, live getters and action target state remain symbolic; atoms are not branch truth.'})
    return result
