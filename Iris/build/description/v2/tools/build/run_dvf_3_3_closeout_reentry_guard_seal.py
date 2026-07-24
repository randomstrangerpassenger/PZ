#!/usr/bin/env python
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from unittest import mock
import uuid

import dvf_3_3_closeout_reentry_guard_seal_common as common


EXPECTED_CONTRACT_PROBE_REQUEST_SHA256 = (
    "3637b794c30ef25766696b37680881a1266512167838befdd7c75cf8cd8ccab2"
)
EXPECTED_FORBIDDEN_SURFACE_PROBE_REQUEST_SHA256 = (
    "821013056117e43b97729e500b246146398173e49061e1bc0bb391d4f90fa93b"
)
ISOLATED_TEMP_ROOT_ENV = "IRIS_DVF_ISOLATED_TEMP_ROOT"


def read_probe_request() -> dict:
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise ValueError("probe request must be a JSON object")
    return payload


def contract_probe_payload(request: dict) -> dict:
    request_sha256 = common.canonical_hash(request)
    if request_sha256 != EXPECTED_CONTRACT_PROBE_REQUEST_SHA256:
        return {
            "status": "FAIL",
            "writes_performed": False,
            "error": "contract_probe_request_hash_mismatch",
            "expected_request_sha256": (
                EXPECTED_CONTRACT_PROBE_REQUEST_SHA256
            ),
            "actual_request_sha256": request_sha256,
        }
    allowed_paths = {
        common.ARCHITECTURE_DOC.relative_to(common.REPO_ROOT).as_posix(): (
            common.ARCHITECTURE_DOC
        ),
        common.DECISIONS_DOC.relative_to(common.REPO_ROOT).as_posix(): (
            common.DECISIONS_DOC
        ),
        common.ROADMAP_DOC.relative_to(common.REPO_ROOT).as_posix(): (
            common.ROADMAP_DOC
        ),
    }
    surface_lines = {}
    for row in request["surface_lines"]:
        path = allowed_paths.get(str(row.get("path")))
        if path is None:
            return {
                "status": "FAIL",
                "writes_performed": False,
                "error": "contract_probe_surface_path_not_allowed",
                "path": row.get("path"),
            }
        surface_lines[str(row["fixture_id"])] = (
            common.classify_surface_line(path, str(row["text"]))
        )
    predecessor_contexts = {
        text: common.classify_predecessor_context(text)
        for text in request["predecessor_contexts"]
    }
    claim_texts = {
        text: common.classify_claim_text(text)
        for text in request["claim_texts"]
    }
    return {
        "status": "PASS",
        "writes_performed": False,
        "request_sha256": request_sha256,
        "expected_current_route_test_count": (
            common.EXPECTED_CURRENT_ROUTE_TEST_COUNT
        ),
        "full_current_route_schema_version": (
            common.FULL_CURRENT_ROUTE_SCHEMA_VERSION
        ),
        "full_current_route_contract_class": (
            common.FULL_CURRENT_ROUTE_CONTRACT_CLASS
        ),
        "route_summary": common.full_current_route_result_summary(),
        "document_paths": {
            "architecture": common.ARCHITECTURE_DOC.relative_to(
                common.REPO_ROOT
            ).as_posix(),
            "decisions": common.DECISIONS_DOC.relative_to(
                common.REPO_ROOT
            ).as_posix(),
            "roadmap": common.ROADMAP_DOC.relative_to(
                common.REPO_ROOT
            ).as_posix(),
        },
        "surface_lines": surface_lines,
        "predecessor_contexts": predecessor_contexts,
        "claim_texts": claim_texts,
    }


def historical_route_payload() -> dict:
    return json.loads(
        json.dumps(common.read_json(common.CURRENT_ROUTE_RESULT))
    )


