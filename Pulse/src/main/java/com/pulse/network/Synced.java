package com.pulse.network;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 자동 동기화 필드 마커.
 * 이 어노테이션이 붙은 필드는 자동으로 서버-클라이언트 간 동기화됨.
 * 
 * 사용 예:
 * 
 * <pre>
 * public class MyEntity {
 *     &#64;Synced
 *     private int health;
 * 
 *     @Synced(direction = SyncDirection.SERVER_TO_CLIENT)
 *     private String name;
 * }
 * </pre>
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface Synced {

    /**
     * 동기화 방향.
     */
    SyncDirection direction() default SyncDirection.BIDIRECTIONAL;

    /**
     * 동기화 우선순위 (낮을수록 먼저).
     */
    int priority() default 100;

    /**
     * 변경 시에만 동기화할지 여부.
     */
    boolean onlyOnChange() default true;

    public enum SyncDirection {
        SERVER_TO_CLIENT, // 서버 → 클라이언트
        CLIENT_TO_SERVER, // 클라이언트 → 서버
        BIDIRECTIONAL // 양방향
    }
}
