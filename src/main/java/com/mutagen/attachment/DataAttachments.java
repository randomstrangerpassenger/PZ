package com.mutagen.attachment;

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
 * </pre>
 */
public class DataAttachments {

    private static final DataAttachments INSTANCE = new DataAttachments();

    // 객체별 첨부 데이터
    // WeakHashMap을 사용하여 객체가 GC되면 자동으로 정리
    private final Map<Object, Map<AttachmentType<?>, Object>> attachments = Collections
            .synchronizedMap(new WeakHashMap<>());

    private DataAttachments() {
    }

    public static DataAttachments getInstance() {
        return INSTANCE;
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
}
