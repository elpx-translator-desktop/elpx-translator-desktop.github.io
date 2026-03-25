from __future__ import annotations

from dataclasses import dataclass

LANGUAGE_OPTIONS = [
    ('es', 'Español'),
    ('en', 'English'),
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


MODEL_CONFIG = ModelConfig(
    repo_id='gn64/M2M100_418M_CTranslate2',
    label='M2M100 418M CTranslate2',
    tokenizer_repo_id='facebook/m2m100_418M',
)
