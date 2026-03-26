const REPO = 'elpx-translator-desktop/elpx-translator-desktop.github.io';
const API_URL = `https://api.github.com/repos/${REPO}/releases`;
const STORAGE_KEY = 'elpx-translator-site-language';
const SUPPORTED_LANGUAGES = ['es', 'en', 'ca', 'eu', 'gl'];

const SITE_I18N = {
  es: {
    meta_description: 'Aplicación de escritorio para traducir archivos .elpx de forma local, pensada para profesorado y usuarios no técnicos.',
    language_label: 'Idioma',
    nav_downloads: 'Descargas',
    nav_screenshots: 'Capturas',
    nav_privacy: 'Privacidad',
    nav_issues: 'Sugerencias y errores',
    hero_eyebrow: 'Para profesorado y personas no técnicas',
    hero_lead: 'ELPX Translator Desktop sirve para traducir proyectos de eXeLearning sin depender de servicios externos. Está pensado para ahorrar tiempo al adaptar materiales ya creados a otro idioma.',
    hero_cta_downloads: 'Ver descargas',
    hero_cta_issues: 'Informar de una sugerencia o problema',
    hero_point_1: 'Funciona en Linux, Windows y macOS.',
    hero_point_2: 'Procesa el contenido del archivo en tu equipo.',
    hero_point_3: 'Interfaz sencilla, pensada para profesorado y personas no técnicas.',
    hero_image_alt: 'Ventana principal de ELPX Translator Desktop',
    what_eyebrow: 'Qué es',
    what_title: 'Una herramienta para traducir materiales de eXeLearning con menos trabajo manual',
    what_card_1_title: 'Qué hace',
    what_card_1_body: 'Abre un archivo <code>.elpx</code>, detecta el texto traducible y genera una copia en el idioma que elijas.',
    what_card_2_title: 'Para quién está pensada',
    what_card_2_body: 'Sobre todo para docentes que ya tienen materiales creados y quieren reutilizarlos sin volver a traducir todo a mano.',
    what_card_3_title: 'Qué no necesitas',
    what_card_3_body: 'No hace falta saber programar, usar terminal ni entender detalles técnicos sobre modelos de IA.',
    downloads_eyebrow: 'Descargas',
    downloads_title: 'Versiones disponibles',
    downloads_body: 'La página consulta GitHub Releases y muestra la última beta publicada. En Linux verás tanto el paquete <code>.deb</code> como la <code>AppImage</code>. Cuando haya una versión estable realmente lista, también aparecerá aquí.',
    downloads_beta_updates_note: 'Si quieres recibir avisos de versiones beta dentro del programa, activa esa opción en la configuración. Por defecto está desactivada.',
    release_stable_label: 'Versión estable',
    release_stable_copy: 'La opción recomendada para la mayoría de personas.',
    release_beta_label: 'Última beta',
    release_beta_copy: 'Si quieres probar antes los cambios más recientes y ayudarnos a detectar fallos.',
    steps_eyebrow: 'Cómo se usa',
    steps_title: 'Tres pasos',
    step_1_title: 'Abre tu archivo',
    step_1_body: 'Selecciona el proyecto <code>.elpx</code> que quieres traducir.',
    step_2_title: 'Elige idiomas',
    step_2_body: 'Marca el idioma de origen y el idioma de destino.',
    step_3_title: 'Genera la copia traducida',
    step_3_body: 'La aplicación crea un nuevo archivo para que puedas revisarlo y seguir trabajándolo en eXeLearning.',
    performance_eyebrow: 'Rendimiento',
    performance_title: 'Qué significa cada modo',
    performance_body: 'La aplicación incluye cuatro modos para adaptarse mejor a tu equipo. No hace falta entender detalles técnicos: basta con elegir el que mejor encaje con tu forma de trabajar.',
    perf_card_1_title: 'Suave',
    perf_card_1_body: 'Prioriza que el ordenador siga respondiendo con comodidad mientras haces otras cosas. Puede tardar más, pero molesta menos al resto del sistema.',
    perf_card_2_title: 'Equilibrado',
    perf_card_2_body: 'Es la opción recomendada para la mayoría de personas. Busca un punto razonable entre velocidad y comodidad de uso.',
    perf_card_3_title: 'Rápido',
    perf_card_3_body: 'Usa más recursos para intentar terminar antes. Puede ser útil si quieres reducir tiempos y no necesitas usar mucho el equipo al mismo tiempo.',
    perf_card_4_title: 'Máximo',
    perf_card_4_body: 'Exprime más el ordenador para ir lo más rápido posible. Conviene usarlo cuando el equipo es potente y no vas a hacer otras tareas importantes a la vez.',
    requirements_eyebrow: 'Equipo recomendado',
    requirements_title: 'Requisitos orientativos',
    requirements_body: 'No hay una lista cerrada de requisitos mínimos exactos, pero estas referencias ayudan a saber qué esperar antes de instalarla.',
    requirements_card_1_title: 'Para un uso cómodo',
    requirements_card_1_body_1: 'Un equipo de 64 bits con al menos <strong>8 GB de RAM</strong> suele ser una base razonable para trabajar con más tranquilidad.',
    requirements_card_1_body_2: 'Si el ordenador tiene más memoria y varios núcleos de CPU, la traducción suele ir mejor, sobre todo con archivos grandes.',
    requirements_card_2_title: 'Qué puede pasar en equipos modestos',
    requirements_card_2_body_1: 'La aplicación puede funcionar en equipos más justos, pero es normal que tarde más y que convenga usar modos como <strong>Suave</strong> o <strong>Equilibrado</strong>.',
    requirements_card_2_body_2: 'La primera ejecución también necesita espacio libre para descargar el modelo y dejarlo guardado en la caché local.',
    screenshots_eyebrow: 'Capturas',
    screenshots_title: 'La aplicación por dentro',
    screenshot_1_alt: 'Pantalla principal de la aplicación',
    screenshot_1_caption: 'Pantalla principal: archivo de entrada, idioma de origen, idioma de destino y progreso.',
    screenshot_2_alt: 'Ventana con información de la aplicación',
    screenshot_2_caption: 'La propia aplicación incluye información sobre el proyecto y acceso a soporte.',
    privacy_eyebrow: 'Privacidad e IA',
    privacy_title: 'Explicado de forma simple',
    privacy_card_1_title: 'Cómo usa la IA',
    privacy_card_1_body_1: 'La aplicación usa un modelo abierto de traducción para proponer el texto en otro idioma. Su trabajo es ayudarte con la traducción automática del contenido del proyecto.',
    privacy_card_1_body_2: 'Para la mayoría de idiomas, la aplicación usa <strong>M2M100 418M</strong>, un modelo abierto publicado por <strong>Facebook AI</strong>. Está preparado para poder ejecutarse en un ordenador corriente sin depender de un servicio externo.',
    privacy_card_1_body_3: 'Cuando la traducción incluye <strong>euskera</strong>, la aplicación usa modelos abiertos de la familia <strong>OPUS-MT</strong>, desarrollados en el entorno académico de <strong>Helsinki-NLP</strong> y la <strong>Universidad de Helsinki</strong>.',
    privacy_card_1_body_4: 'En ambos casos se trata de modelos <strong>abiertos</strong>, pensados para poder descargarse y ejecutarse localmente. Por eso la traducción se hace en tu equipo y no depende de una plataforma comercial externa.',
    privacy_card_2_title: 'Qué pasa con tus datos',
    privacy_card_2_body_1: 'El contenido del archivo se procesa en tu ordenador durante la traducción.',
    privacy_card_2_body_2: 'No envía tu proyecto a un servicio externo para traducirlo. Solo puede conectarse a internet para descargar el modelo la primera vez y para comprobar si hay nuevas versiones.',
    known_eyebrow: 'Problemas conocidos',
    known_title: 'Limitaciones que conviene tener en cuenta',
    known_body: 'La aplicación puede ahorrar mucho trabajo, pero todavía hay casos en los que la revisión manual sigue siendo importante.',
    known_card_1_title: 'Títulos muy cortos o con poco contexto',
    known_card_1_body_1: 'Algunos títulos de navegación, nombres breves de actividades o etiquetas muy cortas pueden traducirse de forma poco natural o directamente incorrecta.',
    known_card_1_body_2: 'Esto ocurre porque, cuando el texto es muy breve y no aporta contexto suficiente, el modelo puede interpretarlo como si fuera un nombre propio, una categoría o una etiqueta técnica distinta de lo que realmente es.',
    known_card_2_title: 'iDevices interactivos complejos',
    known_card_2_body_1: 'Determinados iDevices con lógica propia, mensajes internos o formatos especiales no siempre se traducen completamente.',
    known_card_2_body_2: 'En estos casos, puede ocurrir que parte del contenido quede en el idioma original, que algunos textos automáticos no cambien o que ciertos elementos necesiten retoque manual dentro de eXeLearning.',
    known_card_3_title: 'Revisión final necesaria',
    known_card_3_body_1: 'La herramienta está pensada para acelerar el trabajo, no para sustituir una revisión final del material.',
    known_card_3_body_2: 'Conviene comprobar especialmente los títulos, instrucciones, actividades interactivas, textos incrustados en imágenes o tablas y cualquier contenido que tenga valor didáctico sensible.',
    known_card_4_title: 'Calidad desigual según idioma y contenido',
    known_card_4_body_1: 'La calidad de la traducción puede variar según el par de idiomas, el tipo de texto y la estructura del proyecto.',
    known_card_4_body_2: 'Los textos largos y con contexto suelen salir mejor que las etiquetas sueltas, los menús, los nombres de actividades o los fragmentos muy técnicos.',
    faq_eyebrow: 'Preguntas habituales',
    faq_title: 'Lo importante antes de empezar',
    faq_1_title: '¿Es un proyecto oficial del INTEF o de eXeLearning?',
    faq_1_body: 'No. Es un proyecto independiente y no está afiliado oficialmente con el INTEF ni con eXeLearning.',
    faq_2_title: '¿Necesito internet siempre?',
    faq_2_body: 'No. La primera vez puede hacer falta para descargar el modelo y también para comprobar si hay nuevas versiones. Después, la traducción trabaja en local.',
    faq_3_title: '¿Sirve para cualquier archivo perfecto a la primera?',
    faq_3_body: 'No conviene prometer eso. La aplicación está pensada para ahorrar mucho trabajo, pero siempre es recomendable revisar el resultado final antes de publicarlo.',
    faq_4_title: '¿Qué hago si algo sale mal?',
    faq_4_body: 'Usa el enlace de sugerencias y errores. Si puedes, indica qué sistema operativo usas y adjunta el archivo o una explicación breve del problema.',
    footer_body: 'ELPX Translator Desktop es un proyecto independiente para traducir archivos <code>.elpx</code>.',
    footer_author: 'Creado por <strong>Juan José de Haro</strong>.',
    footer_license: 'Software libre distribuido bajo licencia <strong>GNU AGPLv3 o posterior</strong>.',
    footer_repo: 'Repositorio',
    footer_releases: 'Releases',
    footer_issues: 'Sugerencias y errores',
    release_loading: 'Cargando...',
    release_no_artifacts: 'La release existe, pero todavía no aparecen artefactos adjuntos.',
    release_no_stable: 'Sin release estable',
    release_no_beta: 'Sin beta publicada',
    release_unavailable: 'No disponible',
    download_linux_deb: '.deb para Debian y derivados compatibles',
    download_linux_appimage: 'AppImage para otras distribuciones',
    download_windows: '.exe',
    download_macos: '.dmg',
    download_prefix: 'Descargar',
  },
  en: {
    meta_description: 'Desktop app to translate .elpx files locally, designed for teachers and non-technical users.',
    language_label: 'Language',
    nav_downloads: 'Downloads',
    nav_screenshots: 'Screenshots',
    nav_privacy: 'Privacy',
    nav_issues: 'Suggestions and bugs',
    hero_eyebrow: 'For teachers and non-technical users',
    hero_lead: 'ELPX Translator Desktop helps translate eXeLearning projects without depending on external services. It is designed to save time when adapting existing materials to another language.',
    hero_cta_downloads: 'View downloads',
    hero_cta_issues: 'Report a suggestion or problem',
    hero_point_1: 'Works on Linux, Windows, and macOS.',
    hero_point_2: 'Processes file content on your own computer.',
    hero_point_3: 'Simple interface designed for teachers and non-technical users.',
    hero_image_alt: 'Main window of ELPX Translator Desktop',
    what_eyebrow: 'What it is',
    what_title: 'A tool to translate eXeLearning materials with less manual work',
    what_card_1_title: 'What it does',
    what_card_1_body: 'It opens an <code>.elpx</code> file, detects translatable text, and generates a copy in the language you choose.',
    what_card_2_title: 'Who it is for',
    what_card_2_body: 'Mainly for teachers who already have materials and want to reuse them without translating everything again by hand.',
    what_card_3_title: 'What you do not need',
    what_card_3_body: 'You do not need to know programming, use a terminal, or understand technical details about AI models.',
    downloads_eyebrow: 'Downloads',
    downloads_title: 'Available versions',
    downloads_body: 'This page checks GitHub Releases and shows the latest published beta. On Linux you will see both the <code>.deb</code> package and the <code>AppImage</code>. When a truly ready stable version exists, it will also appear here.',
    downloads_beta_updates_note: 'If you want to receive beta update notices inside the program, enable that option in settings. It is disabled by default.',
    release_stable_label: 'Stable release',
    release_stable_copy: 'The recommended option for most people.',
    release_beta_label: 'Latest beta',
    release_beta_copy: 'If you want to try the newest changes early and help detect bugs.',
    steps_eyebrow: 'How it works',
    steps_title: 'Three steps',
    step_1_title: 'Open your file',
    step_1_body: 'Select the <code>.elpx</code> project you want to translate.',
    step_2_title: 'Choose languages',
    step_2_body: 'Set the source language and the target language.',
    step_3_title: 'Generate the translated copy',
    step_3_body: 'The application creates a new file so you can review it and keep working with it in eXeLearning.',
    performance_eyebrow: 'Performance',
    performance_title: 'What each mode means',
    performance_body: 'The application includes four modes to adapt better to your computer. You do not need technical knowledge: just choose the one that best fits how you work.',
    perf_card_1_title: 'Gentle',
    perf_card_1_body: 'Prioritizes keeping the computer responsive while you do other things. It may take longer, but it disturbs the rest of the system less.',
    perf_card_2_title: 'Balanced',
    perf_card_2_body: 'This is the recommended option for most people. It aims for a reasonable middle ground between speed and comfort.',
    perf_card_3_title: 'Fast',
    perf_card_3_body: 'Uses more resources to try to finish sooner. It can be useful if you want to reduce waiting time and do not need to use the computer much at the same time.',
    perf_card_4_title: 'Maximum',
    perf_card_4_body: 'Pushes the computer harder to go as fast as possible. It fits best when the machine is powerful and you will not be doing other important tasks at the same time.',
    requirements_eyebrow: 'Recommended hardware',
    requirements_title: 'Practical requirements',
    requirements_body: 'There is no strict list of exact minimum requirements, but these references help set expectations before installing it.',
    requirements_card_1_title: 'For comfortable use',
    requirements_card_1_body_1: 'A 64-bit computer with at least <strong>8 GB of RAM</strong> is usually a reasonable starting point for smoother work.',
    requirements_card_1_body_2: 'If the computer has more memory and several CPU cores, translation usually performs better, especially with large files.',
    requirements_card_2_title: 'What can happen on modest hardware',
    requirements_card_2_body_1: 'The application may work on more modest machines, but it is normal for it to take longer and for modes like <strong>Gentle</strong> or <strong>Balanced</strong> to make more sense.',
    requirements_card_2_body_2: 'The first run also needs free space to download the model and keep it in the local cache.',
    screenshots_eyebrow: 'Screenshots',
    screenshots_title: 'Inside the application',
    screenshot_1_alt: 'Main screen of the app',
    screenshot_1_caption: 'Main screen: input file, source language, target language, and progress.',
    screenshot_2_alt: 'Window with application information',
    screenshot_2_caption: 'The application itself includes project information and access to support.',
    privacy_eyebrow: 'Privacy and AI',
    privacy_title: 'Explained simply',
    privacy_card_1_title: 'How it uses AI',
    privacy_card_1_body_1: 'The application uses an open translation model to propose text in another language. Its role is to help you with automatic translation of the project content.',
    privacy_card_1_body_2: 'For most languages, the application uses <strong>M2M100 418M</strong>, an open model published by <strong>Facebook AI</strong>. It is prepared to run on a regular computer without depending on an external service.',
    privacy_card_1_body_3: 'When the translation includes <strong>Basque</strong>, the application uses open models from the <strong>OPUS-MT</strong> family, developed in the academic environment of <strong>Helsinki-NLP</strong> and the <strong>University of Helsinki</strong>.',
    privacy_card_1_body_4: 'In both cases these are <strong>open</strong> models intended to be downloaded and run locally. That is why translation is done on your computer and does not depend on a commercial external platform.',
    privacy_card_2_title: 'What happens to your data',
    privacy_card_2_body_1: 'Your file content is processed on your computer during translation.',
    privacy_card_2_body_2: 'It does not send your project to an external service for translation. It may only connect to the internet to download the model the first time and to check for new versions.',
    known_eyebrow: 'Known issues',
    known_title: 'Limitations worth keeping in mind',
    known_body: 'The application can save a lot of work, but there are still cases where manual review remains important.',
    known_card_1_title: 'Very short titles or little context',
    known_card_1_body_1: 'Some navigation titles, short activity names, or very short labels may be translated unnaturally or simply incorrectly.',
    known_card_1_body_2: 'This happens because when text is very short and provides little context, the model may interpret it as a proper name, a category, or a technical label different from what it actually is.',
    known_card_2_title: 'Complex interactive iDevices',
    known_card_2_body_1: 'Some iDevices with their own logic, internal messages, or special formats are not always translated completely.',
    known_card_2_body_2: 'In these cases, part of the content may remain in the original language, some automatic texts may not change, or certain elements may need manual adjustment inside eXeLearning.',
    known_card_3_title: 'Final review is still needed',
    known_card_3_body_1: 'The tool is designed to speed up work, not to replace final review of the material.',
    known_card_3_body_2: 'It is wise to check titles, instructions, interactive activities, text embedded in images or tables, and any content with sensitive educational value.',
    known_card_4_title: 'Uneven quality depending on language and content',
    known_card_4_body_1: 'Translation quality may vary depending on the language pair, the text type, and the project structure.',
    known_card_4_body_2: 'Longer texts with context usually work better than isolated labels, menus, activity names, or very technical fragments.',
    faq_eyebrow: 'Common questions',
    faq_title: 'What matters before you start',
    faq_1_title: 'Is this an official INTEF or eXeLearning project?',
    faq_1_body: 'No. It is an independent project and is not officially affiliated with INTEF or eXeLearning.',
    faq_2_title: 'Do I always need internet?',
    faq_2_body: 'No. The first time it may be needed to download the model and also to check for updates. After that, translation runs locally.',
    faq_3_title: 'Will it translate any file perfectly the first time?',
    faq_3_body: 'It is better not to promise that. The application is designed to save a lot of work, but reviewing the final result before publishing is still advisable.',
    faq_4_title: 'What should I do if something goes wrong?',
    faq_4_body: 'Use the suggestions and bugs link. If you can, say which operating system you use and attach the file or a short explanation of the problem.',
    footer_body: 'ELPX Translator Desktop is an independent project for translating <code>.elpx</code> files.',
    footer_author: 'Created by <strong>Juan José de Haro</strong>.',
    footer_license: 'Free software distributed under the <strong>GNU AGPLv3 or later</strong> license.',
    footer_repo: 'Repository',
    footer_releases: 'Releases',
    footer_issues: 'Suggestions and bugs',
    release_loading: 'Loading...',
    release_no_artifacts: 'The release exists, but no attached artifacts are shown yet.',
    release_no_stable: 'No stable release',
    release_no_beta: 'No published beta',
    release_unavailable: 'Unavailable',
    download_linux_deb: '.deb for Debian and compatible derivatives',
    download_linux_appimage: 'AppImage for other distributions',
    download_windows: '.exe',
    download_macos: '.dmg',
    download_prefix: 'Download',
  },
  ca: {
    meta_description: 'Aplicació d’escriptori per traduir fitxers .elpx de manera local, pensada per a professorat i usuaris no tècnics.',
    language_label: 'Idioma',
    nav_downloads: 'Descàrregues',
    nav_screenshots: 'Captures',
    nav_privacy: 'Privacitat',
    nav_issues: 'Suggeriments i errors',
    hero_eyebrow: 'Per a professorat i persones no tècniques',
    hero_lead: 'ELPX Translator Desktop serveix per traduir projectes d’eXeLearning sense dependre de serveis externs. Està pensat per estalviar temps quan adaptes materials ja creats a un altre idioma.',
    hero_cta_downloads: 'Veure descàrregues',
    hero_cta_issues: 'Informar d’un suggeriment o problema',
    hero_point_1: 'Funciona a Linux, Windows i macOS.',
    hero_point_2: 'Processa el contingut del fitxer al teu equip.',
    hero_point_3: 'Interfície senzilla, pensada per a professorat i persones no tècniques.',
    hero_image_alt: 'Finestra principal d’ELPX Translator Desktop',
    what_eyebrow: 'Què és',
    what_title: 'Una eina per traduir materials d’eXeLearning amb menys feina manual',
    what_card_1_title: 'Què fa',
    what_card_1_body: 'Obre un fitxer <code>.elpx</code>, detecta el text traduïble i genera una còpia en l’idioma que triïs.',
    what_card_2_title: 'Per a qui està pensada',
    what_card_2_body: 'Sobretot per a docents que ja tenen materials creats i els volen reutilitzar sense tornar-ho a traduir tot a mà.',
    what_card_3_title: 'Què no necessites',
    what_card_3_body: 'No cal saber programar, fer servir terminal ni entendre detalls tècnics sobre models d’IA.',
    downloads_eyebrow: 'Descàrregues',
    downloads_title: 'Versions disponibles',
    downloads_body: 'La pàgina consulta GitHub Releases i mostra l’última beta publicada. A Linux hi veuràs tant el paquet <code>.deb</code> com l’<code>AppImage</code>. Quan hi hagi una versió estable realment llesta, també apareixerà aquí.',
    downloads_beta_updates_note: 'Si vols rebre avisos de versions beta des del programa, activa aquesta opció a la configuració. Per defecte està desactivada.',
    release_stable_label: 'Versió estable',
    release_stable_copy: 'L’opció recomanada per a la majoria de persones.',
    release_beta_label: 'Última beta',
    release_beta_copy: 'Si vols provar abans els canvis més recents i ajudar a detectar errors.',
    steps_eyebrow: 'Com es fa servir',
    steps_title: 'Tres passos',
    step_1_title: 'Obre el fitxer',
    step_1_body: 'Selecciona el projecte <code>.elpx</code> que vols traduir.',
    step_2_title: 'Tria idiomes',
    step_2_body: 'Marca l’idioma d’origen i l’idioma de destí.',
    step_3_title: 'Genera la còpia traduïda',
    step_3_body: 'L’aplicació crea un fitxer nou perquè el puguis revisar i continuar treballant-lo a eXeLearning.',
    performance_eyebrow: 'Rendiment',
    performance_title: 'Què significa cada mode',
    performance_body: 'L’aplicació inclou quatre modes per adaptar-se millor al teu equip. No cal entendre detalls tècnics: només has de triar el que s’ajusti millor a la teva manera de treballar.',
    perf_card_1_title: 'Suau',
    perf_card_1_body: 'Prioritza que l’ordinador continuï responent amb comoditat mentre fas altres coses. Pot trigar més, però molesta menys la resta del sistema.',
    perf_card_2_title: 'Equilibrat',
    perf_card_2_body: 'És l’opció recomanada per a la majoria de persones. Busca un punt raonable entre velocitat i comoditat d’ús.',
    perf_card_3_title: 'Ràpid',
    perf_card_3_body: 'Fa servir més recursos per intentar acabar abans. Pot ser útil si vols reduir temps i no necessites fer gaire ús de l’equip alhora.',
    perf_card_4_title: 'Màxim',
    perf_card_4_body: 'Esprem més l’ordinador per anar tan ràpid com sigui possible. Convé quan l’equip és potent i no faràs altres tasques importants al mateix temps.',
    requirements_eyebrow: 'Equip recomanat',
    requirements_title: 'Requisits orientatius',
    requirements_body: 'No hi ha una llista tancada de requisits mínims exactes, però aquestes referències ajuden a saber què esperar abans d’instal·lar-la.',
    requirements_card_1_title: 'Per a un ús còmode',
    requirements_card_1_body_1: 'Un equip de 64 bits amb almenys <strong>8 GB de RAM</strong> sol ser una base raonable per treballar amb més tranquil·litat.',
    requirements_card_1_body_2: 'Si l’ordinador té més memòria i diversos nuclis de CPU, la traducció sol anar millor, sobretot amb fitxers grans.',
    requirements_card_2_title: 'Què pot passar en equips modestos',
    requirements_card_2_body_1: 'L’aplicació pot funcionar en equips més justos, però és normal que trigui més i que convingui fer servir modes com <strong>Suau</strong> o <strong>Equilibrat</strong>.',
    requirements_card_2_body_2: 'La primera execució també necessita espai lliure per descarregar el model i deixar-lo desat a la memòria cau local.',
    screenshots_eyebrow: 'Captures',
    screenshots_title: 'L’aplicació per dins',
    screenshot_1_alt: 'Pantalla principal de l’aplicació',
    screenshot_1_caption: 'Pantalla principal: fitxer d’entrada, idioma d’origen, idioma de destí i progrés.',
    screenshot_2_alt: 'Finestra amb informació de l’aplicació',
    screenshot_2_caption: 'La mateixa aplicació inclou informació sobre el projecte i accés a suport.',
    privacy_eyebrow: 'Privacitat i IA',
    privacy_title: 'Explicat de manera simple',
    privacy_card_1_title: 'Com fa servir la IA',
    privacy_card_1_body_1: 'L’aplicació fa servir un model obert de traducció per proposar el text en un altre idioma. La seva feina és ajudar-te amb la traducció automàtica del contingut del projecte.',
    privacy_card_1_body_2: 'Per a la majoria d’idiomes, l’aplicació fa servir <strong>M2M100 418M</strong>, un model obert publicat per <strong>Facebook AI</strong>. Està preparat per executar-se en un ordinador corrent sense dependre d’un servei extern.',
    privacy_card_1_body_3: 'Quan la traducció inclou <strong>euskera</strong>, l’aplicació fa servir models oberts de la família <strong>OPUS-MT</strong>, desenvolupats en l’entorn acadèmic de <strong>Helsinki-NLP</strong> i la <strong>Universitat d’Hèlsinki</strong>.',
    privacy_card_1_body_4: 'En tots dos casos es tracta de models <strong>oberts</strong>, pensats per poder-se descarregar i executar localment. Per això la traducció es fa al teu equip i no depèn d’una plataforma comercial externa.',
    privacy_card_2_title: 'Què passa amb les teves dades',
    privacy_card_2_body_1: 'El contingut del fitxer es processa al teu ordinador durant la traducció.',
    privacy_card_2_body_2: 'No envia el teu projecte a un servei extern per traduir-lo. Només es pot connectar a internet per descarregar el model la primera vegada i per comprovar si hi ha noves versions.',
    known_eyebrow: 'Problemes coneguts',
    known_title: 'Limitacions que convé tenir en compte',
    known_body: 'L’aplicació pot estalviar molta feina, però encara hi ha casos en què la revisió manual continua sent important.',
    known_card_1_title: 'Títols molt curts o amb poc context',
    known_card_1_body_1: 'Alguns títols de navegació, noms breus d’activitats o etiquetes molt curtes es poden traduir de manera poc natural o directament incorrecta.',
    known_card_1_body_2: 'Això passa perquè, quan el text és molt breu i aporta poc context, el model el pot interpretar com si fos un nom propi, una categoria o una etiqueta tècnica diferent del que realment és.',
    known_card_2_title: 'iDevices interactius complexos',
    known_card_2_body_1: 'Determinats iDevices amb lògica pròpia, missatges interns o formats especials no sempre es tradueixen completament.',
    known_card_2_body_2: 'En aquests casos, pot passar que part del contingut quedi en l’idioma original, que alguns textos automàtics no canviïn o que certs elements necessitin retoc manual dins d’eXeLearning.',
    known_card_3_title: 'Cal revisió final',
    known_card_3_body_1: 'L’eina està pensada per accelerar la feina, no per substituir una revisió final del material.',
    known_card_3_body_2: 'Convé comprovar especialment els títols, les instruccions, les activitats interactives, els textos incrustats en imatges o taules i qualsevol contingut amb valor didàctic sensible.',
    known_card_4_title: 'Qualitat desigual segons idioma i contingut',
    known_card_4_body_1: 'La qualitat de la traducció pot variar segons el parell d’idiomes, el tipus de text i l’estructura del projecte.',
    known_card_4_body_2: 'Els textos llargs i amb context solen sortir millor que les etiquetes soltes, els menús, els noms d’activitats o els fragments molt tècnics.',
    faq_eyebrow: 'Preguntes habituals',
    faq_title: 'El que importa abans de començar',
    faq_1_title: 'És un projecte oficial de l’INTEF o d’eXeLearning?',
    faq_1_body: 'No. És un projecte independent i no està afiliat oficialment amb l’INTEF ni amb eXeLearning.',
    faq_2_title: 'Necessito internet sempre?',
    faq_2_body: 'No. La primera vegada pot caldre per descarregar el model i també per comprovar si hi ha noves versions. Després, la traducció treballa en local.',
    faq_3_title: 'Serveix per a qualsevol fitxer perfecte a la primera?',
    faq_3_body: 'No convé prometre això. L’aplicació està pensada per estalviar molta feina, però sempre és recomanable revisar el resultat final abans de publicar-lo.',
    faq_4_title: 'Què faig si alguna cosa va malament?',
    faq_4_body: 'Fes servir l’enllaç de suggeriments i errors. Si pots, indica quin sistema operatiu fas servir i adjunta el fitxer o una explicació breu del problema.',
    footer_body: 'ELPX Translator Desktop és un projecte independent per traduir fitxers <code>.elpx</code>.',
    footer_author: 'Creat per <strong>Juan José de Haro</strong>.',
    footer_license: 'Programari lliure distribuït sota la llicència <strong>GNU AGPLv3 o posterior</strong>.',
    footer_repo: 'Repositori',
    footer_releases: 'Releases',
    footer_issues: 'Suggeriments i errors',
    release_loading: 'Carregant...',
    release_no_artifacts: 'La release existeix, però encara no hi apareixen artefactes adjunts.',
    release_no_stable: 'Sense release estable',
    release_no_beta: 'Sense beta publicada',
    release_unavailable: 'No disponible',
    download_linux_deb: '.deb per a Debian i derivats compatibles',
    download_linux_appimage: 'AppImage per a altres distribucions',
    download_windows: '.exe',
    download_macos: '.dmg',
    download_prefix: 'Descarrega',
  },
  eu: {
    meta_description: '.elpx fitxategiak lokalean itzultzeko mahaigaineko aplikazioa, irakasleentzat eta erabiltzaile ez teknikoentzat pentsatua.',
    language_label: 'Hizkuntza',
    nav_downloads: 'Deskargak',
    nav_screenshots: 'Pantaila-argazkiak',
    nav_privacy: 'Pribatutasuna',
    nav_issues: 'Iradokizunak eta akatsak',
    hero_eyebrow: 'Irakasleentzat eta erabiltzaile ez teknikoentzat',
    hero_lead: 'ELPX Translator Desktop-ek eXeLearning proiektuak kanpoko zerbitzuen mende egon gabe itzultzen laguntzen du. Beste hizkuntza batera egokitzeko lehendik sortutako materialekin denbora aurrezteko pentsatuta dago.',
    hero_cta_downloads: 'Deskargak ikusi',
    hero_cta_issues: 'Iradokizun edo arazo baten berri eman',
    hero_point_1: 'Linux, Windows eta macOSen dabil.',
    hero_point_2: 'Fitxategiaren edukia zure ordenagailuan prozesatzen du.',
    hero_point_3: 'Interfaze sinplea, irakasleentzat eta erabiltzaile ez teknikoentzat pentsatua.',
    hero_image_alt: 'ELPX Translator Desktop-en leiho nagusia',
    what_eyebrow: 'Zer den',
    what_title: 'eXeLearning materialak eskuzko lan gutxiagorekin itzultzeko tresna',
    what_card_1_title: 'Zer egiten duen',
    what_card_1_body: '<code>.elpx</code> fitxategi bat ireki, itzul daitekeen testua detektatu eta aukeratzen duzun hizkuntzan kopia bat sortzen du.',
    what_card_2_title: 'Norentzat den',
    what_card_2_body: 'Batez ere materialak lehendik dituzten eta dena eskuz berriro itzuli gabe berrerabili nahi dituzten irakasleentzat.',
    what_card_3_title: 'Zer ez duzun behar',
    what_card_3_body: 'Ez da beharrezkoa programatzen jakitea, terminala erabiltzea edo IA ereduei buruzko xehetasun teknikoak ulertzea.',
    downloads_eyebrow: 'Deskargak',
    downloads_title: 'Eskuragarri dauden bertsioak',
    downloads_body: 'Orri honek GitHub Releases kontsultatzen du eta argitaratutako azken beta erakusten du. Linuxen <code>.deb</code> paketea eta <code>AppImage</code>a ikusiko dituzu. Benetan prest dagoen bertsio egonkor bat dagoenean, hemen ere agertuko da.',
    downloads_beta_updates_note: 'Programaren barruan beta bertsioen oharrak jaso nahi badituzu, aktibatu aukera hori ezarpenetan. Lehenespenez desgaituta dago.',
    release_stable_label: 'Bertsio egonkorra',
    release_stable_copy: 'Jende gehienarentzat gomendatutako aukera.',
    release_beta_label: 'Azken beta',
    release_beta_copy: 'Azken aldaketak lehenago probatu eta akatsak detektatzen lagundu nahi badituzu.',
    steps_eyebrow: 'Nola erabiltzen den',
    steps_title: 'Hiru urrats',
    step_1_title: 'Ireki zure fitxategia',
    step_1_body: 'Hautatu itzuli nahi duzun <code>.elpx</code> proiektua.',
    step_2_title: 'Aukeratu hizkuntzak',
    step_2_body: 'Adierazi jatorrizko hizkuntza eta helburuko hizkuntza.',
    step_3_title: 'Sortu itzulitako kopia',
    step_3_body: 'Aplikazioak fitxategi berri bat sortzen du berrikusi eta eXeLearning-en lanean jarraitu ahal izateko.',
    performance_eyebrow: 'Errendimendua',
    performance_title: 'Zer esan nahi duen modu bakoitzak',
    performance_body: 'Aplikazioak lau modu ditu zure ekipoara hobeto egokitzeko. Ez da xehetasun teknikoak ulertu behar: aukeratu besterik ez dago zure lan egiteko moduarekin ondoen egokitzen dena.',
    perf_card_1_title: 'Leuna',
    perf_card_1_body: 'Lehenesten du ordenagailuak eroso erantzuten jarraitzea beste gauza batzuk egiten dituzun bitartean. Gehiago iraun dezake, baina sistemari gutxiago eragiten dio.',
    perf_card_2_title: 'Orekatua',
    perf_card_2_body: 'Hau da jende gehienarentzat gomendatutako aukera. Abiaduraren eta erabilera-erosotasunaren arteko erdiko puntu arrazoizkoa bilatzen du.',
    perf_card_3_title: 'Azkarra',
    perf_card_3_body: 'Baliabide gehiago erabiltzen ditu lehenago amaitzen saiatzeko. Itxaronaldia murriztu nahi baduzu eta aldi berean ordenagailua asko erabili behar ez baduzu, erabilgarria izan daiteke.',
    perf_card_4_title: 'Gehienezkoa',
    perf_card_4_body: 'Ordenagailua gehiago estutzen du ahalik eta azkarren joateko. Egokia da makina indartsua denean eta aldi berean beste lan garrantzitsurik egingo ez duzunean.',
    requirements_eyebrow: 'Gomendatutako ekipoa',
    requirements_title: 'Gutxi gorabeherako eskakizunak',
    requirements_body: 'Ez dago gutxieneko eskakizun zehatzen zerrenda itxirik, baina erreferentzia hauek instalatu aurretik zer espero den ulertzen laguntzen dute.',
    requirements_card_1_title: 'Erabilera eroso baterako',
    requirements_card_1_body_1: '64 biteko ekipo bat eta gutxienez <strong>8 GB RAM</strong> izatea oinarri zentzuzkoa izan ohi da lasaiago lan egiteko.',
    requirements_card_1_body_2: 'Ordenagailuak memoria gehiago eta CPU nukleo batzuk baditu, itzulpena hobeto joan ohi da, batez ere fitxategi handiekin.',
    requirements_card_2_title: 'Ekipo xumeetan zer gerta daitekeen',
    requirements_card_2_body_1: 'Aplikazioak ekipo apalagoetan funtziona dezake, baina normala da gehiago irautea eta <strong>Leuna</strong> edo <strong>Orekatua</strong> bezalako moduak egokiagoak izatea.',
    requirements_card_2_body_2: 'Lehen exekuzioan, gainera, leku librea behar da eredua deskargatu eta tokiko cachean gordetzeko.',
    screenshots_eyebrow: 'Pantaila-argazkiak',
    screenshots_title: 'Aplikazioa barrutik',
    screenshot_1_alt: 'Aplikazioaren pantaila nagusia',
    screenshot_1_caption: 'Pantaila nagusia: sarrerako fitxategia, jatorrizko hizkuntza, helburuko hizkuntza eta aurrerapena.',
    screenshot_2_alt: 'Aplikazioaren informazio-leihoa',
    screenshot_2_caption: 'Aplikazioak berak proiektuari buruzko informazioa eta laguntzarako sarbidea eskaintzen du.',
    privacy_eyebrow: 'Pribatutasuna eta IA',
    privacy_title: 'Era errazean azaldua',
    privacy_card_1_title: 'Nola erabiltzen duen IA',
    privacy_card_1_body_1: 'Aplikazioak itzulpen eredu ireki bat erabiltzen du testua beste hizkuntza batean proposatzeko. Bere lana proiektuaren edukia automatikoki itzultzen laguntzea da.',
    privacy_card_1_body_2: 'Hizkuntza gehienetan aplikazioak <strong>M2M100 418M</strong> erabiltzen du, <strong>Facebook AI</strong>k argitaratutako eredu irekia. Kanpoko zerbitzu baten mende egon gabe ordenagailu arrunt batean exekutatzeko prestatuta dago.',
    privacy_card_1_body_3: 'Itzulpenak <strong>euskara</strong> duenean, aplikazioak <strong>OPUS-MT</strong> familiako eredu irekiak erabiltzen ditu, <strong>Helsinki-NLP</strong>ren eta <strong>Helsinkiko Unibertsitatearen</strong> ingurune akademikoan garatuak.',
    privacy_card_1_body_4: 'Bi kasuetan eredu <strong>irekiak</strong> dira, lokalki deskargatu eta exekutatzeko pentsatuak. Horregatik itzulpena zure ekipoan egiten da eta ez dago kanpoko plataforma komertzial baten mende.',
    privacy_card_2_title: 'Zer gertatzen den zure datuekin',
    privacy_card_2_body_1: 'Fitxategiaren edukia zure ordenagailuan prozesatzen da itzulpenean.',
    privacy_card_2_body_2: 'Ez du zure proiektua kanpoko zerbitzu batera bidaltzen itzultzeko. Internetera konekta daiteke eredua lehen aldian deskargatzeko eta bertsio berriak dauden egiaztatzeko bakarrik.',
    known_eyebrow: 'Arazo ezagunak',
    known_title: 'Kontuan hartu beharreko mugak',
    known_body: 'Aplikazioak lan asko aurrez dezake, baina oraindik badira eskuzko berrikuspena garrantzitsua den kasuak.',
    known_card_1_title: 'Izenburu oso laburrak edo testuinguru gutxikoak',
    known_card_1_body_1: 'Nabigazio-izenburu batzuk, jardueren izen laburrak edo etiketa oso motzak modu ez natural edo zuzenean okerrean itzul daitezke.',
    known_card_1_body_2: 'Hau gertatzen da testua oso laburra denean eta testuinguru nahikorik ematen ez duenean, ereduak izen propio, kategoria edo benetan ez den etiketa tekniko gisa interpreta dezakeelako.',
    known_card_2_title: 'iDevice interaktibo konplexuak',
    known_card_2_body_1: 'Bere logika propioa, barne-mezuak edo formatu bereziak dituzten iDevice batzuk ez dira beti osorik itzultzen.',
    known_card_2_body_2: 'Kasu horietan, edukiren bat jatorrizko hizkuntzan geratu daiteke, testu automatiko batzuk ez alda daitezke edo elementu batzuek eskuzko ukitua behar izan dezakete eXeLearning barruan.',
    known_card_3_title: 'Azken berrikuspena beharrezkoa da',
    known_card_3_body_1: 'Tresna lana azkartzeko pentsatuta dago, ez materialaren azken berrikuspena ordezkatzeko.',
    known_card_3_body_2: 'Komeni da bereziki egiaztatzea izenburuak, jarraibideak, jarduera interaktiboak, irudi edo tauletan txertatutako testuak eta balio didaktiko sentikorra duen edozein eduki.',
    known_card_4_title: 'Kalitate desberdina hizkuntzaren eta edukiaren arabera',
    known_card_4_body_1: 'Itzulpenaren kalitatea hizkuntza-bikotearen, testu motaren eta proiektuaren egituraren arabera alda daiteke.',
    known_card_4_body_2: 'Testuingurua duten testu luzeek normalean emaitza hobeak ematen dituzte etiketa solteek, menuek, jardueren izenek edo zati oso teknikoek baino.',
    faq_eyebrow: 'Ohiko galderak',
    faq_title: 'Hasi aurretik garrantzitsuena',
    faq_1_title: 'INTEFen edo eXeLearningen proiektu ofiziala al da?',
    faq_1_body: 'Ez. Proiektu independentea da eta ez dago ofizialki lotuta INTEFekin edo eXeLearningekin.',
    faq_2_title: 'Beti behar al dut internet?',
    faq_2_body: 'Ez. Lehen aldian eredua deskargatzeko eta eguneraketak egiaztatzeko behar izan daiteke. Ondoren, itzulpena lokalean egiten da.',
    faq_3_title: 'Edozein fitxategi primeran itzuliko du lehenengoan?',
    faq_3_body: 'Hobe da hori ez agintzea. Aplikazioa lan asko aurrezteko pentsatuta dago, baina argitaratu aurretik azken emaitza berrikustea gomendagarria da beti.',
    faq_4_title: 'Zer egin behar dut zerbait gaizki badoa?',
    faq_4_body: 'Erabili iradokizun eta akatsen esteka. Ahal baduzu, esan zer sistema eragile erabiltzen duzun eta erantsi fitxategia edo arazoaren azalpen laburra.',
    footer_body: 'ELPX Translator Desktop proiektu independentea da <code>.elpx</code> fitxategiak itzultzeko.',
    footer_author: '<strong>Juan José de Haro</strong>k sortua.',
    footer_license: '<strong>GNU AGPLv3 edo berriagoa</strong> lizentziapean banatutako software librea.',
    footer_repo: 'Biltegia',
    footer_releases: 'Releases',
    footer_issues: 'Iradokizunak eta akatsak',
    release_loading: 'Kargatzen...',
    release_no_artifacts: 'Release-a badago, baina oraindik ez da erantsitako artefakturik ageri.',
    release_no_stable: 'Bertsio egonkorrik ez',
    release_no_beta: 'Argitaratutako betarik ez',
    release_unavailable: 'Ez dago erabilgarri',
    download_linux_deb: '.deb Debian eta deribatu bateragarrietarako',
    download_linux_appimage: 'AppImage beste banaketa batzuetarako',
    download_windows: '.exe',
    download_macos: '.dmg',
    download_prefix: 'Deskargatu',
  },
  gl: {
    meta_description: 'Aplicación de escritorio para traducir ficheiros .elpx de forma local, pensada para profesorado e usuarios non técnicos.',
    language_label: 'Idioma',
    nav_downloads: 'Descargas',
    nav_screenshots: 'Capturas',
    nav_privacy: 'Privacidade',
    nav_issues: 'Suxestións e erros',
    hero_eyebrow: 'Para profesorado e persoas non técnicas',
    hero_lead: 'ELPX Translator Desktop serve para traducir proxectos de eXeLearning sen depender de servizos externos. Está pensado para aforrar tempo ao adaptar materiais xa creados a outro idioma.',
    hero_cta_downloads: 'Ver descargas',
    hero_cta_issues: 'Informar dunha suxestión ou dun problema',
    hero_point_1: 'Funciona en Linux, Windows e macOS.',
    hero_point_2: 'Procesa o contido do ficheiro no teu equipo.',
    hero_point_3: 'Interface sinxela, pensada para profesorado e persoas non técnicas.',
    hero_image_alt: 'Xanela principal de ELPX Translator Desktop',
    what_eyebrow: 'Que é',
    what_title: 'Unha ferramenta para traducir materiais de eXeLearning con menos traballo manual',
    what_card_1_title: 'Que fai',
    what_card_1_body: 'Abre un ficheiro <code>.elpx</code>, detecta o texto traducible e xera unha copia no idioma que escollas.',
    what_card_2_title: 'Para quen está pensada',
    what_card_2_body: 'Sobre todo para docentes que xa teñen materiais creados e queren reutilizalos sen volver traducilo todo á man.',
    what_card_3_title: 'Que non precisas',
    what_card_3_body: 'Non fai falta saber programar, usar terminal nin entender detalles técnicos sobre modelos de IA.',
    downloads_eyebrow: 'Descargas',
    downloads_title: 'Versións dispoñibles',
    downloads_body: 'A páxina consulta GitHub Releases e mostra a última beta publicada. En Linux verás tanto o paquete <code>.deb</code> como a <code>AppImage</code>. Cando haxa unha versión estable realmente lista, tamén aparecerá aquí.',
    downloads_beta_updates_note: 'Se queres recibir avisos de versións beta dentro do programa, activa esa opción na configuración. Por defecto está desactivada.',
    release_stable_label: 'Versión estable',
    release_stable_copy: 'A opción recomendada para a maioría da xente.',
    release_beta_label: 'Última beta',
    release_beta_copy: 'Se queres probar antes os cambios máis recentes e axudar a detectar fallos.',
    steps_eyebrow: 'Como se usa',
    steps_title: 'Tres pasos',
    step_1_title: 'Abre o teu ficheiro',
    step_1_body: 'Selecciona o proxecto <code>.elpx</code> que queres traducir.',
    step_2_title: 'Escolle idiomas',
    step_2_body: 'Marca o idioma de orixe e o idioma de destino.',
    step_3_title: 'Xera a copia traducida',
    step_3_body: 'A aplicación crea un novo ficheiro para que poidas revisalo e seguir traballando con el en eXeLearning.',
    performance_eyebrow: 'Rendemento',
    performance_title: 'Que significa cada modo',
    performance_body: 'A aplicación inclúe catro modos para adaptarse mellor ao teu equipo. Non fai falta entender detalles técnicos: chega con escoller o que mellor encaixe coa túa forma de traballar.',
    perf_card_1_title: 'Suave',
    perf_card_1_body: 'Prioriza que o ordenador siga respondendo con comodidade mentres fas outras cousas. Pode tardar máis, pero molesta menos ao resto do sistema.',
    perf_card_2_title: 'Equilibrado',
    perf_card_2_body: 'É a opción recomendada para a maioría da xente. Busca un punto razoable entre velocidade e comodidade de uso.',
    perf_card_3_title: 'Rápido',
    perf_card_3_body: 'Usa máis recursos para intentar rematar antes. Pode ser útil se queres reducir tempos e non precisas usar moito o equipo ao mesmo tempo.',
    perf_card_4_title: 'Máximo',
    perf_card_4_body: 'Espreme máis o ordenador para ir o máis rápido posible. Convén cando o equipo é potente e non vas facer outras tarefas importantes ao mesmo tempo.',
    requirements_eyebrow: 'Equipo recomendado',
    requirements_title: 'Requisitos orientativos',
    requirements_body: 'Non hai unha lista pechada de requisitos mínimos exactos, pero estas referencias axudan a saber que esperar antes de instalala.',
    requirements_card_1_title: 'Para un uso cómodo',
    requirements_card_1_body_1: 'Un equipo de 64 bits con polo menos <strong>8 GB de RAM</strong> adoita ser unha base razoable para traballar con máis tranquilidade.',
    requirements_card_1_body_2: 'Se o ordenador ten máis memoria e varios núcleos de CPU, a tradución adoita ir mellor, sobre todo con ficheiros grandes.',
    requirements_card_2_title: 'Que pode pasar en equipos modestos',
    requirements_card_2_body_1: 'A aplicación pode funcionar en equipos máis xustos, pero é normal que tarde máis e que conveña usar modos como <strong>Suave</strong> ou <strong>Equilibrado</strong>.',
    requirements_card_2_body_2: 'A primeira execución tamén precisa espazo libre para descargar o modelo e deixalo gardado na caché local.',
    screenshots_eyebrow: 'Capturas',
    screenshots_title: 'A aplicación por dentro',
    screenshot_1_alt: 'Pantalla principal da aplicación',
    screenshot_1_caption: 'Pantalla principal: ficheiro de entrada, idioma de orixe, idioma de destino e progreso.',
    screenshot_2_alt: 'Xanela con información da aplicación',
    screenshot_2_caption: 'A propia aplicación inclúe información sobre o proxecto e acceso a soporte.',
    privacy_eyebrow: 'Privacidade e IA',
    privacy_title: 'Explicado de forma simple',
    privacy_card_1_title: 'Como usa a IA',
    privacy_card_1_body_1: 'A aplicación usa un modelo aberto de tradución para propoñer o texto noutro idioma. O seu traballo é axudarche coa tradución automática do contido do proxecto.',
    privacy_card_1_body_2: 'Para a maioría dos idiomas, a aplicación usa <strong>M2M100 418M</strong>, un modelo aberto publicado por <strong>Facebook AI</strong>. Está preparado para executarse nun ordenador corrente sen depender dun servizo externo.',
    privacy_card_1_body_3: 'Cando a tradución inclúe <strong>éuscaro</strong>, a aplicación usa modelos abertos da familia <strong>OPUS-MT</strong>, desenvolvidos no ámbito académico de <strong>Helsinki-NLP</strong> e da <strong>Universidade de Helsinki</strong>.',
    privacy_card_1_body_4: 'En ambos casos trátase de modelos <strong>abertos</strong>, pensados para descargarse e executarse localmente. Por iso a tradución faise no teu equipo e non depende dunha plataforma comercial externa.',
    privacy_card_2_title: 'Que pasa cos teus datos',
    privacy_card_2_body_1: 'O contido do ficheiro procésase no teu ordenador durante a tradución.',
    privacy_card_2_body_2: 'Non envía o teu proxecto a un servizo externo para traducilo. Só pode conectarse a internet para descargar o modelo a primeira vez e para comprobar se hai novas versións.',
    known_eyebrow: 'Problemas coñecidos',
    known_title: 'Limitacións que convén ter en conta',
    known_body: 'A aplicación pode aforrar moito traballo, pero aínda hai casos nos que a revisión manual segue sendo importante.',
    known_card_1_title: 'Títulos moi curtos ou con pouco contexto',
    known_card_1_body_1: 'Algúns títulos de navegación, nomes breves de actividades ou etiquetas moi curtas poden traducirse dun xeito pouco natural ou directamente incorrecto.',
    known_card_1_body_2: 'Isto ocorre porque, cando o texto é moi breve e non achega contexto suficiente, o modelo pode interpretalo como se fose un nome propio, unha categoría ou unha etiqueta técnica diferente do que realmente é.',
    known_card_2_title: 'iDevices interactivos complexos',
    known_card_2_body_1: 'Determinados iDevices con lóxica propia, mensaxes internas ou formatos especiais non sempre se traducen completamente.',
    known_card_2_body_2: 'Nestes casos pode ocorrer que parte do contido quede no idioma orixinal, que algúns textos automáticos non cambien ou que certos elementos precisen retoque manual dentro de eXeLearning.',
    known_card_3_title: 'Revisión final necesaria',
    known_card_3_body_1: 'A ferramenta está pensada para acelerar o traballo, non para substituír unha revisión final do material.',
    known_card_3_body_2: 'Convén comprobar especialmente os títulos, as instrucións, as actividades interactivas, os textos incrustados en imaxes ou táboas e calquera contido con valor didáctico sensible.',
    known_card_4_title: 'Calidade desigual segundo idioma e contido',
    known_card_4_body_1: 'A calidade da tradución pode variar segundo o par de idiomas, o tipo de texto e a estrutura do proxecto.',
    known_card_4_body_2: 'Os textos longos e con contexto adoitan saír mellor que as etiquetas soltas, os menús, os nomes de actividades ou os fragmentos moi técnicos.',
    faq_eyebrow: 'Preguntas habituais',
    faq_title: 'O importante antes de empezar',
    faq_1_title: 'É un proxecto oficial do INTEF ou de eXeLearning?',
    faq_1_body: 'Non. É un proxecto independente e non está afiliado oficialmente co INTEF nin con eXeLearning.',
    faq_2_title: 'Necesito internet sempre?',
    faq_2_body: 'Non. A primeira vez pode facer falta para descargar o modelo e tamén para comprobar se hai novas versións. Despois, a tradución traballa en local.',
    faq_3_title: 'Serve para calquera ficheiro perfecto á primeira?',
    faq_3_body: 'Non convén prometer iso. A aplicación está pensada para aforrar moito traballo, pero sempre é recomendable revisar o resultado final antes de publicalo.',
    faq_4_title: 'Que fago se algo sae mal?',
    faq_4_body: 'Usa a ligazón de suxestións e erros. Se podes, indica que sistema operativo usas e achega o ficheiro ou unha explicación breve do problema.',
    footer_body: 'ELPX Translator Desktop é un proxecto independente para traducir ficheiros <code>.elpx</code>.',
    footer_author: 'Creado por <strong>Juan José de Haro</strong>.',
    footer_license: 'Software libre distribuído baixo licenza <strong>GNU AGPLv3 ou posterior</strong>.',
    footer_repo: 'Repositorio',
    footer_releases: 'Releases',
    footer_issues: 'Suxestións e erros',
    release_loading: 'Cargando...',
    release_no_artifacts: 'A release existe, pero aínda non aparecen artefactos anexos.',
    release_no_stable: 'Sen release estable',
    release_no_beta: 'Sen beta publicada',
    release_unavailable: 'Non dispoñible',
    download_linux_deb: '.deb para Debian e derivados compatibles',
    download_linux_appimage: 'AppImage para outras distribucións',
    download_windows: '.exe',
    download_macos: '.dmg',
    download_prefix: 'Descargar',
  },
};

