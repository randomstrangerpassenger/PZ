package com.pulse.mixin.kahlua;

import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import se.krka.kahlua.vm.KahluaThread;
import se.krka.kahlua.vm.Coroutine;
import se.krka.kahlua.vm.LuaCallFrame;
import se.krka.kahlua.vm.LuaClosure;
import se.krka.kahlua.vm.JavaFunction;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Mixin for se.krka.kahlua.vm.KahluaThread.
 * 
 * v2.5: Multi-Layer Cascading Extraction
 * 
 * Extraction priority:
 * 1. Stack Top: getTop() - nArgs - 1 → objectStack[pos]
 * 2. Direct Stack: objectStack + top field
 * 3. Callframe closure (works for nested calls)
 * 4. Late extraction at RETURN
 * 5. String fallback (guaranteed)
 */
@Mixin(KahluaThread.class)
public class MixinKahluaThread {

    // Stats tracking
    private static final AtomicBoolean LOGGED_ONCE = new AtomicBoolean(false);
    private static final AtomicBoolean LOGGED_STACK_TOP = new AtomicBoolean(false);
    private static final AtomicBoolean LOGGED_DIRECT_STACK = new AtomicBoolean(false);
    private static final AtomicBoolean LOGGED_CALLFRAME = new AtomicBoolean(false);
    private static final AtomicLong SUCCESS_COUNT = new AtomicLong(0);
    private static final AtomicLong FALLBACK_COUNT = new AtomicLong(0);

    // ThreadLocal: 0=callable, 1=startNanos, 2=needsLateExtract, 3=nArgs,
    // 4=callType
    private static final ThreadLocal<Object[]> CALL_CONTEXT = ThreadLocal.withInitial(() -> new Object[5]);

    // ===== Reflection Cache =====
    private static volatile Field currentCoroutineField;
    private static volatile Method getTopMethod; // Coroutine.getTop()
    private static volatile Method getObjectFromStackMethod; // Coroutine.getObjectFromStack(int)
    private static volatile Field objectStackField; // Coroutine.objectStack
    private static volatile Field topField; // Coroutine.top (backup)
    private static volatile Method currentCallFrameMethod;
    private static volatile Field closureField;
    private static volatile Field javaFunctionField;
    private static volatile boolean reflectionInitialized = false;
    private static volatile boolean reflectionFailed = false;

    // ===== Strategy 1: Stack Top via getTop() =====
    private Object extractViaStackTop(Coroutine coroutine, int nArgs) {
        try {
            if (getTopMethod != null && getObjectFromStackMethod != null) {
                int top = (Integer) getTopMethod.invoke(coroutine);
                int funcPos = top - nArgs - 1;
                if (funcPos >= 0) {
                    Object func = getObjectFromStackMethod.invoke(coroutine, funcPos);
                    if (func instanceof LuaClosure || func instanceof JavaFunction) {
                        if (!LOGGED_STACK_TOP.get()) {
                            System.out.println("[Pulse/Mixin] ✓ Strategy 1: Stack Top extraction works!");
                            LOGGED_STACK_TOP.set(true);
                        }
                        return func;
                    }
                }
            }
        } catch (Exception e) {
            // Silent - try next strategy
        }
        return null;
    }

    // ===== Strategy 2: Direct objectStack access =====
    private Object extractViaDirectStack(Coroutine coroutine, int nArgs) {
        try {
            if (objectStackField != null && topField != null) {
                Object[] stack = (Object[]) objectStackField.get(coroutine);
                int top = topField.getInt(coroutine);
                int funcPos = top - nArgs - 1;
                if (stack != null && funcPos >= 0 && funcPos < stack.length) {
                    Object func = stack[funcPos];
                    if (func instanceof LuaClosure || func instanceof JavaFunction) {
                        if (!LOGGED_DIRECT_STACK.get()) {
                            System.out.println("[Pulse/Mixin] ✓ Strategy 2: Direct Stack works!");
                            LOGGED_DIRECT_STACK.set(true);
                        }
                        return func;
                    }
                }
            }
        } catch (Exception e) {
            // Silent - try next strategy
        }
        return null;
    }

