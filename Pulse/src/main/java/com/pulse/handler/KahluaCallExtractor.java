package com.pulse.handler;

import com.pulse.api.log.PulseLogger;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Kahlua Lua 호출 추출기.
 * 
 * <p>
 * MixinKahluaThread에서 분리된 리플렉션 로직을 캡슐화합니다.
 * Multi-Layer Cascading Extraction 전략을 사용하여 Lua 함수 객체를 추출합니다.
 * </p>
 * 
 * <h3>Extraction Priority:</h3>
 * <ol>
 * <li>Stack Top: getTop() - nArgs - 1 → objectStack[pos]</li>
 * <li>Direct Stack: objectStack + top field</li>
 * <li>Callframe closure (works for nested calls)</li>
 * <li>Late extraction at RETURN</li>
 * <li>String fallback (guaranteed)</li>
 * </ol>
 * 
 * @since Pulse 1.6 - Extracted from MixinKahluaThread
 */
public final class KahluaCallExtractor {

    private static final String LOG = "Pulse/KahluaExtractor";

    // Singleton instance
    private static final KahluaCallExtractor INSTANCE = new KahluaCallExtractor();

    // ═══════════════════════════════════════════════════════════════
    // Statistics Tracking
    // ═══════════════════════════════════════════════════════════════

    private final AtomicBoolean loggedStackTop = new AtomicBoolean(false);
    private final AtomicBoolean loggedDirectStack = new AtomicBoolean(false);
    private final AtomicBoolean loggedCallFrame = new AtomicBoolean(false);
    private final AtomicLong successCount = new AtomicLong(0);
    private final AtomicLong fallbackCount = new AtomicLong(0);

    // ═══════════════════════════════════════════════════════════════
    // Reflection Cache
    // ═══════════════════════════════════════════════════════════════

    private volatile Field currentCoroutineField;
    private volatile Method getTopMethod;
    private volatile Method getObjectFromStackMethod;
    private volatile Field objectStackField;
    private volatile Field topField;
    private volatile Method currentCallFrameMethod;
    private volatile Field closureField;
    private volatile Field javaFunctionField;
    private volatile boolean reflectionInitialized = false;
    private volatile boolean reflectionFailed = false;

    // Class references (loaded at runtime)
    private volatile Class<?> kahluaThreadClass;
    private volatile Class<?> coroutineClass;
    private volatile Class<?> luaCallFrameClass;
    private volatile Class<?> luaClosureClass;
    private volatile Class<?> javaFunctionClass;

    private KahluaCallExtractor() {
        // Singleton
    }

    /**
     * Get singleton instance.
     */
    public static KahluaCallExtractor getInstance() {
        return INSTANCE;
    }

    // ═══════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════

    /**
     * Extract callable from KahluaThread at call/pcall start.
     * 
     * @param kahluaThread The KahluaThread instance (this pointer from Mixin)
     * @param callType     "call" or "pcall"
     * @param nArgs        Number of arguments
     * @return Extracted callable object, or null if extraction failed
     */
    public Object extract(Object kahluaThread, String callType, int nArgs) {
        if (reflectionFailed) {
            return null;
        }

        try {
            if (!reflectionInitialized) {
                initReflection();
            }
            if (currentCoroutineField == null) {
                return null;
            }

            Object coroutine = currentCoroutineField.get(kahluaThread);
            if (coroutine == null) {
                return null;
            }

            // Strategy 1: Stack Top (most accurate for call/pcall HEAD)
            Object result = extractViaStackTop(coroutine, nArgs);
            if (result != null) {
                successCount.incrementAndGet();
                return result;
            }

            // Strategy 2: Direct Stack access
            result = extractViaDirectStack(coroutine, nArgs);
            if (result != null) {
                successCount.incrementAndGet();
                return result;
            }

            // Strategy 3: Callframe (works for nested calls)
            result = extractViaCallFrame(coroutine);
            if (result != null) {
                successCount.incrementAndGet();
                return result;
            }

        } catch (Exception e) {
            // Silent - will use fallback
        }
        return null;
    }

