package com.echo.lua;

import com.echo.pulse.TickPhaseBridge;
import com.pulse.api.lua.PulseLuaHook;

/**
 * Lua 경로 히트 프로브 브릿지.
 * 
 * Pulse의 PulseLuaHook.getPathHitCount()를 읽어서
 * 게임 시작 ~30초 후 1회 로그 출력.
 * 
 * 설계 원칙:
 * - Pulse: 주입(Mixin) + 카운터
 * - Echo: 읽기 + 리포트
 * 
 * 사용법: EchoMod.init()에서 register() 호출
 * 
 * @since Echo 2.0
 */
public final class LuaPathHitBridge {

    private static LuaPathHitBridge INSTANCE;

    /** 대략 30초 (60fps 기준 1800틱) */
    private static final int TARGET_TICKS = 1800;

    /** 현재 틱 수 */
    private int tickCount = 0;

    /** 이미 출력했는지 */
    private boolean printed = false;

    /** 마지막으로 읽은 pathHitCount */
    private long lastPathHitCount = 0;

    private LuaPathHitBridge() {
    }

    /**
     * 브릿지 등록
     */
    public static void register() {
        if (INSTANCE != null) {
            return;
        }
        INSTANCE = new LuaPathHitBridge();
        System.out.println("[Echo] LuaPathHitBridge registered (30s validation probe)");
    }

    /**
     * 싱글톤 인스턴스
     */
    public static LuaPathHitBridge getInstance() {
        return INSTANCE;
    }

    /**
     * TickPhaseBridge.onTickComplete() 또는 다른 틱 콜백에서 호출
     */
    public void onTick() {
        if (printed) {
            return;
        }

        if (++tickCount >= TARGET_TICKS) {
            printed = true;
            printPathHitSummary();
        }
    }

    /**
     * 경로 히트 검증 결과 출력
     */
    private void printPathHitSummary() {
        try {
            long hits = PulseLuaHook.getPathHitCount();
            lastPathHitCount = hits;

            if (hits > 0) {
                System.out.println("[Echo/LuaHook] ✅ pathHitCount after ~30s = " + hits + " (Lua path is ACTIVE)");
            } else {
                System.out.println("[Echo/LuaHook] ⚠️ pathHitCount = 0 (Lua path NOT active - check Mixin)");
            }
        } catch (NoClassDefFoundError e) {
            System.out.println("[Echo/LuaHook] ⚠️ PulseLuaHook not available (Pulse outdated?)");
        } catch (Throwable t) {
            System.out.println("[Echo/LuaHook] ❌ Failed to read pathHitCount: " + t.getMessage());
        }
    }

    /**
     * 현재 pathHitCount 조회 (리포트용)
     */
    public long getPathHitCount() {
        try {
            return PulseLuaHook.getPathHitCount();
        } catch (Throwable t) {
            return -1;
        }
    }

    /**
     * 마지막으로 읽은 값 반환
     */
    public long getLastPathHitCount() {
        return lastPathHitCount;
    }

    /**
     * 30초 프로브 완료 여부
     */
    public boolean isValidated() {
        return printed;
    }

    /**
     * 리셋
     */
    public void reset() {
        tickCount = 0;
        printed = false;
        lastPathHitCount = 0;
    }
}
