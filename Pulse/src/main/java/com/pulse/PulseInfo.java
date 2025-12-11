package com.pulse;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.jar.Attributes;
import java.util.jar.Manifest;

/**
 * Pulse 버전 및 빌드 정보 유틸리티.
 * 
 * 빌드 시 생성된 파일(pulse-version.txt, MANIFEST.MF)에서 버전 정보를 읽습니다.
 * 
 * @since Pulse 1.2
 */
public final class PulseInfo {

    private static final String DEFAULT_VERSION = "0.8.0";
    private static final String VERSION_FILE = "pulse-version.txt";

    private static volatile String cachedVersion;

    private PulseInfo() {
    }

    /**
     * Pulse 버전 문자열 반환
     * 
     * @return 버전 문자열 (예: "0.8.0")
     */
    public static String getVersion() {
        if (cachedVersion == null) {
            cachedVersion = loadVersion();
        }
        return cachedVersion;
    }

    /**
     * 버전 정보 로드 (여러 소스 시도)
     */
    private static String loadVersion() {
        // 1. pulse-version.txt 파일에서 읽기 시도 (Gradle generateVersionFile 태스크)
        String version = loadFromVersionFile();
        if (version != null) {
            return version;
        }

        // 2. JAR MANIFEST.MF에서 Implementation-Version 읽기 시도
        version = loadFromManifest();
        if (version != null) {
            return version;
        }

        // 3. 시스템 속성에서 읽기 시도 (테스트 또는 개발 환경)
        version = System.getProperty("pulse.version");
        if (version != null && !version.isEmpty()) {
            return version;
        }

        // 4. 기본값 반환
        return DEFAULT_VERSION;
    }

    /**
     * pulse-version.txt 파일에서 버전 읽기
     */
    private static String loadFromVersionFile() {
        try {
            // 클래스로더에서 리소스로 시도
            InputStream is = PulseInfo.class.getClassLoader().getResourceAsStream(VERSION_FILE);
            if (is != null) {
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
                    String version = reader.readLine();
                    if (version != null && !version.trim().isEmpty()) {
                        return version.trim();
                    }
                }
            }

            // 현재 디렉토리에서 시도
            Path versionPath = Paths.get(VERSION_FILE);
            if (Files.exists(versionPath)) {
                String version = Files.readString(versionPath, StandardCharsets.UTF_8).trim();
                if (!version.isEmpty()) {
                    return version;
                }
            }

            // JAR 파일 옆에서 시도
            URL jarLocation = PulseInfo.class.getProtectionDomain().getCodeSource().getLocation();
            if (jarLocation != null) {
                Path jarDir = Paths.get(jarLocation.toURI()).getParent();
                if (jarDir != null) {
                    Path sideFile = jarDir.resolve(VERSION_FILE);
                    if (Files.exists(sideFile)) {
                        String version = Files.readString(sideFile, StandardCharsets.UTF_8).trim();
                        if (!version.isEmpty()) {
                            return version;
                        }
                    }
                }
            }
        } catch (Exception e) {
            // 무시 - 다음 방법 시도
        }
        return null;
    }

    /**
     * JAR MANIFEST.MF에서 버전 읽기
     */
    private static String loadFromManifest() {
        try {
            InputStream is = PulseInfo.class.getClassLoader().getResourceAsStream("META-INF/MANIFEST.MF");
            if (is != null) {
                try (is) {
                    Manifest manifest = new Manifest(is);
                    Attributes attrs = manifest.getMainAttributes();
                    String version = attrs.getValue("Implementation-Version");
                    if (version != null && !version.isEmpty() && !version.contains("SNAPSHOT")) {
                        return version.replace("-SNAPSHOT", "");
                    }
                    // SNAPSHOT 버전도 허용
                    if (version != null && !version.isEmpty()) {
                        return version.replace("-SNAPSHOT", "");
                    }
                }
            }
        } catch (Exception e) {
            // 무시 - 다음 방법 시도
        }
        return null;
    }

    /**
     * 전체 버전 문자열 (SNAPSHOT 포함)
     */
    public static String getFullVersion() {
        String version = loadFromManifest();
        if (version != null) {
            return version;
        }
        return getVersion();
    }

    /**
     * 빌드 정보 요약
     */
    public static String getBuildInfo() {
        return String.format("Pulse v%s (Java %s)", getVersion(), System.getProperty("java.version"));
    }
}
