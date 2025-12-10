package com.echo.pulse;

import com.echo.measure.TickPhaseProfiler;
import com.pulse.api.profiler.TickPhaseHook;

/**
 * TickPhase Pulse 연동
 * 
 * Echo 초기화 시 Pulse의 TickPhaseHook에 콜백을 등록하여
 * Pulse Mixin에서 TickPhaseProfiler를 호출할 수 있게 합니다.
 * 
 * @since Echo 1.0
 */
public class TickPhaseBridge implements TickPhaseHook.ITickPhaseCallback {

    private static TickPhaseBridge INSTANCE;

    private TickPhaseBridge() {
    }

    /**
     * TickPhase 브릿지 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (INSTANCE != null) {
            return;
        }
        INSTANCE = new TickPhaseBridge();
        TickPhaseHook.setCallback(INSTANCE);
        System.out.println("[Echo] TickPhaseBridge registered with Pulse");
    }

    /**
     * TickPhase 브릿지 해제
     */
    public static void unregister() {
        TickPhaseHook.clearCallback();
        INSTANCE = null;
    }

    @Override
    public long startPhase(String phase) {
        TickPhaseProfiler.TickPhase tickPhase = parsePhase(phase);
        if (tickPhase != null) {
            return TickPhaseProfiler.getInstance().startPhaseRaw(tickPhase);
        }
        return -1;
    }

    @Override
    public void endPhase(String phase, long startTime) {
        if (startTime < 0)
            return;
        TickPhaseProfiler.TickPhase tickPhase = parsePhase(phase);
        if (tickPhase != null) {
            TickPhaseProfiler.getInstance().endPhaseRaw(tickPhase, startTime);
        }
    }

    @Override
    public void onTickComplete() {
        TickPhaseProfiler.getInstance().onTickComplete();
    }

    /**
     * 문자열을 TickPhase enum으로 변환
     */
    private TickPhaseProfiler.TickPhase parsePhase(String phase) {
        if (phase == null)
            return null;
        try {
            return TickPhaseProfiler.TickPhase.valueOf(phase);
        } catch (IllegalArgumentException e) {
            return null;
        }
    }
}
