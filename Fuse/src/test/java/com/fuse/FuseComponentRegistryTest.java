package com.fuse;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

/**
 * FuseComponentRegistry 단위 테스트.
 */
class FuseComponentRegistryTest {

    private FuseComponentRegistry registry;

    @BeforeEach
    void setUp() {
        registry = new FuseComponentRegistry();
    }

    @Test
    @DisplayName("초기 상태에서 모든 컴포넌트는 null")
    void initialStateAllNull() {
        assertEquals(0, registry.getComponentCount());
        assertNull(registry.getGovernor());
        assertNull(registry.getPanicProtocol());
        assertNull(registry.getStats());
        assertNull(registry.getOptimizer());
    }

    @Test
    @DisplayName("컴포넌트 설정 후 getComponentCount 증가")
    void componentCountIncreases() {
        assertEquals(0, registry.getComponentCount());

        registry.setGovernor(new com.fuse.governor.TickBudgetGovernor());
        assertEquals(1, registry.getComponentCount());

        registry.setStats(new com.fuse.governor.RollingTickStats());
        assertEquals(2, registry.getComponentCount());
    }

    @Test
    @DisplayName("Getter는 설정된 값을 반환")
    void getterReturnsSetValue() {
        var governor = new com.fuse.governor.TickBudgetGovernor();
        registry.setGovernor(governor);

        assertSame(governor, registry.getGovernor());
    }
}
