package com.pulse.mixin;

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
 * @since Pulse 1.2
 */
@Mixin(targets = "zombie.characters.IsoZombie")
public abstract class IsoZombieMixin {

    @Unique
    private long Pulse$zombieUpdateStart = -1;

    @Unique
    private static int Pulse$worldTick = 0;

    @Unique
    private static int Pulse$debugCallCount = 0;

    /**
     * IsoZombie.update() 시작
     */
    @Inject(method = "update", at = @At("HEAD"), cancellable = true)
    private void Pulse$onZombieUpdateStart(CallbackInfo ci) {
        try {
            // 디버그: Mixin 호출 확인
            Pulse$debugCallCount++;
            if (Pulse$debugCallCount == 1) {
                System.out.println("[Pulse/IsoZombieMixin] ✅ First update() call! Mixin is working.");
            } else if (Pulse$debugCallCount % 1000 == 0) {
                System.out.println("[Pulse/IsoZombieMixin] update() called - count: " + Pulse$debugCallCount);
            }

            // MP-safe: zombie ID 사용 (클라이언트 간 동일)
            int zombieId = Pulse$getZombieId();

            // Throttle 체크 (Fuse 활성화 시)
            float distSq = Pulse$getDistSqToPlayer();
            boolean attacking = Pulse$isAttacking();
            boolean hasTarget = Pulse$hasTarget();

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

    // --- Helper methods ---

    @Unique
    private float Pulse$getDistSqToPlayer() {
        try {
            Object zombie = this;
            float zx = (float) zombie.getClass().getMethod("getX").invoke(zombie);
            float zy = (float) zombie.getClass().getMethod("getY").invoke(zombie);

            Class<?> playerClass = Class.forName("zombie.characters.IsoPlayer");
            java.lang.reflect.Field playersField = playerClass.getField("players");
            @SuppressWarnings("unchecked")
            java.util.ArrayList<?> players = (java.util.ArrayList<?>) playersField.get(null);

            if (players == null || players.isEmpty())
                return Float.MAX_VALUE;

            float minDistSq = Float.MAX_VALUE;
            for (Object player : players) {
                if (player == null)
                    continue;
                float px = (float) player.getClass().getMethod("getX").invoke(player);
                float py = (float) player.getClass().getMethod("getY").invoke(player);
                float dx = zx - px;
                float dy = zy - py;
                float distSq = dx * dx + dy * dy;
                if (distSq < minDistSq)
                    minDistSq = distSq;
            }
            return minDistSq;
        } catch (Throwable t) {
            return Float.MAX_VALUE;
        }
    }

    @Unique
    private boolean Pulse$isAttacking() {
        try {
            return (boolean) this.getClass().getMethod("isAttacking").invoke(this);
        } catch (Throwable t) {
            return true;
        }
    }

    @Unique
    private boolean Pulse$hasTarget() {
        try {
            Object target = this.getClass().getMethod("getTarget").invoke(this);
            return target != null;
        } catch (Throwable t) {
            return true;
        }
    }

    /**
     * MP-safe zombie ID 가져오기.
     * MP: getOnlineID() (서버 동기화된 ID)
     * SP: getID() (로컬 ID)
     * Fallback: hashCode()
     */
    @Unique
    private int Pulse$getZombieId() {
        try {
            // MP first: getOnlineID()
            Object zombie = this;
            try {
                Object onlineId = zombie.getClass().getMethod("getOnlineID").invoke(zombie);
                if (onlineId != null && ((Number) onlineId).intValue() > 0) {
                    return ((Number) onlineId).intValue();
                }
            } catch (NoSuchMethodException ignored) {
            }

            // SP fallback: getID()
            try {
                Object id = zombie.getClass().getMethod("getID").invoke(zombie);
                if (id != null) {
                    return ((Number) id).intValue();
                }
            } catch (NoSuchMethodException ignored) {
            }

            // Final fallback: object identity (not MP-safe but functional)
            return System.identityHashCode(zombie);
        } catch (Throwable t) {
            return System.identityHashCode(this);
        }
    }

    // =================================================================
    // NOTE: spotted(), Hit(), Kill() 메서드들은 파라미터 타입이
    // IsoMovingObject, IsoGameCharacter 등 게임 클래스를 요구합니다.
    // 컴파일 타임에 이 클래스들이 없으므로 Mixin Injection이 실패합니다.
    //
    // 향후 필요 시:
    // 1. compileOnly로 게임 JAR 의존성 추가
    // 2. 또는 ASM을 이용한 수동 바이트코드 조작
    // =================================================================
}
