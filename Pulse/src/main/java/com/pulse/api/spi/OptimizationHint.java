package com.pulse.api.spi;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Optimization hint from analysis providers.
 * Used by optimization modules to determine targets.
 * 
 * @since Pulse 1.1.0
 */
public class OptimizationHint {

    public final String targetName;
    public final String displayName;
    public final int priority;
    public final String recommendation;
    public final String category;

    public OptimizationHint(String targetName, String displayName, int priority, String recommendation,
            String category) {
        this.targetName = targetName;
        this.displayName = displayName;
        this.priority = priority;
        this.recommendation = recommendation;
        this.category = category;
    }

    public OptimizationHint(String targetName, String displayName, int priority, String recommendation) {
        this(targetName, displayName, priority, recommendation, "GENERAL");
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("target", targetName);
        map.put("display_name", displayName);
        map.put("priority", priority);
        map.put("recommendation", recommendation);
        map.put("category", category);
        return map;
    }
}
