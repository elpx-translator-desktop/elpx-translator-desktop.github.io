from __future__ import annotations

import json
import re

REFERENCE_RE = re.compile(r'^(asset://|https?://|mailto:|tel:|exe-node:|\{\{context_path\}\})', re.I)
HASHLIKE_RE = re.compile(r'^[A-Za-z0-9_-]{20,}$')
HTML_RE = re.compile(r'</?[a-z][\s\S]*>', re.I)
PERCENT_ENCODED_CHUNK_RE = re.compile(r'%[0-9A-Fa-f]{2}')
BASE64ISH_RE = re.compile(r'^[A-Za-z0-9+/=_-]{80,}$')
NUMERIC_LIST_PREFIX_RE = re.compile(r'^(?P<prefix>\(?\d+\)?[.)](?:\s+)?)(?P<rest>(?!\d)\S[\s\S]*)$')
JSON_NUMERIC_VALUE_RE = re.compile(r'^[+-]?\d+(?:[.,]\d+)?$')
HEX_COLOR_RE = re.compile(r'^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$')
TIME_LIKE_RE = re.compile(r'^\d{1,2}:\d{2}(?::\d{2})?$')
DATE_LIKE_RE = re.compile(r'^\d{1,2}/\d{1,2}/\d{2,4}$')
MODEL_ARTIFACT_RE = re.compile(r'\s*<unk>\s*', re.I)
CLOZE_MARKER_RE = re.compile(r'@@(?P<body>[^@]+?)@@')


def split_long_text(text: str, max_length: int = 420) -> list[str]:
    normalized = text.strip()
    if len(normalized) <= max_length:
        return [normalized]

    chunks: list[str] = []
    paragraphs = re.split(r'\n{2,}', normalized)

    for paragraph in paragraphs:
        trimmed_paragraph = paragraph.strip()
        if not trimmed_paragraph:
            continue

        if len(trimmed_paragraph) <= max_length:
            chunks.append(trimmed_paragraph)
            continue

        sentences = re.findall(r'[^.!?\n]+(?:[.!?\n]+|$)', trimmed_paragraph) or [trimmed_paragraph]
        current_chunk = ''

        for sentence in sentences:
            sentence = sentence.strip()
            candidate = f'{current_chunk} {sentence}'.strip() if current_chunk else sentence
            if len(candidate) <= max_length:
                current_chunk = candidate
                continue

            if current_chunk:
                chunks.append(current_chunk)

            if len(sentence) <= max_length:
                current_chunk = sentence
                continue

            words = sentence.split()
            current_chunk = ''
            for word in words:
                word_candidate = f'{current_chunk} {word}'.strip() if current_chunk else word
                if len(word_candidate) <= max_length:
                    current_chunk = word_candidate
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = word

        if current_chunk:
            chunks.append(current_chunk)

    return chunks or [normalized]


def is_translatable_text(text: str | None) -> bool:
    if not text or not text.strip():
        return False

    trimmed = text.strip()
    if not re.search(r'[\w\d]', trimmed, re.UNICODE):
        return False

    if REFERENCE_RE.match(trimmed):
        return False

    if HASHLIKE_RE.match(trimmed):
        return False

    return True


def looks_like_html(value: str) -> bool:
    return bool(HTML_RE.search(value))


def looks_like_reference(value: str) -> bool:
    return bool(REFERENCE_RE.match(value.strip()))


def normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def split_surrounding_whitespace(text: str) -> tuple[str, str, str]:
    leading_match = re.match(r'^\s*', text)
    trailing_match = re.search(r'\s*$', text)
    leading = leading_match.group(0) if leading_match else ''
    trailing = trailing_match.group(0) if trailing_match else ''
    core = text[len(leading) : len(text) - len(trailing) if trailing else len(text)]
    return leading, core, trailing


def split_numeric_list_prefix(text: str) -> tuple[str, str]:
    match = NUMERIC_LIST_PREFIX_RE.match(text)
    if not match:
        return '', text
    return match.group('prefix'), match.group('rest')


def looks_like_nontranslatable_scalar(value: str) -> bool:
    trimmed = value.strip()
    if not trimmed:
        return True
    if JSON_NUMERIC_VALUE_RE.fullmatch(trimmed):
        return True
    if TIME_LIKE_RE.fullmatch(trimmed):
        return True
    if DATE_LIKE_RE.fullmatch(trimmed):
        return True
    return bool(HEX_COLOR_RE.fullmatch(trimmed))


def sanitize_translated_text(text: str) -> str:
    cleaned = MODEL_ARTIFACT_RE.sub(' ', text)
    return re.sub(r'\s{2,}', ' ', cleaned).strip()


def contains_cloze_markers(text: str) -> bool:
    return bool(CLOZE_MARKER_RE.search(text))


def extract_cloze_marker_texts(text: str) -> list[str]:
    extracted: list[str] = []
    for match in CLOZE_MARKER_RE.finditer(text):
        extracted.extend(part.strip() for part in match.group('body').split('|') if part.strip())
    return extracted


def replace_cloze_markers_with_tokens(text: str) -> tuple[str, list[str]]:
    markers: list[str] = []

    def replace(match: re.Match) -> str:
        token = f'__ELPX_CLOZE_{len(markers)}__'
        markers.append(match.group(0))
        return token

    return CLOZE_MARKER_RE.sub(replace, text), markers


def restore_cloze_marker_tokens(text: str, markers: list[str]) -> str:
    restored = text
    for index, marker in enumerate(markers):
        restored = restored.replace(f'__ELPX_CLOZE_{index}__', marker)
    return restored


def translate_cloze_marker(marker: str, translated_parts: list[str]) -> str:
    match = CLOZE_MARKER_RE.fullmatch(marker)
    if not match:
        return marker

    separator = '|' if '|' in match.group('body') else ''
    if separator:
        return f"@@{'|'.join(translated_parts)}@@"
    if translated_parts:
        return f'@@{translated_parts[0]}@@'
    return marker


def looks_like_encoded_payload(value: str) -> bool:
    trimmed = value.strip()
    if len(trimmed) < 32:
        return False

    percent_chunks = PERCENT_ENCODED_CHUNK_RE.findall(trimmed)
    if percent_chunks and (len(percent_chunks) * 3) >= (len(trimmed) * 0.3):
        return True

    return bool(BASE64ISH_RE.fullmatch(trimmed))


def looks_like_json_payload(value: str) -> bool:
    trimmed = value.strip()
    if len(trimmed) < 2:
        return False
    if (not trimmed.startswith('{') or not trimmed.endswith('}')) and (
        not trimmed.startswith('[') or not trimmed.endswith(']')
    ):
        return False

    try:
        parsed = json.loads(trimmed)
    except json.JSONDecodeError:
        return False

    return isinstance(parsed, (dict, list))