let currentLanguage = 'es';
let releasesCache = null;

function getLanguagePack(language) {
  return SITE_I18N[language] || SITE_I18N.es;
}

function translate(language, key) {
  return getLanguagePack(language)[key] || SITE_I18N.es[key] || key;
}

function detectLanguage() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved && SUPPORTED_LANGUAGES.includes(saved)) {
    return saved;
  }

  const candidates = [...(navigator.languages || []), navigator.language, navigator.userLanguage].filter(Boolean);
  for (const candidate of candidates) {
    const code = String(candidate).toLowerCase().split('-', 1)[0];
    if (SUPPORTED_LANGUAGES.includes(code)) {
      return code;
    }
  }
  return 'es';
}

function applyStaticTranslations(language) {
  document.documentElement.lang = language;
  document.title = 'ELPX Translator Desktop';
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute('content', translate(language, 'meta_description'));
  }

  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const key = element.dataset.i18n;
    const value = translate(language, key);
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
        element.setAttribute(attribute.trim(), translate(language, key.trim()));
      }
    }
  });

  const picker = document.getElementById('language-picker');
  if (picker) {
    picker.value = language;
    picker.setAttribute('aria-label', translate(language, 'language_label'));
  }
}

function parseVersion(tag) {
  const match = String(tag || '').trim().match(/^v?(\d+)\.(\d+)\.(\d+)(?:(?:[~-]?beta|b)(\d+))?$/i);
  if (!match) return null;

  return {
    major: Number(match[1]),
    minor: Number(match[2]),
    patch: Number(match[3]),
    beta: match[4] ? Number(match[4]) : null,
  };
}

