--[[
    IrisWikiUnitProfiles.lua

    Pure formatting profiles for values whose current Wiki surfaces use
    different units. Profiles preserve the existing output and do not infer or
    normalize Project Zomboid runtime meaning.
]]

local IrisWikiUnitProfiles = {}
local Presentation = require("Iris/UI/Detail/IrisItemDetailPresentation")

function IrisWikiUnitProfiles.formatSigned(value, profileName)
    return Presentation.formatSigned(value, profileName)
end

function IrisWikiUnitProfiles.getProfile(profileName)
    return Presentation.getProfile(profileName)
end

return IrisWikiUnitProfiles
