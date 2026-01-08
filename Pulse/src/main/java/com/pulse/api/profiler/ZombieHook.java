package com.pulse.api.profiler;

import com.pulse.api.hook.IZombieCallback;
import com.pulse.api.hook.IZombieHook;
import com.pulse.api.log.PulseLogger;
import com.pulse.runtime.MutableHookContext;

/**
 * Zombie Update Hook for profiling and throttling integration.
 * 
 * 이 훅은 IsoZombie.update() 시점에 호출됩니다.
 * 하위 최적화 모드가 스로틀링 정책을 등록할 수 있습니다.
 * 
 * <p>
 * 설계 원칙:
 * </p>
 * <ul>
 * <li>Pulse는 정책의 "의미"를 모름 (FULL/REDUCED 같은 레벨 없음)</li>
 * <li>Pulse는 boolean(처리 여부) 또는 int(예산)만 받음</li>
 * <li>하위 모드가 IThrottlePolicy를 구현하여 등록</li>
 * </ul>
 * 
 * @since Pulse 1.2
 * @since Pulse 2.0 - IThrottlePolicy 기반으로 재설계
 * @since Pulse 2.1 - IZombieHook 인터페이스 구현
 * @since Pulse 2.2 - Zero-allocation ThreadLocal context 패턴 도입
 */
public class ZombieHook implements IZombieHook {

    /** 싱글톤 인스턴스 */
    private static final ZombieHook INSTANCE = new ZombieHook();

    /** Enable detailed profiling (계측 오버헤드 있음) */
    public static boolean profilingEnabled = false;

    /** Throttle policy (하위 최적화 모드가 등록) */
    private static IThrottlePolicy throttlePolicy;

    /** 현재 처리 중인 좀비 (IZombieHook 인터페이스 구현용) */
    @SuppressWarnings("unused")
    private static Object currentZombie;

    /** Profiling callback */
    private static IZombieCallback callback;

    /** Zero-allocation ThreadLocal context (v2.2) */
    private static final ThreadLocal<MutableHookContext> REUSABLE_CTX = ThreadLocal
            .withInitial(MutableHookContext::new);

    // =================================================================
    // 싱글톤 접근
    // =================================================================

    private ZombieHook() {
    }

    public static ZombieHook getInstance() {
        return INSTANCE;
    }

    // =================================================================
    // ThreadLocal Context (Stale 방지)
    // =================================================================

    /** ThreadLocal 컨텍스트 (shouldProcess 결과 + 설정 틱) */
    private static final ThreadLocal<ThrottleContext> currentContext = new ThreadLocal<>();

    /** 컨텍스트 레코드 */
    private static class ThrottleContext {
        final boolean shouldProcess;
        final int budget;
        final long setTick;

        ThrottleContext(boolean shouldProcess, int budget, long setTick) {
            this.shouldProcess = shouldProcess;
            this.budget = budget;
            this.setTick = setTick;
        }
    }

    /**
     * 스로틀링 결과 설정 (Mixin update HEAD에서 호출).
     * 
     * @param shouldProcess 처리 여부
     * @param budget        허용 예산 (0-100)
     * @param worldTick     현재 월드 틱 (stale 감지용)
     */
    public static void setThrottleResult(boolean shouldProcess, int budget, long worldTick) {
        currentContext.set(new ThrottleContext(shouldProcess, budget, worldTick));
    }

    /**
     * 현재 처리 여부 조회 (Step hook에서 호출).
     * 
     * Stale 방지: 1틱 이상 지난 컨텍스트는 true(처리)로 폴백.
     * 
     * @param worldTick 현재 월드 틱
     * @return true면 처리, false면 스킵
     */
    public static boolean shouldProcessCurrentZombie(long worldTick) {
        ThrottleContext ctx = currentContext.get();
        if (ctx == null) {
            return true; // 정책 없으면 처리
        }

        // 1틱 이상 지났으면 stale → 처리
        if (worldTick - ctx.setTick > 1) {
            currentContext.remove();
            return true;
        }
        return ctx.shouldProcess;
    }

    /**
     * 현재 예산 조회.
     * 
     * @param worldTick 현재 월드 틱
     * @return 0-100 예산 (stale이거나 없으면 100)
     */
    public static int getCurrentBudget(long worldTick) {
        ThrottleContext ctx = currentContext.get();
        if (ctx == null || worldTick - ctx.setTick > 1) {
            return 100;
        }
        return ctx.budget;
    }

