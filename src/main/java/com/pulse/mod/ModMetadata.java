package com.pulse.mod;

import java.util.ArrayList;
import java.util.List;

/**
 * 모드 메타데이터.
 * 각 모드의 pulse.mod.json 파일에서 파싱됨.
 * 
 * 예시 pulse.mod.json:
 * {
 * "id": "mymod",
 * "name": "My Awesome Mod",
 * "version": "1.0.0",
 * "author": "ModAuthor",
 * "description": "A cool mod for Project Zomboid",
 * "entrypoint": "com.example.mymod.MyMod",
 * "mixins": ["mixins.mymod.json"],
 * "dependencies": [
 * { "id": "Pulse", "version": ">=1.0.0" },
 * { "id": "othermod", "version": ">=2.0.0", "optional": true }
 * ]
 * }
 */
public class ModMetadata {

    private String id;
    private String name;
    private String version;
    private String author;
    private String description;
    private String entrypoint;
    private List<String> mixins = new ArrayList<>();
    private List<Dependency> dependencies = new ArrayList<>();
    private List<String> conflicts = new ArrayList<>();

    // Phase 2 추가 필드
    private String license;
    private String loaderVersion; // 필요한 Pulse 버전 (예: ">=1.0.0")
    private String gameVersion; // 필요한 PZ 버전 (예: "41.78+")
    private List<String> authors = new ArrayList<>();
    private EntryPoints entryPoints; // 환경별 엔트리포인트
    private List<String> accessWideners = new ArrayList<>();
    private List<String> permissions = new ArrayList<>();
    private String loadOrder; // 로드 순서 힌트 (예: "after:othermod")
    private String homepage;
    private String issues; // 이슈 트래커 URL
    private String source; // 소스 코드 URL

    // 런타임에 설정되는 필드
    private transient String sourceFile; // JAR 파일 경로
    private transient boolean loaded = false;

    // ─────────────────────────────────────────────────────────────
    // Getters & Setters
    // ─────────────────────────────────────────────────────────────

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getEntrypoint() {
        return entrypoint;
    }

    public void setEntrypoint(String entrypoint) {
        this.entrypoint = entrypoint;
    }

    public List<String> getMixins() {
        return mixins;
    }

    public void setMixins(List<String> mixins) {
        this.mixins = mixins != null ? mixins : new ArrayList<>();
    }

    public List<Dependency> getDependencies() {
        return dependencies;
    }

    public void setDependencies(List<Dependency> dependencies) {
        this.dependencies = dependencies != null ? dependencies : new ArrayList<>();
    }

    public List<String> getConflicts() {
        return conflicts;
    }

    public void setConflicts(List<String> conflicts) {
        this.conflicts = conflicts != null ? conflicts : new ArrayList<>();
    }

    public List<String> getPermissions() {
        return permissions;
    }

    public void setPermissions(List<String> permissions) {
        this.permissions = permissions != null ? permissions : new ArrayList<>();
    }

    public String getLicense() {
        return license;
    }

    public void setLicense(String license) {
        this.license = license;
    }

    public String getLoaderVersion() {
        return loaderVersion;
    }

    public void setLoaderVersion(String loaderVersion) {
        this.loaderVersion = loaderVersion;
    }

    public String getGameVersion() {
        return gameVersion;
    }

    public void setGameVersion(String gameVersion) {
        this.gameVersion = gameVersion;
    }

    public List<String> getAuthors() {
        return authors;
    }

    public void setAuthors(List<String> authors) {
        this.authors = authors != null ? authors : new ArrayList<>();
    }

    public EntryPoints getEntryPoints() {
        return entryPoints;
    }

    public void setEntryPoints(EntryPoints entryPoints) {
        this.entryPoints = entryPoints;
    }

    public List<String> getAccessWideners() {
        return accessWideners;
    }

    public void setAccessWideners(List<String> accessWideners) {
        this.accessWideners = accessWideners != null ? accessWideners : new ArrayList<>();
    }

    public String getLoadOrder() {
        return loadOrder;
    }

    public void setLoadOrder(String loadOrder) {
        this.loadOrder = loadOrder;
    }

    public String getHomepage() {
        return homepage;
    }

    public void setHomepage(String homepage) {
        this.homepage = homepage;
    }

    public String getIssues() {
        return issues;
    }

    public void setIssues(String issues) {
        this.issues = issues;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getSourceFile() {
        return sourceFile;
    }

    public void setSourceFile(String sourceFile) {
        this.sourceFile = sourceFile;
    }

    public boolean isLoaded() {
        return loaded;
    }

    public void setLoaded(boolean loaded) {
        this.loaded = loaded;
    }

    // ─────────────────────────────────────────────────────────────
    // 의존성 클래스
    // ─────────────────────────────────────────────────────────────

    public static class Dependency {
        private String id;
        private String version;
        private boolean optional = false;

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getVersion() {
            return version;
        }

        public void setVersion(String version) {
            this.version = version;
        }

        public boolean isOptional() {
            return optional;
        }

        public void setOptional(boolean optional) {
            this.optional = optional;
        }

        @Override
        public String toString() {
            return id + " " + version + (optional ? " (optional)" : "");
        }
    }

    @Override
    public String toString() {
        return String.format("%s (%s) v%s by %s", name, id, version, author);
    }
}
