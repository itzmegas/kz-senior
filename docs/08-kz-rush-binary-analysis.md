# KZ-Rush LJ Stats: análisis estático del binario

## Conclusión

El archivo conserva tablas públicas y datos de depuración que identifican funciones, variables y dimensiones relevantes. Se verificaron el contenedor AMXX, su compresión zlib y la imagen AMX interna. **No se recuperaron fórmulas mediante instrucciones interpretadas**: no se validó un desensamblador compatible. Los símbolos permiten orientar una investigación posterior, pero no demostrar cómo calcula las métricas este build.

Por tanto, hoy podemos definir métricas según documentación pública, no afirmar equivalencia exacta con este plugin. En particular, no podemos diagnosticar una descoordinación concreta entre mouse y teclado a partir de un agregado sin conocer muestreo, segmentación y tratamiento de frames especiales.

Fecha de inspección: 2026-11-02. Investigación estática, sin instalación, ejecución del plugin, recompilación ni cambios en plugins o configuraciones. Solo se creó este informe. No se eligió arquitectura ni tecnología para KZ Coach.

## 1. Identificación y procedencia

| Propiedad | Resultado |
|---|---|
| Archivo proporcionado | `reference/kz_jump_stats.amxx` |
| Tamaño | 114387 bytes |
| SHA-256 original, antes y después | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| Primeros 24 bytes, hexadecimal | `58584d4100030104bbbe01002eb31900444d180018000000` |
| Imagen descomprimida | 1684270 bytes |
| SHA-256 imagen | `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |

La procedencia es el archivo aportado para esta investigación. El hash fija su identidad local; no autentica por sí mismo una publicación de KZ-Rush. Los nombres de archivos fuente incorporados tampoco prueban correspondencia con una versión publicada. No se estableció una versión editorial exacta ni la versión exacta del compilador.

### Coordenadas usadas

- **F:** bytes del archivo comprimido original.
- **I:** bytes de la imagen descomprimida.
- **C:** dirección relativa al código; `I = cod + C`.
- **D:** dirección relativa a datos; `I = dat + D`.
- **FRM:** desplazamiento local firmado respecto del frame; no es offset de archivo.

No existe una conversión general I→F por suma: interviene compresión.

## 2. Métodos y estructura

Se usaron PowerShell, Python 3.14.2 y sus bibliotecas estándar (`struct`, `zlib`, `hashlib`, `pathlib`, `re`), además de lectura de documentación y código fuente público. Se procesó el binario en memoria. No se descargaron ejecutables ni se ejecutaron herramientas de terceros desconocidas.

### Contenedor AMXX

Lectura `<IHB` desde F=0: magic `0x414d5858`, versión de formato `0x0300`, una entrada. Los bytes iniciales son `58 58 4d 41` por little-endian; no se identificó el formato simplemente por una cadena ASCII «AMXX».

Entrada desde F=7, en el orden que lee el loader oficial:

| Campo | Valor |
|---|---:|
| cellsize | 4 |
| disksize | 114363 |
| imagesize | 1684270 |
| memsize | 1592644 |
| offs | 24 |

`offs + disksize = 114387`. La descompresión zlib produjo exactamente `imagesize`, con `eof=True`, `unused_data=0` y `unconsumed_tail=0`.

**Precaución reproducible:** `PluginEntry` declara `imagesize` antes de `disksize`, pero `CAmxxReader` los lee en el orden `cellsize, disksize, imagesize, memsize, offs`. La interpretación sigue al lector, no al orden textual del struct [S1–S2]. El loader utiliza `uncompress` en `GetSection`.

### Imagen AMX

Cabecera interpretada con `<iHBBhh11i` [S3]:

```text
size=1576260 magic=0xf1e0 file_version=8 amx_version=8
flags=2 defsize=8 cod=4912 dat=337028 hea=1576260
stp=1592644 cip=-1 publics=56 natives=1000 libraries=1888
pubvars=1888 tags=1920 nametable=1976
```

`flags=2` corresponde a `AMX_FLAG_DEBUG`; no están activos `COMPACT`, `BYTEOPC` ni `RELOC`. **Compresión zlib del contenedor y codificación compacta AMX son conceptos distintos.**

| Región | Intervalo I o cantidad |
|---|---|
| Código | `[4912,337028)` |
| Datos inicializados | `[337028,1576260)` |
| Debug añadido | `[1576260,1684270)` |
| Funciones públicas | 118 |
| Natives | 111 |
| Libraries | 0 |
| Variables públicas | 4 |
| Tags públicos | 7 |

Las variables públicas son `MapName`, `MaxClients`, `NULL_STRING`, `NULL_VECTOR`. Las matrices métricas son símbolos debug, no variables públicas. Heap/stack describen memoria de ejecución, no secciones adicionales necesariamente almacenadas en el archivo.

### Depuración

En I=1576260, cabecera `<iHBB7h>` [S4–S5]:

```text
size=108010 magic=0xf1ef file_version=8 amx_version=8 flags=0
files=6 lines=4473 symbols=1280 tags=71 automatons=1 states=0
```

Hay 162 símbolos con `ident=9` (función). Se conservan nombres de `float.inc`, `string_stocks.inc`, `fakemeta_util.inc`, `hamsandwich.inc`, `kz_stocks.inc` y `kz_jump_stats.sma`. No se recuperó el contenido de esos archivos.

Después de símbolos y tags se llega a I=1652483; sigue un automaton vacío, identificador y dirección cero. Termina en I=1652490 y quedan 31780 bytes cero. Un primer parser que omitía ese registro falló su aserción de consumo; la inspección posterior explicó esa diferencia. No es evidencia de corrupción ni validación semántica exhaustiva de toda la depuración.

## 3. Inventario de símbolos

Confianza **alta estructural** significa que el registro se interpretó según su formato; no confirma comportamiento.

| Nombre exacto | Evidencia | Dirección / ubicación | Confianza |
|---|---|---|---|
| `cmdDetailed` | Función pública y función debug | C=95108; debug I=1634798, nombre I=1634816 | Alta estructural |
| `calcStrafes` | Función pública y función debug | C=182596; debug I=1634427, nombre I=1634445 | Alta estructural |
| `fwCmdStart` | Función pública y función debug | C=99728; debug I=1635810, nombre I=1635828 | Alta estructural |
| `g_flStrafeEfficiency` | Array global debug, tag Float | D=304408; `[33][50]`; registro I=1642270 | Alta estructural |
| `g_iStrafeOverlaps` | Array global debug | D=297676; `[33][50]`; I=1645654 | Alta estructural |
| `g_iStrafeDesync` | Array global debug | D=311140; `[33][50]`; I=1645562 | Alta estructural |
| `g_flStrafeAngle` | Array global debug, tag Float | D=317872; `[33][50]`; I=1642224 | Alta estructural |
| `g_setStrafesDetailed` | Array global debug | D=454680; `[33]`; I=1647428 | Alta estructural |

Los arrays tienen `ident=3`, `vclass=0`. Las dimensiones no demuestran un límite efectivo de 50 strafes: podrían existir índices reservados u otras restricciones.

### Cadenas solicitadas

Las cadenas de interfaz usan caracteres en celdas de 32 bits; una búsqueda ASCII no es suficiente. Los offsets siguientes son I y las coincidencias son sensibles a mayúsculas.

| Término | Resultado | Clasificación |
|---|---|---|
| `/dt` | Sin literal ASCII ni en celdas | Ausencia acotada a la búsqueda literal |
| `dt`, `detailed` | Desde I=1441100: `detailed\0cmdDetailed\0dt\0cmdDetailed\0` en celdas | Cadenas, no registro demostrado |
| `ljs_strafes_detailed` | Sin coincidencia exacta | Documentado localmente, no localizado |
| `ljs_strafes_last_column` | I=1446964,1463912 | Cadenas en celdas |
| `ljs_strafes_real_gain` | I=1446564,1463480 | Cadenas en celdas |
| `ljs_strafes_full_overlap` | I=1446660,1463584 | Cadenas en celdas |
| `Efficiency` | Entre otras I=1483980 | Cadena en celdas |
| `Overlaps` | I=1484032 | Cadena en celdas |
| `Desync` | I=1484076 | Cadena en celdas |
| `Asynchrony` | Sin coincidencia exacta | No prueba ausencia de la métrica |
| `Gain`, `Loss` | Coincidencias en nombres debug; etiquetas minúsculas presentes | Nombres/cadenas, no fórmulas |
| `Prestrafe` | Nombres y cadenas; por ejemplo I=1440808 en celdas | Nombre/cadena |

Otras salidas recuperadas:

```text
I=1530932 "#N button %s loss duration efficiency overlaps desync angle"
I=1531172 "gain"
I=1531192 "gain-loss"
I=1532344 "Total gain-loss: %.1f / Efficiency: %.1f%s"
I=1534496 "[DETAILED]"
I=1534540 "Too much info to show"
I=1534628 "%s %.1f"
```

La misma región contiene `%sW`, `%sS`, `%sA`, `%sD`, `%s>` y `%s<`. Esto no demuestra qué argumentos se imprimen ni la polaridad de los signos.

**Discrepancia verificada:** el TXT local enumera `ljs_strafes_detailed` y `ljs_strafes_total_gain`; no aparece el primer literal y la imagen contiene `ljs_strafes_total_gaineff`. Puede existir diferencia entre documentación y build; no se resolvió. No se afirma que una cvar funcione o no funcione por una búsqueda de strings.

## 4. Mapa recuperable y límites de las dependencias

| Función | Intervalo C debug | Líneas debug almacenadas | Argumentos identificados |
|---|---|---|---|
| `cmdDetailed` | `[95108,95376)` | 2636–2649 | `id`, FRM=12 |
| `fwCmdStart` | `[99728,100076)` | 2762–2770 | `id`, FRM=12; `uc_handle`, FRM=16 |
| `calcStrafes` | `[182596,192488)` | 4621–4833 | `id`, `flHorSpeed`, `flGain`, `bGround`, `bBadLastFrame` |

Las líneas debug no son citas de un `.sma` recuperado. No se construyó un grafo de llamadas validado. La proximidad de cadenas y los nombres no prueban aristas `fwCmdStart → calcStrafes → cmdDetailed`.

En `calcStrafes`, los argumentos tienen FRM +12,+16,+20,+24,+28. Locales recuperados: `new_WSAD[4]` (−16), `prev_WSAD[4]` (−32), `iGainNum` (−36), `iEarliestFrame` (−40), `bFinished` y `flCos` (−44, ámbitos distintos), `iVelRight` (−48), `iTurnRight` (−52), `flRightAngle` (−56). Son nombres y tipos debug, no expresiones ejecutadas.

| Estructura debug | D | Dimensiones |
|---|---:|---|
| `g_flFrameGain` | 808 | `[33][500]` |
| `g_iFrameWSAD` | 66940 | `[33][500]` |
| `g_iFrameDirection` | 133072 | `[33][500]` |
| `g_iFrameStrafe` | 199204 | `[33][500]` |
| `g_iFrameCount` | 265336 | `[33]` |
| `g_iStrafeFrames` | 277480 | `[33][50]` |
| `g_flStrafeGain` | 284212 | `[33][50]` |
| `g_flStrafeLoss` | 290944 | `[33][50]` |
| `g_flVelocity`, `g_flPrevVelocity` | 329500,330028 | `[33][3]` |
| `g_flAngles`, `g_flPrevAngles` | 332140,332668 | `[33][3]` |
| `g_flFrameTime` | 344020 | `[33]` |

Estas declaraciones son compatibles con un historial por jugador y frame, pero no demuestran escritura, duración efectiva, conservación entre saltos ni exportación. Natives presentes incluyen `get_uc`, `pev`, `register_forward`, `register_clcmd`, `vector_length` y operaciones flotantes/trigonométricas. Falta probar sus sitios de llamada y argumentos.

## 5. Evaluación del desensamblado y punto de parada

Se comprobó disponibilidad mediante:

```powershell
Get-Command amxxdump,amxxpc,pawndisasm,rea,r2,radare2,ghidra,ida,ildasm `
  -ErrorAction SilentlyContinue | Select-Object Name,Source
```

