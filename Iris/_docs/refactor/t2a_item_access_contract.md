# T2-A Item Access Contract

## Scope

The extraction keeps generic Java/Kahlua invocation in `IrisObjectAccess` and item-specific access in `IrisItemAccess`.

## Agreed Signatures

```lua
IrisItemAccess.getFullType(item, fallback)
IrisItemAccess.getDisplayName(item, fallback)
IrisItemAccess.getType(item, fallback)
```

## Boundaries

- `getFullType` delegates to `ItemKey.getFullTypeFromItem`.
- `getDisplayName` reads `getDisplayName()` and falls back to the caller-provided fallback.
- `getType` reads `getType()`, falls back to `getTypeString()`, then falls back to the caller-provided fallback.
- The helper does not call Iris API modules, classification indexes, recipe indexes, or UI renderers.
