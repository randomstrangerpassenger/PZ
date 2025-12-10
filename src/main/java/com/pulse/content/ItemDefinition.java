package com.pulse.content;

import com.pulse.registry.Identifier;

import java.util.*;

/**
 * 커스텀 아이템 정의.
 * JSON 또는 코드로 아이템 속성 정의.
 */
public class ItemDefinition {

    private Identifier id;
    private String name;
    private String description;
    private String icon; // 아이콘 경로

    // 기본 속성
    private float weight = 1.0f;
    private int maxStackSize = 1;
    private ItemType type = ItemType.NORMAL;
    private ItemCategory category = ItemCategory.MISC;

    // 추가 속성
    private final Map<String, Object> properties = new HashMap<>();
    private final List<String> tags = new ArrayList<>();

    public ItemDefinition(Identifier id) {
        this.id = id;
        this.name = id.getPath();
    }

    public ItemDefinition(String namespace, String path) {
        this(Identifier.of(namespace, path));
    }

    // ─────────────────────────────────────────────────────────────
    // 빌더 패턴
    // ─────────────────────────────────────────────────────────────

    public ItemDefinition name(String name) {
        this.name = name;
        return this;
    }

    public ItemDefinition description(String description) {
        this.description = description;
        return this;
    }

    public ItemDefinition icon(String icon) {
        this.icon = icon;
        return this;
    }

    public ItemDefinition weight(float weight) {
        this.weight = weight;
        return this;
    }

    public ItemDefinition maxStack(int maxStackSize) {
        this.maxStackSize = maxStackSize;
        return this;
    }

    public ItemDefinition type(ItemType type) {
        this.type = type;
        return this;
    }

    public ItemDefinition category(ItemCategory category) {
        this.category = category;
        return this;
    }

    public ItemDefinition property(String key, Object value) {
        this.properties.put(key, value);
        return this;
    }

    public ItemDefinition tag(String tag) {
        this.tags.add(tag);
        return this;
    }

    public ItemDefinition tags(String... tags) {
        this.tags.addAll(Arrays.asList(tags));
        return this;
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public Identifier getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public String getIcon() {
        return icon;
    }

    public float getWeight() {
        return weight;
    }

    public int getMaxStackSize() {
        return maxStackSize;
    }

    public ItemType getType() {
        return type;
    }

    public ItemCategory getCategory() {
        return category;
    }

    public Object getProperty(String key) {
        return properties.get(key);
    }

    @SuppressWarnings("unchecked")
    public <T> T getProperty(String key, T defaultValue) {
        Object val = properties.get(key);
        return val != null ? (T) val : defaultValue;
    }

    public List<String> getTags() {
        return Collections.unmodifiableList(tags);
    }

    public boolean hasTag(String tag) {
        return tags.contains(tag);
    }

    // ─────────────────────────────────────────────────────────────
    // 열거형
    // ─────────────────────────────────────────────────────────────

    public enum ItemType {
        NORMAL, // 일반 아이템
        WEAPON, // 무기
        CLOTHING, // 의류
        CONTAINER, // 컨테이너
        FOOD, // 음식
        DRINKABLE, // 음료
        LITERATURE, // 책/잡지
        MOVEABLE, // 이동 가능 오브젝트
        RADIO, // 라디오
        GENERATOR // 발전기
    }

    public enum ItemCategory {
        MISC, // 기타
        WEAPONS, // 무기
        TOOLS, // 도구
        MEDICAL, // 의료
        FOOD, // 음식
        CLOTHING, // 의류
        MATERIALS, // 재료
        ELECTRONICS, // 전자
        LITERATURE // 문헌
    }
}
