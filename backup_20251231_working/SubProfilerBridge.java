package com.echo.pulse;

import com.echo.measure.SubProfiler;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.SubProfilerHook;

import java.lang.reflect.Method;

/**
 * SubProfiler Pulse 연동
 * 
 * Echo 초기화 시 Pulse의 SubProfilerHook에 콜백을 등록하여
 * Pulse Mixin에서 SubProfiler를 호출할 수 있게 합니다.
 * 
 * <p>
 * <b>ClassLoader 분리 해결 (v2.2):</b>
 * </p>
 * Echo(URLClassLoader)와 Mixin(AppClassLoader)이 다른 ClassLoader를 사용하므로,
 * 이 클래스는 모든 가능한 ClassLoader의 SubProfilerHook에 callback을 등록합니다.
 * 
 * @since Echo 1.0
 * @since Echo 2.2 - Multi-ClassLoader callback registration
 */
public class SubProfilerBridge implements SubProfilerHook.ISubProfilerCallback {

    private static SubProfilerBridge INSTANCE;

    private SubProfilerBridge() {
    }

    /**
     * SubProfiler 브릿지 등록
     * EchoMod.init()에서 호출됨
     * 
     * 모든 가능한 ClassLoader의 SubProfilerHook에 callback을 등록합니다.
     */
    public static void register() {
        if (INSTANCE != null) {
            return; // Already registered
        }

        try {
            INSTANCE = new SubProfilerBridge();

            // 1. 자신의 ClassLoader의 SubProfilerHook에 등록
            SubProfilerHook.setCallback(INSTANCE);

            // 2. AppClassLoader의 SubProfilerHook에도 Reflection으로 등록
            registerToClassLoader(ClassLoader.getSystemClassLoader(), "AppClassLoader");

            // 3. Context ClassLoader에도 등록 시도
            ClassLoader contextLoader = Thread.currentThread().getContextClassLoader();
            if (contextLoader != null && contextLoader != SubProfilerBridge.class.getClassLoader()) {
                registerToClassLoader(contextLoader, "ContextClassLoader");
            }

            PulseLogger.info("Echo", "SubProfilerBridge registered with Pulse");
        } catch (Throwable t) {
            PulseLogger.error("Echo", "Failed to register SubProfilerBridge: " + t.getMessage());
            INSTANCE = null;
        }
    }

    /**
     * 특정 ClassLoader의 SubProfilerHook에 callback을 Reflection으로 등록합니다.
     */
    private static void registerToClassLoader(ClassLoader loader, String loaderName) {
        try {
            if (loader == null)
                return;

            Class<?> hookClass = loader.loadClass("com.pulse.api.profiler.SubProfilerHook");

            // 같은 클래스면 이미 등록됨
            if (hookClass == SubProfilerHook.class) {
                return;
            }

            // setCallbackObject(Object) 메서드 호출
            Method setCallbackMethod = hookClass.getMethod("setCallbackObject", Object.class);
            setCallbackMethod.invoke(null, INSTANCE);

            PulseLogger.info("Echo", "SubProfilerBridge also registered to " + loaderName
                    + " (" + loader.getClass().getSimpleName() + ")");
        } catch (ClassNotFoundException e) {
            // SubProfilerHook이 이 ClassLoader에 없음 - 무시
        } catch (NoSuchMethodException e) {
            // setCallbackObject 메서드 없음 - 구버전?
            PulseLogger.warn("Echo", "SubProfilerHook in " + loaderName + " missing setCallbackObject method");
        } catch (Exception e) {
            PulseLogger.warn("Echo", "Failed to register to " + loaderName + ": " + e.getMessage());
        }
    }

    /**
     * SubProfiler 브릿지 해제
     */
    public static void unregister() {
        SubProfilerHook.clearCallback();
        INSTANCE = null;
    }

    @Override
    public long start(String label) {
        SubProfiler.SubLabel subLabel = parseLabel(label);
        if (subLabel != null) {
            return SubProfiler.getInstance().startRaw(subLabel);
        }
        return -1;
    }

    @Override
    public void end(String label, long startTime) {
        if (startTime < 0)
            return;
        SubProfiler.SubLabel subLabel = parseLabel(label);
        if (subLabel != null) {
            SubProfiler.getInstance().endRaw(subLabel, startTime);
        }
    }

    /**
     * 문자열 라벨을 SubLabel enum으로 변환
     */
    private SubProfiler.SubLabel parseLabel(String label) {
        if (label == null)
            return null;
        try {
            return SubProfiler.SubLabel.valueOf(label);
        } catch (IllegalArgumentException e) {
            // Unknown label - 무시
            return null;
        }
    }
}
