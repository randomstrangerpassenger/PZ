package com.pulse.internal;

import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Pulse 내부 Lua 이벤트 훅.
 * 
 * MixinLuaEventManager에서 직접 사용.
 * pulse-api 의존성 문제 우회를 위해 Pulse 내부에 구현.
 * 
 * Phase 2C 설계:
 * - ThreadLocal<Deque> 스택: 중첩 이벤트 대응
 * - profilingEnabled 플래그: true일 때만 nanoTime() 호출
 * - 예외 방어: 스택 언더플로우 시 안전 처리
 * 
 * @since Pulse 1.3
 */
public final class InternalLuaHook {

    /** 콜백 인터페이스 - 프로파일러가 구현 */
    public interface LuaEventCallback {
        void onEventEnd(String eventName, long durationMicros);
    }

    /** 등록된 콜백 (null이면 미등록) */
    private static volatile LuaEventCallback callback = null;

    /** 상세 프로파일링 활성화 여부 */
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

    private InternalLuaHook() {
    }

    // =========================================
    // Mixin에서 호출하는 메서드
    // =========================================

    /**
     * 이벤트 시작 (Phase 2C).
     * 프로파일링 활성화 시에만 스택에 push.
     */
    public static void fireEventStart(String eventName) {
        if (!profilingEnabled) {
            return;
        }
        EVENT_STACK.get().push(new EventFrame(eventName, System.nanoTime()));
    }

    /**
     * 이벤트 종료 (Phase 2C).
     * 스택에서 pop하고 콜백 호출.
     */
    public static void fireEventEnd() {
        if (!profilingEnabled) {
            return;
        }

        Deque<EventFrame> stack = EVENT_STACK.get();
        EventFrame frame = stack.poll();
        if (frame == null) {
            return; // 예외로 빠져나온 경우
        }

        LuaEventCallback cb = callback;
        if (cb != null) {
            long durationNanos = System.nanoTime() - frame.startNanos;
            long durationMicros = durationNanos / 1000;
            cb.onEventEnd(frame.eventName, durationMicros);
        }
    }

    // =========================================
    // 외부 API
    // =========================================

    public static void setCallback(LuaEventCallback cb) {
        callback = cb;
    }

    public static void setProfilingEnabled(boolean value) {
        profilingEnabled = value;
    }

    public static boolean isProfilingEnabled() {
        return profilingEnabled;
    }
}
