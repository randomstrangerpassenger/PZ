package com.echo.report;

import com.echo.aggregate.TimingData;
import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.measure.SubProfiler;
import com.echo.measure.TickPhaseProfiler;
import com.echo.validation.SelfValidation;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Echo Report Quality Scorer
 * 
 * 리포트 품질을 0~100 점수로 평가합니다.
 * 품질이 낮은 리포트는 별도 폴더에 저장하거나 저장을 건너뜁니다.
 * 
 * @since Echo 0.9.0
 */
public class ReportQualityScorer {

    private static final ReportQualityScorer INSTANCE = new ReportQualityScorer();

    // 패널티 최대값
    private static final int TICK_PENALTY_MAX = 25;
    private static final int PHASE_PENALTY_MAX = 15;
    @SuppressWarnings("unused") // Reserved for Lua profiling penalties
    private static final int LUA_PENALTY_MAX = 10;
    private static final int SESSION_PENALTY_MAX = 15;
    @SuppressWarnings("unused") // Reserved for stability scoring
    private static final int STABILITY_PENALTY_MAX = 10;
    private static final int VALIDATION_PENALTY_MAX = 25;

    private ReportQualityScorer() {
    }

    public static ReportQualityScorer getInstance() {
        return INSTANCE;
    }

    /**
     * 품질 점수 계산 (0~100)
     */
    public QualityResult calculateScore(EchoProfiler profiler) {
        QualityResult result = new QualityResult();
        int score = 100;

        // 1. Tick Coverage Penalty
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        if (tickData == null || tickData.getCallCount() == 0) {
            score -= TICK_PENALTY_MAX;
            result.addIssue("no_tick_data", "critical", "No tick data collected (total_ticks = 0)");
        } else if (tickData.getCallCount() < 10) {
            score -= 15;
            result.addIssue("low_tick_count", "warning", "Very few ticks: " + tickData.getCallCount());
        } else if (tickData.getCallCount() < 100) {
            score -= 5;
            result.addIssue("short_sample", "info", "Limited tick sample: " + tickData.getCallCount());
        }

        // 2. Session Length Penalty
        long sessionMs = profiler.getSessionDurationMs();
        if (sessionMs < 3000) { // 3초 미만
            score -= SESSION_PENALTY_MAX;
            result.addIssue("session_too_short", "warning", "Session < 3 seconds: " + (sessionMs / 1000.0) + "s");
        } else if (sessionMs < 10000) { // 10초 미만
            score -= 8;
            result.addIssue("short_session", "info", "Session < 10 seconds");
        }

        // 3. Phase Coverage Penalty (DeepAnalysis가 켜진 경우만)
        EchoConfig config = EchoConfig.getInstance();
        if (config.isDeepAnalysisEnabled()) {
            TickPhaseProfiler tickPhase = TickPhaseProfiler.getInstance();
            if (tickPhase.getTotalPhaseCount() == 0) {
                score -= PHASE_PENALTY_MAX;
                result.addIssue("no_phase_data", "warning", "DeepAnalysis enabled but no phase data");
            }

            // SubProfiler 체크
            SubProfiler subProfiler = SubProfiler.getInstance();
            if (subProfiler.getEntryCount() == 0) {
                score -= 10;
                result.addIssue("no_subprofiler_data", "warning", "DeepAnalysis enabled but SubProfiler empty");
            }
        }

        // 4. Lua Profiling Penalty (Lua가 켜진 경우만)
        if (config.isLuaProfilingEnabled()) {
            // Lua가 켜졌는데 데이터가 없으면 패널티
            // (추후 LuaCallTracker 연동)
        }

        // 5. Validation Status Penalty (현재 상태로 검증)
        SelfValidation.ValidationResult validationResult = SelfValidation.getInstance().validate();
        if (validationResult != null) {
            if (validationResult.hookStatus == SelfValidation.HookStatus.MISSING) {
                score -= VALIDATION_PENALTY_MAX;
                result.addIssue("hook_missing", "critical", "Pulse hook not firing");
            } else if (validationResult.hookStatus == SelfValidation.HookStatus.PARTIAL) {
                score -= 10;
                result.addIssue("hook_partial", "warning", "Tick hook firing intermittently");
            }

            if (validationResult.freezeDetectorStatus == SelfValidation.FreezeDetectorStatus.INACTIVE) {
                score -= 5;
                result.addIssue("freeze_detector_inactive", "info", "FreezeDetector not receiving ticks");
            }
        }

        // 6. Fallback Tick Penalty
        if (config.isUsedFallbackTicks()) {
            score -= 20;
            result.addIssue("used_fallback_ticks", "warning", "Fallback ticks were used - data may be inaccurate");
        }

        result.score = Math.max(0, score);
        return result;
    }

    /**
     * 저장 여부 판단
     */
    public boolean shouldSave(int score) {
        return score >= EchoConfig.getInstance().getMinQualityToSave();
    }

    /**
     * 저장 위치 결정
     * 
     * @return "normal" or "low_quality"
     */
    public String getSaveLocation(int score) {
        int threshold = EchoConfig.getInstance().getMinQualityToSave();
        if (score < threshold) {
            return "low_quality";
        }
        return "normal";
    }

    // --- Result Class ---

    public static class QualityResult {
        public int score = 100;
        public final List<Map<String, String>> issues = new ArrayList<>();

        public void addIssue(String issue, String severity, String description) {
            Map<String, String> issueMap = new LinkedHashMap<>();
            issueMap.put("issue", issue);
            issueMap.put("severity", severity);
            issueMap.put("description", description);
            issues.add(issueMap);
        }

        public boolean hasIssues() {
            return !issues.isEmpty();
        }

        public boolean isCritical() {
            return issues.stream().anyMatch(i -> "critical".equals(i.get("severity")));
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("score", score);
            map.put("issues", issues);
            return map;
        }
    }
}
