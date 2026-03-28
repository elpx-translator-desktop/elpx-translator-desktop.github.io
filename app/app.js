import JSZip from 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm';

const LANGUAGE_OPTIONS = [
  ['ar', 'العربية'],
  ['bn', 'বাংলা'],
  ['es', 'Español'],
  ['en', 'English'],
  ['eu', 'Euskara'],
  ['fr', 'Français'],
  ['de', 'Deutsch'],
  ['it', 'Italiano'],
  ['nl', 'Nederlands'],
  ['pl', 'Polski'],
  ['pt', 'Português'],
  ['ca', 'Català'],
  ['gl', 'Galego'],
  ['ro', 'Română'],
  ['ru', 'Русский'],
  ['tr', 'Türkçe'],
  ['uk', 'Українська'],
  ['ur', 'اردو'],
  ['zh', '中文'],
];

const PROVIDERS = {
  openai: {
    label: 'OpenAI API',
    defaultModel: 'gpt-5-mini',
    defaultModels: ['gpt-5-mini', 'gpt-5-nano', 'gpt-4.1-mini'],
  },
  gemini: {
    label: 'Gemini API',
    defaultModel: 'gemini-2.5-flash',
    defaultModels: ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash'],
  },
  anthropic: {
    label: 'Anthropic API',
    defaultModel: 'claude-sonnet-4-5',
    defaultModels: ['claude-sonnet-4-5', 'claude-opus-4-1', 'claude-3-5-haiku-latest'],
  },
  deepseek: {
    label: 'DeepSeek API',
    defaultModel: 'deepseek-chat',
    defaultModels: ['deepseek-chat', 'deepseek-reasoner'],
  },
};

const HTML_TRANSLATABLE_ATTRIBUTES = ['alt', 'title', 'placeholder', 'aria-label', 'label'];
const EXCLUDED_HTML_TAGS = new Set(['code', 'pre', 'script', 'style', 'kbd', 'samp', 'math', 'svg']);
const JSON_SKIP_KEYS = new Set([
  'id',
  'ideviceId',
  'evaluationID',
  'typeGame',
  'activityType',
  'selectionType',
  'align',
  'width',
  'height',
  'color',
  'fontSize',
  'glassSize',
  'initialZSize',
  'maxZSize',
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
]);

const STORAGE_KEY = 'elpx-web-beta-settings';
const REFERENCE_RE = /^(asset:\/\/|https?:\/\/|mailto:|tel:|exe-node:|\{\{context_path\}\})/i;
const HASHLIKE_RE = /^[A-Za-z0-9_-]{20,}$/;
const HTML_RE = /<\/?[a-z][\s\S]*>/i;
const NUMERIC_LIST_PREFIX_RE = /^(?<prefix>\(?\d+\)?[.)](?:\s+)?)(?<rest>(?!\d)\S[\s\S]*)$/;
const JSON_NUMERIC_VALUE_RE = /^[+-]?\d+(?:[.,]\d+)?$/;
const HEX_COLOR_RE = /^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$/;
const TIME_LIKE_RE = /^\d{1,2}:\d{2}(?::\d{2})?$/;
const DATE_LIKE_RE = /^\d{1,2}\/\d{1,2}\/\d{2,4}$/;
const PERCENT_ENCODED_CHUNK_RE = /%[0-9A-Fa-f]{2}/g;
const BASE64ISH_RE = /^[A-Za-z0-9+/=_-]{80,}$/;
const DEFAULT_BATCH_SIZE = 8;
const CUSTOM_TARGET_LANGUAGE_VALUE = '__custom_target__';

const elements = {
  form: document.getElementById('translator-form'),
  inputFile: document.getElementById('input-file'),
  sourceLanguage: document.getElementById('source-language'),
  targetLanguage: document.getElementById('target-language'),
  customTargetField: document.getElementById('custom-target-field'),
  customTargetLanguage: document.getElementById('custom-target-language'),
  provider: document.getElementById('provider'),
  model: document.getElementById('model'),
  loadModelsButton: document.getElementById('load-models-button'),
  apiKey: document.getElementById('api-key'),
  clearApiKeyButton: document.getElementById('clear-api-key-button'),
  translateButton: document.getElementById('translate-button'),
  resetButton: document.getElementById('reset-button'),
  progress: document.getElementById('progress'),
  statusBadge: document.getElementById('status-badge'),
  statusText: document.getElementById('status-text'),
  statusDetail: document.getElementById('status-detail'),
  resultCard: document.getElementById('result-card'),
  resultText: document.getElementById('result-text'),
  downloadLink: document.getElementById('download-link'),
};

let activeDownloadUrl = null;

class TranslationPlanner {
  constructor() {
    this.cache = new Map();
    this.queue = new Map();
  }

  enqueue(text, apply) {
    if (this.cache.has(text)) {
      apply(this.cache.get(text));
      return;
    }

    const callbacks = this.queue.get(text) || [];
    callbacks.push(apply);
    this.queue.set(text, callbacks);
  }

