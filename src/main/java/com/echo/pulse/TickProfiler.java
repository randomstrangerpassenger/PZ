package com.echo.pulse;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

/**
 * 틱 프로파일러
 * 
 * 게임 틱 시작/종료 시점을 측정합니다.
 * Pulse OnTick 이벤트와 연동됩니다.
 */
public class TickProfiler {

    private final EchoProfiler profiler = EchoProfiler.getInstance();

    // 현재 활성 스코프
    private EchoProfiler.ProfilingScope currentScope = null;

    // 틱 카운터
    private long tickCount = 0;

    // 스파이크 감지 임계값 (마이크로초)
    private long spikeThresholdMicros = 33_000; // 33ms (2 프레임)

    // 마지막 틱 시간
    private long lastTickStartTime = 0;
    private long lastTickDuration = 0;

    /**
     * 틱 시작 시 호출
     */
    public void onTickPre() {
        if (!profiler.isEnabled())
            return;

        lastTickStartTime = System.nanoTime();
        currentScope = profiler.scope(ProfilingPoint.TICK);
        tickCount++;
    }

    /**
     * 틱 종료 시 호출
     */
    public void onTickPost() {
        if (currentScope == null)
            return;

        currentScope.close();
        currentScope = null;

        // 틱 시간 계산
        long elapsed = System.nanoTime() - lastTickStartTime;
        lastTickDuration = elapsed / 1000; // 마이크로초

        // 스파이크 감지
        if (lastTickDuration > spikeThresholdMicros) {
            onSpikeDetected(lastTickDuration);
        }
    }

    /**
     * 스파이크 감지 시 호출
     */
    private void onSpikeDetected(long durationMicros) {
        double durationMs = durationMicros / 1000.0;
        System.out.printf("[Echo] ⚠ SPIKE DETECTED: Tick #%d took %.2f ms (threshold: %.2f ms)%n",
                tickCount, durationMs, spikeThresholdMicros / 1000.0);
    }

    // ============================================================
    // 설정 및 조회
    // ============================================================

    /**
     * 스파이크 임계값 설정 (밀리초)
     */
    public void setSpikeThresholdMs(double thresholdMs) {
        this.spikeThresholdMicros = (long) (thresholdMs * 1000);
        System.out.printf("[Echo] Spike threshold set to %.2f ms%n", thresholdMs);
    }

    /**
     * 현재 스파이크 임계값 (밀리초)
     */
    public double getSpikeThresholdMs() {
        return spikeThresholdMicros / 1000.0;
    }

    /**
     * 총 틱 카운트
     */
    public long getTickCount() {
        return tickCount;
    }

    /**
     * 마지막 틱 시간 (마이크로초)
     */
    public long getLastTickDurationMicros() {
        return lastTickDuration;
    }

    /**
     * 마지막 틱 시간 (밀리초)
     */
    public double getLastTickDurationMs() {
        return lastTickDuration / 1000.0;
    }

    /**
     * 카운터 초기화
     */
    public void reset() {
        tickCount = 0;
        lastTickDuration = 0;
    }
}
