package com.pulse.api.command;

/**
 * 명령어 실행 컨텍스트 인터페이스.
 * 명령어 핸들러에 전달되는 정보.
 * 
 * @since Pulse 2.0
 */
public interface ICommandContext {

    /**
     * 명령어 이름
     */
    String getCommandName();

    /**
     * 원본 인자 배열
     */
    String[] getRawArgs();

    /**
     * 인자 개수
     */
    int getArgCount();

    /**
     * 인자가 있는지 확인
     */
    boolean hasArg(int index);

    /**
     * 인덱스로 인자 가져오기
     */
    String getArg(int index);

    /**
     * 인덱스로 인자 가져오기 (기본값)
     */
    String getArg(int index, String defaultValue);

    /**
     * 응답 전송
     */
    void reply(String message);

    /**
     * 에러 응답 전송
     */
    void replyError(String message);
}
