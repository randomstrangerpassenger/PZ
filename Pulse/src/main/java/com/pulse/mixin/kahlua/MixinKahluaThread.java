package com.pulse.mixin.kahlua;

import com.pulse.api.log.PulseLogger;
import com.pulse.handler.KahluaCallExtractor;
import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import se.krka.kahlua.vm.KahluaThread;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Mixin for se.krka.kahlua.vm.KahluaThread.
 * 
 * <p>
 * Lua 호출(call/pcall)을 가로채서 프로파일링에 노출합니다.
 * </p>
 * 
 * <p>
 * v3.0: 리플렉션 로직을 {@link KahluaCallExtractor}로 분리하여 간소화됨.
 * </p>
 * 
 * @since Pulse 1.0
 * @since Pulse 1.6 - Refactored to use KahluaCallExtractor handler
 */
@Mixin(KahluaThread.class)
public class MixinKahluaThread {

    private static final String LOG = "Pulse/MixinKahluaThread";

    // First activation logging
    private static final AtomicBoolean LOGGED_ONCE = new AtomicBoolean(false);

    // ThreadLocal context: [0]=callable, [1]=startNanos, [2]=needsLateExtract,
    // [3]=nArgs, [4]=callType
    private static final ThreadLocal<Object[]> CALL_CONTEXT = ThreadLocal.withInitial(() -> new Object[5]);

    // ═══════════════════════════════════════════════════════════════
    // call(int) hooks
    // ═══════════════════════════════════════════════════════════════

    @Inject(method = "call(I)I", at = @At("HEAD"), remap = false)
    private void onCallIntStart(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (!PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            return;
        }

        logFirstActivation();

        KahluaCallExtractor extractor = KahluaCallExtractor.getInstance();
        Object callable = extractor.extract(this, "call", nArgs);

        Object[] ctx = CALL_CONTEXT.get();
        ctx[0] = callable;
        ctx[1] = System.nanoTime();
        ctx[2] = (callable == null);
        ctx[3] = nArgs;
        ctx[4] = "call";

        if (callable != null) {
            long startNanos = (Long) ctx[1];
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(callable, startNanos));
        }
    }

    @Inject(method = "call(I)I", at = @At("RETURN"), remap = false)
    private void onCallIntEnd(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (!PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            return;
        }

        Object[] ctx = CALL_CONTEXT.get();
        Object callable = ctx[0];
        long startNanos = ctx[1] != null ? (Long) ctx[1] : System.nanoTime();
        boolean needsLate = ctx[2] != null && (Boolean) ctx[2];
        String callType = ctx[4] != null ? (String) ctx[4] : "call";

        // Late extraction if HEAD failed
        if (needsLate && callable == null) {
            KahluaCallExtractor extractor = KahluaCallExtractor.getInstance();
            callable = extractor.lateExtract(this, nArgs);
            if (callable != null) {
                final Object c = callable;
                final long sn = startNanos;
                PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
            }
        }

        // Final fallback
        if (callable == null) {
            callable = KahluaCallExtractor.getInstance().createFallback(callType, nArgs);
            final Object c = callable;
            final long sn = startNanos;
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
        }

        long endNanos = System.nanoTime();
        final Object c = callable;
        PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(c, endNanos));

        clearContext(ctx);
    }

    // ═══════════════════════════════════════════════════════════════
    // pcall(int) hooks
    // ═══════════════════════════════════════════════════════════════

    @Inject(method = "pcall(I)I", at = @At("HEAD"), remap = false)
    private void onPcallStart(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (!PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            return;
        }

        logFirstActivation();

        KahluaCallExtractor extractor = KahluaCallExtractor.getInstance();
        Object callable = extractor.extract(this, "pcall", nArgs);

        Object[] ctx = CALL_CONTEXT.get();
        ctx[0] = callable;
        ctx[1] = System.nanoTime();
        ctx[2] = (callable == null);
        ctx[3] = nArgs;
        ctx[4] = "pcall";

        if (callable != null) {
            long startNanos = (Long) ctx[1];
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(callable, startNanos));
        }
    }

    @Inject(method = "pcall(I)I", at = @At("RETURN"), remap = false)
    private void onPcallEnd(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (!PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            return;
        }

        Object[] ctx = CALL_CONTEXT.get();
        Object callable = ctx[0];
        long startNanos = ctx[1] != null ? (Long) ctx[1] : System.nanoTime();
        boolean needsLate = ctx[2] != null && (Boolean) ctx[2];
        String callType = ctx[4] != null ? (String) ctx[4] : "pcall";

        if (needsLate && callable == null) {
            KahluaCallExtractor extractor = KahluaCallExtractor.getInstance();
            callable = extractor.lateExtract(this, nArgs);
            if (callable != null) {
                final Object c = callable;
                final long sn = startNanos;
                PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
            }
        }

        if (callable == null) {
            callable = KahluaCallExtractor.getInstance().createFallback(callType, nArgs);
            final Object c = callable;
            final long sn = startNanos;
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
        }

        long endNanos = System.nanoTime();
        final Object c = callable;
        PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(c, endNanos));

        clearContext(ctx);
    }

    // ═══════════════════════════════════════════════════════════════
    // call(Object, Object[]) hooks - direct function access
    // ═══════════════════════════════════════════════════════════════

    @Inject(method = "call(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;", at = @At("HEAD"), remap = false)
    private void onCallObjStart(Object function, Object[] args, CallbackInfoReturnable<Object> cir) {
        if (!PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            return;
        }

        logFirstActivation();

        Object[] ctx = CALL_CONTEXT.get();
        ctx[0] = function; // Direct access - no extraction needed
        ctx[1] = System.nanoTime();
        ctx[2] = false;
        ctx[3] = args != null ? args.length : 0;
        ctx[4] = "call_obj";

        long startNanos = (Long) ctx[1];
        PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(function, startNanos));
    }

    @Inject(method = "call(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;", at = @At("RETURN"), remap = false)
    private void onCallObjEnd(Object function, Object[] args, CallbackInfoReturnable<Object> cir) {
        if (!PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            return;
        }

        long endNanos = System.nanoTime();
        PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(function, endNanos));

        clearContext(CALL_CONTEXT.get());
    }

    // ═══════════════════════════════════════════════════════════════
    // Helper methods
    // ═══════════════════════════════════════════════════════════════

    private static void logFirstActivation() {
        if (LOGGED_ONCE.compareAndSet(false, true)) {
            PulseLogger.info(LOG, "v3.0 active (using KahluaCallExtractor)");
        }
    }

    private static void clearContext(Object[] ctx) {
        ctx[0] = null;
        ctx[1] = null;
        ctx[2] = null;
        ctx[3] = null;
        ctx[4] = null;
    }
}
