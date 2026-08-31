-- Pure lexical comparison. Snapshot/lifecycle owners retain all derived state.
local IrisBrowserSearch = {}

local function compact(text)
    return (text:gsub(" ", ""))
end

function IrisBrowserSearch.document(fullType, displayName)
    local name = displayName:lower()
    return {name = name, compactName = compact(name), id = fullType:lower()}
end

function IrisBrowserSearch.query(raw)
    raw = raw or ""
    local name = raw:lower()
    local compactName = compact(name)
    return {
        raw = raw,
        name = name,
        compactName = compactName,
        -- ID punctuation, numbers and internal spaces remain literal.
        id = name:gsub("^ +", ""):gsub(" +$", ""),
        empty = compactName == "",
    }
end

function IrisBrowserSearch.isEmpty(raw)
    return not raw or raw:find("[^ ]") == nil
end

function IrisBrowserSearch.rowLess(a, b)
    if a.displayName ~= b.displayName then return a.displayName < b.displayName end
    return a.fullType < b.fullType
end

function IrisBrowserSearch.relation(document, query, includeId)
    if query.empty then return nil end
    if document.name == query.name then return 1 end
    if document.compactName == query.compactName then return 2 end
    if document.name:find(query.name, 1, true) or
        document.compactName:find(query.compactName, 1, true) then
        return 3
    end
    if includeId and document.id:find(query.id, 1, true) then return 4 end
    return nil
end

function IrisBrowserSearch.canNarrow(previous, query)
    -- Both membership fields must extend monotonically. Raw UTF-8 length
    -- alone cannot establish this for IME replacement or whitespace edits.
    return previous and not previous.empty and not query.empty and
        #query.name > #previous.name and
        query.compactName:sub(1, #previous.compactName) == previous.compactName and
        query.id:sub(1, #previous.id) == previous.id
end

function IrisBrowserSearch.rank(rows, query, includeId)
    local buckets = {{}, {}, {}, {}}
    local candidates = {}
    -- Input stays in original-name/exact-FullType order, including narrowed
    -- candidates. Do not reuse the previous query's relevance order.
    for _, row in ipairs(rows) do
        local tier = IrisBrowserSearch.relation(row.searchDocument, query, includeId)
        if tier then
            candidates[#candidates + 1] = row
            local bucket = buckets[tier]
            bucket[#bucket + 1] = row
        end
    end
    local ranked = {}
    for _, bucket in ipairs(buckets) do
        for _, row in ipairs(bucket) do ranked[#ranked + 1] = row end
    end
    return ranked, candidates
end

return IrisBrowserSearch
