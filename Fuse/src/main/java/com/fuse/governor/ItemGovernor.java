package com.fuse.governor;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.world.IWorldObjectThrottlePolicy;
import com.pulse.api.world.WorldObjectThrottleLevel;

/**
 * Fuse Item Governor - 월드 아이템 업데이트 쓰로틀링 정책 구현.
 * 
 * IWorldObjectThrottlePolicy를 구현하여 WorldItemMixin에 정책을 주입합니다.
 * 적응형 쓰로틀링: 시스템 부하에 따라 업데이트 주기를 조절합니다.
 * 
 * Phase 4: stub에서 복원 - IWorldObjectThrottlePolicy 구현
 * 
 * @since Fuse 0.3.0
 * @since Fuse 0.4.0 - Phase 4: IWorldObjectThrottlePolicy 구현 복원
 */
public class ItemGovernor implements IWorldObjectThrottlePolicy {

    private static final String LOG = "Fuse";

    // 쓰로틀 설정
    private boolean enabled = true;
    private boolean shellShockActive = false;
    private float baseDistance = 20.0f;
    private int cacheValidTicks = 60;

    // 통계
    private long throttleCount = 0;
    private long fullUpdateCount = 0;
    private long shellShockThrottleCount = 0;
    private long starvationPreventCount = 0;

    public ItemGovernor() {
        PulseLogger.info(LOG, "ItemGovernor initialized (Phase 4 - IWorldObjectThrottlePolicy)");
    }

    // --- IWorldObjectThrottlePolicy Implementation ---

    @Override
    public WorldObjectThrottleLevel decideThrottleLevel(
            Object item, // zombie.iso.objects.IsoWorldInventoryObject
            int sequenceId,
            WorldObjectThrottleLevel cachedLevel,
            long lastCacheTick,
            long currentTick,
            int ticksSinceLastUpdate) {

        if (!enabled) {
            return WorldObjectThrottleLevel.FULL;
        }

        // Starvation 방지: 300틱 이상 업데이트 안된 경우 Full 업데이트
        if (ticksSinceLastUpdate > 300) {
            starvationPreventCount++;
            return WorldObjectThrottleLevel.FULL;
        }

        // 캐시 유효성 확인
        if (cachedLevel != null && (currentTick - lastCacheTick) < cacheValidTicks) {
            return cachedLevel;
        }

        // ShellShock 상태: 최소 업데이트만
        if (shellShockActive) {
            shellShockThrottleCount++;
            return WorldObjectThrottleLevel.MINIMAL;
        }

        // 플레이어 거리 기반 결정 (간략화된 로직)
        // 실제 거리 계산은 Mixin에서 수행하여 전달해야 함
        // 여기서는 sequenceId 기반 분산 처리
        int mod = sequenceId % 4;
        WorldObjectThrottleLevel level;
        switch (mod) {
            case 0:
                level = WorldObjectThrottleLevel.FULL;
                fullUpdateCount++;
                break;
            case 1:
                level = WorldObjectThrottleLevel.REDUCED;
                throttleCount++;
                break;
            case 2:
                level = WorldObjectThrottleLevel.LOW;
                throttleCount++;
                break;
            default:
                level = WorldObjectThrottleLevel.MINIMAL;
                throttleCount++;
                break;
        }

        return level;
    }

    @Override
    public WorldObjectThrottleLevel decideThrottleLevelForCorpse(
            Object corpse, // zombie.iso.objects.IsoDeadBody
            int sequenceId,
            WorldObjectThrottleLevel cachedLevel,
            long lastCacheTick,
            long currentTick,
            int ticksSinceLastUpdate) {

        if (!enabled) {
            return WorldObjectThrottleLevel.FULL;
        }

        // Starvation 방지: 시체는 600틱까지 허용
        if (ticksSinceLastUpdate > 600) {
            starvationPreventCount++;
            return WorldObjectThrottleLevel.FULL;
        }

        // 캐시 유효성 확인
        if (cachedLevel != null && (currentTick - lastCacheTick) < cacheValidTicks * 2) {
            return cachedLevel;
        }

        // ShellShock 상태: 시체는 거의 업데이트 안 함
        if (shellShockActive) {
            shellShockThrottleCount++;
            return WorldObjectThrottleLevel.MINIMAL;
        }

        // 시체는 기본적으로 낮은 우선순위
        throttleCount++;
        return WorldObjectThrottleLevel.LOW;
    }

    // --- Control Methods ---

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
        PulseLogger.info(LOG, "ItemGovernor enabled: " + enabled);
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setShellShockActive(boolean active) {
        this.shellShockActive = active;
        if (active) {
            PulseLogger.warn(LOG, "ItemGovernor ShellShock mode ACTIVATED");
        } else {
            PulseLogger.info(LOG, "ItemGovernor ShellShock mode deactivated");
        }
    }

    public boolean isShellShockActive() {
        return shellShockActive;
    }

    public void setBaseDistance(float distance) {
        this.baseDistance = distance;
    }

    public float getBaseDistance() {
        return baseDistance;
    }

    // --- Statistics ---

    public long getThrottleCount() {
        return throttleCount;
    }

    public long getFullUpdateCount() {
        return fullUpdateCount;
    }

    public long getShellShockThrottleCount() {
        return shellShockThrottleCount;
    }

    public long getStarvationPreventCount() {
        return starvationPreventCount;
    }

    public void resetStats() {
        throttleCount = 0;
        fullUpdateCount = 0;
        shellShockThrottleCount = 0;
        starvationPreventCount = 0;
    }

    public void printStatus() {
        PulseLogger.info(LOG, "ItemGovernor Stats:");
        PulseLogger.info(LOG, "  Enabled: " + enabled);
        PulseLogger.info(LOG, "  ShellShock: " + shellShockActive);
        PulseLogger.info(LOG, "  Throttled: " + throttleCount);
        PulseLogger.info(LOG, "  Full Updates: " + fullUpdateCount);
        PulseLogger.info(LOG, "  ShellShock Throttles: " + shellShockThrottleCount);
        PulseLogger.info(LOG, "  Starvation Prevents: " + starvationPreventCount);
    }
}
