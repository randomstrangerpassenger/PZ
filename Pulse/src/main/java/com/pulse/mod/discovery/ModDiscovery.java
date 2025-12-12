package com.pulse.mod.discovery;

import com.google.gson.Gson;
import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModMetadata;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

/**
 * Handles discovery of mods from the mods directory.
 */
public class ModDiscovery {
    private static final String LOG = PulseLogger.PULSE;
    private final Path modsDirectory;
    private final Gson gson;

    public ModDiscovery(Path modsDirectory, Gson gson) {
        this.modsDirectory = modsDirectory;
        this.gson = gson;
    }

    public Map<String, ModContainer> discoverMods() {
        Map<String, ModContainer> mods = new LinkedHashMap<>();

        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "Discovering mods...");

        ensureDirectoryExists();
        scanJarFiles(mods);

        PulseLogger.info(LOG, "Discovered {} mod(s)", mods.size());
        PulseLogger.info(LOG, "═══════════════════════════════════════");

        return mods;
    }

    private void ensureDirectoryExists() {
        try {
            if (!Files.exists(modsDirectory)) {
                Files.createDirectories(modsDirectory);
                PulseLogger.info(LOG, "Created mods directory");
            }
        } catch (IOException e) {
            PulseLogger.error(LOG, "Failed to create mods directory: {}", e.getMessage());
        }
    }

    private void scanJarFiles(Map<String, ModContainer> mods) {
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(modsDirectory, "*.jar")) {
            for (Path jarPath : stream) {
                try {
                    discoverMod(jarPath, mods);
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Failed to load mod: {}", jarPath.getFileName());
                    e.printStackTrace();
                }
            }
        } catch (IOException e) {
            PulseLogger.error(LOG, "Failed to scan mods directory: {}", e.getMessage());
        }
    }

    private void discoverMod(Path jarPath, Map<String, ModContainer> mods) throws Exception {
        PulseLogger.debug(LOG, "Scanning: {}", jarPath.getFileName());

        try (JarFile jar = new JarFile(jarPath.toFile())) {
            JarEntry metadataEntry = jar.getJarEntry("pulse.mod.json");

            if (metadataEntry == null) {
                PulseLogger.debug(LOG, "  - No pulse.mod.json found, skipping");
                return;
            }

            ModMetadata metadata;
            try (InputStream is = jar.getInputStream(metadataEntry);
                    InputStreamReader reader = new InputStreamReader(is)) {
                metadata = gson.fromJson(reader, ModMetadata.class);
            }

            if (metadata.getId() == null || metadata.getId().isEmpty()) {
                PulseLogger.error(LOG, "  - Invalid mod: missing 'id' field");
                return;
            }

            if (mods.containsKey(metadata.getId())) {
                PulseLogger.error(LOG, "  - Duplicate mod ID: {}", metadata.getId());
                return;
            }

            metadata.setSourceFile(jarPath.toAbsolutePath().toString());

            URL jarUrl = jarPath.toUri().toURL();
            URLClassLoader classLoader = new URLClassLoader(
                    new URL[] { jarUrl },
                    getClass().getClassLoader());

            ModContainer container = new ModContainer(metadata, classLoader);
            container.setState(ModContainer.ModState.METADATA_LOADED);

            mods.put(metadata.getId(), container);

            PulseLogger.info(LOG, "  ✓ {}", metadata);
        }
    }
}
