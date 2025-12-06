package com.mutagen.api;

import com.mutagen.MutagenEnvironment;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * 게임 내부 접근 API.
 * 리플렉션을 사용하여 게임 코드에 접근.
 * 게임 버전 변경에 유연하게 대응 가능.
 */
public final class GameAccess {

    private GameAccess() {
    }

    // 캐시된 클래스/메서드/필드 참조
    private static Class<?> isoWorldClass;
    private static Class<?> isoPlayerClass;
    private static Class<?> gameTimeClass;
    private static Class<?> gameClientClass;
    private static Class<?> gameServerClass;
    private static Class<?> coreClass;

    @SuppressWarnings("unused") // Used in refresh() and for future caching
    private static Object cachedIsoWorldInstance;
    private static boolean classesInitialized = false;

    // ─────────────────────────────────────────────────────────────
    // 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 게임 클래스 초기화 (lazy loading)
     */
    private static void ensureInitialized() {
        if (classesInitialized)
            return;

        ClassLoader gameLoader = MutagenEnvironment.getGameClassLoader();
        if (gameLoader == null) {
            // 아직 게임 클래스 로더가 없으면 시스템 클래스 로더 사용
            gameLoader = ClassLoader.getSystemClassLoader();
        }

        try {
            isoWorldClass = gameLoader.loadClass("zombie.iso.IsoWorld");
        } catch (ClassNotFoundException e) {
            // 무시 - 아직 로드되지 않음
        }

        try {
            isoPlayerClass = gameLoader.loadClass("zombie.characters.IsoPlayer");
        } catch (ClassNotFoundException e) {
            // 무시
        }

        try {
            gameTimeClass = gameLoader.loadClass("zombie.GameTime");
        } catch (ClassNotFoundException e) {
            // 무시
        }

        try {
            gameClientClass = gameLoader.loadClass("zombie.network.GameClient");
        } catch (ClassNotFoundException e) {
            // 무시
        }

        try {
            gameServerClass = gameLoader.loadClass("zombie.network.GameServer");
        } catch (ClassNotFoundException e) {
            // 무시
        }

        try {
            coreClass = gameLoader.loadClass("zombie.core.Core");
        } catch (ClassNotFoundException e) {
            // 무시
        }

        classesInitialized = true;
    }

    /**
     * 게임 클래스 참조 갱신 (게임 클래스 로더 변경 시 호출)
     */
    public static void refresh() {
        classesInitialized = false;
        cachedIsoWorldInstance = null;
        ensureInitialized();
    }

    // ─────────────────────────────────────────────────────────────
    // 월드
    // ─────────────────────────────────────────────────────────────

    /**
     * IsoWorld 인스턴스 가져오기
     */
    private static Object getIsoWorldInstance() {
        ensureInitialized();
        if (isoWorldClass == null)
            return null;

        try {
            // zombie.iso.IsoWorld.instance 필드 접근
            Field instanceField = isoWorldClass.getDeclaredField("instance");
            instanceField.setAccessible(true);
            return instanceField.get(null);
        } catch (Exception e) {
            // 대안: getInstance() 메서드 시도
            try {
                Method getInstance = isoWorldClass.getMethod("getInstance");
                return getInstance.invoke(null);
            } catch (Exception e2) {
                return null;
            }
        }
    }

    /**
     * 현재 월드가 로드되었는지 확인
     */
    public static boolean isWorldLoaded() {
        return getIsoWorldInstance() != null;
    }

