package com.pulse.api.lua;

import com.pulse.api.InternalAPI;
import com.pulse.api.PublicAPI;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lua 실행 시간 Budget 관리자.
 * Nerve같은 Lua 최적화 모드가 Lua 실행 시간을 제어할 수 있습니다.
 * 
 * <pre>
 * // 사용 예시
 * LuaBudgetManager budget = LuaBudgetManager.getInstance();
 * 
 * // 틱당 5ms 예산 설정
 * budget.setBudget("nerve.tick", 5000); // 마이크로초
 * 
 * // Fallback 핸들러 등록
 * budget.setFallbackHandler("nerve.tick", () -> {
 *     System.out.println("Budget exceeded, skipping non-critical tasks");
 * });
 * 
 * // 실행
 * try (LuaExecutionContext ctx = budget.beginExecution("nerve.tick")) {
 *     while (ctx.hasRemainingBudget()) {
 *         // Lua 작업 수행
 *         luaBridge.call("SomeFunction");
 *         ctx.checkpoint();
 *     }
 * }
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public final class LuaBudgetManager {

    private static final LuaBudgetManager INSTANCE = new LuaBudgetManager();

    // ═══════════════════════════════════════════════════════════════
    // 표준 컨텍스트 ID 상수 (v1.1.0)
    // ═══════════════════════════════════════════════════════════════

    /** OnTick 이벤트 컨텍스트 */
    public static final String CTX_ON_TICK = "lua.event.OnTick";

    /** OnPlayerUpdate 이벤트 컨텍스트 */
    public static final String CTX_ON_PLAYER_UPDATE = "lua.event.OnPlayerUpdate";

    /** OnGameTimeTick 이벤트 컨텍스트 */
    public static final String CTX_ON_GAME_TIME_TICK = "lua.event.OnGameTimeTick";

    /** OnContainerUpdate 이벤트 컨텍스트 */
    public static final String CTX_ON_CONTAINER_UPDATE = "lua.event.OnContainerUpdate";

    /** OnZombieDead 이벤트 컨텍스트 */
    public static final String CTX_ON_ZOMBIE_DEAD = "lua.event.OnZombieDead";

    /** OnRenderTick 이벤트 컨텍스트 */
    public static final String CTX_ON_RENDER_TICK = "lua.event.OnRenderTick";

    // ═══════════════════════════════════════════════════════════════
    // Fast-path 토글 (Nerve 활성화 전에는 오버헤드 최소화)
    // ═══════════════════════════════════════════════════════════════

    private static volatile boolean budgetEnforcementEnabled = false;

    /**
     * Budget 강제 적용 활성화 여부.
     * Nerve가 로드되면 true로 설정됨.
     * 
     * @return 활성화되어 있으면 true
     */
    public static boolean isBudgetEnforcementEnabled() {
        return budgetEnforcementEnabled;
    }

    /**
     * Budget 강제 적용 활성화/비활성화.
     * 
     * @param enabled 활성화 여부
     */
    public static void enableBudgetEnforcement(boolean enabled) {
        budgetEnforcementEnabled = enabled;
        System.out.println("[LuaBudgetManager] Budget enforcement: " + (enabled ? "ENABLED" : "DISABLED"));
    }

    /**
     * 모드별 컨텍스트 ID 생성 헬퍼.
     * 
     * @param modId     모드 ID
     * @param eventName 이벤트 이름
     * @return 컨텍스트 ID (예: "lua.mod.mymod.OnTick")
     */
    public static String modContext(String modId, String eventName) {
        return "lua.mod." + modId + "." + eventName;
    }

    // ═══════════════════════════════════════════════════════════════
    // 내부 상태
    // ═══════════════════════════════════════════════════════════════

    // 컨텍스트별 설정
    private final Map<String, BudgetConfig> configs = new ConcurrentHashMap<>();

    // 컨텍스트별 통계
    private final Map<String, LuaBudgetStats> stats = new ConcurrentHashMap<>();

    private LuaBudgetManager() {
    }

    /**
     * 싱글톤 인스턴스 반환.
     */
    public static LuaBudgetManager getInstance() {
        return INSTANCE;
    }

    // ═══════════════════════════════════════════════════════════════
    // Budget 설정
    // ═══════════════════════════════════════════════════════════════

    /**
     * Budget 설정.
     * 
     * @param contextId    컨텍스트 ID (예: "nerve.tick", "mymod.update")
     * @param budgetMicros 예산 (마이크로초)
     */
    public void setBudget(String contextId, long budgetMicros) {
        configs.computeIfAbsent(contextId, k -> new BudgetConfig()).budgetMicros = budgetMicros;

        // 통계도 초기화
        stats.computeIfAbsent(contextId, k -> new LuaBudgetStats());
    }

    /**
     * Budget 조회.
     * 
     * @param contextId 컨텍스트 ID
     * @return 설정된 예산 (마이크로초), 없으면 -1
     */
    public long getBudget(String contextId) {
        BudgetConfig config = configs.get(contextId);
        return config != null ? config.budgetMicros : -1;
    }

    /**
     * 남은 Budget 조회.
     * 활성 컨텍스트가 없으면 전체 budget 반환.
     * 
     * @param contextId 컨텍스트 ID
     * @return 남은 예산 (마이크로초)
     */
    public long getRemainingBudget(String contextId) {
        BudgetConfig config = configs.get(contextId);
        if (config == null)
            return -1;

        if (config.activeContext != null) {
            return config.activeContext.getRemainingMicros();
        }
        return config.budgetMicros;
    }

    // ═══════════════════════════════════════════════════════════════
    // 실행 컨텍스트
    // ═══════════════════════════════════════════════════════════════

    /**
     * 실행 컨텍스트 시작.
     * try-with-resources로 사용 권장.
     * 
     * @param contextId 컨텍스트 ID
     * @return 실행 컨텍스트
     */
    public LuaExecutionContext beginExecution(String contextId) {
        BudgetConfig config = configs.computeIfAbsent(contextId, k -> {
            BudgetConfig c = new BudgetConfig();
            c.budgetMicros = 10_000; // 기본 10ms
            return c;
        });

        LuaExecutionContext ctx = new LuaExecutionContext(
                contextId, config.budgetMicros, this);

        config.activeContext = ctx;
        return ctx;
    }

    /**
     * 컨텍스트 종료 (내부용).
     */
    @InternalAPI
    void endExecution(LuaExecutionContext ctx) {
        BudgetConfig config = configs.get(ctx.getContextId());
        if (config != null) {
            config.activeContext = null;

            // 통계 업데이트
            updateStats(ctx);

            // 예산 초과 시 fallback 호출
            if (ctx.getElapsedMicros() > config.budgetMicros && config.fallbackHandler != null) {
                try {
                    config.fallbackHandler.run();
                } catch (Exception e) {
                    System.err.println("[LuaBudgetManager] Fallback failed: " + e.getMessage());
                }
            }
        }
    }

    private void updateStats(LuaExecutionContext ctx) {
        LuaBudgetStats stat = stats.computeIfAbsent(ctx.getContextId(), k -> new LuaBudgetStats());

        long elapsed = ctx.getElapsedMicros();
        stat.totalExecutions++;
        stat.totalMicros += elapsed;
        stat.avgExecutionMicros = stat.totalMicros / stat.totalExecutions;

        if (elapsed > stat.maxExecutionMicros) {
            stat.maxExecutionMicros = elapsed;
        }

        if (elapsed > getBudget(ctx.getContextId())) {
            stat.budgetExceededCount++;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Fallback 핸들러
    // ═══════════════════════════════════════════════════════════════

    /**
     * Fallback 핸들러 설정.
     * Budget 초과 시 호출됨.
     * 
     * @param contextId 컨텍스트 ID
     * @param handler   핸들러
     */
    public void setFallbackHandler(String contextId, Runnable handler) {
        configs.computeIfAbsent(contextId, k -> new BudgetConfig()).fallbackHandler = handler;
    }

    /**
     * Fallback 핸들러 제거.
     * 
     * @param contextId 컨텍스트 ID
     */
    public void removeFallbackHandler(String contextId) {
        BudgetConfig config = configs.get(contextId);
        if (config != null) {
            config.fallbackHandler = null;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 통계
    // ═══════════════════════════════════════════════════════════════

    /**
     * 통계 조회.
     * 
     * @param contextId 컨텍스트 ID
     * @return 통계 객체 (없으면 빈 통계)
     */
    public LuaBudgetStats getStats(String contextId) {
        return stats.getOrDefault(contextId, new LuaBudgetStats());
    }

    /**
     * 통계 초기화.
     * 
     * @param contextId 컨텍스트 ID
     */
    public void resetStats(String contextId) {
        stats.put(contextId, new LuaBudgetStats());
    }

    /**
     * 모든 통계 초기화.
     */
    public void resetAllStats() {
        stats.clear();
    }

    /**
     * 등록된 모든 컨텍스트 ID 조회.
     */
    public java.util.Set<String> getContextIds() {
        return java.util.Collections.unmodifiableSet(configs.keySet());
    }

    // ═══════════════════════════════════════════════════════════════
    // 리포트
    // ═══════════════════════════════════════════════════════════════

    /**
     * 전체 Budget 상태 리포트 출력.
     */
    public void printReport() {
        System.out.println("═══════════════════════════════════════════════");
        System.out.println("  Lua Budget Report");
        System.out.println("═══════════════════════════════════════════════");

        for (String contextId : configs.keySet()) {
            BudgetConfig config = configs.get(contextId);
            LuaBudgetStats stat = stats.getOrDefault(contextId, new LuaBudgetStats());

            System.out.printf("  [%s]%n", contextId);
            System.out.printf("    Budget: %.2fms%n", config.budgetMicros / 1000.0);
            System.out.printf("    Executions: %d (exceeded: %d)%n",
                    stat.totalExecutions, stat.budgetExceededCount);
            System.out.printf("    Avg: %.2fms, Max: %.2fms%n",
                    stat.avgExecutionMicros / 1000.0, stat.maxExecutionMicros / 1000.0);
        }

        System.out.println("═══════════════════════════════════════════════");
    }

    // ═══════════════════════════════════════════════════════════════
    // 내부 클래스
    // ═══════════════════════════════════════════════════════════════

    private static class BudgetConfig {
        long budgetMicros = 10_000; // 기본 10ms
        Runnable fallbackHandler;
        LuaExecutionContext activeContext;
    }

    /**
     * Lua Budget 통계.
     */
    @PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
    public static class LuaBudgetStats {
        public long totalExecutions = 0;
        public long budgetExceededCount = 0;
        public long avgExecutionMicros = 0;
        public long maxExecutionMicros = 0;
        public long totalMicros = 0;

        @Override
        public String toString() {
            return String.format("LuaBudgetStats[executions=%d, exceeded=%d, avg=%.2fms, max=%.2fms]",
                    totalExecutions, budgetExceededCount,
                    avgExecutionMicros / 1000.0, maxExecutionMicros / 1000.0);
        }
    }
}
