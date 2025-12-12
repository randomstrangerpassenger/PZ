package com.pulse.debug;

import com.pulse.api.DevMode;
import com.pulse.api.log.PulseLogger;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 디버그 오버레이 레지스트리.
 * 모드별 디버그 렌더러를 등록하고 관리.
 * 
 * 사용 예:
 * // 등록
 * DebugOverlayRegistry.register("mymod", ctx -> {
 * ctx.drawLine("FPS: " + fps);
 * });
 * 
 * // 렌더링 (Pulse 또는 게임에서 호출)
 * DebugOverlayRegistry.renderAll(ctx);
 */
public class DebugOverlayRegistry {

    private static final Map<String, DebugOverlayRenderer> renderers = new ConcurrentHashMap<>();
    private static final String LOG = PulseLogger.PULSE;
    private static boolean enabled = true;

    private DebugOverlayRegistry() {
    }

    // ─────────────────────────────────────────────────────────────
    // 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 디버그 오버레이 렌더러 등록
     */
    public static void register(String modId, DebugOverlayRenderer renderer) {
        renderers.put(modId, renderer);

        if (DevMode.isEnabled()) {
            PulseLogger.info(LOG, "Registered overlay renderer for: {}", modId);
        }
    }

    /**
     * 디버그 오버레이 렌더러 해제
     */
    public static void unregister(String modId) {
        renderers.remove(modId);
    }

    // ─────────────────────────────────────────────────────────────
    // 렌더링
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 등록된 렌더러 실행
     */
    public static void renderAll(DebugRenderContext ctx) {
        if (!enabled)
            return;

        for (Map.Entry<String, DebugOverlayRenderer> entry : renderers.entrySet()) {
            String modId = entry.getKey();
            DebugOverlayRenderer renderer = entry.getValue();

            try {
                ctx.beginSection("[" + modId + "]");
                renderer.render(ctx);
                ctx.endSection();
            } catch (Exception e) {
                PulseLogger.error(LOG, "Error in overlay renderer for {}", modId);
                if (DevMode.isEnabled()) {
                    e.printStackTrace();
                }
            }
        }
    }

    /**
     * 콘솔에 디버그 정보 출력 (렌더링 미지원 환경용)
     */
    public static void printToConsole() {
        if (!enabled || renderers.isEmpty())
            return;

        DebugRenderContext ctx = new DebugRenderContext();
        ctx.reset(0);

        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "DEBUG OVERLAY OUTPUT");

        renderAll(ctx);

        PulseLogger.info(LOG, "\n{}", ctx.getOutput());
        PulseLogger.info(LOG, "═══════════════════════════════════════");
    }

    // ─────────────────────────────────────────────────────────────
    // 제어
    // ─────────────────────────────────────────────────────────────

    /**
     * 오버레이 활성화/비활성화
     */
    public static void setEnabled(boolean enable) {
        enabled = enable;
    }

    public static boolean isEnabled() {
        return enabled;
    }

    /**
     * 등록된 렌더러 수
     */
    public static int getRendererCount() {
        return renderers.size();
    }

    /**
     * 등록된 모드 ID 목록
     */
    public static Set<String> getRegisteredMods() {
        return Collections.unmodifiableSet(renderers.keySet());
    }
}
