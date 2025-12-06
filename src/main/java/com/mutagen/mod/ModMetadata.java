package com.mutagen.mod;

import java.util.ArrayList;
import java.util.List;

/**
 * 모드 메타데이터.
 * 각 모드의 mutagen.mod.json 파일에서 파싱됨.
 * 
 * 예시 mutagen.mod.json:
 * {
 *   "id": "mymod",
 *   "name": "My Awesome Mod",
 *   "version": "1.0.0",
 *   "author": "ModAuthor",
 *   "description": "A cool mod for Project Zomboid",
 *   "entrypoint": "com.example.mymod.MyMod",
 *   "mixins": ["mixins.mymod.json"],
 *   "dependencies": [
 *     { "id": "mutagen", "version": ">=1.0.0" },
 *     { "id": "othermod", "version": ">=2.0.0", "optional": true }
 *   ]
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
    
    // 런타임에 설정되는 필드
    private transient String sourceFile;  // JAR 파일 경로
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
