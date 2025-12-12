package com.pulse.api.access;

import com.pulse.api.GameAccess;
import com.pulse.api.util.ReflectionClassCache;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * 시간 관련 접근 API.
 * GameAccess에서 분리된 시간 전용 유틸리티.
 * 
 * @since 1.1.0
 * @see GameAccess
 */
public final class TimeAccess {

    private TimeAccess() {
    }

    // ReflectionClassCache 사용으로 ensureInitialized() 패턴 제거
    private static final ReflectionClassCache<Object> gameTimeCache = new ReflectionClassCache<>("zombie.GameTime");

    /**
     * 클래스 참조 갱신.
     */
    public static void refresh() {
        gameTimeCache.refresh();
    }

    /**
     * GameTime 인스턴스 가져오기.
     */
    public static Object getGameTimeInstance() {
        Class<?> gameTimeClass = gameTimeCache.get();
        if (gameTimeClass == null)
            return null;

        try {
            Method getInstance = gameTimeClass.getMethod("getInstance");
            return getInstance.invoke(null);
        } catch (Exception e) {
            try {
                Field instanceField = gameTimeClass.getDeclaredField("instance");
                instanceField.setAccessible(true);
                return instanceField.get(null);
            } catch (Exception e2) {
                return null;
            }
        }
    }

    /**
     * 게임 내 시간 (시).
     */
    public static int getGameHour() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 0;

        Class<?> gameTimeClass = gameTimeCache.get();
        try {
            Method getHour = gameTimeClass.getMethod("getHour");
            Object result = getHour.invoke(gameTime);
            if (result instanceof Number num) {
                return num.intValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 게임 내 분.
     */
    public static int getGameMinute() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 0;

        Class<?> gameTimeClass = gameTimeCache.get();
        try {
            Method getMinutes = gameTimeClass.getMethod("getMinutes");
            Object result = getMinutes.invoke(gameTime);
            if (result instanceof Number num) {
                return num.intValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 게임 내 일수.
     */
    public static int getGameDay() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 1;

        Class<?> gameTimeClass = gameTimeCache.get();
        try {
            Method getDay = gameTimeClass.getMethod("getDay");
            Object result = getDay.invoke(gameTime);
            if (result instanceof Number num) {
                return num.intValue();
            }
        } catch (Exception e) {
            try {
                Method getNights = gameTimeClass.getMethod("getNightsSurvived");
                Object result = getNights.invoke(gameTime);
                if (result instanceof Number num) {
                    return num.intValue() + 1;
                }
            } catch (Exception e2) {
                // 무시
            }
        }
        return 1;
    }

    /**
     * 게임 내 월.
     */
    public static int getGameMonth() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 7;

        Class<?> gameTimeClass = gameTimeCache.get();
        try {
            Method getMonth = gameTimeClass.getMethod("getMonth");
            Object result = getMonth.invoke(gameTime);
            if (result instanceof Number num) {
                return num.intValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 7;
    }

    /**
     * 게임 내 연도.
     */
    public static int getGameYear() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 1993;

        Class<?> gameTimeClass = gameTimeCache.get();
        try {
            Method getYear = gameTimeClass.getMethod("getYear");
            Object result = getYear.invoke(gameTime);
            if (result instanceof Number num) {
                return num.intValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 1993;
    }

    /**
     * 밤인지 확인.
     */
    public static boolean isNight() {
        int hour = getGameHour();
        return hour < 6 || hour >= 21;
    }

    /**
     * 낮인지 확인.
     */
    public static boolean isDay() {
        return !isNight();
    }
}
