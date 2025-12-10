package com.pulse.mod;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.spongepowered.asm.mixin.Mixins;

import java.io.*;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.*;
import java.util.*;
import java.util.jar.*;
import java.util.stream.Collectors;

/**
 * Pulse 모드 로더.
 * mods/ 폴더에서 모드 JAR를 발견하고 로드.
 */
public class ModLoader {

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
        this.modsDirectory = Paths.get(gameDir, "mods");

        System.out.println("[Pulse/ModLoader] Mods directory: " + modsDirectory.toAbsolutePath());
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 발견
    // ─────────────────────────────────────────────────────────────

    /**
     * mods/ 폴더에서 모든 모드 JAR 스캔
     */
    public void discoverMods() {
        if (discoveryComplete) {
            System.out.println("[Pulse/ModLoader] Discovery already complete");
            return;
        }

        System.out.println("[Pulse/ModLoader] ═══════════════════════════════════════");
        System.out.println("[Pulse/ModLoader] Discovering mods...");

        // mods 폴더 생성 (없으면)
        try {
            if (!Files.exists(modsDirectory)) {
                Files.createDirectories(modsDirectory);
                System.out.println("[Pulse/ModLoader] Created mods directory");
            }
        } catch (IOException e) {
            System.err.println("[Pulse/ModLoader] Failed to create mods directory: " + e.getMessage());
            return;
        }

        // JAR 파일 스캔
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(modsDirectory, "*.jar")) {
            for (Path jarPath : stream) {
                try {
                    discoverMod(jarPath);
                } catch (Exception e) {
                    System.err.println("[Pulse/ModLoader] Failed to load mod: " + jarPath.getFileName());
                    e.printStackTrace();
                }
            }
        } catch (IOException e) {
            System.err.println("[Pulse/ModLoader] Failed to scan mods directory: " + e.getMessage());
        }

