from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.compose_layer3_identity import (
    append_instrumental,
    instrumental_phonological_tail,
)


class InstrumentalParticleAdjustmentTest(unittest.TestCase):
    def test_parenthesized_open_uses_euro(self) -> None:
        self.assertEqual(append_instrumental("통조림 (열림)"), "통조림 (열림)으로")

    def test_parenthesized_sawn_barrel_uses_euro(self) -> None:
        self.assertEqual(
            append_instrumental("산탄총 (총열 자름)"),
            "산탄총 (총열 자름)으로",
        )

    def test_parenthesized_black_uses_euro(self) -> None:
        self.assertEqual(
            append_instrumental("손목시계 (검은색)"),
            "손목시계 (검은색)으로",
        )

    def test_parenthesized_brown_uses_euro(self) -> None:
        self.assertEqual(
            append_instrumental("손목시계 (갈색)"),
            "손목시계 (갈색)으로",
        )

    def test_parenthesized_gold_uses_euro(self) -> None:
        self.assertEqual(
            append_instrumental("손목시계 (금)"),
            "손목시계 (금)으로",
        )

    def test_parenthesized_red_uses_euro(self) -> None:
        self.assertEqual(
            append_instrumental("손목시계 (빨간색)"),
            "손목시계 (빨간색)으로",
        )

    def test_parenthesized_rieul_uses_ro(self) -> None:
        self.assertEqual(
            append_instrumental("손목시계 (메탈릭 드레스 스타일)"),
            "손목시계 (메탈릭 드레스 스타일)로",
        )

    def test_unparenthesized_no_final_consonant_uses_ro(self) -> None:
        self.assertEqual(append_instrumental("시계"), "시계로")

    def test_unparenthesized_final_consonant_uses_euro(self) -> None:
        self.assertEqual(append_instrumental("가방"), "가방으로")

    def test_unparenthesized_rieul_uses_ro(self) -> None:
        self.assertEqual(append_instrumental("망치질"), "망치질로")

    def test_tail_ignores_whitespace_sentence_punctuation_and_closer(self) -> None:
        self.assertEqual(
            append_instrumental("통조림 (열림).!?   "),
            "통조림 (열림)으로",
        )

    def test_phonological_tail_skips_all_trailing_unicode_punctuation(self) -> None:
        self.assertEqual(
            instrumental_phonological_tail("통조림 (열림)]」!?—   "),
            "림",
        )


if __name__ == "__main__":
    unittest.main()
