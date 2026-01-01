package com.pulse.api.profiler;

/**
 * Hook 실행 시점의 컨텍스트 정보.
 * 
 * Pulse가 제공하는 최소한의 실행 컨텍스트.
 * 스로틀링 정책 구현체에서 실행 여부 결정에 활용.
 * 
 * @since Pulse 2.0
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
