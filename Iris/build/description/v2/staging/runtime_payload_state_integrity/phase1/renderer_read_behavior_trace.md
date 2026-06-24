# Renderer Read Behavior Trace

* status: `PASS`
* publish_state read hits: `6`
* source/runtime/quality policy hits: `0`

Renderer code may read `publish_state` as a fallback field, but current payload rows do not carry `publish_state`; the renderer must not become the payload policy checker.
