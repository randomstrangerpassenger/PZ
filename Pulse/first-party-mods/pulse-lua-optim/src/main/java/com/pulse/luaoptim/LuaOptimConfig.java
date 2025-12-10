package com.pulse.luaoptim;

import com.pulse.config.Config;
import com.pulse.config.ConfigValue;

@Config(modId = "Pulse_lua_optim", fileName = "lua_optim.json")
public class LuaOptimConfig {

    @ConfigValue(key = "enableThrottling", comment = "Enable function call throttling")
    public static boolean enableThrottling = true;

    @ConfigValue(key = "enableCaching", comment = "Enable result caching")
    public static boolean enableCaching = true;

    @ConfigValue(key = "debugMode", comment = "Enable debug logging for lua optimizations")
    public static boolean debugMode = false;
}
