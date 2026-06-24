# Renderer Responsibility Boundary

Runtime Lua remains a sealed payload renderer. It may return text that is already present in the payload. It must not compose, repair, validate source, infer quality, judge publish policy, or use `source` / `runtime_state` / `adoption_state` as display policy.
