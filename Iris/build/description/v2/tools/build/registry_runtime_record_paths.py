"""Pure path projection for Registry Runtime Compatibility surface inputs.

This closure-external leaf is stdlib-only and performs no filesystem mutation.
The existing exporter remains the public import and CLI compatibility owner.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def resolve_surface_paths(manifest: dict[str, Any]) -> dict[str, Any]:
    source_row = manifest["source"]
    return {
        "source": {
            component: Path(source_row[component]).resolve()
            for component in ("facts", "decisions", "overlay")
        },
        "rendered": Path(manifest["rendered"]["path"]).resolve(),
        "runtime": {
            "manifest": Path(manifest["runtime"]["manifest"]).resolve(),
            "chunks": Path(manifest["runtime"]["chunks"]).resolve(),
        },
        "package": {
            "manifest": Path(manifest["package"]["manifest"]).resolve(),
            "chunks": Path(manifest["package"]["chunks"]).resolve(),
        },
    }
