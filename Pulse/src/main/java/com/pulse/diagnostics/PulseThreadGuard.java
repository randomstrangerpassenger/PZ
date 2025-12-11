package com.pulse.diagnostics;

/**
 * 메인 게임 스레드 감지 및 보호.
 * 
 * B42는 스레드 구조 변화가 있기 때문에 Echo가 메인 스레드에서만 동작해야 할 때
 * 이 클래스를 사용하여 검증할 수 있습니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 메인 스레드 여부 확인
 * if (PulseThreadGuard.isMainThread()) {
 *     // 메인 스레드 전용 로직
 * }
 * 
 * // 메인 스레드 강제 (아닌 경우 경고)
 * PulseThreadGuard.assertMainThread("EchoProfiler.sample");
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseThreadGuard {

    private static volatile Thread mainThread = null;
    private static volatile String mainThreadName = null;
    private static volatile boolean warningsEnabled = true;
    private static volatile boolean strictMode = false;

    private PulseThreadGuard() {
    }

    /**
     * 현재 스레드를 메인 게임 스레드로 마킹
     * (게임 초기화 시 한 번 호출)
     */
    public static void markMainThread() {
        mainThread = Thread.currentThread();
        mainThreadName = mainThread.getName();
        System.out.println("[Pulse/ThreadGuard] Main thread marked: " + mainThreadName);
    }

    /**
     * 현재 스레드가 메인 스레드인지 확인
     */
    public static boolean isMainThread() {
        Thread main = mainThread;
        if (main == null) {
            // 아직 마킹되지 않은 경우 - 첫 호출을 메인으로 간주
            return true;
        }
        return Thread.currentThread() == main;
    }

    /**
     * 현재 스레드가 메인 스레드가 아니면 경고/예외
     * 
     * @param context 호출 컨텍스트 (디버깅용)
     */
    public static void assertMainThread(String context) {
        if (!isMainThread()) {
            String message = String.format(
                    "[Pulse/ThreadGuard] WARNING: %s called from non-main thread '%s' (expected: '%s')",
                    context, Thread.currentThread().getName(), mainThreadName);

            if (strictMode) {
                throw new IllegalStateException(message);
            } else if (warningsEnabled) {
                System.err.println(message);
                // 스택 트레이스 일부 출력
                StackTraceElement[] stack = Thread.currentThread().getStackTrace();
                for (int i = 2; i < Math.min(6, stack.length); i++) {
                    System.err.println("    at " + stack[i]);
                }
            }
        }
    }

    /**
     * 현재 스레드가 메인 스레드가 아니면 true 반환
     */
    public static boolean isOffMainThread() {
        return !isMainThread();
    }

    /**
     * 경고 활성화/비활성화
     */
    public static void setWarningsEnabled(boolean enabled) {
        warningsEnabled = enabled;
    }

    /**
     * Strict 모드 (비메인 스레드 호출 시 예외)
     */
    public static void setStrictMode(boolean enabled) {
        strictMode = enabled;
    }

    /**
     * 메인 스레드 이름
     */
    public static String getMainThreadName() {
        return mainThreadName != null ? mainThreadName : "Unknown";
    }

    /**
     * 상태 요약
     */
    public static String getStatus() {
        return String.format(
                "MainThread=%s, Current=%s, IsMain=%s",
                mainThreadName, Thread.currentThread().getName(), isMainThread());
    }
}
