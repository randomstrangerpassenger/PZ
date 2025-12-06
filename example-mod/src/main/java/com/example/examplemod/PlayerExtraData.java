package com.example.examplemod;

import com.pulse.attachment.AttachmentType;

/**
 * 플레이어에 첨부할 커스텀 데이터 예제.
 * 
 * DataAttachments API를 사용하여 게임 객체에 붙일 수 있습니다.
 */
public class PlayerExtraData {

    /**
     * 커스텀 데이터 첨부 타입 정의.
     * - persistent(): JSON으로 저장됨
     * - copyOnDeath(): 사망 시 새 플레이어에 복사됨
     */
    public static final AttachmentType<PlayerExtraData> TYPE = AttachmentType
            .builder("examplemod", "player_extra", PlayerExtraData::new)
            .persistent()
            .copyOnDeath()
            .build();

    // ─────────────────────────────────────────────────────────────
    // 데이터 필드
    // ─────────────────────────────────────────────────────────────

    private int killCount = 0;
    private int deathCount = 0;
    private long playTime = 0; // 틱 단위
    private String lastLocation = "";
    private boolean hasCompletedTutorial = false;

    // ─────────────────────────────────────────────────────────────
    // Getters & Setters
    // ─────────────────────────────────────────────────────────────

    public int getKillCount() {
        return killCount;
    }

    public void addKill() {
        this.killCount++;
    }

    public int getDeathCount() {
        return deathCount;
    }

    public void addDeath() {
        this.deathCount++;
    }

    public long getPlayTime() {
        return playTime;
    }

    public void incrementPlayTime() {
        this.playTime++;
    }

    public String getPlayTimeFormatted() {
        long seconds = playTime / 60;
        long minutes = seconds / 60;
        long hours = minutes / 60;
        return String.format("%02d:%02d:%02d", hours, minutes % 60, seconds % 60);
    }

    public String getLastLocation() {
        return lastLocation;
    }

    public void setLastLocation(String lastLocation) {
        this.lastLocation = lastLocation;
    }

    public boolean hasCompletedTutorial() {
        return hasCompletedTutorial;
    }

    public void setCompletedTutorial(boolean completed) {
        this.hasCompletedTutorial = completed;
    }

    @Override
    public String toString() {
        return String.format("PlayerExtraData{kills=%d, deaths=%d, playTime=%s}",
                killCount, deathCount, getPlayTimeFormatted());
    }
}
