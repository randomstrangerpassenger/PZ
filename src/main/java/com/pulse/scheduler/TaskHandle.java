package com.pulse.scheduler;

/**
 * 스케줄된 태스크 핸들.
 * 태스크 취소 및 상태 확인에 사용.
 */
public class TaskHandle {

    private final long taskId;
    private final String name;
    private volatile boolean cancelled = false;
    private volatile boolean completed = false;
    private volatile int executionCount = 0;

    public TaskHandle(long taskId, String name) {
        this.taskId = taskId;
        this.name = name;
    }

    /**
     * 태스크 취소
     */
    public void cancel() {
        this.cancelled = true;
    }

    /**
     * 취소 여부
     */
    public boolean isCancelled() {
        return cancelled;
    }

    /**
     * 완료 여부
     */
    public boolean isCompleted() {
        return completed;
    }

    /**
     * 실행 중 여부
     */
    public boolean isActive() {
        return !cancelled && !completed;
    }

    /**
     * 실행 횟수
     */
    public int getExecutionCount() {
        return executionCount;
    }

    // 내부 사용
    void markCompleted() {
        this.completed = true;
    }

    void incrementExecutionCount() {
        this.executionCount++;
    }

    public long getTaskId() {
        return taskId;
    }

    public String getName() {
        return name;
    }

    @Override
    public String toString() {
        String status = cancelled ? "CANCELLED" : (completed ? "COMPLETED" : "ACTIVE");
        return String.format("TaskHandle[id=%d, name=%s, status=%s, executions=%d]",
                taskId, name, status, executionCount);
    }
}
