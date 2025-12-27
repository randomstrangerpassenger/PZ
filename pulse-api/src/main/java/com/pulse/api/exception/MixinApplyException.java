package com.pulse.api.exception;

/**
 * Mixin 적용 관련 예외.
 * 
 * Mixin 주입 실패, 대상 클래스 찾기 실패, 바이트코드 조작 오류 등에 사용.
 */
public class MixinApplyException extends PulseException {

    private final String mixinClass;
    private final String targetClass;

    public MixinApplyException(String message) {
        super(message);
        this.mixinClass = null;
        this.targetClass = null;
    }

    public MixinApplyException(String message, Throwable cause) {
        super(message, cause);
        this.mixinClass = null;
        this.targetClass = null;
    }

    public MixinApplyException(String message, String mixinClass, String targetClass) {
        super(message);
        this.mixinClass = mixinClass;
        this.targetClass = targetClass;
    }

    public MixinApplyException(String message, String mixinClass, String targetClass, Throwable cause) {
        super(message, cause);
        this.mixinClass = mixinClass;
        this.targetClass = targetClass;
    }

    public String getMixinClass() {
        return mixinClass;
    }

    public String getTargetClass() {
        return targetClass;
    }

    /**
     * 대상 클래스 찾기 실패
     */
    public static MixinApplyException targetNotFound(String mixinClass, String targetClass) {
        return new MixinApplyException(
                String.format("Mixin target class not found: %s (from mixin: %s)", targetClass, mixinClass),
                mixinClass, targetClass);
    }

    /**
     * 주입 실패
     */
    public static MixinApplyException injectionFailed(String mixinClass, String targetClass, Throwable cause) {
        return new MixinApplyException(
                String.format("Failed to inject mixin %s into %s: %s", mixinClass, targetClass, cause.getMessage()),
                mixinClass, targetClass, cause);
    }

    /**
     * 메서드 시그니처 불일치
     */
    public static MixinApplyException signatureMismatch(String mixinClass, String methodName, String expected,
            String actual) {
        return new MixinApplyException(
                String.format("Method signature mismatch in mixin %s.%s. Expected: %s, Got: %s",
                        mixinClass, methodName, expected, actual),
                mixinClass, null);
    }
}
