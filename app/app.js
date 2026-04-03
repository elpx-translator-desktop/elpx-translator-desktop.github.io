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
    defaultModels: ['gpt-5-mini', 'gpt-5', 'gpt-5-nano'],
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

const UI_LANGUAGE_STORAGE_KEY = 'elpx-translator-site-language';
const UI_SUPPORTED_LANGUAGES = ['es', 'en', 'ca', 'eu', 'gl'];
const APP_I18N = {
  es: {
    meta_description: 'Versión web para traducir archivos .elpx desde el navegador usando tu propia API.',
    language_label: 'Idioma',
    nav_home: 'Página principal',
    nav_issues: 'Incidencias',
    hero_eyebrow: 'Versión web',
    hero_title: 'ELPX Translator web',
    hero_lead: 'Traduce archivos .elpx desde el navegador.',
    hero_desktop_note: 'Si no dispones de clave API o prefieres trabajar en local, usa la <a href="../index.html#descargas">versión de escritorio</a>.',
    hero_note_title: 'Qué hace esta versión',
    hero_note_1: 'Traduce archivos .elpx.',
    hero_note_2: 'Genera un nuevo archivo traducido para descargar.',
    hero_note_3: 'Necesita tu propia clave API para funcionar.',
    api_panel_title: 'API y modelo',
    api_panel_body: 'La clave API se guarda en este navegador para que no tengas que escribirla cada vez.',
    provider_label: 'Servicio API',
    api_key_label: 'Clave API',
    clear_api_key_button: 'Borrar clave',
    model_label: 'Modelo',
    load_models_button: 'Cargar modelos',
    privacy_title: 'Privacidad:',
    privacy_1: 'El archivo se abre localmente en el navegador.',
    privacy_2: 'El texto se envía al servicio API que elijas para hacer la traducción.',
    privacy_3: 'No hay un servidor propio intermedio.',
    no_api_title: '¿No tienes API?',
    no_api_1: 'La versión web necesita una clave API de un proveedor externo.',
    no_api_2: 'Si no dispones de ella, usa la versión de escritorio con procesamiento local.',
    no_api_3: '<a href="../index.html">Ir a la página principal</a> para ver información y descargas.',
    file_panel_title: 'Archivo e idiomas',
    file_panel_body: 'Elige el archivo y los idiomas antes de traducir.',
    file_label: 'Archivo .elpx',
    source_language_label: 'Idioma de origen',
    source_language_detected_label: 'Idioma detectado',
    target_language_label: 'Idioma de destino',
    custom_target_label: 'Código de idioma',
    custom_target_placeholder: 'sv, ja, pt-BR, zh-CN',
    translate_button: 'Traducir archivo',
    reset_button: 'Limpiar',
    status_title: 'Estado',
    status_body: 'Aquí verás cómo avanza la traducción.',
    status_idle_badge: 'Listo para empezar',
    status_idle_text: 'Selecciona un archivo, configura el proveedor y lanza la traducción.',
    status_running_badge: 'En proceso',
    status_error_badge: 'Error',
    status_done_badge: 'Completado',
    result_title: 'Resultado',
    result_file_generated: 'Archivo generado: {filename}',
    download_button: 'Descargar archivo traducido',
    tips_title: 'Ten en cuenta',
    tips_1: 'La versión web no sustituye a la versión de escritorio.',
    tips_2: 'Necesitas tu propia clave API.',
    tips_3: 'Conviene revisar el archivo traducido antes de publicarlo.',
    custom_language_option_label: '{code} · idioma detectado',
    custom_target_option: 'Otro código de idioma',
    no_pending_text: 'No hay texto pendiente de traducir.',
    preparing_batches: 'Preparando lotes...',
    sending_unique_blocks: 'Enviando {count} bloques únicos al proveedor remoto.',
    translating_blocks: 'Traduciendo bloques {completed} de {total}.',
    batch_completed: 'Lote {batch} completado.',
    invalid_remote_response: 'La respuesta remota no devolvió una lista de traducciones válida.',
    unsupported_provider: 'Proveedor no soportado: {provider}',
    content_xml_missing: 'No se encontró content.xml dentro del archivo .elpx.',
    xml_parse_error: 'No se pudo analizar content.xml.',
    write_api_key_first: 'Escribe primero tu clave API.',
    loading_models: 'Recuperando modelos disponibles...',
    no_models_found: 'No se han encontrado modelos para este servicio.',
    models_loaded: 'Modelos recuperados.',
    models_available: '{count} modelos disponibles.',
    models_load_failed: 'No se pudieron cargar los modelos.',
    missing_file: 'Falta el archivo .elpx.',
    missing_model: 'Falta el identificador del modelo.',
    missing_api_key: 'Falta la clave API.',
    same_languages: 'El idioma de origen y el de destino no pueden ser iguales.',
    invalid_language_code: 'El código de idioma no es válido.',
    opening_elpx: 'Abriendo el archivo .elpx...',
    translation_done: 'Traducción terminada.',
    unique_blocks_processed: '{count} bloques únicos procesados.',
    translation_failed: 'Ha fallado la traducción.',
    remote_error: 'Error remoto {status}.',
  },
  en: {
    meta_description: 'Web version for translating .elpx files in the browser using your own API.',
    language_label: 'Language',
    nav_home: 'Main page',
    nav_issues: 'Issues',
    hero_eyebrow: 'Web version',
    hero_title: 'ELPX Translator web',
    hero_lead: 'Translate .elpx files from your browser.',
    hero_desktop_note: 'If you do not have an API key or prefer to work locally, use the <a href="../index.html#descargas">desktop version</a>.',
    hero_note_title: 'What this version does',
    hero_note_1: 'Translates .elpx files.',
    hero_note_2: 'Generates a new translated file for download.',
    hero_note_3: 'Needs your own API key to work.',
    api_panel_title: 'API and model',
    api_panel_body: 'The API key is stored in this browser so you do not have to type it every time.',
    provider_label: 'API service',
    api_key_label: 'API key',
    clear_api_key_button: 'Clear key',
    model_label: 'Model',
    load_models_button: 'Load models',
    privacy_title: 'Privacy:',
    privacy_1: 'The file is opened locally in the browser.',
    privacy_2: 'The text is sent to the API service you choose for translation.',
    privacy_3: 'There is no intermediary server of our own.',
    no_api_title: 'No API?',
    no_api_1: 'The web version needs an API key from an external provider.',
    no_api_2: 'If you do not have one, use the desktop version with local processing.',
    no_api_3: '<a href="../index.html">Go to the main page</a> for information and downloads.',
    file_panel_title: 'File and languages',
    file_panel_body: 'Choose the file and languages before translating.',
    file_label: '.elpx file',
    source_language_label: 'Source language',
    source_language_detected_label: 'Detected language',
    target_language_label: 'Target language',
    custom_target_label: 'Language code',
    custom_target_placeholder: 'sv, ja, pt-BR, zh-CN',
    translate_button: 'Translate file',
    reset_button: 'Reset',
    status_title: 'Status',
    status_body: 'You will see translation progress here.',
    status_idle_badge: 'Ready to start',
    status_idle_text: 'Select a file, configure the provider, and start the translation.',
    status_running_badge: 'In progress',
    status_error_badge: 'Error',
    status_done_badge: 'Completed',
    result_title: 'Result',
    result_file_generated: 'Generated file: {filename}',
    download_button: 'Download translated file',
    tips_title: 'Keep in mind',
    tips_1: 'The web version does not replace the desktop version.',
    tips_2: 'You need your own API key.',
    tips_3: 'It is advisable to review the translated file before publishing it.',
    custom_language_option_label: '{code} · detected language',
    custom_target_option: 'Other language code',
    no_pending_text: 'There is no text pending translation.',
    preparing_batches: 'Preparing batches...',
    sending_unique_blocks: 'Sending {count} unique blocks to the remote provider.',
    translating_blocks: 'Translating blocks {completed} of {total}.',
    batch_completed: 'Batch {batch} completed.',
    invalid_remote_response: 'The remote response did not return a valid translations list.',
    unsupported_provider: 'Unsupported provider: {provider}',
    content_xml_missing: 'content.xml was not found inside the .elpx file.',
    xml_parse_error: 'content.xml could not be parsed.',
    write_api_key_first: 'Enter your API key first.',
    loading_models: 'Loading available models...',
    no_models_found: 'No models were found for this service.',
    models_loaded: 'Models loaded.',
    models_available: '{count} models available.',
    models_load_failed: 'The models could not be loaded.',
    missing_file: 'The .elpx file is missing.',
    missing_model: 'The model identifier is missing.',
    missing_api_key: 'The API key is missing.',
    same_languages: 'Source and target languages cannot be the same.',
    invalid_language_code: 'The language code is not valid.',
    opening_elpx: 'Opening the .elpx file...',
    translation_done: 'Translation finished.',
    unique_blocks_processed: '{count} unique blocks processed.',
    translation_failed: 'The translation failed.',
    remote_error: 'Remote error {status}.',
  },
  ca: {
    meta_description: 'Versió web per traduir fitxers .elpx des del navegador amb la teva API.',
    language_label: 'Idioma',
    nav_home: 'Pàgina principal',
    nav_issues: 'Incidències',
    hero_eyebrow: 'Versió web',
    hero_title: 'ELPX Translator web',
    hero_lead: 'Tradueix fitxers .elpx des del navegador.',
    hero_desktop_note: 'Si no disposes de clau API o prefereixes treballar en local, fes servir la <a href="../index.html#descargas">versió d’escriptori</a>.',
    hero_note_title: 'Què fa aquesta versió',
    hero_note_1: 'Tradueix fitxers .elpx.',
    hero_note_2: 'Genera un nou fitxer traduït per descarregar.',
    hero_note_3: 'Necessita la teva pròpia clau API per funcionar.',
    api_panel_title: 'API i model',
    api_panel_body: 'La clau API es guarda en aquest navegador perquè no l’hagis d’escriure cada vegada.',
    provider_label: 'Proveïdor API',
    api_key_label: 'Clau API',
    clear_api_key_button: 'Esborrar clau',
    model_label: 'Model',
    load_models_button: 'Carregar models',
    privacy_title: 'Privacitat:',
    privacy_1: 'El fitxer s’obre localment al navegador.',
    privacy_2: 'El text s’envia al proveïdor d’API que triïs per fer la traducció.',
    privacy_3: 'No hi ha cap servidor intermedi propi.',
    no_api_title: 'No tens API?',
    no_api_1: 'La versió web necessita una clau API d’un proveïdor extern.',
    no_api_2: 'Si no en disposes, fes servir la versió d’escriptori amb processament local.',
    no_api_3: '<a href="../index.html">Ves a la pàgina principal</a> per veure informació i descàrregues.',
    file_panel_title: 'Fitxer i idiomes',
    file_panel_body: 'Tria el fitxer i els idiomes abans de traduir.',
    file_label: 'Fitxer .elpx',
    source_language_label: 'Idioma d’origen',
    source_language_detected_label: 'Idioma detectat',
    target_language_label: 'Idioma de destí',
    custom_target_label: 'Codi d’idioma',
    custom_target_placeholder: 'sv, ja, pt-BR, zh-CN',
    translate_button: 'Traduir fitxer',
    reset_button: 'Netejar',
    status_title: 'Estat',
    status_body: 'Aquí veuràs com avança la traducció.',
    status_idle_badge: 'A punt per començar',
    status_idle_text: 'Selecciona un fitxer, configura el proveïdor i inicia la traducció.',
    status_running_badge: 'En procés',
    status_error_badge: 'Error',
    status_done_badge: 'Completat',
    result_title: 'Resultat',
    result_file_generated: 'Fitxer generat: {filename}',
    download_button: 'Descarregar fitxer traduït',
    tips_title: 'Tingues en compte',
    tips_1: 'La versió web no substitueix la versió d’escriptori.',
    tips_2: 'Necessites la teva pròpia clau API.',
    tips_3: 'Convé revisar el fitxer traduït abans de publicar-lo.',
    custom_language_option_label: '{code} · idioma detectat',
    custom_target_option: 'Un altre codi d’idioma',
    no_pending_text: 'No hi ha text pendent de traduir.',
    preparing_batches: 'Preparant lots...',
    sending_unique_blocks: 'Enviant {count} blocs únics al proveïdor remot.',
    translating_blocks: 'Traduint blocs {completed} de {total}.',
    batch_completed: 'Lot {batch} completat.',
    invalid_remote_response: 'La resposta remota no ha tornat una llista vàlida de traduccions.',
    unsupported_provider: 'Proveïdor no suportat: {provider}',
    content_xml_missing: 'No s’ha trobat content.xml dins del fitxer .elpx.',
    xml_parse_error: 'No s’ha pogut analitzar content.xml.',
    write_api_key_first: 'Escriu primer la teva clau API.',
    loading_models: 'Recuperant models disponibles...',
    no_models_found: 'No s’han trobat models per a aquest servei.',
    models_loaded: 'Models recuperats.',
    models_available: '{count} models disponibles.',
    models_load_failed: 'No s’han pogut carregar els models.',
    missing_file: 'Falta el fitxer .elpx.',
    missing_model: 'Falta l’identificador del model.',
    missing_api_key: 'Falta la clau API.',
    same_languages: 'L’idioma d’origen i el de destí no poden ser iguals.',
    invalid_language_code: 'El codi d’idioma no és vàlid.',
    opening_elpx: 'Obrint el fitxer .elpx...',
    translation_done: 'Traducció acabada.',
    unique_blocks_processed: '{count} blocs únics processats.',
    translation_failed: 'La traducció ha fallat.',
    remote_error: 'Error remot {status}.',
  },
  eu: {
    meta_description: 'Web bertsioa .elpx fitxategiak nabigatzailetik zure APIarekin itzultzeko.',
    language_label: 'Hizkuntza',
    nav_home: 'Orri nagusia',
    nav_issues: 'Gorabeherak',
    hero_eyebrow: 'Web bertsioa',
    hero_title: 'ELPX Translator web',
    hero_lead: '.elpx fitxategiak nabigatzailetik itzuli.',
    hero_desktop_note: 'API gakorik ez baduzu edo lokalean lan egin nahi baduzu, erabili <a href="../index.html#descargas">mahaigaineko bertsioa</a>.',
    hero_note_title: 'Bertsio honek zer egiten duen',
    hero_note_1: '.elpx fitxategiak itzultzen ditu.',
    hero_note_2: 'Deskargatzeko fitxategi itzuli berri bat sortzen du.',
    hero_note_3: 'Funtzionatzeko zure API gakoa behar du.',
    api_panel_title: 'APIa eta eredua',
    api_panel_body: 'API gakoa nabigatzaile honetan gordetzen da, aldiro idatzi behar ez izateko.',
    provider_label: 'API zerbitzua',
    api_key_label: 'API gakoa',
    clear_api_key_button: 'Gakoa ezabatu',
    model_label: 'Eredua',
    load_models_button: 'Ereduak kargatu',
    privacy_title: 'Pribatutasuna:',
    privacy_1: 'Fitxategia lokalean irekitzen da nabigatzailean.',
    privacy_2: 'Testua zuk aukeratutako API zerbitzura bidaltzen da itzulpena egiteko.',
    privacy_3: 'Ez dago gure bitarteko zerbitzaririk.',
    no_api_title: 'APIrik ez?',
    no_api_1: 'Web bertsioak kanpoko hornitzaile baten API gakoa behar du.',
    no_api_2: 'Ez baduzu, erabili prozesamendu lokala duen mahaigaineko bertsioa.',
    no_api_3: '<a href="../index.html">Joan orri nagusira</a> informazioa eta deskargak ikusteko.',
    file_panel_title: 'Fitxategia eta hizkuntzak',
    file_panel_body: 'Aukeratu fitxategia eta hizkuntzak itzuli aurretik.',
    file_label: '.elpx fitxategia',
    source_language_label: 'Jatorrizko hizkuntza',
    source_language_detected_label: 'Detektatutako hizkuntza',
    target_language_label: 'Helburuko hizkuntza',
    custom_target_label: 'Hizkuntza kodea',
    custom_target_placeholder: 'sv, ja, pt-BR, zh-CN',
    translate_button: 'Fitxategia itzuli',
    reset_button: 'Garbitu',
    status_title: 'Egoera',
    status_body: 'Hemen ikusiko duzu itzulpenaren aurrerapena.',
    status_idle_badge: 'Hasteko prest',
    status_idle_text: 'Hautatu fitxategi bat, konfiguratu hornitzailea eta abiarazi itzulpena.',
    status_running_badge: 'Martxan',
    status_error_badge: 'Errorea',
    status_done_badge: 'Osatuta',
    result_title: 'Emaitza',
    result_file_generated: 'Sortutako fitxategia: {filename}',
    download_button: 'Itzulitako fitxategia deskargatu',
    tips_title: 'Kontuan izan',
    tips_1: 'Web bertsioak ez du mahaigaineko bertsioa ordezkatzen.',
    tips_2: 'Zure API gakoa behar duzu.',
    tips_3: 'Argitaratu aurretik itzulitako fitxategia berrikustea komeni da.',
    custom_language_option_label: '{code} · detektatutako hizkuntza',
    custom_target_option: 'Beste hizkuntza kode bat',
    no_pending_text: 'Ez dago itzultzeko testu pendenterik.',
    preparing_batches: 'Multzoak prestatzen...',
    sending_unique_blocks: '{count} bloke bakar hornitzaile urrunera bidaltzen...',
    translating_blocks: '{completed} / {total} bloke itzultzen.',
    batch_completed: '{batch}. multzoa osatuta.',
    invalid_remote_response: 'Erantzun urrunak ez du itzulpen zerrenda baliodunik itzuli.',
    unsupported_provider: 'Onartu gabeko hornitzailea: {provider}',
    content_xml_missing: 'Ez da content.xml aurkitu .elpx fitxategiaren barruan.',
    xml_parse_error: 'Ezin izan da content.xml analizatu.',
    write_api_key_first: 'Idatzi lehenik zure API gakoa.',
    loading_models: 'Eredu erabilgarriak berreskuratzen...',
    no_models_found: 'Ez da eredurik aurkitu zerbitzu honetarako.',
    models_loaded: 'Ereduak berreskuratu dira.',
    models_available: '{count} eredu erabilgarri.',
    models_load_failed: 'Ezin izan dira ereduak kargatu.',
    missing_file: '.elpx fitxategia falta da.',
    missing_model: 'Eredu identifikatzailea falta da.',
    missing_api_key: 'API gakoa falta da.',
    same_languages: 'Jatorrizko eta helburuko hizkuntzak ezin dira berdinak izan.',
    invalid_language_code: 'Hizkuntza kodea ez da baliozkoa.',
    opening_elpx: '.elpx fitxategia irekitzen...',
    translation_done: 'Itzulpena amaitu da.',
    unique_blocks_processed: '{count} bloke bakar prozesatu dira.',
    translation_failed: 'Itzulpenak huts egin du.',
    remote_error: '{status} errore urruna.',
  },
  gl: {
    meta_description: 'Versión web para traducir ficheiros .elpx desde o navegador coa túa API.',
    language_label: 'Idioma',
    nav_home: 'Páxina principal',
    nav_issues: 'Incidencias',
    hero_eyebrow: 'Versión web',
    hero_title: 'ELPX Translator web',
    hero_lead: 'Traduce ficheiros .elpx desde o navegador.',
    hero_desktop_note: 'Se non dispós de clave API ou prefires traballar en local, usa a <a href="../index.html#descargas">versión de escritorio</a>.',
    hero_note_title: 'Que fai esta versión',
    hero_note_1: 'Traduce ficheiros .elpx.',
    hero_note_2: 'Xera un novo ficheiro traducido para descargar.',
    hero_note_3: 'Necesita a túa propia clave API para funcionar.',
    api_panel_title: 'API e modelo',
    api_panel_body: 'A clave API gárdase neste navegador para que non teñas que escribila cada vez.',
    provider_label: 'Servizo API',
    api_key_label: 'Clave API',
    clear_api_key_button: 'Borrar clave',
    model_label: 'Modelo',
    load_models_button: 'Cargar modelos',
    privacy_title: 'Privacidade:',
    privacy_1: 'O ficheiro ábrese localmente no navegador.',
    privacy_2: 'O texto envíase ao servizo API que escollas para facer a tradución.',
    privacy_3: 'Non hai un servidor propio intermedio.',
    no_api_title: 'Non tes API?',
    no_api_1: 'A versión web necesita unha clave API dun provedor externo.',
    no_api_2: 'Se non dispós dela, usa a versión de escritorio con procesamento local.',
    no_api_3: '<a href="../index.html">Ir á páxina principal</a> para ver información e descargas.',
    file_panel_title: 'Ficheiro e idiomas',
    file_panel_body: 'Escolle o ficheiro e os idiomas antes de traducir.',
    file_label: 'Ficheiro .elpx',
    source_language_label: 'Idioma de orixe',
    source_language_detected_label: 'Idioma detectado',
    target_language_label: 'Idioma de destino',
    custom_target_label: 'Código de idioma',
    custom_target_placeholder: 'sv, ja, pt-BR, zh-CN',
    translate_button: 'Traducir ficheiro',
    reset_button: 'Limpar',
    status_title: 'Estado',
    status_body: 'Aquí verás como avanza a tradución.',
    status_idle_badge: 'Listo para empezar',
    status_idle_text: 'Selecciona un ficheiro, configura o provedor e lanza a tradución.',
    status_running_badge: 'En proceso',
    status_error_badge: 'Erro',
    status_done_badge: 'Completado',
    result_title: 'Resultado',
    result_file_generated: 'Ficheiro xerado: {filename}',
    download_button: 'Descargar ficheiro traducido',
    tips_title: 'Ten en conta',
    tips_1: 'A versión web non substitúe a versión de escritorio.',
    tips_2: 'Necesitas a túa propia clave API.',
    tips_3: 'Convén revisar o ficheiro traducido antes de publicalo.',
    custom_language_option_label: '{code} · idioma detectado',
    custom_target_option: 'Outro código de idioma',
    no_pending_text: 'Non hai texto pendente de traducir.',
    preparing_batches: 'Preparando lotes...',
    sending_unique_blocks: 'Enviando {count} bloques únicos ao provedor remoto.',
    translating_blocks: 'Traducindo bloques {completed} de {total}.',
    batch_completed: 'Lote {batch} completado.',
    invalid_remote_response: 'A resposta remota non devolveu unha lista válida de traducións.',
    unsupported_provider: 'Provedor non soportado: {provider}',
    content_xml_missing: 'Non se atopou content.xml dentro do ficheiro .elpx.',
    xml_parse_error: 'Non se puido analizar content.xml.',
    write_api_key_first: 'Escribe primeiro a túa clave API.',
    loading_models: 'Recuperando modelos dispoñibles...',
    no_models_found: 'Non se atoparon modelos para este servizo.',
    models_loaded: 'Modelos recuperados.',
    models_available: '{count} modelos dispoñibles.',
    models_load_failed: 'Non se puideron cargar os modelos.',
    missing_file: 'Falta o ficheiro .elpx.',
    missing_model: 'Falta o identificador do modelo.',
    missing_api_key: 'Falta a clave API.',
    same_languages: 'O idioma de orixe e o de destino non poden ser iguais.',
    invalid_language_code: 'O código de idioma non é válido.',
    opening_elpx: 'Abrindo o ficheiro .elpx...',
    translation_done: 'Tradución rematada.',
    unique_blocks_processed: '{count} bloques únicos procesados.',
    translation_failed: 'A tradución fallou.',
    remote_error: 'Erro remoto {status}.',
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

const APP_SETTINGS_STORAGE_KEY = 'elpx-web-beta-settings';
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
  languagePicker: document.getElementById('language-picker'),
  form: document.getElementById('translator-form'),
  inputFile: document.getElementById('input-file'),
  sourceLanguageLabel: document.querySelector('[data-i18n="source_language_label"]'),
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
let currentLanguage = 'es';
let detectedProjectLanguage = null;
let autoDetectedSourceLanguageActive = false;

function languagePack(language) {
  return APP_I18N[language] || APP_I18N.es;
}

function t(key, params = {}) {
  let value = languagePack(currentLanguage)[key] || APP_I18N.es[key] || key;
  for (const [param, replacement] of Object.entries(params)) {
    value = value.replaceAll(`{${param}}`, String(replacement));
  }
  return value;
}

function detectLanguage() {
  const saved = localStorage.getItem(UI_LANGUAGE_STORAGE_KEY);
  if (saved && UI_SUPPORTED_LANGUAGES.includes(saved)) {
    return saved;
  }

  const candidates = [...(navigator.languages || []), navigator.language, navigator.userLanguage].filter(Boolean);
  for (const candidate of candidates) {
    const code = String(candidate).toLowerCase().split('-', 1)[0];
    if (UI_SUPPORTED_LANGUAGES.includes(code)) {
      return code;
    }
  }

  return 'es';
}

function applyStaticTranslations() {
  document.documentElement.lang = currentLanguage;
  document.title = t('hero_title');
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute('content', t('meta_description'));
  }

  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const key = element.dataset.i18n;
    const value = t(key);
    if (element.dataset.i18nMode === 'html') {
      element.innerHTML = value;
      return;
    }
    element.textContent = value;
  });

  document.querySelectorAll('[data-i18n-attr]').forEach((element) => {
    const mappings = element.dataset.i18nAttr.split(',');
    for (const mapping of mappings) {
      const [attribute, key] = mapping.split(':');
      if (attribute && key) {
        element.setAttribute(attribute.trim(), t(key.trim()));
      }
    }
  });

  if (elements.languagePicker) {
    elements.languagePicker.value = currentLanguage;
    elements.languagePicker.setAttribute('aria-label', t('language_label'));
  }

  updateSourceLanguageLabel();
}

