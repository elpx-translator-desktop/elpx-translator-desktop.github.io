from __future__ import annotations

import json
import unittest

from elpx_translator_desktop.elpx_service import ElpxTranslationService, TranslationOptions
from elpx_translator_desktop.text_utils import looks_like_encoded_payload, looks_like_json_payload


class DummyEngine:
    def translate_texts(self, texts, **kwargs):
        return [f'[[{text}]]' for text in texts]


class CountingEngine:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def translate_texts(self, texts, **kwargs):
        self.calls.append(list(texts))
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

    def test_detects_json_payloads(self) -> None:
        payload = '{"title":"Mapa","points":[{"title":"Editar"}]}'
        self.assertTrue(looks_like_json_payload(payload))

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

    def test_translates_json_payloads_inside_html_without_corrupting_them(self) -> None:
        html = (
            '<div class="mapa-DataGame js-hidden">'
            '{"typeGame":"Mapa","instructions":"","points":[{"title":"Editar","footer":"Pie"}]}'
            '</div>'
        )

        translated = self.service._translate_html_fragment(html, self.tracker, self.options, 'test')
        payload = translated.split('>', 1)[1].rsplit('<', 1)[0]
        parsed = json.loads(payload)

        self.assertEqual(parsed['typeGame'], 'Mapa')
        self.assertEqual(parsed['points'][0]['title'], '[[Editar]]')
        self.assertEqual(parsed['points'][0]['footer'], '[[Pie]]')

    def test_translates_datagame_payloads_with_embedded_html_inside_json_strings(self) -> None:
        html = (
            '<div class="trivial-DataGame js-hidden">'
            '{"instructionsExe":"<p>Texto inicial</p>","instructions":"Contesta la pregunta","items":[{"q":"Pregunta 1"}]}'
            '</div>'
        )

        translated = self.service._translate_html_fragment(html, self.tracker, self.options, 'test')
        payload = translated.split('>', 1)[1].rsplit('<', 1)[0]
        parsed = json.loads(payload)

        self.assertEqual(parsed['instructionsExe'], '<p>[[Texto inicial]]</p>')
        self.assertEqual(parsed['instructions'], '[[Contesta la pregunta]]')
        self.assertEqual(parsed['items'][0]['q'], '[[Pregunta 1]]')

        extracted_texts = self.service._extract_html_texts(html)
        self.assertEqual(extracted_texts, ['Texto inicial', 'Contesta la pregunta', 'Pregunta 1'])

    def test_translates_application_json_scripts_in_html(self) -> None:
        html = (
            '<script type="application/json">'
            '{"slides":[{"type":"text","text":"<p>Pregunta</p>"}],"i18n":{"start":"Inicio","score":"Puntuación"}}'
            '</script>'
        )

        translated = self.service._translate_html_fragment(html, self.tracker, self.options, 'test')
        payload = translated.split('>', 1)[1].rsplit('<', 1)[0]
        parsed = json.loads(payload)

        self.assertEqual(parsed['slides'][0]['text'], '<p>[[Pregunta]]</p>')
        self.assertEqual(parsed['i18n']['start'], '[[Inicio]]')
        self.assertEqual(parsed['i18n']['score'], '[[Puntuación]]')

    def test_reuses_translated_htmlview_inside_json_properties(self) -> None:
        engine = CountingEngine()
        service = ElpxTranslationService(engine=engine)
        html = '<div class="exe-text"><p>Texto repetido</p></div>'
        html_reuse_map = {html: 'TRANSLATED_HTML'}

        translated = service._translate_json_value(
            {'textTextarea': html, 'label': 'Otro texto'},
            self.tracker,
            self.options,
            'test',
            html_reuse_map=html_reuse_map,
        )

        self.assertEqual(translated['textTextarea'], 'TRANSLATED_HTML')
        self.assertEqual(translated['label'], '[[Otro texto]]')
        self.assertEqual(engine.calls, [['Otro texto']])

    def test_count_json_units_skips_reused_htmlview(self) -> None:
        html = '<div class="exe-text"><p>Texto repetido</p></div>'

        count = self.service._count_json_units(
            {'textTextarea': html, 'label': 'Otro texto'},
            html_reuse_map={html: ''},
        )

        self.assertEqual(count, 1)

    def test_translates_title_node_structural_properties(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<root>'
            '<odeNavStructureProperty><key>titlePage</key><value>Qué es eXeLearning</value></odeNavStructureProperty>'
            '<odeNavStructureProperty><key>titleNode</key><value>Qué es eXeLearning</value></odeNavStructureProperty>'
            '</root>'
        )

        translated = self.service._translate_content_xml(xml, self.options, lambda event: None)

        self.assertIn('<value>[[Qué es eXeLearning]]</value>', translated)
        self.assertEqual(translated.count('[[Qué es eXeLearning]]'), 2)

    def test_primes_translation_memory_globally_to_reduce_engine_calls(self) -> None:
        engine = CountingEngine()
        service = ElpxTranslationService(engine=engine)
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<root>'
            '<odeNavStructureProperty><key>titlePage</key><value>Portada</value></odeNavStructureProperty>'
            '<odeComponent>'
            '<htmlView><![CDATA[<p>Texto uno</p>]]></htmlView>'
            '<jsonProperties><![CDATA[{"label":"Texto dos"}]]></jsonProperties>'
            '</odeComponent>'
            '<odeComponent>'
            '<htmlView><![CDATA[<p>Texto tres</p>]]></htmlView>'
            '<jsonProperties><![CDATA[{"label":"Texto cuatro"}]]></jsonProperties>'
            '</odeComponent>'
            '</root>'
        )

        translated = service._translate_content_xml(xml, self.options, lambda event: None)

        self.assertIn('[[Portada]]', translated)
        self.assertIn('[[Texto uno]]', translated)
        self.assertIn('[[Texto cuatro]]', translated)
        self.assertEqual(len(engine.calls), 1)
        self.assertEqual(engine.calls[0], ['Portada', 'Texto uno', 'Texto dos', 'Texto tres', 'Texto cuatro'])

    def test_updates_project_language_metadata_to_target_language(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<root>'
            '<odeProperty><key>pp_title</key><value>Guia</value></odeProperty>'
            '<odeProperty><key>pp_lang</key><value>ca</value></odeProperty>'
            '</root>'
        )
        options = TranslationOptions(source_language='ca', target_language='es', ui_language='es')

        translated = self.service._translate_content_xml(xml, options, lambda event: None)

        self.assertIn('<key>pp_lang</key><value>ca</value>', xml)
        self.assertIn('<key>pp_lang</key><value>es</value>', translated)


if __name__ == '__main__':
    unittest.main()
