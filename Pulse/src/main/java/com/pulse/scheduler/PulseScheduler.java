package com.pulse.scheduler;

import com.pulse.api.log.PulseLogger;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Pulse 태스크 스케줄러.
 * 
 * 게임 틱 기반 태스크 스케줄링을 제공.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 60틱(약 3초) 후 1회 실행
 * TaskHandle handle = PulseScheduler.runLater(() -> {
 *     System.out.println("Hello!");
 * }, 60);
 * 
 * // 20틱마다 반복 실행
 * TaskHandle timer = PulseScheduler.runTimer(() -> {
 *     System.out.println("Tick!");
 * }, 20, 0);
 * 
 * // 취소
 * timer.cancel();
 * 
 * // 비동기 실행
 * PulseScheduler.runAsync(() -> {
 *     // 무거운 작업
 * });
 * </pre>
 */
public class PulseScheduler {

    private static final PulseScheduler INSTANCE = new PulseScheduler();

    // 현재 게임 틱
    private volatile long currentTick = 0;

    // 태스크 ID 생성기
    private final AtomicLong taskIdGenerator = new AtomicLong(0);

    // 스케줄된 태스크 목록
    private final List<ScheduledTask> tasks = new CopyOnWriteArrayList<>();

    // 메인 스레드에서 실행할 태스크 큐
    private final ConcurrentLinkedQueue<Runnable> syncQueue = new ConcurrentLinkedQueue<>();

    // 비동기 실행용 스레드 풀
    private ExecutorService asyncExecutor = Executors.newCachedThreadPool(new PulseThreadFactory("Pulse-Async"));

    // 디버그 모드
    private boolean debug = false;

    // 설정
    private SchedulerConfig config = new SchedulerConfig();

    private PulseScheduler() {
        // 기본 ThreadFactory 설정
        config.setThreadFactory(new PulseThreadFactory("Pulse-Async"));
    }

    /**
     * 설정을 업데이트합니다.
     * 실행 중인 태스크에는 즉시 영향을 미치지 않을 수 있습니다.
     */
    public void setConfig(SchedulerConfig config) {
        this.config = config;
    }

    public SchedulerConfig getConfig() {
        return config;
    }

    public static PulseScheduler getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 정적 편의 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 지정된 틱 수 후에 1회 실행
     * 
     * @param task       실행할 태스크
     * @param delayTicks 지연 틱 수 (20틱 ≈ 1초)
     * @return 태스크 핸들
     */
    public static TaskHandle runLater(Runnable task, long delayTicks) {
        return INSTANCE.scheduleOnce(task, delayTicks, null);
    }

    /**
     * 지정된 틱 수 후에 1회 실행 (이름 지정)
     */
    public static TaskHandle runLater(Runnable task, long delayTicks, String name) {
        return INSTANCE.scheduleOnce(task, delayTicks, name);
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
        return INSTANCE.scheduleRepeating(task, periodTicks, delayTicks, null);
    }

    /**
     * 지정된 간격으로 반복 실행 (이름 지정)
     */
    public static TaskHandle runTimer(Runnable task, long periodTicks, long delayTicks, String name) {
        return INSTANCE.scheduleRepeating(task, periodTicks, delayTicks, name);
    }

    /**
     * 비동기로 즉시 실행 (별도 스레드)
     * 
     * @param task 실행할 태스크
     * @return 태스크 핸들
     */
    public static TaskHandle runAsync(Runnable task) {
        return INSTANCE.executeAsync(task, null);
    }

    /**
     * 비동기로 즉시 실행 (이름 지정)
     */
    public static TaskHandle runAsync(Runnable task, String name) {
        return INSTANCE.executeAsync(task, name);
    }

    /**
     * 메인 스레드(게임 스레드)에서 실행
     * 다음 틱에 실행됨
     * 
     * @param task 실행할 태스크
     */
    public static void runSync(Runnable task) {
        INSTANCE.syncQueue.offer(task);
    }

    /**
     * 현재 게임 틱 가져오기
     */
    public static long getCurrentTick() {
        return INSTANCE.currentTick;
    }

    // ─────────────────────────────────────────────────────────────
    // 인스턴스 메서드 (내부)
    // ─────────────────────────────────────────────────────────────