  get size() {
    return this.queue.size;
  }

  async flush(translator, context, onProgress) {
    const uniqueTexts = [...this.queue.keys()];
    const total = uniqueTexts.length;

    if (!total) {
      onProgress({ status: 'No hay texto pendiente de traducir.', detail: '', progress: 100 });
      return;
    }

    onProgress({
      status: `Enviando ${total} bloques únicos al proveedor remoto.`,
      detail: 'Preparando lotes...',
      progress: 6,
    });

    const translatedMap = await translator.translateMany(uniqueTexts, context, (message) => {
      const percent = 6 + Math.round((message.completed / total) * 82);
      onProgress({
        status: `Traduciendo bloques ${message.completed} de ${total}.`,
        detail: message.detail,
        progress: percent,
      });
    });

    for (const [sourceText, translatedText] of translatedMap.entries()) {
      this.cache.set(sourceText, translatedText);
      const callbacks = this.queue.get(sourceText) || [];
      for (const callback of callbacks) {
        callback(translatedText);
      }
    }
  }
}

class RemoteTranslator {
  constructor({ provider, model, apiKey, batchSize }) {
    this.provider = provider;
    this.model = model;
    this.apiKey = apiKey;
    this.batchSize = batchSize;
  }

  async translateMany(texts, context, onBatchProgress) {
    const chunkJobs = [];
    const textRanges = [];

    for (const text of texts) {
      const chunks = splitLongText(text);
      const start = chunkJobs.length;
      for (const chunk of chunks) {
        chunkJobs.push(chunk);
      }
      textRanges.push({ text, start, count: chunks.length });
    }

    const translatedChunks = new Array(chunkJobs.length);
    let completedChunks = 0;

    for (let offset = 0; offset < chunkJobs.length; offset += this.batchSize) {
      const batch = chunkJobs.slice(offset, offset + this.batchSize);
      const batchResult = await this.requestBatch(batch, context);
      for (let index = 0; index < batch.length; index += 1) {
        translatedChunks[offset + index] = sanitizeTranslatedText(batchResult[index] || batch[index]);
      }
      completedChunks += batch.length;
      onBatchProgress({
        completed: Math.min(completedChunks, chunkJobs.length),
        detail: `Lote ${Math.ceil(completedChunks / this.batchSize)} completado.`,
      });
    }

    const results = new Map();
    for (const { text, start, count } of textRanges) {
      const chunks = translatedChunks.slice(start, start + count);
      results.set(text, chunks.join(' ').trim() || text);
    }

    return results;
  }

  async requestBatch(texts, { sourceLanguage, targetLanguage }) {
    const systemPrompt = [
      'You are a translation engine for .elpx educational projects.',
      'Translate each item from the source language to the target language.',
      'Return only valid JSON with this shape: {"translations":["..."]}.',
      'Preserve order and array length exactly.',
      'Do not omit items.',
      'Keep placeholders, variable names, URLs, HTML entities, XML fragments, HTML tags, whitespace-only items,',
      'and tokens like {{...}}, [[...]], __...__, %s, {0}, <code>, &nbsp; unchanged when they appear.',
      'Do not explain anything.',
    ].join(' ');

    const payload = {
      source_language: sourceLanguage,
      target_language: targetLanguage,
      texts,
    };

    let rawContent = '';
    if (this.provider === 'anthropic') {
      rawContent = await this.callAnthropic(systemPrompt, payload);
    } else {
      rawContent = await this.callOpenAiCompatible(systemPrompt, payload);
    }

    const data = extractJsonObject(rawContent);
    const translations = Array.isArray(data?.translations) ? data.translations : null;
    if (!translations || translations.length !== texts.length) {
      throw new Error('La respuesta remota no devolvió una lista de traducciones válida.');
    }
    return translations.map((item) => (typeof item === 'string' ? item : String(item)));
  }

  async callOpenAiCompatible(systemPrompt, payload) {
    const config = {
      openai: {
        url: 'https://api.openai.com/v1/chat/completions',
        headers: { Authorization: `Bearer ${this.apiKey}` },
      },
      gemini: {
        url: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions',
        headers: { Authorization: `Bearer ${this.apiKey}` },
      },
      deepseek: {
        url: 'https://api.deepseek.com/v1/chat/completions',
        headers: { Authorization: `Bearer ${this.apiKey}` },
      },
    }[this.provider];

    if (!config) {
      throw new Error(`Proveedor no soportado: ${this.provider}`);
    }

    const response = await fetch(config.url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
      body: JSON.stringify({
        model: this.model,
        response_format: { type: 'json_object' },
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: JSON.stringify(payload) },
        ],
      }),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(extractProviderError(data, response.status));
    }

    return data?.choices?.[0]?.message?.content || '';
  }

  async callAnthropic(systemPrompt, payload) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: this.model,
        max_tokens: 4096,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: JSON.stringify(payload),
          },
        ],
      }),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(extractProviderError(data, response.status));
    }

    const content = Array.isArray(data?.content) ? data.content : [];
    return content
      .filter((item) => item?.type === 'text')
      .map((item) => item.text || '')
      .join('\n');
  }
}

