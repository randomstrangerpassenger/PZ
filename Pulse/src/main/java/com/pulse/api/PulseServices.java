package com.pulse.api;

import com.pulse.event.EventBus;
import com.pulse.handler.KahluaCallExtractor;
import com.pulse.handler.WorldTickHandler;
import com.pulse.lifecycle.LifecycleManager;
import com.pulse.scheduler.PulseScheduler;

/**
 * Pulse 핵심 서비스에 대한 타입 안전한 파사드.
 * 
 * <p>
 * 직접 getInstance() 호출 대신 이 클래스를 통해 서비스에 접근합니다.
 * IDE 자동완성 지원, 타입 안전성, 내부 구현 캡슐화를 제공합니다.
 * </p>
 * 
 * <h3>사용 예시:</h3>
 * 
 * <pre>
 * // Before
 * EventBus.getInstance().post(event);
 * PulseScheduler.getInstance().tick();
 * 
 * // After
 * PulseServices.eventBus().post(event);
 * PulseServices.scheduler().tick();
 * </pre>
 * 
 * <h3>테스트 시:</h3>
 * 
 * <pre>
 * // PulseServiceLocator에 Mock 등록
 * PulseServiceLocator.getInstance().registerService(EventBus.class, mockEventBus);
 * 
 * // PulseServices.eventBus()가 mockEventBus 반환
 * </pre>
 * 
 * @since Pulse 1.6
 */
public final class PulseServices {

    private PulseServices() {
        // Utility class
    }

    // ═══════════════════════════════════════════════════════════════
    // Core Services
    // ═══════════════════════════════════════════════════════════════

    /**
     * 이벤트 버스 접근.
     * 
     * @return EventBus 싱글톤 인스턴스
     */
    public static EventBus eventBus() {
        return EventBus.getInstance();
    }

    /**
     * 스케줄러 접근.
     * 
     * @return PulseScheduler 싱글톤 인스턴스
     */
    public static PulseScheduler scheduler() {
        return PulseScheduler.getInstance();
    }

    /**
     * 라이프사이클 매니저 접근.
     * 
     * @return LifecycleManager 싱글톤 인스턴스
     */
    public static LifecycleManager lifecycle() {
        return LifecycleManager.getInstance();
    }

    // ═══════════════════════════════════════════════════════════════
    // Handler Services (Phase 4)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Kahlua 호출 추출기 접근.
     * 
     * @return KahluaCallExtractor 싱글톤 인스턴스
     */
    public static KahluaCallExtractor kahluaExtractor() {
        return KahluaCallExtractor.getInstance();
    }

    /**
     * 월드 틱 핸들러 접근.
     * 
     * @return WorldTickHandler 싱글톤 인스턴스
     */
    public static WorldTickHandler worldTick() {
        return WorldTickHandler.getInstance();
    }
}
