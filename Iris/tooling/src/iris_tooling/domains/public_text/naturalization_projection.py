from __future__ import annotations

from .naturalization_preparation import *  # noqa: F401,F403

def require_phase0(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 0) / "preflight_report.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError("phase0 prerequisite is not PASS")
    return report


def text_skeleton(text: str) -> str:
    value = re.sub(r"[A-Za-z0-9_.]+", "<ID>", text)
    value = re.sub(r"[가-힣]{2,}", "<KO>", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def build_phase1(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    root = phase_root(attempt_root, 1)
    root.mkdir(parents=True, exist_ok=True)
    baseline = load_json(phase_root(attempt_root, 0) / "isolated_default_rendered.json")
    entries = baseline["entries"]
    facts = {row["item_id"]: row for row in load_jsonl(FACTS_PATH)}
    decisions = {row["item_id"]: row for row in load_jsonl(DECISIONS_PATH)}
    profile_counts: Counter[str] = Counter()
    topology_counts: Counter[str] = Counter()
    quality_counts: Counter[str] = Counter()
    origin_counts: Counter[str] = Counter()
    adopted_count = 0
    lengths: list[int] = []
    skeleton_counts: Counter[str] = Counter()
    strata_rows: list[dict[str, Any]] = []
    for item_id in sorted(entries):
        entry = entries[item_id]
        decision = decisions[item_id]
        if decision["state"] == "adopted":
            adopted_count += 1
            profile = str(entry.get("resolved_profile"))
            profile_counts[profile] += 1
            sections = entry.get("body_plan", {}).get("emitted_section_names", [])
            topology = "+".join(sections)
            topology_counts[topology] += 1
            quality_counts[str(entry.get("coverage_quality_candidate"))] += 1
            origin_values = facts[item_id].get("fact_origin", {}).get("primary_use", [])
            origin = str(origin_values[0]) if origin_values else "none"
            origin_counts[origin] += 1
            text = str(entry.get("text_ko") or "")
            lengths.append(len(text))
            skeleton_counts[text_skeleton(text)] += 1
            strata_rows.append(
                {
                    "item_id": item_id,
                    "resolved_profile": profile,
                    "section_topology": topology,
                    "primary_use_origin": origin,
                    "adoption_state": "adopted",
                    "length_band": (
                        "short"
                        if len(text) < 80
                        else "medium"
                        if len(text) < 180
                        else "long"
                    ),
                    "acquisition_present": bool(facts[item_id].get("acquisition_hint")),
                    "limitation_present": bool(facts[item_id].get("limitation_hint")),
                    "family": str(facts[item_id].get("identity_hint")),
                }
            )
    census = {
        "schema_version": "dvf-3-3-current-prose-census-v1",
        "attempt_id": attempt_id,
        "source_universe_count": len(entries),
        "adopted_count": adopted_count,
        "unadopted_count": len(entries) - adopted_count,
        "profile_counts": dict(sorted(profile_counts.items())),
        "section_topology_counts": dict(topology_counts.most_common()),
        "coverage_quality_counts": dict(sorted(quality_counts.items())),
        "primary_use_origin_counts": dict(sorted(origin_counts.items())),
        "missing_required_row_count": sum(
            1
            for entry in entries.values()
            if entry.get("body_plan", {}).get("missing_required_sections")
        ),
        "length_min": min(lengths),
        "length_max": max(lengths),
        "length_mean": sum(lengths) // len(lengths),
        "current_surface_snapshot_is_semantic_authority": False,
    }
    write_once_or_same(root / "current_prose_census.json", census)
    write_once_or_same(
        root / "recurring_skeleton_inventory.json",
        {
            "schema_version": "dvf-3-3-recurring-skeleton-inventory-v1",
            "rows": [
                {"skeleton": skeleton, "count": count}
                for skeleton, count in skeleton_counts.most_common(100)
            ],
        },
    )
    write_once_or_same(
        root / "review_strata_report.json",
        {
            "schema_version": "dvf-3-3-review-strata-report-v1",
            "strata_row_count": len(strata_rows),
            "strata_dimensions": [
                "resolved_profile",
                "family",
                "section_topology",
                "primary_use_origin",
                "acquisition_present",
                "limitation_present",
                "adoption_state",
                "length_band",
            ],
            "selection_is_algorithmic": True,
            "ordered_item_digest": canonical_hash(
                [row["item_id"] for row in strata_rows]
            ),
            "rows": strata_rows,
        },
    )
    corpus = load_json(CORPUS_MANIFEST_PATH)
    corpus_bindings = []
    for item in corpus["artifacts"]:
        path = REPO_ROOT / item["path"]
        corpus_bindings.append(
            {
                "id": item["id"],
                "path": item["path"],
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
        )
    corpus_validation_errors: list[str] = []
    if len({row["path"] for row in corpus_bindings}) != len(corpus_bindings):
        corpus_validation_errors.append("corpus_role_artifact_path_alias")
    if corpus.get("manual_item_only_selection") is not False:
        corpus_validation_errors.append("corpus_selection_not_algorithmic")
    gold_rows = load_jsonl(GOLD_CORPUS_PATH)
    live_source_keys = set(facts)
    for row in gold_rows:
        item_id = str(row.get("item_id"))
        if item_id not in live_source_keys:
            corpus_validation_errors.append(f"gold_item_missing:{item_id}")
            continue
        available_roles = {
            role
            for field, role in SOURCE_ROLE_BY_FIELD.items()
            if facts[item_id].get(field) not in {None, ""}
        }
        expected_roles = set(str(value) for value in row.get("expected_proposition_coverage", []))
        if not expected_roles.issubset(available_roles):
            corpus_validation_errors.append(
                f"gold_claim_exceeds_source:{item_id}"
            )
    style_rows = load_jsonl(DATA_ROOT / "style_regression_fixtures.jsonl")
    for row in style_rows:
        if row.get("kind") == "live_identity" and row.get("item_id") not in live_source_keys:
            corpus_validation_errors.append(
                f"style_live_item_missing:{row.get('item_id')}"
            )
    snapshot_manifest = load_json(
        DATA_ROOT / "current_surface_snapshot_manifest.json"
    )
    if snapshot_manifest.get("semantic_authority") is not False:
        corpus_validation_errors.append("current_snapshot_semantic_authority")
    if snapshot_manifest.get("candidate_answer_corpus") is not False:
        corpus_validation_errors.append("current_snapshot_candidate_answer_corpus")
    snapshot_source = REPO_ROOT / snapshot_manifest["source_path"]
    if (
        not snapshot_source.is_file()
        or sha256_file(snapshot_source) != snapshot_manifest.get("source_raw_sha256")
    ):
        corpus_validation_errors.append("current_snapshot_hash_mismatch")
    approval_errors: list[str] = []
    quality_approval = (
        load_json(QUALITY_APPROVAL_PATH) if QUALITY_APPROVAL_PATH.is_file() else None
    )
    gold_approval = (
        load_json(GOLD_APPROVAL_PATH) if GOLD_APPROVAL_PATH.is_file() else None
    )
    if quality_approval is None:
        approval_errors.append("quality_standard_owner_approval_missing")
    else:
        if quality_approval.get("status") != "approved":
            approval_errors.append("quality_standard_not_approved")
        if quality_approval.get("quality_standard_sha256") != sha256_file(
            QUALITY_STANDARD_PATH
        ):
            approval_errors.append("quality_standard_approval_hash_mismatch")
    if gold_approval is None:
        approval_errors.append("gold_corpus_owner_approval_missing")
    else:
        if gold_approval.get("status") != "approved":
            approval_errors.append("gold_corpus_not_approved")
        if gold_approval.get("gold_corpus_sha256") != sha256_file(GOLD_CORPUS_PATH):
            approval_errors.append("gold_corpus_approval_hash_mismatch")
        if gold_approval.get("corpus_manifest_sha256") != sha256_file(
            CORPUS_MANIFEST_PATH
        ):
            approval_errors.append("corpus_manifest_approval_hash_mismatch")
    result = {
        "schema_version": "dvf-3-3-phase1-census-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "FAIL"
            if corpus_validation_errors
            else "PASS"
            if not approval_errors
            else "blocked_owner_approval_required"
        ),
        "census_sha256": sha256_file(root / "current_prose_census.json"),
        "corpus_manifest_sha256": sha256_file(CORPUS_MANIFEST_PATH),
        "corpus_bindings": corpus_bindings,
        "quality_standard_approval_present": QUALITY_APPROVAL_PATH.is_file(),
        "gold_corpus_approval_present": GOLD_APPROVAL_PATH.is_file(),
        "approval_state": (
            "owner_review_pending"
            if approval_errors
            else "owner_approval_hash_binding_pass"
        ),
        "approval_errors": approval_errors,
        "corpus_validation_errors": corpus_validation_errors,
        "corpus_validation_pass": not corpus_validation_errors,
    }
    write_once_or_same(root / "phase1_result.json", result)
    return result


def require_phase1(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 1) / "phase1_result.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError("phase1 corpus/standard approval is not PASS")
    return report


def proposition_id_for(item_id: str, field: str, value: Any, origin: Any) -> str:
    digest = canonical_hash(
        {
            "item_id": item_id,
            "source_field": field,
            "source_value": value,
            "fact_origin": origin,
        }
    )
    return f"{item_id}#prop-{digest[:20]}"


def acquisition_subtype(value: str) -> str:
    if "제작" in value or "조합" in value or "주조" in value:
        return "craft"
    if "가공" in value or "분해" in value or "열어" in value:
        return "processing"
    if "발견" in value or "찾" in value:
        return "loot"
    return "general_availability"


def build_phase2(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    require_phase1(attempt_root)
    require_files(
        (
            POLICY_PATH,
            BODY_PLAN_APPLICABILITY_APPROVAL_PATH,
            REGISTRY_ADOPTION_CONTRACT,
            REGISTRY_ADOPTION_RECEIPT,
            INITIAL_REGISTRY_ADOPTION_RECEIPT,
            REGISTRY_CORRECTION_TERMINAL_SEAL,
            REGISTRY_NATURALIZATION_HANDOFF,
            FOUNDATION_READINESS_CORRECTION_REBIND,
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
            FOOD_SEMANTIC_SCHEMA,
            FOOD_SEMANTIC_LICENSE,
            phase_root(attempt_root, 0)
            / "registry_adoption_receipt_binding_report.json",
            phase_root(attempt_root, 0) / "g4_foundation_commit_identity.json",
            phase_root(attempt_root, 0)
            / "compiler_particle_correction_binding_report.json",
        )
    )
    root = phase_root(attempt_root, 2)
    root.mkdir(parents=True, exist_ok=True)
    policy = load_json(POLICY_PATH)
    applicability_approval = load_json(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
    applicability_approval_hash = sha256_file(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
    applicability_rule_id = str(applicability_approval["rule_id"])
    applicability_contract = policy.get("structural_applicability_contract", {})
    applicability_policy_match = (
        applicability_contract.get("rule_id") == applicability_rule_id
        and applicability_contract.get("approval_path")
        == repo_relative(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
        and applicability_contract.get(
            "profile_required_role_with_no_approved_source_proposition"
        )
        == "candidate_optional_owner_approved_exclusion"
        and applicability_contract.get("derived_context_from_primary_use")
        == "candidate_required_with_verified_fusion"
        and applicability_contract.get("source_proposition_invention_allowed")
        is False
        and applicability_contract.get("current_compose_profiles_mutated") is False
        and applicability_contract.get("current_source_authority_mutated") is False
    )
    if not applicability_policy_match:
        raise NaturalizationError(
            "body-plan applicability policy does not match owner approval"
        )
    facts_rows = load_jsonl(FACTS_PATH)
    decisions_rows = load_jsonl(DECISIONS_PATH)
    decisions = {str(row["item_id"]): row for row in decisions_rows}
    registry_binding = load_json(
        phase_root(attempt_root, 0)
        / "registry_adoption_receipt_binding_report.json"
    )
    foundation_identity = load_json(
        phase_root(attempt_root, 0) / "g4_foundation_commit_identity.json"
    )
    particle_correction_binding = load_json(
        phase_root(attempt_root, 0)
        / "compiler_particle_correction_binding_report.json"
    )
    food_semantic_schema = load_json(FOOD_SEMANTIC_SCHEMA)
    food_semantic_license = load_json(FOOD_SEMANTIC_LICENSE)
    schema_pairs = {
        (str(axis["axis"]), str(value["value"]))
        for axis in food_semantic_schema["axes"]
        for value in axis["values"]
    }
    license_by_pair = {
        (str(row["fact_axis"]), str(row["fact_value"])): row
        for row in food_semantic_license["licenses"]
    }
    profiles = load_json(BODY_PLAN_PROFILES_PATH)
    identity_map, precedence = load_profile_resolution_rules(
        identity_rules_path=IDENTITY_RULES_PATH,
        precedence_rules_path=PRECEDENCE_RULES_PATH,
    )
    propositions: list[dict[str, Any]] = []
    non_propositions: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    food_semantic_proposition_count = 0
    invalid_food_semantic_assertions: list[dict[str, Any]] = []
    for facts in sorted(facts_rows, key=lambda row: str(row["item_id"])):
        item_id = str(facts["item_id"])
        decision = decisions[item_id]
        item_propositions: list[dict[str, Any]] = []
        for assertion_index, assertion in enumerate(
            facts.get("food_semantic_assertions", [])
        ):
            axis = str(assertion.get("fact_axis") or "")
            value = str(assertion.get("fact_value") or "")
            pair = (axis, value)
            license_row = license_by_pair.get(pair)
            assertion_valid = all(
                (
                    pair in schema_pairs,
                    license_row is not None,
                    assertion.get("authority_state") in {"approved", "owner_approved"},
                    isinstance(assertion.get("proposition_id"), str),
                    bool(assertion.get("proposition_id")),
                    (
                        isinstance(assertion.get("lineage_id"), dict)
                        or (
                            isinstance(assertion.get("lineage_id"), str)
                            and bool(assertion.get("lineage_id"))
                        )
                    ),
                )
            )
            if not assertion_valid:
                invalid_food_semantic_assertions.append(
                    {
                        "item_id": item_id,
                        "assertion_index": assertion_index,
                        "fact_axis": axis,
                        "fact_value": value,
                    }
                )
                continue
            assertion_source_value = f"{axis}={value}"
            proposition = {
                "item_id": item_id,
                "proposition_id": str(assertion["proposition_id"]),
                "role": "food_semantic",
                "source_path": repo_relative(FACTS_PATH),
                "source_field": (
                    f"facts.food_semantic_assertions[{assertion_index}]"
                ),
                "source_value": assertion_source_value,
                "source_value_hash": sha256_bytes(
                    assertion_source_value.encode("utf-8")
                ),
                "fact_origin": [assertion["lineage_id"]],
                "modality": "asserted",
                "qualifier": "none",
                "condition": "none",
                "semantic_key": canonical_hash(
                    {
                        "role": "food_semantic",
                        "fact_axis": axis,
                        "fact_value": value,
                        "authority_class": assertion.get("authority_class"),
                        "authority_state": assertion.get("authority_state"),
                    }
                ),
                "structural_requirement": "semantic_lead_context",
                "emission_eligibility": decision["state"] == "adopted",
                "acquisition_subtype": None,
                "food_semantic_axis": axis,
                "food_semantic_value": value,
                "food_semantic_authority_class": assertion.get(
                    "authority_class"
                ),
                "food_semantic_authority_state": assertion.get(
                    "authority_state"
                ),
                "food_semantic_lineage_id": assertion["lineage_id"],
                "food_semantic_mapping_id": assertion.get("mapping_id"),
                "food_semantic_schema_sha256": (
                    EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256
                ),
                "food_semantic_proposition_license_sha256": (
                    EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
                ),
                "licensed_proposition": license_row["licensed_proposition"],
                "forbidden_propositions": license_row[
                    "forbidden_propositions"
                ],
            }
            item_propositions.append(proposition)
            propositions.append(proposition)
            food_semantic_proposition_count += 1
        for field in sorted(facts):
            value = facts[field]
            if field == "food_semantic_assertions":
                continue
            if field not in SOURCE_ROLE_BY_FIELD or value is None or value == "":
                non_propositions.append(
                    {
                        "item_id": item_id,
                        "source_field": f"facts.{field}",
                        "reason": (
                            "null_value"
                            if value is None
                            else "non_semantic_metadata"
                        ),
                    }
                )
                continue
            role = SOURCE_ROLE_BY_FIELD[field]
            origin = facts.get("fact_origin", {}).get(field, ["source_field"])
            proposition = {
                "item_id": item_id,
                "proposition_id": proposition_id_for(
                    item_id,
                    field,
                    value,
                    origin,
                ),
                "role": role,
                "source_path": repo_relative(FACTS_PATH),
                "source_field": f"facts.{field}",
                "source_value": str(value),
                "source_value_hash": sha256_bytes(str(value).encode("utf-8")),
                "fact_origin": origin,
                "modality": "asserted",
                "qualifier": (
                    "conditional" if any(token in str(value) for token in ("때", "경우", "근처")) else "none"
                ),
                "condition": (
                    str(value) if any(token in str(value) for token in ("때", "경우")) else "none"
                ),
                "semantic_key": canonical_hash(
                    {
                        "role": role,
                        "value": str(value),
                        "origin": origin,
                    }
                ),
                "structural_requirement": {
                    "identity": "identity_core",
                    "use": "use_core",
                    "context": "context_support",
                    "acquisition": "acquisition_support",
                    "limitation": "limitation_tail",
                }[role],
                "emission_eligibility": decision["state"] == "adopted",
                "acquisition_subtype": (
                    acquisition_subtype(str(value))
                    if role == "acquisition"
                    else None
                ),
            }
            item_propositions.append(proposition)
            propositions.append(proposition)
        profile_name, _, _ = resolve_body_profile(
            facts=facts,
            decision=decision,
            identity_hint_target_map=identity_map,
            precedence_rules=precedence,
        )
        requirements.extend(
            build_candidate_body_plan_requirements(
                item_id=item_id,
                profile_name=profile_name,
                profile_spec=profiles["profiles"][profile_name],
                proposition_rows=item_propositions,
                emission_eligible=decision["state"] == "adopted",
                applicability_rule_id=applicability_rule_id,
                applicability_approval_sha256=applicability_approval_hash,
            )
        )
    proposition_hash = write_jsonl_once_or_same(
        root / "source_proposition_inventory.jsonl",
        propositions,
    )
    non_prop_hash = write_jsonl_once_or_same(
        root / "non_proposition_field_ledger.jsonl",
        non_propositions,
    )
    requirement_hash = write_jsonl_once_or_same(
        root / "body_plan_requirement_inventory.jsonl",
        requirements,
    )
    owner_exclusions = [
        row for row in requirements if row["owner_approved_exclusion"]
    ]
    applicability_report = {
        "schema_version": "dvf-3-3-body-plan-applicability-report-v1",
        "status": "PASS",
        "rule_id": applicability_rule_id,
        "approval_path": repo_relative(BODY_PLAN_APPLICABILITY_APPROVAL_PATH),
        "approval_sha256": applicability_approval_hash,
        "policy_contract_match": applicability_policy_match,
        "profile_required_requirement_count": sum(
            1 for row in requirements if row["profile_required"]
        ),
        "candidate_required_requirement_count": sum(
            1 for row in requirements if row["required"]
        ),
        "owner_approved_source_absence_exclusion_count": len(owner_exclusions),
        "owner_approved_source_absence_exclusion_by_role": dict(
            sorted(Counter(row["role"] for row in owner_exclusions).items())
        ),
        "derived_context_required_with_verified_fusion_count": sum(
            1
            for row in requirements
            if row["required"] and row["derived_context_available"]
        ),
        "source_proposition_invention_count": 0,
        "current_compose_profile_mutation_count": 0,
        "current_source_authority_mutation_count": 0,
    }
    write_once_or_same(
        root / "body_plan_applicability_report.json",
        applicability_report,
    )
    four_hash_identity = {
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "selected_successor_manifest_sha256": (
            load_json(INPUT_MANIFEST)
            .get("food_semantic_authority", {})
            .get("source_successor_manifest_sha256")
        ),
        "food_semantic_schema_sha256": sha256_file(FOOD_SEMANTIC_SCHEMA),
        "food_semantic_proposition_license_sha256": sha256_file(
            FOOD_SEMANTIC_LICENSE
        ),
    }
    expected_four_hash_identity = {
        "current_facts_sha256": EXPECTED_CURRENT_FACTS_SHA256,
        "selected_successor_manifest_sha256": (
            EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        ),
        "food_semantic_schema_sha256": EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256,
        "food_semantic_proposition_license_sha256": (
            EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
        ),
    }
    source_authority_reseal_pass = all(
        (
            registry_binding.get("status") == "PASS",
            four_hash_identity == expected_four_hash_identity,
            sha256_file(INPUT_MANIFEST) == EXPECTED_CURRENT_MANIFEST_SHA256,
            sha256_file(REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(INITIAL_REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(REGISTRY_CORRECTION_TERMINAL_SEAL)
            == EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
            sha256_file(REGISTRY_NATURALIZATION_HANDOFF)
            == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
            sha256_file(REGISTRY_ADOPTION_CONTRACT)
            == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
            foundation_identity.get("foundation_contract_sha256")
            == EXPECTED_FOUNDATION_CONTRACT_SHA256,
            foundation_identity.get("foundation_readiness_sha256")
            == EXPECTED_FOUNDATION_READINESS_SHA256,
            foundation_identity.get(
                "foundation_readiness_correction_rebind_sha256"
            )
            == EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_sha256"
            )
            == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_current_facts_sha256"
            )
            == EXPECTED_CURRENT_FACTS_SHA256,
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_current_manifest_sha256"
            )
            == EXPECTED_CURRENT_MANIFEST_SHA256,
            foundation_identity.get("compiler_fix_commit")
            == EXPECTED_COMPILER_FIX_COMMIT,
            foundation_identity.get("compiler_fix_is_ancestor") is True,
            particle_correction_binding.get("status") == "PASS",
            particle_correction_binding.get("correction_commit")
            == EXPECTED_PARTICLE_CORRECTION_COMMIT,
            particle_correction_binding.get("correction_commit_is_ancestor")
            is True,
            particle_correction_binding.get("projection_report_sha256")
            == EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256,
            particle_correction_binding.get("projected_candidate_entry_count")
            == 2084,
            particle_correction_binding.get("projected_changed_item_count") == 9,
            particle_correction_binding.get(
                "projected_unintended_change_count"
            )
            == 0,
            foundation_identity.get("naturalization_start_commit")
            == EXPECTED_START_COMMIT,
            foundation_identity.get("naturalization_start_tree")
            == EXPECTED_START_TREE,
            foundation_identity.get("naturalization_start_actual_tree")
            == EXPECTED_START_TREE,
            foundation_identity.get("naturalization_start_commit_is_ancestor")
            is True,
            foundation_identity.get("foundation_commit_changed_path_count") == 19,
            food_semantic_proposition_count == 718,
            not invalid_food_semantic_assertions,
        )
    )
    source_authority_reseal = {
        "schema_version": "dvf-3-3-phase2-source-authority-reseal-v1",
        "attempt_id": attempt_id,
        "status": "PASS" if source_authority_reseal_pass else "FAIL",
        "current_facts_path": repo_relative(FACTS_PATH),
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "current_manifest_path": repo_relative(INPUT_MANIFEST),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "registry_adoption_contract_path": repo_relative(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_contract_sha256": sha256_file(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_receipt_path": repo_relative(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_path": repo_relative(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "g4_foundation_commit": foundation_identity.get("foundation_commit"),
        "g4_foundation_tree": foundation_identity.get("foundation_tree"),
        "g4_foundation_contract_sha256": foundation_identity.get(
            "foundation_contract_sha256"
        ),
        "g4_foundation_readiness_sha256": foundation_identity.get(
            "foundation_readiness_sha256"
        ),
        "g4_foundation_readiness_correction_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_correction_rebind_sha256"
            )
        ),
        "g4_foundation_readiness_current_input_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_sha256"
            )
        ),
        "naturalization_start_commit": foundation_identity.get(
            "naturalization_start_commit"
        ),
        "naturalization_start_tree": foundation_identity.get(
            "naturalization_start_tree"
        ),
        "compiler_fix_commit": foundation_identity.get("compiler_fix_commit"),
        "compiler_fix_is_ancestor": foundation_identity.get(
            "compiler_fix_is_ancestor"
        ),
        "particle_correction_commit": particle_correction_binding.get(
            "correction_commit"
        ),
        "particle_correction_commit_is_ancestor": (
            particle_correction_binding.get("correction_commit_is_ancestor")
        ),
        "particle_correction_projection_report_path": (
            particle_correction_binding.get("projection_report_path")
        ),
        "particle_correction_projection_report_sha256": (
            particle_correction_binding.get("projection_report_sha256")
        ),
        "particle_correction_binding_status": (
            particle_correction_binding.get("status")
        ),
        "actual_four_hash_identity": four_hash_identity,
        "expected_four_hash_identity": expected_four_hash_identity,
        "food_semantic_proposition_count": food_semantic_proposition_count,
        "invalid_food_semantic_assertion_count": len(
            invalid_food_semantic_assertions
        ),
        "invalid_food_semantic_assertions": invalid_food_semantic_assertions,
        "attempt_0014_reused_as_current_evidence": False,
        "attempt_0018_reused_or_resumed": False,
        "candidate_or_trace_dependency_count": 0,
        "runtime_or_package_compatibility_claimed": False,
        "live_gate_mutation_allowed": False,
        "official_publish_attempt_allowed": False,
    }
    write_once_or_same(
        root / "source_authority_reseal_report.json",
        source_authority_reseal,
    )
    source_manifest = {
        "schema_version": "dvf-3-3-source-proposition-manifest-v2",
        "attempt_id": attempt_id,
        "source_path": repo_relative(FACTS_PATH),
        "source_sha256": sha256_file(FACTS_PATH),
        "source_item_count": len(facts_rows),
        "proposition_count": len(propositions),
        "proposition_inventory_sha256": proposition_hash,
        "non_proposition_field_ledger_sha256": non_prop_hash,
        "candidate_dependency_count": 0,
        "candidate_trace_dependency_count": 0,
        "profile_body_plan_generated_semantic_proposition_count": 0,
        "body_plan_applicability_rule_id": applicability_rule_id,
        "body_plan_applicability_approval_path": repo_relative(
            BODY_PLAN_APPLICABILITY_APPROVAL_PATH
        ),
        "body_plan_applicability_approval_sha256": applicability_approval_hash,
        "current_manifest_path": repo_relative(INPUT_MANIFEST),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "registry_adoption_contract_path": repo_relative(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_contract_sha256": sha256_file(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_receipt_path": repo_relative(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_path": repo_relative(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "g4_foundation_commit": foundation_identity.get("foundation_commit"),
        "g4_foundation_tree": foundation_identity.get("foundation_tree"),
        "g4_foundation_contract_sha256": foundation_identity.get(
            "foundation_contract_sha256"
        ),
        "g4_foundation_readiness_sha256": foundation_identity.get(
            "foundation_readiness_sha256"
        ),
        "g4_foundation_readiness_correction_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_correction_rebind_sha256"
            )
        ),
        "g4_foundation_readiness_current_input_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_sha256"
            )
        ),
        "naturalization_start_commit": foundation_identity.get(
            "naturalization_start_commit"
        ),
        "naturalization_start_tree": foundation_identity.get(
            "naturalization_start_tree"
        ),
        "compiler_fix_commit": foundation_identity.get("compiler_fix_commit"),
        "compiler_fix_is_ancestor": foundation_identity.get(
            "compiler_fix_is_ancestor"
        ),
        "particle_correction_commit": particle_correction_binding.get(
            "correction_commit"
        ),
        "particle_correction_commit_is_ancestor": (
            particle_correction_binding.get("correction_commit_is_ancestor")
        ),
        "particle_correction_projection_report_path": (
            particle_correction_binding.get("projection_report_path")
        ),
        "particle_correction_projection_report_sha256": (
            particle_correction_binding.get("projection_report_sha256")
        ),
        "particle_correction_binding_status": (
            particle_correction_binding.get("status")
        ),
        "four_hash_identity": four_hash_identity,
        "food_semantic_proposition_count": food_semantic_proposition_count,
        "source_authority_reseal_report_sha256": sha256_file(
            root / "source_authority_reseal_report.json"
        ),
        "attempt_0014_reused_as_current_evidence": False,
        "attempt_0018_reused_or_resumed": False,
    }
    write_once_or_same(root / "source_proposition_manifest.json", source_manifest)
    coverage = {
        "schema_version": "dvf-3-3-source-to-proposition-coverage-report-v1",
        "source_field_occurrence_count": len(propositions) + len(non_propositions),
        "proposition_occurrence_count": len(propositions),
        "non_proposition_occurrence_count": len(non_propositions),
        "unassigned_source_field_occurrence_count": 0,
        "source_to_proposition_coverage_pass": True,
        "candidate_dependency_count": 0,
    }
    write_once_or_same(root / "source_to_proposition_coverage_report.json", coverage)
    result = {
        "schema_version": "dvf-3-3-phase2-result-v2",
        "attempt_id": attempt_id,
        "status": "PASS" if source_authority_reseal_pass else "FAIL",
        "source_proposition_manifest_hash": sha256_file(
            root / "source_proposition_manifest.json"
        ),
        "body_plan_requirement_digest": requirement_hash,
        "body_plan_applicability_report_hash": sha256_file(
            root / "body_plan_applicability_report.json"
        ),
        "source_to_proposition_coverage_pass": True,
        "source_authority_reseal_pass": source_authority_reseal_pass,
        "source_authority_reseal_report_hash": sha256_file(
            root / "source_authority_reseal_report.json"
        ),
        "food_semantic_proposition_count": food_semantic_proposition_count,
    }
    write_once_or_same(root / "phase2_result.json", result)
    return result


def require_phase2(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 2) / "phase2_result.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError(
            "phase2 prerequisite is not PASS: "
            f"{report.get('status', 'missing_status')}"
        )
    return report


