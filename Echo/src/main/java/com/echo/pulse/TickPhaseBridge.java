package com.echo.pulse;

import com.echo.measure.TickPhaseProfiler;
import com.echo.validation.PulseContractVerifier;
import com.echo.validation.SelfValidation;
import com.pulse.api.profiler.TickPhaseHook;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * TickPhase Pulse 연동
 * 
 * Echo 초기화 시 Pulse의 TickPhaseHook에 콜백을 등록하여
 * Pulse Mixin에서 TickPhaseProfiler를 호출할 수 있게 합니다.
 * 
 * v0.9: Pulse predefined phase 상수를 Echo TickPhase로 자동 매핑
 * v0.9: Phase mismatch 감지 시 품질 점수 페널티
 * 
 * @since Echo 1.0
 */
public class TickPhaseBridge implements TickPhaseHook.ITickPhaseCallback {

    private static TickPhaseBridge INSTANCE;

    // v0.9: Phase mismatch 품질 페널티 추적
    private static final AtomicInteger phaseMismatchCount = new AtomicInteger(0);
    private static final int QUALITY_PENALTY_PER_MISMATCH = 5; // 품질 점수 5점 감점
    private static final int MAX_PENALTY = 50; // 최대 50점 감점

    // v0.9: Pulse phase 상수 → Echo TickPhase 매핑
    private static final Map<String, TickPhaseProfiler.TickPhase> PHASE_MAPPING = new HashMap<>();

    static {
        // Pulse predefined phases → Echo TickPhase 매핑
        PHASE_MAPPING.put(TickPhaseHook.PHASE_WORLD_UPDATE, TickPhaseProfiler.TickPhase.WORLD_UPDATE);
        PHASE_MAPPING.put(TickPhaseHook.PHASE_AI_UPDATE, TickPhaseProfiler.TickPhase.AI_PHASE);
        PHASE_MAPPING.put(TickPhaseHook.PHASE_PHYSICS_UPDATE, TickPhaseProfiler.TickPhase.PHYSICS_PHASE);
        PHASE_MAPPING.put(TickPhaseHook.PHASE_ZOMBIE_UPDATE, TickPhaseProfiler.TickPhase.AI_PHASE); // Zombie = AI
                                                                                                    // category
        PHASE_MAPPING.put(TickPhaseHook.PHASE_PLAYER_UPDATE, TickPhaseProfiler.TickPhase.AI_PHASE); // Player = AI
                                                                                                    // category
        PHASE_MAPPING.put(TickPhaseHook.PHASE_RENDER_PREP, TickPhaseProfiler.TickPhase.RENDERING_PREP);
        PHASE_MAPPING.put(TickPhaseHook.PHASE_ISOGRID_UPDATE, TickPhaseProfiler.TickPhase.ISO_GRID_UPDATE);

        // Legacy 매핑 (Echo 자체 호출용)
        PHASE_MAPPING.put("WORLD_UPDATE", TickPhaseProfiler.TickPhase.WORLD_UPDATE);
        PHASE_MAPPING.put("AI_PHASE", TickPhaseProfiler.TickPhase.AI_PHASE);
        PHASE_MAPPING.put("PHYSICS_PHASE", TickPhaseProfiler.TickPhase.PHYSICS_PHASE);
        PHASE_MAPPING.put("RENDERING_PREP", TickPhaseProfiler.TickPhase.RENDERING_PREP);
        PHASE_MAPPING.put("ISO_GRID_UPDATE", TickPhaseProfiler.TickPhase.ISO_GRID_UPDATE);
    }

    private TickPhaseBridge() {
    }

    /**
     * TickPhase 브릿지 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (INSTANCE != null) {
            return;
        }
        INSTANCE = new TickPhaseBridge();
        TickPhaseHook.setCallback(INSTANCE);
        System.out.println("[Echo] TickPhaseBridge registered with Pulse (v0.9 mapping enabled)");
    }

    /**
     * TickPhase 브릿지 해제
     */
    public static void unregister() {
        TickPhaseHook.clearCallback();
        INSTANCE = null;
    }

