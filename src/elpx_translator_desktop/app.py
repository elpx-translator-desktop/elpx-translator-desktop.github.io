from __future__ import annotations

import html
import importlib.resources as resources
import sys
import time
import unicodedata
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QThread, QTimer, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
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
    QSizePolicy,
    QStyle,
    QTextBrowser,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

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
        supported_source_languages,
        supported_target_languages,
    )
    from elpx_translator_desktop.elpx_service import ElpxTranslationService, TranslationOptions  # type: ignore[no-redef]
    from elpx_translator_desktop.progress import ProgressEvent, TranslationCancelledError  # type: ignore[no-redef]
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
        supported_source_languages,
        supported_target_languages,
    )
    from .elpx_service import ElpxTranslationService, TranslationOptions
    from .progress import ProgressEvent, TranslationCancelledError
    from .translator_engine import TranslationEngine
    from .update_checker import UpdateCheckWorker
    from .ui_i18n import UI_LANGUAGE_OPTIONS, detect_ui_language, performance_label, tr


class SettingsDialog(QDialog):
    def __init__(self, performance_mode: str, ui_language: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui_language = ui_language
        self.setWindowTitle(tr(ui_language, 'settings_title'))
        self.setModal(True)
        self.resize(460, 280)
        self.setMinimumSize(440, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        language_title = QLabel(tr(ui_language, 'settings_interface_language'))
        language_title.setProperty('fieldLabel', True)
        layout.addWidget(language_title)

        self.ui_language_combo = QComboBox()
        for code, label in UI_LANGUAGE_OPTIONS:
            self.ui_language_combo.addItem(label, code)
        combo_index = self.ui_language_combo.findData(ui_language)
        if combo_index >= 0:
            self.ui_language_combo.setCurrentIndex(combo_index)
        layout.addWidget(self.ui_language_combo)

        title = QLabel(tr(ui_language, 'settings_performance'))
        title.setProperty('fieldLabel', True)
        layout.addWidget(title)

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
        layout.addWidget(self.performance_combo)

        help_label = QLabel(tr(ui_language, 'settings_help'))
        help_label.setWordWrap(True)
        help_label.setObjectName('infoLabel')
        help_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(help_label)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        ok_button = buttons.button(QDialogButtonBox.Ok)
        cancel_button = buttons.button(QDialogButtonBox.Cancel)
        if ok_button is not None:
            ok_button.setText(tr(ui_language, 'ok_button'))
        if cancel_button is not None:
            cancel_button.setText(tr(ui_language, 'cancel_button'))
        layout.addWidget(buttons)

    def selected_performance_mode(self) -> str:
        return str(self.performance_combo.currentData())

    def selected_ui_language(self) -> str:
        return str(self.ui_language_combo.currentData())


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
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.source_language = source_language
        self.target_language = target_language
        self.performance_mode = performance_mode
        self.ui_language = ui_language
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def is_cancel_requested(self) -> bool:
        return self._cancel_requested

    @Slot()
    def run(self) -> None:
        start_time = time.time()
        service = ElpxTranslationService(
            engine=TranslationEngine(
                performance_mode=self.performance_mode,
                ui_language=self.ui_language,
            ),
        )
        try:
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
            suffix = (
                tr(self.ui_language, 'after_elapsed', elapsed=MainWindow.format_elapsed_summary(elapsed))
                if elapsed
                else ''
            )
            self.progress.emit(ProgressEvent(f'{error}{suffix}', state='cancelled'))
        except Exception as error:  # noqa: BLE001
            elapsed = int(time.time() - start_time)
            suffix = (
                tr(self.ui_language, 'after_elapsed', elapsed=MainWindow.format_elapsed_summary(elapsed))
                if elapsed
                else ''
            )
            self.progress.emit(ProgressEvent(f'{error}{suffix}', state='error'))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.resize(1040, 820)

        self.start_time = 0.0
        self.last_eta_update = 0.0
        self.last_eta_seconds: int | None = None
        self.completed_units = 0
        self.total_units = 0
        self.progress_value = 0.0
        self.running = False
        self.last_directory = Path.home()
        self.thread: QThread | None = None
        self.worker: TranslationWorker | None = None
        self.update_thread: QThread | None = None
        self.update_worker: UpdateCheckWorker | None = None
        self.log_entries: list[str] = []
        self.transient_message = ''
        self.cancel_requested = False
        self.latest_version: str | None = None
        self.latest_version_url: str | None = None
        self.settings = QSettings('Juanjo', 'ELPXTranslatorDesktop')
        self.ui_language = self._load_ui_language()
        self.performance_mode = self._load_performance_mode()
        self.current_status = 'waiting'

        self._build_ui()
        self._apply_styles()
        self._apply_ui_texts()
        self._refresh_settings_summary()
        self._start_update_check()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_timers)
        self.timer.start()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)

        header_card = self._make_card()
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 18, 20, 18)
        header_layout.setSpacing(16)

        self.title_label = QLabel('')
        self.title_label.setObjectName('titleLabel')
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.settings_button = QToolButton()
        self.settings_button.setObjectName('headerIconButton')
        self.settings_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.settings_button.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_button)

        self.website_button = QPushButton('')
        self.website_button.setObjectName('headerActionButton')
        self.website_button.clicked.connect(self._open_project_website)
        header_layout.addWidget(self.website_button)

        self.about_button = QPushButton('')
        self.about_button.setObjectName('headerActionButton')
        self.about_button.clicked.connect(self._open_about_dialog)
        header_layout.addWidget(self.about_button)

        self.status_chip = QLabel('')
        self.status_chip.setObjectName('statusChip')
        header_layout.addWidget(self.status_chip)
        root_layout.addWidget(header_card)

        self.update_banner = QLabel('')
        self.update_banner.setObjectName('infoLabel')
        self.update_banner.setOpenExternalLinks(True)
        self.update_banner.setWordWrap(True)
        self.update_banner.hide()
        root_layout.addWidget(self.update_banner)

        stats_card = self._make_card()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 18, 20, 18)
        stats_layout.setSpacing(10)

        self.elapsed_label = QLabel('')
        self.elapsed_label.setObjectName('infoLabel')
        stats_layout.addWidget(self.elapsed_label)

        self.eta_label = QLabel('')
        self.eta_label.setObjectName('infoLabel')
        stats_layout.addWidget(self.eta_label)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(12)

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

        root_layout.addWidget(stats_card)

        self.current_message_label = QLabel('')
        self.current_message_label.setObjectName('messageLabel')
        self.current_message_label.setWordWrap(True)
        root_layout.addWidget(self.current_message_label)

        self.settings_summary_label = QLabel('')
        self.settings_summary_label.setObjectName('infoLabel')
        root_layout.addWidget(self.settings_summary_label)

        controls_card = self._make_card()
        controls_layout = QGridLayout(controls_card)
        controls_layout.setContentsMargins(20, 18, 20, 18)
        controls_layout.setHorizontalSpacing(10)
        controls_layout.setVerticalSpacing(12)

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
        self.language_labels = {code: label for code, label in LANGUAGE_OPTIONS}
        self.language_sort_labels = {
            'ar': 'arabe',
            'bn': 'bangla',
            'nl': 'neerlandes',
            'pl': 'polaco',
            'ru': 'ruso',
            'tr': 'turco',
            'uk': 'ucraniano',
            'ur': 'urdu',
            'zh': 'chino',
        }
        self._rebuild_language_combos(DEFAULT_SOURCE_LANGUAGE, DEFAULT_TARGET_LANGUAGE)
        self.origin_combo.currentIndexChanged.connect(self._sync_language_pairs)
        self.target_combo.currentIndexChanged.connect(self._sync_output_path_with_target_language)
        self.target_combo.currentIndexChanged.connect(self._sync_language_pairs)
        controls_layout.addWidget(self.origin_combo, 5, 0)
        controls_layout.addWidget(self.target_combo, 5, 1)

        self.translate_button = QPushButton('')
        self.translate_button.setObjectName('primaryButton')
        self.translate_button.clicked.connect(self._start_translation)
        controls_layout.addWidget(self.translate_button, 5, 3)

        self.stop_button = QPushButton('')
        self.stop_button.clicked.connect(self._cancel_translation)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button, 5, 2)

        controls_layout.setColumnStretch(0, 1)
        controls_layout.setColumnStretch(1, 1)
        controls_layout.setColumnStretch(2, 1)
        root_layout.addWidget(controls_card)

        log_card = self._make_card()
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(20, 18, 20, 18)
        log_layout.setSpacing(8)

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
        log_layout.addWidget(self.log_view, 1)

        root_layout.addWidget(log_card, 1)

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
                border-radius: 16px;
            }
            QLabel {
                background: transparent;
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: 700;
                color: #16212b;
            }
            QLabel#statusChip {
                background: #e3f3eb;
                color: #1d6c54;
                border-radius: 16px;
                padding: 8px 12px;
                font-weight: 700;
            }
            QLabel#infoLabel {
                color: #5f6b76;
                font-family: "IBM Plex Mono", "Courier New", monospace;
                font-size: 13px;
                padding: 0;
            }
            QLabel#percentLabel {
                color: #1d6c54;
                font-family: "IBM Plex Mono", "Courier New", monospace;
                font-size: 13px;
                font-weight: 700;
                min-width: 42px;
            }
            QLabel#messageLabel {
                color: #16212b;
                font-size: 15px;
                padding-left: 4px;
            }
            QLabel[fieldLabel="true"] {
                font-size: 12px;
                font-weight: 700;
                color: #465361;
            }
            QLineEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #ddd4c8;
                border-radius: 10px;
                padding: 10px 12px;
                min-height: 18px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #1f9d84;
            }
            QPushButton {
                background: #ffffff;
                border: 1px solid #ddd4c8;
                border-radius: 12px;
                padding: 10px 14px;
                font-weight: 600;
            }
            QToolButton#headerIconButton {
                background: #ffffff;
                border: 1px solid #d9d0c4;
                border-radius: 14px;
                padding: 8px;
                min-width: 42px;
                max-width: 42px;
                min-height: 42px;
                max-height: 42px;
            }
            QPushButton#headerActionButton {
                background: #ffffff;
                border: 1px solid #d9d0c4;
                border-radius: 14px;
                padding: 0 16px;
                min-height: 42px;
                color: #30404c;
                font-weight: 600;
            }
            QPushButton:hover {
                border: 1px solid #1f9d84;
            }
            QToolButton#headerIconButton:hover {
                border: 1px solid #1f9d84;
            }
            QPushButton#headerActionButton:hover {
                border: 1px solid #1f9d84;
                color: #1d6c54;
            }
            QPushButton#primaryButton {
                background: #1f9d84;
                color: #ffffff;
                border: 1px solid #1f9d84;
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
            QLabel#statusChip {
                background: #dff0e9;
                color: #1d6c54;
                border: 1px solid #c6e5d9;
                border-radius: 14px;
                padding: 0 18px;
                min-height: 42px;
                qproperty-alignment: AlignCenter;
                font-weight: 700;
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
                padding: 10px;
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

    def _start_translation(self) -> None:
        if self.running:
            return

        input_path = Path(self.file_edit.text().strip())
        if not input_path.exists():
            self._show_error(tr(self.ui_language, 'invalid_input_file'))
            return

        source_language = self.origin_combo.currentData()
        target_language = self.target_combo.currentData()
        if source_language == target_language:
            self._show_error(tr(self.ui_language, 'same_languages_error'))
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
        self._append_log(ProgressEvent(tr(self.ui_language, 'preparing_translation')))

        self.thread = QThread(self)
        self.worker = TranslationWorker(
            input_path=input_path,
            output_path=output_path,
            source_language=source_language,
            target_language=target_language,
            performance_mode=self.performance_mode,
            ui_language=self.ui_language,
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
        self._set_status('working')
        self.current_message_label.setText(tr(self.ui_language, 'preparing_translation'))
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
        self.log_view.setPlainText('\n'.join(lines))
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _set_status(self, status: str) -> None:
        self.current_status = status
        status_label_map = {
            'waiting': tr(self.ui_language, 'status_waiting'),
            'working': tr(self.ui_language, 'status_working'),
            'done': tr(self.ui_language, 'status_done'),
            'error': tr(self.ui_language, 'status_error'),
            'cancelled': tr(self.ui_language, 'status_cancelled'),
        }
        self.status_chip.setText(status_label_map.get(status, status))
        if status == 'error':
            self.status_chip.setStyleSheet('background:#f8e1df;color:#a84034;border-radius:16px;padding:8px 12px;font-weight:700;')
        elif status == 'cancelled':
            self.status_chip.setStyleSheet('background:#efe8d8;color:#8a5a12;border-radius:16px;padding:8px 12px;font-weight:700;')
        elif status == 'done':
            self.status_chip.setStyleSheet('background:#dceee5;color:#1d6c54;border-radius:16px;padding:8px 12px;font-weight:700;')
        else:
            self.status_chip.setStyleSheet('background:#dff0e9;color:#1d6c54;border-radius:16px;padding:8px 12px;font-weight:700;')

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
        QMessageBox.critical(self, tr(self.ui_language, 'app_title'), message)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.performance_mode, self.ui_language, self)
        if dialog.exec() != QDialog.Accepted:
            return

        self.ui_language = dialog.selected_ui_language()
        self.performance_mode = dialog.selected_performance_mode()
        self.settings.setValue('ui_language', self.ui_language)
        self.settings.setValue('performance_mode', self.performance_mode)
        self._apply_ui_texts()
        self._refresh_settings_summary()
        if self.running:
            self._append_log(
                ProgressEvent(
                    tr(self.ui_language, 'settings_applied_next_run'),
                ),
            )

    def _apply_detected_source_language(self, input_path: Path) -> None:
        try:
            detected_language = ElpxTranslationService().detect_project_language(input_path)
        except Exception:  # noqa: BLE001
            return

        if not detected_language or detected_language not in SUPPORTED_LANGUAGE_CODES:
            return

        self._rebuild_language_combos(
            detected_language,
            self.target_combo.currentData() or DEFAULT_TARGET_LANGUAGE,
        )

    def _set_combo_languages(self, combo: QComboBox, language_codes: list[str], selected_code: str) -> None:
        combo.blockSignals(True)
        combo.clear()
        for code in sorted(language_codes, key=self._language_sort_key):
            combo.addItem(f'{code} · {self.language_labels[code]}', code)

        combo_index = combo.findData(selected_code)
        if combo_index < 0 and combo.count():
            combo_index = 0
        if combo_index >= 0:
            combo.setCurrentIndex(combo_index)
        combo.blockSignals(False)

    def _language_sort_key(self, code: str) -> str:
        label = self.language_sort_labels.get(code, self.language_labels[code])
        normalized = unicodedata.normalize('NFKD', label)
        return ''.join(char for char in normalized if not unicodedata.combining(char)).casefold()

    def _rebuild_language_combos(self, source_language: str, target_language: str) -> None:
        source_options = supported_source_languages(target_language)
        if source_language not in source_options:
            source_language = source_options[0] if source_options else DEFAULT_SOURCE_LANGUAGE

        target_options = supported_target_languages(source_language)
        if target_language not in target_options:
            target_language = target_options[0] if target_options else DEFAULT_TARGET_LANGUAGE

        self._set_combo_languages(self.origin_combo, source_options, source_language)
        self._set_combo_languages(self.target_combo, target_options, target_language)

    def _sync_language_pairs(self) -> None:
        source_language = self.origin_combo.currentData() or DEFAULT_SOURCE_LANGUAGE
        target_language = self.target_combo.currentData() or DEFAULT_TARGET_LANGUAGE
        self._rebuild_language_combos(source_language, target_language)

    def _build_output_path(self, input_path: Path) -> Path:
        target_language = self.target_combo.currentData() or 'xx'
        return input_path.with_name(f'{input_path.stem}-{target_language}{input_path.suffix}')

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

    def _load_ui_language(self) -> str:
        configured_value = self.settings.value('ui_language')
        if isinstance(configured_value, str) and configured_value in {code for code, _ in UI_LANGUAGE_OPTIONS}:
            return configured_value
        return detect_ui_language()

    def _refresh_settings_summary(self) -> None:
        self.settings_summary_label.setText(
            tr(self.ui_language, 'performance_summary', value=performance_label(self.ui_language, self.performance_mode)),
        )

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
        self.settings_button.setIcon(self._header_icon('preferences-system', QStyle.SP_FileDialogDetailedView))
        self.settings_button.setToolTip(tr(self.ui_language, 'settings'))
        self.website_button.setIcon(self._header_icon('applications-internet', QStyle.SP_ArrowUp))
        self.website_button.setText(tr(self.ui_language, 'website'))
        self.website_button.setToolTip(tr(self.ui_language, 'website_tooltip'))
        self.about_button.setText(tr(self.ui_language, 'about'))
        self.file_label.setText(tr(self.ui_language, 'file_label'))
        self.file_edit.setPlaceholderText(tr(self.ui_language, 'file_placeholder'))
        self.open_button.setText(tr(self.ui_language, 'open_button'))
        self.output_label.setText(tr(self.ui_language, 'output_label'))
        self.output_edit.setPlaceholderText(tr(self.ui_language, 'output_placeholder'))
        self.save_button.setText(tr(self.ui_language, 'save_as_button'))
        self.source_label.setText(tr(self.ui_language, 'source_label'))
        self.target_label.setText(tr(self.ui_language, 'target_label'))
        self.translate_button.setText(tr(self.ui_language, 'translate_button'))
        self.stop_button.setText(tr(self.ui_language, 'stop_button'))
        self.log_title.setText(tr(self.ui_language, 'log_label'))
        if not self.running:
            self.current_message_label.setText(tr(self.ui_language, 'select_and_start'))
            self.elapsed_label.setText(tr(self.ui_language, 'elapsed_time', value='00:00'))
            self.eta_label.setText(tr(self.ui_language, 'eta', value='--:--'))
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
        self.update_thread = QThread(self)
        self.update_worker = UpdateCheckWorker()
        self.update_worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.update_found.connect(self._handle_update_found)
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self._clear_update_thread)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_thread.start()

    @Slot(str, str)
    def _handle_update_found(self, version: str, url: str) -> None:
        self.latest_version = version
        self.latest_version_url = url
        self._refresh_update_banner()

    @Slot()
    def _clear_update_thread(self) -> None:
        self.update_thread = None
        self.update_worker = None

    def _open_about_dialog(self) -> None:
        dialog = AboutDialog(self.ui_language, self)
        dialog.exec()

    def _open_project_website(self) -> None:
        QDesktopServices.openUrl(QUrl(PROJECT_WEBSITE_URL))

    def _open_help_dialog(self) -> None:
        dialog = HelpDialog(self.ui_language, self)
        dialog.exec()

    def closeEvent(self, event) -> None:  # noqa: N802
        if self.update_thread is not None and self.update_thread.isRunning():
            self.update_thread.quit()
            self.update_thread.wait(2000)
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
    app = QApplication(sys.argv)
    icon_path = _resolve_app_icon_path()
    if icon_path is not None:
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    window.show()
    sys.exit(app.exec())


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
