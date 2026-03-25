# ELPX Translator Desktop

Aplicacion de escritorio multiplataforma para traducir proyectos `.elpx` localmente.

Objetivos:

- Linux, Windows y macOS
- procesamiento local
- misma estructura `.elpx`
- mejor rendimiento que la version web en navegador

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

## Notas

- La primera ejecucion descarga el modelo y el tokenizador en la cache local del usuario.
- La traduccion se hace sobre `content.xml` y preserva la estructura del `.elpx`.
- El repo usa por defecto el modelo `gn64/M2M100_418M_CTranslate2`.
- El motor elige automaticamente un perfil conservador segun la maquina:
  reserva nucleos para el sistema, limita los workers en CPU y baja la prioridad del proceso para evitar bloquear el equipo.
- La app incluye un boton `Configuracion` con cuatro modos:
  `Suave`, `Equilibrado`, `Rapido` y `Maximo`.
- Si cambias la configuracion durante una traduccion, se aplicara en la siguiente.
- La app incluye un boton `Parar` para cancelar la traduccion actual y volver a lanzarla con otra configuracion.