Sin entradas, exit code 1: no se resolvieron por ese comando/PATH; no se hizo una búsqueda exhaustiva del disco.

### Herramientas locales aportadas posteriormente

Se verificó por listado la carpeta `reference/addons/amxmodx/scripting/`. Contiene `amxxpc` (182096 bytes), `amxxpc.exe` (171008), `amxxpc32.dll` (329728), `amxxpc32.so` (219204), `compile.exe` (102912), `compile.sh` (467), además de `include/` y `testsuite/`. Esto corrige cualquier lectura de la comprobación de PATH como ausencia de un compilador local.

Se leyó `compile.sh`: recorre `*.sma` e invoca `./amxxpc` para producir `compiled/*.amxx`; también crea/elimina archivos auxiliares. Por eso no se ejecutó. La presencia de estos archivos no prueba su versión, autenticidad, compatibilidad con el build investigado ni capacidad de desensamblar un `.amxx`. No se ejecutaron tampoco los ejecutables o bibliotecas locales. Su posible utilidad como referencia para una validación futura no elimina el punto de parada actual.

Comandos adicionales usados, exclusivamente de lectura:

```powershell
Get-ChildItem -LiteralPath reference/addons/amxmodx/scripting -File | Select-Object Name,Length
Get-ChildItem -LiteralPath reference/addons/amxmodx/scripting/testsuite -File | Select-Object -First 15 Name,Length
Get-Content -LiteralPath reference/addons/amxmodx/scripting/compile.sh -TotalCount 65
```

