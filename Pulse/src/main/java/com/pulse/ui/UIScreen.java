package com.pulse.ui;

import com.pulse.api.log.PulseLogger;

import java.util.Stack;

/**
 * UI 스크린 매니저.
 * 게임 UI 스크린 관리 및 전환.
 */
public class UIScreen extends Panel {

    private static final Stack<UIScreen> screenStack = new Stack<>();
    private static UIScreen currentScreen = null;
    private static final String LOG = PulseLogger.PULSE;

    private String title;
    private boolean pauseGame = false;

    public UIScreen(String title) {
        super(0, 0, UIConstants.Defaults.DEFAULT_SCREEN_WIDTH, UIConstants.Defaults.DEFAULT_SCREEN_HEIGHT); // 기본 크기
                                                                                                            // (런타임에 조정)
        this.title = title;
        setDrawBackground(true);
        setBackgroundColor(UIConstants.Colors.SCREEN_BG);
    }

    // ─────────────────────────────────────────────────────────────
    // 스크린 라이프사이클
    // ─────────────────────────────────────────────────────────────

    /**
     * 스크린이 열릴 때 호출.
     */
    public void onOpen() {
        PulseLogger.info(LOG, "[UI] Screen opened: {}", title);
    }

    /**
     * 스크린이 닫힐 때 호출.
     */
    public void onClose() {
        PulseLogger.info(LOG, "[UI] Screen closed: {}", title);
    }

    /**
     * 매 프레임 업데이트.
     */
    public void update(float deltaTime) {
        // 하위 클래스에서 오버라이드
    }

    // ─────────────────────────────────────────────────────────────
    // 스크린 관리 (정적 메서드)
    // ─────────────────────────────────────────────────────────────

    /**
     * 스크린 열기.
     */
    public static void open(UIScreen screen) {
        if (currentScreen != null) {
            screenStack.push(currentScreen);
        }
        currentScreen = screen;
        screen.onOpen();
    }

    /**
     * 현재 스크린 닫기.
     */
    public static void close() {
        if (currentScreen != null) {
            currentScreen.onClose();
            currentScreen = screenStack.isEmpty() ? null : screenStack.pop();
        }
    }

    /**
     * 모든 스크린 닫기.
     */
    public static void closeAll() {
        while (currentScreen != null) {
            close();
        }
    }

    /**
     * 현재 스크린 가져오기.
     */
    public static UIScreen getCurrent() {
        return currentScreen;
    }

    /**
     * 스크린이 열려 있는지 확인.
     */
    public static boolean isOpen() {
        return currentScreen != null;
    }

    /**
     * 현재 스크린 렌더링.
     */
    public static void renderCurrent(UIRenderContext ctx) {
        if (currentScreen != null && currentScreen.isVisible()) {
            currentScreen.preRender(ctx);
            currentScreen.render(ctx);
            currentScreen.postRender(ctx);
        }
    }

    /**
     * 현재 스크린 업데이트.
     */
    public static void updateCurrent(float deltaTime) {
        if (currentScreen != null) {
            currentScreen.update(deltaTime);
        }
    }

    // Getters/Setters
    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public boolean isPauseGame() {
        return pauseGame;
    }

    public void setPauseGame(boolean pause) {
        this.pauseGame = pause;
    }
}
