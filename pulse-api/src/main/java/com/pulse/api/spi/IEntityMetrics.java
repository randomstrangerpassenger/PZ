package com.pulse.api.spi;

/**
 * 엔티티 메트릭 인터페이스.
 * 
 * Phase 2.3: 엔티티 타입별 카운터를 제공합니다.
 * Echo에서 구현하여 Pulse에 등록하면 상관관계 분석에 활용됩니다.
 * 
 * @since 1.0.1
 */
public interface IEntityMetrics {

    /**
     * 현재 좀비 수
     */
    int getZombieCount();

    /**
     * 현재 생존자 NPC 수
     */
    int getNpcCount();

    /**
     * 현재 동물 수
     */
    int getAnimalCount();

    /**
     * 현재 차량 수
     */
    int getVehicleCount();

    /**
     * 월드에 놓인 아이템 수
     */
    int getWorldItemCount();

    /**
     * 로드된 셀(청크) 수
     */
    int getLoadedCellCount();

    /**
     * 총 엔티티 수 (좀비 + NPC + 동물)
     */
    default int getTotalEntityCount() {
        return getZombieCount() + getNpcCount() + getAnimalCount();
    }

    /**
     * 엔티티 밀도 (셀당 평균 엔티티 수)
     */
    default double getEntityDensity() {
        int cells = getLoadedCellCount();
        if (cells == 0)
            return 0;
        return (double) getTotalEntityCount() / cells;
    }

    /**
     * 빠른 엔티티 요약 맵
     */
    default java.util.Map<String, Integer> getEntitySummary() {
        java.util.Map<String, Integer> map = new java.util.LinkedHashMap<>();
        map.put("zombies", getZombieCount());
        map.put("npcs", getNpcCount());
        map.put("animals", getAnimalCount());
        map.put("vehicles", getVehicleCount());
        map.put("world_items", getWorldItemCount());
        map.put("cells", getLoadedCellCount());
        return map;
    }
}
