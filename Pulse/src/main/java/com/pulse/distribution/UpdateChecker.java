package com.pulse.distribution;

import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModLoader;
import com.pulse.mod.ModContainer;

import java.io.*;
import java.net.*;
import java.util.*;

/**
 * 모드 업데이트 확인.
 * 원격 저장소에서 모드의 새 버전 확인.
 */
public class UpdateChecker {

    private static final UpdateChecker INSTANCE = new UpdateChecker();
    private static final String LOG = PulseLogger.PULSE;

    private String updateServerUrl = "https://pulse-mods.example.com/api";
    private final Map<String, UpdateInfo> updateCache = new HashMap<>();
    private long lastCheckTime = 0;
    private static final long CHECK_INTERVAL = 3600000; // 1시간

    private UpdateChecker() {
    }

    public static UpdateChecker getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 업데이트 확인
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 모드의 업데이트 확인.
     */
    public static List<UpdateInfo> checkAll() {
        return INSTANCE.checkAllInternal();
    }

    private List<UpdateInfo> checkAllInternal() {
        List<UpdateInfo> updates = new ArrayList<>();

        if (System.currentTimeMillis() - lastCheckTime < CHECK_INTERVAL && !updateCache.isEmpty()) {
            return new ArrayList<>(updateCache.values());
        }

        for (String modId : ModLoader.getInstance().getLoadedModIds()) {
            try {
                UpdateInfo info = checkMod(modId);
                if (info != null && info.hasUpdate()) {
                    updates.add(info);
                    updateCache.put(modId, info);
                }
            } catch (Exception e) {
                PulseLogger.error(LOG, "[Update] Failed to check: {}", modId);
            }
        }

        lastCheckTime = System.currentTimeMillis();
        PulseLogger.info(LOG, "[Update] Found {} updates available", updates.size());
        return updates;
    }

    /**
     * 특정 모드의 업데이트 확인.
     */
    public static UpdateInfo check(String modId) {
        return INSTANCE.checkMod(modId);
    }

    private UpdateInfo checkMod(String modId) {
        ModContainer mod = ModLoader.getInstance().getMod(modId);
        if (mod == null)
            return null;

        String currentVersion = mod.getMetadata().getVersion();

        try {
            // API 호출
            URL url = new URL(updateServerUrl + "/check?mod=" + modId + "&version=" + currentVersion);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);

            if (conn.getResponseCode() == 200) {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(conn.getInputStream()))) {

                    // 간단한 JSON 파싱 (예: {"latestVersion":"1.2.0","downloadUrl":"..."})
                    String line = reader.readLine();
                    if (line != null && line.contains("latestVersion")) {
                        String latestVersion = extractJsonValue(line, "latestVersion");
                        String downloadUrl = extractJsonValue(line, "downloadUrl");
                        String changelog = extractJsonValue(line, "changelog");

                        return new UpdateInfo(modId, currentVersion, latestVersion, downloadUrl, changelog);
                    }
                }
            }
        } catch (Exception e) {
            // 네트워크 오류 무시
        }

        return new UpdateInfo(modId, currentVersion, currentVersion, null, null);
    }

    private String extractJsonValue(String json, String key) {
        int start = json.indexOf("\"" + key + "\":\"");
        if (start < 0)
            return null;
        start += key.length() + 4;
        int end = json.indexOf("\"", start);
        if (end < 0)
            return null;
        return json.substring(start, end);
    }

    /**
     * 업데이트 서버 URL 설정.
     */
    public static void setServerUrl(String url) {
        INSTANCE.updateServerUrl = url;
    }

    // ─────────────────────────────────────────────────────────────
    // 업데이트 정보
    // ─────────────────────────────────────────────────────────────

    public static class UpdateInfo {
        private final String modId;
        private final String currentVersion;
        private final String latestVersion;
        private final String downloadUrl;
        private final String changelog;

        public UpdateInfo(String modId, String currentVersion, String latestVersion,
                String downloadUrl, String changelog) {
            this.modId = modId;
            this.currentVersion = currentVersion;
            this.latestVersion = latestVersion;
            this.downloadUrl = downloadUrl;
            this.changelog = changelog;
        }

        public boolean hasUpdate() {
            return !currentVersion.equals(latestVersion);
        }

        public String getModId() {
            return modId;
        }

        public String getCurrentVersion() {
            return currentVersion;
        }

        public String getLatestVersion() {
            return latestVersion;
        }

        public String getDownloadUrl() {
            return downloadUrl;
        }

        public String getChangelog() {
            return changelog;
        }

        @Override
        public String toString() {
            return modId + ": " + currentVersion + " -> " + latestVersion;
        }
    }
}
