package com.pulse.api.access;

import com.pulse.api.GameAccess;
import com.pulse.api.util.ReflectionClassCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * 월드 관련 접근 API.
 * GameAccess에서 분리된 월드 전용 유틸리티.
 * 
 * @since 1.1.0
 * @see GameAccess
 */
public final class WorldAccess {

    private WorldAccess() {
    }

    // ReflectionClassCache 사용으로 ensureInitialized() 패턴 제거
    private static final ReflectionClassCache<Object> isoWorldCache = new ReflectionClassCache<>("zombie.iso.IsoWorld");

    /**
     * 클래스 참조 갱신.
     */
    public static void refresh() {
        isoWorldCache.refresh();
    }

    /**
     * IsoWorld 인스턴스 가져오기.
     */
    public static Object getIsoWorldInstance() {
        Class<?> isoWorldClass = isoWorldCache.get();
        if (isoWorldClass == null)
            return null;

        try {
            Field instanceField = isoWorldClass.getDeclaredField("instance");
            instanceField.setAccessible(true);
            return instanceField.get(null);
        } catch (Exception e) {
            try {
                Method getInstance = isoWorldClass.getMethod("getInstance");
                return getInstance.invoke(null);
            } catch (Exception e2) {
                return null;
            }
        }
    }

    /**
     * 현재 월드가 로드되었는지 확인.
     */
    public static boolean isWorldLoaded() {
        return getIsoWorldInstance() != null;
    }

    /**
     * 현재 월드 이름.
     */
    public static String getWorldName() {
        Object world = getIsoWorldInstance();
        if (world == null)
            return "";

        Class<?> isoWorldClass = isoWorldCache.get();
        if (isoWorldClass == null)
            return "";

        try {
            Method getWorld = isoWorldClass.getMethod("getWorld");
            Object result = getWorld.invoke(world);
            return result != null ? result.toString() : "";
        } catch (Exception e) {
            return "";
        }
    }

    /**
     * 특정 좌표의 IsoGridSquare 가져오기.
     */
    public static Object getSquare(int x, int y, int z) {
        Object world = getIsoWorldInstance();
        if (world == null)
            return null;

        Class<?> isoWorldClass = isoWorldCache.get();
        if (isoWorldClass == null)
            return null;

        try {
            Object cell = isoWorldClass.getMethod("getCell").invoke(world);
            if (cell == null)
                return null;
            Method getGridSquare = cell.getClass().getMethod("getGridSquare", int.class, int.class, int.class);
            return getGridSquare.invoke(cell, x, y, z);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 현재 IsoCell 가져오기.
     */
    public static Object getCurrentCell() {
        Object world = getIsoWorldInstance();
        if (world == null)
            return null;

        Class<?> isoWorldClass = isoWorldCache.get();
        if (isoWorldClass == null)
            return null;

        try {
            return isoWorldClass.getMethod("getCell").invoke(world);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 로드된 청크(Cell) 개수.
     */
    public static int getLoadedCellCount() {
        Object cell = getCurrentCell();
        if (cell == null)
            return 0;
        try {
            Method getChunkList = cell.getClass().getMethod("getChunkList");
            Object list = getChunkList.invoke(cell);
            if (list instanceof java.util.List<?> l) {
                return l.size();
            }
        } catch (Exception e) {
            // ignore
        }
        return 0;
    }

    /**
     * 전체 엔티티 개수 (좀비 포함).
     */
    public static int getTotalEntityCount() {
        Object cell = getCurrentCell();
        if (cell == null)
            return 0;
        try {
            Method getObjectList = cell.getClass().getMethod("getObjectList");
            Object list = getObjectList.invoke(cell);
            if (list instanceof java.util.List<?> l) {
                return l.size();
            }
        } catch (Exception e) {
            // ignore
        }
        return 0;
    }
}
