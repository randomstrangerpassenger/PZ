local ok, result = pcall(require, "Iris/UI/Wiki/IrisContextMenu")

if not ok then
    print("[IrisBoot] FAILED to load IrisContextMenu: " .. tostring(result))
else
    print("[IrisBoot] Iris context menu loaded")
end
