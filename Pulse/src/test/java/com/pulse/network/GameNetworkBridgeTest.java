package com.pulse.network;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import static org.junit.jupiter.api.Assertions.*;

/**
 * GameNetworkBridge 단위 테스트.
 */
@Tag("unit")
class GameNetworkBridgeTest {

    @Test
    void getInstance_returnsSameInstance() {
        GameNetworkBridge instance1 = GameNetworkBridge.getInstance();
        GameNetworkBridge instance2 = GameNetworkBridge.getInstance();
        assertSame(instance1, instance2);
    }

    @Test
    void getInstance_notNull() {
        assertNotNull(GameNetworkBridge.getInstance());
    }

    @Test
    void isServer_withoutPZRuntime_returnsFalse() {
        assertFalse(GameNetworkBridge.getInstance().isServer());
    }

    @Test
    void isClient_withoutPZRuntime_returnsFalse() {
        assertFalse(GameNetworkBridge.getInstance().isClient());
    }

    @Test
    void reconnect_doesNotThrow() {
        assertDoesNotThrow(() -> GameNetworkBridge.getInstance().reconnect());
    }
}
