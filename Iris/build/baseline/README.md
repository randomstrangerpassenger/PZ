# Iris Baseline

P0.6 baseline artifacts for `iris_refactor_roadmap_v2.0.md`.

## Layout

| Path | Tracking | Purpose |
|---|---|---|
| `capability_by_fulltype.json` | tracked | Moved legacy capability baseline from `Iris/baseline/`. |
| `golden/` | tracked | Reviewable golden subset and marker checklist. |
| `full/` | ignored | Full static proxy dumps for local comparison only. |

## Current Capture Status

The golden subset is a static proxy capture, not a live PZ runtime capture.

Captured:

- `getTags()` / `getTagsForItem()` from `IrisClassifications.lua`
- `getDescriptionBlocks()` proxy from current TagParser/Ordering/Templates/Renderer behavior
- recipe connection proxy from `Iris/output/recipe_index.v2.4.json`
- current `Iris/build/description/v2/output/dvf_3_3_rendered.json`

Pending before P0.7:

- one actual PZ run using `golden/runtime_marker_checklist.md`
- actual Moveables/Fixing build result capture from game runtime
