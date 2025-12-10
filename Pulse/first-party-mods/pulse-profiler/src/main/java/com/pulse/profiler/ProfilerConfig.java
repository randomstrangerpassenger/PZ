package com.pulse.profiler;

import com.pulse.config.Config;
import com.pulse.config.ConfigValue;

/**
 * Profiler 설정.
 */
@Config(modId = "Pulse_profiler", fileName = "profiler.json")
public class ProfilerConfig {

    /**
     * 프로파일러 활성화 여부
     */
    @ConfigValue(key = "enabled", comment = "Enable profiler")
    public static boolean enabled = true;

    /**
     * 통계 로그 출력 간격 (틱 단위)
     */
    @ConfigValue(key = "logInterval", comment = "Statistics log interval in ticks (20 ticks = 1 second)")
    public static int logInterval = 1200; // 1분

    /**
     * 디버그 오버레이 표시 여부
     */
    @ConfigValue(key = "showOverlay", comment = "Show debug overlay")
    public static boolean showOverlay = true;

    /**
     * 상세 로그 출력
     */
    @ConfigValue(key = "verbose", comment = "Verbose logging")
    public static boolean verbose = false;

    /**
     * 최소 로그 시간 (나노초)
     * 이 시간 이상 걸린 구간만 로그
     */
    @ConfigValue(key = "minLogTimeNanos", comment = "Minimum time to log (nanoseconds)")
    public static long minLogTimeNanos = 1_000_000; // 1ms
}
