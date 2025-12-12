package com.pulse.content;

import com.pulse.api.log.PulseLogger;
import com.pulse.registry.Identifier;
import com.google.gson.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/**
 * JSON 기반 데이터 로더.
 * 아이템, 레시피 등을 JSON 파일에서 로드.
 */
public class DataLoader {
    private static final String LOG = PulseLogger.PULSE;

    @SuppressWarnings("unused") // Reserved for future JSON serialization
    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    // ─────────────────────────────────────────────────────────────
    // 아이템 로딩
    // ─────────────────────────────────────────────────────────────

    /**
     * 디렉토리에서 모든 아이템 JSON 로드.
     */
    public static int loadItems(Path directory) throws IOException {
        int count = 0;

        if (!Files.exists(directory)) {
            PulseLogger.warn(LOG, "[Data] Items directory not found: {}", directory);
            return 0;
        }

        try (var stream = Files.walk(directory)) {
            for (Path path : (Iterable<Path>) stream.filter(p -> p.toString().endsWith(".json"))::iterator) {
                try {
                    ItemDefinition item = loadItem(path);
                    if (item != null) {
                        ItemRegistry.register(item);
                        count++;
                    }
                } catch (Exception e) {
                    PulseLogger.error(LOG, "[Data] Failed to load item: {}", path, e);
                }
            }
        }

        PulseLogger.info(LOG, "[Data] Loaded {} items from {}", count, directory);
        return count;
    }

    /**
     * 단일 아이템 JSON 로드.
     */
    public static ItemDefinition loadItem(Path path) throws IOException {
        String json = Files.readString(path, StandardCharsets.UTF_8);
        JsonObject obj = JsonParser.parseString(json).getAsJsonObject();

        String idStr = getOrDefault(obj, "id", path.getFileName().toString().replace(".json", ""));
        Identifier id = Identifier.parse(idStr);

        ItemDefinition item = new ItemDefinition(id)
                .name(getOrDefault(obj, "name", id.getPath()))
                .description(getOrDefault(obj, "description", ""))
                .icon(getOrDefault(obj, "icon", null))
                .weight(getFloatOrDefault(obj, "weight", 1.0f))
                .maxStack(getIntOrDefault(obj, "maxStackSize", 1));

        // 타입
        if (obj.has("type")) {
            item.type(ItemDefinition.ItemType.valueOf(obj.get("type").getAsString().toUpperCase()));
        }

        // 카테고리
        if (obj.has("category")) {
            item.category(ItemDefinition.ItemCategory.valueOf(obj.get("category").getAsString().toUpperCase()));
        }

        // 태그
        if (obj.has("tags") && obj.get("tags").isJsonArray()) {
            for (JsonElement tag : obj.getAsJsonArray("tags")) {
                item.tag(tag.getAsString());
            }
        }

        // 커스텀 속성
        if (obj.has("properties") && obj.get("properties").isJsonObject()) {
            for (var entry : obj.getAsJsonObject("properties").entrySet()) {
                item.property(entry.getKey(), jsonToValue(entry.getValue()));
            }
        }

        return item;
    }

    // ─────────────────────────────────────────────────────────────
    // 레시피 로딩
    // ─────────────────────────────────────────────────────────────

    /**
     * 디렉토리에서 모든 레시피 JSON 로드.
     */
    public static int loadRecipes(Path directory) throws IOException {
        int count = 0;

        if (!Files.exists(directory)) {
            PulseLogger.warn(LOG, "[Data] Recipes directory not found: {}", directory);
            return 0;
        }

        try (var stream = Files.walk(directory)) {
            for (Path path : (Iterable<Path>) stream.filter(p -> p.toString().endsWith(".json"))::iterator) {
                try {
                    RecipeRegistry.Recipe recipe = loadRecipe(path);
                    if (recipe != null) {
                        RecipeRegistry.register(recipe);
                        count++;
                    }
                } catch (Exception e) {
                    PulseLogger.error(LOG, "[Data] Failed to load recipe: {}", path, e);
                }
            }
        }

        PulseLogger.info(LOG, "[Data] Loaded {} recipes from {}", count, directory);
        return count;
    }

    /**
     * 단일 레시피 JSON 로드.
     */
    public static RecipeRegistry.Recipe loadRecipe(Path path) throws IOException {
        String json = Files.readString(path, StandardCharsets.UTF_8);
        JsonObject obj = JsonParser.parseString(json).getAsJsonObject();

        String idStr = getOrDefault(obj, "id", path.getFileName().toString().replace(".json", ""));
        Identifier id = Identifier.parse(idStr);

        Identifier output = Identifier.parse(obj.get("output").getAsString());
        int outputCount = getIntOrDefault(obj, "outputCount", 1);

        RecipeRegistry.Recipe recipe = new RecipeRegistry.Recipe(id, output, outputCount)
                .craftTime(getIntOrDefault(obj, "craftTime", 60))
                .category(getOrDefault(obj, "category", "General"));

        // 재료
        if (obj.has("ingredients") && obj.get("ingredients").isJsonArray()) {
            for (JsonElement elem : obj.getAsJsonArray("ingredients")) {
                JsonObject ing = elem.getAsJsonObject();
                Identifier item = Identifier.parse(ing.get("item").getAsString());
                int count = getIntOrDefault(ing, "count", 1);
                boolean isTool = getBoolOrDefault(ing, "tool", false);

                if (isTool) {
                    recipe.tool(item);
                } else {
                    recipe.ingredient(item, count);
                }
            }
        }

        // 필요 스킬
        if (obj.has("skills") && obj.get("skills").isJsonArray()) {
            for (JsonElement skill : obj.getAsJsonArray("skills")) {
                recipe.skill(skill.getAsString());
            }
        }

        return recipe;
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    private static String getOrDefault(JsonObject obj, String key, String defaultVal) {
        return obj.has(key) ? obj.get(key).getAsString() : defaultVal;
    }

    private static int getIntOrDefault(JsonObject obj, String key, int defaultVal) {
        return obj.has(key) ? obj.get(key).getAsInt() : defaultVal;
    }

    private static float getFloatOrDefault(JsonObject obj, String key, float defaultVal) {
        return obj.has(key) ? obj.get(key).getAsFloat() : defaultVal;
    }

    private static boolean getBoolOrDefault(JsonObject obj, String key, boolean defaultVal) {
        return obj.has(key) ? obj.get(key).getAsBoolean() : defaultVal;
    }

    private static Object jsonToValue(JsonElement elem) {
        if (elem.isJsonPrimitive()) {
            JsonPrimitive prim = elem.getAsJsonPrimitive();
            if (prim.isBoolean())
                return prim.getAsBoolean();
            if (prim.isNumber())
                return prim.getAsNumber();
            return prim.getAsString();
        }
        return elem.toString();
    }
}
