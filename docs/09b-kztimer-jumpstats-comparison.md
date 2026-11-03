# KZTimer JumpStats: referencia conceptual, no sustituto de KZ-Rush

Fecha de consulta: 2026-11-03. Investigación estática complementaria a [08](08-kz-rush-binary-analysis.md) y [09](09-amx-disassembler-research.md).

## 1. Conclusión y efecto sobre la fase 4

**El hallazgo aporta una implementación SourcePawn legible para comparar decisiones de medición, pero no cambia la ruta del lector AMX v8 ni recupera fórmulas del binario de CS 1.6.** Conviene mantener la fase 4 propuesta en 09: lector estático específico de AMXX, validación de instrucciones y referencias antes de interpretar `cmdDetailed`, `fwCmdStart` y `calcStrafes`.

Lo nuevo es evidencia concreta de que nombres similares ocultan contratos diferentes:

- `Sync` cuenta aumentos de velocidad entre callbacks, incluso sin teclas; no mide directamente acuerdo mouse/teclado.
- Los strafes se segmentan por alternancia de grupos **A/W frente a S/D**, habilitada por cualquier cambio de yaw, no por acuerdo direccional.
- `Gained` suma todos los incrementos positivos del segmento; UQ solo suma nuevos récords globales.
- La captura llamada prestrafe usa una norma **3D**, y el supuesto máximo global puede sobrescribir un pico anterior con una recuperación menor.
- La distancia usa desplazamiento **XY + 32**, sin la corrección del último paso descrita por KZ-Rush ni el mínimo de dos candidatos de UQ.

**Cambio recomendado al trabajo de interpretación, no al decoder:** conservar una lista de preguntas sobre fase de muestreo, denominadores, frames sin teclas, recuperación de velocidad, wrap de yaw y límites de arrays. Son casos para buscar evidencia independiente en KZ-Rush, nunca expectativas que deban imponerse a sus instrucciones.

## 2. Procedencia, identidad y estructura

### Revisión inspeccionada

