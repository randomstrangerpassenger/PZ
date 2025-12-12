package com.pulse.lua;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import static org.junit.jupiter.api.Assertions.*;

/**
 * LuaBridge 단위 테스트.
 * PZ 런타임 없이 테스트 가능한 항목만 포함.
 */
@Tag("unit")
class LuaBridgeTest {

    @Test
    void getInstance_returnsSameInstance() {
        LuaBridge instance1 = LuaBridge.getInstance();
        LuaBridge instance2 = LuaBridge.getInstance();
        assertSame(instance1, instance2);
    }

    @Test
    void call_withNullFunction_returnsNull() {
        Object result = LuaBridge.call(null);
        assertNull(result);
    }

    @Test
    void call_withInvalidFunction_returnsNull() {
        Object result = LuaBridge.call("nonExistentLuaFunction12345");
        assertNull(result);
    }

    @Test
    void getGlobal_withNullName_returnsNull() {
        Object result = LuaBridge.getGlobal(null);
        assertNull(result);
    }

    @Test
    void setGlobal_withNullName_doesNotThrow() {
        assertDoesNotThrow(() -> LuaBridge.setGlobal(null, "value"));
    }
}
