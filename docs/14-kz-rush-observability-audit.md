# KZ-Rush: auditoría de observabilidad y validación experimental

Fase 4D.1 · 2026-11-03 · investigación estática y planificación.
**Resultado parcial: salidas principales trazadas; ninguna salida observada jugando.**

## 1. Resumen ejecutivo

- **[V]** El plugin original construye diagnósticos de `preBhop` para consola y HUD. Existe una emisión real por `client_print(plr, 2, buffer)` en C154064; no son solamente cadenas aisladas.
- **[V/D]** En la rama C168720–169048, `post %.3f` recibe directamente la referencia ya corregida `p*`. En otras ramas recibe `p`, y en jumpbug recibe `v`. **La palabra `post` no identifica por sí sola una variable universal.**
- **[V]** `max %.3f` recibe el `M` local; `pre %.3f` recibe `g_flPreHorSpeed[id]`, no el `p` original de la Fase 4D. Dos ramas diferentes imprimen exactamente `[PRE] bad ...`: la etiqueta no prueba la corrección.
- **[V]** `/dt` y `/detailed` alternan detalle por jugador; no recuperan un historial. No se encontró `ljs_strafes_detailed`. Sí existen cvars de columnas y canales. `ljs_strafes_full_overlap` actúa dentro de `calcStrafes`, no solamente al dibujar.
- **[V]** Existen escrituras automáticas de tops y de configuración. No está demostrada la inocuidad de jugar en la instalación original. La futura sesión requiere una copia aislada y autorización independiente.
- **[H]** Faltan comprobar la configuración desplegada, los módulos/nativas instalados, algunas condiciones de presentación y la captura real del cliente. No se alcanza todavía la afirmación de conocer *exactamente todas* las salidas y condiciones de la instalación LAN.

Guía operativa futura: [14a — plan manual](14a-kz-rush-manual-test-plan.md). Este informe no autoriza conexión, arranque, cambios de cvars ni experimentos.

## 2. Integridad y metodología

### Identidad y coordenadas

