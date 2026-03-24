from __future__ import annotations

import re

REFERENCE_RE = re.compile(r'^(asset://|https?://|mailto:|tel:|exe-node:|\{\{context_path\}\})', re.I)
HASHLIKE_RE = re.compile(r'^[A-Za-z0-9_-]{20,}$')
HTML_RE = re.compile(r'</?[a-z][\s\S]*>', re.I)


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