| Opción | Evidencia de compatibilidad | Decisión |
|---|---|---|
| Herramienta específica AMX/Pawn | Es la opción prioritaria; necesita AMX v8, celdas de 32 bits y formato/opcodes del build | No disponible/validada en esta sesión |
| Parser estándar propio | Validó contenedor, tablas y debug | No es un desensamblador |
| Fuente oficial `amx.cpp` | Enum de instrucciones y ejecución AMX consultables [S6] | Base para validar un futuro lector, no herramienta ya validada |
| REA | README consultado; no aportó prueba de soporte AMXX/Pawn [S9] | Solo candidato de apoyo; no instalado ni ejecutado |
| Ghidra/IDA/radare2 genéricos | No se demostró un procesador compatible | No asumir código nativo x86 ni traducción automática |

**Se detuvo aquí la etapa de interpretación del bytecode.** No se validaron decodificación completa, longitud de instrucciones, operandos especiales, targets de salto, llamadas ni reconstrucción del stack. No se ofrecen secuencias de instrucciones, fórmulas ni pseudocódigo de KZ-Rush inventados.

Para avanzar hace falta un lector AMX contrastado con el intérprete apropiado, pruebas de direcciones e instrucciones y listados verificables de las tres funciones. Los símbolos ayudan a delimitar funciones/locales; no recuperan automáticamente expresiones, tipos originales completos ni control de flujo.

