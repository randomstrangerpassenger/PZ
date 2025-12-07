package com.pulse.event.environment;

import com.pulse.event.Event;

/**
 * 날씨 변경 이벤트.
 */
public class WeatherChangeEvent extends Event {

    private final WeatherType previousWeather;
    private final WeatherType newWeather;
    private final float intensity;

    public WeatherChangeEvent(WeatherType previousWeather, WeatherType newWeather, float intensity) {
        this.previousWeather = previousWeather;
        this.newWeather = newWeather;
        this.intensity = intensity;
    }

    public WeatherType getPreviousWeather() {
        return previousWeather;
    }

    public WeatherType getNewWeather() {
        return newWeather;
    }

    public float getIntensity() {
        return intensity;
    }

    @Override
    public String getEventName() {
        return "WeatherChange";
    }

    public enum WeatherType {
        CLEAR,
        CLOUDY,
        RAIN,
        STORM,
        SNOW,
        FOG,
        BLIZZARD
    }
}
