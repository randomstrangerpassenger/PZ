package com.echo.measure;

/** 프로파일링 측정 포인트: CORE, SUBSYSTEM, LUA, CUSTOM, INTERNAL */
public enum ProfilingPoint {

    // CORE
    TICK(Category.CORE, "Game Tick"),
    FRAME(Category.CORE, "Render Frame"),

    // SUBSYSTEM
    RENDER(Category.SUBSYSTEM, "Rendering"),
    RENDER_WORLD(Category.SUBSYSTEM, "World Rendering"),
    RENDER_UI(Category.SUBSYSTEM, "UI Rendering"),
    SIMULATION(Category.SUBSYSTEM, "Simulation"),
    PHYSICS(Category.SUBSYSTEM, "Physics"),
    ZOMBIE_AI(Category.SUBSYSTEM, "Zombie AI"),
    ZOMBIE_DETECTION(Category.SUBSYSTEM, "Zombie Detection"),
    ZOMBIE_PATHFINDING(Category.SUBSYSTEM, "Zombie Pathfinding"),
    ZOMBIE_SOUND(Category.SUBSYSTEM, "Zombie Sound Response"),
    NPC_AI(Category.SUBSYSTEM, "NPC AI"),
    NETWORK(Category.SUBSYSTEM, "Network"),
    AUDIO(Category.SUBSYSTEM, "Audio"),
    CHUNK_IO(Category.SUBSYSTEM, "Chunk I/O"),

    // --- LUA - Lua 관련 (On-Demand) ---

    /** Lua 이벤트 디스패치 */
    LUA_EVENT(Category.LUA, "Lua Event"),

    /** 개별 Lua 함수 호출 */
    LUA_FUNCTION(Category.LUA, "Lua Function"),

    /** Lua 가비지 컬렉션 */
    LUA_GC(Category.LUA, "Lua GC"),

    // CUSTOM
    MOD_INIT(Category.CUSTOM, "Mod Initialization"),
    MOD_TICK(Category.CUSTOM, "Mod Tick Handler"),
    CUSTOM_1(Category.CUSTOM, "Custom 1"),
    CUSTOM_2(Category.CUSTOM, "Custom 2"),
    CUSTOM_3(Category.CUSTOM, "Custom 3"),
    CUSTOM_4(Category.CUSTOM, "Custom 4"),
    CUSTOM_5(Category.CUSTOM, "Custom 5"),

    // INTERNAL
    ECHO_OVERHEAD(Category.INTERNAL, "Echo Overhead");

    // Fields

    private final Category category;
    private final String displayName;

    ProfilingPoint(Category category, String displayName) {
        this.category = category;
        this.displayName = displayName;
    }

    public Category getCategory() {
        return category;
    }

    public String getDisplayName() {
        return displayName;
    }

    /** Lua 관련 포인트 여부 */
    public boolean isLuaRelated() {
        return category == Category.LUA;
    }

    public boolean isCustom() {
        return category == Category.CUSTOM;
    }

    public boolean isInternal() {
        return category == Category.INTERNAL;
    }

    // Category

    public enum Category {
        CORE("Core", "#FF6B6B"),
        SUBSYSTEM("Subsystem", "#4ECDC4"),
        LUA("Lua", "#FFE66D"),
        CUSTOM("Custom", "#95E1D3"),
        INTERNAL("Internal", "#A9A9A9");

        private final String displayName;
        private final String color;

        Category(String displayName, String color) {
            this.displayName = displayName;
            this.color = color;
        }

        public String getDisplayName() {
            return displayName;
        }

        public String getColor() {
            return color;
        }
    }
}
