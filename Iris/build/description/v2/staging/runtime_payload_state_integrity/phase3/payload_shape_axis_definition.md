# Payload Shape Axis Definition

* adoption axis: current chunks use `source = "unadopted"` for unadopted rows; `runtime_state` and `adoption_state` are absent in current runtime payloads.
* publish axis: current/current-looking payload rows must not carry `publish_state`; predecessor rollback `publish_state` is legacy residue.
* text axis: `missing`, `null_or_nil`, and `non_nil_string` are distinct. Explicit Lua `nil` is not display text.
