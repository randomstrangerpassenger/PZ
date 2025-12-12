package com.pulse.bootstrap;

import com.pulse.di.PulseServiceLocator;
import com.pulse.scheduler.PulseScheduler;
import com.pulse.scheduler.SchedulerConfig;
import com.pulse.scheduler.PulseThreadFactory;

/**
 * Assembly class for Pulse.
 * Responsible for wiring up dependencies and registering them with the
 * ServiceLocator.
 */
public class PulseBootstrap {

    public static void initialize() {
        // 1. Core Infrastructure
        setupScheduler();

        // 2. Services (Placeholder for future services like ModLoader, ConfigManager
        // refactoring)
        // ModLoader is currently a singleton, but future refactoring will instantiate
        // it here.

        // 3. Register to ServiceLocator
        PulseServiceLocator.getInstance().registerService(PulseScheduler.class, PulseScheduler.getInstance());
    }

    private static void setupScheduler() {
        SchedulerConfig config = new SchedulerConfig()
                .setTickBatchSize(100)
                .setExceptionPolicy(SchedulerConfig.ExceptionPolicy.LOG_AND_CONTINUE)
                .setThreadFactory(new PulseThreadFactory("Pulse-Async"));

        PulseScheduler.getInstance().setConfig(config);
    }
}
