# AMX/Pawn: selección de una ruta de desensamblado verificable

Fecha: 2026-11-03. Fase 3: investigación de herramientas, no recuperación de fórmulas.

## 1. Resumen ejecutivo

**Recomendación principal: autorizar un lector mínimo estático basado en la ISA de AMX Mod X, con salida de bytes, instrucciones y referencias, sin ejecutar el intérprete.** Es la ruta de menor incertidumbre técnica entre las fuentes que se pudieron inspeccionar. No existe todavía ese lector ni se afirma que una herramienta haya superado la prueba del binario.

**Alternativa: `amxxdump`, condicionada a recuperar y revisar su fuente y licencia antes de compilarlo o ejecutarlo.** Su publicación describe exactamente un desensamblador de AMX Mod X 1.5+, pero el sitio bloqueó la lectura completa con HTTP 403. Esa descripción no certifica AMX v8, debug ni todos los opcodes de este archivo. No se recomienda ejecutar un ejecutable antiguo de procedencia no verificada.

Se buscaron herramientas específicas antes de considerar desarrollar una. Los resultados que cambian la elección son:

- **Lysis Java sí tiene un lector AMXX v3/AMX v8 con debug**, aunque su README destaque SourceMod. Sin embargo, su decoder comparte la tabla ordinal de SourcePawn: diverge de AMXX en posiciones concretas y transforma instrucciones en una representación intermedia. Su CLI entrega fuente reconstruida, no un listado fiel de bytes. No es una validación independiente lista para usar.
- **`pawndisasm` de CompuPhase actual no es compatible con la ISA AMXX estudiada:** por ejemplo, asigna `PROC=30`, frente a `PROC=46` en AMX Mod X. También usa llamadas/saltos relativos donde el formato AMXX en disco usa direcciones C absolutas para esas instrucciones.
- **Ghidra 12.0.2 no incluye un procesador Pawn/AMX.** No se localizó una extensión comunitaria verificable en las búsquedas realizadas. Esto no prueba inexistencia universal.
- **REA no resuelve esa carencia.** El motor de la ruta Ghidra es Ghidra, no Codex. Además, su ruta raw admite una lista de CPU nativas que no incluye Pawn. Instalar un procesador hipotético no basta para habilitar AMX a través de REA.

**Siguiente autorización necesaria:** desarrollar y probar el lector acotado de la sección 9, conservando el original intacto y sin instalar herramientas. Si se prefiere evitar código propio, primero debe obtenerse una fuente verificable de `amxxdump`; eso es una investigación pendiente, no una instalación aprobada.

## 2. Requisitos del binario y alcance

Se leyó íntegramente [08-kz-rush-binary-analysis.md](08-kz-rush-binary-analysis.md). Se reutilizan sus resultados estructurales; no se repitió el parser ni la auditoría de compresión/símbolos. Solo se volvió a calcular SHA-256 mediante `sha256sum`, con resultado coincidente.

