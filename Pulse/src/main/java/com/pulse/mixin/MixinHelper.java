package com.pulse.mixin;

import com.pulse.api.DevMode;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.event.Event;
import com.pulse.event.EventBus;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.function.Function;

/**
 * Mixin 개발 유틸리티.
 * Mixin 클래스에서 자주 사용되는 패턴을 헬퍼 메서드로 제공.
 * 
 * 사용 예:
 * 
 * <pre>
 * {@literal @}Mixin(IsoZombie.class)
 * public class ZombieMixin {
 *     {@literal @}Inject(method = "update", at = @At("HEAD"), cancellable = true)
 *     private void onUpdate(CallbackInfo ci) {
 *         IsoZombie zombie = MixinHelper.self(this);
 *         ZombieUpdateEvent event = new ZombieUpdateEvent(zombie);
 *         MixinHelper.fireEvent(event, ci);  // 자동으로 취소 처리
 *     }
 * }
 * </pre>
 */
public final class MixinHelper {

    private static final String LOG = PulseLogger.PULSE;

    private MixinHelper() {
    }

    // ─────────────────────────────────────────────────────────────
    // 이벤트 발행 헬퍼
    // ─────────────────────────────────────────────────────────────

    /**
     * 이벤트 발행 및 취소 처리.
     * 이벤트가 취소되면 CallbackInfo.cancel()을 자동 호출.
     * 
     * @param event 발행할 이벤트
     * @param ci    Mixin CallbackInfo
     * @return true if event was cancelled
     */
    public static boolean fireEvent(Event event, CallbackInfo ci) {
        EventBus.post(event);
        if (event.isCancellable() && event.isCancelled()) {
            ci.cancel();
            return true;
        }
        return false;
    }

    /**
     * 이벤트 발행만 수행 (취소 처리 없음).
     * 
     * @param event 발행할 이벤트
     * @return 발행된 이벤트 (체이닝용)
     */
    public static <T extends Event> T fire(T event) {
        EventBus.post(event);
        return event;
    }

    /**
     * 반환값이 있는 이벤트 발행.
     * 이벤트가 취소되면 지정된 반환값으로 설정.
     * 
     * @param event       발행할 이벤트
     * @param cir         Mixin CallbackInfoReturnable
     * @param returnValue 취소 시 반환할 값
     * @return true if event was cancelled
     */
    public static <T> boolean fireEventWithReturn(
            Event event,
            CallbackInfoReturnable<T> cir,
            T returnValue) {
        EventBus.post(event);
        if (event.isCancellable() && event.isCancelled()) {
            cir.setReturnValue(returnValue);
            return true;
        }
        return false;
    }

    /**
     * 조건부 이벤트 발행.
     * 조건이 참일 때만 이벤트 발행.
     * 
     * @param condition 발행 조건
     * @param event     발행할 이벤트
     * @param ci        Mixin CallbackInfo
     * @return true if event was cancelled
     */
    public static boolean fireEventIf(boolean condition, Event event, CallbackInfo ci) {
        if (!condition)
            return false;
        return fireEvent(event, ci);
    }

    // ─────────────────────────────────────────────────────────────
    // 캐스팅 헬퍼
    // ─────────────────────────────────────────────────────────────

    /**
     * Mixin에서 this를 원본 타입으로 캐스팅.
     * 
     * <pre>
     * // Mixin 클래스 내에서:
     * IsoZombie zombie = MixinHelper.self(this);
     * </pre>
     * 
     * @param mixinThis Mixin 클래스의 this
     * @return 원본 타입으로 캐스팅된 객체
     */
    @SuppressWarnings("unchecked")
    public static <T> T self(Object mixinThis) {
        return (T) mixinThis;
    }

