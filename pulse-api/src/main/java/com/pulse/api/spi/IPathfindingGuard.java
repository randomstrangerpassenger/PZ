package com.pulse.api.spi;

/**
 * 경로탐색 가드 인터페이스.
 * 
 * Fuse가 구현하여 Pulse에 등록.
 * Pulse는 경로탐색 요청 시 이 가드를 호출하여 defer 여부를 결정받음.
 * 
 * Hub & Spoke 원칙:
 * - Pulse는 "사실 제공 + 가드 호출"만 함
 * - Fuse가 "판단 + defer 설정"을 함
 * 
 * @since Pulse 2.1
 */
public interface IPathfindingGuard {

    /**
     * 경로탐색 요청 검사.
     * 
     * Fuse가 context를 검사하고 필요시 context.setDeferred(true)를 호출.
     * 반환값은 즉시 처리 여부.
     * 
     * @param context 경로탐색 컨텍스트 (읽기 + defer 설정)
     * @return true = 즉시 처리, false = 지연 (context.isDeferred() true)
     */
    boolean checkPathRequest(IPathfindingContext context);

    /**
     * 틱 시작 알림.
     * Fuse가 예산 리셋 등 틱 단위 작업 수행.
     * 
     * @param gameTick 현재 게임 틱
     */
    default void onTickStart(long gameTick) {
    }

    /**
     * 틱 종료 알림.
     * Fuse가 캐시 클리어 등 정리 작업 수행.
     * 
     * @param gameTick 현재 게임 틱
     */
    default void onTickEnd(long gameTick) {
    }
}
