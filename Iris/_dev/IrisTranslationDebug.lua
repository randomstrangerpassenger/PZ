--[[
    IrisTranslationDebug.lua

    Manual translation diagnostics extracted from runtime IrisBrowser.lua.
    Keep this outside media/ so release packaging does not load or ship it.
]]

local IrisTranslationDebug = {}

function IrisTranslationDebug.run()
    print("===============================================================")
    print("[IrisBrowser] TRANSLATION SYSTEM DEBUG START")
    print("===============================================================")

    print("[DEBUG] 1. getText function exists: " .. tostring(getText ~= nil))
    print("[DEBUG]    getText type: " .. type(getText))

    print("[DEBUG] 2. Translator object exists: " .. tostring(Translator ~= nil))
    if Translator then
        print("[DEBUG]    Translator type: " .. type(Translator))
        if Translator.getLanguage then
            local ok, lang = pcall(Translator.getLanguage)
            print("[DEBUG]    Translator.getLanguage(): ok=" .. tostring(ok) .. ", lang=" .. tostring(lang))
        end
    end

    print("[DEBUG] 3. getCore() check:")
    if getCore then
        local ok, core = pcall(getCore)
        if ok and core then
            print("[DEBUG]    getCore() exists")
            if core.getOptionCurrentLanguage then
                local ok2, lang = pcall(function() return core:getOptionCurrentLanguage() end)
                print("[DEBUG]    Current language: ok=" .. tostring(ok2) .. ", lang=" .. tostring(lang))
            end
            if core.getOptionLanguage then
                local ok3, lang = pcall(function() return core:getOptionLanguage() end)
                print("[DEBUG]    Option language: ok=" .. tostring(ok3) .. ", lang=" .. tostring(lang))
            end
        else
            print("[DEBUG]    getCore() failed or nil")
        end
    else
        print("[DEBUG]    getCore not available")
    end

    print("[DEBUG] 4. Translation key tests:")
    local testKeys = {
        "Iris_UI_CategoryLabel",
        "Iris_UI_SubcategoryLabel",
        "Iris_Sub_1A",
        "IG_UI_Iris_UI_CategoryLabel",
        "UI_Iris_CategoryLabel",
    }

    for _, key in ipairs(testKeys) do
        if getText then
            local ok, result = pcall(getText, key)
            local status = "MISS"
            if ok and result and result ~= key then
                status = "HIT"
            end
            print("[DEBUG]    getText('" .. key .. "'): status=" .. status .. ", ok=" .. tostring(ok) .. ", result='" .. tostring(result) .. "'")
        end
    end

    print("[DEBUG] 5. Built-in PZ translation test:")
    local builtinKeys = {"UI_Yes", "UI_No", "UI_Ok", "UI_Cancel"}
    for _, key in ipairs(builtinKeys) do
        if getText then
            local ok, result = pcall(getText, key)
            print("[DEBUG]    getText('" .. key .. "'): ok=" .. tostring(ok) .. ", result='" .. tostring(result) .. "'")
        end
    end

    print("===============================================================")
    print("[IrisBrowser] TRANSLATION SYSTEM DEBUG END")
    print("===============================================================")
end

return IrisTranslationDebug
