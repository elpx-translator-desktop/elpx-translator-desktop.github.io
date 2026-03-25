from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.dom import minidom

from bs4 import BeautifulSoup, NavigableString, Tag

from .config import EXCLUDED_HTML_TAGS, HTML_TRANSLATABLE_ATTRIBUTES, JSON_SKIP_KEYS
from .progress import ProgressEvent, TranslationCancelledError
from .text_utils import (
    is_translatable_text,
    looks_like_encoded_payload,
    looks_like_html,
    looks_like_reference,
    split_surrounding_whitespace,
)
from .translator_engine import TranslationEngine
from .ui_i18n import tr


@dataclass
class TranslationOptions:
    source_language: str
    target_language: str
    ui_language: str = 'es'
    should_cancel: object | None = None


class ProgressTracker:
    def __init__(self, total_units: int, callback) -> None:
        self.total_units = total_units
        self.completed_units = 0
        self.callback = callback
        self.translation_memory: dict[str, str] = {}

    def report(self, message: str, *, transient: bool = False, silent: bool = False) -> None:
        progress_percent = None
        if self.total_units:
            progress_percent = (self.completed_units / self.total_units) * 100
        self.callback(
            ProgressEvent(
                message,
                progress_percent=progress_percent,
                completed_units=self.completed_units,
                total_units=self.total_units,
                transient=transient,
                silent=silent,
            ),
        )

    def create_batch_meta(self, count: int) -> dict | None:
        if not count or not self.total_units:
            return None
        return {
            'start_unit_index': self.completed_units + 1,
            'completed_units_before_batch': self.completed_units,
            'total_units': self.total_units,
        }

    def complete_batch(self, count: int) -> None:
        self.completed_units += count


