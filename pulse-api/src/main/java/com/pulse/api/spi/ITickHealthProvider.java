package com.pulse.api.spi;

/**
 * Tick Health Provider SPI.
 * 
 * Tick 건강 상태(SlowTick, Spike 카운트 등)를 제공하는 인터페이스.
 * Echo 같은 프로파일러 모드가 구현하고, Nerve 같은 최적화 모드가 조회함.
 * 
 * 핵심 철학:
 * - 인터페이스(계약)는 pulse-api에 존재
 * - Echo는 이 인터페이스를 구현해서 Pulse에 등록 (선택)
 * - Nerve는 Pulse 레지스트리를 통해서만 조회 (Echo를 직접 참조 안함)
 * - Provider가 없으면 fail-open (안전 기본값 반환)
 * 
 * @since Pulse 1.1
 */
public interface ITickHealthProvider extends IProvider {

    /**
     * 현재 SlowTick 상태인지 확인.
     * SlowTick: 최근 틱이 임계값(예: 33.33ms)을 초과한 상태.
     * 
     * @return SlowTick 상태면 true
     */
    boolean isSlowTick();

    /**
     * 최근 N초 내 발생한 스파이크 횟수.
     * 스파이크: 틱 시간이 spikeTreshold(예: 100ms)를 초과한 횟수.
     * 
     * @return 스파이크 횟수 (0 이상)
     */
    int getRecentSpikeCount();

    /**
     * 최근 1초 내 최대 틱 시간 (ms).
     * 
     * @return 최대 틱 시간 (0 이상)
     */
    default double getLast1sMaxMs() {
        return 0.0;
    }

    /**
     * 최근 5초 평균 틱 시간 (ms).
     * 
     * @return 평균 틱 시간 (0 이상)
     */
    default double getLast5sAvgMs() {
        return 0.0;
    }

    /**
     * Tick Health가 "위험" 상태인지 확인.
     * 위험: 연속 스파이크, P95 초과 등.
     * 
     * @return 위험 상태면 true
     */
    default boolean isDangerous() {
        return getRecentSpikeCount() >= 3 || getLast1sMaxMs() > 100;
    }

    // ===================================
    // Fail-open 기본 구현 (Provider 없을 때)
    // ===================================

    /**
     * 기본 Tick Health Provider (fail-open).
     * Provider가 등록되지 않았을 때 사용되는 안전 기본값.
     */
    ITickHealthProvider DEFAULT = new ITickHealthProvider() {
        @Override
        public String getId() {
            return "default-tick-health";
        }

        @Override
        public String getName() {
            return "Default Tick Health Provider";
        }

        @Override
        public String getVersion() {
            return "1.0";
        }

        @Override
        public String getDescription() {
            return "Fail-open default provider - always returns safe values";
        }

        @Override
        public boolean isSlowTick() {
            return false; // 안전: SlowTick 아님
        }

        @Override
        public int getRecentSpikeCount() {
            return 0; // 안전: 스파이크 없음
        }

        @Override
        public boolean isEnabled() {
            return true;
        }
    };
}
