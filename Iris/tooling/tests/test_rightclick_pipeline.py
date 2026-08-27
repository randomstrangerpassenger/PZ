from __future__ import annotations

import importlib.util

import pytest

from iris_tooling.domains.rightclick import pipeline_v24
from iris_tooling.domains.rightclick.infra import StageRunner
from iris_tooling.execution import (
    ArtifactRef,
    CanonicalSemanticResult,
    ExecutionEnvelope,
    Issue,
    MachineResult,
    PhaseInput,
    PhaseRunner,
    ResultContractError,
    Severity,
    TerminalStatus,
    decode_legacy_result,
    emit_machine_result,
    encode_legacy_result,
    terminal_exit_code,
)


def test_noncurrent_capability_module_is_not_packaged() -> None:
    assert (
        importlib.util.find_spec("iris_tooling.domains.rightclick.capability")
        is None
    )


def test_fulltype_parser_preserves_unqualified_type() -> None:
    assert pipeline_v24.parse_fulltype_item_type("Base.Hammer") == "Hammer"
    assert pipeline_v24.parse_fulltype_item_type("Hammer") == "Hammer"


def test_semicolon_list_is_normalized() -> None:
    assert pipeline_v24.parse_semicolon_list(" Tool ;WaterSource;; Tool ") == {
        "Tool",
        "WaterSource",
    }
    assert pipeline_v24.parse_semicolon_list(None) == set()


def test_truthy_contract_is_explicit() -> None:
    for value in (True, "true", "TRUE", "1", 1):
        assert pipeline_v24.is_truthy(value)
    for value in (False, "True", "yes", 0, None):
        assert not pipeline_v24.is_truthy(value)


def test_anchor_slug_is_stable() -> None:
    assert (
        pipeline_v24.normalize_slug(
            "lua/client/ISUI/ISWorldObjectContextMenu.lua::onAddFuel"
        )
        == "lua_client_isui_isworldobjectcontextmenu_onaddfuel"
    )


def test_canonical_hash_ignores_mapping_order(capsys: pytest.CaptureFixture[str]) -> None:
    assert pipeline_v24.compute_sha256({"a": 1, "b": 2}) == (
        pipeline_v24.compute_sha256({"b": 2, "a": 1})
    )

    artifact = ArtifactRef("report", "external/report.json", "a" * 64)
    issue = Issue("sample", "concrete", "compile", Severity.ERROR, "sample:1")
    result = CanonicalSemanticResult(
        discriminator="iris.build.sample.v1",
        status=TerminalStatus.FAIL,
        payload={"b": 2, "a": 1},
        issues=(issue,),
        artifacts=(artifact,),
    )
    decoded = CanonicalSemanticResult.from_dict(
        result.to_dict(), expected_discriminator="iris.build.sample.v1"
    )
    assert decoded == result
    assert decoded.canonical_bytes() == result.canonical_bytes()
    assert decoded.sha256() == result.sha256()
    with pytest.raises(ResultContractError, match="unsupported canonical result schema"):
        CanonicalSemanticResult.from_dict(
            {**result.to_dict(), "schema_version": "unknown"},
            expected_discriminator="iris.build.sample.v1",
        )
    with pytest.raises(ResultContractError, match="unsupported.*discriminator"):
        CanonicalSemanticResult.from_dict(
            result.to_dict(), expected_discriminator="iris.build.other.v1"
        )

    legacy = {"status": "PASS", "value": 7}
    assert encode_legacy_result(
        decode_legacy_result(legacy, discriminator="iris.build.legacy.v1")
    ) == legacy
    envelope = ExecutionEnvelope(
        run_id="volatile-run",
        elapsed_seconds=1.5,
        observed_at="volatile-time",
        process={"pid": 1},
        environment={"cwd": "volatile"},
        canonical_result_sha256=result.sha256(),
        canonical_result_locator="external/canonical.json",
    )
    assert "run_id" not in result.to_dict()
    assert envelope.to_dict()["run_id"] == "volatile-run"

    runner = PhaseRunner()
    assert issubclass(StageRunner, PhaseRunner)
    blocked = runner.run_phase(
        PhaseInput("blocked", 0, dependencies=("missing",)), lambda value: value
    )
    assert blocked.status is TerminalStatus.BLOCKED
    produced = runner.run_phase(
        PhaseInput("produce", 3, reuse_key="immutable:3"), lambda value: value + 1
    )
    reused = runner.run_phase(
        PhaseInput("reuse", 99, dependencies=("produce",), reuse_key="immutable:3"),
        lambda value: value + 1,
    )
    failed = runner.run_phase(
        PhaseInput("exception", None, dependencies=("produce",)),
        lambda _: (_ for _ in ()).throw(RuntimeError("specific failure")),
    )
    assert produced.payload == reused.payload == 4
    assert reused.reused is True
    assert failed.issues[0].message == "specific failure"
    assert terminal_exit_code(failed.status) == 2

    emit_machine_result(
        MachineResult(
            exit_code=1,
            canonical_result_sha256=result.sha256(),
            canonical_result_locator="external/canonical.json",
            execution_envelope_locator="external/envelope.json",
        ),
        diagnostic="human diagnostic",
    )
    captured = capsys.readouterr()
    assert '"schema_version":"iris-tooling-machine-result-v1"' in captured.out
    assert captured.err == "human diagnostic\n"


def test_proof_merge_fails_closed_on_boolean_conflict() -> None:
    logger = pipeline_v24.PipelineLogger()

    merged, conflicted = pipeline_v24.merge_prove_value(
        True,
        False,
        "persistent_change",
        "Base.Hammer",
        logger,
    )

    assert merged is None
    assert conflicted is True
    assert logger.has_fails()


def test_item_matchers_cover_current_v24_types() -> None:
    item = {
        "Tags": "Tool;CanOpener",
        "Categories": "Survival;Cooking",
        "DisplayCategory": "Tool",
        "Type": "Normal",
        "CanStoreWater": "true",
    }

    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "type", "value": "TinOpener"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "tag", "value": "CanOpener"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "property", "value": "CanStoreWater"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "category", "value": "Cooking"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "display_category", "value": "Tool"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "script_type", "value": "Normal"})
    assert not pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "unsupported", "value": "Normal"})


def test_property_based_reviews_are_routed_deterministically() -> None:
    decisions = {
        "Base.Zed": {
            "decision": "PASS",
            "review_reason": "",
            "rule_ids": ["pass"],
        },
        "Base.Bucket": {
            "decision": "REVIEW",
            "review_reason": "property_based exclusion (auto conclusion forbidden)",
            "rule_ids": ["water"],
        },
    }

    assert pipeline_v24.collect_property_based_items(decisions) == {
        "Base.Bucket": {
            "fulltype": "Base.Bucket",
            "rule_ids": ["water"],
            "review_reason": "property_based exclusion (auto conclusion forbidden)",
        }
    }
