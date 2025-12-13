package com.echo.debug;

import com.echo.aggregate.TickHistogram;
import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.measure.TickPhaseProfiler;
import com.echo.measure.TickPhaseProfiler.TickPhase;
import com.echo.validation.PulseContractVerifier;

import java.util.*;

/**
 * 통합 DebugOverlay 데이터 제공자
 * 
 * Fuse/Nerve에서 사용할 수 있는 디버그 정보를 수집하고 제공합니다.
 * 실제 UI 렌더링은 Fuse/Nerve에서 담당하고, 이 클래스는 데이터만 제공합니다.
 * 
 * @since Echo 0.9 (Phase 4 DX)
 */
public final class DebugOverlayData {

    private static final DebugOverlayData INSTANCE = new DebugOverlayData();

    private DebugOverlayData() {
    }

    public static DebugOverlayData getInstance() {
        return INSTANCE;
    }

    // --- Pulse 틱 상태 ---

    /**
     * Pulse 계약 상태 반환
     */
    public String getPulseContractStatus() {
        return PulseContractVerifier.getInstance().getStatusForDisplay();
    }

    /**
     * 총 위반 횟수
     */
    public long getViolationCount() {
        return PulseContractVerifier.getInstance().getTotalViolationCount();
    }

    /**
     * 마지막 위반 메시지
     */
    public String getLastViolation() {
        String msg = PulseContractVerifier.getInstance().getLastViolation();
        return msg != null ? msg : "";
    }

    // --- 페이즈 CPU 사용량 상위 3개 ---

    /**
     * CPU 사용량 상위 3개 페이즈 반환
     * 
     * @return [{phase: "World Update", percent: 45.2}, ...]
     */
    public List<Map<String, Object>> getTopPhases() {
        List<Map<String, Object>> result = new ArrayList<>();

        TickPhaseProfiler profiler = TickPhaseProfiler.getInstance();
        Map<TickPhase, Double> percentages = profiler.getPhasePercentages();

        // 비율 기준으로 정렬
        List<Map.Entry<TickPhase, Double>> sorted = new ArrayList<>(percentages.entrySet());
        sorted.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));

        // 상위 3개
        int count = 0;
        for (Map.Entry<TickPhase, Double> entry : sorted) {
            if (count >= 3)
                break;
            if (entry.getValue() <= 0)
                continue;

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("phase", entry.getKey().getDisplayName());
            item.put("percent", Math.round(entry.getValue() * 10) / 10.0);
            item.put("color", entry.getKey().getColor());
            result.add(item);
            count++;
        }

        return result;
    }

    // --- Echo 품질 점수 ---

    /**
     * Echo Histogram 품질 점수 (0-100)
     */
    public int getQualityScore() {
        TickHistogram histogram = EchoProfiler.getInstance().getTickHistogram();
        return histogram != null ? histogram.getQualityScore() : 0;
    }

    /**
     * 품질 등급 반환
     */
    public String getQualityGrade() {
        int score = getQualityScore();
        if (score >= 90)
            return "A";
        if (score >= 80)
            return "B";
        if (score >= 70)
            return "C";
        if (score >= 60)
            return "D";
        return "F";
    }

    /**
     * P50/P95/P99 반환
     */
    public Map<String, Double> getPercentiles() {
        Map<String, Double> result = new LinkedHashMap<>();
        TickHistogram histogram = EchoProfiler.getInstance().getTickHistogram();

        if (histogram != null) {
            result.put("p50", Math.round(histogram.getP50() * 100) / 100.0);
            result.put("p95", Math.round(histogram.getP95() * 100) / 100.0);
            result.put("p99", Math.round(histogram.getP99() * 100) / 100.0);
        }

        return result;
    }

    // --- FallbackTickEmitter 상태 ---

    /**
     * FallbackTickEmitter 사용 여부
     */
    public boolean isFallbackTickActive() {
        return EchoConfig.getInstance().isUsedFallbackTicks();
    }

    /**
     * FallbackTick 간격 (ms)
     */
    public long getFallbackTickIntervalMs() {
        return EchoConfig.getInstance().getFallbackTickIntervalMs();
    }

    // --- 통합 요약 ---

    /**
     * Fuse/Nerve 디버그 화면에 표시할 전체 상태 Map
     */
    public Map<String, Object> getSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();

        // Pulse Contract
        summary.put("pulse_status", getPulseContractStatus());
        summary.put("violations", getViolationCount());

        // Echo Quality
        summary.put("quality_score", getQualityScore());
        summary.put("quality_grade", getQualityGrade());
        summary.put("percentiles", getPercentiles());

        // Top Phases
        summary.put("top_phases", getTopPhases());

        // Fallback
        summary.put("fallback_active", isFallbackTickActive());
        if (isFallbackTickActive()) {
            summary.put("fallback_interval_ms", getFallbackTickIntervalMs());
        }

        return summary;
    }

    /**
     * 콘솔 출력용 한 줄 요약
     */
    public String getOneLiner() {
        return String.format("Pulse:%s | Quality:%s(%d) | Top:%s | Fallback:%s",
                getPulseContractStatus(),
                getQualityGrade(),
                getQualityScore(),
                getTopPhases().isEmpty() ? "N/A" : getTopPhases().get(0).get("phase"),
                isFallbackTickActive() ? "ON" : "OFF");
    }
}
