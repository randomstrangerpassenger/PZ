package com.pulse.api.exception;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 예외 계층 단위 테스트.
 * 각 예외 클래스의 팩토리 메서드 및 메시지 포맷 검증.
 */
@Tag("unit")
class ExceptionHierarchyTest {

    @Test
    void configurationException_invalidValue() {
        var ex = ConfigurationException.invalidValue("threshold", -1, "Must be positive");
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("threshold"));
        assertTrue(ex.getMessage().contains("-1"));
        assertTrue(ex.getMessage().contains("positive"));
    }

    @Test
    void configurationException_missingRequired() {
        var ex = ConfigurationException.missingRequired("api_key");
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("api_key"));
        assertTrue(ex.getMessage().contains("missing"));
    }

    @Test
    void injectionException_serviceNotFound() {
        var ex = InjectionException.serviceNotFound(String.class);
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("String"));
        assertTrue(ex.getMessage().contains("not found"));
    }

    @Test
    void injectionException_circularDependency() {
        var ex = InjectionException.circularDependency(Object.class);
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("Circular"));
    }

    @Test
    void luaInteropException_executionError() {
        var cause = new RuntimeException("nil value");
        var ex = LuaInteropException.executionError("function test()", 42, cause);
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("42"));
        assertEquals(42, ex.getLineNumber());
        assertNotNull(ex.getCause());
    }

    @Test
    void luaInteropException_functionNotFound() {
        var ex = LuaInteropException.functionNotFound("onUpdate");
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("onUpdate"));
    }

    @Test
    void mixinApplyException_targetNotFound() {
        var ex = MixinApplyException.targetNotFound("MyMixin", "zombie.core.Target");
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("zombie.core.Target"));
        assertEquals("MyMixin", ex.getMixinClass());
        assertEquals("zombie.core.Target", ex.getTargetClass());
    }

    @Test
    void mixinApplyException_signatureMismatch() {
        var ex = MixinApplyException.signatureMismatch("TestMixin", "inject", "(I)V", "(J)V");
        assertNotNull(ex);
        assertTrue(ex.getMessage().contains("signature"));
        assertTrue(ex.getMessage().contains("(I)V"));
    }
}