        discoveryComplete = true;
        System.out.println("[Pulse/ModLoader] Discovered " + mods.size() + " mod(s)");
        System.out.println("[Pulse/ModLoader] ═══════════════════════════════════════");
    }

    /**
     * 단일 JAR 파일에서 모드 메타데이터 로드
     */
    private void discoverMod(Path jarPath) throws Exception {
        System.out.println("[Pulse/ModLoader] Scanning: " + jarPath.getFileName());

        try (JarFile jar = new JarFile(jarPath.toFile())) {
            // pulse.mod.json 찾기
            JarEntry metadataEntry = jar.getJarEntry("pulse.mod.json");

            if (metadataEntry == null) {
                System.out.println("[Pulse/ModLoader]   - No pulse.mod.json found, skipping");
                return;
            }

            // 메타데이터 파싱
            ModMetadata metadata;
            try (InputStream is = jar.getInputStream(metadataEntry);
                    InputStreamReader reader = new InputStreamReader(is)) {
                metadata = gson.fromJson(reader, ModMetadata.class);
            }

            // 유효성 검사
            if (metadata.getId() == null || metadata.getId().isEmpty()) {
                System.err.println("[Pulse/ModLoader]   - Invalid mod: missing 'id' field");
                return;
            }

            // 중복 체크
            if (mods.containsKey(metadata.getId())) {
                System.err.println("[Pulse/ModLoader]   - Duplicate mod ID: " + metadata.getId());
                return;
            }

            metadata.setSourceFile(jarPath.toAbsolutePath().toString());

            // 클래스로더 생성
            URL jarUrl = jarPath.toUri().toURL();
            URLClassLoader classLoader = new URLClassLoader(
                    new URL[] { jarUrl },
                    getClass().getClassLoader() // 부모 클래스로더
            );

            // 모드 컨테이너 생성
            ModContainer container = new ModContainer(metadata, classLoader);
            container.setState(ModContainer.ModState.METADATA_LOADED);

            mods.put(metadata.getId(), container);

            System.out.println("[Pulse/ModLoader]   ✓ " + metadata);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 의존성 해결 및 로드 순서 결정
    // ─────────────────────────────────────────────────────────────

    /**
     * 의존성 검사 및 로드 순서 결정 (토폴로지 정렬)
     */
    public void resolveDependencies() {
        System.out.println("[Pulse/ModLoader] Resolving dependencies...");

        List<String> errors = new ArrayList<>();

        // 각 모드의 의존성 검사
        for (ModContainer container : mods.values()) {
            ModMetadata metadata = container.getMetadata();

            for (ModMetadata.Dependency dep : metadata.getDependencies()) {
                // Pulse 자체는 항상 존재
                if ("Pulse".equals(dep.getId())) {
                    continue;
                }

                ModContainer depMod = mods.get(dep.getId());

                if (depMod == null) {
                    if (dep.isOptional()) {
                        System.out.println("[Pulse/ModLoader]   - " + metadata.getId() +
                                ": optional dependency '" + dep.getId() + "' not found");
                    } else {
                        errors.add(metadata.getId() + " requires " + dep.getId() + " " + dep.getVersion());
                    }
                } else {
                    // 버전 비교 로직
                    String actualVersion = depMod.getMetadata().getVersion();
                    String requiredVersion = dep.getVersion();

                    if (requiredVersion != null && !requiredVersion.isEmpty() && !"*".equals(requiredVersion)) {
                        if (VersionComparator.matches(actualVersion, requiredVersion)) {
                            System.out.println("[Pulse/ModLoader]   - " + metadata.getId() +
                                    " → " + dep.getId() + " v" + actualVersion + " ✓");
                        } else {
                            errors.add(metadata.getId() + " requires " + dep.getId() + " " +
                                    requiredVersion + " but found " + actualVersion);
                        }
                    } else {
                        System.out.println("[Pulse/ModLoader]   - " + metadata.getId() +
                                " → " + dep.getId() + " v" + actualVersion + " ✓");
                    }
                }
            }
        }

        // 충돌 검사
        for (ModContainer container : mods.values()) {
            ModMetadata metadata = container.getMetadata();
            for (String conflictId : metadata.getConflicts()) {
                if (mods.containsKey(conflictId)) {
                    errors.add(metadata.getId() + " conflicts with " + conflictId);
                    System.err.println("[Pulse/ModLoader] ✗ Conflict detected: " +
                            metadata.getId() + " and " + conflictId + " cannot be loaded together");
                }
            }
        }

        if (!errors.isEmpty()) {
            System.err.println("[Pulse/ModLoader] Dependency/Conflict errors:");
            for (String error : errors) {
                System.err.println("[Pulse/ModLoader]   ✗ " + error);
            }
        }

        // 토폴로지 정렬로 로드 순서 결정
        loadOrder.clear();
        Set<String> visited = new HashSet<>();
        Set<String> visiting = new HashSet<>();

        for (String modId : mods.keySet()) {
            if (!visited.contains(modId)) {
                topologicalSort(modId, visited, visiting, loadOrder);
            }
        }

        // 의존성 해결 완료 표시
        for (ModContainer container : loadOrder) {
            container.setState(ModContainer.ModState.DEPENDENCIES_RESOLVED);
        }

        System.out.println("[Pulse/ModLoader] Load order: " +
                loadOrder.stream().map(ModContainer::getId).collect(Collectors.joining(" → ")));
    }

    private void topologicalSort(String modId, Set<String> visited, Set<String> visiting,
            List<ModContainer> result) {
        if (visited.contains(modId))
            return;
        if (visiting.contains(modId)) {
            System.err.println("[Pulse/ModLoader] Circular dependency detected: " + modId);
            return;
        }

        visiting.add(modId);

        ModContainer container = mods.get(modId);
        if (container != null) {
            // 의존성 먼저 처리
            for (ModMetadata.Dependency dep : container.getMetadata().getDependencies()) {
                if (mods.containsKey(dep.getId())) {
                    topologicalSort(dep.getId(), visited, visiting, result);
                }
            }

            result.add(container);
        }

        visiting.remove(modId);
        visited.add(modId);
    }

    // ─────────────────────────────────────────────────────────────
    // Mixin 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 모드의 Mixin config 등록
     */
    public void registerMixins() {
        System.out.println("[Pulse/ModLoader] Registering mod mixins...");

        for (ModContainer container : loadOrder) {
            ModMetadata metadata = container.getMetadata();
            List<String> mixinConfigs = metadata.getMixins();

            if (mixinConfigs == null || mixinConfigs.isEmpty()) {
                continue;
            }

            for (String mixinConfig : mixinConfigs) {
                try {
                    System.out.println("[Pulse/Mixin] Registered mixin config " +
                            mixinConfig + " from " + metadata.getId());
                    Mixins.addConfiguration(mixinConfig);
                } catch (Exception e) {
                    System.err.println("[Pulse/Mixin] ✗ Failed to register " +
                            mixinConfig + " from " + metadata.getId() + ": " + e.getMessage());
                }
            }

            container.setState(ModContainer.ModState.MIXINS_APPLIED);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 모드 초기화 (엔트리포인트 호출)
     */
    public void initializeMods() {
        if (initialized) {
            System.out.println("[Pulse/ModLoader] Mods already initialized");
            return;
        }

        System.out.println("[Pulse/ModLoader] ═══════════════════════════════════════");
        System.out.println("[Pulse/ModLoader] Initializing mods...");

        int success = 0;
        int failed = 0;

        for (ModContainer container : loadOrder) {
            try {
                container.initialize();
                success++;
            } catch (Exception e) {
                failed++;
                System.err.println("[Pulse/ModLoader] ✗ " + container.getId() + " failed:");
                e.printStackTrace();
            }
        }

        initialized = true;

        System.out.println("[Pulse/ModLoader] ═══════════════════════════════════════");
        System.out.println("[Pulse/ModLoader] Initialization complete: " +
                success + " loaded, " + failed + " failed");
        System.out.println("[Pulse/ModLoader] ═══════════════════════════════════════");
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

    public Path getModsDirectory() {
        return modsDirectory;
    }
}
