package com.pulse.scheduler;

/**
 * Scheduler API 편의 클래스.
 * 
 * PulseScheduler의 정적 메서드를 re-export하여
 * 더 짧은 이름으로 사용 가능하게 함.
 * 
 * 사용 예:
 * 
 * <pre>
 * import static com.pulse.scheduler.Scheduler.*;
 * 
 * // 3초 후 실행
 * runLater(() -> System.out.println("Hello!"), 60);
 * 
 * // 1초마다 반복
 * TaskHandle timer = runTimer(() -> System.out.println("Tick"), 20, 0);
 * timer.cancel();
 * </pre>
 */
public final class Scheduler {

    private Scheduler() {
    }

    /**
     * 지정된 틱 수 후에 1회 실행
     * 
     * @param task       실행할 태스크
     * @param delayTicks 지연 틱 수 (20틱 ≈ 1초)
     * @return 태스크 핸들
     */
    public static TaskHandle runLater(Runnable task, long delayTicks) {
        return PulseScheduler.runLater(task, delayTicks);
    }

    /**
     * 지정된 틱 수 후에 1회 실행 (이름 지정)
     */
    public static TaskHandle runLater(Runnable task, long delayTicks, String name) {
        return PulseScheduler.runLater(task, delayTicks, name);
    }

    /**
     * 지정된 간격으로 반복 실행
     * 
     * @param task        실행할 태스크
     * @param periodTicks 반복 간격 (틱)
     * @param delayTicks  첫 실행 전 지연 (틱)
     * @return 태스크 핸들
     */
    public static TaskHandle runTimer(Runnable task, long periodTicks, long delayTicks) {
        return PulseScheduler.runTimer(task, periodTicks, delayTicks);
    }

    /**
     * 지정된 간격으로 반복 실행 (이름 지정)
     */
    public static TaskHandle runTimer(Runnable task, long periodTicks, long delayTicks, String name) {
        return PulseScheduler.runTimer(task, periodTicks, delayTicks, name);
    }

    /**
     * 비동기로 즉시 실행 (별도 스레드)
     */
    public static TaskHandle runAsync(Runnable task) {
        return PulseScheduler.runAsync(task);
    }

    /**
     * 비동기로 즉시 실행 (이름 지정)
     */
    public static TaskHandle runAsync(Runnable task, String name) {
        return PulseScheduler.runAsync(task, name);
    }

    /**
     * 메인 스레드(게임 스레드)에서 실행
     */
    public static void runSync(Runnable task) {
        PulseScheduler.runSync(task);
    }

    /**
     * 현재 게임 틱 가져오기
     */
    public static long currentTick() {
        return PulseScheduler.getCurrentTick();
    }

    /**
     * 틱을 초로 변환 (약 20틱 = 1초)
     */
    public static long ticksToSeconds(long ticks) {
        return ticks / 20;
    }

    /**
     * 초를 틱으로 변환
     */
    public static long secondsToTicks(double seconds) {
        return (long) (seconds * 20);
    }

    /**
     * 밀리초를 틱으로 변환
     */
    public static long millisToTicks(long millis) {
        return millis / 50;
    }
}
