package com.pulse.core;

import com.pulse.api.log.PulseLogger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Default environment for mods-folder execution.
 * Works without loader by detecting paths with robust fallbacks.
 * 
 * <p>
 * Path detection priority:
 * </p>
 * <ol>
 * <li>System property: {@code pulse.base.path}</li>
 * <li>Environment variable: {@code PULSE_BASE_PATH}</li>
 * <li>Detected PZ Zomboid folder in user home</li>
 * <li>Current working directory (if writable)</li>
 * <li>Fallback: user.home/Pulse</li>
 * </ol>
 * 
 * @since Pulse 0.9
 */
public final class DefaultCoreEnvironment implements CoreEnvironment {

    private static final String LOG = PulseLogger.PULSE;
    private static volatile DefaultCoreEnvironment instance;

    private final Path basePath;
    private final Path configPath;
    private final Path logPath;
    private final Path gamePath; // May be null

    private DefaultCoreEnvironment() {
        this.gamePath = detectGamePath();
        this.basePath = detectBasePath();
        this.configPath = basePath.resolve("Pulse");
        this.logPath = configPath.resolve("logs");

        // Ensure directories exist
        ensureDirectoryExists(configPath);
        ensureDirectoryExists(logPath);

        PulseLogger.debug(LOG, "[Environment] basePath={}, gamePath={}", basePath, gamePath);
    }

    public static DefaultCoreEnvironment getInstance() {
        if (instance == null) {
            synchronized (DefaultCoreEnvironment.class) {
                if (instance == null) {
                    instance = new DefaultCoreEnvironment();
                }
            }
        }
        return instance;
    }

    // ═══════════════════════════════════════════════════════════════
    // Path Detection with Fallbacks
    // ═══════════════════════════════════════════════════════════════

    /**
     * Detect base path for Pulse data storage.
     * This path is ALWAYS valid and writable.
     */
    private Path detectBasePath() {
        // Strategy 1: System property
        String sysProp = System.getProperty("pulse.base.path");
        if (sysProp != null) {
            Path path = Paths.get(sysProp);
            if (isValidWritablePath(path)) {
                PulseLogger.debug(LOG, "[Environment] Using pulse.base.path: {}", sysProp);
                return path;
            }
        }

        // Strategy 2: Environment variable
        String envVar = System.getenv("PULSE_BASE_PATH");
        if (envVar != null) {
            Path path = Paths.get(envVar);
            if (isValidWritablePath(path)) {
                PulseLogger.debug(LOG, "[Environment] Using PULSE_BASE_PATH: {}", envVar);
                return path;
            }
        }

        // Strategy 3: Use detected game path if available
        if (gamePath != null && isValidWritablePath(gamePath)) {
            PulseLogger.debug(LOG, "[Environment] Using detected game path: {}", gamePath);
            return gamePath;
        }

        // Strategy 4: PZ user data folder (Zomboid in user home)
        Path zomboidDir = getZomboidUserDir();
        if (zomboidDir != null && isValidWritablePath(zomboidDir)) {
            PulseLogger.debug(LOG, "[Environment] Using Zomboid user dir: {}", zomboidDir);
            return zomboidDir;
        }

        // Strategy 5: Safe fallback - user home
        Path fallback = Paths.get(System.getProperty("user.home"), "Pulse");
        PulseLogger.warn(LOG, "[Environment] Using fallback path: {}", fallback);
        return fallback;
    }

    /**
     * Detect actual game installation path (best effort).
     * May return null if detection fails.
     */
    private static Path detectGamePath() {
        // Strategy 1: System property
        String sysProp = System.getProperty("pulse.game.path");
        if (sysProp != null && looksLikeGamePath(Paths.get(sysProp))) {
            return Paths.get(sysProp);
        }

        // Strategy 2: Environment variable
        String envVar = System.getenv("PZ_GAME_PATH");
        if (envVar != null && looksLikeGamePath(Paths.get(envVar))) {
            return Paths.get(envVar);
        }

        // Strategy 3: Current working directory
        Path userDir = Paths.get(System.getProperty("user.dir"));
        if (looksLikeGamePath(userDir)) {
            return userDir;
        }

        // Strategy 4: Common Steam paths
        Path steamPath = findSteamGamePath();
        if (steamPath != null) {
            return steamPath;
        }

        return null; // Game path not detected
    }

