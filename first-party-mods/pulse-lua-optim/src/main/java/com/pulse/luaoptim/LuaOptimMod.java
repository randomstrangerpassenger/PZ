package com.pulse.luaoptim;

import com.pulse.api.Pulse;
import com.pulse.mod.PulseMod;

public class LuaOptimMod implements PulseMod {

    public static final String MOD_ID = "Pulse_lua_optim";

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "Initializing Lua Optimizer...");

        // 초기화 로직 (필요시 전역 Lua 함수 등록 등)
        if (LuaOptimConfig.debugMode) {
            Pulse.log(MOD_ID, "Debug mode enabled");
        }

        Pulse.log(MOD_ID, "Lua Optimizer initialized!");
    }
}
