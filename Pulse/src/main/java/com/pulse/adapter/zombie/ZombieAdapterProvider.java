package com.pulse.adapter.zombie;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.version.GameVersion;

/**
 * Zombie 어댑터 제공자.
 * 
 * 현재 게임 버전에 맞는 IZombieAdapter를 반환합니다.
 * 싱글톤 패턴으로 한 번만 어댑터를 생성합니다.
 * 
 * 사용 예:
 * 
 * <pre>
 * IZombieAdapter adapter = ZombieAdapterProvider.get();
 * int zombieId = adapter.getZombieId(zombie);
 * </pre>
 * 
 * @since Pulse 1.4
 */
public final class ZombieAdapterProvider {

    private static volatile IZombieAdapter instance;
    private static final Object LOCK = new Object();

    private ZombieAdapterProvider() {
    }

    /**
     * 현재 게임 버전에 맞는 어댑터 반환.
     * 
     * @return IZombieAdapter 구현체
     */
    public static IZombieAdapter get() {
        if (instance == null) {
            synchronized (LOCK) {
                if (instance == null) {
                    instance = createAdapter();
                }
            }
        }
        return instance;
    }

    /**
     * 어댑터 초기화 (테스트용).
     */
    public static void reset() {
        synchronized (LOCK) {
            instance = null;
        }
    }

    /**
     * 어댑터 수동 설정 (테스트용).
     */
    public static void override(IZombieAdapter adapter) {
        synchronized (LOCK) {
            instance = adapter;
            PulseLogger.info("Pulse/ZombieAdapterProvider", "Overridden with: " + adapter.getName());
        }
    }

    private static IZombieAdapter createAdapter() {
        int version = GameVersion.get();

        IZombieAdapter adapter;

        if (version >= GameVersion.BUILD_42) {
            Build42ZombieAdapter b42 = new Build42ZombieAdapter();
            if (b42.isCompatible()) {
                adapter = b42;
                PulseLogger.info("Pulse/ZombieAdapterProvider", "Using Build42ZombieAdapter");
            } else {
                adapter = new Build41ZombieAdapter();
                PulseLogger.info("Pulse/ZombieAdapterProvider", "Build 42 not compatible, using Build41ZombieAdapter");
            }
        } else {
            adapter = new Build41ZombieAdapter();
            PulseLogger.info("Pulse/ZombieAdapterProvider", "Using Build41ZombieAdapter");
        }

        return adapter;
    }
}
