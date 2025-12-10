package com.echo.measure;

/**
 * 프로파일링 측정 포인트
 * 
 * 카테고리:
 * - CORE: 핵심 게임 루프
 * - SUBSYSTEM: 주요 서브시스템
 * - LUA: Lua 관련 (On-Demand)
 * - CUSTOM: 사용자 정의
 */
public enum ProfilingPoint {

    // ============================================================
    // CORE - 핵심 게임 루프
    // ============================================================

    /** 전체 게임 틱 */
    TICK(Category.CORE, "Game Tick"),

    /** 전체 렌더링 프레임 */
    FRAME(Category.CORE, "Render Frame"),

    // ============================================================
    // SUBSYSTEM - 주요 서브시스템
    // ============================================================

    /** 렌더링 서브시스템 */
    RENDER(Category.SUBSYSTEM, "Rendering"),

    /** 월드 렌더링 */
    RENDER_WORLD(Category.SUBSYSTEM, "World Rendering"),

    /** UI 렌더링 */
    RENDER_UI(Category.SUBSYSTEM, "UI Rendering"),

    /** 시뮬레이션 업데이트 */
    SIMULATION(Category.SUBSYSTEM, "Simulation"),

    /** 물리 연산 */
    PHYSICS(Category.SUBSYSTEM, "Physics"),

    /** 좀비 AI 업데이트 */
    ZOMBIE_AI(Category.SUBSYSTEM, "Zombie AI"),

    /** NPC AI 업데이트 */
    NPC_AI(Category.SUBSYSTEM, "NPC AI"),

    /** 네트워크 처리 */
    NETWORK(Category.SUBSYSTEM, "Network"),

    /** 사운드 처리 */
    AUDIO(Category.SUBSYSTEM, "Audio"),

    /** 청크 로딩/저장 */
    CHUNK_IO(Category.SUBSYSTEM, "Chunk I/O"),

    // ============================================================
    // LUA - Lua 관련 (On-Demand)
    // ============================================================

    /** Lua 이벤트 디스패치 */
    LUA_EVENT(Category.LUA, "Lua Event"),

    /** 개별 Lua 함수 호출 */
    LUA_FUNCTION(Category.LUA, "Lua Function"),

    /** Lua 가비지 컬렉션 */
    LUA_GC(Category.LUA, "Lua GC"),

    // ============================================================
    // CUSTOM - 사용자/모드 정의
    // ============================================================

    /** 모드 초기화 */
    MOD_INIT(Category.CUSTOM, "Mod Initialization"),

    /** 모드 틱 핸들러 */
    MOD_TICK(Category.CUSTOM, "Mod Tick Handler"),

    /** 커스텀 측정 1-5 */
    CUSTOM_1(Category.CUSTOM, "Custom 1"),
    CUSTOM_2(Category.CUSTOM, "Custom 2"),
    CUSTOM_3(Category.CUSTOM, "Custom 3"),
    CUSTOM_4(Category.CUSTOM, "Custom 4"),
    CUSTOM_5(Category.CUSTOM, "Custom 5"),

    // ============================================================
    // INTERNAL - 프로파일러 내부 진단 (Phase 4)
    // ============================================================

    /** Echo 프로파일러 자체 오버헤드 (메타 프로파일링) */
    ECHO_OVERHEAD(Category.INTERNAL, "Echo Overhead");

    // ============================================================
    // 필드 및 메서드
    // ============================================================

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

    /**
     * Lua 관련 포인트 여부 (On-Demand 토글 대상)
     */
    public boolean isLuaRelated() {
        return category == Category.LUA;
    }

    /**
     * 사용자 정의 포인트 여부
     */
    public boolean isCustom() {
        return category == Category.CUSTOM;
    }

    /**
     * 내부 진단 포인트 여부
     */
    public boolean isInternal() {
        return category == Category.INTERNAL;
    }

    // ============================================================
    // 카테고리 열거형
    // ============================================================

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
