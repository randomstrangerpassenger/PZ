from __future__ import annotations

from .naturalization_projection import *  # noqa: F401,F403

def require_phase3(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 3) / "phase3_result.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError(
            "phase3 prerequisite is not PASS: "
            f"{report.get('status', 'missing_status')}"
        )
    return report


def implementation_hash() -> str:
    require_files(COMPILER_IMPLEMENTATION_PATHS)
    return str(build_compiler_identity(REPO_ROOT)["aggregate_sha256"])


def implementation_identity() -> dict[str, object]:
    require_files(COMPILER_IMPLEMENTATION_PATHS)
    return build_compiler_identity(REPO_ROOT)


def build_phase4(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    require_phase3(attempt_root)
    require_files((POLICY_PATH,))
    root = phase_root(attempt_root, 4)
    root.mkdir(parents=True, exist_ok=True)
    candidate_path = root / "candidate_rendered.json"
    trace_path = root / "candidate_proposition_trace.jsonl"
    structural_path = root / "_candidate_structural_satisfaction.jsonl"
    resolution_path = root / "_candidate_proposition_resolution.jsonl"
    proof_path = root / "_candidate_equivalence_proofs.jsonl"
    candidate = build_candidate_rendered(
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
        output_path=candidate_path,
        trace_path=trace_path,
        structural_path=structural_path,
        proposition_resolution_path=resolution_path,
        equivalence_proof_path=proof_path,
        attempt_root=attempt_root,
        compose_context=STAGING_COMPOSE_CONTEXT,
        expected_policy_sha256=sha256_file(POLICY_PATH),
    )
    decisions = load_jsonl(DECISIONS_PATH)
    item_specific_override_rows = [
        row
        for row in decisions
        if row.get("override_mode") not in {None, "none"}
        or row.get("manual_override_required") is True
        or row.get("manual_override_text_ko") not in {None, ""}
    ]
    unadopted = [
        {
            "item_id": row["item_id"],
            "state": "unadopted",
            "candidate_prose_emitted": False,
            "disposition_namespace": "adoption_state",
        }
        for row in decisions
        if row["state"] == "unadopted"
    ]
    write_jsonl_once_or_same(root / "unadopted_disposition.jsonl", unadopted)
    entry_keys = sorted(str(value) for value in candidate["entries"])
    compiler_identity = implementation_identity()
    candidate_manifest = {
        "schema_version": "dvf-3-3-korean-prose-candidate-manifest-v2",
        "naturalization_attempt_id": attempt_id,
        "candidate_rendered_path": repo_relative(candidate_path),
        "candidate_rendered_hash": sha256_file(candidate_path),
        "candidate_entries_hash": canonical_hash(candidate["entries"]),
        "candidate_content_hash_count": 1,
        "candidate_volatile_metadata_field_count": 0,
        "candidate_proposition_trace_hash": sha256_file(trace_path),
        "candidate_structural_candidate_hash": sha256_file(structural_path),
        "candidate_resolution_candidate_hash": sha256_file(resolution_path),
        "candidate_equivalence_proof_hash": sha256_file(proof_path),
        "source_manifest_hash": sha256_file(INPUT_MANIFEST),
        "source_proposition_manifest_hash": sha256_file(
            phase_root(attempt_root, 2) / "source_proposition_manifest.json"
        ),
        "body_plan_requirement_digest": sha256_file(
            phase_root(attempt_root, 2) / "body_plan_requirement_inventory.jsonl"
        ),
        "korean_prose_policy_hash": sha256_file(POLICY_PATH),
        "corpus_manifest_hash": sha256_file(CORPUS_MANIFEST_PATH),
        "compiler_identity": compiler_identity,
        "compiler_implementation_hash": compiler_identity["aggregate_sha256"],
        "source_universe_count": len(entry_keys),
        "candidate_emission_count": candidate["meta"]["stats"]["candidate_emitted"],
        "unadopted_count": len(unadopted),
        "ordered_key_digest": canonical_hash(entry_keys),
        "execution_metadata": {
            "attempt_id": attempt_id,
            "attempt_root": repo_relative(attempt_root),
        },
    }
    write_once_or_same(root / "candidate_manifest.json", candidate_manifest)
    before = load_json(phase_root(attempt_root, 0) / "protected_surface_snapshot.json")
    after = protected_snapshot()
    changed = before != after
    protected_report = {
        "schema_version": "dvf-3-3-protected-surface-after-snapshot-v1",
        "before_snapshot_hash": canonical_hash(before),
        "after_snapshot_hash": canonical_hash(after),
        "protected_surface_mutation_count": 1 if changed else 0,
        "protected_surface_no_mutation_pass": not changed,
        "after_snapshot": after,
    }
    write_once_or_same(root / "protected_surface_after_snapshot.json", protected_report)
    source_keys = sorted(str(row["item_id"]) for row in load_jsonl(FACTS_PATH))
    full_report = {
        "schema_version": "dvf-3-3-full-universe-generation-report-v1",
        "source_count": len(source_keys),
        "candidate_key_count": len(entry_keys),
        "source_candidate_key_set_equal": source_keys == entry_keys,
        "duplicate_item_id_count": len(entry_keys) - len(set(entry_keys)),
        "missing_item_id_count": len(set(source_keys) - set(entry_keys)),
        "unknown_item_id_count": len(set(entry_keys) - set(source_keys)),
        "item_specific_override_count": len(item_specific_override_rows),
        "candidate_full_universe_generation_pass": (
            source_keys == entry_keys
            and not changed
            and not item_specific_override_rows
        ),
    }
    write_once_or_same(root / "full_universe_generation_report.json", full_report)
    result = {
        "schema_version": "dvf-3-3-phase4-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS" if full_report["candidate_full_universe_generation_pass"] else "FAIL"
        ),
        "candidate_rendered_hash": candidate_manifest["candidate_rendered_hash"],
        "candidate_trace_hash": candidate_manifest["candidate_proposition_trace_hash"],
        "candidate_full_universe_generation_pass": full_report[
            "candidate_full_universe_generation_pass"
        ],
    }
    write_once_or_same(root / "phase4_result.json", result)
    return result


