package com.pulse.api.exception;

/**
 * Lua 초기화 실패 예외.
 * Lua 스크립트 로드 또는 초기화 중 오류 발생 시 throw됩니다.
 * 
 * @since 1.1.0
 */
public class LuaInitializationException extends PulseException {

    private final String scriptPath;

    public LuaInitializationException(String message) {
        super(message);
        this.scriptPath = null;
    }

    public LuaInitializationException(String message, String scriptPath) {
        super(message + " [script: " + scriptPath + "]");
        this.scriptPath = scriptPath;
    }

    public LuaInitializationException(String message, Throwable cause) {
        super(message, cause);
        this.scriptPath = null;
    }

    public LuaInitializationException(String message, String scriptPath, Throwable cause) {
        super(message + " [script: " + scriptPath + "]", cause);
        this.scriptPath = scriptPath;
    }

    public String getScriptPath() {
        return scriptPath;
    }
}
