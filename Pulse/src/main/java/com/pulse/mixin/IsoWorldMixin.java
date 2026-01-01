package com.pulse.mixin;

import com.pulse.api.di.PulseServices;
import com.pulse.api.gc.GcObservedEvent;
import com.pulse.api.gc.GcSample;
import com.pulse.api.log.PulseLogger;
import com.pulse.core.gc.GcEventState;
import com.pulse.core.gc.GcSampler;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.api.event.lifecycle.GameTickStartEvent;
import com.pulse.api.event.lifecycle.GameTickEndEvent;
import com.pulse.api.event.lifecycle.WorldLoadEvent;
import com.pulse.handler.TickEndResult;
import com.pulse.handler.TickStartResult;
import com.pulse.handler.WorldTickHandler;
import com.pulse.hook.HookTypes;
import com.pulse.hook.PulseHookRegistry;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * IsoWorld Mixin.
 * 
 * <p>
 * 월드 로드/언로드 및 게임 틱 이벤트 발생.
 * </p>
 * 
 * <p>
 * v2.0: 상태 관리 로직을 {@link WorldTickHandler}로 분리.
 * </p>
 * 
 * <h3>Responsibilities:</h3>
 * <ul>
 * <li>Mixin injection points</li>
 * <li>Event posting (WorldLoadEvent, GameTickEvent, etc.)</li>
 * <li>HookRegistry broadcasting</li>
 * <li>Scheduler tick triggering</li>
 * </ul>
 * 
 * @since Pulse 1.0
 * @since Pulse 1.6 - Refactored to use WorldTickHandler
 */
@Mixin(targets = "zombie.iso.IsoWorld")
public abstract class IsoWorldMixin {

    private static final String LOG = PulseLogger.PULSE;

    @Shadow
    public abstract String getWorld();

    // Echo: SubProfiler phase tracking
    @Unique
    private static long Pulse$worldUpdateStart = -1;

    // GC Pressure Guard: Sampler and State (v2.1)
    @Unique
    private static GcSampler Pulse$gcSampler = null;
    @Unique
    private static GcEventState Pulse$gcEventState = null;

    // ═══════════════════════════════════════════════════════════════
    // World Init
    // ═══════════════════════════════════════════════════════════════

    /**
     * 월드 로드 완료 시점에 WorldLoadEvent 발생.
     * init() 메서드 리턴 시점에 호출.
     */
    @Inject(method = "init", at = @At("RETURN"))
    private void Pulse$onWorldInit(CallbackInfo ci) {
        PulseLogger.debug(LOG, "IsoWorld.init() CALLED - Mixin injection SUCCESS!");

        String worldName = getWorldNameSafe();

        // Initialize handler
        WorldTickHandler.getInstance().install();

        // Initialize GC Sampler (v2.1)
        if (Pulse$gcSampler == null) {
            Pulse$gcSampler = new GcSampler();
            Pulse$gcEventState = new GcEventState();
            PulseLogger.info(LOG, "GcSampler initialized for GCPressureGuard");
        }

        PulseLogger.info(LOG, "World loaded: {}", worldName);
        // Use PulseServices.events() so mods subscribing via API receive this event
        PulseServices.events().publish(new WorldLoadEvent(worldName));

        PulseLogger.debug(LOG, "WorldLoadEvent posted for: " + worldName);
    }

    // ═══════════════════════════════════════════════════════════════
    // Update Start
    // ═══════════════════════════════════════════════════════════════

