package com.pulse.event.save;

import com.pulse.api.event.Event;

/**
 * 세이브 관련 이벤트 기본 클래스.
 */
public abstract class SaveEvent extends Event {

    private final String saveName;
    private final SaveType saveType;

    protected SaveEvent(String saveName, SaveType saveType) {
        this.saveName = saveName;
        this.saveType = saveType;
    }

    public String getSaveName() {
        return saveName;
    }

    public SaveType getSaveType() {
        return saveType;
    }

    public enum SaveType {
        WORLD, // 월드 데이터
        PLAYER, // 플레이어 데이터
        SERVER, // 서버 설정
        MOD // 모드 데이터
    }
}
