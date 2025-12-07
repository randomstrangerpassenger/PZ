package com.pulse.event.environment;

import com.pulse.event.Event;

/**
 * 게임 내 시간 변경 이벤트.
 */
public class TimeChangeEvent extends Event {

    private final int hour;
    private final int minute;
    private final int day;
    private final int month;
    private final int year;

    public TimeChangeEvent(int hour, int minute, int day, int month, int year) {
        this.hour = hour;
        this.minute = minute;
        this.day = day;
        this.month = month;
        this.year = year;
    }

    public int getHour() {
        return hour;
    }

    public int getMinute() {
        return minute;
    }

    public int getDay() {
        return day;
    }

    public int getMonth() {
        return month;
    }

    public int getYear() {
        return year;
    }

    public boolean isDawn() {
        return hour >= 5 && hour < 7;
    }

    public boolean isDay() {
        return hour >= 7 && hour < 19;
    }

    public boolean isDusk() {
        return hour >= 19 && hour < 21;
    }

    public boolean isNight() {
        return hour >= 21 || hour < 5;
    }

    @Override
    public String getEventName() {
        return "TimeChange";
    }
}
