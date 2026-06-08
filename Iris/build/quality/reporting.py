"""Quality gate build report generation (JSON + Markdown)."""
from collections import Counter
from datetime import datetime, timezone

from quality.config import QUALITY_GATES_VERSION


def generate_build_report(gates: dict, decisions: dict, overlay: dict) -> dict:
    """Build report JSON 생성."""
    stats = Counter(d["decision"] for d in decisions.values())
    by_ft = overlay.get("by_fulltype", {})
    strong = sum(1 for e in by_ft.values()
                 if e.get("uniqueness_summary") == "STRONG_ONLY")
    weak = sum(1 for e in by_ft.values()
               if e.get("uniqueness_summary") == "WEAK_ONLY")
    mixed = sum(1 for e in by_ft.values()
                if e.get("uniqueness_summary") == "MIXED")

    overall = "PASS" if all(
        g["status"] == "PASS" for g in gates.values()
    ) else "FAIL"

    report = {
        "version": QUALITY_GATES_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gates": gates,
        "statistics": {
            "total_items": len(decisions),
            "PASS": stats.get("PASS", 0),
            "NO": stats.get("NO", 0),
            "REVIEW": stats.get("REVIEW", 0),
            "STRONG": strong,
            "WEAK": weak,
            "MIXED": mixed,
        },
        "overall": overall,
    }
    return report


def generate_build_report_md(report: dict) -> str:
    """Build report Markdown 생성."""
    lines = []
    lines.append(f"# Build Report — Quality Gates {QUALITY_GATES_VERSION}")
    lines.append("")
    lines.append(f"**Timestamp**: {report['timestamp']}")
    lines.append(f"**Overall**: {'✅ PASS' if report['overall'] == 'PASS' else '❌ FAIL'}")
    lines.append("")

    lines.append("## Gate Results")
    lines.append("")
    lines.append("| Gate | Status | Details |")
    lines.append("|------|--------|---------|")

    gate_labels = {
        "Q1_pass_integrity": "Q1: PASS 무결성",
        "Q2_strong_integrity": "Q2: Strong 무결성",
        "Q3_anchor_completeness": "Q3: Anchor 완전성",
        "Q4_determinism": "Q4: 결정성",
        "Q5_regression_diff": "Q5: 회귀 diff",
    }

    for gid, label in gate_labels.items():
        gate = report["gates"].get(gid)
        if gate is None:
            lines.append(f"| {label} | ⏭ SKIP | not run |")
            continue
        icon = "✅" if gate["status"] == "PASS" else "❌"
        # Build detail string
        detail_parts = []
        for k, v in gate.items():
            if k in ("status", "details", "warnings"):
                continue
            detail_parts.append(f"{k}={v}")
        detail_str = ", ".join(detail_parts) if detail_parts else "-"
        lines.append(f"| {label} | {icon} {gate['status']} | {detail_str} |")

    lines.append("")
    lines.append("## Statistics")
    lines.append("")
    stats = report["statistics"]
    lines.append(f"- Total items: {stats['total_items']}")
    lines.append(f"- PASS: {stats['PASS']}, NO: {stats['NO']}, REVIEW: {stats['REVIEW']}")
    lines.append(f"- STRONG: {stats['STRONG']}, WEAK: {stats['WEAK']}, MIXED: {stats['MIXED']}")
    lines.append("")

    # Show violations if any
    any_violations = False
    for gid, gate in report["gates"].items():
        details = gate.get("details", [])
        warnings_list = gate.get("warnings", [])
        if details:
            if not any_violations:
                lines.append("## Violations")
                lines.append("")
                any_violations = True
            lines.append(f"### {gate_labels.get(gid, gid)}")
            lines.append("")
            for d in details:
                lines.append(f"- ❌ {d}")
            lines.append("")
        if warnings_list:
            if not any_violations:
                lines.append("## Warnings")
                lines.append("")
                any_violations = True
            lines.append(f"### {gate_labels.get(gid, gid)} (warnings)")
            lines.append("")
            for w in warnings_list:
                lines.append(f"- ⚠️ {w}")
            lines.append("")

    return "\n".join(lines)
