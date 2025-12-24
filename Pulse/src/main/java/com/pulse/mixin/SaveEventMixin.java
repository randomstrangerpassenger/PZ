package com.pulse.mixin;

import com.pulse.api.log.PulseLogger;
import com.pulse.event.EventBus;
import com.pulse.event.save.PostLoadEvent;
import com.pulse.event.save.PostSaveEvent;
import com.pulse.event.save.PreLoadEvent;
import com.pulse.event.save.PreSaveEvent;
import com.pulse.event.save.SaveEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Save Event Mixin.
 * 
 * <p>
 * 세이브/로드 시점에 PreSaveEvent/PostSaveEvent 발행.
 * IOGuard가 이벤트를 구독하여 IO 중 시스템 부하를 완충합니다.
 * </p>
 * 
 * <h3>Hooked Methods:</h3>
 * <ul>
 * <li>{@code GameWindow.SaveGame()} - 수동 세이브 및 오토세이브</li>
 * <li>{@code GameWindow.SaveGameAndWorld()} - 월드 포함 세이브</li>
 * </ul>
 * 
 * <h3>Thread Safety:</h3>
 * AtomicBoolean으로 중복 이벤트 발행 방지.
 * 
 * @since Pulse 1.7
 */
@Mixin(targets = "zombie.GameWindow")
public abstract class SaveEventMixin {

    private static final String LOG = PulseLogger.PULSE;

    // ═══════════════════════════════════════════════════════════════
    // Thread Safety: 중복 이벤트 방지
    // ═══════════════════════════════════════════════════════════════

    @Unique
    private static final AtomicBoolean Pulse$saveInProgress = new AtomicBoolean(false);

    @Unique
    private static volatile long Pulse$saveStartTime = 0;

    // ═══════════════════════════════════════════════════════════════
    // SaveGame Hook
    // ═══════════════════════════════════════════════════════════════

    /**
     * SaveGame 시작 시점에 PreSaveEvent 발행.
     */
    @Inject(method = "SaveGame", at = @At("HEAD"), remap = false)
    private static void Pulse$onSaveGameStart(CallbackInfo ci) {
        Pulse$onPreSave("SaveGame", SaveEvent.SaveType.WORLD);
    }

    /**
     * SaveGame 완료 시점에 PostSaveEvent 발행.
     */
    @Inject(method = "SaveGame", at = @At("RETURN"), remap = false)
    private static void Pulse$onSaveGameEnd(CallbackInfo ci) {
        Pulse$onPostSave("SaveGame", SaveEvent.SaveType.WORLD, true);
    }

    // ═══════════════════════════════════════════════════════════════
    // SaveGameAndWorld Hook (월드 포함 세이브)
    // ═══════════════════════════════════════════════════════════════

    /**
     * SaveGameAndWorld 시작 시점.
     */
    @Inject(method = "SaveGameAndWorld", at = @At("HEAD"), remap = false)
    private static void Pulse$onSaveGameAndWorldStart(CallbackInfo ci) {
        Pulse$onPreSave("SaveGameAndWorld", SaveEvent.SaveType.WORLD);
    }

    /**
     * SaveGameAndWorld 완료 시점.
     */
    @Inject(method = "SaveGameAndWorld", at = @At("RETURN"), remap = false)
    private static void Pulse$onSaveGameAndWorldEnd(CallbackInfo ci) {
        Pulse$onPostSave("SaveGameAndWorld", SaveEvent.SaveType.WORLD, true);
    }

    // ═══════════════════════════════════════════════════════════════
    // 공통 이벤트 발행 (중복 방지 적용)
    // ═══════════════════════════════════════════════════════════════

    @Unique
    private static void Pulse$onPreSave(String source, SaveEvent.SaveType saveType) {
        // 이미 세이브 진행 중이면 중복 이벤트 방지
        if (!Pulse$saveInProgress.compareAndSet(false, true)) {
            PulseLogger.debug(LOG, "[SaveEvent] Skipping duplicate PreSaveEvent (already in progress)");
            return;
        }

        Pulse$saveStartTime = System.currentTimeMillis();

        try {
            String saveName = Pulse$extractSaveName();
            PulseLogger.debug(LOG, "[SaveEvent] PreSaveEvent fired: source={}, type={}, name={}",
                    source, saveType, saveName);
            EventBus.post(new PreSaveEvent(saveName, saveType));
        } catch (Throwable t) {
            // Fail-soft: 이벤트 발행 실패해도 세이브는 진행
            PulseLogger.warn(LOG, "[SaveEvent] Failed to post PreSaveEvent: " + t.getMessage());
            Pulse$saveInProgress.set(false);
        }
    }

    @Unique
    private static void Pulse$onPostSave(String source, SaveEvent.SaveType saveType, boolean success) {
        // PreSaveEvent가 발행되지 않았으면 무시
        if (!Pulse$saveInProgress.compareAndSet(true, false)) {
            PulseLogger.debug(LOG, "[SaveEvent] Skipping PostSaveEvent (no matching PreSaveEvent)");
            return;
        }

        long duration = System.currentTimeMillis() - Pulse$saveStartTime;

        try {
            String saveName = Pulse$extractSaveName();
            PulseLogger.debug(LOG, "[SaveEvent] PostSaveEvent fired: source={}, type={}, name={}, duration={}ms",
                    source, saveType, saveName, duration);
            EventBus.post(new PostSaveEvent(saveName, saveType, success));
        } catch (Throwable t) {
            // Fail-soft: 이벤트 발행 실패해도 무시
            PulseLogger.warn(LOG, "[SaveEvent] Failed to post PostSaveEvent: " + t.getMessage());
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Helper Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * 현재 세이브 이름 추출.
     * PZ Core API에서 동적으로 가져옴.
     */
    @Unique
    private static String Pulse$extractSaveName() {
        try {
            // zombie.core.Core.getInstance().getCurrentSaveDir() 또는 유사한 API
            Class<?> coreClass = Class.forName("zombie.core.Core");
            Object core = coreClass.getMethod("getInstance").invoke(null);
            if (core != null) {
                Object saveDir = coreClass.getMethod("getSaveDir").invoke(core);
                if (saveDir != null) {
                    return saveDir.toString();
                }
            }
        } catch (Throwable ignored) {
            // 실패 시 기본값 반환
        }
        return "World";
    }

    /**
     * 강제 PostSave (예외 발생 시 안전 조치).
     * IOGuard의 Deadman Switch와 별도로 Pulse 레벨에서 정리.
     */
    @Unique
    private static void Pulse$forcePostSaveIfNeeded() {
        if (Pulse$saveInProgress.get()) {
            long elapsed = System.currentTimeMillis() - Pulse$saveStartTime;
            if (elapsed > 30_000) { // 30초 초과 시
                PulseLogger.warn(LOG, "[SaveEvent] Force releasing stale save state ({}ms elapsed)", elapsed);
                Pulse$saveInProgress.set(false);
            }
        }
    }
}
