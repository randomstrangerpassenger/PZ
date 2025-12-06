package com.mutagen.input;

import com.mutagen.event.EventBus;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 키 바인딩 레지스트리.
 * 모든 키 바인딩을 관리하고 입력 처리.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 키 바인딩 생성 및 등록
 * KeyBinding openMenu = KeyBinding.create("mymod", "open_menu")
 *         .defaultKey(KeyCode.KEY_M)
 *         .category("My Mod")
 *         .build();
 * 
 * KeyBindingRegistry.register(openMenu);
 * 
 * // 사용 (매 틱)
 * if (openMenu.wasPressed()) {
 *     openMyMenu();
 * }
 * </pre>
 */
public class KeyBindingRegistry {

    private static final KeyBindingRegistry INSTANCE = new KeyBindingRegistry();

    // 등록된 키 바인딩
    private final Map<String, KeyBinding> bindings = new ConcurrentHashMap<>();

    // 카테고리별 바인딩
    private final Map<String, List<KeyBinding>> byCategory = new ConcurrentHashMap<>();

    // 현재 키 상태
    private final Set<Integer> pressedKeys = ConcurrentHashMap.newKeySet();
    private boolean ctrlPressed = false;
    private boolean shiftPressed = false;
    private boolean altPressed = false;

    private KeyBindingRegistry() {
    }

    public static KeyBindingRegistry getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 정적 편의 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 키 바인딩 등록
     */
    public static void register(KeyBinding binding) {
        INSTANCE.registerBinding(binding);
    }

    /**
     * 키 바인딩 가져오기
     */
    public static KeyBinding get(String modId, String id) {
        return INSTANCE.getBinding(modId + ":" + id);
    }

    /**
     * 모든 키 바인딩
     */
    public static Collection<KeyBinding> getAll() {
        return INSTANCE.getAllBindings();
    }

    /**
     * 카테고리별 키 바인딩
     */
    public static List<KeyBinding> getByCategory(String category) {
        return INSTANCE.getBindingsByCategory(category);
    }

    // ─────────────────────────────────────────────────────────────
    // 인스턴스 메서드
    // ─────────────────────────────────────────────────────────────

    public void registerBinding(KeyBinding binding) {
        String fullId = binding.getFullId();

        if (bindings.containsKey(fullId)) {
            System.err.println("[Mutagen/Input] Duplicate keybinding: " + fullId);
            return;
        }

        bindings.put(fullId, binding);
        byCategory.computeIfAbsent(binding.getCategory(), k -> new ArrayList<>())
                .add(binding);

        System.out.println("[Mutagen/Input] Registered keybinding: " + fullId +
                " (" + binding + ")");
    }

    public KeyBinding getBinding(String fullId) {
        return bindings.get(fullId);
    }

    public Collection<KeyBinding> getAllBindings() {
        return Collections.unmodifiableCollection(bindings.values());
    }

    public List<KeyBinding> getBindingsByCategory(String category) {
        return byCategory.getOrDefault(category, Collections.emptyList());
    }

    public Set<String> getCategories() {
        return Collections.unmodifiableSet(byCategory.keySet());
    }

    // ─────────────────────────────────────────────────────────────
    // 입력 처리 (Mixin에서 호출)
    // ─────────────────────────────────────────────────────────────

    /**
     * 키 프레스 이벤트 처리
     */
    public void onKeyPress(int keyCode, boolean ctrl, boolean shift, boolean alt) {
        // 수정자 키 상태 업데이트
        this.ctrlPressed = ctrl;
        this.shiftPressed = shift;
        this.altPressed = alt;

        pressedKeys.add(keyCode);

        // 매칭되는 키 바인딩 업데이트
        for (KeyBinding binding : bindings.values()) {
            if (binding.matches(keyCode, ctrl, shift, alt)) {
                binding.updateState(true);
            }
        }

        // KeyEvent 발생
        EventBus.post(new KeyEvent(KeyEvent.Type.PRESS, keyCode, ctrl, shift, alt));
    }

    /**
     * 키 릴리즈 이벤트 처리
     */
    public void onKeyRelease(int keyCode, boolean ctrl, boolean shift, boolean alt) {
        this.ctrlPressed = ctrl;
        this.shiftPressed = shift;
        this.altPressed = alt;

        pressedKeys.remove(keyCode);

        // 매칭되는 키 바인딩 업데이트
        for (KeyBinding binding : bindings.values()) {
            if (binding.getKeyCode() == keyCode) {
                binding.updateState(false);
            }
        }

        // KeyEvent 발생
        EventBus.post(new KeyEvent(KeyEvent.Type.RELEASE, keyCode, ctrl, shift, alt));
    }

    /**
     * 특정 키가 현재 눌려있는지 확인
     */
    public boolean isKeyPressed(int keyCode) {
        return pressedKeys.contains(keyCode);
    }

    public boolean isCtrlPressed() {
        return ctrlPressed;
    }

    public boolean isShiftPressed() {
        return shiftPressed;
    }

    public boolean isAltPressed() {
        return altPressed;
    }

    /**
     * 모든 상태 리셋 (포커스 손실 시 등)
     */
    public void resetAll() {
        pressedKeys.clear();
        ctrlPressed = false;
        shiftPressed = false;
        altPressed = false;

        for (KeyBinding binding : bindings.values()) {
            binding.updateState(false);
            binding.resetPressCount();
        }
    }
}
