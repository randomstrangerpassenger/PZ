package com.pulse.attachment;

import com.pulse.api.log.PulseLogger;

import com.pulse.registry.Identifier;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * 데이터 첨부 타입.
 * 게임 객체에 커스텀 데이터를 첨부하기 위한 타입 정의.
 * 
 * NeoForge의 Data Attachment와 유사한 개념.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 첨부 타입 정의
 * public static final AttachmentType<MyData> MY_DATA = AttachmentType.builder("mymod", "my_data", MyData::new)
 *         .persistent() // NBT 저장
 *         .copyOnDeath() // 사망 시 복사
 *         .build();
 * 
 * // 데이터 접근
 * MyData data = DataAttachments.get(entity, MY_DATA);
 * data.setValue(42);
 * </pre>
 * 
 * @param <T> 첨부 데이터 타입
 */
public class AttachmentType<T> {

    private final Identifier id;
    private final Supplier<T> defaultFactory;
    private final boolean persistent;
    private final boolean copyOnDeath;
    private final Serializer<T> serializer;

    // 등록된 모든 첨부 타입
    private static final Map<Identifier, AttachmentType<?>> REGISTRY = new ConcurrentHashMap<>();
    private static final String LOG = PulseLogger.PULSE;

    private AttachmentType(Identifier id, Supplier<T> defaultFactory,
            boolean persistent, boolean copyOnDeath,
            Serializer<T> serializer) {
        this.id = id;
        this.defaultFactory = defaultFactory;
        this.persistent = persistent;
        this.copyOnDeath = copyOnDeath;
        this.serializer = serializer;

        REGISTRY.put(id, this);
    }

    /**
     * 빌더 생성
     */
    public static <T> Builder<T> builder(String modId, String name, Supplier<T> defaultFactory) {
        return new Builder<>(Identifier.of(modId, name), defaultFactory);
    }

    /**
     * ID로 첨부 타입 가져오기
     */
    @SuppressWarnings("unchecked")
    public static <T> AttachmentType<T> get(Identifier id) {
        return (AttachmentType<T>) REGISTRY.get(id);
    }

    /**
     * 모든 등록된 첨부 타입
     */
    public static Collection<AttachmentType<?>> getAll() {
        return Collections.unmodifiableCollection(REGISTRY.values());
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public Identifier getId() {
        return id;
    }

    public Supplier<T> getDefaultFactory() {
        return defaultFactory;
    }

    public boolean isPersistent() {
        return persistent;
    }

    public boolean isCopyOnDeath() {
        return copyOnDeath;
    }

    public Serializer<T> getSerializer() {
        return serializer;
    }

    /**
     * 기본값 생성
     */
    public T createDefault() {
        return defaultFactory.get();
    }

    // ─────────────────────────────────────────────────────────────
    // 빌더
    // ─────────────────────────────────────────────────────────────

    public static class Builder<T> {
        private final Identifier id;
        private final Supplier<T> defaultFactory;
        private boolean persistent = false;
        private boolean copyOnDeath = false;
        private Serializer<T> serializer = null;

        private Builder(Identifier id, Supplier<T> defaultFactory) {
            this.id = id;
            this.defaultFactory = defaultFactory;
        }

        /**
         * 영구 저장 활성화
         */
        public Builder<T> persistent() {
            this.persistent = true;
            return this;
        }

        /**
         * 사망 시 복사
         */
        public Builder<T> copyOnDeath() {
            this.copyOnDeath = true;
            return this;
        }

        /**
         * 커스텀 직렬화기 설정
         */
        public Builder<T> serializer(Serializer<T> serializer) {
            this.serializer = serializer;
            return this;
        }

        public AttachmentType<T> build() {
            AttachmentType<T> type = new AttachmentType<>(
                    id, defaultFactory, persistent, copyOnDeath, serializer);
            PulseLogger.info(LOG, "[Attachment] Registered: {}", id);
            return type;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 직렬화 인터페이스
    // ─────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface Serializer<T> {
        /**
         * 객체를 Map으로 직렬화
         */
        Map<String, Object> serialize(T value);

        /**
         * Map에서 객체 복원
         */
        default T deserialize(Map<String, Object> data, Supplier<T> factory) {
            // 기본 구현: 팩토리로 새 객체 생성
            return factory.get();
        }
    }
}
