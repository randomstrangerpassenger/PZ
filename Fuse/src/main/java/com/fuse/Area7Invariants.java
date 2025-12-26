package com.fuse;

/**
 * Area 7 불변 원칙 (코드 수준 문서화).
 * 
 * <p>
 * <b>이 주석을 삭제하거나 무시하지 말 것.</b>
 * </p>
 * 
 * <p>
 * 이 클래스는 WorldItem & Corpse Governor의 경계를 정의합니다.
 * 모든 최적화는 이 원칙 내에서만 수행되어야 합니다.
 * </p>
 * 
 * <h2>절대 금지 (NEVER)</h2>
 * <ul>
 * <li>아이템/시체 삭제</li>
 * <li>아이템 합치기</li>
 * <li>물리 알고리즘 변경</li>
 * <li>부패 속도 변경</li>
 * <li>상호작용 지연</li>
 * </ul>
 * 
 * <h2>허용 (ALLOWED)</h2>
 * <ul>
 * <li>update() 호출 빈도 조정 (결과 동일, 시간 분산)</li>
 * <li>비가시/원거리 객체 업데이트 주기 감소</li>
 * <li>Sleep 모드 (update 중지, 존재 유지)</li>
 * <li>폭주 감지 시 보수적 모드 전환</li>
 * </ul>
 * 
 * @since Fuse 2.2
 * @see com.fuse.governor.ItemGovernor
 */
public final class Area7Invariants {

    // ═══════════════════════════════════════════════════════════════
    // 절대 금지 (Documentation Constants)
    // ═══════════════════════════════════════════════════════════════

    /** 절대 금지: 아이템/시체 삭제 */
    public static final String NEVER_DELETE = "아이템/시체 삭제 금지";

    /** 절대 금지: 아이템 합치기 */
    public static final String NEVER_MERGE = "아이템 합치기 금지";

    /** 절대 금지: 물리 알고리즘 변경 */
    public static final String NEVER_ALTER_PHYSICS = "물리 알고리즘 변경 금지";

    /** 절대 금지: 부패 속도 변경 */
    public static final String NEVER_ALTER_DECAY = "부패 속도 변경 금지";

    /** 절대 금지: 상호작용 지연 */
    public static final String NEVER_DELAY_INTERACTION = "상호작용 지연 금지";

    // ═══════════════════════════════════════════════════════════════
    // 거리 임계값 (Distance Thresholds)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 즉시 철수 거리 (제곱).
     * 이 거리 내에서는 모든 최적화를 중단하고 정상 모드로 복귀.
     * 기본값: 400 (20타일²)
     */
    public static final float RETREAT_DIST_SQ = 20f * 20f; // 400

    /**
     * 중거리 임계값 (제곱).
     * 이 거리 이상에서는 업데이트 빈도 감소 시작.
     * 기본값: 1600 (40타일²)
     */
    public static final float MEDIUM_DIST_SQ = 40f * 40f; // 1600

    /**
     * 원거리 임계값 (제곱).
     * 이 거리 이상에서는 최소 업데이트 빈도 적용.
     * 기본값: 6400 (80타일²)
     */
    public static final float FAR_DIST_SQ = 80f * 80f; // 6400

    // ═════════════════════════════════════════════════════════════════
    // 폭주 감지 (Burst Detection)
    // ═══════════════════════════════════════════════════════════════

    /**
     * ShellShock 발동 임계값 (초당 아이템 생성 수).
     * 이 값 이상이면 ShellShock 모드 진입.
     * 기본값: 50개/초
     */
    public static final int SHELL_SHOCK_THRESHOLD = 50;

    /**
     * 과부하 임계값 (총 오브젝트 수).
     * 이 값 이상이면 보수적 모드 전환.
     * 기본값: 1000개
     */
    public static final int OVERLOAD_THRESHOLD = 1000;

    // ═══════════════════════════════════════════════════════════════
    // Starvation 방지
    // ═══════════════════════════════════════════════════════════════

    /**
     * 최대 스킵 틱 수.
     * 이 값 이상 update를 스킵한 객체는 강제 실행.
     * 기본값: 120 ticks (2초 @ 60fps)
     */
    public static final int MAX_SKIP_TICKS = 120;

    /**
     * ShellShock 모드 최소 지속 시간 (틱).
     * 발동 후 최소 이 시간 동안 유지.
     * 기본값: 60 ticks (1초)
     */
    public static final int SHELL_SHOCK_MIN_DURATION = 60;

    // ═══════════════════════════════════════════════════════════════
    // Fail-soft
    // ═══════════════════════════════════════════════════════════════

    /**
     * 최대 연속 에러 수.
     * 이 값 이상 연속 에러 발생 시 RETREAT 모드로 전환.
     * 기본값: 5회
     */
    public static final int MAX_CONSECUTIVE_ERRORS = 5;

    /**
     * 레벨 캐시 갱신 주기 (틱).
     * Throttle 레벨을 이 주기마다 재계산.
     * 기본값: 5 ticks (아이템), 10 ticks (시체)
     */
    public static final int LEVEL_CACHE_INTERVAL_ITEM = 5;
    public static final int LEVEL_CACHE_INTERVAL_CORPSE = 10;

    // ═══════════════════════════════════════════════════════════════
    // 샘플링 (WorldObjectSampler)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 월드 오브젝트 샘플링 주기 (틱).
     * 성능 영향 최소화를 위해 1초마다 샘플링.
     * 기본값: 60 ticks (1초 @ 60fps)
     */
    public static final int SAMPLE_INTERVAL = 60;

    /**
     * 근거리 샘플링 거리 (제곱).
     * 기본값: 400 (20타일²)
     */
    public static final float SAMPLE_NEAR_DIST_SQ = 20f * 20f; // 400

    /**
     * 중거리 샘플링 거리 (제곱).
     * 기본값: 1600 (40타일²)
     */
    public static final float SAMPLE_MID_DIST_SQ = 40f * 40f; // 1600

    /**
     * 원거리 샘플링 거리 (제곱).
     * 기본값: 6400 (80타일²)
     */
    public static final float SAMPLE_FAR_DIST_SQ = 80f * 80f; // 6400

    // ═══════════════════════════════════════════════════════════════
    // Private Constructor
    // ═══════════════════════════════════════════════════════════════

    /**
     * Private constructor to prevent instantiation.
     */
    private Area7Invariants() {
        throw new AssertionError("Area7Invariants는 인스턴스화할 수 없습니다.");
    }
}
