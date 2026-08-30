from __future__ import annotations

from iris_tooling.domains.tooltip_t1.contract import canonical_bytes, sha256_bytes
from iris_tooling.domains.tooltip_t1.models import TooltipContractError

LUA_NAME = "IrisTooltipStaticData.lua"
MANIFEST_NAME = "tooltip_t2_projection_manifest.json"
RUN_RECEIPT = "run_receipt.json"
FINAL_CLOSEOUT = "tooltip_t2_closeout.json"


def lua_string(value: str) -> str:
    try:
        data = value.encode("utf-8")
    except UnicodeError as exc:
        raise TooltipContractError("Lua string cannot be encoded as UTF-8") from exc
    parts = []
    for byte in data:
        if byte == 34:
            parts.append('\\"')
        elif byte == 92:
            parts.append("\\\\")
        elif 32 <= byte <= 126:
            parts.append(chr(byte))
        else:
            parts.append(f"\\{byte:03d}")
    return '"' + "".join(parts) + '"'


def lua_bytes(data: dict) -> bytes:
    output = ["return {"]
    for full_type in sorted(data):
        output.append(f"    [{lua_string(full_type)}] = {{")
        for locale in ("ko", "en"):
            lines = data[full_type][locale]
            if lines:
                output.append(f"        {locale} = {{")
                output.extend(f"            {lua_string(line)}," for line in lines)
                output.append("        },")
            else:
                output.append(f"        {locale} = {{}},")
        output.append("    },")
    output.append("}")
    return ("\n".join(output) + "\n").encode("utf-8")


def artifact_binding(data: bytes) -> dict:
    return {"byte_count": len(data), "sha256": sha256_bytes(data)}


def manifest_bytes(binding: dict, contract_hash: str, contract: dict, lua: bytes,
                   provenance: dict, summary: dict) -> bytes:
    return canonical_bytes({
        "schema_version": "iris-tooltip-t2-projection-manifest-v1",
        "generator_version": contract["generator_version"],
        "projection_contract_sha256": contract_hash,
        "t1_input": binding,
        **summary,
        "lua": {"file_name": LUA_NAME, **artifact_binding(lua)},
        "fulltypes": provenance,
    })
