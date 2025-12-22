package com.pulse.api.dto;

/**
 * 틱 타이밍 DTO.
 * 
 * <p>
 * 게임 틱의 타이밍 정보를 표현합니다.
 * </p>
 * 
 * @param tickNumber    틱 번호
 * @param durationNanos 틱 처리 시간 (나노초)
 * @param deltaTime     이전 틱과의 시간 차이 (초)
 * 
 * @since Pulse 1.6
 */
public record TickTiming(
        long tickNumber,
        long durationNanos,
        float deltaTime) {
    /**
     * 밀리초 단위 duration 반환.
     */
    public double durationMs() {
        return durationNanos / 1_000_000.0;
    }

    /**
     * FPS 추정값 반환.
     */
    public float estimatedFps() {
        return deltaTime > 0 ? 1.0f / deltaTime : 0;
    }
}
