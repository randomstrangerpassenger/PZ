package com.pulse.api.util;

/**
 * 게임 클래스 이름 레지스트리.
 * 
 * 리플렉션에서 사용하는 게임 클래스 이름들을 중앙 관리합니다.
 * 하드코딩된 문자열 대신 이 상수들을 사용하세요.
 * 
 * @since 1.1.0
 */
public final class GameClassRegistry {

    private GameClassRegistry() {
    }

    // --- IsoWorld 관련---

    /** zombie.iso.IsoWorld */
    public static final String ISO_WORLD = "zombie.iso.IsoWorld";

    /** zombie.iso.IsoCell */
    public static final String ISO_CELL = "zombie.iso.IsoCell";

    /** zombie.iso.IsoGridSquare */
    public static final String ISO_GRID_SQUARE = "zombie.iso.IsoGridSquare";

    /** zombie.iso.IsoChunk */
    public static final String ISO_CHUNK = "zombie.iso.IsoChunk";

    // --- Character 관련---

    /** zombie.characters.IsoPlayer */
    public static final String ISO_PLAYER = "zombie.characters.IsoPlayer";

    /** zombie.characters.IsoZombie */
    public static final String ISO_ZOMBIE = "zombie.characters.IsoZombie";

    /** zombie.characters.IsoGameCharacter */
    public static final String ISO_GAME_CHARACTER = "zombie.characters.IsoGameCharacter";

    /** zombie.characters.IsoLivingCharacter */
    public static final String ISO_LIVING_CHARACTER = "zombie.characters.IsoLivingCharacter";

    // --- Core 관련---

    /** zombie.GameTime */
    public static final String GAME_TIME = "zombie.GameTime";

    /** zombie.GameWindow */
    public static final String GAME_WINDOW = "zombie.GameWindow";

    /** zombie.core.Core */
    public static final String CORE = "zombie.core.Core";

    // --- Network 관련---

    /** zombie.network.GameClient */
    public static final String GAME_CLIENT = "zombie.network.GameClient";

    /** zombie.network.GameServer */
    public static final String GAME_SERVER = "zombie.network.GameServer";

    // --- UI 관련---

    /** zombie.ui.UIManager */
    public static final String UI_MANAGER = "zombie.ui.UIManager";

    // --- Pathfinding 관련---

    /** zombie.ai.astar.Mover */
    public static final String ASTAR_MOVER = "zombie.ai.astar.Mover";

    /** zombie.ai.states.ZombiePathFindState */
    public static final String ZOMBIE_PATHFIND_STATE = "zombie.ai.states.ZombiePathFindState";

    // --- Lua 관련---

    /** se.krka.kahlua.vm.KahluaTable */
    public static final String KAHLUA_TABLE = "se.krka.kahlua.vm.KahluaTable";

    /** zombie.Lua.LuaManager */
    public static final String LUA_MANAGER = "zombie.Lua.LuaManager";
}
