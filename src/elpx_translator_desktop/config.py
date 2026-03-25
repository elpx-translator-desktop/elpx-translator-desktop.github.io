from __future__ import annotations

from dataclasses import dataclass

LANGUAGE_OPTIONS = [
    ('es', 'Español'),
    ('en', 'English'),
    ('eu', 'Euskara'),
    ('fr', 'Français'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('pt', 'Português'),
    ('ca', 'Català'),
    ('gl', 'Galego'),
]
SUPPORTED_LANGUAGE_CODES = {code for code, _ in LANGUAGE_OPTIONS}

DEFAULT_SOURCE_LANGUAGE = 'es'
DEFAULT_TARGET_LANGUAGE = 'en'
DEFAULT_PERFORMANCE_MODE = 'equilibrado'

PERFORMANCE_MODE_OPTIONS = [
    ('suave', 'Suave'),
    ('equilibrado', 'Equilibrado'),
    ('rapido', 'Rápido'),
    ('maximo', 'Máximo'),
]
PERFORMANCE_MODE_LABELS = dict(PERFORMANCE_MODE_OPTIONS)

HTML_TRANSLATABLE_ATTRIBUTES = ['alt', 'title', 'placeholder', 'aria-label', 'label']
EXCLUDED_HTML_TAGS = {'code', 'pre', 'script', 'style', 'kbd', 'samp', 'math', 'svg'}
JSON_SKIP_KEYS = {
    'id',
    'ideviceId',
    'evaluationID',
    'typeGame',
    'url',
    'urls',
    'path',
    'paths',
    'filename',
    'fileName',
    'file',
    'image',
    'images',
    'audio',
    'video',
    'author',
    'license',
    'lang',
    'language',
    'cssClass',
    'class',
    'classes',
    'assetId',
    'assetUUID',
    'uuid',
    'hash',
    'slug',
    'template',
    'icon',
}


@dataclass(frozen=True)
class ModelConfig:
    repo_id: str
    label: str
    tokenizer_repo_id: str
    model_type: str = 'm2m100'


MODEL_CONFIG = ModelConfig(
    repo_id='gn64/M2M100_418M_CTranslate2',
    label='M2M100 418M CTranslate2',
    tokenizer_repo_id='facebook/m2m100_418M',
)

EUSKERA_MODEL_CONFIGS = {
    ('es', 'eu'): ModelConfig(
        repo_id='gaudi/opus-mt-es-eu-ctranslate2',
        label='OPUS-MT es-eu',
        tokenizer_repo_id='Helsinki-NLP/opus-mt-es-eu',
        model_type='opus_mt',
    ),
    ('eu', 'es'): ModelConfig(
        repo_id='gaudi/opus-mt-eu-es-ctranslate2',
        label='OPUS-MT eu-es',
        tokenizer_repo_id='Helsinki-NLP/opus-mt-eu-es',
        model_type='opus_mt',
    ),
    ('en', 'eu'): ModelConfig(
        repo_id='gaudi/opus-mt-en-eu-ctranslate2',
        label='OPUS-MT en-eu',
        tokenizer_repo_id='Helsinki-NLP/opus-mt-en-eu',
        model_type='opus_mt',
    ),
    ('eu', 'en'): ModelConfig(
        repo_id='gaudi/opus-mt-eu-en-ctranslate2',
        label='OPUS-MT eu-en',
        tokenizer_repo_id='Helsinki-NLP/opus-mt-eu-en',
        model_type='opus_mt',
    ),
}


def is_supported_language_pair(source_language: str, target_language: str) -> bool:
    if source_language == target_language:
        return False

    if source_language not in SUPPORTED_LANGUAGE_CODES or target_language not in SUPPORTED_LANGUAGE_CODES:
        return False

    if 'eu' in {source_language, target_language}:
        return (source_language, target_language) in EUSKERA_MODEL_CONFIGS

    return True


def supported_target_languages(source_language: str) -> list[str]:
    return [code for code, _ in LANGUAGE_OPTIONS if is_supported_language_pair(source_language, code)]


def supported_source_languages(target_language: str) -> list[str]:
    return [code for code, _ in LANGUAGE_OPTIONS if is_supported_language_pair(code, target_language)]