function fillSelect(select, options, selectedValue) {
  select.innerHTML = options
    .map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`)
    .join('');
  select.value = selectedValue;
}

function fillTargetLanguageOptions(selectedValue) {
  const options = [...LANGUAGE_OPTIONS, [CUSTOM_TARGET_LANGUAGE_VALUE, 'Otro código de idioma']];
  elements.targetLanguage.innerHTML = options
    .map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`)
    .join('');
  elements.targetLanguage.value = selectedValue;
}

function fillProviderOptions() {
  elements.provider.innerHTML = Object.entries(PROVIDERS)
    .map(([value, config]) => `<option value="${escapeHtml(value)}">${escapeHtml(config.label)}</option>`)
    .join('');
}

function loadSavedSettings() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    return {};
  }
}

function saveSettings() {
  const saved = loadSavedSettings();
  const providerApiKeys = {
    ...(saved.providerApiKeys || {}),
    [elements.provider.value]: elements.apiKey.value,
  };
  const providerModels = {
    ...(saved.providerModels || {}),
    [elements.provider.value]: elements.model.value.trim(),
  };

  const payload = {
    sourceLanguage: elements.sourceLanguage.value,
    targetLanguage: elements.targetLanguage.value,
    customTargetLanguage: elements.customTargetLanguage.value.trim(),
    provider: elements.provider.value,
    providerApiKeys,
    providerModels,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function isCustomTargetSelected() {
  return elements.targetLanguage.value === CUSTOM_TARGET_LANGUAGE_VALUE;
}

function toggleCustomTargetVisibility() {
  const visible = isCustomTargetSelected();
  elements.customTargetField.classList.toggle('hidden', !visible);
}

function selectedTargetLanguage() {
  if (isCustomTargetSelected()) {
    return elements.customTargetLanguage.value.trim();
  }
  return elements.targetLanguage.value;
}

function isValidCustomTargetLanguage(value) {
  if (!value || value.length > 15) {
    return false;
  }
  return /^[A-Za-z0-9_-]+$/.test(value);
}

async function fetchJson(url, headers) {
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      ...headers,
    },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(extractProviderError(data, response.status));
  }
  return data;
}

function isValidRemoteModel(provider, modelId) {
  if (!modelId) {
    return false;
  }

  const lowered = modelId.toLowerCase();
  if (provider === 'openai') {
    const excluded = ['audio', 'realtime', 'transcribe', 'tts', 'whisper', 'dall', 'embedding', 'moderation', 'search', 'omni-moderation', 'computer-use', 'image'];
    return lowered.startsWith('gpt-') && !excluded.some((marker) => lowered.includes(marker));
  }
  if (provider === 'gemini') {
    return lowered.startsWith('gemini-');
  }
  if (provider === 'anthropic') {
    return lowered.startsWith('claude-');
  }
  if (provider === 'deepseek') {
    return lowered.startsWith('deepseek-');
  }
  return false;
}

function remoteModelSortKey(left, right) {
  const preferredOrder = {
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
  };
  const leftRank = preferredOrder[left] ?? 999;
  const rightRank = preferredOrder[right] ?? 999;
  if (leftRank !== rightRank) {
    return leftRank - rightRank;
  }
  return left.localeCompare(right);
}

async function listAvailableModels(provider, apiKey) {
  if (provider === 'openai') {
    const payload = await fetchJson('https://api.openai.com/v1/models', {
      Authorization: `Bearer ${apiKey}`,
    });
    return [...new Set(
      (payload?.data || [])
        .map((item) => item?.id || '')
        .filter((id) => isValidRemoteModel(provider, id)),
    )].sort(remoteModelSortKey);
  }

  if (provider === 'gemini') {
    const payload = await fetchJson('https://generativelanguage.googleapis.com/v1beta/models', {
      'x-goog-api-key': apiKey,
    });
    return [...new Set(
      (payload?.models || [])
        .map((item) => String(item?.name || '').split('/', 2)[1] || '')
        .filter((id) => isValidRemoteModel(provider, id)),
    )].sort(remoteModelSortKey);
  }

  if (provider === 'anthropic') {
    const payload = await fetchJson('https://api.anthropic.com/v1/models', {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    });
    return [...new Set(
      (payload?.data || [])
        .map((item) => item?.id || '')
        .filter((id) => isValidRemoteModel(provider, id)),
    )].sort(remoteModelSortKey);
  }

  if (provider === 'deepseek') {
    const payload = await fetchJson('https://api.deepseek.com/v1/models', {
      Authorization: `Bearer ${apiKey}`,
    });
    return [...new Set(
      (payload?.data || [])
        .map((item) => item?.id || '')
        .filter((id) => isValidRemoteModel(provider, id)),
    )].sort(remoteModelSortKey);
  }

  return [];
}

