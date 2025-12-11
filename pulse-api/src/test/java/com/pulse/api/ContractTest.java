package com.pulse.api;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Pulse API Contract Tests.
 * 
 * Echo가 Pulse에 기대하는 계약을 테스트합니다.
 * 이 테스트가 깨지면 Echo 호환성이 영향받을 수 있습니다.
 * 
 * Note: pulse-api 인터페이스만 테스트합니다.
 * Pulse 구현체 테스트는 Pulse 모듈에서 수행합니다.
 * 
 * @since 1.0.1
 */
public class ContractTest {

    /**
     * IPulseMetrics 인터페이스에 Echo가 필요로 하는 메서드가 존재하는지 확인
     */
    @Test
    void ipulseMetricsHasRequiredMethods() {
        Set<String> methodNames = Arrays.stream(IPulseMetrics.class.getMethods())
                .map(Method::getName)
                .collect(Collectors.toSet());

        // Echo가 기대하는 필수 메서드
        assertTrue(methodNames.contains("getFps"), "getFps() required by Echo");
        assertTrue(methodNames.contains("getTickTimeMs"), "getTickTimeMs() required by Echo");
        assertTrue(methodNames.contains("getFrameTimeMs"), "getFrameTimeMs() required by Echo");
    }

    /**
     * IPulseEvent 인터페이스의 기본 계약이 유지되는지 확인 (안정성)
     */
    @Test
    void ipulseEventHasExpectedMethods() {
        Set<String> methodNames = Arrays.stream(IPulseEvent.class.getDeclaredMethods())
                .map(Method::getName)
                .collect(Collectors.toSet());

        // IPulseEvent 필수 메서드
        assertTrue(methodNames.contains("getEventName"), "getEventName() required");
        assertTrue(methodNames.contains("isCancellable"), "isCancellable() required");
        assertTrue(methodNames.contains("isCancelled"), "isCancelled() required");
        assertTrue(methodNames.contains("cancel"), "cancel() required");
    }

    /**
     * IPulse 인터페이스에 필수 메서드가 존재하는지 확인
     */
    @Test
    void ipulseHasRequiredMethods() {
        Set<String> methodNames = Arrays.stream(IPulse.class.getMethods())
                .map(Method::getName)
                .collect(Collectors.toSet());

        assertTrue(methodNames.contains("getVersion"), "getVersion() required");
        assertTrue(methodNames.contains("isModLoaded"), "isModLoaded() required");
        assertTrue(methodNames.contains("isInitialized"), "isInitialized() required");
    }

    /**
     * FailsoftPolicy가 예상된 액션을 가지고 있는지 확인
     */
    @Test
    void failsoftPolicyHasRequiredActions() {
        // FailsoftPolicy.Action enum 존재 확인
        FailsoftPolicy.Action[] actions = FailsoftPolicy.Action.values();
        assertTrue(actions.length >= 3, "FailsoftPolicy should have at least 3 actions");

        Set<String> actionNames = Arrays.stream(actions)
                .map(Enum::name)
                .collect(Collectors.toSet());

        assertTrue(actionNames.contains("WARNING"), "WARNING action required");
        assertTrue(actionNames.contains("CRITICAL"), "CRITICAL action required");
        assertTrue(actionNames.contains("TICK_CONTRACT_VIOLATION"), "TICK_CONTRACT_VIOLATION action required");
    }
}
