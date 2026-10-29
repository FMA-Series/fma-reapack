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
## FMA Sub-Air

- **Versión vigente: 1.7.1** (2026-10-26). Idéntica en sonido a la 1.7.0; solo cambia la cabecera del archivo (sin changelog, con aviso de licencia: uso tal cual, sin modificar, sin difundir sin aviso previo y autorización por escrito de Free Mix Audio).
- **Manuales:** [Español](FMA Series/docs/Manual-FMA-Sub-Air-v1.7.1-ES.pdf) · [English](FMA Series/docs/Manual-FMA-Sub-Air-v1.7.1-EN.pdf).
- **Changelog resumido:** [FMA Series/CHANGELOG.md](FMA Series/CHANGELOG.md). El changelog detallado ya no viaja dentro del archivo.

## ReEQ – FMA Edition
Install via ReaPack from this repository (FMA Series category). Manual-install package (two-file edition with manuals): see the Release 'ReEQ – FMA Edition 1.2.0-fma.20 — manual install package'.
### Original filename (drop-in replacement)

Coming from Sai'ke's original ReEQ? The manual-install package in the [release](https://github.com/FMA-Series/fma-reapack/releases/tag/reeq-fma-edition-1.2.0-fma.20) also contains **ReEQ.jsfx** — the same plugin under the original filename. Copy it (with the included folders) over your original `ReEQ.jsfx` and your existing projects reopen with every setting intact, in the original Classic look. ReaPack installs the FMA-named file above; the twin is manual-install only.

### Changelog

#### 1.2.6 (2026-10-29)
- Solo metadatos: el changelog vive ahora en este README; el código del plugin es el mismo que en la 1.2.5.

#### 1.2.5 (2026-10-29)
- Selector de temas dentro de Settings > GUI.
- Píldoras del pie al tamaño de su texto, con salto a segunda fila.
- Sin desapariciones por falta de espacio (solo afecta con escalado de pantalla, p. ej. 175 %): el pie se envuelve y el panel se recoge en una pestaña, todo accesible.
- Panel por etapas: controles que se esconden de los extremos hacia adentro y quedan editables en el panel "…" por páginas.
- Fix: pulsar Settings ya no deselecciona el nodo.
