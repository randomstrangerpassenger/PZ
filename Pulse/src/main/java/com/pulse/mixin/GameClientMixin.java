package com.pulse.mixin;

import org.spongepowered.asm.mixin.Mixin;

/**
 * GameClient Mixin.
 * 멀티플레이어 전용 클라이언트 업데이트 훅.
 * 
 * v0.9: Scheduler tick consolidated to IsoWorldMixin only.
 * GameClientMixin no longer calls tick() to prevent double-tick in MP.
 * 
 * Note: GameTickEvent는 IsoWorldMixin에서만 발행됨.
 * Note: PulseScheduler.tick()도 IsoWorldMixin에서만 호출됨.
 * 
 * 이 Mixin은 향후 MP 전용 훅 추가를 위해 유지됩니다.
 */
@Mixin(targets = "zombie.network.GameClient")
public abstract class GameClientMixin {
    // v0.9: tick() 호출 제거됨 - IsoWorldMixin에서 단일 호출로 통합
    // MP 환경에서 double-tick 방지를 위한 필수 수정
}
