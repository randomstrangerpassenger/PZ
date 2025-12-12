package com.pulse.api;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Indicates that a method, field, or constructor has relaxed visibility
 * solely for testing purposes. Production code should not use elements
 * marked with this annotation.
 * 
 * @since 1.1.0
 */
@Retention(RetentionPolicy.SOURCE)
@Target({ ElementType.METHOD, ElementType.FIELD, ElementType.CONSTRUCTOR })
public @interface VisibleForTesting {
}
