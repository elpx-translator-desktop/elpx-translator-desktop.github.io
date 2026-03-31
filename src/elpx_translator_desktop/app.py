from __future__ import annotations

import faulthandler
import html
import importlib.resources as resources
import sys
import time
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QThread, QTimer, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

APP_LOG_PATH = Path(__file__).resolve().parents[2] / 'elpx-translator-desktop-runtime.log'
FAULT_LOG_PATH = Path(__file__).resolve().parents[2] / 'elpx-translator-desktop-fault.log'
CUSTOM_TARGET_LANGUAGE_VALUE = '__custom_target__'
SETTINGS_ORGANIZATION = 'elpx-translator-desktop'
LEGACY_SETTINGS_ORGANIZATION = 'Juanjo'
SETTINGS_APPLICATION = 'ELPXTranslatorDesktop'
_FAULT_LOG_HANDLE = None


def _append_runtime_log(message: str) -> None:
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        APP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with APP_LOG_PATH.open('a', encoding='utf-8') as handle:
            handle.write(f'[{timestamp}] {message}\n')
    except Exception:
        pass


def _migrate_legacy_settings_if_needed() -> QSettings:
    settings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
    if settings.allKeys():
        return settings

    legacy_settings = QSettings(LEGACY_SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
    legacy_keys = legacy_settings.allKeys()
    if not legacy_keys:
        return settings

    for key in legacy_keys:
        settings.setValue(key, legacy_settings.value(key))
    settings.sync()
    _append_runtime_log(
        f'Migrated QSettings from {LEGACY_SETTINGS_ORGANIZATION} to {SETTINGS_ORGANIZATION}',
    )
    return settings


if __package__ in {None, ''}:
    package_root = Path(__file__).resolve().parent.parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))

    from elpx_translator_desktop import (  # type: ignore[no-redef]
        PROJECT_AUTHOR,
        PROJECT_ISSUES_URL,
        PROJECT_LICENSE_NAME,
        PROJECT_RELEASES_URL,
        PROJECT_REPOSITORY_URL,
        PROJECT_WEBSITE_URL,
        __version__,
    )
    from elpx_translator_desktop.config import (  # type: ignore[no-redef]
        DEFAULT_PERFORMANCE_MODE,
        DEFAULT_SOURCE_LANGUAGE,
        DEFAULT_TARGET_LANGUAGE,
        LANGUAGE_OPTIONS,
        SUPPORTED_LANGUAGE_CODES,
        TRANSLATION_PROVIDER_OPTIONS,
        supported_source_languages,
        supported_target_languages,
    )
    from elpx_translator_desktop.elpx_service import ElpxTranslationService, TranslationOptions  # type: ignore[no-redef]
    from elpx_translator_desktop.progress import ProgressEvent, TranslationCancelledError  # type: ignore[no-redef]
    from elpx_translator_desktop.remote_provider import (  # type: ignore[no-redef]
        RemoteProviderError,
        get_api_key_url,
        is_valid_remote_model,
        list_available_models,
    )
    from elpx_translator_desktop.translator_engine import TranslationEngine  # type: ignore[no-redef]
    from elpx_translator_desktop.update_checker import UpdateCheckWorker  # type: ignore[no-redef]
    from elpx_translator_desktop.ui_i18n import (  # type: ignore[no-redef]
        UI_LANGUAGE_OPTIONS,
        detect_ui_language,
        performance_label,
        tr,
    )
else:
    from . import (
        PROJECT_AUTHOR,
        PROJECT_ISSUES_URL,
        PROJECT_LICENSE_NAME,
        PROJECT_RELEASES_URL,
        PROJECT_REPOSITORY_URL,
        PROJECT_WEBSITE_URL,
        __version__,
    )
    from .config import (
        DEFAULT_PERFORMANCE_MODE,
        DEFAULT_SOURCE_LANGUAGE,
        DEFAULT_TARGET_LANGUAGE,
        LANGUAGE_OPTIONS,
        SUPPORTED_LANGUAGE_CODES,
        TRANSLATION_PROVIDER_OPTIONS,
        supported_source_languages,
        supported_target_languages,
    )
    from .elpx_service import ElpxTranslationService, TranslationOptions
    from .progress import ProgressEvent, TranslationCancelledError
    from .remote_provider import RemoteProviderError, get_api_key_url, is_valid_remote_model, list_available_models
    from .translator_engine import TranslationEngine
    from .update_checker import UpdateCheckWorker
    from .ui_i18n import UI_LANGUAGE_OPTIONS, detect_ui_language, performance_label, tr