    /**
     * Late extraction at RETURN point.
     * 
     * @param kahluaThread The KahluaThread instance
     * @param nArgs        Number of arguments
     * @return Extracted callable object, or null if extraction failed
     */
    public Object lateExtract(Object kahluaThread, int nArgs) {
        if (reflectionFailed || currentCoroutineField == null) {
            return null;
        }
        try {
            Object coroutine = currentCoroutineField.get(kahluaThread);
            if (coroutine != null) {
                Object result = extractViaCallFrame(coroutine);
                if (result != null) {
                    successCount.incrementAndGet();
                }
                return result;
            }
        } catch (Exception e) {
            // Silent
        }
        return null;
    }

    /**
     * Create fallback string when all extraction strategies fail.
     */
    public String createFallback(String callType, int nArgs) {
        fallbackCount.incrementAndGet();
        return callType + ":" + nArgs;
    }

    /**
     * Check if extractor is ready.
     */
    public boolean isReady() {
        return reflectionInitialized && !reflectionFailed;
    }

    // ═══════════════════════════════════════════════════════════════
    // Statistics
    // ═══════════════════════════════════════════════════════════════

    public long getSuccessCount() {
        return successCount.get();
    }

    public long getFallbackCount() {
        return fallbackCount.get();
    }

    public double getSuccessRate() {
        long total = successCount.get() + fallbackCount.get();
        if (total == 0)
            return 0.0;
        return (double) successCount.get() / total * 100.0;
    }

    // ═══════════════════════════════════════════════════════════════
    // Extraction Strategies
    // ═══════════════════════════════════════════════════════════════

