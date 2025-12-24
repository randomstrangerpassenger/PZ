package com.pulse.mixin;

import com.pulse.api.log.PulseLogger;
import com.pulse.event.EventBus;
import com.pulse.event.save.PostSaveEvent;
import com.pulse.event.save.PreSaveEvent;
import com.pulse.event.save.SaveEvent;
import com.pulse.event.save.SaveEventState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

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
 * <li>{@code GameWindow.save(boolean)} - 게임 세이브</li>
 * </ul>
 * 
 * <h3>Thread Safety:</h3>
 * SaveEventState를 통해 중복 이벤트 발행 방지.
 * 
 * <h3>Note:</h3>
 * Mixin 클래스에서 public static 메서드는 허용되지 않으므로,
 * 상태 관리는 {@link SaveEventState}로 분리됨.
 * 
 * @since Pulse 1.7
 */
@Mixin(targets = "zombie.GameWindow", remap = false)
public abstract class SaveEventMixin {

    @Unique
    private static final String LOG = PulseLogger.PULSE;

    // ═══════════════════════════════════════════════════════════════
    // save(boolean) Hook
    // ═══════════════════════════════════════════════════════════════

    /**
     * save(boolean) 시작 시점에 PreSaveEvent 발행.
     * 
     * @param doWorld 월드 포함 세이브 여부
     * @param ci      Callback info
     */
    @Inject(method = "save(Z)V", at = @At("HEAD"), remap = false, require = 0)
    private static void Pulse$onSaveStart(boolean doWorld, CallbackInfo ci) {
        SaveEvent.SaveType saveType = doWorld ? SaveEvent.SaveType.WORLD : SaveEvent.SaveType.PLAYER;
        Pulse$onPreSave("save", saveType);
    }

    /**
     * save(boolean) 완료 시점에 PostSaveEvent 발행.
     * 
     * @param doWorld 월드 포함 세이브 여부
     * @param ci      Callback info
     */
    @Inject(method = "save(Z)V", at = @At("RETURN"), remap = false, require = 0)
    private static void Pulse$onSaveEnd(boolean doWorld, CallbackInfo ci) {
        SaveEvent.SaveType saveType = doWorld ? SaveEvent.SaveType.WORLD : SaveEvent.SaveType.PLAYER;
        Pulse$onPostSave("save", saveType, true);
    }

    // ═══════════════════════════════════════════════════════════════
    // 공통 이벤트 발행 (중복 방지 적용)
    // ═══════════════════════════════════════════════════════════════

    @Unique
    private static void Pulse$onPreSave(String source, SaveEvent.SaveType saveType) {
        // SaveEventState를 통한 중복 방지
        if (!SaveEventState.beginSave()) {
            PulseLogger.debug(LOG, "[SaveEvent] Skipping duplicate PreSaveEvent (already in progress)");
            return;
        }

        try {
            String saveName = Pulse$extractSaveName();
            PulseLogger.info(LOG, "[SaveEvent] PreSaveEvent fired: source={}, type={}, name={}",
                    source, saveType, saveName);
            EventBus.post(new PreSaveEvent(saveName, saveType));
        } catch (Throwable t) {
            // Fail-soft: 이벤트 발행 실패해도 세이브는 진행
            PulseLogger.warn(LOG, "[SaveEvent] Failed to post PreSaveEvent: " + t.getMessage());
            SaveEventState.forceReset();
        }
    }

    @Unique
    private static void Pulse$onPostSave(String source, SaveEvent.SaveType saveType, boolean success) {
        // SaveEventState를 통한 상태 확인
        if (!SaveEventState.endSave()) {
            PulseLogger.debug(LOG, "[SaveEvent] Skipping PostSaveEvent (no matching PreSaveEvent)");
            return;
        }

        long duration = System.currentTimeMillis() - SaveEventState.getSaveStartTime();

        try {
            String saveName = Pulse$extractSaveName();
            PulseLogger.info(LOG, "[SaveEvent] PostSaveEvent fired: source={}, type={}, name={}, duration={}ms",
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
}
