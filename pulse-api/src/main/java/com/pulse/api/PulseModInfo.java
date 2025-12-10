package com.pulse.api;

/**
 * 모드 정보 DTO.
 * 로드된 모드의 메타데이터를 담는 불변 객체.
 */
public final class PulseModInfo {

    private final String modId;
    private final String name;
    private final String version;
    private final String description;
    private final String[] authors;

    public PulseModInfo(String modId, String name, String version, String description, String[] authors) {
        this.modId = modId;
        this.name = name;
        this.version = version;
        this.description = description;
        this.authors = authors != null ? authors.clone() : new String[0];
    }

    public String getModId() {
        return modId;
    }

    public String getName() {
        return name;
    }

    public String getVersion() {
        return version;
    }

    public String getDescription() {
        return description;
    }

    public String[] getAuthors() {
        return authors.clone();
    }

    @Override
    public String toString() {
        return String.format("%s (%s) v%s", name, modId, version);
    }
}
