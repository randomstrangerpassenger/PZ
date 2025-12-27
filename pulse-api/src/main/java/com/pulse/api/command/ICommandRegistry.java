package com.pulse.api.command;

import java.util.Collection;
import java.util.function.Consumer;

/**
 * 명령어 레지스트리 인터페이스.
 * 명령어 등록 및 실행 관리.
 * 
 * @since Pulse 2.0
 */
public interface ICommandRegistry {

    /**
     * 람다 기반 명령어 등록
     * 
     * @param name        명령어 이름
     * @param description 설명
     * @param executor    실행 핸들러
     */
    void register(String name, String description, Consumer<ICommandContext> executor);

    /**
     * 명령어 등록 해제
     * 
     * @param name 명령어 이름
     */
    void unregister(String name);

    /**
     * 명령어 존재 확인
     * 
     * @param name 명령어 이름
     * @return 존재 여부
     */
    boolean hasCommand(String name);

    /**
     * 모든 명령어 이름 가져오기
     */
    Collection<String> getCommandNames();

    /**
     * 명령어 접두사 가져오기
     */
    String getPrefix();
}
