package com.example.examplemod;

import com.mutagen.api.GameAccess;
import com.mutagen.api.Mutagen;
import com.mutagen.attachment.DataAttachments;
import com.mutagen.config.ConfigManager;
import com.mutagen.event.EventBus;
import com.mutagen.event.EventPriority;
import com.mutagen.event.lifecycle.GameInitEvent;
import com.mutagen.event.lifecycle.GameTickEvent;
import com.mutagen.event.lifecycle.WorldLoadEvent;
import com.mutagen.event.lifecycle.WorldUnloadEvent;
import com.mutagen.event.player.PlayerDamageEvent;
import com.mutagen.event.player.PlayerUpdateEvent;
import com.mutagen.input.KeyBinding;
import com.mutagen.input.KeyBindingRegistry;
import com.mutagen.input.KeyCode;
import com.mutagen.mod.MutagenMod;
import com.mutagen.scheduler.MutagenScheduler;

/**
 * Example Mod - Mutagen API 사용 예제
 *
 * 이 모드는 Mutagen의 주요 기능을 보여줍니다:
 * - 설정 시스템 (@Config)
 * - 이벤트 구독 및 처리
 * - 명령어 시스템 (@Command)
 * - 데이터 첨부 (DataAttachments)
 * - 스케줄러 (MutagenScheduler)
 * - 키 바인딩 (KeyBinding)
 * - GameAccess API 사용
 */
public class ExampleMod implements MutagenMod {

    private static final String MOD_ID = "examplemod";
    private long lastLogTick = 0;

    // 키 바인딩
    private KeyBinding openMenuKey;
    private KeyBinding toggleDebugKey;

    @Override
    public void onInitialize() {
        Mutagen.log(MOD_ID, "Example Mod initializing...");

        // 1. 설정 등록 및 로드
        ConfigManager.register(ExampleConfig.class);
        Mutagen.log(MOD_ID, "Config loaded - Debug mode: " + ExampleConfig.debugMode);

        // 2. 명령어 등록
        ExampleCommands.register();
        Mutagen.log(MOD_ID, "Commands registered");

        // 3. 이벤트 리스너 등록
        registerEventListeners();

        // 4. 키 바인딩 등록
        registerKeyBindings();

        // 5. 스케줄러 예제
        scheduleExampleTasks();

        Mutagen.log(MOD_ID, "Example Mod initialized!");
    }

    private void registerEventListeners() {
        // 게임 초기화 완료 이벤트
        EventBus.subscribe(GameInitEvent.class, this::onGameInit);

        // 게임 틱 이벤트
        EventBus.subscribe(GameTickEvent.class, this::onGameTick);

        // 월드 로드/언로드 이벤트
        EventBus.subscribe(WorldLoadEvent.class, this::onWorldLoad);
        EventBus.subscribe(WorldUnloadEvent.class, this::onWorldUnload);

        // 플레이어 이벤트
        EventBus.subscribe(PlayerUpdateEvent.class, this::onPlayerUpdate);

        // 플레이어 데미지 이벤트 - 높은 우선순위로 설정 적용
        EventBus.subscribe(PlayerDamageEvent.class, this::onPlayerDamage, EventPriority.HIGH);
    }

    private void registerKeyBindings() {
        // 메뉴 열기 키 (M)
        openMenuKey = KeyBinding.create(MOD_ID, "open_menu")
                .defaultKey(KeyCode.KEY_M)
                .category("Example Mod")
                .build();
        KeyBindingRegistry.register(openMenuKey);

        // 디버그 토글 키 (Ctrl+D)
        toggleDebugKey = KeyBinding.create(MOD_ID, "toggle_debug")
                .defaultKey(KeyCode.KEY_D)
                .withCtrl()
                .category("Example Mod")
                .build();
        KeyBindingRegistry.register(toggleDebugKey);
    }

