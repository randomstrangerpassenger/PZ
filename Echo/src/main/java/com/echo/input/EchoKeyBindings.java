package com.echo.input;

import com.echo.EchoRuntime;
import com.echo.measure.EchoProfiler;
import com.echo.ui.EchoExtendedHUD;

/**
 * Echo 키바인딩 관리
 * 
 * F6: HUD 토글
 * F7: 프로파일링 On/Off
 * F8: HotspotPanel 토글
 * F9: Extended HUD 토글 (메모리/네트워크/병목)
 */
public final class EchoKeyBindings {

    // 키바인딩 상태
    private static boolean hudVisible = true;
    private static boolean panelVisible = false;

    // 키 코드 (PZ/LWJGL 키코드)
    public static final int KEY_F6 = 64; // 0x40 - HUD 토글
    public static final int KEY_F7 = 65; // 0x41 - 프로파일링 토글
    public static final int KEY_F8 = 66; // 0x42 - 패널 토글
    public static final int KEY_F9 = 67; // 0x43 - Extended HUD 토글

    private EchoKeyBindings() {
        // Utility class
    }

    /**
     * 키바인딩 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        // Pulse KeyBindings API 시도
        if (tryPulseKeyBindings()) {
            System.out.println("[Echo] Key bindings registered via Pulse API");
            return;
        }

        // 폴백: 수동 키 체크 (render 루프에서 호출 필요)
        System.out.println("[Echo] Key bindings: F6=HUD, F7=Profile, F8=Panel, F9=Extended");
        System.out.println("[Echo] Note: Use PulseEventAdapter.checkKeys() in render loop");
    }

    /**
     * Pulse KeyBindings API로 등록 시도
     * 
     * @return 등록 성공 여부
     */
    private static boolean tryPulseKeyBindings() {
        try {
            Class<?> keyBindings = Class.forName("com.pulse.api.KeyBindings");

            // register(String name, int key, Runnable action)
            java.lang.reflect.Method registerMethod = keyBindings.getMethod(
                    "register", String.class, int.class, Runnable.class);

            registerMethod.invoke(null, "echo_hud", KEY_F6, (Runnable) EchoKeyBindings::toggleHud);
            registerMethod.invoke(null, "echo_profile", KEY_F7, (Runnable) EchoKeyBindings::toggleProfiling);
            registerMethod.invoke(null, "echo_panel", KEY_F8, (Runnable) EchoKeyBindings::togglePanel);
            registerMethod.invoke(null, "echo_extended", KEY_F9, (Runnable) EchoKeyBindings::toggleExtendedHud);

            return true;
        } catch (ClassNotFoundException e) {
            return false;
        } catch (Exception e) {
            System.out.println("[Echo] Warning: Failed to register key bindings: " + e.getMessage());
            return false;
        }
    }

    /**
     * 수동 키 체크 (Pulse API 없을 때 렌더 루프에서 호출)
     * 
     * @param keyCode 눌린 키 코드
     */
    public static void onKeyPressed(int keyCode) {
        if (!EchoRuntime.isEnabled())
            return;

        switch (keyCode) {
            case KEY_F6 -> toggleHud();
            case KEY_F7 -> toggleProfiling();
            case KEY_F8 -> togglePanel();
            case KEY_F9 -> toggleExtendedHud();
        }
    }

    /**
     * HUD 토글 (F6)
     */
    public static void toggleHud() {
        if (!EchoRuntime.isEnabled())
            return;
        hudVisible = !hudVisible;
        System.out.println("[Echo] HUD " + (hudVisible ? "ON" : "OFF"));
    }

    /**
     * 프로파일링 토글 (F7)
     */
    public static void toggleProfiling() {
        if (!EchoRuntime.isEnabled())
            return;
        EchoProfiler profiler = EchoProfiler.getInstance();
        if (profiler.isEnabled()) {
            profiler.disable();
            System.out.println("[Echo] Profiling OFF");
        } else {
            profiler.enable();
            System.out.println("[Echo] Profiling ON");
        }
    }

    /**
     * HotspotPanel 토글 (F8)
     */
    public static void togglePanel() {
        if (!EchoRuntime.isEnabled())
            return;
        panelVisible = !panelVisible;
        System.out.println("[Echo] Panel " + (panelVisible ? "ON" : "OFF"));
    }

    /**
     * Extended HUD 토글 (F9)
     */
    public static void toggleExtendedHud() {
        if (!EchoRuntime.isEnabled())
            return;
        EchoExtendedHUD.toggle();
    }

    // Getters
    public static boolean isHudVisible() {
        return hudVisible && EchoRuntime.isEnabled();
    }

    public static boolean isPanelVisible() {
        return panelVisible && EchoRuntime.isEnabled();
    }

    public static boolean isExtendedHudVisible() {
        return EchoExtendedHUD.isShown() && EchoRuntime.isEnabled();
    }

    // Setters (테스트/명령어용)
    public static void setHudVisible(boolean visible) {
        hudVisible = visible;
    }

    public static void setPanelVisible(boolean visible) {
        panelVisible = visible;
    }
}
