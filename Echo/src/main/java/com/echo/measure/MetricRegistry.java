package com.echo.measure;

import com.echo.aggregate.SpikeLog;
import com.echo.aggregate.TickHistogram;
import com.echo.history.MetricCollector;

/**
 * MetricRegistry - 비핫패스 메트릭 저장소
 * 
 * Phase 1-A: EchoProfiler에서 비핫패스 필드만 분리
 * 
 * <p>
 * 핫패스 필드 (`timingRegistry`)는 EchoProfiler에 유지됩니다.
 * v3.1 조건: 핫패스 접근 경로 동등성 유지
 * </p>
 * 
 * <p>
 * 포함된 필드:
 * </p>
 * <ul>
 * <li>{@link TickHistogram} - 틱 히스토그램</li>
 * <li>{@link SpikeLog} - 스파이크 로그</li>
 * <li>{@link MetricCollector} - 메트릭 수집기</li>
 * </ul>
 */
public class MetricRegistry {

    private final TickHistogram tickHistogram;
    private final SpikeLog spikeLog;
    private final MetricCollector metricCollector;

    /**
     * 기본 생성자 - 새 인스턴스 생성
     */
    public MetricRegistry() {
        this.tickHistogram = new TickHistogram();
        this.spikeLog = new SpikeLog();
        this.metricCollector = new MetricCollector();
    }

    /**
     * 의존성 주입용 생성자
     * 
     * @param tickHistogram   틱 히스토그램
     * @param spikeLog        스파이크 로그
     * @param metricCollector 메트릭 수집기
     */
    public MetricRegistry(TickHistogram tickHistogram, SpikeLog spikeLog, MetricCollector metricCollector) {
        this.tickHistogram = tickHistogram;
        this.spikeLog = spikeLog;
        this.metricCollector = metricCollector;
    }

    /**
     * 틱 히스토그램 조회
     * 
     * @return TickHistogram 인스턴스
     */
    public TickHistogram getTickHistogram() {
        return tickHistogram;
    }

    /**
     * 스파이크 로그 조회
     * 
     * @return SpikeLog 인스턴스
     */
    public SpikeLog getSpikeLog() {
        return spikeLog;
    }

    /**
     * 메트릭 수집기 조회
     * 
     * @return MetricCollector 인스턴스
     */
    public MetricCollector getMetricCollector() {
        return metricCollector;
    }

    /**
     * 모든 메트릭 리셋
     */
    public void reset() {
        tickHistogram.reset();
        spikeLog.reset();
        // MetricCollector has no reset - it's append-only history
    }

    /**
     * 틱 샘플 기록 (비핫패스)
     * 
     * <p>
     * EchoProfiler.pop()에서 TICK 포인트일 때만 호출됩니다.
     * </p>
     * 
     * @param elapsedMicros 경과 시간 (마이크로초)
     */
    public void recordTickSample(long elapsedMicros) {
        tickHistogram.addSample(elapsedMicros);
    }

    /**
     * 스파이크 기록 (비핫패스)
     * 
     * @param elapsedMicros 경과 시간 (마이크로초)
     * @param point         프로파일링 포인트
     * @param label         커스텀 라벨 (nullable)
     */
    public void logSpike(long elapsedMicros, ProfilingPoint point, String label) {
        spikeLog.logSpike(elapsedMicros, point, label);
    }
}