    private void scheduleExampleTasks() {
        // 게임 시작 후 5초(100틱) 뒤에 환영 메시지
        MutagenScheduler.runLater(() -> {
            Mutagen.log(MOD_ID, "Welcome to Example Mod! Press M to open menu.");
        }, 100, "welcome-message");

        // 1분마다 플레이어 데이터 자동 저장 (1200틱)
        MutagenScheduler.runTimer(() -> {
            Object player = GameAccess.getLocalPlayer();
            if (player != null) {
                DataAttachments.save(player, "examplemod_player.json");
                if (ExampleConfig.debugMode) {
                    Mutagen.log(MOD_ID, "Player data auto-saved");
                }
            }
        }, 1200, 1200, "auto-save");
    }

    // ─────────────────────────────────────────────────────────────
    // 이벤트 핸들러
    // ─────────────────────────────────────────────────────────────

    private void onGameInit(GameInitEvent event) {
        Mutagen.log(MOD_ID, "Game initialization complete!");
    }

    private void onGameTick(GameTickEvent event) {
        // 키 바인딩 체크
        checkKeyBindings();

        // 플레이어 데이터 업데이트
        updatePlayerData();

        // 설정된 간격으로 상태 로그 출력
        if (event.getTick() - lastLogTick >= ExampleConfig.logInterval) {
            lastLogTick = event.getTick();
            if (ExampleConfig.debugMode) {
                logGameStatus();
            }
        }
    }

    private void checkKeyBindings() {
        if (openMenuKey != null && openMenuKey.wasPressed()) {
            Mutagen.log(MOD_ID, "Menu key pressed! (Placeholder for actual menu)");
        }

        if (toggleDebugKey != null && toggleDebugKey.wasPressed()) {
            ExampleConfig.debugMode = !ExampleConfig.debugMode;
            ConfigManager.save(ExampleConfig.class);
            Mutagen.log(MOD_ID, "Debug mode: " + (ExampleConfig.debugMode ? "ON" : "OFF"));
        }
    }

    private void updatePlayerData() {
        Object player = GameAccess.getLocalPlayer();
        if (player == null)
            return;

        // 플레이어 데이터 가져오기 (없으면 자동 생성)
        PlayerExtraData data = DataAttachments.get(player, PlayerExtraData.TYPE);

        // 플레이 시간 증가
        data.incrementPlayTime();

        // 현재 위치 저장
        String location = String.format("%.0f, %.0f, %.0f",
                GameAccess.getPlayerX(),
                GameAccess.getPlayerY(),
                GameAccess.getPlayerZ());
        data.setLastLocation(location);
    }

    private void onWorldLoad(WorldLoadEvent event) {
        Mutagen.log(MOD_ID, "World loaded: " + event.getWorldName());

        // 플레이어 데이터 로드 시도
        Object player = GameAccess.getLocalPlayer();
        if (player != null) {
            DataAttachments.load(player, "examplemod_player.json");
            PlayerExtraData data = DataAttachments.get(player, PlayerExtraData.TYPE);
            Mutagen.log(MOD_ID, "Loaded player data: " + data);
        }

        // 월드 로드 시 게임 상태 출력
        if (ExampleConfig.debugMode) {
            logGameStatus();
        }
    }

    private void onWorldUnload(WorldUnloadEvent event) {
        Mutagen.log(MOD_ID, "World unloaded");

        // 플레이어 데이터 저장
        Object player = GameAccess.getLocalPlayer();
        if (player != null) {
            DataAttachments.save(player, "examplemod_player.json");
            Mutagen.log(MOD_ID, "Player data saved on world unload");
        }
    }

    private void onPlayerUpdate(PlayerUpdateEvent event) {
        // 플레이어 업데이트는 매우 빈번하므로 로그 생략
        // 필요시 여기서 플레이어 상태 모니터링 가능
    }

