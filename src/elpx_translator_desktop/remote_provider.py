from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from urllib import error, request


OPENAI_API_KEY_URL = 'https://platform.openai.com/api-keys'
GEMINI_API_KEY_URL = 'https://aistudio.google.com/api-keys'
ANTHROPIC_API_KEY_URL = 'https://console.anthropic.com/settings/keys'
DEEPSEEK_API_KEY_URL = 'https://platform.deepseek.com/api_keys'

OPENAI_API_BASE_URL = 'https://api.openai.com/v1'
GEMINI_OPENAI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai'
GEMINI_API_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'
ANTHROPIC_API_BASE_URL = 'https://api.anthropic.com/v1'
DEEPSEEK_API_BASE_URL = 'https://api.deepseek.com/v1'

DEFAULT_REMOTE_MODEL_IDS = {
    'openai': [
        'gpt-5-mini',
        'gpt-5-nano',
        'gpt-4.1-mini',
    ],
    'gemini': [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
    ],
    'anthropic': [
        'claude-sonnet-4-5',
        'claude-opus-4-1',
        'claude-3-5-haiku-latest',
    ],
    'deepseek': [
        'deepseek-chat',
        'deepseek-reasoner',
    ],
}


class RemoteProviderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after_seconds: float | None = None,
        raw_details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after_seconds = retry_after_seconds
        self.raw_details = raw_details


@dataclass(frozen=True)
class ProviderModel:
    model_id: str
    label: str


def get_api_key_url(provider: str) -> str | None:
    if provider == 'openai':
        return OPENAI_API_KEY_URL
    if provider == 'gemini':
        return GEMINI_API_KEY_URL
    if provider == 'anthropic':
        return ANTHROPIC_API_KEY_URL
    if provider == 'deepseek':
        return DEEPSEEK_API_KEY_URL
    return None


def fallback_models(provider: str) -> list[ProviderModel]:
    return [ProviderModel(model_id=model_id, label=model_id) for model_id in DEFAULT_REMOTE_MODEL_IDS.get(provider, [])]


def list_available_models(provider: str, api_key: str) -> list[ProviderModel]:
    if provider == 'openai':
        return _list_openai_models(api_key)
    if provider == 'gemini':
        return _list_gemini_models(api_key)
    if provider == 'anthropic':
        return _list_anthropic_models(api_key)
    if provider == 'deepseek':
        return _list_deepseek_models(api_key)
    return []


def create_translation_completion(
    provider: str,
    *,
    api_key: str,
    model_id: str,
    source_language: str,
    target_language: str,
    texts: list[str],
) -> list[str]:
    if provider == 'local':
        raise RemoteProviderError('El proveedor local no usa API remota.')

    system_prompt = (
        'You are a translation engine for .elpx educational projects. '
        'Translate each item from the source language to the target language. '
        'Return only valid JSON with this shape: {"translations":["..."]}. '
        'Preserve order and array length exactly. '
        'Do not omit items. '
        'Keep placeholders, variable names, URLs, HTML entities, XML fragments, HTML tags, '
        'whitespace-only items, and tokens like {{...}}, [[...]], __...__, %s, {0}, <code>, &nbsp; unchanged when they appear. '
        'Do not explain anything.'
    )
    user_payload = {
        'source_language': source_language,
        'target_language': target_language,
        'texts': texts,
    }
    content = _chat_completion(
        provider,
        api_key=api_key,
        model_id=model_id,
        system_prompt=system_prompt,
        user_prompt=json.dumps(user_payload, ensure_ascii=False),
    )
    data = _extract_json(content)
    translations = data.get('translations')
    if not isinstance(translations, list) or len(translations) != len(texts):
        raise RemoteProviderError('La respuesta del proveedor remoto no devolvió una lista de traducciones válida.')
    normalized = [item if isinstance(item, str) else str(item) for item in translations]
    if len(normalized) != len(texts):
        raise RemoteProviderError('La respuesta remota no coincide con el tamaño del lote enviado.')
    return normalized


def _list_openai_models(api_key: str) -> list[ProviderModel]:
    payload = _http_json(
        f'{OPENAI_API_BASE_URL}/models',
        headers={
            'Authorization': f'Bearer {api_key}',
        },
    )
    model_ids = sorted(
        {
            item.get('id', '')
            for item in payload.get('data', [])
            if isinstance(item, dict) and _is_supported_openai_model(item.get('id', ''))
        },
        key=_remote_model_sort_key,
    )
    return [ProviderModel(model_id=model_id, label=model_id) for model_id in model_ids]


