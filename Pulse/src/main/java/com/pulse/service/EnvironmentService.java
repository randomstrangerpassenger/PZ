package com.pulse.service;

import com.pulse.api.PulseConstants;
import com.pulse.api.PulseSide;
import com.pulse.api.adapter.SideDetector;
import com.pulse.api.log.PulseLogger;
import com.pulse.adapter.Build41SideDetector;
import com.pulse.adapter.Build42SideDetector;
import com.pulse.mod.ModLoader;
import com.pulse.PulseEnvironment;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * 환경 정보 서비스.
 * 
 * v4 Phase 2: Pulse의 환경/경로/side 감지 책임을 분리.
 * - 경로 관련 기능
 * - Side 감지 (SideDetector 어댑터 활용)
 * - 초기화 상태
 * 
 * @since Pulse 0.8.0
 */
public class EnvironmentService {

    private static final String LOG = PulseLogger.PULSE;
    private static final EnvironmentService INSTANCE = new EnvironmentService();

    private final List<SideDetector> sideDetectors = new ArrayList<>();
    private volatile PulseSide currentSide = PulseSide.UNKNOWN;

    private EnvironmentService() {
        // 기본 Side 감지기 등록 (우선순위 순)
        registerDefaultDetectors();
    }

    public static EnvironmentService getInstance() {
        return INSTANCE;
    }

    // ═══════════════════════════════════════════════════════════════
    // Side 감지
    // ═══════════════════════════════════════════════════════════════

    private void registerDefaultDetectors() {
        // Build42 먼저 (더 높은 우선순위, 하지만 현재는 isAvailable=false)
        sideDetectors.add(new Build42SideDetector());
        // Build41 다음
        sideDetectors.add(new Build41SideDetector());

        // 우선순위 내림차순 정렬
        sideDetectors.sort(Comparator.comparingInt(SideDetector::getPriority).reversed());
    }

    /**
     * 커스텀 Side 감지기 등록.
     * 
     * @param detector 추가할 감지기
     */
    public void registerSideDetector(SideDetector detector) {
        sideDetectors.add(detector);
        sideDetectors.sort(Comparator.comparingInt(SideDetector::getPriority).reversed());
    }

    /**
     * 현재 Side 반환.
     * 처음 호출 시 자동 감지.
     * 
     * @return 현재 Side
     */
    public PulseSide getSide() {
        if (currentSide == PulseSide.UNKNOWN) {
            currentSide = detectSide();
        }
        return currentSide;
    }

    /**
     * Side 강제 설정 (내부용).
     * 
     * @param side 설정할 Side
     */
    public void setSide(PulseSide side) {
        if (side != null) {
            currentSide = side;
            PulseLogger.debug(LOG, "Side set to: {}", side);
        }
    }

    /**
     * Side 감지 로직.
     * 등록된 감지기들을 우선순위 순으로 시도.
     * 
     * @return 감지된 Side
     */
    private PulseSide detectSide() {
        for (SideDetector detector : sideDetectors) {
            if (detector.isAvailable()) {
                PulseSide detected = detector.detect();
                if (detected != PulseSide.UNKNOWN) {
                    PulseLogger.info(LOG, "Side detected by {}: {}",
                            detector.getClass().getSimpleName(), detected);
                    return detected;
                }
            }
        }
        return PulseSide.UNKNOWN;
    }

    public boolean isClient() {
        return getSide().isClient();
    }

    public boolean isServer() {
        return getSide().isServer();
    }

    public boolean isDedicatedServer() {
        return getSide().isDedicated();
    }

    // ═══════════════════════════════════════════════════════════════
    // 경로 관련
    // ═══════════════════════════════════════════════════════════════

    /**
     * 게임 디렉토리 경로.
     */
    public Path getGameDirectory() {
        return Path.of(System.getProperty("user.dir"));
    }

    /**
     * mods 디렉토리 경로.
     */
    public Path getModsDirectory() {
        return ModLoader.getInstance().getModsDirectory();
    }

    /**
     * 설정 디렉토리 경로.
     */
    public Path getConfigDirectory() {
        return getGameDirectory().resolve(PulseConstants.CONFIG_DIR_NAME);
    }

    // ═══════════════════════════════════════════════════════════════
    // 초기화 상태
    // ═══════════════════════════════════════════════════════════════

    /**
     * Pulse 초기화 완료 여부.
     */
    public boolean isInitialized() {
        return PulseEnvironment.isInitialized();
    }
}
