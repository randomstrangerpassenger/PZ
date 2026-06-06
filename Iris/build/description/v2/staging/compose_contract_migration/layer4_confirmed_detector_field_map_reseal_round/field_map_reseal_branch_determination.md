# Field Map Reseal Branch Determination

contract_closeout_state = `complete`

branch_closeout = `closed_with_layer4_confirmed_detector_field_map_resealed`

All four required detector roles bind to admitted trace-edge artifact fields:

- `source_object` -> `source_ref`
- `target_layer3_row_or_item` -> `row_id`
- `destination_body_slot` -> `destination_slot`
- `explicit_edge_relation` -> `edge_type` with tuple fields `source_ref`, `edge_basis`, and `destination_slot`

Traversal coverage over `24` admitted edge rows is recorded as field-map
readiness coverage only. It is not a confirmed count.
