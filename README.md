# ELPX Translator

Herramienta para traducir proyectos `.elpx` con version de escritorio y version web.

La version de escritorio trabaja en local, en tu propio equipo. La version web funciona en el navegador y usa la clave API del propio usuario.

Objetivos:

- Linux, Windows y macOS
- procesamiento local por defecto
- version web sin backend propio
- modo opcional por API con clave propia del usuario
- misma estructura `.elpx`
- reconstruccion conservadora del `.elpx`

## Stack

- Python 3.11+
- PySide6 para la interfaz
- CTranslate2 para la inferencia
- Transformers solo para el tokenizador

## Desarrollo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m elpx_translator_desktop
```

## Version web

El repo incluye una app web en `app/`, pensada para publicarse en GitHub Pages sin backend propio.

- La web informativa principal sigue en `index.html` y `docs/`.
- La version web abre el `.elpx` en navegador, traduce usando la API del usuario y reconstruye el archivo.
- No sustituye al modo local de escritorio: es una ruta web separada para quien prefiera trabajar desde el navegador.

## Empaquetado

El binario final se debe construir en cada sistema operativo de destino:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[build]
wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
APPIMAGE_TOOL="./appimagetool-x86_64.AppImage --appimage-extract-and-run" ./packaging/linux/build-linux-artifacts.sh
```

Notas:

- Linux genera un paquete `.deb`.
- Linux genera tambien una `AppImage` para distribucion mas portable entre distros.
- El build de Linux valida la `glibc` requerida por el `libpython` empaquetado. Por defecto exige una linea base maxima `2.35`, para que el `.deb` siga siendo instalable en Ubuntu 22.04+, Debian 12 / MX Linux 23 y otras distros con `glibc` compatible.
- Si necesitas otra politica de compatibilidad, puedes ajustar `GLIBC_BASELINE`, pero el paquete siempre debe construirse en una distro igual o mas antigua que la minima soportada.
- Windows genera un instalador `.exe`.
- macOS genera una imagen `.dmg`.
- La primera ejecucion seguira descargando el modelo si no esta en la cache local del usuario.
- GitHub Actions genera artefactos nativos para Linux, Windows y macOS en cada release.
- La secuencia correcta para publicar versiones y evitar errores de versionado esta en `RELEASING.md`.

## Notas

- La primera ejecucion descarga el modelo y el tokenizador en la cache local del usuario.
- La traduccion se hace sobre `content.xml` y preserva la estructura del `.elpx`.
- El modelo general del repo es `gn64/M2M100_418M_CTranslate2`.
- Para traducciones con euskera se usan modelos `OPUS-MT` específicos: `gaudi/opus-mt-es-eu-ctranslate2`, `gaudi/opus-mt-eu-es-ctranslate2`, `gaudi/opus-mt-en-eu-ctranslate2` y `gaudi/opus-mt-eu-en-ctranslate2`.
- El motor elige automaticamente un perfil conservador segun la maquina:
  reserva nucleos para el sistema, limita los workers en CPU y baja la prioridad del proceso para evitar bloquear el equipo.
- La app incluye un boton `Configuracion` con cuatro modos:
  `Suave`, `Equilibrado`, `Rapido` y `Maximo`.
- Si cambias la configuracion durante una traduccion, se aplicara en la siguiente.
- La app incluye un boton `Parar` para cancelar la traduccion actual y volver a lanzarla con otra configuracion.

## Modo API opcional

La app de escritorio sigue siendo local por defecto. El modo por API es opcional y esta pensado para usuarios que quieran usar su propia cuenta de proveedor.

- Proveedores disponibles: `OpenAI API`, `Gemini API`, `Anthropic API` y `DeepSeek API`.
- La clave API la aporta el propio usuario.
- Los modelos remotos se cargan al pulsar `Actualizar modelos`.
- El idioma de destino admite un codigo personalizado en modo API, por ejemplo `sv`, `ja`, `pt-BR` o `zh-CN`.
- Si activas este modo, el contenido traducible se enviara al proveedor externo elegido.

Obtener claves API:

- OpenAI: `https://platform.openai.com/api-keys`
- Gemini: `https://aistudio.google.com/api-keys`
- Anthropic: `https://console.anthropic.com/settings/keys`
- DeepSeek: `https://platform.deepseek.com/api_keys`

Notas importantes:

- La clave API se guarda localmente en la configuracion del programa en texto plano.
- Puedes borrar la clave guardada desde `Configuracion`.
- La version web usa la clave API guardada en el navegador y mantiene claves separadas por proveedor.
- La version web tambien permite usar `OpenAI API` con tu propia clave desde el navegador.