class SettingsDialog(QDialog):
    def __init__(
        self,
        performance_mode: str,
        ui_language: str,
        receive_beta_updates: bool,
        translation_provider: str,
        api_keys: dict[str, str],
        selected_models: dict[str, str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.ui_language = ui_language
        self.api_keys = dict(api_keys)
        self.provider_models = dict(selected_models)
        self._displayed_provider = translation_provider
        self._preferred_remote_provider = translation_provider if translation_provider != 'local' else 'openai'
        self._updating_provider_section = False
        self._initializing = True
        self.setWindowTitle(tr(ui_language, 'settings_title'))
        self.setModal(True)
        self.resize(680, 640)
        self.setMinimumSize(620, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area, 1)

        content = QWidget()
        scroll_area.setWidget(content)

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        interface_card, interface_layout = self._make_settings_section(
            tr(ui_language, 'settings_interface_section'),
        )
        content_layout.addWidget(interface_card)

        self.ui_language_combo = QComboBox()
        for code, label in UI_LANGUAGE_OPTIONS:
            self.ui_language_combo.addItem(label, code)
        combo_index = self.ui_language_combo.findData(ui_language)
        if combo_index >= 0:
            self.ui_language_combo.setCurrentIndex(combo_index)
        interface_layout.addWidget(self.ui_language_combo)

        updates_card, updates_layout = self._make_settings_section(
            tr(ui_language, 'settings_updates_section'),
        )
        content_layout.addWidget(updates_card)

        self.receive_beta_updates_checkbox = QCheckBox(tr(ui_language, 'settings_receive_beta_updates'))
        self.receive_beta_updates_checkbox.setChecked(receive_beta_updates)
        updates_layout.addWidget(self.receive_beta_updates_checkbox)

        updates_help_label = QLabel(tr(ui_language, 'settings_receive_beta_updates_help'))
        updates_help_label.setWordWrap(True)
        updates_help_label.setObjectName('infoLabel')
        updates_help_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        updates_layout.addWidget(updates_help_label)

        translation_card, translation_layout = self._make_settings_section(
            tr(ui_language, 'settings_translation_section'),
            tr(ui_language, 'settings_translation_section_help'),
        )
        content_layout.addWidget(translation_card)

        mode_title = QLabel(tr(ui_language, 'settings_translation_provider'))
        mode_title.setProperty('fieldLabel', True)
        translation_layout.addWidget(mode_title)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(tr(ui_language, 'translation_provider_local'), 'local')
        self.mode_combo.addItem('API', 'api')
        self.mode_combo.setCurrentIndex(0 if translation_provider == 'local' else 1)
        self.mode_combo.currentIndexChanged.connect(self._handle_mode_changed)
        translation_layout.addWidget(self.mode_combo)

        self.performance_section = QWidget()
        performance_layout = QVBoxLayout(self.performance_section)
        performance_layout.setContentsMargins(6, 4, 6, 4)
        performance_layout.setSpacing(10)

        title = QLabel(tr(ui_language, 'settings_performance'))
        title.setProperty('fieldLabel', True)
        performance_layout.addWidget(title)

        self.performance_combo = QComboBox()
        for code, _ in (
            ('suave', ''),
            ('equilibrado', ''),
            ('rapido', ''),
            ('maximo', ''),
        ):
            self.performance_combo.addItem(performance_label(ui_language, code), code)
        combo_index = self.performance_combo.findData(performance_mode)
        if combo_index >= 0:
            self.performance_combo.setCurrentIndex(combo_index)
        performance_layout.addWidget(self.performance_combo)

        performance_help_label = QLabel(tr(ui_language, 'settings_help'))
        performance_help_label.setWordWrap(True)
        performance_help_label.setObjectName('infoLabel')
        performance_help_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        performance_layout.addWidget(performance_help_label)
        translation_layout.addWidget(self.performance_section)

        self.remote_section = QWidget()
        remote_layout = QVBoxLayout(self.remote_section)
        remote_layout.setContentsMargins(6, 4, 6, 4)
        remote_layout.setSpacing(10)

        provider_title = QLabel(tr(ui_language, 'settings_api_provider'))
        provider_title.setProperty('fieldLabel', True)
        remote_layout.addWidget(provider_title)

        self.provider_combo = QComboBox()
        for code, _label in TRANSLATION_PROVIDER_OPTIONS:
            if code == 'local':
                continue
            self.provider_combo.addItem(tr(ui_language, f'translation_provider_{code}'), code)
        provider_index = self.provider_combo.findData(self._preferred_remote_provider)
        if provider_index >= 0:
            self.provider_combo.setCurrentIndex(provider_index)
        self.provider_combo.currentIndexChanged.connect(self._handle_provider_changed)
        remote_layout.addWidget(self.provider_combo)

        self.provider_help_label = QLabel()
        self.provider_help_label.setWordWrap(True)
        self.provider_help_label.setObjectName('infoLabel')
        remote_layout.addWidget(self.provider_help_label)

        api_key_title = QLabel(tr(ui_language, 'settings_api_key'))
        api_key_title.setProperty('fieldLabel', True)
        remote_layout.addWidget(api_key_title)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.api_key_edit.textEdited.connect(self._persist_current_provider_inputs)
        self.api_key_edit.textChanged.connect(self._handle_api_key_text_changed)
        api_key_row_widget = QWidget()
        api_key_row = QHBoxLayout(api_key_row_widget)
        api_key_row.setContentsMargins(0, 0, 0, 0)
        api_key_row.setSpacing(10)
        api_key_row.addWidget(self.api_key_edit, 1)
        self.clear_api_key_button = QPushButton(tr(ui_language, 'clear_api_key'))
        self.clear_api_key_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.clear_api_key_button.clicked.connect(self._clear_current_provider_api_key)
        api_key_row.addWidget(self.clear_api_key_button)
        remote_layout.addWidget(api_key_row_widget)

        self.api_key_url_label = QLabel()
        self.api_key_url_label.setOpenExternalLinks(True)
        self.api_key_url_label.setWordWrap(True)
        self.api_key_url_label.setObjectName('infoLabel')
        remote_layout.addWidget(self.api_key_url_label)

        self.api_key_status_label = QLabel()
        self.api_key_status_label.setWordWrap(True)
        self.api_key_status_label.setObjectName('infoLabel')
        remote_layout.addWidget(self.api_key_status_label)

        model_title = QLabel(tr(ui_language, 'settings_remote_model'))
        model_title.setProperty('fieldLabel', True)
        remote_layout.addWidget(model_title)

        model_row_widget = QWidget()
        model_row = QHBoxLayout(model_row_widget)
        model_row.setContentsMargins(0, 0, 0, 0)
        model_row.setSpacing(10)
        self.model_combo = QComboBox()
        self.model_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.model_combo.currentIndexChanged.connect(self._persist_current_provider_inputs)
        self.model_combo.currentIndexChanged.connect(self._refresh_provider_status_labels)
        model_row.addWidget(self.model_combo, 1)
        self.refresh_models_button = QPushButton(tr(ui_language, 'refresh_models'))
        self.refresh_models_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.refresh_models_button.clicked.connect(self._refresh_remote_models)
        model_row.addWidget(self.refresh_models_button)
        remote_layout.addWidget(model_row_widget)

        self.model_help_label = QLabel(tr(ui_language, 'settings_model_help'))
        self.model_help_label.setWordWrap(True)
        self.model_help_label.setObjectName('infoLabel')
        remote_layout.addWidget(self.model_help_label)

        self.model_status_label = QLabel()
        self.model_status_label.setWordWrap(True)
        self.model_status_label.setObjectName('infoLabel')
        remote_layout.addWidget(self.model_status_label)
        translation_layout.addWidget(self.remote_section)

        content_layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.Ok)
        cancel_button = buttons.button(QDialogButtonBox.Cancel)
        if ok_button is not None:
            ok_button.setText(tr(ui_language, 'ok_button'))
        if cancel_button is not None:
            cancel_button.setText(tr(ui_language, 'cancel_button'))
        buttons.setCenterButtons(False)
        layout.addWidget(buttons)

        self._update_provider_section()
        self._initializing = False

    def _make_settings_section(self, title: str, description: str | None = None) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setProperty('card', True)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName('sectionTitle')
        layout.addWidget(title_label)

        if description:
            description_label = QLabel(description)
            description_label.setObjectName('infoLabel')
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        return card, layout

    def selected_performance_mode(self) -> str:
        return str(self.performance_combo.currentData())

    def selected_ui_language(self) -> str:
        return str(self.ui_language_combo.currentData())

    def selected_receive_beta_updates(self) -> bool:
        return self.receive_beta_updates_checkbox.isChecked()

    def selected_translation_provider(self) -> str:
        if str(self.mode_combo.currentData()) == 'local':
            return 'local'
        return str(self.provider_combo.currentData())

    def selected_api_keys(self) -> dict[str, str]:
        self._persist_provider_inputs(self._displayed_provider)
        return dict(self.api_keys)

    def selected_models(self) -> dict[str, str]:
        self._persist_provider_inputs(self._displayed_provider)
        return dict(self.provider_models)

    @staticmethod
    def _normalized_remote_model(provider: str, model_id: str) -> str:
        if provider not in {'openai', 'gemini', 'anthropic', 'deepseek'}:
            return ''
        normalized = str(model_id or '').strip()
        if not normalized:
            return ''
        return normalized if is_valid_remote_model(provider, normalized) else ''

    def _handle_provider_changed(self) -> None:
        self._persist_provider_inputs(self._displayed_provider)
        self._preferred_remote_provider = str(self.provider_combo.currentData())
        self._displayed_provider = self._preferred_remote_provider
        self._update_provider_section()

    def _handle_mode_changed(self) -> None:
        self._persist_provider_inputs(self._displayed_provider)
        if str(self.mode_combo.currentData()) == 'local':
            self._displayed_provider = 'local'
        else:
            self._displayed_provider = str(self.provider_combo.currentData())
            self._preferred_remote_provider = self._displayed_provider
        self._update_provider_section()

    def _update_provider_section(self) -> None:
        if self._updating_provider_section:
            return
        self._updating_provider_section = True
        provider = self.selected_translation_provider()
        try:
            provider_is_local = provider == 'local'
            self.performance_section.setVisible(provider_is_local)
            self.remote_section.setVisible(not provider_is_local)
            self.performance_combo.setEnabled(provider_is_local)
            self.provider_help_label.setText(tr(self.ui_language, 'settings_provider_help_remote'))
            self.api_key_edit.setEnabled(not provider_is_local)
            current_api_key = self.api_keys.get(provider, '')
            has_api_key = bool(current_api_key.strip())
            self.clear_api_key_button.setEnabled(not provider_is_local and has_api_key)
            self.model_combo.setEnabled(not provider_is_local and has_api_key)
            self.refresh_models_button.setEnabled(not provider_is_local and has_api_key)
            self.api_key_edit.blockSignals(True)
            self.api_key_edit.setPlaceholderText(
                '' if provider_is_local or current_api_key else tr(self.ui_language, 'settings_api_key_placeholder')
            )
            self.api_key_edit.setText(current_api_key)
            self.api_key_edit.blockSignals(False)
            self._populate_model_combo()
            key_url = get_api_key_url(provider)
            if key_url:
                self.api_key_url_label.setText(
                    tr(
                        self.ui_language,
                        'settings_api_key_url',
                        url=key_url,
                    )
                )
            else:
                self.api_key_url_label.setText(tr(self.ui_language, 'settings_local_provider_note'))
            self._refresh_provider_status_labels()
        finally:
            self._updating_provider_section = False

    def _populate_model_combo(self, models=None) -> None:
        provider = self.selected_translation_provider()
        selected_model = self._normalized_remote_model(provider, self.provider_models.get(provider, ''))
        self.provider_models[provider] = selected_model
        available_models = models if models is not None else []

        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        if provider == 'local':
            self.model_combo.addItem(tr(self.ui_language, 'settings_model_not_required'), '')
        elif available_models:
            for item in available_models:
                self.model_combo.addItem(item.label, item.model_id)
        elif selected_model:
            self.model_combo.addItem(selected_model, selected_model)
        else:
            self.model_combo.addItem(tr(self.ui_language, 'settings_model_fetch_required'), '')

        combo_index = self.model_combo.findData(selected_model)
        if combo_index < 0 and self.model_combo.count():
            combo_index = 0
        if combo_index >= 0:
            self.model_combo.setCurrentIndex(combo_index)
        self.model_combo.blockSignals(False)
        self._persist_provider_inputs(provider)

    def _refresh_remote_models(self) -> None:
        provider = self.selected_translation_provider()
        if provider == 'local':
            return

        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, tr(self.ui_language, 'app_title'), tr(self.ui_language, 'api_key_required_for_models'))
            return

        try:
            models = list_available_models(provider, api_key)
        except RemoteProviderError as error:
            QMessageBox.warning(self, tr(self.ui_language, 'app_title'), str(error))
            return

        self._populate_model_combo(models)

    def _clear_current_provider_api_key(self) -> None:
        provider = self.selected_translation_provider()
        if provider not in {'openai', 'gemini', 'anthropic', 'deepseek'}:
            return
        self.api_keys[provider] = ''
        self.provider_models[provider] = ''
        parent = self.parent()
        if parent is not None:
            if hasattr(parent, 'provider_api_keys'):
                parent.provider_api_keys[provider] = ''
            if hasattr(parent, 'provider_models'):
                parent.provider_models[provider] = ''
            settings = getattr(parent, 'settings', None)
            if settings is not None:
                settings.setValue(f'api_key_{provider}', '')
                settings.setValue(f'model_{provider}', '')
                settings.sync()
        self.api_key_edit.clear()
        self._populate_model_combo([])

    def _persist_current_provider_inputs(self) -> None:
        self._persist_provider_inputs(self._displayed_provider)

    def _persist_provider_inputs(self, provider: str) -> None:
        if self._initializing or self._updating_provider_section:
            return
        if provider not in {'openai', 'gemini', 'anthropic', 'deepseek'}:
            return
        self.api_keys[provider] = self.api_key_edit.text().strip()
        self.provider_models[provider] = self._normalized_remote_model(provider, str(self.model_combo.currentData() or ''))

    def _handle_api_key_text_changed(self) -> None:
        self._persist_current_provider_inputs()
        self._refresh_provider_status_labels()

    def _refresh_provider_status_labels(self) -> None:
        provider = self.selected_translation_provider()
        provider_is_local = provider == 'local'
        current_api_key = self.api_keys.get(provider, '')
        has_api_key = bool(current_api_key.strip())
        self.clear_api_key_button.setEnabled(not provider_is_local and has_api_key)
        self.model_combo.setEnabled(not provider_is_local and has_api_key)
        self.refresh_models_button.setEnabled(not provider_is_local and has_api_key)
        if provider_is_local:
            self.api_key_status_label.setText('')
        elif current_api_key:
            self.api_key_status_label.setText(tr(self.ui_language, 'settings_api_key_saved'))
        else:
            self.api_key_status_label.setText(tr(self.ui_language, 'settings_api_key_missing_notice'))

        current_model = self.provider_models.get(provider, '')
        if provider_is_local:
            self.model_status_label.setText('')
        elif current_model:
            self.model_status_label.setText(tr(self.ui_language, 'settings_model_saved', model=current_model))
        else:
            self.model_status_label.setText(tr(self.ui_language, 'settings_model_missing_notice'))


