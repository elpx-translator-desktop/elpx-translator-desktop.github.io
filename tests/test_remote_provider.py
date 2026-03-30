from __future__ import annotations

import json
import socket
import unittest
from unittest.mock import patch
from urllib import error

from elpx_translator_desktop.remote_provider import (
    ProviderModel,
    RemoteProviderError,
    create_translation_completion,
    fallback_models,
    get_api_key_url,
    is_structured_response_error,
    list_available_models,
)


class RemoteProviderTests(unittest.TestCase):
    def test_api_key_urls_include_new_providers(self) -> None:
        self.assertEqual(get_api_key_url('anthropic'), 'https://console.anthropic.com/settings/keys')
        self.assertEqual(get_api_key_url('deepseek'), 'https://platform.deepseek.com/api_keys')

    def test_fallback_models_include_new_providers(self) -> None:
        self.assertEqual(fallback_models('openai'), [])
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
    def test_create_translation_completion_for_openai_requests_json_mode(self, http_json_mock) -> None:
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
            'openai',
            api_key='test-key',
            model_id='gpt-4.1-mini',
            source_language='en',
            target_language='es',
            texts=['hello'],
        )

        self.assertEqual(result, ['hola'])
        _, kwargs = http_json_mock.call_args
        self.assertEqual(kwargs['body']['response_format'], {'type': 'json_object'})

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

    @patch('elpx_translator_desktop.remote_provider._http_json')
    def test_create_translation_completion_accepts_json_wrapped_in_text(self, http_json_mock) -> None:
        http_json_mock.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'Aquí tienes el resultado:\n```json\n{"translations":["hola","adiós"]}\n```',
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
            texts=['hello', 'goodbye'],
        )

        self.assertEqual(result, ['hola', 'adiós'])

    @patch('elpx_translator_desktop.remote_provider._http_json')
    def test_create_translation_completion_reports_raw_details_for_invalid_list(self, http_json_mock) -> None:
        http_json_mock.return_value = {
            'choices': [
                {
                    'message': {
                        'content': '{"translations":["hola"]}',
                    },
                },
            ],
        }

        with self.assertRaises(RemoteProviderError) as error_info:
            create_translation_completion(
                'deepseek',
                api_key='test-key',
                model_id='deepseek-chat',
                source_language='en',
                target_language='es',
                texts=['hello', 'goodbye'],
            )

        self.assertTrue(is_structured_response_error(error_info.exception))
        self.assertEqual(error_info.exception.raw_details, '{"translations":["hola"]}')

    @patch('elpx_translator_desktop.remote_provider.request.urlopen')
    def test_http_json_uses_explicit_ssl_context(self, urlopen_mock) -> None:
        from elpx_translator_desktop import remote_provider

        class FakeHeaders:
            @staticmethod
            def get_content_charset() -> str:
                return 'utf-8'

        class FakeResponse:
            headers = FakeHeaders()

            def read(self) -> bytes:
                return json.dumps({'data': []}).encode('utf-8')

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                return None

        urlopen_mock.return_value = FakeResponse()

        remote_provider._http_json('https://api.openai.com/v1/models')

        _, kwargs = urlopen_mock.call_args
        self.assertIs(kwargs['context'], remote_provider.SSL_CONTEXT)

    @patch('elpx_translator_desktop.remote_provider.request.urlopen')
    def test_http_json_wraps_timeouts_as_retryable_remote_error(self, urlopen_mock) -> None:
        urlopen_mock.side_effect = error.URLError(socket.timeout('timed out'))

        with self.assertRaises(RemoteProviderError) as error_info:
            from elpx_translator_desktop import remote_provider

            remote_provider._http_json('https://api.openai.com/v1/chat/completions', method='POST', body={'model': 'gpt-5-mini'})

        self.assertEqual(str(error_info.exception), 'Tiempo de espera agotado al llamar al proveedor remoto.')
        self.assertEqual(error_info.exception.retry_after_seconds, 2.0)


if __name__ == '__main__':
    unittest.main()
