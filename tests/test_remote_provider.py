from __future__ import annotations

import unittest
from unittest.mock import patch

from elpx_translator_desktop.remote_provider import (
    ProviderModel,
    create_translation_completion,
    fallback_models,
    get_api_key_url,
    list_available_models,
)


class RemoteProviderTests(unittest.TestCase):
    def test_api_key_urls_include_new_providers(self) -> None:
        self.assertEqual(get_api_key_url('anthropic'), 'https://console.anthropic.com/settings/keys')
        self.assertEqual(get_api_key_url('deepseek'), 'https://platform.deepseek.com/api_keys')

    def test_fallback_models_include_new_providers(self) -> None:
        self.assertEqual(
            fallback_models('anthropic'),
            [
                ProviderModel(model_id='claude-sonnet-4-5', label='claude-sonnet-4-5'),
                ProviderModel(model_id='claude-opus-4-1', label='claude-opus-4-1'),
                ProviderModel(model_id='claude-3-5-haiku-latest', label='claude-3-5-haiku-latest'),
            ],
        )
        self.assertEqual(
            fallback_models('deepseek'),
            [
                ProviderModel(model_id='deepseek-chat', label='deepseek-chat'),
                ProviderModel(model_id='deepseek-reasoner', label='deepseek-reasoner'),
            ],
        )

    @patch('elpx_translator_desktop.remote_provider._http_json')
    def test_list_available_models_for_anthropic(self, http_json_mock) -> None:
        http_json_mock.return_value = {
            'data': [
                {'id': 'claude-sonnet-4-5'},
                {'id': 'claude-opus-4-1'},
                {'id': 'not-a-chat-model'},
            ],
        }

        models = list_available_models('anthropic', 'test-key')

        self.assertEqual([item.model_id for item in models], ['claude-sonnet-4-5', 'claude-opus-4-1'])

    @patch('elpx_translator_desktop.remote_provider._http_json')
    def test_list_available_models_for_deepseek(self, http_json_mock) -> None:
        http_json_mock.return_value = {
            'data': [
                {'id': 'deepseek-reasoner'},
                {'id': 'deepseek-chat'},
                {'id': 'text-embedding-3-small'},
            ],
        }

        models = list_available_models('deepseek', 'test-key')

        self.assertEqual([item.model_id for item in models], ['deepseek-chat', 'deepseek-reasoner'])

    @patch('elpx_translator_desktop.remote_provider._http_json')
    def test_create_translation_completion_for_anthropic(self, http_json_mock) -> None:
        http_json_mock.return_value = {
            'content': [
                {
                    'type': 'text',
                    'text': '{"translations":["hola"]}',
                },
            ],
        }

        result = create_translation_completion(
            'anthropic',
            api_key='test-key',
            model_id='claude-sonnet-4-5',
            source_language='en',
            target_language='es',
            texts=['hello'],
        )

        self.assertEqual(result, ['hola'])

    @patch('elpx_translator_desktop.remote_provider._http_json')
    def test_create_translation_completion_for_deepseek(self, http_json_mock) -> None:
        http_json_mock.return_value = {
            'choices': [
                {
                    'message': {
                        'content': '{"translations":["hola"]}',
                    },
                },
            ],
        }

        result = create_translation_completion(
            'deepseek',
            api_key='test-key',
            model_id='deepseek-chat',
            source_language='en',
            target_language='es',
            texts=['hello'],
        )

        self.assertEqual(result, ['hola'])


if __name__ == '__main__':
    unittest.main()