class AboutDialog(QDialog):
    def __init__(self, ui_language: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr(ui_language, 'about_title'))
        self.resize(620, 520)
        self.setMinimumSize(560, 460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        license_path = Path(__file__).resolve().parents[2] / 'LICENSE'
        license_text = license_path.read_text(encoding='utf-8').strip() if license_path.exists() else PROJECT_LICENSE_NAME

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(
            f'''
            <h2>{tr(ui_language, 'app_title')} {__version__}</h2>
            <div style="margin: 10px 0 18px; padding: 12px 14px; border: 1px solid #cfd8dc; border-radius: 8px; background: #f6f8fa;">
                <p><strong>{tr(ui_language, 'about_independence_title')}</strong></p>
                <p>{tr(ui_language, 'about_independence_body')}</p>
            </div>
            <p><strong>{tr(ui_language, 'about_author')}:</strong> {PROJECT_AUTHOR}</p>
            <p><strong>{tr(ui_language, 'about_license')}:</strong> {PROJECT_LICENSE_NAME}</p>
            <p>{tr(ui_language, 'about_license_body')}</p>
            <pre>{html.escape(license_text)}</pre>
            <h3>{tr(ui_language, 'about_versions')}</h3>
            <p><a href="{PROJECT_REPOSITORY_URL}">{tr(ui_language, 'about_repo_link')}</a></p>
            <p><a href="{PROJECT_RELEASES_URL}">{tr(ui_language, 'about_releases_link')}</a></p>
            <p><a href="{PROJECT_ISSUES_URL}">{tr(ui_language, 'about_issues_link')}</a></p>
            <h3>{tr(ui_language, 'about_credits')}</h3>
            <p>{tr(ui_language, 'about_credits_body')}</p>
            <h4>{tr(ui_language, 'about_models_title')}</h4>
            <p>{tr(ui_language, 'about_models_body')}</p>
            <h4>{tr(ui_language, 'about_tech_title')}</h4>
            <p>{tr(ui_language, 'about_tech_body')}</p>
            ''',
        )
        layout.addWidget(browser, 1)

        close_button = QPushButton(tr(ui_language, 'close_button'))
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignRight)


class HelpDialog(QDialog):
    def __init__(self, ui_language: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr(ui_language, 'help_title'))
        self.resize(680, 560)
        self.setMinimumSize(620, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(
            f'''
            <h2>{tr(ui_language, 'help_title')}</h2>
            <p>{tr(ui_language, 'help_intro')}</p>
            <h3>{tr(ui_language, 'help_how_title')}</h3>
            <p>{tr(ui_language, 'help_how_body')}</p>
            <h3>{tr(ui_language, 'help_ai_title')}</h3>
            <p>{tr(ui_language, 'help_ai_body')}</p>
            <h3>{tr(ui_language, 'help_privacy_title')}</h3>
            <p>{tr(ui_language, 'help_privacy_body')}</p>
            <h3>{tr(ui_language, 'help_api_mode_title')}</h3>
            <p>{tr(ui_language, 'help_api_mode_body')}</p>
            <h3>{tr(ui_language, 'help_support_title')}</h3>
            <p>{tr(ui_language, 'help_support_body')}</p>
            <p><a href="{PROJECT_ISSUES_URL}">{tr(ui_language, 'about_issues_link')}</a></p>
            ''',
        )
        layout.addWidget(browser, 1)

        close_button = QPushButton(tr(ui_language, 'close_button'))
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignRight)


