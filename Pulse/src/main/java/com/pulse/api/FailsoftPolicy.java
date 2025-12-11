package com.pulse.api;

import com.pulse.api.mixin.MixinInjectionValidator;
import com.pulse.debug.CrashReporter;

/**
 * Fail-soft 정책 시스템.
 * Mixin 실패, Lua 예산 초과 등의 오류가 발생해도 게임을 크래시하지 않고
 * 해당 기능만 비활성화합니다.
 * 
 * <pre>
 * // 사용 예시
 * try {
 *     // 위험한 작업
 * } catch (Exception e) {
 *     FailsoftPolicy.handle(FailsoftAction.WARN_AND_CONTINUE, "MyMod", e);
 * }
 * 
 * // Mixin 실패 처리
 * FailsoftPolicy.handleMixinFailure("com.mymod.mixin.MyMixin", "zombie.SomeClass", error);
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class FailsoftPolicy {

    private FailsoftPolicy() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // Fail-soft 액션 enum
    // ═══════════════════════════════════════════════════════════════

    /**
     * Fail-soft 액션 타입.
     */
    public enum FailsoftAction {
        /**
         * 실패한 Mixin만 비활성화, 게임 계속.
         */
        DISABLE_MIXIN_ONLY,

        /**
         * 경고 로그 후 계속 실행.
         */
        WARN_AND_CONTINUE,

        /**
         * 해당 기능 스킵, 크래시 없음.
         */
        SKIP_FEATURE,

        /**
         * 전체 기능 모듈 비활성화.
         */
        DISABLE_FEATURE,

        /**
         * 페이즈 시퀀스 오류 (v0.9 Fuse/Nerve 지원).
         */
        PHASE_SEQUENCE_ERROR,

        /**
         * 안전하지 않은 월드 상태 접근 (v0.9 Fuse/Nerve 지원).
         */
        UNSAFE_WORLDSTATE_ACCESS
    }

    // ═══════════════════════════════════════════════════════════════
    // 핵심 핸들러
    // ═══════════════════════════════════════════════════════════════

    /**
     * Fail-soft 액션 수행.
     * 
     * @param action 수행할 액션
     * @param source 오류 발생 소스 (클래스명, 모드ID 등)
     * @param error  발생한 예외 (null 가능)
     */
    public static void handle(FailsoftAction action, String source, Throwable error) {
        String message = error != null ? error.getMessage() : "Unknown error";

        switch (action) {
            case DISABLE_MIXIN_ONLY:
                MixinInjectionValidator.disableMixin(source);
                Pulse.warn("pulse", "[Failsoft] Mixin disabled: " + source);
                break;

            case WARN_AND_CONTINUE:
                Pulse.warn("pulse", "[Failsoft] " + source + ": " + message);
                break;

            case SKIP_FEATURE:
                FeatureFlags.disable(source);
                Pulse.warn("pulse", "[Failsoft] Feature skipped: " + source);
                break;

            case DISABLE_FEATURE:
                FeatureFlags.disableModule(source);
                Pulse.warn("pulse", "[Failsoft] Feature module disabled: " + source);
                break;

            case PHASE_SEQUENCE_ERROR:
                Pulse.warn("pulse", "[Failsoft] Phase sequence error: " + source + " - " + message);
                break;

            case UNSAFE_WORLDSTATE_ACCESS:
                Pulse.warn("pulse", "[Failsoft] Unsafe worldstate access: " + source + " - " + message);
                break;
        }

        // CrashReporter에 이벤트 기록
        CrashReporter.recordEvent(
                CrashReporter.EVENT_FAILSOFT_TRIGGERED,
                source,
                action.name() + ": " + message);

        // DevMode에서는 스택트레이스 출력
        if (DevMode.isEnabled() && error != null) {
            error.printStackTrace();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 특화 핸들러
    // ═══════════════════════════════════════════════════════════════

    /**
     * Mixin 실패 처리.
     * 해당 Mixin만 비활성화하고 게임 계속.
     * 
     * @param mixinClass  Mixin 클래스 전체 경로
     * @param targetClass 대상 클래스 전체 경로
     * @param error       발생한 예외
     */
    public static void handleMixinFailure(String mixinClass, String targetClass, Throwable error) {
        MixinInjectionValidator.recordFailure(mixinClass, targetClass,
                error != null ? error.getMessage() : "Unknown mixin error");
        MixinInjectionValidator.disableMixin(mixinClass);

        Pulse.error("pulse", "[Failsoft/Mixin] " + mixinClass + " → " + targetClass + " FAILED");

        CrashReporter.recordEvent(
                CrashReporter.EVENT_MIXIN_FAILURE,
                mixinClass,
                "Target: " + targetClass + ", Error: " + (error != null ? error.getMessage() : "Unknown"));

        if (DevMode.isEnabled() && error != null) {
            error.printStackTrace();
        }
    }

    /**
     * Lua 예산 초과 처리.
     * 경고만 남기고 계속 실행.
     * 
     * @param contextId    컨텍스트 ID
     * @param actualMicros 실제 사용 시간 (마이크로초)
     * @param budgetMicros 설정된 예산 (마이크로초)
     */
    public static void handleLuaBudgetExceeded(String contextId, long actualMicros, long budgetMicros) {
        double actualMs = actualMicros / 1000.0;
        double budgetMs = budgetMicros / 1000.0;

        Pulse.warn("pulse", String.format(
                "[Failsoft/Lua] Budget exceeded: %s (%.2fms / %.2fms)",
                contextId, actualMs, budgetMs));

        CrashReporter.recordEvent(
                CrashReporter.EVENT_LUA_BUDGET_EXCEEDED,
                contextId,
                String.format("%.2fms / %.2fms (%.0f%% over)",
                        actualMs, budgetMs, ((actualMs - budgetMs) / budgetMs) * 100));
    }

    /**
     * ClassNotFound 처리.
     * 해당 기능만 스킵.
     * 
     * @param className 찾지 못한 클래스명
     * @param feature   관련 기능명
     */
    public static void handleClassNotFound(String className, String feature) {
        FeatureFlags.disable(feature);

        Pulse.warn("pulse", "[Failsoft/Class] " + className + " not found, disabling: " + feature);

        CrashReporter.recordEvent(
                "CLASS_NOT_FOUND",
                feature,
                "Missing class: " + className);
    }

    /**
     * 시그니처 미스매치 처리.
     * 해당 기능 비활성화.
     * 
     * @param className  클래스명
     * @param methodName 메서드명
     * @param feature    관련 기능명
     * @param expected   예상 시그니처
     * @param actual     실제 시그니처
     */
    public static void handleSignatureMismatch(String className, String methodName,
            String feature, String expected, String actual) {
        FeatureFlags.disable(feature);

        Pulse.warn("pulse", String.format(
                "[Failsoft/Signature] %s.%s mismatch, disabling: %s",
                className, methodName, feature));

        CrashReporter.recordEvent(
                "SIGNATURE_MISMATCH",
                feature,
                String.format("%s.%s: expected %s, got %s", className, methodName, expected, actual));
    }

    // ═══════════════════════════════════════════════════════════════
    // v0.9 Fuse/Nerve 전용 핸들러
    // ═══════════════════════════════════════════════════════════════

    /**
     * 페이즈 시퀀스 오류 처리 (v0.9 Fuse/Nerve).
     * 페이즈 순서가 예상과 다를 때 호출.
     * 
     * @param phase    현재 페이즈
     * @param expected 예상된 페이즈
     * @param actual   실제 페이즈
     */
    public static void handlePhaseSequenceError(String phase, String expected, String actual) {
        Pulse.warn("pulse", String.format(
                "[Failsoft/Phase] Sequence error in '%s': expected '%s', got '%s'",
                phase, expected, actual));

        CrashReporter.recordEvent(
                "PHASE_SEQUENCE_ERROR",
                phase,
                String.format("Expected: %s, Actual: %s", expected, actual));
    }

    /**
     * 안전하지 않은 월드 상태 접근 처리 (v0.9 Fuse/Nerve).
     * 월드 초기화 전이나 언로드 후 월드 상태에 접근할 때 호출.
     * 
     * @param context   컨텍스트 (어떤 모듈/기능에서 발생했는지)
     * @param operation 시도한 작업
     */
    public static void handleUnsafeWorldstateAccess(String context, String operation) {
        Pulse.warn("pulse", String.format(
                "[Failsoft/Worldstate] Unsafe access in '%s': %s",
                context, operation));

        CrashReporter.recordEvent(
                "UNSAFE_WORLDSTATE_ACCESS",
                context,
                "Operation: " + operation);
    }
}