Repositorio: [neko-pm/KZJumpStats](https://github.com/neko-pm/KZJumpStats). Rama predeterminada `master`; commit consultado **`fb7ed467f20f2909e55f2ca61707412d757240d2`**, fechado 2017-12-14, mensaje `Initial Commit`, sin padres en la respuesta de la API. Es una importación inicial, no un historial verificable del desarrollo original.

La API informa `fork=false`, `archived=false`, `license=null`. Esto no demuestra autoría original, mantenimiento actual ni permiso de reutilización. No hay `LICENSE` en el árbol inspeccionado ni aviso de licencia en la cabecera del `.sp`. No distribuir una adaptación suponiendo una licencia por pertenecer al ecosistema SourceMod.

| Ruta en la revisión | Tipo y contenido |
|---|---|
| `README.md` | Documentación, atribución, ejemplo de entrada de base de datos y convars/comandos. No es un archivo de configuración instalado. |
| `addons/sourcemod/scripting/KZJumpStats.sp` | Único archivo fuente del plugin: 153789 bytes, 4218 líneas según el diff del commit; captura, cálculo, geometría, presentación y SQL en el mismo archivo. |
| `addons/sourcemod/translations/kzjumpstats.phrases.txt` | Diccionario de mensajes SourceMod, no algoritmo de movimiento. |
| `sound/quake/{dominating,godlike,perfect,rampage}.mp3` | Cuatro recursos binarios de audio, no plugins compilados. |

El árbol recursivo devolvió `truncated=false`. **No contiene `.smx`, `.amxx`, `.sma`, `.cfg`, compilador ni includes vendorizados.** Esta afirmación se limita al árbol del commit, no a releases, adjuntos del foro u otros repositorios. El `.sp` incluye `sourcemod`, `sdktools`, `sdkhooks` y `clientprefs` (líneas 1–6); declara `VERSION "1.0"` (8). `OnPluginStart` contiene convars y `AutoExecConfig(true, "KZJumpStats")` (211–274): que el plugin pueda generar configuración no significa que exista un `.cfg` versionado.

Identidad de los textos descargados para lectura, sin compilación ni ejecución:

```text
KZJumpStats.sp SHA-256 f4539b630b2239e277270205cb0585580cd3b41b1ac0b127dde5282137394643
README.md     SHA-256 42b249b1dad9549bef4d6cfb90ce2c9938d8a6abfc46c6e57c90e562b80bc597
```

### Relación verificable con la publicación original

1. El README, líneas 1–4, se presenta como repositorio del módulo JumpStats de KZTimer y atribuye explícitamente el original al [hilo AlliedModders 252392](https://forums.alliedmods.net/showthread.php?t=252392).
2. `myinfo` declara nombre `KZ JumpStats`, autor `1NutWunDeR`, versión y URL vacía (`KZJumpStats.sp:193–200`). El mensaje de conexión menciona `KZTimer Jumpstats` (403).
3. Tanto el enlace original como [su vista de impresión](https://forums.alliedmods.net/printthread.php?t=252392) respondieron **HTTP 403**. No se pudieron inspeccionar el texto completo, fecha/autor publicados, changelog, licencia ni adjuntos originales, ni comparar hashes con estos.

**Conclusión de procedencia:** hay atribución explícita y consistente dentro del repositorio. No queda demostrada identidad byte a byte con el adjunto original, aprobación del autor, revisión exacta de KZTimer de la que se extrajo ni continuidad de versiones. `fork=false` no contradice una importación manual. No se encontró evidencia en los textos examinados de parentesco con KZ-Rush o UQ.

## 3. Convenciones de evidencia y recorrido de captura

Todas las líneas de `.sp` siguientes corresponden a [este archivo fijado al commit](https://github.com/neko-pm/KZJumpStats/blob/fb7ed467f20f2909e55f2ca61707412d757240d2/addons/sourcemod/scripting/KZJumpStats.sp). Son líneas físicas, no direcciones de bytecode.

- **[V] Visible:** lectura directa del código; no certifica precisión física ni comportamiento de un build compilado.
- **[D] Documentado:** afirmación de una fuente identificada; no recuperación del algoritmo del binario local.
- **[I] Inferido/propuesto:** consecuencia o idea para KZ Coach, con condiciones; no implementación existente.

Unidades: distancias en unidades del motor, velocidades en unidades/s; los contadores llamados frames cuentan invocaciones elegibles, no tiempo por sí solos.

| Etapa | Función y líneas | Evidencia [V] |
|---|---|---|
| Inicio | `OnPluginStart:301`; `Event_OnJump:546–553` | Hook `player_jump` en modo Pre; guarda tiempo y llama `Prethink` si `WallCheck` no detecta pared. Pre del evento no demuestra la fase exacta de integración física. |
| Inicialización | `Prethink:1339–1396` | Rechazo contextual de base velocity, reset de acumuladores, captura de posición/prestrafe, banderas bhop/drop. Los argumentos `pos` y `vel` no producen estas capturas. |
| Muestreo | `OnPlayerRunCmd:580–608` | Lee origen, ángulos de ojos y velocidad de entidad; aplica chequeos y calcula máximo, altura y sync. |
| Finalización | `OnPlayerRunCmd:638–644` | Con salto activo, grounded, suelo actual/anterior válidos, entidad de arma válida y sin agua: captura posición de suelo, calcula tiempo y llama `Postthink`. |
| Histórico | `OnPlayerRunCmd:646–659` | Actualiza origen grounded, ángulos, velocidad, posición y botones al terminar el callback. |
| Invalidación | `ResetJump:805–810` | Presenta `invalid`, borra contador de suelo y desactiva salto. No ofrece por sí mismo un diagnóstico causal detallado. |

**Importante:** `Prethink` y `Postthink` son nombres de funciones propias. El comentario `postthink jumpstats` no convierte el bloque de `OnPlayerRunCmd` en un hook post-física. La API SourceMod describe `vel` como velocidad **deseada**; este código no la usa para calcular speed, sino `m_vecVelocity`. Tampoco usa `mouse[2]`, `cmdnum` o `tickcount` para las métricas estudiadas.

## 4. Algoritmos y fórmulas encontrados

### 4.1 Velocidad, prestrafe, máximos y altura [V]

| Métrica | Fórmula literal o equivalente | Ruta funcional / condiciones |
|---|---|---|
| Speed | `s = sqrt(vx² + vy²)` | `GetSpeed:561–567`, leyendo `m_vecVelocity`; llamada desde `OnPlayerRunCmd:591,597`. |
| Velocidad 3D auxiliar | `sqrt(vx² + vy² + vz²)` | `GetVelocity:570–576`; no confundirla con `GetSpeed`. |
| Prestrafe | `pre = sqrt(vx² + vy² + vz²)` | `Prethink:1372–1375`, invocado desde evento de salto. No elimina Z ni demuestra que Z sea cero en esa fase. |
| “MaxSpeed” global | Si activo y `s_anterior <= s_actual`, asigna `M = s_actual` | `CalcJumpMaxSpeed:663–668`; inicializa `M=0` en `Prethink:1362`; se copia a final en `Postthink:1406`. **No compara con M.** |
| Máximo por strafe | `M_j = max(M_j, s_actual)` | Inicializa al comenzar segmento (721,730), actualiza en `CalcJumpSync:751–755`. Este sí conserva el pico del segmento dentro de su rango. |
| Z máxima | `Zmax = max(Zmax, origin.z)` | `CalcJumpHeight:670–679`, inicializa a −99999 en 1369. |
| Altura publicada | `H = abs(abs(Z_takeoff) − abs(Zmax))` | Ramas `Postthink:1435–1440`. No equivale siempre a `Zmax−Z_takeoff`, particularmente si cruza Z=0. |
| Tiempo de aire | `T = GetEngineTime_fin − GetEngineTime_inicio` | Inicio en `Event_OnJump:549`, cierre 642; `T>0.83` invalida en `Postthink:1519–1524`. No es una duración derivada de número de ticks. |

**Contraejemplo aritmético del máximo [I]:** muestras 300→280→290 terminan asignando 290, aunque hubo 300. No prueba una ejecución concreta, pero demuestra que la regla visible no garantiza un máximo global. No adoptar esta implementación como referencia de corrección.

### 4.2 Segmentación de strafes [V]

En `CalcJumpSync:698–732`:

1. Compara yaw actual con yaw anterior: menor → `turning_right`, mayor → `turning_left`; igualdad → ninguna.
2. Basta **cualquier** giro para habilitar detección. No exige que el signo de giro coincida con la tecla.
3. Nuevo grupo AW: `(W || A) && !D && !S`, si AW no estaba activo. Nuevo grupo SD: `(S || D) && !A && !W`, si SD no estaba activo. Incrementa contador y cambia las banderas mutuamente excluyentes.
4. **W+A y S+D son admisibles.** A→W sin pasar por SD no crea un segmento nuevo. A+D no cumple ninguna rama, pero no suspende el acumulador del segmento previo.

No hay normalización circular del delta de yaw: pasar de +179° a −179° se clasifica según comparación numérica, no por el giro corto. En este archivo el signo solo habilita la segmentación, pero sería insuficiente para derivar desync. La actualización del histórico sí existe en 656, a diferencia del histórico no actualizado visiblemente de UQ descrito en 03.

`MAX_STRAFES=100` (31). Las escrituras de inicialización de segmento en 719–721 y 728–730 ocurren **antes de un límite visible**. Las actualizaciones posteriores tienen guardas `0 < count <= MAX_STRAFES`; los bucles de salida 1453 y 1484 recorren `strafes` sin cap visible. No asumir truncamiento seguro a 100 ni trasladar esta gestión de límites.

### 4.3 Gain, loss y sync [V]

Sea `Δs = s_actual − s_anterior`, comparando lecturas de callbacks sucesivos. Durante salto activo:

```text
N += 1
si Δs > 0: G += 1
si hay segmento numerado dentro de capacidad:
    N_j += 1
    si Δs > 0: G_j += 1; gained_j += Δs
    si Δs < 0: lost_j += −Δs

sync_global = RoundToNearest(100 * G / N)
sync_j      = RoundToNearest(100 * G_j / N_j)
```

Producción: `CalcJumpSync:733–758`; salida global: `Postthink:1442–1445`; por strafe en chat: 1451–1460 y consola: 1481–1504. El chat devuelve 0 si `N_j==0` o `G_j==0`; el cociente global y el de consola no tienen la misma guarda explícita frente a denominador cero. El `if(sync2<0)` posterior no sustituye esa validación.

**Condiciones que definen la métrica:**

- El contador global no requiere tecla, giro ni segmento; incluye muestras previas al primer strafe. Igual velocidad suma denominador pero no numerador.
- Las muestras sin teclas o con teclas conflictivas se atribuyen al segmento anterior si existe. No hay contador separado de overlaps/desync en esta lógica.
- `CalcJumpSync` se ejecuta antes del bloque de aterrizaje, por lo que la llamada que ya observa `FL_ONGROUND` puede entrar con salto todavía activo (607 frente a 639–643).
- El aumento observado no se empareja con pre/post de **un mismo** comando. No atribuirlo automáticamente a los botones leídos en esa llamada.
- `gained_j` cuenta recuperaciones bajo el máximo histórico. Su diferencia con `lost_j` es balance de variaciones del segmento contabilizado, no “eficiencia contra aceleración ideal”.

**Ejemplo [I]:** 300→290→295 produce pérdida 10 y ganancia 5 en el segmento, aunque no haya nuevo récord. Esto separa esta semántica de la ganancia UQ. No se usa para completar `g_flFrameGain` de KZ-Rush.

### 4.4 Suelo, detección de tipos y validación [V]

`g_js_GroundFrames` aumenta solo cuando no hay salto activo, está grounded y hay W/A/S/D (`OnPlayerRunCmd:593–594`); se resetea en condiciones específicas (653–654, `ResetJump`, finalización). **No cuenta universalmente todo frame grounded**, por lo que no es automáticamente el FOG de KZ-Rush.

`Prethink:1376–1395` compara altura de suelo con referencia anterior: diferencias estrictamente entre −0.1 y 0.1 se hacen cero; diferencia ≤−1.5 marca drop. Marca bhop con contador `<11`. Las ramas de `Postthink` distinguen:

| Rama indicada por el código | Condiciones relevantes, no lista exhaustiva de aceptación | Líneas |
|---|---|---|
| LJ | `ground_frames>11`, mismo suelo normalizado, altura ≤67, distancia <300, “max” >200; después exige pre entre 200 y 278 | 1530–1545 |
| Multibhop | Contador previo y actual `<11`, mismo suelo, altura ≤67, sin drop | 1707 |
| Dropbhop | Actual `<11`, previo `>11`, botón jump histórico, mismo suelo, altura ≤67, con drop | 1829 |
| Weirdjump | Actual `<11`, sin botón jump histórico, mismo suelo, altura ≤67, con drop | 1941 |
| Bhop | Actual `<11`, previo `>10`, mismo suelo, altura ≤67, sin drop, pre >200 | 2053 |

El valor exactamente 11 no se debe redondear conceptualmente hacia `<11` o `>11`. Antes de estas ramas se filtran diferencias de altura (`1511–1517`) y tiempo de aire. Hay invalidaciones por agua, noclip, gravedad de entidad y base velocity (`773–810,880–885`), pared/contactos (`470–494,787–793`) y desplazamiento entre muestras >25 (`682–695`). Son reglas de este productor, no física universal ni prueba de trampas. No se recuperó aquí una implementación de aceleración óptima: se observan resultados de movimiento del motor.

### 4.5 Distancia y geometría [V]

En `Postthink:1410–1419`:

```text
D = sqrt((landing.x − takeoff.x)² + (landing.y − takeoff.y)²) + 32
```

La variable `DistanceZ` usa el índice **[1], Y**, no altura. No suma trayectoria ni integra velocidad. Las referencias provienen de `GetGroundOrigin:847–854`: XY del origen absoluto y Z de `TraceClientGroundOrigin`. Este último traza desde los ojos hacia abajo, offset 100, hull auxiliar `mins=(-16,-16,0)`, `maxs=(16,16,60)`, `MASK_SHOT`, excluyendo jugadores (`856–878`). El llamador no comprueba el retorno de éxito antes de usar el resultado. **Esos 60 no son prueba de la altura real del hull de CS:GO.**

El registro manual `sm_ljblock` lleva a `Function_BlockJump:968–995` y `CalculateBlockGap:1159–1269`. Busca bordes con rayos laterales de yaw ±10°, pasos de 10, longitud de búsqueda `distance/cos(15°)`; normaliza el vector entre bordes y mide el gap con un rayo perpendicular. Almacena `block=RoundToNearest(norm3(edge1−edge0))` (1226–1235); acepta registro de más de 225 y hasta 300 (1256–1259). Son restricciones del medidor, no un algoritmo general de viabilidad.

`CorrectEdgePoint:1328–1337` desplaza el punto por `16*(-edge.y, edge.x, 0)`. `GetEdgeOrigin:1022–1028`, para vector `e`, punto `p` y origen `g`, calcula literalmente:

```text
r.x = (e.x*g.x + e.y*p.x)/(e.x+e.y)
r.y = (e.y*g.y − e.x*p.y)/(e.y−e.x)
r.z = g.z
edge_dist = norm3(r−g)                 # OnPlayerRunCmd:620–621
```

No hay guardas locales de denominador cero en esas divisiones; no reinterpretarlas como proyección ortogonal general ni como el `jof` exacto de KZ-Rush. La aceptación de bloque también comprueba pertenencia a las regiones de origen/destino (`1552–1575`), no solo `D>=block`.

No se encontró en este recorrido un estimador general de `last` en fallos ni reconstrucción de primer contacto dentro del último paso. El código disponible no resuelve los helpers ausentes de UQ.

## 5. Comparación de métricas sin equivalencias implícitas

KZ-Rush [R] es documentación pública consultada nuevamente; UQ [U] corresponde a la fuente 2.42 auditada en 03. Las fórmulas del binario local KZ-Rush siguen pendientes según 08.

| Concepto | KZTimer de esta revisión [V] | UQ 2.42 [U] | KZ-Rush documentado [R] |
|---|---|---|---|
| Speed / pre | Speed XY; pre capturado en 3D | Speed XY; pre snapshot de esa speed | Pre/post según modo; no demuestra la fase de este build |
| Máximo | Global no garantiza pico; por strafe sí compara contra pico | Máximo global conservado en pre-think activo | Máxima velocidad horizontal durante vuelo; implementación local por recuperar |
| Gain | Suma todos los `Δs>0` por segmento | Solo incrementos sobre récord global; total `max−pre` | Columna balance gain−loss, y pérdida separada; no fija aún la fase de cálculo |
| Sync / efficiency | Fracción de callbacks activos con aumento, sin gate de teclas | Sync: post-speed > pre-speed, requiere alguna W/A/S/D; excluye slot 0 del agregado | Efficiency: frames positivos / frames del strafe. La forma del cociente se parece; pertenencia, fase y segmentación no quedan igualadas |
| Strafe | Alternancia AW/SD con cualquier giro | Nueva tecla individual y condición angular, con límites del histórico documentados en 03 | Botón y frames por strafe; algoritmo exacto pendiente |
| Overlaps | No contador en la lógica examinada; algunas combinaciones siguen acumulando | No métrica publicada visible | Frames con más de un botón al final del strafe |
| Desync | Giro habilita segmento, no mide desacuerdo | No fórmula nombrada visible | Frames con dirección de mouse diferente de dirección del botón |
| FOG | Contador condicionado por movimiento y estado | Ausente como salida FOG | Frames en suelo antes del comando de salto |
| Distancia | XY entre referencias +32 | Mínimo de dos normas 3D +32; offset ladder distinto, helper de fallo ausente | Artículo geométrico [G]: snap/primer contacto y reconstrucción del último paso; normalización HUD no totalmente recuperada |
| jof / land / last | Registro manual y distancia a borde propia; no tripleta equivalente demostrada | Probes por eje; `LandingCalculate` y `GetFailedDistance` faltan | Cercanía de salida, reserva de aterrizaje y déficit en fallo; no identidad general `land=D−block−jof` |
| Altura/contexto | Pico de Z y diferencia de absolutos; filtros propios | Estimador muestreado de ápice y normalizaciones de postura | Altura estimada/real y contexto `fuser2`; no sustituibles por un umbral CS:GO |

Fuentes locales precisas: [03, §§1–3 y 7](03-metrics-dictionary.md), `fwdPreThink:2892–2926,4252–4354,4553–4583` y `fwdPostThink:7801–7928` de `reference/uq_jumpstats.sma`; [07, §§3–4](07-distance-and-landing-model.md) para límites del modelo de distancia KZ-Rush. No se afirma una relación de código entre las tres familias.

## 6. Source frente a GoldSrc: diferencias que impiden copiar reglas

| Área | Evidencia y diferencia relevante | Consecuencia para KZ Coach [I] |
|---|---|---|
| Lenguaje/runtime | Este archivo es SourcePawn `.sp` para SourceMod, normalmente compilado a `.smx`; objetivo local: Pawn/AMXX y AMX v8 identificado en 08. 09 demuestra divergencias de ISA. | No usar tabla SMX/SourcePawn ni herramienta compatible solo con SMX para el `.amxx`. |
| API y fases | SourceMod: `OnPlayerRunCmd`, evento `player_jump`, propiedades `m_vecVelocity`, `m_vecBaseVelocity`, SDKTools/SDKHooks. UQ: `fwdPreThink`, `fwdPostThink`, `pev`, flags y traces GoldSrc. | Mapear fases y coordenadas explícitamente; un nombre de función no demuestra equivalencia temporal. |
| Entradas | Firma SourceMod expone botones, movimiento deseado, ángulos, identificadores y mouse. Este plugin usa ángulos de ojos de entidad, no mouse crudo. `usercmd_t` del SDK Half-Life [H] tiene `msec`, `viewangles`, `forwardmove/sidemove/upmove` y botones. | No confundir velocidad deseada con física, ni delta angular con raw mouse. No asumir que el export o demo retenga esos campos. |
| Tickrate / duración | SourceMod expone `GetTickInterval()` [S]. El plugin no lo consulta ni normaliza sus contadores. GoldSrc tiene duración de comando `msec` [H]; no es evidencia de timestep universal de 10 ms. | No equiparar callback, tick, comando y frame renderizado. Registrar duración real y fase si una futura captura lo permite. |
| Física y reglas | No hay implementación de air acceleration ideal en las funciones estudiadas. Hay filtros de altura 67, pre 278, vuelo 0.83 y suelo 11. KZ-Rush documenta `fuser2`, edgefriction, FOG y técnicas GoldSrc [R]. | No importar constantes ni deducir aceleración, gravedad, fricción o bhop GoldSrc de los límites del plugin CS:GO. |
| Colisión / postura | Hull auxiliar y `MASK_SHOT` del medidor Source no acreditan colisión del jugador. UQ normaliza centros según duck; [G] describe AABB y snap GoldSrc. | Verificar origen/pies/hull/postura, filtros de trace y primer contacto para cada motor/build. Compartir “32” no prueba algoritmo común. |

**Ejemplo temporal, no configuración detectada [I]:** si hubiera exactamente una muestra por tick de duración fija, 11 muestras serían 171.875 ms a 64 Hz y 85.9375 ms a 128 Hz; a pasos de 10 ms serían 110 ms. El repositorio no fija cuál de esas condiciones se cumple. Convertir automáticamente su `11` a FOG, milisegundos o criterio CS 1.6 sería injustificado.

No se auditó el código de movimiento de CS:GO ni el binario del motor GoldSrc; el SDK Half-Life es evidencia del contrato de comandos, no fuente exacta de toda la física de Counter-Strike 1.6. No se propone un simulador ni se afirma paridad entre motores.

## 7. Ideas transferibles y aspectos no transferibles

### Aplicables conceptualmente [I], sin implementación en esta fase

1. **Contrato explícito por métrica:** productor/versión, plano XY o XYZ, fase y referencias inicial/final. Evita presentar el pre 3D como pre horizontal o el agregado como coordinación de entradas.
2. **Separar acumuladores:** incremento positivo, pérdida, balance neto, pico y porcentaje de muestras positivas son medidas diferentes. Pruebas con pérdida y recuperación distinguen sus significados.
3. **Segmentación auditable:** conservar evidencia de entradas y muestras asignadas; tratar sin-teclas, combinaciones, inversión y wrap de yaw de forma explícita. No adoptar AW/SD como regla universal.
4. **Separar vuelo, validez y resultado geométrico:** pared, agua, cambio de gravedad y boost son contexto; una invalidación no prueba mala técnica. Mantener motivos identificables antes de emitir consejo causal.
5. **Objetivo declarado:** la selección manual de destino demuestra una forma conceptual de distinguir superficie objetivo de distancia escalar. No obliga a copiar su detección de cajas o sus rayos.
6. **No depender solo de récords:** el esquema SQL visible (`.sp:150–177`) guarda resúmenes de mejores marcas, no una secuencia completa de frames de cada intento. Un coach necesitaría evidencia de intentos fallidos y variación, cuya disponibilidad sigue sin demostrarse.

### No transferibles sin evidencia y calibración independientes

- Umbrales 11/67/278/0.83, tiers de distancias y filtros anti-cheat de esta revisión.
- Callbacks, propiedades, máscaras, traces, offsets de hull y coordenadas del entorno Source.
- La segmentación AW/SD como definición de strafe GoldSrc, o su Sync como desync/efficiency exactos de KZ-Rush.
- Sus reglas de distancia/altura, falta de corrección de último paso y comportamientos defectuosos de máximo/límites/división.
- SQL, HUD y comandos SourceMod como formatos de entrada de KZ Coach; disponibilidad de fuente no demuestra disponibilidad de export.
- Cualquier fórmula usada para llenar un hueco del desensamblado AMXX, o cualquier licencia supuesta por similitud.

## 8. Referencias adicionales y alcance de la búsqueda

**Encontradas en el código:**

- Comentarios en 941 y 960 agradecen a **V952** y enlazan [AlliedModders 212886](https://forums.alliedmods.net/showthread.php?t=212886), junto a `TraceClientViewEntity` y `TRDontHitSelf`. Es atribución de helpers de trace, no de todas las métricas; no se verificó el contenido de ese hilo.
- Comentarios desde 968 hasta 1328 acreditan **“LJStats by justshoot, Zipcore”** en funciones de bloques/bordes. Es una referencia explícita para investigar después; no determina revisión, repositorio, licencia ni identidad completa del algoritmo original.
- Includes de SourceMod/SDKTools/SDKHooks/ClientPrefs; `myinfo.url` está vacío. No se encontró enlace a un paper o algoritmo de aceleración óptima en los textos examinados.

**Pista externa, no evidencia de linaje aceptada:** una búsqueda por el número 252392 localizó un extracto indexado titulado “[CS:GO] amuJS (better KZTimer Jumpstats) [UPDATED 01/29/2020]”, [post 2665776](https://forums.alliedmods.net/showthread.php?p=2665776), que menciona el hilo original y una versión de Powerind. La página también respondió 403. No se inspeccionó fuente de amuJS/Powerind ni se usaron sus supuestas mejoras para corregir esta revisión.

**Desde la publicación original:** referencias adicionales, adjuntos y comentarios no verificables por el bloqueo; no se afirma que estén ausentes.

## 9. Recomendación operativa y comprobación de alcance

Mantener **sin cambios técnicos** el lector AMX v8 propuesto en 09: mismos hashes y coordenadas, ISA AMXX oficial, pruebas sintéticas, parada ante opcode desconocido y listado reproducible. Este `.sp` no es un fixture AMX v8, no aporta validación independiente del decoder y no justifica ampliar a SMX ni instalar SourceMod.

Después de validar ese lector, contrastar con evidencia propia de KZ-Rush:

- Dónde se capturan y emparejan velocidad/botones/dirección, y qué callbacks originan las muestras.
- Qué muestras entran al strafe y al denominador, incluidos igualdad, no-input y overlaps de transición.
- Si la ganancia es positiva acumulada, récord o balance; no elegir de antemano por similitud de nombres.
- Qué límites, redondeos y reglas de dirección se implementan realmente.

Solo se creó este informe en el proyecto. Los textos externos se guardaron en un directorio temporal para lectura; no se descargaron binarios de plugins, compiladores ni audio, no se ejecutaron plugins, no se instalaron paquetes ni se modificaron servidor, fuente de KZ Coach, configuración, 08 o 09. Los archivos no versionados preexistentes `.atl/` y `docs/09-amx-disassembler-research.md` se conservaron. Se intentó la consulta CodeGraph exigida por el entorno, pero su ejecutable no está instalado; se recurrió a lectura directa, sin instalarlo.

### Fuentes reproducibles

- **[K]** [Árbol completo fijado](https://api.github.com/repos/neko-pm/KZJumpStats/git/trees/fb7ed467f20f2909e55f2ca61707412d757240d2?recursive=1), [commit](https://api.github.com/repos/neko-pm/KZJumpStats/commits/fb7ed467f20f2909e55f2ca61707412d757240d2), [README](https://github.com/neko-pm/KZJumpStats/blob/fb7ed467f20f2909e55f2ca61707412d757240d2/README.md), [fuente `.sp`](https://github.com/neko-pm/KZJumpStats/blob/fb7ed467f20f2909e55f2ca61707412d757240d2/addons/sourcemod/scripting/KZJumpStats.sp). Metadata de licencia/fork consultada en la [API del repositorio](https://api.github.com/repos/neko-pm/KZJumpStats).
- **[O]** [Publicación original](https://forums.alliedmods.net/showthread.php?t=252392) y vista de impresión: HTTP 403, no contenido inspeccionado.
- **[R]** Kpoluk, [KZ-Rush LJ stats](https://kz-rush.ru/en/article/kz-rush-lj-stats), 2020-12-20, texto accesible; secciones Main and strafe statistics, ShowPre, JumpOff, Fuser2 and Height, LJ Settings Menu. No se digitalizaron imágenes.
- **[G]** [Calculating distance](https://kz-rush.ru/en/page/calculating-distance), evidencia previamente documentada en [07](07-distance-and-landing-model.md), no nueva inspección del motor ni recuperación de fórmula del binario.
- **[U]** [03 — Metrics dictionary](03-metrics-dictionary.md), basado en `reference/uq_jumpstats.sma` 2.42; [08 — límites del análisis binario](08-kz-rush-binary-analysis.md); [09 — lector propuesto](09-amx-disassembler-research.md).
- **[S]** API oficial [OnPlayerRunCmd](https://sm.alliedmods.net/new-api/sdktools_hooks/OnPlayerRunCmd), [GetTickInterval](https://sm.alliedmods.net/new-api/timers/GetTickInterval); comentarios de `plugins/include/sdktools_hooks.inc` (58–75) y `timers.inc` (declaración 174) en [SourceMod master](https://github.com/alliedmodders/sourcemod/tree/master/plugins/include), consultados como contrato actual, no versión certificada de 2017. Context7 se consultó como búsqueda de documentación; sus resultados no resolvieron este detalle y se contrastó directamente con los includes oficiales.
- **[H]** Valve, [Half-Life SDK `common/usercmd.h`](https://github.com/ValveSoftware/halflife/blob/master/common/usercmd.h), declaración `usercmd_s`; consulta del contrato, no implementación exacta de movimiento de CS 1.6.

## Key Learnings:

1. Hay fuente SourcePawn inspeccionable y atribución explícita al hilo original, pero el 403 impide verificar identidad con sus adjuntos y referencias completas.
2. Sync, gain, pre y max tienen diferencias verificables frente a UQ y a las definiciones documentadas de KZ-Rush; nombres y cocientes parecidos no demuestran equivalencia.
3. No conviene modificar el lector AMX v8: se añaden preguntas de interpretación y casos límite, no opcodes, fórmulas suplentes ni dependencias SourceMod.

**No comprobado:** compilación, comportamiento runtime, física exacta de ambos motores, demos, adjuntos originales y proyectos enlazados. **Riesgo:** reutilizar umbrales o atribuir coordinación causal a un porcentaje de aceleración produciría diagnósticos no sustentados.
