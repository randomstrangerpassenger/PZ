package com.pulse.debug;

import com.pulse.api.log.PulseLogger;
import com.pulse.security.PermissionManager;
import com.pulse.security.PermissionManager.Permission;

import java.util.Set;

/**
 * DevConsole 권한 및 보안 유효성 검사기.
 * 멀티플레이어 환경에서의 보안 정책과 관리자 권한을 관리합니다.
 */
public class PermissionValidator {

    private static final String LOG = PulseLogger.PULSE;
    private static final PermissionValidator INSTANCE = new PermissionValidator();

    /** 위험 명령어 목록 - 권한 검사 필요 */
    private static final Set<String> PRIVILEGED_COMMANDS = Set.of("lua");
    private static final Set<String> MOD_MANAGE_SUBCOMMANDS = Set.of("reload", "disable", "enable");

    /** 현재 콘솔 사용자의 권한 (플레이어 ID 또는 "pulse:system") */
    private String currentExecutor = "pulse:system";
    private boolean currentExecutorIsAdmin = false;

    /** 디버그 모드 여부 (개발 중에만 true) */
    private boolean debugModeEnabled = false;

    /** 멀티플레이어 세션 여부 */
    private boolean inMultiplayerSession = false;

    private PermissionValidator() {
    }

    public static PermissionValidator getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 관리
    // ─────────────────────────────────────────────────────────────

    public void setCurrentExecutor(String executorId, boolean isAdmin) {
        this.currentExecutor = executorId != null ? executorId : "pulse:system";
        this.currentExecutorIsAdmin = isAdmin;
        PulseLogger.info(LOG, "[PermissionValidator] Executor set: {} (admin={})", currentExecutor, isAdmin);
    }

    public boolean isCurrentExecutorAdmin() {
        return currentExecutorIsAdmin;
    }

    public void resetExecutorToSystem() {
        this.currentExecutor = "pulse:system";
        this.currentExecutorIsAdmin = true;
    }

    public void setDebugMode(boolean enabled) {
        this.debugModeEnabled = enabled;
        PulseLogger.info(LOG, "[PermissionValidator] Debug mode: {}", enabled ? "ENABLED" : "DISABLED");
    }

    public boolean isDebugModeEnabled() {
        return debugModeEnabled;
    }

    public void onMultiplayerSessionStart() {
        this.inMultiplayerSession = true;
        this.debugModeEnabled = false;
        PulseLogger.info(LOG, "[PermissionValidator] Multiplayer session started - security enforced");
    }

    public void onMultiplayerSessionEnd() {
        this.inMultiplayerSession = false;
        resetExecutorToSystem();
        PulseLogger.info(LOG, "[PermissionValidator] Multiplayer session ended");
    }

    public boolean isInMultiplayerSession() {
        return inMultiplayerSession;
    }

    // ─────────────────────────────────────────────────────────────
    // 검증 로직
    // ─────────────────────────────────────────────────────────────

    /**
     * 명령어 실행 권한 검사.
     * 
     * @return 검증 실패 시 에러 메시지, 성공 시 null
     */
    public String validateCommand(String cmdName, String args) {
        // [최우선] Project Zomboid 권한 직접 검사
        if (PRIVILEGED_COMMANDS.contains(cmdName) ||
                ("mods".equals(cmdName) && args.length() > 0
                        && MOD_MANAGE_SUBCOMMANDS.contains(args.split("\\s+")[0].toLowerCase()))) {

            // PZ 멀티플레이어 클라이언트에서 Admin이 아니면 차단
            if (isInPZMultiplayerClient() && !isPZAdmin()) {
                PulseLogger.error(LOG,
                        "[DevConsole] BLOCKED: Non-admin attempted privileged command in multiplayer: {}", cmdName);
                return "§c[보안] Error: 관리자 권한이 없습니다. 이 명령어는 멀티플레이에서 관리자만 사용할 수 있습니다.";
            }
        }

        // 보안 검사 (Anti-Cheat) - 2차 검증
        boolean bypassSecurity = (debugModeEnabled && !inMultiplayerSession) || currentExecutorIsAdmin;

        if (!bypassSecurity) {
            // Lua 명령어
            if (PRIVILEGED_COMMANDS.contains(cmdName)) {
                if (!PermissionManager.hasPermission(currentExecutor, Permission.CONSOLE_LUA_EXEC)) {
                    PulseLogger.error(LOG, "[DevConsole] BLOCKED: User '{}' attempted privileged command: {}",
                            currentExecutor, cmdName);
                    return "§c[보안] 권한 부족: '" + cmdName + "' 명령어는 관리자만 사용할 수 있습니다.";
                }
            }

            // 모드 관리 명령어
            if ("mods".equals(cmdName) && args.length() > 0) {
                String subCmd = args.split("\\s+")[0].toLowerCase();
                if (MOD_MANAGE_SUBCOMMANDS.contains(subCmd)) {
                    if (!PermissionManager.hasPermission(currentExecutor, Permission.CONSOLE_MOD_MANAGE)) {
                        PulseLogger.error(LOG, "[DevConsole] BLOCKED: User '{}' attempted mod management: mods {}",
                                currentExecutor, subCmd);
                        return "§c[보안] 권한 부족: 'mods " + subCmd + "'는 관리자만 사용할 수 있습니다.";
                    }
                }
            }
        }

        // Lua 콘솔 허용 여부 (Lua 명령어인 경우)
        if ("lua".equals(cmdName) && inMultiplayerSession) {
            if (!isLuaConsoleAllowedByServer()) {
                PulseLogger.error(LOG, "[DevConsole] BLOCKED: Lua console not allowed on this server");
                return "§c[보안] 이 서버에서는 Lua 콘솔이 비활성화되어 있습니다.";
            }
        }

        return null; // 검증 통과
    }

