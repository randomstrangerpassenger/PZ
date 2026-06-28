--[[
    IrisRequirementPolicy.lua

    Browser requirement display policy.
]]

local IrisRequirementPolicy = {}

local ProtectedCall = require("Iris/Util/IrisProtectedCall")

IrisRequirementPolicy.COLOR_MET     = {r=0.5, g=0.85, b=0.5, a=0.9}
IrisRequirementPolicy.COLOR_UNMET   = {r=0.85, g=0.4, b=0.4, a=0.9}
IrisRequirementPolicy.COLOR_UNKNOWN = {r=0.6, g=0.6, b=0.6, a=0.8}

local CHECK_HANDLERS = {
    perk = function(check, player)
        local perkObj = (Perks.FromString and Perks.FromString(check.perk_id))
                        or Perks[check.perk_id]
        if not perkObj then return nil end
        return player:getPerkLevel(perkObj) >= check.level
    end,

    flag = function(check, player)
        if check.flag_id == "NeedToBeLearn" then
            return player:isRecipeKnown(check.recipe_name)
        end
        return nil
    end,

    near_item = function(check, player)
        return nil
    end,
}

function IrisRequirementPolicy.evalColor(check, player)
    if not check or not check.type then
        return IrisRequirementPolicy.COLOR_UNKNOWN
    end
    local handler = CHECK_HANDLERS[check.type]
    if not handler then
        return IrisRequirementPolicy.COLOR_UNKNOWN
    end
    local ok, result = ProtectedCall.engine(handler, check, player)
    if not ok or result == nil then
        return IrisRequirementPolicy.COLOR_UNKNOWN
    end
    return result and IrisRequirementPolicy.COLOR_MET or IrisRequirementPolicy.COLOR_UNMET
end

function IrisRequirementPolicy.displayText(req, color, tr)
    local reqDisplay = req.display or "?"
    local check = req.check
    if check and check.type == "flag"
        and check.flag_id == "NeedToBeLearn"
        and color == IrisRequirementPolicy.COLOR_MET then
        return tr("Iris_Requirement_Learned", "Learned")
    end
    return reqDisplay
end

return IrisRequirementPolicy
