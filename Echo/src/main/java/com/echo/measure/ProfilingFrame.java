package com.echo.measure;

import java.util.concurrent.atomic.AtomicLong;

/**
 * 스택 프레임 - 진행 중인 측정 정보
 */
class ProfilingFrame {
    private static final AtomicLong idCounter = new AtomicLong(0);

    final long id;
    final ProfilingPoint point;
    final String customLabel;
    final long startTime;

    ProfilingFrame(ProfilingPoint point, long startTime) {
        this.id = idCounter.incrementAndGet();
        this.point = point;
        this.customLabel = null;
        this.startTime = startTime;
    }

    ProfilingFrame(ProfilingPoint point, String customLabel, long startTime) {
        this.id = idCounter.incrementAndGet();
        this.point = point;
        this.customLabel = customLabel;
        this.startTime = startTime;
    }
}