    private void onPlayerDamage(PlayerDamageEvent event) {
        float damage = event.getDamage();
        String type = event.getDamageType();

        if (ExampleConfig.debugMode) {
            Mutagen.log(MOD_ID, String.format(
                    "Player taking %.1f damage (type: %s)", damage, type));
        }

        // 설정에 따른 데미지 감소
        if (ExampleConfig.damageReduction > 0) {
            float reducedDamage = damage * (1.0f - ExampleConfig.damageReduction);
            event.setDamage(reducedDamage);
            if (ExampleConfig.debugMode) {
                Mutagen.log(MOD_ID, String.format(
                        "Damage reduced: %.1f -> %.1f", damage, reducedDamage));
            }
        }

        // 화염 면역 설정
        if (ExampleConfig.fireImmunity && "fire".equals(type)) {
            event.cancel();
            Mutagen.log(MOD_ID, "Fire damage blocked!");
        }

        // 사망 시 데이터 업데이트
        if (!event.isCancelled() && damage >= GameAccess.getPlayerHealth()) {
            Object player = GameAccess.getLocalPlayer();
            if (player != null) {
                PlayerExtraData data = DataAttachments.get(player, PlayerExtraData.TYPE);
                data.addDeath();
            }
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    private void logGameStatus() {
        StringBuilder sb = new StringBuilder();
        sb.append("\n");
        sb.append("═══════════════════════════════════════\n");
        sb.append("       EXAMPLE MOD - GAME STATUS       \n");
        sb.append("═══════════════════════════════════════\n");

        // 월드 정보
        sb.append("World: ").append(GameAccess.isWorldLoaded() ? GameAccess.getWorldName() : "Not loaded").append("\n");

        // 시간 정보
        sb.append(String.format("Time: Day %d, %02d:%02d (%s)\n",
                GameAccess.getGameDay(),
                GameAccess.getGameHour(),
                GameAccess.getGameMinute(),
                GameAccess.isNight() ? "Night" : "Day"));

        // 플레이어 정보
        Object player = GameAccess.getLocalPlayer();
        if (player != null) {
            sb.append(String.format("Player: %.1f HP at (%.0f, %.0f, %.0f)\n",
                    GameAccess.getPlayerHealth(),
                    GameAccess.getPlayerX(),
                    GameAccess.getPlayerY(),
                    GameAccess.getPlayerZ()));
            sb.append("Status: ").append(GameAccess.isPlayerAlive() ? "Alive" : "Dead").append("\n");

            // 커스텀 데이터
            PlayerExtraData data = DataAttachments.get(player, PlayerExtraData.TYPE);
            sb.append(String.format("Stats: %d kills, %d deaths, %s played\n",
                    data.getKillCount(), data.getDeathCount(), data.getPlayTimeFormatted()));
        } else {
            sb.append("Player: Not spawned\n");
        }

        // 게임 상태
        sb.append("Mode: ").append(GameAccess.isSinglePlayer() ? "Singleplayer" : "Multiplayer").append("\n");
        sb.append("Paused: ").append(GameAccess.isPaused() ? "Yes" : "No").append("\n");

        sb.append("═══════════════════════════════════════");

        Mutagen.log(MOD_ID, sb.toString());
    }

    // ─────────────────────────────────────────────────────────────
    // 라이프사이클
    // ─────────────────────────────────────────────────────────────

    @Override
    public void onWorldLoad() {
        // MutagenMod 인터페이스의 월드 로드 콜백
        Mutagen.log(MOD_ID, "MutagenMod.onWorldLoad() called");
    }

    @Override
    public void onWorldUnload() {
        // MutagenMod 인터페이스의 월드 언로드 콜백
        Mutagen.log(MOD_ID, "MutagenMod.onWorldUnload() called");
    }

    @Override
    public void onUnload() {
        Mutagen.log(MOD_ID, "Example Mod unloading...");

        // 설정 저장
        ConfigManager.save(ExampleConfig.class);

        // 플레이어 데이터 저장
        Object player = GameAccess.getLocalPlayer();
        if (player != null) {
            DataAttachments.save(player, "examplemod_player.json");
        }

        Mutagen.log(MOD_ID, "Example Mod unloaded");
    }
}
