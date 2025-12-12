package com.pulse.mod;

import com.pulse.api.log.PulseLogger;
import com.pulse.config.ConfigManager;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.ModReloadEvent;

import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 모드 핫 리로드 매니저.
 * 런타임에 모드를 비활성화/재활성화할 수 있는 기능 제공.
 * 
 * 제한사항:
 * - Mixin이 적용된 모드는 완전한 언로드가 불가능
 * - 리로드는 설정 및 이벤트 리스너만 갱신
 * - 바이트코드 변경은 게임 재시작 필요
 * 
 * 사용 예:
 * 
 * <pre>
 * // 모드 비활성화
 * ModReloadManager.disable("mymod");
 * 
 * // 모드 재활성화
 * ModReloadManager.enable("mymod");
 * 
 * // 설정만 리로드
 * ModReloadManager.reloadConfig("mymod");
 * 
 * // 전체 소프트 리로드 (Mixin 제외)
 * ModReloadManager.softReload("mymod");
 * </pre>
 */
public class ModReloadManager {

    private static final String LOG = PulseLogger.PULSE;
    private static final ModReloadManager INSTANCE = new ModReloadManager();

    // 비활성화된 모드 목록
    private final Set<String> disabledMods = ConcurrentHashMap.newKeySet();

    private ModReloadManager() {
    }

    public static ModReloadManager getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 활성화/비활성화
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 비활성화.
     * 이벤트 리스너 해제, 스케줄러 태스크 취소.
     * 
     * @param modId 비활성화할 모드 ID
     * @return 성공 여부
     */
    public static boolean disable(String modId) {
        return INSTANCE.disableMod(modId);
    }

    /**
     * 모드 활성화.
     * 비활성화된 모드를 다시 활성화.
     * 
     * @param modId 활성화할 모드 ID
     * @return 성공 여부
     */
    public static boolean enable(String modId) {
        return INSTANCE.enableMod(modId);
    }

    /**
     * 모드가 활성 상태인지 확인.
     */
    public static boolean isEnabled(String modId) {
        return !INSTANCE.disabledMods.contains(modId);
    }

    /**
     * 비활성화된 모드 목록.
     */
    public static Set<String> getDisabledMods() {
        return Collections.unmodifiableSet(INSTANCE.disabledMods);
    }

    private boolean disableMod(String modId) {
        ModLoader loader = ModLoader.getInstance();
        ModContainer container = loader.getMod(modId);

        if (container == null) {
            PulseLogger.error(LOG, "Mod not found: {}", modId);
            return false;
        }

        if (disabledMods.contains(modId)) {
            PulseLogger.debug(LOG, "Mod already disabled: {}", modId);
            return true;
        }

        try {
            PulseLogger.info(LOG, "Disabling mod: {}", modId);

            // 1. 모드의 onUnload 호출
            PulseMod instance = container.getModInstance(PulseMod.class);
            if (instance != null) {
                try {
                    instance.onUnload();
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Error in onUnload: {}", e.getMessage());
                }
            }

            // 2. 설정 저장
            ConfigManager.saveAll();

            // 3. 비활성화 상태로 표시
            disabledMods.add(modId);
            container.setState(ModContainer.ModState.DISABLED);

            // 4. 이벤트 발행
            EventBus.post(new ModReloadEvent(modId, ModReloadEvent.Action.DISABLED));

            PulseLogger.info(LOG, "Mod disabled: {}", modId);
            return true;

        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to disable mod: {}", modId);
            e.printStackTrace();
            return false;
        }
    }

