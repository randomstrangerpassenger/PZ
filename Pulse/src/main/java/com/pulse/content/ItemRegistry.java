package com.pulse.content;

import com.pulse.registry.Identifier;

import java.util.*;

/**
 * 아이템 레지스트리.
 * 커스텀 아이템 등록 및 조회.
 */
public class ItemRegistry {

    private static final ItemRegistry INSTANCE = new ItemRegistry();

    private final Map<Identifier, ItemDefinition> items = new LinkedHashMap<>();
    private final Map<String, Set<Identifier>> byTag = new HashMap<>();
    private final Map<ItemDefinition.ItemCategory, Set<Identifier>> byCategory = new HashMap<>();

    private ItemRegistry() {
    }

    public static ItemRegistry getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 아이템 등록.
     */
    public static void register(ItemDefinition item) {
        INSTANCE.registerInternal(item);
    }

    private void registerInternal(ItemDefinition item) {
        Identifier id = item.getId();

        if (items.containsKey(id)) {
            System.err.println("[Pulse/Items] Duplicate item ID: " + id);
            return;
        }

        items.put(id, item);

        // 태그 인덱싱
        for (String tag : item.getTags()) {
            byTag.computeIfAbsent(tag, k -> new HashSet<>()).add(id);
        }

        // 카테고리 인덱싱
        byCategory.computeIfAbsent(item.getCategory(), k -> new HashSet<>()).add(id);

        System.out.println("[Pulse/Items] Registered: " + id);
    }

    /**
     * 아이템 등록 해제.
     */
    public static void unregister(Identifier id) {
        INSTANCE.unregisterInternal(id);
    }

    private void unregisterInternal(Identifier id) {
        ItemDefinition item = items.remove(id);
        if (item != null) {
            // 태그에서 제거
            for (String tag : item.getTags()) {
                Set<Identifier> set = byTag.get(tag);
                if (set != null)
                    set.remove(id);
            }
            // 카테고리에서 제거
            Set<Identifier> catSet = byCategory.get(item.getCategory());
            if (catSet != null)
                catSet.remove(id);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * ID로 아이템 조회.
     */
    public static ItemDefinition get(Identifier id) {
        return INSTANCE.items.get(id);
    }

    /**
     * 문자열 ID로 조회.
     */
    public static ItemDefinition get(String id) {
        return get(Identifier.parse(id));
    }

    /**
     * 태그로 아이템 조회.
     */
    public static Set<ItemDefinition> getByTag(String tag) {
        Set<Identifier> ids = INSTANCE.byTag.get(tag);
        if (ids == null)
            return Collections.emptySet();

        Set<ItemDefinition> result = new HashSet<>();
        for (Identifier id : ids) {
            result.add(INSTANCE.items.get(id));
        }
        return result;
    }

    /**
     * 카테고리로 아이템 조회.
     */
    public static Set<ItemDefinition> getByCategory(ItemDefinition.ItemCategory category) {
        Set<Identifier> ids = INSTANCE.byCategory.get(category);
        if (ids == null)
            return Collections.emptySet();

        Set<ItemDefinition> result = new HashSet<>();
        for (Identifier id : ids) {
            result.add(INSTANCE.items.get(id));
        }
        return result;
    }

    /**
     * 모든 등록된 아이템.
     */
    public static Collection<ItemDefinition> getAll() {
        return Collections.unmodifiableCollection(INSTANCE.items.values());
    }

    /**
     * 등록된 아이템 수.
     */
    public static int count() {
        return INSTANCE.items.size();
    }
}
