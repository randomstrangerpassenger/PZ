package com.echo;

import com.echo.config.EchoConfigSnapshot;

/**
 * Echo 런타임 상태 홀더
 * 
 * 핫패스에서 설정에 접근하기 위한 단일 진입점입니다.
 * - current()는 절대 예외를 던지지 않음
 * - current()는 절대 null을 반환하지 않음
 * - 스냅샷 갱신은 느린 경로에서만 수행
 * 
 * 사용법:
 * 
 * <pre>
 * EchoConfigSnapshot state = EchoRuntimeState.current();
 * if (!state.enabled)
 *     return; // Fast-Exit
 * </pre>
 * 
 * @since Bundle A - Hot Path 무음화
 */
public final class EchoRuntimeState {

    /** 현재 스냅샷 (volatile - 핫패스에서 안전하게 읽기) */
    private static volatile EchoConfigSnapshot snapshot = EchoConfigSnapshot.DEFAULT;

    // 생성자 금지
    private EchoRuntimeState() {
    }

    /**
     * 현재 설정 스냅샷 조회 (핫패스 안전)
     * 
     * 규약:
     * - 절대 예외를 던지지 않음
     * - 절대 null을 반환하지 않음
     * - volatile read만 수행 (O(1))
     * 
     * @return 현재 스냅샷 (항상 non-null)
     */
    public static EchoConfigSnapshot current() {
        return snapshot; // volatile read only
    }

    /**
     * 스냅샷 갱신 (느린 경로 전용)
     * 
     * 호출 시점:
     * - OnGameStart 이벤트
     * - UI에서 설정 변경 Apply
     * - enable() / disable() 호출
     * 
     * 핫패스에서 호출 금지!
     * 
     * @param newSnapshot 새 스냅샷 (null이면 DEFAULT 사용)
     */
    public static void update(EchoConfigSnapshot newSnapshot) {
        snapshot = (newSnapshot != null) ? newSnapshot : EchoConfigSnapshot.DEFAULT;
    }

    /**
     * 기본 스냅샷으로 리셋
     * 
     * 종료 시 또는 테스트에서 사용합니다.
     */
    public static void reset() {
        snapshot = EchoConfigSnapshot.DEFAULT;
    }

    /**
     * 스냅샷 직접 설정 (테스트 전용)
     * 
     * @param testSnapshot 테스트용 스냅샷
     */
    @com.pulse.api.VisibleForTesting
    public static void setForTest(EchoConfigSnapshot testSnapshot) {
        snapshot = testSnapshot;
    }
}
