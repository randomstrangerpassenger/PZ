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
    def test_append_instrumental_cases(self) -> None:
        cases = (
            ("parenthesized_open", "통조림 (열림)", "통조림 (열림)으로"),
            ("parenthesized_sawn_barrel", "산탄총 (총열 자름)", "산탄총 (총열 자름)으로"),
            ("parenthesized_black", "손목시계 (검은색)", "손목시계 (검은색)으로"),
            ("parenthesized_brown", "손목시계 (갈색)", "손목시계 (갈색)으로"),
            ("parenthesized_gold", "손목시계 (금)", "손목시계 (금)으로"),
            ("parenthesized_red", "손목시계 (빨간색)", "손목시계 (빨간색)으로"),
            ("parenthesized_rieul", "손목시계 (메탈릭 드레스 스타일)", "손목시계 (메탈릭 드레스 스타일)로"),
            ("unparenthesized_no_final_consonant", "시계", "시계로"),
            ("unparenthesized_final_consonant", "가방", "가방으로"),
            ("unparenthesized_rieul", "망치질", "망치질로"),
            ("trailing_whitespace_punctuation_and_closer", "통조림 (열림).!?   ", "통조림 (열림)으로"),
        )
        for case_id, source, expected in cases:
            with self.subTest(case_id=case_id):
                self.assertEqual(append_instrumental(source), expected)

    def test_phonological_tail_skips_all_trailing_unicode_punctuation(self) -> None:
        self.assertEqual(
            instrumental_phonological_tail("통조림 (열림)]」!?—   "),
            "림",
        )


if __name__ == "__main__":
    unittest.main()
