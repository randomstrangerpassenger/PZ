package com.mutagen.attachment;

import com.google.gson.*;
import com.mutagen.registry.Identifier;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 데이터 첨부 관리자.
 * 게임 객체에 커스텀 데이터를 첨부하고 관리.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 엔티티에 데이터 첨부
 * MyData data = DataAttachments.get(entity, MY_DATA);
 * 
 * // 데이터 설정
 * DataAttachments.set(entity, MY_DATA, newData);
 * 
 * // 데이터 제거
 * DataAttachments.remove(entity, MY_DATA);
 * 
 * // 존재 여부 확인
 * if (DataAttachments.has(entity, MY_DATA)) { ... }
 * 
 * // 영구 데이터 저장
 * DataAttachments.save(entity, "player_data.json");
 * 
 * // 영구 데이터 로드
 * DataAttachments.load(entity, "player_data.json");
 * </pre>
 */
public class DataAttachments {

    private static final DataAttachments INSTANCE = new DataAttachments();

    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .serializeNulls()
            .create();

    // 객체별 첨부 데이터
    // WeakHashMap을 사용하여 객체가 GC되면 자동으로 정리
    private final Map<Object, Map<AttachmentType<?>, Object>> attachments = Collections
            .synchronizedMap(new WeakHashMap<>());

    // 영구 저장용 디렉토리
    private Path saveDirectory;

    private DataAttachments() {
        String gameDir = System.getProperty("user.dir");
        this.saveDirectory = Paths.get(gameDir, "mutagen", "attachments");
    }

    public static DataAttachments getInstance() {
        return INSTANCE;
    }

    /**
     * 저장 디렉토리 설정
     */
    public static void setSaveDirectory(Path directory) {
        INSTANCE.saveDirectory = directory;
    }

    public static Path getSaveDirectory() {
        return INSTANCE.saveDirectory;
    }

    // ─────────────────────────────────────────────────────────────
    // 데이터 접근
    // ─────────────────────────────────────────────────────────────

    /**
     * 첨부 데이터 가져오기 (없으면 생성)
     */
    public static <T> T get(Object holder, AttachmentType<T> type) {
        return INSTANCE.getData(holder, type);
    }

    /**
     * 첨부 데이터 가져오기 (Optional)
     */
    public static <T> Optional<T> getOptional(Object holder, AttachmentType<T> type) {
        return INSTANCE.getDataOptional(holder, type);
    }

    /**
     * 첨부 데이터 설정
     */
    public static <T> void set(Object holder, AttachmentType<T> type, T value) {
        INSTANCE.setData(holder, type, value);
    }

    /**
     * 첨부 데이터 제거
     */
    public static <T> void remove(Object holder, AttachmentType<T> type) {
        INSTANCE.removeData(holder, type);
    }

