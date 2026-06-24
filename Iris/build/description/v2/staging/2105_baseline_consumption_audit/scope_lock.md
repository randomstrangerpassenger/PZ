# 2105 Baseline Consumption Audit Scope Lock

Status: staging-only audit scope lock.
Generated UTC: 2026-06-12T11:25:27+00:00

This audit classifies baseline-related occurrences in the audited checkout. It does not mutate runtime Lua, chunk payloads, Lua bridge payloads, source facts, decisions, rendered output, canonical DECISIONS.md, or canonical ROADMAP.md.

Current readpoint:

- Runtime baseline: 2105 rows / adopted 2084 / unadopted 21.
- Current vocabulary: adopted / unadopted.
- Legacy vocabulary: active / silent, historical / diagnostic / import alias only.
- Layer3 deployable runtime authority: IrisLayer3DataChunks.lua manifest plus IrisLayer3DataChunks/*.lua chunk files.
- Current 6-entry facts / decisions / rendered files are fixture / non-authority.
- Source-universe 2105 is a comparison reference, not runtime regeneration authority.

Scan boundary:

- Root: C:\Users\MW\Downloads\coding\PZ
- Self-audit directory excluded from raw enumeration: Iris/build/description/v2/staging/2105_baseline_consumption_audit
- Text files scanned: 5026

Closeout rule:

- complete = Gate A PASS + Gate B PASS + ambiguous-needs-adjudication 0.
- partial = ambiguity remains or a gate is incomplete but named follow-up exists.
- blocked = required tool, unreadable file, or executing consumer route unknown prevents inventory completeness.
