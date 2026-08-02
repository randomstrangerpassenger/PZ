--[[
    IrisWikiUnitProfiles.lua

    Pure formatting profiles for values whose current Wiki surfaces use
    different units. Profiles preserve the existing output and do not infer or
    normalize Project Zomboid runtime meaning.
]]

local IrisWikiUnitProfiles = {}

local PROFILES = {
    raw = {
        multiplier = 1,
        format_string = "%.0f",
    },
    percent_scaled = {
        multiplier = 100,
        format_string = "%.0f",
    },
}

function IrisWikiUnitProfiles.formatSigned(value, profileName)
    local profile = assert(PROFILES[profileName], "unknown Wiki unit profile: " .. tostring(profileName))
    local sign = value < 0 and "" or "+"
    return sign .. string.format(profile.format_string, value * profile.multiplier)
end

function IrisWikiUnitProfiles.getProfile(profileName)
    local profile = assert(PROFILES[profileName], "unknown Wiki unit profile: " .. tostring(profileName))
    return {
        multiplier = profile.multiplier,
        format_string = profile.format_string,
    }
end

return IrisWikiUnitProfiles
