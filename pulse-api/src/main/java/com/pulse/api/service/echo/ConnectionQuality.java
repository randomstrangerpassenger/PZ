package com.pulse.api.service.echo;

public enum ConnectionQuality {
    EXCELLENT("Excellent - Low latency, no packet loss"),
    GOOD("Good - Minor latency or occasional packet loss"),
    FAIR("Fair - Noticeable latency or packet loss"),
    POOR("Poor - High latency and significant packet loss");

    private final String description;

    ConnectionQuality(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
