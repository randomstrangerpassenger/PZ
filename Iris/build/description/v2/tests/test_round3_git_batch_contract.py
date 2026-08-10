from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[5]
RUNNER_PATH = REPO / "Iris/_docs/round3/round3_run_contract_tests.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("round3_git_batch_runner", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Round3GitBatchContractTest(unittest.TestCase):
    def git(self, root: Path, *args: str) -> None:
        completed = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, check=False
        )
        self.assertEqual(0, completed.returncode, completed.stderr.decode(errors="replace"))

    def make_repository(self, root: Path) -> list[Path]:
        self.git(root, "init", "--quiet")
        (root / ".gitignore").write_text("*.ignored\n", encoding="utf-8")
        names = ["tracked.txt", "space name.txt", "한글.txt"]
        for name in names:
            (root / name).write_text(name, encoding="utf-8")
        (root / "untracked.txt").write_text("untracked", encoding="utf-8")
        (root / "sample.ignored").write_text("ignored", encoding="utf-8")
        self.git(root, "add", "--", ".gitignore", *names)
        return [
            root / "tracked.txt",
            root / "space name.txt",
            root / "한글.txt",
            root / "untracked.txt",
            root / "sample.ignored",
            root / "missing.txt",
        ]

    def test_batch_states_preserve_path_order_and_use_two_git_calls(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = self.make_repository(root)
            calls: list[list[str]] = []
            real_run = subprocess.run

            def spy(*args, **kwargs):
                calls.append(list(args[0]))
                return real_run(*args, **kwargs)

            with mock.patch.object(runner, "REPO", root), mock.patch.object(
                runner.subprocess, "run", side_effect=spy
            ):
                states = runner.batch_git_path_states(paths)

            self.assertEqual([path.name for path in paths], list(states))
            for name in ("tracked.txt", "space name.txt", "한글.txt"):
                self.assertEqual({"tracked": True, "ignored": False}, states[name])
            self.assertEqual(
                {"tracked": False, "ignored": False}, states["untracked.txt"]
            )
            self.assertEqual(
                {"tracked": False, "ignored": True}, states["sample.ignored"]
            )
            self.assertEqual(
                {"tracked": False, "ignored": False}, states["missing.txt"]
            )
            self.assertEqual(2, len(calls))
            self.assertEqual(["git", "ls-files", "-z"], calls[0])
            self.assertEqual(["git", "check-ignore", "--stdin", "-z"], calls[1])

    def test_git_failures_are_not_treated_as_empty_sets(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "fixture.txt"
            path.write_text("x", encoding="utf-8")
            failed = subprocess.CompletedProcess(
                ["git", "ls-files"], 128, stdout=b"", stderr=b"fatal fixture"
            )
            with mock.patch.object(runner, "REPO", root), mock.patch.object(
                runner.subprocess, "run", return_value=failed
            ):
                with self.assertRaisesRegex(RuntimeError, "git ls-files failed"):
                    runner.batch_git_path_states([path])


if __name__ == "__main__":
    unittest.main()
