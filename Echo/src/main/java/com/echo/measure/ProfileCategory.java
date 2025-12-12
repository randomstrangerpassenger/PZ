package com.echo.measure;

/**
 * 프로파일링 카테고리.
 * 
 * Phase 2.1: 스레드별 계측을 위한 카테고리 분류.
 * 메인 스레드 외 렌더링/네트워크/I/O 등 병목을 추적합니다.
 * 
 * @since 1.0.1
 */
public enum ProfileCategory {

    /**
     * 메인 게임 틱 (메인 스레드)
     */
    TICK_MAIN("Main Tick", Thread.currentThread().getId()),

    /**
     * 렌더링 스레드
     */
    THREAD_RENDER("Render Thread", -1),

    /**
     * 네트워크 스레드
     */
    THREAD_NETWORK("Network Thread", -1),

    /**
     * I/O 스레드 (파일, 청크 로딩)
     */
    THREAD_IO("I/O Thread", -1),

    /**
     * 워커 스레드 (백그라운드 작업)
     */
    THREAD_WORKER("Worker Thread", -1),

    /**
     * 알 수 없는/기타 스레드
     */
    THREAD_OTHER("Other Thread", -1);

    private final String displayName;
    private long associatedThreadId;

    ProfileCategory(String displayName, long associatedThreadId) {
        this.displayName = displayName;
        this.associatedThreadId = associatedThreadId;
    }

    public String getDisplayName() {
        return displayName;
    }

    public long getAssociatedThreadId() {
        return associatedThreadId;
    }

    /**
     * 현재 스레드에 맞는 카테고리 자동 감지
     */
    public static ProfileCategory fromCurrentThread() {
        Thread current = Thread.currentThread();
        String name = current.getName().toLowerCase();

        if (name.contains("render") || name.contains("lwjgl")) {
            return THREAD_RENDER;
        } else if (name.contains("network") || name.contains("netty") || name.contains("socket")) {
            return THREAD_NETWORK;
        } else if (name.contains("io") || name.contains("file") || name.contains("chunk")) {
            return THREAD_IO;
        } else if (name.contains("worker") || name.contains("pool") || name.contains("executor")) {
            return THREAD_WORKER;
        } else if (name.equals("main") || name.contains("game")) {
            return TICK_MAIN;
        }

        return THREAD_OTHER;
    }

    /**
     * 스레드 ID로 카테고리 연결
     */
    public void associateThread(long threadId) {
        this.associatedThreadId = threadId;
    }

    /**
     * 현재 스레드가 메인 스레드인지 확인
     */
    public static boolean isMainThread() {
        return fromCurrentThread() == TICK_MAIN;
    }
}
