from __future__ import annotations

import unittest
from types import SimpleNamespace
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

    def test_drops_language_prefix_only_for_m2m100_models(self) -> None:
        engine = TranslationEngine()
        engine._translator = FakeTranslator([['__es__', 'Hola']])
        engine._tokenizer = FakeTokenizer()
        engine._runtime_profile = SimpleNamespace(batch_size=8)
        engine._model_config = MODEL_CONFIG
        engine._model_key = MODEL_CONFIG.repo_id

        translated = engine.translate_texts(
            ['Hello'],
            source_language='en',
            target_language='es',
            progress_callback=lambda _: None,
            progress_label='test',
        )

        self.assertEqual(translated, ['Hola'])

    def test_keeps_first_token_for_opus_models(self) -> None:
        engine = TranslationEngine()
        engine._translator = FakeTranslator([['Zer', 'beste', 'materialak']])
        engine._tokenizer = FakeTokenizer()
        engine._runtime_profile = SimpleNamespace(batch_size=8)
        engine._model_config = EUSKERA_MODEL_CONFIGS[('es', 'eu')]
        engine._model_key = EUSKERA_MODEL_CONFIGS[('es', 'eu')].repo_id

        translated = engine.translate_texts(
            ['Qué otros materiales'],
            source_language='es',
            target_language='eu',
            progress_callback=lambda _: None,
            progress_label='test',
        )

        self.assertEqual(translated, ['Zer beste materialak'])


class FakeTokenizer:
    lang_code_to_token = {'es': '__es__', 'en': '__en__', 'eu': '__eu__'}

    def __init__(self) -> None:
        self.src_lang = None

    @staticmethod
    def encode(text: str, add_special_tokens: bool = True) -> list[str]:
        return text.split()

    @staticmethod
    def convert_ids_to_tokens(tokens: list[str]) -> list[str]:
        return list(tokens)

    @staticmethod
    def convert_tokens_to_ids(tokens: list[str]) -> list[str]:
        return list(tokens)

    @staticmethod
    def decode(tokens: list[str], skip_special_tokens: bool = True) -> str:
        return ' '.join(token for token in tokens if not skip_special_tokens or not token.startswith('__'))


class FakeTranslator:
    def __init__(self, hypotheses: list[list[str]]) -> None:
        self._hypotheses = hypotheses

    def translate_batch(self, tokenized_batch, **kwargs):
        return [SimpleNamespace(hypotheses=[hypothesis]) for hypothesis in self._hypotheses]


if __name__ == '__main__':
    unittest.main()
