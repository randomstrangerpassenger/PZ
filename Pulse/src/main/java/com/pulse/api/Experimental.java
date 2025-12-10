package com.pulse.api;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 실험적 기능 마커.
 * 이 어노테이션이 붙은 API는 실험적이며 언제든 변경될 수 있음.
 * 
 * 사용 예:
 * 
 * <pre>
 * &#64;Experimental("Hot reload may cause memory leaks")
 * public void hotReload() { ... }
 * </pre>
 */
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target({ ElementType.TYPE, ElementType.METHOD, ElementType.FIELD })
public @interface Experimental {

    /**
     * 실험적인 이유 또는 주의사항.
     */
    String value() default "";

    /**
     * 안정화 예정 버전.
     */
    String targetVersion() default "";
}
