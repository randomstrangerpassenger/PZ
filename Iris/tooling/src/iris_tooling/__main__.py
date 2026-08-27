from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import subprocess
import sys

from iris_tooling.build.repository_context import configure_repository


BUILD_TARGETS = ("classification", "rightclick", "layer3", "layer4", "public-text")
LEGACY_COMMANDS = BUILD_TARGETS


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iris-tooling",
        description="Iris repository-bound offline build and validation adapter.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        help="Explicit root of the Iris Git checkout.",
    )
    subparsers = parser.add_subparsers(dest="command")

    build = subparsers.add_parser("build", help="Run a current package-owned producer.")
    build.add_argument("target", choices=BUILD_TARGETS)

    validate = subparsers.add_parser(
        "validate", help="Delegate validation to the repository-owned authority."
    )
    validate_subparsers = validate.add_subparsers(dest="validate_action", required=True)
    full = validate_subparsers.add_parser("full")
    full.add_argument("--commit", required=True)
    full.add_argument("--claim-id", required=True)
    full.add_argument("--environment-receipt", type=Path, required=True)
    full.add_argument("--work-root", type=Path, required=True)
    full.add_argument("--result-root", type=Path, required=True)
    full.add_argument("--orchestration-receipt", type=Path, required=True)
    full.add_argument(
        "--execution-context",
        choices=("standalone_full_gate", "composite_baseline_admission_chain_stage_6"),
        default="standalone_full_gate",
    )
    full.add_argument("--predecessor-stage-receipt-set-sha256")
    full.add_argument("--qualification-contract-sha256")
    full.add_argument("--predecessor-stage-receipt-set", type=Path)
    full.add_argument("--qualification-contract", type=Path)

    inspect = subparsers.add_parser("inspect", help="Read a static current route projection.")
    inspect.add_argument("target", choices=("current",))

    install = subparsers.add_parser("install", help="Run a package-owned immutable installer.")
    install.add_argument("target", choices=("classification",))

    for name in LEGACY_COMMANDS:
        subparsers.add_parser(name, help=argparse.SUPPRESS)
    return parser


def _require_repository(parser: argparse.ArgumentParser, repository_root: Path | None) -> Path:
    if repository_root is None:
        parser.error("--repository-root is required")
    root = repository_root.resolve()
    configure_repository(root)
    return root


def _domain_main(target: str, remainder: Sequence[str]) -> int:
    if target == "classification":
        from iris_tooling.domains.classification.cli import main as command_main
    elif target == "rightclick":
        from iris_tooling.domains.rightclick.cli import main as command_main
    elif target == "layer3":
        from iris_tooling.domains.layer3.cli import main as command_main
    elif target == "layer4":
        from iris_tooling.domains.layer4.cli import main as command_main
    else:
        from iris_tooling.domains.public_text.cli import main as command_main
    return command_main(remainder)


def _validate_full(
    args: argparse.Namespace,
    repository_root: Path,
    parser: argparse.ArgumentParser,
) -> int:
    launcher = repository_root / "Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1"
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(launcher),
        "-RepositoryRoot",
        str(repository_root),
        "-Commit",
        args.commit,
        "-ClaimId",
        args.claim_id,
        "-EnvironmentReceipt",
        str(args.environment_receipt.resolve()),
        "-WorkRoot",
        str(args.work_root.resolve()),
        "-ResultRoot",
        str(args.result_root.resolve()),
        "-OrchestrationReceipt",
        str(args.orchestration_receipt.resolve()),
        "-BaselineAdmissionExecutionContext",
        args.execution_context,
    ]
    composite_inputs = (
        ("--predecessor-stage-receipt-set-sha256", args.predecessor_stage_receipt_set_sha256),
        ("--qualification-contract-sha256", args.qualification_contract_sha256),
        ("--predecessor-stage-receipt-set", args.predecessor_stage_receipt_set),
        ("--qualification-contract", args.qualification_contract),
    )
    if args.execution_context == "composite_baseline_admission_chain_stage_6":
        missing = [flag for flag, value in composite_inputs if value is None]
        if missing:
            parser.error(
                "composite execution context requires " + ", ".join(missing)
            )
        command.extend(
            [
                "-PredecessorStageReceiptSetSha256",
                args.predecessor_stage_receipt_set_sha256,
                "-QualificationContractSha256",
                args.qualification_contract_sha256,
                "-PredecessorStageReceiptSet",
                str(args.predecessor_stage_receipt_set.resolve()),
                "-QualificationContract",
                str(args.qualification_contract.resolve()),
            ]
        )
    elif any(value is not None for _, value in composite_inputs):
        parser.error(
            "composite identity inputs require "
            "--execution-context composite_baseline_admission_chain_stage_6"
        )
    completed = subprocess.run(
        command,
        cwd=repository_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    return completed.returncode


def _inspect_current(repository_root: Path) -> int:
    route_path = repository_root / "Iris/_docs/authority/iris_current_route_index.json"
    try:
        route = json.loads(route_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"current route unavailable: {exc}", file=sys.stderr)
        return 2
    if route.get("schema_version") != "iris-current-route-index-v1":
        print("current route has an unsupported schema", file=sys.stderr)
        return 2
    print(json.dumps(route, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args, remainder = parser.parse_known_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    repository_root = _require_repository(parser, args.repository_root)

    if args.command == "build":
        forwarded = list(remainder)
        if args.target == "classification":
            forwarded.insert(0, "build")
        return _domain_main(args.target, forwarded)
    if args.command == "install":
        return _domain_main(args.target, ["install", *remainder])
    if args.command == "validate":
        if remainder:
            parser.error("unrecognized arguments: " + " ".join(remainder))
        return _validate_full(args, repository_root, parser)
    if args.command == "inspect":
        return _inspect_current(repository_root)
    return _domain_main(args.command, remainder)


if __name__ == "__main__":
    raise SystemExit(main())
