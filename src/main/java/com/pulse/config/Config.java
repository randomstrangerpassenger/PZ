package com.pulse.config;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 설정 클래스 마커 어노테이션.
 * 이 어노테이션이 붙은 클래스는 ConfigManager에 의해 자동으로 처리됨.
 * 
 * 사용 예:
 * 
 * <pre>
 * {@literal @}Config(modId = "mymod", fileName = "config.json")
 * public class MyModConfig {
 *     {@literal @}ConfigValue(comment = "Enable feature X")
 *     public static boolean enableFeatureX = true;
 * }
 * </pre>
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface Config {
    /**
     * 모드 ID (필수)
     */
    String modId();

    /**
     * 설정 파일 이름 (선택, 기본값: modId.json)
     */
    String fileName() default "";

    /**
     * 설정 카테고리 (선택, 폴더 구분용)
     */
    String category() default "";
}
