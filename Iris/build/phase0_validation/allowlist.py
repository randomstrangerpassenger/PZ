"""
Iris Build Pipeline - Phase 0: Allowlist
Gate-0: Single Source of Truth for allowed field values

Loads and enforces the Evidence Allowlist as the authoritative source
for all field values, deprecated mappings, and guard conditions.
"""
from dataclasses import dataclass, field
from typing import Any

# === Allowlist Definition ===
# This is the Single Source of Truth (SoT) derived from iris-evidence-allowlist.md

ALLOWLIST = {
    "version": "0.3",
    
    # === 1. Item Script Fields ===
    "fields": {
        # Classification fields (eq/contains operators)
        "classification": ["Type", "Categories", "SubCategory", "BodyLocation", "AmmoType", "Tags"],
        
        # Weapon detail fields (exists/eq operators)
        "weapon_detail": ["TwoHandWeapon", "IsAimedFirearm", "MountOn"],
        
        # Medical fields (exists/eq operators)
        "medical": ["Medical", "CanBandage", "AlcoholPower"],
        
        # Light/Fire fields (exists only for numerics)
        "light_fire": ["LightStrength", "TorchCone", "ActivatedItem"],
        
        # Action-indicating fields
        "action": ["CustomContextMenu", "TeachedRecipes", "SkillTrained", 
                   "CanStoreWater", "Alcoholic", "TwoWay", "IsCookable"],
        
        # State/numeric fields (exists with Type guard)
        "state_guarded": ["HungerChange", "ThirstChange", "StressChange", "UnhappyChange"],
        
        # Vehicle fields (exists/eq operators)
        "vehicle": ["MechanicsItem", "VehicleType", "WheelFriction", 
                    "brakeForce", "SuspensionDamping", "SuspensionCompression",
                    "EngineLoudness"],
        
        # Display-only fields (NOT for classification)
        "display_only": ["DisplayName", "DisplayCategory", "Weight", 
                         "MaxDamage", "MinDamage", "UseDelta", "BandagePower"],
    },
    
    # === 2. Type Enum ===
    "Type": [
        "Normal", "Weapon", "Food", "Drainable", "Clothing",
        "Literature", "Map", "Radio", "Container", "WeaponPart",
        "Moveable", "Key", "AlarmClock", "AlarmClockClothing"
    ],
    
    # === 3. SubCategory Enum ===
    "SubCategory": ["Swinging", "Stab", "Spear", "Firearm"],
    
    # === 4. Categories ===
    "Categories": [
        "Axe", "Blunt", "SmallBlunt", "LongBlade", "SmallBlade", 
        "Spear", "Improvised"
    ],
    
    # === 5. Recipe Roles ===
    "RecipeRole": ["input", "keep", "require"],
    
    # === 6. Recipe Categories ===
    "RecipeCategory": [
        "Carpentry", "Cooking", "Electrical", "Engineer", "Farming",
        "Fishing", "Health", "Smithing", "Survivalist", "Trapper", "Welding"
    ],
    
    # === 7. Tags (from iris-evidence-allowlist.md Section 5) ===
    "Tags": {
        # Tool-related
        "tool": [
            "Hammer", "Saw", "Screwdriver", "Crowbar", "Scissors", "CanOpener",
            "RemoveBarricade", "FishingRod", "FishingSpear", "Lighter", "StartFire",
            "ChopTree", "DigPlow", "DigGrave", "ClearAshes", "TakeDirt",
            "Sledgehammer", "WeldingMask"
        ],
        # Medical-related
        "medical": ["RemoveBullet", "RemoveGlass", "SewingNeedle", "Disinfectant"],
        # Cooking-related
        "cooking": ["CoffeeMaker", "SharpKnife", "DullKnife", "Fork", "Spoon"],
        # Food/Drink-related
        "consumable": ["AlcoholicBeverage", "LowAlcohol", "HerbalTea"],
        # Vehicle-related
        "vehicle": ["CarBattery"],
        # Other
        "other": ["Petrol", "Rope", "GasMask"],
    },
    
    # === 8. CustomContextMenu ===
    "CustomContextMenu": ["Drink", "Smoke", "Take"],
    
    # === 9. BodyLocation Mapping ===
    "BodyLocation": {
        "6-A": ["Hat", "FullHat", "FullHelmet", "Mask", "MaskEyes", "MaskFull"],
        "6-B": ["Shirt", "ShortSleeveShirt", "Tshirt", "TankTop", "Sweater", 
                "SweaterHat", "Jacket", "JacketHat", "JacketHat_Bulky", 
                "JacketSuit", "Jacket_Bulky", "Jacket_Down", 
                "TorsoExtra", "TorsoExtraVest"],
        "6-C": ["Pants", "Skirt", "Legs1"],
        "6-D": ["Hands"],
        "6-E": ["Shoes", "Socks"],
        "6-G": ["Belt", "BeltExtra", "Neck", "Necklace", "Necklace_Long", 
                "Eyes", "LeftEye", "RightEye", "Ears", "EarTop", "Scarf",
                "LeftWrist", "RightWrist", "Left_MiddleFinger", "Left_RingFinger",
                "Right_MiddleFinger", "Right_RingFinger", "Nose", "BellyButton", 
                "AmmoStrap", "FannyPackFront", "FannyPackBack"],
        # Multi-tag (full-body)
        "multi": {
            "Boilersuit": ["6-B", "6-C"],
            "Dress": ["6-B", "6-C"],
            "FullSuit": ["6-B", "6-C"],
            "FullSuitHead": ["6-A", "6-B", "6-C"],
        },
        # Excluded
        "excluded": ["ZedDmg", "Wound", "Bandage", "Tail"],
    },
    
    # === 10. AmmoType Mapping ===
    "AmmoType": {
        "2-G": ["Base.Bullets9mm", "Base.Bullets45", "Base.Bullets44", "Base.Bullets38"],
        "2-H": ["Base.223Bullets", "Base.308Bullets", "Base.556Bullets"],
        "2-I": ["Base.ShotgunShells"],
    },
    
    # === 11. Moveables ===
    "Moveables": {
        "itemIds": ["Base.Hammer", "Base.Screwdriver", "Base.Shovel", 
                    "Base.Wrench", "Base.PipeWrench"],
        "tags": ["Crowbar", "SharpKnife", "Scissors", "WeldingMask"],
    },
    
    # === 12. Deprecated Values (v0.2) ===
    "deprecated": {
        "Categories": ["Blade", "Thrown"],
        "RecipeCategory": ["MetalWelding", "Masonry", "Mechanics", "Electronics"],
        "Tags": [
            "Cookware", "Medical", "Tool", "Weapon", "Clothing", 
            "Food", "Literature"
        ],
        "CustomContextMenu": [
            "Disinfect", "Bandage", "Splint", "Stitch", 
            "RemoveBullet", "RemoveGlass", "CleanWound"
        ],
    },
    
    # === 13. Guarded Fields ===
    # Fields that require Type guard for exists operation
    "guarded_fields": {
        "HungerChange": ["Type=Food"],
        "ThirstChange": ["Type=Food", "Type=Drainable"],
        "StressChange": ["Type=Food"],
        "UnhappyChange": ["Type=Food"],
    },
    
    # === 14. Standalone exists allowed ===
    # Fields that can use exists without Type guard
    "standalone_exists": [
        "Medical", "CanBandage", "MountOn", "TorchCone",
        "TeachedRecipes", "SkillTrained",
        # Vehicle (Phase 2)
        "MechanicsItem", "VehicleType", "WheelFriction",
        "brakeForce", "SuspensionDamping", "SuspensionCompression",
        "EngineLoudness",
    ],
    
    # === 15. Manual Override Required ===
    "manual_override_required": {
        "Tool.1-J": ["Base.Generator"],
        "Combat.2-J": [],  # 투척/폭발물 - no automatic detection
        "Combat.2-K": [],  # 탄약류 - no automatic detection
        "Resource.4-D": [],  # 연료류
        "Consumable.3-E": [],  # 약초류
        "Vehicle.8-A": [],  # 가스탱크/엔진 파츠 — 구동계 전용 필드 없음
    },
}


