import json
import hashlib
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BUILD_DIR.parent / "output"
EXPECTED_DIFF_PATH = BUILD_DIR / "data" / "v2.4" / "expected_diff.json"
USECASES_PATH = OUTPUT_DIR / "usecases_by_fulltype.v2.4.json"

def main():
    ed = json.loads(EXPECTED_DIFF_PATH.read_text("utf-8"))

    # Recompute usecase hash
    usecases_data = json.loads(USECASES_PATH.read_text("utf-8"))
    uc_fulltypes = usecases_data.get("fulltypes", {})
    uc_entries = sorted(
        (ft, sorted(uc["use_case_id"] for uc in info["use_cases"]))
        for ft, info in uc_fulltypes.items()
    )
    ed["frozen_usecase_count"] = len(uc_entries)
    ed["frozen_usecase_hash"] = hashlib.sha256(json.dumps(uc_entries).encode("utf-8")).hexdigest()

    # Recompute new metrics manually here to inject them before quality_gates is even run
    rc_ev_ft = 0
    rc_ev_lines = 0
    rc_ex_ft = 0
    rc_ex_lines = 0
    rec_ev_ft = 0

    for ft, info in uc_fulltypes.items():
        ft_has_rc_ev = False
        ft_has_rc_ex = False
        ft_has_rec_ev = False
        for uc in info.get("use_cases", []):
            is_recipe = any(s["source_type"] == "recipe_evidence" for s in uc.get("evidence_sources", []))
            is_rc = any(s["source_type"] == "rightclick" for s in uc.get("evidence_sources", []))
            kind = uc.get("line_kind")
            if is_recipe: ft_has_rec_ev = True
            if is_rc:
                if kind == "evidence":
                    ft_has_rc_ev = True
                    rc_ev_lines += 1
                elif kind == "exclusion":
                    ft_has_rc_ex = True
                    rc_ex_lines += 1
        if ft_has_rc_ev: rc_ev_ft += 1
        if ft_has_rc_ex: rc_ex_ft += 1
        if ft_has_rec_ev: rec_ev_ft += 1

    ed["frozen_rightclick_evidence_fulltype_count"] = rc_ev_ft
    ed["frozen_rightclick_evidence_line_count"] = rc_ev_lines
    ed["frozen_rightclick_exclusion_fulltype_count"] = rc_ex_ft
    ed["frozen_rightclick_exclusion_line_count"] = rc_ex_lines
    ed["frozen_recipe_evidence_fulltype_count"] = rec_ev_ft

    # Fetch unknown_prefix_line_count
    diag_path = OUTPUT_DIR / "diagnostics.v2.4.json"
    if diag_path.exists():
        diag_data = json.loads(diag_path.read_text("utf-8"))
        ed["frozen_unknown_prefix_line_count"] = len(diag_data.get("unknown_prefix", []))

    EXPECTED_DIFF_PATH.write_text(json.dumps(ed, indent=4, ensure_ascii=False) + "\n", "utf-8")
    print("expected_diff updated successfully!")

if __name__ == "__main__":
    main()
