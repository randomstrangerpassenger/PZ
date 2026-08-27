from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


SLOT_ORDER = ("S1", "S2", "S3", "S4")
SUPPORTED_LOCALES = ("ko", "en")


class TooltipContractError(ValueError):
    """Raised when a T1 contract or projection violates the adopted boundary."""


class SemanticSlotState(StrEnum):
    SELECTED = "selected"
    LEGITIMATE_ABSENCE = "legitimate_absence"
    CORRECTION_REQUIRED = "upstream_identity_correction_required"


class LocaleSurfaceReadiness(StrEnum):
    READY = "ready"
    CORRECTION_REQUIRED = "correction_required"
    NOT_APPLICABLE = "not_applicable"


class MenuParityStatus(StrEnum):
    VERIFIED = "verified"
    CORRECTION_REQUIRED = "correction_required"
    UNVERIFIED = "unverified_without_independent_consumer_evidence"
    NOT_APPLICABLE = "not_applicable"


class T2Progression(StrEnum):
    OPEN = "OPEN"
    UPSTREAM = "BLOCKED_BY_UPSTREAM_CORRECTIONS"
    CONTRACT = "BLOCKED_BY_T1_CONTRACT_INCOMPLETENESS"
    MIXED = "BLOCKED_BY_MIXED_CAUSES"


@dataclass(frozen=True, slots=True)
class Slot:
    slot_id: str
    semantic_identity: str | None
    semantic_state: SemanticSlotState
    localized_surfaces: dict[str, str | None]
    locale_readiness: dict[str, LocaleSurfaceReadiness]
    reason_codes: tuple[str, ...] = ()
    t2_blocking: bool = False
    authority_ref: str | None = None

    def __post_init__(self) -> None:
        if self.slot_id not in SLOT_ORDER:
            raise TooltipContractError(f"unknown slot_id: {self.slot_id}")
        if set(self.localized_surfaces) != set(SUPPORTED_LOCALES):
            raise TooltipContractError("localized_surfaces must contain exactly ko/en")
        if set(self.locale_readiness) != set(SUPPORTED_LOCALES):
            raise TooltipContractError("locale_readiness must contain exactly ko/en")
        if self.semantic_state is SemanticSlotState.SELECTED and not self.semantic_identity:
            raise TooltipContractError("selected slot requires semantic_identity")
        if self.semantic_state is SemanticSlotState.LEGITIMATE_ABSENCE:
            if self.semantic_identity is not None:
                raise TooltipContractError("legitimate absence cannot carry an identity")
            if any(
                state is not LocaleSurfaceReadiness.NOT_APPLICABLE
                for state in self.locale_readiness.values()
            ):
                raise TooltipContractError("legitimate absence locale state must be not_applicable")
            if not self.authority_ref:
                raise TooltipContractError("legitimate absence requires positive owner proof")

    def displayable(self, locale: str) -> bool:
        return (
            self.semantic_state is SemanticSlotState.SELECTED
            and self.locale_readiness[locale] is LocaleSurfaceReadiness.READY
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "semantic_identity": self.semantic_identity,
            "semantic_slot_state": self.semantic_state.value,
            "localized_surfaces": dict(self.localized_surfaces),
            "locale_surface_readiness": {
                key: value.value for key, value in self.locale_readiness.items()
            },
            "reason_codes": list(self.reason_codes),
            "t2_blocking": self.t2_blocking,
            "authority_ref": self.authority_ref,
        }


def ordered_slots(slots: list[Slot] | tuple[Slot, ...]) -> tuple[Slot, ...]:
    by_id = {slot.slot_id: slot for slot in slots}
    if len(by_id) != len(slots):
        raise TooltipContractError("duplicate semantic slot")
    return tuple(by_id[slot_id] for slot_id in SLOT_ORDER if slot_id in by_id)


def validate_handoff_row(row: dict[str, Any]) -> None:
    if not isinstance(row, dict):
        raise TooltipContractError("handoff row must be an object")
    allowed_row_fields = {"schema_version", "subject_binding_ref", "full_type", "slots"}
    if set(row) != allowed_row_fields:
        raise TooltipContractError("handoff contains audit or unknown fields")
    if row.get("schema_version") != "iris-tooltip-t2-handoff-v1":
        raise TooltipContractError("handoff schema version mismatch")
    if not isinstance(row.get("subject_binding_ref"), str) or not row["subject_binding_ref"]:
        raise TooltipContractError("handoff subject binding is missing")
    if not isinstance(row.get("full_type"), str) or not row["full_type"]:
        raise TooltipContractError("handoff FullType is missing")
    slots = row.get("slots")
    if not isinstance(slots, list) or len(slots) > 4:
        raise TooltipContractError("logical row overflow")
    prior_index = -1
    for slot in slots:
        if not isinstance(slot, dict) or set(slot) != {"slot_id", "semantic_identity", "localized_surfaces"}:
            raise TooltipContractError("handoff slot contains audit or unknown fields")
        slot_id = slot.get("slot_id")
        if slot_id not in SLOT_ORDER:
            raise TooltipContractError("handoff slot identity is invalid")
        index = SLOT_ORDER.index(slot_id)
        if index <= prior_index:
            raise TooltipContractError("handoff slots are not unique and in fixed semantic order")
        prior_index = index
        if not isinstance(slot.get("semantic_identity"), str) or not slot["semantic_identity"]:
            raise TooltipContractError("handoff semantic identity is missing")
        surfaces = slot.get("localized_surfaces")
        if not isinstance(surfaces, dict) or set(surfaces) != set(SUPPORTED_LOCALES):
            raise TooltipContractError("handoff locale set mismatch")
        if any(not isinstance(text, str) or not text or "\n" in text or "\r" in text for text in surfaces.values()):
            raise TooltipContractError("handoff locale surface is unavailable or multiline")


def build_handoff_row(
    full_type: str,
    slots: list[Slot] | tuple[Slot, ...],
    *,
    progression: T2Progression,
) -> dict[str, Any]:
    if progression is not T2Progression.OPEN:
        raise TooltipContractError("T2 handoff generation requires progression OPEN")
    ordered = ordered_slots(slots)
    if tuple(slot.slot_id for slot in ordered) != SLOT_ORDER:
        raise TooltipContractError("T2 handoff producer requires all four audited semantic slots before compaction")
    blockers = [slot for slot in ordered if slot.t2_blocking]
    if blockers:
        raise TooltipContractError(f"{full_type}: T2-blocking slot cannot enter handoff")
    compacted = [slot for slot in ordered if slot.semantic_state is not SemanticSlotState.LEGITIMATE_ABSENCE]
    if any(slot.semantic_state is not SemanticSlotState.SELECTED for slot in compacted):
        raise TooltipContractError(f"{full_type}: unresolved slot cannot be compacted")
    row = {
        "schema_version": "iris-tooltip-t2-handoff-v1",
        "subject_binding_ref": "subject_binding.json",
        "full_type": full_type,
        "slots": [
            {
                "slot_id": slot.slot_id,
                "semantic_identity": slot.semantic_identity,
                "localized_surfaces": dict(slot.localized_surfaces),
            }
            for slot in compacted
        ],
    }
    validate_handoff_row(row)
    return row


def mock_consume(row: dict[str, Any], locale: str) -> list[str]:
    if locale not in SUPPORTED_LOCALES:
        raise TooltipContractError(f"unsupported locale: {locale}")
    validate_handoff_row(row)
    result: list[str] = []
    for slot in row["slots"]:
        surfaces = slot["localized_surfaces"]
        text = surfaces[locale]
        result.append(text)
    return result