    // ===== Strategy 3: Callframe closure =====
    private Object extractViaCallFrame(Coroutine coroutine) {
        try {
            if (currentCallFrameMethod != null) {
                LuaCallFrame frame = (LuaCallFrame) currentCallFrameMethod.invoke(coroutine);
                if (frame != null) {
                    if (closureField != null) {
                        Object closure = closureField.get(frame);
                        if (closure != null) {
                            if (!LOGGED_CALLFRAME.get()) {
                                System.out.println("[Pulse/Mixin] ✓ Strategy 3: Callframe closure works!");
                                LOGGED_CALLFRAME.set(true);
                            }
                            return closure;
                        }
                    }
                    if (javaFunctionField != null) {
                        Object javaFunc = javaFunctionField.get(frame);
                        if (javaFunc != null) {
                            return javaFunc;
                        }
                    }
                }
            }
        } catch (Exception e) {
            // Silent
        }
        return null;
    }

    // ===== Main extraction: Try all strategies =====
    private Object extractCallable(String callType, int nArgs) {
        if (reflectionFailed)
            return null;

        try {
            if (!reflectionInitialized)
                initReflection();
            if (currentCoroutineField == null)
                return null;

            Coroutine coroutine = (Coroutine) currentCoroutineField.get(this);
            if (coroutine == null)
                return null;

            // Strategy 1: Stack Top (most accurate for call/pcall HEAD)
            Object result = extractViaStackTop(coroutine, nArgs);
            if (result != null)
                return result;

            // Strategy 2: Direct Stack access
            result = extractViaDirectStack(coroutine, nArgs);
            if (result != null)
                return result;

            // Strategy 3: Callframe (works for nested calls)
            result = extractViaCallFrame(coroutine);
            if (result != null)
                return result;

        } catch (Exception e) {
            // Silent
        }
        return null; // Will try late extraction or fallback
    }

    // ===== Late extraction at RETURN =====
    private Object lateExtractCallable(int nArgs) {
        if (reflectionFailed || currentCoroutineField == null)
            return null;
        try {
            Coroutine coroutine = (Coroutine) currentCoroutineField.get(this);
            if (coroutine != null) {
                // At RETURN, callframe should be fully set up
                return extractViaCallFrame(coroutine);
            }
        } catch (Exception e) {
            // Silent
        }
        return null;
    }

