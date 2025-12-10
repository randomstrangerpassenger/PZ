package com.pulse.mod;

/**
 * 모드 엔트리포인트 인터페이스.
 * 모든 Pulse 모드는 이 인터페이스를 구현해야 함.
 * 
 * 예시:
 * public class MyMod implements PulseMod {
 *     @Override
 *     public void onInitialize() {
 *         System.out.println("My mod loaded!");
 *         // 이벤트 리스너 등록, 설정 로드 등
 *     }
 * }
 */
public interface PulseMod {
    
    /**
     * 모드 초기화 시 호출됨.
     * 이벤트 리스너 등록, 설정 로드 등을 수행.
     */
    void onInitialize();
    
    /**
     * 모드가 언로드될 때 호출됨 (선택적 구현).
     * 리소스 정리 등을 수행.
     */
    default void onUnload() {
        // 기본 구현: 아무것도 안 함
    }
    
    /**
     * 게임 월드가 로드된 후 호출됨 (선택적 구현).
     */
    default void onWorldLoad() {
        // 기본 구현: 아무것도 안 함
    }
    
    /**
     * 게임 월드가 언로드될 때 호출됨 (선택적 구현).
     */
    default void onWorldUnload() {
        // 기본 구현: 아무것도 안 함
    }
}
