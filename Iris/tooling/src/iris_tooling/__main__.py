from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from iris_tooling.build.repository_context import configure_repository


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iris-tooling",
        description="Iris repository-bound offline build tools.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Explicit root of the Iris Git checkout (required by build commands).",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("classification", help="Build Iris classification indexes.")
    subparsers.add_parser("rightclick", help="Build v2.4 right-click evidence.")
    subparsers.add_parser("layer3", help="Compose the current Layer 3 generation.")
    subparsers.add_parser("layer4", help="Export the current Layer 4 Lua projection.")
    subparsers.add_parser("public-text", help="Run current public-text assessment tooling.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args, remainder = parser.parse_known_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.repository_root is None:
        parser.error("--repository-root is required for build commands")
    configure_repository(args.repository_root)

    if args.command == "classification":
        from iris_tooling.domains.classification.cli import main as command_main
    elif args.command == "rightclick":
        from iris_tooling.domains.rightclick.cli import main as command_main
    elif args.command == "layer3":
        from iris_tooling.domains.layer3.cli import main as command_main
    elif args.command == "layer4":
        from iris_tooling.domains.layer4.cli import main as command_main
    else:
        from iris_tooling.domains.public_text.cli import main as command_main
    return command_main(remainder)


if __name__ == "__main__":
    raise SystemExit(main())
