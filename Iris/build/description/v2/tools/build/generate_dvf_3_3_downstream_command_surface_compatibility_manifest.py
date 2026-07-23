from __future__ import annotations

from dvf_3_3_consumer_migration_normalization_common import phase_path, read_json, write_phase5


def main() -> int:
    write_phase5()
    manifest = read_json(phase_path("phase5", "downstream_command_surface_compatibility_manifest.json"))
    binding = read_json(phase_path("phase5", "compatibility_source_binding.json"))
    return 0 if manifest.get("status") == "PASS" and binding.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
