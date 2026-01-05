package com.fuse;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

/**
 * FuseLifecycle 단위 테스트.
 * 
 * 참고: 전체 init()은 Pulse 환경 의존성으로 인해 통합 테스트에서 수행.
 * 여기서는 기본 상태와 접근자만 테스트.
 */
class FuseLifecycleTest {

    private FuseComponentRegistry registry;
    private FuseLifecycle lifecycle;

    @BeforeEach
    void setUp() {
        registry = new FuseComponentRegistry();
        lifecycle = new FuseLifecycle(registry);
    }

    @Test
    @DisplayName("생성 직후 initialized는 false")
    void notInitializedOnConstruction() {
        assertFalse(lifecycle.isInitialized());
    }

    @Test
    @DisplayName("tickCounter는 0으로 시작")
    void tickCounterStartsAtZero() {
        assertEquals(0, lifecycle.getTickCounter());
    }

    @Test
    @DisplayName("getRegistry는 생성자에서 받은 registry 반환")
    void getRegistryReturnsInjectedRegistry() {
        assertSame(registry, lifecycle.getRegistry());
    }

    @Test
    @DisplayName("초기화 전 onTick 호출은 안전하게 무시됨")
    void onTickBeforeInitIsSafe() {
        // Should not throw
        assertDoesNotThrow(() -> lifecycle.onTick());
    }
}
