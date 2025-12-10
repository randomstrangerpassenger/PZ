package com.pulse.config;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 설정 유효성 검사 메서드 표시.
 * 메서드는 boolean을 반환해야 하며, 설정 로드 후 호출됨.
 * 
 * 사용 예:
 * 
 * <pre>
 * {@literal @}Config(modId = "mymod")
 * public class MyConfig {
 *     {@literal @}ConfigValue
 *     public static int minValue = 10;
 *     
 *     {@literal @}ConfigValue
 *     public static int maxValue = 100;
 *     
 *     {@literal @}Validate
 *     public static boolean validate() {
 *         // minValue가 maxValue보다 작아야 함
 *         return minValue < maxValue;
 *     }
 * }
 * </pre>
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Validate {
    /**
     * 검증 실패 시 메시지
     */
    String message() default "Validation failed";
}
