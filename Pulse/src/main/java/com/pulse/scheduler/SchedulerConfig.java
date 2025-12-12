package com.pulse.scheduler;

import java.util.concurrent.Executors;
import java.util.concurrent.ThreadFactory;

/**
 * Configuration for PulseScheduler.
 */
public class SchedulerConfig {

    private int tickBatchSize = 100;
    private ExceptionPolicy exceptionPolicy = ExceptionPolicy.LOG_AND_CONTINUE;
    private ThreadFactory threadFactory = Executors.defaultThreadFactory();

    /**
     * Policy for handling exceptions during task execution.
     */
    public enum ExceptionPolicy {
        /** Retry the task once immediately (not implemented yet for all types). */
        RETRY_ONCE,
        /** Log the error and continue with next tasks. */
        LOG_AND_CONTINUE,
        /** Abort the specific task (mark as cancelled). */
        ABORT_TASK
    }

    public int getTickBatchSize() {
        return tickBatchSize;
    }

    public SchedulerConfig setTickBatchSize(int tickBatchSize) {
        this.tickBatchSize = tickBatchSize;
        return this;
    }

    public ExceptionPolicy getExceptionPolicy() {
        return exceptionPolicy;
    }

    public SchedulerConfig setExceptionPolicy(ExceptionPolicy exceptionPolicy) {
        this.exceptionPolicy = exceptionPolicy;
        return this;
    }

    public ThreadFactory getThreadFactory() {
        return threadFactory;
    }

    public SchedulerConfig setThreadFactory(ThreadFactory threadFactory) {
        this.threadFactory = threadFactory;
        return this;
    }
}
