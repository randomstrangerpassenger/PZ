from artifact_lifecycle_executor_support import *

class ArtifactLifecycleExecutorTest(unittest.TestCase):
    def test_full_chain_is_receipt_bound_and_exact_leaf_delete_is_recoverable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="f-") as temporary:
            root = Path(temporary)
            repo, external, candidate = build_fixture(root)
            self.assertFalse(candidate["zero_live_consumers"])
            self.assertGreater(len(candidate["direct_consumers"]), 0)
            durable = repo / DURABLE
            pre_delete = durable / "pre_delete_current_route_receipt.json"
            selection = external / "owner-selection.json"
            baseline_promotion = durable / "baseline_promotion_receipt.json"
            write_json(
                selection,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_exact_archive_selection_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "physical_resolved_root": repo.as_posix(),
                    "baseline_run_identity": json.loads(
                        (durable / "baseline_inventory.json").read_text(encoding="utf-8")
                    )["run_identity"],
                    "baseline_promotion_receipt_sha256": sha256(baseline_promotion),
                    "pre_delete_current_route_receipt_sha256": sha256(pre_delete),
                    "rows": [
                        {
                            "logical_artifact_id": candidate["logical_artifact_id"],
                            "path": candidate["path"],
                            "sha256": candidate["sha256"],
                            "size_bytes": candidate["size_bytes"],
                        }
                    ],
                },
            )

            checkpoint_manifest = durable / "validation_checkpoint_manifest.json"
            protected_manifest = durable / "protected_surface_successor_manifest.json"
            protected_bytes = protected_manifest.read_bytes()

            def refresh_protected_successor_bindings() -> None:
                payload = json.loads(protected_bytes.decode("utf-8"))
                targets = {
                    pre_delete.relative_to(repo).as_posix(): pre_delete,
                    checkpoint_manifest.relative_to(repo).as_posix(): checkpoint_manifest,
                }
                for row in payload["revisions"][-1]["added_protected_rows"]:
                    target = targets[row["path"]]
                    row["expected_git_blob_id"] = git_blob_id(target.read_bytes())
                    row["after_sha256_lf"] = sha256(target)
                write_json(protected_manifest, payload)

            def assert_protected_successor_rejected(label: str, mutator) -> None:
                payload = json.loads(protected_bytes.decode("utf-8"))
                mutator(payload)
                write_json(protected_manifest, payload)
                git(repo, "add", protected_manifest.relative_to(repo).as_posix())
                git(repo, "commit", "-m", f"tamper STEP 8 protected successor {label}")
                rejected = invoke(
                    EXECUTOR,
                    "dry-run",
                    "--repo", repo,
                    "--baseline", durable / "baseline_inventory.json",
                    "--promotion-receipt", baseline_promotion,
                    "--pre-delete-route-receipt", pre_delete,
                    "--selection", selection,
                    "--manifest-out", external / f"rejected-protected-{label}/operation.json",
                    "--receipt-out", external / f"rejected-protected-{label}/receipt.json",
                    cwd=repo,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("STEP 8 protected successor", rejected.stderr)
                protected_manifest.write_bytes(protected_bytes)
                git(repo, "add", protected_manifest.relative_to(repo).as_posix())
                git(repo, "commit", "-m", f"restore STEP 8 protected successor after {label}")

            assert_protected_successor_rejected(
                "prior-revision",
                lambda payload: payload["revisions"][0].update(
                    {"reason": "tampered predecessor revision"}
                ),
            )
            assert_protected_successor_rejected(
                "extra-revision",
                lambda payload: payload["revisions"].append(
                    dict(payload["revisions"][-1])
                ),
            )
            assert_protected_successor_rejected(
                "missing-row",
                lambda payload: payload["revisions"][-1]["added_protected_rows"].pop(),
            )
            assert_protected_successor_rejected(
                "predecessor",
                lambda payload: payload["revisions"][-1].update(
                    {"predecessor_commit": "0" * 40}
                ),
            )
            assert_protected_successor_rejected(
                "after-hash",
                lambda payload: payload["revisions"][-1]["added_protected_rows"][0].update(
                    {"after_sha256_lf": "0" * 64}
                ),
            )
            assert_protected_successor_rejected(
                "before-blob",
                lambda payload: payload["revisions"][-1]["added_protected_rows"][0].update(
                    {"before_git_blob_id": "0" * 40}
                ),
            )

            audit_receipt_path = external / "output-isolation-audit/current_route_output_isolation_audit_receipt.json"
            audit_receipt_bytes = audit_receipt_path.read_bytes()
            tampered_audit = json.loads(audit_receipt_bytes.decode("utf-8"))
            tampered_audit["status"] = "FAIL"
            write_json(audit_receipt_path, tampered_audit)
            rejected_audit_receipt = invoke(
                EXECUTOR,
                "dry-run",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--promotion-receipt", baseline_promotion,
                "--pre-delete-route-receipt", pre_delete,
                "--selection", selection,
                "--manifest-out", external / "rejected-audit-receipt/operation.json",
                "--receipt-out", external / "rejected-audit-receipt/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_audit_receipt.returncode, 0)
            self.assertIn("output-isolation audit identity", rejected_audit_receipt.stderr)
            audit_receipt_path.write_bytes(audit_receipt_bytes)

            pre_delete_bytes = pre_delete.read_bytes()
            checkpoint_bytes = checkpoint_manifest.read_bytes()
            omitted = json.loads(pre_delete_bytes.decode("utf-8"))
            omitted["command_receipts"] = [
                row
                for row in omitted["command_receipts"]
                if not str(row["path"]).endswith("verify-current-route-output-isolation.json")
            ]
            omitted_command_set = []
            for row in omitted["command_receipts"]:
                payload = json.loads(Path(row["path"]).read_text(encoding="utf-8"))
                omitted_command_set.append(
                    {
                        "command_id": payload["command_id"],
                        "path": Path(row["path"]).resolve().as_posix(),
                        "sha256": row["sha256"],
                    }
                )
            omitted_command_set.sort(key=lambda row: row["command_id"])
            omitted["command_receipt_set_sha256"] = hashlib.sha256(
                canonical_bytes(omitted_command_set)
            ).hexdigest()
            write_json(pre_delete, omitted)
            omitted_checkpoint = json.loads(checkpoint_bytes.decode("utf-8"))
            omitted_checkpoint["checkpoints"][-1]["command_receipt_set_sha256"] = omitted[
                "command_receipt_set_sha256"
            ]
            omitted_checkpoint["checkpoints"][-1]["required_receipt"]["sha256"] = sha256(
                pre_delete
            )
            write_json(checkpoint_manifest, omitted_checkpoint)
            refresh_protected_successor_bindings()
            git(
                repo,
                "add",
                pre_delete.relative_to(repo).as_posix(),
                checkpoint_manifest.relative_to(repo).as_posix(),
                protected_manifest.relative_to(repo).as_posix(),
            )
            git(repo, "commit", "-m", "tamper pre-delete audit command omission")
            rejected_audit_omission = invoke(
                EXECUTOR,
                "dry-run",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--promotion-receipt", baseline_promotion,
                "--pre-delete-route-receipt", pre_delete,
                "--selection", selection,
                "--manifest-out", external / "rejected-audit-omission/operation.json",
                "--receipt-out", external / "rejected-audit-omission/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_audit_omission.returncode, 0)
            self.assertIn("output-isolation mismatch", rejected_audit_omission.stderr)
            pre_delete.write_bytes(pre_delete_bytes)
            checkpoint_manifest.write_bytes(checkpoint_bytes)
            protected_manifest.write_bytes(protected_bytes)
            git(
                repo,
                "add",
                pre_delete.relative_to(repo).as_posix(),
                checkpoint_manifest.relative_to(repo).as_posix(),
                protected_manifest.relative_to(repo).as_posix(),
            )
            git(repo, "commit", "-m", "restore exact pre-delete audit command")

            current_command = external / "commands/001-pre-delete-current-route.json"
            current_spec = external / "commands/001-pre-delete-current-route.command.json"
            current_command_bytes = current_command.read_bytes()
            current_spec_bytes = current_spec.read_bytes()
            canonical_current_argv = json.loads(current_spec_bytes.decode("utf-8"))["argv"]

            def assert_rejected_current_argv(label: str, mutated_argv: list[str]) -> None:
                spec_payload = json.loads(current_spec_bytes.decode("utf-8"))
                spec_payload["argv"] = mutated_argv
                write_json(current_spec, spec_payload)
                command_payload = json.loads(current_command_bytes.decode("utf-8"))
                command_payload["decoded_argv"] = mutated_argv
                command_payload["command_spec"]["sha256"] = sha256(current_spec)
                write_json(current_command, command_payload)
                receipt_payload = json.loads(pre_delete_bytes.decode("utf-8"))
                for row in receipt_payload["command_receipts"]:
                    if Path(row["path"]).resolve() == current_command.resolve():
                        row["sha256"] = sha256(current_command)
                command_set = []
                for row in receipt_payload["command_receipts"]:
                    payload = json.loads(Path(row["path"]).read_text(encoding="utf-8"))
                    command_set.append(
                        {
                            "command_id": payload["command_id"],
                            "path": Path(row["path"]).resolve().as_posix(),
                            "sha256": row["sha256"],
                        }
                    )
                command_set.sort(key=lambda row: row["command_id"])
                receipt_payload["command_receipt_set_sha256"] = hashlib.sha256(
                    canonical_bytes(command_set)
                ).hexdigest()
                write_json(pre_delete, receipt_payload)
                checkpoint_payload = json.loads(checkpoint_bytes.decode("utf-8"))
                checkpoint_payload["checkpoints"][-1]["command_receipt_set_sha256"] = receipt_payload[
                    "command_receipt_set_sha256"
                ]
                checkpoint_payload["checkpoints"][-1]["required_receipt"]["sha256"] = sha256(
                    pre_delete
                )
                write_json(checkpoint_manifest, checkpoint_payload)
                refresh_protected_successor_bindings()
                git(
                    repo,
                    "add",
                    pre_delete.relative_to(repo).as_posix(),
                    checkpoint_manifest.relative_to(repo).as_posix(),
                    protected_manifest.relative_to(repo).as_posix(),
                )
                git(repo, "commit", "-m", f"tamper current-route argv {label}")
                rejected = invoke(
                    EXECUTOR,
                    "dry-run",
                    "--repo", repo,
                    "--baseline", durable / "baseline_inventory.json",
                    "--promotion-receipt", baseline_promotion,
                    "--pre-delete-route-receipt", pre_delete,
                    "--selection", selection,
                    "--manifest-out", external / f"rejected-{label}/operation.json",
                    "--receipt-out", external / f"rejected-{label}/receipt.json",
                    cwd=repo,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("exact canonical invocation", rejected.stderr)
                current_spec.write_bytes(current_spec_bytes)
                current_command.write_bytes(current_command_bytes)
                pre_delete.write_bytes(pre_delete_bytes)
                checkpoint_manifest.write_bytes(checkpoint_bytes)
                protected_manifest.write_bytes(protected_bytes)
                git(
                    repo,
                    "add",
                    pre_delete.relative_to(repo).as_posix(),
                    checkpoint_manifest.relative_to(repo).as_posix(),
                    protected_manifest.relative_to(repo).as_posix(),
                )
                git(repo, "commit", "-m", f"restore current-route argv after {label}")

            assert_rejected_current_argv(
                "alternate-taxonomy",
                canonical_current_argv
                + [
                    "--taxonomy",
                    "Iris/_docs/round3/current_route_required_validations.json",
                ],
            )
            alternate_route_result = external / "commands/alternate-current-route-result.json"
            write_json(
                alternate_route_result,
                {"status": "PASS", "summary": {"failed": 0, "errors": 0}},
            )
            assert_rejected_current_argv(
                "duplicate-out",
                canonical_current_argv + ["--out", alternate_route_result.as_posix()],
            )

            def assert_fresh_reference_blocked(
                label: str,
                relative: Path,
                content: str,
            ) -> None:
                source = repo / relative
                source.parent.mkdir(parents=True, exist_ok=True)
                original = source.read_bytes() if source.exists() else None
                source.write_text(content, encoding="utf-8")
                rejected = invoke(
                    EXECUTOR,
                    "dry-run",
                    "--repo", repo,
                    "--baseline", durable / "baseline_inventory.json",
                    "--promotion-receipt", baseline_promotion,
                    "--pre-delete-route-receipt", pre_delete,
                    "--selection", selection,
                    "--manifest-out", external / f"rejected-{label}/operation.json",
                    "--receipt-out", external / f"rejected-{label}/receipt.json",
                    cwd=repo,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn(
                    "current reference graph does not prove zero live consumers",
                    rejected.stderr,
                )
                self.assertFalse((external / f"rejected-{label}/operation.json").exists())
                if original is None:
                    source.unlink()
                else:
                    source.write_bytes(original)

            matched_reader = (
                repo / "Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py"
            )
            matched_reader_bytes = matched_reader.read_bytes()
            matched_reader.write_text(
                (
                    "from pathlib import Path\n"
                    f"Path({CANDIDATE.as_posix()!r}).read_text(encoding='utf-8')\n"
                ),
                encoding="utf-8",
            )
            graph_probe_script = "\n".join(
                [
                    "import json,sys",
                    "from pathlib import Path",
                    f"sys.path.insert(0, {str(REPORTER.parent)!r})",
                    (
                        "from report_artifact_lifecycle import "
                        "git_path_set,load_lifecycle_reference_policy,reference_graph"
                    ),
                    "repo=Path.cwd().resolve()",
                    f"target={CANDIDATE.as_posix()!r}",
                    (
                        "rows=[{'path':target,'path_access':'readable',"
                        "'producer':'build_legacy_active_silent_current_surface_guard_round.py'}]"
                    ),
                    "policy=load_lifecycle_reference_policy(repo)",
                    (
                        "graph=reference_graph(repo,rows,git_path_set(repo,'ls-files','-z'),"
                        "git_path_set(repo,'ls-files','-z','--others','--exclude-standard'),"
                        "lifecycle_policy=policy)"
                    ),
                    "print(json.dumps(graph[target],sort_keys=True))",
                ]
            )
            matched_probe = subprocess.run(
                [sys.executable, "-B", "-c", graph_probe_script],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            matched_reader.write_bytes(matched_reader_bytes)
            self.assertEqual(matched_probe.returncode, 0, matched_probe.stderr)
            matched_graph = json.loads(matched_probe.stdout)
            matched_relative = matched_reader.relative_to(repo).as_posix()
            self.assertIn(matched_relative, matched_graph["consumer_axes"]["python_read"])
            self.assertIn(matched_relative, matched_graph["direct_consumers"])
            self.assertNotIn(
                matched_relative,
                matched_graph["consumer_axes"].get("test_fixture_reference", []),
            )

            assert_fresh_reference_blocked(
                "explicit-read",
                Path("live_guard_consumer.py"),
                (
                    "from pathlib import Path\n"
                    f"Path({CANDIDATE.as_posix()!r}).read_text(encoding='utf-8')\n"
                ),
            )
            assert_fresh_reference_blocked(
                "unscoped-manifest",
                Path("live_guard_manifest.json"),
                json.dumps({"path": CANDIDATE.as_posix()}) + "\n",
            )

            archive_root = external / "archive"
            restore_root = external / "restore"
            archive_root.mkdir(parents=True)
            restore_root.mkdir(parents=True)
            operation = archive_root / "archive_operation_manifest.json"
            dry = archive_root / "dry_run_receipt.json"
            archive_receipt = archive_root / "archive_receipt.json"
            verify = archive_root / "archive_verify_receipt.json"
            restore = archive_root / "restore_verify_receipt.json"
            commands = [
                (
                    "dry-run",
                    "--repo", repo,
                    "--baseline", durable / "baseline_inventory.json",
                    "--promotion-receipt", baseline_promotion,
                    "--pre-delete-route-receipt", pre_delete,
                    "--selection", selection,
                    "--manifest-out", operation,
                    "--receipt-out", dry,
                ),
                (
                    "archive",
                    "--repo", repo,
                    "--operation-manifest", operation,
                    "--prior-receipt", dry,
                    "--archive-root", archive_root,
                    "--receipt-out", archive_receipt,
                ),
                (
                    "verify",
                    "--operation-manifest", operation,
                    "--prior-receipt", archive_receipt,
                    "--receipt-out", verify,
                ),
                (
                    "restore-verify",
                    "--operation-manifest", operation,
                    "--prior-receipt", verify,
                    "--restore-root", restore_root,
                    "--receipt-out", restore,
                ),
            ]
            result = invoke(EXECUTOR, *commands[0], cwd=repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            operation_payload = json.loads(operation.read_text(encoding="utf-8"))
            self.assertFalse(operation_payload["delete_eligible"])
            self.assertGreater(
                len(operation_payload["rows"][0]["direct_consumers"]),
                0,
            )
            fresh_report = operation_payload["zero_live_reference_report"]
            self.assertEqual(fresh_report["live_reference_count"], 0)
            self.assertEqual(fresh_report["consumer_scan_hold_count"], 0)
            self.assertTrue(fresh_report["rows"][0]["zero_live_consumers"])
            self.assertEqual(fresh_report["rows"][0]["direct_consumers"], [])
            self.assertEqual(
                operation_payload["lifecycle_reference_policy"],
                fresh_report["reference_policy"],
            )
            self.assertTrue(fresh_report["reference_policy"]["git_blob_id"])
            for role in (
                "report_only_staging_residue",
                "cold_archive_payload",
                "test_fixture",
            ):
                self.assertGreaterEqual(fresh_report["excluded_role_counts"][role], 1)

            tampered_operation_payload = json.loads(operation.read_text(encoding="utf-8"))
            tampered_report = tampered_operation_payload["zero_live_reference_report"]
            tampered_report["excluded_role_counts"]["test_fixture"] += 1
            tampered_report.pop("report_sha256")
            tampered_report["report_sha256"] = hashlib.sha256(
                canonical_bytes(tampered_report)
            ).hexdigest()
            tampered_operation = external / "tampered-summary/operation.json"
            write_json(tampered_operation, tampered_operation_payload)
            rejected_summary = invoke(
                EXECUTOR,
                "archive",
                "--repo", repo,
                "--operation-manifest", tampered_operation,
                "--prior-receipt", dry,
                "--archive-root", external / "tampered-summary/archive",
                "--receipt-out", external / "tampered-summary/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_summary.returncode, 0)
            self.assertIn("excluded-role summary mismatch", rejected_summary.stderr)
            self.assertFalse((external / "tampered-summary/receipt.json").exists())

            result = invoke(EXECUTOR, *commands[1], cwd=repo)
            self.assertEqual(result.returncode, 0, result.stderr)

            archive_receipt_bytes = archive_receipt.read_bytes()
            archive_receipt_payload = json.loads(archive_receipt_bytes.decode("utf-8"))
            archive_path = Path(archive_receipt_payload["archive_path"])
            archive_bytes = archive_path.read_bytes()
            with zipfile.ZipFile(archive_path, "r") as source_bundle:
                member_payloads = [
                    (info.filename, source_bundle.read(info.filename))
                    for info in source_bundle.infolist()
                ]
            with zipfile.ZipFile(
                archive_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
                allowZip64=True,
            ) as tampered_bundle:
                for name, payload in member_payloads:
                    tampered_bundle.writestr(
                        name,
                        b'{"tampered":true}\n'
                        if name == "_iris_archive_operation_manifest.json"
                        else payload,
                    )
            archive_receipt_payload["archive_sha256"] = sha256(archive_path)
            archive_receipt_payload["archive_bytes"] = archive_path.stat().st_size
            write_json(archive_receipt, archive_receipt_payload)
            rejected_embedded_manifest = invoke(
                EXECUTOR,
                "verify",
                "--operation-manifest", operation,
                "--prior-receipt", archive_receipt,
                "--receipt-out", archive_root / "rejected_embedded_manifest.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_embedded_manifest.returncode, 0)
            self.assertIn("embedded archive operation manifest byte identity", rejected_embedded_manifest.stderr)
            self.assertFalse((archive_root / "rejected_embedded_manifest.json").exists())
            archive_path.write_bytes(archive_bytes)
            archive_receipt.write_bytes(archive_receipt_bytes)

            for command in commands[2:]:
                result = invoke(EXECUTOR, *command, cwd=repo)
                self.assertEqual(result.returncode, 0, result.stderr)

            guard_policy = repo / DURABLE / "current_surface_guard_successor_manifest.json"
            guard_policy_bytes = guard_policy.read_bytes()
            guard_policy.write_bytes(guard_policy_bytes + b"\n")
            rejected_uncommitted_policy = invoke(
                EXECUTOR,
                "verify",
                "--operation-manifest", operation,
                "--prior-receipt", archive_receipt,
                "--receipt-out", archive_root / "rejected_uncommitted_policy.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_uncommitted_policy.returncode, 0)
            self.assertIn("not exact and HEAD-bound", rejected_uncommitted_policy.stderr)
            guard_policy.write_bytes(guard_policy_bytes)

            broadened_policy = json.loads(guard_policy_bytes.decode("utf-8"))
            broadened_policy["lifecycle_reference_disposition"][
                "nonblocking_referrer_rules"
            ][-1]["allowed_axes"].append("python_read")
            write_json(guard_policy, broadened_policy)
            git(repo, "add", guard_policy.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "broaden lifecycle reference policy fixture")
            rejected_broadened_policy = invoke(
                EXECUTOR,
                "verify",
                "--operation-manifest", operation,
                "--prior-receipt", archive_receipt,
                "--receipt-out", archive_root / "rejected_broadened_policy.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_broadened_policy.returncode, 0)
            self.assertIn("rule contract mismatch", rejected_broadened_policy.stderr)
            self.assertFalse((archive_root / "rejected_broadened_policy.json").exists())
            guard_policy.write_bytes(guard_policy_bytes)
            git(repo, "add", guard_policy.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "restore broadened lifecycle reference policy fixture")

            write_json(guard_policy, {"malformed": True})
            git(repo, "add", guard_policy.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "malform lifecycle reference policy fixture")
            rejected_malformed_policy = invoke(
                EXECUTOR,
                "verify",
                "--operation-manifest", operation,
                "--prior-receipt", archive_receipt,
                "--receipt-out", archive_root / "rejected_malformed_policy.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_malformed_policy.returncode, 0)
            self.assertIn("authority/schema mismatch", rejected_malformed_policy.stderr)
            guard_policy.write_bytes(guard_policy_bytes)
            git(repo, "add", guard_policy.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "restore lifecycle reference policy fixture")

            guard_policy.unlink()
            git(repo, "add", "-u", guard_policy.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "remove lifecycle reference policy fixture")
            rejected_missing_policy = invoke(
                EXECUTOR,
                "verify",
                "--operation-manifest", operation,
                "--prior-receipt", archive_receipt,
                "--receipt-out", archive_root / "rejected_missing_policy.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_missing_policy.returncode, 0)
            self.assertIn("policy is missing", rejected_missing_policy.stderr)
            guard_policy.write_bytes(guard_policy_bytes)
            git(repo, "add", guard_policy.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "restore missing lifecycle reference policy fixture")

            archive_promotion_external = external / "promotion/archive.json"
            promotion = invoke(
                PROMOTER,
                "archive",
                "--repo", repo,
                "--source-operation-manifest", operation,
                "--source-archive-receipt", archive_receipt,
                "--source-verify-receipt", verify,
                "--source-restore-receipt", restore,
                "--destination-root", durable,
                "--receipt-out", archive_promotion_external,
                cwd=repo,
            )
            self.assertEqual(promotion.returncode, 0, promotion.stderr)
            durable_operation = durable / "archive_operation_manifest.json"
            durable_restore = durable / "archive_restore_receipt.json"
            durable_promotion = durable / "archive_promotion_receipt.json"
            durable_archive_bytes = {
                path: path.read_bytes()
                for path in (durable_operation, durable_restore, durable_promotion)
            }
            physical_branch = git(repo, "branch", "--show-current")
            git(repo, "switch", "-c", "side-archive-evidence")
            git(repo, "add", DURABLE.as_posix())
            git(repo, "commit", "-m", "side-branch archive evidence")
            side_archive_commit = git(repo, "rev-parse", "HEAD")
            side_approval = external / "side-delete-approval.json"
            write_json(
                side_approval,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_post_archive_delete_approval_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "archive_evidence_commit": side_archive_commit,
                    "operation_id": json.loads(durable_operation.read_text(encoding="utf-8"))["operation_id"],
                    "exact_paths": [CANDIDATE.as_posix()],
                    "archive_operation_manifest_sha256": sha256(durable_operation),
                    "archive_restore_receipt_sha256": sha256(durable_restore),
                    "archive_promotion_receipt_sha256": sha256(durable_promotion),
                    "pre_delete_current_route_receipt_sha256": sha256(pre_delete),
                },
            )
            git(repo, "switch", physical_branch)
            for path, payload in durable_archive_bytes.items():
                path.write_bytes(payload)
            rejected_side_branch = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", side_archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", side_approval,
                "--out", external / "archive/rejected-side-branch-evidence.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_side_branch.returncode, 0)
            self.assertIn("ancestor of physical HEAD", rejected_side_branch.stderr)
            self.assertFalse((external / "archive/rejected-side-branch-evidence.json").exists())
            physical_runner = repo / "Iris/_docs/round3/round3_run_contract_tests.py"
            validated_runner_bytes = physical_runner.read_bytes()
            physical_runner.write_text("raise SystemExit('changed after validation')\n", encoding="utf-8")
            git(repo, "add", DURABLE.as_posix(), physical_runner.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "adopt archive evidence with stale candidate change")
            archive_commit = git(repo, "rev-parse", "HEAD")
            approval = external / "delete-approval.json"
            write_json(
                approval,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_post_archive_delete_approval_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "archive_evidence_commit": archive_commit,
                    "operation_id": json.loads(durable_operation.read_text(encoding="utf-8"))["operation_id"],
                    "exact_paths": [CANDIDATE.as_posix()],
                    "archive_operation_manifest_sha256": sha256(durable_operation),
                    "archive_restore_receipt_sha256": sha256(durable_restore),
                    "archive_promotion_receipt_sha256": sha256(durable_promotion),
                    "pre_delete_current_route_receipt_sha256": sha256(pre_delete),
                },
            )
            rejected_stale = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-stale-candidate.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_stale.returncode, 0)
            self.assertIn("validated Common candidate", rejected_stale.stderr)
            self.assertFalse((external / "archive/rejected-stale-candidate.json").exists())
            physical_runner.write_bytes(validated_runner_bytes)
            git(repo, "add", physical_runner.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "restore exact validated Common candidate")

            selection_bytes = selection.read_bytes()
            rejected_selection = json.loads(selection_bytes.decode("utf-8"))
            rejected_selection["approved"] = False
            write_json(selection, rejected_selection)
            rejected_owner = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-owner-selection.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_owner.returncode, 0)
            self.assertIn("owner-selection", rejected_owner.stderr)
            self.assertFalse((external / "archive/rejected-owner-selection.json").exists())
            selection.write_bytes(selection_bytes)

            baseline_path = durable / "baseline_inventory.json"
            baseline_bytes = baseline_path.read_bytes()
            rejected_baseline = json.loads(baseline_bytes.decode("utf-8"))
            rejected_baseline["physical_bytes"] = int(rejected_baseline["physical_bytes"]) + 1
            write_json(baseline_path, rejected_baseline)
            rejected_promoted_baseline = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", baseline_path,
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-promoted-baseline.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_promoted_baseline.returncode, 0)
            self.assertIn("baseline", rejected_promoted_baseline.stderr)
            self.assertFalse((external / "archive/rejected-promoted-baseline.json").exists())
            baseline_path.write_bytes(baseline_bytes)

            fresh_consumer = repo / "delete_time_guard_consumer.py"
            fresh_consumer.write_text(
                (
                    "from pathlib import Path\n"
                    f"Path({CANDIDATE.as_posix()!r}).read_text(encoding='utf-8')\n"
                ),
                encoding="utf-8",
            )
            rejected_fresh_reference = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", external / "archive/rejected-fresh-reference.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_fresh_reference.returncode, 0)
            self.assertIn(
                "final reference graph does not prove zero live consumers",
                rejected_fresh_reference.stderr,
            )
            self.assertFalse((external / "archive/rejected-fresh-reference.json").exists())
            fresh_consumer.unlink()

            prerequisite = external / "archive/delete-prerequisite.json"
            validated = invoke(
                EXECUTOR,
                "validate-delete-prerequisites",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--archive-receipt", durable_restore,
                "--archive-promotion-receipt", durable_promotion,
                "--archive-evidence-commit", archive_commit,
                "--pre-delete-route-receipt", pre_delete,
                "--approval", approval,
                "--out", prerequisite,
                cwd=repo,
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)
            delete_receipt = external / "archive/delete.json"
            candidate_path = repo / CANDIDATE
            candidate_bytes = candidate_path.read_bytes()
            same_content_target = external / "same-content-delete-target"
            same_content_target.mkdir()
            same_content_payload = same_content_target / "candidate.json"
            same_content_payload.write_bytes(candidate_bytes)
            candidate_path.unlink()
            create_directory_junction(candidate_path, same_content_target)
            rejected_symlink = invoke(
                EXECUTOR,
                "delete",
                "--repo", repo,
                "--operation-manifest", durable_operation,
                "--prerequisite-receipt", prerequisite,
                "--receipt-out", external / "archive/rejected-symlink-delete.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_symlink.returncode, 0)
            self.assertIn("symlink or reparse point", rejected_symlink.stderr)
            self.assertTrue(candidate_path.is_junction())
            self.assertEqual(same_content_payload.read_bytes(), candidate_bytes)
            self.assertFalse((external / "archive/rejected-symlink-delete.json").exists())
            candidate_path.rmdir()
            candidate_path.write_bytes(candidate_bytes)
            deleted = invoke(
                EXECUTOR,
                "delete",
                "--repo", repo,
                "--operation-manifest", durable_operation,
                "--prerequisite-receipt", prerequisite,
                "--receipt-out", delete_receipt,
                cwd=repo,
            )
            self.assertEqual(deleted.returncode, 0, deleted.stderr)
            self.assertFalse((repo / CANDIDATE).exists())
            self.assertEqual(same_content_payload.read_bytes(), candidate_bytes)
            self.assertTrue(Path(json.loads(archive_receipt.read_text(encoding="utf-8"))["archive_path"]).is_file())
            durable_restore_bytes = durable_restore.read_bytes()
            durable_restore.unlink()
            rejected_missing_evidence = invoke(
                EXECUTOR,
                "post-delete-census",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--prior-receipt", delete_receipt,
                "--receipt-out", external / "archive/rejected-missing-evidence.json",
                cwd=repo,
            )
            self.assertNotEqual(rejected_missing_evidence.returncode, 0)
            self.assertIn(
                "post-delete validated candidate binding mismatch",
                rejected_missing_evidence.stderr,
            )
            self.assertFalse((external / "archive/rejected-missing-evidence.json").exists())
            durable_restore.write_bytes(durable_restore_bytes)
            post = invoke(
                EXECUTOR,
                "post-delete-census",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--operation-manifest", durable_operation,
                "--prior-receipt", delete_receipt,
                "--receipt-out", external / "archive/post-delete.json",
                cwd=repo,
            )
            self.assertEqual(post.returncode, 0, post.stderr)
            post_receipt = json.loads(
                (external / "archive/post-delete.json").read_text(encoding="utf-8")
            )
            approved_paths = {
                row["path"]
                for row in (
                    post_receipt["approved_durable_additions"]
                    + post_receipt["approved_durable_changes"]
                )
            }
            self.assertTrue(
                {
                    "Iris/_docs/round3/round3_test_taxonomy.json",
                    "Iris/build/description/v2/tests/test_artifact_lifecycle_executor.py",
                    (
                        "Iris/_docs/refactor/repository_runtime_lightweighting/"
                        "current_surface_guard_successor_manifest.json"
                    ),
                }.issubset(approved_paths)
            )
            self.assertGreater(
                post_receipt["validated_candidate_delta_allowset"][
                    "bound_path_count"
                ],
                0,
            )

    def test_selection_outside_baseline_is_rejected_without_source_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s-") as temporary:
            root = Path(temporary)
            repo, external, candidate = build_fixture(root)
            durable = repo / DURABLE
            selection = external / "bad-selection.json"
            baseline = json.loads((durable / "baseline_inventory.json").read_text(encoding="utf-8"))
            write_json(
                selection,
                {
                    "schema_version": "iris_repository_runtime_lightweighting_exact_archive_selection_v1",
                    "owner": "repository_owner_user",
                    "approved": True,
                    "physical_resolved_root": repo.as_posix(),
                    "baseline_run_identity": baseline["run_identity"],
                    "baseline_promotion_receipt_sha256": sha256(durable / "baseline_promotion_receipt.json"),
                    "pre_delete_current_route_receipt_sha256": sha256(
                        durable / "pre_delete_current_route_receipt.json"
                    ),
                    "rows": [
                        {
                            "logical_artifact_id": candidate["logical_artifact_id"],
                            "path": CANDIDATE.parent.as_posix(),
                            "sha256": candidate["sha256"],
                            "size_bytes": candidate["size_bytes"],
                        }
                    ],
                },
            )
            result = invoke(
                EXECUTOR,
                "dry-run",
                "--repo", repo,
                "--baseline", durable / "baseline_inventory.json",
                "--promotion-receipt", durable / "baseline_promotion_receipt.json",
                "--pre-delete-route-receipt", durable / "pre_delete_current_route_receipt.json",
                "--selection", selection,
                "--manifest-out", external / "bad/operation.json",
                "--receipt-out", external / "bad/receipt.json",
                cwd=repo,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside promoted baseline", result.stderr)
            self.assertTrue((repo / CANDIDATE).is_file())


if __name__ == "__main__":
    unittest.main()
