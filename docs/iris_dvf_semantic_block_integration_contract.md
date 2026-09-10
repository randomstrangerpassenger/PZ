# DVF Semantic Composition Contract

## 1. Purpose and authority boundary

This contract defines the locale-neutral meaning structure produced from the adopted r6 Layer 3 facts for `DVF-COMPOSITION-1`. It is an Iris offline composition input for the Problem 2 text composer. It does not replace r6 semantic or acquisition truth, change the current product route, or define a Tooltip/Menu layout.

The input is `Iris/_docs/authority/dvf/layer3_expression/successors/r6/adoption.json` at SHA-256 `7dded22fad93b7eeff8debf56205cb9ee84220758d53ecb41396889fb49bd799`. The normal `recovery.load_adopted` path supplies the bound semantic and acquisition payloads.

## 2. Decision order

Composition applies the following rules in order. Generated KO/EN prose, Profile names, input array order, and item names are never relation evidence.

1. Preserve each accepted fact's item, kind, payload, provenance, explicit context reference, and qualifier application refs.
2. Reject an inferred merge when role, target, result, or context direction conflicts. A `repair_target` is not a `tool`; a condition attached to writing does not become a lock condition.
3. Bind a `context_role` to the `use_context` named by its explicit `context_fact_ref`. The role is a directed refinement of that context.
4. Treat a function-to-effect direction as a result relation only when that exact function/property/direction correspondence is recorded in the reusable source-rule mapping. The mapping covers the established washing, drinking, crop watering/treatment, burn cleaning, reading multiplier, floor-glass, medical, drying, fertilizing, furnace-bellows, smoking, splint, and body-washing correspondences. A shared admission rule, qualifier, or scope is never sufficient by itself.
5. Apply only reusable relation overlays grounded in the accepted r6 source/admission definitions:
   - the `campfire_fuel` and `heat_controls` admissions establish fuel or tinder supply to distinct campfire, hearth/furnace, and drum targets; these keep each target and its own predicate as a context-variant branch;
   - `carpentry_menu_construction` facts come from the building-object/build-action consumer path while `construction` comes from the build-util/inventory construction path. A child-to-parent refinement is permitted only when both contexts carry exactly the same explicit role set; an additional role keeps the branch independent;
   - `smithing_parts` and `shovel_smithing` use the accepted craft-action recipe path under the broader `metal_forging` use and refine it only under the same exact-role rule;
   - the `washing_target` admission explicitly supplies both washing and blood-removal facts, so they are a directed function/result compound;
   - body washing and its accepted `washed_surface_blood` removal effect follow the same function/result rule;
   - accepted splint application and its `splint_factor` result are a directed compound; splint removal remains a separate operation;
   - note viewing, writing, page/title effects, and lock effect form a compound note meaning while remaining separate branches with their own conditions.
6. Keep all other anchors in separate blocks. The accepted spear-fishing function and item-condition decrease effect are a real relation candidate, but r6 contains no application/direction reference between them, so they remain one `undetermined` block pair. Same-rule pairs do not create unresolved questions by themselves.
7. Keep acquisition outside semantic function blocks. Multiple accepted acquisition facts are alternative obtainable routes; each retains its route, conditions, and provenance.

The overlay sets are keyed by semantic function/context values, not FullType. They therefore apply to every item carrying the same accepted meaning and are not per-item exceptions. Adding a new overlay requires evidence for its role/target/result relation; naming similarity is insufficient.

## 3. Qualifier ownership

Conditions and constraints are item-level qualifier records. Exact equal qualifier payloads are represented once while all original qualifier fact refs, provenance refs, and `applies_to_fact_refs` remain present.

- `block_common`: the qualifier's exact application refs reach every branch of one block.
- `branch_local`: the qualifier applies to fewer branches or crosses independently retained blocks. It must be expressed only with those referenced branches.
- `scope_unresolved`: reserved for an input whose target cannot be resolved. A valid adopted r6 input does not produce this state because r6 already validates qualifier targets; it must not be synthesized to hide a rule gap.

Qualifier sharing does not merge blocks. Problem 2 may omit repeated wording when it can preserve the exact scope, but it may not broaden a branch-local condition.

## 4. Handoff structure

The durable result is `Iris/build/description/composition/blocks.json`, schema `iris-layer3-composition-v1`, contract version `1`.

Each item contains:

- `blocks`: semantic and acquisition blocks;
- `branches`: independently addressable meanings inside a justified compound/variant block;
- `relations`: direction, participating branches/facts, and the accepted basis for a confirmed relation;
- `qualifiers`: deduplicated item-level conditions with exact fact, branch, and block scope;
- `separate_block_refs`: the complete set Problem 2 must keep separately available, including blocks whose pair relation remains undetermined;
- `unresolved_relations`: explicitly reviewed relation candidates that lack an accepted direction and must stay separate.

Every accepted semantic and acquisition fact has exactly one representation: an anchor branch or a qualifier record. Stable block, branch, qualifier, and relation identities depend on item and fact identities, not input order, prose, or Profile order. A target with no accepted fact has an empty block list and makes no public semantic claim.

## 5. Problem 2 permissions and prohibitions

Problem 2 may merge or split sentences, express branches in parallel, omit repeated common wording, and produce different compact/expanded arrangements. A meaning block is not a mandated sentence or screen block.

Problem 2 must not:

- choose a `primary_use`, discard an independent block, or treat ordering as priority;
- change a role, result direction, confirmed relation, alternative route, or qualifier scope;
- turn `undetermined` into equivalence/containment/alternative without new accepted evidence;
- parse r6 KO/EN prose or Profile names to override this structure;
- treat acquisition as a semantic function or import Layer 4 procedure detail into Layer 3 meaning.

The reader in `composition_results.read_result` validates this handoff structure. Its validation is a consumer contract check, not a new truth authority or a claim that every relation has received human semantic review.
