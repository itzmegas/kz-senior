# AMXX v8 static disassembly
Objective: implement the explicitly authorized Phase 4 read-only inspector; no runtime execution or formula reconstruction.
Branch: feat/amx-v8-inspector. Delivery: ask-on-risk, feature-branch-chain explicitly selected. Forecast: 800 authored lines plus generated listings; actual authored count recorded below. Runner: Python standard-library unittest.

## Specs
- S1: “No modificar ningún archivo dentro de `reference/`.” “No ejecutar el plugin.” No server, compiler, system dependencies, production changes, or game hooks.
- S2: “SHA-256 esperado del AMXX: `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e`”; image `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433`. Exact size 1684270; cod=4912, dat=337028, hea=size=1576260, stp=1592644. Stop on mismatch.
- S3: “Utilizar como referencia principal el código oficial de AMX Mod X, revisión: `8fc12670ea86470a0bfed4c35db5de73d3a39e8a`”. Explicit opcode formats, C/I/D/FRM separation, strict unknown/truncation/range/alignment/native/switch validation. No guessed lengths.
- S4: “No intentar interpretar de inmediato todo el plugin.” A `cmdDetailed` [95108,95376), then B `fwCmdStart` [99728,100076), then C `calcStrafes` [182596,192488). Validate outside destinations independently; debug boundaries are provisional.
- S5: “No asumir que un símbolo prueba que una función utiliza una variable.” Record instruction evidence, direct read/write/address versus indirect candidate; preserve original numbers. Frame/strafe symbols and all three functions are targets. Lines, locals, globals, publics and natives must remain inspectable.
- S6: “Crear pruebas con datos sintéticos y/o estructuras controladas.” Headers/magic/hashes/zlib/opcodes/truncation/signs/coordinates/absolute+relative branches/calls/natives/switch/case/range/alignment. No external dependencies.
- S7: Outputs under analysis/amx_disassembly, tool under tools/amx_inspector, report docs/10-amx-disassembly-validation.md; reproducible listings, opcode inventory, validations, confirmed/candidate references. Report [V]/[D]/[I]/[H], limitations, tests, hashes, next phase without implementing it.

## Tasks
- T1 | S1-S2 | inline (no writer trigger) | verified | d66b792 | container, header, debug reader; exact hashes verified.
- T2 | S3,S5,S6 | inline (no writer trigger) | verified | d66b792 | 27 tests GREEN including SCTRL CIP-write RED/GREEN; 144 legal ISA formats and pinned enum comparison.
- T3 | S4-S5,S7 | inline (no writer trigger) | verified | d66b792 | A 42 instructions, B 55, C 1729; boundaries/targets valid; all 12 array references remain candidates.
- T4 | S1,S6-S7 | inline (no writer trigger) | verified | d66b792 | 27 tests, CLI guards, filesystem reproduction and integrity passed; native medium/under_budget, no review due.

## Log
- L1 (2026-11-03): Original request reproduced verbatim below.

