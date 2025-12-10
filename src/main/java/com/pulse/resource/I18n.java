package com.pulse.resource;

import com.pulse.registry.Identifier;

import java.util.*;

/**
 * 번역/다국어 지원.
 * 모드의 번역 문자열을 관리.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 번역 로드
 * I18n.loadLanguage("mymod", "ko_kr");
 * 
 * // 번역 사용
 * String text = I18n.translate("mymod.item.cool_item.name");
 * String formatted = I18n.translate("mymod.message.welcome", playerName);
 * </pre>
 */
public class I18n {

    private static final I18n INSTANCE = new I18n();

    // 현재 언어
    private String currentLanguage = "en_us";

    // 로드된 번역 (modId -> key -> translation)
    private final Map<String, Map<String, String>> translations = new HashMap<>();

    // 폴백 번역 (영어)
    private final Map<String, Map<String, String>> fallback = new HashMap<>();

    private I18n() {
    }

    public static I18n getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 언어 설정
    // ─────────────────────────────────────────────────────────────

    /**
     * 현재 언어 설정
     */
    public static void setLanguage(String language) {
        INSTANCE.currentLanguage = language.toLowerCase();
        INSTANCE.reloadAllTranslations();
    }

    /**
     * 현재 언어 가져오기
     */
    public static String getLanguage() {
        return INSTANCE.currentLanguage;
    }

    // ─────────────────────────────────────────────────────────────
    // 번역 로드
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드의 번역 파일 로드
     */
    public static void loadLanguage(String modId, String language) {
        INSTANCE.loadTranslations(modId, language, false);
    }

    /**
     * 모드의 현재 언어 번역 로드
     */
    public static void loadLanguage(String modId) {
        INSTANCE.loadTranslations(modId, INSTANCE.currentLanguage, false);
        // 폴백으로 영어도 로드
        if (!INSTANCE.currentLanguage.equals("en_us")) {
            INSTANCE.loadTranslations(modId, "en_us", true);
        }
    }

    private void loadTranslations(String modId, String language, boolean isFallback) {
        Identifier langId = Identifier.of(modId, "lang/" + language + ".json");
        String json = ResourceLoader.loadString(langId);

        if (json == null) {
            // .properties 파일도 시도
            langId = Identifier.of(modId, "lang/" + language + ".properties");
            Properties props = ResourceLoader.loadProperties(langId);
            if (props != null) {
                Map<String, String> map = new HashMap<>();
                for (String key : props.stringPropertyNames()) {
                    map.put(key, props.getProperty(key));
                }
                if (isFallback) {
                    fallback.put(modId, map);
                } else {
                    translations.put(modId, map);
                }
                return;
            }
            return;
        }

        // JSON 파싱 (간단한 구현)
        Map<String, String> map = parseSimpleJson(json);
        if (isFallback) {
            fallback.put(modId, map);
        } else {
            translations.put(modId, map);
        }
    }

    private Map<String, String> parseSimpleJson(String json) {
        Map<String, String> result = new HashMap<>();
        // 간단한 JSON 파싱 ({"key": "value"} 형식)
        json = json.trim();
        if (json.startsWith("{") && json.endsWith("}")) {
            json = json.substring(1, json.length() - 1);
            String[] pairs = json.split(",");
            for (String pair : pairs) {
                int colonIdx = pair.indexOf(':');
                if (colonIdx > 0) {
                    String key = pair.substring(0, colonIdx).trim();
                    String value = pair.substring(colonIdx + 1).trim();
                    // 따옴표 제거
                    key = stripQuotes(key);
                    value = stripQuotes(value);
                    result.put(key, value);
                }
            }
        }
        return result;
    }

    private String stripQuotes(String s) {
        if ((s.startsWith("\"") && s.endsWith("\"")) ||
                (s.startsWith("'") && s.endsWith("'"))) {
            return s.substring(1, s.length() - 1);
        }
        return s;
    }

    private void reloadAllTranslations() {
        Set<String> modIds = new HashSet<>(translations.keySet());
        translations.clear();
        for (String modId : modIds) {
            loadLanguage(modId);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 번역 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * 키를 번역
     */
    public static String translate(String key) {
        return INSTANCE.getTranslation(key);
    }

    /**
     * 키를 번역하고 포맷팅
     */
    public static String translate(String key, Object... args) {
        String translation = INSTANCE.getTranslation(key);
        if (args.length > 0) {
            try {
                return String.format(translation, args);
            } catch (Exception e) {
                return translation;
            }
        }
        return translation;
    }

    /**
     * 번역이 존재하는지 확인
     */
    public static boolean hasTranslation(String key) {
        return INSTANCE.translationExists(key);
    }

    private String getTranslation(String key) {
        // modId 추출 시도
        String modId = extractModId(key);

        // 현재 언어에서 찾기
        Map<String, String> modTranslations = translations.get(modId);
        if (modTranslations != null && modTranslations.containsKey(key)) {
            return modTranslations.get(key);
        }

        // 폴백에서 찾기
        Map<String, String> modFallback = fallback.get(modId);
        if (modFallback != null && modFallback.containsKey(key)) {
            return modFallback.get(key);
        }

        // 번역 없음 - 키 반환
        return key;
    }

    private boolean translationExists(String key) {
        String modId = extractModId(key);
        Map<String, String> modTranslations = translations.get(modId);
        if (modTranslations != null && modTranslations.containsKey(key)) {
            return true;
        }
        Map<String, String> modFallback = fallback.get(modId);
        return modFallback != null && modFallback.containsKey(key);
    }

    private String extractModId(String key) {
        int dotIdx = key.indexOf('.');
        if (dotIdx > 0) {
            return key.substring(0, dotIdx);
        }
        return "Pulse";
    }
}
