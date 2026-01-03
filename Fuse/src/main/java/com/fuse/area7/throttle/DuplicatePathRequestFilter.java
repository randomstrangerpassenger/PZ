package com.fuse.area7.throttle;

import java.util.HashMap;
import java.util.Map;

/**
 * 동일 틱 중복 경로탐색 요청 필터.
 * 
 * <p>
 * 2/3 모델 강한 합의: 동일 틱 내 중복 요청 제거.
 * </p>
 * 
 * <h2>매커니즘</h2>
 * <ul>
 * <li>키 = (zombie_id, target_x, target_y, tick)</li>
 * <li>동일 키로 재요청 시 첫 결과 재사용</li>
 * <li>틱 종료 시 맵 클리어</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class DuplicatePathRequestFilter {

    private final Map<Long, Boolean> processedRequests = new HashMap<>();
    private long currentTick = -1;
    private boolean stricterMatching = false;

    // 텔레메트리
    private int duplicatesFiltered;

    /**
     * 틱 시작 시 호출.
     */
    public void onTickStart(long gameTick) {
        if (gameTick != currentTick) {
            processedRequests.clear();
            currentTick = gameTick;
        }
    }

    /**
     * 중복 요청인지 확인.
     * 
     * @param zombieId 좀비 ID
     * @param targetX  목표 X
     * @param targetY  목표 Y
     * @return true = 이미 처리됨 (중복), false = 새 요청
     */
    public boolean isDuplicate(int zombieId, float targetX, float targetY) {
        long key = computeKey(zombieId, targetX, targetY);

        if (processedRequests.containsKey(key)) {
            duplicatesFiltered++;
            return true;
        }

        processedRequests.put(key, Boolean.TRUE);
        return false;
    }

    /**
     * 요청 키 계산.
     * 
     * Strict 모드: 정확한 좌표 매칭
     * 일반 모드: 타일 단위 반올림
     */
    private long computeKey(int zombieId, float targetX, float targetY) {
        int x, y;
        if (stricterMatching) {
            // 소수점 1자리까지 고려
            x = (int) (targetX * 10);
            y = (int) (targetY * 10);
        } else {
            // 타일 단위 반올림
            x = Math.round(targetX);
            y = Math.round(targetY);
        }

        // zombieId (20비트) + x (22비트) + y (22비트) = 64비트
        return ((long) zombieId << 44) | ((long) (x & 0x3FFFFF) << 22) | (y & 0x3FFFFF);
    }

    /**
     * Stricter 매칭 모드 설정 (PanicProtocol에서 호출).
     */
    public void setStricterMatching(boolean stricter) {
        this.stricterMatching = stricter;
    }

    /**
     * 틱 종료 시 호출.
     */
    public void onTickEnd() {
        processedRequests.clear();
    }

    // ═══════════════════════════════════════════════════════════════
    // 텔레메트리
    // ═══════════════════════════════════════════════════════════════

    public int getDuplicatesFiltered() {
        return duplicatesFiltered;
    }

    public int getMapSize() {
        return processedRequests.size();
    }

    public void resetTelemetry() {
        duplicatesFiltered = 0;
    }
}
