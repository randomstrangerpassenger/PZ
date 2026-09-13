from __future__ import annotations

import collections
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "Iris/_docs/authority/dvf/layer3_expression/successors/r6/descriptions.json"
OUT = Path(__file__).resolve().parent
CHUNK_SIZE = 400


def exact(value: object) -> str:
    """Render one JSON string without changing any whitespace inside it."""
    return json.dumps(value if isinstance(value, str) else "", ensure_ascii=False)


def surface(item: dict, locale: str, kind: str) -> list[str]:
    entry = item.get("locales", {}).get(locale, {})
    if kind == "s2":
        return [entry.get("s2", {}).get("text", "")]
    return [row.get("text", "") for row in entry.get("expanded", [])]


def sentence_count(text: str) -> int:
    return len([part for part in re.split(r"(?<=[.!?])\s+", text) if part])


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    items = payload["items"]

    for old in OUT.glob("source-*.md"):
        old.unlink()

    for chunk_start in range(0, len(items), CHUNK_SIZE):
        chunk = items[chunk_start : chunk_start + CHUNK_SIZE]
        chunk_end = chunk_start + len(chunk)
        path = OUT / f"source-{chunk_start + 1:04d}-{chunk_end:04d}.md"
        lines = [
            f"# DVF description source {chunk_start + 1:04d}-{chunk_end:04d}",
            "",
            "Source: `Iris/_docs/authority/dvf/layer3_expression/successors/r6/descriptions.json`",
            "",
            "Each text is an exact JSON string literal. Escapes and whitespace are therefore explicit; item and expanded-entry order match the source.",
            "",
        ]
        for offset, item in enumerate(chunk, start=chunk_start + 1):
            item_id = item["item_id"]
            lines.extend([f"## {offset:04d} `{item_id}`", ""])
            for locale in ("ko", "en"):
                s2 = surface(item, locale, "s2")[0]
                lines.extend([f"- `{locale}.s2.text`: `{exact(s2)}`", ""])
                expanded = surface(item, locale, "expanded")
                if not expanded:
                    lines.extend([f"- `{locale}.expanded`: `[]`", ""])
                else:
                    for index, text in enumerate(expanded):
                        lines.extend(
                            [f"- `{locale}.expanded[{index}].text`: `{exact(text)}`", ""]
                        )
        path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    counts: dict[tuple[str, str], collections.Counter[str]] = {}
    owners: dict[tuple[str, str], dict[str, list[str]]] = {}
    metrics = []
    for locale in ("ko", "en"):
        for kind in ("s2", "expanded"):
            key = (locale, kind)
            counts[key] = collections.Counter()
            owners[key] = collections.defaultdict(list)

    for position, item in enumerate(items, start=1):
        item_id = item["item_id"]
        row = {"position": position, "item_id": item_id}
        for locale in ("ko", "en"):
            s2 = surface(item, locale, "s2")[0]
            expanded = surface(item, locale, "expanded")
            row[f"{locale}_s2_chars"] = len(s2)
            row[f"{locale}_s2_sentences"] = sentence_count(s2)
            row[f"{locale}_expanded_entries"] = len(expanded)
            row[f"{locale}_expanded_chars"] = sum(len(text) for text in expanded)
            row[f"{locale}_s2_empty"] = s2 == ""
            counts[(locale, "s2")][s2] += 1
            owners[(locale, "s2")][s2].append(item_id)
            for text in expanded:
                counts[(locale, "expanded")][text] += 1
                owners[(locale, "expanded")][text].append(item_id)
        metrics.append(row)

    (OUT / "screening-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "# Mechanical screening aid",
        "",
        "This is a reading aid, not a quality verdict. Counts are exact-text counts and may overlap.",
        "",
    ]
    for locale in ("ko", "en"):
        for kind in ("s2", "expanded"):
            lines.extend([f"## {locale} {kind}: repeated exact texts", ""])
            groups = [
                (text, count)
                for text, count in counts[(locale, kind)].most_common()
                if text and count >= 2
            ]
            for text, count in groups:
                ids = owners[(locale, kind)][text]
                lines.extend(
                    [
                        f"### {count} items",
                        "",
                        f"Text: `{exact(text)}`",
                        "",
                        "Items: " + ", ".join(f"`{item_id}`" for item_id in ids),
                        "",
                    ]
                )
    (OUT / "screening-repetitions.md").write_text(
        "\n".join(lines), encoding="utf-8", newline="\n"
    )

    print(f"items={len(items)} chunks={(len(items) + CHUNK_SIZE - 1) // CHUNK_SIZE}")
    print("source=" + str(SOURCE))
    print("output=" + str(OUT))


if __name__ == "__main__":
    main()
