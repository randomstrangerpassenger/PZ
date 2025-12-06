package com.pulse.scheduler;

/**
 * 내부 태스크 래퍼.
 * 스케줄러 내부에서 사용.
 */
class ScheduledTask {

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
    void execute() {
        if (handle.isCancelled())
            return;

        try {
            task.run();
            handle.incrementExecutionCount();

            if (type == TaskType.ONCE) {
                handle.markCompleted();
            } else if (type == TaskType.REPEATING) {
                // 다음 실행 시점 계산
                nextExecutionTick += periodTicks;
            }
        } catch (Exception e) {
            System.err.println("[Pulse/Scheduler] Task execution error: " + handle.getName());
            e.printStackTrace();
        }
    }

    /**
     * 반복 태스크인지 확인
     */
    boolean shouldContinue() {
        return type == TaskType.REPEATING && !handle.isCancelled();
    }
}
