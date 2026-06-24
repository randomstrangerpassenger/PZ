# Runtime Payload Shape Contract

Runtime payload state shape is sealed at build time.

The current route consumes `runtime_payload_shape_matrix.json`, `payload_shape_validation_report.json`, and `current_route_payload_state_guard_report.json`. Forbidden current/current-looking payload combinations fail loud; predecessor residues are counted separately.

Runtime Lua remains a renderer and does not become a source, quality, or publish policy checker.
