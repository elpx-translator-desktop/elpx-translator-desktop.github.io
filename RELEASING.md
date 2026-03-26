# Publicacion de Releases

Este repositorio publica binarios nativos para Linux, Windows y macOS mediante GitHub Releases y el workflow `Build Desktop`.

## Regla principal

No crear nunca el commit de version, el tag y la release en paralelo.

Si el tag se crea antes de que termine el commit de version, la release puede apuntar al commit anterior y generar artefactos con una version equivocada.

## Secuencia correcta

1. Actualizar la version en `pyproject.toml` y en `src/elpx_translator_desktop/__init__.py`.
2. Verificar localmente:
   - `pytest -q tests/test_translator_engine.py tests/test_elpx_service.py`
   - comprobaciones rapidas de sintaxis si hace falta
3. Hacer commit del cambio de version.
4. Crear el tag solo despues de que el commit exista ya:
   - `git tag -a vX.Y.Z -m "vX.Y.Z"`
5. Subir primero la rama:
   - `git push origin main`
6. Subir despues el tag:
   - `git push origin vX.Y.Z`
7. Crear la release en GitHub solo cuando el tag ya exista en remoto:
   - `gh release create vX.Y.Z --title "vX.Y.Z" --generate-notes`
8. Vigilar el workflow `Build Desktop` hasta que aparezcan los 4 artefactos:
   - `.deb`
   - `AppImage`
   - `.exe`
   - `.dmg`

## Si una release sale con la version equivocada

No intentar arreglarla dejando la release tal cual.

La correccion correcta es:

1. Cancelar el workflow en curso.
2. Borrar la release equivocada.
3. Borrar el tag local y remoto.
4. Recrear el tag apuntando explicitamente al commit correcto.
5. Volver a subir el tag.
6. Volver a crear la release.

## Versionado y Debian

Para usuarios de Debian, Ubuntu y derivadas, una beta `0.1.5b10` puede considerarse mas nueva que una estable `0.1.5` al instalar con `apt` o `dpkg`.

Para evitar mensajes de "desactualizacion" en Linux:

- si ya se han distribuido betas de una serie, la estable publica siguiente debe subir de version, por ejemplo `0.1.6`;
- mejor aun, las futuras betas deberian usar un esquema compatible con Debian, por ejemplo `0.1.7~beta1`, `0.1.7~beta2`, etc., de modo que `0.1.7` quede por encima de todas ellas.

## Web del proyecto

La web muestra:

- solo la estable, si es la version mas nueva;
- estable y beta, solo si la beta es realmente posterior.

Esto evita que una beta antigua siga apareciendo destacada cuando ya existe una estable mas reciente.
