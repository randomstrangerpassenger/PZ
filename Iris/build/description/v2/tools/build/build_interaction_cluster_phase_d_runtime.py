from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.export_dvf_3_3_lua_bridge import export_lua_bridge
from tools.build.validate_interaction_cluster_phase_d_runtime import build_phase_d_runtime_report

STAGING_DIR = ROOT / "staging" / "interaction_cluster" / "phase_d_runtime"
CHECKLIST_PATH = STAGING_DIR / "phase_d_in_game_checklist.md"


def write_checklist(path: Path = CHECKLIST_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Phase D In-Game Checklist",
                "",
                "1. Enable the `Iris` mod in the Project Zomboid mod list.",
                "2. Start or load a save with inventory access.",
                "3. Acquire one of the known bridge items:",
                "   - Base.TinOpener",
                "   - Base.WeldingTorch",
                "   - Base.ModKit",
                "4. Open the inventory context menu on the item and confirm `Iris: View More` appears.",
                "5. Open the Iris panel and verify the item opens in `IrisWikiPanel`.",
                "6. Confirm the 3-3 body text is sentence-form, not a recipe/material list.",
                "7. Use the browser search to switch between at least two bridged items.",
                "8. Reopen the panel once to confirm second-run behavior is stable.",
                "",
                "Expected current scope:",
                "- This workspace currently bridges the rendered batch in `dvf_3_3_rendered.json`.",
                "- The current rendered batch is sample-sized; runtime hookup is the Phase D target here.",
            ]
        ),
        encoding="utf-8",
    )
    return path


def build_phase_d_runtime() -> dict:
    bridge_report = export_lua_bridge()
    runtime_report = build_phase_d_runtime_report(
        bridge_report_path=Path(bridge_report["report_path"]),
    )
    checklist_path = write_checklist()
    return {
        "bridge_report": bridge_report,
        "runtime_report": runtime_report,
        "checklist_path": str(checklist_path),
    }


def main() -> int:
    payload = build_phase_d_runtime()
    print("phase d runtime built:", payload["runtime_report"]["overall_status"])
    return 0 if payload["runtime_report"]["overall_status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
