package com.echo.measure;

import com.echo.EchoRuntimeState;
import com.echo.LifecyclePhase;
import com.echo.config.EchoConfigSnapshot;
import org.junit.jupiter.api.*;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Phase 1-A: Stack Protocol Test
 * 
 * EchoProfiler의 스택 규약을 봉인합니다.
 * 이 테스트가 실패하면 리팩토링 즉시 롤백.
 */
class StackProtocolTest {

    private EchoProfiler profiler;
    private EchoConfigSnapshot originalSnapshot;

    @BeforeEach
    void setUp() {
        profiler = EchoProfiler.getInstance();
        profiler.reset();

        // 원래 스냅샷 저장
        originalSnapshot = EchoRuntimeState.current();

        // 테스트용 스냅샷 설정 (enabled=true, lifecyclePhase=RUNNING)
        EchoConfigSnapshot testSnapshot = new EchoConfigSnapshot(
                true, // enabled
                false, // luaProfilingEnabled
                33.33, // spikeThresholdMs
                LifecyclePhase.RUNNING, // lifecyclePhase - 핵심!
                true // debugMode
        );
        EchoRuntimeState.setForTest(testSnapshot);

        // 메인 스레드 설정
        EchoProfiler.setMainThread(Thread.currentThread());
    }

    @AfterEach
    void tearDown() {
        profiler.disable();
        // 원래 스냅샷 복원
        EchoRuntimeState.setForTest(originalSnapshot);
    }

    // =========================================================
    // 규약 1: 메인 스레드 Fast-Path
    // =========================================================

    @Test
    @DisplayName("Protocol: Main thread fast-path uses dedicated stack")
    void mainThreadFastPath_정상동작() {
        // 메인 스레드에서 push/pop
        profiler.push(ProfilingPoint.TICK);
        assertEquals(1, profiler.getCurrentStackDepth(),
                "Main thread stack should have 1 frame after push");

        profiler.pop(ProfilingPoint.TICK);
        assertEquals(0, profiler.getCurrentStackDepth(),
                "Main thread stack should be empty after pop");

        // 데이터가 기록되었는지 확인
        var data = profiler.getTimingData(ProfilingPoint.TICK);
        assertEquals(1, data.getCallCount(), "Timing data should record 1 call");
    }

    @Test
    @DisplayName("Protocol: Main thread bypasses ThreadLocal")
    void mainThreadFastPath_ThreadLocal우회() throws Exception {
        // 메인 스레드에서 push
        profiler.push(ProfilingPoint.ZOMBIE_AI);

        // 다른 스레드에서 확인 - ThreadLocal은 비어있어야 함
        AtomicInteger otherThreadDepth = new AtomicInteger(-1);
        Thread otherThread = new Thread(() -> {
            otherThreadDepth.set(profiler.getCurrentStackDepth());
        });
        otherThread.start();
        otherThread.join(1000);

        assertEquals(0, otherThreadDepth.get(),
                "Other thread should not see main thread's stack");

        profiler.pop(ProfilingPoint.ZOMBIE_AI);
    }

    // =========================================================
    // 규약 2: ThreadLocal 격리
    // =========================================================

    @Test
    @DisplayName("Protocol: ThreadLocal isolation between threads")
    void threadLocal_격리확인() throws Exception {
        // 메인 스레드가 아닌 다른 스레드로 설정하여 ThreadLocal 사용
        Thread dummyMainThread = new Thread(() -> {
        });
        EchoProfiler.setMainThread(dummyMainThread);

        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch endLatch = new CountDownLatch(2);

        AtomicInteger thread1Depth = new AtomicInteger(-1);
        AtomicInteger thread2Depth = new AtomicInteger(-1);

        Thread t1 = new Thread(() -> {
            try {
                startLatch.await();
                profiler.push(ProfilingPoint.RENDER);
                profiler.push(ProfilingPoint.RENDER);
                thread1Depth.set(profiler.getCurrentStackDepth());
                Thread.sleep(50);
                profiler.pop(ProfilingPoint.RENDER);
                profiler.pop(ProfilingPoint.RENDER);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                endLatch.countDown();
            }
        });

        Thread t2 = new Thread(() -> {
            try {
                startLatch.await();
                profiler.push(ProfilingPoint.ZOMBIE_PATHFINDING);
                thread2Depth.set(profiler.getCurrentStackDepth());
                Thread.sleep(50);
                profiler.pop(ProfilingPoint.ZOMBIE_PATHFINDING);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                endLatch.countDown();
            }
        });

        t1.start();
        t2.start();
        startLatch.countDown();
        assertTrue(endLatch.await(5, TimeUnit.SECONDS));

        assertEquals(2, thread1Depth.get(), "Thread 1 should have depth 2");
        assertEquals(1, thread2Depth.get(), "Thread 2 should have depth 1");

        // 메인 스레드 복원
        EchoProfiler.setMainThread(Thread.currentThread());
    }

