package com.pulse.debug;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import static org.junit.jupiter.api.Assertions.*;

/**
 * DevConsole 단위 테스트.
 * 싱글톤 상태에 영향받지 않는 기본 테스트만 포함.
 */
@Tag("unit")
class DevConsoleTest {

    @Test
    void getInstance_returnsSameInstance() {
        DevConsole instance1 = DevConsole.getInstance();
        DevConsole instance2 = DevConsole.getInstance();
        assertSame(instance1, instance2);
    }

    @Test
    void getInstance_notNull() {
        assertNotNull(DevConsole.getInstance());
    }

    @Test
    void execute_withNull_doesNotThrow() {
        assertDoesNotThrow(() -> DevConsole.execute(null));
    }

    @Test
    void execute_withEmptyString_doesNotThrow() {
        assertDoesNotThrow(() -> DevConsole.execute(""));
    }
}
