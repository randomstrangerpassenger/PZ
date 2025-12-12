package com.pulse.mod;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.PulseConstants;
import com.pulse.mod.dependency.DependencyResolver;
import com.pulse.mod.discovery.ModDiscovery;
import com.pulse.mod.mixin.MixinRegistrar;

import java.nio.file.*;
import java.util.*;

/**
 * Pulse 모드 로더.
 * mods/ 폴더에서 모드 JAR를 발견하고 로드.
 */
public class ModLoader {

    private static final String LOG = PulseLogger.PULSE;

    private static ModLoader instance;

    private final Path modsDirectory;
    private final Map<String, ModContainer> mods = new LinkedHashMap<>();
    private final List<ModContainer> loadOrder = new ArrayList<>();
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    private boolean discoveryComplete = false;
    private boolean initialized = false;

    // ─────────────────────────────────────────────────────────────
    // 싱글톤
    // ─────────────────────────────────────────────────────────────

    public static ModLoader getInstance() {
        if (instance == null) {
            instance = new ModLoader();
        }
        return instance;
    }

    private ModLoader() {
        // 게임 디렉토리에서 mods 폴더 찾기
        String gameDir = System.getProperty("user.dir");
        this.modsDirectory = Paths.get(gameDir, PulseConstants.MODS_DIR_NAME);

        PulseLogger.info(LOG, "Mods directory: {}", modsDirectory.toAbsolutePath());
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 발견
    // ─────────────────────────────────────────────────────────────

    /**
     * mods/ 폴더에서 모든 모드 JAR 스캔
     */
    public void discoverMods() {
        if (discoveryComplete) {
            PulseLogger.info(LOG, "Discovery already complete");
            return;
        }

        ModDiscovery discovery = new ModDiscovery(modsDirectory, gson);
        Map<String, ModContainer> discoveredMods = discovery.discoverMods();
        mods.putAll(discoveredMods);

        discoveryComplete = true;
    }

    // ─────────────────────────────────────────────────────────────
    // 의존성 해결 및 로드 순서 결정
    // ─────────────────────────────────────────────────────────────

    /**
     * 의존성 검사 및 로드 순서 결정 (토폴로지 정렬)
     */
    public void resolveDependencies() {
        DependencyResolver resolver = new DependencyResolver(mods);
        List<ModContainer> resolvedOrder = resolver.resolve();

        loadOrder.clear();
        loadOrder.addAll(resolvedOrder);
    }

    // ─────────────────────────────────────────────────────────────
    // Mixin 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 모드의 Mixin config 등록
     */
    public void registerMixins() {
        new MixinRegistrar().registerMixins(loadOrder);
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 모드 초기화 (엔트리포인트 호출)
     */
    public void initializeMods() {
        if (initialized) {
            PulseLogger.info(LOG, "Mods already initialized");
            return;
        }

        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "Initializing mods...");

        int success = 0;
        int failed = 0;

        for (ModContainer container : loadOrder) {
            try {
                container.initialize();
                success++;
            } catch (Exception e) {
                failed++;
                PulseLogger.error(LOG, "✗ {} failed:", container.getId());
                e.printStackTrace();
            }
        }

        initialized = true;

        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "Initialization complete: {} loaded, {} failed", success, failed);
        PulseLogger.info(LOG, "═══════════════════════════════════════");
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    public ModContainer getMod(String id) {
        return mods.get(id);
    }

    public Collection<ModContainer> getAllMods() {
        return Collections.unmodifiableCollection(mods.values());
    }

    public List<ModContainer> getLoadOrder() {
        return Collections.unmodifiableList(loadOrder);
    }

    public int getModCount() {
        return mods.size();
    }

    public Set<String> getLoadedModIds() {
        return Collections.unmodifiableSet(mods.keySet());
    }

    public boolean isModLoaded(String id) {
        ModContainer container = mods.get(id);
        return container != null && container.isLoaded();
    }

    /**
     * 모든 모드 언로드 (게임 종료 시)
     */
    public void unloadAll() {
        PulseLogger.info(LOG, "Unloading all mods...");

        // 역순으로 언로드 (의존성 고려)
        for (int i = loadOrder.size() - 1; i >= 0; i--) {
            ModContainer container = loadOrder.get(i);
            try {
                PulseMod mod = container.getModInstance(PulseMod.class);
                if (mod != null) {
                    mod.onUnload();
                }
                container.setState(ModContainer.ModState.UNLOADED);
                PulseLogger.debug(LOG, "Unloaded: {}", container.getId());
            } catch (Exception e) {
                PulseLogger.error(LOG, "Failed to unload mod: {}", container.getId());
            }
        }

        loadOrder.clear();
        mods.clear();
        initialized = false;
        discoveryComplete = false;

        PulseLogger.info(LOG, "All mods unloaded");
    }

    public Path getModsDirectory() {
        return modsDirectory;
    }
}
