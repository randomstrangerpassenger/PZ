package com.example.examplemod;

import com.mutagen.api.GameAccess;
import com.mutagen.api.Mutagen;
import com.mutagen.event.EventBus;
import com.mutagen.event.lifecycle.GameInitEvent;
import com.mutagen.event.lifecycle.GameTickEvent;
import com.mutagen.event.lifecycle.WorldLoadEvent;
import com.mutagen.event.lifecycle.WorldUnloadEvent;
import com.mutagen.event.player.PlayerDamageEvent;
import com.mutagen.event.player.PlayerUpdateEvent;
import com.mutagen.mod.MutagenMod;

/**
 * Example Mod - Mutagen API 사용 예제
 *
 * 이 모드는 Mutagen의 주요 기능을 보여줍니다:
 * - 이벤트 구독 및 처리
 * - GameAccess API 사용
 * - 모드 라이프사이클 관리
 */
public class ExampleMod implements MutagenMod {

    private static final String MOD_ID = "examplemod";
    private long lastLogTick = 0;

    @Override
    public void onInitialize() {
        Mutagen.log(MOD_ID, "Example Mod initializing...");

        // 이벤트 리스너 등록
        registerEventListeners();

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
        EventBus.subscribe(PlayerDamageEvent.class, this::onPlayerDamage);
    }

    // ─────────────────────────────────────────────────────────────
    // 이벤트 핸들러
    // ─────────────────────────────────────────────────────────────

    private void onGameInit(GameInitEvent event) {
        Mutagen.log(MOD_ID, "Game initialization complete!");
    }

    private void onGameTick(GameTickEvent event) {
        // 10초마다 상태 로그 출력 (약 600 틱)
        if (event.getTick() - lastLogTick >= 600) {
            lastLogTick = event.getTick();
            logGameStatus();
        }
    }

    private void onWorldLoad(WorldLoadEvent event) {
        Mutagen.log(MOD_ID, "World loaded: " + event.getWorldName());

        // 월드 로드 시 게임 상태 출력
        logGameStatus();
    }

    private void onWorldUnload(WorldUnloadEvent event) {
        Mutagen.log(MOD_ID, "World unloaded");
    }

    private void onPlayerUpdate(PlayerUpdateEvent event) {
        // 플레이어 업데이트는 매우 빈번하므로 로그 생략
        // 필요시 여기서 플레이어 상태 모니터링 가능
    }

    private void onPlayerDamage(PlayerDamageEvent event) {
        float damage = event.getDamage();
        String type = event.getDamageType();

        Mutagen.log(MOD_ID, String.format(
            "Player taking %.1f damage (type: %s)", damage, type));

        // 예제: 데미지 50% 감소
        // event.setDamage(damage * 0.5f);

        // 예제: 특정 데미지 타입 완전 무효화
        // if ("fire".equals(type)) {
        //     event.cancel();
        //     Mutagen.log(MOD_ID, "Fire damage blocked!");
        // }
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
        sb.append("World: ").append(GameAccess.isWorldLoaded() ?
            GameAccess.getWorldName() : "Not loaded").append("\n");

        // 시간 정보
        sb.append(String.format("Time: Day %d, %02d:%02d (%s)\n",
            GameAccess.getGameDay(),
            GameAccess.getGameHour(),
            GameAccess.getGameMinute(),
            GameAccess.isNight() ? "Night" : "Day"));

        // 플레이어 정보
        if (GameAccess.getLocalPlayer() != null) {
            sb.append(String.format("Player: %.1f HP at (%.0f, %.0f, %.0f)\n",
                GameAccess.getPlayerHealth(),
                GameAccess.getPlayerX(),
                GameAccess.getPlayerY(),
                GameAccess.getPlayerZ()));
            sb.append("Status: ").append(GameAccess.isPlayerAlive() ?
                "Alive" : "Dead").append("\n");
        } else {
            sb.append("Player: Not spawned\n");
        }

        // 게임 상태
        sb.append("Mode: ").append(GameAccess.isSinglePlayer() ?
            "Singleplayer" : "Multiplayer").append("\n");
        sb.append("Paused: ").append(GameAccess.isPaused() ?
            "Yes" : "No").append("\n");

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

        // 이벤트 리스너 정리는 필요시 수행
        // EventBus.getInstance().clearAll()은 모든 리스너를 제거하므로 주의

        Mutagen.log(MOD_ID, "Example Mod unloaded");
    }
}