    /**
     * 첨부 데이터 존재 여부
     */
    public static <T> boolean has(Object holder, AttachmentType<T> type) {
        return INSTANCE.hasData(holder, type);
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 구현
    // ─────────────────────────────────────────────────────────────

    @SuppressWarnings("unchecked")
    private <T> T getData(Object holder, AttachmentType<T> type) {
        Map<AttachmentType<?>, Object> holderData = attachments.computeIfAbsent(
                holder, k -> new ConcurrentHashMap<>());

        return (T) holderData.computeIfAbsent(type, t -> type.createDefault());
    }

    @SuppressWarnings("unchecked")
    private <T> Optional<T> getDataOptional(Object holder, AttachmentType<T> type) {
        Map<AttachmentType<?>, Object> holderData = attachments.get(holder);
        if (holderData == null)
            return Optional.empty();
        return Optional.ofNullable((T) holderData.get(type));
    }

    private <T> void setData(Object holder, AttachmentType<T> type, T value) {
        Map<AttachmentType<?>, Object> holderData = attachments.computeIfAbsent(
                holder, k -> new ConcurrentHashMap<>());
        holderData.put(type, value);
    }

    private <T> void removeData(Object holder, AttachmentType<T> type) {
        Map<AttachmentType<?>, Object> holderData = attachments.get(holder);
        if (holderData != null) {
            holderData.remove(type);
        }
    }

    private <T> boolean hasData(Object holder, AttachmentType<T> type) {
        Map<AttachmentType<?>, Object> holderData = attachments.get(holder);
        return holderData != null && holderData.containsKey(type);
    }

    // ─────────────────────────────────────────────────────────────
    // 복사/이전
    // ─────────────────────────────────────────────────────────────

    /**
     * 한 객체에서 다른 객체로 모든 첨부 데이터 복사
     */
    public static void copyAll(Object from, Object to) {
        INSTANCE.copyAllData(from, to);
    }

    /**
     * copyOnDeath가 설정된 첨부 데이터만 복사 (사망 시 사용)
     */
    public static void copyOnDeath(Object from, Object to) {
        INSTANCE.copyDeathData(from, to);
    }

    private void copyAllData(Object from, Object to) {
        Map<AttachmentType<?>, Object> fromData = attachments.get(from);
        if (fromData == null || fromData.isEmpty())
            return;

        Map<AttachmentType<?>, Object> toData = attachments.computeIfAbsent(
                to, k -> new ConcurrentHashMap<>());
        toData.putAll(fromData);
    }

    private void copyDeathData(Object from, Object to) {
        Map<AttachmentType<?>, Object> fromData = attachments.get(from);
        if (fromData == null || fromData.isEmpty())
            return;

        Map<AttachmentType<?>, Object> toData = attachments.computeIfAbsent(
                to, k -> new ConcurrentHashMap<>());

        for (Map.Entry<AttachmentType<?>, Object> entry : fromData.entrySet()) {
            if (entry.getKey().isCopyOnDeath()) {
                toData.put(entry.getKey(), entry.getValue());
            }
        }
    }

    /**
     * 객체의 모든 첨부 데이터 제거
     */
    public static void clearAll(Object holder) {
        INSTANCE.attachments.remove(holder);
    }

    /**
     * 첨부 데이터 통계
     */
    public static int getAttachmentCount() {
        return INSTANCE.attachments.size();
    }

    // ─────────────────────────────────────────────────────────────
    // 직렬화/역직렬화
    // ─────────────────────────────────────────────────────────────

    /**
     * 객체의 영구 첨부 데이터를 JSON 파일로 저장.
     * 
     * @param holder   데이터 홀더 객체
     * @param filename 저장할 파일명 (예: "player_123.json")
     * @return 저장 성공 여부
     */
    public static boolean save(Object holder, String filename) {
        return INSTANCE.saveToFile(holder, filename);
    }

    /**
     * JSON 파일에서 영구 첨부 데이터를 로드.
     * 
     * @param holder   데이터 홀더 객체
     * @param filename 로드할 파일명
     * @return 로드 성공 여부
     */
    public static boolean load(Object holder, String filename) {
        return INSTANCE.loadFromFile(holder, filename);
    }

    /**
     * 모든 영구 첨부 데이터를 저장.
     * 각 객체는 hashCode 기반 파일명으로 저장됨.
     */
    public static void saveAll() {
        INSTANCE.saveAllPersistent();
    }

    @SuppressWarnings("unchecked")
    private boolean saveToFile(Object holder, String filename) {
        Map<AttachmentType<?>, Object> holderData = attachments.get(holder);
        if (holderData == null || holderData.isEmpty()) {
            return true; // 저장할 데이터 없음
        }

        try {
            // 디렉토리 생성
            Files.createDirectories(saveDirectory);

            Path filePath = saveDirectory.resolve(filename);

            // 영구 저장 가능한 데이터만 필터링
            JsonObject root = new JsonObject();
            root.addProperty("_version", "1.0");
            root.addProperty("_timestamp", System.currentTimeMillis());

            JsonObject dataObj = new JsonObject();

            for (Map.Entry<AttachmentType<?>, Object> entry : holderData.entrySet()) {
                AttachmentType<?> type = entry.getKey();

                if (!type.isPersistent()) {
                    continue;
                }

                Object value = entry.getValue();
                String key = type.getId().toString();

                // 직렬화
                AttachmentType.Serializer<Object> serializer = (AttachmentType.Serializer<Object>) type.getSerializer();

                if (serializer != null) {
                    // 커스텀 직렬화기 사용
                    Map<String, Object> serialized = serializer.serialize(value);
                    dataObj.add(key, GSON.toJsonTree(serialized));
                } else {
                    // 기본 GSON 직렬화
                    dataObj.add(key, GSON.toJsonTree(value));
                }
            }

            root.add("data", dataObj);

            // 파일에 쓰기
            String json = GSON.toJson(root);
            Files.writeString(filePath, json, StandardCharsets.UTF_8);

            System.out.println("[Mutagen/Attachment] Saved: " + filePath.getFileName());
            return true;

        } catch (Exception e) {
            System.err.println("[Mutagen/Attachment] Failed to save: " + filename);
            e.printStackTrace();
            return false;
        }
    }

    @SuppressWarnings("unchecked")
    private boolean loadFromFile(Object holder, String filename) {
        Path filePath = saveDirectory.resolve(filename);

        if (!Files.exists(filePath)) {
            return true; // 파일 없음 = 새 데이터
        }

        try {
            String json = Files.readString(filePath, StandardCharsets.UTF_8);
            JsonObject root = JsonParser.parseString(json).getAsJsonObject();

            if (!root.has("data")) {
                return true;
            }

            JsonObject dataObj = root.getAsJsonObject("data");

            Map<AttachmentType<?>, Object> holderData = attachments.computeIfAbsent(
                    holder, k -> new ConcurrentHashMap<>());

            for (String key : dataObj.keySet()) {
                Identifier id = Identifier.parse(key);
                AttachmentType<?> type = AttachmentType.get(id);

                if (type == null) {
                    System.err.println("[Mutagen/Attachment] Unknown type: " + key);
                    continue;
                }

                JsonElement element = dataObj.get(key);

                AttachmentType.Serializer<Object> serializer = (AttachmentType.Serializer<Object>) type.getSerializer();

                Object value;
                if (serializer != null) {
                    // 커스텀 역직렬화
                    Map<String, Object> map = GSON.fromJson(element, Map.class);
                    value = serializer.deserialize(map, (java.util.function.Supplier<Object>) type.getDefaultFactory());
                } else {
                    // GSON으로 직접 역직렬화 시도
                    // 기본 팩토리로 새 객체 생성 후 필드 복사
                    value = type.createDefault();
                    if (element.isJsonObject()) {
                        // 리플렉션으로 필드 복사
                        copyJsonToObject(element.getAsJsonObject(), value);
                    }
                }

                holderData.put(type, value);
            }

            System.out.println("[Mutagen/Attachment] Loaded: " + filePath.getFileName());
            return true;

        } catch (Exception e) {
            System.err.println("[Mutagen/Attachment] Failed to load: " + filename);
            e.printStackTrace();
            return false;
        }
    }

    private void copyJsonToObject(JsonObject json, Object target) {
        try {
            for (java.lang.reflect.Field field : target.getClass().getDeclaredFields()) {
                if (java.lang.reflect.Modifier.isStatic(field.getModifiers())) {
                    continue;
                }

                String fieldName = field.getName();
                if (!json.has(fieldName)) {
                    continue;
                }

                field.setAccessible(true);
                JsonElement element = json.get(fieldName);

                Class<?> fieldType = field.getType();
                Object value = GSON.fromJson(element, fieldType);
                field.set(target, value);
            }
        } catch (Exception e) {
            System.err.println("[Mutagen/Attachment] Failed to copy JSON to object: " + e.getMessage());
        }
    }

    private void saveAllPersistent() {
        int saved = 0;
        for (Map.Entry<Object, Map<AttachmentType<?>, Object>> entry : attachments.entrySet()) {
            Object holder = entry.getKey();

            // holder의 고유 식별자 생성
            String filename = "holder_" + System.identityHashCode(holder) + ".json";

            if (saveToFile(holder, filename)) {
                saved++;
            }
        }
        System.out.println("[Mutagen/Attachment] Saved " + saved + " holder(s)");
    }

    /**
     * 특정 파일 삭제
     */
    public static boolean delete(String filename) {
        try {
            Path filePath = INSTANCE.saveDirectory.resolve(filename);
            return Files.deleteIfExists(filePath);
        } catch (IOException e) {
            return false;
        }
    }
}
