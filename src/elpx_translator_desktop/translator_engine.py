from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import ctranslate2
from huggingface_hub import snapshot_download
from platformdirs import user_cache_dir
from transformers import AutoTokenizer

from .config import DEFAULT_PERFORMANCE_MODE, EUSKERA_MODEL_CONFIGS, MODEL_CONFIG, ModelConfig
from .progress import ProgressEvent, TranslationCancelledError
from .remote_provider import RemoteProviderError, create_translation_completion, is_structured_response_error
from .text_utils import sanitize_translated_text, split_long_text
from .ui_i18n import tr


@dataclass(frozen=True)
class RuntimeProfile:
    device: str
    compute_type: str
    inter_threads: int
    intra_threads: int
    batch_size: int
    cpu_count: int
    reserved_cores: int
    process_nice: int

    def describe(self, ui_language: str) -> str:
        if self.device == 'cuda':
            return tr(
                ui_language,
                'gpu_profile',
                compute_type=self.compute_type,
                batch_size=self.batch_size,
            )

        return tr(
            ui_language,
            'cpu_profile',
            cpu_count=self.cpu_count,
            reserved_cores=self.reserved_cores,
            inter_threads=self.inter_threads,
            intra_threads=self.intra_threads,
            batch_size=self.batch_size,
        )