def _list_gemini_models(api_key: str) -> list[ProviderModel]:
    payload = _http_json(
        f'{GEMINI_API_BASE_URL}/models',
        headers={
            'x-goog-api-key': api_key,
        },
    )
    model_ids = sorted(
        {
            item.get('name', '').split('/', 1)[1]
            for item in payload.get('models', [])
            if isinstance(item, dict) and _is_supported_gemini_model(item)
        },
        key=_remote_model_sort_key,
    )
    return [ProviderModel(model_id=model_id, label=model_id) for model_id in model_ids]


def _is_supported_openai_model(model_id: str) -> bool:
    if not model_id:
        return False

    lowered = model_id.lower()
    excluded_markers = (
        'audio',
        'realtime',
        'transcribe',
        'tts',
        'whisper',
        'dall',
        'embedding',
        'moderation',
        'search',
        'omni-moderation',
        'computer-use',
        'image',
    )
    if any(marker in lowered for marker in excluded_markers):
        return False
    return lowered.startswith('gpt-')


def _list_anthropic_models(api_key: str) -> list[ProviderModel]:
    payload = _http_json(
        f'{ANTHROPIC_API_BASE_URL}/models',
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
        },
    )
    model_ids = sorted(
        {
            item.get('id', '')
            for item in payload.get('data', [])
            if isinstance(item, dict) and _is_supported_anthropic_model(item.get('id', ''))
        },
        key=_remote_model_sort_key,
    )
    return [ProviderModel(model_id=model_id, label=model_id) for model_id in model_ids]


def _list_deepseek_models(api_key: str) -> list[ProviderModel]:
    payload = _http_json(
        f'{DEEPSEEK_API_BASE_URL}/models',
        headers={
            'Authorization': f'Bearer {api_key}',
        },
    )
    model_ids = sorted(
        {
            item.get('id', '')
            for item in payload.get('data', [])
            if isinstance(item, dict) and _is_supported_deepseek_model(item.get('id', ''))
        },
        key=_remote_model_sort_key,
    )
    return [ProviderModel(model_id=model_id, label=model_id) for model_id in model_ids]


def _is_supported_anthropic_model(model_id: str) -> bool:
    if not model_id:
        return False
    lowered = model_id.lower()
    return lowered.startswith('claude-')


def _is_supported_gemini_model(model: dict) -> bool:
    name = model.get('name', '')
    if not isinstance(name, str) or not name.startswith('models/gemini'):
        return False
    generation_methods = model.get('supportedGenerationMethods', [])
    if 'generateContent' not in generation_methods:
        return False

    lowered = name.lower()
    excluded_markers = (
        'embedding',
        'aqa',
        'image-generation',
        'vision',
        'tts',
        'live',
    )
    return not any(marker in lowered for marker in excluded_markers)


def _is_supported_deepseek_model(model_id: str) -> bool:
    if not model_id:
        return False
    lowered = model_id.lower()
    return lowered.startswith('deepseek-')


def _remote_model_sort_key(model_id: str) -> tuple[int, str]:
    priority_map = {
        'gpt-5-mini': 0,
        'gpt-5-nano': 1,
        'gpt-4.1-mini': 2,
        'gemini-2.5-flash': 0,
        'gemini-2.5-pro': 1,
        'gemini-2.0-flash': 2,
        'claude-sonnet-4-5': 0,
        'claude-opus-4-1': 1,
        'claude-3-5-haiku-latest': 2,
        'deepseek-chat': 0,
        'deepseek-reasoner': 1,
    }
    return (priority_map.get(model_id, 100), model_id)