    /**
     * 현재 월드 이름
     */
    public static String getWorldName() {
        Object world = getIsoWorldInstance();
        if (world == null)
            return "";

        try {
            Method getWorld = isoWorldClass.getMethod("getWorld");
            Object result = getWorld.invoke(world);
            return result != null ? result.toString() : "";
        } catch (Exception e) {
            return "";
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 플레이어
    // ─────────────────────────────────────────────────────────────

    /**
     * 로컬 플레이어 가져오기
     */
    public static Object getLocalPlayer() {
        ensureInitialized();
        if (isoPlayerClass == null)
            return null;

        try {
            // IsoPlayer.getInstance() 시도
            Method getInstance = isoPlayerClass.getMethod("getInstance");
            return getInstance.invoke(null);
        } catch (Exception e) {
            // 대안: IsoPlayer.players.get(0) 시도
            try {
                Field playersField = isoPlayerClass.getDeclaredField("players");
                playersField.setAccessible(true);
                Object players = playersField.get(null);
                if (players instanceof java.util.List<?> list && !list.isEmpty()) {
                    return list.get(0);
                }
            } catch (Exception e2) {
                // 무시
            }
            return null;
        }
    }

    /**
     * 플레이어가 살아있는지 확인
     */
    public static boolean isPlayerAlive() {
        Object player = getLocalPlayer();
        if (player == null)
            return false;

        try {
            // isDead() 메서드 호출
            Method isDead = player.getClass().getMethod("isDead");
            Object result = isDead.invoke(player);
            return result instanceof Boolean b && !b;
        } catch (Exception e) {
            // 플레이어 객체가 있으면 살아있다고 가정
            return true;
        }
    }

    /**
     * 플레이어 체력 가져오기
     */
    public static float getPlayerHealth() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getHealth = player.getClass().getMethod("getHealth");
            Object result = getHealth.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 위치 X
     */
    public static float getPlayerX() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getX = player.getClass().getMethod("getX");
            Object result = getX.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 위치 Y
     */
    public static float getPlayerY() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getY = player.getClass().getMethod("getY");
            Object result = getY.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    /**
     * 플레이어 위치 Z (층)
     */
    public static float getPlayerZ() {
        Object player = getLocalPlayer();
        if (player == null)
            return 0;

        try {
            Method getZ = player.getClass().getMethod("getZ");
            Object result = getZ.invoke(player);
            if (result instanceof Number num) {
                return num.floatValue();
            }
        } catch (Exception e) {
            // 무시
        }
        return 0;
    }

    // ─────────────────────────────────────────────────────────────
    // 시간
    // ─────────────────────────────────────────────────────────────

    /**
     * GameTime 인스턴스 가져오기
     */
    private static Object getGameTimeInstance() {
        ensureInitialized();
        if (gameTimeClass == null)
            return null;

        try {
            Method getInstance = gameTimeClass.getMethod("getInstance");
            return getInstance.invoke(null);
        } catch (Exception e) {
            // 대안: instance 필드 접근
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
     * 게임 내 시간 (시)
     */
    public static int getGameHour() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 0;

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
     * 게임 내 분
     */
    public static int getGameMinute() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 0;

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
     * 게임 내 일수
     */
    public static int getGameDay() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 1;

        try {
            Method getDay = gameTimeClass.getMethod("getDay");
            Object result = getDay.invoke(gameTime);
            if (result instanceof Number num) {
                return num.intValue();
            }
        } catch (Exception e) {
            // 대안: NightsSurvived + 1
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
     * 게임 내 월
     */
    public static int getGameMonth() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 7; // 기본값: 7월

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
     * 게임 내 연도
     */
    public static int getGameYear() {
        Object gameTime = getGameTimeInstance();
        if (gameTime == null)
            return 1993; // 기본값

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
     * 밤인지 확인
     */
    public static boolean isNight() {
        int hour = getGameHour();
        return hour < 6 || hour >= 21;
    }

    /**
     * 낮인지 확인
     */
    public static boolean isDay() {
        return !isNight();
    }

    // ─────────────────────────────────────────────────────────────
    // 게임 상태
    // ─────────────────────────────────────────────────────────────

    /**
     * 게임 일시정지 상태인지 확인
     */
    public static boolean isPaused() {
        ensureInitialized();

        // Core.getInstance().isGamePaused() 시도
        if (coreClass != null) {
            try {
                Method getInstance = coreClass.getMethod("getInstance");
                Object core = getInstance.invoke(null);
                if (core != null) {
                    Method isGamePaused = coreClass.getMethod("isGamePaused");
                    Object result = isGamePaused.invoke(core);
                    if (result instanceof Boolean b) {
                        return b;
                    }
                }
            } catch (Exception e) {
                // 무시
            }
        }

        // 대안: UIManager.bSuspend 확인
        try {
            ClassLoader loader = MutagenEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> uiManagerClass = loader.loadClass("zombie.ui.UIManager");
            Field suspendField = uiManagerClass.getDeclaredField("bSuspend");
            suspendField.setAccessible(true);
            Object result = suspendField.get(null);
            if (result instanceof Boolean b) {
                return b;
            }
        } catch (Exception e) {
            // 무시
        }

        return false;
    }

    /**
     * 멀티플레이어인지 확인
     */
    public static boolean isMultiplayer() {
        ensureInitialized();

        // GameClient.bClient 확인
        if (gameClientClass != null) {
            try {
                Field bClientField = gameClientClass.getDeclaredField("bClient");
                bClientField.setAccessible(true);
                Object result = bClientField.get(null);
                if (result instanceof Boolean b && b) {
                    return true;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        // GameServer.bServer 확인
        if (gameServerClass != null) {
            try {
                Field bServerField = gameServerClass.getDeclaredField("bServer");
                bServerField.setAccessible(true);
                Object result = bServerField.get(null);
                if (result instanceof Boolean b && b) {
                    return true;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        return false;
    }

    /**
     * 서버인지 확인 (멀티플레이어)
     */
    public static boolean isServer() {
        ensureInitialized();

        if (gameServerClass != null) {
            try {
                Field bServerField = gameServerClass.getDeclaredField("bServer");
                bServerField.setAccessible(true);
                Object result = bServerField.get(null);
                if (result instanceof Boolean b) {
                    return b;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        return false;
    }

    /**
     * 클라이언트인지 확인 (멀티플레이어)
     */
    public static boolean isClient() {
        ensureInitialized();

        if (gameClientClass != null) {
            try {
                Field bClientField = gameClientClass.getDeclaredField("bClient");
                bClientField.setAccessible(true);
                Object result = bClientField.get(null);
                if (result instanceof Boolean b) {
                    return b;
                }
            } catch (Exception e) {
                // 무시
            }
        }

        return false;
    }

    /**
     * 싱글플레이어인지 확인
     */
    public static boolean isSinglePlayer() {
        return !isMultiplayer();
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 리플렉션으로 정적 필드 값 가져오기
     */
    public static Object getStaticField(String className, String fieldName) {
        try {
            ClassLoader loader = MutagenEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> clazz = loader.loadClass(className);
            Field field = clazz.getDeclaredField(fieldName);
            field.setAccessible(true);
            return field.get(null);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 리플렉션으로 정적 메서드 호출
     */
    public static Object invokeStaticMethod(String className, String methodName, Object... args) {
        try {
            ClassLoader loader = MutagenEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> clazz = loader.loadClass(className);

            // 인자 없는 메서드
            if (args.length == 0) {
                Method method = clazz.getMethod(methodName);
                return method.invoke(null);
            }

            // 인자 타입 추론
            Class<?>[] argTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                argTypes[i] = args[i] != null ? args[i].getClass() : Object.class;
            }

            Method method = clazz.getMethod(methodName, argTypes);
            return method.invoke(null, args);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 게임 클래스 로드
     */
    public static Class<?> getGameClass(String className) {
        try {
            ClassLoader loader = MutagenEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();
            return loader.loadClass(className);
        } catch (ClassNotFoundException e) {
            return null;
        }
    }
}
