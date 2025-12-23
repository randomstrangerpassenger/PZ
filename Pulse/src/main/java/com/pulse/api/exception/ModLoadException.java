package com.pulse.api.exception;

/**
 * 모드 로딩 관련 예외.
 * 
 * <p>
 * 모드 로드 실패, 의존성 해결 실패, 초기화 실패 등의 상황에서 발생합니다.
 * </p>
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * try {
 *     loadMod(modInfo);
 * } catch (ModLoadException e) {
 *     // 해당 모드만 비활성화하고 계속 진행
 *     logger.warn("Mod load failed, disabling: {}", modInfo.getId(), e);
 *     disableMod(modInfo);
 * }
 * }</pre>
 * 
 * @since Pulse 2.0
 */
public class ModLoadException extends PulseException {

    private final String modId;

    public ModLoadException(String message) {
        super(message);
        this.modId = null;
    }

    public ModLoadException(String modId, String message) {
        super(String.format("Mod '%s': %s", modId, message));
        this.modId = modId;
    }

    public ModLoadException(String modId, String message, Throwable cause) {
        super(String.format("Mod '%s': %s", modId, message), cause);
        this.modId = modId;
    }

    /**
     * 실패한 모드의 ID를 반환합니다.
     * 
     * @return 모드 ID (알 수 없는 경우 null)
     */
    public String getModId() {
        return modId;
    }
}