```text
# KZ Coach — Fase 4: lector estático y desensamblador AMX v8

## Contexto

Estamos desarrollando una investigación técnica para KZ Coach, un futuro entrenador de saltos Kreedz en Counter-Strike 1.6.

Nuestro objetivo final es comprender y diagnosticar:

- Coordinación entre teclado y mouse.
- Segmentación de strafes.
- Gain y loss de velocidad.
- Efficiency.
- Overlaps.
- Desync.
- Ángulos de strafe.
- Distancia y aterrizaje.
- Diferencias entre intentos exitosos y fallidos.

Ya completamos las fases de investigación documental y comparación de implementaciones.

Documentos existentes:

- `docs/01-plugin-architecture.md`
- `docs/02-data-inventory.md`
- `docs/03-metrics-dictionary.md`
- `docs/04-frame-analysis.md`
- `docs/05-diagnostic-capabilities.md`
- `docs/06-open-questions.md`
- `docs/07-distance-and-landing-model.md`
- `docs/08-kz-rush-binary-analysis.md`
- `docs/09-amx-disassembler-research.md`
- `docs/09b-kztimer-jumpstats-comparison.md`
- `docs/09c-exolent-jumpstats-source-analysis.md`

Leer especialmente los informes 08, 09, 09b y 09c antes de comenzar.

## Objetivo de esta fase

Implementar una herramienta mínima, reproducible y estrictamente de solo lectura que permita desensamblar el bytecode AMX v8 del plugin original KZ-Rush LJ Stats.

Archivo objetivo:

`reference/kz_jump_stats.amxx`

La herramienta debe permitir inspeccionar instrucciones, operandos, llamadas, saltos y referencias a símbolos sin ejecutar el plugin.

**No queremos todavía una decompilación completa ni una reconstrucción especulativa de las fórmulas.**

El resultado principal debe ser un desensamblado técnicamente validado que sirva como base para una fase posterior de análisis semántico.

---

## 1. Restricciones obligatorias

### Seguridad del proyecto

- No modificar ningún archivo dentro de `reference/`.
- No modificar ni reemplazar `kz_jump_stats.amxx`.
- No ejecutar el plugin.
- No cargarlo en un servidor AMX Mod X.
- No iniciar ni modificar el servidor LAN.
- No compilar código Pawn.
- No modificar registros ni estadísticas existentes.
- No instalar dependencias del sistema.
- No usar Ghidra, REA o Lysis sin autorización adicional.
- No implementar funcionalidades de KZ Coach.
- No modificar código de producción existente.
- No crear hooks de captura en el juego.
- No ejecutar funciones del bytecode.

### Herramientas permitidas

- Python 3.
- Biblioteca estándar de Python.
- Lectura binaria.
- `struct`.
- `zlib`.
- `hashlib`.
- `pathlib`.
- `argparse`.
- `unittest` u otras herramientas estándar de pruebas.
- Código fuente oficial de AMX Mod X como referencia de especificación.

Crear el lector preferentemente en:

`tools/amx_inspector/`

Si esa ruta no existe, crearla sin alterar otros componentes.

Los archivos de salida generados deben quedar fuera de `reference/`.

---

## 2. Identidad del binario

Antes de interpretar instrucciones, verificar la identidad del archivo original.

SHA-256 esperado del AMXX:

`8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e`

SHA-256 esperado de la imagen AMX descomprimida:

`d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433`

Datos previamente investigados:

- Contenedor AMXX comprimido.
- Magic externo: `0x414d5858`.
- Imagen descomprimida: 1.684.270 bytes.
- AMX interno versión 8.
- Cell size: 4 bytes.
- Debug symbols presentes.
- Bytecode no compactado.

Coordenadas del AMX interno:

- `cod = 4912`
- `dat = 337028`
- `hea = 1576260`
- `size = 1576260`
- `stp = 1592644`

Rangos:

- Código relativo C: `[0, 332116)`.
- Código en imagen I: `[4912, 337028)`.
- Datos en imagen I: `[337028, 1576260)`.
- Debug en imagen I: `[1576260, 1684270)`.

Convenciones:

- `C`: offset relativo al inicio de código.
- `I`: offset absoluto dentro de la imagen descomprimida.
- `D`: offset relativo al inicio de datos.
- `FRM`: offset relativo al frame de la función, con signo.

No mezclar estas coordenadas.

Si algún dato no coincide, detener el análisis del binario y documentar la discrepancia.

No adaptar silenciosamente offsets ni hashes para conseguir que el lector funcione.

---

## 3. Fuente normativa de instrucciones

Utilizar como referencia principal el código oficial de AMX Mod X, revisión:

`8fc12670ea86470a0bfed4c35db5de73d3a39e8a`

Repositorio:

https://github.com/alliedmodders/amxmodx

Consultar especialmente:

- La enumeración `OPCODE` de `amx.cpp`.
- La lógica de `amx_BrowseRelocate`.
- La codificación y longitud de operandos.
- Las instrucciones de salto.
- Las instrucciones de llamada.
- `SWITCH` y `CASETBL`.
- `SYSREQ_C`, `SYSREQ_N` y variantes.
- Las instrucciones especiales que puedan aparecer en este AMX.

**No usar automáticamente tablas de opcodes de Pawn moderno, SourcePawn o CompuPhase.**

La investigación 09 encontró diferencias relevantes entre sus tablas y la variante AMXX.

Ejemplos de incompatibilidad que deben considerarse:

- `PROC` y `CALL` tienen identificadores distintos en algunas tablas externas.
- Algunas herramientas interpretan destinos relativos cuando aquí son absolutos.
- Lysis presenta diferencias de enumeración en determinados opcodes.

No suponer que una herramienta es compatible porque reconoce el encabezado AMX.

Si la fuente normativa no está accesible o una instrucción no puede definirse de manera confiable, detener esa región y documentarlo.

---

## 4. Diseño del lector

Implementar componentes pequeños y comprobables.

### A. Lector de contenedor

Debe:

1. Abrir el AMXX en modo binario de solo lectura.
2. Validar magic y estructura.
3. Extraer la imagen AMX mediante descompresión zlib.
4. Verificar tamaño y SHA-256.
5. Validar encabezado AMX.
6. Identificar código, datos, tablas y debug.

No escribir imágenes descomprimidas dentro de `reference/`.

### B. Tabla de instrucciones

Crear una representación explícita de los opcodes AMXX.

Cada entrada debe definir:

- Identificador numérico.
- Nombre.
- Longitud.
- Cantidad y tipo de operandos.
- Reglas especiales de interpretación.
- Si puede alterar el flujo de control.

No adivinar longitudes de instrucciones desconocidas.

### C. Desensamblador

Para cada instrucción reconocida, generar:

- Offset C.
- Offset I.
- Bytes originales.
- Opcode.
- Operandos.
- Longitud.
- Destinos de llamadas o saltos.
- Referencias a símbolos cuando puedan resolverse.

Mantener los valores numéricos originales disponibles, incluso cuando se agreguen nombres simbólicos.

### D. Símbolos y debug

Aprovechar las tablas existentes de:

- Funciones públicas.
- Natives.
- Símbolos debug.
- Variables globales.
- Argumentos y variables locales.
- Registros de líneas de código.

No asumir que un símbolo prueba que una función utiliza una variable.

Una relación entre función y variable debe establecerse mediante instrucciones o flujo de datos.

---

## 5. Validación de instrucciones

Antes de considerar válida una región, verificar:

- Que cada instrucción tenga un opcode reconocido.
- Que la longitud coincida con su formato.
- Que ningún operando sobrepase el límite de código.
- Que el recorrido termine exactamente en el límite esperado.
- Que las direcciones de código estén dentro del rango válido.
- Que los destinos internos de control correspondan a límites de instrucciones.
- Que las referencias a natives usen índices válidos.
- Que `SWITCH` y `CASETBL` se interpreten correctamente.
- Que no se confundan tablas de casos con instrucciones ejecutables.

Distinguir:

1. Destino dentro de la región actual.
2. Destino fuera de la región, pero dentro del código global.
3. Destino inválido.

Un destino fuera de la función no debe considerarse automáticamente incorrecto.

Pero tampoco debe considerarse validado hasta comprobar su alineación con el desensamblado global o una frontera de instrucción establecida independientemente.

**Fallar de forma explícita ante inconsistencias.**

No saltar bytes desconocidos para continuar produciendo un listado aparentemente válido.

---

## 6. Validación progresiva obligatoria

No intentar interpretar de inmediato todo el plugin.

### Etapa A: `cmdDetailed`

Dirección:

- C = `95108`
- Longitud debug aproximada = 268 bytes.
- Intervalo = `[95108, 95376)`.

Objetivo:

- Decodificar completamente la región.
- Validar longitudes.
- Identificar llamadas y saltos.
- Comprobar referencias simbólicas posibles.

### Etapa B: `fwCmdStart`

Dirección:

- C = `99728`
- Longitud debug aproximada = 348 bytes.
- Intervalo = `[99728, 100076)`.

Objetivo:

- Repetir las validaciones.
- Localizar operaciones de lectura o almacenamiento de datos.
- No interpretar todavía su semántica como definitiva.

### Etapa C: `calcStrafes`

**Solo comenzar si las etapas A y B están correctamente validadas.**

Dirección:

- C = `182596`
- Longitud debug aproximada = 9892 bytes.
- Intervalo = `[182596, 192488)`.

Objetivo:

- Desensamblar la región completa.
- Identificar bloques básicos.
- Resolver saltos y llamadas.
- Detectar accesos potenciales a variables de frames y strafes.
- Producir evidencia para la futura reconstrucción de fórmulas.

Si una etapa falla, registrar:

- Offset.
- Bytes involucrados.
- Opcode.
- Motivo.
- Regla de especificación relevante.

No continuar con la etapa siguiente hasta resolver el problema o recibir autorización para ampliar el alcance.

**Importante:** los intervalos debug son referencias de partida, no una prueba automática de que cada byte pertenezca exclusivamente a una única función. Verificar sus límites antes de tratarlos como fronteras ejecutables.

---

## 7. Símbolos de interés

Localizar y registrar referencias verificables a:

### Datos por frame

- `g_flFrameGain`
- `g_iFrameWSAD`
- `g_iFrameDirection`
- `g_iFrameStrafe`
- `g_iFrameCount`

### Datos por strafe

- `g_iStrafeFrames`
- `g_flStrafeGain`
- `g_flStrafeLoss`
- `g_flStrafeEfficiency`
- `g_iStrafeOverlaps`
- `g_iStrafeDesync`
- `g_flStrafeAngle`

### Funciones

- `cmdDetailed`
- `fwCmdStart`
- `calcStrafes`

Para cada referencia indicar:

- Dirección de instrucción.
- Operación.
- Operando.
- Símbolo resuelto.
- Tipo de referencia que realmente puede justificarse.

No confundir:

- Dirección cargada con lectura efectiva.
- Lectura con escritura.
- Escritura directa con actualización mediante una función.
- Nombre debug con acceso real.
- Posible referencia con dependencia de datos demostrada.

Si una referencia es indirecta, dejarla como candidata hasta reconstruir el flujo.

---

## 8. Pruebas automáticas

Crear pruebas con datos sintéticos y/o estructuras controladas.

Cubrir:

- Encabezados válidos e inválidos.
- Magic incorrecto.
- Hash incorrecto.
- Descompresión fallida.
- Opcode conocido.
- Opcode desconocido.
- Instrucción truncada.
- Operando con signo.
- Direcciones C/I/D.
- Salto absoluto.
- Salto relativo.
- Llamada.
- Native.
- `SWITCH`.
- `CASETBL`.
- Destino fuera de rango.
- Destino dentro de código pero no alineado.

Las pruebas no deben requerir ejecutar Pawn ni cargar un plugin en el servidor.

El lector debe ser utilizable sin dependencias externas.

---

## 9. Salidas reproducibles

Generar listados de desensamblado en una carpeta nueva, por ejemplo:

`analysis/amx_disassembly/`

Incluir:

- `cmdDetailed.txt`
- `fwCmdStart.txt`
- `calcStrafes.txt`, solo si pasa las validaciones previas.
- Inventario de opcodes observados.
- Resumen de validaciones.
- Referencias simbólicas confirmadas y candidatas.

Si una región no pasa, su listado debe quedar identificado explícitamente como parcial o inválido, no presentarse como resultado validado.

Evitar archivos binarios derivados innecesarios.

---

## 10. Informe final

Crear:

`docs/10-amx-disassembly-validation.md`

Debe incluir:

1. Resumen ejecutivo.
2. Identidad del binario y hashes.
3. Fuente normativa utilizada.
4. Diseño de la herramienta.
5. Cobertura de opcodes.
6. Resultados de pruebas.
7. Validación de `cmdDetailed`.
8. Validación de `fwCmdStart`.
9. Validación de `calcStrafes`, si corresponde.
10. Saltos, llamadas y referencias simbólicas.
11. Instrucciones o estructuras no resueltas.
12. Limitaciones de la herramienta.
13. Recomendación para la siguiente fase.

Usar categorías:

- [V] Verificado en bytes/instrucciones.
- [D] Documentado por fuente normativa.
- [I] Inferido.
- [H] Hipótesis.

No presentar fórmulas como verificadas por la mera aparición de nombres de variables.

---

## 11. Criterios de éxito

### Éxito completo

- Los hashes coinciden.
- El contenedor se interpreta correctamente.
- La ISA usada está respaldada por AMXX oficial.
- Las pruebas automáticas pasan.
- Las tres regiones objetivo están completamente decodificadas.
- No hay opcodes desconocidos.
- No hay instrucciones truncadas.
- Los destinos de control están validados.
- Los listados son reproducibles.
- El binario original permanece intacto.

### Éxito parcial

- Se validan `cmdDetailed` y `fwCmdStart`.
- `calcStrafes` queda pendiente por una limitación concreta y documentada.

### Bloqueo

- Hash incorrecto.
- Estructura AMX inconsistente.
- Tabla de opcodes no confiable.
- Instrucciones imposibles de decodificar sin especulación.
- Inconsistencias de control de flujo no resueltas.

En caso de bloqueo, detenerse y explicar exactamente qué hace falta investigar.

---

## 12. Lo que NO debe hacerse todavía

No reconstruir de forma definitiva:

- Fórmula de efficiency.
- Fórmula de overlaps.
- Fórmula de desync.
- Criterios de strafe perfecto.
- Causas de pérdida de velocidad.
- Reglas de éxito o fallo de un salto.
- Diagnósticos de técnica del jugador.

Eso corresponde a una fase posterior, cuando el desensamblado haya sido validado.

Tampoco iniciar un entrenador en vivo ni modificar el plugin para capturar datos.

## Entrega final

Al terminar:

1. Mostrar los archivos creados.
2. Indicar cómo ejecutar las pruebas y generar los listados.
3. Resumir qué regiones se validaron.
4. Informar qué referencias a variables se confirmaron y cuáles son candidatas.
5. Explicar los bloqueos encontrados.
6. Confirmar mediante hashes que el AMXX original no cambió.
7. Recomendar el siguiente paso, sin implementarlo.

La prioridad es **exactitud y trazabilidad**, no velocidad de desarrollo.

Preferimos un desensamblado parcial confiable antes que una decompilación completa pero incorrecta.
```
- L2: Existing untracked docs/09*.md, .atl/ and reference sources belong to the user; preserve untouched. Initial branch main, baseline e9aa3cd. Read-only explorer read all four required reports and pinned normative source. Parent checked enum, relocation and debug layouts directly. CodeGraph CLI unavailable; targeted reads used.
- L3: Initial AMXX and image hashes, lengths and header coordinates match S2 exactly. Normative source downloaded outside worktree to /tmp/opencode/amx-spec-8fc1267; no plugin execution.
- L4: New isolated inspection code does not change shared production behavior. Risk: none provisionally; assess actual diff before closure. Test-first applies to deterministic parsing and decoding. No pre-existing application behavior is touched, so differential sibling-command checks are inapplicable.
- L5: Initial RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.amx_inspector.test_inspector -v` failed importing the not-yet-implemented inspector. First implementation passed 19 tests and decoded all stages. Additional focused RED reproduced unvalidated external-table destinations, static D/FRM classification and SYSREQ_C flow metadata; one correction batch fixed all three. The final 26 tests passed in 0.983 seconds.
- L6: Normative enum equality verified against downloaded pinned amx.cpp; 56 one-operand, 66 zero-operand and 15 absolute-target lengths independently compared without mismatches. Source URLs/hashes recorded in docs/10. No SYSREQ_N in this ISA.
- L7: A/B/C pass structural validation: 268/348/9892 bytes, 42/55/1729 instructions, 5/8/169 blocks. Boundary-only global scan: 51250 records, 75 opcodes. No unknown/truncated records. Twelve requested arrays matched CONST_ALT constants; no effective array access upgraded to confirmed. Source hash unchanged; artifact readback equals regeneration byte-for-byte.
- L8: Report and README written in English under artifact-language contract. All outputs are new isolated files. Native RDD switch read as on (global); assessment pending. Authored forecast exceeds 400 lines; ask-on-risk delivery-chain decision must be resolved before committing. No push/PR/publication authorized.
- L9: Final functional suite: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/amx_inspector -v`: 26 pass, 0.954 seconds. CLI reproduced all 10 artifacts to an external mktemp directory with `diff -rq` showing no difference. Existing-output, protected-reference-output and wrong-hash guards each exited 1 with no source mutation; scratch and Python cache removed by parent. Final original SHA-256 matches S2. `git diff -- reference/` empty.
- L10: Native assess initially required an explicit declaration for pre-existing untracked consumer files. Canonical inventory obtained; re-assessed with those unrelated files excluded and exact inventory binding. Result medium, configuration_change (generated JSON), review_due=false, under_budget; no review START or consent requested, no independent high-risk verifier applicable. No authority created. Risk: none (new isolated tool only). Source normalization not applicable; no formatter, hook or production helper changed.
- L11: Pinned interpreter also allows SCTRL register 6 to write CIP from PRI (amx.cpp:1984-2005). Added a RED regression before implementing conservative flow metadata and unresolved/no-fallthrough CFG handling, then observed 27 tests GREEN. SCTRL is not observed anywhere in the actual binary; instruction/reference results are unchanged. Refreshed the ISA metadata. Final diff whitespace check exposed trailing spaces in rendered listing lines; normalized them in the generator before final verification. No review identity has been frozen.
- L12: Final normalized candidate: 27 tests pass in 0.954 seconds; CLI-generated filesystem artifacts match delivered output exactly. `git diff --cached --check` passes; no staged or unstaged reference changes. Original hash remains 8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e. All temporary spec downloads and reproduction scratch removed. All 15 owned paths staged on feat/amx-v8-inspector; original untracked consumer paths excluded. No commit or publishing performed. Only delivery-chain decision is pending before the first work-unit commit; functional implementation and requested evidence are verified.
- L13: User selected “Cadena en rama de feature” in the delivery-strategy question; no push or PR authorization. Current slice: complete Phase 4 reader, decoder, tests, documentation and deterministic evidence together. This naturally exceeds the advisory 400-line target; separating parser, tests or evidence solely to meet that number would make intermediate delivery incomplete. Future independent research stays outside this slice. Functional checks and rollback are bounded to the 15 new paths; runtime harness N/A (static-only by explicit requirement).
- L14: Work-unit commit d66b792 (`feat(amx-inspector): validate static AMXX v8 disassembly`) holds T1-T4 together: 1625 authored changed lines including the verbatim-request tracker; generated analysis output excluded. Committed-range assessment from baseline e9aa3cd, with the exact unrelated-untracked inventory excluded, returns medium/under_budget/review_due=false. No START, receipt or independent high-risk verifier required. Closing metadata is passive documentation only. Feature-branch-chain slice 1 contains d66b792 plus its passive evidence closure; no PR/push created.
- L15: Recovery mirror is the complete task document, losslessly encoded as XZ/base64 in Engram topic odd/amx-v8-disassembly/tasks with relative locator, byte count and SHA-256. Decode with Python standard-library base64/lzma to reconcile exact bytes on resume; this is a full archive, not an abbreviated summary. Final Risk: none. No functional checks remain pending; future pointer/dataflow analysis is recommendation only.
