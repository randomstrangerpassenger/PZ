package com.pulse.mixin;

import com.pulse.api.DevMode;
import com.pulse.api.mixin.MixinInjectionValidator;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Mixin 진단 도구.
 * 적용된 Mixin 추적 및 잠재적 충돌 감지.
 * 
 * DevMode가 활성화되면 상세한 리포트 출력.
 */
public class MixinDiagnostics {

    private static final MixinDiagnostics INSTANCE = new MixinDiagnostics();

    // 타겟 클래스 → 적용된 Mixin 정보 목록
    private final Map<String, List<MixinInfo>> appliedMixins = new ConcurrentHashMap<>();

    // 로드 실패한 Mixin 목록
    private final List<FailedMixin> failedMixins = new ArrayList<>();

    public static MixinDiagnostics getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // Mixin 추적
    // ─────────────────────────────────────────────────────────────

    /**
     * Mixin 적용 기록
     */
    public void recordMixinApplied(String targetClass, String mixinClass,
            String modId, int priority) {
        long startTime = System.currentTimeMillis();
        MixinInfo info = new MixinInfo(mixinClass, modId, priority);
        appliedMixins.computeIfAbsent(targetClass, k -> new ArrayList<>()).add(info);
        long elapsed = System.currentTimeMillis() - startTime;

        // v1.0.1: MixinInjectionValidator에도 성공 기록
        try {
            MixinInjectionValidator.recordSuccess(mixinClass, targetClass, elapsed);
        } catch (Exception e) {
            // ignore - Validator가 초기화되지 않았을 수 있음
        }

        if (DevMode.isEnabled()) {
            System.out.println("[Pulse/Mixin] Applied " + mixinClass +
                    " to " + targetClass + " (mod: " + modId + ", priority: " + priority + ")");
        }
    }

    /**
     * Mixin 실패 기록
     */
    public void recordMixinFailed(String mixinClass, String modId,
            String targetClass, String reason) {
        FailedMixin failed = new FailedMixin(mixinClass, modId, targetClass, reason);
        failedMixins.add(failed);

        // v1.0.1: MixinInjectionValidator에도 실패 기록
        try {
            MixinInjectionValidator.recordFailure(mixinClass, targetClass, reason);
        } catch (Exception e) {
            // ignore - Validator가 초기화되지 않았을 수 있음
        }

        System.err.println("[Pulse/Mixin] Failed " + mixinClass + " from " + modId +
                " to " + targetClass + ": " + reason);
    }

    // ─────────────────────────────────────────────────────────────
    // 충돌 감지
    // ─────────────────────────────────────────────────────────────

    /**
     * 잠재적 충돌 검사 및 경고
     */
    public void checkConflicts() {
        if (!DevMode.isEnabled())
            return;

        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");
        System.out.println("[Pulse/Mixin] Checking for potential Mixin conflicts...");

        int conflictCount = 0;

        for (Map.Entry<String, List<MixinInfo>> entry : appliedMixins.entrySet()) {
            String targetClass = entry.getKey();
            List<MixinInfo> mixins = entry.getValue();

            if (mixins.size() > 1) {
                // 동일 타겟에 여러 Mixin - 잠재적 충돌
                Set<String> mods = new HashSet<>();
                for (MixinInfo info : mixins) {
                    mods.add(info.modId);
                }

                if (mods.size() > 1) {
                    // 다른 모드의 Mixin이 같은 클래스를 수정
                    System.out.println("[Pulse/Mixin] Potential conflict on " + targetClass + ":");
                    for (MixinInfo info : mixins) {
                        System.out.println("[Pulse/Mixin]   - " + info.modId +
                                ": " + info.mixinClass + " (priority: " + info.priority + ")");
                    }
                    conflictCount++;
                }
            }
        }

        if (conflictCount == 0) {
            System.out.println("[Pulse/Mixin] No conflicts detected.");
        } else {
            System.out.println("[Pulse/Mixin] " + conflictCount + " potential conflict(s) found.");
        }

        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");
    }

    // ─────────────────────────────────────────────────────────────
    // 리포트
    // ─────────────────────────────────────────────────────────────