function compareVersions(left, right) {
  const a = parseVersion(left);
  const b = parseVersion(right);
  if (!a || !b) return 0;

  for (const key of ['major', 'minor', 'patch']) {
    if (a[key] !== b[key]) return a[key] - b[key];
  }

  if (a.beta === null && b.beta === null) return 0;
  if (a.beta === null) return 1;
  if (b.beta === null) return -1;
  return a.beta - b.beta;
}

function pickDownloads(assets, language) {
  const match = (pattern) => assets.find((asset) => pattern.test(asset.name));
  return [
    { label: 'Linux', hint: translate(language, 'download_linux_deb'), asset: match(/\.deb$/i) },
    { label: 'Linux', hint: translate(language, 'download_linux_appimage'), asset: match(/\.AppImage$/i) },
    { label: 'Windows', hint: translate(language, 'download_windows'), asset: match(/\.exe$/i) },
    { label: 'macOS', hint: translate(language, 'download_macos'), asset: match(/\.dmg$/i) },
  ].filter((item) => item.asset);
}

function renderRelease(cardId, release, fallbackText, language) {
  const card = document.getElementById(cardId);
  if (!card) return;

  const title = card.querySelector('[data-release-title]');
  const links = card.querySelector('.download-links');

  if (!release) {
    card.classList.add('is-hidden');
    if (title) {
      title.textContent = fallbackText;
    }
    links.innerHTML = '';
    return;
  }

  card.classList.remove('is-hidden');
  if (title) {
    title.textContent = `${release.name || release.tag_name}`;
  }
  const downloads = pickDownloads(release.assets || [], language);
  links.innerHTML = downloads.length
    ? downloads.map((item) => `
        <a class="download-link" href="${item.asset.browser_download_url}" target="_blank" rel="noopener noreferrer">
          <span>${item.label}</span>
          <span>${translate(language, 'download_prefix')} ${item.hint}</span>
        </a>
      `).join('')
    : `<p class="release-copy">${translate(language, 'release_no_artifacts')}</p>`;
}

