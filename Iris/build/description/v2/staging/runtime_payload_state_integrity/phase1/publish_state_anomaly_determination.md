# Publish State Anomaly Determination

Status: `current_payload_absent_predecessor_residue_present`.

Current/current-looking runtime payload rows have no authoritative `publish_state` field. `publish_state = exposed` appears only in predecessor rollback residue for `2` row(s), so it is guarded as legacy residue rather than repaired as a live current mutation.
