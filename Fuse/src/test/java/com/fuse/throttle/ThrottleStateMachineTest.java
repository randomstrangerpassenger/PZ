package com.fuse.throttle;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * ThrottleStateMachine 단위 테스트.
 * 
 * Game-free 테스트: 게임 객체 없이 상태 전이 로직만 검증.
 */
class ThrottleStateMachineTest {

    private ThrottleStateMachine stateMachine;

    @BeforeEach
    void setUp() {
        stateMachine = new ThrottleStateMachine();
    }

    @Test
    @DisplayName("초기 상태는 FULL 레벨과 비활성")
    void initialState() {
        assertEquals(ThrottleLevel.FULL, stateMachine.getCurrentLevel());
        assertFalse(stateMachine.isActive());
        assertEquals(0, stateMachine.getStabilityCounter());
    }

    @Test
    @DisplayName("통계 없으면 입력 레벨 그대로 반환")
    void bypassWithoutStats() {
        ThrottleLevel result = stateMachine.apply(null, ThrottleLevel.REDUCED);
        assertEquals(ThrottleLevel.REDUCED, result);
    }

    @Test
    @DisplayName("진입 조건 - 1초 max 초과 시 상태 전환")
    void entryConditionMax1s() {
        MockRollingTickStats stats = new MockRollingTickStats();
        stats.setLast1sMaxMs(40.0); // > 33.33ms
        stats.setLast5sAvgMs(10.0);
        stats.setHasEnoughData(true);

        ThrottleLevel result = stateMachine.apply(stats, ThrottleLevel.FULL);

        assertTrue(stateMachine.isActive());
        assertEquals(ThrottleLevel.REDUCED, result); // FULL -> REDUCED
    }

    @Test
    @DisplayName("진입 조건 - 5초 avg 초과 시 상태 전환")
    void entryConditionAvg5s() {
        MockRollingTickStats stats = new MockRollingTickStats();
        stats.setLast1sMaxMs(20.0);
        stats.setLast5sAvgMs(25.0); // > 20ms
        stats.setHasEnoughData(true);

        stateMachine.apply(stats, ThrottleLevel.FULL);

        assertTrue(stateMachine.isActive());
    }

    @Test
    @DisplayName("복구 조건 - 5초 avg < 12ms가 N틱 유지 시 복구")
    void exitCondition() {
        // 먼저 진입
        MockRollingTickStats highStats = new MockRollingTickStats();
        highStats.setLast1sMaxMs(40.0);
        highStats.setLast5sAvgMs(10.0);
        highStats.setHasEnoughData(true);
        stateMachine.apply(highStats, ThrottleLevel.FULL);
        assertTrue(stateMachine.isActive());

        // 안정 상태 시뮬레이션 (300틱)
        MockRollingTickStats lowStats = new MockRollingTickStats();
        lowStats.setLast1sMaxMs(10.0);
        lowStats.setLast5sAvgMs(10.0); // < 12ms
        lowStats.setHasEnoughData(true);

        for (int i = 0; i < 300; i++) {
            stateMachine.apply(lowStats, ThrottleLevel.REDUCED);
        }

        assertFalse(stateMachine.isActive());
        assertEquals(ThrottleLevel.FULL, stateMachine.getCurrentLevel());
    }

    @Test
    @DisplayName("연속 강등 - FULL -> REDUCED -> LOW -> MINIMAL")
    void consecutiveDemotion() {
        MockRollingTickStats highStats = new MockRollingTickStats();
        highStats.setLast1sMaxMs(40.0);
        highStats.setLast5sAvgMs(10.0);
        highStats.setHasEnoughData(true);

        // 1차 강등
        stateMachine.apply(highStats, ThrottleLevel.FULL);
        assertEquals(ThrottleLevel.REDUCED, stateMachine.getCurrentLevel());

        // 2차 강등
        stateMachine.apply(highStats, ThrottleLevel.FULL);
        assertEquals(ThrottleLevel.LOW, stateMachine.getCurrentLevel());

        // 3차 강등
        stateMachine.apply(highStats, ThrottleLevel.FULL);
        assertEquals(ThrottleLevel.MINIMAL, stateMachine.getCurrentLevel());

        // 최하위에서 더 이상 강등 안됨
        stateMachine.apply(highStats, ThrottleLevel.FULL);
        assertEquals(ThrottleLevel.MINIMAL, stateMachine.getCurrentLevel());
    }

    @Test
    @DisplayName("reset()은 모든 상태 초기화")
    void resetClearsState() {
        MockRollingTickStats highStats = new MockRollingTickStats();
        highStats.setLast1sMaxMs(40.0);
        highStats.setLast5sAvgMs(10.0);
        highStats.setHasEnoughData(true);
        stateMachine.apply(highStats, ThrottleLevel.FULL);

        stateMachine.reset();

        assertEquals(ThrottleLevel.FULL, stateMachine.getCurrentLevel());
        assertFalse(stateMachine.isActive());
        assertEquals(0, stateMachine.getStabilityCounter());
    }

    // === Mock RollingTickStats ===
    static class MockRollingTickStats extends com.fuse.governor.RollingTickStats {
        private double last1sMaxMs;
        private double last5sAvgMs;
        private boolean hasEnoughData;

        @Override
        public double getLast1sMaxMs() {
            return last1sMaxMs;
        }

        void setLast1sMaxMs(double value) {
            this.last1sMaxMs = value;
        }

        @Override
        public double getLast5sAvgMs() {
            return last5sAvgMs;
        }

        void setLast5sAvgMs(double value) {
            this.last5sAvgMs = value;
        }

        @Override
        public boolean hasEnoughData() {
            return hasEnoughData;
        }

        void setHasEnoughData(boolean value) {
            this.hasEnoughData = value;
        }
    }
}