    // ─────────────────────────────────────────────────────────────
    // Project Zomboid 연동 (Reflection)
    // ─────────────────────────────────────────────────────────────

    public boolean isLuaConsoleAllowedByServer() {
        try {
            Class<?> sandboxOptionsClass = Class.forName("zombie.SandboxOptions");
            java.lang.reflect.Field instanceField = sandboxOptionsClass.getField("instance");
            Object instance = instanceField.get(null);

            if (instance == null) {
                PulseLogger.warn(LOG, "[PermissionValidator] SandboxOptions.instance is null, defaulting to blocked");
                return false;
            }

            java.lang.reflect.Field luaConsoleField = sandboxOptionsClass.getField("AllowedToLuaConsole");
            Object luaConsoleOption = luaConsoleField.get(instance);

            if (luaConsoleOption == null) {
                PulseLogger.warn(LOG, "[PermissionValidator] AllowedToLuaConsole is null, defaulting to blocked");
                return false;
            }

            java.lang.reflect.Method getValueMethod = luaConsoleOption.getClass().getMethod("getValue");
            Object result = getValueMethod.invoke(luaConsoleOption);

            if (result instanceof Boolean) {
                return (Boolean) result;
            }
            return false;
        } catch (ClassNotFoundException e) {
            if (debugModeEnabled)
                return true;
            PulseLogger.info(LOG, "[PermissionValidator] Not running in PZ runtime, Lua console blocked");
            return false;
        } catch (Exception e) {
            PulseLogger.error(LOG, "[PermissionValidator] Error checking SandboxOptions: {}", e.getMessage());
            return false;
        }
    }

    public boolean isInPZMultiplayerClient() {
        if (inMultiplayerSession)
            return true;

        try {
            Class<?> gameWindowClass = Class.forName("zombie.GameWindow");
            java.lang.reflect.Field bServerField = gameWindowClass.getField("bServer");
            boolean isServer = bServerField.getBoolean(null);

            if (isServer)
                return false;

            Class<?> gameClientClass = Class.forName("zombie.network.GameClient");
            java.lang.reflect.Field bConnectedField = gameClientClass.getField("bConnected");
            return bConnectedField.getBoolean(null);

        } catch (ClassNotFoundException e) {
            return inMultiplayerSession;
        } catch (Exception e) {
            PulseLogger.error(LOG, "[PermissionValidator] Error checking multiplayer state: {}", e.getMessage());
            return inMultiplayerSession;
        }
    }

    public boolean isPZAdmin() {
        try {
            Class<?> gameClientClass = Class.forName("zombie.network.GameClient");
            java.lang.reflect.Field connectionField = gameClientClass.getDeclaredField("connection");
            connectionField.setAccessible(true);
            Object connection = connectionField.get(null);

            if (connection != null) {
                java.lang.reflect.Method isAdminMethod = connection.getClass().getMethod("isAdmin");
                Object result = isAdminMethod.invoke(connection);
                if (result instanceof Boolean) {
                    return (Boolean) result;
                }
            }

            Class<?> coreClass = Class.forName("zombie.core.Core");
            java.lang.reflect.Field bDebugField = coreClass.getField("bDebug");
            boolean isDebug = bDebugField.getBoolean(null);
            if (isDebug)
                return true;

            return false;
        } catch (ClassNotFoundException e) {
            return debugModeEnabled;
        } catch (Exception e) {
            PulseLogger.error(LOG, "[PermissionValidator] Error checking admin status: {}", e.getMessage());
            return false;
        }
    }
}
