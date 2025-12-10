package com.pulse.test.b.mixin;

import com.pulse.test.b.TestModB;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Test Mixin - Phase 1 검증용 간단한 Mixin
 * 
 * 이 Mixin은 Object 클래스의 toString()을 타겟으로 합니다.
 * 실제 게임에서는 zombie.* 클래스를 타겟으로 해야 합니다.
 * 
 * 이 예제는 Mixin 시스템 동작 확인용입니다.
 */
@Mixin(Object.class)
public class TestMixin {

    /**
     * 정적 초기화 블록에서 Mixin 적용 알림
     * Mixin 클래스가 로드되면 실행됨
     */
    static {
        try {
            TestModB.onMixinApplied("java.lang.Object");
        } catch (Throwable t) {
            // TestModB가 아직 로드되지 않았을 수 있음
            System.out.println("[TestMixin] Mixin class loaded (TestModB not ready yet)");
        }
    }

    // Note: 실제로 Object.toString()에 Inject하면 성능 영향이 있으므로
    // 이 예제에서는 static 블록으로 로딩만 확인합니다.
    // 실제 모드에서는 게임 클래스를 타겟으로 해야 합니다.
}
