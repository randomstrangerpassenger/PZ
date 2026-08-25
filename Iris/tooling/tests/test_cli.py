from __future__ import annotations

from pathlib import Path

import pytest

from iris_tooling.__main__ import main


def test_help_is_repository_independent(capsys) -> None:
    assert main([]) == 0
    assert "Iris repository-bound offline build tools" in capsys.readouterr().out


@pytest.mark.parametrize("legacy_flag", ["--v22", "--v23", "--v24"])
def test_rightclick_rejects_predecessor_mode_flags(legacy_flag: str) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    with pytest.raises(SystemExit) as error:
        main(
            [
                "--repository-root",
                str(repository_root),
                "rightclick",
                legacy_flag,
            ]
        )
    assert error.value.code == 2
