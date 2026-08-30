import json

import pytest

from iris_tooling.domains.tooltip_static_data_projection import cli
from iris_tooling.domains.tooltip_t1.contract import canonical_bytes
from iris_tooling.domains.tooltip_t1.models import TooltipContractError
from iris_tooling.domains.tooltip_static_data_projection.serialization import LUA_NAME, MANIFEST_NAME, RUN_RECEIPT, FINAL_CLOSEOUT
from test_tooltip_t2_projection import fixture_handoff


@pytest.mark.parametrize("case", ["success", "internal", "nonempty", "failure_atomicity", "tamper", "subject"])
def test_cli_finalization(tmp_path, monkeypatch, case):
    repo, handoff, _, _, _ = fixture_handoff(tmp_path)
    a, b, final = (tmp_path / name for name in ("a", "b", "final"))
    if case == "internal":
        with pytest.raises(TooltipContractError, match="repository-external"):
            cli.build(repo, handoff, repo / "output")
        return
    if case == "nonempty":
        a.mkdir()
        (a / "keep").write_text("keep")
        with pytest.raises(TooltipContractError, match="empty"):
            cli.build(repo, handoff, a)
        assert (a / "keep").read_text() == "keep"
        return
    if case == "failure_atomicity":
        def fail(*args):
            raise TooltipContractError("projection defect")
        monkeypatch.setattr(cli, "project", fail)
        with pytest.raises(TooltipContractError, match="projection defect"):
            cli.build(repo, handoff, a)
        assert not a.exists()
        return
    first = cli.build(repo, handoff, a)
    cli.build(repo, handoff, b)
    if case == "tamper":
        with (b / LUA_NAME).open("ab") as stream:
            stream.write(b"--tampered\n")
    elif case == "subject":
        receipt = json.loads((b / RUN_RECEIPT).read_bytes())
        receipt["implementation"]["subject"]["commit"] = "0" * 40
        (b / RUN_RECEIPT).write_bytes(canonical_bytes(receipt))
    if case != "success":
        with pytest.raises(TooltipContractError):
            cli.finalize(repo, a, b, final)
        assert not (final / FINAL_CLOSEOUT).exists()
        return
    monkeypatch.setattr(cli, "require_repository_context", lambda: type("Context", (), {"repository_root": repo})())
    assert cli.main(["finalize", "--run-a-root", str(a), "--run-b-root", str(b), "--output-root", str(final)]) == 0
    closeout = json.loads((final / FINAL_CLOSEOUT).read_bytes())
    assert closeout["state"] == "partial"
    assert closeout["unvalidated_but_in_scope"]
    assert closeout["artifacts"] == first["artifacts"]
    assert {path.name for path in final.iterdir()} == {LUA_NAME, MANIFEST_NAME, FINAL_CLOSEOUT}
    assert (final / LUA_NAME).read_bytes() == (a / LUA_NAME).read_bytes() == (b / LUA_NAME).read_bytes()
