package com.pulse.security;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 모드 권한 관리자.
 * 모드별 권한을 검증하고 관리.
 */
public class PermissionManager {

    private static final PermissionManager INSTANCE = new PermissionManager();

    // modId -> 허용된 권한 세트
    private final Map<String, Set<Permission>> grantedPermissions = new ConcurrentHashMap<>();

    // 권한별 기본 정책
    private final Map<Permission, PermissionPolicy> defaultPolicies = new EnumMap<>(Permission.class);

    private PermissionManager() {
        // 기본 정책 설정
        for (Permission p : Permission.values()) {
            defaultPolicies.put(p, p.getDefaultPolicy());
        }
    }

    public static PermissionManager getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 검사
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드가 특정 권한을 가지고 있는지 확인.
     */
    public static boolean hasPermission(String modId, Permission permission) {
        return INSTANCE.checkPermission(modId, permission);
    }

    private boolean checkPermission(String modId, Permission permission) {
        // 명시적으로 부여된 권한
        Set<Permission> perms = grantedPermissions.get(modId);
        if (perms != null && perms.contains(permission)) {
            return true;
        }

        // 기본 정책 확인
        PermissionPolicy policy = defaultPolicies.get(permission);
        return policy == PermissionPolicy.ALLOW_ALL;
    }

    /**
     * 권한 검사 및 예외 발생.
     */
    public static void require(String modId, Permission permission) throws SecurityException {
        if (!hasPermission(modId, permission)) {
            throw new SecurityException("Mod '" + modId + "' lacks permission: " + permission);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 부여
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드에 권한 부여.
     */
    public static void grant(String modId, Permission permission) {
        INSTANCE.grantedPermissions
                .computeIfAbsent(modId, k -> ConcurrentHashMap.newKeySet())
                .add(permission);
        System.out.println("[Pulse/Security] Granted " + permission + " to " + modId);
    }

    /**
     * 모드에서 권한 제거.
     */
    public static void revoke(String modId, Permission permission) {
        Set<Permission> perms = INSTANCE.grantedPermissions.get(modId);
        if (perms != null) {
            perms.remove(permission);
        }
    }

    /**
     * 모드의 모든 권한 제거.
     */
    public static void revokeAll(String modId) {
        INSTANCE.grantedPermissions.remove(modId);
    }

    /**
     * pulse.mod.json의 permissions 필드에서 권한 로드.
     */
    public static void loadFromMetadata(String modId, List<String> permissionNames) {
        for (String name : permissionNames) {
            try {
                Permission perm = Permission.valueOf(name.toUpperCase().replace(".", "_"));
                grant(modId, perm);
            } catch (IllegalArgumentException e) {
                System.err.println("[Pulse/Security] Unknown permission: " + name);
            }
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 권한 열거형
    // ─────────────────────────────────────────────────────────────

    public enum Permission {
        // 파일 시스템
        FILE_READ(PermissionPolicy.ALLOW_ALL),
        FILE_WRITE(PermissionPolicy.ASK),
        FILE_DELETE(PermissionPolicy.DENY),

        // 네트워크
        NETWORK_CLIENT(PermissionPolicy.ALLOW_ALL),
        NETWORK_SERVER(PermissionPolicy.ASK),
        NETWORK_EXTERNAL(PermissionPolicy.DENY),

        // 시스템
        SYSTEM_EXEC(PermissionPolicy.DENY),
        SYSTEM_CLASSLOADER(PermissionPolicy.DENY),
        SYSTEM_REFLECTION(PermissionPolicy.ASK),

        // 게임
        GAME_WORLD_MODIFY(PermissionPolicy.ALLOW_ALL),
        GAME_PLAYER_DATA(PermissionPolicy.ALLOW_ALL),
        GAME_ADMIN_COMMANDS(PermissionPolicy.ASK),

        // 콘솔 (멀티플레이 보안)
        CONSOLE_ACCESS(PermissionPolicy.ALLOW_ALL), // 기본 콘솔 접근
        CONSOLE_LUA_EXEC(PermissionPolicy.DENY), // Lua 코드 실행 (위험)
        CONSOLE_MOD_MANAGE(PermissionPolicy.DENY), // 모드 reload/disable/enable

        // 모드 간
        MOD_IMC(PermissionPolicy.ALLOW_ALL),
        MOD_ACCESS_INTERNAL(PermissionPolicy.DENY);

        private final PermissionPolicy defaultPolicy;

        Permission(PermissionPolicy defaultPolicy) {
            this.defaultPolicy = defaultPolicy;
        }

        public PermissionPolicy getDefaultPolicy() {
            return defaultPolicy;
        }
    }

    public enum PermissionPolicy {
        ALLOW_ALL, // 항상 허용
        ASK, // 사용자 확인 필요
        DENY // 항상 거부 (명시적 부여 필요)
    }
}
