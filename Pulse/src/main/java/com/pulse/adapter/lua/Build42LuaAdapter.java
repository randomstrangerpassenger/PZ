package com.pulse.adapter.lua;

import com.pulse.api.version.GameVersion;

/**
 * Build 42+ 전용 Lua 시스템 어댑터.
 * 
 * Build 42 출시 후 구현 예정입니다.
 * 현재는 Build41LuaAdapter를 상속받아 동일하게 동작합니다.
 * 
 * Build 42에서 변경될 수 있는 사항:
 * - Lua 엔진 변경 (Kahlua → ?)
 * - 패키지 구조 변경
 * - 새로운 이벤트 시스템
 * 
 * @since Pulse 1.4
 */
public class Build42LuaAdapter extends Build41LuaAdapter {

    @Override
    public int getSupportedBuild() {
        return GameVersion.BUILD_42;
    }

    @Override
    public String getName() {
        return "Build42LuaAdapter";
    }

    @Override
    public boolean isCompatible() {
        // Build 42 전용 Lua 클래스 확인
        try {
            return false; // 아직 출시되지 않음
        } catch (Exception e) {
            return false;
        }
    }
}
