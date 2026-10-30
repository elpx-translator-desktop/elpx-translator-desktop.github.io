# 1. La web y la versión web no recogen estadísticas de uso

Fecha: 2026-10-30 · Estado: aceptado

## Contexto

Desde marzo de 2026 la web del proyecto (`index.html`) y la versión web (`app/index.html`) enviaban cada visita a un contador propio en bilateria.org (`track.php`), con dos identificadores: `elpx-translator-desktop` para la web y `elpx-translator-web` para la versión web. Lo hacía `docs/analytics.js`, que leía la dirección del contador de unas etiquetas `meta` y mandaba la dirección de la página y la de procedencia. No usaba cookies; guardaba en el navegador la hora de la última visita para no contarla dos veces en 30 minutos.

El programa de escritorio nunca ha llevado ese contador: en ninguna versión publicada, de la 0.1.0 a la 0.1.17, el código de `src/` ni el empaquetado llaman a bilateria.org. Sus únicas conexiones son la descarga del modelo, la comprobación de versiones nuevas en GitHub y, si el usuario lo activa, el proveedor de API que elija.

La evaluación con la rúbrica VCER de la guía «Vibe coding responsable» puntúa con 0 el punto de datos personales si el recurso lleva analítica, sea propia o ajena. Además, la dirección de procedencia puede delatar el aula virtual o la página desde la que se abre la herramienta.

## Decisión

Se retira toda la analítica de la web y de la versión web: las etiquetas `meta` (`analytics-endpoint`, `analytics-stats-url`, `analytics-site-id`) y la carga de `docs/analytics.js` en las dos páginas, y el propio `docs/analytics.js`. Los textos de privacidad no mencionaban el contador y siguen describiendo lo que hacen la web y el programa.

No se publica una versión nueva del programa de escritorio: su código no cambia, y una release sin cambios haría que todas las copias instaladas avisaran de una actualización que no aporta nada. La web se publica en GitHub Pages desde la rama `main`, como los demás cambios de la web.

## Alternativas descartadas

- **Mantener el contador propio.** Aunque no usaba cookies, seguía enviando la dirección de la página y la de procedencia a un servidor propio, y la rúbrica VCER puntúa con 0 cualquier analítica.

## Consecuencias

- Ya no hay cifras de uso de la web ni de la versión web.
- Los datos y los archivos del contador en el alojamiento de IONOS (`/app/estadistica/elpx-translator-desktop/` y `/app/estadistica/elpx-translator-web/`) se archivan y se borran aparte, fuera de este repositorio.
- Cuando desaparezca el servicio, las versiones instaladas del programa de escritorio no se ven afectadas, porque nunca lo han usado. La web y la versión web se sirven siempre desde GitHub Pages, así que tras el despliegue nadie carga ya el contador. Si un navegador conserva en caché una copia antigua de la página, la petición a `track.php` falla en silencio: se hace después del evento `load`, el error (`onerror`) o un plazo de 4 segundos la descartan, y no muestra mensajes ni retrasa la carga. Se comprobó en Chromium con Playwright, respondiendo 404 a `track.php`: las dos páginas cargaron con normalidad y solo quedó el aviso de recurso no encontrado en la consola del navegador.
