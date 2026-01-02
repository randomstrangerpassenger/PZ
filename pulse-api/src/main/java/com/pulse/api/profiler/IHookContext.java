package com.pulse.api.profiler;

/**
 * Hook 실행 시점의 컨텍스트 정보.
 * 
 * Pulse가 제공하는 최소한의 실행 컨텍스트.
 * 스로틀링 정책 구현체에서 실행 여부 결정에 활용.
 * 
 * @since Pulse 2.0
 * @since Pulse 2.2 - getTarget(), getTimestamp() 추가
 */
public interface IHookContext {

    /**
     * 훅 식별자.
     * 
     * @return 훅 ID (예: "ZOMBIE_UPDATE", "WORLD_TICK")
     */
    String hookId();

    /**
     * 현재 게임 틱.
     * 
     * @return 월드 틱 카운트
     */
    long gameTick();

    /**
     * 훅의 대상 객체 (좀비, 아이템 등).
     * 
     * Pulse는 이 객체의 타입을 모르고 전달만 함.
     * 하위 모드가 리플렉션 등을 통해 실제 정보 추출.
     * 
     * @return 대상 객체, 없으면 null
     * @since Pulse 2.2
     */
    default Object getTarget() {
        return null;
    }

    /**
     * 고해상도 타임스탬프 (System.nanoTime).
     * 
     * 설정 시점의 값을 반환 (호출마다 새로 측정하지 않음).
     * 
     * @return 나노초 타임스탬프, 설정되지 않았으면 0
     * @since Pulse 2.2
     */
    default long getTimestamp() {
        return 0L;
    }

    /**
     * 빈 컨텍스트 (기본값).
     */
    IHookContext EMPTY = new IHookContext() {
        @Override
        public String hookId() {
            return "UNKNOWN";
        }

        @Override
        public long gameTick() {
            return 0;
        }
    };
}