| Propiedad | Requisito para la herramienta |
|---|---|
| Original | `reference/kz_jump_stats.amxx`, 114387 bytes |
| SHA-256 original | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| Contenedor | AMXX `0x0300`, zlib; seleccionar entrada de 4 bytes por celda |
| Imagen AMX | `file_version=8`, `amx_version=8`, magic `0xf1e0`, little-endian |
| Codificación | Celdas de 32 bits; sin COMPACT, BYTEOPC ni RELOC; DEBUG activo |
| Código | I `[4912,337028)`, longitud 332116 bytes; C `[0,332116)` |
| Datos/debug | Datos I `[337028,1576260)`; debug desde I=1576260 |
| Imagen extraída | 1684270 bytes; SHA-256 `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |
| Símbolos | Publics, natives y debug Pawn: funciones, ámbitos, offsets FRM, tags, dimensiones |

Coordenadas: **I** es offset en imagen; **C** es dirección en código (`I=4912+C`); **D** es dirección en datos (`I=337028+D`); **FRM** es offset local firmado. No confundirlas ni convertir C en índice de celda sin indicarlo.

| Función objetivo | Intervalo C debug | Tamaño en bytes |
|---|---|---:|
| `cmdDetailed` | `[95108,95376)` | 268 |
| `fwCmdStart` | `[99728,100076)` | 348 |
| `calcStrafes` | `[182596,192488)` | 9892 |

Los intervalos son metadata previa, no CFG validado. No se supone ninguna llamada entre estas funciones. El trabajo necesario es decodificar 10508 bytes objetivo, más tablas de salto y destinos externos que hagan falta para validar referencias; no decompilar todo el plugin.

### Niveles de evidencia

- **Documentada:** README, código fuente o especificación inspeccionados sostienen la capacidad indicada. No significa que se haya probado este archivo.
- **Inferida:** hay correspondencia técnica parcial, pero falta verificar una condición o el recorrido completo.
- **No comprobada:** no existe evidencia suficiente o hace falta ejecutar una prueba autorizada.
- **Incompatible para una ruta concreta:** existe una contradicción identificable, por ejemplo un opcode con significado/longitud diferentes. No implica que sea imposible adaptar la herramienta.

## 3. Herramientas investigadas y procedencia

Las referencias [S1–S12] fijan las revisiones usadas cuando se obtuvo un commit. Fechas de commits/push son señales de actividad, no garantías de soporte ni auditorías de seguridad.

| Candidato | Repositorio/publicación y licencia | Mantenimiento observado | Formato, versión y celda |
|---|---|---|---|
| `amxxdump` | Publicación AlliedModders [S7]; repositorio fuente verificable y licencia **pendientes** | Publicación de 2007; estado actual desconocido | Anuncia plugins AMXX 1.5+; AMX v8 y celda no certificados por el extracto accesible |
| Lysis Java | `peace-maker/lysis-java` [S4]; API GitHub no identifica licencia y no se localizó archivo LICENSE en el árbol consultado: **no asumir MIT/GPL** | Commit de `master`: 2023-06-14; `pushed_at`: 2024-03-10; no archivado al consultar | `.smx`, `.amxx`, `.amx`; lector AMXX acepta hasta `0x0300`, AMX 6–8, selecciona celda 4 |
| Pawn `pawndisasm` | `compuphase/pawn`, `compiler/pawndisasm.c` [S5]; Apache-2.0 en el archivo | Commit de rama consultada: 2025-09-26; archivo con revisión interna de 2023 | AMX sin contenedor AMXX; ISA moderna asociada a cabecera v11; celdas 16/32/64 |
| DeAMX histórico | `AmyrAhmady/DeAMX` [S6]; licencia propia en `deamx.lua`, atribución obligatoria y prohibición de venta; no licencia permisiva estándar | Commit de `master`: 2021-04-10; push 2021-05-12; origen trc_ 2008 | `.amx` de SA:MP; operaciones de 4 bytes; rango exacto de versiones y soporte debug v8 no comprobados |
| DeAMX moderno anunciado | `intcost/DeAMX` [S10]; licencia no identificada | API indica push 2026-07-12, pero el árbol de `main` respondió 409 y README 404 | Descripción anuncia Pawn/SA-MP; no hay implementación inspeccionable que permita certificar formato/versión/celda |
| `amx_assembly/disasm.inc` | `pawn-lang/amx_assembly` [S8]; MIT en `disasm.inc` | Commit 2023-11-08 | Auto-desensamblado de AMX en memoria, ecosistema Pawn/SA:MP; no loader offline AMXX; compatibilidad exacta v8 no probada |
| Ghidra | `NationalSecurityAgency/ghidra`, tag `Ghidra_12.0.2_build` [S2]; Apache-2.0, con licencias de componentes | Proyecto activo; se inspeccionó una versión fijada, no se presupone que sea la última | Múltiples CPU/formatos; **sin módulo oficial AMX/Pawn en esa versión** |
| REA | `morluto/rea` [S3]; MIT para código propio, dependencias con términos propios | Commit de `main`: 2026-11-03 | Fachada MCP/CLI de varios motores; no parser Pawn/AMX documentado; ruta raw restringida a CPU enumeradas |
| AMX Mod X oficial | `alliedmodders/amxmodx` [S1]; proyecto GPL-3.0-or-later con excepciones; `amx.cpp` conserva aviso permisivo CompuPhase propio | Commit 2026-10-11 | AMX 6–8 según cabecera/runtime; `PAWN_CELL_SIZE` 16/32/64, 32 por defecto; loader AMXX |

No se heredó la licencia de un proyecto a otro por parentesco. En particular, comprobar la licencia exacta de Lysis/amxxdump es una condición previa a distribuir una adaptación.

### Sistemas, dependencias y ejecución

| Candidato | Host y dependencias | ¿Ejecuta código de terceros para usarlo? | ¿Análisis sin ejecutar el plugin? | Limitación relevante |
|---|---|---|---|---|
| amxxdump | Host, toolchain y bibliotecas por confirmar con la distribución/fuente concreta; tutorial histórico muestra uso en Windows [S7] | Sí, el desensamblador; no se ejecutó | Anunciado como desensamblado estático; implementación no auditada | Recuperar fuente/licencia antes de elegir build o comandos |
| Lysis Java | JVM; para construir: JDK, Gradle/wrapper, Guava 26.0-jre; tests JUnit 4.12; build usa `jcenter()` | Sí; también scripts Gradle al construir | Sí, inspección de buffers y reconstrucción; no necesita servidor GoldSrc | Build antiguo, resolución JCenter y compatibilidad JDK/Gradle pendientes; jar no equivale necesariamente a paquete autocontenido |
| pawndisasm | C y libc; fuente contempla GCC/Clang/MSVC; Windows/Linux/macOS son rutas de compilación plausibles, no probadas aquí | Sí, ejecutable compilado | Sí | ISA y direcciones incompatibles sin adaptación; no importa debug Pawn completo |
| DeAMX | Lua 5.1 según README, scripts auxiliares; Windows documentado, otros hosts con Lua inferidos | Sí, scripts Lua | Reconstrucción estática/simbólica, sin cargar el plugin en servidor | Heurísticas y natives/callbacks de SA:MP; no loader AMXX acreditado; handlers vacíos o falsos para algunas instrucciones |
| amx_assembly | Runtime Pawn y entorno anfitrión, includes de memoria/header/opcodes | Sí, código Pawn en runtime | **No por la vía ofrecida:** lee su propia imagen en ejecución | Descartado por restricciones; extraer ideas de la fuente no obliga a ejecutarlo |
| Ghidra 12.0.2 | Windows/macOS/Linux, JDK 21 de 64 bits; Gradle 8.5+ para construir desde fuente [S2] | Sí, Ghidra y cualquier extensión/script | Sí, con procesador/loader correcto | No hay ruta AMX identificada; Java no aporta por sí solo ISA Pawn |
| REA | Node/npm y motor instalado; requisitos exactos de la revisión en sección 6 | Sí, paquete, bridge y motor | La ruta estática sí; otras funciones de REA pueden ejecutar targets y deben excluirse | No admite Pawn por la ruta documentada; no usar captura runtime |
| Intérprete como referencia | Ningún host adicional si solo se lee su fuente | No para consulta; sí si se compilara/invocara | Consultar fuente es estático | No invocar `amx_Init`/`amx_Exec` como sustituto de un lector |
| Lector propio propuesto | Python 3 y biblioteca estándar, disponible como `python3` en este workspace | Solo nuestro lector y el runtime instalado; no motor descargado | Sí, sin natives, relocación ni JIT | Habrá que implementar y probarlo; hoy es diseño, no herramienta validada |

Los servicios web de Lysis y Decompiler.com se localizaron, pero **no se subió el archivo**. Una interfaz web no fija versión del motor ni genera automáticamente evidencia reproducible; además transfiere el binario a terceros. No es necesario asumir ese coste para esta investigación.

## 4. Compatibilidad específica con AMX v8

### Lysis: buena evidencia de loader, no certificación del decoder

En `AMXModXFile.java` [S4] se verificaron:

- `MAGIC2=0x414D5858`, `MAGIC2_VERSION=0x0300`; entrada con `cellsize==4`.
- Lectura `disksize, imagesize, memsize, offset`, descompresión con `Inflater` y comprobación del tamaño **que solo imprime advertencia**, no necesariamente aborta.
- `MIN_FILE_VERSION=6`, `CUR_FILE_VERSION=8`, `DEFSIZE=8` y lectura debug a partir de versión 8 con DEBUG activo.
- Importación de funciones, variables, ámbitos, tags, dimensiones, archivos, líneas, automatons y states. Argumentos desde FRM `12+4*n`.

**Resultado documentado:** el lector contempla nuestro contenedor y metadata. **Resultado inferido:** probablemente puede cargar esta imagen. **No comprobado:** decodificación fiel de las tres funciones.

La cautela no es solo genérica. `MethodParser.readOp()` indexa directamente `SPOpcode.values()` con la celda leída. Comparación de fuentes, **no lectura de instrucciones de KZ-Rush**:

| Valor ordinal | AMX Mod X `amx.cpp` | Lysis `SPOpcode.java` | Consecuencia si aparece |
|---:|---|---|---|
| 46 | `OP_PROC` | `proc` | Coincidencia de base |
| 123 | `OP_SYSREQ_C` | `sysreq_c` | Coincidencia de base; aun así revisar tratamiento |
| 135 | `OP_SYSREQ_D` | `sysreq_n` | AMXX lleva un operando; parser Lysis de `sysreq_n` consume dos |
| 137 | `OP_BREAK` | `dbreak` | Coincidencia funcional que requiere normalizar nombre |
| 138 | `OP_FLOAT_MUL` | `push2_c` | Semántica y longitud distintas |
| 139 | `OP_FLOAT_DIV` | `push2` | Semántica y longitud distintas |

No se afirma que los valores conflictivos aparezcan en disco en este build. AMXX puede optimizar/transformar llamadas flotantes durante carga; no debe confundirse bytecode del archivo con código relocalizado o parcheado del runtime. **Sin inventariar las instrucciones efectivas, Lysis no queda declarado incompatible con todo el archivo; sí queda descartado como decoder universal AMXX sin condiciones.**

Además, `MethodParser` transforma instrucciones: el caso `sysreq_c` inspecciona y consume una secuencia posterior de limpieza de stack; `Lysis.java` tiene `DebugSpew.DumpGraph` comentado y la CLI recorre todos los métodos para generar fuente. Activar un dump de IR no garantiza preservar cada instrucción original, sus bytes y longitudes. Para la salida requerida haría falta instrumentación/adaptación autorizada, más validación.

### CompuPhase: incompatibilidad demostrada, no «más moderno = mejor»

El `amx.h` contemporáneo declara versión actual/mínima 11. Más importante, `pawndisasm.c` [S5] tiene una tabla distinta: `0=nop`, `30=proc`, `33=call`; AMXX usa `0=inválido`, `46=proc`, `49=call`. Su `do_call` y `do_jump` suman el PC al operando. Aceptar una magic de celda de 32 bits no corrige esa diferencia.

**No usar esa versión sobre nuestra imagen como si fuera AMX v8 compatible.** Una versión histórica podría servir, pero no se identificó y auditó aquí un tag antiguo que resuelva simultáneamente ISA AMXX, debug y salida requerida. La herramienta actual es referencia de diseño, no elección de ejecución.

### DeAMX y amxxdump

DeAMX histórico usa opcodes de la familia clásica y offsets de 4 bytes; eso permite inferir coincidencias de base, no soporte integral AMXX. `deamx_opcodes.lua` incluye handlers vacíos para `JREL`, `CALL.pri`, `SWITCH` y otros, y handlers falsos para instrucciones obsoletas. Una fuente reconstruida plausible puede ocultar falta de semántica. Su catálogo SA:MP no define los natives de GoldSrc.

`amxxdump` es el candidato con mejor **propósito declarado** para el listado pedido, pero «AMXX 1.5+» no es una especificación exhaustiva. Quedan no comprobados su tabla exacta, lectura debug, plataforma, dependencias, errores ante opcodes desconocidos y versión distribuida. El bloqueo de fuente pesa en la selección; no se rellenan esos campos por intuición.

## 5. Evaluación de Ghidra

### Soporte oficial y comunitario

Se consultó la lista oficial `Ghidra/Processors` del tag `Ghidra_12.0.2_build` [S2]. No contiene AMX/Pawn/SourcePawn. Se buscaron `ghidra pawn`, `ghidra AMX`, `ghidra SourcePawn`, `ghidra smx` y extensiones de procesador, en buscador público y búsqueda de repositorios GitHub. No se obtuvo una extensión Pawn con fuente auditable. **No localizada**, no «es imposible que exista». Tampoco una extensión SMX hipotética demostraría la ISA AMXX.

| Pregunta | Resultado |
|---|---|
| ¿Interpreta nuestras instrucciones de fábrica? | No hay procesador oficial identificado para hacerlo |
| ¿Puede abrir bytes de la imagen? | Sí mediante BinaryLoader como datos; eso no es desensamblado Pawn |
| ¿Puede importar AMX correctamente? | Requiere procesador y mapeo correcto; un loader AMX específico automatizaría el formato |
| ¿Aprovecha símbolos/debug Pawn automáticamente? | No se encontró importador para estas tablas; requiere loader/script/analyzer |
| ¿Hace falta loader además del procesador? | Para importación reproducible con secciones, publics/natives y debug, sí; para una prueba manual de código raw podría suplirse con configuración/script |
| ¿Produce pseudocódigo verificable ahora? | No; sin semántica Pawn en p-code sería una apariencia sin fundamento |

### Qué habría que desarrollar, sin implementarlo

1. Procesador SLEIGH: tokens little-endian de 32 bits, registros virtuales PRI/ALT/CIP/STK/FRM/HEA, instrucciones y operandos variables.
2. Espacios de código/datos separados o un mapeo equivalente explícito; las direcciones C y D pueden compartir valores numéricos y no son la misma memoria.
3. Semántica p-code, stack descendente, llamadas, retorno, offsets FRM, indirectos y switch/casetbl. Un catálogo de mnemónicos sin semántica no basta para decompilar.
4. `.ldefs`, `.pspec`, `.cspec` y convenciones de llamada; tratamiento de natives y flotantes.
5. Loader AMX, opcional envoltura AMXX/zlib, importación de publics/natives/debug, tipos/arrays/ámbitos y referencias.
6. Fixtures y pruebas frente a la ISA oficial, incluidas instrucciones desconocidas, límites, tablas y valores firmados.

Estimación de ingeniería, no plazo verificado: **1–2 semanas** para un prototipo acotado de listado/mapeo por alguien con experiencia SLEIGH; **varias semanas adicionales** para llamadas/debug/p-code suficientemente fiables y pruebas de pseudocódigo. El coste puede crecer por stack virtual e indirectos. Para tres funciones, excede un lector que solo decodifique y anote. Ghidra sí sería atractivo si luego se necesitara navegación interactiva sostenida de muchos plugins.

No se importó como x86/ARM ni se propone esa maniobra.

## 6. Evaluación de REA y su integración con Codex/Ghidra

Según README y documentación fijados en [S3], Codex es **cliente MCP**: el agente solicita consultas a REA y recibe evidencias. REA coordina proveedores; para assembly/pseudocódigo de la ruta Ghidra ejecuta un bridge Java y Ghidra headless. Otros proveedores nativos incluyen Hopper, IDA y Kuna, sin que eso documente soporte Pawn.

REA aporta búsqueda/orquestación por agente, resultados estructurados, sesiones, snapshots, identidad/hash del input, consultas de funciones/llamadas/referencias y controles del proceso. **No aporta una ISA Pawn que el motor desconozca.** Las hipótesis del LLM no reemplazan la interpretación de instrucciones.

Un procesador Pawn instalado en Ghidra podría beneficiar a REA **solo si** su importación/perfil/proveedor admitiera ese lenguaje y loader. En la revisión inspeccionada, `docs/raw-binary.md` enumera exclusivamente `x86`, `x86_64`, `arm`, `arm64`, `6502`, `m68k`, con language IDs concretos. AMX no figura. No está documentado un passthrough arbitrario Pawn por esa vía; harían falta cambios y pruebas de integración, no solo copiar una extensión.

Dependencias declaradas en ese commit de REA: Node 22.x >=22.23.4, 24.x >=24.22.1 o 26.12.1+, npm, Ghidra/JDK instalados por el operador para ese proveedor; Linux requiere `ps` compatible con procps. Son requisitos de **esa revisión de main**, no de cualquier release npm. Se deben fijar paquete y motor antes de instalar; no usar `latest` para reproducibilidad.

### Windows

`docs/windows-ghidra-p0.md` describe soporte experimental Windows 10+ x64, volúmenes locales NTFS, controles nativos de procesos/archivos/DACL, Ghidra 12.x >=12.1 (verificado allí con 12.1.4) y JDK completo dentro del rango del motor. Su frontera admite PE nativo x86/x64/ARMNT/ARM64 y raw NMOS 6502, **no AMX**. Hay diferencias entre main y versiones npm, restricciones de rutas/reparse points y ausencia de paridad general GUI/anotaciones.

No confundir: la versión Ghidra 12.0.2 inspeccionada para el catálogo oficial no cumple el mínimo de esa ruta Windows de REA. Actualizarla no añade Pawn automáticamente. Ghidra directo funciona en Windows, pero eso no implica que REA admita cualquier target de Ghidra.

**Decisión:** no instalar REA ni configurar MCP para esta fase o como siguiente paso inmediato. Su utilidad empezaría después de disponer de un motor AMX validado y de comprobar su admisión efectiva.

## 7. El intérprete oficial como referencia normativa práctica

La referencia más próxima al archivo es el fork **AMX Mod X**, no la última ISA de Pawn ni SourcePawn. [S1] fija `amx.h`, `amx.cpp`, `amxdbg.h/.cpp`, `amxxfile.cpp` y `float.cpp`.

| Tema | Evidencia en fuente y regla para validar |
|---|---|
| Versiones | `amx.h`: `CUR_FILE_VERSION=8`, `MIN_FILE_VERSION=6`, `MIN_AMX_VERSION=8`; `amx_Init` comprueba cabecera |
| Identidad de opcode | Enum `OPCODE` de `amx.cpp`; aserciones oficiales como `OP_PROC==46`, `OP_MOVS==117` |
| Longitudes | `amx_BrowseRelocate`: grupos sin parámetros, con un parámetro y casos especiales; usarlo como especificación, no ejecutarlo |
| Operandos ordinarios | Celdas little-endian de 4 bytes; representar tanto raw u32 como signed i32 cuando corresponda |
| Debug antiguo inline | `FILE`/`SYMBOL`: longitud adicional en bytes; `LINE`/`SRANGE`: dos celdas; `SYMTAG`: una. Rechazar explícitamente si no se implementan y aparecen |
| Switch | `SWITCH` apunta a C de `CASETBL`; tabla con count, default y pares valor/destino; tamaño total `(3+2*n)*4` bytes |
| Saltos/calls | En disco no relocalizado, `CALL`, `JUMP` y condicionales ordinarios usan targets C absolutos; `JREL` usa desplazamiento firmado desde después del operando: `C_dest=C_opcode+8+disp` |
| Indirectos | `CALL_PRI`, `JUMP_PRI`, `SYSREQ_PRI`: target/índice en registro; no inventar arista estática si no se demuestra valor |
| Frame/stack | `PUSH` reduce STK en 4; `PROC` guarda FRM; frame: FRM+0 anterior, +4 retorno, +8 tamaño de argumentos en bytes, +12 primer argumento; `RETN` elimina argumentos y tamaño |
| Natives | `SYSREQ_C`: índice de la tabla natives, no C ni puntero de archivo; `amx_Callback` documenta `params[0]` en bytes; `SYSREQ_D` corresponde a solicitud directa y requiere tratar el contexto de runtime |
| Flotantes | Bits en celda, `amx_ctof`/`amx_ftoc`; natives de `float.cpp` y extensiones `OP_FLOAT_*` del runtime. Un tag Float ayuda a anotar, no convierte cualquier entero en float |

**Advertencia:** `amx_BrowseRelocate` modifica opcodes/targets en memoria y puede invocar un browse hook; `amx_Init` escribe memoria y relocaliza. No son APIs de lectura inmutables. No invocarlas para «ver qué pasa», ni cargar natives, ni JIT. La propuesta usa su código como referencia humana para un decoder independiente.

La revisión upstream actual no prueba el compilador exacto de KZ-Rush ni la versión del servidor original. Para cada opcode encontrado habrá que comprobar valor, longitud y semántica; si no coincide, detenerse y buscar la revisión pertinente. El oficial es una base fuerte, no un certificado por parentesco.

## 8. Comparación de rutas

Probabilidades y esfuerzos son valoraciones cualitativas sustentadas en la inspección, no mediciones de ejecución.

| Ruta | Probabilidad de servir al objetivo | Configuración y dependencias | Listado/debug/reproducibilidad | Riesgo y esfuerzo para las tres funciones |
|---|---|---|---|---|
| **A. amxxdump** | Media, condicional: propósito exacto documentado; fuente/build sin verificar | Desconocidos hasta recuperar distribución fuente auténtica | Potencialmente buen listado; soporte debug y determinismo pendientes | Menor trabajo si pasa el gate; riesgo elevado si se usa un binario antiguo sin auditoría |
| **A. Lysis Java** | Alta para loader; indeterminada para decoder efectivo, con conflictos ordinales demostrados | JVM + build Gradle/Guava antiguo | Debug rico; CLI produce reconstrucción, no bytes fieles; requiere adaptación para listado | Medio/alto: evitar IR que oculta secuencias, revisar ISA y patrones de stack; no compensa asumir fidelidad |
| **A. pawndisasm actual / DeAMX** | Bajo sin modificaciones: ISA incompatible / soporte parcial SA:MP | C / Lua | Listado en el primero, fuente reconstruida en el segundo; debug insuficiente o no comprobado | Adaptación y pruebas; no son soluciones completas listas para este caso |
| **B. Ghidra + extensión** | No hay implementación compatible identificada | Ghidra, JDK, desarrollo SLEIGH/Java y pruebas | Potencial muy alto de navegación, símbolos y CFG después de desarrollar soporte | Alto; semanas, más riesgo si se confía temprano en pseudocódigo |
| **C. REA + motor compatible** | Bloqueada hoy por motor y admisión Pawn | Todo B + Node/npm/bridge; Windows más restringido | Facilita consultas/evidencia, no corrige decoder; más versiones que fijar | Mayor que B para estas funciones; sin beneficio inmediato |
| **D. Lector mínimo propio** | Alta viabilidad para este formato acotado; compatibilidad aún no probada | Python 3 estándar; no dependencias nuevas | Bytes/longitudes/operandos y símbolos explícitos, salida determinista diseñada | Medio y acotable: estimación 2–4 jornadas para decoder, anotación y pruebas; sin decompilador ni análisis completo de arrays |

Elegir D no significa escribir un framework ni un intérprete. Se elige porque A no quedó acreditada como listado fiel accesible, y B/C introducen más trabajo que el necesario. Si se recupera una fuente auditable de amxxdump y supera exactamente la misma prueba, A puede reemplazar D sin cambiar criterios de evidencia.

## 9. Diseño del lector mínimo, no implementado

Alcance propuesto:

- Un lector de solo lectura del contenedor conocido/imagen extraída, con límites y hashes; reutilizar las reglas ya documentadas en 08, sin generalizar a todos los formatos.
- Tabla explícita de opcode, operandos, signo y rol basada en AMXX; decoder para las instrucciones encontradas en los intervalos autorizados y sus tablas necesarias. Desconocido implica fallo, nunca salto de una celda para intentar resincronizar.
- Primera pasada para límites y registros; segunda para resolver targets directos y símbolos. Para certificar destinos externos como fronteras, ampliar de forma explícita la decodificación a sus regiones, o hacer una pasada estructural de toda la sección de código. Eso no implica decompilarla.
- Leer metadata debug conservando ámbitos; anotar D y FRM sin inferir tipos/índices por heurísticas no declaradas.
- Salida estable por registro: `C, I, raw_bytes, opcode_u32, mnemonic, byte_length, operands_raw, operands_typed, target, symbol, diagnostic`; stdout/listado y archivo de resultados en directorio separado.
- Tests pequeños con bytes sintéticos: instrucción sin operando, un operando negativo, `CALL` absoluto, `JREL` negativo, `CASETBL`, opcode desconocido, truncamiento y target dentro de un operando. No compilar ni ejecutar plugins para generar esos fixtures.

No se incluyen ejecución simbólica, fórmulas, pseudocódigo, grafo indirecto resuelto, propagación completa de tipos, UI, exportaciones múltiples ni integración MCP. Las referencias a matrices multidimensionales pueden construirse con aritmética e indirección: anotar una base D no demuestra por sí sola la expresión del índice ni todas las lecturas/escrituras posibles.

## 10. Plan reproducible de compatibilidad

**Este es un procedimiento futuro; no se ejecutó el desensamblado ni se extrajo una imagen a disco en esta fase.** No se indican flags inventados de amxxdump ni un comando de Lysis que prometa un listado que su CLI no ofrece.

### 10.1 Preparar identidad y entorno

1. Registrar host, versiones del runtime/herramienta, commit, hashes de fuentes/artefactos, configuración y línea de comandos exacta. No depender de `master`/`latest` en la ejecución.
2. Recalcular hash del original y comparar con la sección 2 antes y después. En Linux: `sha256sum reference/kz_jump_stats.amxx`; en Windows: `Get-FileHash -LiteralPath reference/kz_jump_stats.amxx -Algorithm SHA256`.
3. Ejecutar únicamente el analizador aprobado, como usuario sin privilegios, sin servidor, red ni resolución de natives; input de solo lectura y salidas fuera de `reference/`. Límites de memoria, tiempo y volumen de logs. El aislamiento reduce riesgo del parser, no certifica su exactitud.

### 10.2 Extraer y validar regiones sin alterar el original

4. Con el procedimiento de extracción de 08, seleccionar entrada cellsize=4 y descomprimir zlib en buffer acotado; verificar offset/tamaño, fin zlib, ausencia de trailing stream y longitud 1684270. Guardar únicamente una imagen nueva en el directorio de análisis autorizado, sin truncarla a `AMX_HEADER.size`: eso perdería debug.
5. Exigir hash de imagen `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433`; si no coincide, detenerse. No parchear flags, cabecera ni orden de bytes para satisfacer la herramienta.
6. Validar `cod=4912`, `dat=337028`, límites dentro de imagen y alineación de 4 bytes; flags/versiones esperados. Distinguir tamaño almacenado, memoria virtual y debug. Conservar manifest con ambas identidades y fórmula de coordenadas.

### 10.3 Decodificar y contrastar

7. Comenzar por `cmdDetailed`, luego `fwCmdStart`, luego `calcStrafes`, usando intervalos C de la sección 2. Verificar comienzo/frontera contra public y función debug; comprobar `PROC` si la convención oficial predice ese prólogo. Una discrepancia exige explicación, no corrección silenciosa.
8. Registrar cada instrucción con bytes y longitud. Debe cumplirse `C_next=C_actual+longitud`, sin huecos ni solapamientos en las regiones decodificadas; distinguir `CASETBL` como registro de tabla, no flujo ejecutable ordinario. Límites debug no sustituyen límites del decoder.
9. Para cada opcode efectivo, contrastar número y longitud con enum y `amx_BrowseRelocate`; contrastar saltos, llamadas, stack y flotantes con los handlers oficiales. Crear una matriz `opcode → fuente oficial → regla → test → ocurrencias`; cero reglas importadas ciegamente de SourcePawn/AMX v11.
10. Validar targets directos: C alineado y dentro de código, en frontera conocida; saltos no deben aterrizar en operandos ni pares de tabla. `SWITCH` sí referencia un `CASETBL` válido; sus destinos default/cases deben ser instrucciones. Un call fuera del intervalo de la función es válido si apunta a código válido: no exigir que quede dentro ni que tenga símbolo público.
11. Para targets fuera de los tres intervalos, validar su frontera mediante la ampliación indicada en sección 9. Registrar separado el alcance ampliado. Para indirectos, conservar operación y evidencia disponible; informar destino no resuelto sin fabricar llamada.
12. Verificar índices de natives en `[0,111)` para `SYSREQ_C` del archivo y resolver nombres por tabla; no tratarlos como direcciones de función Pawn. Rechazar formas relocalizadas/directas que no puedan justificarse en este input no relocalizado.

### 10.4 Símbolos, cobertura y resultados

13. Verificar nombres y direcciones de los tres públicos contra debug. Confirmar identidad de globals: `g_flFrameGain` D=808, `g_iFrameWSAD` D=66940, `g_iFrameDirection` D=133072, `g_iFrameStrafe` D=199204, `g_flStrafeEfficiency` D=304408, `g_iStrafeOverlaps` D=297676 y `g_iStrafeDesync` D=311140.
14. Para operandos que realmente referencien esas bases, imprimir instrucción C, bytes, D y nombre; para FRM usar signo y ámbito, por ejemplo argumentos +12 y locales negativos de `calcStrafes`. Si una base solo se construye indirectamente, declarar referencia pendiente; no convertir cualquier constante numéricamente igual en una referencia ni exigir que cada variable aparezca en las tres funciones.
15. Contrastar manualmente, desde bytes y reglas oficiales, prólogo/epílogo, al menos una llamada/salto y una referencia de cada clase presente por función; para clases ausentes, registrar ausencia. Verificar **todas** las longitudes y targets directos automáticamente. Una segunda herramienta solo suma evidencia si su decoder es independiente y su ISA fue verificada.
16. Repetir con idéntico input y configuración y comparar listado normalizado byte a byte; conservar listado raw, manifest, diagnósticos, inventario de opcodes, tabla de referencias, tests y sus resultados. Hash final del original debe seguir coincidiendo.

### Criterios de decisión

**Compatible para el alcance acotado:** identidad/extracción exactas; cobertura completa de las regiones objetivo y tablas necesarias; todos los opcodes efectivos con regla oficial y longitud correcta; cero desconocidos, truncamientos o resincronizaciones; todos los targets directos comprobados o discrepancias resueltas con evidencia; nombres/debug coherentes; reproducibilidad y original intacto. Los indirectos pueden quedar explícitamente no resueltos: eso limita el grafo, no invalida el significado de la instrucción.

**Incompatible en la configuración probada:** un opcode efectivo con otro significado/longitud, target calculado con coordenadas incorrectas, consumo fuera de sección, tabla mal leída, pérdida silenciosa de instrucciones o necesidad de importar como una CPU ajena. Un parser que emite fuente pese a errores no pasa.

**No concluyente:** solo abre cabecera, solo muestra símbolos, falla antes de decodificar, no expone bytes/longitudes o necesita adaptar el exportador. No etiquetar ese caso como éxito ni como prueba de que el plugin está corrupto.

Pasar esta prueba demuestra interpretación del bytecode **en el alcance declarado**, no las fórmulas de efficiency/overlaps/desync ni equivalencia de pseudocódigo. Eso corresponde a la siguiente fase de análisis de flujo/datos.

## 11. Instalaciones y autorizaciones pendientes

| Acción futura | Autorización requerida / punto de parada |
|---|---|
| Desarrollar lector D, tests y salidas de análisis | **Sí**, autorizar implementación acotada y creación de archivos; no se necesita instalar dependencia nueva |
| Recuperar fuente de amxxdump | Resolver primero origen, versión, licencia y contenido; no ejecutar adjuntos ni builds antiguos |
| Compilar/ejecutar amxxdump o Lysis | **Sí**, aprobación separada, revisión de fuentes y dependencias, aislamiento y plan anterior; detenerse antes de hacerlo |
| Instalar Ghidra/JDK o extensión | **Sí**; no recomendado sin módulo Pawn verificable o decisión de desarrollarlo |
| Instalar REA/configurar Codex/MCP | **Sí**; explícitamente aplazado, no desbloquea AMX por sí solo |
| Ejecutar plugin/servidor LAN | Fuera de esta ruta estática; no requerido ni autorizado |

En esta fase se creó únicamente este documento. Se consultaron fuentes públicas como texto y el hash local; no se instalaron paquetes, no se ejecutaron binarios descargados ni compiladores locales, no se modificaron plugin, LAN ni configuraciones. El directorio no versionado `.atl/` ya existía y no se tocó.

## 12. Riesgos y preguntas abiertas

1. ¿Se puede recuperar una versión fuente auténtica y licenciada de amxxdump que preserve bytes, debug y operandos? El foro bloqueó acceso completo; no se asume respuesta positiva.
2. ¿Qué opcodes aparecen realmente en los tres rangos y sus tablas? Sigue pendiente: esta fase comparó fuentes, no desensambló KZ-Rush.
3. ¿Hay diferencias entre la revisión AMXX oficial consultada y el compilador del build? El hash identifica el archivo, no el compilador.
4. ¿Se necesita ampliar la decodificación por saltos, tablas o llamadas externas? No asumir un grafo de tres nodos ni cortar en el primer retorno.
5. Debug puede ser incompleto o tener ámbitos superpuestos; tags/dimensiones no son fórmulas ni garantizan tipos reconstruidos. Ver 08 para el automaton y el relleno final ya explicados.
6. Flotantes y optimizaciones de carga requieren separar disco de runtime. No interpretar `OP_FLOAT_*` como evidencia de presencia sin encontrarlos.
7. Código de terceros puede tener errores de parser y dependencias antiguas aunque no ejecute el plugin. Una prueba aislada y hashes no reemplazan revisión de seguridad.
8. No localizar una extensión comunitaria no demuestra inexistencia; si aparece una, revisar su commit, ISA, loader/debug, licencia y pasar el mismo gate antes de cambiar la recomendación.

**Respuesta operativa:** para interpretar fiablemente las instrucciones, la mejor ruta acreditable hoy es un lector mínimo de la ISA AMXX, validado por bytes y reglas del intérprete oficial. amxxdump queda como alternativa existente condicionada a recuperar evidencia suficiente. No autorizar REA/Ghidra por popularidad ni aceptar pseudocódigo como prueba.

## 13. Fuentes y límites de consulta

### S1 — AMX Mod X oficial, revisión fijada

Repositorio: [alliedmodders/amxmodx, commit `8fc12670ea86470a0bfed4c35db5de73d3a39e8a`](https://github.com/alliedmodders/amxmodx/tree/8fc12670ea86470a0bfed4c35db5de73d3a39e8a).

- [amx.cpp](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.cpp): enum OPCODE, `amx_BrowseRelocate`, `amx_Init`, `amx_Callback`, `amx_Exec`, `JUMPABS`, handlers y aviso de licencia.
- [amx.h](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.h): versiones, celda, cabeceras y conversiones float.
- [amxxfile.cpp](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amxxfile.cpp), [amxdbg.h](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amxdbg.h), [amxdbg.cpp](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amxdbg.cpp): referencias estructurales previamente estudiadas en 08; no se repite la auditoría.
- [float.cpp](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/float.cpp), [licencia del proyecto](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/public/licenses/LICENSE.txt).

### S2 — Ghidra oficial

- [Procesadores de Ghidra 12.0.2](https://github.com/NationalSecurityAgency/ghidra/tree/Ghidra_12.0.2_build/Ghidra/Processors); [lista vía API](https://api.github.com/repos/NationalSecurityAgency/ghidra/contents/Ghidra/Processors?ref=Ghidra_12.0.2_build).
- [README del tag](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0.2_build/README.md): hosts, JDK y build.
- [Conceptos del decompilador](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0.2_build/Ghidra/Features/Decompiler/src/main/help/help/topics/DecompilePlugin/DecompilerConcepts.html): SLEIGH, p-code, pspec/cspec. Documentación técnica consultada también mediante Context7; no prueba soporte Pawn.

### S3 — REA, revisión fijada

[morluto/rea, commit `4f7c4cc21834b1183655b532df104990180c66f6`](https://github.com/morluto/rea/tree/4f7c4cc21834b1183655b532df104990180c66f6):

- [README](https://github.com/morluto/rea/blob/4f7c4cc21834b1183655b532df104990180c66f6/README.md): integración MCP/Codex, proveedores, dependencias y licencia.
- [Raw binary](https://github.com/morluto/rea/blob/4f7c4cc21834b1183655b532df104990180c66f6/docs/raw-binary.md): arquitecturas admitidas, language IDs y límites.
- [Windows Ghidra P0](https://github.com/morluto/rea/blob/4f7c4cc21834b1183655b532df104990180c66f6/docs/windows-ghidra-p0.md): requisitos, versiones y frontera experimental.

### S4 — Lysis Java, revisión fijada

[peace-maker/lysis-java, commit `b8ba93c10b93f33c69012244bdf8485a62170448`](https://github.com/peace-maker/lysis-java/tree/b8ba93c10b93f33c69012244bdf8485a62170448):

- [AMXModXFile.java](https://github.com/peace-maker/lysis-java/blob/b8ba93c10b93f33c69012244bdf8485a62170448/src/main/java/lysis/amxmodx/AMXModXFile.java): contenedores, AMX 6–8, debug y argumentos.
- [SPOpcode.java](https://github.com/peace-maker/lysis-java/blob/b8ba93c10b93f33c69012244bdf8485a62170448/src/main/java/lysis/sourcepawn/SPOpcode.java) y [MethodParser.java](https://github.com/peace-maker/lysis-java/blob/b8ba93c10b93f33c69012244bdf8485a62170448/src/main/java/lysis/builder/MethodParser.java): tabla ordinal y decoder/transformaciones.
- [Lysis.java](https://github.com/peace-maker/lysis-java/blob/b8ba93c10b93f33c69012244bdf8485a62170448/src/main/java/lysis/Lysis.java), [build.gradle](https://github.com/peace-maker/lysis-java/blob/b8ba93c10b93f33c69012244bdf8485a62170448/build.gradle), [tests/amxx](https://github.com/peace-maker/lysis-java/tree/b8ba93c10b93f33c69012244bdf8485a62170448/tests/amxx). Fixtures existentes demuestran intención de soporte AMXX, no que este plugin pase.

### S5 — CompuPhase Pawn

[compuphase/pawn, commit `db97293fa949d7627272a1c8d7a9470818bdbe91`](https://github.com/compuphase/pawn/tree/db97293fa949d7627272a1c8d7a9470818bdbe91): [compiler/pawndisasm.c](https://github.com/compuphase/pawn/blob/db97293fa949d7627272a1c8d7a9470818bdbe91/compiler/pawndisasm.c), [amx/amx.h](https://github.com/compuphase/pawn/blob/db97293fa949d7627272a1c8d7a9470818bdbe91/amx/amx.h). Tabla de instrucciones, targets relativos, tamaños de celda y versión 11.

### S6 — DeAMX histórico

[AmyrAhmady/DeAMX, commit `b660d826e183c7c01d06d058fb434aa00284ce01`](https://github.com/AmyrAhmady/DeAMX/tree/b660d826e183c7c01d06d058fb434aa00284ce01): `README.md`, `deamx.lua` (licencia propia y carga de scripts), `deamx_opcodes.lua` (handlers).

### S7 — amxxdump

[Publicación original AlliedModders, hilo 52875](https://forums.alliedmods.net/showthread.php?t=52875), 2007-03-21; [tutorial histórico, hilo 294847](https://forums.alliedmods.net/showthread.php?t=294847). Se consultaron extractos indexados; página y versiones archive devolvieron HTTP 403. Evidencia limitada al propósito declarado y referencias de uso; no se inspeccionó un paquete ni su fuente. Búsqueda GitHub por nombre no arrojó repositorio verificable en esta consulta.

### S8 — Auto-desensamblado Pawn

[pawn-lang/amx_assembly, commit `66ca1f13ffb83923cdba3e6ad2855a516d484ee6`](https://github.com/pawn-lang/amx_assembly/tree/66ca1f13ffb83923cdba3e6ad2855a516d484ee6), `disasm.inc`: aviso MIT, lectura de base/memoria del propio AMX y dependencia de includes. No es un analizador offline listo para AMXX.

### S9–S12 — Otros resultados y evidencia local

- **S9:** [Lysis web](https://headlinedev.xyz/lysis), anuncia `.smx/.amxx/.amx` y uso de lysis-java. No se envió ningún archivo.
- **S10:** [intcost/DeAMX](https://github.com/intcost/DeAMX), metadata pública y descripción; sin árbol fuente accesible al consultar. No usado como respaldo técnico.
- **S11:** [Decompiler.com AMXX](https://www.decompiler.com/amxx), servicio localizado, no validado ni usado.
- **S12:** `docs/08-kz-rush-binary-analysis.md` completo y `sha256sum reference/kz_jump_stats.amxx` en esta fase. No se usaron fórmulas UQ para completar ningún hueco.

## Key Learnings:

1. Compatibilidad del contenedor AMXX/debug no demuestra correspondencia de la tabla de opcodes: Lysis necesita una prueba específica del bytecode efectivo.
2. La ISA Pawn actual de CompuPhase y la ISA AMXX v8 no son intercambiables; deben verificarse números, longitudes y coordenadas de salto.
3. REA agrega orquestación, no soporte de arquitectura; sus restricciones de importación también deben validarse aunque Ghidra tenga una extensión.
