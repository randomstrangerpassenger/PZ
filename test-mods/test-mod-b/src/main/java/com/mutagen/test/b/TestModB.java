package com.pulse.test.b;

import com.pulse.api.Pulse;
import com.pulse.mod.PulseMod;

/**
 * Test Mod B - Phase 1 검증용 Mixin 테스트 모드
 * 
 * 테스트 항목:
 * - PulseMod 인터페이스 작동
 * - 외부 Mixin 설정 로딩
 * - Mixin 적용 확인
 */
public class TestModB implements PulseMod {

    private static final String MOD_ID = "test_mod_b";
    private static boolean mixinApplied = false;

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "═══════════════════════════════════════");
        Pulse.log(MOD_ID, "Test Mod B - onInitialize() called!");
        Pulse.log(MOD_ID, "═══════════════════════════════════════");

        // Mixin 적용 확인
        if (mixinApplied) {
            Pulse.log(MOD_ID, "✓ Mixin was applied successfully!");
        } else {
            Pulse.log(MOD_ID, "⚠ Mixin not yet applied (might be applied after class loads)");
        }

        Pulse.log(MOD_ID, "Test Mod B initialized successfully!");
    }

    /**
     * Mixin에서 호출하는 콜백 메서드
     */
    public static void onMixinApplied(String targetClass) {
        mixinApplied = true;
        Pulse.log("test_mod_b", "Mixin successfully applied to: " + targetClass);
    }

    @Override
    public void onUnload() {
        Pulse.log(MOD_ID, "Test Mod B unloading...");
        Pulse.log(MOD_ID, "Mixin was applied: " + mixinApplied);
    }
}
