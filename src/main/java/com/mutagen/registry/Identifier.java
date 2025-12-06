package com.mutagen.registry;

import java.util.Objects;

/**
 * 리소스 식별자.
 * 네임스페이스:경로 형식 (예: "mymod:my_item")
 * Minecraft의 ResourceLocation과 동일한 개념.
 */
public final class Identifier {

    public static final String DEFAULT_NAMESPACE = "mutagen";
    public static final char SEPARATOR = ':';

    private final String namespace;
    private final String path;

    private Identifier(String namespace, String path) {
        this.namespace = namespace;
        this.path = path;
    }

    /**
     * 식별자 생성
     */
    public static Identifier of(String namespace, String path) {
        validateNamespace(namespace);
        validatePath(path);
        return new Identifier(namespace, path);
    }

    /**
     * 문자열에서 파싱
     * "namespace:path" 또는 "path" (기본 네임스페이스 사용)
     */
    public static Identifier parse(String id) {
        if (id == null || id.isEmpty()) {
            throw new IllegalArgumentException("Identifier cannot be null or empty");
        }

        int colonIndex = id.indexOf(SEPARATOR);
        if (colonIndex < 0) {
            // 네임스페이스 없음 - 기본 사용
            return of(DEFAULT_NAMESPACE, id);
        }

        String namespace = id.substring(0, colonIndex);
        String path = id.substring(colonIndex + 1);
        return of(namespace, path);
    }

    /**
     * 모드 ID로 네임스페이스 지정하여 생성
     */
    public static Identifier mod(String modId, String path) {
        return of(modId, path);
    }

    // ─────────────────────────────────────────────────────────────
    // 유효성 검사
    // ─────────────────────────────────────────────────────────────

    private static void validateNamespace(String namespace) {
        if (namespace == null || namespace.isEmpty()) {
            throw new IllegalArgumentException("Namespace cannot be null or empty");
        }
        if (!isValidNamespace(namespace)) {
            throw new IllegalArgumentException("Invalid namespace: " + namespace);
        }
    }

    private static void validatePath(String path) {
        if (path == null || path.isEmpty()) {
            throw new IllegalArgumentException("Path cannot be null or empty");
        }
        if (!isValidPath(path)) {
            throw new IllegalArgumentException("Invalid path: " + path);
        }
    }

    /**
     * 네임스페이스 유효성 (a-z, 0-9, _, -)
     */
    public static boolean isValidNamespace(String namespace) {
        for (char c : namespace.toCharArray()) {
            if (!(c >= 'a' && c <= 'z') &&
                    !(c >= '0' && c <= '9') &&
                    c != '_' && c != '-') {
                return false;
            }
        }
        return true;
    }

    /**
     * 경로 유효성 (a-z, 0-9, _, -, ., /)
     */
    public static boolean isValidPath(String path) {
        for (char c : path.toCharArray()) {
            if (!(c >= 'a' && c <= 'z') &&
                    !(c >= '0' && c <= '9') &&
                    c != '_' && c != '-' && c != '.' && c != '/') {
                return false;
            }
        }
        return true;
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public String getNamespace() {
        return namespace;
    }

    public String getPath() {
        return path;
    }

    /**
     * 전체 문자열 (namespace:path)
     */
    @Override
    public String toString() {
        return namespace + SEPARATOR + path;
    }

    /**
     * 파일 경로 형식 (namespace/path)
     */
    public String toFilePath() {
        return namespace + "/" + path;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Identifier that = (Identifier) o;
        return namespace.equals(that.namespace) && path.equals(that.path);
    }

    @Override
    public int hashCode() {
        return Objects.hash(namespace, path);
    }
}