    private synchronized void initReflection() {
        if (reflectionInitialized)
            return;

        try {
            // KahluaThread.currentCoroutine
            try {
                currentCoroutineField = KahluaThread.class.getField("currentCoroutine");
                System.out.println("[Pulse/Mixin] ✓ currentCoroutine (public)");
            } catch (NoSuchFieldException e) {
                currentCoroutineField = KahluaThread.class.getDeclaredField("currentCoroutine");
                currentCoroutineField.setAccessible(true);
            }

            // Coroutine.getTop()
            try {
                getTopMethod = Coroutine.class.getMethod("getTop");
                System.out.println("[Pulse/Mixin] ✓ getTop()");
            } catch (NoSuchMethodException e) {
                // Try declared
                try {
                    getTopMethod = Coroutine.class.getDeclaredMethod("getTop");
                    getTopMethod.setAccessible(true);
                } catch (NoSuchMethodException ex) {
                    System.out.println("[Pulse/Mixin] getTop() not found, will use backup");
                }
            }

            // Coroutine.getObjectFromStack(int)
            try {
                getObjectFromStackMethod = Coroutine.class.getMethod("getObjectFromStack", int.class);
                System.out.println("[Pulse/Mixin] ✓ getObjectFromStack()");
            } catch (NoSuchMethodException e) {
                try {
                    getObjectFromStackMethod = Coroutine.class.getDeclaredMethod("getObjectFromStack", int.class);
                    getObjectFromStackMethod.setAccessible(true);
                } catch (NoSuchMethodException ex) {
                    // Optional
                }
            }

            // Coroutine.objectStack (backup)
            try {
                objectStackField = Coroutine.class.getField("objectStack");
                System.out.println("[Pulse/Mixin] ✓ objectStack field");
            } catch (NoSuchFieldException e) {
                try {
                    objectStackField = Coroutine.class.getDeclaredField("objectStack");
                    objectStackField.setAccessible(true);
                } catch (NoSuchFieldException ex) {
                    // Not critical
                }
            }

            // Coroutine.top (backup for direct stack access)
            try {
                topField = Coroutine.class.getDeclaredField("top");
                topField.setAccessible(true);
                System.out.println("[Pulse/Mixin] ✓ top field");
            } catch (NoSuchFieldException e) {
                // Not critical
            }

            // Coroutine.currentCallFrame()
            try {
                currentCallFrameMethod = Coroutine.class.getMethod("currentCallFrame");
                System.out.println("[Pulse/Mixin] ✓ currentCallFrame()");
            } catch (NoSuchMethodException e) {
                try {
                    currentCallFrameMethod = Coroutine.class.getDeclaredMethod("currentCallFrame");
                    currentCallFrameMethod.setAccessible(true);
                } catch (NoSuchMethodException ex) {
                    // Critical
                }
            }

            // LuaCallFrame.closure
            try {
                closureField = LuaCallFrame.class.getField("closure");
            } catch (NoSuchFieldException e) {
                closureField = LuaCallFrame.class.getDeclaredField("closure");
                closureField.setAccessible(true);
            }

            // LuaCallFrame.javaFunction
            try {
                javaFunctionField = LuaCallFrame.class.getField("javaFunction");
            } catch (NoSuchFieldException e) {
                try {
                    javaFunctionField = LuaCallFrame.class.getDeclaredField("javaFunction");
                    javaFunctionField.setAccessible(true);
                } catch (NoSuchFieldException ex) {
                    // Optional
                }
            }

            // Verify minimum requirements
            if (currentCoroutineField == null) {
                System.err.println("[Pulse/Mixin] Missing currentCoroutine - fallback only");
                reflectionFailed = true;
            } else {
                System.out.println("[Pulse/Mixin] ✓ Reflection v2.5 ready (Multi-Layer)");
            }
        } catch (Exception e) {
            System.err.println("[Pulse/Mixin] Init failed: " + e.getMessage());
            reflectionFailed = true;
        }
        reflectionInitialized = true;
    }

    // ========== call(int) ==========

