package com.pulse.api;

import com.pulse.diagnostics.HotspotMap;
import com.pulse.diagnostics.PulseThreadGuard;
import com.pulse.diagnostics.PulseTickContext;
import com.pulse.mixin.PulseErrorHandler;

import java.util.List;
import java.util.Map;

/**
 * Pulse 진단 API.
 * 
 * 외부 모드에서 Pulse의 진단 정보에 접근할 수 있도록 하는 Facade입니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 현재 틱 컨텍스트
 * int zombies = PulseDiagnostics.getZombieUpdateCount();
 * boolean mp = PulseDiagnostics.isMultiplayer();
 * 
 * // 핫스팟 분석
 * var hotspots = PulseDiagnostics.getTopHotspots(10);
 * 
 * // Mixin 오류 조회
 * int errors = PulseDiagnostics.getMixinErrorCount();
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseDiagnostics {

    private PulseDiagnostics() {
    }

    // ─────────────────────────────────────────────────────────────
    // Tick Context
    // ─────────────────────────────────────────────────────────────

    /**
     * 현재 틱 번호
     */
    public static long getCurrentTick() {
        return PulseTickContext.get().getCurrentTick();
    }

    /**
     * 멀티플레이어 여부
     */
    public static boolean isMultiplayer() {
        return PulseTickContext.get().isMultiplayer();
    }

    /**
     * 이번 틱의 좀비 업데이트 수
     */
    public static int getZombieUpdateCount() {
        return PulseTickContext.get().getZombieUpdateCount();
    }

    /**
     * 이번 틱의 청크 로드 수
     */
    public static int getChunkLoadCount() {
        return PulseTickContext.get().getChunkLoadCount();
    }

    /**
     * 이번 틱의 청크 언로드 수
     */
    public static int getChunkUnloadCount() {
        return PulseTickContext.get().getChunkUnloadCount();
    }

    /**
     * 현재 플레이어 수 (MP)
     */
    public static int getPlayerCount() {
        return PulseTickContext.get().getPlayerCount();
    }

    /**
     * 이번 틱의 차량 업데이트 수
     */
    public static int getVehicleUpdateCount() {
        return PulseTickContext.get().getVehicleUpdateCount();
    }

    /**
     * 틱 컨텍스트 스냅샷
     */
    public static String getTickSnapshot() {
        return PulseTickContext.get().getSnapshot();
    }

    // ─────────────────────────────────────────────────────────────
    // Thread Guard
    // ─────────────────────────────────────────────────────────────

    /**
     * 현재 메인 게임 스레드 여부
     */
    public static boolean isMainThread() {
        return PulseThreadGuard.isMainThread();
    }

    /**
     * 메인 스레드 아닌 경우 경고
     */
    public static void assertMainThread(String context) {
        PulseThreadGuard.assertMainThread(context);
    }

    // ─────────────────────────────────────────────────────────────
    // Hotspot Map
    // ─────────────────────────────────────────────────────────────

    /**
     * 함수 실행 시간 기록
     */
    public static void recordTiming(String function, long nanos) {
        HotspotMap.record(function, nanos);
    }

    /**
     * 상위 N개 핫스팟 조회
     */
    public static List<HotspotMap.HotspotEntry> getTopHotspots(int n) {
        return HotspotMap.getTopHotspots(n);
    }

    /**
     * 모든 핫스팟 통계
     */
    public static Map<String, HotspotMap.TimingStats> getAllHotspots() {
        return HotspotMap.getAll();
    }

    /**
     * 핫스팟 통계 초기화
     */
    public static void resetHotspots() {
        HotspotMap.reset();
    }

    // ─────────────────────────────────────────────────────────────
    // Mixin Errors
    // ─────────────────────────────────────────────────────────────

    /**
     * Mixin 오류 총 개수
     */
    public static int getMixinErrorCount() {
        return PulseErrorHandler.getTotalErrorCount();
    }

    /**
     * Mixin별 오류 개수
     */
    public static Map<String, Integer> getMixinErrorCounts() {
        return PulseErrorHandler.getErrorCounts();
    }

    /**
     * 최근 Mixin 오류 목록
     */
    public static List<PulseErrorHandler.MixinError> getRecentMixinErrors() {
        return PulseErrorHandler.getRecentErrors();
    }

    /**
     * Mixin 오류 기록 초기화
     */
    public static void clearMixinErrors() {
        PulseErrorHandler.clearErrors();
    }
}
