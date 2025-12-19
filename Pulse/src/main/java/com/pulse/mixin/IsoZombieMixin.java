package com.pulse.mixin;

import com.pulse.adapter.zombie.IZombieAdapter;
import com.pulse.adapter.zombie.ZombieAdapterProvider;
import com.pulse.api.profiler.SubProfilerHook;
import com.pulse.api.profiler.ZombieHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoZombie Mixin.
 * 
 * Phase 2 Fixed: SubProfilerHook 항상 실행, Fuse 콜백만 조건부
 * 
 * Version Adapter 적용:
 * - 직접 reflection 호출 → ZombieAdapterProvider 사용
 * - Build 41/42 버전 호환성 보장
 * 
 * @since Pulse 1.2
 * @since Pulse 1.4 - Version Adapter 적용
 */
@Mixin(targets = "zombie.characters.IsoZombie")
public abstract class IsoZombieMixin {

    @Unique
    private long Pulse$zombieUpdateStart = -1;

    @Unique
    private static int Pulse$worldTick = 0;

    @Unique
    private static int Pulse$debugCallCount = 0;

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
     */
    @Inject(method = "update", at = @At("HEAD"), cancellable = true)
    private void Pulse$onZombieUpdateStart(CallbackInfo ci) {
        try {
            // 디버그: Mixin 호출 확인
            Pulse$debugCallCount++;
            if (Pulse$debugCallCount == 1) {
                IZombieAdapter adapter = Pulse$getAdapter();
                System.out.println("[Pulse/IsoZombieMixin] ✅ First update() call! Mixin is working.");
                System.out.println("[Pulse/IsoZombieMixin] Using adapter: " + adapter.getName());
            } else if (Pulse$debugCallCount % 1000 == 0) {
                System.out.println("[Pulse/IsoZombieMixin] update() called - count: " + Pulse$debugCallCount);
            }

            IZombieAdapter adapter = Pulse$getAdapter();

            // MP-safe: zombie ID 사용 (클라이언트 간 동일)
            int zombieId = adapter.getZombieId(this);

            // Throttle 체크 (Fuse 활성화 시) - 어댑터 사용
            float distSq = adapter.getDistanceSquaredToNearestPlayer(this);
            boolean attacking = adapter.isAttacking(this);
            boolean hasTarget = adapter.hasTarget(this);

            if (ZombieHook.shouldSkipFast(distSq, attacking, hasTarget, zombieId, Pulse$worldTick)) {
                ci.cancel();
                return;
            }

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
