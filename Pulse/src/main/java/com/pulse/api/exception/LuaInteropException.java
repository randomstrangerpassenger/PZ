package com.pulse.api.exception;

/**
 * Lua 상호 운용 예외.
 * 
 * Lua 스크립트 실행 오류, 타입 변환 실패 등에 사용.
 */
public class LuaInteropException extends PulseException {

    private final String luaScript;
    private final int lineNumber;

    public LuaInteropException(String message) {
        super(message);
        this.luaScript = null;
        this.lineNumber = -1;
    }

    public LuaInteropException(String message, Throwable cause) {
        super(message, cause);
        this.luaScript = null;
        this.lineNumber = -1;
    }

    public LuaInteropException(String message, String luaScript, int lineNumber) {
        super(message);
        this.luaScript = luaScript;
        this.lineNumber = lineNumber;
    }

    public LuaInteropException(String message, String luaScript, int lineNumber, Throwable cause) {
        super(message, cause);
        this.luaScript = luaScript;
        this.lineNumber = lineNumber;
    }

    public String getLuaScript() {
        return luaScript;
    }

    public int getLineNumber() {
        return lineNumber;
    }

    /**
     * 스크립트 실행 오류
     */
    public static LuaInteropException executionError(String script, int line, Throwable cause) {
        return new LuaInteropException(
                String.format("Lua execution error at line %d: %s", line, cause.getMessage()),
                script, line, cause);
    }

    /**
     * 타입 변환 오류
     */
    public static LuaInteropException typeConversionError(String expectedType, Object actualValue) {
        return new LuaInteropException(
                String.format("Failed to convert Lua value to %s. Got: %s",
                        expectedType, actualValue != null ? actualValue.getClass().getSimpleName() : "nil"));
    }

    /**
     * 함수 찾을 수 없음
     */
    public static LuaInteropException functionNotFound(String functionName) {
        return new LuaInteropException(
                String.format("Lua function not found: %s", functionName));
    }
}
