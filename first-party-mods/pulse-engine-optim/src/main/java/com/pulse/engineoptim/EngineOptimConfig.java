package com.pulse.engineoptim;

import com.pulse.config.Config;
import com.pulse.config.ConfigValue;

/**
 * 엔진 최적화 설정.
 */
@Config(modId = "Pulse_engine_optim", fileName = "engine_optim.json")
public class EngineOptimConfig {

    @ConfigValue(key = "optimizeWorldLoading", comment = "Optimize world loading and chunk processing")
    public static boolean optimizeWorldLoading = true;

    @ConfigValue(key = "optimizeAiPathfinding", comment = "Optimize zombie AI pathfinding calculations")
    public static boolean optimizeAiPathfinding = true;

    @ConfigValue(key = "optimizeRendering", comment = "Optimize rendering performance (batching, culling)")
    public static boolean optimizeRendering = true;

    @ConfigValue(key = "safeMode", comment = "Disable risky optimizations if stability issues occur")
    public static boolean safeMode = false;
}
