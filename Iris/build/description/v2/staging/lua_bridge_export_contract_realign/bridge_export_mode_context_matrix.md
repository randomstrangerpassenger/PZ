# Lua Bridge Export Mode/Context Matrix

| bridge_context | format | status | output rule |
| --- | --- | --- | --- |
| staging | chunk | allowed | default/current build-time route; non-deployable staging output only |
| staging | monolith | rejected | monolith is not a staging/default route |
| historical | monolith | allowed | explicit non-current output path required |
| diagnostic | monolith | allowed | explicit non-current output path required |
| historical | chunk | allowed | non-current chunk reproduction, protected destinations rejected |
| diagnostic | chunk | allowed | non-current chunk inspection, protected destinations rejected |
| current | any | rejected | no cutover-class writer context exists in this round |

Path classification is performed by resolved absolute path comparison against the protected live/package destination set.
