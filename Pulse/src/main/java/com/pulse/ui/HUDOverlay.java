package com.pulse.ui;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.ui.IHUDLayer;
import com.pulse.api.ui.IHUDOverlay;
import com.pulse.api.ui.IUIRenderContext;

import java.util.*;
import java.util.function.Consumer;

/**
 * HUD 오버레이 매니저.
 * 게임 화면 위에 표시되는 UI 레이어.
 */
public class HUDOverlay implements IHUDOverlay {

    private static final HUDOverlay INSTANCE = new HUDOverlay();
    private static final String LOG = PulseLogger.PULSE;

    private final Map<String, HUDLayer> layers = new LinkedHashMap<>();
    private boolean visible = true;

    private HUDOverlay() {
    }

    public static HUDOverlay getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // IHUDOverlay 구현 (Phase 2: API 계약)
    // ─────────────────────────────────────────────────────────────

    /**
     * HUD 렌더링 콜백 등록 (IHUDOverlay 구현).
     * 
     * @param id       고유 식별자
     * @param renderer 렌더링 함수
     */
    @Override
    public void registerRenderer(String id, Consumer<IUIRenderContext> renderer) {
        // Consumer를 HUDLayer로 래핑하여 기존 시스템에 통합
        HUDLayer layer = new HUDLayer() {
            @Override
            public void render(UIRenderContext ctx) {
                // UIRenderContext가 IUIRenderContext를 구현하므로 안전하게 전달
                renderer.accept((IUIRenderContext) ctx);
            }
        };
        registerLayer(id, layer, 0); // 기본 우선순위 0
    }

    /**
     * HUD 렌더링 콜백 제거 (IHUDOverlay 구현).
     */
    @Override
    public void unregisterRenderer(String id) {
        unregisterLayer(id);
    }

    // ─────────────────────────────────────────────────────────────
    // 레이어 관리 (Phase 3에서 Frame으로 이동 예정)
    // ─────────────────────────────────────────────────────────────

    /**
     * HUD 레이어 등록.
     * 
     * @param id       레이어 식별자
     * @param layer    레이어
     * @param priority 우선순위 (낮을수록 먼저 렌더링)
     * @deprecated Phase 3에서 Frame으로 이동 예정. registerRenderer() 사용 권장.
     */
    @Deprecated
    public static void registerLayer(String id, HUDLayer layer, int priority) {
        layer.id = id;
        layer.priority = priority;
        INSTANCE.layers.put(id, layer);
        INSTANCE.sortLayers();
        PulseLogger.info(LOG, "[HUD] Registered layer: {}", id);
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
                    PulseLogger.error(LOG, "[HUD] Error rendering layer: {}", layer.id, e);
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
