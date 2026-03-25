from __future__ import annotations

import unittest

from elpx_translator_desktop.elpx_service import ElpxTranslationService, TranslationOptions
from elpx_translator_desktop.text_utils import looks_like_encoded_payload


class DummyEngine:
    def translate_texts(self, texts, **kwargs):
        return [f'[[{text}]]' for text in texts]


class DummyTracker:
    def __init__(self) -> None:
        self.translation_memory: dict[str, str] = {}

    def callback(self, event) -> None:
        return None

    def create_batch_meta(self, count: int):
        return None

    def complete_batch(self, count: int) -> None:
        return None


class ElpxServiceHtmlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ElpxTranslationService(engine=DummyEngine())
        self.tracker = DummyTracker()
        self.options = TranslationOptions(source_language='es', target_language='ca', ui_language='es')

    def test_detects_percent_encoded_payloads(self) -> None:
        payload = '%E9%B0%E6%EB%E2%F7%D5%F3%FF%F7%B0%A8%B0%C1%FD%E2%F3%B0%BE%B0%FB%FC%E1%E6%E0%E7'
        self.assertTrue(looks_like_encoded_payload(payload))

    def test_preserves_inline_whitespace_around_formatted_text(self) -> None:
        html = '<p>Utilizaremos este iDevice para <strong>crear actividades tipo sopa de letras</strong> en las que podrá utilizar texto.</p>'

        translated = self.service._translate_html_fragment(html, self.tracker, self.options, 'test')

        self.assertIn('[[Utilizaremos este iDevice para]] <strong>', translated)
        self.assertIn('</strong> [[en las que podrá utilizar texto.]]', translated)

    def test_skips_translating_encoded_game_payloads(self) -> None:
        payload = '%E9%B0%E6%EB%E2%F7%D5%F3%FF%F7%B0%A8%B0%C1%FD%E2%F3%B0%BE%B0%FB%FC%E1%E6%E0%E7'
        html = (
            '<div class="sopa-IDevice">'
            '<div class="sopa-instructions"><p>Encuentra palabras</p></div>'
            f'<div class="sopa-DataGame js-hidden">{payload}</div>'
            '</div>'
        )

        translated = self.service._translate_html_fragment(html, self.tracker, self.options, 'test')

        self.assertIn('[[Encuentra palabras]]', translated)
        self.assertIn(payload, translated)
        self.assertNotIn(f'[[{payload}]]', translated)


if __name__ == '__main__':
    unittest.main()
