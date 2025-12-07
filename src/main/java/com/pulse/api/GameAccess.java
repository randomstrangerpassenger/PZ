package com.pulse.api;

import com.pulse.PulseEnvironment;

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

        ClassLoader gameLoader = PulseEnvironment.getGameClassLoader();
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
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
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
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
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
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
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
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();
            return loader.loadClass(className);
        } catch (ClassNotFoundException e) {
            return null;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 좀비
    // ─────────────────────────────────────────────────────────────

    /**
     * 특정 위치 주변의 좀비 목록 가져오기
     * 
     * @param x      중심 X 좌표
     * @param y      중심 Y 좌표
     * @param radius 반경
     * @return 좀비 객체 리스트 (IsoZombie)
     */
    public static java.util.List<Object> getNearbyZombies(float x, float y, float radius) {
        java.util.List<Object> result = new java.util.ArrayList<>();
        ensureInitialized();

        try {
            // IsoWorld.instance.getCell().getZombieList() 접근
            Object world = getIsoWorldInstance();
            if (world == null)
                return result;

            Method getCellMethod = isoWorldClass.getMethod("getCell");
            Object cell = getCellMethod.invoke(world);
            if (cell == null)
                return result;

            Method getZombieListMethod = cell.getClass().getMethod("getZombieList");
            Object zombieList = getZombieListMethod.invoke(cell);

            if (zombieList instanceof java.util.List<?> list) {
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
    public static java.util.List<Object> getAllZombies() {
        java.util.List<Object> result = new java.util.ArrayList<>();
        ensureInitialized();

        try {
            Object world = getIsoWorldInstance();
            if (world == null)
                return result;

            Method getCellMethod = isoWorldClass.getMethod("getCell");
            Object cell = getCellMethod.invoke(world);
            if (cell == null)
                return result;

            Method getZombieListMethod = cell.getClass().getMethod("getZombieList");
            Object zombieList = getZombieListMethod.invoke(cell);

            if (zombieList instanceof java.util.List<?> list) {
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

    /**
     * 현재 셀의 좀비 수
     */
    public static int getZombieCount() {
        return getAllZombies().size();
    }

    // ─────────────────────────────────────────────────────────────
    // 아이템 / 인벤토리
    // ─────────────────────────────────────────────────────────────

    /**
     * 아이템 생성
     * 
     * @param itemType 아이템 타입 (예: "Base.Axe", "Base.Apple")
     * @return 생성된 InventoryItem 또는 null
     */
    public static Object createItem(String itemType) {
        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> instanceManagerClass = loader.loadClass("zombie.inventory.InventoryItemFactory");
            Method createMethod = instanceManagerClass.getMethod("CreateItem", String.class);
            return createMethod.invoke(null, itemType);
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to create item: " + itemType);
            return null;
        }
    }

    /**
     * 월드에 아이템 스폰
     * 
     * @param itemType 아이템 타입
     * @param x        X 좌표
     * @param y        Y 좌표
     * @param z        Z 좌표 (층)
     * @return 스폰된 아이템 또는 null
     */
    public static Object spawnItem(String itemType, float x, float y, float z) {
        Object item = createItem(itemType);
        if (item == null)
            return null;

        try {
            Object square = getSquare((int) x, (int) y, (int) z);
            if (square == null)
                return null;

            Method addItemMethod = square.getClass().getMethod("AddWorldInventoryItem",
                    item.getClass().getSuperclass(), float.class, float.class, float.class);
            addItemMethod.invoke(square, item, x % 1, y % 1, 0f);
            return item;
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to spawn item: " + e.getMessage());
            return null;
        }
    }

    /**
     * 플레이어 인벤토리 아이템 목록
     */
    public static java.util.List<Object> getInventoryItems(Object player) {
        java.util.List<Object> result = new java.util.ArrayList<>();
        if (player == null)
            return result;

        try {
            Method getInventoryMethod = player.getClass().getMethod("getInventory");
            Object inventory = getInventoryMethod.invoke(player);
            if (inventory == null)
                return result;

            Method getItemsMethod = inventory.getClass().getMethod("getItems");
            Object items = getItemsMethod.invoke(inventory);

            if (items instanceof java.util.ArrayList<?> list) {
                result.addAll(list);
            }
        } catch (Exception e) {
            // 무시
        }

        return result;
    }

    /**
     * 플레이어 인벤토리에 아이템 추가
     */
    public static boolean addInventoryItem(Object player, Object item) {
        if (player == null || item == null)
            return false;

        try {
            Method getInventoryMethod = player.getClass().getMethod("getInventory");
            Object inventory = getInventoryMethod.invoke(player);
            if (inventory == null)
                return false;

            Method addItemMethod = inventory.getClass().getMethod("AddItem", item.getClass().getSuperclass());
            addItemMethod.invoke(inventory, item);
            return true;
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to add item to inventory");
            return false;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 그리드 / 월드
    // ─────────────────────────────────────────────────────────────

    /**
     * 특정 좌표의 그리드 스퀘어 가져오기
     */
    public static Object getSquare(int x, int y, int z) {
        ensureInitialized();

        try {
            Object world = getIsoWorldInstance();
            if (world == null)
                return null;

            Method getCellMethod = isoWorldClass.getMethod("getCell");
            Object cell = getCellMethod.invoke(world);
            if (cell == null)
                return null;

            Method getGridSquareMethod = cell.getClass().getMethod("getGridSquare", int.class, int.class, int.class);
            return getGridSquareMethod.invoke(cell, x, y, z);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 특정 좌표의 건물 가져오기
     */
    public static Object getBuilding(int x, int y) {
        Object square = getSquare(x, y, 0);
        if (square == null)
            return null;

        try {
            Method getBuildingMethod = square.getClass().getMethod("getBuilding");
            return getBuildingMethod.invoke(square);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 범위 내 차량 목록
     */
    public static java.util.List<Object> getVehiclesInRange(float x, float y, float radius) {
        java.util.List<Object> result = new java.util.ArrayList<>();
        ensureInitialized();

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> vehicleManagerClass = loader.loadClass("zombie.vehicles.VehicleManager");
            Method getInstanceMethod = vehicleManagerClass.getMethod("instance");
            Object manager = getInstanceMethod.invoke(null);

            if (manager == null)
                return result;

            Method getVehiclesMethod = vehicleManagerClass.getMethod("getVehicles");
            Object vehicles = getVehiclesMethod.invoke(manager);

            if (vehicles instanceof java.util.ArrayList<?> list) {
                for (Object vehicle : list) {
                    if (vehicle == null)
                        continue;
                    try {
                        Method getX = vehicle.getClass().getMethod("getX");
                        Method getY = vehicle.getClass().getMethod("getY");
                        float vx = ((Number) getX.invoke(vehicle)).floatValue();
                        float vy = ((Number) getY.invoke(vehicle)).floatValue();

                        float dx = vx - x;
                        float dy = vy - y;
                        if (dx * dx + dy * dy <= radius * radius) {
                            result.add(vehicle);
                        }
                    } catch (Exception e) {
                        // 개별 차량 처리 실패 무시
                    }
                }
            }
        } catch (Exception e) {
            // 무시
        }

        return result;
    }

    /**
     * 현재 셀 가져오기
     */
    public static Object getCell() {
        ensureInitialized();

        try {
            Object world = getIsoWorldInstance();
            if (world == null)
                return null;

            Method getCellMethod = isoWorldClass.getMethod("getCell");
            return getCellMethod.invoke(world);
        } catch (Exception e) {
            return null;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 사운드 / 이펙트
    // ─────────────────────────────────────────────────────────────

    /**
     * 특정 위치에서 사운드 재생
     */
    public static void playSound(String soundName, float x, float y, float z) {
        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            // zombie.core.audio.BaseSoundManager 사용
            Class<?> soundManagerClass = loader.loadClass("zombie.core.audio.BaseSoundManager");
            Method getInstanceMethod = soundManagerClass.getMethod("instance");
            Object manager = getInstanceMethod.invoke(null);

            if (manager == null)
                return;

            Method playMethod = soundManagerClass.getMethod("playSound", String.class, float.class, float.class,
                    float.class);
            playMethod.invoke(manager, soundName, x, y, z);
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to play sound: " + soundName);
        }
    }

    /**
     * 그리드 스퀘어에서 사운드 재생
     */
    public static void playWorldSound(String soundName, Object gridSquare) {
        if (gridSquare == null)
            return;

        try {
            Method getXMethod = gridSquare.getClass().getMethod("getX");
            Method getYMethod = gridSquare.getClass().getMethod("getY");
            Method getZMethod = gridSquare.getClass().getMethod("getZ");

            float x = ((Number) getXMethod.invoke(gridSquare)).floatValue();
            float y = ((Number) getYMethod.invoke(gridSquare)).floatValue();
            float z = ((Number) getZMethod.invoke(gridSquare)).floatValue();

            playSound(soundName, x, y, z);
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to play world sound");
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 / 상태 체크
    // ─────────────────────────────────────────────────────────────

    /**
     * 현재 플레이어가 관리자인지 확인 (멀티플레이어)
     */
    public static boolean isAdmin() {
        if (!isMultiplayer())
            return true; // 싱글플레이어는 항상 관리자

        Object player = getLocalPlayer();
        if (player == null)
            return false;

        try {
            // IsoPlayer.accessLevel 확인
            Method getAccessLevelMethod = player.getClass().getMethod("getAccessLevel");
            Object accessLevel = getAccessLevelMethod.invoke(player);

            if (accessLevel != null) {
                String level = accessLevel.toString().toLowerCase();
                return level.equals("admin") || level.equals("moderator") || level.equals("gm");
            }
        } catch (Exception e) {
            // 무시
        }

        return false;
    }

    /**
     * 현재 플레이어가 협동 호스트인지 확인
     */
    public static boolean isCoopHost() {
        ensureInitialized();

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> coopClass = loader.loadClass("zombie.characters.IsoPlayer");
            Field coopField = coopClass.getDeclaredField("isCoopHost");
            coopField.setAccessible(true);
            Object result = coopField.get(null);

            if (result instanceof Boolean b) {
                return b;
            }
        } catch (Exception e) {
            // 무시
        }

        return false;
    }

    /**
     * 디버그 모드인지 확인
     */
    public static boolean isDebugMode() {
        ensureInitialized();

        // Core.bDebug 확인
        if (coreClass != null) {
            try {
                Field debugField = coreClass.getDeclaredField("bDebug");
                debugField.setAccessible(true);
                Object result = debugField.get(null);
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
     * 게임이 튜토리얼 모드인지 확인
     */
    public static boolean isTutorial() {
        ensureInitialized();

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> gameClass = loader.loadClass("zombie.core.Core");
            Method getInstance = gameClass.getMethod("getInstance");
            Object core = getInstance.invoke(null);

            if (core != null) {
                Method isTutorial = gameClass.getMethod("isTutorial");
                Object result = isTutorial.invoke(core);
                if (result instanceof Boolean b) {
                    return b;
                }
            }
        } catch (Exception e) {
            // 무시
        }

        return false;
    }

    // ─────────────────────────────────────────────────────────────
    // 멀티플레이어 전용 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 연결된 플레이어 목록 가져오기 (멀티플레이어)
     * 싱글플레이어에서는 로컬 플레이어만 포함된 리스트 반환
     * 
     * @return 플레이어 객체 리스트
     */
    public static java.util.List<Object> getAllPlayers() {
        java.util.List<Object> result = new java.util.ArrayList<>();
        ensureInitialized();

        if (isoPlayerClass == null)
            return result;

        try {
            // IsoPlayer.players 정적 필드 접근
            Field playersField = isoPlayerClass.getDeclaredField("players");
            playersField.setAccessible(true);
            Object players = playersField.get(null);

            if (players instanceof java.util.List<?> list) {
                for (Object player : list) {
                    if (player != null) {
                        result.add(player);
                    }
                }
            }
        } catch (Exception e) {
            // 대안: 로컬 플레이어만 반환
            Object local = getLocalPlayer();
            if (local != null) {
                result.add(local);
            }
        }

        return result;
    }

    /**
     * 현재 연결된 플레이어 수
     */
    public static int getPlayerCount() {
        return getAllPlayers().size();
    }

    /**
     * 이름으로 플레이어 찾기
     * 
     * @param username 플레이어 이름
     * @return 플레이어 객체 또는 null
     */
    public static Object getPlayerByName(String username) {
        if (username == null)
            return null;

        for (Object player : getAllPlayers()) {
            try {
                Method getUsernameMethod = player.getClass().getMethod("getUsername");
                Object name = getUsernameMethod.invoke(player);
                if (username.equalsIgnoreCase(String.valueOf(name))) {
                    return player;
                }
            } catch (Exception e) {
                // 무시
            }
        }
        return null;
    }

    // ─────────────────────────────────────────────────────────────
    // 좀비 스폰 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 특정 위치에 좀비 스폰
     * 
     * @param x X 좌표
     * @param y Y 좌표
     * @param z Z 좌표 (층)
     * @return 스폰된 좀비 객체 또는 null
     */
    public static Object spawnZombie(int x, int y, int z) {
        ensureInitialized();

        try {
            Object cell = getCell();
            if (cell == null)
                return null;

            // VirtualZombieManager 또는 직접 생성 시도
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            // zombie.characters.IsoZombie 직접 생성
            Class<?> zombieClass = loader.loadClass("zombie.characters.IsoZombie");
            Object zombie = zombieClass.getDeclaredConstructor(cell.getClass())
                    .newInstance(cell);

            // 위치 설정
            Method setXMethod = zombieClass.getMethod("setX", float.class);
            Method setYMethod = zombieClass.getMethod("setY", float.class);
            Method setZMethod = zombieClass.getMethod("setZ", float.class);

            setXMethod.invoke(zombie, (float) x);
            setYMethod.invoke(zombie, (float) y);
            setZMethod.invoke(zombie, (float) z);

            // 셀에 추가
            Method addToWorldMethod = zombieClass.getMethod("addToWorld");
            addToWorldMethod.invoke(zombie);

            System.out.println("[Pulse/GameAccess] Spawned zombie at " + x + ", " + y + ", " + z);
            return zombie;
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to spawn zombie: " + e.getMessage());
            return null;
        }
    }

    /**
     * 플레이어 근처에 좀비 스폰
     * 
     * @param offsetX 플레이어로부터의 X 오프셋
     * @param offsetY 플레이어로부터의 Y 오프셋
     * @return 스폰된 좀비 객체 또는 null
     */
    public static Object spawnZombieNearPlayer(int offsetX, int offsetY) {
        int px = (int) getPlayerX();
        int py = (int) getPlayerY();
        int pz = (int) getPlayerZ();
        return spawnZombie(px + offsetX, py + offsetY, pz);
    }

    // ─────────────────────────────────────────────────────────────
    // 거리 계산 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 두 엔티티 간의 거리 계산
     * 
     * @param entity1 첫 번째 엔티티 (IsoGameCharacter, IsoObject 등)
     * @param entity2 두 번째 엔티티
     * @return 거리 (단위: 타일), 측정 불가 시 -1
     */
    public static float getDistance(Object entity1, Object entity2) {
        if (entity1 == null || entity2 == null)
            return -1;

        try {
            float x1 = getEntityX(entity1);
            float y1 = getEntityY(entity1);
            float x2 = getEntityX(entity2);
            float y2 = getEntityY(entity2);

            float dx = x2 - x1;
            float dy = y2 - y1;
            return (float) Math.sqrt(dx * dx + dy * dy);
        } catch (Exception e) {
            return -1;
        }
    }

    /**
     * 엔티티와 좌표 간의 거리 계산
     */
    public static float getDistanceToPoint(Object entity, float x, float y) {
        if (entity == null)
            return -1;

        try {
            float ex = getEntityX(entity);
            float ey = getEntityY(entity);
            float dx = x - ex;
            float dy = y - ey;
            return (float) Math.sqrt(dx * dx + dy * dy);
        } catch (Exception e) {
            return -1;
        }
    }

    /**
     * 플레이어와 엔티티 간의 거리 계산
     */
    public static float getDistanceToPlayer(Object entity) {
        Object player = getLocalPlayer();
        if (player == null || entity == null)
            return -1;
        return getDistance(player, entity);
    }

    /**
     * 엔티티의 X 좌표 가져오기
     */
    private static float getEntityX(Object entity) throws Exception {
        Method getX = entity.getClass().getMethod("getX");
        return ((Number) getX.invoke(entity)).floatValue();
    }

    /**
     * 엔티티의 Y 좌표 가져오기
     */
    private static float getEntityY(Object entity) throws Exception {
        Method getY = entity.getClass().getMethod("getY");
        return ((Number) getY.invoke(entity)).floatValue();
    }

    // ─────────────────────────────────────────────────────────────
    // 날씨 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 현재 날씨 상태 가져오기
     * 
     * @return 날씨 상태 문자열 (예: "sunny", "rain", "fog" 등)
     */
    public static String getWeather() {
        ensureInitialized();

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> climateClass = loader.loadClass("zombie.iso.weather.ClimateManager");
            Method getInstanceMethod = climateClass.getMethod("getInstance");
            Object climate = getInstanceMethod.invoke(null);

            if (climate != null) {
                // 비 확인
                Method isRainingMethod = climateClass.getMethod("isRaining");
                Object raining = isRainingMethod.invoke(climate);
                if (raining instanceof Boolean b && b) {
                    return "rain";
                }

                // 안개 확인
                try {
                    Method getFogMethod = climateClass.getMethod("getFogIntensity");
                    Object fog = getFogMethod.invoke(climate);
                    if (fog instanceof Number num && num.floatValue() > 0.3f) {
                        return "fog";
                    }
                } catch (Exception e) {
                    // 무시
                }

                // 눈 확인
                try {
                    Method isSnowingMethod = climateClass.getMethod("isSnowing");
                    Object snowing = isSnowingMethod.invoke(climate);
                    if (snowing instanceof Boolean b && b) {
                        return "snow";
                    }
                } catch (Exception e) {
                    // 무시
                }

                return "sunny";
            }
        } catch (Exception e) {
            // 무시
        }

        return "unknown";
    }

    /**
     * 비가 오는지 확인
     */
    public static boolean isRaining() {
        return "rain".equals(getWeather());
    }

    /**
     * 눈이 오는지 확인
     */
    public static boolean isSnowing() {
        return "snow".equals(getWeather());
    }

    /**
     * 안개가 끼었는지 확인
     */
    public static boolean isFoggy() {
        return "fog".equals(getWeather());
    }

    /**
     * 날씨 강도 설정 (비)
     * 
     * @param intensity 강도 (0.0 ~ 1.0)
     */
    public static void setRainIntensity(float intensity) {
        ensureInitialized();

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> climateClass = loader.loadClass("zombie.iso.weather.ClimateManager");
            Method getInstanceMethod = climateClass.getMethod("getInstance");
            Object climate = getInstanceMethod.invoke(null);

            if (climate != null) {
                Method setRainMethod = climateClass.getMethod("setRainIntensity", float.class);
                setRainMethod.invoke(climate, Math.max(0, Math.min(1, intensity)));
                System.out.println("[Pulse/GameAccess] Set rain intensity to " + intensity);
            }
        } catch (Exception e) {
            System.err.println("[Pulse/GameAccess] Failed to set rain: " + e.getMessage());
        }
    }

    /**
     * 비 시작
     */
    public static void startRain() {
        setRainIntensity(0.5f);
    }

    /**
     * 비 중지
     */
    public static void stopRain() {
        setRainIntensity(0f);
    }
}
