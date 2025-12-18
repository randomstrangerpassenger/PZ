package com.pulse.api.lua;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.atomic.LongAdder;

/**
 * Pulse Lua Hook API.
 * 
 * LuaEventManager Mixin이 호출하는 Lua 이벤트 훅.
 * Echo 등 외부 모드는 콜백을 등록하여 이벤트 통계를 수집.
 * 
 * Phase 2C 설계:
 * - ThreadLocal<Deque> 스택: 중첩 이벤트 대응 (OnTick → OnPlayerUpdate 등)
 * - profilingEnabled 플래그: true일 때만 nanoTime() 호출
 * - 예외 방어: 스택 언더플로우 시 안전 처리
 * 
 * @since Pulse 1.3
 */
public final class PulseLuaHook {

    // =========================================
    // Phase 1B: 경로 히트 카운터 (경량)
    // =========================================

    private static final LongAdder PATH_HITS = new LongAdder();
    private static volatile boolean enabled = true;

    // =========================================
    // Phase 2C: 콜백 & 프로파일링
    // =========================================

    /** 콜백 인터페이스 - Echo가 구현 */
    public interface LuaEventCallback {
        void onEventEnd(String eventName, long durationMicros);
    }

    /** 등록된 콜백 (null이면 미등록) */
    private static volatile LuaEventCallback callback = null;

    /** 상세 프로파일링 활성화 여부 (별도 플래그, 콜백 유지하면서 ON/OFF 가능) */
    private static volatile boolean profilingEnabled = false;

    /** 중첩 이벤트 대응 스택 (ThreadLocal) */
    private static final ThreadLocal<Deque<EventFrame>> EVENT_STACK = ThreadLocal.withInitial(ArrayDeque::new);

    /** 이벤트 프레임 (eventName + startNanos) */
    private static final class EventFrame {
        final String eventName;
        final long startNanos;

        EventFrame(String eventName, long startNanos) {
            this.eventName = eventName;
            this.startNanos = startNanos;
        }
    }

    private PulseLuaHook() {
        // 유틸리티 클래스
    }

    // =========================================
    // Mixin에서 호출하는 메서드
    // =========================================

    /**
     * 경로 히트 증가 (Phase 1B).
     * 매 triggerEvent마다 호출. ~10ns 미만.
     */
    public static void incrementPathHit() {
        if (enabled) {
            PATH_HITS.increment();
        }
    }

    /**
     * 이벤트 시작 (Phase 2C).
     * 프로파일링 활성화 시에만 스택에 push.
     * 
     * @param eventName Lua 이벤트 이름 (OnTick, OnPlayerUpdate 등)
     */
    public static void fireEventStart(String eventName) {
        // On-Demand: 비활성화 시 nanoTime() 호출 자체를 스킵
        if (!profilingEnabled) {
            return;
        }
        EVENT_STACK.get().push(new EventFrame(eventName, System.nanoTime()));
    }

    /**
     * 이벤트 종료 (Phase 2C).
     * 스택에서 pop하고 콜백 호출.
     * 
     * 예외 방어: 스택이 비어있으면 무시 (예외로 onEventStart 없이 도달 시)
     */
    public static void fireEventEnd() {
        if (!profilingEnabled) {
            return;
        }

        Deque<EventFrame> stack = EVENT_STACK.get();

        // 스택 언더플로우 방어
        EventFrame frame = stack.poll();
        if (frame == null) {
            return; // 예외로 빠져나온 경우
        }

        LuaEventCallback cb = callback;
        if (cb != null) {
            long durationNanos = System.nanoTime() - frame.startNanos;
            long durationMicros = durationNanos / 1000; // ns → μs
            cb.onEventEnd(frame.eventName, durationMicros);
        }
    }

    // =========================================
    // Echo 등 외부에서 호출하는 API
    // =========================================

    /** 경로 히트 카운트 조회 */
    public static long getPathHitCount() {
        return PATH_HITS.sum();
    }

    /** 카운터 리셋 */
    public static void resetPathHitCount() {
        PATH_HITS.reset();
    }

    /** 콜백 등록 */
    public static void setCallback(LuaEventCallback cb) {
        callback = cb;
    }

    /** 상세 프로파일링 활성화 */
    public static void setProfilingEnabled(boolean value) {
        profilingEnabled = value;
    }

    /** 상세 프로파일링 활성화 여부 */
    public static boolean isProfilingEnabled() {
        return profilingEnabled;
    }

    // =========================================
    // 안전 장치
    // =========================================

    public static void setEnabled(boolean value) {
        enabled = value;
    }

    public static boolean isEnabled() {
        return enabled;
    }
}
