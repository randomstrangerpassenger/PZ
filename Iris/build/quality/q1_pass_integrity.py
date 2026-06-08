"""Quality Gate Q1 — PASS integrity."""
from quality.config import BUILD_VERSION, DATA_DIR
from tools.common.io import load_json


def gate_q1(decisions: dict, usecases: dict = None, registry: dict = None) -> dict:
    """PASS인 FullType의 prove 중 하나라도 unknown이면 FAIL.
       추가로 usecases 데이터의 line_kind 검증 (Prefix 규칙 부합 및 생략 여부)."""
    violations = []
    checked = 0

    for ft, dec in decisions.items():
        if dec["decision"] != "PASS":
            continue
        checked += 1
        proof = dec.get("proof", {})
        for key in ["A_static_source", "B_external_target", "C_persistent_change"]:
            if proof.get(key) == "unknown":
                violations.append(f"{ft}: {key}=unknown")

    # line_kind 검증
    if usecases:
        for ft, entry in usecases.get("fulltypes", {}).items():
            for uc in entry.get("use_cases", []):
                line_kind = uc.get("line_kind")
                if line_kind not in {"evidence", "exclusion"}:
                    violations.append(f"{ft}: invalid line_kind='{line_kind}' for {uc['use_case_id']}")
                # Step 2(현재는 unknown_prefix 배제하므로 여기 도달하는 uc들은 모두 evidence/exclusion임이 보장됨.
                # 그러나 만약 uc.exclusion.* 인데 evidence로 배정됐다면 FAIL.
                ucid = uc.get("use_case_id", "")
                if ucid.startswith("uc.exclusion.") and line_kind != "exclusion":
                    violations.append(f"{ft}: {ucid} must be line_kind='exclusion'")

                # evidence_strength 검증 (uc.action.* 라인 전용)
                ev_strength = uc.get("evidence_strength")
                if ev_strength is not None:
                    if ev_strength not in {"strong", "weak", "exclude"}:
                        violations.append(
                            f"{ft}: {ucid} invalid evidence_strength='{ev_strength}'"
                        )
                    if ev_strength == "exclude" and not uc.get("reason_code"):
                        violations.append(
                            f"{ft}: {ucid} evidence_strength=exclude but missing reason_code"
                        )

    # Alias 검증 (Q1 구조 보장)
    if registry:
        rules = registry.get("rules", {})
        for rid, props in rules.items():
            alias_of = props.get("alias_of")
            if alias_of:
                # 1. Missing target 방지 (alias_of를 use_case_id로 가지는 노드가 존재해야 함)
                target_exists = any(r.get("use_case_id") == alias_of for r in rules.values())
                if not target_exists:
                    violations.append(f"Registry Rule '{rid}': alias_of target '{alias_of}' is explicitly missing from registry")
                
                # 2. 순환 참조 검증
                visited = set()
                curr_alias = alias_of
                while curr_alias:
                    if curr_alias in visited:
                        violations.append(f"Registry Rule '{rid}': circular alias detected -> {curr_alias}")
                        break
                    visited.add(curr_alias)
                    target_rule = next((r for r in rules.values() if r.get("use_case_id") == curr_alias), None)
                    curr_alias = target_rule.get("alias_of") if target_rule else None

                # 3. 체인 금지: alias_of target 노드는 자체 alias_of를 가지면 안 됨
                # (virtual.rule 포함 target 규칙 전체 참조)
                visited = set()
                curr_alias = alias_of
                while curr_alias:
                    if curr_alias in visited:
                        break # circular alias logic handles this
                    visited.add(curr_alias)
                    target_rule = next((r for r in rules.values() if r.get("use_case_id") == curr_alias), None)
                    if target_rule and target_rule.get("alias_of"):
                        violations.append(
                            f"Registry Rule '{rid}': alias chain detected — "
                            f"target '{curr_alias}' itself has alias_of='{target_rule['alias_of']}'"
                        )
                        break
                    curr_alias = None

            # 4. Registry Oeverride 검증 (A안 규칙)
            decision = props.get("decision")
            strength = props.get("strength")
            reason_code = props.get("override_reason_code")
            
            if decision or strength:
                ucid = props.get("use_case_id", "")
                if props.get("alias_of"):
                    ucid = props["alias_of"] # Target ID 기준

                if not ucid.startswith("uc.action."):
                    violations.append(f"Registry Rule '{rid}': override is only allowed for 'uc.action.*' (found '{ucid}')")
                
                if decision not in {"PASS", "REVIEW"}:
                    violations.append(f"Registry Rule '{rid}': invalid decision override '{decision}'")
                
                if strength not in {"STRONG", "WEAK", "EXCLUDE"}:
                    violations.append(f"Registry Rule '{rid}': invalid strength override '{strength}' (must be uppercase STRONG/WEAK/EXCLUDE)")
                
                if not reason_code:
                    violations.append(f"Registry Rule '{rid}': override requires 'override_reason_code'")

    # Old capability ID 잔존 검증 (리네이밍 대상 old ID가 출력에 남아있으면 FAIL)
    alias_map_path = DATA_DIR / f"use_case_id_alias_map.{BUILD_VERSION}.json"
    if usecases and alias_map_path.exists():
        alias_map = load_json(alias_map_path)
        old_ids = set(alias_map.get("map", {}).keys())
        for ft, entry in usecases.get("fulltypes", {}).items():
            for uc in entry.get("use_cases", []):
                ucid = uc.get("use_case_id", "")
                if ucid in old_ids:
                    violations.append(
                        f"{ft}: old capability ID '{ucid}' still present in output "
                        f"(should be '{alias_map['map'][ucid]}')"
                    )

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "checked": checked,
        "violations": len(violations),
        "details": violations[:10] if violations else [],
    }
