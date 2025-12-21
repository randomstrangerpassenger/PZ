package com.echo.pulse;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.measure.ProfilingScope;

/**
 * 틱 프로파일러
 * 
 * 게임 틱 시작/종료 시점을 측정합니다.
 * Pulse GameTickStartEvent/GameTickEndEvent와 연동됩니다.
 * 
 * @since Echo 0.9 - Added Start/End event-based profiling
 */
public class TickProfiler {

    private final EchoProfiler profiler = EchoProfiler.getInstance();

    // 현재 활성 스코프
    private ProfilingScope currentScope = null;

    // 틱 카운터
    private long tickCount = 0;

    // 스파이크 감지 임계값 (마이크로초)
    private long spikeThresholdMicros = 33_000; // 33ms (2 프레임)

    // 마지막 틱 시간
    private long lastTickStartTime = 0;
    private long lastTickDuration = 0;

    /**
     * 틱 완료 시 호출 (GameTickEvent의 deltaTime 기반)
     * 
     * GameTickEvent는 틱 완료 후 발생하므로 Pre/Post 패턴이 아닌
     * 단일 이벤트로 deltaTime을 직접 기록합니다.
     * 
     * @param deltaTimeMs 틱 소요 시간 (밀리초)
     */
    public void onTick(float deltaTimeMs) {
        // Self-Validation: heartbeat 증가 (Echo 0.9.0)
        com.echo.validation.SelfValidation.getInstance().tickHeartbeat();

        // 디버그: 매 100번째 틱마다 상태 출력
        if (tickCount % 100 == 0) {
            System.out.printf("[Echo/DEBUG] onTick called: tick=%d, deltaMs=%.2f, profilerEnabled=%b%n",
                    tickCount, deltaTimeMs, profiler.isEnabled());
        }

        if (!profiler.isEnabled()) {
            // 비활성화 상태면 최초 1회만 경고
            if (tickCount == 0) {
                System.out.println("[Echo/WARN] TickProfiler.onTick(): Profiler is DISABLED!");
            }
            tickCount++;
            return;
        }

        long durationMicros = (long) (deltaTimeMs * 1000);
        long durationNanos = durationMicros * 1000;

        tickCount++;
        lastTickDuration = durationMicros;

        // TimingData에 직접 샘플 추가 (Raw API와 동일한 방식)
        profiler.getTimingData(ProfilingPoint.TICK).addSample(durationNanos, null);

        // Histogram에 기록
        // Histogram에 기록 (Warmup 체크: 3초)
        if (profiler.getSessionDurationMs() < 3000) {
            profiler.getTickHistogram().addWarmupSample(durationMicros);
        } else {
            profiler.getTickHistogram().addSample(durationMicros);
        }

        // 스파이크 로그에 기록
        profiler.getSpikeLog().logSpike(durationMicros, ProfilingPoint.TICK, null);

        // 스파이크 감지
        if (durationMicros > spikeThresholdMicros) {
            onSpikeDetected(durationMicros);
        }

        // 첫 틱에서 정상 동작 확인
        if (tickCount == 1) {
            System.out.println("[Echo] ✓ First tick recorded successfully!");
        }
    }

    // --- v0.9: Start/End Event-Based Profiling (Primary API) ---

    /**
     * 틱 시작 시 호출 (GameTickStartEvent)
     * 타이밍은 GameTickEndEvent의 durationNanos로 측정하므로
     * 이 메서드는 contract 검증용으로만 사용됩니다.
     */
    public void onTickStart() {
        lastTickStartTime = System.nanoTime();
        // Contract verification은 PulseContractVerifier에서 처리
    }

    /**
     * 정밀 틱 소요 시간 기록 (GameTickEndEvent)
     * Pulse에서 직접 계산한 나노초 단위의 정밀 타이밍을 사용합니다.
     * 
     * @param durationNanos 틱 소요 시간 (나노초) - Pulse에서 계산됨
     */
    public void recordTickDuration(long durationNanos) {
        // v0.9.1: Real tick 수신 알림 - Fallback 자동 비활성화
        com.echo.validation.FallbackTickEmitter.getInstance().onRealTickReceived();

        // Self-Validation: heartbeat 증가
        com.echo.validation.SelfValidation.getInstance().tickHeartbeat();

        if (!profiler.isEnabled()) {
            if (tickCount == 0) {
                System.out.println("[Echo/WARN] TickProfiler: Profiler is DISABLED!");
            }
            tickCount++;
            return;
        }

        tickCount++;
        long durationMicros = durationNanos / 1000;
        lastTickDuration = durationMicros;

        // TimingData에 직접 샘플 추가
        profiler.getTimingData(ProfilingPoint.TICK).addSample(durationNanos, null);

        // Histogram에 기록 (Warmup 체크: 3초)
        if (profiler.getSessionDurationMs() < 3000) {
            profiler.getTickHistogram().addWarmupSample(durationMicros);
        } else {
            profiler.getTickHistogram().addSample(durationMicros);
        }

        // 스파이크 로그에 기록
        profiler.getSpikeLog().logSpike(durationMicros, ProfilingPoint.TICK, null);

        // 스파이크 감지
        if (durationMicros > spikeThresholdMicros) {
            onSpikeDetected(durationMicros);
        }

        // 첫 틱 / 100번째 틱 로그
        if (tickCount == 1) {
            System.out.println("[Echo] ✓ First tick recorded via Start/End events!");
        } else if (tickCount % 100 == 0) {
            System.out.printf("[Echo/DEBUG] recordTickDuration: tick=%d, durationMs=%.2f%n",
                    tickCount, durationNanos / 1_000_000.0);
        }
    }

    /**
     * 틱 시작 시 호출 (Legacy - 수동 계측용)
     * 
     * @deprecated Use onTick(float deltaTimeMs) instead
     */
    @Deprecated
    public void onTickPre() {
        if (!profiler.isEnabled())
            return;

        lastTickStartTime = System.nanoTime();
        currentScope = profiler.scope(ProfilingPoint.TICK);
        tickCount++;
    }

    /**
     * 틱 종료 시 호출 (Legacy - 수동 계측용)
     * 
     * @deprecated Use onTick(float deltaTimeMs) instead
     */
    @Deprecated
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

        // Phase 3.2: Slow Tick 발생 시 Detailed Window 자동 트리거
        try {
            com.echo.lua.DetailedWindowManager.getInstance()
                    .trigger(com.echo.lua.DetailedWindowManager.DetailedTrigger.SLOW_TICK);
        } catch (Exception ignored) {
            // DetailedWindowManager 초기화 전이면 무시
        }
    }

    // --- 설정 및 조회 ---

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