## 6. Diccionario provisional y rutas pendientes

Niveles de evidencia:

1. **Confirmado por bytecode:** ninguna fórmula de movimiento en este informe. El parseo estructural no se cuenta como interpretación de instrucciones.
2. **Documentado externamente:** artículo KZ-Rush, README y TXT local; no garantiza equivalencia con este build.
3. **Hipótesis:** interpretación todavía sin prueba; no se usa como diagnóstico confirmado.

| Métrica | Definición externa / evidencia | Qué falta demostrar en este binario |
|---|---|---|
| Efficiency | Artículo: proporción de frames con gain positivo sobre frames totales del strafe [S7] | Numerador/denominador efectivos, exclusiones, comparación estricta, dependencia de velocidad, agregado por salto, redondeo |
| Overlaps | Artículo: frames con overlaps al final del strafe [S7] | Combinaciones exactas, límites de strafe, unidad efectiva, atribución, frames intermedios y completamente solapados |
| Desync | Artículo: frames donde dirección del mouse difiere de dirección de tecla [S7] | Fuente de dirección, signos, igualdad angular, frames sin giro/tecla, atribución y agregado |
| Asynchrony | TXT: opción 2 de última columna; artículo usa Desync [S7,S10] | Si ambos nombres designan exactamente el mismo contador en este build |
| Gain/loss | TXT: `real_gain=0` muestra gain−loss limitado a cero si negativo; `1` muestra gain [S10] | Velocidad usada, máximos vs incrementos, acumuladores, pérdidas y fases excluidas |
| Angle | Array Float y cabecera de tabla | Definición, unidad, signos, acumulación; no llamarlo ángulo ideal o error angular |
| Prestrafe | Artículo describe velocidad y modos de presentación previos/al salto [S7] | Snapshot efectivo, componentes y sincronización de cada modo |

Las expresiones `100 × frames_con_gain_positivo / frames_totales_del_strafe` y `max(gain−loss,0)` son **formalizaciones de documentación externa**, no fórmulas recuperadas del bytecode. Sus términos aún necesitan definiciones operacionales. No se presenta pseudocódigo porque no se validó la implementación.

### A. Captura de comandos

