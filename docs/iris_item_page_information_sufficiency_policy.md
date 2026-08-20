# Iris Item Page Information Sufficiency Policy

<!-- IPS-POLICY-ENTRY-START -->

Status: adopted on 2026-08-21. This policy is bounded by the exact ratification record in `Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json` and its immutable proposal subject. The ratification contract is the only authoritative `IPS-RAT-*` list.

## Purpose and authority

The assessment observes the current vanilla offline item-page denominator and projects Layer 3 and Layer 4 producer evidence into a page-level information-sufficiency disposition. It is read-only Publish Boundary component evidence. It does not generate facts, replace DVF System or QG, issue a Publish Boundary verdict, or alter runtime/UI behavior.

Public Text Quality and page information sufficiency are independent axes. Either axis may pass or produce findings while the other reaches a different result. Public-text metrics, waivers, denominators, or human-review outcomes are forbidden inputs to this assessment.

## Denominator and baseline

The denominator is the execution-time exact case-sensitive FullType set in `Iris/input/items_itemscript.json`. Counts observed while planning are diagnostics, never constants. Duplicate keys, a key/`FullType` mismatch, out-of-universe producer rows, or a reader that cannot preserve case-distinct identities fail closed.

Layer 1 baseline authority is the ratified explicit ItemScript field registry. `IrisItemDetailViewModel` and `renderCoreInfoSection()` are cross-checks, not sources of baseline authority. The registry is a lower bound: runtime-only fields can appear marginal and bias results toward `information_sufficient`, particularly for food, weapon, literature, and moveable families. No runtime value is synthesized to correct that limitation. Layer 2 `primary_subcategory` is diagnostic identity comparison only and never positive marginal contribution.

## Producer states

Layer 3 state is derived from current pointer-selected generation provenance. An approved non-baseline proposition in the sealed declared set makes Layer 3 `required`; a zero-result query makes it artifact-set-scoped `not_required`. `optional` requires exact owner-approved provenance. An unclosed producer decision or binding is `unresolved`. Representation remains an independent `represented / missing / unresolved` axis.

Producer JSON and JSONL inputs are identified by canonical content, not checkout-specific line endings. Generator source keeps exact declared paths, serializer and chunking contract while its UTF-8 text identity is LF-normalized. For a legacy descriptor that contains only raw-byte identities, compatibility is accepted only when the current bytes reproduce the descriptor hash and size through LF/CRLF conversion alone; any other content difference fails closed. Generated runtime, Lua, and packaged outputs remain raw-byte identified because their delivered bytes are material.

Layer 4 `applicable` requires approved `PASS` evidence and its structured use-case binding. Recipe and Right-click remain independent and equal sources. `NO`, exclusion, debug-only, or review-only material is not positive contribution. When the sealed declared set query is empty, the state is `approved_fact_set_empty`, applicability is `unresolved`, representation is `missing`, and scope limitation is `blocked_by_negative_authority`. That tuple is a closed observation of unavailable negative authority, not a world-level negative or a dispositive unresolved condition. Current output never emits a non-applicability token.

`sealed_complete` means only that a producer-declared record set is identity-bound and exhaustively queried. It does not claim extraction coverage, denominator-wide authoring, semantic completeness, every possible game fact, or world-level absence.

The exception ledger records residue routing only. It has `authority_effect=none`, `semantic_production=false`, and `terminal_state_override_allowed=false`; it cannot change a derived terminal state.

## Page decision precedence

1. A required Layer 3 or applicable Layer 4 confirmed fact that is not represented is `known_information_missing`.
2. A materially unclosed producer, requiredness, representation, or applicability state is `unresolved`. The exact blocked-negative tuple above is excluded from this trigger and remains a limitation reason.
3. With no higher-precedence condition, any represented confirmed fact not derived from baseline makes the page `information_sufficient`.
4. When both declared producer sets are sealed and empty, Layer 3 is `optional` or set-scoped `not_required`, and no non-baseline fact is represented, the page is `evidence_limited`.
5. Every unmatched vector fails closed to `unresolved`.

One layer cannot compensate for a required/applicable missing fact in the other. Page identity, string length, sentence count, numeric score, ranking, recommendation, or item-specific branch cannot determine a disposition. Execution `PASS` means deterministic calculation and contract validation succeeded, not that every page is sufficient.

## Presentation boundary

Menu remains the detailed surface. Tooltip remains a maximum-four-line projection of the same confirmed facts and is not a separate facts authority. The assessment adds no heading rename, copy, badge, filter, sort key, recommendation, trust signal, or visibility rule. It does not change Recipe/Right-click equality or Layer 3/Layer 4 ownership.

## Closure and non-claims

Machine validation, eligible independent review, owner seal, and exact successor-entry binding are separate evidence. The only terminal vocabulary is axis-qualified. A complete item-page assessment does not mean Public Text Quality PASS, Publish Boundary PASS, Registry or runtime-compatibility PASS, package publication, release/Workshop/B42 readiness, external-mod coverage, or in-game QA.

The all-item denominator is not an obligation to author an independent long-form Layer 3 body for every item. Disposition distribution is not authorization for content authoring, extraction expansion, Evidence Allowlist expansion, or taxonomy repartition.

<!-- IPS-POLICY-ENTRY-END -->
