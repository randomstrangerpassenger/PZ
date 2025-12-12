package com.pulse.test;

import com.pulse.api.log.PulseLogger;
import java.lang.reflect.*;
import java.util.*;

/**
 * 헤드리스 테스트 러너.
 * 게임 없이 모드 코드 테스트.
 */
public class TestRunner {

    private static final TestRunner INSTANCE = new TestRunner();
    private static final String LOG = PulseLogger.PULSE;

    private final List<TestResult> results = new ArrayList<>();
    private int passed = 0;
    private int failed = 0;

    private TestRunner() {
    }

    public static TestRunner getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 테스트 실행
    // ─────────────────────────────────────────────────────────────

    /**
     * 테스트 클래스 실행.
     */
    public static void run(Class<?> testClass) {
        INSTANCE.runClass(testClass);
    }

    private void runClass(Class<?> testClass) {
        PulseLogger.info(LOG, "\n═══════════════════════════════════════");
        PulseLogger.info(LOG, "  Running: {}", testClass.getSimpleName());
        PulseLogger.info(LOG, "═══════════════════════════════════════");

        Object instance = null;
        try {
            instance = testClass.getDeclaredConstructor().newInstance();
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to instantiate test class: {}", e.getMessage());
            return;
        }

        // @BeforeAll
        invokeAnnotatedMethods(testClass, instance, BeforeAll.class, true);

        // 테스트 메서드 실행
        for (Method method : testClass.getDeclaredMethods()) {
            if (method.isAnnotationPresent(Test.class)) {
                // @BeforeEach
                invokeAnnotatedMethods(testClass, instance, BeforeEach.class, false);

                runTest(instance, method);

                // @AfterEach
                invokeAnnotatedMethods(testClass, instance, AfterEach.class, false);
            }
        }

        // @AfterAll
        invokeAnnotatedMethods(testClass, instance, AfterAll.class, true);

        printSummary();
    }

    private void runTest(Object instance, Method method) {
        String testName = method.getDeclaringClass().getSimpleName() + "." + method.getName();
        long startTime = System.nanoTime();

        try {
            method.setAccessible(true);
            method.invoke(instance);

            long duration = (System.nanoTime() - startTime) / 1_000_000;
            passed++;
            results.add(new TestResult(testName, true, duration, null));
            PulseLogger.info(LOG, "  ✓ {} ({}ms)", method.getName(), duration);

        } catch (InvocationTargetException e) {
            long duration = (System.nanoTime() - startTime) / 1_000_000;
            Throwable cause = e.getCause();
            failed++;
            results.add(new TestResult(testName, false, duration, cause));
            results.add(new TestResult(testName, false, duration, cause));
            PulseLogger.info(LOG, "  ✗ {} - {}", method.getName(), cause.getMessage());
        } catch (Exception e) {
            failed++;
            results.add(new TestResult(testName, false, 0, e));
            results.add(new TestResult(testName, false, 0, e));
            PulseLogger.info(LOG, "  ✗ {} - {}", method.getName(), e.getMessage());
        }
    }

    private void invokeAnnotatedMethods(Class<?> clazz, Object instance,
            Class<? extends java.lang.annotation.Annotation> annotation, boolean isStatic) {
        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(annotation)) {
                try {
                    method.setAccessible(true);
                    method.invoke(isStatic && Modifier.isStatic(method.getModifiers()) ? null : instance);
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Setup/Teardown failed: {}", e.getMessage());
                }
            }
        }
    }

    private void printSummary() {
        PulseLogger.info(LOG, "───────────────────────────────────────");
        PulseLogger.info(LOG, "  Results: {} passed, {} failed", passed, failed);
        PulseLogger.info(LOG, "═══════════════════════════════════════\n");
    }

    /**
     * 모든 테스트 결과 초기화.
     */
    public static void reset() {
        INSTANCE.results.clear();
        INSTANCE.passed = 0;
        INSTANCE.failed = 0;
    }

    /**
     * 테스트 결과 조회.
     */
    public static List<TestResult> getResults() {
        return new ArrayList<>(INSTANCE.results);
    }

    // ─────────────────────────────────────────────────────────────
    // 테스트 결과
    // ─────────────────────────────────────────────────────────────

    public static class TestResult {
        public final String testName;
        public final boolean passed;
        public final long durationMs;
        public final Throwable error;

        TestResult(String testName, boolean passed, long durationMs, Throwable error) {
            this.testName = testName;
            this.passed = passed;
            this.durationMs = durationMs;
            this.error = error;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 어노테이션
    // ─────────────────────────────────────────────────────────────

    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
    public @interface Test {
    }

    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
    public @interface BeforeEach {
    }

    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
    public @interface AfterEach {
    }

    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
    public @interface BeforeAll {
    }

    @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
    @java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
    public @interface AfterAll {
    }
}
