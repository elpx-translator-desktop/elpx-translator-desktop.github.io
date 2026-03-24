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
pyinstaller --name ELPXTranslatorDesktop --windowed --noconfirm --clean src/elpx_translator_desktop/app.py
```

Notas:

- Linux genera un build para Linux.
- Windows genera un build para Windows.
- macOS genera un build para macOS.
- La primera ejecucion seguira descargando el modelo si no esta en la cache local del usuario.
- GitHub Actions genera artefactos para Linux, Windows y macOS.

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
