package com.echo.pulse;

import com.echo.measure.SubProfiler;
import com.pulse.api.profiler.SubProfilerHook;

/**
 * SubProfiler Pulse 연동
 * 
 * Echo 초기화 시 Pulse의 SubProfilerHook에 콜백을 등록하여
 * Pulse Mixin에서 SubProfiler를 호출할 수 있게 합니다.
 * 
 * @since Echo 1.0
 */
public class SubProfilerBridge implements SubProfilerHook.ISubProfilerCallback {

    private static SubProfilerBridge INSTANCE;

    private SubProfilerBridge() {
    }

    /**
     * SubProfiler 브릿지 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (INSTANCE != null) {
            return;
        }
        INSTANCE = new SubProfilerBridge();
        SubProfilerHook.setCallback(INSTANCE);
        System.out.println("[Echo] SubProfilerBridge registered with Pulse");
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