function updateSourceLanguageLabel() {
  if (!elements.sourceLanguageLabel) {
    return;
  }
  const labelKey = autoDetectedSourceLanguageActive ? 'source_language_detected_label' : 'source_language_label';
  elements.sourceLanguageLabel.textContent = t(labelKey);
}

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
      onProgress({ status: t('no_pending_text'), detail: '', progress: 100 });
      return;
    }

    onProgress({
      status: t('sending_unique_blocks', { count: total }),
      detail: t('preparing_batches'),
      progress: 6,
    });

    const translatedMap = await translator.translateMany(uniqueTexts, context, (message) => {
      const percent = 6 + Math.round((message.completed / total) * 82);
      onProgress({
        status: t('translating_blocks', { completed: message.completed, total }),
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
        detail: t('batch_completed', { batch: Math.ceil(completedChunks / this.batchSize) }),
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
      throw new Error(t('invalid_remote_response'));
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
      throw new Error(t('unsupported_provider', { provider: this.provider }));
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

function languageOptionLabel(code) {
  const match = LANGUAGE_OPTIONS.find(([value]) => value === code);
  if (match) {
    return `${code} · ${match[1]}`;
  }
  return t('custom_language_option_label', { code });
}

function fillSourceLanguageOptions(selectedValue) {
  const options = [...LANGUAGE_OPTIONS];
  if (selectedValue && !options.some(([value]) => value === selectedValue)) {
    options.unshift([selectedValue, languageOptionLabel(selectedValue)]);
  }
  fillSelect(
    elements.sourceLanguage,
    options.map(([value]) => [value, languageOptionLabel(value)]),
    selectedValue,
  );
}

function fillTargetLanguageOptions(selectedValue) {
  const options = [...LANGUAGE_OPTIONS, [CUSTOM_TARGET_LANGUAGE_VALUE, t('custom_target_option')]];
  fillSelect(
    elements.targetLanguage,
    options.map(([value, label]) => [
      value,
      value === CUSTOM_TARGET_LANGUAGE_VALUE ? label : languageOptionLabel(value),
    ]),
    selectedValue,
  );
}

function fillProviderOptions() {
  elements.provider.innerHTML = Object.entries(PROVIDERS)
    .map(([value, config]) => `<option value="${escapeHtml(value)}">${escapeHtml(config.label)}</option>`)
    .join('');
}

function loadSavedSettings() {
  try {
    return JSON.parse(localStorage.getItem(APP_SETTINGS_STORAGE_KEY) || '{}');
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
  localStorage.setItem(APP_SETTINGS_STORAGE_KEY, JSON.stringify(payload));
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
    'gpt-5': 1,
    'gpt-5-nano': 2,
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
  elements.statusBadge.textContent = isError ? t('status_error_badge') : t('status_running_badge');
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
  elements.statusBadge.textContent = t('status_idle_badge');
  elements.statusBadge.classList.remove('is-error');
  elements.progress.value = 0;
  elements.statusText.textContent = t('status_idle_text');
  elements.statusDetail.textContent = '';
}

function setDoneStatus(message, detail = '') {
  elements.statusBadge.textContent = t('status_done_badge');
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
  elements.resultText.textContent = t('result_file_generated', { filename });
  elements.downloadLink.href = activeDownloadUrl;
  elements.downloadLink.download = filename;
}

async function translateElpxFile(file, settings) {
  const zip = await JSZip.loadAsync(await file.arrayBuffer());
  const contentXmlPath = findContentXmlPath(Object.keys(zip.files));
  if (!contentXmlPath) {
    throw new Error(t('content_xml_missing'));
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

async function detectProjectLanguageFromFile(file) {
  const zip = await JSZip.loadAsync(await file.arrayBuffer());
  const contentXmlPath = findContentXmlPath(Object.keys(zip.files));
  if (!contentXmlPath) {
    return null;
  }

  const xmlContent = await zip.file(contentXmlPath).async('string');
  const xmlDocument = parseXml(xmlContent);
  const languageNode = getPropertyValueNodes(xmlDocument, 'odeProperty', new Set(['pp_lang']))[0];
  const detectedLanguage = languageNode ? getNodeText(languageNode).trim().toLowerCase() : '';
  return detectedLanguage || null;
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
    throw new Error(t('xml_parse_error'));
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
  return messages[0] || t('remote_error', { status });
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
  const defaultProvider = Object.keys(PROVIDERS)[0] || '';
  fillSourceLanguageOptions(saved.sourceLanguage || 'es');
  const savedTarget = saved.customTargetLanguage ? CUSTOM_TARGET_LANGUAGE_VALUE : (saved.targetLanguage || 'en');
  fillTargetLanguageOptions(savedTarget);
  fillProviderOptions();
  elements.provider.value = saved.provider && PROVIDERS[saved.provider] ? saved.provider : defaultProvider;
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

function applyLanguage(language) {
  currentLanguage = UI_SUPPORTED_LANGUAGES.includes(language) ? language : 'es';
  localStorage.setItem(UI_LANGUAGE_STORAGE_KEY, currentLanguage);
  applyStaticTranslations();

  const currentSource = elements.sourceLanguage.value || 'es';
  fillSourceLanguageOptions(currentSource);
  const currentTarget = elements.targetLanguage.value || 'en';
  fillTargetLanguageOptions(currentTarget);
  toggleCustomTargetVisibility();

  if (elements.statusBadge.classList.contains('is-error')) {
    if (elements.statusBadge.textContent === APP_I18N.es.status_error_badge
      || Object.values(APP_I18N).some((pack) => pack.status_error_badge === elements.statusBadge.textContent)) {
      elements.statusBadge.textContent = t('status_error_badge');
    }
  } else if (elements.progress.value === 100) {
    if (Object.values(APP_I18N).some((pack) => pack.status_done_badge === elements.statusBadge.textContent)) {
      elements.statusBadge.textContent = t('status_done_badge');
    }
  } else if (Object.values(APP_I18N).some((pack) => pack.status_idle_badge === elements.statusBadge.textContent)) {
    setIdleStatus();
  } else if (Object.values(APP_I18N).some((pack) => pack.status_running_badge === elements.statusBadge.textContent)) {
    elements.statusBadge.textContent = t('status_running_badge');
  }
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
elements.inputFile.addEventListener('change', async () => {
  const file = elements.inputFile.files?.[0];
  if (!file) {
    detectedProjectLanguage = null;
    autoDetectedSourceLanguageActive = false;
    updateSourceLanguageLabel();
    return;
  }

  try {
    const detectedLanguage = await detectProjectLanguageFromFile(file);
    const supportedSourceLanguages = new Set(LANGUAGE_OPTIONS.map(([code]) => code));
    detectedProjectLanguage = detectedLanguage;
    if (!detectedLanguage || !supportedSourceLanguages.has(detectedLanguage)) {
      autoDetectedSourceLanguageActive = false;
      fillSourceLanguageOptions(elements.sourceLanguage.value || 'es');
      updateSourceLanguageLabel();
      return;
    }
    fillSourceLanguageOptions(detectedLanguage);
    elements.sourceLanguage.value = detectedLanguage;
    autoDetectedSourceLanguageActive = true;
    updateSourceLanguageLabel();
    saveSettings();
  } catch {
    // If detection fails, keep the current manual selection.
    detectedProjectLanguage = null;
    autoDetectedSourceLanguageActive = false;
    updateSourceLanguageLabel();
  }
});
elements.sourceLanguage.addEventListener('change', () => {
  if (!autoDetectedSourceLanguageActive || elements.sourceLanguage.value !== detectedProjectLanguage) {
    autoDetectedSourceLanguageActive = false;
  }
  updateSourceLanguageLabel();
  saveSettings();
});
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
  localStorage.setItem(APP_SETTINGS_STORAGE_KEY, JSON.stringify({
    ...saved,
    providerApiKeys,
  }));
  syncApiDependentControls();
});

elements.resetButton.addEventListener('click', () => {
  elements.form.reset();
  detectedProjectLanguage = null;
  autoDetectedSourceLanguageActive = false;
  initializeForm();
  elements.apiKey.value = '';
  syncApiDependentControls();
  clearResult();
  updateSourceLanguageLabel();
  setIdleStatus();
});

elements.loadModelsButton.addEventListener('click', async () => {
  const provider = elements.provider.value;
  const apiKey = elements.apiKey.value.trim();

  if (!apiKey) {
    setStatus(t('write_api_key_first'), { isError: true, progress: 0 });
    return;
  }

  elements.loadModelsButton.disabled = true;
  setStatus(t('loading_models'), { progress: 5 });

  try {
    const models = await listAvailableModels(provider, apiKey);
    if (!models.length) {
      setStatus(t('no_models_found'), { isError: true, progress: 0 });
      return;
    }
    renderModelOptions(models);
    elements.model.value = models[0];
    saveSettings();
    setDoneStatus(t('models_loaded'), t('models_available', { count: models.length }));
  } catch (error) {
    setStatus(error instanceof Error ? error.message : t('models_load_failed'), {
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
    setStatus(t('missing_file'), { isError: true, progress: 0 });
    return;
  }
  if (!model) {
    setStatus(t('missing_model'), { isError: true, progress: 0 });
    return;
  }
  if (!apiKey) {
    setStatus(t('missing_api_key'), { isError: true, progress: 0 });
    return;
  }
  if (sourceLanguage === targetLanguage) {
    setStatus(t('same_languages'), { isError: true, progress: 0 });
    return;
  }
  if (isCustomTargetSelected() && !isValidCustomTargetLanguage(targetLanguage)) {
    setStatus(t('invalid_language_code'), { isError: true, progress: 0 });
    return;
  }

  saveSettings();
  setBusy(true);
  setStatus(t('opening_elpx'), { progress: 2 });

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
    setDoneStatus(t('translation_done'), t('unique_blocks_processed', { count: result.queuedUnits }));
  } catch (error) {
    setStatus(error instanceof Error ? error.message : t('translation_failed'), {
      isError: true,
      progress: 0,
    });
  } finally {
    setBusy(false);
  }
});

if (elements.languagePicker) {
  elements.languagePicker.addEventListener('change', (event) => {
    applyLanguage(event.target.value);
  });
}

initializeForm();
applyLanguage(detectLanguage());
setIdleStatus();
