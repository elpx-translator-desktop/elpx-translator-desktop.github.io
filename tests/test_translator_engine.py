from __future__ import annotations

import unittest
from unittest.mock import patch

from elpx_translator_desktop.config import EUSKERA_MODEL_CONFIGS, MODEL_CONFIG
from elpx_translator_desktop.translator_engine import TranslationEngine


class TranslatorEngineTests(unittest.TestCase):
    @patch('elpx_translator_desktop.translator_engine.os.nice')
    def test_does_not_report_priority_change_for_normal_priority(self, mock_nice) -> None:
        self.assertFalse(TranslationEngine._lower_process_priority(0))
        mock_nice.assert_not_called()

    def test_routes_euskera_pairs_to_opus_models(self) -> None:
        self.assertEqual(
            TranslationEngine._resolve_model_config('es', 'eu'),
            EUSKERA_MODEL_CONFIGS[('es', 'eu')],
        )
        self.assertEqual(
            TranslationEngine._resolve_model_config('eu', 'en'),
            EUSKERA_MODEL_CONFIGS[('eu', 'en')],
        )

    def test_keeps_default_model_for_non_euskera_pairs(self) -> None:
        self.assertEqual(TranslationEngine._resolve_model_config('es', 'en'), MODEL_CONFIG)
        self.assertEqual(TranslationEngine._resolve_model_config('ca', 'gl'), MODEL_CONFIG)


if __name__ == '__main__':
    unittest.main()
