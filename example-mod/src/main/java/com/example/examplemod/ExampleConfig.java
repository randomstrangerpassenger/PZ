package com.example.examplemod;

import com.pulse.config.Config;
import com.pulse.config.ConfigValue;

/**
 * Example Mod 설정.
 * 
 * @Config 어노테이션이 붙은 클래스는 자동으로 JSON 설정 파일로 관리됩니다.
 *         파일 위치: config/examplemod.json
 */
@Config(modId = "examplemod")
public class ExampleConfig {

    // ─────────────────────────────────────────────────────────────
    // 일반 설정
    // ─────────────────────────────────────────────────────────────

    @ConfigValue(comment = "Enable debug logging")
    public static boolean debugMode = false;

    @ConfigValue(comment = "Status log interval in ticks (600 = 10 seconds)")
    public static int logInterval = 600;

    // ─────────────────────────────────────────────────────────────
    // 게임플레이 설정
    // ─────────────────────────────────────────────────────────────

    @ConfigValue(comment = "Damage reduction multiplier (0.0 - 1.0)")
    public static float damageReduction = 0.0f;

    @ConfigValue(comment = "Enable fire damage immunity")
    public static boolean fireImmunity = false;

    @ConfigValue(comment = "Enable night vision effect")
    public static boolean nightVision = false;

    // ─────────────────────────────────────────────────────────────
    // 알림 설정
    // ─────────────────────────────────────────────────────────────

    @ConfigValue(comment = "Show status notifications")
    public static boolean showNotifications = true;

    @ConfigValue(comment = "Notification display duration in ticks")
    public static int notificationDuration = 100;
}
