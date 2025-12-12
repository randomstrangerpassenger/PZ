package com.pulse.api.access;

import com.pulse.api.GameAccess;
import com.pulse.api.util.ReflectionClassCache;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

/**
 * 좀비 관련 접근 API.
 * GameAccess에서 분리된 좀비 전용 유틸리티.
 * 
 * @since 1.1.0
 * @see GameAccess
 */
public final class ZombieAccess {

    private ZombieAccess() {
    }

    private static final ReflectionClassCache<Object> isoWorldCache = new ReflectionClassCache<>("zombie.iso.IsoWorld");

    public static void refresh() {
        isoWorldCache.refresh();
    }

    /**
     * 특정 위치 주변의 좀비 목록 가져오기
     */
    public static List<Object> getNearbyZombies(float x, float y, float radius) {
        List<Object> result = new ArrayList<>();

        try {
            Object world = WorldAccess.getIsoWorldInstance();
            if (world == null)
                return result;

            Class<?> isoWorldClass = isoWorldCache.get();
            if (isoWorldClass == null)
                return result;

            Method getCellMethod = isoWorldClass.getMethod("getCell");
            Object cell = getCellMethod.invoke(world);
            if (cell == null)
                return result;

            Method getZombieListMethod = cell.getClass().getMethod("getZombieList");
            Object zombieList = getZombieListMethod.invoke(cell);

            if (zombieList instanceof List<?> list) {
                for (Object zombie : list) {
                    if (zombie == null)
                        continue;
                    try {
                        Method getX = zombie.getClass().getMethod("getX");
                        Method getY = zombie.getClass().getMethod("getY");
                        float zx = ((Number) getX.invoke(zombie)).floatValue();
                        float zy = ((Number) getY.invoke(zombie)).floatValue();

                        float dx = zx - x;
                        float dy = zy - y;
                        if (dx * dx + dy * dy <= radius * radius) {
                            result.add(zombie);
                        }
                    } catch (Exception e) {
                        // 개별 좀비 처리 실패 무시
                    }
                }
            }
        } catch (Exception e) {
            // 무시
        }

        return result;
    }

    /**
     * 현재 셀의 모든 좀비 목록 가져오기
     */
    public static List<Object> getAllZombies() {
        List<Object> result = new ArrayList<>();

        try {
            Object world = WorldAccess.getIsoWorldInstance();
            if (world == null)
                return result;

            Class<?> isoWorldClass = isoWorldCache.get();
            if (isoWorldClass == null)
                return result;

            Method getCellMethod = isoWorldClass.getMethod("getCell");
            Object cell = getCellMethod.invoke(world);
            if (cell == null)
                return result;

            Method getZombieListMethod = cell.getClass().getMethod("getZombieList");
            Object zombieList = getZombieListMethod.invoke(cell);

            if (zombieList instanceof List<?> list) {
                for (Object zombie : list) {
                    if (zombie != null) {
                        result.add(zombie);
                    }
                }
            }
        } catch (Exception e) {
            // 무시
        }

        return result;
    }
}