    @Override
    public long startPhase(String phase) {
        TickPhaseProfiler.TickPhase tickPhase = parsePhase(phase);
        if (tickPhase != null) {
            // v0.9: Pulse에서 이미 phase sequence 검증을 수행하므로
            // 여기서는 Echo ContractVerifier에 알림만 전달
            PulseContractVerifier.getInstance().onPhaseStart(tickPhase);

            // v0.9: SelfValidation heartbeat
            SelfValidation.getInstance().phaseStartHeartbeat();

            return TickPhaseProfiler.getInstance().startPhaseRaw(tickPhase);
        }

        // Unknown phase - 경미한 경고만 (품질에 영향 없음)
        return -1;
    }

    @Override
    public void endPhase(String phase, long startTime) {
        if (startTime < 0)
            return;
        TickPhaseProfiler.TickPhase tickPhase = parsePhase(phase);
        if (tickPhase != null) {
            // v0.9: Phase 순서 검증은 Pulse TickPhaseHook에서 수행
            // Echo는 결과만 기록
            PulseContractVerifier.getInstance().onPhaseEnd(tickPhase);

            // v0.9: SelfValidation heartbeat
            SelfValidation.getInstance().phaseEndHeartbeat();

            TickPhaseProfiler.getInstance().endPhaseRaw(tickPhase, startTime);
        }
    }

    @Override
    public void onTickComplete() {
        // v0.9: Pulse TickPhaseHook에서 phase sequence 에러가 발생했는지 확인
        int pulsePhaseErrors = TickPhaseHook.getPhaseErrorCount();
        if (pulsePhaseErrors > 0 && phaseMismatchCount.get() < pulsePhaseErrors) {
            // 새로운 에러 발생
            phaseMismatchCount.set(pulsePhaseErrors);
        }

        // v2.0: Lua 경로 히트 프로브 (30초 후 1회 검증)
        com.echo.lua.LuaPathHitBridge probe = com.echo.lua.LuaPathHitBridge.getInstance();
        if (probe != null) {
            probe.onTick();
        }

        TickPhaseProfiler.getInstance().onTickComplete();
    }

    /**
     * Pulse phase 문자열을 Echo TickPhase enum으로 변환
     * v0.9: 매핑 테이블 사용, enum.valueOf() 폴백
     */
    private TickPhaseProfiler.TickPhase parsePhase(String phase) {
        if (phase == null)
            return null;

        // 매핑 테이블에서 먼저 검색
        TickPhaseProfiler.TickPhase mapped = PHASE_MAPPING.get(phase);
        if (mapped != null) {
            return mapped;
        }

        // 폴백: enum 직접 매칭 시도
        try {
            return TickPhaseProfiler.TickPhase.valueOf(phase);
        } catch (IllegalArgumentException e) {
            // Unknown phase - 무시 (디버그 로그용)
            return null;
        }
    }

    /**
     * 등록된 매핑 수 반환 (디버그용)
     */
    public static int getMappingCount() {
        return PHASE_MAPPING.size();
    }

    // ═══════════════════════════════════════════════════════════════
    // v0.9: 품질 점수 페널티 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * Phase mismatch로 인한 품질 점수 페널티 반환
     * 
     * @return 0-50 범위의 품질 감점
     */
    public static int getQualityPenalty() {
        int penalty = phaseMismatchCount.get() * QUALITY_PENALTY_PER_MISMATCH;
        return Math.min(penalty, MAX_PENALTY);
    }

    /**
     * Phase mismatch 카운트 반환
     */
    public static int getPhaseMismatchCount() {
        return phaseMismatchCount.get();
    }

    /**
     * 상태 리셋 (세션 리셋 시)
     */
    public static void reset() {
        phaseMismatchCount.set(0);
    }
}
