from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IRIS_MOD_ROOT = Path(__file__).resolve().parents[5]
OUTPUT_DIR = ROOT / "output"
STAGING_DIR = ROOT / "staging" / "interaction_cluster" / "phase_d_runtime"
RENDERED_PATH = OUTPUT_DIR / "dvf_3_3_rendered.json"
BRIDGE_REPORT_PATH = STAGING_DIR / "phase_d_lua_bridge_report.json"
PHASE_D_REPORT_PATH = STAGING_DIR / "phase_d_runtime_report.json"
LAYER3_DATA_DIR = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data"
LAYER3_DATA_PATH = LAYER3_DATA_DIR / "IrisLayer3Data.lua"
LAYER3_CHUNK_MANIFEST_PATH = LAYER3_DATA_DIR / "IrisLayer3DataChunks.lua"
LAYER3_CHUNK_DIR = LAYER3_DATA_DIR / "IrisLayer3DataChunks"
LAYER3_RENDERER_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua"
BOOT_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "AIrisBoot.lua"
MAIN_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "IrisMain.lua"
CONTEXT_MENU_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisContextMenu.lua"
BULLET_COMPAT_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Compat" / "IrisBulletReloadCompat.lua"
TEXTURE_COMPAT_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Compat" / "IrisContextMenuTextureCompat.lua"
BROWSER_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Browser" / "IrisBrowser.lua"
PANEL_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiPanel.lua"
WIKI_SECTIONS_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiSections.lua"
VNEXT_EXECUTION_DIR = ROOT / "staging" / "dvf_3_3_vnext_execution"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_text_or_empty(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def read_browser_runtime_text(browser_path: Path) -> str:
    texts = [read_text_or_empty(browser_path)]
    if browser_path.exists():
        for sibling in sorted(browser_path.parent.glob("IrisBrowser*.lua")):
            if sibling != browser_path:
                texts.append(read_text_or_empty(sibling))
    return "\n".join(texts)


def is_under_path(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def build_phase_d_runtime_report(
    *,
    rendered_path: Path = RENDERED_PATH,
    bridge_report_path: Path = BRIDGE_REPORT_PATH,
    layer3_data_path: Path = LAYER3_DATA_PATH,
    layer3_chunk_manifest_path: Path = LAYER3_CHUNK_MANIFEST_PATH,
    layer3_chunk_dir: Path = LAYER3_CHUNK_DIR,
    layer3_renderer_path: Path = LAYER3_RENDERER_PATH,
    boot_path: Path = BOOT_PATH,
    main_path: Path = MAIN_PATH,
    context_menu_path: Path = CONTEXT_MENU_PATH,
    bullet_compat_path: Path = BULLET_COMPAT_PATH,
    texture_compat_path: Path = TEXTURE_COMPAT_PATH,
    browser_path: Path = BROWSER_PATH,
    panel_path: Path = PANEL_PATH,
    wiki_sections_path: Path = WIKI_SECTIONS_PATH,
    output_path: Path = PHASE_D_REPORT_PATH,
) -> dict[str, Any]:
    rendered = load_json(rendered_path)
    bridge_report = load_json(bridge_report_path) if bridge_report_path.exists() else None
    browser_text = read_browser_runtime_text(browser_path)
    panel_text = read_text_or_empty(panel_path)
    renderer_text = read_text_or_empty(layer3_renderer_path)
    boot_text = read_text_or_empty(boot_path)
    main_text = read_text_or_empty(main_path)
    context_menu_text = read_text_or_empty(context_menu_path)
    wiki_sections_text = read_text_or_empty(wiki_sections_path)
    chunk_paths = sorted(layer3_chunk_dir.glob("Chunk*.lua")) if layer3_chunk_dir.exists() else []

    rendered_count = len(rendered.get("entries", {}))
    checks = [
        {
            "code": "layer3_chunk_manifest_exists",
            "status": "pass" if layer3_chunk_manifest_path.exists() else "fail",
            "details": str(layer3_chunk_manifest_path),
        },
        {
            "code": "layer3_chunk_files_exist",
            "status": "pass" if chunk_paths else "fail",
            "details": {
                "chunk_dir": str(layer3_chunk_dir),
                "chunk_count": len(chunk_paths),
            },
        },
        {
            "code": "layer3_active_monolith_absent",
            "status": (
                "pass"
                if not layer3_data_path.exists() or is_under_path(layer3_data_path, VNEXT_EXECUTION_DIR)
                else "fail"
            ),
            "details": {
                "path": str(layer3_data_path),
                "vnext_staging_candidate": is_under_path(layer3_data_path, VNEXT_EXECUTION_DIR),
            },
        },
        {
            "code": "bridge_report_exists",
            "status": "pass" if bridge_report is not None else "fail",
            "details": str(bridge_report_path),
        },
        {
            "code": "layer3_source_entry_count_matches_rendered",
            "status": (
                "pass"
                if bridge_report is not None
                and bridge_report.get("source_entry_count", bridge_report.get("entry_count")) == rendered_count
                else "fail"
            ),
            "details": {
                "rendered_count": rendered_count,
                "bridge_source_count": (
                    None
                    if bridge_report is None
                    else bridge_report.get("source_entry_count", bridge_report.get("entry_count"))
                ),
            },
        },
        {
            "code": "layer3_runtime_entry_count_covers_rendered",
            "status": (
                "pass"
                if bridge_report is not None
                and bridge_report.get("runtime_entry_count", bridge_report.get("entry_count", 0)) >= rendered_count
                else "fail"
            ),
            "details": {
                "rendered_count": rendered_count,
                "bridge_runtime_count": (
                    None
                    if bridge_report is None
                    else bridge_report.get("runtime_entry_count", bridge_report.get("entry_count"))
                ),
            },
        },
        {
            "code": "layer3_renderer_present",
            "status": "pass" if layer3_renderer_path.exists() else "fail",
            "details": str(layer3_renderer_path),
        },
        {
            "code": "consumer_files_present",
            "status": (
                "pass"
                if (
                    boot_path.exists()
                    and main_path.exists()
                    and context_menu_path.exists()
                    and browser_path.exists()
                    and panel_path.exists()
                    and wiki_sections_path.exists()
                )
                else "fail"
            ),
            "details": {
                "boot_path": str(boot_path),
                "context_menu_path": str(context_menu_path),
                "main_path": str(main_path),
                "browser_path": str(browser_path),
                "panel_path": str(panel_path),
                "wiki_sections_path": str(wiki_sections_path),
            },
        },
        {
            "code": "boot_loads_iris_main",
            "status": (
                "pass"
                if (
                    'require, "Iris/IrisMain"' in boot_text
                    or 'ProtectedCall.require("Iris/IrisMain")' in boot_text
                )
                else "fail"
            ),
            "details": str(boot_path),
        },
        {
            "code": "main_loads_and_hooks_context_menu",
            "status": (
                "pass"
                if 'require, "Iris/UI/Wiki/IrisContextMenu"' in main_text
                and "hookContextMenu()" in main_text
                else "fail"
            ),
            "details": str(main_path),
        },
        {
            "code": "context_menu_hooks_inventory_context_menu",
            "status": (
                "pass"
                if "OnFillInventoryObjectContextMenu.Add" in context_menu_text
                and ("Iris: View More" in context_menu_text or "Iris Wiki" in context_menu_text)
                else "fail"
            ),
            "details": str(context_menu_path),
        },
        {
            "code": "context_menu_resolves_stack_wrapped_items",
            "status": (
                "pass"
                if "resolveFirstInventoryItem" in context_menu_text
                and (
                    "candidate:getItems()" in context_menu_text
                    or 'ObjectAccess.call(candidate, "getItems")' in context_menu_text
                )
                and (
                    "container:get(0)" in context_menu_text
                    or 'ObjectAccess.call(container, "get", 0)' in context_menu_text
                )
                else "fail"
            ),
            "details": str(context_menu_path),
        },
        {
            "code": "iris_global_context_menu_patches_absent",
            "status": (
                "pass"
                if not bullet_compat_path.exists()
                and not texture_compat_path.exists()
                and "IrisBulletReloadCompat" not in main_text
                and "IrisContextMenuTextureCompat" not in main_text
                and "doReloadMenuForBullets" not in context_menu_text
                and "ISContextMenu.render" not in context_menu_text
                else "fail"
            ),
            "details": {
                "bullet_compat_path": str(bullet_compat_path),
                "texture_compat_path": str(texture_compat_path),
                "expected": "compat implementations absent and no Iris installer references",
            },
        },
        {
            "code": "wiki_sections_render_layer3_section",
            "status": (
                "pass"
                if "renderLayer3Section" in wiki_sections_text
                and 'require, "Iris/Data/layer3_renderer"' in wiki_sections_text
                else "fail"
            ),
            "details": str(wiki_sections_path),
        },
        {
            "code": "panel_uses_layer3_section",
            "status": (
                "pass"
                if "renderLayer3Section(" in panel_text
                else "fail"
            ),
            "details": str(panel_path),
        },
        {
            "code": "browser_uses_layer3_section",
            "status": (
                "pass"
                if "renderLayer3Section(" in browser_text
                else "fail"
            ),
            "details": str(browser_path),
        },
        {
            "code": "layer3_renderer_loads_chunk_manifest",
            "status": (
                "pass"
                if 'require, "Iris/Data/IrisLayer3DataChunks"' in renderer_text
                and 'safeRequire("Iris/Data/IrisLayer3DataChunks")' in renderer_text
                and 'safeRequire("Iris/Data/IrisLayer3Data")' not in renderer_text
                else "fail"
            ),
            "details": str(layer3_renderer_path),
        },
        {
            "code": "bridge_report_tracks_publish_state_counts",
            "status": (
                "pass"
                if bridge_report is not None
                and "runtime_publish_state_counts" in bridge_report
                and "publish_state_entry_count" in bridge_report
                else "fail"
            ),
            "details": None if bridge_report is None else bridge_report.get("runtime_publish_state_counts"),
        },
        {
            "code": "layer3_renderer_honors_publish_state_visibility",
            "status": (
                "pass"
                if "publish_state" in renderer_text
                and "internal_only" in renderer_text
                else "fail"
            ),
            "details": str(layer3_renderer_path),
        },
    ]

    failures = [check["code"] for check in checks if check["status"] != "pass"]
    payload = {
        "schema_version": "interaction-cluster-phase-d-runtime-v0",
        "overall_status": "ready_for_in_game_validation" if not failures else "blocked",
        "rendered_path": str(rendered_path),
        "rendered_entry_count": rendered_count,
        "checks": checks,
        "failures": failures,
        "in_game_validation": {
            "status": "pending",
            "reason": "Requires manual runtime verification inside Project Zomboid.",
        },
    }
    dump_json(output_path, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate layer3 runtime bridge and consumer hookup.")
    parser.add_argument("--rendered-path", type=Path, default=RENDERED_PATH)
    parser.add_argument("--bridge-report-path", type=Path, default=BRIDGE_REPORT_PATH)
    parser.add_argument("--layer3-data-path", type=Path, default=LAYER3_DATA_PATH)
    parser.add_argument("--layer3-chunk-manifest-path", type=Path, default=LAYER3_CHUNK_MANIFEST_PATH)
    parser.add_argument("--layer3-chunk-dir", type=Path, default=LAYER3_CHUNK_DIR)
    parser.add_argument("--layer3-renderer-path", type=Path, default=LAYER3_RENDERER_PATH)
    parser.add_argument("--boot-path", type=Path, default=BOOT_PATH)
    parser.add_argument("--main-path", type=Path, default=MAIN_PATH)
    parser.add_argument("--context-menu-path", type=Path, default=CONTEXT_MENU_PATH)
    parser.add_argument("--bullet-compat-path", type=Path, default=BULLET_COMPAT_PATH)
    parser.add_argument("--texture-compat-path", type=Path, default=TEXTURE_COMPAT_PATH)
    parser.add_argument("--browser-path", type=Path, default=BROWSER_PATH)
    parser.add_argument("--panel-path", type=Path, default=PANEL_PATH)
    parser.add_argument("--wiki-sections-path", type=Path, default=WIKI_SECTIONS_PATH)
    parser.add_argument("--output-path", type=Path, default=PHASE_D_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_phase_d_runtime_report(
        rendered_path=args.rendered_path,
        bridge_report_path=args.bridge_report_path,
        layer3_data_path=args.layer3_data_path,
        layer3_chunk_manifest_path=args.layer3_chunk_manifest_path,
        layer3_chunk_dir=args.layer3_chunk_dir,
        layer3_renderer_path=args.layer3_renderer_path,
        boot_path=args.boot_path,
        main_path=args.main_path,
        context_menu_path=args.context_menu_path,
        bullet_compat_path=args.bullet_compat_path,
        texture_compat_path=args.texture_compat_path,
        browser_path=args.browser_path,
        panel_path=args.panel_path,
        wiki_sections_path=args.wiki_sections_path,
        output_path=args.output_path,
    )
    print("phase d runtime status:", report["overall_status"])
    return 0 if report["overall_status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
