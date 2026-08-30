from __future__ import annotations

from typing import Any

from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, sha256_bytes
from iris_tooling.domains.tooltip_t1.models import SLOT_ORDER, SUPPORTED_LOCALES
from .contract import AcceptedInput, check_surface


def project(accepted: AcceptedInput, contract: dict[str, Any]) -> tuple[dict, dict, dict]:
    data, provenance = {}, {}
    distribution = {str(count): 0 for count in range(5)}
    for row in accepted.rows:
        full_type, slots = row["full_type"], row["slots"]
        lines = {locale: [] for locale in SUPPORTED_LOCALES}
        line_provenance = []
        for position, slot in enumerate(slots, 1):
            hashes = {}
            for locale in SUPPORTED_LOCALES:
                surface = slot["localized_surfaces"][locale]
                check_surface(surface, locale, contract, f"{full_type}/{slot['slot_id']}/{locale}")
                lines[locale].append(surface)
                digest = sha256_bytes(surface.encode("utf-8"))
                hashes[locale] = {"source_sha256": digest, "final_sha256": digest}
            line_provenance.append({
                "position": position, "slot_id": slot["slot_id"],
                "role": contract["slot_roles"][slot["slot_id"]],
                "semantic_identity": slot["semantic_identity"], "surface_sha256": hashes,
            })
        present = [slot["slot_id"] for slot in slots]
        data[full_type] = lines
        provenance[full_type] = {
            "status": "generated_nonempty" if slots else "generated_empty",
            "line_count": {locale: len(slots) for locale in SUPPORTED_LOCALES},
            "present_slots": present,
            "omitted_slots": [slot for slot in SLOT_ORDER if slot not in present],
            "lines": line_provenance,
        }
        distribution[str(len(slots))] += 1
    summary = {
        "line_distribution": distribution, "generation_success_count": len(data),
        "generation_failure_count": 0, "contract_violation_count": 0, "lexical_guard_hit_count": 0,
        "locale_projection_sha256": {
            locale: sha256_bytes(canonical_bytes({key: data[key][locale] for key in sorted(data)}))
            for locale in SUPPORTED_LOCALES
        },
    }
    return data, provenance, summary