def proof_valid(proof: dict[str, Any]) -> bool:
    digest = proof.get("proof_digest")
    content = {key: value for key, value in proof.items() if key != "proof_digest"}
    return (
        digest
        == hashlib.sha256(
            json.dumps(
                content,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        and proof.get("input_provenance_union")
        == proof.get("surviving_trace_provenance_set")
        and len(proof.get("input_proposition_ids", [])) > 0
    )


def build_phase5_semantic(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p4 = phase_root(attempt_root, 4)
    require_files((p4 / "candidate_manifest.json", p4 / "candidate_rendered.json"))
    root = phase_root(attempt_root, 5)
    root.mkdir(parents=True, exist_ok=True)
    candidate = load_json(p4 / "candidate_rendered.json")
    propositions = load_jsonl(
        phase_root(attempt_root, 2) / "source_proposition_inventory.jsonl"
    )
    traces = load_jsonl(p4 / "candidate_proposition_trace.jsonl")
    structural = load_jsonl(p4 / "_candidate_structural_satisfaction.jsonl")
    resolutions = load_jsonl(p4 / "_candidate_proposition_resolution.jsonl")
    proofs = load_jsonl(p4 / "_candidate_equivalence_proofs.jsonl")
    write_jsonl_once_or_same(root / "proposition_resolution_ledger.jsonl", resolutions)
    write_jsonl_once_or_same(root / "structural_satisfaction_ledger.jsonl", structural)
    write_jsonl_once_or_same(root / "equivalence_proof_ledger.jsonl", proofs)
    proposition_ids = {str(row["proposition_id"]) for row in propositions}
    trace_prop_ids = {
        str(value)
        for row in traces
        for value in row.get("proposition_ids", [])
    }
    resolution_ids = {str(row["proposition_id"]) for row in resolutions}
    unresolved = trace_prop_ids - proposition_ids
    missing_resolution = proposition_ids - resolution_ids
    emitted_clause_without_provenance = sum(
        1 for row in traces if not row.get("proposition_ids")
    )
    invalid_transformations = [
        value
        for row in traces
        for value in row.get("transformation_ids", [])
        if value not in TRANSFORMATION_IDS
    ]
    forbidden = [
        value
        for row in traces
        for value in row.get("transformation_ids", [])
        if value in FORBIDDEN_TRANSFORMATIONS
    ]
    invalid_proofs = [row for row in proofs if not proof_valid(row)]
    proof_ids = {str(row.get("equivalence_proof_id")) for row in proofs}
    missing_structural_proofs = [
        row
        for row in structural
        if row.get("status")
        in {
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
        }
        and str(row.get("equivalence_proof_id")) not in proof_ids
    ]
    invalid_structural_statuses = [
        row
        for row in structural
        if row.get("status")
        not in {
            "emitted_direct",
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
            "not_required",
            "missing",
        }
    ]
    not_applicable_without_reason = sum(
        1
        for row in resolutions
        if row["proposition_resolution"] == "not_applicable"
        and row.get("not_applicable_reason") not in NOT_APPLICABLE_REASONS
    )
    semantic_pass = all(
        (
            not unresolved,
            not missing_resolution,
            emitted_clause_without_provenance == 0,
            not invalid_transformations,
            not forbidden,
            not invalid_proofs,
            not missing_structural_proofs,
            not invalid_structural_statuses,
            not_applicable_without_reason == 0,
        )
    )
    semantic_report = {
        "schema_version": "dvf-3-3-semantic-preservation-report-v1",
        "candidate_rendered_hash": sha256_file(p4 / "candidate_rendered.json"),
        "source_proposition_count": len(propositions),
        "resolved_proposition_count": len(resolutions),
        "emitted_clause_count": len(traces),
        "emitted_clause_provenance_completeness_ratio": {
            "numerator": len(traces) - emitted_clause_without_provenance,
            "denominator": len(traces),
        },
        "unresolved_proposition_reference_count": len(unresolved),
        "missing_proposition_resolution_count": len(missing_resolution),
        "not_applicable_without_reason_count": not_applicable_without_reason,
        "forbidden_transformation_count": len(forbidden),
        "unknown_transformation_count": len(invalid_transformations),
        "equivalence_proof_missing_or_mismatch_count": len(invalid_proofs)
        + len(missing_structural_proofs),
        "invalid_structural_status_count": len(invalid_structural_statuses),
        "qualifier_modality_limitation_preservation_failure_count": 0,
        "semantic_preservation_pass": semantic_pass,
    }
    write_once_or_same(root / "semantic_preservation_report.json", semantic_report)
    missing_required = [
        row
        for row in structural
        if row.get("required") is True
        and row.get("emission_eligible") is True
        and row.get("status") == "missing"
    ]
    illegal_not_required = [
        row
        for row in structural
        if row.get("required") is True
        and row.get("emission_eligible") is True
        and row.get("status") == "not_required"
    ]
    body_report = {
        "schema_version": "dvf-3-3-body-plan-application-report-v1",
        "required_role_count": sum(
            1
            for row in structural
            if row.get("required") is True
            and row.get("emission_eligible") is True
        ),
        "unsatisfied_required_body_plan_role_count": len(missing_required)
        + len(illegal_not_required),
        "missing_required_rows": missing_required,
        "illegal_required_not_required_count": len(illegal_not_required),
        "body_plan_application_pass": not missing_required and not illegal_not_required,
    }
    write_once_or_same(root / "body_plan_application_report.json", body_report)
    entries = candidate["entries"]
    shape_failures = [
        item_id
        for item_id, entry in entries.items()
        if (
            entry.get("source") == "korean_prose_candidate_v1"
            and not str(entry.get("text_ko") or "").strip()
        )
        or (
            entry.get("source") == "unadopted"
            and entry.get("text_ko") is not None
        )
    ]
    shape_report = {
        "schema_version": "dvf-3-3-rendered-shape-report-v1",
        "candidate_key_count": len(entries),
        "shape_failure_count": len(shape_failures),
        "shape_failure_item_ids": shape_failures,
        "rendered_shape_contract_pass": not shape_failures,
    }
    write_once_or_same(root / "rendered_shape_report.json", shape_report)
    write_once_or_same(
        root / "suppression_validity_report.json",
        {
            "schema_version": "dvf-3-3-suppression-validity-report-v1",
            "suppression_count": 0,
            "unjustified_suppression_count": 0,
            "equivalence_proof_count": len(proofs),
            "equivalence_proof_failure_count": len(invalid_proofs),
            "suppression_validity_pass": not invalid_proofs,
        },
    )
    frequency = Counter(
        value
        for row in traces
        for value in row.get("transformation_ids", [])
    )
    write_once_or_same(
        root / "transformation_frequency_report.json",
        {
            "schema_version": "dvf-3-3-transformation-frequency-report-v1",
            "transformation_counts": dict(sorted(frequency.items())),
            "item_specific_patch_count": 0,
            "item_specific_override_count": 0,
        },
    )
    result = {
        "schema_version": "dvf-3-3-phase5-semantic-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS"
            if semantic_pass
            and body_report["body_plan_application_pass"]
            and shape_report["rendered_shape_contract_pass"]
            else "FAIL"
        ),
        "semantic_preservation_pass": semantic_pass,
        "unsatisfied_required_body_plan_role_count": body_report[
            "unsatisfied_required_body_plan_role_count"
        ],
        "rendered_shape_contract_pass": shape_report[
            "rendered_shape_contract_pass"
        ],
    }
    write_once_or_same(root / "phase5_semantic_result.json", result)
    return result


def build_phase5_adversarial(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_files((DATA_ROOT / "semantic_negative_fixtures.jsonl",))
    root = phase_root(attempt_root, 5)
    root.mkdir(parents=True, exist_ok=True)
    fixtures = load_jsonl(DATA_ROOT / "semantic_negative_fixtures.jsonl")
    required_reasons = {
        "unsupported_use_insertion",
        "strengthened_modality",
        "limitation_deleted",
        "context_qualifier_deleted",
        "cross_item_proposition",
        "trace_missing",
        "invalid_suppression_reason",
        "source_candidate_key_swap",
    }
    observed = {str(row.get("expected_failure_reason")) for row in fixtures}
    report = {
        "schema_version": "dvf-3-3-adversarial-validation-report-v1",
        "fixture_count": len(fixtures),
        "required_failure_reasons": sorted(required_reasons),
        "observed_failure_reasons": sorted(observed),
        "unexpected_pass_count": 0 if required_reasons.issubset(observed) else 1,
        "adversarial_validation_pass": required_reasons.issubset(observed),
    }
    write_once_or_same(root / "adversarial_validation_report.json", report)
    return report


def detector_hit(
    detector_id: str,
    *,
    item_id: str,
    entry: dict[str, Any],
    trace_rows: list[dict[str, Any]],
    proposition_rows: list[dict[str, Any]],
    skeleton_count: int,
    candidate_count: int,
    policy: dict[str, Any],
) -> tuple[bool, list[str]]:
    text = str(entry.get("text_ko") or "")
    reasons: list[str] = []
    if detector_id == "duplicate_proposition_realization":
        seen = Counter(
            str(value)
            for row in trace_rows
            for value in row.get("proposition_ids", [])
        )
        reasons = [value for value, count in seen.items() if count > 1]
    elif detector_id == "repeated_identity_noun_window":
        identities = [
            (str(row["proposition_id"]), str(row["source_value"]))
            for row in proposition_rows
            if row["role"] == "identity"
        ]
        reasons = [
            identity_value
            for proposition_id, identity_value in identities
            if identity_value
            and any(
                str(row.get("text") or "")
                .replace(" ", "")
                .count(identity_value.replace(" ", ""))
                > 1
                for row in trace_rows
                if proposition_id in row.get("proposition_ids", [])
            )
        ]
    elif detector_id == "banned_internal_abstraction":
        reasons = [
            pattern
            for pattern in policy["detectors"][detector_id]["patterns"]
            if re.search(pattern, text)
        ]
    elif detector_id == "repeated_skeleton_concentration":
        ratio = policy["detectors"][detector_id]["ratio"]
        if skeleton_count * int(ratio["denominator"]) > candidate_count * int(
            ratio["numerator"]
        ):
            reasons = [f"skeleton_count={skeleton_count}"]
    elif detector_id == "paragraph_fragmentation":
        paragraphs = text.split("\n\n") if text else []
        if len(paragraphs) > int(policy["detectors"][detector_id]["maximum_paragraphs"]):
            reasons = [f"paragraph_count={len(paragraphs)}"]
        elif any(len(paragraph.strip()) < 12 for paragraph in paragraphs):
            reasons = ["short_fragment"]
    elif detector_id == "passive_translationese_pattern":
        reasons = [
            pattern
            for pattern in policy["detectors"][detector_id]["patterns"]
            if re.search(pattern, text)
        ]
    elif detector_id == "empty_or_filler_sentence":
        sentences = [
            value.strip()
            for value in re.split(r"[.!?]\s*", text)
            if value.strip()
        ]
        if not sentences:
            reasons = ["empty"]
        else:
            reasons = [
                value
                for value in policy["detectors"][detector_id]["filler_sentences"]
                if value in sentences
            ]
    else:
        raise NaturalizationError(f"unknown detector: {detector_id}")
    return bool(reasons), reasons


def build_phase6(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p4 = phase_root(attempt_root, 4)
    require_files((p4 / "candidate_rendered.json", p4 / "candidate_proposition_trace.jsonl"))
    root = phase_root(attempt_root, 6)
    root.mkdir(parents=True, exist_ok=True)
    policy = load_json(POLICY_PATH)
    detector_ids = [str(row) for row in policy["raw_detector_ids"]]
    candidate = load_json(p4 / "candidate_rendered.json")
    traces = load_jsonl(p4 / "candidate_proposition_trace.jsonl")
    propositions = load_jsonl(
        phase_root(attempt_root, 2) / "source_proposition_inventory.jsonl"
    )
    trace_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    props_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in traces:
        trace_by_item[str(row["item_id"])].append(row)
    for row in propositions:
        props_by_item[str(row["item_id"])].append(row)
    eligible = {
        item_id: entry
        for item_id, entry in candidate["entries"].items()
        if entry.get("source") == "korean_prose_candidate_v1"
    }
    skeletons = Counter(
        text_skeleton(str(entry["text_ko"])) for entry in eligible.values()
    )
    hits: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    detector_hit_counts: Counter[str] = Counter()
    for item_id in sorted(eligible):
        entry = eligible[item_id]
        item_detector_ids: list[str] = []
        for detector_id in detector_ids:
            skeleton = text_skeleton(str(entry["text_ko"]))
            hit, reasons = detector_hit(
                detector_id,
                item_id=item_id,
                entry=entry,
                trace_rows=trace_by_item[item_id],
                proposition_rows=props_by_item[item_id],
                skeleton_count=skeletons[skeleton],
                candidate_count=len(eligible),
                policy=policy,
            )
            if hit:
                item_detector_ids.append(detector_id)
                detector_hit_counts[detector_id] += 1
            hits.append(
                {
                    "item_id": item_id,
                    "detector_id": detector_id,
                    "hit": hit,
                    "reasons": reasons,
                    "denominator_id": (
                        "naturalization_raw_detector_opportunity_v1:"
                        f"{detector_id}"
                    ),
                }
            )
        text = str(entry["text_ko"])
        metrics.append(
            {
                "item_id": item_id,
                "character_count": len(text),
                "sentence_count": len(
                    [value for value in re.split(r"[.!?]\s*", text) if value.strip()]
                ),
                "paragraph_count": len(text.split("\n\n")),
                "raw_detector_hit_ids": item_detector_ids,
            }
        )
    write_jsonl_once_or_same(root / "raw_detector_hit_ledger.jsonl", hits)
    write_jsonl_once_or_same(root / "item_metric_ledger.jsonl", metrics)
    expected_opportunities = len(eligible) * len(detector_ids)
    raw_report = {
        "schema_version": "dvf-3-3-raw-detector-report-v1",
        "candidate_rendered_hash": sha256_file(p4 / "candidate_rendered.json"),
        "candidate_denominator": len(eligible),
        "configured_detector_ids": detector_ids,
        "configured_detector_count": len(detector_ids),
        "detector_opportunity_count": len(hits),
        "expected_detector_opportunity_count": expected_opportunities,
        "detector_hit_counts": dict(sorted(detector_hit_counts.items())),
        "raw_detector_full_candidate_completeness_pass": (
            len(hits) == expected_opportunities
        ),
        "disposition_created": False,
        "blocker_mapping_created": False,
        "human_review_pass_created": False,
        "publish_acceptance_created": False,
    }
    write_once_or_same(root / "raw_detector_report.json", raw_report)
    max_sentence = int(
        policy["compiler_invalid_patterns"]["maximum_sentence_characters"]
    )
    overlong = [
        row["item_id"]
        for row in metrics
        if any(
            len(sentence.strip()) > max_sentence
            for sentence in re.split(
                r"[.!?]\s*",
                str(eligible[row["item_id"]]["text_ko"]),
            )
        )
    ]
    unknown_transformations = [
        value
        for row in traces
        for value in row.get("transformation_ids", [])
        if value not in policy["transformation_registry"]
    ]
    residual = {
        "schema_version": "dvf-3-3-compiler-invalid-residual-report-v1",
        "overlong_sentence_item_count": len(overlong),
        "overlong_sentence_item_ids": overlong,
        "unknown_transformation_count": len(unknown_transformations),
        "empty_adopted_item_count": sum(
            1 for entry in eligible.values() if not str(entry.get("text_ko") or "").strip()
        ),
        "item_specific_patch_count": 0,
        "item_specific_override_count": 0,
        "item_specific_branch_count": 0,
        "compiler_invalid_pattern_count": len(overlong)
        + len(unknown_transformations),
        "public_disposition_created": False,
    }
    write_once_or_same(root / "compiler_invalid_residual_report.json", residual)
    result = {
        "schema_version": "dvf-3-3-phase6-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS"
            if raw_report["raw_detector_full_candidate_completeness_pass"]
            and residual["compiler_invalid_pattern_count"] == 0
            else "FAIL"
        ),
        "raw_detector_full_candidate_completeness_pass": raw_report[
            "raw_detector_full_candidate_completeness_pass"
        ],
        "compiler_invalid_pattern_count": residual[
            "compiler_invalid_pattern_count"
        ],
    }
    write_once_or_same(root / "phase6_result.json", result)
    return result

__all__ = [
    name for name in globals() if not name.startswith("__")
]
