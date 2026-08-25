from __future__ import annotations

from pathlib import Path

from iris_tooling.build.repository_context import configure_repository


configure_repository(Path(__file__).resolve().parents[3])