# === Allowlist Access Functions ===

def get_allowed_types() -> frozenset[str]:
    """Get allowed Type enum values."""
    return frozenset(ALLOWLIST["Type"])


def get_allowed_subcategories() -> frozenset[str]:
    """Get allowed SubCategory enum values."""
    return frozenset(ALLOWLIST["SubCategory"])


def get_allowed_categories() -> frozenset[str]:
    """Get allowed Categories values."""
    return frozenset(ALLOWLIST["Categories"])


def get_allowed_tags() -> frozenset[str]:
    """Get all allowed Tags (flattened from categories)."""
    all_tags = set()
    for category_tags in ALLOWLIST["Tags"].values():
        all_tags.update(category_tags)
    return frozenset(all_tags)


def get_allowed_recipe_roles() -> frozenset[str]:
    """Get allowed Recipe roles."""
    return frozenset(ALLOWLIST["RecipeRole"])


def get_allowed_recipe_categories() -> frozenset[str]:
    """Get allowed Recipe categories."""
    return frozenset(ALLOWLIST["RecipeCategory"])


def get_deprecated_values(field: str) -> frozenset[str]:
    """Get deprecated values for a field."""
    return frozenset(ALLOWLIST["deprecated"].get(field, []))


def is_deprecated(field: str, value: str) -> bool:
    """Check if a value is deprecated for a field."""
    return value in ALLOWLIST["deprecated"].get(field, [])


