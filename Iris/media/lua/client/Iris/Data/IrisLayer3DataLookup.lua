-- Internal demand lookup. The complete IrisLayer3DataChunks facade remains public.

local safeRequire = require("Iris/Util/IrisRequire").safeRequire
local RuntimeLookupDiagnostics = require("Iris/Data/IrisRuntimeLookupDiagnostics")
local currentOk, current = safeRequire("Iris/Data/IrisLayer3DataCurrent")
local productPointerOk, productPointer = safeRequire("Iris/Data/IrisLayer3ProductCurrent")
-- A missing optional module may return nil without throwing. A successful
-- protected call alone does not mean that a product pointer exists.
if productPointerOk and productPointer ~= nil and (type(current) ~= "table" or current.schema_version ~= "iris_layer3_product_compat_v1") then
    currentOk = false
end

-- Successor products use one session snapshot for both Menu locales. The
-- legacy router below retains its exact schema and module-name restrictions.
if not currentOk or (type(current) == "table" and current.schema_version == "iris_layer3_product_compat_v1") then
    return require("Iris/Data/IrisLayer3ProductLookup").create(currentOk, current, safeRequire)
end
return require("Iris/Data/IrisLayer3LegacyLookup").create(currentOk, current, safeRequire, RuntimeLookupDiagnostics)
