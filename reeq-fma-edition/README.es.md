# ReEQ – FMA Edition

Una edición corregida y extendida de **ReEQ v1.2.0**, el ecualizador gráfico
paramétrico escrito por **Justin Johnson («Sai'ke»)** para REAPER (JSFX).

ReEQ es uno de los diseños de ecualizador más admirados del mundo JSFX:
hasta 16 bandas totalmente paramétricas dibujadas directamente sobre un
gráfico de espectro, ubicación estéreo por banda (Stereo / Mid / Side /
Left / Right), 14 formas de filtro — y una interfaz que todavía se siente
moderna años después. Esta edición existe porque ese diseño merecía ser
terminado: algunas cosas del código original nunca llegaron a conectarse,
otras estaban discretamente mal, y su autor pasó a otros proyectos. La FMA
Edition completa el trabajo pendiente como un **homenaje a su diseño** —
la interfaz, el flujo de trabajo y la filosofía de sonido son suyos; las
correcciones y los agregados están documentados uno por uno en la cabecera
del archivo del plugin.

> **Autor original:** Justin Johnson («Sai'ke») — ReEQ forma parte de su
> colección de JSFX, compartida gratuitamente con la comunidad de REAPER
> (vía ReaPack y los foros de Cockos).
> **Edición FMA:** Juan de Dios Vázquez Reyes — Free Mix Audio (FMA Series).
> **Licencia:** MIT — ver [LICENSE](LICENSE). El copyright y la atribución
> originales se conservan en cada archivo.

> ⚠ **[READ-ME-FIRST.md](READ-ME-FIRST.md)** — este paquete trae **dos
> archivos del mismo plugin**: `reeq-fma-edition.jsfx` (abre con el tema
> FMA Solid) y `ReEQ.jsfx`, el reemplazo directo del ReEQ original de
> Sai'ke, que tus proyectos existentes cargarán en su lugar y que abre con
> su aspecto Classic original. Lee ese archivo antes de instalar.

---

## Qué agrega y corrige la FMA Edition

Todo lo siguiente está verificado contra el código; el registro completo
por versión (fma.1 → fma.20) vive en la cabecera de
`Effects/reeq-fma-edition.jsfx`.

**Dinámica por banda, completada.** El archivo original ya traía un valor
`Band_Dynamic_Range` que se guardaba en cada sesión pero nunca se usaba
(hallazgo H1 de la auditoría). La FMA Edition lo conecta: cada banda puede
ser dinámica, con su propio rango **DYN** (−24…+24 dB), umbral **THR**,
**ATK** (0.5–250 ms) y **REL** (5–1000 ms), interruptor ON/OFF por banda, y
visualización en vivo sobre el gráfico — un relleno translúcido y una curva
móvil alrededor del nodo, para ver la ganancia dinámica mientras ocurre.

**HQ reconstruido — sobremuestreo ×2 de fase mínima, sin fase lineal.** La
cadena HQ original dejaba filtrar la primera imagen del sobremuestreo de
vuelta a la banda audible (medido: +32 dB a 23.76 kHz a 48 kHz) mientras su
gráfico lo ocultaba. Las primeras versiones FMA experimentaron con un motor
de fase lineal; fue retirado a pedido. HQ es ahora una ruta limpia de
sobremuestreo ×2 en el espíritu del método original: los filtros corren al
doble de la frecuencia de muestreo a través de un FIR de media banda
generado por fórmula al cargar (125 taps, rechazo de imagen ≈ −109 dB en
banda de rechazo / −151 dB de residuo plegado), con solo **31 muestras de
latencia** (declaradas vía PDC, REAPER las compensa). Funciona a **cualquier**
frecuencia de muestreo, y el gráfico dibuja la respuesta verdadera de los
filtros.

**SILK (solo HQ).** Una etapa excitadora espectral que vive dentro de la
ruta ×2. Solo agrega armónicos — la ganancia de señal pequeña se mantiene
en la unidad, así que los tonos estables conservan su nivel — con un
carácter por banda: graves profundos, medios definidos, agudos caros.
Al 0 % la etapa se salta por completo y HQ renderiza bit-idéntico. En ECO
el control SILK se muestra bloqueado, porque la etapa vive físicamente en
la ruta sobremuestreada.

**Un limitador terminado.** El limitador de salida de fábrica era un
recorte duro a 0 dBFS. LIMIT ahora activa un techo suave a **−1 dBFS**:
paso bit-exacto por debajo de una rodilla a −3 dBFS, una curva suave por
encima, y un techo que nunca puede superarse — sin latencia agregada en
ningún modo.

**Correcciones de la auditoría sobre el código original.**
- **B6** — el modo «Full» del espectro sumaba L+R y leía +6 dB de más;
  ahora promedia como los demás modos.
- **B7** — la tabla FIR de HQ solo se inicializaba para 44.1/48 kHz; la
  selección ahora es determinista (sustituida por la media banda generada
  por fórmula, correcta a cualquier frecuencia por construcción).
- **B8** — a 88.2 kHz y más, el HQ original se comportaba en silencio como
  ECO; la ruta ×2 ahora corre de verdad a cualquier frecuencia.
- **B11** — el mapeo de frecuencias estaba fijo a un Nyquist de 22050 Hz y
  se rompía a 48 kHz y más; ahora se deriva de la frecuencia real.
- **B1** — una variable mal escrita en el desvanecido del dial de
  pendiente (cosmético, corregido).

**Una piel nueva y seis temas.** Una piel de la casa FMA (grafito, botones
naranja intenso, panel del nodo translúcido con esquinas redondeadas — el
diseño original del panel se respeta en espíritu) más seis temas de ventana
completa: **FMA Fire Storm, FMA Ice Storm, FMA Sand Storm, FMA Star Rain,
FMA Sea Mist** y **FMA Bronze Wall**, junto al tema base **FMA Solid** y el
aspecto **Classic** intacto. El selector de temas es la píldora `GUI:` de
la barra inferior. El audio es bit-idéntico en todos ellos.

**Arranca en ECO, siempre.** El plugin abre en ECO (ligero en CPU); HQ está
a un clic cuando lo quieres.

## Requisitos

- REAPER con soporte JSFX (cualquier REAPER moderno).
- Sin dependencias externas más allá de los dos archivos include de este
  paquete.

## Instalación

1. En REAPER: **Options → Show REAPER resource path in explorer/finder**.
2. Abre la carpeta `Effects` dentro de esa ruta.
3. Copia el contenido de la carpeta `Effects` de este paquete ahí dentro,
   conservando la estructura de carpetas:
   - `Effects/ReEQ.jsfx` — *el reemplazo directo del original de Sai'ke
     (mismo nombre de archivo; abre con el aspecto Classic original).
     Instálalo encima del original y tus proyectos seguirán funcionando,
     con sus ajustes intactos.*
   - `Effects/reeq-fma-edition.jsfx` — *el mismo plugin con nombre propio
     (abre con el tema FMA Solid). Instala un archivo, o los dos.*
   - `Effects/reeq-fma-edition-deps/spectrum.jsfx-inc`
   - `Effects/Dependencies/svf_filter.jsfx-inc` *(archivo original de
     Sai'ke, sin modificar)*
4. En el explorador de FX de REAPER, reescanea (F5) e inserta
   **«JS: ReEQ - Parametric Graphic Equalizer (FMA Edition)»**.

## Manual

Con este paquete viaja un manual corto, enfocado en los botones y en lo
básico: **MANUAL-EN.pdf** (English) y **MANUAL-ES.pdf** (Español).

## Créditos

- **Justin Johnson («Sai'ke»)** — diseño, código e interfaz originales.
  Esta edición es un homenaje a ese trabajo.
- **Juan de Dios Vázquez Reyes (Free Mix Audio / FMA Series)** — auditoría,
  correcciones, dinámica completada, HQ reconstruido, SILK, limitador,
  pieles y temas.

Tanto la obra original como las modificaciones FMA están bajo la licencia
MIT.
