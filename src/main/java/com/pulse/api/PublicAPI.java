package com.pulse.api;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 공개 API 마커.
 * 이 어노테이션이 붙은 클래스/메서드는 안정적인 공개 API로 간주됨.
 * 
 * - 시맨틱 버저닝 준수 (breaking change = major version)
 * - Deprecation 정책 적용 (최소 1 major version 유지)
 * - 문서화 의무
 * 
 * 사용 예:
 * 
 * <pre>
 * @PublicAPI(since = "1.0.0")
 * public class EventBus { ... }
 * </pre>
 */
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target({ ElementType.TYPE, ElementType.METHOD, ElementType.FIELD, ElementType.CONSTRUCTOR })
public @interface PublicAPI {

    /**
     * API가 도입된 버전.
     */
    String since() default "1.0.0";

    /**
     * API 상태.
     */
    Status status() default Status.STABLE;

    public enum Status {
        STABLE, // 안정 - 프로덕션 사용 가능
        EXPERIMENTAL, // 실험적 - 변경 가능
        BETA // 베타 - 대부분 안정, 마이너 변경 가능
    }
}
