from __future__ import annotations

from iris_tooling.__main__ import main


def test_help_is_repository_independent(capsys) -> None:
    assert main([]) == 0
    assert "Iris repository-bound offline build tools" in capsys.readouterr().out