def build_facts_authority_enrichment_request_payload(
    *,
    blocking_conditions: list[dict[str, Any]],
    blocked_item_count: int,
    current_facts_authority_path: str,
    current_facts_authority_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-facts-authority-enrichment-request-v1",
        "status": (
            "blocked_facts_authority_information_insufficient"
            if blocking_conditions
            else "not_required"
        ),
        "owner": "dvf_3_3_facts_authority",
        "authority_domain": "layer3_3_facts",
        "routing_target": "dvf_3_3_facts_authority_enrichment_plan",
        "facts_authority_plan_path": "docs/dvf_3_3_facts_authority_enrichment_plan.md",
        "layer4_qg_role": "separate_interaction_quality_gate",
        "layer4_qg_routing_allowed": False,
        "layer4_qg_source_authority_allowed": False,
        "cross_layer_promotion_requires_separate_approved_plan": True,
        "current_facts_authority_path": current_facts_authority_path,
        "current_facts_authority_sha256": current_facts_authority_sha256,
        "blocked_item_count": blocked_item_count,
        "blocking_conditions": blocking_conditions,
        "required_approved_distinctions": [
            "cooking_ingredient_vs_ready_to_eat",
            "beverage_vs_snack_vs_meal_component",
            "raw_edibility",
            "preparation_or_cooking_required",
            "preserved_or_shelf_stable",
            "distinct_acquisition_or_use_mode",
        ],
        "candidate_inputs_requiring_facts_authority_review": [
            "Iris/input/items_itemscript.json",
            "Iris/output/tags_by_fulltype.json",
            "Iris/build/description/v2/data/upstream_usecases_by_fulltype.json",
        ],
        "candidate_inputs_are_current_facts_authority": False,
        "facts_authority_promotion_required_before_compiler_use": True,
        "forbidden_fallbacks": [
            "item_id_based_template_selection",
            "hash_based_template_selection",
            "random_template_selection",
            "same_meaning_paraphrase_rotation",
            "compiler_invented_food_subtype",
            "automatic_layer4_qg_routing",
            "layer4_trace_as_layer3_facts_authority",
        ],
        "earliest_naturalization_resume_phase": (
            "phase2_source_inventory_reseal_then_phase3"
        ),
    }


