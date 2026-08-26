"""Retained non-current predecessor for the context-outcome pipeline.

The former implementation depended on retired phase packages, defaulted to the
repository-local ``Iris/output`` workspace, and copied generated Lua directly
over the current runtime source.  The adopted lightweighting plan selects the
C disposition: do not recover those missing phases or introduce a replacement
CLI.  Current ``IrisContextOutcomes.lua`` is a Git-authored runtime source; any
future producer must use an external candidate and a separately reviewed,
hash-bound installer.
"""

from __future__ import annotations


def main() -> int:
    raise SystemExit(
        "context_outcomes_main.py is a retired predecessor; "
        "repository-local output and direct runtime installation are unsupported"
    )


if __name__ == "__main__":
    main()
