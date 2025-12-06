package com.pulse.profiler;

import com.pulse.api.Pulse;
import com.pulse.debug.DebugOverlayRegistry;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.mod.PulseMod;

/**
 * Pulse Profiler 모드 엔트리포인트.
 */
public class ProfilerMod implements PulseMod {

    public static final String MOD_ID = "Pulse_profiler";
    private int tickCounter = 0;

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "Initializing Pulse Profiler...");

        // 이벤트 등록
        EventBus.subscribe(GameTickEvent.class, this::onTick, MOD_ID);

        // 디버그 오버레이 등록
        if (ProfilerConfig.showOverlay) {
            DebugOverlayRegistry.register(MOD_ID, new ProfilerOverlay());
        }

        Pulse.log(MOD_ID, "Pulse Profiler initialized!");
    }

    private void onTick(GameTickEvent event) {
        if (!ProfilerConfig.enabled)
            return;

        tickCounter++;

        // 설정된 간격마다 통계 로그 출력
        if (tickCounter >= ProfilerConfig.logInterval) {
            PulseProfiler.logStats();
            tickCounter = 0;

            // 주기적으로 통계 리셋 (선택적)
            // PulseProfiler.reset();
        }
    }
}
