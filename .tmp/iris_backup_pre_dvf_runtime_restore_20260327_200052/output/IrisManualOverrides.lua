-- Iris Manual Overrides
-- ONLY for subcategories that cannot be auto-classified
-- Schema: v1.0.0
--
-- Allowed manual override tags (자동 분류 불가):
--   Combat.2-B
--   Combat.2-D
--   Combat.2-J
--   Combat.2-K
--   Combat.2-L
--   Consumable.3-C
--   Consumable.3-E
--   Literature.5-B
--   Literature.5-C
--   Literature.5-D
--   Resource.4-F
--   Tool.1-D
--   Tool.1-J
--   Wearable.6-F

IrisData = IrisData or {}

IrisData.ManualOverrides = {
    -- Example:
    -- ["Base.Generator"] = { "Tool.1-J" },
}