function renderReleases(language) {
  if (!releasesCache) {
    return;
  }

  const stable = releasesCache.find((release) => !release.prerelease && !release.draft);
  const latestBeta = releasesCache.find((release) => release.prerelease && !release.draft);
  const beta = latestBeta && (!stable || compareVersions(latestBeta.tag_name, stable.tag_name) > 0)
    ? latestBeta
    : null;

  renderRelease('stable-release', stable, translate(language, 'release_no_stable'), language);
  renderRelease('beta-release', beta, translate(language, 'release_no_beta'), language);
}

async function loadReleases() {
  try {
    const response = await fetch(API_URL, {
      headers: { Accept: 'application/vnd.github+json' },
    });
    if (!response.ok) throw new Error('GitHub API error');
    releasesCache = await response.json();
    renderReleases(currentLanguage);
  } catch (error) {
    renderRelease('stable-release', null, translate(currentLanguage, 'release_unavailable'), currentLanguage);
    renderRelease('beta-release', null, translate(currentLanguage, 'release_unavailable'), currentLanguage);
  }
}

function applyLanguage(language) {
  currentLanguage = SUPPORTED_LANGUAGES.includes(language) ? language : 'es';
  localStorage.setItem(STORAGE_KEY, currentLanguage);
  applyStaticTranslations(currentLanguage);
  renderReleases(currentLanguage);
}

function initLanguagePicker() {
  const picker = document.getElementById('language-picker');
  if (!picker) {
    return;
  }

  picker.addEventListener('change', (event) => {
    applyLanguage(event.target.value);
  });
}

applyLanguage(detectLanguage());
initLanguagePicker();

document.querySelectorAll('[data-release-title]').forEach((element) => {
  element.textContent = translate(currentLanguage, 'release_loading');
});

loadReleases();