    /**
     * Strategy 1: Stack Top via getTop().
     */
    private Object extractViaStackTop(Object coroutine, int nArgs) {
        try {
            if (getTopMethod != null && getObjectFromStackMethod != null) {
                int top = (Integer) getTopMethod.invoke(coroutine);
                int funcPos = top - nArgs - 1;
                if (funcPos >= 0) {
                    Object func = getObjectFromStackMethod.invoke(coroutine, funcPos);
                    if (isLuaCallable(func)) {
                        if (!loggedStackTop.get()) {
                            PulseLogger.debug(LOG, "✓ Strategy 1: Stack Top extraction works!");
                            loggedStackTop.set(true);
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

    /**
     * Strategy 2: Direct objectStack access.
     */
    private Object extractViaDirectStack(Object coroutine, int nArgs) {
        try {
            if (objectStackField != null && topField != null) {
                Object[] stack = (Object[]) objectStackField.get(coroutine);
                int top = topField.getInt(coroutine);
                int funcPos = top - nArgs - 1;
                if (stack != null && funcPos >= 0 && funcPos < stack.length) {
                    Object func = stack[funcPos];
                    if (isLuaCallable(func)) {
                        if (!loggedDirectStack.get()) {
                            PulseLogger.debug(LOG, "✓ Strategy 2: Direct Stack works!");
                            loggedDirectStack.set(true);
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

    /**
     * Strategy 3: Callframe closure.
     */
    private Object extractViaCallFrame(Object coroutine) {
        try {
            if (currentCallFrameMethod != null) {
                Object frame = currentCallFrameMethod.invoke(coroutine);
                if (frame != null) {
                    if (closureField != null) {
                        Object closure = closureField.get(frame);
                        if (closure != null) {
                            if (!loggedCallFrame.get()) {
                                PulseLogger.debug(LOG, "✓ Strategy 3: Callframe closure works!");
                                loggedCallFrame.set(true);
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

    /**
     * Check if object is a Lua callable (LuaClosure or JavaFunction).
     */
    private boolean isLuaCallable(Object obj) {
        if (obj == null)
            return false;
        if (luaClosureClass != null && luaClosureClass.isInstance(obj))
            return true;
        if (javaFunctionClass != null && javaFunctionClass.isInstance(obj))
            return true;
        // Fallback: check class name
        String className = obj.getClass().getName();
        return className.contains("LuaClosure") || className.contains("JavaFunction");
    }

    // ═══════════════════════════════════════════════════════════════
    // Reflection Initialization
    // ═══════════════════════════════════════════════════════════════

    private synchronized void initReflection() {
        if (reflectionInitialized) {
            return;
        }

        try {
            // Load Kahlua classes
            kahluaThreadClass = Class.forName("se.krka.kahlua.vm.KahluaThread");
            coroutineClass = Class.forName("se.krka.kahlua.vm.Coroutine");
            luaCallFrameClass = Class.forName("se.krka.kahlua.vm.LuaCallFrame");

            try {
                luaClosureClass = Class.forName("se.krka.kahlua.vm.LuaClosure");
            } catch (ClassNotFoundException e) {
                // Optional
            }

            try {
                javaFunctionClass = Class.forName("se.krka.kahlua.vm.JavaFunction");
            } catch (ClassNotFoundException e) {
                // Optional
            }

            // KahluaThread.currentCoroutine
            currentCoroutineField = getFieldSafe(kahluaThreadClass, "currentCoroutine");
            if (currentCoroutineField != null) {
                PulseLogger.debug(LOG, "✓ currentCoroutine field");
            }

            // Coroutine.getTop()
            getTopMethod = getMethodSafe(coroutineClass, "getTop");
            if (getTopMethod != null) {
                PulseLogger.debug(LOG, "✓ getTop()");
            }

            // Coroutine.getObjectFromStack(int)
            getObjectFromStackMethod = getMethodSafe(coroutineClass, "getObjectFromStack", int.class);
            if (getObjectFromStackMethod != null) {
                PulseLogger.debug(LOG, "✓ getObjectFromStack()");
            }

            // Coroutine.objectStack
            objectStackField = getFieldSafe(coroutineClass, "objectStack");
            if (objectStackField != null) {
                PulseLogger.debug(LOG, "✓ objectStack field");
            }

            // Coroutine.top
            topField = getFieldSafe(coroutineClass, "top");
            if (topField != null) {
                PulseLogger.debug(LOG, "✓ top field");
            }

            // Coroutine.currentCallFrame()
            currentCallFrameMethod = getMethodSafe(coroutineClass, "currentCallFrame");
            if (currentCallFrameMethod != null) {
                PulseLogger.debug(LOG, "✓ currentCallFrame()");
            }

            // LuaCallFrame.closure
            closureField = getFieldSafe(luaCallFrameClass, "closure");

            // LuaCallFrame.javaFunction
            javaFunctionField = getFieldSafe(luaCallFrameClass, "javaFunction");

            if (currentCoroutineField == null) {
                PulseLogger.error(LOG, "Missing currentCoroutine - fallback only mode");
                reflectionFailed = true;
            } else {
                PulseLogger.info(LOG, "✓ KahluaCallExtractor v1.0 ready (Multi-Layer)");
            }
        } catch (Exception e) {
            PulseLogger.error(LOG, "Init failed: " + e.getMessage());
            reflectionFailed = true;
        }
        reflectionInitialized = true;
    }

    /**
     * Safe field getter - tries public first, then declared.
     */
    private Field getFieldSafe(Class<?> clazz, String name) {
        try {
            return clazz.getField(name);
        } catch (NoSuchFieldException e) {
            try {
                Field f = clazz.getDeclaredField(name);
                f.setAccessible(true);
                return f;
            } catch (NoSuchFieldException ex) {
                return null;
            }
        }
    }

    /**
     * Safe method getter - tries public first, then declared.
     */
    private Method getMethodSafe(Class<?> clazz, String name, Class<?>... paramTypes) {
        try {
            return clazz.getMethod(name, paramTypes);
        } catch (NoSuchMethodException e) {
            try {
                Method m = clazz.getDeclaredMethod(name, paramTypes);
                m.setAccessible(true);
                return m;
            } catch (NoSuchMethodException ex) {
                return null;
            }
        }
    }
}
