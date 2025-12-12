package com.pulse.command;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import static org.junit.jupiter.api.Assertions.*;

/**
 * CommandContext 단위 테스트.
 */
@Tag("unit")
class CommandContextTest {

    private CommandContext ctx;

    @BeforeEach
    void setUp() {
        String[] args = { "status", "verbose", "42" };
        ctx = new CommandContext(new MockSender(), "test", args);
    }

    @Test
    void getArg_returnsCorrectArg() {
        assertEquals("status", ctx.getArg(0));
        assertEquals("verbose", ctx.getArg(1));
        assertEquals("42", ctx.getArg(2));
    }

    @Test
    void getArg_returnsNullForInvalidIndex() {
        assertNull(ctx.getArg(-1));
        assertNull(ctx.getArg(10));
    }

    @Test
    void getArg_withDefault_returnsDefaultForMissing() {
        assertEquals("default", ctx.getArg(10, "default"));
    }

    @Test
    void hasArg_returnsTrueForValidIndex() {
        assertTrue(ctx.hasArg(0));
        assertTrue(ctx.hasArg(2));
        assertFalse(ctx.hasArg(3));
    }

    @Test
    void getInt_parsesInteger() {
        Integer value = ctx.getInt(2);
        assertEquals(42, value);
    }

    @Test
    void getInt_returnsNullForNonInteger() {
        Integer value = ctx.getInt(0); // "status" is not an integer
        assertNull(value);
    }

    @Test
    void getInt_withDefault_returnsDefaultForMissing() {
        int value = ctx.getInt(10, 99);
        assertEquals(99, value);
    }

    @Test
    void getBoolean_parsesTruthy() {
        CommandContext boolCtx = new CommandContext(new MockSender(), "cmd",
                new String[] { "true", "yes", "1", "false" });

        assertTrue(boolCtx.getBoolean(0));
        assertTrue(boolCtx.getBoolean(1));
        assertTrue(boolCtx.getBoolean(2));
        assertFalse(boolCtx.getBoolean(3));
    }

    @Test
    void getRemainingArgs_joinsArgs() {
        ctx.nextArg(); // consume "status"
        String remaining = ctx.getRemainingArgs();
        assertEquals("verbose 42", remaining);
    }

    @Test
    void getArgCount_returnsCorrectCount() {
        assertEquals(3, ctx.getArgCount());
    }

    // 테스트용 Mock CommandSender
    // 테스트용 Mock CommandSender
    private static class MockSender implements CommandSender {

        @Override
        public void sendMessage(String message) {
        }

        @Override
        public void sendError(String message) {
        }

        @Override
        public boolean hasPermission(String permission) {
            return true;
        }

        @Override
        public String getName() {
            return "TestSender";
        }

        @Override
        public boolean isPlayer() {
            return false;
        }

        @Override
        public boolean isConsole() {
            return true;
        }

        @Override
        public Object getPlayer() {
            return null;
        }
    }
}
