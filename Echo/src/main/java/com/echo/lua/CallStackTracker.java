package com.echo.lua;

import java.util.ArrayDeque;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Lua 호출 스택 관리.
 * 
 * <p>
 * LuaCallTracker에서 분리된 스택 전용 클래스입니다.
 * ThreadLocal 스택, 프레임 관리, 틱 경계 처리를 담당합니다.
 * </p>
 * 
 * <h3>핵심 원칙:</h3>
 * <ul>
 * <li>"tracked 프레임만 push" - 추적 조건 만족 시에만 스택에 push</li>
 * <li>빈 스택 = 정상 (Start가 추적 안 됨)</li>
 * </ul>
 * 
 * <h3>Thread Safety:</h3>
 * <ul>
 * <li>ThreadLocal로 스레드별 스택 격리</li>
 * <li>Game Thread에서만 쓰기, 동기화 불필요</li>
 * </ul>
 * 
 * @since Echo 0.9 - Extracted from LuaCallTracker
 */
public class CallStackTracker {

    // ═══════════════════════════════════════════════════════════════
    // Configuration
    // ═══════════════════════════════════════════════════════════════

    private static final int MAX_STACK_DEPTH = 128;
    private static final long FRAME_TTL_NANOS = 5_000_000_000L; // 5초

    // ═══════════════════════════════════════════════════════════════
    // ThreadLocal Stack
    // ═══════════════════════════════════════════════════════════════

    private final ThreadLocal<ArrayDeque<CallFrame>> callStack = ThreadLocal.withInitial(() -> new ArrayDeque<>(32));
    private final AtomicLong currentFrameId = new AtomicLong(0);

    // ═══════════════════════════════════════════════════════════════
    // CallFrame Structure
    // ═══════════════════════════════════════════════════════════════

    /**
     * 호출 프레임 정보.
     */
    public static class CallFrame {
        public final String funcName;
        public final String contextTag;
        public final long startNanos;
        public final long frameId;
        public long childTime = 0; // 하위 호출에 소요된 시간

        public CallFrame(String funcName, String contextTag, long startNanos, long frameId) {
            this.funcName = funcName;
            this.contextTag = contextTag;
            this.startNanos = startNanos;
            this.frameId = frameId;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Call Result DTO
    // ═══════════════════════════════════════════════════════════════

    /**
     * recordEnd 결과를 담는 DTO.
     */
    public static class CallResult {
        public final String funcName;
        public final String contextTag;
        public final long elapsedMicros;
        public final long selfMicros;

        public CallResult(String funcName, String contextTag, long elapsedMicros, long selfMicros) {
            this.funcName = funcName;
            this.contextTag = contextTag;
            this.elapsedMicros = elapsedMicros;
            this.selfMicros = selfMicros;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Core API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 호출 시작 시 스택에 push.
     * 
     * @param funcName   함수 이름
     * @param contextTag 컨텍스트 태그
     * @param startNanos 시작 시간 (nanos)
     * @return push 성공 여부 (스택 오버플로우 시 false)
     */
    public boolean recordStart(String funcName, String contextTag, long startNanos) {
        ArrayDeque<CallFrame> stack = callStack.get();

        // Fail-safe: 스택 깊이 초과 시 정리
        if (stack.size() >= MAX_STACK_DEPTH) {
            cleanupStaleFrames(stack, startNanos);
            if (stack.size() >= MAX_STACK_DEPTH) {
                return false; // 여전히 초과 시 push 실패
            }
        }

        stack.push(new CallFrame(funcName, contextTag, startNanos, currentFrameId.get()));
        return true;
    }

    /**
     * 호출 종료 시 스택에서 pop하고 결과 반환.
     * 
     * @param endNanos 종료 시간 (nanos)
     * @return 결과 (스택이 비어있으면 null - 정상 케이스)
     */
    public CallResult recordEnd(long endNanos) {
        ArrayDeque<CallFrame> stack = callStack.get();

        // 스택이 비어있다 = Start가 추적 안 됨 (정상 케이스)
        if (stack.isEmpty()) {
            return null;
        }

        CallFrame frame = stack.pop();
        long elapsed = endNanos - frame.startNanos;
        long elapsedMicros = elapsed / 1000;

        // Self time 계산 (하위 호출 시간 제외)
        long selfTime = elapsed - frame.childTime;
        long selfMicros = selfTime / 1000;

        // 상위 프레임에 child time 전파
        if (!stack.isEmpty()) {
            stack.peek().childTime += elapsed;
        }

        return new CallResult(frame.funcName, frame.contextTag, elapsedMicros, selfMicros);
    }

    /**
     * 오래된 프레임 정리 (예외 탈출 대응).
     * 
     * @return 정리된 프레임 수
     */
    public int cleanupStaleFrames(long nowNanos) {
        return cleanupStaleFrames(callStack.get(), nowNanos);
    }

    private int cleanupStaleFrames(ArrayDeque<CallFrame> stack, long nowNanos) {
        int cleaned = 0;
        while (!stack.isEmpty()) {
            CallFrame oldest = stack.peekLast();
            if (nowNanos - oldest.startNanos > FRAME_TTL_NANOS) {
                stack.pollLast();
                cleaned++;
            } else {
                break;
            }
        }
        if (cleaned > 0) {
            System.out.println("[Echo/CallStack] Cleaned " + cleaned + " stale frames (likely exception escape)");
        }
        return cleaned;
    }

    /**
     * 스택 강제 리셋.
     * 
     * @return 리셋된 프레임 수
     */
    public int resetStack() {
        ArrayDeque<CallFrame> stack = callStack.get();
        int size = stack.size();
        if (size > 0) {
            stack.clear();
            System.out.println("[Echo/CallStack] Stack reset (had " + size + " frames)");
        }
        return size;
    }

    /**
     * 스택이 비어있는지 확인.
     */
    public boolean isEmpty() {
        return callStack.get().isEmpty();
    }

    /**
     * 현재 스택 깊이.
     */
    public int getStackDepth() {
        return callStack.get().size();
    }

    // ═══════════════════════════════════════════════════════════════
    // Tick Boundary
    // ═══════════════════════════════════════════════════════════════

    /**
     * 틱 경계에서 호출 - 프레임 ID 증가.
     */
    public void onTickBoundary() {
        currentFrameId.incrementAndGet();
    }

    /**
     * 현재 프레임 ID.
     */
    public long getCurrentFrameId() {
        return currentFrameId.get();
    }
}
