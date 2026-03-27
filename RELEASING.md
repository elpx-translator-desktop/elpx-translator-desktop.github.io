# Publicacion de Releases

Este repositorio publica binarios nativos para Linux, Windows y macOS mediante GitHub Releases y el workflow `Build Desktop`.

## Regla principal

No crear nunca el commit de version, el tag y la release en paralelo.

Si el tag se crea antes de que termine el commit de version, la release puede apuntar al commit anterior y generar artefactos con una version equivocada.

## Secuencia correcta

1. Actualizar la version en `pyproject.toml` y en `src/elpx_translator_desktop/__init__.py`.
   - estable: `0.1.7`
   - beta para Python y Windows/macOS/AppImage: `0.1.7b4`
   - no usar `~` en `pyproject.toml` ni en `__version__`, porque rompe `pip install -e .[build]`
2. Verificar localmente:
   - `pytest -q tests/test_translator_engine.py tests/test_elpx_service.py`
   - `pytest -q tests/test_update_checker.py tests/test_config.py tests/test_translator_engine.py`
   - `python -m pip install -e .[build]`
   - comprobaciones rapidas de sintaxis si hace falta
3. Hacer commit del cambio de version.
4. Crear el tag solo despues de que el commit exista ya:
   - `git tag -a vX.Y.Z -m "vX.Y.Z"`
   - comprobar que el tag apunta al commit correcto, no solo al objeto anotado:
     - `git rev-parse HEAD`
     - `git rev-parse vX.Y.Z^{}`
     - ambos hashes deben coincidir antes de hacer `push`
5. Subir primero la rama:
   - `git push origin main`
6. Subir despues el tag:
   - `git push origin vX.Y.Z`
7. Crear la release en GitHub solo cuando el tag ya exista en remoto:
   - `gh release create vX.Y.Z --title "vX.Y.Z" --generate-notes`
   - justo despues, comprobar que el workflow nuevo ha arrancado sobre el commit esperado:
     - `gh run list --workflow "Build Desktop" --limit 5`
     - `gh run view <run_id> --json headSha,status`
     - `headSha` debe coincidir con `git rev-parse HEAD`
8. Vigilar el workflow `Build Desktop` hasta que aparezcan los 4 artefactos:
   - `.deb`
   - `AppImage`
   - `.exe`
   - `.dmg`
9. Verificar la release publicada con:
   - `gh release view vX.Y.Z --json assets,url`
   - no dar la release por buena hasta ver los 4 assets adjuntos

## Si una release sale con la version equivocada

No intentar arreglarla dejando la release tal cual.

La correccion correcta es:

1. Cancelar el workflow en curso.
2. Borrar la release equivocada.
3. Borrar el tag local y remoto.
4. Recrear el tag apuntando explicitamente al commit correcto.
   - usar el hash del commit, por ejemplo:
     - `git tag -a vX.Y.Z <commit_sha> -m "vX.Y.Z"`
5. Volver a subir el tag.
6. Volver a crear la release.

## Comprobacion critica de tags

Un tag anotado tiene dos hashes distintos:

- `git rev-parse vX.Y.Z` devuelve el hash del objeto tag
- `git rev-parse vX.Y.Z^{}` devuelve el hash del commit real al que apunta

Para publicar releases en este repo, la comprobacion buena es siempre `vX.Y.Z^{}`.
Si se mira solo `git rev-parse vX.Y.Z`, se puede creer por error que el tag es correcto cuando en realidad apunta al commit anterior.

## Versionado y Debian

Para usuarios de Debian, Ubuntu y derivadas, una beta `0.1.5b10` puede considerarse mas nueva que una estable `0.1.5` al instalar con `apt` o `dpkg`.

Para evitar mensajes de "desactualizacion" en Linux y, a la vez, no romper el build de Python:

- si ya se han distribuido betas de una serie, la estable publica siguiente debe subir de version, por ejemplo `0.1.6`;
- la version de Python y de la app debe seguir un formato PEP 440, por ejemplo `0.1.7b4`;
- el paquete `.deb` debe convertirse automaticamente a formato Debian, por ejemplo `0.1.7~beta4`;
- el tag y la release de GitHub deben usar un nombre valido como ref, por ejemplo `v0.1.7-beta4`.

Resumen practico de una beta correcta:

- `pyproject.toml`: `0.1.7b4`
- `src/elpx_translator_desktop/__init__.py`: `0.1.7b4`
- `.deb`: `0.1.7~beta4`
- tag Git: `v0.1.7-beta4`
- release GitHub: `v0.1.7-beta4`

## Workflow de Linux

En prereleases, el workflow `Build Desktop` no puede asumir que el nombre del `.deb` coincide con `app_version`.

Regla:

- `app_version` se usa para `AppImage`, `.exe` y `.dmg`
- `deb_version` se usa para el `.deb`

Si se toca `.github/workflows/build-desktop.yml`, comprobar que:

- el `.deb` se sube con `deb_version`
- la `AppImage` se sube con `app_version`
- la release final muestra ambos artefactos de Linux

## Web del proyecto

La web muestra:

- solo la estable, si es la version mas nueva;
- estable y beta, solo si la beta es realmente posterior.

Esto evita que una beta antigua siga apareciendo destacada cuando ya existe una estable mas reciente.
