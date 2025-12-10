package com.pulse.ui;

import java.util.*;

/**
 * HUD 오버레이 매니저.
 * 게임 화면 위에 표시되는 UI 레이어.
 */
public class HUDOverlay {

    private static final HUDOverlay INSTANCE = new HUDOverlay();

    private final Map<String, HUDLayer> layers = new LinkedHashMap<>();
    private boolean visible = true;

    private HUDOverlay() {
    }

    public static HUDOverlay getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 레이어 관리
    // ─────────────────────────────────────────────────────────────

    /**
     * HUD 레이어 등록.
     * 
     * @param id       레이어 식별자
     * @param layer    레이어
     * @param priority 우선순위 (낮을수록 먼저 렌더링)
     */
    public static void registerLayer(String id, HUDLayer layer, int priority) {
        layer.id = id;
        layer.priority = priority;
        INSTANCE.layers.put(id, layer);
        INSTANCE.sortLayers();
        System.out.println("[Pulse/HUD] Registered layer: " + id);
    }

    /**
     * HUD 레이어 등록 해제.
     */
    public static void unregisterLayer(String id) {
        INSTANCE.layers.remove(id);
    }

    /**
     * 레이어 가져오기.
     */
    public static HUDLayer getLayer(String id) {
        return INSTANCE.layers.get(id);
    }

    private void sortLayers() {
        List<Map.Entry<String, HUDLayer>> entries = new ArrayList<>(layers.entrySet());
        entries.sort(Comparator.comparingInt(e -> e.getValue().priority));

        layers.clear();
        for (var entry : entries) {
            layers.put(entry.getKey(), entry.getValue());
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 렌더링
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 HUD 레이어 렌더링.
     */
    public static void render(UIRenderContext ctx) {
        if (!INSTANCE.visible)
            return;

        for (HUDLayer layer : INSTANCE.layers.values()) {
            if (layer.isVisible()) {
                try {
                    layer.render(ctx);
                } catch (Exception e) {
                    System.err.println("[Pulse/HUD] Error rendering layer: " + layer.id);
                    e.printStackTrace();
                }
            }
        }
    }

    /**
     * 모든 HUD 레이어 업데이트.
     */
    public static void update(float deltaTime) {
        for (HUDLayer layer : INSTANCE.layers.values()) {
            if (layer.isVisible()) {
                layer.update(deltaTime);
            }
        }
    }

    // Getters/Setters
    public static boolean isVisible() {
        return INSTANCE.visible;
    }

    public static void setVisible(boolean visible) {
        INSTANCE.visible = visible;
    }

    public static Collection<HUDLayer> getLayers() {
        return Collections.unmodifiableCollection(INSTANCE.layers.values());
    }

    // ─────────────────────────────────────────────────────────────
    // HUD 레이어 추상 클래스
    // ─────────────────────────────────────────────────────────────

    public static abstract class HUDLayer {
        String id;
        int priority;
        private boolean visible = true;

        /**
         * 레이어 렌더링.
         */
        public abstract void render(UIRenderContext ctx);

        /**
         * 레이어 업데이트.
         */
        public void update(float deltaTime) {
            // 선택적 오버라이드
        }

        public String getId() {
            return id;
        }

        public int getPriority() {
            return priority;
        }

        public boolean isVisible() {
            return visible;
        }

        public void setVisible(boolean visible) {
            this.visible = visible;
        }
    }
}