`fwCmdStart` tiene un argumento debug `uc_handle`; existen `get_uc` y `pev`. No se probaron lecturas concretas de botones, viewangles, forwardmove/sidemove, velocidad, posición o tiempo en esta función. La existencia de matrices angulares tampoco demuestra deltas crudos de mouse. Un ángulo observado puede incluir otras causas y su diferencia exige reglas de wrapping y muestreo.

### B. Segmentación

`calcStrafes` conserva nombres relacionados con WSAD actual/previo, giro y frames. Quedan desconocidos inicio, fin, cambio de strafe, frames sin teclas, simultaneidad, cambios de dirección y overlaps completos. `ljs_strafes_full_overlap` documenta inclusión/exclusión, pero no define el algoritmo.

### C–F. Cálculos

Las tablas anteriores cubren efficiency, overlaps, desync y gain/loss. No se confirmó si efficiency incluye un total ponderado, promedio simple o recálculo; si overlap cuenta exclusivamente A+D; si gain suma toda aceleración o nuevos máximos; ni si desync excluye el giro cero. Todas estas alternativas siguen abiertas.

### G. `/dt`

`reference/ReadMe[EN].txt:54` documenta `/dt, /detailed` para información detallada en consola junto a las estadísticas generales. El artículo especifica por frame gain−loss, teclas presionadas y dirección de movimiento del mouse [S7].

El binario contiene `dt`, `detailed`, `cmdDetailed`, etiquetas y formatos consistentes con esa finalidad. **No se demostró el registro del comando**: el literal `/dt` no aparece y no se interpretó la llamada a `register_clcmd`.

La cabecera recuperada sugiere columnas de botón, gain o gain−loss, loss, duration, efficiency, overlaps, desync y angle; se la clasifica como texto de salida, no contrato de filas demostrado. Los formatos numéricos y W/S/A/D/`<`/`>` no prueban qué muestra cada token, su polaridad ni si cada cifra corresponde a un frame. Tampoco se recuperaron truncamiento, límites, toggles ni persistencia de datos entre salto y comando.

## 7. Contraste con UQ JumpStats 2.42

Referencia independiente: `reference/uq_jumpstats.sma`; no se usó para completar huecos de KZ-Rush.

| Comportamiento UQ observado en fuente | Evidencia |
|---|---|
| Conteo de aumentos respecto de `old_speed` y frames | Líneas 2892–2899 |
| Gain por strafe suma incrementos sobre máximo global del salto | 2901–2907 |
| Loss suma reducciones respecto de `TempSpeed` | 2909–2926 |
| Sync entero `good*100/(good+bad)`, cero sin muestras | 4571–4577 |
| Con alguna W/A/S/D, aumento de velocidad es good; igualdad/caída es bad | 7889–7903 |
| Sin tecla tiene contador opcional separado | 7918–7919 |
| Varias teclas reinician historial de detección | 7921–7928 |

UQ sync no demuestra coordinación mouse/teclado. Su gain basado en máximos no define el gain de KZ-Rush. Tampoco el reinicio por teclas simultáneas equivale a una métrica Overlaps. La similitud nominal no es equivalencia algorítmica.

Se revisaron las investigaciones previas de `docs/`, especialmente 03 y 07. El artículo de distancia [S8] mantiene separadas distancia XY, resultado del plugin, bloque nominal, AABB, ground snap, contacto inicial y posición posterior. Este análisis no recupera el algoritmo de distancia de KZ-Rush ni modifica esas distinciones.

## 8. Consecuencias para KZ Coach

### Qué podemos definir y qué no

Podemos formular una métrica propia explícita de porcentaje de frames con aumento de velocidad, contadores de estados de teclas y variaciones positivas/negativas de una velocidad bien definida. No se deben etiquetar «idénticos a KZ-Rush». Las fórmulas exactas de todas las métricas prioritarias del build siguen sin demostrar.

Para interpretar la coordinación se necesitan, conceptualmente, muestras ordenadas y alineadas de entradas y movimiento. Esto es un contrato de investigación, **no elección de mecanismo de captura**:

