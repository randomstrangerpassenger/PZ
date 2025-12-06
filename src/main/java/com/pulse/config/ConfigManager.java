package com.pulse.config;

import com.google.gson.*;

import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Pulse 설정 관리자.
 * 
 * 모드별 설정 파일 자동 생성, 로드, 저장을 담당.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 설정 클래스 정의
 * {@literal @}Config(modId = "mymod")
 * public class MyModConfig {
 *     {@literal @}ConfigValue(comment = "Enable feature X")
 *     public static boolean enableFeatureX = true;
 *     
 *     {@literal @}ConfigValue(min = 0, max = 100)
 *     public static int someValue = 50;
 * }
 * 
 * // 등록 및 로드
 * ConfigManager.register(MyModConfig.class);
 * 
 * // 사용
 * if (MyModConfig.enableFeatureX) { ... }
 * 
 * // 저장
 * ConfigManager.save(MyModConfig.class);
 * </pre>
 */
public class ConfigManager {

    private static final ConfigManager INSTANCE = new ConfigManager();

    // 등록된 설정 스펙
    private final Map<Class<?>, ConfigSpec> specs = new ConcurrentHashMap<>();

    // 설정 디렉토리
    private Path configDirectory;

    // JSON 파서
    private final Gson gson = new GsonBuilder()
            .setPrettyPrinting()
            .serializeNulls()
            .create();

    private ConfigManager() {
        // 기본 설정 디렉토리: 게임 폴더/config
        String gameDir = System.getProperty("user.dir");
        this.configDirectory = Paths.get(gameDir, "config");
    }

    public static ConfigManager getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 정적 편의 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 설정 클래스 등록 및 로드
     */
    public static void register(Class<?> configClass) {
        INSTANCE.registerConfig(configClass);
    }

    /**
     * 설정 저장
     */
    public static void save(Class<?> configClass) {
        INSTANCE.saveConfig(configClass);
    }

    /**
     * 설정 리로드
     */
    public static void reload(Class<?> configClass) {
        INSTANCE.loadConfig(configClass);
    }

    /**
     * 모든 설정 저장
     */
    public static void saveAll() {
        INSTANCE.saveAllConfigs();
    }

    /**
     * 모든 설정 리로드
     */
    public static void reloadAll() {
        INSTANCE.loadAllConfigs();
    }

    // ─────────────────────────────────────────────────────────────
    // 인스턴스 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 설정 클래스 등록
     */
    public void registerConfig(Class<?> configClass) {
        if (!configClass.isAnnotationPresent(Config.class)) {
            throw new IllegalArgumentException("Class must have @Config annotation: " + configClass.getName());
        }

        ConfigSpec spec = new ConfigSpec(configClass);
        specs.put(configClass, spec);

        System.out.println("[Pulse/Config] Registered config: " + spec.getModId());

        // 파일에서 로드 시도
        loadConfig(configClass);
    }

    /**
     * 설정 로드
     */
    public void loadConfig(Class<?> configClass) {
        ConfigSpec spec = specs.get(configClass);
        if (spec == null) {
            System.err.println("[Pulse/Config] Config not registered: " + configClass.getName());
            return;
        }

        Path configFile = getConfigPath(spec);

        if (!Files.exists(configFile)) {
            // 파일이 없으면 기본값으로 생성
            saveConfig(configClass);
            return;
        }

        try {
            String json = Files.readString(configFile, StandardCharsets.UTF_8);
            JsonObject root = JsonParser.parseString(json).getAsJsonObject();

            for (ConfigSpec.ConfigEntry entry : spec.getEntries()) {
                if (root.has(entry.getKey())) {
                    JsonElement element = root.get(entry.getKey());
                    Object value = parseValue(element, entry.getType());
                    if (value != null) {
                        entry.setValue(value);
                    }
                }
            }

            System.out.println("[Pulse/Config] Loaded: " + configFile.getFileName());

        } catch (Exception e) {
            System.err.println("[Pulse/Config] Failed to load " + configFile + ": " + e.getMessage());
            // 로드 실패 시 기본값 유지
        }
    }

    /**
     * 설정 저장
     */
    public void saveConfig(Class<?> configClass) {
        ConfigSpec spec = specs.get(configClass);
        if (spec == null) {
            System.err.println("[Pulse/Config] Config not registered: " + configClass.getName());
            return;
        }

        Path configFile = getConfigPath(spec);

        try {
            // 디렉토리 생성
            Files.createDirectories(configFile.getParent());

            // JSON 객체 구성
            JsonObject root = new JsonObject();

            // 메타데이터 주석
            root.addProperty("_comment", "Configuration for " + spec.getModId());

            for (ConfigSpec.ConfigEntry entry : spec.getEntries()) {
                Object value = entry.getValue();
                JsonElement element = serializeValue(value);

                // 주석이 있으면 _key_comment 형태로 추가
                if (!entry.getComment().isEmpty()) {
                    root.addProperty("_" + entry.getKey() + "_comment", entry.getComment());
                }

                root.add(entry.getKey(), element);
            }

            // 파일에 쓰기
            String json = gson.toJson(root);
            Files.writeString(configFile, json, StandardCharsets.UTF_8);

            System.out.println("[Pulse/Config] Saved: " + configFile.getFileName());

        } catch (Exception e) {
            System.err.println("[Pulse/Config] Failed to save " + configFile + ": " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 모든 설정 저장
     */
    public void saveAllConfigs() {
        for (Class<?> configClass : specs.keySet()) {
            saveConfig(configClass);
        }
    }

    /**
     * 모든 설정 로드
     */
    public void loadAllConfigs() {
        for (Class<?> configClass : specs.keySet()) {
            loadConfig(configClass);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 직렬화/역직렬화 헬퍼
    // ─────────────────────────────────────────────────────────────

    private Path getConfigPath(ConfigSpec spec) {
        Path base = configDirectory;
        if (!spec.getCategory().isEmpty()) {
            base = base.resolve(spec.getCategory());
        }
        return base.resolve(spec.getFileName());
    }

    private Object parseValue(JsonElement element, Class<?> type) {
        if (element.isJsonNull())
            return null;

        try {
            if (type == boolean.class || type == Boolean.class) {
                return element.getAsBoolean();
            }
            if (type == int.class || type == Integer.class) {
                return element.getAsInt();
            }
            if (type == long.class || type == Long.class) {
                return element.getAsLong();
            }
            if (type == float.class || type == Float.class) {
                return element.getAsFloat();
            }
            if (type == double.class || type == Double.class) {
                return element.getAsDouble();
            }
            if (type == String.class) {
                return element.getAsString();
            }
            if (type.isArray()) {
                return gson.fromJson(element, type);
            }
            if (List.class.isAssignableFrom(type)) {
                return gson.fromJson(element, type);
            }

            // 기타 객체 타입
            return gson.fromJson(element, type);

        } catch (Exception e) {
            System.err.println("[Pulse/Config] Failed to parse value: " + e.getMessage());
            return null;
        }
    }

    private JsonElement serializeValue(Object value) {
        if (value == null)
            return JsonNull.INSTANCE;
        return gson.toJsonTree(value);
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    public void setConfigDirectory(Path directory) {
        this.configDirectory = directory;
    }

    public Path getConfigDirectory() {
        return configDirectory;
    }

    public ConfigSpec getSpec(Class<?> configClass) {
        return specs.get(configClass);
    }

    public Collection<ConfigSpec> getAllSpecs() {
        return Collections.unmodifiableCollection(specs.values());
    }
}
