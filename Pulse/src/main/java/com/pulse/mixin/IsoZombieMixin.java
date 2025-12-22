package com.pulse.mixin;

import com.pulse.adapter.zombie.IZombieAdapter;
import com.pulse.adapter.zombie.ZombieAdapterProvider;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.SubProfilerHook;
import com.pulse.api.profiler.ThrottleLevel;
import com.pulse.api.profiler.ZombieHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoZombie Mixin.
 * 
 * Phase 3: Tiered throttle - update() 절대 취소 안 함!
 * ThrottleLevel을 컨텍스트에 저장하여 Step hook에서 활용.
 * 
 * Version Adapter 적용:
 * - 직접 reflection 호출 → ZombieAdapterProvider 사용
 * - Build 41/42 버전 호환성 보장
 * 
 * @since Pulse 1.2
 * @since Pulse 1.4 - Version Adapter 적용
 * @since Pulse 1.5 - Tiered throttle (ci.cancel 제거)
 */
@Mixin(targets = "zombie.characters.IsoZombie")
public abstract class IsoZombieMixin {

    @Unique
    private long Pulse$zombieUpdateStart = -1;

    @Unique
    private static int Pulse$worldTick = 0;

    @Unique
    private static final java.util.concurrent.atomic.AtomicInteger Pulse$debugCallCount = new java.util.concurrent.atomic.AtomicInteger(
            0);

    @Unique
    private static IZombieAdapter Pulse$adapter = null;

    /**
     * 어댑터 Lazy Initialization.
     * Mixin 로드 시점에 어댑터가 초기화되지 않을 수 있으므로 지연 로드.
     */
    @Unique
    private static IZombieAdapter Pulse$getAdapter() {
        if (Pulse$adapter == null) {
            Pulse$adapter = ZombieAdapterProvider.get();
        }
        return Pulse$adapter;
    }

    /**
     * IsoZombie.update() 시작
     * 
     * 중요: cancellable = false! update()는 절대 취소하지 않음.
     * ThrottleLevel만 컨텍스트에 저장하여 Step hook에서 활용.
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onZombieUpdateStart(CallbackInfo ci) {
        try {
            Pulse$worldTick++;

            // 디버그: Mixin 호출 확인
            int callCount = Pulse$debugCallCount.incrementAndGet();
            if (callCount == 1) {
                IZombieAdapter adapter = Pulse$getAdapter();
                PulseLogger.info("Pulse/IsoZombieMixin", "✅ First update() call! Tiered Throttle active.");
                PulseLogger.info("Pulse/IsoZombieMixin", "Using adapter: " + adapter.getName());
            }

            IZombieAdapter adapter = Pulse$getAdapter();

            // MP-safe: zombie ID 사용 (클라이언트 간 동일)
            int zombieId = adapter.getZombieId(this);

            // 거리 및 상태 체크
            float distSq = adapter.getDistanceSquaredToNearestPlayer(this);
            boolean attacking = adapter.isAttacking(this);
            boolean hasTarget = adapter.hasTarget(this);

            // 최근 피격 여부 (어댑터 기반 - B41/B42 호환)
            boolean recentlyEngaged = adapter.isRecentlyHit(this);

            // ThrottleLevel 결정 (cancel 없음!)
            ThrottleLevel level = ZombieHook.getThrottleLevel(distSq, attacking, hasTarget, recentlyEngaged);
            ZombieHook.setCurrentThrottleLevel(level, Pulse$worldTick);

            // SubProfiler - 항상 실행 (Echo heavy_functions용)
            Pulse$zombieUpdateStart = SubProfilerHook.start("ZOMBIE_UPDATE");

            // Fuse 콜백 - 조건부 (zombie.total_updates용)
            if (ZombieHook.profilingEnabled) {
                ZombieHook.onZombieUpdate(this);
                ZombieHook.onMotionUpdateStart(this);
            }
        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("IsoZombieMixin.onZombieUpdateStart", t);
        }
    }

    /**
     * IsoZombie.update() 종료
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onZombieUpdateEnd(CallbackInfo ci) {
        try {
            // ThrottleLevel 컨텍스트 정리 (필수!)
            ZombieHook.clearCurrentThrottleLevel();

            // SubProfiler - 항상 실행
            if (Pulse$zombieUpdateStart > 0) {
                SubProfilerHook.end("ZOMBIE_UPDATE", Pulse$zombieUpdateStart);
                Pulse$zombieUpdateStart = -1;
            }

            // Fuse 콜백 - 조건부
            if (ZombieHook.profilingEnabled) {
                ZombieHook.onMotionUpdateEnd(this);
            }
        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("IsoZombieMixin.onZombieUpdateEnd", t);
        }
    }

    // =================================================================
    // NOTE: Helper methods removed - now using ZombieAdapterProvider
    //
    // 기존 Pulse$getDistSqToPlayer(), Pulse$isAttacking(),
    // Pulse$hasTarget(), Pulse$getZombieId() 메서드들은
    // Build41ZombieAdapter로 이동되었습니다.
    //
    // spotted(), Hit(), Kill() 메서드들은 파라미터 타입이
    // IsoMovingObject, IsoGameCharacter 등 게임 클래스를 요구합니다.
    // 컴파일 타임에 이 클래스들이 없으므로 Mixin Injection이 실패합니다.
    //
    // 향후 필요 시:
    // 1. compileOnly로 게임 JAR 의존성 추가
    // 2. 또는 ASM을 이용한 수동 바이트코드 조작
    // =================================================================
}