function renderModelOptions(models) {
  const currentValue = elements.model.value;
  elements.model.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model)}">${escapeHtml(model)}</option>`)
    .join('');
  const nextValue = models.includes(currentValue) ? currentValue : models[0];
  if (nextValue) {
    elements.model.value = nextValue;
  }
}

function applyProviderDefaults(force = false) {
  const saved = loadSavedSettings();
  const provider = PROVIDERS[elements.provider.value];
  if (!provider) {
    return;
  }

  const savedModels = saved.providerModels || {};
  const savedModel = typeof savedModels[elements.provider.value] === 'string' ? savedModels[elements.provider.value].trim() : '';
  const currentValue = savedModel || elements.model.value.trim();
  if (force || !currentValue || !provider.defaultModels.includes(currentValue)) {
    renderModelOptions(provider.defaultModels);
    elements.model.value = provider.defaultModel;
    return;
  }
  renderModelOptions(provider.defaultModels);
  elements.model.value = currentValue;
}

function syncApiDependentControls() {
  const hasApiKey = Boolean(elements.apiKey.value.trim());
  elements.model.disabled = !hasApiKey;
  elements.loadModelsButton.disabled = !hasApiKey;
  elements.clearApiKeyButton.disabled = !hasApiKey;
}

function setBusy(isBusy) {
  elements.translateButton.disabled = isBusy;
  elements.resetButton.disabled = isBusy;
  elements.form.querySelectorAll('input, select').forEach((field) => {
    field.disabled = isBusy;
  });
  if (!isBusy) {
    syncApiDependentControls();
  } else {
    elements.loadModelsButton.disabled = true;
    elements.clearApiKeyButton.disabled = true;
  }
}

function setStatus(message, { detail = '', progress = null, isError = false } = {}) {
  elements.statusBadge.textContent = isError ? 'Error' : 'En proceso';
  elements.statusBadge.classList.toggle('is-error', isError);
  if (progress === null) {
    elements.progress.removeAttribute('value');
  } else {
    elements.progress.value = progress;
  }
  elements.statusText.textContent = message;
  elements.statusDetail.textContent = detail;
}

function setIdleStatus() {
  elements.statusBadge.textContent = 'Listo para empezar';
  elements.statusBadge.classList.remove('is-error');
  elements.progress.value = 0;
  elements.statusText.textContent = 'Selecciona un archivo, configura el proveedor y lanza la traducción.';
  elements.statusDetail.textContent = '';
}

function setDoneStatus(message, detail = '') {
  elements.statusBadge.textContent = 'Completado';
  elements.statusBadge.classList.remove('is-error');
  elements.progress.value = 100;
  elements.statusText.textContent = message;
  elements.statusDetail.textContent = detail;
}

function clearResult() {
  if (activeDownloadUrl) {
    URL.revokeObjectURL(activeDownloadUrl);
    activeDownloadUrl = null;
  }
  elements.resultCard.classList.add('hidden');
  elements.resultText.textContent = '';
  elements.downloadLink.removeAttribute('href');
}

function showResult(blob, filename) {
  clearResult();
  activeDownloadUrl = URL.createObjectURL(blob);
  elements.resultCard.classList.remove('hidden');
  elements.resultText.textContent = `Archivo generado: ${filename}`;
  elements.downloadLink.href = activeDownloadUrl;
  elements.downloadLink.download = filename;
}

async function translateElpxFile(file, settings) {
  const zip = await JSZip.loadAsync(await file.arrayBuffer());
  const contentXmlPath = findContentXmlPath(Object.keys(zip.files));
  if (!contentXmlPath) {
    throw new Error('No se encontró content.xml dentro del archivo .elpx.');
  }

  const xmlContent = await zip.file(contentXmlPath).async('string');
  const xmlDocument = parseXml(xmlContent);
  const planner = new TranslationPlanner();
  const finalizers = [];

  processStructuralNodes(xmlDocument, planner);
  processComponents(xmlDocument, planner, finalizers);
  replaceProjectLanguage(xmlDocument, settings.targetLanguage);

  const translator = new RemoteTranslator(settings);
  await planner.flush(
    translator,
    {
      sourceLanguage: settings.sourceLanguage,
      targetLanguage: settings.targetLanguage,
    },
    ({ status, detail, progress }) => setStatus(status, { detail, progress }),
  );

  for (const finalize of finalizers) {
    finalize();
  }

  const translatedXml = serializeXml(xmlDocument, xmlContent);
  zip.file(contentXmlPath, translatedXml);
  const outputBlob = await zip.generateAsync({ type: 'blob' });
  return {
    blob: outputBlob,
    filename: buildOutputFilename(file.name, settings.targetLanguage),
    queuedUnits: planner.size,
  };
}

