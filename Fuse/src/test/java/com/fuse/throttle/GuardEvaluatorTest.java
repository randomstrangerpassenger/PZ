package com.fuse.throttle;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * GuardEvaluator 단위 테스트.
 * 
 * Game-free 테스트: 비트마스크 기반 Hot-path 로직 검증.
 */
class GuardEvaluatorTest {

    private GuardEvaluator evaluator;

    @BeforeEach
    void setUp() {
        evaluator = new GuardEvaluator();
    }

    @Test
    @DisplayName("Guard 없으면 isBlocked() = false")
    void noGuards() {
        evaluator.setGuards(null, null);
        evaluator.updateForTick();

        assertFalse(evaluator.isBlocked());
        assertNull(evaluator.getOverrideLevel());
    }

    @Test
    @DisplayName("updateForTick() 호출 전에는 isBlocked() = false")
    void beforeUpdate() {
        assertFalse(evaluator.isBlocked());
    }

    @Test
    @DisplayName("캐시된 플래그는 updateForTick()으로만 갱신")
    void cacheConsistency() {
        evaluator.updateForTick();
        boolean first = evaluator.isBlocked();
        boolean second = evaluator.isBlocked();

        assertEquals(first, second);
    }

    @Test
    @DisplayName("isVehiclePassive()와 isStreamingYield() 분리 동작")
    void separateFlags() {
        evaluator.updateForTick();

        // Guard 없으면 둘 다 false
        assertFalse(evaluator.isVehiclePassive());
        assertFalse(evaluator.isStreamingYield());
    }
}