def is_guarded_field(field: str) -> bool:
    """Check if a field requires Type guard for exists operation."""
    return field in ALLOWLIST["guarded_fields"]


def get_guard_conditions(field: str) -> list[str]:
    """Get required guard conditions for a field."""
    return ALLOWLIST["guarded_fields"].get(field, [])


def is_standalone_exists_allowed(field: str) -> bool:
    """Check if field can use exists without guard."""
    return field in ALLOWLIST["standalone_exists"]


def is_display_only_field(field: str) -> bool:
    """Check if field is display-only (not for classification)."""
    return field in ALLOWLIST["fields"]["display_only"]


def get_body_location_tag(location: str) -> str | None:
    """Get the classification tag for a BodyLocation value."""
    for tag, locations in ALLOWLIST["BodyLocation"].items():
        if tag in ("multi", "excluded"):
            continue
        if location in locations:
            return tag
    return None


def get_multi_body_location_tags(location: str) -> list[str]:
    """Get multiple classification tags for full-body BodyLocation."""
    return ALLOWLIST["BodyLocation"]["multi"].get(location, [])


def is_excluded_body_location(location: str) -> bool:
    """Check if BodyLocation is excluded from classification."""
    return location in ALLOWLIST["BodyLocation"]["excluded"]


def get_ammo_type_tag(ammo_type: str) -> str | None:
    """Get the classification tag for an AmmoType value."""
    for tag, ammo_types in ALLOWLIST["AmmoType"].items():
        if ammo_type in ammo_types:
            return tag
    return None


def get_moveables_allowed_item_ids() -> frozenset[str]:
    """Get allowed Moveables itemIds."""
    return frozenset(ALLOWLIST["Moveables"]["itemIds"])


def get_moveables_allowed_tags() -> frozenset[str]:
    """Get allowed Moveables tags."""
    return frozenset(ALLOWLIST["Moveables"]["tags"])


# === Validation Functions ===

@dataclass
class AllowlistValidationResult:
    """Result of allowlist validation."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_field_value(field_name: str, value: Any, context: str = "") -> AllowlistValidationResult:
    """
    Validate a field value against the allowlist.
    Returns validation result with errors/warnings.
    """
    result = AllowlistValidationResult()
    
    # Check if field is display-only
    if is_display_only_field(field_name):
        result.warnings.append(f"{context}: Field '{field_name}' is display-only, should not be used for classification")
        return result
    
    # Validate Type
    if field_name == "Type":
        if value not in get_allowed_types():
            result.passed = False
            result.errors.append(f"{context}: Invalid Type '{value}'")
        return result
    
    # Validate SubCategory
    if field_name == "SubCategory":
        if value not in get_allowed_subcategories():
            result.passed = False
            result.errors.append(f"{context}: Invalid SubCategory '{value}'")
        return result
    
    # Validate Categories (can be semicolon-separated)
    if field_name == "Categories":
        categories = [c.strip() for c in str(value).split(";") if c.strip()]
        allowed = get_allowed_categories()
        deprecated = get_deprecated_values("Categories")
        for cat in categories:
            if cat in deprecated:
                result.passed = False
                result.errors.append(f"{context}: Deprecated Categories value '{cat}'")
            elif cat not in allowed:
                result.warnings.append(f"{context}: Unknown Categories value '{cat}' (may be mod-added)")
        return result
    
    # Validate Tags (can be semicolon-separated)
    if field_name == "Tags":
        tags = [t.strip() for t in str(value).split(";") if t.strip()]
        allowed = get_allowed_tags()
        deprecated = get_deprecated_values("Tags")
        for tag in tags:
            if tag in deprecated:
                result.passed = False
                result.errors.append(f"{context}: Deprecated Tags value '{tag}'")
            # Note: Unknown tags are allowed (mod compatibility)
        return result
    
    return result


def validate_against_deprecated(field: str, value: str, context: str = "") -> AllowlistValidationResult:
    """Check if a value is deprecated and should not be used."""
    result = AllowlistValidationResult()
    if is_deprecated(field, value):
        result.passed = False
        result.errors.append(f"{context}: Deprecated {field} value '{value}' - see allowlist for replacement")
    return result


if __name__ == "__main__":
    # Quick sanity check
    print(f"Allowlist version: {ALLOWLIST['version']}")
    print(f"Allowed Types: {get_allowed_types()}")
    print(f"Allowed Tags count: {len(get_allowed_tags())}")
    print(f"Deprecated Categories: {get_deprecated_values('Categories')}")
    print(f"Guarded fields: {list(ALLOWLIST['guarded_fields'].keys())}")
    print("✅ Allowlist loaded successfully")