function processStructuralNodes(xmlDocument, planner) {
  for (const tagName of ['pageName', 'blockName']) {
    for (const node of [...xmlDocument.getElementsByTagName(tagName)]) {
      const text = getNodeText(node).trim();
      if (!isTranslatableText(text)) {
        continue;
      }
      enqueuePlainText(planner, text, (translated) => replaceNodeText(node, translated));
    }
  }

  for (const [propertyTag, allowedKeys] of [
    ['odeNavStructureProperty', new Set(['titlePage', 'titleNode'])],
    ['odeProperty', new Set(['pp_title', 'pp_description'])],
  ]) {
    for (const node of getPropertyValueNodes(xmlDocument, propertyTag, allowedKeys)) {
      const text = getNodeText(node).trim();
      if (!isTranslatableText(text)) {
        continue;
      }
      enqueuePlainText(planner, text, (translated) => replaceNodeText(node, translated));
    }
  }
}

function processComponents(xmlDocument, planner, finalizers) {
  for (const component of [...xmlDocument.getElementsByTagName('odeComponent')]) {
    const htmlNode = component.getElementsByTagName('htmlView')[0];
    if (htmlNode) {
      const html = getNodeText(htmlNode);
      if (html.trim()) {
        const holder = { html };
        processHtmlFragment(holder, planner, finalizers);
        finalizers.push(() => replaceNodeWithCdata(htmlNode, holder.html));
      }
    }

    const jsonNode = component.getElementsByTagName('jsonProperties')[0];
    if (jsonNode) {
      const rawJson = getNodeText(jsonNode).trim();
      if (!rawJson) {
        continue;
      }
      try {
        const parsed = JSON.parse(rawJson);
        processJsonValue({ root: parsed }, 'root', planner, finalizers);
        finalizers.push(() => replaceNodeWithCdata(jsonNode, JSON.stringify(parsed)));
      } catch {
        // Invalid jsonProperties blocks are left untouched in this MVP.
      }
    }
  }
}

function processHtmlFragment(holder, planner, finalizers) {
  if (!holder.html.trim()) {
    return;
  }

  const template = document.createElement('template');
  template.innerHTML = holder.html;

  const walk = (node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      const parent = node.parentElement;
      const rawText = node.nodeValue || '';
      const trimmed = rawText.trim();

      if (looksLikeJsonPayload(trimmed)) {
        try {
          const parsed = JSON.parse(trimmed);
          processJsonValue({ root: parsed }, 'root', planner, finalizers);
          const [leading, , trailing] = splitSurroundingWhitespace(rawText);
          finalizers.push(() => {
            node.nodeValue = `${leading}${JSON.stringify(parsed)}${trailing}`;
          });
        } catch {
          // Ignore malformed inline JSON.
        }
        return;
      }

      const [leading, core, trailing] = splitSurroundingWhitespace(rawText);
      if (shouldTranslateHtmlText(parent, core)) {
        enqueuePlainText(planner, core, (translated) => {
          node.nodeValue = `${leading}${translated}${trailing}`;
        });
      }
      return;
    }

    if (node.nodeType !== Node.ELEMENT_NODE) {
      return;
    }

    if (!EXCLUDED_HTML_TAGS.has(node.tagName.toLowerCase())) {
      for (const attribute of HTML_TRANSLATABLE_ATTRIBUTES) {
        const value = node.getAttribute(attribute);
        if (typeof value === 'string' && isTranslatableText(value)) {
          enqueuePlainText(planner, value, (translated) => {
            node.setAttribute(attribute, translated);
          });
        }
      }
    }

    for (const child of [...node.childNodes]) {
      walk(child);
    }
  };

  for (const child of [...template.content.childNodes]) {
    walk(child);
  }

  finalizers.push(() => {
    holder.html = template.innerHTML;
  });
}

function processJsonValue(container, key, planner, finalizers) {
  const value = container[key];
  if (shouldSkipJsonSubtree(key, value)) {
    return;
  }

  if (typeof value === 'string') {
    if (shouldSkipJsonValue(key, value)) {
      return;
    }

    if (looksLikeJsonPayload(value)) {
      try {
        const parsed = JSON.parse(value);
        if (shouldSkipSerializedJsonPayload(parsed)) {
          return;
        }
        processJsonValue({ root: parsed }, 'root', planner, finalizers);
        finalizers.push(() => {
          container[key] = JSON.stringify(parsed);
        });
        return;
      } catch {
        return;
      }
    }

    if (looksLikeHtml(value)) {
      const holder = { html: value };
      processHtmlFragment(holder, planner, finalizers);
      finalizers.push(() => {
        container[key] = holder.html;
      });
      return;
    }

    enqueuePlainText(planner, value, (translated) => {
      container[key] = translated;
    });
    return;
  }

  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      processJsonValue(value, index, planner, finalizers);
    }
    return;
  }

  if (value && typeof value === 'object') {
    for (const childKey of Object.keys(value)) {
      processJsonValue(value, childKey, planner, finalizers);
    }
  }
}

function replaceProjectLanguage(xmlDocument, targetLanguage) {
  for (const node of getPropertyValueNodes(xmlDocument, 'odeProperty', new Set(['pp_lang']))) {
    replaceNodeText(node, targetLanguage);
  }
}

function enqueuePlainText(planner, text, apply) {
  const [prefix, core] = splitNumericListPrefix(text);
  if (!isTranslatableText(core)) {
    apply(text);
    return;
  }
  planner.enqueue(core, (translated) => apply(`${prefix}${translated}`));
}

