package com.pulse.content;

import com.pulse.registry.Identifier;

import java.util.*;

/**
 * 아이템 태그 시스템.
 * 아이템을 그룹화하여 레시피나 로직에서 사용.
 */
public class ItemTag {

    private static final Map<Identifier, ItemTag> TAGS = new HashMap<>();

    private final Identifier id;
    private final Set<Identifier> items = new HashSet<>();

    private ItemTag(Identifier id) {
        this.id = id;
    }

    // ─────────────────────────────────────────────────────────────
    // 정적 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 태그 생성 또는 가져오기.
     */
    public static ItemTag getOrCreate(Identifier id) {
        return TAGS.computeIfAbsent(id, ItemTag::new);
    }

    /**
     * 문자열 ID로 태그 가져오기.
     */
    public static ItemTag getOrCreate(String id) {
        return getOrCreate(Identifier.parse(id));
    }

    /**
     * 태그 가져오기 (없으면 null).
     */
    public static ItemTag get(Identifier id) {
        return TAGS.get(id);
    }

    /**
     * 모든 태그 ID 가져오기.
     */
    public static Set<Identifier> getAllTags() {
        return Collections.unmodifiableSet(TAGS.keySet());
    }

    // ─────────────────────────────────────────────────────────────
    // 인스턴스 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 태그에 아이템 추가.
     */
    public ItemTag add(Identifier item) {
        items.add(item);
        return this;
    }

    /**
     * 태그에 아이템들 추가.
     */
    public ItemTag addAll(Identifier... items) {
        this.items.addAll(Arrays.asList(items));
        return this;
    }

    /**
     * 태그에서 아이템 제거.
     */
    public ItemTag remove(Identifier item) {
        items.remove(item);
        return this;
    }

    /**
     * 아이템이 태그에 포함되는지 확인.
     */
    public boolean contains(Identifier item) {
        return items.contains(item);
    }

    /**
     * 태그의 모든 아이템 가져오기.
     */
    public Set<Identifier> getItems() {
        return Collections.unmodifiableSet(items);
    }

    /**
     * 태그 ID.
     */
    public Identifier getId() {
        return id;
    }

    /**
     * 태그 크기.
     */
    public int size() {
        return items.size();
    }

    @Override
    public String toString() {
        return "#" + id.toString();
    }
}
