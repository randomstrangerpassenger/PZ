package com.pulse.mixin;

import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.event.lifecycle.WorldLoadEvent;
import com.pulse.scheduler.PulseScheduler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * IsoWorld Mixin.
 * 월드 로드/언로드 및 게임 틱 이벤트 발생.
 * 
 * Note: IsoWorld.update()는 싱글플레이어와 멀티플레이어 모두에서 호출됨.
 * GameClient.update()는 멀티플레이어 전용이므로 여기서 GameTickEvent를 발생시킴.
 * 
 * @since Pulse 1.0
 * @since Echo 1.0 - SubProfilerHook 통합
 */
@Mixin(targets = "zombie.iso.IsoWorld")
public abstract class IsoWorldMixin {

    @Shadow
    public abstract String getWorld();

    // Echo 2.0 Phase 2: LOS Hook
    @Inject(method = "checkLineOfSight(Lzombie/iso/IsoGridSquare;Lzombie/iso/IsoGridSquare;)Z", at = @At("HEAD"))
    private void Pulse$onCheckLineOfSightStart(CallbackInfoReturnable<Boolean> cir) {
        if (com.pulse.api.profiler.PathfindingHook.enabled) {
            com.pulse.api.profiler.PathfindingHook.onLosCalculationStart();
        }
    }

    @Inject(method = "checkLineOfSight(Lzombie/iso/IsoGridSquare;Lzombie/iso/IsoGridSquare;)Z", at = @At("RETURN"))
    private void Pulse$onCheckLineOfSightEnd(CallbackInfoReturnable<Boolean> cir) {
        if (com.pulse.api.profiler.PathfindingHook.enabled) {
            com.pulse.api.profiler.PathfindingHook.onLosCalculationEnd();
        }
    }

    @Unique
    private static long Pulse$tickCount = 0;

    @Unique
    private static long Pulse$lastTickTime = System.nanoTime();

    @Unique
    private static boolean Pulse$firstTickLogged = false;

    // Echo 1.0: SubProfiler 시작 시간
    @Unique
    private static long Pulse$worldUpdateStart = -1;

    /**
     * 월드 로드 완료 시점에 WorldLoadEvent 발생
     * init() 메서드 리턴 시점에 호출
     */
    @Inject(method = "init", at = @At("RETURN"))
    private void Pulse$onWorldInit(CallbackInfo ci) {
        String worldName = "Unknown";
        try {
            worldName = getWorld();
            if (worldName == null || worldName.isEmpty()) {
                worldName = "World";
            }
        } catch (Exception e) {
            // 월드 이름을 가져올 수 없는 경우 기본값 사용
        }

        // 틱 카운터 리셋
        Pulse$tickCount = 0;
        Pulse$lastTickTime = System.nanoTime();
        Pulse$firstTickLogged = false;

        System.out.println("[Pulse] World loaded: " + worldName);
        EventBus.post(new WorldLoadEvent(worldName));
    }

    /**
     * IsoWorld.update() 시작 시점
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onUpdateStart(CallbackInfo ci) {
        // Echo 1.0: WORLD_UPDATE Phase Start
        Pulse$worldUpdateStart = com.pulse.api.profiler.TickPhaseHook.startPhase("WORLD_UPDATE");
    }

    /**
     * IsoWorld.update()에서 GameTickEvent 발생
     * 이 메서드는 싱글플레이어와 멀티플레이어 모두에서 매 프레임 호출됨
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onUpdate(CallbackInfo ci) {
        // Echo 1.0: WORLD_UPDATE Phase End
        com.pulse.api.profiler.TickPhaseHook.endPhase("WORLD_UPDATE", Pulse$worldUpdateStart);
        Pulse$worldUpdateStart = -1;

        long currentTime = System.nanoTime();
        float deltaTime = (currentTime - Pulse$lastTickTime) / 1_000_000_000.0f;
        Pulse$lastTickTime = currentTime;

        Pulse$tickCount++;

        // 첫 틱 디버그 로그
        if (!Pulse$firstTickLogged) {
            Pulse$firstTickLogged = true;
            System.out.println("[Pulse] First IsoWorld.update() tick! GameTickEvent will now fire.");
        }

        // 매 1000번째 틱마다 상태 로그
        if (Pulse$tickCount % 1000 == 0) {
            System.out.printf("[Pulse/DEBUG] IsoWorld tick #%d, deltaTime=%.4f%n", Pulse$tickCount, deltaTime);
        }

        // 스케줄러 틱 처리
        PulseScheduler.getInstance().tick();

        // Tick Phase 완료 알림
        com.pulse.api.profiler.TickPhaseHook.onTickComplete();

        // GameTickEvent 발생
        EventBus.post(new GameTickEvent(Pulse$tickCount, deltaTime));
    }
}