    /**
     * 전체 Mixin 적용 상태 리포트
     */
    public void printReport() {
        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");
        System.out.println("[Pulse/Mixin] MIXIN APPLICATION REPORT");
        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");

        System.out.println("[Pulse/Mixin] Applied Mixins by Target:");
        for (Map.Entry<String, List<MixinInfo>> entry : appliedMixins.entrySet()) {
            System.out.println("[Pulse/Mixin]   " + entry.getKey() + ":");
            for (MixinInfo info : entry.getValue()) {
                System.out.println("[Pulse/Mixin]     - " + info.mixinClass +
                        " (" + info.modId + ", p=" + info.priority + ")");
            }
        }

        if (!failedMixins.isEmpty()) {
            System.out.println("[Pulse/Mixin] Failed Mixins:");
            for (FailedMixin failed : failedMixins) {
                System.out.println("[Pulse/Mixin]   ✗ " + failed.mixinClass +
                        " from " + failed.modId + " → " + failed.targetClass);
                System.out.println("[Pulse/Mixin]     Reason: " + failed.reason);
            }
        }

        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public int getAppliedCount() {
        return appliedMixins.values().stream().mapToInt(List::size).sum();
    }

    public int getFailedCount() {
        return failedMixins.size();
    }

    public List<MixinInfo> getMixinsForTarget(String targetClass) {
        return appliedMixins.getOrDefault(targetClass, Collections.emptyList());
    }

    /**
     * 크래시 리포트용 변환 상세 정보 반환.
     * 
     * @return 타겟 클래스 → Mixin 클래스 목록 맵
     */
    public static Map<String, List<String>> getTransformationDetails() {
        Map<String, List<String>> result = new LinkedHashMap<>();

        for (Map.Entry<String, List<MixinInfo>> entry : INSTANCE.appliedMixins.entrySet()) {
            List<String> mixinNames = new ArrayList<>();
            for (MixinInfo info : entry.getValue()) {
                mixinNames.add(info.mixinClass + " (" + info.modId + ")");
            }
            result.put(entry.getKey(), mixinNames);
        }

        return result;
    }

    /**
     * 적용된 Mixin 목록 문자열로 반환.
     */
    public static List<String> getAppliedMixins() {
        List<String> result = new ArrayList<>();
        for (Map.Entry<String, List<MixinInfo>> entry : INSTANCE.appliedMixins.entrySet()) {
            for (MixinInfo info : entry.getValue()) {
                result.add(info.mixinClass + " → " + entry.getKey() + " (" + info.modId + ")");
            }
        }
        return result;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    public static class MixinInfo {
        public final String mixinClass;
        public final String modId;
        public final int priority;

        public MixinInfo(String mixinClass, String modId, int priority) {
            this.mixinClass = mixinClass;
            this.modId = modId;
            this.priority = priority;
        }
    }

    public static class FailedMixin {
        public final String mixinClass;
        public final String modId;
        public final String targetClass;
        public final String reason;

        public FailedMixin(String mixinClass, String modId,
                String targetClass, String reason) {
            this.mixinClass = mixinClass;
            this.modId = modId;
            this.targetClass = targetClass;
            this.reason = reason;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 통계 메서드 (평가 개선사항)
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드별 적용된 Mixin 수 반환.
     * 
     * @return 모드 ID → Mixin 수 맵
     */
    public Map<String, Integer> getMixinCountByMod() {
        Map<String, Integer> counts = new HashMap<>();
        for (List<MixinInfo> infos : appliedMixins.values()) {
            for (MixinInfo info : infos) {
                counts.merge(info.modId, 1, (a, b) -> a + b);
            }
        }
        return counts;
    }

    /**
     * 가장 많이 Mixin이 적용된 클래스 TOP N 반환.
     * 
     * @param n 반환할 개수
     * @return (클래스명, Mixin 수) 리스트
     */
    public List<Map.Entry<String, Integer>> getTopMixedClasses(int n) {
        List<Map.Entry<String, Integer>> entries = new ArrayList<>();
        for (Map.Entry<String, List<MixinInfo>> entry : appliedMixins.entrySet()) {
            entries.add(new AbstractMap.SimpleEntry<>(entry.getKey(), entry.getValue().size()));
        }
        entries.sort((a, b) -> Integer.compare(b.getValue(), a.getValue()));
        return entries.subList(0, Math.min(n, entries.size()));
    }

    /**
     * 동일 타겟, 동일 모드 내에서 우선순위 충돌 검사.
     * 같은 모드에서 같은 타겟에 다른 우선순위의 Mixin이 있으면 경고.
     */
    public void checkPriorityConflicts() {
        if (!DevMode.isEnabled())
            return;

        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");
        System.out.println("[Pulse/Mixin] Checking priority conflicts...");

        int conflictCount = 0;

        for (Map.Entry<String, List<MixinInfo>> entry : appliedMixins.entrySet()) {
            String targetClass = entry.getKey();
            List<MixinInfo> mixins = entry.getValue();

            // 같은 모드 내 우선순위별 그룹화
            Map<String, List<Integer>> modPriorities = new HashMap<>();
            for (MixinInfo info : mixins) {
                modPriorities.computeIfAbsent(info.modId, k -> new ArrayList<>()).add(info.priority);
            }

            // 같은 모드에서 여러 우선순위 있으면 경고
            for (Map.Entry<String, List<Integer>> modEntry : modPriorities.entrySet()) {
                List<Integer> priorities = modEntry.getValue();
                if (priorities.size() > 1) {
                    Set<Integer> uniquePriorities = new HashSet<>(priorities);
                    if (uniquePriorities.size() > 1) {
                        System.out.println("[Pulse/Mixin] Priority variation in " + modEntry.getKey() +
                                " for " + targetClass + ": " + uniquePriorities);
                        conflictCount++;
                    }
                }
            }
        }

        if (conflictCount == 0) {
            System.out.println("[Pulse/Mixin] No priority conflicts detected.");
        } else {
            System.out.println("[Pulse/Mixin] " + conflictCount + " priority variation(s) found.");
        }

        System.out.println("[Pulse/Mixin] ═══════════════════════════════════════");
    }

    /**
     * 전체 진단 실행 (충돌 + 우선순위 검사).
     */
    public void runFullDiagnostics() {
        printReport();
        checkConflicts();
        checkPriorityConflicts();
    }
}
