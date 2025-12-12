package com.pulse.mod;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

/**
 * ModLoader 단위 테스트.
 */
@Tag("unit")
class ModLoaderTest {

    @Test
    void getInstance_returnsSameInstance() {
        ModLoader instance1 = ModLoader.getInstance();
        ModLoader instance2 = ModLoader.getInstance();
        assertSame(instance1, instance2, "ModLoader should be singleton");
    }

    @Test
    void getModsDirectory_returnsValidPath() {
        ModLoader loader = ModLoader.getInstance();
        Path modsDir = loader.getModsDirectory();

        assertNotNull(modsDir, "Mods directory should not be null");
        assertTrue(modsDir.toString().endsWith("mods"), "Should end with 'mods'");
    }

    @Test
    void getMod_returnsNullForUnknown() {
        ModLoader loader = ModLoader.getInstance();
        ModContainer result = loader.getMod("nonexistent-mod-id");

        assertNull(result, "Should return null for unknown mod ID");
    }

    @Test
    void isModLoaded_returnsFalseForUnknown() {
        ModLoader loader = ModLoader.getInstance();
        boolean loaded = loader.isModLoaded("unknown-mod");

        assertFalse(loaded, "Unknown mod should not be loaded");
    }

    @Test
    void getModCount_returnsNonNegative() {
        ModLoader loader = ModLoader.getInstance();
        int count = loader.getModCount();

        assertTrue(count >= 0, "Mod count should be non-negative");
    }

    @Test
    void getAllMods_returnsCollection() {
        ModLoader loader = ModLoader.getInstance();
        var mods = loader.getAllMods();

        assertNotNull(mods, "getAllMods should return non-null collection");
    }

    @Test
    void getLoadOrder_returnsUnmodifiableList() {
        ModLoader loader = ModLoader.getInstance();
        var loadOrder = loader.getLoadOrder();

        assertNotNull(loadOrder, "getLoadOrder should return non-null list");
        assertThrows(UnsupportedOperationException.class, () -> {
            loadOrder.clear();
        }, "Load order should be unmodifiable");
    }
}
