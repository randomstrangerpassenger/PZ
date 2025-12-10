package com.pulse.debug;

/**
 * 디버그 렌더링 컨텍스트.
 * 디버그 오버레이에 정보를 그리기 위한 추상화 레이어.
 * 
 * 실제 구현은 PZ 렌더링 시스템과 연동 필요.
 * 이 버전은 콘솔 출력 기반 플레이스홀더.
 */
public class DebugRenderContext {

    private final StringBuilder buffer = new StringBuilder();
    private int currentY = 0;

    // ─────────────────────────────────────────────────────────────
    // 텍스트 그리기
    // ─────────────────────────────────────────────────────────────

    /**
     * 텍스트 그리기
     */
    public void drawText(int x, int y, String text) {
        // 플레이스홀더: 콘솔에 출력
        buffer.append(String.format("[%d,%d] %s\n", x, y, text));
    }

    /**
     * 색상 있는 텍스트 그리기
     */
    public void drawText(int x, int y, String text, int color) {
        drawText(x, y, text);
    }

    /**
     * 다음 줄에 텍스트 그리기 (자동 위치)
     */
    public void drawLine(String text) {
        drawText(10, currentY, text);
        currentY += 15;
    }

    // ─────────────────────────────────────────────────────────────
    // 도형 그리기
    // ─────────────────────────────────────────────────────────────

    /**
     * 사각형 그리기
     */
    public void drawRect(int x, int y, int width, int height, int color) {
        // 플레이스홀더
    }

    /**
     * 채워진 사각형 그리기
     */
    public void fillRect(int x, int y, int width, int height, int color) {
        // 플레이스홀더
    }

    /**
     * 선 그리기
     */
    public void drawLine(int x1, int y1, int x2, int y2, int color) {
        // 플레이스홀더
    }

    // ─────────────────────────────────────────────────────────────
    // 섹션
    // ─────────────────────────────────────────────────────────────

    /**
     * 섹션 시작 (구분선 + 제목)
     */
    public void beginSection(String title) {
        drawLine("═══════════════════════════════════════");
        drawLine(title);
        drawLine("───────────────────────────────────────");
    }

    /**
     * 섹션 종료
     */
    public void endSection() {
        currentY += 5;
    }

    // ─────────────────────────────────────────────────────────────
    // 출력
    // ─────────────────────────────────────────────────────────────

    /**
     * 버퍼 내용 반환 (콘솔 출력용)
     */
    public String getOutput() {
        return buffer.toString();
    }

    /**
     * 현재 Y 위치 초기화
     */
    public void reset(int startY) {
        currentY = startY;
        buffer.setLength(0);
    }
}
