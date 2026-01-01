package com.echo.analysis;

import java.util.*;

/**
 * 최적화 우선순위 DTO.
 * 
 * @since Echo 1.0.1
 */
public class OptimizationPriority {

    public final String targetName;
    public final String displayName;
    public final int priority;
    public final String recommendation;

    public OptimizationPriority(String targetName, String displayName, int priority, String recommendation) {
        this.targetName = targetName;
        this.displayName = displayName;
        this.priority = priority;
        this.recommendation = recommendation;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("target", targetName);
        map.put("display_name", displayName);
        map.put("priority", priority);
        map.put("recommendation", recommendation);
        return map;
    }
}
