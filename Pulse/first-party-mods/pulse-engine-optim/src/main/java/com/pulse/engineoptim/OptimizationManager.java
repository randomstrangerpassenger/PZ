package com.pulse.engineoptim;

import com.pulse.api.Pulse;
import java.util.HashSet;
import java.util.Set;

/**
 * 최적화 기능 관리자.
 */
public class OptimizationManager {

    private static final Set<String> activeOptimizations = new HashSet<>();
    private static final Set<String> failedOptimizations = new HashSet<>();

    public static void registerOptimization(String name, boolean enabled) {
        if (enabled) {
            activeOptimizations.add(name);
            Pulse.log("Pulse_engine_optim", "Optimization enabled: " + name);
        } else {
            Pulse.log("Pulse_engine_optim", "Optimization disabled: " + name);
        }
    }

    public static void reportFailure(String name, Throwable t) {
        failedOptimizations.add(name);
        activeOptimizations.remove(name);
        Pulse.error("Pulse_engine_optim", "Optimization failed: " + name, t);

        if (EngineOptimConfig.safeMode) {
            Pulse.warn("Pulse_engine_optim",
                    "SafeMode enabled - potentially dangerous optimizations will be skipped");
        }
    }

    public static boolean isOptimizationActive(String name) {
        return activeOptimizations.contains(name) && !failedOptimizations.contains(name);
    }
}
