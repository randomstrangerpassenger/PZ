package com.pulse.adapter.lua;

import com.pulse.api.version.IVersionAdapter;

/**
 * Lua 시스템 관련 버전별 API 추상화 인터페이스.
 * 
 * LuaEventManager, LuaManager 클래스의 메서드에 접근하는
 * 표준화된 방법을 제공합니다.
 * 
 * @since Pulse 1.4
 */
public interface ILuaAdapter extends IVersionAdapter {

    // ═══════════════════════════════════════════════════════════════
    // Class Information
    // ═══════════════════════════════════════════════════════════════

    /**
     * LuaEventManager 클래스의 전체 경로 반환.
     * 
     * @return 패키지 포함 클래스명 (예: "zombie.Lua.LuaEventManager")
     */
    String getEventManagerClassName();

    /**
     * LuaManager 클래스의 전체 경로 반환.
     * 
     * @return 패키지 포함 클래스명 (예: "zombie.Lua.LuaManager")
     */
    String getLuaManagerClassName();

    // ═══════════════════════════════════════════════════════════════
    // Event System
    // ═══════════════════════════════════════════════════════════════

    /**
     * triggerEvent 메서드의 최대 인자 개수 반환.
     * 
     * Mixin에서 어떤 오버로드까지 후킹해야 하는지 결정에 사용.
     * 
     * @return 최대 인자 개수 (Build 41: 8)
     */
    int getMaxTriggerEventArgs();

    /**
     * 이벤트 시작 처리.
     * 
     * @param eventName 이벤트 이름
     */
    void onEventStart(String eventName);

    /**
     * 이벤트 종료 처리.
     */
    void onEventEnd();

    // ═══════════════════════════════════════════════════════════════
    // Lua State Access
    // ═══════════════════════════════════════════════════════════════

    /**
     * GlobalLua 환경 접근 가능 여부.
     * 
     * @return 접근 가능하면 true
     */
    boolean hasGlobalLuaAccess();

    /**
     * Lua 글로벌 변수 값 조회.
     * 
     * @param name 변수 이름
     * @return 값 (없으면 null)
     */
    Object getGlobalLuaValue(String name);
}