def _chat_completion(
    provider: str,
    *,
    api_key: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    if provider == 'openai':
        url = f'{OPENAI_API_BASE_URL}/chat/completions'
        headers = {'Authorization': f'Bearer {api_key}'}
    elif provider == 'gemini':
        url = f'{GEMINI_OPENAI_BASE_URL}/chat/completions'
        headers = {'Authorization': f'Bearer {api_key}'}
    elif provider == 'deepseek':
        url = f'{DEEPSEEK_API_BASE_URL}/chat/completions'
        headers = {'Authorization': f'Bearer {api_key}'}
    elif provider == 'anthropic':
        return _anthropic_message_completion(
            api_key=api_key,
            model_id=model_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
    else:
        raise RemoteProviderError(f'Proveedor remoto no soportado: {provider}')

    payload = _http_json(
        url,
        method='POST',
        headers=headers,
        body={
            'model': model_id,
            'temperature': 0,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
        },
    )
    try:
        message = payload['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError) as error_info:
        raise RemoteProviderError('La respuesta del proveedor remoto no tiene el formato esperado.') from error_info

    if isinstance(message, str):
        return message

    if isinstance(message, list):
        return ''.join(part.get('text', '') for part in message if isinstance(part, dict))

    raise RemoteProviderError('No se ha podido leer el contenido de la respuesta remota.')


def _anthropic_message_completion(
    *,
    api_key: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    payload = _http_json(
        f'{ANTHROPIC_API_BASE_URL}/messages',
        method='POST',
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
        },
        body={
            'model': model_id,
            'max_tokens': 8192,
            'temperature': 0,
            'system': system_prompt,
            'messages': [
                {'role': 'user', 'content': user_prompt},
            ],
        },
    )
    content = payload.get('content')
    if not isinstance(content, list):
        raise RemoteProviderError('La respuesta de Anthropic no tiene el formato esperado.')

    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get('type') != 'text':
            continue
        text = item.get('text')
        if isinstance(text, str):
            parts.append(text)

    if not parts:
        raise RemoteProviderError('No se ha podido leer el texto devuelto por Anthropic.')
    return ''.join(parts)


def _extract_json(content: str) -> dict:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find('{')
        end = content.rfind('}')
        if start < 0 or end <= start:
            raise RemoteProviderError('La respuesta del proveedor remoto no contiene JSON válido.') from None
        try:
            parsed = json.loads(content[start : end + 1])
        except json.JSONDecodeError as error_info:
            raise RemoteProviderError('La respuesta del proveedor remoto no contiene un JSON utilizable.') from error_info

    if not isinstance(parsed, dict):
        raise RemoteProviderError('La respuesta del proveedor remoto no contiene el objeto JSON esperado.')
    return parsed


def _http_json(
    url: str,
    *,
    method: str = 'GET',
    headers: dict[str, str] | None = None,
    body: dict | None = None,
    timeout: int = 30,
) -> dict:
    request_headers = {'Accept': 'application/json'}
    if headers:
        request_headers.update(headers)

    data = None
    if body is not None:
        request_headers['Content-Type'] = 'application/json'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')

    req = request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or 'utf-8'
            parsed = json.loads(response.read().decode(charset))
            if not isinstance(parsed, dict):
                raise RemoteProviderError('La respuesta HTTP no devolvió un objeto JSON válido.')
            return parsed
    except error.HTTPError as http_error:
        details = http_error.read().decode('utf-8', errors='replace').strip()
        retry_after_seconds = _extract_retry_after_seconds(http_error.headers)
        if details:
            try:
                parsed = json.loads(details)
                details = _extract_error_details(parsed, details)
                retry_after_seconds = retry_after_seconds or _extract_retry_delay_from_payload(parsed)
            except json.JSONDecodeError:
                pass
        raise RemoteProviderError(
            _format_http_error_message(http_error.code, details or http_error.reason, retry_after_seconds),
            status_code=http_error.code,
            retry_after_seconds=retry_after_seconds,
            raw_details=details or http_error.reason,
        ) from http_error
    except error.URLError as url_error:
        raise RemoteProviderError(f'No se ha podido conectar con el proveedor remoto: {url_error.reason}') from url_error


def _extract_error_details(parsed, fallback: str) -> str:
    if isinstance(parsed, dict):
        error_payload = parsed.get('error')
        if isinstance(error_payload, dict):
            message = error_payload.get('message') or error_payload.get('status') or fallback
            quota_summary = _extract_quota_summary(error_payload)
            if quota_summary:
                return quota_summary
            if isinstance(message, str):
                return _sanitize_error_message(message)
            return str(message)
        if isinstance(error_payload, list):
            messages = [str(item) for item in error_payload if item]
            return '; '.join(messages) or fallback
        return str(error_payload or fallback)

    if isinstance(parsed, list):
        messages = [str(item) for item in parsed if item]
        return '; '.join(messages) or fallback

    return fallback


def _extract_quota_summary(error_payload: dict) -> str | None:
    details = error_payload.get('details', [])
    if not isinstance(details, list):
        return None
    for item in details:
        if not isinstance(item, dict):
            continue
        violations = item.get('violations', [])
        if not isinstance(violations, list):
            continue
        for violation in violations:
            if not isinstance(violation, dict):
                continue
            quota_id = str(violation.get('quotaId') or '')
            quota_metric = str(violation.get('quotaMetric') or '').strip()
            quota_value = str(violation.get('quotaValue') or '').strip()
            quota_dimensions = violation.get('quotaDimensions') or {}
            model = ''
            if isinstance(quota_dimensions, dict):
                model = str(quota_dimensions.get('model') or '').strip()
            if 'perday' in quota_id.lower():
                return _format_quota_summary('Cuota diaria agotada.', quota_metric, quota_value, model)
            if 'perminute' in quota_id.lower():
                return _format_quota_summary('Límite por minuto agotado.', quota_metric, quota_value, model)
    return None


def _format_quota_summary(prefix: str, quota_metric: str, quota_value: str, model: str) -> str:
    parts = [prefix]
    if quota_metric:
        parts.append(quota_metric)
    if quota_value:
        parts.append(f'límite: {quota_value}')
    if model:
        parts.append(f'modelo: {model}')
    return ' '.join(parts)


def _extract_retry_after_seconds(headers) -> float | None:
    if headers is None:
        return None
    retry_after = headers.get('Retry-After')
    if not retry_after:
        return None
    try:
        return max(float(retry_after), 0.0)
    except ValueError:
        return None


def _extract_retry_delay_from_payload(parsed) -> float | None:
    if not isinstance(parsed, dict):
        return None
    error_payload = parsed.get('error')
    if not isinstance(error_payload, dict):
        return None
    details = error_payload.get('details', [])
    if not isinstance(details, list):
        return None
    for item in details:
        if not isinstance(item, dict):
            continue
        retry_delay = item.get('retryDelay')
        if isinstance(retry_delay, str):
            seconds = _parse_duration_seconds(retry_delay)
            if seconds is not None:
                return seconds
    message = error_payload.get('message')
    if isinstance(message, str):
        marker = 'Please retry in '
        index = message.find(marker)
        if index >= 0:
            snippet = message[index + len(marker) :].split('.', 1)[0].strip()
            seconds = _parse_duration_seconds(snippet)
            if seconds is not None:
                return seconds
    return None


def _parse_duration_seconds(value: str) -> float | None:
    if not value:
        return None
    normalized = value.strip().lower()
    try:
        if normalized.endswith('ms'):
            return max(float(normalized[:-2].strip()) / 1000.0, 0.0)
        if normalized.endswith('s'):
            return max(float(normalized[:-1].strip()), 0.0)
        return max(float(normalized), 0.0)
    except ValueError:
        return None


def _sanitize_error_message(message: str) -> str:
    cleaned = ' '.join(message.split())
    quota_marker = '* Quota exceeded for metric:'
    quota_index = cleaned.find(quota_marker)
    if quota_index >= 0:
        quota_summary = cleaned[quota_index + len(quota_marker) :].strip()
        retry_marker = 'Please retry in '
        retry_index = quota_summary.find(retry_marker)
        if retry_index >= 0:
            quota_summary = quota_summary[:retry_index].strip()
        return f'Cuota agotada. {quota_summary}'
    marker = 'For more information on this error'
    index = cleaned.find(marker)
    if index >= 0:
        cleaned = cleaned[:index].strip()
    return cleaned


def _format_http_error_message(status_code: int, details: str, retry_after_seconds: float | None) -> str:
    details = _normalize_error_details_text(details)
    if status_code == 429:
        lowered = details.lower()
        if 'perday' in lowered or 'quota diaria' in lowered or 'per day' in lowered:
            return f'Cuota diaria agotada del proveedor remoto (HTTP 429). {details}'
        if retry_after_seconds is not None:
            retry_seconds = max(retry_after_seconds, 1.0)
            return f'Límite temporal del proveedor remoto (HTTP 429). Reintenta en {retry_seconds:.1f} s. {details}'
        return f'Límite temporal del proveedor remoto (HTTP 429). {details}'
    return f'Error HTTP {status_code} al llamar al proveedor remoto: {details}'


def _normalize_error_details_text(details: str) -> str:
    if not details:
        return details

    parsed = None
    try:
        parsed = json.loads(details)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(details)
        except (ValueError, SyntaxError):
            parsed = None

    if parsed is not None:
        normalized = _extract_error_details(parsed, details)
        if isinstance(normalized, str):
            return normalized

    return details
