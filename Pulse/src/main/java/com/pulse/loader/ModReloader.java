package com.pulse.loader;

import com.pulse.api.log.PulseLogger;
import com.pulse.event.EventBus;
import com.pulse.hook.PulseHookRegistry;

import java.io.File;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * 안전한 모드 핫 리로드 관리자.
 * 
 * 코드 전체 재시작 없이 모드의 Lua/Core 부분만 재적용합니다.
 * Fuse/Nerve 파라미터 실험 시 유용합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 특정 모드 리로드
 * ModReloader.reload("my-mod");
 * 
 * // 리로드 리스너 등록
 * ModReloader.addListener((modId, success) -> {
 *     System.out.println(modId + " reloaded: " + success);
 * });
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class ModReloader {

    private static final String LOG = PulseLogger.PULSE;

    // 등록된 모드 정보
    private static final Map<String, ModInfo> registeredMods = new LinkedHashMap<>();

    // 리로드 리스너
    private static final List<ReloadListener> listeners = new CopyOnWriteArrayList<>();

    // 리로드 히스토리
    private static final List<ReloadRecord> history = new ArrayList<>();
    private static final int MAX_HISTORY = 50;

    private ModReloader() {
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 리로드 가능한 모드 등록
     * 
     * @param modId   모드 ID
     * @param modPath 모드 루트 경로
     */
    public static void registerMod(String modId, File modPath) {
        registerMod(modId, modPath, null);
    }

    /**
     * 리로드 가능한 모드 등록 (콜백 포함)
     * 
     * @param modId    모드 ID
     * @param modPath  모드 루트 경로
     * @param callback 리로드 시 호출될 콜백
     */
    public static void registerMod(String modId, File modPath, ReloadCallback callback) {
        if (modId == null || modId.isEmpty()) {
            throw new IllegalArgumentException("Mod ID cannot be null or empty");
        }

        ModInfo info = new ModInfo(modId, modPath, callback);
        registeredMods.put(modId, info);
        PulseLogger.info(LOG, "[ModReloader] Registered mod: {}", modId);
    }

    /**
     * 모드 등록 해제
     */
    public static void unregisterMod(String modId) {
        if (registeredMods.remove(modId) != null) {
            PulseLogger.info(LOG, "[ModReloader] Unregistered mod: {}", modId);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 리로드 실행
    // ─────────────────────────────────────────────────────────────

    /**
     * 특정 모드 리로드
     * 
     * @param modId 리로드할 모드 ID
     * @return 성공 여부
     */
    public static boolean reload(String modId) {
        ModInfo info = registeredMods.get(modId);
        if (info == null) {
            PulseLogger.error(LOG, "[ModReloader] Unknown mod: {}", modId);
            return false;
        }

        long startTime = System.currentTimeMillis();
        boolean success = false;
        String errorMessage = null;

        try {
            PulseLogger.info(LOG, "[ModReloader] Starting reload: {}", modId);

            // 1. 모드의 이벤트 리스너 해제
            int unsubscribed = EventBus.unsubscribeAll(modId);
            PulseLogger.info(LOG, "[ModReloader]   Unsubscribed {} event listeners", unsubscribed);

            // 2. 모드의 Hook 콜백 해제
            int unregisteredHooks = PulseHookRegistry.unregisterAll(modId);
            PulseLogger.info(LOG, "[ModReloader]   Unregistered {} hook callbacks", unregisteredHooks);

            // 3. Lua 파일 리로드 (게임 API 호출)
            success = reloadLuaFiles(info);

            // 4. 모드 콜백 호출
            if (info.callback != null) {
                info.callback.onReload();
            }

            PulseLogger.info(LOG, "[ModReloader] Reload {}: {}", success ? "successful" : "failed", modId);

        } catch (Exception e) {
            errorMessage = e.getMessage();
            PulseLogger.error(LOG, "[ModReloader] Reload failed: {} - {}", modId, e.getMessage(), e);
        }

        long duration = System.currentTimeMillis() - startTime;

        // 히스토리 기록
        addToHistory(new ReloadRecord(modId, success, duration, errorMessage));

        // 리스너 알림
        for (ReloadListener listener : listeners) {
            try {
                listener.onModReloaded(modId, success);
            } catch (Exception e) {
                // 리스너 예외 무시
            }
        }

        return success;
    }

    /**
     * 모든 등록된 모드 리로드
     * 
     * @return 리로드된 모드 수
     */
    public static int reloadAll() {
        int reloaded = 0;
        for (String modId : new ArrayList<>(registeredMods.keySet())) {
            if (reload(modId)) {
                reloaded++;
            }
        }
        return reloaded;
    }

    /**
     * Lua 파일 리로드 (내부 구현)
     * 
     * PZ의 Lua API를 reflection으로 호출합니다:
     * 1. LuaManager.LoadDirRecursive 시도
     * 2. LuaManager.LoadDir 폴백
     * 3. 게임 런타임 외부면 시뮬레이션
     */
    private static boolean reloadLuaFiles(ModInfo info) {
        if (info.modPath == null) {
            PulseLogger.info(LOG, "[ModReloader] No mod path specified, skipping Lua reload");
            return true;
        }

        String luaPath = info.modPath.getAbsolutePath() + "/media/lua";
        java.io.File luaDir = new java.io.File(luaPath);

        if (!luaDir.exists() || !luaDir.isDirectory()) {
            PulseLogger.info(LOG, "[ModReloader] Lua directory not found: {}", luaPath);
            return true; // 디렉토리 없으면 성공으로 처리 (Java-only 모드 가능)
        }

        try {
            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");

            // 1. LoadDirRecursive 시도 (PZ B41+)
            try {
                java.lang.reflect.Method loadDirRecursive = luaManagerClass.getMethod(
                        "LoadDirRecursive", String.class, boolean.class, boolean.class);
                loadDirRecursive.invoke(null, luaPath, true, false);
                PulseLogger.info(LOG, "[ModReloader] Reloaded Lua via LoadDirRecursive: {}", luaPath);
                return true;
            } catch (NoSuchMethodException e) {
                // LoadDirRecursive 없음, 다음 시도
            }

            // 2. LoadDir 시도 (older API)
            try {
                java.lang.reflect.Method loadDir = luaManagerClass.getMethod("LoadDir", String.class);
                loadDir.invoke(null, luaPath);
                PulseLogger.info(LOG, "[ModReloader] Reloaded Lua via LoadDir: {}", luaPath);
                return true;
            } catch (NoSuchMethodException e) {
                // LoadDir 없음, 실패
            }

            // 3. reloadLuaFiles 시도 (alternative API)
            try {
                java.lang.reflect.Method reloadMethod = luaManagerClass.getMethod("reloadLuaFiles", String.class);
                reloadMethod.invoke(null, luaPath);
                PulseLogger.info(LOG, "[ModReloader] Reloaded Lua via reloadLuaFiles: {}", luaPath);
                return true;
            } catch (NoSuchMethodException e) {
                PulseLogger.error(LOG, "[ModReloader] No suitable Lua reload method found in LuaManager");
                return false;
            }

        } catch (ClassNotFoundException e) {
            // 게임 런타임 외부에서 실행 중
            PulseLogger.info(LOG, "[ModReloader] Not in game runtime, simulating Lua reload: {}", luaPath);
            return true;
        } catch (Exception e) {
            PulseLogger.error(LOG, "[ModReloader] Lua reload failed: {}", e.getMessage());
            if (e.getCause() != null) {
                PulseLogger.error(LOG, "[ModReloader]   Cause: {}", e.getCause().getMessage());
            }
            return false;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 리스너
    // ─────────────────────────────────────────────────────────────

    /**
     * 리로드 리스너 추가
     */
    public static void addListener(ReloadListener listener) {
        if (listener != null) {
            listeners.add(listener);
        }
    }

    /**
     * 리로드 리스너 제거
     */
    public static void removeListener(ReloadListener listener) {
        listeners.remove(listener);
    }

    // ─────────────────────────────────────────────────────────────
    // 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * 등록된 모드 목록
     */
    public static Set<String> getRegisteredMods() {
        return new LinkedHashSet<>(registeredMods.keySet());
    }

    /**
     * 모드 등록 여부
     */
    public static boolean isRegistered(String modId) {
        return registeredMods.containsKey(modId);
    }

    /**
     * 리로드 히스토리
     */
    public static List<ReloadRecord> getHistory() {
        synchronized (history) {
            return new ArrayList<>(history);
        }
    }

    private static void addToHistory(ReloadRecord record) {
        synchronized (history) {
            if (history.size() >= MAX_HISTORY) {
                history.remove(0);
            }
            history.add(record);
        }
    }

    /**
     * 상태 요약
     */
    public static String getStatusSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append("ModReloader Status:\n");
        sb.append("  Registered Mods: ").append(registeredMods.size()).append("\n");
        for (String modId : registeredMods.keySet()) {
            sb.append("    - ").append(modId).append("\n");
        }
        sb.append("  Reload History: ").append(history.size()).append(" records\n");
        return sb.toString();
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 정보
     */
    private static class ModInfo {
        @SuppressWarnings("unused") // Used for identification in future modId-based operations
        final String modId;
        final File modPath;
        final ReloadCallback callback;

        ModInfo(String modId, File modPath, ReloadCallback callback) {
            this.modId = modId;
            this.modPath = modPath;
            this.callback = callback;
        }
    }

    /**
     * 리로드 콜백
     */
    @FunctionalInterface
    public interface ReloadCallback {
        void onReload();
    }

    /**
     * 리로드 리스너
     */
    @FunctionalInterface
    public interface ReloadListener {
        void onModReloaded(String modId, boolean success);
    }

    /**
     * 리로드 기록
     */
    public static class ReloadRecord {
        private final String modId;
        private final boolean success;
        private final long durationMs;
        private final String errorMessage;
        private final long timestamp;

        public ReloadRecord(String modId, boolean success, long durationMs, String errorMessage) {
            this.modId = modId;
            this.success = success;
            this.durationMs = durationMs;
            this.errorMessage = errorMessage;
            this.timestamp = System.currentTimeMillis();
        }

        public String getModId() {
            return modId;
        }

        public boolean isSuccess() {
            return success;
        }

        public long getDurationMs() {
            return durationMs;
        }

        public String getErrorMessage() {
            return errorMessage;
        }

        public long getTimestamp() {
            return timestamp;
        }

        @Override
        public String toString() {
            return String.format("%s: %s (%dms)%s",
                    modId, success ? "OK" : "FAILED", durationMs,
                    errorMessage != null ? " - " + errorMessage : "");
        }
    }
}
