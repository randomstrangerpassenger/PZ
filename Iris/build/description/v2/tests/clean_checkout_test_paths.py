"""External temporary paths for repository validation tests."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


OUTPUT_ROOT_ENV = "IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT"
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
_DEFAULT_TEMP_DIRECTORY: tempfile.TemporaryDirectory | None = None


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _default_external_base(checkout_key: str) -> Path:
    public_root = os.environ.get("PUBLIC")
    system_temp_root = Path(public_root) if public_root else Path(tempfile.gettempdir())
    return system_temp_root.resolve() / "IT" / checkout_key


def external_test_root() -> Path:
    global _DEFAULT_TEMP_DIRECTORY
    configured = os.environ.get(OUTPUT_ROOT_ENV)
    if configured:
        root = Path(configured).resolve()
    else:
        checkout_key = hashlib.sha256(
            str(REPOSITORY_ROOT).casefold().encode("utf-8")
        ).hexdigest()[:12]
        if _DEFAULT_TEMP_DIRECTORY is None:
            base = _default_external_base(checkout_key)
            base.mkdir(parents=True, exist_ok=True)
            _DEFAULT_TEMP_DIRECTORY = tempfile.TemporaryDirectory(
                prefix="r-",
                dir=base,
            )
        root = Path(_DEFAULT_TEMP_DIRECTORY.name).resolve()
    if _is_within(root, REPOSITORY_ROOT):
        raise RuntimeError(
            f"{OUTPUT_ROOT_ENV} must resolve outside the checkout: {root}"
        )
    root.mkdir(parents=True, exist_ok=True)
    return root


def external_test_path(name: str) -> Path:
    root = external_test_root()
    path = (root / name).resolve()
    if not _is_within(path, root):
        raise RuntimeError(f"test path escapes external root: {name}")
    return path
