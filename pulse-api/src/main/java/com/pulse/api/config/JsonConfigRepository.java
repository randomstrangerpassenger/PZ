package com.pulse.api.config;

import java.io.*;
import java.nio.file.*;
import java.util.Optional;
import java.util.function.Consumer;

/**
 * JSON 기반 설정 파일 I/O 유틸리티.
 * 
 * <h2>설계 원칙 (Philosophy.md 준수)</h2>
 * <ul>
 * <li>이 클래스는 순수 I/O + 버전 업그레이드 도구만 제공</li>
 * <li>게임 의미를 가진 기본값/임계값/결정 로직은 각 모듈이 정의</li>
 * <li>Pulse-api는 정책을 갖지 않음</li>
 * </ul>
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 모듈에서 사용
 * JsonConfigRepository<MyConfig> repo = new JsonConfigRepository<>(
 *         MyConfig.class,
 *         Paths.get(System.getProperty("user.home"), "Zomboid", "MyMod"),
 *         "config.json");
 * 
 * MyConfig config = repo.load().orElseGet(MyConfig::createDefaults);
 * repo.save(config);
 * }</pre>
 * 
 * @param <T> 설정 타입
 * @since Pulse 1.2.0
 */
public class JsonConfigRepository<T> {

    private final Class<T> configClass;
    private final Path configDir;
    private final String fileName;
    private final Object gson;

    // Gson reflection (pulse-api는 Gson 의존성 없음)
    private static final String GSON_CLASS = "com.google.gson.Gson";
    private static final String GSON_BUILDER_CLASS = "com.google.gson.GsonBuilder";

    /**
     * 저장소 생성.
     * 
     * @param configClass 설정 클래스 타입
     * @param configDir   설정 디렉토리 경로
     * @param fileName    설정 파일명 (예: "config.json")
     */
    public JsonConfigRepository(Class<T> configClass, Path configDir, String fileName) {
        this.configClass = configClass;
        this.configDir = configDir;
        this.fileName = fileName;
        this.gson = createGson();
    }

    /**
     * 설정 파일 경로 반환.
     */
    public Path getConfigPath() {
        return configDir.resolve(fileName);
    }

    /**
     * 설정 로드.
     * 
     * @return 로드된 설정 (파일이 없거나 오류 시 empty)
     */
    public Optional<T> load() {
        Path configPath = getConfigPath();

        if (!Files.exists(configPath)) {
            return Optional.empty();
        }

        try (Reader reader = new FileReader(configPath.toFile())) {
            T loaded = fromJson(reader, configClass);
            return Optional.ofNullable(loaded);
        } catch (Exception e) {
            System.err.println("[pulse-api] Failed to load config: " + e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * 설정 로드 (마이그레이션 콜백 지원).
     * 
     * @param migrator 버전 마이그레이션 콜백 (로드 후 호출)
     * @return 로드된 설정
     */
    public Optional<T> load(Consumer<T> migrator) {
        return load().map(config -> {
            if (migrator != null) {
                migrator.accept(config);
            }
            return config;
        });
    }

    /**
     * 설정 저장.
     * 
     * @param config 저장할 설정
     * @return 성공 여부
     */
    public boolean save(T config) {
        try {
            if (!Files.exists(configDir)) {
                Files.createDirectories(configDir);
            }

            Path configPath = getConfigPath();
            try (Writer writer = new FileWriter(configPath.toFile())) {
                toJson(config, writer);
            }
            return true;
        } catch (Exception e) {
            System.err.println("[pulse-api] Failed to save config: " + e.getMessage());
            return false;
        }
    }

    /**
     * 설정 파일 존재 여부.
     */
    public boolean exists() {
        return Files.exists(getConfigPath());
    }

    /**
     * 설정 파일 삭제.
     */
    public boolean delete() {
        try {
            return Files.deleteIfExists(getConfigPath());
        } catch (IOException e) {
            return false;
        }
    }

    // ========================================
    // Gson Reflection (pulse-api에 Gson 의존성X)
    // ========================================

    private Object createGson() {
        try {
            Class<?> builderClass = Class.forName(GSON_BUILDER_CLASS);
            Object builder = builderClass.getConstructor().newInstance();

            // setPrettyPrinting()
            builder = builderClass.getMethod("setPrettyPrinting").invoke(builder);

            // create()
            return builderClass.getMethod("create").invoke(builder);
        } catch (Exception e) {
            throw new IllegalStateException("Gson not available. Add Gson dependency.", e);
        }
    }

    @SuppressWarnings("unchecked")
    private T fromJson(Reader reader, Class<T> type) throws Exception {
        Class<?> gsonClass = Class.forName(GSON_CLASS);
        return (T) gsonClass.getMethod("fromJson", Reader.class, Class.class)
                .invoke(gson, reader, type);
    }

    private void toJson(T config, Writer writer) throws Exception {
        Class<?> gsonClass = Class.forName(GSON_CLASS);
        gsonClass.getMethod("toJson", Object.class, Appendable.class)
                .invoke(gson, config, writer);
    }
}