class TranslationWorker(QObject):
    progress = Signal(object)
    finished = Signal()

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        source_language: str,
        target_language: str,
        performance_mode: str,
        ui_language: str,
        translation_provider: str,
        remote_model_id: str,
        remote_api_key: str,
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.source_language = source_language
        self.target_language = target_language
        self.performance_mode = performance_mode
        self.ui_language = ui_language
        self.translation_provider = translation_provider
        self.remote_model_id = remote_model_id
        self.remote_api_key = remote_api_key
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def is_cancel_requested(self) -> bool:
        return self._cancel_requested

    @Slot()
    def run(self) -> None:
        start_time = time.time()
        _append_runtime_log(
            'Worker run: start '
            f'provider={self.translation_provider} model={self.remote_model_id or "-"} '
            f'source={self.source_language} target={self.target_language} input={self.input_path}',
        )
        service = ElpxTranslationService(
            engine=TranslationEngine(
                performance_mode=self.performance_mode,
                ui_language=self.ui_language,
                translation_provider=self.translation_provider,
                remote_model_id=self.remote_model_id,
                remote_api_key=self.remote_api_key,
            ),
        )
        try:
            _append_runtime_log('Worker run: service.translate_file enter')
            service.translate_file(
                self.input_path,
                self.output_path,
                TranslationOptions(
                    source_language=self.source_language,
                    target_language=self.target_language,
                    ui_language=self.ui_language,
                    should_cancel=self.is_cancel_requested,
                ),
                self.progress.emit,
            )
            elapsed = int(time.time() - start_time)
            _append_runtime_log(f'Worker run: success output={self.output_path}')
            self.progress.emit(
                ProgressEvent(
                    tr(
                        self.ui_language,
                        'translation_finished',
                        elapsed=MainWindow.format_elapsed_summary(elapsed),
                        output_path=self.output_path,
                    ),
                    state='done',
                    progress_percent=100,
                ),
            )
        except TranslationCancelledError as error:
            elapsed = int(time.time() - start_time)
            if self.output_path.exists():
                self.output_path.unlink(missing_ok=True)
            _append_runtime_log(f'Worker run: cancelled error={error}')
            suffix = (
                tr(self.ui_language, 'after_elapsed', elapsed=MainWindow.format_elapsed_summary(elapsed))
                if elapsed
                else ''
            )
            self.progress.emit(ProgressEvent(f'{error}{suffix}', state='cancelled'))
        except Exception as error:  # noqa: BLE001
            elapsed = int(time.time() - start_time)
            _append_runtime_log(f'Worker run: error {error.__class__.__name__}: {error}')
            suffix = (
                tr(self.ui_language, 'after_elapsed', elapsed=MainWindow.format_elapsed_summary(elapsed))
                if elapsed
                else ''
            )
            self.progress.emit(ProgressEvent(f'{error}{suffix}', state='error'))
        finally:
            _append_runtime_log('Worker run: finished signal emit')
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.start_time = 0.0
        self.last_eta_update = 0.0
        self.last_eta_seconds: int | None = None
        self.completed_units = 0
        self.total_units = 0
        self.progress_value = 0.0
        self.running = False
        self.thread: QThread | None = None
        self.worker: TranslationWorker | None = None
        self.update_worker: UpdateCheckWorker | None = None
        self.update_check_pending = False
        self.closing = False
        self.log_entries: list[str] = []
        self.transient_message = ''
        self.cancel_requested = False
        self.latest_version: str | None = None
        self.latest_version_url: str | None = None
        self.settings = _migrate_legacy_settings_if_needed()
        self.ui_language = self._load_ui_language()
        self.performance_mode = self._load_performance_mode()
        self.translation_provider = self._load_translation_provider()
        self.provider_api_keys = self._load_provider_api_keys()
        self.provider_models = self._load_provider_models()
        for provider, model_id in list(self.provider_models.items()):
            self.provider_models[provider] = SettingsDialog._normalized_remote_model(provider, model_id)
        self.last_directory = self._load_last_directory()
        self.preferred_target_language = self._load_target_language()
        self.receive_beta_updates = self._load_receive_beta_updates()
        self.detected_project_language: str | None = None
        self.auto_detected_source_language_active = False
        self.current_status = 'waiting'

        self._build_ui()
        self._apply_styles()
        self._apply_ui_texts()
        self._refresh_settings_summary()
        self.adjustSize()
        self.resize(max(self.width(), 980), self.height())
        self._start_update_check()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_timers)
        self.timer.start()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(8)

        header_card = self._make_card()
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_layout.setSpacing(10)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        self.title_label = QLabel('')
        self.title_label.setObjectName('titleLabel')
        title_layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.version_label = QLabel('')
        self.version_label.setObjectName('infoLabel')
        title_layout.addWidget(self.version_label, 0, Qt.AlignmentFlag.AlignVCenter)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.settings_button = QPushButton('')
        self.settings_button.setObjectName('headerActionButton')
        self.settings_button.setFixedHeight(40)
        self.settings_button.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_button)
        header_layout.setAlignment(self.settings_button, Qt.AlignmentFlag.AlignVCenter)

        self.website_button = QPushButton('')
        self.website_button.setObjectName('headerActionButton')
        self.website_button.setFixedHeight(40)
        self.website_button.clicked.connect(self._open_project_website)
        header_layout.addWidget(self.website_button)
        header_layout.setAlignment(self.website_button, Qt.AlignmentFlag.AlignVCenter)

        self.about_button = QPushButton('')
        self.about_button.setObjectName('headerActionButton')
        self.about_button.setFixedHeight(40)
        self.about_button.clicked.connect(self._open_about_dialog)
        header_layout.addWidget(self.about_button)
        header_layout.setAlignment(self.about_button, Qt.AlignmentFlag.AlignVCenter)

        root_layout.addWidget(header_card)

        self.update_banner = QLabel('')
        self.update_banner.setObjectName('infoLabel')
        self.update_banner.setOpenExternalLinks(True)
        self.update_banner.setWordWrap(True)
        self.update_banner.hide()
        root_layout.addWidget(self.update_banner)

        self.context_card = self._make_card()
        context_layout = QHBoxLayout(self.context_card)
        context_layout.setContentsMargins(14, 12, 14, 12)
        context_layout.setSpacing(10)

        context_text_layout = QVBoxLayout()
        context_text_layout.setContentsMargins(0, 0, 0, 0)
        context_text_layout.setSpacing(4)

        self.settings_summary_label = QLabel('')
        self.settings_summary_label.setObjectName('infoLabel')
        self.settings_summary_label.setWordWrap(True)
        context_text_layout.addWidget(self.settings_summary_label)

        self.active_model_label = QLabel('')
        self.active_model_label.setObjectName('infoLabel')
        self.active_model_label.setWordWrap(True)
        context_text_layout.addWidget(self.active_model_label)

        context_layout.addLayout(context_text_layout, 1)

        context_actions_layout = QHBoxLayout()
        context_actions_layout.setContentsMargins(0, 0, 0, 0)
        context_actions_layout.setSpacing(6)

        self.quick_settings_button = QPushButton('')
        self.quick_settings_button.setObjectName('subtleButton')
        self.quick_settings_button.clicked.connect(self._open_settings)
        self.quick_settings_button.setFixedHeight(30)
        context_actions_layout.addWidget(self.quick_settings_button, 0, Qt.AlignmentFlag.AlignVCenter)

        context_layout.addLayout(context_actions_layout, 0)
        root_layout.addWidget(self.context_card)

        controls_card = self._make_card()
        controls_layout = QGridLayout(controls_card)
        controls_layout.setContentsMargins(16, 14, 16, 14)
        controls_layout.setHorizontalSpacing(8)
        controls_layout.setVerticalSpacing(8)

        self.file_label = self._make_field_label('')
        controls_layout.addWidget(self.file_label, 0, 0)
        self.file_edit = QLineEdit()
        controls_layout.addWidget(self.file_edit, 1, 0, 1, 3)
        self.open_button = QPushButton('')
        self.open_button.clicked.connect(self._choose_file)
        controls_layout.addWidget(self.open_button, 1, 3)

        self.output_label = self._make_field_label('')
        controls_layout.addWidget(self.output_label, 2, 0)
        self.output_edit = QLineEdit()
        controls_layout.addWidget(self.output_edit, 3, 0, 1, 3)
        self.save_button = QPushButton('')
        self.save_button.clicked.connect(self._choose_output)
        controls_layout.addWidget(self.save_button, 3, 3)

        self.source_label = self._make_field_label('')
        self.target_label = self._make_field_label('')
        controls_layout.addWidget(self.source_label, 4, 0)
        controls_layout.addWidget(self.target_label, 4, 1)

        self.origin_combo = QComboBox()
        self.target_combo = QComboBox()
        self.custom_target_label = self._make_field_label('')
        self.custom_target_edit = QLineEdit()
        self.custom_target_edit.setMaximumWidth(220)
        self.custom_target_edit.textEdited.connect(self._handle_custom_target_text_changed)
        self.language_labels = {code: label for code, label in LANGUAGE_OPTIONS}
        self._rebuild_language_combos(self._default_source_language(), self.preferred_target_language)
        self.origin_combo.currentIndexChanged.connect(self._handle_source_language_changed)
        self.target_combo.currentIndexChanged.connect(self._sync_output_path_with_target_language)
        self.target_combo.currentIndexChanged.connect(self._persist_target_language)
        self.target_combo.currentIndexChanged.connect(self._toggle_custom_target_visibility)
        self.target_combo.currentIndexChanged.connect(self._sync_language_pairs)
        controls_layout.addWidget(self.origin_combo, 5, 0)
        controls_layout.addWidget(self.target_combo, 5, 1)
        controls_layout.addWidget(self.custom_target_label, 6, 0)
        controls_layout.addWidget(self.custom_target_edit, 6, 1)

        self.translate_button = QPushButton('')
        self.translate_button.setObjectName('primaryButton')
        self.translate_button.clicked.connect(self._start_translation)
        controls_layout.addWidget(self.translate_button, 5, 2)

        self.stop_button = QPushButton('')
        self.stop_button.clicked.connect(self._cancel_translation)
        self.stop_button.setEnabled(False)
        self.stop_button.setVisible(False)
        controls_layout.addWidget(self.stop_button, 5, 3)

        controls_layout.setColumnStretch(0, 1)
        controls_layout.setColumnStretch(1, 1)
        controls_layout.setColumnStretch(2, 1)
        root_layout.addWidget(controls_card)

        self.progress_card = self._make_card()
        stats_layout = QVBoxLayout(self.progress_card)
        stats_layout.setContentsMargins(16, 14, 16, 14)
        stats_layout.setSpacing(8)

        self.current_message_label = QLabel('')
        self.current_message_label.setObjectName('messageLabel')
        self.current_message_label.setWordWrap(True)
        stats_layout.addWidget(self.current_message_label)

        self.elapsed_label = QLabel('')
        self.elapsed_label.setObjectName('infoLabel')
        stats_layout.addWidget(self.elapsed_label)

        self.eta_label = QLabel('')
        self.eta_label.setObjectName('infoLabel')
        stats_layout.addWidget(self.eta_label)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName('progressBar')
        progress_row.addWidget(self.progress_bar, 1)

        self.progress_percent_label = QLabel('0%')
        self.progress_percent_label.setObjectName('percentLabel')
        progress_row.addWidget(self.progress_percent_label)
        stats_layout.addLayout(progress_row)

        self.progress_card.hide()
        root_layout.addWidget(self.progress_card)

        self.log_card = self._make_card()
        log_layout = QVBoxLayout(self.log_card)
        log_layout.setContentsMargins(16, 14, 16, 14)
        log_layout.setSpacing(6)

        self.log_title = self._make_field_label('')
        log_layout.addWidget(self.log_title)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.log_view.setObjectName('logView')
        self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mono_font = QFont('IBM Plex Mono', 10)
        if mono_font.family() == '':
            mono_font = QFont('Courier New', 10)
        self.log_view.setFont(mono_font)
        self.log_view.setMinimumHeight(130)
        log_layout.addWidget(self.log_view, 1)

        self.log_card.hide()
        root_layout.addWidget(self.log_card)
        root_layout.addStretch()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            '''
            QWidget {
                background: #f6f3ee;
                color: #16212b;
                font-family: "Segoe UI", "Noto Sans", sans-serif;
                font-size: 14px;
            }
            QFrame[card="true"] {
                background: #fffdf9;
                border: 1px solid #e8e1d6;
                border-radius: 14px;
            }
            QLabel {
                background: transparent;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: 700;
                color: #16212b;
            }
            QLabel#sectionTitle {
                color: #175d98;
                background: #eef5fb;
                border: 1px solid #d7e5f2;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 700;
                padding: 8px 10px;
                margin-bottom: 2px;
            }
            QLabel#infoLabel {
                color: #5f6b76;
                font-family: "IBM Plex Mono", "Courier New", monospace;
                font-size: 12px;
                padding: 0;
            }
            QLabel#percentLabel {
                color: #1d6c54;
                font-family: "IBM Plex Mono", "Courier New", monospace;
                font-size: 12px;
                font-weight: 700;
                min-width: 42px;
            }
            QLabel#messageLabel {
                color: #16212b;
                font-size: 14px;
                padding-left: 0;
            }
            QLabel[fieldLabel="true"] {
                font-size: 12px;
                font-weight: 700;
                color: #175d98;
                padding-top: 2px;
            }
            QLineEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #ddd4c8;
                border-radius: 10px;
                padding: 8px 10px;
                min-height: 18px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #1f9d84;
            }
            QPushButton {
                background: #ffffff;
                border: 1px solid #ddd4c8;
                border-radius: 10px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton#headerActionButton {
                background: #fcfaf6;
                border: 1px solid #ddd4c8;
                border-radius: 12px;
                padding: 0 12px;
                min-height: 40px;
                max-height: 40px;
                color: #30404c;
                font-weight: 600;
            }
            QPushButton:hover {
                border: 1px solid #1f9d84;
            }
            QPushButton#headerActionButton:hover {
                border: 1px solid #1f9d84;
                background: #f5fbf8;
                color: #1d6c54;
            }
            QPushButton#primaryButton {
                background: #1f9d84;
                color: #ffffff;
                border: 1px solid #1f9d84;
            }
            QPushButton#subtleButton {
                padding: 0 10px;
                min-height: 30px;
                max-height: 30px;
                color: #30404c;
                border-radius: 9px;
            }
            QPushButton#primaryButton:hover {
                background: #17816c;
                border: 1px solid #17816c;
            }
            QPushButton:disabled {
                background: #ebe6dd;
                color: #887f73;
                border: 1px solid #e0d8cd;
            }
            QProgressBar {
                background: #ece5da;
                border: none;
                border-radius: 8px;
                min-height: 12px;
            }
            QProgressBar::chunk {
                background: #1f9d84;
                border-radius: 8px;
            }
            QPlainTextEdit#logView {
                background: #131920;
                color: #d8f5e8;
                border: none;
                border-radius: 12px;
                padding: 8px;
            }
            '''
        )

    @staticmethod
    def _make_card() -> QFrame:
        card = QFrame()
        card.setProperty('card', True)
        return card

    @staticmethod
    def _make_field_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty('fieldLabel', True)
        return label

    def _choose_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            tr(self.ui_language, 'select_file_dialog'),
            str(self.last_directory),
            tr(self.ui_language, 'elpx_files'),
        )
        if not filename:
            return

        input_path = Path(filename)
        self.file_edit.setText(str(input_path))
        self.last_directory = input_path.parent
        self._persist_last_directory()
        suggested_output = self._build_output_path(input_path)
        self.output_edit.setText(str(suggested_output))
        self._apply_detected_source_language(input_path)
        self.output_edit.setText(str(self._build_output_path(input_path)))

    def _choose_output(self) -> None:
        current_file = self.file_edit.text().strip()
        if current_file:
            input_path = Path(current_file)
            suggested_output = self._build_output_path(input_path)
        else:
            target_language = self.target_combo.currentData() or 'xx'
            suggested_output = self.last_directory / f'{tr(self.ui_language, "default_output_basename")}-{target_language}.elpx'

        filename, _ = QFileDialog.getSaveFileName(
            self,
            tr(self.ui_language, 'save_file_dialog'),
            str(suggested_output),
            tr(self.ui_language, 'elpx_files'),
        )
        if not filename:
            return

        self.output_edit.setText(filename)
        self.last_directory = Path(filename).parent
        self._persist_last_directory()

    def _start_translation(self) -> None:
        if self.running:
            return

        input_path = Path(self.file_edit.text().strip())
        if not input_path.exists():
            self._show_error(tr(self.ui_language, 'invalid_input_file'))
            return

        source_language = self._selected_source_language()
        target_language = self._selected_target_language()
        if self.translation_provider == 'local' and source_language not in SUPPORTED_LANGUAGE_CODES:
            self._show_error(tr(self.ui_language, 'local_mode_source_requires_api', language=source_language))
            return
        if source_language == target_language:
            self._show_error(tr(self.ui_language, 'same_languages_error'))
            return
        if self._is_custom_target_selected() and not self._is_valid_custom_target_language(target_language):
            self._show_error(tr(self.ui_language, 'custom_target_language_invalid'))
            return
        if self.detected_project_language and source_language != self.detected_project_language:
            detected_label = self.language_labels.get(self.detected_project_language, self.detected_project_language)
            selected_label = self.language_labels.get(source_language, source_language)
            self._show_error(
                tr(
                    self.ui_language,
                    'source_language_mismatch_warning',
                    detected_language=f'{self.detected_project_language} · {detected_label}',
                    selected_language=f'{source_language} · {selected_label}',
                )
            )
            return

        remote_api_key = self.provider_api_keys.get(self.translation_provider, '').strip()
        remote_model_id = self.provider_models.get(self.translation_provider, '').strip()
        if self.translation_provider != 'local':
            if not remote_api_key:
                self._show_error(tr(self.ui_language, 'remote_api_key_missing'))
                return
            if not remote_model_id:
                self._show_error(tr(self.ui_language, 'remote_model_missing'))
                return

        output_text = self.output_edit.text().strip()
        if output_text:
            output_path = Path(output_text)
        else:
            output_path = self._build_output_path(input_path)
            self.output_edit.setText(str(output_path))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._reset_run_state()
        self._set_running(True)
        _append_runtime_log(
            'Start translation: '
            f'provider={self.translation_provider} model={remote_model_id or "-"} '
            f'source={source_language} target={target_language} input={input_path} output={output_path}',
        )
        self._append_log(ProgressEvent(tr(self.ui_language, 'preparing_translation')))

        self.thread = QThread(self)
        self.worker = TranslationWorker(
            input_path=input_path,
            output_path=output_path,
            source_language=source_language,
            target_language=target_language,
            performance_mode=self.performance_mode,
            ui_language=self.ui_language,
            translation_provider=self.translation_provider,
            remote_model_id=remote_model_id,
            remote_api_key=remote_api_key,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._handle_progress)
        self.worker.finished.connect(self._handle_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _set_running(self, running: bool) -> None:
        self.running = running
        self.translate_button.setEnabled(not running)
        self.stop_button.setVisible(running)
        self.stop_button.setEnabled(running and not self.cancel_requested)

    def _reset_run_state(self) -> None:
        self.start_time = time.time()
        self.last_eta_update = 0.0
        self.last_eta_seconds = None
        self.completed_units = 0
        self.total_units = 0
        self.progress_value = 0.0
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText('0%')
        self.log_entries.clear()
        self.transient_message = ''
        self.cancel_requested = False
        self.log_view.setPlainText('')
        self.progress_card.show()
        self.log_card.show()
        self._set_status('working')
        self.current_message_label.setText(tr(self.ui_language, 'preparing_translation'))
        self.active_model_label.setText(tr(self.ui_language, 'active_model', model_label='-'))
        self.elapsed_label.setText(tr(self.ui_language, 'elapsed_time', value='00:00'))
        self.eta_label.setText(tr(self.ui_language, 'eta', value='--:--'))

    @Slot(object)
    def _handle_progress(self, event: object) -> None:
        assert isinstance(event, ProgressEvent)
        self._append_log(event)

    @Slot()
    def _handle_finished(self) -> None:
        self._set_running(False)
        self.thread = None
        self.worker = None

    def _append_log(self, event: ProgressEvent) -> None:
        self._set_status(event.state)
        self.current_message_label.setText(event.message)
        if event.active_model_label is not None:
            self.active_model_label.setText(tr(self.ui_language, 'active_model', model_label=event.active_model_label))
        if event.state == 'done':
            self.last_eta_seconds = 0
            self.eta_label.setText(tr(self.ui_language, 'eta', value=tr(self.ui_language, 'finished_eta')))
        elif event.state in {'error', 'cancelled'}:
            self.last_eta_seconds = None
            self.eta_label.setText(tr(self.ui_language, 'eta', value='--:--'))

        if event.progress_percent is not None:
            self.progress_value = max(0.0, min(100.0, event.progress_percent))
            self.progress_bar.setValue(round(self.progress_value))
            self.progress_percent_label.setText(f'{round(self.progress_value)}%')

        if event.completed_units is not None:
            self.completed_units = event.completed_units

        if event.total_units is not None:
            self.total_units = event.total_units

        if event.silent:
            return

        if event.transient:
            self.transient_message = event.message
        else:
            self.transient_message = ''
            self.log_entries.append(f'{len(self.log_entries) + 1}. {event.message}')

        self._render_log()

    def _render_log(self) -> None:
        lines = list(self.log_entries)
        if self.transient_message:
            lines.append(self.transient_message)
        self.log_card.setVisible(bool(lines))
        self.log_view.setPlainText('\n'.join(lines))
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _set_status(self, status: str) -> None:
        self.current_status = status

    def _update_timers(self) -> None:
        if not self.running or not self.start_time:
            return

        elapsed = int(time.time() - self.start_time)
        self.elapsed_label.setText(tr(self.ui_language, 'elapsed_time', value=self.format_clock(elapsed)))

        if elapsed < 60 or self.progress_value < 3:
            self.eta_label.setText(tr(self.ui_language, 'eta', value=tr(self.ui_language, 'calculating')))
            return

        now = time.time()
        if self.last_eta_update == 0 or now - self.last_eta_update >= 10:
            progress_fraction = self.progress_value / 100 if self.progress_value else 0
            current_eta = (
                int(elapsed * (1 - progress_fraction) / progress_fraction)
                if progress_fraction > 0
                else None
            )
            if current_eta is None:
                self.last_eta_seconds = None
            elif self.last_eta_seconds is None:
                self.last_eta_seconds = current_eta
            else:
                self.last_eta_seconds = min(self.last_eta_seconds, current_eta)
            self.last_eta_update = now

        if self.last_eta_seconds is None:
            self.eta_label.setText(tr(self.ui_language, 'eta', value=tr(self.ui_language, 'calculating')))
        else:
            self.eta_label.setText(tr(self.ui_language, 'eta', value=self.format_clock(self.last_eta_seconds)))

    def _show_error(self, message: str) -> None:
        self._set_status('error')
        self.current_message_label.setText(message)
        self._append_log(ProgressEvent(message, state='error'))
        _append_runtime_log(f'UI error: {message}')

    def _show_warning(self, message: str) -> None:
        self.current_message_label.setText(message)
        self._append_log(ProgressEvent(message))
        _append_runtime_log(f'UI warning: {message}')

    def _open_settings(self) -> None:
        dialog = SettingsDialog(
            self.performance_mode,
            self.ui_language,
            self.receive_beta_updates,
            self.translation_provider,
            self.provider_api_keys,
            self.provider_models,
            self,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        previous_receive_beta_updates = self.receive_beta_updates
        try:
            _append_runtime_log('Settings accept: reading dialog values')
            self.ui_language = dialog.selected_ui_language()
            self.performance_mode = dialog.selected_performance_mode()
            self.receive_beta_updates = dialog.selected_receive_beta_updates()
            self.translation_provider = dialog.selected_translation_provider()
            self.provider_api_keys = dialog.selected_api_keys()
            self.provider_models = dialog.selected_models()

            _append_runtime_log('Settings accept: writing QSettings values')
            self.settings.setValue('ui_language', self.ui_language)
            self.settings.setValue('performance_mode', self.performance_mode)
            self.settings.setValue('receive_beta_updates', self.receive_beta_updates)
            self.settings.setValue('translation_provider', self.translation_provider)
            for provider, api_key in self.provider_api_keys.items():
                self.settings.setValue(f'api_key_{provider}', api_key)
            for provider, model_id in self.provider_models.items():
                self.settings.setValue(f'model_{provider}', model_id)
            self.settings.sync()

            _append_runtime_log('Settings accept: refreshing main window UI')
            self.latest_version = None
            self.latest_version_url = None
            self._apply_ui_texts()
            self._rebuild_language_combos(
                self.origin_combo.currentData() or DEFAULT_SOURCE_LANGUAGE,
                self.target_combo.currentData() or DEFAULT_TARGET_LANGUAGE,
            )
            self._refresh_settings_summary()

            if self.receive_beta_updates != previous_receive_beta_updates:
                _append_runtime_log('Settings accept: restarting update check')
                self._restart_update_check()
            else:
                _append_runtime_log('Settings accept: update check unchanged')

            if self.running:
                self._append_log(
                    ProgressEvent(
                        tr(self.ui_language, 'settings_applied_next_run'),
                    ),
                )
            _append_runtime_log('Settings accept: completed')
        except Exception as error:  # noqa: BLE001
            _append_runtime_log(f'Settings accept failed: {error}')
            self._show_error(f'Error aplicando ajustes: {error}')

    def _apply_detected_source_language(self, input_path: Path) -> None:
        try:
            detected_language = ElpxTranslationService().detect_project_language(input_path)
        except Exception:  # noqa: BLE001
            self.detected_project_language = None
            self.auto_detected_source_language_active = False
            self._update_source_label()
            return

        if not detected_language:
            self.detected_project_language = None
            self.auto_detected_source_language_active = False
            self._update_source_label()
            return

        self.detected_project_language = detected_language
        self._rebuild_language_combos(
            detected_language,
            self.target_combo.currentData() or DEFAULT_TARGET_LANGUAGE,
        )
        self.auto_detected_source_language_active = True
        self._update_source_label()
        if self.translation_provider == 'local' and detected_language not in SUPPORTED_LANGUAGE_CODES:
            self._show_warning(
                tr(
                    self.ui_language,
                    'local_mode_detected_source_requires_api',
                    language=detected_language,
                )
            )

    def _set_combo_languages(self, combo: QComboBox, language_codes: list[str], selected_code: str) -> None:
        combo.blockSignals(True)
        combo.clear()
        for code in sorted(language_codes):
            combo.addItem(self._language_option_label(code), code)

        combo_index = combo.findData(selected_code)
        if combo_index < 0 and combo.count():
            combo_index = 0
        if combo_index >= 0:
            combo.setCurrentIndex(combo_index)
        combo.blockSignals(False)

    def _rebuild_language_combos(self, source_language: str, target_language: str) -> None:
        effective_target_language = target_language
        custom_target_language = ''
        if self.translation_provider != 'local' and target_language not in SUPPORTED_LANGUAGE_CODES:
            custom_target_language = target_language
            effective_target_language = DEFAULT_TARGET_LANGUAGE if target_language == source_language else target_language

        if self.translation_provider != 'local' and effective_target_language not in SUPPORTED_LANGUAGE_CODES:
            source_options = sorted(SUPPORTED_LANGUAGE_CODES)
        else:
            source_options = supported_source_languages(effective_target_language, self.translation_provider)
        if source_language and source_language not in source_options:
            source_options = [source_language, *source_options]
        if source_language not in source_options:
            source_language = source_options[0] if source_options else DEFAULT_SOURCE_LANGUAGE

        target_options = supported_target_languages(source_language, self.translation_provider)
        selected_target_code = effective_target_language
        if selected_target_code not in target_options:
            selected_target_code = target_options[0] if target_options else DEFAULT_TARGET_LANGUAGE

        self._set_combo_languages(self.origin_combo, source_options, source_language)
        self.target_combo.blockSignals(True)
        self.target_combo.clear()
        for code in sorted(target_options):
            self.target_combo.addItem(self._language_option_label(code), code)
        if self.translation_provider != 'local':
            self.target_combo.addItem(tr(self.ui_language, 'custom_target_language_option'), CUSTOM_TARGET_LANGUAGE_VALUE)
        combo_target = selected_target_code
        if custom_target_language:
            combo_target = CUSTOM_TARGET_LANGUAGE_VALUE
        combo_index = self.target_combo.findData(combo_target)
        if combo_index < 0 and self.target_combo.count():
            combo_index = 0
        if combo_index >= 0:
            self.target_combo.setCurrentIndex(combo_index)
        self.target_combo.blockSignals(False)
        if custom_target_language:
            self.custom_target_edit.setText(custom_target_language)
        self._toggle_custom_target_visibility()
        self._persist_target_language()

    def _sync_language_pairs(self) -> None:
        if self._is_custom_target_selected():
            self._toggle_custom_target_visibility()
            self._persist_target_language()
            self._sync_output_path_with_target_language()
            return
        source_language = self.origin_combo.currentData() or DEFAULT_SOURCE_LANGUAGE
        target_language = self._selected_target_language()
        self._rebuild_language_combos(source_language, target_language)

    def _handle_source_language_changed(self) -> None:
        self._sync_language_pairs()
        source_language = self._selected_source_language()
        if not self.auto_detected_source_language_active or source_language != self.detected_project_language:
            self.auto_detected_source_language_active = False
        self._update_source_label()
        if not self.detected_project_language or source_language == self.detected_project_language:
            return
        detected_label = self.language_labels.get(self.detected_project_language, self.detected_project_language)
        selected_label = self.language_labels.get(source_language, source_language)
        self._show_warning(
            tr(
                self.ui_language,
                'source_language_mismatch_warning',
                detected_language=f'{self.detected_project_language} · {detected_label}',
                selected_language=f'{source_language} · {selected_label}',
            )
        )

    def _build_output_path(self, input_path: Path) -> Path:
        target_language = self._selected_target_language() or 'xx'
        return input_path.with_name(f'{input_path.stem}-{target_language}{input_path.suffix}')

    def _default_source_language(self) -> str:
        if self.ui_language in SUPPORTED_LANGUAGE_CODES:
            return self.ui_language
        return DEFAULT_SOURCE_LANGUAGE

    def _sync_output_path_with_target_language(self) -> None:
        current_file = self.file_edit.text().strip()
        if not current_file:
            return

        input_path = Path(current_file)
        current_output = self.output_edit.text().strip()
        if not current_output:
            self.output_edit.setText(str(self._build_output_path(input_path)))
            return

        current_output_path = Path(current_output)
        expected_stems = {f'{input_path.stem}-{code}' for code, _ in LANGUAGE_OPTIONS}
        if current_output_path.parent == input_path.parent and current_output_path.stem in expected_stems:
            self.output_edit.setText(str(self._build_output_path(input_path)))

    def _load_performance_mode(self) -> str:
        configured_value = self.settings.value('performance_mode', DEFAULT_PERFORMANCE_MODE)
        if isinstance(configured_value, str) and configured_value in {'suave', 'equilibrado', 'rapido', 'maximo'}:
            return configured_value
        return DEFAULT_PERFORMANCE_MODE

    def _load_translation_provider(self) -> str:
        configured_value = self.settings.value('translation_provider', 'local')
        if isinstance(configured_value, str) and configured_value in {code for code, _ in TRANSLATION_PROVIDER_OPTIONS}:
            return configured_value
        return 'local'

    def _load_ui_language(self) -> str:
        configured_value = self.settings.value('ui_language')
        if isinstance(configured_value, str) and configured_value in {code for code, _ in UI_LANGUAGE_OPTIONS}:
            return configured_value
        return detect_ui_language()

    def _load_target_language(self) -> str:
        configured_value = self.settings.value('target_language', DEFAULT_TARGET_LANGUAGE)
        if isinstance(configured_value, str) and configured_value.strip():
            return configured_value.strip()
        return DEFAULT_TARGET_LANGUAGE

    def _load_receive_beta_updates(self) -> bool:
        configured_value = self.settings.value('receive_beta_updates', False)
        if isinstance(configured_value, bool):
            return configured_value
        if isinstance(configured_value, str):
            return configured_value.strip().lower() in {'1', 'true', 'yes'}
        if isinstance(configured_value, int):
            return configured_value != 0
        return False

    def _load_last_directory(self) -> Path:
        configured_value = self.settings.value('last_directory', '')
        if isinstance(configured_value, str) and configured_value.strip():
            configured_path = Path(configured_value).expanduser()
            if configured_path.exists() and configured_path.is_dir():
                return configured_path
        return Path.home()

    def _load_provider_api_keys(self) -> dict[str, str]:
        return {
            'openai': str(self.settings.value('api_key_openai', '') or ''),
            'gemini': str(self.settings.value('api_key_gemini', '') or ''),
            'anthropic': str(self.settings.value('api_key_anthropic', '') or ''),
            'deepseek': str(self.settings.value('api_key_deepseek', '') or ''),
        }

    def _load_provider_models(self) -> dict[str, str]:
        return {
            'openai': str(self.settings.value('model_openai', '') or ''),
            'gemini': str(self.settings.value('model_gemini', '') or ''),
            'anthropic': str(self.settings.value('model_anthropic', '') or ''),
            'deepseek': str(self.settings.value('model_deepseek', '') or ''),
        }

    def _persist_target_language(self) -> None:
        target_language = self._selected_target_language()
        if isinstance(target_language, str) and target_language.strip():
            self.preferred_target_language = target_language
            self.settings.setValue('target_language', target_language)

    def _persist_last_directory(self) -> None:
        if self.last_directory.exists() and self.last_directory.is_dir():
            self.settings.setValue('last_directory', str(self.last_directory))

    def _selected_target_language(self) -> str:
        combo_value = self.target_combo.currentData()
        if combo_value == CUSTOM_TARGET_LANGUAGE_VALUE:
            return self.custom_target_edit.text().strip()
        return str(combo_value or DEFAULT_TARGET_LANGUAGE)

    def _selected_source_language(self) -> str:
        return str(self.origin_combo.currentData() or DEFAULT_SOURCE_LANGUAGE)

    def _update_source_label(self) -> None:
        label_key = 'source_label_detected' if self.auto_detected_source_language_active else 'source_label'
        self.source_label.setText(tr(self.ui_language, label_key))

    def _is_custom_target_selected(self) -> bool:
        return self.target_combo.currentData() == CUSTOM_TARGET_LANGUAGE_VALUE

    def _toggle_custom_target_visibility(self) -> None:
        visible = self.translation_provider != 'local' and self._is_custom_target_selected()
        self.custom_target_label.setVisible(visible)
        self.custom_target_edit.setVisible(visible)
        if visible:
            self.custom_target_edit.setPlaceholderText(tr(self.ui_language, 'custom_target_language_placeholder'))

    def _handle_custom_target_text_changed(self) -> None:
        if not self._is_custom_target_selected():
            return
        self._persist_target_language()
        self._sync_output_path_with_target_language()

    @staticmethod
    def _is_valid_custom_target_language(value: str) -> bool:
        if not value:
            return False
        if len(value) > 15:
            return False
        allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        return all(char in allowed for char in value)

    def _language_option_label(self, code: str) -> str:
        label = self.language_labels.get(code)
        if label:
            return f'{code} · {label}'
        return tr(self.ui_language, 'custom_language_option_label', code=code)

    def _refresh_settings_summary(self) -> None:
        if self.translation_provider == 'local':
            summary = tr(
                self.ui_language,
                'settings_summary_local',
                provider=tr(self.ui_language, f'translation_provider_{self.translation_provider}'),
                performance=performance_label(self.ui_language, self.performance_mode),
            )
        else:
            summary = tr(
                self.ui_language,
                'settings_summary_remote',
                provider=tr(self.ui_language, f'translation_provider_{self.translation_provider}'),
                model=self.provider_models.get(self.translation_provider, '-') or '-',
            )
        self.settings_summary_label.setText(summary)

    def _cancel_translation(self) -> None:
        if not self.running or self.worker is None:
            return

        self.cancel_requested = True
        self.stop_button.setEnabled(False)
        cancelled_label = tr(self.ui_language, 'status_cancelled')
        self.current_message_label.setText(cancelled_label)
        self._append_log(ProgressEvent(cancelled_label, state='cancelled', transient=True))
        self.worker.request_cancel()

    def _apply_ui_texts(self) -> None:
        self.setWindowTitle(tr(self.ui_language, 'app_title'))
        self.title_label.setText(tr(self.ui_language, 'app_title'))
        self.version_label.setText(f'v{__version__}')
        self.settings_button.setIcon(self._header_icon('preferences-system', QStyle.SP_FileDialogDetailedView))
        self.settings_button.setText(tr(self.ui_language, 'settings'))
        self.settings_button.setToolTip(tr(self.ui_language, 'settings'))
        self.website_button.setIcon(self._header_icon('applications-internet', QStyle.SP_ArrowUp))
        self.website_button.setText(tr(self.ui_language, 'website'))
        self.website_button.setToolTip(tr(self.ui_language, 'website_tooltip'))
        self.about_button.setIcon(self._header_icon('help-about', QStyle.SP_MessageBoxInformation))
        self.about_button.setText(tr(self.ui_language, 'about'))
        self.quick_settings_button.setText(tr(self.ui_language, 'change_translation_settings'))
        self.quick_settings_button.setToolTip(tr(self.ui_language, 'settings'))
        self.file_label.setText(tr(self.ui_language, 'file_label'))
        self.file_edit.setPlaceholderText(tr(self.ui_language, 'file_placeholder'))
        self.open_button.setText(tr(self.ui_language, 'open_button'))
        self.output_label.setText(tr(self.ui_language, 'output_label'))
        self.output_edit.setPlaceholderText(tr(self.ui_language, 'output_placeholder'))
        self.save_button.setText(tr(self.ui_language, 'save_as_button'))
        self._update_source_label()
        self.target_label.setText(tr(self.ui_language, 'target_label'))
        self.custom_target_label.setText(tr(self.ui_language, 'custom_target_language_label'))
        self.custom_target_edit.setPlaceholderText(tr(self.ui_language, 'custom_target_language_placeholder'))
        self.translate_button.setText(tr(self.ui_language, 'translate_button'))
        self.stop_button.setText(tr(self.ui_language, 'stop_button'))
        self.log_title.setText(tr(self.ui_language, 'log_label'))
        if not self.running:
            self.current_message_label.setText(tr(self.ui_language, 'select_and_start'))
            self.elapsed_label.setText(tr(self.ui_language, 'elapsed_time', value='00:00'))
            self.eta_label.setText(tr(self.ui_language, 'eta', value='--:--'))
            self.active_model_label.setText(tr(self.ui_language, 'active_model', model_label='-'))
        self._rebuild_language_combos(
            self.origin_combo.currentData() or self._default_source_language(),
            self._selected_target_language(),
        )
        self._set_status(self.current_status)
        self._refresh_update_banner()

    def _refresh_update_banner(self) -> None:
        if not self.latest_version or not self.latest_version_url:
            self.update_banner.hide()
            return

        self.update_banner.setText(
            tr(
                self.ui_language,
                'update_available',
                version=self.latest_version,
                url=self.latest_version_url,
            ),
        )
        self.update_banner.show()

    def _start_update_check(self) -> None:
        if self.closing:
            return
        if self.update_worker is not None and self.update_worker.is_running():
            return
        self.update_worker = UpdateCheckWorker(allow_prereleases=self.receive_beta_updates)
        self.update_worker.update_found.connect(self._handle_update_found)
        self.update_worker.finished.connect(self._clear_update_thread)
        self.update_worker.start()

    def _restart_update_check(self) -> None:
        if self.update_worker is not None and self.update_worker.is_running():
            self.update_check_pending = True
            self.update_worker.cancel()
            return
        self._start_update_check()

    @Slot(str, str)
    def _handle_update_found(self, version: str, url: str) -> None:
        if self.closing:
            return
        self.latest_version = version
        self.latest_version_url = url
        self._refresh_update_banner()

    @Slot()
    def _clear_update_thread(self) -> None:
        self.update_worker = None
        if self.update_check_pending and not self.closing:
            self.update_check_pending = False
            self._start_update_check()

    def _open_about_dialog(self) -> None:
        dialog = AboutDialog(self.ui_language, self)
        dialog.exec()

    def _open_project_website(self) -> None:
        QDesktopServices.openUrl(QUrl(PROJECT_WEBSITE_URL))

    def _open_help_dialog(self) -> None:
        dialog = HelpDialog(self.ui_language, self)
        dialog.exec()

    def closeEvent(self, event) -> None:  # noqa: N802
        self.closing = True
        self.update_check_pending = False
        if self.update_worker is not None:
            self.update_worker.cancel()
        super().closeEvent(event)

    def _header_icon(self, theme_name: str, fallback: QStyle.StandardPixmap) -> QIcon:
        icon = QIcon.fromTheme(theme_name)
        if icon.isNull():
            icon = self.style().standardIcon(fallback)
        return icon

    @staticmethod
    def format_clock(total_seconds: int) -> str:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        return f'{minutes:02d}:{seconds:02d}'

    @staticmethod
    def format_elapsed_summary(total_seconds: int) -> str:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        parts = []
        if hours:
            parts.append(f'{hours} h')
        if minutes or hours:
            parts.append(f'{minutes} min')
        parts.append(f'{seconds} s')
        return ' '.join(parts)


def main() -> None:
    global _FAULT_LOG_HANDLE

    def handle_unhandled_exception(exc_type, exc_value, exc_traceback) -> None:
        formatted = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        _append_runtime_log(f'Unhandled exception:\n{formatted}')
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

    sys.excepthook = handle_unhandled_exception
    _append_runtime_log('Application start')
    try:
        FAULT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _FAULT_LOG_HANDLE = FAULT_LOG_PATH.open('a', encoding='utf-8')
        _FAULT_LOG_HANDLE.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Application start\n')
        _FAULT_LOG_HANDLE.flush()
        faulthandler.enable(file=_FAULT_LOG_HANDLE, all_threads=True)
    except Exception as error:  # noqa: BLE001
        _append_runtime_log(f'Faulthandler setup failed: {error}')
    app = QApplication(sys.argv)
    icon_path = _resolve_app_icon_path()
    if icon_path is not None:
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    window.show()
    exit_code = app.exec()
    _append_runtime_log(f'Application exit code: {exit_code}')
    sys.exit(exit_code)


def _resolve_app_icon_path() -> Path | None:
    icon_name = 'elpx-translator-desktop.svg'

    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            for candidate in (
                Path(meipass) / 'elpx_translator_desktop' / 'assets' / icon_name,
                Path(meipass) / 'assets' / icon_name,
            ):
                if candidate.exists():
                    return candidate

    try:
        icon_path = resources.files('elpx_translator_desktop.assets').joinpath(icon_name)
        if icon_path.is_file():
            return Path(icon_path)
    except (ModuleNotFoundError, FileNotFoundError, AttributeError):
        pass

    fallback = Path(__file__).resolve().parent / 'assets' / icon_name
    return fallback if fallback.exists() else None


if __name__ == '__main__':
    main()
