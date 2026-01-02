package com.pulse.mixin;

import com.pulse.api.profiler.SubProfilerHook;
import com.pulse.api.profiler.ZombieHook;
import com.pulse.handler.WorldTickHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoZombie Mixin.
 * 
 * 좀비 업데이트 시점 훅을 제공합니다.
 * 
 * <p>
 * <b>중요:</b> Mixin 0.8.5는 Java 17 익명 클래스를 제대로 처리하지 못합니다.
 * 따라서 이 클래스에서는 익명 클래스(new Interface(){...})를 사용하지 않습니다.
 * </p>
 * 
 * @since Pulse 1.2
 * @since Pulse 2.2 - 익명 클래스 제거 (Mixin 0.8.5 호환성)
 * @since Pulse 2.3 - WorldTickHandler 사용 (전역 틱 무결성)
 */
@Mixin(targets = "zombie.characters.IsoZombie")
public abstract class IsoZombieMixin {

    @Unique
    private long Pulse$zombieUpdateStart = -1;

    /**
     * IsoZombie.update() 시작
     */
    @Inject(method = "update()V", at = @At("HEAD"))
    private void Pulse$onZombieUpdateStart(CallbackInfo ci) {
        try {
            // 전역 월드 틱 조회 (좀비 수에 상관없이 일정)
            final long currentTick = WorldTickHandler.getInstance().getTickCount();

            // 스로틀링 정책 체크 - 좀비 객체(this)를 context에 전달
            if (ZombieHook.hasPolicyRegistered()) {
                boolean shouldProcess = ZombieHook.shouldProcessWithTarget(this, currentTick);
                int budget = ZombieHook.getAllowedBudgetWithTarget(this, currentTick);
                ZombieHook.setThrottleResult(shouldProcess, budget, currentTick);
            }

            // SubProfiler
            Pulse$zombieUpdateStart = SubProfilerHook.start("ZOMBIE_UPDATE");

            // 프로파일링 콜백
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
    @Inject(method = "update()V", at = @At("RETURN"))
    private void Pulse$onZombieUpdateEnd(CallbackInfo ci) {
        try {
            // 컨텍스트 정리
            ZombieHook.clearContext();

            // SubProfiler
            if (Pulse$zombieUpdateStart > 0) {
                SubProfilerHook.end("ZOMBIE_UPDATE", Pulse$zombieUpdateStart);
                Pulse$zombieUpdateStart = -1;
            }

            // 프로파일링 콜백
            if (ZombieHook.profilingEnabled) {
                ZombieHook.onMotionUpdateEnd(this);
            }
        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("IsoZombieMixin.onZombieUpdateEnd", t);
        }
    }
}
