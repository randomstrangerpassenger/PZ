package com.pulse.api.optimization;

import com.pulse.api.PublicAPI;
import java.util.Optional;

/**
 * 최적화 지점 정의.
 * 각 포인트는 Mixin 타깃 클래스와 Echo 프로파일러 라벨 prefix와 연결됩니다.
 * 
 * <p>
 * Tier 1 (Base): 핵심 병목 영역 - 7개
 * </p>
 * <p>
 * Tier 2 (Platform Extension): Pulse 생태계 확장용 - 3개
 * </p>
 * 
 * <pre>
 * // 사용 예시
 * OptimizationPoint point = OptimizationPoint.ZOMBIE_AI_UPDATE;
 * String target = point.getMixinTarget(); // "zombie.ai.ZombieAI"
 * String prefix = point.getEchoPrefix(); // "zombie.ai"
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public enum OptimizationPoint {

    // ═══════════════════════════════════════════════════════════════
    // Tier 1: Base - 핵심 병목 영역 (7개)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 메인 게임 틱 루프.
     * 전체 프레임 시간의 병목점을 파악하는 데 사용.
     */
    TICK_LOOP("zombie.gameStates.IngameState", "update", "tick", 1),

    /**
     * 좀비 AI 업데이트.
     * AI 경로 탐색 및 상태 머신 처리.
     */
    ZOMBIE_AI_UPDATE("zombie.ai.ZombieAI", "update", "zombie.ai", 1),

    /**
     * 청크 스트리밍.
     * 월드 청크 로드/언로드 처리.
     */
    CHUNK_STREAMING("zombie.iso.IsoChunkGrid", "loadChunk", "chunk", 1),

    /**
     * Lua 이벤트 시스템.
     * Lua 모드의 이벤트 핸들러 호출.
     */
    LUA_EVENT("zombie.Lua.LuaEventManager", "triggerEvent", "lua.event", 1),

    /**
     * 네트워크 패킷 처리.
     * 클라이언트-서버 통신.
     */
    NETWORK_PACKET("zombie.network.GameClient", "processPacket", "network", 1),

    /**
     * 경로 탐색.
     * A* 알고리즘 기반 경로 계산.
     */
    PATHFINDING("zombie.ai.astar.AStarPathFinder", "findPath", "pathfind", 1),

    /**
     * 메인 렌더링.
     * 화면 렌더링 파이프라인.
     */
    RENDER_MAIN("zombie.core.Core", "render", "render", 1),

    // ═══════════════════════════════════════════════════════════════
    // Tier 2: Platform Extension - Pulse 생태계 확장 (3개)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 인벤토리 업데이트.
     * 컨테이너, 아이템 정렬/스캔/트랜잭션 처리.
     * 멀티플레이어에서 병목이 자주 발생하는 영역.
     */
    INVENTORY_UPDATE("zombie.inventory.InventoryContainer", "update", "inventory", 2),

    /**
     * 차량 업데이트.
     * 차량 물리 연산, 충돌 처리, tick-based update.
     */
    VEHICLE_UPDATE("zombie.vehicles.BaseVehicle", "update", "vehicle", 2),

    /**
     * 애니메이션 업데이트.
     * 모델 업데이트, 스킨, 애니메이션 처리.
     */
    ANIMATION_UPDATE("zombie.core.skinnedmodel.ModelManager", "updateAnimation", "animation", 2);

    // ═══════════════════════════════════════════════════════════════
    // 필드 및 메서드
    // ═══════════════════════════════════════════════════════════════

    private final String mixinTarget;
    private final String targetMethod;
    private final String echoPrefix;
    private final int tier;

    OptimizationPoint(String mixinTarget, String targetMethod, String echoPrefix, int tier) {
        this.mixinTarget = mixinTarget;
        this.targetMethod = targetMethod;
        this.echoPrefix = echoPrefix;
        this.tier = tier;
    }

    /**
     * Mixin 대상 클래스의 전체 경로 반환.
     * 
     * @return Mixin 대상 클래스 (예: "zombie.ai.ZombieAI")
     */
    public String getMixinTarget() {
        return mixinTarget;
    }

    /**
     * Mixin 대상 메서드 이름 반환.
     * 
     * @return 대상 메서드명 (예: "update")
     */
    public String getTargetMethod() {
        return targetMethod;
    }

    /**
     * Echo 프로파일러 라벨 prefix 반환.
     * 
     * @return Echo 라벨 prefix (예: "zombie.ai")
     */
    public String getEchoPrefix() {
        return echoPrefix;
    }

    /**
     * Tier 레벨 반환.
     * 
     * @return 1 = Base, 2 = Platform Extension
     */
    public int getTier() {
        return tier;
    }

    /**
     * Echo 프로파일러용 전체 라벨 반환.
     * prefix + "." + targetMethod 형식.
     * 
     * @return 전체 Echo 라벨 (예: "zombie.ai.update")
     */
    public String getEchoLabel() {
        return echoPrefix + "." + targetMethod;
    }

    /**
     * Echo 라벨 생성 헬퍼 (커스텀 suffix 사용).
     * 
     * @param suffix 라벨 suffix (예: "start", "end")
     * @return 전체 라벨 (예: "zombie.ai.start")
     */
    public String createEchoLabel(String suffix) {
        return echoPrefix + "." + suffix;
    }

    /**
     * ID로 OptimizationPoint 찾기.
     * 
     * @param id enum 이름 (예: "ZOMBIE_AI_UPDATE")
     * @return Optional containing the point, or empty if not found
     */
    public static Optional<OptimizationPoint> byId(String id) {
        try {
            return Optional.of(valueOf(id.toUpperCase()));
        } catch (IllegalArgumentException e) {
            return Optional.empty();
        }
    }

    /**
     * Mixin 타깃으로 OptimizationPoint 찾기.
     * 
     * @param mixinTarget Mixin 대상 클래스 전체 경로
     * @return Optional containing the point, or empty if not found
     */
    public static Optional<OptimizationPoint> byMixinTarget(String mixinTarget) {
        for (OptimizationPoint point : values()) {
            if (point.mixinTarget.equals(mixinTarget)) {
                return Optional.of(point);
            }
        }
        return Optional.empty();
    }

    /**
     * Echo prefix로 OptimizationPoint 찾기.
     * 
     * @param prefix Echo 라벨 prefix
     * @return Optional containing the point, or empty if not found
     */
    public static Optional<OptimizationPoint> byEchoPrefix(String prefix) {
        for (OptimizationPoint point : values()) {
            if (point.echoPrefix.equals(prefix)) {
                return Optional.of(point);
            }
        }
        return Optional.empty();
    }
}