class TranslationEngine:
    def __init__(
        self,
        performance_mode: str = DEFAULT_PERFORMANCE_MODE,
        ui_language: str = 'es',
        translation_provider: str = 'local',
        remote_model_id: str | None = None,
        remote_api_key: str | None = None,
    ) -> None:
        self._translator: ctranslate2.Translator | None = None
        self._tokenizer = None
        self._model_dir: Path | None = None
        self._runtime_profile: RuntimeProfile | None = None
        self._model_key: str | None = None
        self._model_config: ModelConfig | None = None
        self._remote_ready = False
        self.performance_mode = performance_mode
        self.ui_language = ui_language
        self.translation_provider = translation_provider
        self.remote_model_id = (remote_model_id or '').strip()
        self.remote_api_key = (remote_api_key or '').strip()

    def ensure_model(self, source_language: str, target_language: str, progress_callback, should_cancel=None) -> None:
        if self.translation_provider != 'local':
            self._ensure_remote_provider(progress_callback)
            return

        self._raise_if_cancelled(should_cancel)
        model_config = self._resolve_model_config(source_language, target_language)
        model_key = model_config.repo_id

        runtime_profile = self._runtime_profile or self._build_runtime_profile(self.performance_mode)
        self._runtime_profile = runtime_profile

        if (
            self._translator is not None
            and self._tokenizer is not None
            and self._model_key == model_key
            and self._model_config == model_config
        ):
            return

        cache_dir = Path(user_cache_dir('elpx-translator-desktop', 'Juanjo')) / 'models'
        cache_dir.mkdir(parents=True, exist_ok=True)

        progress_callback(
            ProgressEvent(
                tr(self.ui_language, 'model_prepare', model_label=model_config.label),
                active_model_label=model_config.label,
                transient=True,
            ),
        )
        snapshot_dir = Path(
            snapshot_download(
                repo_id=model_config.repo_id,
                cache_dir=str(cache_dir),
                etag_timeout=30,
                max_workers=1,
            ),
        )
        self._raise_if_cancelled(should_cancel)

        tokenizer = AutoTokenizer.from_pretrained(model_config.tokenizer_repo_id, cache_dir=str(cache_dir))

        if runtime_profile.device == 'cpu':
            priority_message_key = 'priority_lowered' if self._lower_process_priority(runtime_profile.process_nice) else 'priority_normal'
            progress_callback(
                ProgressEvent(
                    tr(self.ui_language, priority_message_key),
                    active_model_label=model_config.label,
                ),
            )

        progress_callback(ProgressEvent(runtime_profile.describe(self.ui_language), active_model_label=model_config.label))

        progress_callback(
            ProgressEvent(
                tr(
                    self.ui_language,
                    'loading_model',
                    device=runtime_profile.device,
                    compute_type=runtime_profile.compute_type,
                ),
                active_model_label=model_config.label,
                transient=True,
            ),
        )

        model_dir = snapshot_dir
        translator = ctranslate2.Translator(
            str(model_dir),
            device=runtime_profile.device,
            compute_type=runtime_profile.compute_type,
            inter_threads=runtime_profile.inter_threads,
            intra_threads=runtime_profile.intra_threads,
        )

        self._model_dir = model_dir
        self._translator = translator
        self._tokenizer = tokenizer
        self._model_key = model_key
        self._model_config = model_config

    def translate_texts(
        self,
        texts: list[str],
        *,
        source_language: str,
        target_language: str,
        progress_callback,
        progress_label: str,
        progress_meta: dict | None = None,
        batch_size: int | None = None,
        should_cancel=None,
    ) -> list[str]:
        if not texts:
            return []

        if source_language == target_language:
            return list(texts)

        if self.translation_provider != 'local':
            return self._translate_texts_remote(
                texts,
                source_language=source_language,
                target_language=target_language,
                progress_callback=progress_callback,
                progress_label=progress_label,
                progress_meta=progress_meta,
                batch_size=batch_size,
                should_cancel=should_cancel,
            )

        self.ensure_model(source_language, target_language, progress_callback, should_cancel)
        assert self._translator is not None
        assert self._tokenizer is not None
        assert self._runtime_profile is not None
        assert self._model_config is not None

        tokenizer = self._tokenizer
        effective_batch_size = batch_size or self._runtime_profile.batch_size
        if self._model_config.model_type == 'm2m100':
            tokenizer.src_lang = source_language

        jobs: list[dict] = []
        for index, text in enumerate(texts):
            chunks = split_long_text(text)
            for chunk_index, chunk in enumerate(chunks):
                jobs.append(
                    {
                        'text': chunk,
                        'result_index': index,
                        'chunk_index': chunk_index,
                        'chunk_count': len(chunks),
                        'unit_index': (progress_meta or {}).get('start_unit_index', 1) + index,
                        'unit_offset': index,
                    },
                )

        results: list[list[str]] = [[] for _ in texts]
        completed_units: set[int] = set()

        for offset in range(0, len(jobs), effective_batch_size):
            self._raise_if_cancelled(should_cancel)
            batch = jobs[offset : offset + effective_batch_size]
            first_job = batch[0]
            progress_callback(
                ProgressEvent(
                    self._build_batch_message(progress_label, batch, progress_meta),
                    progress_percent=self._get_batch_progress_percent(batch, progress_meta),
                    total_units=(progress_meta or {}).get('total_units'),
                    transient=True,
                ),
            )

            tokenized_batch = [
                tokenizer.convert_ids_to_tokens(tokenizer.encode(job['text'], add_special_tokens=True))
                for job in batch
            ]
            translate_kwargs = {
                'beam_size': 4,
                'max_batch_size': effective_batch_size,
                'no_repeat_ngram_size': 3,
            }
            if self._model_config.model_type == 'm2m100':
                target_prefix = [tokenizer.lang_code_to_token[target_language]]
                translate_kwargs['target_prefix'] = [target_prefix] * len(batch)

            translated_batch = self._translator.translate_batch(
                tokenized_batch,
                **translate_kwargs,
            )

            for batch_index, output in enumerate(translated_batch):
                self._raise_if_cancelled(should_cancel)
                job = batch[batch_index]
                hypothesis = output.hypotheses[0]
                if self._model_config.model_type == 'm2m100':
                    hypothesis = hypothesis[1:]
                text = sanitize_translated_text(
                    tokenizer.decode(tokenizer.convert_tokens_to_ids(hypothesis), skip_special_tokens=True).strip(),
                )
                results[job['result_index']].append(text or job['text'])

                if job['result_index'] not in completed_units and len(results[job['result_index']]) == job['chunk_count']:
                    completed_units.add(job['result_index'])
                    completed_value = (progress_meta or {}).get('completed_units_before_batch', 0) + job['unit_offset'] + 1
                    progress_callback(
                        ProgressEvent(
                            tr(
                                self.ui_language,
                                'unit_completed',
                                progress_label=progress_label,
                                unit_index=job['unit_index'],
                                total_units=(progress_meta or {}).get('total_units', '?'),
                            ),
                            progress_percent=(completed_value / (progress_meta or {}).get('total_units', 1)) * 100,
                            completed_units=completed_value,
                            total_units=(progress_meta or {}).get('total_units'),
                            silent=True,
                        ),
                    )

        return [' '.join(chunks).strip() or texts[index] for index, chunks in enumerate(results)]

    def _translate_texts_remote(
        self,
        texts: list[str],
        *,
        source_language: str,
        target_language: str,
        progress_callback,
        progress_label: str,
        progress_meta: dict | None = None,
        batch_size: int | None = None,
        should_cancel=None,
    ) -> list[str]:
        self.ensure_model(source_language, target_language, progress_callback, should_cancel)
        effective_batch_size = batch_size or 24

        jobs: list[dict] = []
        for index, text in enumerate(texts):
            chunks = split_long_text(text)
            for chunk_index, chunk in enumerate(chunks):
                jobs.append(
                    {
                        'text': chunk,
                        'result_index': index,
                        'chunk_index': chunk_index,
                        'chunk_count': len(chunks),
                        'unit_index': (progress_meta or {}).get('start_unit_index', 1) + index,
                        'unit_offset': index,
                    },
                )

        results: list[list[str]] = [[] for _ in texts]
        completed_units: set[int] = set()

        for offset in range(0, len(jobs), effective_batch_size):
            self._raise_if_cancelled(should_cancel)
            batch = jobs[offset : offset + effective_batch_size]
            progress_callback(
                ProgressEvent(
                    self._build_batch_message(progress_label, batch, progress_meta),
                    progress_percent=self._get_batch_progress_percent(batch, progress_meta),
                    total_units=(progress_meta or {}).get('total_units'),
                    transient=True,
                ),
            )
            translated_batch = self._translate_remote_batch_with_retries(
                batch,
                source_language=source_language,
                target_language=target_language,
                progress_callback=progress_callback,
                progress_label=progress_label,
                progress_meta=progress_meta,
                should_cancel=should_cancel,
            )
            for batch_index, translated_text in enumerate(translated_batch):
                self._raise_if_cancelled(should_cancel)
                job = batch[batch_index]
                text = sanitize_translated_text(translated_text.strip())
                results[job['result_index']].append(text or job['text'])

                if job['result_index'] not in completed_units and len(results[job['result_index']]) == job['chunk_count']:
                    completed_units.add(job['result_index'])
                    completed_value = (progress_meta or {}).get('completed_units_before_batch', 0) + job['unit_offset'] + 1
                    progress_callback(
                        ProgressEvent(
                            tr(
                                self.ui_language,
                                'unit_completed',
                                progress_label=progress_label,
                                unit_index=job['unit_index'],
                                total_units=(progress_meta or {}).get('total_units', '?'),
                            ),
                            progress_percent=(completed_value / (progress_meta or {}).get('total_units', 1)) * 100,
                            completed_units=completed_value,
                            total_units=(progress_meta or {}).get('total_units'),
                            silent=True,
                        ),
                    )

        return [' '.join(chunks).strip() or texts[index] for index, chunks in enumerate(results)]

    def _translate_remote_batch_with_retries(
        self,
        batch: list[dict],
        *,
        source_language: str,
        target_language: str,
        progress_callback,
        progress_label: str,
        progress_meta: dict | None = None,
        should_cancel=None,
    ) -> list[str]:
        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            self._raise_if_cancelled(should_cancel)
            try:
                return create_translation_completion(
                    self.translation_provider,
                    api_key=self.remote_api_key,
                    model_id=self.remote_model_id,
                    source_language=source_language,
                    target_language=target_language,
                    texts=[job['text'] for job in batch],
                )
            except RemoteProviderError as error:
                if len(batch) > 1 and is_structured_response_error(error):
                    midpoint = max(len(batch) // 2, 1)
                    first_half = self._translate_remote_batch_with_retries(
                        batch[:midpoint],
                        source_language=source_language,
                        target_language=target_language,
                        progress_callback=progress_callback,
                        progress_label=progress_label,
                        progress_meta=progress_meta,
                        should_cancel=should_cancel,
                    )
                    second_half = self._translate_remote_batch_with_retries(
                        batch[midpoint:],
                        source_language=source_language,
                        target_language=target_language,
                        progress_callback=progress_callback,
                        progress_label=progress_label,
                        progress_meta=progress_meta,
                        should_cancel=should_cancel,
                    )
                    return first_half + second_half
                if error.status_code != 429 or attempt >= max_attempts:
                    raise
                retry_delay = max(error.retry_after_seconds or 2.0, 1.0)
                progress_callback(
                    ProgressEvent(
                        tr(
                            self.ui_language,
                            'remote_rate_limit_retry',
                            provider=tr(self.ui_language, f'translation_provider_{self.translation_provider}'),
                            wait_seconds=f'{retry_delay:.1f}',
                            attempt=attempt,
                            max_attempts=max_attempts,
                        ),
                        progress_percent=self._get_batch_progress_percent(batch, progress_meta),
                        total_units=(progress_meta or {}).get('total_units'),
                        transient=True,
                    ),
                )
                end_time = time.monotonic() + retry_delay
                while time.monotonic() < end_time:
                    self._raise_if_cancelled(should_cancel)
                    time.sleep(min(0.2, end_time - time.monotonic()))

        raise RemoteProviderError('No se ha podido completar el lote remoto tras varios reintentos.')

    @staticmethod
    def _resolve_model_config(source_language: str, target_language: str) -> ModelConfig:
        return EUSKERA_MODEL_CONFIGS.get((source_language, target_language), MODEL_CONFIG)

    def _build_batch_message(self, progress_label: str, batch: list[dict], progress_meta: dict | None) -> str:
        if len(batch) == 1:
            job = batch[0]
            suffix = (
                tr(
                    self.ui_language,
                    'chunk_suffix',
                    chunk_index=job['chunk_index'] + 1,
                    chunk_count=job['chunk_count'],
                )
                if job['chunk_count'] > 1
                else ''
            )
            return tr(
                self.ui_language,
                'single_unit_progress',
                progress_label=progress_label,
                unit_index=job['unit_index'],
                total_units=(progress_meta or {}).get('total_units', '?'),
                suffix=suffix,
            )

        first_job = batch[0]
        last_job = batch[-1]
        return tr(
            self.ui_language,
            'multi_unit_progress',
            progress_label=progress_label,
            first_unit=first_job['unit_index'],
            last_unit=last_job['unit_index'],
            total_units=(progress_meta or {}).get('total_units', '?'),
        )

    def _ensure_remote_provider(self, progress_callback) -> None:
        if not self.remote_api_key:
            raise ValueError(tr(self.ui_language, 'remote_api_key_missing'))
        if not self.remote_model_id:
            raise ValueError(tr(self.ui_language, 'remote_model_missing'))
        if self._remote_ready:
            return

        progress_callback(
            ProgressEvent(
                tr(
                    self.ui_language,
                    'remote_provider_ready',
                    provider=tr(self.ui_language, f'translation_provider_{self.translation_provider}'),
                    model_label=self.remote_model_id,
                ),
                active_model_label=f'{tr(self.ui_language, f"translation_provider_{self.translation_provider}")} · {self.remote_model_id}',
            ),
        )
        self._remote_ready = True

    @staticmethod
    def _get_batch_progress_percent(batch: list[dict], progress_meta: dict | None) -> float | None:
        if not progress_meta or not progress_meta.get('total_units'):
            return None

        first_job = batch[0]
        last_job = batch[-1]
        midpoint_units = (
            progress_meta.get('completed_units_before_batch', 0)
            + first_job['unit_offset']
            + (last_job['unit_offset'] - first_job['unit_offset'] + 1) / 2
        )
        return max(0.0, min(99.0, (midpoint_units / progress_meta['total_units']) * 100))

    @staticmethod
    def _build_runtime_profile(performance_mode: str) -> RuntimeProfile:
        if ctranslate2.get_cuda_device_count() > 0:
            batch_size_map = {
                'suave': 16,
                'equilibrado': 24,
                'rapido': 32,
                'maximo': 40,
            }
            batch_size = batch_size_map.get(performance_mode, 24)
            return RuntimeProfile(
                device='cuda',
                compute_type='int8_float16',
                inter_threads=1,
                intra_threads=1,
                batch_size=batch_size,
                cpu_count=os.cpu_count() or 1,
                reserved_cores=0,
                process_nice=0,
            )

        cpu_count = max(1, os.cpu_count() or 4)
        if performance_mode == 'suave':
            reserved_cores = 2 if cpu_count > 2 else 1
            worker_cap = 1
            thread_budget_ratio = 0.35
            batch_size_cap = 12
            process_nice = 10
        elif performance_mode == 'maximo':
            reserved_cores = 0
            worker_cap = 4
            thread_budget_ratio = 1.0
            batch_size_cap = 40
            process_nice = 0
        elif performance_mode == 'rapido':
            reserved_cores = 1 if cpu_count > 2 else 0
            worker_cap = 3
            thread_budget_ratio = 0.8
            batch_size_cap = 32
            process_nice = 0
        else:
            reserved_cores = 1 if cpu_count <= 4 else 2
            worker_cap = 2
            thread_budget_ratio = 0.55
            batch_size_cap = 16
            process_nice = 7

        usable_cores = max(1, cpu_count - reserved_cores)
        thread_budget = max(1, min(usable_cores, round(usable_cores * thread_budget_ratio)))
        inter_threads = min(worker_cap, thread_budget)
        intra_threads = max(1, min(4, thread_budget // inter_threads))
        batch_size = max(8, min(batch_size_cap, thread_budget * 2))

        return RuntimeProfile(
            device='cpu',
            compute_type='int8',
            inter_threads=inter_threads,
            intra_threads=intra_threads,
            batch_size=batch_size,
            cpu_count=cpu_count,
            reserved_cores=reserved_cores,
            process_nice=process_nice,
        )

    @staticmethod
    def _lower_process_priority(target_nice: int) -> bool:
        try:
            if target_nice <= 0:
                return False

            if os.name == 'nt':
                import ctypes

                priority_classes = {
                    0: 0x00000020,   # NORMAL_PRIORITY_CLASS
                    4: 0x00004000,   # BELOW_NORMAL_PRIORITY_CLASS
                    7: 0x00004000,
                    10: 0x00004000,
                }
                priority_class = priority_classes.get(target_nice, 0x00004000)
                process_handle = ctypes.windll.kernel32.GetCurrentProcess()
                return bool(ctypes.windll.kernel32.SetPriorityClass(process_handle, priority_class))

            current_nice = os.nice(0)
            if current_nice >= target_nice:
                return False

            os.nice(target_nice - current_nice)
            return True
        except Exception:
            return False

    def _raise_if_cancelled(self, should_cancel) -> None:
        if callable(should_cancel) and should_cancel():
            raise TranslationCancelledError(tr(self.ui_language, 'translation_cancelled'))
