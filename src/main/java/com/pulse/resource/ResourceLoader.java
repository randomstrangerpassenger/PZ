package com.pulse.resource;

import com.pulse.registry.Identifier;

import java.io.*;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

/**
 * 리소스 로더.
 * 모드 JAR 및 리소스 팩에서 리소스를 로드.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 텍스처 로드
 * InputStream tex = ResourceLoader.getResource(
 *         Identifier.of("mymod", "textures/item/cool_item.png"));
 * 
 * // JSON 데이터 로드
 * String json = ResourceLoader.loadString(
 *         Identifier.of("mymod", "data/items.json"));
 * 
 * // 번역 파일 로드
 * Properties lang = ResourceLoader.loadProperties(
 *         Identifier.of("mymod", "lang/ko_kr.properties"));
 * </pre>
 */
public class ResourceLoader {

    private static final ResourceLoader INSTANCE = new ResourceLoader();

    // 등록된 리소스 소스
    private final List<ResourceSource> sources = new ArrayList<>();

    // 리소스 캐시
    private final Map<Identifier, byte[]> cache = new ConcurrentHashMap<>();
    private boolean cacheEnabled = true;

    private ResourceLoader() {
    }

    public static ResourceLoader getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 리소스 소스 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * JAR 파일을 리소스 소스로 추가
     */
    public static void addJarSource(Path jarPath) {
        INSTANCE.registerJarSource(jarPath);
    }

    /**
     * 디렉토리를 리소스 소스로 추가
     */
    public static void addDirectorySource(Path directory) {
        INSTANCE.registerDirectorySource(directory);
    }

    /**
     * 클래스로더를 리소스 소스로 추가
     */
    public static void addClassLoaderSource(ClassLoader classLoader, String namespace) {
        INSTANCE.registerClassLoaderSource(classLoader, namespace);
    }

    private void registerJarSource(Path jarPath) {
        sources.add(new JarResourceSource(jarPath));
        System.out.println("[Pulse/Resource] Added JAR source: " + jarPath.getFileName());
    }

    private void registerDirectorySource(Path directory) {
        sources.add(new DirectoryResourceSource(directory));
        System.out.println("[Pulse/Resource] Added directory source: " + directory);
    }

    private void registerClassLoaderSource(ClassLoader classLoader, String namespace) {
        sources.add(new ClassLoaderResourceSource(classLoader, namespace));
        System.out.println("[Pulse/Resource] Added classloader source for: " + namespace);
    }

    // ─────────────────────────────────────────────────────────────
    // 리소스 로드
    // ─────────────────────────────────────────────────────────────

    /**
     * 리소스를 InputStream으로 가져오기
     */
    public static InputStream getResource(Identifier id) {
        return INSTANCE.loadResource(id);
    }

    /**
     * 리소스를 문자열로 로드
     */
    public static String loadString(Identifier id) {
        byte[] data = INSTANCE.loadBytesInternal(id);
        if (data == null)
            return null;
        return new String(data, StandardCharsets.UTF_8);
    }

    /**
     * 리소스를 바이트 배열로 로드
     */
    public static byte[] loadBytes(Identifier id) {
        return INSTANCE.loadBytesInternal(id);
    }

    /**
     * Properties 파일 로드
     */
    public static Properties loadProperties(Identifier id) {
        try (InputStream is = getResource(id)) {
            if (is == null)
                return null;
            Properties props = new Properties();
            props.load(is);
            return props;
        } catch (IOException e) {
            System.err.println("[Pulse/Resource] Failed to load properties: " + id);
            return null;
        }
    }

    /**
     * 리소스 존재 여부 확인
     */
    public static boolean exists(Identifier id) {
        return INSTANCE.resourceExists(id);
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 구현
    // ─────────────────────────────────────────────────────────────

    private InputStream loadResource(Identifier id) {
        byte[] data = loadBytesInternal(id);
        if (data == null)
            return null;
        return new ByteArrayInputStream(data);
    }

    private byte[] loadBytesInternal(Identifier id) {
        // 캐시 확인
        if (cacheEnabled && cache.containsKey(id)) {
            return cache.get(id);
        }

        // 소스에서 로드
        for (ResourceSource source : sources) {
            byte[] data = source.load(id);
            if (data != null) {
                if (cacheEnabled) {
                    cache.put(id, data);
                }
                return data;
            }
        }

        return null;
    }

    private boolean resourceExists(Identifier id) {
        if (cacheEnabled && cache.containsKey(id)) {
            return true;
        }
        for (ResourceSource source : sources) {
            if (source.exists(id)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 캐시 비우기
     */
    public static void clearCache() {
        INSTANCE.cache.clear();
    }

    public static void setCacheEnabled(boolean enabled) {
        INSTANCE.cacheEnabled = enabled;
    }

    // ─────────────────────────────────────────────────────────────
    // 리소스 소스 인터페이스 및 구현
    // ─────────────────────────────────────────────────────────────

    interface ResourceSource {
        byte[] load(Identifier id);

        boolean exists(Identifier id);
    }

    static class JarResourceSource implements ResourceSource {
        private final Path jarPath;

        JarResourceSource(Path jarPath) {
            this.jarPath = jarPath;
        }

        @Override
        public byte[] load(Identifier id) {
            String path = "assets/" + id.getNamespace() + "/" + id.getPath();
            try (JarFile jar = new JarFile(jarPath.toFile())) {
                JarEntry entry = jar.getJarEntry(path);
                if (entry != null) {
                    try (InputStream is = jar.getInputStream(entry)) {
                        return is.readAllBytes();
                    }
                }
            } catch (IOException e) {
                // Ignore
            }
            return null;
        }

        @Override
        public boolean exists(Identifier id) {
            String path = "assets/" + id.getNamespace() + "/" + id.getPath();
            try (JarFile jar = new JarFile(jarPath.toFile())) {
                return jar.getJarEntry(path) != null;
            } catch (IOException e) {
                return false;
            }
        }
    }

    static class DirectoryResourceSource implements ResourceSource {
        private final Path baseDir;

        DirectoryResourceSource(Path baseDir) {
            this.baseDir = baseDir;
        }

        @Override
        public byte[] load(Identifier id) {
            Path file = baseDir.resolve("assets")
                    .resolve(id.getNamespace())
                    .resolve(id.getPath());
            if (Files.exists(file)) {
                try {
                    return Files.readAllBytes(file);
                } catch (IOException e) {
                    return null;
                }
            }
            return null;
        }

        @Override
        public boolean exists(Identifier id) {
            Path file = baseDir.resolve("assets")
                    .resolve(id.getNamespace())
                    .resolve(id.getPath());
            return Files.exists(file);
        }
    }

    static class ClassLoaderResourceSource implements ResourceSource {
        private final ClassLoader classLoader;
        private final String namespace;

        ClassLoaderResourceSource(ClassLoader classLoader, String namespace) {
            this.classLoader = classLoader;
            this.namespace = namespace;
        }

        @Override
        public byte[] load(Identifier id) {
            if (!id.getNamespace().equals(namespace)) {
                return null;
            }
            String path = "assets/" + id.getNamespace() + "/" + id.getPath();
            try (InputStream is = classLoader.getResourceAsStream(path)) {
                if (is != null) {
                    return is.readAllBytes();
                }
            } catch (IOException e) {
                // Ignore
            }
            return null;
        }

        @Override
        public boolean exists(Identifier id) {
            if (!id.getNamespace().equals(namespace)) {
                return false;
            }
            String path = "assets/" + id.getNamespace() + "/" + id.getPath();
            URL url = classLoader.getResource(path);
            return url != null;
        }
    }
}
