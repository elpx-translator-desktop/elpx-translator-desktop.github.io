from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QFont
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
    QVBoxLayout,
    QWidget,
)

from .config import (
    DEFAULT_PERFORMANCE_MODE,
    DEFAULT_SOURCE_LANGUAGE,
    DEFAULT_TARGET_LANGUAGE,
    LANGUAGE_OPTIONS,
    PERFORMANCE_MODE_LABELS,
    PERFORMANCE_MODE_OPTIONS,
    SUPPORTED_LANGUAGE_CODES,
)
from .elpx_service import ElpxTranslationService, TranslationOptions
from .progress import ProgressEvent, TranslationCancelledError
from .translator_engine import TranslationEngine


class SettingsDialog(QDialog):
    def __init__(self, performance_mode: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Configuracion')
        self.setModal(True)
        self.resize(460, 280)
        self.setMinimumSize(440, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel('Rendimiento')
        title.setProperty('fieldLabel', True)
        layout.addWidget(title)

        self.performance_combo = QComboBox()
        for code, label in PERFORMANCE_MODE_OPTIONS:
            self.performance_combo.addItem(label, code)
        combo_index = self.performance_combo.findData(performance_mode)
        if combo_index >= 0:
            self.performance_combo.setCurrentIndex(combo_index)
        layout.addWidget(self.performance_combo)

        help_label = QLabel(
            'Suave: mas margen para el sistema.\n'
            'Equilibrado: opcion recomendada.\n'
            'Rapido: mas CPU si compensa.\n'
            'Maximo: exprime mas la maquina.'
        )
        help_label.setWordWrap(True)
        help_label.setObjectName('infoLabel')
        help_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(help_label)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_performance_mode(self) -> str:
        return str(self.performance_combo.currentData())


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
    ) -> None:
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.source_language = source_language
        self.target_language = target_language
        self.performance_mode = performance_mode
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def is_cancel_requested(self) -> bool:
        return self._cancel_requested

    @Slot()
    def run(self) -> None:
        start_time = time.time()
        service = ElpxTranslationService(engine=TranslationEngine(performance_mode=self.performance_mode))
        try:
            service.translate_file(
                self.input_path,
                self.output_path,
                TranslationOptions(
                    source_language=self.source_language,
                    target_language=self.target_language,
                    should_cancel=self.is_cancel_requested,
                ),
                self.progress.emit,
            )
            elapsed = int(time.time() - start_time)
            self.progress.emit(
                ProgressEvent(
                    f'Traduccion terminada en {MainWindow.format_elapsed_summary(elapsed)}. '
                    f'Archivo guardado en {self.output_path}.',
                    state='Listo',
                    progress_percent=100,
                ),
            )
        except TranslationCancelledError as error:
            elapsed = int(time.time() - start_time)
            if self.output_path.exists():
                self.output_path.unlink(missing_ok=True)
            suffix = f' Tras {MainWindow.format_elapsed_summary(elapsed)}.' if elapsed else ''
            self.progress.emit(ProgressEvent(f'{error}{suffix}', state='Cancelado'))
        except Exception as error:  # noqa: BLE001
            elapsed = int(time.time() - start_time)
            suffix = f' Tras {MainWindow.format_elapsed_summary(elapsed)}.' if elapsed else ''
            self.progress.emit(ProgressEvent(f'{error}{suffix}', state='Error'))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('ELPX Translator Desktop')
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
        self.log_entries: list[str] = []
        self.transient_message = ''
        self.cancel_requested = False
        self.settings = QSettings('Juanjo', 'ELPXTranslatorDesktop')
        self.performance_mode = self._load_performance_mode()

        self._build_ui()
        self._apply_styles()
        self._refresh_settings_summary()

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

        title = QLabel('ELPX Translator Desktop')
        title.setObjectName('titleLabel')
        header_layout.addWidget(title)
        header_layout.addStretch()

        settings_button = QPushButton('Configuracion')
        settings_button.clicked.connect(self._open_settings)
        header_layout.addWidget(settings_button)

        self.status_chip = QLabel('En espera')
        self.status_chip.setObjectName('statusChip')
        header_layout.addWidget(self.status_chip)
        root_layout.addWidget(header_card)

        stats_card = self._make_card()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(20, 18, 20, 18)
        stats_layout.setSpacing(10)

        self.elapsed_label = QLabel('Tiempo transcurrido: 00:00')
        self.elapsed_label.setObjectName('infoLabel')
        stats_layout.addWidget(self.elapsed_label)

        self.eta_label = QLabel('Tiempo restante estimado: --:--')
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

        self.current_message_label = QLabel('Selecciona un archivo y arranca la traduccion.')
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

        controls_layout.addWidget(self._make_field_label('Archivo .elpx'), 0, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText('Selecciona el archivo .elpx a traducir')
        controls_layout.addWidget(self.file_edit, 1, 0, 1, 3)
        open_button = QPushButton('Abrir...')
        open_button.clicked.connect(self._choose_file)
        controls_layout.addWidget(open_button, 1, 3)

        controls_layout.addWidget(self._make_field_label('Salida'), 2, 0)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText('Ruta del archivo traducido')
        controls_layout.addWidget(self.output_edit, 3, 0, 1, 3)
        save_button = QPushButton('Guardar como...')
        save_button.clicked.connect(self._choose_output)
        controls_layout.addWidget(save_button, 3, 3)

        controls_layout.addWidget(self._make_field_label('Origen'), 4, 0)
        controls_layout.addWidget(self._make_field_label('Destino'), 4, 1)

        self.origin_combo = QComboBox()
        self.target_combo = QComboBox()
        language_labels = {code: label for code, label in LANGUAGE_OPTIONS}
        for code, label in LANGUAGE_OPTIONS:
            text = f'{code} · {label}'
            self.origin_combo.addItem(text, code)
            self.target_combo.addItem(text, code)
        self.origin_combo.setCurrentText(f'{DEFAULT_SOURCE_LANGUAGE} · {language_labels[DEFAULT_SOURCE_LANGUAGE]}')
        self.target_combo.setCurrentText(f'{DEFAULT_TARGET_LANGUAGE} · {language_labels[DEFAULT_TARGET_LANGUAGE]}')
        self.target_combo.currentIndexChanged.connect(self._sync_output_path_with_target_language)
        controls_layout.addWidget(self.origin_combo, 5, 0)
        controls_layout.addWidget(self.target_combo, 5, 1)

        self.translate_button = QPushButton('Traducir archivo')
        self.translate_button.setObjectName('primaryButton')
        self.translate_button.clicked.connect(self._start_translation)
        controls_layout.addWidget(self.translate_button, 5, 3)

        self.stop_button = QPushButton('Parar')
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

        log_title = self._make_field_label('Registro')
        log_layout.addWidget(log_title)

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
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                border: 1px solid #1f9d84;
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
            'Seleccionar archivo .elpx',
            str(self.last_directory),
            'Archivos ELPX (*.elpx)',
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
            suggested_output = self.last_directory / f'archivo-{target_language}.elpx'

        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Guardar archivo traducido',
            str(suggested_output),
            'Archivos ELPX (*.elpx)',
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
            self._show_error('Selecciona un archivo .elpx valido.')
            return

        source_language = self.origin_combo.currentData()
        target_language = self.target_combo.currentData()
        if source_language == target_language:
            self._show_error('El idioma origen y destino no pueden ser iguales.')
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
        self._append_log(ProgressEvent('Preparando la traduccion...'))

        self.thread = QThread(self)
        self.worker = TranslationWorker(
            input_path=input_path,
            output_path=output_path,
            source_language=source_language,
            target_language=target_language,
            performance_mode=self.performance_mode,
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
        self._set_status('Trabajando')
        self.current_message_label.setText('Preparando la traduccion...')
        self.elapsed_label.setText('Tiempo transcurrido: 00:00')
        self.eta_label.setText('Tiempo restante estimado: --:--')

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
        self.status_chip.setText(status)
        if status == 'Error':
            self.status_chip.setStyleSheet('background:#f8e1df;color:#a84034;border-radius:16px;padding:8px 12px;font-weight:700;')
        elif status == 'Cancelado':
            self.status_chip.setStyleSheet('background:#efe8d8;color:#8a5a12;border-radius:16px;padding:8px 12px;font-weight:700;')
        elif status == 'Listo':
            self.status_chip.setStyleSheet('background:#dceee5;color:#1d6c54;border-radius:16px;padding:8px 12px;font-weight:700;')
        else:
            self.status_chip.setStyleSheet('background:#dff0e9;color:#1d6c54;border-radius:16px;padding:8px 12px;font-weight:700;')

    def _update_timers(self) -> None:
        if not self.running or not self.start_time:
            return

        elapsed = int(time.time() - self.start_time)
        self.elapsed_label.setText(f'Tiempo transcurrido: {self.format_clock(elapsed)}')

        if elapsed < 60 or self.completed_units < 24 or self.total_units <= 0:
            self.eta_label.setText('Tiempo restante estimado: calculando...')
            return

        now = time.time()
        if self.last_eta_update == 0 or now - self.last_eta_update >= 10:
            remaining_units = max(0, self.total_units - self.completed_units)
            units_per_second = self.completed_units / elapsed if elapsed else 0
            self.last_eta_seconds = int(remaining_units / units_per_second) if units_per_second > 0 else None
            self.last_eta_update = now

        if self.last_eta_seconds is None:
            self.eta_label.setText('Tiempo restante estimado: calculando...')
        else:
            self.eta_label.setText(f'Tiempo restante estimado: {self.format_clock(self.last_eta_seconds)}')

    def _show_error(self, message: str) -> None:
        self._set_status('Error')
        QMessageBox.critical(self, 'ELPX Translator Desktop', message)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.performance_mode, self)
        if dialog.exec() != QDialog.Accepted:
            return

        self.performance_mode = dialog.selected_performance_mode()
        self.settings.setValue('performance_mode', self.performance_mode)
        self._refresh_settings_summary()
        if self.running:
            self._append_log(
                ProgressEvent(
                    'La nueva configuracion se aplicara en la proxima traduccion. '
                    'Si quieres usarla ya, pulsa Parar y vuelve a iniciar.',
                ),
            )

    def _apply_detected_source_language(self, input_path: Path) -> None:
        try:
            detected_language = ElpxTranslationService().detect_project_language(input_path)
        except Exception:  # noqa: BLE001
            return

        if not detected_language or detected_language not in SUPPORTED_LANGUAGE_CODES:
            return

        combo_index = self.origin_combo.findData(detected_language)
        if combo_index >= 0:
            self.origin_combo.setCurrentIndex(combo_index)

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
        if isinstance(configured_value, str) and configured_value in PERFORMANCE_MODE_LABELS:
            return configured_value
        return DEFAULT_PERFORMANCE_MODE

    def _refresh_settings_summary(self) -> None:
        label = PERFORMANCE_MODE_LABELS.get(self.performance_mode, PERFORMANCE_MODE_LABELS[DEFAULT_PERFORMANCE_MODE])
        self.settings_summary_label.setText(f'Rendimiento: {label}')

    def _cancel_translation(self) -> None:
        if not self.running or self.worker is None:
            return

        self.cancel_requested = True
        self.stop_button.setEnabled(False)
        self.current_message_label.setText('Cancelando traduccion...')
        self._append_log(ProgressEvent('Cancelando traduccion...', state='Cancelado', transient=True))
        self.worker.request_cancel()

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
