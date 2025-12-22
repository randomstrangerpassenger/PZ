package com.echo.lua;

import com.echo.config.EchoConfig;

/**
 * Echo Lua 샘플링 브릿지.
 * 
 * <p>
 * Lua 스크립트에서 Echo와 통신하기 위한 브릿지입니다.
 * 노출된 메서드는 Lua에서 호출됩니다.
 * </p>
 * 
 * <p>
 * v2.0: LuaBridge → EchoLuaSamplingBridge로 이름 변경
 * (Pulse LuaBridge와의 충돌 방지)
 * </p>
 * 
 * @since Echo 0.9
 * @since Echo 1.0 - Renamed from LuaBridge
 */
public class EchoLuaSamplingBridge {

    private EchoLuaSamplingBridge() {
        // Static utility class
    }

    /**
     * 샘플링 프로파일러 활성화 여부 확인.
     * 
     * @return Lua 프로파일링 + 샘플링 모두 활성화되었으면 true
     */
    public static boolean isSamplingEnabled() {
        EchoConfig config = EchoConfig.getInstance();
        return config.isLuaProfilingEnabled() && config.isLuaSamplingEnabled();
    }

    /**
     * Lua에서 샘플 기록.
     * 
     * @param functionName 함수 이름
     * @param source       소스 파일
     */
    public static void recordSample(String functionName, String source) {
        // 1 샘플 = 1 단위의 "무거움"으로 처리
        LuaCallTracker.getInstance().recordFunctionCall(functionName, source, 1);
    }
}
