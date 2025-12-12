package com.pulse.debug;

import com.pulse.mixin.MixinDiagnostics;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModLoader;

import com.pulse.api.log.PulseLogger;

import java.io.*;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * 크래시 리포터.
 * 예외 발생 시 상세 리포트 생성.
 * 
 * 기능:
 * - 예외 정보 및 스택트레이스
 * - 원인 모드 자동 추적
 * - Mixin 적용 현황
 * - 최근 로그 라인
 * - 시스템/게임 정보
 */
public class CrashReporter {

    private static final String LOG = PulseLogger.PULSE;
    private static Path crashLogDirectory = Paths.get("crash-reports");

    // ═══════════════════════════════════════════════════════════════
    // 이벤트 타입 상수
    // ═══════════════════════════════════════════════════════════════

    /** Mixin 실패 이벤트 */
    public static final String EVENT_MIXIN_FAILURE = "MIXIN_FAILURE";

    /** Lua 예산 초과 이벤트 */
    public static final String EVENT_LUA_BUDGET_EXCEEDED = "LUA_BUDGET_EXCEEDED";

    /** SafeGameAccess fallback 이벤트 */
    public static final String EVENT_SAFE_ACCESS_FALLBACK = "SAFE_ACCESS_FALLBACK";

    /** Fail-soft 정책 트리거 이벤트 */
    public static final String EVENT_FAILSOFT_TRIGGERED = "FAILSOFT_TRIGGERED";

    /** 클래스 미발견 이벤트 */
    public static final String EVENT_CLASS_NOT_FOUND = "CLASS_NOT_FOUND";

    // ═══════════════════════════════════════════════════════════════
    // 로그/이벤트 버퍼
    // ═══════════════════════════════════════════════════════════════

    // 최근 로그 버퍼
    private static final int MAX_LOG_LINES = 100;
    private static final LinkedList<String> recentLogs = new LinkedList<>();
    private static final Object logLock = new Object();

    // 최근 이벤트 버퍼
    private static final int MAX_EVENTS = 50;
    private static final LinkedList<EventRecord> recentEvents = new LinkedList<>();
    private static final Object eventLock = new Object();

    /**
     * 로그 라인 추가 (순환 버퍼).
     */
    public static void addLogLine(String line) {
        synchronized (logLock) {
            if (recentLogs.size() >= MAX_LOG_LINES) {
                recentLogs.removeFirst();
            }
            recentLogs.add(line);
        }
    }