@contextmanager
def isolated_fixture_candidate(label: str):
    nonce = uuid.uuid4().hex
    isolated_temp_root_value = os.environ.get(ISOLATED_TEMP_ROOT_ENV)
    isolated_temp_root = (
        Path(isolated_temp_root_value).resolve()
        if isolated_temp_root_value
        else None
    )
    if (
        isolated_temp_root is not None
        and not isolated_temp_root.is_dir()
    ):
        raise ValueError("isolated temp root is not an existing directory")
    with tempfile.TemporaryDirectory(
        prefix=f"d3c_{label[:3]}_{nonce[:8]}_",
        dir=isolated_temp_root,
    ) as temp_dir:
        temp_root = Path(temp_dir)
        candidate_root = temp_root / "e"
        shutil.copytree(common.EVIDENCE_ROOT, candidate_root)
        candidate_docs = temp_root / "docs"
        candidate_docs.mkdir(parents=True, exist_ok=True)
        candidate_claim_boundary = (
            candidate_docs / common.CLAIM_BOUNDARY_DOC.name
        )
        candidate_ledger_packet = (
            candidate_docs / common.LEDGER_PACKET_DOC.name
        )
        candidate_completion_policy = (
            candidate_docs / common.COMPLETION_POLICY_DOC.name
        )
        candidate_predecessor_policy = (
            candidate_docs / common.PREDECESSOR_POLICY_DOC.name
        )
        shutil.copy2(common.CLAIM_BOUNDARY_DOC, candidate_claim_boundary)
        shutil.copy2(common.LEDGER_PACKET_DOC, candidate_ledger_packet)
        shutil.copy2(
            common.COMPLETION_POLICY_DOC,
            candidate_completion_policy,
        )
        shutil.copy2(
            common.PREDECESSOR_POLICY_DOC,
            candidate_predecessor_policy,
        )
        with mock.patch.multiple(
            common,
            EVIDENCE_ROOT=candidate_root,
            CURRENT_ROUTE_RESULT=(
                candidate_root
                / "phase7"
                / "full_current_route_validation_result.json"
            ),
            CLAIM_BOUNDARY_DOC=candidate_claim_boundary,
            LEDGER_PACKET_DOC=candidate_ledger_packet,
            COMPLETION_POLICY_DOC=candidate_completion_policy,
            PREDECESSOR_POLICY_DOC=candidate_predecessor_policy,
        ):
            yield {
                "root": candidate_root,
                "nonce": nonce,
                "route_path": common.CURRENT_ROUTE_RESULT,
            }


def forbidden_surface_probe_payload(request: dict) -> dict:
    request_sha256 = common.canonical_hash(request)
    if (
        request_sha256
        != EXPECTED_FORBIDDEN_SURFACE_PROBE_REQUEST_SHA256
    ):
        return {
            "status": "FAIL",
            "writes_performed": False,
            "error": "forbidden_surface_probe_request_hash_mismatch",
            "expected_request_sha256": (
                EXPECTED_FORBIDDEN_SURFACE_PROBE_REQUEST_SHA256
            ),
            "actual_request_sha256": request_sha256,
        }
    with isolated_fixture_candidate("forbidden_surface") as candidate:
        bad_surface = (
            candidate["root"]
            / "phase7"
            / "fixtures"
            / f"forbidden_claim_{candidate['nonce']}.md"
        )
        bad_surface.parent.mkdir(parents=True, exist_ok=True)
        with bad_surface.open("x", encoding="utf-8") as stream:
            stream.write(str(request["fixture_text"]))
        with mock.patch.object(
            common,
            "scan_surface_files",
            return_value=[bad_surface],
        ):
            fixture_final = common.generate_artifacts()
        payload = {
            "status": (
                "PASS"
                if fixture_final.get("status") == "FAIL"
                and fixture_final.get("machine_contract_status") == "FAIL"
                and fixture_final.get("claim_surface_scan_state") == "FAIL"
                and fixture_final.get(
                    "claim_surface_scan_blocked_claim_surface_count",
                    0,
                )
                > 0
                else "FAIL"
            ),
            "writes_performed": True,
            "live_evidence_writes_performed": False,
            "candidate_disposition": "discarded_isolated_fixture",
            "fixture_nonce": candidate["nonce"],
            "request_sha256": request_sha256,
            "fixture_final": {
                "status": fixture_final.get("status"),
                "machine_contract_status": fixture_final.get(
                    "machine_contract_status"
                ),
                "claim_surface_scan_state": fixture_final.get(
                    "claim_surface_scan_state"
                ),
                "claim_surface_scan_blocked_claim_surface_count": (
                    fixture_final.get(
                        "claim_surface_scan_blocked_claim_surface_count"
                    )
                ),
            },
        }
    payload["candidate_discarded"] = True
    return payload


