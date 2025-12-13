package com.echo.validation;

import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

import com.pulse.api.profiler.TickPhaseHook;

/**
 * Echo Self-Validation Layer
 * 
 * Echo가 스스로 살아있는지 확인하는 자가 검증 시스템.
 * enable() 후 일정 시간이 지나면 자동으로 검증을 수행하여
 * Hook 누락, FreezeDetector 비활성화, SubProfiler 데이터 없음 등을 감지합니다.
 * 
 * @since Echo 0.9.0
 */
public class SelfValidation {

    private static final SelfValidation INSTANCE = new SelfValidation();

    // 검증 지연 시간 (10초 - 월드 로드 대기)
    // Note: 게임 시작 후 월드 로드까지 시간이 걸리므로 충분한 지연 필요
    private static final long VALIDATION_DELAY_MS = 10000;

    // --- Heartbeat Counters ---

    /** Tick 호출 횟수 (매 onTick() 마다 증가) */
    private final AtomicLong heartbeatCount = new AtomicLong(0);

    /** FreezeDetector.tick() 호출 횟수 */
    private final AtomicLong freezeCheckCount = new AtomicLong(0);

    // Phase 2 State (reserved for future use)
    @SuppressWarnings("unused")
    private volatile boolean usedFallbackTicks = false;

    /** SubProfiler 엔트리 수 (마지막 검증 시점) */
    @SuppressWarnings("unused")
    private volatile int subProfilerEntryCount = 0;

    // --- v0.9: Phase State Tracking ---

    /** Phase 시작 호출 횟수 */
    private final AtomicLong phaseStartCount = new AtomicLong(0);

    /** Phase 종료 호출 횟수 */
    private final AtomicLong phaseEndCount = new AtomicLong(0);

    // --- Validation State ---

    /** 마지막 검증 시간 (reserved for future use) */
    @SuppressWarnings("unused")
    private volatile long lastValidationTime = 0;

    /** 검증 결과 */
    private volatile ValidationResult lastResult = null;

    /** 검증 스케줄러 */
    private ScheduledExecutorService scheduler;

    private SelfValidation() {
        // Singleton
    }

    public static SelfValidation getInstance() {
        return INSTANCE;
    }

    // --- Heartbeat API (호출되는 쪽에서 증가) ---

    /**
     * Tick heartbeat 증가 (TickProfiler.onTick()에서 호출)
     */
    public void tickHeartbeat() {
        heartbeatCount.incrementAndGet();
    }

    /**
     * FreezeDetector check 증가 (FreezeDetector.tick()에서 호출)
     */
    public void freezeCheckHeartbeat() {
        freezeCheckCount.incrementAndGet();
    }

    /**
     * 현재 heartbeat 카운트 반환
     */
    public long getHeartbeatCount() {
        return heartbeatCount.get();
    }

    /**
     * 현재 freeze check 카운트 반환
     */
    public long getFreezeCheckCount() {
        return freezeCheckCount.get();
    }

    /**
     * v0.9: Phase 시작 heartbeat (TickPhaseBridge.startPhase()에서 호출)
     */
    public void phaseStartHeartbeat() {
        phaseStartCount.incrementAndGet();
    }

    /**
     * v0.9: Phase 종료 heartbeat (TickPhaseBridge.endPhase()에서 호출)
     */
    public void phaseEndHeartbeat() {
        phaseEndCount.incrementAndGet();
    }

    /**
     * v0.9: Phase 시작 카운트 반환
     */
    public long getPhaseStartCount() {
        return phaseStartCount.get();
    }

    /**
     * v0.9: Phase 종료 카운트 반환
     */
    public long getPhaseEndCount() {
        return phaseEndCount.get();
    }

    // --- Validation Control ---

    /**
     * 검증 스케줄 시작 (EchoProfiler.enable() 에서 호출)
     * 지정된 지연 시간 후 자동으로 validate() 실행
     */
    public synchronized void scheduleValidation() {
        // 이전 스케줄러가 있으면 종료
        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdownNow();
        }

        scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "Echo-SelfValidation");
            t.setDaemon(true);
            return t;
        });

        scheduler.schedule(this::performValidation, VALIDATION_DELAY_MS, TimeUnit.MILLISECONDS);
        System.out.println("[Echo] Self-validation scheduled in " + VALIDATION_DELAY_MS + "ms");
    }

    /**
     * 검증 수행
     */
    private void performValidation() {
        ValidationResult result = validate();
        this.lastResult = result;
        this.lastValidationTime = System.currentTimeMillis();

        // 콘솔에 결과 출력
        printValidationResult(result);
    }

    /**
     * 즉시 검증 수행 (수동 호출용)
     */
    public ValidationResult validate() {
        ValidationResult result = new ValidationResult();

        // 1. Tick Hook 검증
        long ticks = heartbeatCount.get();
        if (ticks == 0) {
            result.hookStatus = HookStatus.MISSING;
            result.addIssue(ValidationIssue.TICK_HOOK_MISSING);
        } else if (ticks < 10) {
            result.hookStatus = HookStatus.PARTIAL;
            result.addIssue(ValidationIssue.TICK_HOOK_LOW_COUNT);
        } else {
            result.hookStatus = HookStatus.OK;
        }
        result.heartbeatCount = ticks;

        // 2. FreezeDetector 검증
        long freezeChecks = freezeCheckCount.get();
        if (freezeChecks == 0) {
            result.freezeDetectorStatus = FreezeDetectorStatus.INACTIVE;
            result.addIssue(ValidationIssue.FREEZE_DETECTOR_INACTIVE);
        } else {
            result.freezeDetectorStatus = FreezeDetectorStatus.ACTIVE;
        }
        result.freezeCheckCount = freezeChecks;

        // 3. SubProfiler 검증 (DeepAnalysis가 켜진 경우만)
        if (com.echo.config.EchoConfig.getInstance().isDeepAnalysisEnabled()) {
            com.echo.measure.SubProfiler subProfiler = com.echo.measure.SubProfiler.getInstance();
            int entryCount = subProfiler.getEntryCount();
            this.subProfilerEntryCount = entryCount;

            if (entryCount == 0) {
                result.subProfilerStatus = SubProfilerStatus.NO_DATA;
                result.addIssue(ValidationIssue.SUBPROFILER_NO_DATA);
            } else {
                result.subProfilerStatus = SubProfilerStatus.OK;
            }
            result.subProfilerEntryCount = entryCount;
        } else {
            result.subProfilerStatus = SubProfilerStatus.DISABLED;
        }

        // 4. v0.9: Phase State 검증
        result.phaseStartCount = phaseStartCount.get();
        result.phaseEndCount = phaseEndCount.get();

        // Phase Hook에서 발생한 에러 검사
        int phaseErrors = TickPhaseHook.getPhaseErrorCount();
        result.phaseErrorCount = phaseErrors;

        if (phaseErrors > 0) {
            result.phaseStatus = PhaseStatus.ERRORS;
            result.addIssue(ValidationIssue.PHASE_SEQUENCE_ERRORS);
        } else if (phaseStartCount.get() == 0 && heartbeatCount.get() > 60) {
            // 60틱 이상 지났는데 phase가 하나도 없음
            result.phaseStatus = PhaseStatus.NO_PHASES;
            result.addIssue(ValidationIssue.NO_PHASE_DATA);
        } else if (phaseStartCount.get() != phaseEndCount.get()) {
            // Start/End 불일치 (Phase 누수)
            result.phaseStatus = PhaseStatus.MISMATCH;
            result.addIssue(ValidationIssue.PHASE_COUNT_MISMATCH);
        } else {
            result.phaseStatus = PhaseStatus.OK;
        }

        // 5. v0.9: Pulse Contract 검증
        PulseContractVerifier contract = PulseContractVerifier.getInstance();
        result.contractViolated = contract.isViolated();
        result.tickMissing = contract.isTickMissing();
        if (contract.isViolated()) {
            result.addIssue(ValidationIssue.PULSE_CONTRACT_VIOLATED);
        }

        result.validationTime = System.currentTimeMillis();
        return result;
    }

    /**
     * 검증 결과 콘솔 출력
     */
    private void printValidationResult(ValidationResult result) {
        System.out.println("\n[Echo] ══════════════════════════════════════");
        System.out.println("[Echo]          SELF-VALIDATION RESULT");
        System.out.println("[Echo] ══════════════════════════════════════");

        // Hook Status
        String hookIcon = result.hookStatus == HookStatus.OK ? "✓"
                : result.hookStatus == HookStatus.PARTIAL ? "⚠" : "✗";
        System.out.printf("[Echo] %s Hook Status: %s (heartbeat: %d)%n",
                hookIcon, result.hookStatus, result.heartbeatCount);

        // FreezeDetector Status
        String freezeIcon = result.freezeDetectorStatus == FreezeDetectorStatus.ACTIVE ? "✓" : "✗";
        System.out.printf("[Echo] %s FreezeDetector: %s (checks: %d)%n",
                freezeIcon, result.freezeDetectorStatus, result.freezeCheckCount);

        // SubProfiler Status
        if (result.subProfilerStatus != SubProfilerStatus.DISABLED) {
            String subIcon = result.subProfilerStatus == SubProfilerStatus.OK ? "✓" : "✗";
            System.out.printf("[Echo] %s SubProfiler: %s (entries: %d)%n",
                    subIcon, result.subProfilerStatus, result.subProfilerEntryCount);
        }

        // Issues
        if (!result.issues.isEmpty()) {
            System.out.println("[Echo] ──────────────────────────────────────");
            for (ValidationIssue issue : result.issues) {
                System.out.printf("[Echo] ⚠ %s: %s%n", issue.name(), issue.getDescription());
            }
        }

        // Critical Error: Hook Missing
        if (result.hookStatus == HookStatus.MISSING) {
            System.err.println("[Echo] ══════════════════════════════════════");
            System.err.println("[Echo] ERROR: Tick hook not firing!");
            System.err.println("[Echo] Pulse hook may be missing or misconfigured.");
            System.err.println("[Echo] total_ticks will be 0 in the report.");
            System.err.println("[Echo] ══════════════════════════════════════");
        }

        System.out.println("[Echo] ══════════════════════════════════════\n");
    }

    /**
     * 카운터 초기화 (세션 리셋 시)
     */
    public void reset() {
        heartbeatCount.set(0);
        freezeCheckCount.set(0);
        phaseStartCount.set(0);
        phaseEndCount.set(0);
        subProfilerEntryCount = 0;
        lastValidationTime = 0;
        lastResult = null;
    }

    /**
     * 스케줄러 종료 (EchoProfiler.disable() 에서 호출)
     */
    public synchronized void shutdown() {
        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdownNow();
            scheduler = null;
        }
    }

    /**
     * 마지막 검증 결과
     */
    public ValidationResult getLastResult() {
        return lastResult;
    }

    /**
     * 보고서용 Map 생성
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        // 리포트 생성 시 항상 최신 검증 수행 (캐시된 초기 결과는 월드 로드 전일 수 있음)
        ValidationResult result = validate();

        map.put("hook_status", result.hookStatus.name());
        map.put("heartbeat_count", result.heartbeatCount);

        // Data Sufficiency Check (Phase 2.3)
        if (result.heartbeatCount < 10) {
            map.put("min_required_data", "INSUFFICIENT");
        } else if (result.heartbeatCount < 100) {
            map.put("min_required_data", "WARMUP");
        } else {
            map.put("min_required_data", "OK");
        }
        map.put("freeze_detector", result.freezeDetectorStatus.name());
        map.put("freeze_check_count", result.freezeCheckCount);
        map.put("subprofiler_status", result.subProfilerStatus.name());
        map.put("subprofiler_entry_count", result.subProfilerEntryCount);

        if (result.validationTime > 0) {
            map.put("validation_time", java.time.Instant.ofEpochMilli(result.validationTime).toString());
        }

        // Issues 목록
        List<String> issueList = new ArrayList<>();
        for (ValidationIssue issue : result.issues) {
            issueList.add(issue.name());
        }
        if (!issueList.isEmpty()) {
            map.put("issues", issueList);
        }

        // Fallback Tick 정보 (Echo 0.9.0)
        FallbackTickEmitter fallback = FallbackTickEmitter.getInstance();
        map.put("used_fallback_ticks", com.echo.config.EchoConfig.getInstance().isUsedFallbackTicks());
        if (fallback.isFallbackActive()) {
            map.put("fallback_tick_count", fallback.getFallbackTickCount());
        }

        // v0.9: Phase State 정보
        map.put("phase_status", result.phaseStatus != null ? result.phaseStatus.name() : "UNKNOWN");
        map.put("phase_start_count", result.phaseStartCount);
        map.put("phase_end_count", result.phaseEndCount);
        map.put("phase_error_count", result.phaseErrorCount);

        // v0.9: Pulse Contract 정보
        map.put("pulse_contract_violated", result.contractViolated);
        map.put("tick_missing", result.tickMissing);

        return map;
    }

    // --- Inner Classes ---

    public static class ValidationResult {
        public HookStatus hookStatus = HookStatus.UNKNOWN;
        public FreezeDetectorStatus freezeDetectorStatus = FreezeDetectorStatus.UNKNOWN;
        public SubProfilerStatus subProfilerStatus = SubProfilerStatus.UNKNOWN;

        public long heartbeatCount = 0;
        public long freezeCheckCount = 0;
        public int subProfilerEntryCount = 0;
        public long validationTime = 0;

        // v0.9: Phase State
        public PhaseStatus phaseStatus = PhaseStatus.UNKNOWN;
        public long phaseStartCount = 0;
        public long phaseEndCount = 0;
        public int phaseErrorCount = 0;

        // v0.9: Pulse Contract
        public boolean contractViolated = false;
        public boolean tickMissing = false;

        public final List<ValidationIssue> issues = new ArrayList<>();

        public void addIssue(ValidationIssue issue) {
            issues.add(issue);
        }

        public boolean hasIssues() {
            return !issues.isEmpty();
        }

        public boolean isCritical() {
            return hookStatus == HookStatus.MISSING;
        }
    }

    public enum HookStatus {
        OK, // 정상 (heartbeat > 10)
        PARTIAL, // 부분 작동 (0 < heartbeat < 10)
        MISSING, // 누락 (heartbeat == 0)
        UNKNOWN
    }

    public enum FreezeDetectorStatus {
        ACTIVE, // 정상 작동 중
        INACTIVE, // 비활성화됨
        UNKNOWN
    }

    public enum SubProfilerStatus {
        OK, // 데이터 있음
        NO_DATA, // DeepAnalysis ON인데 데이터 없음
        DISABLED, // DeepAnalysis OFF
        UNKNOWN
    }

    public enum ValidationIssue {
        TICK_HOOK_MISSING("Pulse tick hook is not firing. Check Pulse installation."),
        TICK_HOOK_LOW_COUNT("Very few ticks recorded. Session may be too short."),
        FREEZE_DETECTOR_INACTIVE("FreezeDetector is not receiving tick updates."),
        SUBPROFILER_NO_DATA("DeepAnalysis enabled but no SubProfiler data collected."),
        // v0.9: Phase 검증 이슈
        PHASE_SEQUENCE_ERRORS("Phase sequence errors detected (startPhase/endPhase mismatch)."),
        NO_PHASE_DATA("No phase data received despite active tick hook."),
        PHASE_COUNT_MISMATCH("Phase start/end count mismatch (possible phase leak)."),
        PULSE_CONTRACT_VIOLATED("Pulse tick contract violated (abnormal deltaTime detected).");

        private final String description;

        ValidationIssue(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }

    // v0.9: Phase Status Enum
    public enum PhaseStatus {
        OK, // Phase 정상 동작
        NO_PHASES, // Phase 데이터 없음
        MISMATCH, // Start/End 불일치
        ERRORS, // 시퀀스 에러 발생
        UNKNOWN
    }
}
