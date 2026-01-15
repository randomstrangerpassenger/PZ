# Area 6: Event Dispatch Stability

## Overview

Area 6 provides **Lua Event Dispatch stability** for the Nerve module. It monitors event listeners for potential issues (recursion, exceptions) and responds by **withdrawing** (pass-through) rather than blocking or modifying event flow.

## Constitution (Immutable)

### ✅ Allowed
- **Triggers**: Only 2
  1. Same-tick self-recursion
  2. Exception (error in listener)
- **Action**: Only 1
  - Same-tick pass-through (withdrawal)
- **Evidence**: Lazy collection ONLY after incident triggers

### ❌ Forbidden
- Drop, Delay, Reorder events
- Policy enforcement
- Constant measurement / cumulative reports
- Cooldown recovery / time-based cooldowns
- Cascade/Depth as triggers (evidence only)
- Performance KPIs in verification

## Key Principle

> **"Nerve가 막았다" ❌**  
> **"Nerve가 물러났다(pass-through)" ⭕**

Nerve does NOT block or modify events. When an incident is detected, Nerve **withdraws** its wrapper for that tick/scope, allowing vanilla behavior to proceed.

## Execution Flow (Sealed)

```
1. if !area6.enabled -> original
2. if passthroughThisTick(scope) -> original
3. reentry check -> if hit: mark incident + passthrough(scope)
4. xpcall listener -> if error: mark incident + passthrough(scope)
5. if incident: lazy evidence collect + emit summary (rate-limited)
6. return
```

## Configuration

Located in `media/lua/shared/Nerve/NerveConfig.lua`:

```lua
NerveConfig.area6 = {
    enabled = false,  -- DEFAULT OFF (vanilla-safe)
    
    triggers = {
        reentry = { enabled = true },
        exception = { enabled = true },
    },
    
    action = {
        type = "SAME_TICK_PASSTHROUGH",  -- Immutable
    },
    
    evidence = {
        enabled = true,
        incidentGatedOnly = true,  -- Constant measurement forbidden
    },
}
```

## Log Format

When an incident occurs:

```
==========================================
[Area6] INCIDENT: reentry|error
  eventId: OnTick
  listenerId: function: 0x12345678
  signature: Test.lua:123:error message
  installState: Applied|Partial|Bypassed
  action: SAME_TICK_PASSTHROUGH
==========================================
```

Evidence (only on incident):
```
  [Evidence]
    dupCount: 5 (5-9)
    chainDepth: 3
    fanoutExecuted: 12 (10-19)
    repeatCount: 2
```

## Testing

Run the test harness in a dev environment:

```lua
require "Nerve/dev-only/Area6TestHarness"
Nerve.Area6TestHarness.runAll()
```

## Files

| File | Purpose |
|------|---------|
| `Area6Guard.lua` | Constitution enforcement, forbidden keywords |
| `Area6Install.lua` | Events.*.Add wrapper installation |
| `Area6InstallState.lua` | Applied/Partial/Bypassed tracking |
| `Area6TickCtx.lua` | Per-tick context (wipe at tick end) |
| `Area6FailSoft.lua` | xpcall isolation + error handling |
| `Area6ErrorSig.lua` | Error signature normalization |
| `Area6Reentry.lua` | Same-tick self-recursion trigger |
| `Area6Evidence.lua` | Incident-gated evidence orchestrator |
| `Area6Dispatcher.lua` | Sealed execution flow |
