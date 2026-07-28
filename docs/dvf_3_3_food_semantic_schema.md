# DVF 3-3 Food Semantic Schema

Status: implementation proposal; semantic owner approval is not yet consumed.

This closed schema represents orthogonal, evidence-bound food facts. It does not
infer meaning from display text, item identifiers, numeric thresholds, Layer 4
interactions, hashes, ordering, or randomness. Values outside the JSON contract
require an additive schema-amendment round.

The axes cover consumption form, preparation requirement, culinary role,
preparation state, preservation form, ingredient origin, meal role, and
beverage properties. A multi-role food may carry multiple compatible assertions.
`unknown`, `generic`, and `other` completion buckets are not part of the schema.

Every value is licensed only for the proposition declared in
`proposition_licensing_contract.json`; no value licenses recommendations,
efficiency comparisons, or negative facts from missing evidence.