    /**
     * Check if path looks like a PZ game installation.
     * Uses minimal markers to avoid false negatives.
     */
    private static boolean looksLikeGamePath(Path path) {
        if (path == null || !Files.exists(path))
            return false;

        // Check for at least one PZ marker
        return Files.exists(path.resolve("media"))
                || Files.exists(path.resolve("ProjectZomboid64.exe"))
                || Files.exists(path.resolve("ProjectZomboid64.bat"))
                || Files.exists(path.resolve("ProjectZomboid64"))
                || Files.exists(path.resolve("projectzomboid")); // Linux lowercase
    }

    /**
     * Get PZ user data directory (Zomboid folder in user home).
     */
    private static Path getZomboidUserDir() {
        String userHome = System.getProperty("user.home");

        // Windows: C:\Users\<user>\Zomboid
        // Linux/Mac: ~/Zomboid
        Path zomboidDir = Paths.get(userHome, "Zomboid");
        if (Files.exists(zomboidDir)) {
            return zomboidDir;
        }

        return null;
    }

    /**
     * Find game in common Steam installation paths.
     */
    private static Path findSteamGamePath() {
        String os = System.getProperty("os.name", "").toLowerCase();
        String userHome = System.getProperty("user.home");

        Path[] steamPaths;
        if (os.contains("win")) {
            steamPaths = new Path[] {
                    Paths.get("C:", "Program Files (x86)", "Steam", "steamapps", "common", "ProjectZomboid"),
                    Paths.get("C:", "Program Files", "Steam", "steamapps", "common", "ProjectZomboid"),
                    Paths.get("D:", "SteamLibrary", "steamapps", "common", "ProjectZomboid"),
                    Paths.get("E:", "SteamLibrary", "steamapps", "common", "ProjectZomboid")
            };
        } else if (os.contains("mac")) {
            steamPaths = new Path[] {
                    Paths.get(userHome, "Library", "Application Support", "Steam", "steamapps", "common",
                            "ProjectZomboid")
            };
        } else {
            steamPaths = new Path[] {
                    Paths.get(userHome, ".steam", "steam", "steamapps", "common", "ProjectZomboid"),
                    Paths.get(userHome, ".local", "share", "Steam", "steamapps", "common", "ProjectZomboid")
            };
        }

        for (Path path : steamPaths) {
            if (looksLikeGamePath(path)) {
                return path;
            }
        }

        return null;
    }

    private static boolean isValidWritablePath(Path path) {
        if (path == null)
            return false;

        try {
            if (!Files.exists(path)) {
                // Try to create it
                Files.createDirectories(path);
            }
            return Files.isWritable(path);
        } catch (Exception e) {
            return false;
        }
    }

    private void ensureDirectoryExists(Path dir) {
        try {
            if (!Files.exists(dir)) {
                Files.createDirectories(dir);
                PulseLogger.debug(LOG, "[Environment] Created directory: {}", dir);
            }
        } catch (Exception e) {
            PulseLogger.warn(LOG, "[Environment] Failed to create directory {}: {}",
                    dir, e.getMessage());
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // CoreEnvironment Implementation
    // ═══════════════════════════════════════════════════════════════

    @Override
    public Path getBasePath() {
        return basePath;
    }

    @Override
    public Path getConfigPath() {
        return configPath;
    }

    @Override
    public Path getLogPath() {
        return logPath;
    }

    @Override
    public Path getGamePath() {
        return gamePath;
    }

    @Override
    public boolean isServer() {
        return System.getProperty("zomboid.server") != null
                || "true".equalsIgnoreCase(System.getProperty("pulse.server"));
    }

    @Override
    public boolean isDebugMode() {
        return Boolean.getBoolean("pulse.debug");
    }

    // For testing
    static void resetInstance() {
        instance = null;
    }
}
