# Layer4 Confirmed Measurement Canonicalization Boundary Seal - Non-Mutation Hash Diff

round_id: layer4_confirmed_measurement_canonicalization_boundary_seal_round

non-mutation hash diff = pass
mismatches = 0

comparison_rule: compare normalized path -> sha256 entries; ignore manifest generation metadata; stable path ordering required.
hash_proof_scope: supports non-mutation claims only, not runtime behavior validation.

| Surface | Entry count | Result |
|---|---:|---|
| runtime_lua | 92 | pass |
| packaged_lua | 92 | pass |
| bridge_runtime_payload | 42 | pass |
| rendered_text | 3 | pass |
| source_facts | 3 | pass |
| source_decisions | 1 | pass |
| quality_state | 25 | pass |
| publish_state | 189 | pass |
| runtime_state | 196 | pass |
