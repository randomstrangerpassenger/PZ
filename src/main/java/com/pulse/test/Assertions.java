package com.pulse.test;

/**
 * 테스트 어설션.
 */
public class Assertions {

    public static void assertTrue(boolean condition) {
        if (!condition) {
            throw new AssertionError("Expected true but was false");
        }
    }

    public static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static void assertFalse(boolean condition) {
        if (condition) {
            throw new AssertionError("Expected false but was true");
        }
    }

    public static void assertFalse(boolean condition, String message) {
        if (condition) {
            throw new AssertionError(message);
        }
    }

    public static void assertEquals(Object expected, Object actual) {
        if (!java.util.Objects.equals(expected, actual)) {
            throw new AssertionError("Expected: " + expected + " but was: " + actual);
        }
    }

    public static void assertEquals(Object expected, Object actual, String message) {
        if (!java.util.Objects.equals(expected, actual)) {
            throw new AssertionError(message + " - Expected: " + expected + " but was: " + actual);
        }
    }

    public static void assertNotEquals(Object unexpected, Object actual) {
        if (java.util.Objects.equals(unexpected, actual)) {
            throw new AssertionError("Expected not equal to: " + unexpected);
        }
    }

    public static void assertNull(Object obj) {
        if (obj != null) {
            throw new AssertionError("Expected null but was: " + obj);
        }
    }

    public static void assertNotNull(Object obj) {
        if (obj == null) {
            throw new AssertionError("Expected not null");
        }
    }

    public static void assertNotNull(Object obj, String message) {
        if (obj == null) {
            throw new AssertionError(message);
        }
    }

    public static <T extends Throwable> T assertThrows(Class<T> expectedType, Runnable executable) {
        try {
            executable.run();
            throw new AssertionError("Expected " + expectedType.getSimpleName() + " to be thrown");
        } catch (Throwable t) {
            if (expectedType.isInstance(t)) {
                return expectedType.cast(t);
            }
            throw new AssertionError("Expected " + expectedType.getSimpleName() +
                    " but was " + t.getClass().getSimpleName());
        }
    }

    public static void fail() {
        throw new AssertionError("Test failed");
    }

    public static void fail(String message) {
        throw new AssertionError(message);
    }
}
