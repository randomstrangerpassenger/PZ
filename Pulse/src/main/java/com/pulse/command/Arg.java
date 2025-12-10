package com.pulse.command;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 명령어 인자 어노테이션.
 * 메서드 파라미터에 적용.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.PARAMETER)
public @interface Arg {
    /**
     * 인자 이름
     */
    String value();

    /**
     * 선택적 인자 여부
     */
    boolean optional() default false;

    /**
     * 기본값 (선택적 인자용)
     */
    String defaultValue() default "";
}
