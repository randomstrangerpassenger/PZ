package com.echo.measure;

/**
 * ProfilingScope 객체 풀 (Zero-Allocation)
 * 스레드당 하나씩 유지되어 동기화 불필요
 */
class ProfilingScopePool {
    private static final int POOL_SIZE = 16;
    private final ProfilingScope[] pool = new ProfilingScope[POOL_SIZE];
    private int index = 0;

    ProfilingScopePool() {
        for (int i = 0; i < POOL_SIZE; i++) {
            pool[i] = new ProfilingScope();
        }
    }

    ProfilingScope acquire(ProfilingPoint point, EchoProfiler profiler) {
        ProfilingScope scope;
        if (index > 0) {
            scope = pool[--index];
        } else {
            // 풀이 비어있으면 새로 생성 (드문 경우)
            scope = new ProfilingScope();
        }
        scope.init(point, profiler, this);
        return scope;
    }

    void release(ProfilingScope scope) {
        if (index < POOL_SIZE) {
            pool[index++] = scope;
        }
        // 풀이 가득 차면 버림 (GC가 정리)
    }
}
