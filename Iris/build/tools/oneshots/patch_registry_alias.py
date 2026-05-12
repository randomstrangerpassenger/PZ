import json
from pathlib import Path

TARGET_KEYS = {
    "uc.craft.blowtorch": "uc.action.blowtorch",
    "uc.craft.hammer": "uc.action.hammer",
    "uc.craft.saw": "uc.action.saw",
    "uc.craft.screwdriver": "uc.action.screwdriver",
    "uc.firefighting.extinguish": "uc.action.extinguish_fire",
    "uc.food.open_can": "uc.action.open_can",
    "uc.medical.remove_bullet": "uc.action.remove_bullet",
    "uc.medical.stitch": "uc.action.stitch",
    "uc.vehicle.fuel": "uc.action.fuel",
    "uc.weapon.attach_part": "uc.action.attach_weapon_part"
}

def main():
    registry_path = Path("Iris/build/data/v2.4/use_case_registry.v2.4.json")
    data = json.loads(registry_path.read_text("utf-8"))
    
    rules = data.get("rules", {})
    # Update existing rules to have alias_of
    for rule_id, props in rules.items():
        use_case_id = props.get("use_case_id")
        if use_case_id in TARGET_KEYS:
            props["alias_of"] = TARGET_KEYS[use_case_id]
            print(f"Added alias_of to rule {rule_id}: {use_case_id} -> {TARGET_KEYS[use_case_id]}")

    # Add missing target explicit nodes directly to `rules` for the registry to validate them if needed
    # However, use_case_registry maps rule_id -> use_case properties.
    # Where should the target nodes live? If it maps rule_id -> use_case_id, we don't have a "target rule_id", 
    # but the instructions say: "신규 uc.action.* 노드를 명시적으로 신규 생성합니다."
    # Let's create dummy rules so the explicit use cases exist in the registry.
    for old_use_case, new_use_case in TARGET_KEYS.items():
        dummy_rule_id = f"virtual.rule.{new_use_case}"
        if dummy_rule_id not in rules:
            rules[dummy_rule_id] = {
                "use_case_id": new_use_case,
                "_comment": "Explicit target node for aliasing"
            }
            print(f"Created explicit target rule: {dummy_rule_id} -> {new_use_case}")

    registry_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print("Patch complete.")

if __name__ == "__main__":
    main()