function parseXml(xmlContent) {
  const xmlDocument = new DOMParser().parseFromString(xmlContent, 'application/xml');
  if (xmlDocument.querySelector('parsererror')) {
    throw new Error('No se pudo analizar content.xml.');
  }
  return xmlDocument;
}

function serializeXml(xmlDocument, originalXml) {
  const declarationMatch = originalXml.match(/^\s*<\?xml[^>]+\?>/);
  const doctypeMatch = originalXml.match(/<!DOCTYPE[^>]+>/);
  const serializer = new XMLSerializer();
  const rootXml = serializer.serializeToString(xmlDocument.documentElement);
  const parts = [declarationMatch?.[0] || '<?xml version="1.0" encoding="UTF-8"?>'];
  if (doctypeMatch?.[0]) {
    parts.push(doctypeMatch[0]);
  }
  parts.push(rootXml);
  return parts.join('\n');
}

function getNodeText(node) {
  let text = '';
  for (const child of [...node.childNodes]) {
    if (child.nodeType === Node.TEXT_NODE || child.nodeType === Node.CDATA_SECTION_NODE) {
      text += child.nodeValue || '';
    }
  }
  return text;
}

function getPropertyValueNodes(xmlDocument, propertyTag, allowedKeys) {
  const results = [];
  for (const propertyNode of [...xmlDocument.getElementsByTagName(propertyTag)]) {
    const keyNode = propertyNode.getElementsByTagName('key')[0];
    const valueNode = propertyNode.getElementsByTagName('value')[0];
    const key = keyNode ? getNodeText(keyNode).trim() : '';
    if (!valueNode || !allowedKeys.has(key)) {
      continue;
    }
    results.push(valueNode);
  }
  return results;
}

function replaceNodeText(node, text) {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
  node.appendChild(node.ownerDocument.createTextNode(text));
}

function replaceNodeWithCdata(node, text) {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }

  const chunks = text.split(']]>');
  chunks.forEach((chunk, index) => {
    const suffix = index < chunks.length - 1 ? ']]' : '';
    node.appendChild(node.ownerDocument.createCDATASection(`${chunk}${suffix}`));
    if (index < chunks.length - 1) {
      node.appendChild(node.ownerDocument.createTextNode('>'));
    }
  });
}

function findContentXmlPath(names) {
  if (names.includes('content.xml')) {
    return 'content.xml';
  }
  return names.find((name) => name.endsWith('/content.xml')) || null;
}

function buildOutputFilename(filename, targetLanguage) {
  const dotIndex = filename.toLowerCase().lastIndexOf('.elpx');
  if (dotIndex === -1) {
    return `${filename}-${targetLanguage}.elpx`;
  }
  return `${filename.slice(0, dotIndex)}-${targetLanguage}.elpx`;
}

function splitLongText(text, maxLength = 420) {
  const normalized = text.trim();
  if (normalized.length <= maxLength) {
    return [normalized];
  }

  const chunks = [];
  const paragraphs = normalized.split(/\n{2,}/);
  for (const paragraph of paragraphs) {
    const trimmedParagraph = paragraph.trim();
    if (!trimmedParagraph) {
      continue;
    }

    if (trimmedParagraph.length <= maxLength) {
      chunks.push(trimmedParagraph);
      continue;
    }

    const sentences = trimmedParagraph.match(/[^.!?\n]+(?:[.!?\n]+|$)/g) || [trimmedParagraph];
    let currentChunk = '';

    for (const sentenceRaw of sentences) {
      const sentence = sentenceRaw.trim();
      const candidate = currentChunk ? `${currentChunk} ${sentence}` : sentence;
      if (candidate.length <= maxLength) {
        currentChunk = candidate;
        continue;
      }

      if (currentChunk) {
        chunks.push(currentChunk);
      }

      if (sentence.length <= maxLength) {
        currentChunk = sentence;
        continue;
      }

      let wordChunk = '';
      for (const word of sentence.split(/\s+/)) {
        const wordCandidate = wordChunk ? `${wordChunk} ${word}` : word;
        if (wordCandidate.length <= maxLength) {
          wordChunk = wordCandidate;
        } else {
          if (wordChunk) {
            chunks.push(wordChunk);
          }
          wordChunk = word;
        }
      }
      currentChunk = wordChunk;
    }

    if (currentChunk) {
      chunks.push(currentChunk);
    }
  }

  return chunks.length ? chunks : [normalized];
}

function isTranslatableText(text) {
  if (!text || !text.trim()) {
    return false;
  }
  const trimmed = text.trim();
  if (!/[\p{L}\p{N}]/u.test(trimmed)) {
    return false;
  }
  if (REFERENCE_RE.test(trimmed)) {
    return false;
  }
  if (HASHLIKE_RE.test(trimmed)) {
    return false;
  }
  return true;
}

function looksLikeHtml(value) {
  return HTML_RE.test(value);
}