def build_phase3_repetition_remediation_reports(
    *,
    attempt_id: str,
    attempt_root: Path,
    root: Path,
) -> dict[str, Any]:
    facts_rows = load_jsonl(FACTS_PATH)
    decisions_rows = load_jsonl(DECISIONS_PATH)
    facts_by_item = {str(row["item_id"]): row for row in facts_rows}
    decisions_by_item = {str(row["item_id"]): row for row in decisions_rows}
    propositions_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in load_jsonl(
        phase_root(attempt_root, 2) / "source_proposition_inventory.jsonl"
    ):
        propositions_by_item[str(row["item_id"])].append(row)
    identity_map, precedence = load_profile_resolution_rules(
        identity_rules_path=IDENTITY_RULES_PATH,
        precedence_rules_path=PRECEDENCE_RULES_PATH,
    )
    adopted_ids = [
        item_id
        for item_id, decision in decisions_by_item.items()
        if decision["state"] == "adopted"
    ]
    policy = load_json(POLICY_PATH)
    ratio = policy["detectors"]["repeated_skeleton_concentration"]["ratio"]
    maximum_repetition_count = (
        len(adopted_ids)
        * int(ratio["numerator"])
        // int(ratio["denominator"])
    )
    current_surface_path = (
        phase_root(attempt_root, 0) / "isolated_default_rendered.json"
    )
    require_files(
        (
            current_surface_path,
            phase_root(attempt_root, 1) / "recurring_skeleton_inventory.json",
        )
    )
    current_surface = load_json(current_surface_path)
    current_surface_skeletons = {
        item_id: text_skeleton(str(entry.get("text_ko") or ""))
        for item_id, entry in current_surface["entries"].items()
        if item_id in adopted_ids
    }
    current_skeleton_counts = Counter(current_surface_skeletons.values())
    baseline_hit_ids = {
        item_id
        for item_id, skeleton in current_surface_skeletons.items()
        if current_skeleton_counts[skeleton] > maximum_repetition_count
    }
    baseline_hits = [
        {
            "item_id": item_id,
            "detector_id": "repeated_skeleton_concentration",
            "hit": True,
            "skeleton": current_surface_skeletons[item_id],
        }
        for item_id in sorted(baseline_hit_ids)
    ]
    condition_rows: dict[str, dict[str, Any]] = {}
    condition_item_ids: dict[str, list[str]] = defaultdict(list)
    projected_rows: list[dict[str, Any]] = []
    for item_id in sorted(adopted_ids):
        facts = facts_by_item[item_id]
        decision = decisions_by_item[item_id]
        proposition_rows = sorted(
            propositions_by_item[item_id],
            key=lambda row: str(row["proposition_id"]),
        )
        by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in proposition_rows:
            by_role[str(row["role"])].append(row)
        identity_row = by_role["identity"][0] if by_role["identity"] else None
        use_row = by_role["use"][0] if by_role["use"] else None
        profile_name, _, _ = resolve_body_profile(
            facts=facts,
            decision=decision,
            identity_hint_target_map=identity_map,
            precedence_rules=precedence,
        )
        lead_context = build_candidate_lead_context(
            facts=facts,
            resolved_profile=profile_name,
            identity_row=identity_row,
            use_row=use_row,
            proposition_rows=proposition_rows,
        )
        semantic_bindings = sorted(
            [
                {
                    "role": row["role"],
                    "semantic_key": row["semantic_key"],
                    "source_field": row["source_field"],
                    "fact_origin": row.get("fact_origin", []),
                }
                for row in proposition_rows
            ],
            key=lambda row: (
                str(row["role"]),
                str(row["semantic_key"]),
                str(row["source_field"]),
            ),
        )
        condition_payload = {
            "lead_context": lead_context,
            "semantic_bindings": semantic_bindings,
        }
        condition_digest = canonical_hash(condition_payload)
        condition_rows.setdefault(
            condition_digest,
            {
                "semantic_condition_digest": condition_digest,
                "lead_context": lead_context,
                "semantic_bindings": semantic_bindings,
                "identity_text": (
                    identity_row.get("source_value") if identity_row else None
                ),
                "use_text": use_row.get("source_value") if use_row else None,
            },
        )
        condition_item_ids[condition_digest].append(item_id)
        if item_id in baseline_hit_ids:
            projected_text, _, rule_id = select_candidate_lead_realization(
                identity_text=(
                    str(identity_row["source_value"]) if identity_row else None
                ),
                use_text=str(use_row["source_value"]) if use_row else None,
                lead_context=lead_context,
            )
            projected_rows.append(
                {
                    "item_id": item_id,
                    "projected_text": projected_text,
                    "projected_skeleton": text_skeleton(projected_text),
                    "realization_rule_id": rule_id,
                    "semantic_condition_digest": condition_digest,
                }
            )
    oversized_conditions = []
    for digest, item_ids in sorted(
        condition_item_ids.items(),
        key=lambda row: (-len(row[1]), row[0]),
    ):
        if len(item_ids) <= maximum_repetition_count:
            continue
        row = condition_rows[digest]
        oversized_conditions.append(
            {
                **row,
                "item_count": len(item_ids),
                "item_ids": item_ids,
                "maximum_repetition_count": maximum_repetition_count,
                "minimum_required_semantic_partition_count": math.ceil(
                    len(item_ids) / maximum_repetition_count
                ),
                "compiler_can_split_without_unapproved_information": False,
                "facts_authority_enrichment_required": True,
            }
        )
    projected_skeleton_counts = Counter(
        row["projected_skeleton"] for row in projected_rows
    )
    projected_rule_counts = Counter(
        row["realization_rule_id"] for row in projected_rows
    )
    projected_over_limit = [
        {"skeleton": skeleton, "count": count}
        for skeleton, count in projected_skeleton_counts.most_common()
        if count > maximum_repetition_count
    ]
    blocked_projected_skeletons = {
        row["skeleton"] for row in projected_over_limit
    }
    projected_blocked_ids = [
        row["item_id"]
        for row in projected_rows
        if row["projected_skeleton"] in blocked_projected_skeletons
    ]
    facts_authority_blocked_ids = sorted(
        {
            item_id
            for condition in oversized_conditions
            for item_id in condition["item_ids"]
            if item_id in baseline_hit_ids
        }
    )
    unexplained_compiler_blocked_ids = sorted(
        set(projected_blocked_ids) - set(facts_authority_blocked_ids)
    )
    cause_report = {
        "schema_version": "dvf-3-3-repeated-skeleton-cause-analysis-v3",
        "attempt_id": attempt_id,
        "baseline_source": "fresh_phase0_current_surface_snapshot",
        "fresh_current_surface_path": repo_relative(current_surface_path),
        "fresh_current_surface_sha256": sha256_file(current_surface_path),
        "phase1_recurring_skeleton_inventory_path": repo_relative(
            phase_root(attempt_root, 1)
            / "recurring_skeleton_inventory.json"
        ),
        "phase1_recurring_skeleton_inventory_sha256": sha256_file(
            phase_root(attempt_root, 1)
            / "recurring_skeleton_inventory.json"
        ),
        "historical_attempt_id": HISTORICAL_ATTEMPT_ID,
        "historical_attempt_role": "immutable_historical_evidence_only",
        "historical_attempt_gate_evidence_reused": False,
        "baseline_repeated_skeleton_hit_count": len(baseline_hits),
        "candidate_denominator": len(adopted_ids),
        "maximum_repetition_count": maximum_repetition_count,
        "oversized_identical_approved_semantic_condition_count": len(
            oversized_conditions
        ),
        "oversized_identical_approved_semantic_conditions": oversized_conditions,
        "facts_authority_blocked_item_count": len(facts_authority_blocked_ids),
        "compiler_rule_remediable_item_count": (
            len(projected_rows) - len(facts_authority_blocked_ids)
        ),
        "layer4_qg_routing_count": 0,
        "item_id_hash_or_random_rule_selection_count": 0,
        "source_proposition_invention_count": 0,
    }
    write_once_or_same(root / "repeated_skeleton_cause_analysis.json", cause_report)
    projection_report = {
        "schema_version": "dvf-3-3-semantic-lead-rule-projection-report-v1",
        "attempt_id": attempt_id,
        "projection_scope": "preserved_phase6_repeated_skeleton_hit_population",
        "projection_row_count": len(projected_rows),
        "maximum_repetition_count": maximum_repetition_count,
        "realization_rule_counts": dict(sorted(projected_rule_counts.items())),
        "projected_skeleton_counts": [
            {"skeleton": skeleton, "count": count}
            for skeleton, count in projected_skeleton_counts.most_common()
        ],
        "projected_over_limit_skeletons": projected_over_limit,
        "projected_over_limit_item_count": len(projected_blocked_ids),
        "facts_authority_explained_projected_blocked_item_count": len(
            set(projected_blocked_ids) & set(facts_authority_blocked_ids)
        ),
        "unexplained_compiler_blocked_item_count": len(
            unexplained_compiler_blocked_ids
        ),
        "unexplained_compiler_blocked_item_ids": unexplained_compiler_blocked_ids,
        "compiler_rule_projection_pass": not unexplained_compiler_blocked_ids,
        "full_candidate_acceptance_claimed": False,
    }
    write_once_or_same(
        root / "semantic_lead_rule_projection_report.json",
        projection_report,
    )
    facts_authority_request = build_facts_authority_enrichment_request_payload(
        blocking_conditions=oversized_conditions,
        blocked_item_count=len(facts_authority_blocked_ids),
        current_facts_authority_path=repo_relative(FACTS_PATH),
        current_facts_authority_sha256=sha256_file(FACTS_PATH),
    )
    write_once_or_same(
        root / "facts_authority_enrichment_request.json",
        facts_authority_request,
    )
    return {
        "facts_authority_gate_pass": not oversized_conditions,
        "compiler_rule_projection_pass": not unexplained_compiler_blocked_ids,
        "facts_authority_blocked_item_count": len(facts_authority_blocked_ids),
        "compiler_rule_remediable_item_count": (
            len(projected_rows) - len(facts_authority_blocked_ids)
        ),
        "cause_report_hash": sha256_file(
            root / "repeated_skeleton_cause_analysis.json"
        ),
        "projection_report_hash": sha256_file(
            root / "semantic_lead_rule_projection_report.json"
        ),
        "facts_authority_enrichment_request_hash": sha256_file(
            root / "facts_authority_enrichment_request.json"
        ),
    }


