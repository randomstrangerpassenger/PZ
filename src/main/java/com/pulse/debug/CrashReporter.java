package com.pulse.debug;

import com.pulse.mod.ModLoader;

import java.io.*;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * 크래시 리포터.
 * 예외 발생 시 상세 리포트 생성.
 */
public class CrashReporter {

    private static Path crashLogDirectory = Paths.get("crash-reports");

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

            // 예외 정보
            report.append("── EXCEPTION ─────────────────────────────────────────────\n");
            report.append(throwable.getClass().getName()).append(": ");
            report.append(throwable.getMessage()).append("\n\n");

            // 스택트레이스
            report.append("── STACK TRACE ───────────────────────────────────────────\n");
            StringWriter sw = new StringWriter();
            throwable.printStackTrace(new PrintWriter(sw));
            report.append(sw.toString()).append("\n");

            // 원인 체인
            Throwable cause = throwable.getCause();
            while (cause != null) {
                report.append("── CAUSED BY ─────────────────────────────────────────────\n");
                report.append(cause.getClass().getName()).append(": ");
                report.append(cause.getMessage()).append("\n");
                sw = new StringWriter();
                cause.printStackTrace(new PrintWriter(sw));
                report.append(sw.toString()).append("\n");
                cause = cause.getCause();
            }

            // 로드된 모드 목록
            report.append("── LOADED MODS ───────────────────────────────────────────\n");
            ModLoader loader = ModLoader.getInstance();
            for (String modId : loader.getLoadedModIds()) {
                var mod = loader.getMod(modId);
                var meta = mod.getMetadata();
                report.append("  - ").append(meta.getName())
                        .append(" (").append(modId).append(") v").append(meta.getVersion())
                        .append(" [").append(mod.getState()).append("]\n");
            }
            report.append("\n");

            // 시스템 정보
            report.append("── SYSTEM INFO ───────────────────────────────────────────\n");
            report.append("Java: ").append(System.getProperty("java.version")).append("\n");
            report.append("Java Vendor: ").append(System.getProperty("java.vendor")).append("\n");
            report.append("OS: ").append(System.getProperty("os.name")).append(" ");
            report.append(System.getProperty("os.version")).append("\n");
            report.append("Memory: ");
            Runtime rt = Runtime.getRuntime();
            long usedMB = (rt.totalMemory() - rt.freeMemory()) / 1024 / 1024;
            long maxMB = rt.maxMemory() / 1024 / 1024;
            report.append(usedMB).append("MB / ").append(maxMB).append("MB\n\n");

            // 푸터
            report.append("═══════════════════════════════════════════════════════════\n");
            report.append("Please report this crash to the mod developers.\n");
            report.append("Include this file with your bug report.\n");
            report.append("═══════════════════════════════════════════════════════════\n");

            // 파일 저장
            Files.writeString(reportPath, report.toString());
            System.err.println("[Pulse/Crash] Report saved to: " + reportPath.toAbsolutePath());

            return reportPath.toFile();

        } catch (IOException e) {
            System.err.println("[Pulse/Crash] Failed to write crash report: " + e.getMessage());
            return null;
        }
    }

    /**
     * 예외 핸들러 설치.
     */
    public static void installHandler() {
        Thread.setDefaultUncaughtExceptionHandler((thread, throwable) -> {
            System.err.println("[Pulse/Crash] Uncaught exception in thread: " + thread.getName());
            report(throwable, "Uncaught exception in " + thread.getName());
        });
        System.out.println("[Pulse/Crash] Exception handler installed");
    }

    /**
     * 크래시 로그 디렉토리 설정.
     */
    public static void setLogDirectory(Path path) {
        crashLogDirectory = path;
    }
}
