"""Leaf path helper for the description-v2 build tree.

Single source for the description-v2 roots that build scripts otherwise
recompute inline as ``ROOT = Path(__file__).resolve().parents[2]`` (often paired
with a ``sys.path`` bootstrap). Importing these under package form
(``from tools.common.paths import V2_ROOT``) keeps path resolution identical
while removing per-script bootstrap repetition.

Note: this is the ``description/v2`` tools tree's helper. It is distinct from
``Iris/build/tools/`` (the root build tree used by ``quality_gates.py`` etc.);
compose and the other ``description/v2/tools/build`` scripts resolve ``tools`` as
``description/v2/tools``.

Intentionally a **leaf** (stdlib-only) so it can never form an import cycle.

Path anchors (this file lives at
``Iris/build/description/v2/tools/common/paths.py``):

- ``V2_ROOT``    -> ``Iris/build/description/v2``  (parents[2])
- ``BUILD_ROOT`` -> ``Iris/build``                 (parents[4])
"""
from pathlib import Path

_HERE = Path(__file__).resolve()

# parents: [0]=common [1]=tools [2]=v2 [3]=description [4]=build [5]=Iris
V2_ROOT = _HERE.parents[2]
BUILD_ROOT = _HERE.parents[4]

# description-v2 sub-roots (identical to values scripts derive from their own
# ``ROOT = Path(__file__).resolve().parents[2]``).
DATA_DIR = V2_ROOT / "data"
OUTPUT_DIR = V2_ROOT / "output"
STAGING_DIR = V2_ROOT / "staging"
