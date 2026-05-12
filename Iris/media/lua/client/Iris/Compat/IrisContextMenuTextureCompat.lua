--[[
    IrisContextMenuTextureCompat.lua - defensive context menu texture guard

    Some context-menu providers assign the result of getTexture() directly to
    ISContextMenu.tickTexture. If getTexture() returns the engine null object,
    vanilla ISContextMenu:render() calls getWidthOrig() on null every frame.
]]

local IrisContextMenuTextureCompat = {}

local Logger = require("Iris/Util/IrisLogger")

local fallbackTickTexture = nil
local warnedInvalidTexture = false

local function isTextureUsable(texture)
    if not texture then
        return false
    end

    local ok = pcall(function()
        texture:getWidthOrig()
        texture:getHeightOrig()
    end)
    return ok
end

local function getFallbackTickTexture()
    if isTextureUsable(fallbackTickTexture) then
        return fallbackTickTexture
    end

    fallbackTickTexture = getTexture("Quest_Succeed")
    if isTextureUsable(fallbackTickTexture) then
        return fallbackTickTexture
    end

    return nil
end

local function sanitizeTickTexture(context)
    if not context or isTextureUsable(context.tickTexture) then
        return
    end

    local fallback = getFallbackTickTexture()
    if not fallback then
        return
    end

    context.tickTexture = fallback
    if not warnedInvalidTexture then
        Logger.warn("Replaced invalid ISContextMenu.tickTexture with vanilla fallback")
        warnedInvalidTexture = true
    end
end

function IrisContextMenuTextureCompat.install()
    if not ISContextMenu or ISContextMenu._irisTickTextureCompatApplied then
        return true
    end

    if type(ISContextMenu.render) ~= "function" then
        return false
    end

    local originalRender = ISContextMenu.render
    ISContextMenu._irisTickTextureCompatApplied = true
    ISContextMenu._irisOriginalRender = ISContextMenu._irisOriginalRender or originalRender

    ISContextMenu.render = function(self, ...)
        sanitizeTickTexture(self)
        return originalRender(self, ...)
    end

    return true
end

return IrisContextMenuTextureCompat
