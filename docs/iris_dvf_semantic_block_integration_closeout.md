# DVF-COMPOSITION-1 Closeout

## Status

**Complete — reusable semantic composition rules, full-corpus result, and Problem 2 reader are available.**

This completes Problem 1 only. It does not claim final KO/EN prose quality, Tooltip/Menu integration, product adoption, package correctness, or in-game behavior.

## Delivered result

- Consumer artifact: `Iris/build/description/composition/blocks.json`
- Consumer reader/producer: `Iris/tooling/src/iris_tooling/domains/layer3/composition_results.py`
- Structure and strict read contract: `composition_model.py`
- Relation and qualifier rules: `composition_rules.py`
- Human contract: `docs/iris_dvf_semantic_block_integration_contract.md`

The result binds adopted r6 input SHA-256 `7dded22fad93b7eeff8debf56205cb9ee84220758d53ecb41396889fb49bd799`. Its current size is 27,555,498 bytes.

## Full application result

| Measure | Result |
| --- | ---: |
| Exact FullType targets | 2,105 |
| Accepted semantic + acquisition facts represented | 29,202 |
| Meaning/acquisition blocks | 10,304 |
| Multi-branch grouped blocks | 1,591 |
| Block-common qualifiers | 9,430 |
| Branch-local qualifiers | 2,285 |
| Undetermined relations | 14 |

Fact disposition is `represented=29,202`, `residual=0`, `non_public=0` for the accepted input fact collections. Audit claims outside those accepted collections were not promoted into public meaning.

Confirmed relation instances are: refinement 1,453, context variant 645, function/result 2,057, compound 4, acquisition alternative 19, and equivalent qualifier 1,374. These counts describe structural applications of the implemented rules; they are not quality scores or a claim of human semantic review for all items.

## Representative meaning review

- `Base.Plank`: `carpentry_menu_construction` is retained as a directed refinement branch of `construction` because both carry exactly the `material` role. Campfire/hearth fuel uses are target variants with separate predicates. Splint application and its factor result are grouped, while splint removal remains an independent operation. Woodworking, furniture, spear, trap, campfire-kit, metal-forging, and watermelon roles remain separately available rather than being collapsed into a primary use.
- `Base.Hammer`: the repair meaning retains `repair_target`; it is not rewritten as a repair `tool`. Shovel smithing refines metal forging only under the same `tool` role. Construction, woodworking, moving, barricade, melee, washing, and acquisition meanings remain independently addressable. Four accepted acquisition routes are alternative branches with their own conditions.
- `Base.Notebook`: viewing, writing, page/title updates, and lock update share one compound note block but remain five branches. Writing/page/title and lock qualifiers retain their exact application refs, so the writing-implement condition is not widened to every note action. Fuel and tinder target variants are separate from note meaning.
- `Base.Molotov`: physics attack remains independent from the washing/blood-removal result block; its attack condition does not migrate to washing or vice versa.
- Shared fuel, tinder, washing, body-washing, and function/effect rules are keyed by accepted semantic values and relation evidence rather than item names, Profiles, or generated prose.

The full-corpus review exposed and fixed a common rule gap during implementation. Directed result relations now come only from reusable, source-grounded function/property/direction mappings. A shared admission rule, qualifier, or scope does not merge meanings; the focused fixture includes a same-rule, same-condition counterexample.

## Remaining uncertainty and consumer impact

Fourteen spear-fishing items contain both accepted `fish_with_spear` and `item_condition/decrease` facts but no accepted application or direction reference between them. They are emitted as `undetermined`. Problem 2 may describe both separately, but must not claim that spear fishing causes the condition loss unless later accepted evidence supplies that direction.

Broad same-rule coincidences—such as prepared-food renaming versus chef attribution, vehicle installation versus running wear, or device headphone controls versus media-code outcomes—are kept separate and are not inflated into unresolved pair inventories.

## Validation

Final required command:

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py -q
```

Result: **PASS**, exit `0`, `1 passed in 15.34s`.

The focused test used one normal adopted load and one full producer result for fact conservation, relation/reference integrity, qualifier scope, actual positive grouping, representative risk cases, durable write, and reader readback. Small in-memory fixtures covered input-order stability, permitted grouping, independent meanings, alternatives, undetermined handling, and an invalid qualifier reference.

No repository-wide suite, historical replay, Run A/B comparator, validation registry/preflight, package/runtime test, adoption/seal, or additional confidence run was performed.

## Validation limit

The machine checks establish complete fact disposition and structural reference/scope integrity, not the human semantic correctness of every relation or the truth of every upstream game fact. Manual review was limited to the planned high-risk rule families and representative Hammer, Notebook, Molotov, and Plank cases. Final prose readability and whole-output quality remain Problem 3 responsibilities; compact/expanded text composition remains Problem 2.
