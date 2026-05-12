"""Central version labels for Iris build scripts."""

BUILD_VERSION = "v2.4"
REQUIRE_FIELDS_VERSION = "v2.5"
QUALITY_GATES_VERSION = "v2.5"


def versioned_name(stem: str, version: str = BUILD_VERSION, suffix: str = ".json") -> str:
    return f"{stem}.{version}{suffix}"