    /**
     * IsoWorld.update() 시작 시점.
     * 
     * <p>
     * v2.0: 상태 관리는 WorldTickHandler에 위임.
     * </p>
     */
    @Inject(method = "update", at = @At("HEAD"))
    private void Pulse$onUpdateStart(CallbackInfo ci) {
        try {
            WorldTickHandler handler = WorldTickHandler.getInstance();
            TickStartResult result = handler.onUpdateStart();

            // First tick - post WorldLoadEvent if init() wasn't called
            if (result.isFirstTick()) {
                String worldName = getWorldNameSafe();
                PulseLogger.debug(LOG, "First update() detected - firing WorldLoadEvent for: " + worldName);
                PulseLogger.info(LOG, "World loaded (via update): {}", worldName);
                // Use PulseServices.events() so mods subscribing via API receive this event
                WorldLoadEvent worldLoadEvent = new WorldLoadEvent(worldName);
                PulseLogger.info(LOG, "Publishing WorldLoadEvent: {} (class={})", worldName,
                        worldLoadEvent.getClass().getName());
                PulseServices.events().publish(worldLoadEvent);
                PulseLogger.info(LOG, "WorldLoadEvent published successfully");
            }

            // GameTickStartEvent - use PulseServices.events() so Echo can receive it
            GameTickStartEvent tickStartEvent = new GameTickStartEvent(result.getExpectedTickCount());
            if (result.getExpectedTickCount() == 1) {
                PulseLogger.info(LOG, "First GameTickStartEvent: tick={}, class={}", result.getExpectedTickCount(),
                        tickStartEvent.getClass().getName());
            }
            PulseServices.events().publish(tickStartEvent);

            // HookRegistry broadcast
            final long tickNum = result.getExpectedTickCount();
            PulseHookRegistry.broadcast(HookTypes.GAME_TICK, cb -> cb.onGameTickStart(tickNum));

            // Echo: WORLD_UPDATE Phase Start
            Pulse$worldUpdateStart = com.pulse.api.profiler.TickPhaseHook.startPhase("WORLD_UPDATE");
        } catch (Throwable t) {
            if (com.pulse.PulseEnvironment.isDevelopmentMode()) {
                throw t;
            }
            PulseErrorHandler.reportMixinFailure("IsoWorldMixin.onUpdateStart", t);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Update End
    // ═══════════════════════════════════════════════════════════════

    /**
     * IsoWorld.update() 종료 시점.
     * 
     * <p>
     * v2.0: 타이밍 계산은 WorldTickHandler에 위임.
     * </p>
     */
    @Inject(method = "update", at = @At("RETURN"))
    private void Pulse$onUpdate(CallbackInfo ci) {
        try {
            // Echo: WORLD_UPDATE Phase End
            com.pulse.api.profiler.TickPhaseHook.endPhase("WORLD_UPDATE", Pulse$worldUpdateStart);
            Pulse$worldUpdateStart = -1;

            WorldTickHandler handler = WorldTickHandler.getInstance();
            TickEndResult result = handler.onUpdateEnd();

            // Scheduler tick
            PulseServices.scheduler().tick();

            // Tick complete hook
            com.pulse.api.profiler.TickPhaseHook.onTickComplete();

            // GameTickEndEvent - use PulseServices.events() so Echo can receive it
            PulseServices.events().publish(new GameTickEndEvent(result.getTickCount(), result.getDurationNanos()));

            // GcObservedEvent (v2.1 - for GCPressureGuard)
            try {
                if (Pulse$gcSampler != null && Pulse$gcEventState != null) {
                    GcSample sample = Pulse$gcSampler.sample(result.getTickCount());
                    if (Pulse$gcEventState.shouldPublish(sample)) {
                        PulseServices.events().publish(new GcObservedEvent(sample));
                    }
                }
            } catch (Throwable gcError) {
                // Fail-soft: GC sampling failure should not affect game
            }

            // HookRegistry broadcast
            final long tickNum = result.getTickCount();
            final long duration = result.getDurationNanos();
            PulseHookRegistry.broadcast(HookTypes.GAME_TICK, cb -> cb.onGameTickEnd(tickNum, duration));

            // Legacy GameTickEvent (backward compatibility)
            EventBus.post(new GameTickEvent(result.getTickCount(), result.getDeltaTime()));
        } catch (Throwable t) {
            if (com.pulse.PulseEnvironment.isDevelopmentMode()) {
                throw t;
            }
            PulseErrorHandler.reportMixinFailure("IsoWorldMixin.onUpdate", t);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Helper Methods
    // ═══════════════════════════════════════════════════════════════

    @Unique
    private String getWorldNameSafe() {
        try {
            String worldName = getWorld();
            if (worldName == null || worldName.isEmpty()) {
                return "World";
            }
            return worldName;
        } catch (Exception e) {
            return "Unknown";
        }
    }
}
