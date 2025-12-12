package com.pulse.scheduler;

import com.pulse.api.log.PulseLogger;

/**
 * 내부 태스크 래퍼.
 * 스케줄러 내부에서 사용.
 */
class ScheduledTask {

    private static final String LOG = PulseLogger.PULSE;

    enum TaskType {
        ONCE, // 1회 실행
        REPEATING, // 반복 실행
        ASYNC // 비동기 실행
    }

    final TaskHandle handle;
    final Runnable task;
    final TaskType type;
    final long delayTicks;
    final long periodTicks;

    long nextExecutionTick;

    ScheduledTask(TaskHandle handle, Runnable task, TaskType type,
            long delayTicks, long periodTicks, long currentTick) {
        this.handle = handle;
        this.task = task;
        this.type = type;
        this.delayTicks = delayTicks;
        this.periodTicks = periodTicks;
        this.nextExecutionTick = currentTick + delayTicks;
    }

    /**
     * 실행 시점인지 확인
     */
    boolean isReadyToExecute(long currentTick) {
        return currentTick >= nextExecutionTick && !handle.isCancelled();
    }

    /**
     * 태스크 실행
     */
    private int retryCount = 0;

    /**
     * 태스크 실행
     */
    void execute(SchedulerConfig.ExceptionPolicy policy) {
        if (handle.isCancelled())
            return;

        try {
            task.run();
            handle.incrementExecutionCount();
            retryCount = 0; // Reset retry count on success

            if (type == TaskType.ONCE) {
                handle.markCompleted();
            } else if (type == TaskType.REPEATING) {
                // 다음 실행 시점 계산
                nextExecutionTick += periodTicks;
            }
        } catch (Exception e) {
            handleException(e, policy);
        }
    }

    private void handleException(Exception e, SchedulerConfig.ExceptionPolicy policy) {
        PulseLogger.error(LOG, "Task execution error: {} ({})", handle.getName(), policy);
        e.printStackTrace();

        switch (policy) {
            case ABORT_TASK:
                handle.cancel();
                break;
            case RETRY_ONCE:
                if (retryCount == 0) {
                    PulseLogger.info(LOG, "Retrying task: {}", handle.getName());
                    retryCount++;
                    // Do not advance nextExecutionTick, so it runs again next tick (or immediately
                    // if loop allows)
                    // For now, next tick is safest.
                    // However, we need to ensure it doesn't get removed if it was ONCE.
                } else {
                    PulseLogger.warn(LOG, "Retry failed, aborting task: {}", handle.getName());
                    handle.cancel();
                }
                break;
            case LOG_AND_CONTINUE:
            default:
                if (type == TaskType.REPEATING) {
                    nextExecutionTick += periodTicks; // Skip to next period
                } else {
                    handle.markCompleted(); // Mark done if it was ONCE
                }
                break;
        }
    }

    /**
     * 반복 태스크인지 확인
     */
    boolean shouldContinue() {
        return type == TaskType.REPEATING && !handle.isCancelled();
    }
}
