from __future__ import annotations

import unittest

from elpx_translator_desktop.config import (
    LANGUAGE_OPTIONS,
    is_supported_language_pair,
    supported_source_languages,
    supported_target_languages,
)


class ConfigLanguagePairTests(unittest.TestCase):
    def test_rejects_unsupported_pairs_with_euskera(self) -> None:
        self.assertFalse(is_supported_language_pair('ca', 'eu'))
        self.assertFalse(is_supported_language_pair('eu', 'gl'))
        self.assertFalse(is_supported_language_pair('eu', 'fr'))

    def test_accepts_supported_pairs_with_euskera(self) -> None:
        self.assertTrue(is_supported_language_pair('es', 'eu'))
        self.assertTrue(is_supported_language_pair('eu', 'es'))
        self.assertTrue(is_supported_language_pair('en', 'eu'))
        self.assertTrue(is_supported_language_pair('eu', 'en'))

    def test_supported_target_languages_filters_euskera_pairs(self) -> None:
        self.assertIn('eu', supported_target_languages('es'))
        self.assertNotIn('eu', supported_target_languages('ca'))

    def test_supported_source_languages_filters_euskera_pairs(self) -> None:
        self.assertEqual(supported_source_languages('eu'), ['es', 'en'])
        self.assertNotIn('ca', supported_source_languages('eu'))

    def test_exposes_new_languages_in_language_options(self) -> None:
        language_codes = {code for code, _ in LANGUAGE_OPTIONS}
        self.assertTrue({'ar', 'bn', 'nl', 'pl', 'ro', 'ru', 'tr', 'uk', 'ur', 'zh'}.issubset(language_codes))

    def test_accepts_supported_pairs_for_new_non_euskera_languages(self) -> None:
        self.assertTrue(is_supported_language_pair('es', 'ar'))
        self.assertTrue(is_supported_language_pair('ar', 'es'))
        self.assertTrue(is_supported_language_pair('bn', 'tr'))
        self.assertTrue(is_supported_language_pair('nl', 'pl'))
        self.assertTrue(is_supported_language_pair('zh', 'ro'))
        self.assertTrue(is_supported_language_pair('uk', 'ru'))

    def test_supported_target_languages_include_new_non_euskera_languages(self) -> None:
        target_languages = supported_target_languages('es')
        for code in ('ar', 'bn', 'nl', 'pl', 'ro', 'ru', 'tr', 'uk', 'ur', 'zh'):
            self.assertIn(code, target_languages)


if __name__ == '__main__':
    unittest.main()