    /**
     * 크래시 리포트 생성.
     */
    public static File report(Throwable throwable, String context) {
        String timestamp = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss").format(new Date());
        String filename = "crash-" + timestamp + ".txt";

        try {
            Files.createDirectories(crashLogDirectory);
            Path reportPath = crashLogDirectory.resolve(filename);

            StringBuilder report = new StringBuilder();

            // 헤더
            report.append("═══════════════════════════════════════════════════════════\n");
            report.append("               PULSE MOD LOADER CRASH REPORT               \n");
            report.append("═══════════════════════════════════════════════════════════\n\n");

            // 시간
            report.append("Time: ").append(new Date()).append("\n");
            report.append("Context: ").append(context != null ? context : "Unknown").append("\n\n");

            // 의심 모드 분석
            String suspectedMod = analyzeSuspectedMod(throwable);
            if (suspectedMod != null) {
                report.append("⚠️ SUSPECTED MOD: ").append(suspectedMod).append("\n\n");
            }

            // 예외 정보
            report.append("── EXCEPTION ─────────────────────────────────────────────\n");
            report.append(throwable.getClass().getName()).append(": ");
            report.append(throwable.getMessage()).append("\n\n");

            // 스택트레이스 (모드 표시 포함)
            report.append("── STACK TRACE ───────────────────────────────────────────\n");
            appendAnnotatedStackTrace(report, throwable);
            report.append("\n");

            // 원인 체인
            Throwable cause = throwable.getCause();
            while (cause != null) {
                report.append("── CAUSED BY ─────────────────────────────────────────────\n");
                report.append(cause.getClass().getName()).append(": ");
                report.append(cause.getMessage()).append("\n");
                appendAnnotatedStackTrace(report, cause);
                report.append("\n");
                cause = cause.getCause();
            }

            // 로드된 모드 목록
            report.append("── LOADED MODS ───────────────────────────────────────────\n");
            appendLoadedMods(report);
            report.append("\n");

            // Mixin 적용 현황
            report.append("── APPLIED MIXINS ────────────────────────────────────────\n");
            appendMixinInfo(report);
            report.append("\n");

            // 최근 로그
            report.append("── RECENT LOG LINES ──────────────────────────────────────\n");
            appendRecentLogs(report);
            report.append("\n");

            // 시스템 정보
            report.append("── SYSTEM INFO ───────────────────────────────────────────\n");
            appendSystemInfo(report);
            report.append("\n");

            // 푸터
            report.append("═══════════════════════════════════════════════════════════\n");
            report.append("Please report this crash to the mod developers.\n");
            if (suspectedMod != null) {
                report.append("The crash appears to be related to: ").append(suspectedMod).append("\n");
            }
            report.append("Include this file with your bug report.\n");
            report.append("═══════════════════════════════════════════════════════════\n");

            // 파일 저장
            Files.writeString(reportPath, report.toString());
            PulseLogger.error(LOG, "[Crash] Report saved to: {}", reportPath.toAbsolutePath());

            return reportPath.toFile();

        } catch (IOException e) {
            PulseLogger.error(LOG, "[Crash] Failed to write crash report: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 스택트레이스에서 의심 모드 분석.
     */
    private static String analyzeSuspectedMod(Throwable throwable) {
        Set<String> suspectedMods = new LinkedHashSet<>();

        for (StackTraceElement element : throwable.getStackTrace()) {
            String modName = findModByClassName(element.getClassName());
            if (modName != null) {
                suspectedMods.add(modName);
            }
        }

        // 원인 체인도 분석
        Throwable cause = throwable.getCause();
        while (cause != null) {
            for (StackTraceElement element : cause.getStackTrace()) {
                String modName = findModByClassName(element.getClassName());
                if (modName != null) {
                    suspectedMods.add(modName);
                }
            }
            cause = cause.getCause();
        }

        if (suspectedMods.isEmpty()) {
            return null;
        }

        return String.join(", ", suspectedMods);
    }

    /**
     * 클래스 이름으로 모드 찾기.
     */
    private static String findModByClassName(String className) {
        ModLoader loader = ModLoader.getInstance();

        for (String modId : loader.getLoadedModIds()) {
            ModContainer mod = loader.getMod(modId);
            if (mod == null)
                continue;

            // 모드 엔트리포인트 확인
            String entrypoint = mod.getMetadata().getEntrypoint();
            if (entrypoint != null && entrypoint.contains(".")) {
                String packageName = entrypoint.substring(0, entrypoint.lastIndexOf('.'));
                if (className.startsWith(packageName)) {
                    return mod.getMetadata().getName() + " (" + modId + ")";
                }
            }

            // 모드 ID 기반 패키지 추정
            if (className.toLowerCase().contains(modId.toLowerCase())) {
                return mod.getMetadata().getName() + " (" + modId + ")";
            }
        }

        // Pulse 내부 패키지 확인
        if (className.startsWith("com.pulse.")) {
            return "Pulse (core)";
        }

        return null;
    }

    /**
     * 모드 표시가 포함된 스택트레이스 출력.
     */
    private static void appendAnnotatedStackTrace(StringBuilder report, Throwable throwable) {
        for (StackTraceElement element : throwable.getStackTrace()) {
            report.append("    at ").append(element.toString());

            String modName = findModByClassName(element.getClassName());
            if (modName != null) {
                report.append(" [").append(modName).append("]");
            }

            report.append("\n");
        }
    }

    /**
     * 로드된 모드 목록 출력.
     */
    private static void appendLoadedMods(StringBuilder report) {
        ModLoader loader = ModLoader.getInstance();
        List<String> modIds = new ArrayList<>(loader.getLoadedModIds());

        if (modIds.isEmpty()) {
            report.append("  (No mods loaded)\n");
            return;
        }

        for (String modId : modIds) {
            ModContainer mod = loader.getMod(modId);
            if (mod != null) {
                var meta = mod.getMetadata();
                report.append("  - ").append(meta.getName())
                        .append(" (").append(modId).append(") v").append(meta.getVersion())
                        .append(" [").append(mod.getState()).append("]\n");
            }
        }
    }

    /**
     * Mixin 적용 현황 출력.
     */
    private static void appendMixinInfo(StringBuilder report) {
        try {
            // MixinDiagnostics에서 정보 가져오기
            Map<String, List<String>> mixinInfo = MixinDiagnostics.getTransformationDetails();

            if (mixinInfo.isEmpty()) {
                report.append("  (No Mixin transformations recorded)\n");
                return;
            }

            for (var entry : mixinInfo.entrySet()) {
                report.append("  ").append(entry.getKey()).append(":\n");
                for (String mixin : entry.getValue()) {
                    report.append("    - ").append(mixin).append("\n");
                }
            }
        } catch (Exception e) {
            report.append("  (Unable to retrieve Mixin info: ").append(e.getMessage()).append(")\n");
        }
    }

    /**
     * 최근 로그 라인 출력.
     */
    private static void appendRecentLogs(StringBuilder report) {
        synchronized (logLock) {
            if (recentLogs.isEmpty()) {
                report.append("  (No recent logs captured)\n");
                return;
            }

            int count = Math.min(recentLogs.size(), 50); // 최대 50줄
            int start = recentLogs.size() - count;

            for (int i = start; i < recentLogs.size(); i++) {
                report.append("  ").append(recentLogs.get(i)).append("\n");
            }
        }
    }

    /**
     * 시스템 정보 출력.
     */
    private static void appendSystemInfo(StringBuilder report) {
        // Java 정보
        report.append("Java Version: ").append(System.getProperty("java.version")).append("\n");
        report.append("Java Vendor: ").append(System.getProperty("java.vendor")).append("\n");
        report.append("Java VM: ").append(System.getProperty("java.vm.name")).append(" ")
                .append(System.getProperty("java.vm.version")).append("\n");

        // OS 정보
        report.append("OS: ").append(System.getProperty("os.name")).append(" ")
                .append(System.getProperty("os.version")).append(" (")
                .append(System.getProperty("os.arch")).append(")\n");

        // 메모리 정보
        Runtime rt = Runtime.getRuntime();
        long usedMB = (rt.totalMemory() - rt.freeMemory()) / 1024 / 1024;
        long totalMB = rt.totalMemory() / 1024 / 1024;
        long maxMB = rt.maxMemory() / 1024 / 1024;
        report.append("Memory: ").append(usedMB).append("MB used / ")
                .append(totalMB).append("MB allocated / ")
                .append(maxMB).append("MB max\n");

        // CPU 정보
        report.append("CPU Cores: ").append(rt.availableProcessors()).append("\n");

        // Pulse 버전
        report.append("Pulse Version: 1.0.0-SNAPSHOT\n");

        // 작업 디렉토리
        report.append("Working Directory: ").append(System.getProperty("user.dir")).append("\n");
    }

    /**
     * 예외 핸들러 설치.
     */
    public static void installHandler() {
        Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
            PulseLogger.error(LOG, "[Crash] Uncaught exception in thread: {}", thread.getName());
            report(throwable, "Uncaught exception in " + thread.getName());
        });
        PulseLogger.info(LOG, "[Crash] Exception handler installed");
    }

    /**
     * 크래시 로그 디렉토리 설정.
     */
    public static void setLogDirectory(Path path) {
        crashLogDirectory = path;
    }

    /**
     * 크래시 로그 디렉토리 가져오기.
     */
    public static Path getLogDirectory() {
        return crashLogDirectory;
    }

    // ═══════════════════════════════════════════════════════════════
    // 구조화된 이벤트 기록 (Fail-soft 연동)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 구조화된 이벤트 기록.
     * Fail-soft 정책에서 호출됨.
     * 
     * @param eventType 이벤트 타입 (EVENT_* 상수)
     * @param source    이벤트 발생 소스
     * @param message   이벤트 메시지
     */
    public static void recordEvent(String eventType, String source, String message) {
        EventRecord record = new EventRecord(eventType, source, message);

        synchronized (eventLock) {
            if (recentEvents.size() >= MAX_EVENTS) {
                recentEvents.removeFirst();
            }
            recentEvents.add(record);
        }

        // 콘솔에도 출력
        PulseLogger.info(LOG, "[Event] {} | {} | {}", eventType, source, message);
    }

    /**
     * 최근 이벤트 목록 반환.
     *
     * @return 최근 이벤트 리스트 (복사본)
     */
    public static List<EventRecord> getRecentEvents() {
        synchronized (eventLock) {
            return new ArrayList<>(recentEvents);
        }
    }

    /**
     * 특정 타입의 이벤트만 반환.
     *
     * @param eventType 이벤트 타입
     * @return 해당 타입 이벤트 리스트
     */
    public static List<EventRecord> getEventsByType(String eventType) {
        synchronized (eventLock) {
            return recentEvents.stream()
                    .filter(e -> e.eventType.equals(eventType))
                    .collect(java.util.stream.Collectors.toList());
        }
    }

    /**
     * 이벤트 버퍼 초기화.
     */
    public static void clearEvents() {
        synchronized (eventLock) {
            recentEvents.clear();
        }
    }

    /**
     * 이벤트 개수.
     *
     * @return 기록된 이벤트 수
     */
    public static int getEventCount() {
        synchronized (eventLock) {
            return recentEvents.size();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 이벤트 레코드 클래스
    // ═══════════════════════════════════════════════════════════════

    /**
     * 구조화된 이벤트 레코드.
     */
    public static class EventRecord {
        public final String eventType;
        public final String source;
        public final String message;
        public final long timestamp;

        public EventRecord(String eventType, String source, String message) {
            this.eventType = eventType;
            this.source = source;
            this.message = message;
            this.timestamp = System.currentTimeMillis();
        }

        @Override
        public String toString() {
            return String.format("[%tF %tT] %s | %s | %s",
                    timestamp, timestamp, eventType, source, message);
        }
    }
}
