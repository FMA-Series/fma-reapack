# FMA Series — Repositorio ReaPack de Free Mix Audio

Este repositorio permite que REAPER **descargue y actualice automáticamente**
los plugins de la serie FMA en las computadoras de tus alumnos (y en la tuya).

## Cómo funciona

1. Los archivos `.jsfx` (y sus PNGs de la interfaz) viven en este repositorio.
2. La herramienta oficial `reapack-index` genera el archivo `index.xml`
   a partir de los encabezados `@version`, `@changelog`, `@provides`, etc.
3. El alumno agrega **una sola vez** la URL del `index.xml` en
   REAPER → Extensions → ReaPack → Import repositories.
4. Desde entonces, ReaPack → Synchronize packages descarga lo nuevo y
   actualiza lo que ya tenía. Automático.

Es exactamente el mismo modelo que usa Tukan Studios.

## Publicarlo por primera vez

Necesitas una cuenta gratuita de GitHub.

```bash
# 1. Instalar la herramienta oficial (requiere Ruby, una sola vez)
gem install reapack-index

# 2. Crear el repo en GitHub (ej. "fma-reapack") y subir estos archivos
git init
git add .
git commit -m "FMA Series ReaPack repo"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/fma-reapack.git
git push -u origin main

# 3. Generar el index.xml (desde la raíz del repo)
reapack-index --about README.md .

# 4. Subir el index.xml generado
git add index.xml
git commit -m "index.xml"
git push
```

## URL que le das a tus alumnos

```
https://raw.githubusercontent.com/TU-USUARIO/fma-reapack/main/index.xml
```

El alumno la pega en REAPER → Extensions → ReaPack → Import repositories →
OK → ReaPack → Browse packages → instala "FMA Sub-Air".

## Publicar una actualización (cuando haya una v1.4, un plugin nuevo, etc.)

1. Edita el `.jsfx`: sube `@version` y agrega la entrada en `@changelog`.
2. Si agregas PNGs nuevos, ya están cubiertos por `@provides fma-sub-air_gfx/*.png`.
3. Regenera y sube:

```bash
reapack-index --about README.md .
git add -A
git commit -m "Sub-Air v1.4"
git push
```

Los alumnos verán la actualización disponible en
ReaPack → Synchronize packages. Sin reenviar archivos por WhatsApp.

## Estructura

```
FMA Series/
  fma-sub-air.jsfx          <- plugin (con encabezados ReaPack)
  fma-sub-air_gfx/          <- PNGs de la interfaz (cuando existan)
screenshots/                <- capturas para el catálogo ReaPack
index.xml                   <- generado por reapack-index (no editar a mano)
```
