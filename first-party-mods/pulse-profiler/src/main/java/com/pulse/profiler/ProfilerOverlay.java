package com.pulse.profiler;

import com.pulse.debug.DebugOverlayRenderer;
import com.pulse.debug.DebugRenderContext;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * 프로파일러 디버그 오버레이.
 * 현재 활성화된 프로파일링 섹션의 실시간 통계를 표시.
 */
public class ProfilerOverlay implements DebugOverlayRenderer {

    @Override
    public void render(DebugRenderContext ctx) {
        if (!ProfilerConfig.enabled) {
            ctx.drawLine("Profiler: Disabled");
            return;
        }

        Collection<ProfileSection> sections = PulseProfiler.getAllSections();
        if (sections.isEmpty()) {
            ctx.drawLine("Profiler: No data");
            return;
        }

        ctx.drawLine("Profiler Stats (" + sections.size() + " sections)");

        // 평균 시간 기준 정렬
        List<ProfileSection> sorted = new ArrayList<>(sections);
        sorted.sort((a, b) -> Long.compare(b.getAverageNanos(), a.getAverageNanos()));

        // 상위 10개만 표시
        int count = 0;
        for (ProfileSection section : sorted) {
            if (count++ >= 10)
                break;

            if (section.getCallCount() == 0)
                continue;

            String line = String.format("%s: %.2fms (max: %.2fms)",
                    section.getName(),
                    section.getAverageMs(),
                    section.getMaxNanos() / 1_000_000.0);

            ctx.drawLine(line);
        }
    }
}