    private TaskHandle scheduleOnce(Runnable task, long delayTicks, String name) {
        long id = taskIdGenerator.incrementAndGet();
        String taskName = name != null ? name : "task-" + id;
        TaskHandle handle = new TaskHandle(id, taskName);

        ScheduledTask scheduled = new ScheduledTask(
                handle, task, ScheduledTask.TaskType.ONCE,
                delayTicks, 0, currentTick);

        tasks.add(scheduled);

        if (debug) {
            PulseLogger.debug(PulseLogger.PULSE, "Scheduled once: {} (delay={} ticks)", taskName, delayTicks);
        }

        return handle;
    }

    private TaskHandle scheduleRepeating(Runnable task, long periodTicks, long delayTicks, String name) {
        long id = taskIdGenerator.incrementAndGet();
        String taskName = name != null ? name : "timer-" + id;
        TaskHandle handle = new TaskHandle(id, taskName);

        ScheduledTask scheduled = new ScheduledTask(
                handle, task, ScheduledTask.TaskType.REPEATING,
                delayTicks, periodTicks, currentTick);

        tasks.add(scheduled);

        if (debug) {
            PulseLogger.debug(PulseLogger.PULSE, "Scheduled repeating: {} (period={}, delay={} ticks)",
                    taskName, periodTicks, delayTicks);
        }

        return handle;
    }

    private TaskHandle executeAsync(Runnable task, String name) {
        long id = taskIdGenerator.incrementAndGet();
        String taskName = name != null ? name : "async-" + id;
        TaskHandle handle = new TaskHandle(id, taskName);

        asyncExecutor.submit(() -> {
            try {
                task.run();
                handle.incrementExecutionCount();
                handle.markCompleted();
            } catch (Exception e) {
                PulseLogger.error(PulseLogger.PULSE, "Async task error: {}", taskName);
                e.printStackTrace();
            }
        });

        if (debug) {
            PulseLogger.debug(PulseLogger.PULSE, "Submitted async: {}", taskName);
        }

        return handle;
    }

    // ─────────────────────────────────────────────────────────────
    // 틱 핸들러 (게임 루프에서 호출되어야 함)
    // ─────────────────────────────────────────────────────────────

    /**
     * 틱 처리.
     * 게임의 메인 루프에서 매 틱마다 호출되어야 함.
     * (Mixin으로 GameTime.tick()에 연결)
     */
    public void tick() {
        currentTick++;

        // 동기 큐 처리
        processSyncQueue();

        // 스케줄된 태스크 처리
        processScheduledTasks();
    }

    private void processSyncQueue() {
        Runnable task;
        int processed = 0;
        int maxPerTick = config.getTickBatchSize(); // 한 틱당 최대 처리량

        while ((task = syncQueue.poll()) != null && processed < maxPerTick) {
            try {
                task.run();
                processed++;
            } catch (Exception e) {
                PulseLogger.error(PulseLogger.PULSE, "Sync task error");
                e.printStackTrace();
            }
        }
    }

    private void processScheduledTasks() {
        List<ScheduledTask> toRemove = new ArrayList<>();

        for (ScheduledTask task : tasks) {
            if (task.handle.isCancelled()) {
                toRemove.add(task);
                continue;
            }

            if (task.isReadyToExecute(currentTick)) {
                task.execute(config.getExceptionPolicy());

                if (!task.shouldContinue()) {
                    toRemove.add(task);
                }
            }
        }

        tasks.removeAll(toRemove);
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 태스크 취소
     */
    public void cancelAll() {
        for (ScheduledTask task : tasks) {
            task.handle.cancel();
        }
        tasks.clear();
        syncQueue.clear();
    }

    /**
     * 활성 태스크 수
     */
    public int getActiveTaskCount() {
        return tasks.size();
    }

    /**
     * 팬딩 동기 태스크 수
     */
    public int getPendingSyncTaskCount() {
        return syncQueue.size();
    }

    public void setDebug(boolean debug) {
        this.debug = debug;
    }

    /**
     * 스케줄러 종료 (게임 종료 시)
     */
    public void shutdown() {
        cancelAll();
        asyncExecutor.shutdown();
        try {
            if (!asyncExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                asyncExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            asyncExecutor.shutdownNow();
        }
    }
}