    /**
     * 컨텍스트 정리 (Mixin update RETURN에서 호출).
     */
    public static void clearContext() {
        currentContext.remove();
    }

    // =================================================================
    // Registration
    // =================================================================

    public static void setCallback(IZombieCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    // =================================================================
    // IZombieHook 인터페이스 구현 (인스턴스 메서드)
    // =================================================================

    @Override
    public void setThrottlePolicy(IThrottlePolicy policy) {
        ZombieHook.throttlePolicy = policy;
        if (policy != null) {
            PulseLogger.info("Pulse", "Throttle policy registered via IZombieHook");
        }
    }

    @Override
    public boolean shouldProcessCurrentZombie() {
        if (throttlePolicy == null) {
            return true;
        }
        try {
            // IHookContext 없이 간단한 shouldProcess 호출
            return throttlePolicy.shouldProcess(null);
        } catch (Throwable t) {
            return true;
        }
    }

    @Override
    public void setCurrentZombie(Object zombie) {
        ZombieHook.currentZombie = zombie;
    }

    @Override
    public void clearCurrentZombie() {
        ZombieHook.currentZombie = null;
    }

    @Override
    public boolean hasThrottlePolicy() {
        return throttlePolicy != null;
    }

    @Override
    public void clearThrottlePolicy() {
        ZombieHook.throttlePolicy = null;
    }

    // =================================================================
    // 정적 유틸리티 메서드 (Mixin 호환용)
    // =================================================================

    /**
     * 스로틀링 정책 등록 (정적 버전, Mixin 호환용).
     */
    public static void setPolicy(IThrottlePolicy policy) {
        throttlePolicy = policy;
        if (policy != null) {
            PulseLogger.info("Pulse", "Throttle policy registered");
        }
    }

    public static void clearPolicy() {
        throttlePolicy = null;
    }

    public static IThrottlePolicy getPolicy() {
        return throttlePolicy;
    }

    public static boolean hasPolicyRegistered() {
        return throttlePolicy != null;
    }

    // =================================================================
    // Throttle API
    // =================================================================

    /**
     * 스로틀링 정책 조회 (Mixin에서 호출).
     * 
     * @param context 훅 컨텍스트
     * @return 처리 여부
     */
    public static boolean shouldProcess(IHookContext context) {
        if (throttlePolicy == null) {
            return true;
        }
        try {
            return throttlePolicy.shouldProcess(context);
        } catch (Throwable t) {
            return true;
        }
    }

    /**
     * 예산 조회 (Mixin에서 호출).
     * 
     * @param context 훅 컨텍스트
     * @return 0-100 예산
     */
    public static int getAllowedBudget(IHookContext context) {
        if (throttlePolicy == null) {
            return 100;
        }
        try {
            return throttlePolicy.getAllowedBudget(context);
        } catch (Throwable t) {
            return 100;
        }
    }

    // =================================================================
    // Zero-allocation Context Methods (v2.2)
    // =================================================================

    /**
     * 좀비 객체와 함께 shouldProcess 호출 (Zero-allocation).
     * 
     * ThreadLocal MutableHookContext를 재사용하여 GC 압력 최소화.
     * 
     * @param zombie   좀비 객체 (Object 타입으로 전달)
     * @param gameTick 현재 게임 틱
     * @return 처리 여부
     * @since Pulse 2.2
     */
    public static boolean shouldProcessWithTarget(Object zombie, long gameTick) {
        // DEBUG: 1000틱마다 로그 출력 (스팸 방지)
        boolean shouldLog = (gameTick % 1000 == 0);

        if (throttlePolicy == null) {
            if (shouldLog) {
                PulseLogger.debug("ZombieHook", "[DEBUG] shouldProcessWithTarget: throttlePolicy is NULL");
            }
            return true;
        }

        if (shouldLog) {
            PulseLogger.debug("ZombieHook", "[DEBUG] shouldProcessWithTarget: tick=" + gameTick
                    + ", zombie=" + (zombie != null ? zombie.getClass().getSimpleName() : "null")
                    + ", policy=" + throttlePolicy.getClass().getSimpleName());
        }

        MutableHookContext ctx = REUSABLE_CTX.get();
        try {
            ctx.update("ZOMBIE_UPDATE", gameTick, zombie);
            boolean result = throttlePolicy.shouldProcess(ctx);

            if (shouldLog) {
                PulseLogger.debug("ZombieHook", "[DEBUG] shouldProcessWithTarget: result=" + result);
            }
            return result;
        } catch (Throwable t) {
            PulseLogger.warn("ZombieHook", "[ERROR] shouldProcessWithTarget failed: " + t.getMessage());
            return true; // fail-open
        } finally {
            ctx.clear(); // 참조 해제 (메모리 누수 방지)
        }
    }

    /**
     * 좀비 객체와 함께 getAllowedBudget 호출 (Zero-allocation).
     * 
     * @param zombie   좀비 객체 (Object 타입으로 전달)
     * @param gameTick 현재 게임 틱
     * @return 0-100 예산
     * @since Pulse 2.2
     */
    public static int getAllowedBudgetWithTarget(Object zombie, long gameTick) {
        if (throttlePolicy == null) {
            return 100;
        }
        MutableHookContext ctx = REUSABLE_CTX.get();
        try {
            ctx.update("ZOMBIE_BUDGET", gameTick, zombie);
            return throttlePolicy.getAllowedBudget(ctx);
        } catch (Throwable t) {
            return 100; // fail-open
        } finally {
            ctx.clear();
        }
    }

    // =================================================================
    // Legacy Methods (Deprecated)
    // =================================================================

    /**
     * 익명 클래스 없이 shouldProcess 호출.
     * 
     * @deprecated Use {@link #shouldProcessWithTarget(Object, long)} instead.
     * @param hookId   훅 ID (예: "ZOMBIE_UPDATE")
     * @param gameTick 현재 게임 틱
     * @return 처리 여부
     */
    @Deprecated
    public static boolean shouldProcessSimple(String hookId, long gameTick) {
        return shouldProcessWithTarget(null, gameTick);
    }

    /**
     * 익명 클래스 없이 getAllowedBudget 호출.
     * 
     * @deprecated Use {@link #getAllowedBudgetWithTarget(Object, long)} instead.
     * @param hookId   훅 ID (예: "ZOMBIE_UPDATE")
     * @param gameTick 현재 게임 틱
     * @return 0-100 예산
     */
    @Deprecated
    public static int getAllowedBudgetSimple(String hookId, long gameTick) {
        return getAllowedBudgetWithTarget(null, gameTick);
    }

    // =================================================================
    // Profiling Callbacks (조건부)
    // =================================================================

    public static void onZombieUpdate(Object zombie) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieUpdateWithContext(zombie);
            } catch (Throwable t) {
            }
        }
    }

    public static void onMotionUpdateStart(Object zombie) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onMotionUpdateStartWithContext(zombie);
            } catch (Throwable t) {
            }
        }
    }

    public static void onMotionUpdateEnd(Object zombie) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onMotionUpdateEndWithContext(zombie);
            } catch (Throwable t) {
            }
        }
    }

    public static void onZombieSpotted(Object zombie, Object target, boolean forced) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieSpottedWithContext(zombie, target, forced);
            } catch (Throwable t) {
            }
        }
    }

    public static void onZombieHit(Object zombie, Object attacker, float damage) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieHitWithContext(zombie, attacker, damage);
            } catch (Throwable t) {
            }
        }
    }

    public static void onZombieKill(Object zombie, Object killer) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onZombieKillWithContext(zombie, killer);
            } catch (Throwable t) {
            }
        }
    }

    // Legacy - disabled (하위 호환)
    public static void onZombieUpdate() {
    }

    public static void onMotionUpdateStart() {
    }

    public static void onMotionUpdateEnd() {
    }

    public static void onSoundPerceptionStart() {
    }

    public static void onSoundPerceptionEnd() {
    }

    public static void onTargetTrackingStart() {
    }

    public static void onTargetTrackingEnd() {
    }

    public static void onSoundPerceptionStart(Object z) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onSoundPerceptionStartWithContext(z);
            } catch (Throwable t) {
            }
        }
    }

    public static void onSoundPerceptionEnd(Object z) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onSoundPerceptionEndWithContext(z);
            } catch (Throwable t) {
            }
        }
    }

    public static void onTargetTrackingStart(Object z) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onTargetTrackingStartWithContext(z);
            } catch (Throwable t) {
            }
        }
    }

    public static void onTargetTrackingEnd(Object z) {
        if (callback != null && profilingEnabled) {
            try {
                callback.onTargetTrackingEndWithContext(z);
            } catch (Throwable t) {
            }
        }
    }
}
