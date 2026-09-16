-- Product lookup owns one session snapshot and never falls back to legacy data.
local Lookup = {}

function Lookup.create(currentOk, current, safeRequire)
    local Product = { isProduct = true }
    local cache, records = {}, nil
    local reason = "product_pointer_invalid"
    local productId = currentOk and current.product_id or nil
    local prefix = type(productId) == "string" and
        ("Iris/Data/IrisLayer3ProductGenerations/" .. productId .. "/") or nil
    local function dense(values)
        if type(values) ~= "table" then return false end
        local count = 0
        for key in pairs(values) do
            if type(key) ~= "number" or key < 1 or key ~= math.floor(key) then return false end
            count = count + 1
        end
        return count == #values
    end
    local function validTargetGroups(unit)
        local detail = unit.target_groups
        if detail == nil then return true end
        if type(detail) ~= "table" or type(detail.introduction) ~= "string" or
            not dense(detail.groups) or #detail.groups == 0 or detail.group_count ~= #detail.groups then return false end
        local lines, names, ids, keys = {}, {}, {}, {}
        for line in unit.text:gmatch("[^\n]+") do lines[#lines + 1] = line end
        if lines[1] ~= detail.introduction then return false end
        for i = 2, #lines do
            if lines[i]:sub(1, 2) ~= "- " then return false end
            local name = lines[i]:sub(3)
            if names[name] then return false end
            names[name] = true
        end
        local count, identityField = 0, nil
        for _, group in ipairs(detail.groups) do
            if type(group) ~= "table" or type(group.key) ~= "string" or group.key == "" or keys[group.key] or
                type(group.label) ~= "string" or group.label == "" or not dense(group.entries) or
                #group.entries == 0 or group.count ~= #group.entries then return false end
            if group.scope ~= nil and group.scope ~= "mapped" and group.scope ~= "some" then return false end
            if group.presentation ~= nil and group.presentation ~= "inline" and group.presentation ~= "disclosure" then return false end
            keys[group.key] = true
            for _, entry in ipairs(group.entries) do
                if type(entry) ~= "table" or type(entry.label) ~= "string" or not names[entry.label] then return false end
                local sourceIds, identityCount = nil, 0
                for _, field in ipairs({"item_ids", "recipe_keys", "target_keys"}) do
                    if entry[field] ~= nil then
                        if identityField and identityField ~= field then return false end
                        identityField = field
                        sourceIds = entry[field]
                        identityCount = identityCount + 1
                    end
                end
                if identityCount ~= 1 or not dense(sourceIds) or #sourceIds == 0 then return false end
                names[entry.label] = nil
                count = count + 1
                for _, id in ipairs(sourceIds) do
                    if type(id) ~= "string" or id == "" or ids[id] then return false end
                    ids[id] = true
                end
            end
        end
        return count == #lines - 1
    end
    local function validId(value)
        return type(value) == "string" and #value == 68 and value:match("^l3p%-[0-9a-f]+$") ~= nil
    end
    if validId(productId) and current.index_module == prefix .. "Index" then
        local ok, loaded = safeRequire(current.index_module)
        if ok and type(loaded) == "table" and loaded.schema_version == "iris_layer3_product_index_v1" and
            loaded.product_id == productId and type(loaded.chunks) == "table" then
            local count, previous, valid = 0, nil, true
            for ordinal, record in ipairs(loaded.chunks) do
                if type(record) ~= "table" or type(record.first) ~= "string" or type(record.last) ~= "string" or
                    record.first > record.last or (previous and record.first <= previous) or
                    record.module ~= prefix .. string.format("Chunks/Chunk%03d", ordinal) or
                    type(record.count) ~= "number" or record.count < 1 or record.count ~= math.floor(record.count) or
                    type(record.sha256) ~= "string" or #record.sha256 ~= 64 or
                    record.sha256:match("^[0-9a-f]+$") == nil then
                    valid = false
                    break
                end
                previous, count = record.last, count + record.count
            end
            if valid and count == 2105 and count == loaded.entry_count then records, reason = loaded.chunks, nil end
        end
    end
    local function validEntry(key, entry)
        if type(entry) ~= "table" or entry.item_id ~= key or entry.product_id ~= productId or
            type(entry.locales) ~= "table" then return false end
        for _, locale in ipairs({"ko", "en"}) do
            local value = entry.locales[locale]
            if type(value) ~= "table" or type(value.text) ~= "string" or type(value.blocks) ~= "table" then return false end
            local count = 0
            for position, text in pairs(value.blocks) do
                if type(position) ~= "number" or position < 1 or position ~= math.floor(position) or
                    type(text) ~= "string" or text == "" then return false end
                count = count + 1
            end
            if count ~= #value.blocks then return false end
            if current.display_schema == "iris_expanded_display_v1" then
                if value.schema_version ~= current.display_schema or type(value.units) ~= "table" or
                    type(value.reason) ~= "string" or (value.state ~= "present" and value.state ~= "absent") or
                    (value.state == "present") ~= (value.text ~= "") then return false end
                if value.state == "absent" and (value.reason == "" or #value.units ~= 0) then return false end
                local position, unitCount = 1, 0
                for ordinal, unit in pairs(value.units) do
                    if type(ordinal) ~= "number" or ordinal < 1 or ordinal ~= math.floor(ordinal) then return false end
                    unitCount = unitCount + 1
                end
                if unitCount ~= #value.units then return false end
                local unitTexts = {}
                for _, unit in ipairs(value.units) do
                    if type(unit) ~= "table" or unit.first_segment ~= position or
                        type(unit.last_segment) ~= "number" or unit.last_segment ~= math.floor(unit.last_segment) or
                        unit.last_segment < position or unit.last_segment > count or type(unit.text) ~= "string" then return false end
                    local texts = {}
                    for i = position, unit.last_segment do texts[#texts + 1] = value.blocks[i] end
                    if table.concat(texts, " ") ~= unit.text then return false end
                    if not validTargetGroups(unit) then return false end
                    unitTexts[#unitTexts + 1] = unit.text
                    position = unit.last_segment + 1
                end
                if position ~= count + 1 then return false end
                if table.concat(unitTexts, "\n") ~= value.text then return false end
            elseif table.concat(value.blocks, "\n") ~= value.text then
                return false
            end
        end
        return true
    end
    function Product.get(fullType)
        if type(fullType) ~= "string" or fullType == "" then return nil, "lookup_miss" end
        if not records then return nil, reason end
        local low, high = 1, #records
        while low <= high do
            local middle = math.floor((low + high) / 2)
            local record = records[middle]
            if fullType < record.first then high = middle - 1
            elseif fullType > record.last then low = middle + 1
            else
                local chunk = cache[record.module]
                if not chunk then
                    local ok, loaded = safeRequire(record.module)
                    if not ok or type(loaded) ~= "table" then return nil, "product_chunk_unavailable" end
                    local count, first, last = 0, nil, nil
                    for key, entry in pairs(loaded) do
                        if type(key) ~= "string" or not validEntry(key, entry) then return nil, "product_chunk_invalid" end
                        count = count + 1
                        if not first or key < first then first = key end
                        if not last or key > last then last = key end
                    end
                    if count ~= record.count or first ~= record.first or last ~= record.last then return nil, "product_chunk_invalid" end
                    chunk, cache[record.module] = loaded, loaded
                end
                if not chunk[fullType] then return nil, "lookup_miss" end
                return chunk[fullType], nil
            end
        end
        return nil, "lookup_miss"
    end
    function Product.getLocale(fullType, locale)
        if locale ~= "ko" and locale ~= "en" then return nil, "locale_invalid" end
        local entry, failure = Product.get(fullType)
        return entry and entry.locales[locale] or nil, failure
    end
    function Product.getDiagnostics()
        local modules = {}
        for name, _ in pairs(cache) do modules[#modules + 1] = name end
        table.sort(modules)
        return { indexValid = records ~= nil, productId = productId, loadedChunkCount = #modules, loadedChunkModules = modules }
    end
    function Product.reset() cache = {} end
    return Product
end

return Lookup
