package com.echo.measure;

/**
 * try-with-resources용 스코프 (Poolable)
 * 
 * 예외 안전성:
 * try-with-resources 블록 내에서 예외가 발생해도 close()가 자동 호출되어
 * pop()이 실행됩니다. 이로 인해 스택의 정합성이 유지됩니다.
 */
public class ProfilingScope implements AutoCloseable {
    private ProfilingPoint point;
    private EchoProfiler profiler;
    private ProfilingScopePool pool;

    /**
     * 초기화 (객체 재사용을 위해 생성자 대신 사용)
     */
    void init(ProfilingPoint point, EchoProfiler profiler, ProfilingScopePool pool) {
        this.point = point;
        this.profiler = profiler;
        this.pool = pool;
    }

    @Override
    public void close() {
        if (profiler != null) {
            profiler.pop(point);
        }
        if (pool != null) {
            pool.release(this);
        }
    }
}