def build_phase3(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    require_phase2(attempt_root)
    root = phase_root(attempt_root, 3)
    root.mkdir(parents=True, exist_ok=True)
    baseline = load_json(
        phase_root(attempt_root, 0) / "default_mode_golden_baseline.json"
    )
    replay_output = root / "default_mode_replay.json"
    replay = build_rendered(
        FACTS_PATH,
        DECISIONS_PATH,
        BODY_PLAN_PROFILES_PATH,
        replay_output,
        CURRENT_OVERLAY_SUPPORT_PATH,
        root / "default_mode_replay_style_log.jsonl",
        None,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    replay_hash = canonical_hash(normalize_legacy_rendered(replay))
    regression = {
        "schema_version": "dvf-3-3-default-mode-regression-report-v1",
        "baseline_normalized_content_sha256": baseline[
            "normalized_content_sha256"
        ],
        "replay_normalized_content_sha256": replay_hash,
        "legacy_normalized_content_hash_identity_pass": (
            baseline["normalized_content_sha256"] == replay_hash
        ),
        "legacy_metadata_contract_pass": (
            isinstance(replay["meta"].get("generated_at"), str)
        ),
        "legacy_raw_file_byte_identity_pass": "not_claimed",
    }
    write_once_or_same(root / "default_mode_regression_report.json", regression)
    negative_reasons: list[str] = []
    try:
        build_candidate_rendered(
            facts_path=FACTS_PATH,
            decisions_path=DECISIONS_PATH,
            profiles_path=BODY_PLAN_PROFILES_PATH,
            identity_rules_path=IDENTITY_RULES_PATH,
            precedence_rules_path=PRECEDENCE_RULES_PATH,
            policy_path=POLICY_PATH,
            source_proposition_inventory_path=phase_root(attempt_root, 2)
            / "source_proposition_inventory.jsonl",
            body_plan_requirement_inventory_path=phase_root(attempt_root, 2)
            / "body_plan_requirement_inventory.jsonl",
            output_path=V2_ROOT / "output" / "dvf_3_3_rendered.json",
            trace_path=root / "forbidden-trace.jsonl",
            structural_path=root / "forbidden-structural.jsonl",
            proposition_resolution_path=root / "forbidden-resolution.jsonl",
            equivalence_proof_path=root / "forbidden-proof.jsonl",
            attempt_root=attempt_root,
            compose_context=STAGING_COMPOSE_CONTEXT,
            expected_policy_sha256=sha256_file(POLICY_PATH),
        )
    except ComposeEntrypointGuardError as exc:
        negative_reasons.append(exc.reason)
    negative_report = {
        "schema_version": "dvf-3-3-write-boundary-negative-test-report-v1",
        "tested_forbidden_surfaces": [
            "current_rendered_output",
            "outside_attempt_trace",
        ],
        "observed_reasons": negative_reasons,
        "write_boundary_negative_test_pass": bool(negative_reasons),
    }
    write_once_or_same(root / "write_boundary_negative_test_report.json", negative_report)
    contract = {
        "schema_version": "dvf-3-3-compiler-contract-test-report-v1",
        "attempt_id": attempt_id,
        "compiler_identity": implementation_identity(),
        "candidate_mode_requires_staging": True,
        "policy_hash_required": True,
        "attempt_local_output_required": True,
        "source_inventory_required": True,
        "transformation_registry": list(TRANSFORMATION_IDS),
        "forbidden_transformations": list(FORBIDDEN_TRANSFORMATIONS),
        "item_specific_patch_count": 0,
        "item_specific_override_count": 0,
        "current_core_module_count_changed": False,
        "tooling_allowlist_changed": False,
        "compiler_contract_pass": (
            regression["legacy_normalized_content_hash_identity_pass"]
            and negative_report["write_boundary_negative_test_pass"]
        ),
    }
    write_once_or_same(root / "compiler_contract_test_report.json", contract)
    repetition = build_phase3_repetition_remediation_reports(
        attempt_id=attempt_id,
        attempt_root=attempt_root,
        root=root,
    )
    phase3_pass = (
        contract["compiler_contract_pass"]
        and repetition["facts_authority_gate_pass"]
        and repetition["compiler_rule_projection_pass"]
    )
    result = {
        "schema_version": "dvf-3-3-phase3-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS"
            if phase3_pass
            else "blocked_facts_authority_information_insufficient"
            if not repetition["facts_authority_gate_pass"]
            else "FAIL"
        ),
        "phase3_compiler_evidence_pass": contract["compiler_contract_pass"],
        "semantic_condition_facts_authority_gate_pass": repetition[
            "facts_authority_gate_pass"
        ],
        "compiler_rule_projection_pass": repetition[
            "compiler_rule_projection_pass"
        ],
        "facts_authority_blocked_item_count": repetition[
            "facts_authority_blocked_item_count"
        ],
        "compiler_rule_remediable_item_count": repetition[
            "compiler_rule_remediable_item_count"
        ],
        "repeated_skeleton_cause_analysis_hash": repetition["cause_report_hash"],
        "semantic_lead_rule_projection_report_hash": repetition[
            "projection_report_hash"
        ],
        "facts_authority_enrichment_request_hash": repetition[
            "facts_authority_enrichment_request_hash"
        ],
    }
    write_once_or_same(root / "phase3_result.json", result)
    return result

__all__ = [
    name for name in globals() if not name.startswith("__")
]
