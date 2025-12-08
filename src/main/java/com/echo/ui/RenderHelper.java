package com.echo.ui;

import java.lang.reflect.Method;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 렌더링 헬퍼 유틸리티
 * 
 * PZ 렌더링 API 호출 시 리플렉션 결과를 캐싱하여
 * 매 프레임마다 발생하는 리플렉션 오버헤드를 제거합니다.
 * 
 * Phase 0 최적화: Gemini 피드백 기반 리플렉션 캐싱 구현
 */
public final class RenderHelper {

    private RenderHelper() {
        // Utility class
    }

    // ============================================================
    // 캐시된 Method 객체
    // ============================================================

    private static volatile Method cachedDrawRect = null;
    private static volatile Method cachedDrawString = null;
    private static volatile Method cachedDrawLine = null;
    private static volatile Method cachedGetTextWidth = null;

    // 초기화 상태 플래그 (실패 시 재시도 방지)
    private static volatile boolean drawRectInitialized = false;
    private static volatile boolean drawStringInitialized = false;
    private static volatile boolean drawLineInitialized = false;
    private static volatile boolean getTextWidthInitialized = false;

    // 동적 메서드 캐시 (추가 확장용)
    private static final ConcurrentHashMap<String, MethodHolder> methodCache = new ConcurrentHashMap<>();

    // ============================================================
    // Method 캐싱 Holder
    // ============================================================

    private static class MethodHolder {
        final Method method;

        MethodHolder(Method method) {
            this.method = method;
        }
    }

    // ============================================================

    /**
     * 캐시된 DrawRect 메서드 가져오기
     * 
     * @return DrawRect 메서드 (없으면 null)
     */
    public static Method getDrawRect() {
        if (!drawRectInitialized) {
            synchronized (RenderHelper.class) {
                if (!drawRectInitialized) {
                    try {
                        Class<?> uiManager = Class.forName("zombie.ui.UIManager");
                        cachedDrawRect = uiManager.getMethod(
                                "DrawRect",
                                int.class, int.class, int.class, int.class,
                                float.class, float.class, float.class, float.class);
                    } catch (Exception e) {
                        // 개발 환경에서는 실패 예상 - 무시
                        cachedDrawRect = null;
                    }
                    drawRectInitialized = true;
                }
            }
        }
        return cachedDrawRect;
    }

    /**
     * 사각형 그리기 (ARGB 색상)
     * 
     * @param x         X 좌표
     * @param y         Y 좌표
     * @param width     너비
     * @param height    높이
     * @param argbColor ARGB 색상 (0xAARRGGBB)
     */
    public static void drawRect(int x, int y, int width, int height, int argbColor) {
        Method method = getDrawRect();
        if (method == null)
            return;

        try {
            float a = ((argbColor >> 24) & 0xFF) / 255f;
            float r = ((argbColor >> 16) & 0xFF) / 255f;
            float g = ((argbColor >> 8) & 0xFF) / 255f;
            float b = (argbColor & 0xFF) / 255f;
            method.invoke(null, x, y, width, height, r, g, b, a);
        } catch (Exception e) {
            // 렌더링 실패 무시 (게임 안정성 우선)
        }
    }

    // ============================================================
    // 텍스트 그리기 (TextManager.DrawString)
    // ============================================================

    /**
     * 캐시된 DrawString 메서드 가져오기
     * 
     * @return DrawString 메서드 (없으면 null)
     */
    public static Method getDrawString() {
        if (!drawStringInitialized) {
            synchronized (RenderHelper.class) {
                if (!drawStringInitialized) {
                    try {
                        Class<?> textManager = Class.forName("zombie.ui.TextManager");
                        cachedDrawString = textManager.getMethod(
                                "DrawString",
                                Object.class, int.class, int.class,
                                float.class, float.class, float.class, float.class);
                    } catch (Exception e) {
                        cachedDrawString = null;
                    }
                    drawStringInitialized = true;
                }
            }
        }
        return cachedDrawString;
    }

    /**
     * 텍스트 그리기 (RGB 색상)
     * 
     * @param text     텍스트
     * @param x        X 좌표
     * @param y        Y 좌표
     * @param rgbColor RGB 색상 (0xRRGGBB)
     */
    public static void drawText(String text, int x, int y, int rgbColor) {
        drawText(text, x, y, rgbColor, 1.0f);
    }

    /**
     * 텍스트 그리기 (RGB 색상 + 알파)
     * 
     * @param text     텍스트
     * @param x        X 좌표
     * @param y        Y 좌표
     * @param rgbColor RGB 색상 (0xRRGGBB)
     * @param alpha    투명도 (0.0 - 1.0)
     */
    public static void drawText(String text, int x, int y, int rgbColor, float alpha) {
        Method method = getDrawString();
        if (method == null)
            return;

        try {
            float r = ((rgbColor >> 16) & 0xFF) / 255f;
            float g = ((rgbColor >> 8) & 0xFF) / 255f;
            float b = (rgbColor & 0xFF) / 255f;
            method.invoke(null, text, x, y, r, g, b, alpha);
        } catch (Exception e) {
            // 렌더링 실패 무시
        }
    }

