from pathlib import Path
import re

import pytest

from iris_tooling.domains.tooltip_t1.models import TooltipContractError
from iris_tooling.domains.tooltip_static_data_projection.contract import check_surface, decode_object, load_contract
from iris_tooling.domains.tooltip_static_data_projection.serialization import lua_string


@pytest.mark.parametrize("case", ["roundtrip_allowed", "encoding", "logical_line", "forbidden"])
def test_serialization_guard(case):
    contract, _ = load_contract(Path(__file__).resolve().parents[3])
    if case == "encoding":
        with pytest.raises(TooltipContractError):
            decode_object(b'{"text":"\xff"}\n', "fixture")
    elif case == "logical_line":
        with pytest.raises(TooltipContractError):
            check_surface(" \t ", "ko", contract, "Base.X/S2/ko")
    elif case == "forbidden":
        with pytest.raises(TooltipContractError, match="Base.X/S2/en.*useful"):
            check_surface("A USEFUL tool.", "en", contract, "Base.X/S2/en")
    else:
        value = '한국어 "quote" \\ path\x00\x07\b\t\v\f\x1f9 usefulness inefficient betterment'
        check_surface(value, "en", contract, "Base.X/S2/en")
        encoded = lua_string(value)
        # Deliberately test-local, not a production parser or validation authority.
        tokens = re.findall(r'\\[0-9]{3}|\\["\\]|[^\\]', encoded[1:-1])
        decoded = bytearray()
        for token in tokens:
            if token.startswith("\\"):
                decoded.append(int(token[1:]) if token[1:].isdigit() else ord(token[1]))
            else:
                decoded.extend(token.encode("ascii"))
        assert decoded.decode("utf-8") == value