    private boolean enableMod(String modId) {
        ModLoader loader = ModLoader.getInstance();
        ModContainer container = loader.getMod(modId);

        if (container == null) {
            PulseLogger.error(LOG, "Mod not found: {}", modId);
            return false;
        }

        if (!disabledMods.contains(modId)) {
            PulseLogger.debug(LOG, "Mod already enabled: {}", modId);
            return true;
        }

        try {
            PulseLogger.info(LOG, "Enabling mod: {}", modId);

            // 1. 활성화 상태로 표시
            disabledMods.remove(modId);
            container.setState(ModContainer.ModState.LOADED);

            // 2. 설정 리로드
            reloadConfigInternal(modId);

            // 3. 모드의 onInitialize 다시 호출
            PulseMod instance = container.getModInstance(PulseMod.class);
            if (instance != null) {
                try {
                    instance.onInitialize();
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Error in onInitialize: {}", e.getMessage());
                }
            }

            // 4. 이벤트 발행
            EventBus.post(new ModReloadEvent(modId, ModReloadEvent.Action.ENABLED));

            PulseLogger.info(LOG, "Mod enabled: {}", modId);
            return true;

        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to enable mod: {}", modId);
            e.printStackTrace();
            return false;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 리로드
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 설정만 리로드.
     * 파일에서 설정을 다시 읽어옴.
     */
    public static boolean reloadConfig(String modId) {
        return INSTANCE.reloadConfigInternal(modId);
    }

    /**
     * 모드 소프트 리로드.
     * 설정 리로드 + 이벤트 리스너 재등록.
     * Mixin 변경은 반영되지 않음.
     */
    public static boolean softReload(String modId) {
        return INSTANCE.softReloadMod(modId);
    }

    /**
     * 모든 모드 설정 리로드.
     */
    public static void reloadAllConfigs() {
        ConfigManager.reloadAll();
        PulseLogger.info(LOG, "All configs reloaded");
    }

    private boolean reloadConfigInternal(String modId) {
        try {
            // modId에 해당하는 설정 클래스를 알 수 없으므로 전체 리로드
            ConfigManager.reloadAll();
            PulseLogger.debug(LOG, "Config reloaded for: {}", modId);
            return true;
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to reload config: {}", modId);
            e.printStackTrace();
            return false;
        }
    }

    private boolean softReloadMod(String modId) {
        ModLoader loader = ModLoader.getInstance();
        ModContainer container = loader.getMod(modId);

        if (container == null) {
            PulseLogger.error(LOG, "Mod not found: {}", modId);
            return false;
        }

        try {
            PulseLogger.info(LOG, "Soft reloading mod: {}", modId);

            PulseMod instance = container.getModInstance(PulseMod.class);

            // 1. onUnload 호출 (정리)
            if (instance != null) {
                try {
                    instance.onUnload();
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Error in onUnload: {}", e.getMessage());
                }
            }

            // 2. 설정 리로드
            reloadConfigInternal(modId);

            // 3. onInitialize 호출 (재초기화)
            if (instance != null) {
                try {
                    instance.onInitialize();
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Error in onInitialize: {}", e.getMessage());
                }
            }

            // 4. 이벤트 발행
            EventBus.post(new ModReloadEvent(modId, ModReloadEvent.Action.RELOADED));

            PulseLogger.info(LOG, "Mod soft reloaded: {}", modId);
            return true;

        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to soft reload mod: {}", modId);
            e.printStackTrace();
            return false;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 핫 스왑 (실험적)
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 JAR 파일 핫 스왑 (실험적).
     * 새 JAR 파일을 로드하여 모드 클래스를 교체 시도.
     * 
     * ⚠️ 제한 사항:
     * - JVM은 이미 로드된 클래스를 교체할 수 없음
     * - 새 클래스만 새 로더에서 로드됨
     * - 완전한 핫 스왑은 게임 재시작 필요
     */
    public static boolean hotSwap(String modId, File newJarFile) {
        return INSTANCE.hotSwapMod(modId, newJarFile);
    }

    private boolean hotSwapMod(String modId, File newJarFile) {
        if (!newJarFile.exists() || !newJarFile.getName().endsWith(".jar")) {
            PulseLogger.error(LOG, "Invalid JAR file: {}", newJarFile);
            return false;
        }

        try {
            PulseLogger.info(LOG, "Hot swapping mod: {}", modId);
            PulseLogger.info(LOG, "New JAR: {}", newJarFile.getAbsolutePath());

            // 1. 현재 모드 비활성화
            disable(modId);

            // 2. 새 클래스 로더로 JAR 로드
            URL jarUrl = newJarFile.toURI().toURL();
            @SuppressWarnings("resource")
            URLClassLoader newLoader = new URLClassLoader(
                    new URL[] { jarUrl },
                    getClass().getClassLoader());

            // 3. 새 entrypoint 로드 시도
            ModLoader loader = ModLoader.getInstance();
            ModContainer container = loader.getMod(modId);

            if (container != null) {
                String entrypoint = container.getMetadata().getEntrypoint();
                if (entrypoint != null && !entrypoint.isEmpty()) {
                    try {
                        Class<?> newModClass = newLoader.loadClass(entrypoint);
                        Object newInstance = newModClass.getDeclaredConstructor().newInstance();

                        if (newInstance instanceof PulseMod) {
                            // 새 인스턴스로 교체 (리플렉션)
                            java.lang.reflect.Field instanceField = ModContainer.class.getDeclaredField("modInstance");
                            instanceField.setAccessible(true);
                            instanceField.set(container, newInstance);

                            PulseLogger.info(LOG, "Loaded new mod instance");
                        }
                    } catch (ClassNotFoundException e) {
                        PulseLogger.debug(LOG, "Entrypoint not found in new JAR, using existing");
                    }
                }
            }

            // 4. 다시 활성화
            enable(modId);

            // 5. 이벤트 발행
            EventBus.post(new ModReloadEvent(modId, ModReloadEvent.Action.HOT_SWAPPED));

            PulseLogger.info(LOG, "Hot swap complete (partial - JVM limitations apply)");
            return true;

        } catch (Exception e) {
            PulseLogger.error(LOG, "Hot swap failed: {}", modId);
            e.printStackTrace();
            return false;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 비활성화 여부를 확인하고 실행을 스킵할지 결정.
     * 이벤트 핸들러 등에서 사용.
     */
    public static boolean shouldSkip(String modId) {
        return INSTANCE.disabledMods.contains(modId);
    }

    /**
     * 모든 모드 상태 출력.
     */
    public static void printStatus() {
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "       MOD RELOAD MANAGER STATUS       ");
        PulseLogger.info(LOG, "═══════════════════════════════════════");

        ModLoader loader = ModLoader.getInstance();
        for (String modId : loader.getLoadedModIds()) {
            ModContainer mod = loader.getMod(modId);
            String status = INSTANCE.disabledMods.contains(mod.getId()) ? "DISABLED" : "ENABLED";
            PulseLogger.info(LOG, "  {} v{} [{}]", mod.getId(), mod.getMetadata().getVersion(), status);
        }

        PulseLogger.info(LOG, "═══════════════════════════════════════");
    }
}
