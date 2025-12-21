package com.echo.lua;

import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Detailed Window 트리거 관리자 (v2.1)
 * 
 * 특정 조건에서 Detailed Lua Profiling Window를 열어
 * 상세 통계를 수집합니다.
 * 
 * P1: 윈도우 통계 추적 지원
 * P2: 컨텍스트 태깅 지원
 */
public class DetailedWindowManager {

    private static DetailedWindowManager INSTANCE;

    private final LuaCallTracker tracker;
    private final AtomicLong lastTriggerTime = new AtomicLong(0);
    private static final long COOLDOWN_MS = 1000; // 1초 쿨다운

    // 트리거 유형
    public enum DetailedTrigger {
        SLOW_TICK, // 틱이 25ms 초과
        CONTEXT_MENU, // OnFillWorldObjectContextMenu 이벤트
        INVENTORY_BURST, // 인벤토리 갱신 폭발
        MANUAL_CAPTURE // 개발자 핫키/명령
    }

    // 트리거별 윈도우 설정 (durationMs, sampleRate, contextTag)
    private static final Map<DetailedTrigger, WindowConfig> CONFIGS = Map.of(
            DetailedTrigger.SLOW_TICK, new WindowConfig(300, 4, "SLOW_TICK"),
            DetailedTrigger.CONTEXT_MENU, new WindowConfig(300, 2, "CONTEXT_MENU"), // P1: 300ms로 증가
            DetailedTrigger.INVENTORY_BURST, new WindowConfig(200, 4, "INVENTORY_BURST"),
            DetailedTrigger.MANUAL_CAPTURE, new WindowConfig(2000, 1, "MANUAL"));

    private record WindowConfig(long durationMs, int sampleRate, String contextTag) {
    }

    private DetailedWindowManager(LuaCallTracker tracker) {
        this.tracker = tracker;
    }

    public static DetailedWindowManager getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new DetailedWindowManager(LuaCallTracker.getInstance());
        }
        return INSTANCE;
    }

    /**
     * Detailed Window 트리거
     * 
     * @param type 트리거 유형
     */
    public void trigger(DetailedTrigger type) {
        long now = System.currentTimeMillis();

        // 쿨다운 체크
        long lastTrigger = lastTriggerTime.get();
        if (now - lastTrigger < COOLDOWN_MS) {
            return;
        }

        // CAS로 동시 호출 방지
        if (!lastTriggerTime.compareAndSet(lastTrigger, now)) {
            return;
        }

        WindowConfig config = CONFIGS.get(type);
        if (config == null) {
            System.err.println("[Echo/DetailedWindow] Unknown trigger type: " + type);
            return;
        }

        // P2: 컨텍스트 태그 전달
        tracker.openDetailedWindow(config.durationMs, config.sampleRate, config.contextTag);
        System.out.println("[Echo/DetailedWindow] Triggered: " + type +
                " (" + config.durationMs + "ms, 1/" + config.sampleRate + " sample, context=" + config.contextTag
                + ")");
    }

    /**
     * Detailed Window가 활성 상태인지 확인
     */
    public boolean isActive() {
        return tracker.isDetailedActive();
    }

    /**
     * 수동 캡처 시작 (콘솔 명령용)
     * 
     * @param durationMs 지속 시간 (밀리초)
     */
    public void startManualCapture(long durationMs) {
        tracker.openDetailedWindow(durationMs, 1, "MANUAL_COMMAND"); // 100% 샘플링
        System.out.println("[Echo/DetailedWindow] Manual capture started: " + durationMs + "ms");
    }

    /**
     * 상태 출력
     */
    public void printStatus() {
        System.out.println("\n[Echo/DetailedWindow] Status:");
        System.out.println("  active = " + isActive());
        System.out.println("  cooldown_ms = " + COOLDOWN_MS);
        System.out.println("  last_trigger = " +
                (System.currentTimeMillis() - lastTriggerTime.get()) + "ms ago");
        System.out.println("  windows_opened = " + tracker.getDetailedWindowsOpened());
        System.out.println("  total_active_ms = " + tracker.getDetailedTotalActiveMs());
    }
}
