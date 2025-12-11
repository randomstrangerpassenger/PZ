package com.pulse.mixin.kahlua;

import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import se.krka.kahlua.vm.LuaClosure;
import se.krka.kahlua.vm.KahluaThread;

/**
 * Mixin for se.krka.kahlua.vm.KahluaThread.
 * 
 * Provides hooks for Lua function execution (start/end).
 * Critical for verifying Pulse Scheduler - Kahlua integration.
 */
@Mixin(KahluaThread.class)
public class MixinKahluaThread {

    @Inject(method = "call(Lse/krka/kahlua/vm/LuaClosure;[Ljava/lang/Object;[Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private void onCallStart(LuaClosure closure, Object[] args, Object[] returnValues, CallbackInfo ci) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(closure));
        }
    }

    @Inject(method = "call(Lse/krka/kahlua/vm/LuaClosure;[Ljava/lang/Object;[Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private void onCallEnd(LuaClosure closure, Object[] args, Object[] returnValues, CallbackInfo ci) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(closure));
        }
    }
}