function looksLikeReference(value) {
  return REFERENCE_RE.test(value.trim());
}

function looksLikeNontranslatableScalar(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return true;
  }
  if (JSON_NUMERIC_VALUE_RE.test(trimmed)) {
    return true;
  }
  if (TIME_LIKE_RE.test(trimmed)) {
    return true;
  }
  if (DATE_LIKE_RE.test(trimmed)) {
    return true;
  }
  return HEX_COLOR_RE.test(trimmed);
}

function sanitizeTranslatedText(text) {
  return text.replace(/\s*<unk>\s*/gi, ' ').replace(/\s{2,}/g, ' ').trim();
}

function splitSurroundingWhitespace(text) {
  const leading = (text.match(/^\s*/) || [''])[0];
  const trailing = (text.match(/\s*$/) || [''])[0];
  const core = text.slice(leading.length, text.length - trailing.length);
  return [leading, core, trailing];
}

function splitNumericListPrefix(text) {
  const match = text.match(NUMERIC_LIST_PREFIX_RE);
  if (!match?.groups) {
    return ['', text];
  }
  return [match.groups.prefix, match.groups.rest];
}

function looksLikeEncodedPayload(value) {
  const trimmed = value.trim();
  if (trimmed.length < 32) {
    return false;
  }

  const percentChunks = trimmed.match(PERCENT_ENCODED_CHUNK_RE) || [];
  if (percentChunks.length && (percentChunks.length * 3) >= (trimmed.length * 0.3)) {
    return true;
  }
  return BASE64ISH_RE.test(trimmed);
}

function looksLikeJsonPayload(value) {
  const trimmed = value.trim();
  if (trimmed.length < 2) {
    return false;
  }
  const wrapped = (trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'));
  if (!wrapped) {
    return false;
  }
  try {
    const parsed = JSON.parse(trimmed);
    return Array.isArray(parsed) || (parsed && typeof parsed === 'object');
  } catch {
    return false;
  }
}

function shouldSkipJsonValue(key, value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return true;
  }
  if (JSON_SKIP_KEYS.has(String(key))) {
    return true;
  }
  if (String(key).toLowerCase().endsWith('type') && /^[A-Za-z][A-Za-z0-9-]*$/.test(trimmed)) {
    return true;
  }
  if (looksLikeNontranslatableScalar(trimmed)) {
    return true;
  }
  if (looksLikeReference(trimmed)) {
    return true;
  }
  if (looksLikeEncodedPayload(trimmed)) {
    return true;
  }
  if (/^[A-Za-z0-9_-]{20,}$/.test(trimmed)) {
    return true;
  }
  return false;
}

function shouldSkipJsonSubtree(key, value) {
  return key === 'msgs' && value && typeof value === 'object' && !Array.isArray(value);
}

function shouldSkipSerializedJsonPayload(value) {
  return value && typeof value === 'object' && !Array.isArray(value) && value.msgs && typeof value.msgs === 'object';
}

function shouldTranslateHtmlText(parent, text) {
  if (!(parent instanceof Element)) {
    return false;
  }
  if (EXCLUDED_HTML_TAGS.has(parent.tagName.toLowerCase())) {
    return false;
  }

  const trimmed = text.trim();
  if (looksLikeEncodedPayload(trimmed)) {
    return false;
  }
  if (looksLikeJsonPayload(trimmed)) {
    return false;
  }
  if (looksLikeNontranslatableScalar(trimmed)) {
    return false;
  }
  return isTranslatableText(trimmed);
}

function extractJsonObject(content) {
  if (!content) {
    return null;
  }
  if (typeof content === 'object') {
    return content;
  }
  try {
    return JSON.parse(content);
  } catch {
    const start = content.indexOf('{');
    const end = content.lastIndexOf('}');
    if (start !== -1 && end > start) {
      try {
        return JSON.parse(content.slice(start, end + 1));
      } catch {
        return null;
      }
    }
    return null;
  }
}

