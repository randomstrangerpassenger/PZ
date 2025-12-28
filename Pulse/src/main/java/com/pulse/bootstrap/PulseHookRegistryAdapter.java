package com.pulse.bootstrap;

import com.pulse.api.hook.HookType;
import com.pulse.api.hook.IPulseHookRegistry;
import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;

/**
 * IPulseHookRegistry 어댑터.
 * PulseHookRegistry 정적 메서드들을 IPulseHookRegistry 인터페이스에 연결.
 * 
 * @since Pulse 2.1
 */
public class PulseHookRegistryAdapter implements IPulseHookRegistry {

    private static final PulseHookRegistryAdapter INSTANCE = new PulseHookRegistryAdapter();

    private PulseHookRegistryAdapter() {
    }

    public static PulseHookRegistryAdapter getInstance() {
        return INSTANCE;
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T> void register(HookType type, T callback, String ownerId) {
        com.pulse.hook.HookType<?> hookType = convertHookType(type);
        if (hookType != null) {
            PulseHookRegistry.register((com.pulse.hook.HookType<T>) hookType, callback, ownerId);
        }
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T> void unregister(HookType type, T callback) {
        com.pulse.hook.HookType<?> hookType = convertHookType(type);
        if (hookType != null) {
            PulseHookRegistry.unregister((com.pulse.hook.HookType<T>) hookType, callback);
        }
    }

    @Override
    public void unregisterAll(String ownerId) {
        PulseHookRegistry.unregisterAll(ownerId);
    }

    @Override
    public int getCallbackCount(HookType type) {
        com.pulse.hook.HookType<?> hookType = convertHookType(type);
        if (hookType != null) {
            return PulseHookRegistry.getCallbacks(hookType).size();
        }
        return 0;
    }

    /**
     * API HookType enum을 Core HookType으로 변환.
     */
    private com.pulse.hook.HookType<?> convertHookType(HookType apiType) {
        if (apiType == null)
            return null;

        switch (apiType) {
            case LUA_CALL:
                return HookTypes.LUA_CALL;
            case TICK_START:
            case TICK_END:
                return HookTypes.TICK_PHASE;
            case RENDER_FRAME:
                return HookTypes.RENDER_FRAME;
            case ZOMBIE_UPDATE:
                return HookTypes.ZOMBIE;
            case PATHFINDING:
                return HookTypes.PATHFINDING;
            case ISO_GRID:
                return HookTypes.ISO_GRID;
            case SAVE:
            case LOAD:
                return null;
            default:
                return null;
        }
    }
}
