package com.pulse.api.service.echo;

public enum RenderEfficiency {
    EXCELLENT("Optimal batching and low draw calls"),
    GOOD("Good performance with minor optimization opportunities"),
    FAIR("Noticeable inefficiencies, consider optimization"),
    POOR("High draw calls or poor batching efficiency");

    private final String description;

    RenderEfficiency(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }
}
