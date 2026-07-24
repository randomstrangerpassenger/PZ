from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parent
    / "reserve_registry_runtime_compatibility_attempt.py"
)
SPEC = importlib.util.spec_from_file_location("rtc_reservation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
rtc = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rtc
SPEC.loader.exec_module(rtc)


def write_event(
    path: Path,
    *,
    sequence: int,
    attempt_id: str,
    event_type: str,
    previous_hash: str,
) -> str:
    record = {
        "schema_version": "rtc-attempt-event-v1",
        "event_sequence": sequence,
        "round_id": rtc.ROUND_ID,
        "attempt_id": attempt_id,
        "event_type": event_type,
        "record_path": f"attempts/{attempt_id}/{event_type}_record.json",
        "record_sha256": "a" * 64,
        "previous_event_sha256": previous_hash,
    }
    raw = rtc.canonical_json_bytes(record)
    with path.open("ab") as handle:
        handle.write(raw)
    return rtc.sha256_bytes(raw)


class LedgerReplayTest(unittest.TestCase):
    def test_empty_ledger_has_no_open_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            path.touch()
            state = rtc.replay_event_ledger(path)
        self.assertEqual(state.event_count, 0)
        self.assertEqual(state.open_attempt_ids, ())
        self.assertEqual(state.prefix_sha256, rtc.sha256_bytes(b""))

    def test_reservation_creates_one_open_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            previous = "0" * 64
            write_event(
                path,
                sequence=1,
                attempt_id="attempt-0001",
                event_type="reservation",
                previous_hash=previous,
            )
            state = rtc.replay_event_ledger(path)
        self.assertEqual(state.open_attempt_ids, ("attempt-0001",))

    def test_terminal_closes_attempt_and_allows_next_id(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            previous = write_event(
                path,
                sequence=1,
                attempt_id="attempt-0001",
                event_type="reservation",
                previous_hash="0" * 64,
            )
            write_event(
                path,
                sequence=2,
                attempt_id="attempt-0001",
                event_type="terminal",
                previous_hash=previous,
            )
            state = rtc.replay_event_ledger(path)
        self.assertEqual(state.open_attempt_ids, ())
        self.assertEqual(rtc.next_attempt_id(state.used_attempt_ids), "attempt-0002")

    def test_duplicate_reservation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            previous = write_event(
                path,
                sequence=1,
                attempt_id="attempt-0001",
                event_type="reservation",
                previous_hash="0" * 64,
            )
            write_event(
                path,
                sequence=2,
                attempt_id="attempt-0001",
                event_type="reservation",
                previous_hash=previous,
            )
            with self.assertRaisesRegex(rtc.ReservationError, "Duplicate reservation"):
                rtc.replay_event_ledger(path)

    def test_terminal_without_reservation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            write_event(
                path,
                sequence=1,
                attempt_id="attempt-0001",
                event_type="terminal",
                previous_hash="0" * 64,
            )
            with self.assertRaisesRegex(
                rtc.ReservationError, "without open reservation"
            ):
                rtc.replay_event_ledger(path)

    def test_hash_chain_break_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            write_event(
                path,
                sequence=1,
                attempt_id="attempt-0001",
                event_type="reservation",
                previous_hash="f" * 64,
            )
            with self.assertRaisesRegex(rtc.ReservationError, "wrong previous hash"):
                rtc.replay_event_ledger(path)

    def test_truncated_event_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "attempt_events.jsonl"
            path.write_text(json.dumps({"event_sequence": 1}), encoding="utf-8")
            with self.assertRaisesRegex(rtc.ReservationError, "lacks LF"):
                rtc.replay_event_ledger(path)

    def test_attempt_id_is_monotonic(self) -> None:
        self.assertEqual(
            rtc.next_attempt_id(["attempt-0002", "attempt-0009"]),
            "attempt-0010",
        )


class BootstrapScopeTest(unittest.TestCase):
    def test_executor_has_round_local_fixed_paths(self) -> None:
        self.assertEqual(rtc.ROUND_ID, "dvf_3_3_registry_runtime_compatibility")
        self.assertIn(
            "registry_runtime_compatibility", rtc.EVENT_LEDGER_REL.as_posix()
        )
        self.assertIn(
            "registry_runtime_compatibility",
            rtc.DURABLE_ATTEMPT_ROOT_REL.as_posix(),
        )

    def test_executor_has_no_compatibility_surface_literals(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        forbidden = (
            "dvf_3_3_rendered.json",
            "package_iris.ps1",
            "export_dvf_3_3_lua_bridge",
            "IrisLayer3DataChunks",
        )
        self.assertEqual([value for value in forbidden if value in source], [])

    def test_exclusive_write_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "immutable.json"
            rtc.exclusive_write(path, b"{}\n")
            with self.assertRaisesRegex(rtc.ReservationError, "overwrite"):
                rtc.exclusive_write(path, b"{}\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