class ElpxTranslationService:
    def __init__(self, engine: TranslationEngine | None = None) -> None:
        self.engine = engine or TranslationEngine()

    def detect_project_language(self, input_path: Path) -> str | None:
        with zipfile.ZipFile(input_path, 'r') as archive:
            content_xml_path = self._find_content_xml_path(archive.namelist())
            if not content_xml_path:
                return None

            xml_content = archive.read(content_xml_path).decode('utf-8')

        document = minidom.parseString(xml_content.encode('utf-8'))
        property_nodes = self._get_property_value_nodes(document, 'odeProperty', {'pp_lang'})
        if property_nodes:
            return property_nodes[0][1].strip().lower()

        return None

    def translate_file(self, input_path: Path, output_path: Path, options: TranslationOptions, progress_callback) -> None:
        self._raise_if_cancelled(options)
        progress_callback(ProgressEvent(tr(options.ui_language, 'opening_elpx')))
        with zipfile.ZipFile(input_path, 'r') as archive:
            content_xml_path = self._find_content_xml_path(archive.namelist())
            if not content_xml_path:
                raise ValueError(tr(options.ui_language, 'content_xml_missing'))

            self._raise_if_cancelled(options)
            progress_callback(ProgressEvent(tr(options.ui_language, 'reading_content_xml')))
            xml_content = archive.read(content_xml_path).decode('utf-8')
            translated_xml = self._translate_content_xml(xml_content, options, progress_callback)

            self._raise_if_cancelled(options)
            progress_callback(ProgressEvent(tr(options.ui_language, 'rebuilding_elpx')))
            with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as destination:
                for member in archive.infolist():
                    self._raise_if_cancelled(options)
                    data = archive.read(member.filename)
                    if member.filename == content_xml_path:
                        data = translated_xml.encode('utf-8')
                    destination.writestr(member, data)

        self._raise_if_cancelled(options)
        progress_callback(ProgressEvent(tr(options.ui_language, 'file_ready'), state='done', progress_percent=100))

    def _translate_content_xml(self, xml_content: str, options: TranslationOptions, progress_callback) -> str:
        document = minidom.parseString(xml_content.encode('utf-8'))
        components = document.getElementsByTagName('odeComponent')
        total_units = self._count_structural_units(document) + sum(self._count_component_units(component) for component in components)
        tracker = ProgressTracker(total_units, progress_callback)

        if total_units == 0:
            tracker.report(tr(options.ui_language, 'no_translatable_text'))
            return xml_content

        tracker.report(
            tr(
                options.ui_language,
                'detected_units',
                total_units=total_units,
                component_count=len(components),
            ),
        )
        self._translate_structural_nodes(document, tracker, options)

        for index, component in enumerate(components, start=1):
            self._raise_if_cancelled(options)
            tracker.report(tr(options.ui_language, 'preparing_idevice', index=index, total=len(components)))
            self._translate_component(component, tracker, options, index, len(components))

        return self._serialize_document(document, xml_content)

    def _translate_component(self, component, tracker: ProgressTracker, options: TranslationOptions, index: int, total: int) -> None:
        progress_label = f'iDevice {index} de {total}'

        html_nodes = component.getElementsByTagName('htmlView')
        if html_nodes and html_nodes[0].firstChild:
            translated_html = self._translate_html_fragment(
                html_nodes[0].firstChild.nodeValue or '',
                tracker,
                options,
                progress_label,
            )
            self._replace_node_with_cdata(html_nodes[0], translated_html)

        json_nodes = component.getElementsByTagName('jsonProperties')
        if json_nodes and json_nodes[0].firstChild and json_nodes[0].firstChild.nodeValue.strip():
            try:
                parsed = json.loads(json_nodes[0].firstChild.nodeValue)
                translated = self._translate_json_value(parsed, tracker, options, progress_label)
                self._replace_node_with_cdata(json_nodes[0], json.dumps(translated, ensure_ascii=False))
            except json.JSONDecodeError:
                tracker.report(tr(options.ui_language, 'invalid_json_properties'))

    def _translate_structural_nodes(self, document, tracker: ProgressTracker, options: TranslationOptions) -> None:
        page_name_nodes = self._get_text_nodes_by_tag(document, 'pageName')
        if page_name_nodes:
            translated = self._translate_plain_texts(page_name_nodes, tracker, options, tr(options.ui_language, 'page_titles'))
            for node, text in translated:
                self._replace_node_text(node, text)

        block_name_nodes = self._get_text_nodes_by_tag(document, 'blockName')
        if block_name_nodes:
            translated = self._translate_plain_texts(block_name_nodes, tracker, options, tr(options.ui_language, 'block_titles'))
            for node, text in translated:
                self._replace_node_text(node, text)

        nav_title_nodes = self._get_property_value_nodes(document, 'odeNavStructureProperty', {'titlePage'})
        if nav_title_nodes:
            translated = self._translate_plain_texts(nav_title_nodes, tracker, options, tr(options.ui_language, 'navigation_titles'))
            for node, text in translated:
                self._replace_node_text(node, text)

        project_meta_nodes = self._get_property_value_nodes(document, 'odeProperty', {'pp_title', 'pp_description'})
        if project_meta_nodes:
            translated = self._translate_plain_texts(project_meta_nodes, tracker, options, tr(options.ui_language, 'project_metadata'))
            for node, text in translated:
                self._replace_node_text(node, text)

    def _translate_html_fragment(
        self,
        html: str,
        tracker: ProgressTracker,
        options: TranslationOptions,
        progress_label: str,
    ) -> str:
        if not html.strip():
            return html

        soup = BeautifulSoup(f'<div id="translation-root">{html}</div>', 'html.parser')
        root = soup.find(id='translation-root')
        if root is None:
            return html

        text_targets: list[tuple[NavigableString, str, str, str]] = []
        for text_node in root.find_all(string=True):
            parent = text_node.parent
            text_value = str(text_node)
            leading_ws, core_text, trailing_ws = split_surrounding_whitespace(text_value)
            if (
                self._should_translate_html_text(parent, core_text)
            ):
                text_targets.append((text_node, leading_ws, core_text, trailing_ws))

        attribute_targets: list[tuple[Tag, str, str]] = []
        for element in root.find_all(True):
            if element.name in EXCLUDED_HTML_TAGS:
                continue
            for attribute in HTML_TRANSLATABLE_ATTRIBUTES:
                value = element.get(attribute)
                if isinstance(value, str) and is_translatable_text(value):
                    attribute_targets.append((element, attribute, value))

        translated_texts = self._translate_plain_texts(
            [(node, core_text) for node, _, core_text, _ in text_targets],
            tracker,
            options,
            progress_label,
        )
        for (target, leading_ws, _, trailing_ws), (_, translated) in zip(text_targets, translated_texts, strict=False):
            target.replace_with(f'{leading_ws}{translated}{trailing_ws}')

        translated_attributes = self._translate_plain_texts(
            [(item, item[2]) for item in attribute_targets],
            tracker,
            options,
            progress_label,
        )
        for (element, attribute, _), (_, translated) in zip(attribute_targets, translated_attributes, strict=False):
            element[attribute] = translated

        return ''.join(str(child) for child in root.contents)

    def _translate_json_value(self, value, tracker: ProgressTracker, options: TranslationOptions, progress_label: str, key: str = ''):
        if isinstance(value, str):
            if self._should_skip_json_value(key, value):
                return value
            if looks_like_html(value):
                return self._translate_html_fragment(value, tracker, options, progress_label)
            return self._translate_plain_texts([(None, value)], tracker, options, progress_label)[0][1]

        if isinstance(value, list):
            return [self._translate_json_value(item, tracker, options, progress_label, key) for item in value]

        if isinstance(value, dict):
            return {
                child_key: self._translate_json_value(child_value, tracker, options, progress_label, child_key)
                for child_key, child_value in value.items()
            }

        return value

    def _translate_plain_texts(
        self,
        text_nodes: list[tuple[object, str]],
        tracker: ProgressTracker,
        options: TranslationOptions,
        progress_label: str,
    ) -> list[tuple[object, str]]:
        if not text_nodes:
            return []

        texts = [text for _, text in text_nodes]

        results: list[str | None] = [None] * len(texts)
        pending_texts: list[str] = []
        pending_indexes: dict[str, list[int]] = {}

        for index, text in enumerate(texts):
            cached = tracker.translation_memory.get(text)
            if cached:
                results[index] = cached
                continue

            pending_indexes.setdefault(text, []).append(index)
            if len(pending_indexes[text]) == 1:
                pending_texts.append(text)

        if pending_texts:
            translated = self.engine.translate_texts(
                pending_texts,
                source_language=options.source_language,
                target_language=options.target_language,
                progress_callback=tracker.callback,
                progress_label=progress_label,
                progress_meta=tracker.create_batch_meta(len(pending_texts)),
                should_cancel=options.should_cancel,
            )
            for source_text, translated_text in zip(pending_texts, translated, strict=False):
                tracker.translation_memory[source_text] = translated_text
                for target_index in pending_indexes.get(source_text, []):
                    results[target_index] = translated_text

        tracker.complete_batch(len(texts))
        return [(text_nodes[index][0], item or texts[index]) for index, item in enumerate(results)]

    def _count_component_units(self, component) -> int:
        total = 0
        html_nodes = component.getElementsByTagName('htmlView')
        if html_nodes and html_nodes[0].firstChild:
            total += self._count_html_units(html_nodes[0].firstChild.nodeValue or '')

        json_nodes = component.getElementsByTagName('jsonProperties')
        if json_nodes and json_nodes[0].firstChild:
            try:
                total += self._count_json_units(json.loads(json_nodes[0].firstChild.nodeValue or ''))
            except json.JSONDecodeError:
                pass

        return total

    def _count_structural_units(self, document) -> int:
        return (
            len(self._get_text_nodes_by_tag(document, 'pageName'))
            + len(self._get_text_nodes_by_tag(document, 'blockName'))
            + len(self._get_property_value_nodes(document, 'odeNavStructureProperty', {'titlePage'}))
            + len(self._get_property_value_nodes(document, 'odeProperty', {'pp_title', 'pp_description'}))
        )

    def _count_html_units(self, html: str) -> int:
        if not html.strip():
            return 0

        soup = BeautifulSoup(f'<div id="translation-root">{html}</div>', 'html.parser')
        root = soup.find(id='translation-root')
        if root is None:
            return 0

        count = 0
        for text_node in root.find_all(string=True):
            parent = text_node.parent
            if self._should_translate_html_text(parent, str(text_node)):
                count += 1

        for element in root.find_all(True):
            if element.name in EXCLUDED_HTML_TAGS:
                continue
            for attribute in HTML_TRANSLATABLE_ATTRIBUTES:
                value = element.get(attribute)
                if isinstance(value, str) and is_translatable_text(value):
                    count += 1

        return count

    def _count_json_units(self, value, key: str = '') -> int:
        if isinstance(value, str):
            if self._should_skip_json_value(key, value):
                return 0
            if looks_like_html(value):
                return self._count_html_units(value)
            return 1

        if isinstance(value, list):
            return sum(self._count_json_units(item, key) for item in value)

        if isinstance(value, dict):
            return sum(self._count_json_units(child_value, child_key) for child_key, child_value in value.items())

        return 0

    @staticmethod
    def _get_text_nodes_by_tag(document, tag_name: str) -> list[tuple[object, str]]:
        results: list[tuple[object, str]] = []
        for node in document.getElementsByTagName(tag_name):
            text = ''.join(
                child.data for child in node.childNodes if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE)
            ).strip()
            if is_translatable_text(text):
                results.append((node, text))
        return results

    @staticmethod
    def _get_property_value_nodes(document, property_tag: str, allowed_keys: set[str]) -> list[tuple[object, str]]:
        results: list[tuple[object, str]] = []
        for property_node in document.getElementsByTagName(property_tag):
            key_nodes = property_node.getElementsByTagName('key')
            value_nodes = property_node.getElementsByTagName('value')
            if not key_nodes or not value_nodes:
                continue

            key = ''.join(
                child.data for child in key_nodes[0].childNodes if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE)
            ).strip()
            if key not in allowed_keys:
                continue

            value = ''.join(
                child.data for child in value_nodes[0].childNodes if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE)
            ).strip()
            if is_translatable_text(value):
                results.append((value_nodes[0], value))
        return results

    @staticmethod
    def _replace_node_text(node, text: str) -> None:
        while node.firstChild:
            node.removeChild(node.firstChild)
        node.appendChild(node.ownerDocument.createTextNode(text))

    @staticmethod
    def _find_content_xml_path(names: list[str]) -> str | None:
        if 'content.xml' in names:
            return 'content.xml'
        for name in names:
            if name.endswith('/content.xml'):
                return name
        return None

    @staticmethod
    def _should_skip_json_value(key: str, value: str) -> bool:
        trimmed = value.strip()
        if not trimmed:
            return True
        if key in JSON_SKIP_KEYS:
            return True
        if looks_like_reference(trimmed):
            return True
        if looks_like_encoded_payload(trimmed):
            return True
        if re.fullmatch(r'[A-Za-z0-9_-]{20,}', trimmed):
            return True
        return False

    @staticmethod
    def _should_translate_html_text(parent, text: str) -> bool:
        if not isinstance(parent, Tag):
            return False
        if parent.name in EXCLUDED_HTML_TAGS:
            return False

        trimmed = text.strip()
        if looks_like_encoded_payload(trimmed):
            return False

        return is_translatable_text(trimmed)

    @staticmethod
    def _replace_node_with_cdata(node, text: str) -> None:
        while node.firstChild:
            node.removeChild(node.firstChild)
        owner_document = node.ownerDocument
        chunks = text.split(']]>')
        for index, chunk in enumerate(chunks):
            suffix = ']]' if index < len(chunks) - 1 else ''
            node.appendChild(owner_document.createCDATASection(f'{chunk}{suffix}'))
            if index < len(chunks) - 1:
                node.appendChild(owner_document.createTextNode('>'))

    @staticmethod
    def _serialize_document(document, original_xml: str) -> str:
        xml_declaration_match = re.match(r'^\s*<\?xml[^>]+\?>', original_xml)
        xml_declaration = xml_declaration_match.group(0) if xml_declaration_match else '<?xml version="1.0" encoding="UTF-8"?>'
        doctype_match = re.search(r'<!DOCTYPE[^>]+>', original_xml)
        doctype = doctype_match.group(0) if doctype_match else ''
        root_xml = document.documentElement.toxml()
        parts = [xml_declaration]
        if doctype:
            parts.append(doctype)
        parts.append(root_xml)
        return '\n'.join(parts)

    @staticmethod
    def _raise_if_cancelled(options: TranslationOptions) -> None:
        if callable(options.should_cancel) and options.should_cancel():
            raise TranslationCancelledError(tr(options.ui_language, 'translation_cancelled'))
