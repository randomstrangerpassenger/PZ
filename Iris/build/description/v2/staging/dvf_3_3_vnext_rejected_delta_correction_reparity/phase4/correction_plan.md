# Correction Plan

Apply row-level predecessor-maintain alignment to the 54 rejected keys only.

- operation: `predecessor_maintain_alignment`
- source input: staging-local corrected copy of the source decisions JSONL
- old value: `silent`
- new value: `active`
- global remap: `false`
