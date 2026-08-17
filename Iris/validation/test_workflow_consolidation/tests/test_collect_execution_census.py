from __future__ import annotations

import ast

from Iris.validation.test_workflow_consolidation.collect_execution_census import classify, function_rows


def test_function_rows_preserve_class_node_identity() -> None:
    tree = ast.parse("class SampleTest:\n    def test_case(self):\n        pass\n")
    assert [node_id for node_id, _ in function_rows("test_sample.py", tree)] == [
        "test_sample.py::SampleTest::test_case"
    ]


def test_mutating_failure_contract_is_must_isolate() -> None:
    function = ast.parse("def test_rollback():\n    pass\n").body[0]
    assert classify("source.py::test_rollback", "source.py", function)[0] == "must_isolate"
