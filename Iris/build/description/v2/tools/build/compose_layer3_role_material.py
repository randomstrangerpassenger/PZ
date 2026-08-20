from __future__ import annotations

from typing import Any

try:
    from .layer3_body_role_realign import compose_role_material
except ImportError:
    from layer3_body_role_realign import compose_role_material


def compose_item_role_material(
    *,
    item_id: str,
    mapped_facts: list[dict[str, Any]],
    readiness: str,
    current_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compile source-bound role material without reading rendered prose semantically."""
    return compose_role_material(item_id, mapped_facts, readiness, current_entry)