    /**
     * 안전한 캐스팅 (실패 시 null 반환).
     * 
     * @param obj   캐스팅할 객체
     * @param clazz 타겟 클래스
     * @return 캐스팅된 객체 또는 null
     */
    public static <T> T safeCast(Object obj, Class<T> clazz) {
        if (obj == null)
            return null;
        if (clazz.isInstance(obj)) {
            return clazz.cast(obj);
        }
        return null;
    }

    // ─────────────────────────────────────────────────────────────
    // 반환값 조작 헬퍼
    // ─────────────────────────────────────────────────────────────

    /**
     * 반환값 설정 및 메서드 종료.
     * 
     * @param cir   Mixin CallbackInfoReturnable
     * @param value 반환할 값
     */
    public static <T> void setReturn(CallbackInfoReturnable<T> cir, T value) {
        cir.setReturnValue(value);
    }

    /**
     * 조건부 반환값 설정.
     * 
     * @param condition 조건
     * @param cir       Mixin CallbackInfoReturnable
     * @param value     반환할 값
     * @return true if return value was set
     */
    public static <T> boolean setReturnIf(boolean condition, CallbackInfoReturnable<T> cir, T value) {
        if (condition) {
            cir.setReturnValue(value);
            return true;
        }
        return false;
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * null-safe 비교.
     */
    public static boolean equals(Object a, Object b) {
        if (a == b)
            return true;
        if (a == null || b == null)
            return false;
        return a.equals(b);
    }

    /**
     * 디버그 로그 출력.
     * 
     * @param mixinName Mixin 클래스 이름
     * @param message   로그 메시지
     */
    public static void debug(String mixinName, String message) {
        PulseLogger.debug(LOG, "[Mixin/{}] {}", mixinName, message);
    }

    /**
     * 메서드 주입 성공 로그.
     * 
     * @param targetClass  타겟 클래스
     * @param targetMethod 타겟 메서드
     */
    public static void logInjection(String targetClass, String targetMethod) {
        PulseLogger.debug(LOG, "Injected: {}.{}", targetClass, targetMethod);
    }

    // ─────────────────────────────────────────────────────────────
    // @ModifyVariable / @Redirect 헬퍼
    // ─────────────────────────────────────────────────────────────

    /**
     * 로컬 변수 수정 헬퍼 (@ModifyVariable 용).
     * 
     * <pre>
     * {@literal @}ModifyVariable(method = "update", at = @At("HEAD"))
     * private float modifySpeed(float original) {
     *     return MixinHelper.modifyLocal(original, speed -> speed * 1.5f);
     * }
     * </pre>
     * 
     * @param original 원본 값
     * @param modifier 수정 함수
     * @return 수정된 값
     */
    public static <T> T modifyLocal(T original, Function<T, T> modifier) {
        return modifier.apply(original);
    }

    /**
     * 메서드 반환값 수정 헬퍼 (@Redirect 용).
     * 
     * <pre>
     * {@literal @}Redirect(method = "update", at = @At(value = "INVOKE", target = "..."))
     * private float redirectDamage(float original) {
     *     return MixinHelper.redirect(original, dmg -> dmg * 0.5f);
     * }
     * </pre>
     * 
     * @param original   원본 값
     * @param redirector 리다이렉트 함수
     * @return 수정된 값
     */
    public static <T> T redirect(T original, Function<T, T> redirector) {
        return redirector.apply(original);
    }

    /**
     * DevMode일 때만 디버그 로그 출력.
     * 
     * @param mixinName Mixin 이름
     * @param message   로그 메시지
     */
    public static void debugIf(String mixinName, String message) {
        if (DevMode.isEnabled()) {
            debug(mixinName, message);
        }
    }

    /**
     * DevMode일 때만 주입 로그 출력.
     * 
     * @param targetClass  타겟 클래스
     * @param targetMethod 타겟 메서드
     */
    public static void logInjectionIf(String targetClass, String targetMethod) {
        if (DevMode.isEnabled()) {
            logInjection(targetClass, targetMethod);
        }
    }
}
