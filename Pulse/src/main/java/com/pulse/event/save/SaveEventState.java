package com.pulse.event.save;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Save Event 상태 관리 유틸리티.
 * 
 * <p>
 * SaveEventMixin과 LuaEventAdapter 간의 상태 공유용.
 * Mixin 클래스에서 public static 메서드가 허용되지 않으므로,
 * 상태 관리를 별도 클래스로 분리.
 * </p>
 * 
 * @since Pulse 1.7
 */
public final class SaveEventState {

    private static final AtomicBoolean saveInProgress = new AtomicBoolean(false);
    private static volatile int preSaveHookHits = 0;
    private static volatile int postSaveHookHits = 0;
    private static volatile long saveStartTime = 0;

    private SaveEventState() {
    } // Utility class

    // ═══════════════════════════════════════════════════════════════
    // State Management (Called by SaveEventMixin)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 세이브 시작 표시.
     * 
     * @return true if state changed (was not already saving)
     */
    public static boolean beginSave() {
        if (saveInProgress.compareAndSet(false, true)) {
            saveStartTime = System.currentTimeMillis();
            preSaveHookHits++;
            return true;
        }
        return false;
    }

    /**
     * 세이브 완료 표시.
     * 
     * @return true if state changed (was saving)
     */
    public static boolean endSave() {
        if (saveInProgress.compareAndSet(true, false)) {
            postSaveHookHits++;
            return true;
        }
        return false;
    }

    /**
     * 강제 상태 리셋 (타임아웃 등).
     */
    public static void forceReset() {
        saveInProgress.set(false);
    }

    // ═══════════════════════════════════════════════════════════════
    // Query API (Called by LuaEventAdapter, IOGuard, etc.)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 세이브 진행 중 여부.
     * LuaEventAdapter에서 중복 발행 방지용.
     */
    public static boolean isActive() {
        return saveInProgress.get();
    }

    /**
     * Mixin 훅이 실제로 활성화되었는지 확인.
     * Primary(Mixin) 활성화 증명용.
     */
    public static boolean isHookActive() {
        return preSaveHookHits > 0;
    }

    /**
     * 세이브 시작 시각 (ms).
     */
    public static long getSaveStartTime() {
        return saveStartTime;
    }

    /**
     * PreSave 훅 히트 수 (텔레메트리용).
     */
    public static int getPreSaveHookHits() {
        return preSaveHookHits;
    }

    /**
     * PostSave 훅 히트 수 (텔레메트리용).
     */
    public static int getPostSaveHookHits() {
        return postSaveHookHits;
    }
}
