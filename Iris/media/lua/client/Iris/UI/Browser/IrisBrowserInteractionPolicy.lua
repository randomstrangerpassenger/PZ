local IrisBrowserInteractionPolicy = {
    SMALL_MAX = 8,
    DENSE_MIN = 9,
    SOURCE_ORDER = {"recipe", "rightclick"},
}

function IrisBrowserInteractionPolicy.density(total)
    if total <= 0 then return "empty" end
    if total == 1 then return "single" end
    if total <= IrisBrowserInteractionPolicy.SMALL_MAX then return "small" end
    return "dense"
end

return IrisBrowserInteractionPolicy