    // =========================================================
    // 규약 3: Push/Pop 순서
    // =========================================================

    @Test
    @DisplayName("Protocol: Push/Pop must follow LIFO order")
    void pushPop_순서규약() {
        profiler.push(ProfilingPoint.TICK);
        profiler.push(ProfilingPoint.ZOMBIE_AI);
        profiler.push(ProfilingPoint.ZOMBIE_PATHFINDING);

        assertEquals(3, profiler.getCurrentStackDepth());
        assertEquals(ProfilingPoint.ZOMBIE_PATHFINDING, profiler.getCurrentPoint());

        profiler.pop(ProfilingPoint.ZOMBIE_PATHFINDING);
        assertEquals(2, profiler.getCurrentStackDepth());
        assertEquals(ProfilingPoint.ZOMBIE_AI, profiler.getCurrentPoint());

        profiler.pop(ProfilingPoint.ZOMBIE_AI);
        assertEquals(1, profiler.getCurrentStackDepth());
        assertEquals(ProfilingPoint.TICK, profiler.getCurrentPoint());

        profiler.pop(ProfilingPoint.TICK);
        assertEquals(0, profiler.getCurrentStackDepth());
        assertNull(profiler.getCurrentPoint());
    }

    @Test
    @DisplayName("Protocol: Mismatched pop should not crash (resilience)")
    void pushPop_불일치시복원력() {
        profiler.push(ProfilingPoint.TICK);

        // 불일치 pop (다른 포인트) - 크래시 없이 처리
        assertDoesNotThrow(() -> profiler.pop(ProfilingPoint.ZOMBIE_AI));

        // 스택은 비워짐
        assertEquals(0, profiler.getCurrentStackDepth());
    }

    @Test
    @DisplayName("Protocol: Pop on empty stack should not crash")
    void pushPop_빈스택Pop안전() {
        assertEquals(0, profiler.getCurrentStackDepth());

        // 빈 스택에서 pop - 크래시 없이 처리
        assertDoesNotThrow(() -> profiler.pop(ProfilingPoint.TICK));

        assertEquals(0, profiler.getCurrentStackDepth());
    }

    // =========================================================
    // 규약 4: Scope Pool 재사용
    // =========================================================

    @Test
    @DisplayName("Protocol: Scope API uses object pool")
    void scopePool_재사용규약() {
        // 첫 번째 scope
        try (var scope1 = profiler.scope(ProfilingPoint.TICK)) {
            assertEquals(1, profiler.getCurrentStackDepth());
        }
        assertEquals(0, profiler.getCurrentStackDepth());

        // 두 번째 scope - 풀에서 재사용되어야 함 (allocation 감소)
        try (var scope2 = profiler.scope(ProfilingPoint.TICK)) {
            assertEquals(1, profiler.getCurrentStackDepth());
        }
        assertEquals(0, profiler.getCurrentStackDepth());

        // 호출 횟수 확인
        var data = profiler.getTimingData(ProfilingPoint.TICK);
        assertEquals(2, data.getCallCount(), "Should record 2 scope calls");
    }

    @Test
    @DisplayName("Protocol: Scope auto-closes on exception")
    void scopePool_예외시자동종료() {
        try {
            try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI)) {
                assertEquals(1, profiler.getCurrentStackDepth());
                throw new RuntimeException("Test exception");
            }
        } catch (RuntimeException e) {
            // 예외 발생 후 스택이 비워져야 함
            assertEquals(0, profiler.getCurrentStackDepth(),
                    "Stack should be empty after exception in scope");
        }

        // 호출은 기록되어야 함
        var data = profiler.getTimingData(ProfilingPoint.ZOMBIE_AI);
        assertEquals(1, data.getCallCount());
    }

    // =========================================================
    // 규약 5: 핫패스 접근 경로 유지 (v3.1 조건)
    // =========================================================

    @Test
    @DisplayName("Protocol: TimingData access must be O(1)")
    void hotPath_TimingData접근O1() {
        // 사전 웜업
        for (int i = 0; i < 1000; i++) {
            profiler.push(ProfilingPoint.TICK);
            profiler.pop(ProfilingPoint.TICK);
        }

        // 벤치마크
        long start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            var data = profiler.getTimingData(ProfilingPoint.TICK);
            assertNotNull(data);
        }
        long elapsed = System.nanoTime() - start;
        double nsPerAccess = (double) elapsed / 10000;

        System.out.println("TimingData access: " + nsPerAccess + " ns/op");

        // O(1) 접근은 200ns 미만이어야 함 (관대한 기준 - CI 환경 고려)
        assertTrue(nsPerAccess < 200,
                "TimingData access should be < 200ns, actual: " + nsPerAccess);
    }
}
