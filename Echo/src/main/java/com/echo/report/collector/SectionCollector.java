package com.echo.report.collector;

import java.util.Map;

/**
 * 리포트 섹션 수집기 인터페이스.
 * 
 * <p>
 * 각 섹션(Summary, Spikes, Fuse 등)은 이 인터페이스를 구현하여
 * ReportPipeline에서 조합됩니다.
 * </p>
 * 
 * <h2>설계 원칙 (Phase 1-A)</h2>
 * <ul>
 * <li>Collector는 상태를 갖지 않음 (stateless)</li>
 * <li>ReportContext에서 불변 스냅샷만 읽음</li>
 * <li>collect()에서 새 Map 반환</li>
 * </ul>
 * 
 * @since Echo 2.1.0
 */
public interface SectionCollector {

    /**
     * 섹션 키 반환 (리포트 JSON에서 사용).
     * 
     * @return 섹션 키 (예: "summary", "spikes")
     */
    String getSectionKey();

    /**
     * 섹션 데이터 수집.
     * 
     * @param context 불변 리포트 컨텍스트
     * @return 섹션 데이터 (never null)
     */
    Map<String, Object> collect(ReportContext context);

    /**
     * 이 섹션이 활성화되어야 하는지 여부.
     * 
     * @param context 리포트 컨텍스트
     * @return 활성화 여부 (기본: true)
     */
    default boolean isEnabled(ReportContext context) {
        return true;
    }

    /**
     * 섹션 우선순위 (낮을수록 먼저 실행).
     * 
     * @return 우선순위 (기본: 100)
     */
    default int getPriority() {
        return 100;
    }
}