def route_shape_probe_case(case: str) -> dict:
    with isolated_fixture_candidate(f"route_{case}") as candidate:
        route_path = candidate["route_path"]
        if case == "missing":
            route_path.unlink(missing_ok=True)
        else:
            payload = historical_route_payload()
            if case == "malformed":
                payload = {
                    "success": True,
                    "test_count": common.EXPECTED_CURRENT_ROUTE_TEST_COUNT,
                    "closure_enforced": True,
                }
            elif case == "bad_required":
                payload["required_validations"][
                    "required_test_count"
                ] = 1
            route_path.parent.mkdir(parents=True, exist_ok=True)
            route_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        final = None
        if case != "missing":
            final = common.generate_artifacts()
        report, ok = common.validate_all(require_complete=True)
        row = {
            "fixture_nonce": candidate["nonce"],
            "ok": ok,
            "error_codes": sorted(
                {
                    str(error.get("code"))
                    for error in report.get("errors", [])
                    if isinstance(error, dict)
                }
            ),
            "report_status": report.get("status"),
            "relocated_surface_families": {
                "generated_evidence": common.surface_family(
                    candidate["root"]
                    / "phase0"
                    / "owner_reserved_seal_requirements.json"
                ),
                "ledger_packet": common.surface_family(
                    common.LEDGER_PACKET_DOC
                ),
                "policy_doc": common.surface_family(
                    common.CLAIM_BOUNDARY_DOC
                ),
            },
        }
        if isinstance(final, dict):
            row["final"] = {
                "status": final.get("status"),
                "machine_contract_status": final.get(
                    "machine_contract_status"
                ),
                "full_current_route_runner_result_valid": final.get(
                    "full_current_route_runner_result_valid"
                ),
            }
    row["candidate_discarded"] = True
    return row


def route_shape_probe_payload() -> dict:
    cases = {
        case: route_shape_probe_case(case)
        for case in ("missing", "malformed", "bad_required", "valid")
    }
    status = (
        "PASS"
        if cases["missing"]["ok"] is False
        and "full_current_route_validation_missing"
        in cases["missing"]["error_codes"]
        and cases["malformed"]["ok"] is False
        and "full_current_route_runner_shape_invalid"
        in cases["malformed"]["error_codes"]
        and cases["bad_required"]["ok"] is False
        and "full_current_route_runner_shape_invalid"
        in cases["bad_required"]["error_codes"]
        and cases["valid"]["ok"] is True
        and cases["valid"]["relocated_surface_families"]
        == {
            "generated_evidence": "generated_evidence",
            "ledger_packet": "ledger_packets",
            "policy_doc": "docs",
        }
        else "FAIL"
    )
    return {
        "status": status,
        "writes_performed": True,
        "live_evidence_writes_performed": False,
        "candidate_disposition": "discarded_isolated_fixtures",
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 closeout / reentry guard seal.")
    parser.add_argument("--mode", choices=("generate", "validate", "all"), default="all")
    parser.add_argument("--require-complete", action="store_true")
    probes = parser.add_mutually_exclusive_group()
    probes.add_argument("--probe-contract", action="store_true")
    probes.add_argument("--probe-forbidden-surface", action="store_true")
    probes.add_argument("--probe-route-shapes", action="store_true")
    parser.add_argument("--report-json", action="store_true")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    if args.probe_contract:
        payload = contract_probe_payload(read_probe_request())
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1
    if args.probe_forbidden_surface:
        payload = forbidden_surface_probe_payload(read_probe_request())
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1
    if args.probe_route_shapes:
        payload = route_shape_probe_payload()
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if payload["status"] == "PASS" else 1

    if args.mode in {"generate", "all"}:
        final = common.generate_artifacts()
        print(
            json.dumps(
                {
                    "status": final["status"],
                    "machine_contract_status": final["machine_contract_status"],
                    "closeout_state": final["closeout_state"],
                    "canonical_seal_allowed": final["canonical_seal_allowed"],
                },
                sort_keys=True,
            )
        )
        if args.mode == "generate" and (
            final.get("status") != "PASS" or final.get("machine_contract_status") != "PASS"
        ):
            return 1
    if args.mode in {"validate", "all"}:
        report, ok = common.validate_all(
            require_complete=args.require_complete or args.mode == "all",
            write_report=not args.no_write_report,
        )
        output = (
            report
            if args.report_json
            else {
                "status": report["status"],
                "error_count": report["error_count"],
            }
        )
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