| Dato candidato por muestra | Utilidad | Precaución |
|---|---|---|
| Secuencia, timestamp/duración y fase de muestreo | Comparaciones temporales y denominadores | «Frame» debe definirse: comando, simulación u otro evento |
| Botones W/A/S/D y valores de movimiento si están disponibles | Overlap, neutralidad, dirección solicitada | Tecla y vector solicitado no son necesariamente equivalentes |
| Viewangles actuales/previos, yaw normalizado | Giro observable | No es movimiento físico del mouse |
| Velocidad vectorial actual/previa | Speed XY, gain/loss | Conservar vector para no fijar prematuramente una definición |
| Posición, estado en suelo y eventos de despegue/contacto | Delimitar intento y condiciones | No mezclar contacto con posición posterior |
| Contexto de física y configuración relevante | Comparabilidad | Un agregado sin contexto puede ocultar causas distintas |
| Límites de strafe y motivo de transición, si se derivan | Auditoría de atribución | Conservar regla/versión, no asumir segmentación KZ-Rush |

### Diagnósticos razonables

- Describir coincidencia temporal entre teclas simultáneas y pérdida de velocidad, si ambas se observaron.
- Señalar discrepancia entre dirección angular observada y entrada direccional bajo una regla explícita.
- Comparar consistencia del mismo jugador con condiciones y definición constantes.

Son asociaciones o descripciones, no causalidad garantizada. El artículo menciona overlaps mayores que 1 y desync mayores que 2 como posibles explicaciones de baja eficiencia; no son umbrales clínicos universales ni verificados para este build.

### Diagnósticos especulativos

- «Moviste tarde el mouse» usando solamente desync agregado.
- Atribuir pérdida exclusivamente al mouse, sin velocidad, física, timing y estado de suelo.
- Interpretar `<` o `>` como izquierda/derecha concretas sin validar el código o salida controlada.
- Usar un porcentaje UQ como sustituto de efficiency KZ-Rush.
- Inferir calidad de aterrizaje a partir de distancia o efficiency aisladas.

### Pruebas LAN futuras, no realizadas

Solo con autorización posterior, en una instancia separada sin envío de récords y sin alterar el sistema oficial:

1. Fijar identidad del plugin y configuración efectiva; comprobar nombres de cvars frente a TXT/build.
2. Capturar salida completa de `/dt` y `/detailed`; distinguir toggle, impresión inmediata, último salto y salto siguiente. Contrastar el último intento propio y posibles datos de espectador, sin asumir su soporte.
3. Ensayar transiciones A→D limpias, un intervalo simultáneo y un intervalo neutral; mantener o invertir giro. Comparar cómo se asignan frames y strafes.
4. Ensayar giro cero y ambos signos de yaw, incluidos cruces de ±180°, para interpretar tokens y desync.
5. Contrastar ganancia positiva, pérdida y recuperación por debajo/sobre máximo previo. Comparar opciones `real_gain`, `full_overlap` y última columna solo en el entorno aislado autorizado.
6. Variar duración del comando/FPS de forma controlada para distinguir conteos y tiempos. Una ejecución manual no garantiza una entrada idéntica: registrar esa limitación y repetir.
7. Mantener aparte las pruebas de geometría de docs/07: eje/45°, contacto parcial, alturas y soporte móvil.

Cada prueba debe conservar entradas observables, condiciones, salida íntegra, resultado esperado de cada hipótesis y explicaciones alternativas. No se propone ejecutar ahora el plugin ni automatizar entradas.

### Métricas propias frente a reproducción exacta

Las métricas propias permiten definiciones auditables, tratamiento explícito de neutralidad y tiempo, pruebas pequeñas y diagnósticos basados en datos conservados. Evitan depender de una versión opaca. El coste es perder comparabilidad directa con tablas KZ-Rush; deben tener nombres/versión propios y nunca presentarse como réplicas exactas.

## 9. Reproducción del análisis estructural

Desde la raíz del workspace, sin modificar el archivo:

```powershell
Get-Item reference/kz_jump_stats.amxx | Select-Object Length
Get-FileHash reference/kz_jump_stats.amxx -Algorithm SHA256
```

El script siguiente imprime tablas, símbolos y coincidencias; procesa buffers en memoria. Las URLs de fuentes están en la sección 11. Su salida completa es regenerable, no se adjunta como un volcado masivo al informe.

