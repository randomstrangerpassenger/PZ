# DECISIONS Draft Entry - DVF 3-3 vNext Current Authority

> Status: draft-only
> Intended target: `docs/DECISIONS.md`
> Do not apply without a separate approved reflection step.

## Iris DVF 3-3 - vNext Current Authority Definition

- Status: draft current readpoint candidate / definition-only, not cutover
- Decision:
  - DVF 3-3 vNext is defined as a successor-authority model path, not a frozen `2105 / 2084 / 21` revival path.
  - `vNext-CAB` is a pre-cutover program / roadmap / authority-model label.
  - The actual sealed baseline identity remains deferred until a later execution round produces source count, source manifest fingerprint, rendered hash, chunk manifest fingerprint, consumer migration result, and ledger reflection evidence.
- Current read:
  - Frozen `2105 / 2084 / 21` remains predecessor, comparison reference, and migration input.
  - Existing runtime chunks remain deployable runtime authority before a later approved cutover.
  - Runtime chunks are not source authority.
  - Runtime-derived seed is non-authority bootstrap material and requires `derived-from-runtime-chunks` provenance.
  - Source authority requires a later validated source universe manifest.
  - Required later chain is `source manifest -> facts -> decisions -> compose profile + body_plan -> rendered -> Lua bridge -> chunk manifest + chunk files`.
  - `body_plan` remains compose profile implementation surface / alias label, not a second authority.
  - Successor parity means successor source-to-runtime self-consistency, not byte-level predecessor parity.
  - Old runtime chunks and successor chunks must not both be treated as current authority.
  - Consumer migration must use the 2105 audit as read-only migration input and must change authority roles, not mechanically replace numbers or vocabulary.
  - DECISIONS / ARCHITECTURE / ROADMAP reflection is draft-only until a separate approved application.
- Minimum trace:
  - Plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
  - Scope lock: `docs/dvf_3_3_vnext_authority_scope_lock.md`
  - Seed disposition: `docs/dvf_3_3_vnext_runtime_seed_disposition.md`
  - Source authority conditions: `docs/dvf_3_3_vnext_source_authority_conditions.md`
  - Regeneration requirements: `docs/dvf_3_3_vnext_regeneration_requirements.md`
  - Consumer migration principles: `docs/dvf_3_3_vnext_consumer_migration_principles.md`
  - Cutover contract: `docs/dvf_3_3_vnext_cutover_contract.md`
  - Reflection packet: `docs/dvf_3_3_vnext_ledger_update_packet.md`
  - Audit input: `Iris/build/description/v2/staging/2105_baseline_consumption_audit/`
- Non-decision:
  - This draft does not approve source reconstruction completion, successor baseline creation, facts / decisions / rendered generation, Lua bridge export, chunk generation, runtime cutover, consumer migration execution, direct canon mutation, package readiness, release readiness, Workshop readiness, B42 readiness, manual in-game validation, Browser / Wiki / Tooltip behavior change, quality exposure change, Layer4 reopen, ACQ_DOMINANT reopen, Acquisition Lexical reopen, or closed readpoint re-adjudication.
  - `active / silent` remains historical / diagnostic / import alias vocabulary only.
  - `adopted / unadopted` remains current runtime vocabulary and must not be overloaded as quality, publish, deletion, or suppression state.
