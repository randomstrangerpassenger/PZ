package com.pulse.event;

import com.pulse.api.PerformanceAlertEvent;

/**
 * PerformanceAlertEvent 기본 구현체.
 * 
 * 성능 문제 감지 시 이 이벤트를 생성하여 발행합니다.
 * 소비자 모듈에서 수신하여 처리합니다.
 * 
 * @since 1.0.1
 */
public class DefaultPerformanceAlert implements PerformanceAlertEvent {

    private final AlertType alertType;
    private final double severity;
    private final String message;
    private final long timestamp;
    private final ThreadContext threadContext;
    private final String sourceId;
    private boolean cancelled = false;

    public DefaultPerformanceAlert(AlertType alertType, double severity, String message,
            ThreadContext threadContext, String sourceId) {
        this.alertType = alertType;
        this.severity = Math.max(0.0, Math.min(1.0, severity)); // 클램프 0.0~1.0
        this.message = message;
        this.timestamp = System.currentTimeMillis();
        this.threadContext = threadContext;
        this.sourceId = sourceId;
    }

    /**
     * 간단한 생성자 (메인 스레드 기본값)
     */
    public DefaultPerformanceAlert(AlertType alertType, double severity, String message, String sourceId) {
        this(alertType, severity, message, ThreadContext.MAIN, sourceId);
    }

    // --- PerformanceAlertEvent 구현 ---

    @Override
    public AlertType getAlertType() {
        return alertType;
    }

    @Override
    public double getSeverity() {
        return severity;
    }

    @Override
    public String getMessage() {
        return message;
    }

    @Override
    public long getTimestamp() {
        return timestamp;
    }

    @Override
    public ThreadContext getThreadContext() {
        return threadContext;
    }

    @Override
    public String getSourceId() {
        return sourceId;
    }

    // --- IPulseEvent 구현 ---

    @Override
    public String getEventName() {
        return "PerformanceAlert:" + alertType.name();
    }

    @Override
    public boolean isCancellable() {
        return true;
    }

    @Override
    public boolean isCancelled() {
        return cancelled;
    }

    @Override
    public void cancel() {
        this.cancelled = true;
    }

    // --- 유틸리티 메서드 ---
    // [REMOVED] isHighSeverity(), isCritical() - 정책 판단은 소비자 모듈 책임

    @Override
    public String toString() {
        return String.format("PerformanceAlert[type=%s, severity=%.2f, source=%s, thread=%s, msg=%s]",
                alertType, severity, sourceId, threadContext, message);
    }

    // --- Factory 메서드 ---

    /**
     * LAG_SPIKE 경보 생성
     */
    public static DefaultPerformanceAlert lagSpike(double spikeMs, double threshold, String source) {
        double severity = Math.min(1.0, spikeMs / (threshold * 3));
        String msg = String.format("Lag spike detected: %.2fms (threshold: %.2fms)", spikeMs, threshold);
        return new DefaultPerformanceAlert(AlertType.LAG_SPIKE, severity, msg, source);
    }

    /**
     * FREEZE_WARNING 경보 생성
     */
    public static DefaultPerformanceAlert freezeWarning(long freezeDurationMs, String source) {
        double severity = Math.min(1.0, freezeDurationMs / 3000.0); // 3초에 severity 1.0
        String msg = String.format("Freeze detected: %dms", freezeDurationMs);
        return new DefaultPerformanceAlert(AlertType.FREEZE_WARNING, severity, msg, source);
    }

    /**
     * MEMORY_PRESSURE 경보 생성
     */
    public static DefaultPerformanceAlert memoryPressure(double usagePercent, String source) {
        double severity = Math.max(0, (usagePercent - 70) / 30); // 70%에서 시작, 100%에서 1.0
        String msg = String.format("Memory pressure: %.1f%% used", usagePercent);
        return new DefaultPerformanceAlert(AlertType.MEMORY_PRESSURE, severity, msg, source);
    }

    /**
     * TPS_DROP 경보 생성
     */
    public static DefaultPerformanceAlert tpsDrop(double currentTps, double targetTps, String source) {
        double ratio = currentTps / targetTps;
        double severity = Math.min(1.0, Math.max(0, 1.0 - ratio));
        String msg = String.format("TPS drop: %.1f / %.1f", currentTps, targetTps);
        return new DefaultPerformanceAlert(AlertType.TPS_DROP, severity, msg, source);
    }

    /**
     * ENTITY_OVERLOAD 경보 생성
     */
    public static DefaultPerformanceAlert entityOverload(int entityCount, int threshold, String source) {
        double severity = Math.min(1.0, (double) entityCount / (threshold * 2));
        String msg = String.format("Entity overload: %d entities (threshold: %d)", entityCount, threshold);
        return new DefaultPerformanceAlert(AlertType.ENTITY_OVERLOAD, severity, msg, source);
    }
}