```powershell
@'
import pathlib, struct, zlib, hashlib, re
p = pathlib.Path('reference/kz_jump_stats.amxx')
b = p.read_bytes()
digest = hashlib.sha256(b).hexdigest()
print('ORIGINAL', len(b), digest)
print('OUTER', struct.unpack_from('<IHB', b))
cell, disk, image, memory, offset = struct.unpack_from('<Biiii', b, 7)
print('ENTRY', cell, disk, image, memory, offset)
assert cell == 4 and offset + disk == len(b)
assert 0 < image <= 4_000_000
z = zlib.decompressobj()
a = z.decompress(b[offset:offset+disk], image+1)
assert z.eof and not z.unused_data and not z.unconsumed_tail
assert len(a) == image
print('IMAGE', len(a), hashlib.sha256(a).hexdigest())
h = struct.unpack_from('<iHBBhh11i', a)
print('AMX', h)
size, magic, fv, av, flags, defs, cod, dat, hea, stp, cip, pub, nat, lib, pv, tags, nt = h
assert magic == 0xf1e0 and defs == 8 and flags == 2
assert 0 <= pub <= nat <= lib <= pv <= tags <= nt < cod < dat <= hea == size <= len(a)
def string(pos):
    end = a.index(b'\0', pos)
    return a[pos:end].decode('ascii', errors='replace'), end+1
for label, lo, hi in [('PUBLIC',pub,nat),('NATIVE',nat,lib),('PUBVAR',pv,tags),('TAG',tags,nt)]:
    assert (hi-lo) % defs == 0
    print('TABLE', label, (hi-lo)//defs)
    for pos in range(lo,hi,defs):
        address, nameoffset = struct.unpack_from('<II',a,pos)
        print(label,string(nameoffset)[0],address,'record_I',pos,'name_I',nameoffset)
dh = struct.unpack_from('<iHBB7h',a,size)
print('DEBUG',size,dh)
ds,dm,dfv,dav,dflags,nf,nl,ns,ntag,nm,nstate = dh
assert dm == 0xf1ef and size+ds == len(a)
x = size+22
for _ in range(nf):
    address = struct.unpack_from('<I',a,x)[0]
    name,x = string(x+4)
    print('FILE',address,name)
lines = [struct.unpack_from('<Ii',a,x+8*i) for i in range(nl)]
x += 8*nl
symbols = []
for _ in range(ns):
    pos = x
    address,tag,start,end,ident,vclass,dim = struct.unpack_from('<IhIIBBh',a,x)
    name,x = string(x+18)
    dimensions = []
    for _ in range(dim):
        dimensions.append(struct.unpack_from('<hI',a,x))
        x += 6
    row = (name,address,tag,start,end,ident,vclass,dimensions,pos)
    symbols.append(row)
    print('SYMBOL',row)
for fn in ('cmdDetailed','calcStrafes','fwCmdStart'):
    f = next(s for s in symbols if s[0] == fn and s[5] == 9)
    mapped = [line for address,line in lines if f[3] <= address < f[4]]
    print('FUNCTION',fn,'raw_lines',min(mapped),max(mapped))
for _ in range(ntag):
    tag = struct.unpack_from('<h',a,x)[0]
    name,x = string(x+2)
    print('DEBUG_TAG',tag,name)
for _ in range(nm):
    machine,address = struct.unpack_from('<hI',a,x)
    name,x = string(x+6)
    print('AUTOMATON',machine,address,name)
for _ in range(nstate):
    state,machine = struct.unpack_from('<hh',a,x)
    name,x = string(x+4)
    print('STATE',state,machine,name)
print('DEBUG_TAIL',x,len(a)-x,'nonzero',sum(v != 0 for v in a[x:]))
terms = '''cmdDetailed calcStrafes fwCmdStart g_flStrafeEfficiency
g_iStrafeOverlaps g_iStrafeDesync g_flStrafeAngle g_setStrafesDetailed
/dt ljs_strafes_detailed ljs_strafes_last_column ljs_strafes_real_gain
ljs_strafes_full_overlap Efficiency Overlaps Desync Asynchrony Gain Loss Prestrafe'''.split()
for term in terms:
    raw = [m.start() for m in re.finditer(re.escape(term.encode()),a)]
    needle = b''.join(struct.pack('<I',c) for c in term.encode())
    found = [dat+m.start() for m in re.finditer(re.escape(needle),a[dat:hea])]
    print('TERM',term,'ASCII_I',raw,'CELL_I',found,'CELL_D',[v-dat for v in found])
cells = struct.unpack('<'+'I'*((hea-dat)//4),a[dat:hea])
i = 0
while i < len(cells):
    j = i
    while j < len(cells) and (32 <= cells[j] < 127 or cells[j] in (9,10,13)):
        j += 1
    if j > i and j < len(cells) and cells[j] == 0:
        text = ''.join(chr(v) for v in cells[i:j])
        if len(text) >= 2:
            print('STRING',dat+4*i,repr(text))
    i = max(i+1,j+1)
assert hashlib.sha256(p.read_bytes()).hexdigest() == digest
print('ORIGINAL_UNCHANGED',digest)
'@ | python -
```

