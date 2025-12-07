package com.pulse.config;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 설정 값 필드 어노테이션.
 * 설정 클래스 내의 필드에 적용하여 설정 메타데이터 제공.
 * 
 * 지원 타입:
 * - 기본형: boolean, int, long, float, double, String
 * - 배열: String[], int[] 등
 * - 리스트: List<String> 등
 * 
 * 사용 예:
 * 
 * <pre>
 * {@literal @}ConfigValue(comment = "Maximum items", min = 1, max = 1000)
 * public static int maxItems = 100;
 * 
 * {@literal @}ConfigValue(options = {"LOW", "MEDIUM", "HIGH"})
 * public static String quality = "MEDIUM";
 * 
 * {@literal @}ConfigValue(min = 0, max = 100, step = 5)
 * public static int volume = 50;
 * </pre>
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface ConfigValue {
    /**
     * 설정 설명/주석
     */
    String comment() default "";

    /**
     * 설정 키 이름 (기본값: 필드 이름)
     */
    String key() default "";

    /**
     * 최소값 (숫자 타입에만 적용)
     */
    double min() default Double.MIN_VALUE;

    /**
     * 최대값 (숫자 타입에만 적용)
     */
    double max() default Double.MAX_VALUE;

    /**
     * 재시작 필요 여부
     */
    boolean requiresRestart() default false;

    /**
     * 허용 값 목록 (String/Enum 타입용)
     * 비어있으면 제한 없음
     */
    String[] options() default {};

    /**
     * 증감 단위 (슬라이더 UI용)
     * 0이면 연속 값
     */
    double step() default 0;

    /**
     * 카테고리 (UI 그룹화용)
     */
    String category() default "";

    /**
     * 숨김 여부 (고급 사용자용)
     */
    boolean hidden() default false;
}