| Objeto | Resultado [V] |
|---|---|
| `reference/kz_jump_stats.amxx`, SHA-256 | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| Imagen descomprimida, SHA-256 | `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |
| Imagen / cabecera | 1684270 bytes; `cod=4912`, `dat=337028`; código C[0,332116) |
| Correspondencia | I=4912+C; para datos inicializados I=337028+D; C y D en bytes decimales |
| `preBhop` | símbolo de depuración C[164904,171748), coincide con Fase 4D |
| `cmdDetailed` / `calcStrafes` | C[95108,95376) / C[182596,192488), coinciden con Fase 4B |
| `hamPlayerPreThink` | C[101720,117536), coincide con Fase 4C |
| Barrido estructural | 51250 instrucciones, 111 nativas; índices y destinos aceptados por `validate` |

Se usó `tools/amx_inspector/inspector.py` sin modificarlo: `unpack_container(raw, AMXX_SHA, AMX_SHA)`, `Header.parse`, `definitions`, `debug_info`, `decode` y `validate`. Un desacuerdo de hashes detiene `unpack_container`. Descomprimir, leer celdas y decodificar instrucciones **no** ejecuta ni emula Pawn. Python se invocó con `PYTHONDONTWRITEBYTECODE=1`; `python` no estaba disponible y se utilizó `python3`.

Se preservaron los artefactos previos, incluidos los no seguidos por Git. No se modificaron `reference/`, informes 11–13, herramientas, servidor ni datos. No se ejecutaron plugin, servidor, VM, compilador ni gameplay. No corresponde RED/GREEN: solamente se crean documentos pasivos.

### Etiquetas y alcance de la evidencia

- **[V]** Verificado directamente en bytes, símbolos o archivos originales. Una llamada estática verificada **no significa que se haya visto su mensaje jugando**.
- **[D]** Documentado en una fuente identificable; no demuestra equivalencia de la build instalada.
- **[I]** Inferencia fundamentada, con sus supuestos explícitos.
- **[H]** Hipótesis o dependencia pendiente.

Las tablas usan rangos de función cuando no se redujo un predicado a una instrucción. Esto señala una limitación, no una condición reconstruida exhaustivamente. `id` es el jugador fuente; `plr` puede ser otro destinatario. Los varargs Pawn son direcciones: no deben confundirse con valores enteros de puntero impresos como Float.

**[V]** La enumeración actual de `reference/` contiene el `.amxx`, fuentes de otros jumpstats y sus includes; no contiene los archivos de configuración/idioma originales de KZ-Rush mencionados en el encargo. No se sustituyeron por configuraciones de otro plugin. Los valores siguientes son predeterminados incrustados, **no valores efectivos del servidor**. Las cadenas prioritarias están incrustadas en la imagen.

### Fuentes

- B: binario identificado arriba y sus tablas nativas/depuración; [artefactos estáticos](../analysis/amx_disassembly/).
- F4B: [informe 11](11-kz-rush-frame-counters-reconstruction.md), especialmente §§4–9.
- F4C: [informe 12](12-kz-rush-prethink-state-machine.md), especialmente §§4–10.
- F4D: [informe 13](13-kz-rush-previous-speed-correction.md), especialmente §§3–7.
- D1: [AMXX `client_print`](https://www.amxmodx.org/api/amxmodx/client_print) y [constantes `amxconst.inc`](https://github.com/alliedmodders/amxmodx/blob/master/plugins/include/amxconst.inc): tipo 2=`print_console`.
- D2: [AMXX `formatex`](https://www.amxmodx.org/api/string/formatex), contrato del destino; F4D §4 identifica además el contrato del formateador para leer varargs Float.
- D3: [AMXX `create_cvar`](https://www.amxmodx.org/api/cvars/create_cvar): orden de límites, registro inicial y valores existentes. Consultadas el 2026-11-03; documentación actual, no inventario de módulos LAN.
- D4: [guía comunitaria de demos CS 1.6](https://capdisk.com/cs16/guides/demo-record-cs16), `record nombre` / `stop`, archivos `.dem` en `cstrike`; fuente secundaria, pendiente verificar en el cliente elegido.
- D5: [guía comunitaria de parámetros GoldSrc](https://steamcommunity.com/sharedfiles/filedetails/?id=2726775482), `-condebug` / `condebug`, `qconsole.log`; fuente secundaria, pendiente verificar alcance y ruta en esa build.
- D6: [Valve Half-Life SDK, `cl_dll/demo.cpp`](https://github.com/ValveSoftware/halflife/blob/master/cl_dll/demo.cpp): buffers específicos de demo; no documenta que CS conserve toda la consola. Las páginas Valve Developer Wiki consultadas devolvieron una barrera anti-bot: no se usaron como prueba de comandos.

## 3. Inventario de canales

| Canal | Función | Dirección C | Nativa | Condición | Datos | Destinatario | Evidencia |
|---|---|---|---|---|---|---|---|
| Consola de pre | `preBhop` → `preCalc` → `showRealtimeHUD` | formatos 167696/168024/168360/168636/168972; emisión 154064 | `formatex` → `client_print`, tipo 2 | `bPreShow`, `ljs_pre_console != 0`, buffer no vacío; §5 | pre/post, FOG, M, fuser2 según rama | `plr`, buffer de `id` | [V] B; [D] D1/D2 |
| Consola de strafes | `showStrafes` | 195080–211520; emisiones 197148,201416,201612,203756,208396 | `client_print`, tipo 2 | console; contadores suficientes; selección del receptor | filas y resúmenes §6 | receptor elegido por bucle | [V] B; predicados completos de todos los resúmenes pendientes |
| Consola por frame | `showStrafes` | 209228/209424/211160/211396 | `client_print`, tipo 2 | console y `/dt`; límites 15 strafes/300 frames | gains, teclas, giro, agrupación | `plr` | [V] B |
| Consola principal | `showDistance` | 234080–272804; emisiones 261688–263304 | `client_print` | `ljs_main_console` y rutas de resultado | distancia, prestrafes, máximo, frames, strafes, etiquetas | receptores seleccionados; no se afirma broadcast universal | [V] B; desglose completo de umbrales pendiente |
| Chat de opciones | `cmdDetailed` → `client_print_f` → `ShowColorMessage` | 95108–95376; wrapper10512–11608 | `vformat`, `message_begin`/`write_string`/`message_end` | orden de alternancia `/dt` | enabled/disabled, prefijo | jugador que ejecuta comando | [V] B; no es el detalle del salto |
| Chat de resultados | `showDistance`, `edgeBugDone`, `jumpBugDone` y wrapper de color | 234080–272804; 290132–290880; 296440–297524; wrapper11336–11608 | `client_print` y mensajes de usuario, según sitio | umbrales/tipo, opciones de chat | resultados y avisos especiales | según índice y ruta; alcance exacto pendiente | [V] sitios; [H] inventario de cada predicado/receptor |
| HUD de strafes | `showStrafes` | 209084 | `set_hudmessage`, `show_hudmessage` | `ljs_strafes_hud`, selección/columnas | filas redondeadas | `plr` | [V] B |
| HUD de pre y tiempo real | `preBhop` → `showRealtimeHUD` | formatos169180–171020; emisor146992–160488 | `set_hudmessage`, `show_hudmessage` | `bPreShow`, `ljs_pre_hud`, `g_setShowPre[plr]`, buffer | completo o corto; también velocidad/altura según ruta | `plr` | [V] B; §5 |
| DHUD | `showRealtimeHUD` | 157616/159548 | `set_dhudmessage`, `show_dhudmessage` | variantes de presentación de tiempo real | buffers/indicadores del HUD | `plr` | [V] existe; asignación exhaustiva de variantes pendiente |
| HUD principal / especiales | `showDistance`, `calcJumpOff`, `edgeBugDone`, `jumpBugDone`, `jumpBugNotPoss`, `jumpBugFailed` | 266476/267148;131816/132184;290488/290556;297060/297192;307260;310608 | `show_hudmessage` | resultado, jof, éxito/fallo según función | distancias, salto, jof, avisos | según ruta | [V] B; no equivaler etiqueta de fallo con `bBadLastFrame` |
| Menús de opciones | `statsMenu1/2`, `preMenu1/2`, `enableMenu1/2/3` → `show_my_menu` | 62368–81300; wrapper8448–8604 | `show_menu` | comandos y controles localhost | opciones actuales; no historial de frames | solicitante | [V] B; seleccionar puede cambiar cvars |
| Menús de tops / MOTD | `cmdTopMenu`, `topMenu1/2/3`, `cmdTopSpeedMenu`, `showMOTD` | 311252–320832; `show_motd`320792 | `show_menu`, `show_motd` | solicitud y selección de categoría | récords almacenados | solicitante | [V] B; no recupera intento no récord |
| Trazos visuales | `draw_line` | 5280–6312, begin5396/end6288 | `message_begin`, `write_coord`, `write_byte`, `message_end` | beam habilitado y ruta que lo dibuja | geometría, no escalares internos completos | ruta de mensaje | [V] B; no usar imagen del beam como trace de velocidad |
| Sonido / orden al cliente | `edgeBugDone`, `playSound` | 293084/293164/293244;332084 | `client_cmd` | EB count>3/==3/==2; playSound omite cadena0 y usa opción de sonido | `speak misc/mod_godlike`, `speak misc/triple`, `speak misc/double`; `speak %s` con szSound | cliente indicado por la llamada; selección global depende del llamador | [V] los cuatro sitios directos; no son captura ni log |
| Registro administrativo dedicado | no establecido | — | — | no se encontró canal separado con control de flags admin | no demostrado | no demostrado | [V] checks hallados son localhost; no afirmar ausencia de toda notificación administrativa indirecta |
| Logs de servidor del plugin | sin importación directa | tabla de 111 nativas | no `log_amx`, `log_message`, `log_to_file` ni otras `log*` | — | ningún log métrico propio demostrado | — | [V] negativo acotado a importaciones; logs del motor/otros plugins quedan fuera |
| Archivos de tops | `setTop` → `saveTop` / `readTops` | 324276–331484 / 320832–324276 | `fopen`, `fputs`, `fgets`, `parse`, `fclose` | candidato a top que admite `setTop` | SteamID, nombre, distancia, máximo, pre, strafes, efficiency | archivos servidor `amxx_datadir/ljtop` | [V] B; riesgo de escritura automática |
| Configuración persistente | `plugin_init` → `saveCvars`; `cmdSaveCvars` | 46772;46964–58288;81300–81388 | `fopen("wt")`, `fprintf`, `fclose` | inicialización y guardado explícito autorizado por localhost | cvars, no trace de salto | `amxx_configsdir/kz_jump_stats.cfg` | [V] B; ejecución de cfg46708/46736 |

**Temporalidad y recuperación. [V/I]** `/dt` responde al comando inmediatamente y afecta emisiones posteriores. Filas/resúmenes se construyen desde arrays acumulados al cierre/presentación, no desde un historial consultado. La consola produce varias líneas por intento; HUD/DHUD son transitorios y pueden reemplazarse. Pre formatea antes de emitir, en el mismo recorrido de `preCalc`, y el mismo evento puede llegar a varios receptores. Tops son recuperables posteriormente, pero sólo contienen una selección de resultados; no frames ni diagnósticos completos. No se encontró un archivo de debug por frame. El registro cliente debe hacerse durante la futura sesión.

**[V] Cobertura de sitios directos:** el barrido global encuentra 37 llamadas `client_print`, 17 `show_hudmessage`, 2 `show_dhudmessage`, 1 `show_motd`, 1 `show_menu`, 4 `client_cmd`; y configuración mediante 16 `set_hudmessage`/2 `set_dhudmessage`. Los wrappers de mensajes contienen 3 `message_begin`, 13 `write_byte`, 6 `write_coord`, 1 `write_short`, 2 `write_string`, 3 `message_end`. Un único sitio dentro de un wrapper puede producir muchas emisiones. No se importa `console_print` ni `server_print`: la consola métrica llega por `client_print` tipo2. Los sitios se inventariaron sin ejecutar sus nativas; la tabla agrupa productores, no asegura haber reducido cada predicado de cada mensaje secundario.

## 4. Comandos y cvars

### Registro y permisos

**[V]** `plugin_init` C12692–46816 llama al wrapper `register_saycmd` C7848. Éste registra `say /%s`, `say .%s`, `say_team /%s`, `say_team .%s` mediante `register_clcmd` C8008/8144/8280/8416. `/dt` se registra en C15068. La escritura `/dt` en esta sección abrevia esas variantes, no un comando de consola llamado `ljs_strafes_detailed`.

**[V]** Varios comandos/menús de ajustes llaman a `is_user_localhost` C9636–9924, que compara `loopback` y `127.0.0.1`. Es una restricción de IP local, **no privilegios administrativos AMXX**. `/dt` no tiene ese control. El acceso de un cliente LAN remoto a opciones no se debe prometer por tener flags admin.

| Nombre | Tipo | Registro/lectura C | Valor | Efecto | Requiere modificación | Evidencia |
|---|---|---|---|---|---|---|
| `/dt`, `/detailed` | comando de jugador | registro15068 para dt; handler95108–95376; init96220 | alterna 0/1; inicial0 | `g_setStrafesDetailed[id]`, detalle futuro en consola; aviso de estado | sí, estado del jugador en plugin; no cvar global | [V] B; sin gate localhost/admin |
| `ljs_strafes_detailed` | no identificado en esta build | sin cadena/registro hallado | — | no equiparar a `/dt` | no proponerlo | [V] búsqueda estática negativa |
| `ljs_strafes_hud` | cvar | create21512; show209084 | default1; gate0/no0 | canal HUD | cambiarla sí; lectura estática no | [V] B |
| `ljs_strafes_console` | cvar | create21640;209112 | default1; gate0/no0 | consola, requisito de `/dt` | igual | [V] B |
| `ljs_strafes_real_gain` | cvar | create21768;197648–197864 | default0; gate0/no0 | 0=`max(gain-loss,0)`; no0=gain bruto mostrado | sí; presentación local trazada, no prueba universal de inocuidad de config | [V] B |
| `ljs_strafes_full_overlap` | cvar | create21896; **calcStrafes190060–190232** | default0; gate0/no0 | permite exportar filas totalmente solapadas; altera arrays/conteo resultante | **sí; no es sólo presentación** | [V] B/F4B§7 |
| `ljs_strafes_always` | cvar / menú | create22024;196576–196688;statsMenu2 | default0; gate0/no0 | relaja filtro de mostrar strafes | sí | [V] B |
| `ljs_strafes_total_gaineff` | cvar / menú | create22160;setSettings61676;202584/202668 | default0; gate0/no0 | resumen total gain-loss/efficiency | sí | [V] B; no llamarla `total_gain` |
| `ljs_strafes_last_column` | cvar / menú | create22296;setSettings61724;statsMenu2 C66804–68080 | default0; cvar0..2 según límites/D3; menú contiene0..3 | 0 efficiency,1 overlaps,2 desync,3 angle en código de menú/render | sí; discrepancia para3 sin resolver en entorno instalado | [V/D] B/D3; no recomendar forzar3 |
| `ljs_strafes_first_column` | cvar / menú | create22432;showStrafes195080–211520 | default0; gate0/no0 | índice o letra de tecla | sí | [V] B; asociación de cada valor se debe capturar con encabezado |
| `ljs_showpre` | cvar / opción por jugador | create18744;showRealtimeHUD146992–160488 | default0; modo0 off,1 completo,2 corto | modo HUD del receptor | sí; no habilita por sí sola consola pre | [V] B; [D] límites D3 |
| `ljs_pre_hud` | cvar | create23512;154084 | default1; rango0..2 según D3 | deshabilita/selecciona variante de HUD | sí | [V/D] B/D3 |
| `ljs_pre_console` | cvar | **create23640;153896–154064** | **default0**; gate0/no0 | permite diagnósticos pre en consola con gates adicionales | sí si está0; no se cambió ni se propone cambiar en LAN | [V] B |
| `ljs_pre_lj`, `ljs_pre_cj`, `ljs_pre_bhop`, `ljs_pre_multibhop`, `ljs_pre_dd` | cvars / selección copiada a jugador | create23768/23904/24040/24176/24312; selector151900–153884 | default1 cada una; gates0/no0 | elegibilidad de familia pre, no prueba de llamada a preBhop | sí | [V] B |
| `ljs_pre_slide`, `ljs_pre_ladderjump`, `ljs_pre_duck`, `ljs_pre_fall`, `ljs_pre_slip_bounce`, `ljs_pre_water` | cvars de familia | create24448/24984/25120/25256/25392/25528 | default0 cada una; gates0/no0 | visibilidad por familia | sí | [V] B |
| `ljs_pre_ladder` | cvar de familia | create24848 | default1; gate0/no0 | pre de escalera | sí | [V] B |
| `ljs_pre_jumpbug` | no identificado | no registro/cadena hallado | — | jumpbug usa ramas de preBhop, no cvar propia demostrada | no proponerlo | [V] negativo acotado B |
| `ljs_main_hud`, `ljs_main_console` | cvars | create19996/20124;showDistance234080–272804 | default1/1 | resultados principales | sí | [V] B |
| `ljs_main_style`, `ljs_main_name`, `ljs_main_deviation`, `ljs_main_maxspeed`, `ljs_main_prestrafes`, `ljs_main_efficiency`, `ljs_main_strafes` | cvars de presentación principal | create20252/20388/20524/20660/20796/20932/21068 | defaults1/1/0/0/2/0/1; dominios multivalor no completamente auditados | formato/campos de principal | sí; no cambiar sin inventario efectivo | [V] B; [H] dominio completo |
| `ljs_jof_hud`, `ljs_jof_console` | cvars | create23256/23384;calcJumpOff | defaults1/0 | jump-off HUD/consola | sí | [V] B |
| `ljs_chat_show_block`, `ljs_chat_min_block`, `ljs_chat_show_strafes` | cvars | create22872/23000/23128;showDistance | defaults0/1/0; umbral min_block, no booleano universal | contenido/filtro de chat | sí; efectos fuera de formato no exhaustivamente descartados | [V] B |

`gate0/no0` describe lo que **lee** el código, no autorización de cualquier entero ni prueba de sus límites de registro. Los defaults pueden estar sustituidos por la cfg: D3 dice que registrar una cvar ya existente no restablece su valor. La consulta de una cvar en una consola de servidor ya autorizada sin asignar valor puede ser sólo lectura; **no está demostrado que un jugador remoto pueda consultarla**. Aquí sólo se consultaron bytes. No usar RCON ni abrir consola LAN para resolverlo en esta fase.

### Inventario de alias de jugador

Todos los registros siguientes pertenecen a `plugin_init` C12692–46816 y al wrapper descrito. La dirección de la tabla es el inicio del handler, no una supuesta dirección de emisión. **[V]** No hay alias directos `cj`, `dcj` o `bj` en este conjunto: los tipos de salto no implican comandos homónimos.

| Nombre | Tipo | Registro/lectura C | Valor | Efecto | Requiere modificación | Evidencia |
|---|---|---|---|---|---|---|
| `/stats`, `/ljstats`, `/lj` | comandos de ajuste | `cmdStats`81472 | depende de handler | estadísticas habilitadas/ajustes; no historial personal demostrado | tratar como mutador, localhost | [V] B |
| `/style`; `/name`; `/deviation`, `/dev`; `/maxspeed` | comandos de presentación | 87072;87624;88484;89036 | estado de ajuste | campos principales | sí, localhost | [V] B |
| `/prestrafes`; `/eff`, `/efficiency`; `/strafes` | comandos de presentación | 89588;90264;91124 | estado de ajuste | pre/eff/filas | sí, localhost | [V] B |
| `/showpre`, `/pre`, `/prestrafe`; `/jumpoff`, `/jof` | comandos de presentación | 82360;83248 | modos del handler | pre/jump-off | sí, localhost | [V] B |
| `/colorchat`; `/ljsound`; `/beam`, `/ljbeam`; `/speed` | comandos de presentación | 84136;85024;85604;86184 | estado de ajuste | chat, sonido, beam, velocidad | sí, localhost | [V] B |
| `/duck`, `/ducks`, `/duckspre`, `/duckpre`; `/multibhop`; `/ljpre` | ajustes de pre | 92228;92920;93612 | estado de ajuste | familias pre | sí, localhost | [V] B |
| `/height`, `/jheight`; `/fuser2`; `/angle`, `/ang`; `/patterns`, `/pt` | ajustes de diagnóstico/presentación | 94304;94572;94840;91676 | handler específico; dominio pendiente | indicadores adicionales; no trazas internas completas | tratar como mutadores, no consultas | [V] registro B; [H] efecto exhaustivo |
| `/ljmenu`, `/ljsmenu`, `/ljoptions`, `/ljsoptions`, `/ljoption`, `/ljsoption`, `/ljsettings`, `/ljs` | menú | `statsMenu1`62368 | opciones actuales | acceso a páginas Stats/Pre/Enable | acceso localhost; seleccionar cambia estado/cvars | [V] B |
| `/savelj`, `/saveljcvars`, `/saveljsettings` | guardado | `cmdSaveCvars`81300; localhost81328 | no usar | llama saveCvars, escribe cfg | **sí, disco** | [V] B |
| `/ljversion` | información | `cmdLjVersion`81388 | texto de build | versión declarada, no hash | no escritura de métricas trazada | [V] B |
| `/ljtop`, `/ljtop10`, `/ljtop15` | menú de récords | `cmdTopMenu`311252 | categorías | tops almacenados, no detalle del último salto | consulta; sin gate localhost hallado | [V] B |
| `/weapontop`, `/wpntop`, `/weaponlj`, `/weaponljtop`, `/wpnlj` | menú de récords | `cmdTopSpeedMenu`317288 | categorías | tops de arma/velocidad | consulta; no historial completo | [V] B |

**[H]** No se identificó un comando que garantice modo de práctica sin escrituras ni un historial personal completo. Menús de categorías pueden contener LJ/CJ/DCJ/BJ sin que existan `/cj`, `/dcj`, `/bj`. No se recomienda ningún comando de borrado/restauración de récords.

## 5. Mensajes de `preBhop`

### Variables: no equiparar nombres de etiquetas y modelo

| Símbolo | Procedencia y significado acotado [V] |
|---|---|
| `pre` de estos formatos, abreviado `s` | `g_flPreHorSpeed[id]`, D329104; velocidad pre almacenada, distinta del argumento anterior `p` |
| `v` | `flHorSpeed`, FRM+16: velocidad horizontal actual que llega al helper |
| `p` / `p*` | `flPrevHorSpeed`, referencia FRM+20; original al entrar, corregida después de C168772 |
| `old` | `flOldHorSpeed`, FRM+24: velocidad antigua, no el `p` mutable |
| `M` | `flMaxHorSpeed`, FRM−68; calculada C167284–167524 a partir de `pev(id,56)` |
| `f` | `g_flPrevFuser2[id]`, D333328; histórico almacenado |
| `n`, `FOG` | `szJumpName`, FRM−64, cadena local; `g_iFOG[id]`, D325396, entero |

**[V]** `n` se construye con `duckbhop` (D1179792/C165124), `sbj` (D1179828/C165660) o `bhop` (D1179844/C166792). Estas tres llamadas a `formatex` sólo construyen la etiqueta local de 15 caracteres; no emiten mensajes. Su selección usa `g_bPreInDuck`, `g_bInDuck`, `g_bPrevInDuck` (las tres activas → duckbhop; preduck sin ambas restantes → sbj; sin preduck → bhop).

### Formatos de consola exactos

**[V]** Todos están en datos inicializados como cadenas de celdas terminadas en cero. Se conservan espacios, signos, mayúsculas y precisión. Ningún ejemplo numérico se presenta como observación.

```text
F1 D1179864: [PRE] jumpbug: pre %.3f post %.3f / fuser2: %.0f
F2 D1180060: [PRE] good %s (%d FOG): pre %.3f post %.3f (max: %.3f) / fuser2: %.0f
F3 D1180340: [PRE] minloss %s (%d FOG): pre %.3f post %.3f (max: %.3f) / fuser2: %.0f
F4 D1180632: [PRE] bad %s (%d FOG): pre %.3f post %.3f (max: %.3f) / fuser2: %.0f
F5 D1180908: [PRE] bad %s (%d FOG): pre %.3f post %.3f (max: %.3f) / fuser2: %.0f
```

En la tabla, `P=(g_szPreConMessage[id],79,formato)` son los tres primeros argumentos formales; después se enumeran **todos** los varargs en orden. `LE` y `GT` son comparaciones Float compiladas, no comparaciones de enteros reinterpretados. Los predicados de la tabla eligen el formateador; **además** se necesita el gate de emisión inferior.

| Mensaje | Formato | Argumentos | Valores observables | Condición | Destino | Precisión | Evidencia |
|---|---|---|---|---|---|---|---|
| Jumpbug | F1 | `P,s(Float),v(Float),f(Float)` | s, actual v, f; no M ni p | `bJumpbug != 0` | buffer D366196 → consola si gate | s/v3 decimales; f0 | [V] C167552–167704; call167696 |
| Good | F2 | `P,n(string),FOG(int),s(Float),p(Float por referencia),M(Float),f(Float)` | s, p sin corregir, M, FOG, f | `!JB && LE(p,M) && FOG==1` | igual | velocidades3; FOG entero; f0 | [V] C167832–168032; call168024 |
| Minloss | F3 | mismos tipos/orden que F2 | s, p sin corregir, M, FOG, f | `!JB && LE(p,M) && FOG!=1 && GT(old,M)` | igual | igual | [V] C168108–168368; call168360 |
| Bad sin corrección | F4 | mismos tipos/orden que F2 | s, p sin corregir, M, FOG, f | `!JB && LE(p,M) && FOG!=1 && !GT(old,M)` | igual | igual | [V] C168444–168644; call168636 |
| Bad con corrección | F5 | `P,n,FOG,s,p*(Float por referencia),M,f` | **p*** directamente en post; s, M, FOG, f | `!JB && !LE(p,M)`; write168772 previo | igual | igual | [V] C168720–168980; call168972; [D] D2/F4D§4 |

**Control del orden. [V]** C168112 carga M; C168120 carga old en ALT; después se guardan M como temporal y argumento2, y old como argumento1. `CALL C684` en C168148 evalúa **`old > M`**, no `M > old`. C684–752 empuja sus argumentos a `floatcmp` y usa `SGRTR`. La misma disciplina se aplicó a `PUSH_S20`: pasa la dirección guardada, no su valor; el formateador lee el Float apuntado. En F5 esa celda fue escrita por `SREF_S_PRI20` C168772.

**[V/I]** La corrección es `p*=floatmul(FloatCell(1061997773),M)`, aproximadamente `0.8M`, con M aproximadamente `sqrt((1.2*pev56)^2-16)`; se preservan orden/Float y excepciones de F4D. F5 no conserva el p anterior a la escritura. El `pre` impreso no permite recuperarlo. Las dos cadenas bad son idénticas; ver `post≈0.8*max` es compatible con corrección, pero también con coincidencia de un p original ya parecido. La etiqueta `max` no es automáticamente el máximo del salto de `[MAIN]`.

### Destino efectivo, destinatarios y periodicidad

1. **[V]** `preCalc` C140896/140952/141008 vacía los buffers completo, corto y consola antes de construir el evento. Invoca `preBhop` en C143680 sólo por la ruta de F4D §6 (`!G && PG`, jump-edge, historial/FOG y otras puertas); no todo bhop humano garantiza entrada.
2. **[V]** C145584–145684 conserva al propio jugador **o** a quien cumpla `is_spec_of_user(plr,id)`; omite los demás. No omite al propio jugador. El helper C10228–10512 exige receptor no vivo, `pev(plr,101)==id`, `pev(plr,100)` igual a 2 o 4. Los selectores se mantienen numéricos, sin asignar nombres no verificados a modos de cámara.
3. **[V]** `preCalc` llama `showRealtimeHUD(id,plr,...)` en C145772. La selección `bPreShow` usa familia de elemento y ajustes del **receptor**, antes del gate C153884. Para tipos actuales1–3: anterior4/7/8 usa `g_setCjPre`; anterior1/2/3 distingue bhop/multibhop usando un elemento más antiguo; sin índice anterior válido no habilita esta ruta. Otras familias usan Lj/DD/Duck/Fall/SlipBounce/Ladder/Slide/Water. No hay un gate universal «todo preBhop siempre visible».
4. **[V]** C153896–153984 exige `g_cvarPreConsole` D455588 no cero y primer carácter de `g_szPreConMessage[id]` no cero. C154036 empuja buffer, C154040 tipo2, C154048 **`plr`**, C154064 invoca `client_print`. **[D]** D1 identifica tipo2 como consola, no chat ni archivo de log.
5. **[I]** Es una emisión posterior al formateo dentro de ese recorrido, no una cola persistente. Un evento fuente puede producir una línea a cada receptor admitido y eventos sucesivos varias líneas; no se garantiza una sola línea por intento de salto. Un HUD posterior puede reemplazar al anterior. No hay archivo servidor de estos cinco mensajes demostrado.

**[V/D/I]** El plugin sin parchear tiene esta ruta, pero `ljs_pre_console` nace en **0**. Obtener consola puede requerir una modificación de cvar si la configuración efectiva también es0. No se recomienda hacerla en el servidor original. Los 79 caracteres máximos del buffer pueden recortar el final: no prometer que fuser2 o M siempre sobrevivan, especialmente con números largos. La captura no recupera dígitos eliminados por el formateador.

### Formatos HUD adicionales de `preBhop`

`H=(g_szPreHUDMessage[id],79,formato)`, D344812; `S=(g_szPreHUDShort[id],79,formato)`, D355504. `\n` representa el carácter salto de línea. `q=v` en jumpbug, `q=p*` (o p si no hubo write) fuera de jumpbug; `delta=q-s`. Las diferencias se calculan antes de formatear, no restando textos redondeados.

| Mensaje | Formato | Argumentos | Valores observables | Condición | Destino | Precisión | Evidencia |
|---|---|---|---|---|---|---|---|
| Completo JB | `jumpbug:\n%.3f\n%.3f` D1181184 | `H,s,v` | s y v | JB | buffer → HUD, modo completo | 3 decimales | [V] call169180 |
| Completo no JB | `%s %d FOG:\n%.3f\n%.3f` D1181372 | `H,n,FOG,s,p*` | s y p/p* | !JB | buffer → HUD, modo completo | 3; FOG entero | [V] call170188 |
| Corto positivo | `%.0f(+%.0f)` D1181260 /1181456 | `S,s,delta` | s y diferencia positiva redondeados | `q>s` | buffer → HUD corto | 0 decimales | [V] calls169520/170528 |
| Corto negativo | `%.0f(%.0f)` D1181308 /1181504 | `S,s,delta` | s y diferencia negativa redondeados | `q<s` | igual | 0 decimales | [V] calls169876/170884 |
| Corto sin diferencia | `%.0f` D1181352 /1181548 | `S,s` | sólo s | no pasa ninguna comparación estricta | igual | 0 decimales | [V] calls170012/171020 |

**[V]** `showRealtimeHUD` comprueba `ljs_pre_hud` C154084 y `g_setShowPre[plr]`: modo1 usa completo, modo2 corto. También hay buffers/ramas de altura/hold y DHUD, por lo que no se asigna indiscriminadamente cada formato a todas las llamadas HUD/DHUD del inventario. El completo no JB expone p* a tres decimales si selecciona esa variante, pero no M ni p original. El corto **no expone directamente p***: sólo s y una diferencia fuertemente redondeada.

## 6. Estadísticas detalladas y `/dt`

**[V]** `cmdDetailed` sólo alterna `g_setStrafesDetailed[id]` D454680 y envía aviso de activación/desactivación. `showStrafes` C195080–211520 consume los arrays del resultado que se está presentando. No es una consulta posterior de todos los intentos. Cinco llamadas terminales desde PreThink están en C110976/112336/113824/114348/115244; el fallback ordinario de captura no imprime todo en cada frame.

### Campos y transformaciones

| Campo visible | Variable fuente | Transformación | Formato | Condición | Canal | Evidencia |
|---|---|---|---|---|---|---|
| Número/tipo de strafe | `g_iStrafeCount` D324604; `g_iStrafeType` D270748 | índice o W/S/A/D; otro caso U | entero/letra | filas exportadas; first_column | consola/HUD | [V] showStrafes, selección197264 |
| Frames de fila | `g_iStrafeFrames` D266128 | copia del acumulador al cerrar | `%d` en formato D1194248 | fila no filtrada | consola/HUD | [V] showStrafes; F4B§9 |
| Gain mostrado | `g_flStrafeGain` D284212, `g_flStrafeLoss` D290944 | real_gain: bruto; sin él `max(gain-loss,0)` | `%.1f` | real_gain/filas | consola/HUD | [V] C197648–197864; D1194248 |
| Loss de fila | `g_flStrafeLoss` D290944 | acumulado positivo de pérdidas, no gain negativo neto | `%.1f` | fila | consola/HUD | [V] B/F4B; D1194248 |
| Efficiency de fila | `g_flStrafeEfficiency` D304408 | valor exportado `100*GoodFrames/Frames` | `%.0f` y texto porcentual D1194556 | columna/variante | consola/HUD | [V] F4B§6, showStrafes |
| Overlaps de fila | `g_iStrafeOverlaps` D297676 | entero copiado; racha, no porcentaje global | `%d` D1194520 | columna/variante, full_overlap afecta exportación | consola/HUD | [V] F4B§7, showStrafes |
| Desync de fila | `g_iStrafeDesync` D311140 | contador copiado, no porcentaje | `%d` D1194484 | columna/variante | consola/HUD | [V] F4B§8, showStrafes |
| Angle de fila | `g_flStrafeAngle` D317872 | `abs(suma firmada de giros)` al cerrar | `%.1f` D1194416 | modo Angle en render; discrepancia last_column §4 | consola/HUD | [V] F4B§8; no sumar magnitudes impresas |
| Gain total | local `flTotalGain` FRM−4 | suma de `max(gain_i-loss_i,0)`; independiente de real_gain de fila | `%.1f` en resumen total D1195316/1195488 | Total gain/Eff habilitado | consola/HUD según variante | [V] C195548–196028; formato `Total gain-loss: %.1f / Efficiency: %.1f%s` y variante minúscula |
| Efficiency total de strafes | local `flEfficiency` FRM−8 | media aritmética de efficiencies de filas, divide por strafeCount | `%.1f` en resumen total | opción total | consola/HUD | [V] C196048–196360, gates202584/202668; no es media ponderada por frames |
| Gain por frame | `g_flFrameGain` D808 | valor registrado, ya pierde precisión al mostrar | `%.1f` | `/dt`, consola y límites | consola | [V] C209448–211396 |
| Teclas por frame | `g_iFrameWSAD` D66940 | bits W8/S4/A2/D1 → texto | letras/indicadores | igual | consola | [V] mismo recorrido |
| Giro por frame | `g_iFrameDirection` D133072 | 1→`>`;−1→`<` | carácter | igual | consola | [V] mismo recorrido |
| Agrupación por frame | `g_iFrameStrafe` D199204 | agrupa/descarga líneas por fila | `%d)%s` | igual | consola | [V] emisiones211160/211396 |
| Distancia principal | `g_flDistance[id]` D338608 | valor calculado del resultado | `Distance: %.6f units` consola; HUD3 decimales | `ljs_main_console`, tipo/resultado | consola/HUD | [V] showDistance, llamada261688; D1206420/1207100 |
| Velocidad máxima principal | `g_flMaxSpeed[id]` D339136 | máximo almacenado; no M de preBhop; acompaña total de gain neto de filas | `Maxspeed: %.3f (%s%.3f)` | opciones principal | consola | [V] llamada261948; args máximo, signo, flTotalGain FRM−512 |
| Velocidad de despegue | `szConsoleFullPre` FRM−1536, construido desde `szConsole` D1204948 | concatena elementos hasta iCurElement, no un único escalar universal | `Prestrafe (FOG): %s`; precisión depende del texto previo | tipo de salto/opción | consola/HUD | [V] C262000–262288; getPrestrafesString C272804–288420; [H] desglose de todos los elementos |
| Frames/Strafes principales | `g_iFrameCount` D265336 / `g_iStrafeCount` D324604 | enteros del intento presentado | `Frames: %d`, `Strafes: %d` | resultado/opciones | consola | [V] llamadas262372/262456 |
| Efficiency principal | local `flEfficiency` FRM−516 | media de efficiencies de filas; porcentaje de fila no equivale a ratio global ponderado | `Efficiency: %.1f%s`; HUD variantes0 decimales | resultado/opciones | consola/HUD | [V] llamada262524; g_szPercent D792 |
| Velocidad de aterrizaje | ningún campo inequívoco hallado en literales MAIN | **no confundir** `land`/`last` con velocidad | no establecido | — | no establecido | [V] negativo acotado a MAIN; [H] no demostrar ausencia universal en cualquier ruta |
| Jof / land / last / block | `g_flJumpOff`, `g_flLanding`, `g_flBlock` | jof>0; land si landing>0; last=abs(landing) si<0; cero omite landing | block entero HUD/3 decimales consola | pruebas de signo y variante | consola/HUD | [V] showStrafes; estas magnitudes no certifican velocidad de aterrizaje |
| Tipo / intento fallido | clasificación y flags usados por showDistance | etiquetas Failed/Backwards/Sideways y nombres de salto | texto | ruta/tipo/config | principal/chat/HUD según variante | [V] B; [H] todas las causas de invalidación no reducidas |
| GoodFrames / bad / ground | acumuladores/estado interno | **no hay campo inequívoco directo hallado** | — | — | no establecido | [V] recorrido showStrafes no lee un marcador bad para imprimirlo; [I] límites de identificación |

**[V]** Formato base de fila D1194248: `%s%.1f %s%.1f %s%s%d %s`. Los `%s` insertan colores/prefijos/columnas: no autorizan a inventar una cabecera completa ni afirmar que todas las columnas aparecen simultáneamente. El modo de última columna elige una métrica; los encabezados y el canal deben conservarse con la fila.

**[V]** El formato MAIN D1206420 es `\n[MAIN] %s%s%s%s\nDistance: %.6f units` (D1207100, variante minúscula). Sus varargs formales en C261688 son etiqueta direccional (Backwards/Sideways/vacía), etiqueta de fallo (`Failed ` o vacía), `szJumpType` FRM−236, `szHeight` FRM−896 y `g_flDistance[id]`. La cabecera es construcción de texto más emisión posterior, no una medición independiente del tipo/validez física.

### Puertas, límites y redondeo

- **[V]** C195224–195300 retorna si HUD y consola están ambos apagados; C195308–195436 rechaza strafeCount0 o frameCount≤1. C196576–196688 evalúa filtros de receptor (`g_setStrafesAlways`, `g_bShouldBeShown`); no basta con haber saltado.
- **[V]** F4B C189632–192480 cierra según `P[i] && (ground || bad || !N[i])`; sólo exporta si `full_overlap!=0 || Frames[i]>Overlaps[i]`. La fila oculta no equivale a cero frames ni a ausencia de pulsación.
- **[V]** C209112–209184 exige consola y detalle del receptor. Imprime `[DETAILED]` C209228, pero si strafeCount>15 **o** frameCount>300 imprime `Too much info to show` C209424 en vez del detalle. Son límites de **visualización**, distintos de 500 frames/50 strafes de almacenamiento/admisión.
- **[V/I]** `%.1f`, `%.0f`, `%.3f` son precisión de presentación. No certifican exactitud de los Float. El desempate exacto de redondeo depende del formateador instalado; no se simuló. Un gain mostrado `0.0` puede ser pequeño positivo, negativo, cero o una muestra afectada por bad; no permite recuperar su signo original.
- **[V/I]** Un frame bad puede afectar denominador/cierre aunque no contribuya a GoodFrames/gain/loss (F4B/F4C). No tiene marcador explícito por frame en esta salida: la fila por sí sola no certifica bad ni la llamada de admisión que la produjo.
- **[H]** Los tipos de salto comparten rutas de strafes, pero tienen cierres y presentación específicos; no se ha demostrado igualdad de todas las columnas/mensajes en LJ/CJ/DCJ/BJ/JB. No hay promesa de recuperar un intento anterior mediante `/dt` o tops.

## 7. Matriz de observabilidad

A=directamente observable (valor/transformation visible), B=contrastable indirectamente, C=no identificable de forma única con la salida actual, D=necesita instrumentación para verificar su estado exacto. Clasificación referida a la **regla**, no sólo a la existencia de un número. Confianza alta en bytes no implica control humano alto.

| Regla | Observable | Canal | Prueba posible | Variables ocultas | Confianza |
|---|---|---|---|---|---|
| Segmentación de strafes | B; A para filas emitidas | detalle/filas | E2/E3/E10 | P/N admitidos, resets, cierres filtrados | [V/I] F4B§9; alta local/condicional causal |
| Frames | A para contador/filas; B para atribución temporal | filas y `/dt` | E1/E2 | callbacks rechazados, teclas retenidas | [V] D266128; alta |
| GoodFrames | B, no contador directo | efficiency + frames | E2/E7 | bad, q, redondeo, gain real pequeño | [V/I] F4B§6; media; no invertir % como valor exacto garantizado |
| Efficiency | A redondeada; B regla del numerador | fila/columna | E2/E7 | GoodFrames, q, bad | [V] D304408; alta presentación |
| Gain/loss | A redondeados; B origen físico | fila/detalle | E7/E14 | p original, p*, callbacks, redondeo | [V/I] F4B/F4D; alta valor visible |
| Overlaps | A contador exportado; B regla de racha | columna | E4/E5 | muestras P no emitidas/resets | [V/I] F4B§7; alta local |
| Desync | A contador; B regla direccional | columna | E6 | prevVelocity/yaw, giro exacto/q | [V/I] F4B§8; media causal |
| Angle | A valor absoluto redondeado; B cancelación | columna si accesible | E3/E6 | suma firmada, wrap, modo3 | [V/I] F4B§8; condicional |
| `bBadLastFrame` | C; D para confirmación | sin marcador directo | E11 exploratoria | flag y rama exacta | [V/I] F4C§5; alta no-identificabilidad actual |
| `g_bCatGround` | C/D | ningún escalar directo | E10 sólo compatible | categorías frente a suelo físico | [V/I] F4C§6 |
| `p*` | **A condicional**, 3 decimales; C para saber qué rama sólo por `bad` | pre consola / HUD completo | E8/E14 | p antes del write, nativas, gates | [V/D] C168772/168824/168972/154064; alta estática |
| `M` | A condicional,3 decimales | pre consola no JB | E8/E14 | entrada pev56, redondeo/truncamiento | [V] FRM−68; alta |
| Corrección `preBhop` | B; C para distinguir ramas bad coincidentes | pre + detalle | E14 | p original ausente; write no marcado | [V/I] F4D; no confirmar con gain positivo |
| Admisión `calcStrafes` | C/D por callback exacto | sólo resultados derivados | E1/E10 | puertas, B, bad, estados categorizados | [V/I] F4C§4; seis sitios no etiquetados |
| Decisiones `calcLandingAir` | C/D | etiquetas/landing derivados | E12 exploratoria | retorno y entradas de cada llamada | [V/I] F4C/F4D; ninguna etiqueta de callsite |
| Resets del intento | B para efecto; C/D para causa concreta | separación de resultados | E12 | resetVars, historia retenida, early return | [V/I] F4C§9 |
| Capacidad500 frames | C/D con detalle actual | detalle se corta antes a300 | no buscar límite jugando | entrada de CS/rechazos/historial | [V] C182608–182664; no test de estrés autorizado |
| Capacidad50 strafes | C/D | detalle se corta antes a15 | no provocar desborde | cierres múltiples en49/BOUNDS | [V/I] C182700–182728 y F4C§10 |

## 8. Protocolo experimental propuesto

**Ningún experimento se ejecuta ahora.** E1–E14 son diseños. Incluso los ensayos manuales sencillos son **no ejecutables bajo la autorización actual**; una futura autorización sólo podría habilitar los de observación en una copia aislada previamente verificada. E11 exacto y los límites de capacidad requieren evidencia adicional/instrumentación: no se convierten en pruebas manuales controladas por describir una maniobra.

### Preparación común P0 para una futura autorización

- Instalación aislada, sin carpetas compartidas/symlinks hacia LAN, con datos/config propios y sin sincronización de tops; comprobar plugins adicionales y posibles destinos externos. No preparar esa copia en esta fase.
- Identificar hashes de plugin, mapa, AMXX/módulos, cliente, FPS, parámetros de red/física, arma, punto de salida, superficie, altura y receptor. Mantenerlos constantes; anotar cualquier variación.
- Capturar capacidades/valores efectivos sin asignaciones, por el operador autorizado. No cambiar física, récords, permisos ni cvars de cálculo. Habilitar detalle sólo con consentimiento para ese estado por jugador; si falta consola, detener el objetivo en vez de «arreglar» LAN.
- Definir identificadores `S01-E01-I001`, notas de preparación y captura de consola+HUD. Registrar fallos, ausencia de salida y todos los intentos, no seleccionar sólo los compatibles.
- Bloques cortos, por ejemplo cinco intentos por condición como exploración, no como garantía estadística. Sin macros, scripts de inputs, plugins ni promesa de idéntico frame humano. Comparaciones entre intentos son aproximadas.
- Riesgo común R: un salto puede alcanzar `setTop`; incluso iniciar el plugin ejecuta/guarda cfg. **Todos** los E comparten R. Si no hay aislamiento demostrado, ninguno es seguro para récords originales.

### E1 — Salto normal con detalle

- **Objetivo/hipótesis [H]:** establecer una captura base; con gates correctos aparecerán resumen, filas y detalle del resultado.
- **Preparación/constantes:** P0, consola de strafes ya permitida, confirmar el aviso enabled de `/dt`; misma arma, lugar, tipo de salto, opciones y FPS.
- **Acciones futuras:** un salto sencillo, pausa para guardar toda la salida antes del siguiente; repetir en bloque corto sin buscar récord.
- **Esperado/registro [I]:** formatos de §6, no números predichos; copiar cabeceras, filas, `[DETAILED]`, gain/teclas/giro y screenshot del HUD.
- **Alternativas/dato discriminante:** falta de detalle puede ser filtro, captura incompleta o límite, no ausencia de `calcStrafes`; contar frames/filas y conservar aviso de `/dt` y configuración conocida.
- **Falsación/control/riesgo:** salida incompatible con formatos en build idéntica y gates verificados refutaría el modelo de presentación; ausencia sola es inconclusa. Control medio para salto, bajo para callbacks. R; no cambiar cvars globales.

### E2 — Un único strafe

- **Objetivo/hipótesis [H]:** una tecla sostenida sin cambios puede producir una fila atribuible a esa tecla.
- **Preparación/constantes:** P0/E1; mismo despegue, sin segunda tecla voluntaria; duración y giro sólo aproximados.
- **Acciones futuras:** sostener una dirección durante el aire y aterrizar; registrar también la liberación real, sin asumir un número exacto de muestras.
- **Esperado/registro [I]:** fila/agrupación compatible con esa tecla, frames y efficiency; conservar detalle completo y vídeo/demo auxiliar si existe.
- **Alternativas/dato discriminante:** más filas pueden venir de teclas del despegue, bad o resets; WSAD de detalle ayuda, pero no expone toda la historia P/N de callbacks rechazados.
- **Falsación/control/riesgo:** una fila cuya eficiencia sea incompatible con cualquier GoodFrames entero entre0 y Frames, incluso considerando redondeo, contradice la fórmula bajo sus supuestos. Control medio; no llamar a una tecla humana «una llamada». R.

### E3 — Cambio de dirección

- **Objetivo/hipótesis [H]:** liberación/cambio de tecla puede cerrar una fila; angle acumula giro firmado antes de abs.
- **Preparación/constantes:** P0; mismo recorrido; una secuencia A→D y otra con giro revertido, sin alterar sensibilidad/FPS.
- **Acciones futuras:** cambio manual distinguible a mitad del aire, guardar cada intento por separado.
- **Esperado/registro [I]:** agrupaciones y letras distintas; si Angle es accesible, valor absoluto posiblemente menor con giro que se cancela. Registrar filas, marcadores, columna seleccionada y vídeo.
- **Alternativas/dato discriminante:** admisión/resets y wrap del yaw pueden dar igual angle; falta yaw exacto y no está disponible como trace completo.
- **Falsación/control/riesgo:** letras/agrupación manifiestamente incompatibles con la máscara capturada justificarían revisar segmentación; cancelación fallida entre inputs humanos no basta para refutarla. Control bajo de ángulo exacto. R; no forzar modo3.

### E4 — Dos teclas simultáneas

- **Objetivo/hipótesis [H]:** WSAD conserva combinaciones; denominadores por tecla no equivalen a GoodFrames compartidos.
- **Preparación/constantes:** P0; elegir W+A o A+D, una combinación por bloque, mismo lugar y giro.
- **Acciones futuras:** sostener ambas y liberar, sin automatización; no extrapolar cancelación física de pares opuestos a contadores.
- **Esperado/registro [I]:** máscaras multitecla en detalle y filas si pasan filtro. Guardar frames, efficiencies, overlaps y encabezados.
- **Alternativas/dato discriminante:** fila ausente puede ser full_overlap=0; prioridad q depende de Start. Se conoce máscara, pero no todos los Start ni good/bad.
- **Falsación/control/riesgo:** no observar dos filas no refuta dos denominadores; una contradicción necesitaría cierres exportados y estado completo. Control medio de combinación, bajo de atribución temporal. R.

### E5 — Overlaps deliberados

- **Objetivo/hipótesis [H]:** el contador refleja racha final de multitecla, no total de todos los solapamientos.
- **Preparación/constantes:** P0; secuencias A→A+D→A frente a A→A+D→liberación, sin cambiar full_overlap.
- **Acciones futuras:** introducir un intervalo visible de doble tecla y, en una condición, volver a una tecla antes de cierre.
- **Esperado/registro [I]:** con suficiente muestra monotecla previa al cierre puede verse overlap0 aunque antes hubo doble tecla. Guardar detalle y columna overlap de cada condición.
- **Alternativas/dato discriminante:** muestreo P, cierre anticipado o fila filtrada; máscaras ayudan, no identifican todos los callbacks.
- **Falsación/control/riesgo:** acumulación conservada tras un reset monotecla confirmado y mismo segmento contradiría la regla; sin esa confirmación, resultado sólo compatible. Control medio/bajo. R; no habilitar full_overlap como simple cambio visual.

### E6 — Desync deliberado

- **Objetivo/hipótesis [H]:** desync puede crecer con discordancia tecla/giro y no está definido por gain negativo.
- **Preparación/constantes:** P0; pareja misma tecla con giro habitual y contrario; opción Desync ya accesible sin mutar cálculo.
- **Acciones futuras:** invertir voluntariamente giro durante un tramo; anotar intención separada de datos capturados.
- **Esperado/registro [I]:** posible cambio del contador, compatible con F4B§8. Guardar desync, gain/loss, dirección y vídeo.
- **Alternativas/dato discriminante:** prevVelocity/yaw y q cambian también; giro contrario humano no demuestra la relación exacta del helper. Faltan vectores precisos.
- **Falsación/control/riesgo:** ni gain positivo ni contador0 refutan por sí solos la regla. Sólo entradas direccionales completas permitirían falsación de su tabla. Control bajo; R.

### E7 — Gain positivo y negativo

- **Objetivo/hipótesis [H]:** bruto, loss y gain neto presentado no son la misma magnitud; efficiency usa signo real, no texto redondeado.
- **Preparación/constantes:** P0, real_gain efectivo conocido y fijo; mismo salto, tramo acelerado y tramo con desaceleración voluntaria.
- **Acciones futuras:** realizar intentos con ambas tendencias sin cambiar cvars; conservar todos, incluidos0.0.
- **Esperado/registro [I]:** signos en detalle y loss en filas; anotar bruto/neto según encabezado. Copiar valores sin recalcularlos desde screenshots parciales.
- **Alternativas/dato discriminante:** corrección de p, bad, redondeo y filtro; sums de `%.1f` no recuperan acumulados exactos. p original y bad no están expuestos.
- **Falsación/control/riesgo:** un neto mostrado negativo bajo la rama0 y formato inequívoco contradice el clamp; discrepancias de décimas al sumar no lo hacen. Control medio; R.

### E8 — Bhop

- **Objetivo/hipótesis [H]:** una transición admitida puede producir diagnóstico preBhop y HUD completo/corto.
- **Preparación/constantes:** P0, gates pre efectivos conocidos; si pre_console está0, limitarse al HUD disponible o posponer. No activarlo en LAN.
- **Acciones futuras:** bhop manual sencillo con historia inicial comparable; registrar eventos previos al salto, no sólo aterrizaje.
- **Esperado/registro [I]:** alguna variante §5 si se alcanza su ruta; guardar FOG, etiqueta bhop/sbj/duckbhop, pre/post/max/fuser2 presentes y HUD.
- **Alternativas/dato discriminante:** categoría/FOG pueden impedir helper o emisión; ausencia de mensaje no prueba ausencia de corrección. Diagnóstico completo acota más que gain solo.
- **Falsación/control/riesgo:** valores inequívocos incompatibles con la correspondencia post/argumento ameritan revisar dataflow/build; «no salió PRE» es inconcluso sin gates. Control bajo de FOG exacto; R.

### E9 — Jumpbug

- **Objetivo/hipótesis [H]:** la build admite rutas JB; su formato pre usa s y v, omite M y no ejecuta la corrección local.
- **Preparación/constantes:** P0, zona segura de copia aislada, técnica conocida, sin instalar entrenamiento ni alterar gravedad.
- **Acciones futuras:** intento manual sólo si autorizado y viable; en otro caso registrar «no ejecutable por control insuficiente».
- **Esperado/registro [I]:** posible `jumpbug`/avisos success/failure; capturar pre completo y contexto de caída. No prometer trigger JB por maniobra.
- **Alternativas/dato discriminante:** el JB del helper es FOG/old en F4D, no nombre de input humano; falla técnica o gate puede ocultar formato. No hay trace del booleano.
- **Falsación/control/riesgo:** un mensaje íntegro F1 con campo max no corresponde al formato reconstruido; ausencia de F1 no refuta admisión JB. Control bajo; R y top de JB C297524.

### E10 — Aterrizaje que cierre un strafe

- **Objetivo/hipótesis [H]:** tecla sostenida hasta llegada puede cerrar por bGround sin liberación previa.
- **Preparación/constantes:** P0, superficie plana, misma altura, evitar ladder/duck y contactos ajenos en lo posible.
- **Acciones futuras:** sostener tecla hasta tocar superficie y soltar después, anotando la incertidumbre temporal.
- **Esperado/registro [I]:** fila final presentada con tecla previa y conteo; guardar detalle final, HUD, landing/jof y vídeo auxiliar.
- **Alternativas/dato discriminante:** liberación ya muestreada, bad o categorización anticipada cierran igual. `g_bCatGround` no se ve; vídeo no lo sustituye.
- **Falsación/control/riesgo:** el resultado sólo contrasta cierre, no identifica ground; para falsar el predicado exacto hace falta flag/callsite oculto. Control bajo del frame terminal; R.

### E11 — Frame bad

- **Objetivo/hipótesis [H]:** bad puede sumar Frames/cerrar sin sumar gain/loss/good.
- **Preparación/constantes:** P0 más identificación independiente de la rama bad; esta última **no está disponible** en salida actual.
- **Acciones futuras:** no ordenar colisiones o manipulación para «forzar un bad». Sólo catalogar capturas incidentales con final atípico.
- **Esperado/registro [I]:** posible fila terminal/efficiency menor, sin marcador bad; conservar salida bruta completa.
- **Alternativas/dato discriminante:** pérdida normal, redondeo, q y callbacks admitidos explican lo mismo. Se necesitaría flag y contador por callback, instrumentación no autorizada.
- **Falsación/control/riesgo:** prueba exacta **no ejecutable sin instrumentación adicional**; no hay falsación limpia desde esa captura. Control insuficiente; R. Una etiqueta Failed no es ese flag.

### E12 — Intento invalidado

- **Objetivo/hipótesis [H]:** cierre con etiqueta Failed y reset sin salida son situaciones distintas.
- **Preparación/constantes:** P0, condición manual inocua conocida del mapa; sin muerte forzada, comandos de reset ni alteración de datos.
- **Acciones futuras:** salto corto que no complete la llegada prevista; guardar inmediatamente cualquier salida y el siguiente intento base.
- **Esperado/registro [I]:** quizá resultado Failed o silencio; anotar ambos, continuidad de filas y contexto, sin atribuir causa única.
- **Alternativas/dato discriminante:** filtro de presentación, reset, admisión y `calcLandingAir` dan observaciones parecidas. Faltan retorno, estados y motivo de reset.
- **Falsación/control/riesgo:** el silencio no falsaría ninguna rama específica; sólo un trace de estados permitiría prueba exacta. Control medio de maniobra/bajo de invalidación; R, no se demostró que Failed impida guardar en toda ruta.

### E13 — Comparación de opciones

- **Objetivo/hipótesis [H]:** seleccionar presentación puede cambiar lo visible sin equivaler a cambiar captura; full_overlap es excepción interna demostrada.
- **Preparación/constantes:** P0 y autorización **separada** para cada ajuste en copia aislada; guardar valores previos. Sin permiso de cambios, prueba pospuesta.
- **Acciones futuras:** primero comparar `/dt` off/on; después, sólo opciones cuya inocuidad esté suficientemente delimitada, una por bloque. No comparar un salto humano como si fuera replay idéntico.
- **Esperado/registro [I]:** `/dt` agrega detalle, real_gain cambia definición de columna, last_column cambia métrica si estado alcanzable. Guardar menú/aviso/encabezado y valores antes/después.
- **Alternativas/dato discriminante:** inputs diferentes y estado heredado explican variaciones numéricas; no se puede demostrar invariancia de cálculo sólo con dos intentos humanos.
- **Falsación/control/riesgo:** cambio de significado contrario al mapeo en una captura bien identificada refuta presentación; cambios de números entre saltos no. Control medio de opción/bajo de inputs; R y cfg; **excluir full_overlap**, no forzar angle3.

### E14 — Corrección preBhop potencial

- **Objetivo/hipótesis [H]:** observar post y M de una rama compatible con p*=0.8M, sin convertir compatibilidad en prueba de write.
- **Preparación/constantes:** P0/E8, diagnóstico completo ya permitido; mismas historia, arma, física y familia en lo posible. Si faltan campos por gate/truncamiento, posponer.
- **Acciones futuras:** recopilar bhops manuales ordinarios; clasificar después good/minloss/bad/JB. No buscar estados extremos ni tocar pev/cvars.
- **Esperado/registro [I]:** algunas líneas bad podrían mostrar post aproximadamente0.8max. Guardar línea íntegra, HUD completo, detalle del salto, contexto y orden de eventos.
- **Alternativas/dato discriminante:** rama bad sin write con p≈0.8M, aceleración normal, evento distinto y redondeo. Para distinguir hace falta **p original del mismo evento**, no s etiquetado pre; no está expuesto por estos formatos.
- **Falsación/control/riesgo:** post lejos de0.8max rechaza atribuir *esa línea* a la rama corregida bajo aritmética finita, pero no refuta existencia de corrección ni dice qué callback fue. Igualdad aproximada no la confirma. Control bajo; R; prueba causal concluyente no ejecutable con salida actual.

## 9. Captura de evidencia del cliente

No se ejecutó ningún comando del cliente. Los comandos son propuestas **condicionadas** a autorización futura y comprobación local de soporte; no se extrapolan comandos Source a GoldSrc.

| Mecanismo | Conserva | Puede perder / redondeo | Cronología | Cambios/archivos/privacidad | Estado de evidencia |
|---|---|---|---|---|---|
| Copiar/guardar consola visible | texto recibido, encabezados y valores ya formateados | scrollback finito, recortes previos, HUD no impreso; no recupera Float | orden local si se guardan todos los bloques | sólo cliente; archivo de notas local; puede incluir nombres/IP/chat | [I] mecanismo general; soporte de selección/exportación de esa build pendiente |
| `condump`, si existe en cliente GoldSrc elegido | candidato a volcado del buffer de consola | no se verificaron soporte, sintaxis ni nombre/ruta; no confundir con Source | orden de buffer, no timestamp garantizado | no usar hasta verificar localmente sin conectar; nunca sustituir por orden servidor | [H] no prescrito como mecanismo garantizado |
| `condebug` / `-condebug` | log de consola según build | alcance cliente/servidor y activación pendientes; no incluye HUD sólo por estar en pantalla | append local; puede no tener timestamp por línea | D5 menciona qconsole.log; crece; verificar ruta/rotación local; no tocar server.cfg | [D] secundario D5; [H] compatibilidad exacta |
| Captura de pantalla del SO / Steam | HUD, DHUD, chat o consola que realmente se vea | nada fuera de pantalla; solapamiento, desaparición; sólo precisión impresa | nombre+ID y hora externa; reloj no da frame del servidor | sólo cliente, imagen local; ocultar datos personales antes de compartir | [I] preferencia conservadora sin depender de comando de motor |
| `snapshot`, si se verifica en cliente | candidato a imagen local | comando/formato/ruta no confirmados aquí; no ordenarlo a ciegas | igual que imagen | sólo cliente, tamaño acumulativo | [H] preferir captura del SO hasta documentar build |
| Demo `record nombre` / `stop` | secuencia reproducible de datos de demo, contexto de movimiento | **no garantía de toda la consola, chat o HUD**; replay puede diferir; no es trace interno | secuencia/ticks relativos de demo, enlazar a ID externo | `.dem` local en cstrike según D4; tamaño crece; puede incluir identidades/voz según build | [D] D4; D6 no prueba cobertura total de CS |
| Vídeo de pantalla opcional | lo renderizado, varios canales y orden visible | frames de vídeo no son callbacks; HUD puede durar menos de una captura; compresión | reloj/ID en notas, sincronización aproximada | sólo cliente/SO; mayor tamaño, voz/privacidad, carga puede cambiar FPS | [I] auxiliar, no instrumentación del plugin |
| Tops/MOTD | resultados seleccionados persistidos | no todos los intentos, ni frames, ni pre-diagnóstico completo | no historial cronológico demostrado | servidor; no tocar/extraer sin autorización | [V] B; no usar como archivo principal de evidencia |

**Procedimiento futuro mínimo [I]:** verificar mecanismo de captura **sólo en cliente desconectado** bajo autorización posterior; marcar un ID en notas externas y, si `echo` está documentado en esa build, en consola local; guardar consola+HUD por intento sin borrar scrollback; cerrar la demo con `stop` sólo si se inició; comprobar archivos y espacio local. No usar `log on`, `rcon`, `exec`, `writecfg`, comandos de guardado del plugin ni cambiar cvars de física como sustituto de captura.

No se puede asegurar registro cronológico completo si faltan líneas entre intentos. Los mensajes pre pueden preceder al resumen del salto; agrupar por tiempo/contexto y no por simple proximidad de dos números. Una demo sin captura textual no acredita que el jugador recibiera determinada línea. Chat conservado en consola depende del cliente y debe comprobarse, no suponerse.

## 10. Riesgos y precauciones

**[V] Riesgo positivo, no mera posibilidad genérica:** `showDistance` llama `setTop` C267960; `edgeBugDone` C290880 y `jumpBugDone` C297524 también. `setTop` llama `saveTop` C329436. `saveTop` abre con `"wt"` C330376 y escribe C331400: puede reescribir el archivo de la categoría. `readTops` usa `amxx_datadir/ljtop`, abre `"rt"` C322904. El formato D1239088 es `%s "%s" %s %s %s %s %s\n` (SteamID, nombre, distancia, máximo, prestrafe, strafes, efficiency). No se hallaron importaciones SQL/nvault; esto no prueba que otros plugins no escriban bases de datos.

**[V]** `plugin_init` construye la ruta de cfg C46512–46612, la ejecuta C46708/46736 si existe y llama `saveCvars` C46772; `saveCvars` abre `"wt"` C47208, escribe con `fprintf` y cierra C58168. Por tanto **arrancar para “sólo mirar” tampoco se ha demostrado sin efectos de disco**. Los menús/órdenes de ajustes no son consultas inocuas universales.

Comprobaciones previas a cualquier sesión, **todas pendientes**:

- [ ] Autorización explícita: instalación destino, operador/sesión, conexión y acciones concretas; ninguna credencial implícita.
- [ ] Confirmar si LAN es compartida y quién es propietario de récords/configuración; no usarla como laboratorio por defecto.
- [ ] Copia aislada de instalación y datos, creada sólo tras autorización; independencia real de directorios de configs, tops, backups, módulos y sincronizadores.
- [ ] Copia de seguridad verificable y procedimiento de restauración de **la copia experimental**, sin plan de sobrescribir la instalación original.
- [ ] Hashes de plugin/mapa, AMXX/nativas/JIT, cliente y módulos; no basta `/ljversion`.
- [ ] Inventario efectivo de cvars por operador autorizado en modo lectura; distinguir defaults de cfg y preferencias por receptor.
- [ ] Confirmar que ningún otro plugin escribe récords, bases remotas o estadísticas compartidas. Ausencia de SQL en este plugin no basta.
- [ ] Determinar elegibilidad de tops y modo de práctica, si existe, sin asumir que apagar HUD/chat/dt impida escribir; no se demostró un interruptor seguro de no-persistencia.
- [ ] Excluir cambios de física, ljs_strafes_full_overlap, resets, borrado, guardado de cvars y límites de capacidad del bloque inicial.
- [ ] Captura local probada, espacio disponible, nombres únicos, política de retención y privacidad; medir carga de vídeo/FPS sin alterar condiciones entre bloques.
- [ ] Regla de parada y responsable: ante cambio inesperado, posible escritura compartida, configuración distinta o datos insuficientes, detener maniobras y conservar evidencia; no «limpiar» récords para ocultar el incidente.

**[I] Recomendación:** hasta demostrar aislamiento, no recomendar pruebas en la instalación original, ni siquiera saltos modestos. No se garantiza que no alcancen un récord ni que un fallo de salto excluya toda persistencia.

## 11. Limitaciones de identificación causal

Cada E documenta observación, hipótesis compatible, alternativas, dato discriminante y disponibilidad. Principios comunes:

1. **[V/I]** Gain positivo es compatible con aceleración, corrección de p, historia distinta y selección de muestras; no demuestra `preBhop` ni C168772.
2. **[V/I]** `[PRE] bad` no identifica la rama corregida. `pre`≠p; post≈0.8max es condición compatible, no observación del p perdido. El HUD corto agrega pérdida de información.
3. **[V/I]** Una fila es resultado de captura+resets+atribución+cierre+filtro+presentación. No identifica el callsite, ground, bad ni `calcLandingAir` de cada callback.
4. **[V/I]** `%` de efficiency y décimas de gain son funciones muchos-a-uno. No reconstruir GoodFrames, sumas exactas ni signo de0.0 sin considerar todos los valores que redondean igual.
5. **[I]** La intención del jugador y un vídeo no fijan P/N, FOG o prevVelocity del servidor. Demos y FPS del cliente tampoco equivalen a muestras admitidas. No introducir macros para resolverlo en esta fase.
6. **[H]** La semántica instalada de nativas y límites puede diferir de documentación actual. El desacuerdo entre modo Angle3 y límite cvar2 merece investigación estática puntual o futura comprobación autorizada, no parchear el plugin.

No hay resultados experimentales en este informe. Toda «salida esperada» es una predicción del análisis estático, no una transcripción obtenida en CS.

## 12. Conclusiones

**[V/D]** La prioridad se resolvió a nivel estático: cinco formatos de consola y sus argumentos están identificados, el flujo llega a `client_print` de consola y p* se pasa directamente en la rama corregida; también existe representación HUD completa. Se distinguen explícitamente s, p/p*, v, old y M.

**[V/I]** La Fase 4B puede contrastarse sobre contadores/filas emitidos, detalle por frame redondeado y selección de columnas. No es observación directa de GoodFrames, bad, categoría, admisión o historia completa. La Fase 4D tiene un escalar observable, pero no una marca inequívoca del write; Fase 4C conserva estados ocultos. Los límites de detalle impiden usar `/dt` como validación directa de500/50.

**Resultado parcial, no bloqueo:** hay relación demostrada entre cadenas, argumentos y canales principales. Quedan incompletos algunos predicados y variantes de resultados principales, chat/DHUD, dominios de ciertas opciones, configuración original ausente y compatibilidad de captura. Las cuatro órdenes directas al cliente se identificaron como sonido, no telemetría. Los pendientes se reportan en vez de inventar mensajes o garantizar seguridad de LAN.

## 13. Recomendación para la siguiente fase

Primero obtener, mediante una entrega de archivos autorizada y sin conectarse ahora, la configuración/idioma de KZ-Rush que falta y la identificación de builds del cliente/AMXX. Resolver estáticamente las discrepancias de presentación y decidir el aislamiento de datos. Después solicitar autorización específica para **una sesión manual en copia aislada**, empezando E1/E2/E7 y luego E8/E14 si los diagnósticos ya son accesibles.

No avanzar automáticamente, no activar cvars en LAN y no implementar KZ Coach. La prueba causal exacta de la corrección y de las ramas ocultas continúa pendiente de evidencia que la salida actual no proporciona.
