package com.pulse.api;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 내부 API 마커.
 * 이 어노테이션이 붙은 클래스/메서드는 내부 구현용.
 * 
 * - 언제든 변경/제거 가능
 * - 외부 모드에서 사용 금지
 * - 문서화 대상 아님
 * 
 * 사용 예:
 * 
 * <pre>
 * @InternalAPI
 * public class MixinHelper { ... }
 * </pre>
 */
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target({ ElementType.TYPE, ElementType.METHOD, ElementType.FIELD, ElementType.CONSTRUCTOR, ElementType.PACKAGE })
public @interface InternalAPI {

    /**
     * 내부 API 사용 이유 (선택적 문서화).
     */
    String reason() default "";
}
