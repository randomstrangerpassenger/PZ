package com.pulse.test.a;

import com.pulse.api.Pulse;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.mod.PulseMod;

/**
 * Test Mod A - Phase 1 검증용 단순 로그/이벤트 테스트 모드
 * 
 * 테스트 항목:
 * - PulseMod 인터페이스 작동
 * - onInitialize() 호출
 * - EventBus 구독/이벤트 처리
 */
public class TestModA implements PulseMod {

    private static final String MOD_ID = "test_mod_a";
    private int tickCount = 0;

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "═══════════════════════════════════════");
        Pulse.log(MOD_ID, "Test Mod A - onInitialize() called!");
        Pulse.log(MOD_ID, "═══════════════════════════════════════");

        // 이벤트 리스너 등록
        registerEventListeners();

        Pulse.log(MOD_ID, "Test Mod A initialized successfully!");
    }

    private void registerEventListeners() {
        Pulse.log(MOD_ID, "Registering event listeners...");

        // 게임 틱 이벤트 구독
        EventBus.subscribe(GameTickEvent.class, this::onGameTick);

        Pulse.log(MOD_ID, "Event listeners registered!");
    }

    private void onGameTick(GameTickEvent event) {
        tickCount++;

        // 매 1000틱마다 로그 출력 (약 50초)
        if (tickCount % 1000 == 0) {
            Pulse.log(MOD_ID, "Tick count: " + tickCount + " (Event handling works!)");
        }
    }

    @Override
    public void onWorldLoad() {
        Pulse.log(MOD_ID, "World loaded! Test Mod A is active.");
    }

    @Override
    public void onUnload() {
        Pulse.log(MOD_ID, "Test Mod A unloading...");
        Pulse.log(MOD_ID, "Total ticks processed: " + tickCount);
    }
}
