"""Compatibility facade for the public-text naturalization domain."""

from iris_tooling.domains.public_text.naturalization_application import *  # noqa: F401,F403
from iris_tooling.domains.public_text.cli import build_parser, main


if __name__ == "__main__":
    raise SystemExit(main())
