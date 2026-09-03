-- QG-only Layer 4 collection. Legacy capability and recipe-index synthesis are
-- intentionally absent; the status-bearing ViewModel projection is the input.
local Projection = require("Iris/UI/Browser/IrisBrowserInteractionProjection")

local IrisBrowserInteractionCollector = {}

function IrisBrowserInteractionCollector.collect(interactionState, evolvedRecipeState, locale, tr)
    return Projection.build(interactionState, evolvedRecipeState, locale, tr)
end

return IrisBrowserInteractionCollector
