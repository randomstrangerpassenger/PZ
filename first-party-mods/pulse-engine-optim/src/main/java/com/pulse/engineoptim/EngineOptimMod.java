package com.pulse.engineoptim;

import com.pulse.api.Pulse;
import com.pulse.mod.PulseMod;

/**
 * Pulse Engine Optimizer 모드 엔트리포인트.
 */
public class EngineOptimMod implements PulseMod {

    public static final String MOD_ID = "Pulse_engine_optim";

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "Initializing Engine Optimizer...");

        // 설정에 따른 최적화 활성화 상태 로깅
        OptimizationManager.registerOptimization("WorldLoading", EngineOptimConfig.optimizeWorldLoading);
        OptimizationManager.registerOptimization("AIPathfinding", EngineOptimConfig.optimizeAiPathfinding);
        OptimizationManager.registerOptimization("Rendering", EngineOptimConfig.optimizeRendering);

        if (EngineOptimConfig.safeMode) {
            Pulse.warn(MOD_ID, "Safe Mode is ENABLED. Some optimizations may be skipped for stability.");
        }

        Pulse.log(MOD_ID, "Engine Optimizer initialized!");
    }
}