    @Inject(method = "call(I)I", at = @At("HEAD"), remap = false)
    private void onCallIntStart(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            if (LOGGED_ONCE.compareAndSet(false, true)) {
                System.out.println("[Pulse] MixinKahluaThread v2.5 active (Multi-Layer)");
            }
            Object[] ctx = CALL_CONTEXT.get();
            Object callable = extractCallable("call", nArgs);
            ctx[0] = callable;
            ctx[1] = System.nanoTime();
            ctx[2] = (callable == null);
            ctx[3] = nArgs;
            ctx[4] = "call";

            if (callable != null) {
                SUCCESS_COUNT.incrementAndGet();
                long startNanos = (Long) ctx[1];
                PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(callable, startNanos));
            }
        }
    }

    @Inject(method = "call(I)I", at = @At("RETURN"), remap = false)
    private void onCallIntEnd(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            Object[] ctx = CALL_CONTEXT.get();
            Object callable = ctx[0];
            long startNanos = ctx[1] != null ? (Long) ctx[1] : System.nanoTime();
            boolean needsLate = ctx[2] != null && (Boolean) ctx[2];
            String callType = ctx[4] != null ? (String) ctx[4] : "call";

            // Late extraction if HEAD failed
            if (needsLate && callable == null) {
                callable = lateExtractCallable(nArgs);
                if (callable != null) {
                    SUCCESS_COUNT.incrementAndGet();
                    final Object c = callable;
                    final long sn = startNanos;
                    PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
                }
            }

            // Final fallback
            if (callable == null) {
                callable = callType + ":" + nArgs;
                FALLBACK_COUNT.incrementAndGet();
                final Object c = callable;
                final long sn = startNanos;
                PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
            }

            long endNanos = System.nanoTime();
            final Object c = callable;
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(c, endNanos));

            ctx[0] = null;
            ctx[1] = null;
            ctx[2] = null;
            ctx[3] = null;
            ctx[4] = null;
        }
    }

    // ========== pcall(int) ==========

    @Inject(method = "pcall(I)I", at = @At("HEAD"), remap = false)
    private void onPcallStart(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            if (LOGGED_ONCE.compareAndSet(false, true)) {
                System.out.println("[Pulse] MixinKahluaThread v2.5 active (Multi-Layer)");
            }
            Object[] ctx = CALL_CONTEXT.get();
            Object callable = extractCallable("pcall", nArgs);
            ctx[0] = callable;
            ctx[1] = System.nanoTime();
            ctx[2] = (callable == null);
            ctx[3] = nArgs;
            ctx[4] = "pcall";

            if (callable != null) {
                SUCCESS_COUNT.incrementAndGet();
                long startNanos = (Long) ctx[1];
                PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(callable, startNanos));
            }
        }
    }

    @Inject(method = "pcall(I)I", at = @At("RETURN"), remap = false)
    private void onPcallEnd(int nArgs, CallbackInfoReturnable<Integer> cir) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            Object[] ctx = CALL_CONTEXT.get();
            Object callable = ctx[0];
            long startNanos = ctx[1] != null ? (Long) ctx[1] : System.nanoTime();
            boolean needsLate = ctx[2] != null && (Boolean) ctx[2];
            String callType = ctx[4] != null ? (String) ctx[4] : "pcall";

            if (needsLate && callable == null) {
                callable = lateExtractCallable(nArgs);
                if (callable != null) {
                    SUCCESS_COUNT.incrementAndGet();
                    final Object c = callable;
                    final long sn = startNanos;
                    PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
                }
            }

            if (callable == null) {
                callable = callType + ":" + nArgs;
                FALLBACK_COUNT.incrementAndGet();
                final Object c = callable;
                final long sn = startNanos;
                PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(c, sn));
            }

            long endNanos = System.nanoTime();
            final Object c = callable;
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(c, endNanos));

            ctx[0] = null;
            ctx[1] = null;
            ctx[2] = null;
            ctx[3] = null;
            ctx[4] = null;
        }
    }

    // ========== call(Object, Object[]) ==========

    @Inject(method = "call(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;", at = @At("HEAD"), remap = false)
    private void onCallObjStart(Object function, Object[] args, CallbackInfoReturnable<Object> cir) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            if (LOGGED_ONCE.compareAndSet(false, true)) {
                System.out.println("[Pulse] MixinKahluaThread v2.5 active (Multi-Layer)");
            }
            Object[] ctx = CALL_CONTEXT.get();
            ctx[0] = function; // Direct access
            ctx[1] = System.nanoTime();
            ctx[2] = false;
            ctx[3] = args != null ? args.length : 0;
            ctx[4] = "call_obj";

            SUCCESS_COUNT.incrementAndGet();
            long startNanos = (Long) ctx[1];
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallStart(function, startNanos));
        }
    }

    @Inject(method = "call(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;", at = @At("RETURN"), remap = false)
    private void onCallObjEnd(Object function, Object[] args, CallbackInfoReturnable<Object> cir) {
        if (PulseHookRegistry.hasCallbacks(HookTypes.LUA_CALL)) {
            long endNanos = System.nanoTime();
            PulseHookRegistry.broadcast(HookTypes.LUA_CALL, cb -> cb.onLuaCallEnd(function, endNanos));

            Object[] ctx = CALL_CONTEXT.get();
            ctx[0] = null;
            ctx[1] = null;
            ctx[2] = null;
            ctx[3] = null;
            ctx[4] = null;
        }
    }
}
