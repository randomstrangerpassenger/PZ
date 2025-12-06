package com.mutagen.service;

import org.spongepowered.asm.service.IClassTracker;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * 클래스 로딩 상태를 추적하는 서비스.
 */
public class MutagenClassTracker implements IClassTracker {

    private final Set<String> loadedClasses = Collections.synchronizedSet(new HashSet<>());
    private final Set<String> invalidClasses = Collections.synchronizedSet(new HashSet<>());

    // IClassTracker 메서드들 - @Override 없이 구현
    
    public void registerClass(String name) {
        loadedClasses.add(name);
    }

    public boolean isClassLoaded(String name) {
        return loadedClasses.contains(name);
    }

    public String getClassRestrictions(String className) {
        if (loadedClasses.contains(className)) {
            return "already loaded";
        }
        if (invalidClasses.contains(className)) {
            return "invalid class";
        }
        return "";
    }

    public void registerInvalidClass(String name) {
        invalidClasses.add(name);
    }

    // Mutagen 내부용 메서드
    
    public Set<String> getLoadedClasses() {
        return Collections.unmodifiableSet(loadedClasses);
    }

    public int countLoadedWithPrefix(String prefix) {
        return (int) loadedClasses.stream()
            .filter(n -> n.startsWith(prefix))
            .count();
    }
}
