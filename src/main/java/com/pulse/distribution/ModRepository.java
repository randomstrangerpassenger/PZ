package com.pulse.distribution;

import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;

/**
 * 모드 저장소 클라이언트.
 * 공식/커뮤니티 모드 저장소에서 모드 검색 및 다운로드.
 */
public class ModRepository {

    private static final ModRepository INSTANCE = new ModRepository();

    private final List<String> repositoryUrls = new ArrayList<>();
    private Path downloadDirectory;

    private ModRepository() {
        // 기본 저장소
        repositoryUrls.add("https://pulse-mods.example.com");
        downloadDirectory = Paths.get("mods");
    }

    public static ModRepository getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 저장소 관리
    // ─────────────────────────────────────────────────────────────

    /**
     * 저장소 URL 추가.
     */
    public static void addRepository(String url) {
        INSTANCE.repositoryUrls.add(url);
    }

    /**
     * 다운로드 디렉토리 설정.
     */
    public static void setDownloadDirectory(Path path) {
        INSTANCE.downloadDirectory = path;
    }

    // ─────────────────────────────────────────────────────────────
    // 검색
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 검색.
     */
    public static List<ModInfo> search(String query) {
        return INSTANCE.searchInternal(query);
    }

    private List<ModInfo> searchInternal(String query) {
        List<ModInfo> results = new ArrayList<>();

        for (String repoUrl : repositoryUrls) {
            try {
                URL url = new URL(repoUrl + "/api/search?q=" + URLEncoder.encode(query, "UTF-8"));
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setConnectTimeout(5000);

                if (conn.getResponseCode() == 200) {
                    // JSON 응답 파싱 (간략화)
                    try (BufferedReader reader = new BufferedReader(
                            new InputStreamReader(conn.getInputStream()))) {
                        String line;
                        while ((line = reader.readLine()) != null) {
                            // 간단한 파싱 로직
                            if (line.contains("\"id\"")) {
                                results.add(parseModInfo(line));
                            }
                        }
                    }
                }
            } catch (Exception e) {
                System.err.println("[Pulse/Repo] Search failed for " + repoUrl);
            }
        }

        return results;
    }

    private ModInfo parseModInfo(String json) {
        // 간단한 파싱 (실제로는 Gson 사용)
        String id = extractValue(json, "id");
        String name = extractValue(json, "name");
        String version = extractValue(json, "version");
        String author = extractValue(json, "author");
        String downloadUrl = extractValue(json, "downloadUrl");
        int downloads = extractIntValue(json, "downloads");

        return new ModInfo(id, name, version, author, downloadUrl, downloads);
    }

    private String extractValue(String json, String key) {
        int start = json.indexOf("\"" + key + "\":\"");
        if (start < 0)
            return "";
        start += key.length() + 4;
        int end = json.indexOf("\"", start);
        return end > start ? json.substring(start, end) : "";
    }

    private int extractIntValue(String json, String key) {
        try {
            int start = json.indexOf("\"" + key + "\":");
            if (start < 0)
                return 0;
            start += key.length() + 3;
            int end = start;
            while (end < json.length() && Character.isDigit(json.charAt(end)))
                end++;
            return Integer.parseInt(json.substring(start, end));
        } catch (Exception e) {
            return 0;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 다운로드
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 다운로드.
     */
    public static File download(ModInfo modInfo) throws IOException {
        return INSTANCE.downloadInternal(modInfo);
    }

    private File downloadInternal(ModInfo modInfo) throws IOException {
        if (modInfo.downloadUrl == null || modInfo.downloadUrl.isEmpty()) {
            throw new IOException("No download URL for mod: " + modInfo.id);
        }

        Files.createDirectories(downloadDirectory);
        Path targetPath = downloadDirectory.resolve(modInfo.id + "-" + modInfo.version + ".jar");

        System.out.println("[Pulse/Repo] Downloading: " + modInfo.name);

        URL url = new URL(modInfo.downloadUrl);
        try (InputStream in = url.openStream()) {
            Files.copy(in, targetPath, StandardCopyOption.REPLACE_EXISTING);
        }

        System.out.println("[Pulse/Repo] Downloaded: " + targetPath);
        return targetPath.toFile();
    }

    /**
     * 의존성 포함 다운로드.
     */
    public static List<File> downloadWithDependencies(ModInfo modInfo) throws IOException {
        List<File> downloaded = new ArrayList<>();
        downloaded.add(download(modInfo));

        // 의존성 다운로드는 추후 구현

        return downloaded;
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 정보
    // ─────────────────────────────────────────────────────────────

    public static class ModInfo {
        public final String id;
        public final String name;
        public final String version;
        public final String author;
        public final String downloadUrl;
        public final int downloads;

        public ModInfo(String id, String name, String version, String author,
                String downloadUrl, int downloads) {
            this.id = id;
            this.name = name;
            this.version = version;
            this.author = author;
            this.downloadUrl = downloadUrl;
            this.downloads = downloads;
        }

        @Override
        public String toString() {
            return String.format("%s (%s) v%s by %s - %d downloads",
                    name, id, version, author, downloads);
        }
    }
}
