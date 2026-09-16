"""Per-call frame assembly shared by ordered, independent purpose handlers."""
from dataclasses import dataclass
from typing import Any


@dataclass
class FrameAssembly:
    plan: Any
    locale: Any
    links: Any
    compact: Any
    units: Any
    used: Any
    output: Any
    material_frames: Any
    functions: Any
    select: Any
    emit: Any
    emit_material: Any
    parallel_names: Any
    names: Any
    object_name: Any
