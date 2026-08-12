"""Bootstrap-only pytest options for the Round 3 route contract.

Selection, denominator enforcement, and receipt generation remain owned by
``Iris/build/description/v2/tests/conftest.py``.  Pytest must know the custom
options before it resolves ``testpaths``, so their registration lives at the
repository root.
"""


def pytest_addoption(parser):
    group = parser.getgroup("round3")
    group.addoption(
        "--round3-contract",
        action="store",
        default="current",
        choices=["all", "current", "diagnostic", "historical"],
        help="Round 3 source contract to collect; default: current.",
    )
    group.addoption(
        "--round3-additional-source",
        action="append",
        default=[],
        help="Exact repository-relative test source selected by a tracked validation contract.",
    )
    group.addoption(
        "--round3-enforce-denominator",
        action="store_true",
        default=False,
        help="Fail closed unless collected source coverage equals the approved denominator.",
    )
    group.addoption(
        "--round3-denominator-receipt",
        action="store",
        default=None,
        help="Optional external path for the collection/execution denominator receipt.",
    )