Es un inspector del archivo concreto, con aserciones de identidad/formato, no un parser seguro y general de cualquier archivo hostil ni un descompilador. El límite de imagen evita una expansión sin cota en esta operación. Su búsqueda de texto no reemplaza resolución de referencias de código.

## 10. Preguntas abiertas y siguiente fase

1. ¿A qué publicación exacta corresponde este hash y qué TXT corresponde a ese build?
2. ¿Qué instrucciones y convenciones de llamadas usa efectivamente la imagen, incluidas extensiones flotantes?
3. ¿Dónde se escriben y leen los arrays identificados y cuándo se reinician?
4. ¿Qué significa un frame en cada contador y qué muestras se excluyen?
5. ¿Qué giro observado se compara con qué entrada y con qué desfase temporal?
6. ¿Cómo se asignan overlaps completos, neutrales y cambios de dirección?
7. ¿Qué significan cada número y cada `<`/`>` de la salida detallada?

**Recomendación concreta:** primero fijar correspondencia del build y evaluar, con autorización separada antes de instalar o ejecutar herramientas, un desensamblador AMX/Pawn que produzca listados verificables. Limitar su validación a cabecera/opcodes, targets y las tres funciones objetivo; después seguir referencias a los arrays. Si no se logra, mantener definiciones propias claramente separadas y diseñar pruebas LAN aisladas para las hipótesis pendientes. No iniciar todavía la implementación del entrenador.

## 11. Fuentes y alcance de las referencias

Los enlaces a `master` se consultaron como texto durante esta investigación; **no están fijados a un commit**, por lo que pueden cambiar. Los hashes locales y el script fijan la evidencia binaria, no una instantánea de esas páginas.

- **S1:** [AMXX loader: amxxfile.cpp](https://raw.githubusercontent.com/alliedmodders/amxmodx/master/amxmodx/amxxfile.cpp), `CAmxxReader`, lecturas de entrada y `GetSection`/`uncompress`.
- **S2:** [amxxfile.h](https://raw.githubusercontent.com/alliedmodders/amxmodx/master/amxmodx/amxxfile.h), `PluginEntry`.
- **S3:** [amx.h](https://raw.githubusercontent.com/alliedmodders/amxmodx/master/amxmodx/amx.h), cabecera AMX, flags y tablas.
- **S4:** [amxdbg.h](https://raw.githubusercontent.com/alliedmodders/amxmodx/master/amxmodx/amxdbg.h), cabeceras, símbolos y dimensiones.
- **S5:** [amxdbg.cpp](https://raw.githubusercontent.com/alliedmodders/amxmodx/master/amxmodx/amxdbg.cpp), recorrido de registros debug.
- **S6:** [amx.cpp](https://raw.githubusercontent.com/alliedmodders/amxmodx/master/amxmodx/amx.cpp), enum/intérprete de instrucciones; no se validó un decoder completo.
- **S7:** [KZ-Rush LJ Stats](https://kz-rush.ru/en/article/kz-rush-lj-stats), secciones «Main and strafe statistics», «ShowPre», «Chat commands», «LJ Settings Menu». Define efficiency como «ratio … of number of frames with a positive gain to the total amount of frames»; describe overlaps al final del strafe y desync como diferencia de dirección de mouse/tecla.
- **S8:** [Calculating distance](https://kz-rush.ru/en/page/calculating-distance), contexto geométrico separado de los contadores aquí estudiados.
- **S9:** [morluto/rea](https://github.com/morluto/rea), README; no se estableció compatibilidad AMXX/Pawn.
- **S10:** `reference/addons/amxmodx/configs/kz_jump_stats_info[EN].txt:20–29`, semántica documental de opciones; `reference/ReadMe[EN].txt:37–56`, comandos.
- **S11:** `reference/uq_jumpstats.sma`, rangos citados en sección 7; evidencia únicamente de UQ JumpStats 2.42.

**No comprobado:** comportamiento en servidor, fórmulas interpretadas, equivalencia documental del build ni causalidad de diagnósticos. Riesgo principal: confundir metadata y textos con ejecución demostrada.