function extractProviderError(data, status) {
  const messages = [
    data?.error?.message,
    data?.message,
    data?.detail,
    typeof data?.error === 'string' ? data.error : '',
  ].filter(Boolean);
  return messages[0] || `Error remoto ${status}.`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function initializeForm() {
  const saved = loadSavedSettings();
  fillSelect(elements.sourceLanguage, LANGUAGE_OPTIONS, saved.sourceLanguage || 'es');
  const savedTarget = saved.customTargetLanguage ? CUSTOM_TARGET_LANGUAGE_VALUE : (saved.targetLanguage || 'en');
  fillTargetLanguageOptions(savedTarget);
  fillProviderOptions();
  elements.provider.value = saved.provider || 'openai';
  applyProviderDefaults(true);
  renderModelOptions(PROVIDERS[elements.provider.value]?.defaultModels || []);
  if (typeof saved.customTargetLanguage === 'string') {
    elements.customTargetLanguage.value = saved.customTargetLanguage;
  }
  const savedApiKey = saved.providerApiKeys?.[elements.provider.value];
  if (typeof savedApiKey === 'string') {
    elements.apiKey.value = savedApiKey;
  }
  const savedModel = saved.providerModels?.[elements.provider.value];
  if (typeof savedModel === 'string' && savedModel.trim()) {
    const providerDefaults = PROVIDERS[elements.provider.value]?.defaultModels || [];
    const options = providerDefaults.includes(savedModel) ? providerDefaults : [...providerDefaults, savedModel];
    renderModelOptions(options);
    elements.model.value = savedModel;
  }
  toggleCustomTargetVisibility();
  syncApiDependentControls();
}

elements.provider.addEventListener('change', () => {
  const saved = loadSavedSettings();
  const provider = elements.provider.value;
  const providerApiKey = saved.providerApiKeys?.[provider];
  const providerModel = saved.providerModels?.[provider];

  elements.apiKey.value = typeof providerApiKey === 'string' ? providerApiKey : '';
  applyProviderDefaults(true);
  if (typeof providerModel === 'string' && providerModel.trim()) {
    const providerDefaults = PROVIDERS[provider]?.defaultModels || [];
    const options = providerDefaults.includes(providerModel) ? providerDefaults : [...providerDefaults, providerModel];
    renderModelOptions(options);
    elements.model.value = providerModel;
  }
  syncApiDependentControls();
  saveSettings();
});
elements.sourceLanguage.addEventListener('change', saveSettings);
elements.targetLanguage.addEventListener('change', () => {
  toggleCustomTargetVisibility();
  saveSettings();
});
elements.customTargetLanguage.addEventListener('input', saveSettings);
elements.model.addEventListener('change', saveSettings);
elements.apiKey.addEventListener('input', () => {
  syncApiDependentControls();
  saveSettings();
});

elements.clearApiKeyButton.addEventListener('click', () => {
  const saved = loadSavedSettings();
  const providerApiKeys = {
    ...(saved.providerApiKeys || {}),
    [elements.provider.value]: '',
  };
  elements.apiKey.value = '';
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    ...saved,
    providerApiKeys,
  }));
  syncApiDependentControls();
});

elements.resetButton.addEventListener('click', () => {
  elements.form.reset();
  initializeForm();
  elements.apiKey.value = '';
  syncApiDependentControls();
  clearResult();
  setIdleStatus();
});

elements.loadModelsButton.addEventListener('click', async () => {
  const provider = elements.provider.value;
  const apiKey = elements.apiKey.value.trim();

  if (!apiKey) {
    setStatus('Escribe primero tu clave API.', { isError: true, progress: 0 });
    return;
  }

  elements.loadModelsButton.disabled = true;
  setStatus('Recuperando modelos disponibles...', { progress: 5 });

  try {
    const models = await listAvailableModels(provider, apiKey);
    if (!models.length) {
      setStatus('No se han encontrado modelos para este servicio.', { isError: true, progress: 0 });
      return;
    }
    renderModelOptions(models);
    elements.model.value = models[0];
    saveSettings();
    setDoneStatus('Modelos recuperados.', `${models.length} modelos disponibles.`);
  } catch (error) {
    setStatus(error instanceof Error ? error.message : 'No se pudieron cargar los modelos.', {
      isError: true,
      progress: 0,
    });
  } finally {
    elements.loadModelsButton.disabled = false;
  }
});

elements.form.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearResult();

  const file = elements.inputFile.files?.[0];
  const sourceLanguage = elements.sourceLanguage.value;
  const targetLanguage = selectedTargetLanguage();
  const provider = elements.provider.value;
  const model = elements.model.value.trim();
  const apiKey = elements.apiKey.value.trim();

  if (!file) {
    setStatus('Falta el archivo `.elpx`.', { isError: true, progress: 0 });
    return;
  }
  if (!model) {
    setStatus('Falta el identificador del modelo.', { isError: true, progress: 0 });
    return;
  }
  if (!apiKey) {
    setStatus('Falta la clave API.', { isError: true, progress: 0 });
    return;
  }
  if (sourceLanguage === targetLanguage) {
    setStatus('El idioma de origen y el de destino no pueden ser iguales.', { isError: true, progress: 0 });
    return;
  }
  if (isCustomTargetSelected() && !isValidCustomTargetLanguage(targetLanguage)) {
    setStatus('El código de idioma no es válido.', { isError: true, progress: 0 });
    return;
  }

  saveSettings();
  setBusy(true);
  setStatus('Abriendo el archivo `.elpx`...', { progress: 2 });

  try {
    const result = await translateElpxFile(file, {
      sourceLanguage,
      targetLanguage,
      provider,
      model,
      apiKey,
      batchSize: DEFAULT_BATCH_SIZE,
    });

    showResult(result.blob, result.filename);
    setDoneStatus('Traducción terminada.', `${result.queuedUnits} bloques únicos procesados.`);
  } catch (error) {
    setStatus(error instanceof Error ? error.message : 'Ha fallado la traducción.', {
      isError: true,
      progress: 0,
    });
  } finally {
    setBusy(false);
  }
});

initializeForm();
setIdleStatus();
