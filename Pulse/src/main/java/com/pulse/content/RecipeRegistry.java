package com.pulse.content;

import com.pulse.api.log.PulseLogger;
import com.pulse.registry.Identifier;

import java.util.*;

/**
 * 레시피 레지스트리.
 * 제작 레시피 등록 및 관리.
 */
public class RecipeRegistry {

    private static final RecipeRegistry INSTANCE = new RecipeRegistry();
    private static final String LOG = PulseLogger.PULSE;

    private final Map<Identifier, Recipe> recipes = new LinkedHashMap<>();
    private final Map<Identifier, Set<Recipe>> byOutput = new HashMap<>();

    private RecipeRegistry() {
    }

    public static RecipeRegistry getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 레시피 등록.
     */
    public static void register(Recipe recipe) {
        INSTANCE.registerInternal(recipe);
    }

    private void registerInternal(Recipe recipe) {
        if (recipes.containsKey(recipe.getId())) {
            PulseLogger.error(LOG, "[Recipes] Duplicate recipe ID: {}", recipe.getId());
            return;
        }

        recipes.put(recipe.getId(), recipe);

        // 출력 아이템으로 인덱싱
        byOutput.computeIfAbsent(recipe.getOutput(), k -> new HashSet<>()).add(recipe);

        PulseLogger.info(LOG, "[Recipes] Registered: {}", recipe.getId());
    }

    /**
     * 레시피 제거.
     */
    public static void unregister(Identifier id) {
        Recipe recipe = INSTANCE.recipes.remove(id);
        if (recipe != null) {
            Set<Recipe> set = INSTANCE.byOutput.get(recipe.getOutput());
            if (set != null)
                set.remove(recipe);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 조회
    // ─────────────────────────────────────────────────────────────

    public static Recipe get(Identifier id) {
        return INSTANCE.recipes.get(id);
    }

    public static Set<Recipe> getRecipesFor(Identifier outputItem) {
        Set<Recipe> result = INSTANCE.byOutput.get(outputItem);
        return result != null ? Collections.unmodifiableSet(result) : Collections.emptySet();
    }

    public static Collection<Recipe> getAll() {
        return Collections.unmodifiableCollection(INSTANCE.recipes.values());
    }

    // ─────────────────────────────────────────────────────────────
    // 레시피 클래스
    // ─────────────────────────────────────────────────────────────

    public static class Recipe {
        private final Identifier id;
        private final Identifier output;
        private final int outputCount;
        private final List<Ingredient> ingredients = new ArrayList<>();
        private final List<String> requiredSkills = new ArrayList<>();
        private int craftTime = 60; // 틱
        private String category = "General";

        public Recipe(Identifier id, Identifier output) {
            this(id, output, 1);
        }

        public Recipe(Identifier id, Identifier output, int outputCount) {
            this.id = id;
            this.output = output;
            this.outputCount = outputCount;
        }

        // 빌더
        public Recipe ingredient(Identifier item, int count) {
            ingredients.add(new Ingredient(item, count, false));
            return this;
        }

        public Recipe tool(Identifier item) {
            ingredients.add(new Ingredient(item, 1, true));
            return this;
        }

        public Recipe skill(String skill) {
            requiredSkills.add(skill);
            return this;
        }

        public Recipe craftTime(int ticks) {
            this.craftTime = ticks;
            return this;
        }

        public Recipe category(String category) {
            this.category = category;
            return this;
        }

        // Getters
        public Identifier getId() {
            return id;
        }

        public Identifier getOutput() {
            return output;
        }

        public int getOutputCount() {
            return outputCount;
        }

        public List<Ingredient> getIngredients() {
            return Collections.unmodifiableList(ingredients);
        }

        public List<String> getRequiredSkills() {
            return Collections.unmodifiableList(requiredSkills);
        }

        public int getCraftTime() {
            return craftTime;
        }

        public String getCategory() {
            return category;
        }
    }

    public static class Ingredient {
        private final Identifier item;
        private final int count;
        private final boolean isTool; // 도구는 소비되지 않음

        public Ingredient(Identifier item, int count, boolean isTool) {
            this.item = item;
            this.count = count;
            this.isTool = isTool;
        }

        public Identifier getItem() {
            return item;
        }

        public int getCount() {
            return count;
        }

        public boolean isTool() {
            return isTool;
        }
    }
}
