package com.pulse.bindings;

import com.pulse.adapter.lua.Build42LuaAdapter;
import com.pulse.adapter.lua.ILuaAdapter;
import com.pulse.adapter.zombie.Build42ZombieAdapter;
import com.pulse.adapter.zombie.IZombieAdapter;

/**
 * Build 42 engine bindings implementation.
 * 
 * <p>
 * Wraps existing B42 adapters in the new bindings interface.
 * </p>
 * 
 * @since Pulse 0.9
 */
final class Build42EngineBindings implements EngineBindings {

    private final int gameBuild;
    private final Build42LuaBindings luaBindings;
    private final Build42ZombieBindings zombieBindings;

    Build42EngineBindings(int gameBuild) {
        this.gameBuild = gameBuild;
        this.luaBindings = new Build42LuaBindings();
        this.zombieBindings = new Build42ZombieBindings();
    }

    @Override
    public ILuaBindings lua() {
        return luaBindings;
    }

    @Override
    public IZombieBindings zombie() {
        return zombieBindings;
    }

    @Override
    public int getGameBuild() {
        return gameBuild;
    }

    // ═══════════════════════════════════════════════════════════════
    // Build 42 Lua Bindings
    // ═══════════════════════════════════════════════════════════════

    private static class Build42LuaBindings implements ILuaBindings {

        private final ILuaAdapter adapter = new Build42LuaAdapter();

        @Override
        public String getEventManagerClassName() {
            return adapter.getEventManagerClassName();
        }

        @Override
        public String getLuaManagerClassName() {
            return adapter.getLuaManagerClassName();
        }

        @Override
        public int getMaxTriggerEventArgs() {
            return adapter.getMaxTriggerEventArgs();
        }

        @Override
        public void onEventStart(String eventName) {
            adapter.onEventStart(eventName);
        }

        @Override
        public void onEventEnd() {
            adapter.onEventEnd();
        }

        @Override
        public boolean hasGlobalLuaAccess() {
            return adapter.hasGlobalLuaAccess();
        }

        @Override
        public Object getGlobalLuaValue(String name) {
            return adapter.getGlobalLuaValue(name);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Build 42 Zombie Bindings
    // ═══════════════════════════════════════════════════════════════

    private static class Build42ZombieBindings implements IZombieBindings {

        private final IZombieAdapter adapter = new Build42ZombieAdapter();

        @Override
        public int getZombieId(Object zombie) {
            return adapter.getZombieId(zombie);
        }

        @Override
        public int getOnlineId(Object zombie) {
            return adapter.getOnlineId(zombie);
        }

        @Override
        public int getLocalId(Object zombie) {
            return adapter.getLocalId(zombie);
        }

        @Override
        public float getX(Object zombie) {
            return adapter.getX(zombie);
        }

        @Override
        public float getY(Object zombie) {
            return adapter.getY(zombie);
        }

        @Override
        public float getZ(Object zombie) {
            return adapter.getZ(zombie);
        }

        @Override
        public float getDistanceSquaredToNearestPlayer(Object zombie) {
            return adapter.getDistanceSquaredToNearestPlayer(zombie);
        }

        @Override
        public boolean isAttacking(Object zombie) {
            return adapter.isAttacking(zombie);
        }

        @Override
        public boolean hasTarget(Object zombie) {
            return adapter.hasTarget(zombie);
        }

        @Override
        public Object getTarget(Object zombie) {
            return adapter.getTarget(zombie);
        }

        @Override
        public boolean isCrawler(Object zombie) {
            return adapter.isCrawler(zombie);
        }

        @Override
        public boolean isOnFloor(Object zombie) {
            return adapter.isOnFloor(zombie);
        }
    }
}
