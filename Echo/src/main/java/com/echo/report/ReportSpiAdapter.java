package com.echo.report;

import com.pulse.api.spi.IProviderRegistry;
import com.pulse.api.spi.IStabilizerSnapshotProvider;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * SPI/Fuse Provider 접근 어댑터.
 * 
 * v4 Phase 3: ReportDataCollector에서 분리.
 * Pulse SPI를 통한 Stabilizer 스냅샷 수집 책임.
 * 
 * @since Echo 0.8.0
 */
public class ReportSpiAdapter {

    private static final ReportSpiAdapter INSTANCE = new ReportSpiAdapter();

    private ReportSpiAdapter() {
    }

    public static ReportSpiAdapter getInstance() {
        return INSTANCE;
    }

    /**
     * Fuse 딥 분석 데이터 수집.
     * 
     * @return 분석 결과 Map
     */
    public Map<String, Object> generateFuseDeepAnalysis() {
        Map<String, Object> result = new LinkedHashMap<>();

        // === Step 1: SPI 가용성 확인 ===
        IProviderRegistry registry = null;
        try {
            registry = com.pulse.api.Pulse.getProviderRegistry();
        } catch (Exception e) {
            result.put("spi_available", false);
            result.put("error_code", "REGISTRY_UNAVAILABLE");
            result.put("error_message", e.getMessage());
            result.put("providers", createEmptyFuseEntry("REGISTRY_UNAVAILABLE", e.getMessage()));
            return result;
        }

        result.put("spi_available", true);

        // === Step 2: Provider 수집 ===
        Map<String, Object> providers = new LinkedHashMap<>();
        providers.put("fuse", collectStabilizerSnapshot(registry, "fuse"));
        result.put("providers", providers);

        return result;
    }

    /**
     * 개별 Stabilizer 스냅샷 수집 (no-throw).
     * 
     * Bundle B 핵심: "0 분해"를 위해 present/active/snapshot_ok 필드 보장.
     */
    public Map<String, Object> collectStabilizerSnapshot(IProviderRegistry registry, String stabilizerId) {
        Map<String, Object> snapshot = new LinkedHashMap<>();

        // === Step 1: Provider 목록 조회 ===
        List<IStabilizerSnapshotProvider> matchingProviders;
        try {
            matchingProviders = registry.getAllProviders().stream()
                    .filter(p -> p instanceof IStabilizerSnapshotProvider)
                    .filter(p -> stabilizerId.equals(p.getId()))
                    .map(p -> (IStabilizerSnapshotProvider) p)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            return createErrorSnapshot(false, "REGISTRY_QUERY_FAILED", e.getMessage());
        }

        // === Step 2: 중복 ID 감지 ===
        if (matchingProviders.size() > 1) {
            snapshot.put("present", true);
            return addErrorFields(snapshot, "DUPLICATE_PROVIDER_ID",
                    "Found " + matchingProviders.size() + " providers with id: " + stabilizerId);
        }

        // === Step 3: Provider 미존재 ===
        if (matchingProviders.isEmpty()) {
            return createErrorSnapshot(false, "PROVIDER_MISSING",
                    "No provider registered with id: " + stabilizerId);
        }

        // === Step 4: Provider 존재 - 스냅샷 캡처 ===
        IStabilizerSnapshotProvider provider = matchingProviders.get(0);

        snapshot.put("present", true);
        snapshot.put("provider_name", provider.getName());
        snapshot.put("provider_version", provider.getVersion());

        try {
            snapshot.put("provider_status", provider.getProviderStatus().name());
        } catch (Exception e) {
            snapshot.put("provider_status", "UNKNOWN");
        }

        // 스냅샷 캡처
        try {
            Map<String, Object> captured = provider.captureSnapshot();
            if (captured != null) {
                Map<String, Object> filtered = new LinkedHashMap<>(captured);
                filtered.remove("present"); // Echo가 결정하므로 제거
                snapshot.putAll(filtered);
            } else {
                return addErrorFields(snapshot, "SNAPSHOT_NULL", "Provider returned null snapshot");
            }
        } catch (Exception e) {
            return addErrorFields(snapshot, "SNAPSHOT_THROWN", e.getMessage());
        }

        normalizeRequiredKeys(snapshot);
        return snapshot;
    }

    /**
     * 필수 키 정규화 - Provider가 누락해도 리포트 일관성 보장.
     */
    public void normalizeRequiredKeys(Map<String, Object> snapshot) {
        if (!snapshot.containsKey("active")) {
            snapshot.put("active", false);
        }
        if (!snapshot.containsKey("snapshot_ok")) {
            snapshot.put("snapshot_ok", false);
            if (!snapshot.containsKey("error_code") || "".equals(snapshot.get("error_code"))) {
                snapshot.put("error_code", "SNAPSHOT_MALFORMED");
            }
        }
        if (!snapshot.containsKey("error_code")) {
            snapshot.put("error_code", "");
        }
        if (!snapshot.containsKey("total_interventions")) {
            snapshot.put("total_interventions", 0L);
        }
        if (!snapshot.containsKey("reason_counts")) {
            snapshot.put("reason_counts", Collections.emptyMap());
        }
    }

    /**
     * 에러 스냅샷 생성 헬퍼.
     */
    public Map<String, Object> createErrorSnapshot(boolean present, String errorCode, String errorMessage) {
        Map<String, Object> snapshot = new LinkedHashMap<>();
        snapshot.put("present", present);
        snapshot.put("active", false);
        snapshot.put("snapshot_ok", false);
        snapshot.put("error_code", errorCode);
        snapshot.put("error_message", errorMessage != null ? errorMessage : "");
        snapshot.put("total_interventions", 0L);
        snapshot.put("reason_counts", Collections.emptyMap());
        return snapshot;
    }

    /**
     * 기존 스냅샷에 에러 필드 추가 헬퍼.
     */
    public Map<String, Object> addErrorFields(Map<String, Object> snapshot, String errorCode, String errorMessage) {
        snapshot.put("active", false);
        snapshot.put("snapshot_ok", false);
        snapshot.put("error_code", errorCode);
        snapshot.put("error_message", errorMessage != null ? errorMessage : "");
        snapshot.put("total_interventions", 0L);
        snapshot.put("reason_counts", Collections.emptyMap());
        return snapshot;
    }

    /**
     * 빈 fuse 엔트리 생성 (registry 자체 실패 시).
     */
    public Map<String, Object> createEmptyFuseEntry(String errorCode, String errorMessage) {
        Map<String, Object> providers = new LinkedHashMap<>();
        Map<String, Object> fuse = new LinkedHashMap<>();
        fuse.put("present", false);
        fuse.put("active", false);
        fuse.put("snapshot_ok", false);
        fuse.put("error_code", errorCode);
        fuse.put("error_message", errorMessage != null ? errorMessage : "");
        fuse.put("total_interventions", 0L);
        fuse.put("reason_counts", Collections.emptyMap());
        providers.put("fuse", fuse);
        return providers;
    }
}
