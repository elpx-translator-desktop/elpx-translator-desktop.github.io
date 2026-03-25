from __future__ import annotations

import unittest

from elpx_translator_desktop.config import (
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


if __name__ == '__main__':
    unittest.main()
