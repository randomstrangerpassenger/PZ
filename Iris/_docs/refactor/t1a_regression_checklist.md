# T1-A Regression Checklist - Fallback Resolver

Scope: Browser/Wiki Korean display regression checks for shared translation fallback resolver changes.

## Browser Surface

- Browser title panel opens without Lua errors.
- Top-level column labels render Korean when KO language data is active:
  - `Iris_UI_CategoryLabel`
  - `Iris_UI_SubcategoryLabel`
  - `Iris_UI_ItemLabel`
  - `Iris_UI_DetailLabel`
- Category labels use translated display text instead of raw category IDs where translations exist.
- Subcategory labels use translated display text instead of raw subcategory codes where translations exist.
- Search boxes remain usable and do not replace typed text with translation keys.
- Detail panel fallback keeps readable fallback text when a translation key is missing.

## Wiki / Context Menu Surface

- Inventory context menu entry renders Korean for `Iris_Menu_ViewMore` when KO language data is active.
- Basic detail labels render translated text:
  - `Iris_Detail_Weight`
  - `Iris_Detail_Type`
  - `Iris_Detail_Module`
  - `Iris_Detail_Tags`
- Food / consumable detail labels render translated text:
  - `Iris_Detail_Hunger`
  - `Iris_Detail_Thirst`
  - `Iris_Detail_Stress`
  - `Iris_Detail_Boredom`
  - `Iris_Detail_Calories`
- Weapon / tool detail labels render translated text:
  - `Iris_Detail_Damage`
  - `Iris_Detail_Range`
  - `Iris_Detail_Critical`
  - `Iris_Detail_Durability`
- Connection labels render translated text:
  - `Iris_Detail_Recipe`
  - `Iris_Detail_Furniture`
  - `Iris_Detail_Fixer`
- Meta labels render translated text:
  - `Iris_Detail_ClassificationID`
  - `Iris_Detail_Module`

## Static Acceptance

- `IrisBrowser.lua`, `IrisBrowserData.lua`, `IrisWikiSections.lua`, and `IrisContextMenu.lua` do not each carry their own duplicated translation loader fallback implementation.
- Missing translation fallback remains caller-controlled: fallback text wins over raw key when provided.
- PZ `getText()` fallback remains protected by `IrisProtectedCall.engine`.

## Validation Ceiling

- Validated by this checklist: static review targets and manual KO display targets.
- Not validated by this checklist alone: in-game KO runtime pass.