    // ============================================================
    // 선 그리기 (UIManager.DrawLine - 필요시 확장)
    // ============================================================

    /**
     * 캐시된 DrawLine 메서드 가져오기
     * 
     * @return DrawLine 메서드 (없으면 null)
     */
    public static Method getDrawLine() {
        if (!drawLineInitialized) {
            synchronized (RenderHelper.class) {
                if (!drawLineInitialized) {
                    try {
                        Class<?> uiManager = Class.forName("zombie.ui.UIManager");
                        cachedDrawLine = uiManager.getMethod(
                                "DrawLine",
                                int.class, int.class, int.class, int.class,
                                float.class, float.class, float.class, float.class);
                    } catch (Exception e) {
                        cachedDrawLine = null;
                    }
                    drawLineInitialized = true;
                }
            }
        }
        return cachedDrawLine;
    }

    /**
     * 선 그리기
     * 
     * @param x1        시작 X
     * @param y1        시작 Y
     * @param x2        끝 X
     * @param y2        끝 Y
     * @param argbColor ARGB 색상
     */
    public static void drawLine(int x1, int y1, int x2, int y2, int argbColor) {
        Method method = getDrawLine();
        if (method == null)
            return;

        try {
            float a = ((argbColor >> 24) & 0xFF) / 255f;
            float r = ((argbColor >> 16) & 0xFF) / 255f;
            float g = ((argbColor >> 8) & 0xFF) / 255f;
            float b = (argbColor & 0xFF) / 255f;
            method.invoke(null, x1, y1, x2, y2, r, g, b, a);
        } catch (Exception e) {
            // 렌더링 실패 무시
        }
    }

    // ============================================================
    // 텍스트 너비 측정 (TextManager.GetWidth - 필요시 확장)
    // ============================================================

    /**
     * 캐시된 GetTextWidth 메서드 가져오기
     * 
     * @return GetWidth 메서드 (없으면 null)
     */
    public static Method getGetTextWidth() {
        if (!getTextWidthInitialized) {
            synchronized (RenderHelper.class) {
                if (!getTextWidthInitialized) {
                    try {
                        Class<?> textManager = Class.forName("zombie.ui.TextManager");
                        cachedGetTextWidth = textManager.getMethod("GetTextWidth", Object.class);
                    } catch (Exception e) {
                        cachedGetTextWidth = null;
                    }
                    getTextWidthInitialized = true;
                }
            }
        }
        return cachedGetTextWidth;
    }

    /**
     * 텍스트 너비 측정
     * 
     * @param text 측정할 텍스트
     * @return 텍스트 너비 (픽셀), 측정 실패 시 text.length() * 8 추정값
     */
    public static int getTextWidth(String text) {
        Method method = getGetTextWidth();
        if (method == null) {
            // 폴백: 글자당 8픽셀 추정
            return text != null ? text.length() * 8 : 0;
        }

        try {
            Object result = method.invoke(null, text);
            if (result instanceof Number) {
                return ((Number) result).intValue();
            }
        } catch (Exception e) {
            // 측정 실패
        }
        return text != null ? text.length() * 8 : 0;
    }

    // ============================================================
    // 동적 메서드 캐싱 (확장용)
    // ============================================================

    /**
     * 동적 메서드 캐싱
     * 
     * @param className  클래스명 (예: "zombie.ui.UIManager")
     * @param methodName 메서드명
     * @param paramTypes 파라미터 타입들
     * @return 캐시된 Method (없으면 null)
     */
    public static Method getCachedMethod(String className, String methodName, Class<?>... paramTypes) {
        String key = className + "#" + methodName;

        return methodCache.computeIfAbsent(key, k -> {
            try {
                Class<?> clazz = Class.forName(className);
                Method method = clazz.getMethod(methodName, paramTypes);
                return new MethodHolder(method);
            } catch (Exception e) {
                return new MethodHolder(null);
            }
        }).method;
    }

    /**
     * 캐시 초기화 (테스트용)
     */
    public static void resetCache() {
        synchronized (RenderHelper.class) {
            cachedDrawRect = null;
            cachedDrawString = null;
            cachedDrawLine = null;
            cachedGetTextWidth = null;
            drawRectInitialized = false;
            drawStringInitialized = false;
            drawLineInitialized = false;
            getTextWidthInitialized = false;
            methodCache.clear();
        }
    }

    /**
     * PZ 환경 여부 확인
     * 
     * @return PZ 렌더링 API가 사용 가능하면 true
     */
    public static boolean isPZEnvironment() {
        return getDrawRect() != null || getDrawString() != null;
    }
}
