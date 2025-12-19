package com.pulse.mixin;

import com.pulse.api.log.PulseLogger;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.event.lifecycle.GameTickStartEvent;
import com.pulse.event.lifecycle.GameTickEndEvent;
import com.pulse.event.lifecycle.WorldLoadEvent;
import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;
import com.pulse.scheduler.PulseScheduler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoWorld Mixin.
 * 월드 로드/언로드 및 게임 틱 이벤트 발생.
 * 
 * Note: IsoWorld.update()는 싱글플레이어와 멀티플레이어 모두에서 호출됨.
 * GameClient.update()는 멀티플레이어 전용이므로 여기서 GameTickEvent를 발생시킴.
 * 
 * @since Pulse 1.0
 * @since Pulse 1.2 - GameTickStartEvent/GameTickEndEvent, HookRegistry 통합
 * @since Pulse 1.3 - LOS Hook activated
 */
@Mixin(targets = "zombie.iso.IsoWorld")
public abstract class IsoWorldMixin {

    @Unique
    private static final String LOG = PulseLogger.PULSE;

    @Shadow
    public abstract String getWorld();

    // Echo 2.0 Phase 2: LOS Hook
    // NOTE: checkLineOfSight is NOT in IsoWorld - it's in LosUtil
    // This hook was removed to prevent Mixin failure
    // NOTE: Move LOS profiling to a separate LosUtilMixin if needed

    @Unique
    private static long Pulse$tickCount = 0;

    @Unique
    private static long Pulse$lastTickTime = System.nanoTime();

    @Unique
    private static boolean Pulse$firstTickLogged = false;

    // Pulse 1.2: Tick 시작 시간 (정밀 측정용)
    @Unique
    private static long Pulse$tickStartNanos = -1;

    // Echo 1.0: SubProfiler 시작 시간
    @Unique
    private static long Pulse$worldUpdateStart = -1;

    /**
     * 월드 로드 완료 시점에 WorldLoadEvent 발생
     * init() 메서드 리턴 시점에 호출
     */
    @Inject(method = "init", at = @At("RETURN"))
    private void Pulse$onWorldInit(CallbackInfo ci) {
        System.out.println("[Pulse/DEBUG] IsoWorld.init() CALLED - Mixin injection SUCCESS!");

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

        PulseLogger.info(LOG, "World loaded: {}", worldName);
        EventBus.post(new WorldLoadEvent(worldName));

        System.out.println("[Pulse/DEBUG] WorldLoadEvent posted for: " + worldName);
    }

    /**
     * IsoWorld.update() 시작 시점
     * 
     * v2.1: init() Mixin이 작동하지 않으므로 첫 update()에서 WorldLoadEvent 발생
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onUpdateStart(CallbackInfo ci) {
        try {
            // v2.1: init() 대신 첫 update()에서 WorldLoadEvent 발생
            if (!Pulse$firstTickLogged) {
                String worldName = "Unknown";
                try {
                    worldName = getWorld();
                    if (worldName == null || worldName.isEmpty()) {
                        worldName = "World";
                    }
                } catch (Exception e) {
                    // ignore
                }

                Pulse$tickCount = 0;
                Pulse$lastTickTime = System.nanoTime();
                Pulse$firstTickLogged = true;

                System.out.println("[Pulse] First update() detected - firing WorldLoadEvent for: " + worldName);
                PulseLogger.info(LOG, "World loaded (via update): {}", worldName);
                EventBus.post(new WorldLoadEvent(worldName));

                // Note: Session state is managed by Echo via WorldLoadEvent subscription
                // MixinSessionState.enterGame() removed to avoid cross-class issues in Mixin
            }

            // Pulse 1.2: 틱 시작 시간 기록
            Pulse$tickStartNanos = System.nanoTime();

            // Pulse 1.3: PulseMetrics 틱 시작 알림 (Echo 연동)
            com.pulse.api.PulseMetrics.onTickStart();

            // Pulse 1.2: GameTickStartEvent 발생
            EventBus.post(new GameTickStartEvent(Pulse$tickCount + 1));

            // Pulse 1.2: HookRegistry 콜백 호출
            final long tickNum = Pulse$tickCount + 1;
            PulseHookRegistry.broadcast(HookTypes.GAME_TICK, cb -> cb.onGameTickStart(tickNum));

            // Echo 1.0: WORLD_UPDATE Phase Start
            Pulse$worldUpdateStart = com.pulse.api.profiler.TickPhaseHook.startPhase("WORLD_UPDATE");
        } catch (Throwable t) {
            if (com.pulse.PulseEnvironment.isDevelopmentMode()) {
                throw t;
            }
            PulseErrorHandler.reportMixinFailure("IsoWorldMixin.onUpdateStart", t);
        }
    }

    /**
     * IsoWorld.update()에서 GameTickEvent 발생
     * 이 메서드는 싱글플레이어와 멀티플레이어 모두에서 매 프레임 호출됨
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onUpdate(CallbackInfo ci) {
        try {
            // Echo 1.0: WORLD_UPDATE Phase End
            com.pulse.api.profiler.TickPhaseHook.endPhase("WORLD_UPDATE", Pulse$worldUpdateStart);
            Pulse$worldUpdateStart = -1;

            long currentTime = System.nanoTime();

            // Pulse 1.2: 정밀 틱 소요 시간 계산
            long tickDurationNanos = currentTime - Pulse$tickStartNanos;

            // Pulse 1.3: PulseMetrics 틱 종료 알림 (Echo 연동)
            com.pulse.api.PulseMetrics.onTickEnd(tickDurationNanos);

            float deltaTime = (currentTime - Pulse$lastTickTime) / 1_000_000_000.0f;
            Pulse$lastTickTime = currentTime;

            Pulse$tickCount++;

            // 첦 틱 디버그 로그
            if (!Pulse$firstTickLogged) {
                Pulse$firstTickLogged = true;
                PulseLogger.info(LOG, "First IsoWorld.update() tick! GameTickEvent will now fire.");
            }

            // 매 1000번째 틱마다 상태 로그
            if (Pulse$tickCount % 1000 == 0) {
                PulseLogger.debug(LOG, "IsoWorld tick #{}, deltaTime={}", Pulse$tickCount,
                        String.format("%.4f", deltaTime));
            }

            // 스케줄러 틱 처리
            PulseScheduler.getInstance().tick();

            // v0.9: CRITICAL - onTickComplete() MUST be called from game logic loop
            // (IsoWorld.update)
            // NOT from render loop (GameWindow.render) to avoid FPS/TPS confusion
            // This is the correct injection point: RETURN of IsoWorld.update()
            com.pulse.api.profiler.TickPhaseHook.onTickComplete();

            // Pulse 1.2: GameTickEndEvent 발생 (정밀 소요 시간 포함)
            EventBus.post(new GameTickEndEvent(Pulse$tickCount, tickDurationNanos));

            // Pulse 1.2: HookRegistry 콜백 호출
            final long tickNum = Pulse$tickCount;
            final long duration = tickDurationNanos;
            PulseHookRegistry.broadcast(HookTypes.GAME_TICK, cb -> cb.onGameTickEnd(tickNum, duration));

            // 기존 GameTickEvent 발생 (하위 호환성)
            EventBus.post(new GameTickEvent(Pulse$tickCount, deltaTime));
        } catch (Throwable t) {
            if (com.pulse.PulseEnvironment.isDevelopmentMode()) {
                throw t;
            }
            PulseErrorHandler.reportMixinFailure("IsoWorldMixin.onUpdate", t);
        }
    }
}
