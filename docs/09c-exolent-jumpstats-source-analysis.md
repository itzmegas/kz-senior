# Exolent JumpStats 1.7.3: qué mide y qué no permite diagnosticar

Investigación 09c · 2026-11-03 · análisis estático, sin compilación ni ejecución.

## 1. Resumen ejecutivo

**Exolent mide variaciones de velocidad horizontal entre muestras PostThink, las agrupa por alternancia AW/SD habilitada por cambios de yaw y calcula una distancia corregida con muestras PreThink y helpers balísticos. No mide directamente coordinación mouse–teclado ni conserva un historial completo de los intentos.**

- **[V]** Están los seis `.sma` y los includes `jumpstats`, `jumpstats_const` y `jumpstats_stocks`. A diferencia del material UQ disponible, aquí se pueden leer los helpers de aterrizaje, fallo y bordes. Su presencia **no recupera los helpers de UQ**.
- **[V]** Sync global es el porcentaje redondeado de muestras aéreas con velocidad mayor que la anterior. Incluye ausencia de teclas, igualdad en el denominador y muestras anteriores al primer strafe. No exige giro ni coincidencia de dirección.
- **[V]** Gain por strafe suma todos los incrementos positivos; loss suma las caídas. El paréntesis junto a MaxSpeed es `máximo−pre`, una tercera cantidad. El máximo global sí compara contra el máximo anterior, a diferencia de KZTimer analizado en 09b.
- **[V]** El código de acumulación PostThink no comprueba salto activo: puede trabajar durante otras situaciones aéreas. La inicialización del intento reinicia acumuladores; eso delimita el resultado ordinario, pero no convierte el callback en un capturador exclusivo del salto.
- **[V]** La distancia exitosa ordinaria es el menor de dos candidatos de norma 3D, más 32. LadderJump resta después 16. El fallo tiene otra fórmula, no un aterrizaje observado ni una medida explícita de déficit al destino.
- **[V/I]** Hay riesgos verificables: contador de strafes sin tope aunque arrays de 20; salida sin cap; divisiones sin guarda; orígenes mutados por el helper de bordes; resets diferidos y tareas compartiendo identificador. No se corrigen aquí.

**Efecto sobre AMX v8 [I]: no cambia la ruta técnica de 09.** Exolent ofrece contrastes y casos para interpretar KZ-Rush, no opcodes ni evidencia de sus fórmulas. Siguen pendientes `cmdDetailed`, `fwCmdStart`, `calcStrafes` y sus flujos de datos. No se inició ese desensamblado.

### Convenciones y mapa de lectura

| Marca | Alcance |
|---|---|
| **[V]** | Verificado directamente en el código local; no implica ejecución ni precisión física certificada. |
| **[D]** | Documentado por una fuente identificada o informe previo; no fórmula recuperada de otro binario. |
| **[I]** | Consecuencia, comparación o propuesta derivada, con condiciones. |
| **[H]** | Hipótesis que requiere pruebas independientes. |

En las citas: **M** = `reference/jumpstats_main.sma`; **L** = `reference/jumpstats_long.sma`; **B** = `reference/jumpstats_bhop.sma`; **C** = `reference/jumpstats_count.sma`; **A** = `reference/jumpstats_ladder.sma`; **W** = `reference/jumpstats_weird.sma`; **K** = `reference/scripting/include/jumpstats_const.inc`; **S** = `reference/scripting/include/jumpstats_stocks.inc`; **J** = `reference/scripting/include/jumpstats.inc`. Los rangos son líneas físicas de los archivos identificados por hash, no líneas debug de AMX. Una referencia abreviada conserva esa ruta exacta.

Unidades: posición/distancia en unidades del motor, velocidad en unidades/s, `get_gametime()` en segundos. «Frame» significa ejecución contada por esta lógica, **no** frame renderizado, duración fija ni comando identificado. Se leyeron completos los seis archivos y S/K/J; se revisaron los documentos 03, 04, 05, 07, 08, 09 y 09b antes de comparar.

## 2. Procedencia, archivos y dependencias

### 2.1 Identidad reproducible [V]

La identidad declarada común es **JumpStats 1.7.3, Exolent** (`K:9–11`). Los registros de plugin usan esa identidad: `M:316`, `L:156`, `B:166`, `C:168`, `A:164`, `W:150`. No se deduce una fecha de release o compilador de esos textos.

| Archivo bajo `reference/` | Líneas | SHA-256 de los bytes originales |
|---|---:|---|
| `jumpstats_main.sma` | 2868 | `7b08b1599d839a883d3d6c0bbd0b7da53cd687bd31b091c01d3b33f0ad835ec6` |
| `jumpstats_long.sma` | 1447 | `489120984b3e86c981c653c7ad499e2ddb11140563b63ce85d920e9928aa3e05` |
| `jumpstats_bhop.sma` | 1559 | `88cb151eaa155fb08b6436203d760b304025455aea0d92c73b1a61bfce43719b` |
| `jumpstats_count.sma` | 1621 | `d1697ebf4462205937cc3b9f821b65c3d4f3eff298a753046db8b03c82c0010c` |
| `jumpstats_ladder.sma` | 1528 | `1162ad9cb3c8e9685dc70142f039737e4582b4f9e0a94aaa24b73fe010e8863f` |
| `jumpstats_weird.sma` | 1384 | `2145a05bd91601e9bfcf1a5bbe7d01df6ecc1d8ec5811b327ba8585048f4cac8` |

| Include bajo `reference/scripting/include/` | Líneas | SHA-256 |
|---|---:|---|
| `jumpstats.inc` | 50 | `9def4ea60abc5fda1b6782002b070a7b25c1c910a2a3e755a8daa423f86f776f` |
| `jumpstats_const.inc` | 314 | `5ca058a7a753b855a1766bca5d6a1f417a518bf4d04c546292064b90c37cd534` |
| `jumpstats_stocks.inc` | 919 | `df51d53766739f693d456d6bb61cd9da461638a3ffd398ccccb8c0c18b6ef83c` |
| `colorchat.inc` | 147 | `370ea4b46b1cccff8d11ef70476e7fead5b4090aaf56f8ec1a730786e54ec756` |
| `fvault.inc` | 648 | `af2081ee9f94e4b0c9019066821870afa3db166ae2d5873864af661cf7ee11bc` |

El enlace aportado es [AlliedModders 87906](https://forums.alliedmods.net/showthread.php?t=87906). La consulta devolvió **HTTP 403**. **[D]** Es la procedencia indicada por el usuario; **[V]** la autoría/versión están en el include local; **no se comprobó** identidad byte a byte con adjuntos originales, changelog, licencia de redistribución o correspondencia con un servidor instalado. No afirmar linaje entre plugins por parecido del código.

### 2.2 Includes y dependencias [V]

- `M:1–9`: amxmodx, amxmisc, fakemeta, colorchat, hamsandwich, jumpstats_const, jumpstats_stocks, engine, fvault.
- `L:1–8`: amxmodx, amxmisc, fakemeta, colorchat, hamsandwich, jumpstats, cstrike, engine. B/C/A/W agregan fakemeta_util (`:1–9`).
- J incluye K/S (`J:8–9`) y requiere la biblioteca `jumpstats` (`J:12–19`), provista por `plugin_natives` de M (`M:574–598`).
- S depende además de fun y xs (`S:7–16`); K de hlsdk_const (`K:7`). Son APIs/constantes del entorno AMXX; sus versiones locales exactas no están vendorizadas en esta carpeta. No se instaló nada para resolverlas.
- Recursos/configuración referidos: `sprites/zbeam1.spr`, sonidos de K (`K:193–202`), `jumpstats_sounds.ini`, `jumpstats_reset.ini`, `jumpstats.cfg`, directorio de datos `jumpstats`, y vaults de mejores marcas/preferencias/acuerdo (`M:178–180,194–312,503–565`). No se necesita ejecutarlos para leer la aritmética.

**No hay bloqueo por helpers Exolent ausentes.** Dependen de K: límites, gravedad, máscara grounded, offsets, enums y tamaños de bloques. Dependen de S: `CalculateLandOrigin`, `GetFailedDistance`, `GetEdgeDistances`, postura/suelo, dirección, equipos/armas y velocidad máxima de arma. Las funciones AMXX de trace, físicas y almacenamiento son externas: observar una llamada no prueba fidelidad del motor ni de un build concreto.

### 2.3 Variables y retención [V]

| Grupo | Declaraciones representativas y diferencias |
|---|---|
| Estado por jugador | Slots `[33]`: conexión, vida, reset, salto, suelo previo, primer frame y reentrada PostThink (`L:20–29`); B agrega jumped/bhopped/springjump (`B:23–43`); C caída/DD/contador (`C:23–44`); A ladderjump/ladderbhop/referencia (`A:21–39`); W caída (`W:11–27`). |
| Velocidades/agregados | `g_jump_maxspeed` es **límite del arma**, no pico medido; `g_prestrafe`, `g_maxspeed`, `g_old_speed`, `g_good_sync`, `g_sync_frames`, `g_strafes`, AW/SD y giros (`L:31–58`, `B:34–66`, `C:37–67`, `A:33–62`, `W:21–50`). |
| Filas por strafe | Cinco arrays Float `[33][20]`: good, frames, max, gained, lost. No guardan yaw/botones/tiempo por muestra. `MAX_STRAFES=20` (`K:18`). |
| Referencias de vuelo | Inicio de intento, primer origen/velocidad aérea, última pareja aérea, última pareja apta para fallo y postura (`L:34–35,60–73`; equivalentes B/C/A/W en las declaraciones anteriores). No es una matriz de todos los frames. |
| Geometría visual | `[33][120][3]` posiciones, `[33][120]` postura/tipo, contador; admite separación XY mínima 2.5 (`K:34–37`, `L:77–79`). Entidad de salida guarda origen/mins/maxs/ángulos (`L:83–87`). |
| Historia de callback | `static old_origin[33]`, old_maxspeed, last_maxspeed_change y descenso en PreThink; `static old_angle[33]` en PostThink (`L:333–336,1314–1331`). Los temporales `origin[3]`/`maxspeed` son static compartidos por invocaciones, no arrays por jugador. |
| Persistencia M | Tops `[JUMP_TYPES][10]` y mejor marca `[33][JUMP_TYPES]`: nombre/dirección/distancia/pre/max/strafes/sync (`M:146–162`, `K:29,72–92`). No almacena loss/gain por strafe ni la secuencia de todos los intentos. |

Otros globals son handles/caches de cvars, colores, sonidos, flags de presentación, menús y Tries (`M:11–192`; `L:81–147`, `B:89–157`, `C:93–159`, `A:89–155`, `W:75–141`). No constituyen señales físicas adicionales.

## 3. Arquitectura y callbacks

### 3.1 Relaciones entre módulos [V]

M provee preferencias, rankings, cvars, resets y sonidos; **no centraliza la captura de los cinco módulos**. Cada uno tiene su propia máquina de estados, PreThink/PostThink y arrays. J declara natives y forwards (`J:22–47`). M registra natives (`M:574–598`), crea los multiforwards `js_update_cvars`/`js_reset_jump` (`M:454–455`) y distribuye sonidos mediante `callfunc` (`M:457–473`). `EventCacheCvars` ejecuta el forward de actualización (`M:1416–1442`). No hay llamadas de L hacia la máquina de estados B/C/A/W.

La captura/segmentación/acumulación y gran parte de HUD, consola, sonidos y beams están **duplicadas**, no extraídas a un único servicio. El cálculo de distancia/bordes y las validaciones auxiliares sí están compartidos como stocks de include: cada plugin incorpora su uso, no son natives de M. El orden entre plugins no se fija en estos archivos; no reconstruir un orden total de callbacks de L/B/C/A/W a partir de su nombre.

### 3.2 Índice de públicos de los módulos [V]

Cada celda da la línea inicial de la función en su ruta abreviada; los cuerpos llegan hasta el siguiente público, salvo notas finales.

| Público | L | B | C | A | W |
|---|---:|---:|---:|---:|---:|
| `plugin_precache` | 149 | 159 | 161 | 157 | 143 |
| `plugin_init` | 154 | 164 | 166 | 162 | 148 |
| `js_load_sounds` | 211 | 237 | 237 | 221 | 201 |
| `js_update_cvars` | 216 | 242 | 242 | 226 | 206 |
| `client_putinserver` | 257 | 285 | 284 | 268 | 245 |
| `client_disconnect` | 265 | 293 | 292 | 276 | 253 |
| `FwdPlayerSpawn` | 271 | 299 | 298 | 282 | 259 |
| `FwdPlayerDeath` | 283 | 312 | 311 | 295 | 272 |
| `js_reset_jump` | 288 | 317 | 316 | 300 | 277 |
| `FwdTouch` | 293 | 325 | 321 | 305 | 282 |
| `client_PreThink` | 314 | 346 | 342 | 326 | 303 |
| `TaskResetJump` | 1297 | 1409 | 1457 | 1378 | 1234 |
| `client_PostThink` | 1302 | 1414 | 1462 | 1383 | 1239 |
| `TaskRemovePreStrafeScript` | 1438 | 1550 | 1612 | 1519 | 1375 |

Spawn/Killed son hooks Ham **post** (`L:161–162` y respectivos `plugin_init`); FM_Touch se registra sin post (`L:164`). PreThink/PostThink son forwards de engine por nombre, no `register_forward(FM_PlayerPostThink,...,1)` en estos módulos. M registra contactos específicos (`M:414–422`) y comandos de reset leídos de configuración (`M:424`, `S:73–97`).

### 3.3 Públicos de M [V]

Inventario completo, agrupado para no confundir presentación con captura:

- Ciclo/config: `plugin_precache:194`, `plugin_init:314`, `TaskDelayedConfig:503`, `plugin_end:567`, `plugin_natives:574`, `FwdCacheCvars:1406`, `EventCacheCvars:1416`.
- Natives: `_colorchat:600`, `_sounds:605`, `_jumpstats:611`, `_strafestats:616`, `_beam:621`, `_specstats:626`, `_prestrafe:631`, `_dirhud:636`, `_blockdist:641`, `_edgedist:646`, `_check_top:651`, `_check_best:665`, `_get_top:679`, `_get_top_num:701`, `_get_weapons_allow:721`, `_get_weapons_chat:726`, `_get_weapons_sound:731`.
- Clientes/reglas: `client_authorized:736`, `client_putinserver:794`, `client_disconnect:821`, `FwdPlayerSpawn:1282`, `FwdPlayerDeath:1295`, `TaskCheckCvars:2029`, `QueryCvar:2041`.
- Resets/lecturas: `FwdResetJump:1306`, `FwdResetJumpDoor:1311`, `FwdResetJumpBCM3:1316`, `FwdResetJumpBCM5:1327`, `CmdResetJump:1341`, `FwdSpeedometer:1346`, `TaskDoSpeed:1353`, `server_frame:1378`.
- Comandos: `CmdReset:836`, `CmdTop:851`, `CmdMenu:1200`, `CmdVersion:1217`, `CmdUpdateCvars:1222`, `CmdAddWeapon:1233`.
- Menús/ordenación: `CallbackTopMain:858`, `MenuTopMain:897`, `SortPositions:992`, `MenuReset:1006`, `CallbackResetTops:1027`, `MenuResetTops:1057`, `CallbackResetBest:1128`, `MenuResetBest:1167`, `MenuMain:1455`, `MenuOnOff:1528`, `MenuAdmin:1586`, `MenuCustomize:1778`, `MenuAllowTeam:1832`, `MenuWeapon:1881`, `MenuTech:1922`, `MenuAgree:1982`, `MenuTop:2136`, `MenuMOTD:2219` (condicional), `MenuBestMain:2303`, `CallbackDisabled:2366`, `MenuBestView:2371`, `MenuBestReset:2488`.

Helpers internos relevantes de M: `ResetJump:1300–1304`, `LoadTops:2536–2575`, `SaveTops:2577–2596`, `CheckTop:2598–2696`, `GetTopPos:2698–2714`, `LoadBest:2716–2745`, `SaveBest:2818–2836`, `CheckBest:2838–2865`. No añaden fórmulas de vuelo a las métricas recibidas.

### 3.4 Helpers compartidos y fase de API

**[V]** S define: colores `18–71`; registro reset `73–97`; archivos `99–118`; dirección `120–146` y nombre `148–158`; equipos `160–197`; técnica `199–202`; ángulo entre vectores `204–228`; espectador `230–248`; duck `250–258`; suelo `260–263`; aterrizaje `268–289`; fallo `292–308`; límite de arma `310–399`; escape MOTD `401–430`; armas `432–439`; bordes `450–804`; helpers geométricos `GetBoxHitPos:820–870`, `GetPlane:872–892`, beam de prueba `894–916`.

**[D]** Como control externo se consultó AMXX oficial: `modules/engine/forwards.cpp`, funciones `PlayerPreThink` y `PlayerPostThink_Post`. El segundo ejecuta el forward de scripts desde la ruta post; el primero desde PreThink. Consulta de documentación mediante Context7 y fuente enlazada al final. No identifica la versión AMXX que compiló/ejecutaría este material.

**[I]** Es razonable distinguir el muestreo normal PreThink como previo y PostThink como posterior al movimiento del ciclo. **No se demuestra aquí una pareja por ID de comando ni una reproducción de física**: el plugin no captura `usercmd`, `msec`, número de comando o timestep. Además, llamar manualmente `client_PreThink` desde PostThink hace que ese cuerpo lea datos **posteriores**, pese a llamarse PreThink. El orden local de esa llamada sí está probado; la relación exacta entre dos comandos de red no.

## 4. Cronología de captura

### 4.1 Recorrido LongJump [V]

| Etapa | Lectura/cambio exacto | Función y líneas L |
|---|---|---|
| Preparación | Alive; calcula `on_ground`; consume sospecha touch; lee origin/velocity, maxspeed, gravedad, postura, arma y AA. Aplica filtros. | `client_PreThink:314–372` |
| Historia de suelo | Al final, incrementa `g_ground_frames` si grounded, o lo pone en cero si aéreo, salvo reentrada marcada; guarda `g_on_ground`, origen y límite de arma. | `1282–1295` |
| Nuevo intento | `on_ground && IN_JUMP && !old_IN_JUMP`, con **contador previo >=20**. Guarda posición/tiempo/arma, pre XY; inicializa max y old_speed con pre; borra ambos grupos, giros, sync y filas. | `432–505` |
| Primer PostThink aéreo | Actualiza yaw previo y teclas; si no grounded, detecta segmento y acumula speed, max, sync/gain/loss. No espera a la primera captura aérea PreThink. | `1302–1401` |
| Primera captura aérea PreThink | Con `g_jumped`, primer origen/velocidad pasan a `g_start_*`. En llamadas posteriores reemplaza `g_land_*`. | `374–430` |
| Último punto aún apto | Si altura ajustada por postura alcanza Z de salida, conserva origen/velocidad/postura para fórmula de fallo; se deja de renovar cuando ya es demasiado bajo. | `376–386` |
| Aterrizaje/fallo | Transición `on_ground && !g_on_ground` o failstats, con salto activo; limpia activo/primer frame y calcula candidatos si pasa tiempo/altura. | `508–538,590–724` |
| Reentrada final | Si PostThink ve grounded, salto activo y suelo previo falso: marca `g_post_think=true` y llama PreThink. Ese cuerpo puede finalizar con lecturas post; no vuelve a sumar contador de suelo. | `1308–1312,1287–1294` |
| Presentación | Ventana de distancia y preferencias; sync redondeado; mejor marca solo si no fallo/no script/límite arma 250; HUD/consola/filas/bordes; tops/sonidos según gates. | `726–1142` |
| Limpieza | Resetea agregados/filas/beam; tarea independiente puede solicitar reset posteriormente. | `1260–1300` |

**Muestras distintas:** pre inicial es una lectura del origen/velocidad durante detección grounded, no velocidad ideal ni máximo de carrera. Las parejas `g_start_*`/`g_land_*` proceden del cuerpo PreThink durante vuelo; los incrementos de velocidad proceden del cuerpo PostThink. No sustituir una por otra en una ecuación.

### 4.2 Grounded y postura no son solo botones [V]

`IsUserOnGround` prueba **cualquier bit** de `FL_ONGROUND2` (`S:260–263`), cuya máscara es `FL_ONGROUND|FL_PARTIALGROUND|FL_INWATER|FL_CONVEYOR|FL_FLOAT` (`K:32`). No es equivalente literal a FL_ONGROUND. El filtro de `waterlevel>0` es otra condición, separada.

`IsUserDucking` lee absmin/absmax y devuelve `!((absmin.z+64)<absmax.z)` (`S:250–258`): altura de caja <=64. No lee IN_DUCK ni simplemente FL_DUCKING. IN_DUCK y esta postura pueden producir condiciones distintas; B usa ambos explícitamente (`B:513–535`).

### 4.3 Acumulación fuera del intento y fin de muestra [V/I]

El gate PostThink es vivo, equipo permitido y `!g_failstats` (`L:1304`); el de acumulación es únicamente `!on_ground` (`L:1335`). Los equivalentes están en `B:1416,1447`, `C:1464,1495`, `A:1385,1416`, `W:1241,1272`. **No exige** `g_jumped`, `g_bhopped` ni MOVETYPE_WALK. [I] Puede acumular mientras cae sin intento, en aproximaciones DD/ladder y después de resets; el reset de inicio evita arrastrar ordinariamente esos totales al nuevo intento, pero no hay un registro continuo limpio de intentos.

Una muestra que ya observa suelo **no entra** a la acumulación aérea Exolent. Puede disparar finalización por reentrada antes de actualizar yaw y antes del bloque `!on_ground`. La velocidad de impacto/rozamiento de esa muestra no entra como loss final. En un fallo aéreo, la llamada que activa y procesa el fallo es PreThink; el siguiente PostThink puede volver a acumular si el bloque final ya limpió `g_failstats`. No interpretar esos nuevos contadores como parte del resultado ya publicado.

## 5. Segmentación de strafes

### 5.1 Pseudocódigo fiel [V]

La misma estructura está en `L:1314–1400`, `B:1426–1512`, `C:1474–1560`, `A:1395–1481`, `W:1251–1337`. Los resets de inicio de cada tipo están en §8.

```text
# Tras el gate de PostThink y eventual llamada manual a PreThink:
angles = pev_angles
right = false; left = false
if yaw < old_angle[player]: right = true
else if yaw > old_angle[player]: left = true
old_angle[player] = yaw
button = pev_button

if not on_ground:
    speed = sqrt(vx*vx + vy*vy)
    if left or right:
        if not aw and (W or A) and not D and not S:
            aw = true; sd = false
            strafes = strafes + 1
            if 0 < strafes <= 20: max_strafe[strafes-1] = speed
        else if not sd and (S or D) and not A and not W:
            aw = false; sd = true
            strafes = strafes + 1
            if 0 < strafes <= 20: max_strafe[strafes-1] = speed

    if maxspeed < speed: maxspeed = speed
    if old_speed < speed:
        good_sync += 1
        if 0 < strafes <= 20:
            good_strafe[strafes-1] += 1
            gained[strafes-1] += speed-old_speed
    else if old_speed > speed:
        if 0 < strafes <= 20: lost[strafes-1] += old_speed-speed
    sync_frames += 1
    if 0 < strafes <= 20:
        frames[strafes-1] += 1
        if max_strafe[strafes-1] < speed:
            max_strafe[strafes-1] = speed
    old_speed = speed
```

Es pseudocódigo de medición, no código del entrenador ni simulación. Las comparaciones encadenadas se conservan como intervalos Pawn; no se reinterpretan con semántica C de booleano intermedio.

### 5.2 Consecuencias que cambian el resultado [V/I]

- **No hay fin por soltar teclas o dejar de girar.** El grupo queda activo hasta reconocer el opuesto o reinicializar. Todos los frames posteriores siguen asignados al último segmento dentro del rango.
- **Cambio de tecla no basta:** A→D sin cambio numérico de yaw no abre strafe. Si luego hay giro manteniendo D, puede abrirlo entonces; no exige un flanco D nuevo.
- **Cambio de signo de giro no basta:** con A constante, invertir mouse no abre otro AW. El signo solo produce `left || right`.
- **Combinaciones:** W, A, W+A son AW; S, D, S+D son SD. A+D, W+S, W+D y A+S no cumplen ningún grupo; tampoco combinaciones mayores que contengan ambos grupos. No limpian el anterior. A→W y S→D no separan segmentos.
- **Neutralidad:** sin teclas no abre segmento aunque gire; sigue contando sync global y, si existe, la fila anterior. «Sin movimiento» debe distinguir sin teclas de velocidad cero: con teclas y yaw cambiado puede abrir segmento aun con speed=0.
- **Primer strafe:** no existe slot 0 de acumulación especial; la primera fila usa índice 0 cuando `strafes=1`. Antes de reconocerla, solo se acumula globalmente. El delta del frame que abre el segmento pertenece ya a la nueva fila, aunque su baseline sea de antes de ese segmento.
- **Duración mínima:** no hay debounce, mínimo de frames, mínimo delta angular ni filtro por magnitud. Alternancias elegibles de un solo frame cuentan. Dos cambios dentro de una única observación no se recuperan.
- **Último strafe:** no se cierra con timestamp: deja de recibir muestras cuando no se ejecuta el bloque aéreo o se limpia el intento. No hay duración temporal por fila.
- **Yaw:** se lee `pev_angles[1]`, no raw mouse ni `pev_v_angle`. No normaliza ±180°. +179→−179 da `right=true` por comparación numérica. Como solo se usa la disyunción, el signo errado no invierte el gate, pero impide usarlo como desync circular correcto. `old_angle` sí se actualiza; no tiene seed específico en inicio de salto (`L:1314–1331`).
- **Capacidad:** `++g_strafes` ocurre aun superando 20. Se protegen escrituras/acumuladores por fila, no el contador; el global continúa. La presentación recorre `i<g_strafes` sin cap (`L:872–903`, `B:986–1017`, `C:1029–1060`, `A:940–971`, `W:803–834`). [I] Con 21 filas reconocidas puede acceder fuera de arrays al publicar, no un truncamiento seguro a 20. El resultado runtime depende del build/checks y de que alcance la salida.

## 6. Fórmulas de estadísticas

### 6.1 Velocidad, gain, loss, sync y tiempo [V]

Sea `P` pre inicial, `s_k` speed de la muestra aérea admitida k, `s_0=P` al inicializar, `Δ_k=s_k−old_speed`. Las fórmulas se aplican al estado del intento correctamente iniciado; el gate amplio de §4 sigue siendo una limitación.

| Métrica | Fórmula/variables | Productor, muestras, denominador y precisión |
|---|---|---|
| Velocidad horizontal | `sqrt(vx²+vy²)` | PostThink `L:1337–1339`; copias B/C/A/W citadas en §5. Sin Z, sin redondear para acumular; unidades/s. |
| Prestrafe | `P=sqrt(vx²+vy²)` | L `456–458`; B `616`; C `685`; A LadderBhop `541`, LadderJump `659`; W `484`. Snapshot del inicio **específico** de §8; no máximo de carrera. |
| Máximo global | `M=max(P,s_1,…,s_n)` | Inicialización anterior; actualización L `1365–1368`. Conserva pico, no sobrescribe por mera recuperación. No incorpora muestra final grounded. |
| Máximo por strafe | Inicializa con speed del frame que lo abre; luego `M_j=max(M_j,s_k)` | L `1348–1360,1390–1397`. No incorpora pre como máximo de la fila; empieza en la muestra ya procesada. |
| Gained por strafe | `G_j=Σ max(Δ_k,0)` de frames asignados | L `1370–1378`. Incluye recuperación bajo M y delta de apertura; solo con índice válido. No necesita teclas/giro para sumar. |
| Lost por strafe | `L_j=Σ max(−Δ_k,0)` | L `1380–1385`, positivo acumulado; igualdad aporta cero. Misma asignación, no una prueba de colisión o desync. |
| Balance neto derivable | `G_j−L_j=ΣΔ_k` de esa fila | **[I]** Identidad aritmética sobre muestras asignadas, no campo publicado aquí. No confundir con velocidad final menos inicial de todo el salto si se omiten muestras previas al primer strafe. |
| Mejora de pico publicada | `M−P` | L `819–825`; B `933–939`; C `982–988`; A `887–893`; W `750–756`. No suma de positivos ni balance neto. Presenta `%.3f` en paréntesis. |
| Sync global | `floatround(100*good_sync/sync_frames)` | L `728`; B `842`; C `873`; A `796`; W `663`. Numerador: `Δ>0`; denominador: **todos** los frames del bloque aéreo; sin ponderación por duración ni guarda local si N=0. |
| Sync por fila | `floatround(100*good_j/frames_j)` | L `883–900` y salida equivalente §5. Misma comparación; N_j solo desde primera fila válida. Igualdad suma N, no good. Sin guarda de cero explícita. Tabla solo se emite si strafes>1. |
| Cantidad | Incrementos de AW/SD reconocidos | No cantidad de giros ni pulsaciones individuales; no se limita el valor a 20. L `1341–1363`. |
| Duración interna | `T=get_gametime_fin−g_jump_start` | L `450,534`; B `606,771`; C `677,821`; A `539/657,728`; W `482,611`. Se usa en aceptación; no se presenta como duración ni se almacena por fila. Fin = callback de cierre, incluido fallo sin aterrizaje. |
| Altura | **No hay métrica de ápice/altura máxima publicada** | Hay Z de referencias, control de descenso y trazas de HJ, no `max(Z)−Z_start`. `height` de L `1146` es el plano del beam, no altura de salto. |

El cálculo de ratios usa Float y `floatround` sin método explícito; el default de AMXX es `floatround_round`, no truncamiento entero UQ. El native oficial aplica al modo por defecto `floor(value+0.5)`; esto describe ratios no negativos normales, no sanea NaN/división por cero. Distancia/speed permanecen Float; `%f` y `%.3f` son presentación, no resolución física certificada. No hay tolerancia epsilon en comparaciones de speed.

**Ejemplo diferenciador [I]:** pre y máximo inicial 300, un segmento ya activo, muestras 290 y 295: gained=5, lost=10, balance=−5, máximo global=300, mejora de pico=0, máximo de esa fila según su historia (puede ser 300), sync de esas dos muestras=50%. La recuperación 290→295 cuenta como good aunque no supere el récord. Si además se cuenta una muestra 300 igual a su baseline, son tres muestras y sync redondeado=33%, no 50%.

### 6.2 Aterrizaje exitoso: helper exacto [V]

`S:265–289` acredita las cuentas a SchlumPF, NumB y eDark; es atribución del archivo, no verificación de los originales. Para `CalculateLandOrigin(ducking,g,current_origin,O[2],V[2],land_origin)`:

```text
t = (-sqrt(V0.z² + 2*g*(O0.z-current_origin.z)) - V1.z) / (-g)
V1.x = abs(V1.x); V1.y = abs(V1.y)  # también modifica estos argumentos
dx = t*V1.x; dy = t*V1.y
land.x = O1.x + dx si O1.x < current.x; si no, O1.x - dx
land.y = O1.y + dy si O1.y < current.y; si no, O1.y - dy
si ducking: current_origin.z += 18   # modifica el array del llamador
land.z = current_origin.z
```

`O0/V0`: primera muestra PreThink aérea activa; `O1/V1`: posteriores muestras aéreas, última conservada antes de cerrar (`L:406–428`). No se deducen de una integración de todos los comandos. `t` es una corrección temporal del helper, **no** el `T` total medido para validación. Gravedad pasada: `GRAVITY=800.0`, validada además contra cvar (`K:13`, `L:360,607`).

No hay guardas internas para radicando negativo, g=0, t negativo o muestras no inicializadas. En este uso g no es cero, pero eso no valida los demás supuestos. El helper infiere dirección XY por comparación de posiciones, no por signo de velocidad; en igualdad resta.

El llamador prepara copias locales de V/O y calcula `D=min(norm3(J−observado),norm3(J−estimado))+32` (`L:599–623`; B `804–830`; C `835–861`; A `753–779`; W `625–651`). **Detalles por módulo:**

- L usa `origin`, que el helper ya puede haber ajustado +18 en Z, como candidato observado; `origin2` se había preparado para el gate de altura (`L:515–537,607–616`).
- B/C/A/W usan `origin2` normalizado, y antes de medir fijan `J.z=origin2.z` (`B:814–818`, `C:845–849`, `A:763–767`, `W:635–639`). No es permiso para aplicar esa asignación a L.
- `get_distance_f` es norma 3D: no se aplana Z en la expresión. Condiciones de altura frecuentemente igualan referencias; eso no cambia la fórmula literal a una XY universal.
- LadderJump resta `EXTRA_DISTANCE/2=16` después de bordes (`A:789–792`), tanto si la distancia vino del helper de éxito como del de fallo. LadderBhop no resta.

No es suma de trayectoria, un integrador de speed, certificado de contacto inicial ni modelo de snap de KZ-Rush.

**Dirección de salto [V]:** `GetDirection` (`S:120–146`) usa `pev_v_angle`, genera forward, elimina Z, normaliza y multiplica por 250. Compara ese vector con velocidad en dos dimensiones mediante `acos(dot/(norm1*norm2))`, en grados (`S:204–228`). Si producto de normas=0 lo reemplaza por 1; no limita el coseno a [−1,1]. Clasifica sideways si `45.5<=angle<120`, backwards si `134.5<=angle<=180`, y forwards en cualquier otro caso, incluido el hueco 120..134.5. No es el yaw usado en segmentación ni un error angular ideal; tampoco hay razón para reemplazar sus intervalos por cuadrantes simétricos.

### 6.3 Fallo: fórmula completa disponible solo para Exolent [V]

`S:GetFailedDistance:292–308`, con J salida, F última posición elegible, U su velocidad, V velocidad **actual** al procesar fallo:

```text
si failed_ducking: J.z -= 18
t = (-sqrt(U.z² - 2*(-g)*(F.z-J.z)) - U.z) / (-g)
E.x = abs(F.x-J.x) + abs(V.x*t)
E.y = abs(F.y-J.y) + abs(V.y*t)
D = vector_length(E) + 32
si failed_ducking: J.z += 18
return D
```

`E` es el `static Float:land_origin[3]` del helper; **E.z no recibe asignación en ese cuerpo** (`S:294–303`). No se reescribe aquí como una norma XY explícita: [I] con su inicialización estática a cero y sin otra escritura en ese ámbito, el tercer componente permanece cero. El helper ajusta/restaura J.z en el camino ordinario, a diferencia de `GetEdgeDistances`.

Combina velocidad vertical **guardada** para t con velocidad horizontal **actual**, no únicamente la guardada. Los valores absolutos suman magnitudes por eje y no conservan una inversión de dirección como desplazamiento firmado. [I] Puede sobreestimar avance en un recorrido que revierta un eje respecto de su dirección previa; la magnitud real requiere pruebas. No comprueba radicando, signo de t, destino, soporte ni colisiones. No devuelve una posición de contacto real.

L llama en `593`; B `798`; C `829`; A `747`; W `619`. El origen enviado luego a bordes/beams **no es E**: L usa `origin` actual (`L:595`); B/C/A/W usan `origin2`, reemplazado por el snapshot de fallo (`B:766–800`, `C:816–831`, `A:723–749`, `W:606–621`). Por tanto, no exigir que distancia escalar y extremo visual coincidan en fallos.

### 6.4 Jump Edge, Land Edge y Block [V]

`GetEdgeDistances` (`S:450–804`) devuelve booleano de bloque aceptado y escribe tres resultados; no invalida por sí solo la distancia del salto. Estado inicial: jump/land edge=−1, block=−1.

1. Modifica J.z restando 36 y fuerza landing.z=J.z (`458–459`). Si `bJumpEntity`, retorna 0 con `ENTITY_EDGES_WORK` **sin definir** (`441–469`). `USE_FAKE_JUMP_ENTITY` sí está definido, pero su rama está anidada dentro de la opción deshabilitada: no se debe describir como activa.
2. Punto medio XY; Z una unidad por debajo de esas referencias. Si no es CONTENTS_EMPTY, retorna 0 (`472–482`). Usa HULL_HEAD si duck o fallo, HULL_HUMAN en otro caso (`484–487`).
3. Rama activa sin soporte de entidad: TraceHull desde medio hacia J; requiere normal vertical en el sentido `normal.z==0` y cara alineada exactamente a X o Y. La distancia de salida es `abs(hit_axis−J_axis)`, salvo LadderJump; resta `HLBSP_EXTRA=0.03125` (`645–681`, `K:70`).
4. Éxito: TraceHull desde medio hacia landing (`744–755`). Fallo: prolonga hasta 300 unidades por el eje de la normal de salida; obtiene cara de llegada; ajusta punto 16.1 hacia la superficie y Z+37, sube también medio +37 y exige trace libre (`683–741`). Son búsquedas restringidas, no un destino declarado por el jugador.
5. `land_edge=abs(hit_land_axis−landing_axis)−0.03125`. `fBlock=abs(hit_jump_axis−hit_land_axis)`; para LadderJump usa J como hit_jump (`757–781`).
6. En no-ladder suma 32 a fBlock en la rama activa sin entidad; la alternativa de entidad sumaría 17 pero está bloqueada por el retorno anterior. Ladder no añade offset de bloque. `block=floatround(fBlock)`; retorno 1 solo si block queda dentro de tabla: 210..280 para todos salvo LadderJump 120..220 (`783–803`, `K:160–178`).

No hay fórmula de «last» ni déficit escalar publicada. Land edge se oculta en fallos (`L:864–866,943–950`). El booleano de bloque no es un certificado universal de salto exitoso. Pueden conservarse resultados parciales aunque una rama posterior retorne 0; la salida prueba edges>=0 independientemente de block_jump (`L:855–869`).

**Efecto lateral importante [V/I]:** los arrays Pawn se pasan al helper sin copia protectora. No restaura J.z/landing.z ni en retornos tempranos ni al final. En un recorrido que llega a `S:487`, ambos quedan a altura inicial de J−37; en uno que retorna antes, J ya fue reducido 36. Se invoca antes de guardar extremo final/mostrar beams (`L:721–724,773–775,1146`). [I] El beam horizontal puede usar un plano desplazado por ese efecto, aunque D escalar ya estuviera calculada. Las llamadas B/C/A/W usan igualmente arrays reales. No «arreglar» mentalmente el helper ni presentar esos orígenes como snapshots inmutables.

## 7. Aterrizajes y validación

### 7.1 Qué activa un resultado [V]

No hay selección explícita de un bloque objetivo. La transición de grounded, según la máscara amplia, cierra el vuelo activo; alternativamente puede cerrar como fallo sin tocar el suelo.

- Mientras vuela, `origin.z+18 < J.z` marca failstats, incluso si no está duck. El snapshot se actualiza solo cuando `(duck?origin.z+18:origin.z)>=J.z` (`L:374–386`; B `407–419`; C `408–420`; A `399–411`; W `365–377`). Son umbrales diferentes: puede haber un intervalo sin renovación antes de activar fallo.
- Al cerrar sin fallo previo, normaliza aterrizaje con +18 si duck y marca fallo si queda por debajo de J; B admite margen de 2 (`L:515–526`, `B:752–763`, `C:802–813`, `A:709–720`, `W:592–603`).
- Solo calcula/presenta tras pasar ventanas de T y altura; una distancia fuera de cvar min/max no se publica. Los límites configurables de distancia no son una prueba de alcanzar el bloque.

### 7.2 Ventanas exactas de aceptación [V]

Intervalos **abiertos**, no aproximaciones redondeadas. Las condiciones de técnica, entorno y preferencias siguen aplicando.

| Familia | Condición de tiempo/altura | Cita |
|---|---|---|
| LJ/HJ, C y W | Fallo: `0.710<T<0.790`. Éxito: altura normalizada exactamente igual a salida; duck `0.718<T<0.790`; de pie `0.650<T<0.689`. | L `534–538`, C `821–824`, W `611–614` |
| B con noslow | Mismos intervalos de fallo; éxito con `abs(Zfin−Zbhop)<2` y ventanas duck/de pie como LJ. | B `773–779` |
| B sin noslow, normal | Fallo `0.620<T<0.710`; éxito altura diff<2 y duck `0.590<T<0.700` **o**, con springjump, `0.610<T<0.710`; de pie `0.540<T<0.610`. | B `780–791` |
| B sin noslow, drop | Fallo `0.640<T<0.740`; éxito altura diff<2, duck `0.650<T<0.750`; de pie `0.610<T<0.690`. | B `780–791` |
| LadderBhop | Fallo ventana LJ; éxito igualdad Z y ventanas duck/de pie LJ. | A `728–742` |
| LadderJump | Además referencia encontrada y `last_ladder_height<origin.z`; fallo `0.700<T<1.100`; éxito igualdad Z y `0.650<T<1.000`. | A `730–742` |

Ventanas de **distancia por defecto**, inclusivas y configurables: LJ/HJ 215..270 (`L:184–194`); B normal/standup 205..265, drop/standup-drop 210..270 (`B:194–216`); todas las C 225..280 (`C:196–218`); LadderJump 140..195, LadderBhop 225..280 (`A:192–202`); W 225..280 (`W:178–182`). Son gates de publicación distintos de la tabla de tamaño de bloque de K y de los tiers good/pro/leet: no describen el alcance físico mínimo/máximo de cada técnica.

### 7.3 Invalidaciones y estados especiales [V]

Filtros comunes de PreThink (`L:351–372`, `B:383–405`, `C:379–406`, `A:370–397`, `W:340–363`): reset pendiente; equipo/arma no permitidos; movetype no admitido; cambio de pev_maxspeed; discrepancia con `GetClientWeaponMaxspeed`; gravedad del jugador distinta de 1; waterlevel>0; salto espacial entre orígenes mayor que 20 (B:24); cvar gravedad distinta de 800; AA entero distinto de 10 y 100. Ladder permite WALK/FLY con prohibición de FLY en determinadas fases activas (`A:373–374`).

`IsTeamAllowed` no es simplemente un bit: si el equipo no está habilitado, solo devuelve false si encuentra un vivo de otro equipo (`S:160–197`). `GetClientWeaponMaxspeed` puede incluso escribir maxspeed si detecta VIP (`S:384–395`); no es un getter puro. No atribuir estas decisiones a técnica del jugador.

Otros caminos:

- **Pared/surf:** FM_Touch marca `g_bCheckSurf` para jugadores que la máscara considera aéreos. El siguiente PreThink pide reset si sigue aéreo y el suelo anterior también era falso (`L:293–330` y equivalentes). No exige normal, pérdida de velocidad ni pared concreta; el comentario reconoce que puede resetear un roce inocuo. No es detección física demostrada de surfing.
- **Trayectoria vertical:** una vez detectado descenso, una muestra posterior no descendente pide reset; también incremento Z>280 (`L:418–428` y equivalentes). No calcula altura máxima; puede rechazar contactos o discontinuidades sin diagnóstico causal.
- **Entidades/teleport/boost:** M propaga resets por train, puertas, conveyors, rotating, trigger_push/teleport y blockmakers (`M:414–424,1300–1344`). B ignora específicamente `func_door=true` en `js_reset_jump` (`B:317–323`); los otros cuatro no lo ignoran. `server_frame` busca teleports blockmaker y fuerza cinco cvars (`M:1378–1404`, valores `M:82–98`). **Ejecutar el plugin sí modificaría el entorno; aquí no se ejecutó.**
- **Duck:** postura de caja y botón son señales diferentes. Hay restricciones específicas de comienzo B/W/C, y ajustes de Z y ventanas temporales al cerrar; no hay contador induck.
- **IN_LEFT/IN_RIGHT:** marca SCRIPT_PRESTRAFE/SCRIPT_AIRSTRAFE con reglas de estado y tareas propias (`L:1403–1443`, `B:1515–1555`, `C:1563–1617`, `A:1484–1524`, `W:1340–1380`). Son botones de giro, no los bits A/D. Etiqueta «Script!» no prueba automatización; bloquea marcas/colores aun si se muestran estadísticas.
- **Timeout:** tareas de 0.8 L/C/W/LadderBhop, 0.7 B, 1.0 LadderJump solo ponen `g_reset=true` (`L:505,1297–1300`; B `722,1409–1412`; C `757,1457–1460`; A `627,691,1378–1381`; W `570,1234–1237`). La limpieza se difiere a PreThink.

### 7.4 Válido, fallido, inválido e incompleto [V/I]

| Categoría conceptual | Qué permite afirmar este código |
|---|---|
| Aceptado sin fallo | Pasó sus filtros, cerró en suelo y pasó altura/tiempo/distancia. Puede participar en ranking con requisitos adicionales. No prueba aterrizaje en el destino pretendido. |
| Aceptado como Failed | Alcanzó el camino de fallo y pasó sus ventanas; calcula distancia estimada y puede mostrarla. No requiere tocar un bloque destino. No equivale a «faltaron D unidades». |
| Invalidado/suprimido | Reset o filtro descarta estado o impide salida; script puede permitir HUD pero impedir ranking. No existe una salida exhaustiva de motivo por intento. |
| Incompleto | Vida/estado/timeouts pueden terminar el seguimiento sin resultado; no hay objeto persistente separado que conserve «intento incompleto». [I] Ausencia de stats no permite distinguirlo de filtrado, preferencias u otros resets. |

Exolent separa mejor el booleano failstats de ciertos resets que una única etiqueta universal, pero **no ofrece una taxonomía histórica completa de esos cuatro casos**. Comparar solo tops sesga contra fallos e invalidados (`M:2577–2596,2818–2864`; gates por ejemplo `L:726–732,1001–1011`).

## 8. Diferencias entre tipos de salto

### 8.1 Máquina de estado y comienzo de medición [V]

| Módulo | Estado previo y disparador | Pre/start y diferencias |
|---|---|---|
| LongJump / HighJump | Nuevo jump grounded con >=20 observaciones previas de suelo (`L:435–437`). | Pre/posición/tiempo en ese press (`446–482`). HJ se decide al cerrar con trazas, no porque mida otro ápice. |
| Bhop / Standup / Drop | Primer jump tras >=20 y `!g_jumped` arma historia, **no** el vuelo medido. En nuevo press grounded con contador<5 y g_jumped, rechaza IN_DUCK actual; normaliza Zbhop si postura duck (`B:490–535`). | Mide desde **segundo** despegue (`604–665`). Altura diff<2 normaliza Z a salida anterior; caída positiva <=200 clasifica drop; spring=postura duck o `0<now−last_duck<=0.125` (`535–581`). No medir desde primer J. |
| Count / Double / Multi / Drop Count | Secuencia Duck press grounded, release y posterior observación aérea de DD (`C:506–631`). Primer DD requiere historia de suelo o caída y condiciones de 574; repetición <20 grounded exige misma Z, con conversión drop especial (`574–625`). | Solo nuevo jump grounded con ducks>0, ground_frames<5 y Z exacta del último duck inicia medición (`632–685`). Ducks 1/2/otro→single/double/multi; drop solo single (`643–668`). Pre no es velocidad del primer DD. |
| LadderJump | Sin suelo, WALK después de FLY y oldbuttons sin Jump (`A:635–636`); no es un press grounded. | Guarda pre XY/origen/tiempo al detectar transición (`650–691`). Busca después suelo 150 debajo durante primeros <75 air_frames; cambia **solo J.z** a hit.z+36 y captura dirección (`456–480`). Exige referencia para aceptar; offset neto de distancia +16. |
| LadderBhop | >=50 ladder_frames y nuevo Jump aéreo arman ladderbhopped/fall_origin (`A:493–509`). Después nuevo Jump grounded, con caída<=200 (`518–539`). | Pre y reloj comienzan en ese jump de suelo (`541–627`), no en ladder. Offset +32 y ventanas LJ; contador de 5 expira estados (`484–488`). |
| WeirdJump | Sin suelo actual/anterior y old_ground_frames>=20, caída desde último origen de suelo >=16 arma fell (`W:409–423`). Se expira tras >=5 grounded; salir sin saltar resetea (`425–434`). | Nuevo jump grounded con fell y caída<=200; rechaza postura duck (`453–484`). Mide desde ese despegue posterior a caída, no desde borde original. |

**Matices que no deben simplificarse:**

- B limpia el estado de preparación si está en suelo sin bhop medido y contador>=5 (`B:465–468`); rechaza caídas/salida descendente en preparación (`478–487`). Rechazo de pre>=1.2*límite arma está **dentro** del gate pre>=`js_min_pre` (`B:618–649`); C, LadderBhop y W repiten esa estructura (`C:687–718`, `A:543–574`, `W:486–517`). Cambiar js_min_pre puede cambiar también alcance del rechazo, no solo HUD.
- C detecta caída con velocidad Z<0, sin DD en curso y old_ground_frames>=20 (`C:484–496`); drop-DD controla caída<=200 y solo un duck (`534–571`). La cadena no equivale a cualquier cantidad de pulsaciones IN_DUCK: exige las transiciones específicas y altura.
- El requisito **50 ladder frames** es visible para armar LadderBhop; la rama LadderJump `A:635` **no lo exige explícitamente**. No imponerlo por el comentario de K:22.
- LadderJump mantiene `g_jumped=false` (`A:667`) y `g_ladderjumped=true`; su PostThink reentra a PreThink solo si `g_jumped` (`A:1389`). [I] A diferencia de LadderBhop, su cierre grounded puede esperar al siguiente PreThink normal, con otro instante/origen observado. No asumir mismo endpoint temporal.
- B/C reentran al detectar suelo sin requerir salto activo (`B:1420–1424`, `C:1468–1472`); L/W requieren g_jumped, A también. El flag evita doble **conteo de suelo**, no todas las lecturas/efectos del cuerpo.

### 8.2 HighJump específico [V]

L calcula punto medio entre salida y origen final, fija Z a J.z−37 y exige contenido vacío. Traza hacia detrás de salida, requiere cara alineada a ejes, y desde un punto ajustado hace trace vertical de 70; fracción 1 arma HJ (`L:539–588`). En éxito comprueba cuatro esquinas ±16 bajo aterrizaje con trazas de 70 para evitar skywalk, y trazas laterales/verticales para descartar salto a lo largo de borde (`625–707`). Finalmente elige TYPE_HIGH/TYPE_LONG (`710–711`). No usa un umbral de ápice ni un salto más alto como definición suficiente.

### 8.3 Qué comparten y qué no [V/I]

Comparten literalmente el esquema de PostThink, max/gain/loss/sync, helpers de distancia y presentación muy parecida. Difieren en preparación, comienzo de reloj/pre, tolerancias de altura, tiempos de cierre, referencia vertical de ladder, gates de reentrada, reset de puertas y snapshot visual del fallo. La similitud del acumulador no hace equivalentes todos sus conjuntos de muestras.

## 9. Comparación Exolent / UQ / KZTimer / KZ-Rush

**Fuentes de contraste [D]:** [03](03-metrics-dictionary.md), [04](04-frame-analysis.md), [05](05-diagnostic-capabilities.md), [07](07-distance-and-landing-model.md), [08](08-kz-rush-binary-analysis.md), [09b](09b-kztimer-jumpstats-comparison.md). UQ 2.42 = fuente local allí auditada; KZTimer = `.sp` commit `fb7ed467f20f2909e55f2ca61707412d757240d2`, no cualquier versión. No se reinterpreta KZ-Rush con los algoritmos Exolent.

| Eje | Exolent [V] | UQ [D, auditoría de fuente] | KZTimer [D, auditoría de fuente] | KZ-Rush: documentación / binario / desconocido |
|---|---|---|---|---|
| Captura por frame | PreThink y PostThink independientes; no usercmd journal | PreThink/PostThink, marcadores opcionales | OnPlayerRunCmd y evento player_jump; helpers propios llamados Prethink/Postthink | [D] `/dt` por frame. [V de 08] fwCmdStart/get_uc y arrays debug. Uso y flujo efectivo no recuperados. |
| Fase de velocidad | Sync/gain/loss entre PostThink aéreos consecutivos; primer baseline=pre | Sync post frente a pre guardado; gain/loss entre pre elegibles | Speed de entidad entre callbacks; nombre Postthink no acredita fase post-física | Desconocida en build: no emparejar comandos por nombres. |
| Strafe | AW/SD con cualquier yaw cambiado; diagonales W+A/S+D admitidas; sin cierre neutral | Nueva tecla única + gate angular; old_angle1 sin update visible | AW/SD parecido; historial yaw actualizado | [D] botón/frames por strafe; [V de 08] calcStrafes/locales WSAD. Algoritmo pendiente. |
| Sync / efficiency | Good Δ>0; incluye sin teclas y antes de primer strafe; igualdad solo N | Requiere alguna tecla, excluye slot 0 de total; división entera | Good Δ>0 sin gate teclas; puede incluir callback ya grounded antes del cierre | [D] efficiency=frames positivos/frames del strafe. Exclusiones/fase/redondeo del binario desconocidos. |
| Gain/loss | Todos los Δ positivos/negativos asignados; M−P es mejora de pico | Gain solo nuevos récords globales; loss caídas pre | Todos los Δ+/Δ− por fila | [D] modos gain o balance limitado a cero según TXT; [V de 08] arrays gain/loss. Fórmulas operacionales sin recuperar. |
| MaxSpeed | Pico real inicializado con pre, compara M<speed | Pico pre-think activo | Global compara anterior<=actual, no M; puede perder un pico | [D] máxima horizontal; implementación del build desconocida. |
| Prestrafe | XY en inicio específico de cada tipo | XY en setup, variantes propias | Pre 3D; speed ordinaria XY | [D] modos pre/post; snapshot/fase del binario pendientes. |
| Distancia | min de normas 3D observada/estimada +32; LadderJump −16; fallo helper propio | min dos candidatos +32; ladder offset propio; helper fallo ausente | XY+32; sin corrección del último paso en recorrido auditado | [D] artículo snap/primer contacto; normalización HUD y algoritmo exacto pendientes. |
| Aterrizaje | Máscara amplia de flags; reentrada variable; helper balístico y traces de bordes | Flags, correcciones y LandingCalculate ausente | Grounded y refs de suelo/traces; registro manual de bloque | [D] snap y contacto parcial; no implementación certificada en binario. |
| Fallidos | Failstats por altura, proyección propia, no déficit al target | Flag failed sobrecargado; GetFailedDistance faltante | No estimador general de last demostrado | [D] last=shortfall; detalles de fallo omitidos por artículo de distancia. Algoritmo pendiente. |
| Historial | 20 filas, contador sin cap seguro; 120 puntos separados por distancia; tops/best selectivos | Beam 100 y marcadores opcionales limitados/mutables; tops | Arrays de strafe 100 con problemas de límites; mejores marcas SQL | [V de 08] arrays debug [33][500] y [33][50]; no prueba límite efectivo/export/retención. |
| Datos para diagnóstico | Agregados y path visual; no joint input/yaw/speed/timestamp completo | Parcial, con exclusiones/fases distintas | Agregados; no prueba all-attempt stream | [D] `/dt` promete gain/keys/dirección; contrato exacto del build y conservación desconocidos. |

Referencias precisas de otras fuentes: UQ `fwdPreThink:2892–2926,4252–4354,4553–4583`, `fwdPostThink:7801–7928` (03/04); KZTimer `OnPlayerRunCmd:580–659`, `CalcJumpMaxSpeed:663–668`, `CalcJumpSync:698–758`, `Prethink:1339–1396`, `Postthink:1406–1524` (09b). Son evidencia de esos productores, no equivalencias físicas.

### Separación estricta de KZ-Rush

1. **[D] Definiciones públicas:** efficiency por frames positivos; overlaps al final del strafe; desync por discrepancia dirección mouse/tecla; jof/land/last; artículos de distancia y pre. Respaldos y límites en `08:220–250`, `07:141–150`.
2. **[V, resultado estructural de 08] Símbolos:** `cmdDetailed C=95108`, `fwCmdStart C=99728`, `calcStrafes C=182596`; `g_flFrameGain`, `g_iFrameWSAD`, `g_iFrameDirection`, `g_iFrameStrafe`, `g_flStrafeEfficiency`, `g_iStrafeOverlaps`, `g_iStrafeDesync` y `g_flStrafeAngle` (`08:99–108,149–173`). Direcciones/nombres no son expresiones ni llamadas demostradas.
3. **Desconocido:** segmentación real, fase y definición de gain, atribución de frames, denominadores efectivos, tratamiento de sin teclas/igualdad/wrap, límites, último frame y persistencia. **Exolent no llena ninguno de esos huecos.**

## 10. Casos de prueba conceptuales

Predicciones **[I] derivadas de ramas [V]**, no resultados ejecutados. Salvo indicación, se presupone intento inicializado, callback aéreo admitido, índice dentro de capacidad y ausencia de invalidaciones. Cada caso debe especificar baseline y estado AW/SD; una lista de teclas aislada no basta.

| Caso mínimo | Predicción Exolent | Qué no se concluye sin ejecución/evidencia adicional |
|---|---|---|
| Pre=300; 290→295, mismo segmento | Gain 5, loss 10, global M=300, mejora pico 0, sync de esos dos frames=50%. | Que el motor produzca esa secuencia con determinada entrada; la historia de max de fila debe fijarse. |
| Speed aumenta sin W/A/S/D | Good global. Si hay fila previa válida, también good/gain de esa fila; si no, no hay fila. | Causa del aumento, técnica correcta ni sync mouse/tecla. |
| A→D, yaw constante, AW activo | No crea fila SD; delta y frame siguen en AW. Con giro posterior y D sostenida puede abrir SD. | Si las lecturas angulares reales quedan exactamente iguales o intervienen otros efectos. |
| Giro invierte sentido con A constante | No crea nuevo AW si ya está activo; sí puede crear primera fila si no había grupo. | Si `pev_angles` representa raw mouse; no lo mide. |
| A+D simultáneos, existe fila | No cambia grupo ni lo borra; acumula good/flat/loss según speed en fila anterior. | Aceleración física resultante de bits opuestos. |
| W+A simultáneos, yaw cambia | Abre AW si no estaba AW; si ya estaba, continúa. | Que equivalga a un strafe lateral puro. |
| Sin teclas ni giro | No abre strafe; aumenta N global y N de fila previa; Δ decide good/gain/loss. | Si hubo movimiento físico o si el jugador quiso un intervalo neutral. |
| Speed constante | N++ y N_j++ si fila; good sin cambio, gain/loss cero. | Ausencia de aceleraciones compensadas dentro del paso. |
| Primer strafe después de dos frames sin grupo | Los dos frames solo afectan global; apertura incluye inmediatamente el delta respecto de la muestra anterior en fila 1. | Equivalencia entre total global y suma de filas; no tienen iguales muestras. |
| Un strafe dura un solo frame | Cuenta y puede tener sync 0 o 100 y Δ completo. Si es el único strafe, no se emite tabla de filas. | Si supera las demás condiciones para publicar el intento. |
| +179°→−179°, grupo opuesto elegible | right=true; cambio de grupo permitido; sin normalización circular. | Giro físico corto/largo ni desync real a partir de ese signo. |
| Aterriza en muestra final PostThink | No añade N ni loss aéreo de ese PostThink; puede llamar PreThink para cerrar antes de actualizar yaw. | Contacto inicial subframe o último rozamiento; LadderJump tiene reentrada distinta. |
| No alcanza el bloque y desciende | Puede activar failstats y estimar D si T/distancia/entorno pasan; no necesita contacto con destino. Si no pasa, puede no mostrar resultado. | Déficit exacto al bloque, causa del fallo o mismo resultado para un destino lateral distinto. |
| Strafe 21 elegible | Contador=21; no escribe fila 21 durante captura, pero salida intenta leerla si publica. | Error exacto del runtime/si llega a esa salida. |
| Roce aéreo sin pérdida | Touch puede pedir reset en próximo PreThink si permanece aéreo con historia aérea. | Que haya surfing o error técnico del jugador. |
| Salida desde entidad con origen no nulo | Helper de bordes retorna 0 después de modificar J.z/landing.z; distancia ya calculada permanece. | Artefacto visual exacto sin ejecutar trazas/HUD. |

Estos casos distinguen las **reglas** de medición, no predicen resultados físicos para UQ/KZTimer/KZ-Rush. Los contrastes de §9 son solo los ya respaldados por sus fuentes.

## 11. Implicaciones para KZ Coach

### 11.1 Algoritmos observados [V]

Exolent da un ejemplo completo de snapshots de inicio/fin, acumulación asimétrica de muestras globales/filas, clasificación histórica por técnica y dos rutas de distancia (aterrizaje/fallo). La fórmula de fallo es ahora legible **en Exolent**. La separación de máximo, suma positiva y pérdida demuestra que un nombre de columna no basta para definir una métrica.

### 11.2 Limitaciones o posibles defectos [V/I]

| Evidencia | Impacto potencial, sin reparación |
|---|---|
| `last_maxspeed_change > gametime+0.7` (`L:440`, B `495/521`, C `525/637`, A `498/529/638`, W `414/472`) | Con tiempo monótono y timestamp guardado en pasado, no implementa espera de 0.7 s. No documentarlo como debounce correcto; un rewind de reloj sería otro escenario. |
| Goto por touch antes de leer origin/maxspeed (`L:320–340`), epílogo los usa (`1284–1285`); estructura repetida B/C/A/W | Temporales static compartidos pueden retener una invocación anterior, incluso otro jugador, y contaminar baseline de siguiente validación. El reset siguiente no convierte la lectura omitida en fresca. |
| Contador sin cap y salida sin límite (§5) | Posible error de límites con más de 20 strafes; buffers de texto de 512 agregan truncamiento de presentación. |
| Cocientes sin N>0 y helpers sin validación numérica (§6) | No asumir resultado definido para vuelo sin muestras o entradas geométricas degeneradas; secuencia admitida real debe probarse. |
| GetEdgeDistances cambia arrays y no restaura (§6.4) | Ref de salida/beam deja de ser origen original; partial results y retornos tempranos importan. |
| Tareas usan ID cliente para reset y retiro de script (`L:505,1412,1431–1433`) y no se cancelan sistemáticamente al finalizar/desconectar (`L:265–269,1260–1279`) | `remove_task(client)` puede cancelar otra función con mismo ID dentro del módulo; un timeout previo puede afectar un intento posterior. [H] Requiere traza temporal para demostrar un caso concreto; no se presupone aislamiento entre nombres de tarea. |
| Sumas PostThink sin salto activo (§4.3) y cierre grounded sin muestra aérea final | No hay un conjunto universal de frames que pueda llamarse «todo el salto» sin definir fases y resets. |
| `GetFailedDistance` magnitudes por eje y velocidad actual (§6.3) | No prueba trayectoria/contacto; las inversiones y movimientos especiales exigen validación independiente. |
| Ranking de distancias iguales: `CheckTop` rechaza solo anterior>nueva, pero busca posición con distancia estrictamente menor (`M:2653–2688`) | [I] Puede escoger una posición posterior o mantener newpos=−1 si no hay valor menor; no asumir estabilidad/seguridad del empate. Hallazgo secundario, no modifica fórmulas de vuelo. |

No se afirma que todo caso sea alcanzable bajo configuración normal ni que un plugin compilado concreto falle exactamente de una manera; se distingue la condición visible de su manifestación runtime.

### 11.3 Ideas conceptuales transferibles [I], sin arquitectura definitiva

1. **Captura:** conservar señales y fase de procedencia antes de elegir una métrica; las filas y beams no permiten reconstruir entradas conjuntas ni cada pérdida. Snapshot de intento y datos usados por un helper no deberían confundirse conceptualmente con el mismo registro inmutable.
2. **Modelo temporal:** separar inicio de preparación, despegue medido, primera muestra aérea, primera colisión, observación grounded y cierre. Reentrada de una función no cambia el momento de sus lecturas.
3. **Métricas:** nombrar por separado porcentaje de muestras positivas, gain acumulado, loss, balance y mejora de pico. Registrar pertenencia, baseline, denominador, rounding y tratamiento de neutralidad.
4. **Errores y explicaciones:** «perdiste 10 y recuperaste 5» es más fiel que «no aceleraste porque no superaste tu máximo». «No hubo aumento en X muestras» no equivale a «cambiaste tarde el mouse».
5. **Intentos comparables:** seleccionar contexto constante de técnica, arma/física, postura, fase y destino. Un Failed estimado puede compararse solo con referencias compatibles, no presentarse como aterrizaje real.
6. **Resultados:** separar observación, validez y resultado respecto del target. Guardar solo récords impide estudiar recurrencia e intentos fallidos sin sesgo; Exolent no demuestra que ese dataset ya exista.

### 11.4 Hipótesis para pruebas posteriores [H]

- Cuánto altera la distancia el helper balístico respecto del primer contacto real en snap, duck y aterrizaje parcial.
- Si los efectos laterales de bordes explican un beam desplazado en mapas representativos.
- Qué diferencias observables introduce el cierre tardío de LadderJump y qué resets anteriores alcanzan intentos nuevos.
- Si una captura autorizada permite correlacionar de forma inequívoca entradas y física por comando. Estos archivos no conservan esa evidencia.

No se propone copiar AW/SD, thresholds, filtros de «Script» ni helpers geométricos como estándares del entrenador; se extraen preguntas y contratos de evidencia, no una arquitectura.

## 12. Limitaciones y preguntas abiertas

- Investigación estática: no se comprobó compilación, reachability completa, orden de otros plugins, exactitud física, compatibilidad con una versión AMXX instalada ni resultado real de traces.
- Los seis originales están presentes; los includes propios esenciales también. Los includes de UQ siguen faltando: **no son intercambiables con S/K/J** aunque aparezcan fórmulas parecidas.
- El 403 impide autenticar adjuntos del hilo, versión editorial y licencia. Identidad local queda fijada por hashes, no por una afirmación de release auténtica.
- No se inspeccionó la física exacta del motor/servidor ni se equiparó `pev_angles` con raw mouse. La consulta AMXX externa confirma un contrato actual, no el build histórico.
- No se comprobó disponibilidad de datos en demos ni export lossless. El HUD no es prueba de persistencia; el buffer visual no es una cronología de comandos.
- Las preguntas abiertas de KZ-Rush sobre gain, overlaps, desync, angle y `/dt` siguen abiertas. La similitud Exolent/KZTimer no demuestra descendencia ni licencia compartida.

**Reproducción de inventario:** `wc -l reference/jumpstats*.sma`, `sha256sum reference/jumpstats*.sma` y los includes enumerados en §2; lectura numerada sin normalizar bytes. Se verificaron las fórmulas siguiendo productores, consumidores, resets y todos los módulos, no solo búsquedas de nombres. CodeGraph no estaba disponible: el intento de inicialización falló con `exec: "codegraph": executable file not found in $PATH`; se usó lectura directa, sin instalarlo.

## 13. Recomendación para la siguiente fase

**Mantener el plan AMX v8 de 09 sin cambiar decoder, ISA, funciones objetivo ni criterios de validación.** [I] Si la meta es entender exactamente KZ-Rush, el análisis de Exolent no reemplaza evidencia del binario. Autorizar por separado la implementación del lector mínimo sigue siendo un paso pendiente, no realizado aquí.

Lo que sí cambia es la precisión de las preguntas de interpretación:

- ¿Gain compara consecutivas, nuevas marcas o pre/post, y cuál es su baseline inicial?
- ¿El denominador incluye igualdad, ausencia de teclas, frames antes del primer strafe y muestra grounded final?
- ¿Se segmenta por tecla, grupo, giro, flanco o combinación, y qué pasa con estados conflictivos persistentes?
- ¿Se preservan pico, referencias originales y límites efectivos, o existen sobrescrituras/efectos laterales?
- ¿La distancia fallida, el punto visual y el déficit al destino son datos distintos?

No usar Exolent como fixture binario AMX ni validar el decoder por producir fórmulas parecidas. Primero bytes/opcodes/targets; después flujo y datos; recién entonces comparación con casos conceptuales y documentación pública. Si el objetivo futuro fuera solo definir métricas propias, se podría evitar reproducir cada plugin, **a costa de perder comparabilidad exacta con KZ-Rush**; eso no se decide en esta investigación.

### Fuentes externas consultadas y referencias

- Hilo Exolent: <https://forums.alliedmods.net/showthread.php?t=87906> — 403, sin inspección de adjuntos originales.
- AMXX oficial, revisión de referencia ya fijada en 09: <https://github.com/alliedmodders/amxmodx/tree/8fc12670ea86470a0bfed4c35db5de73d3a39e8a>. Consulta adicional de texto actual: <https://github.com/alliedmodders/amxmodx/blob/master/modules/engine/forwards.cpp> (`PlayerPreThink`, `PlayerPostThink_Post`), <https://github.com/alliedmodders/amxmodx/blob/master/plugins/include/float.inc> (`floatround`), <https://github.com/alliedmodders/amxmodx/blob/master/amxmodx/float.cpp> (implementación de redondeo). `master` no identifica el entorno histórico de Exolent.
- Documentación KZ-Rush, interpretada con límites de 07/08/09b: <https://kz-rush.ru/en/article/kz-rush-lj-stats>, <https://kz-rush.ru/en/page/calculating-distance>. En esta fase se reutilizaron las lecturas documentadas, sin recuperar algoritmos nuevos de KZ-Rush.
- [09 — ruta de lector AMX](09-amx-disassembler-research.md), [09b — comparación KZTimer](09b-kztimer-jumpstats-comparison.md), [03 — diccionario UQ](03-metrics-dictionary.md), [04 — frames UQ](04-frame-analysis.md), [05 — límites diagnósticos](05-diagnostic-capabilities.md), [07 — geometría](07-distance-and-landing-model.md), [08 — binario KZ-Rush](08-kz-rush-binary-analysis.md).

## Key Learnings:

1. Exolent distingue suma positiva, pérdida y mejora del pico; su sync sigue siendo un contador de aumentos de speed, no coordinación mouse–teclado.
2. Tener todos los helpers revela las fórmulas de Exolent y sus efectos laterales, pero no recupera dependencias UQ ni instrucciones KZ-Rush.
3. Las fases, gates, grupos persistentes y referencias de cada tipo son parte de la métrica. Un coach necesita conservar esa distinción antes de atribuir un fallo a habilidad.

**No realizado:** ejecución/compilación de plugins, instalación de dependencias, cambios en fuentes originales, UQ/KZ-Rush, LAN o implementación del entrenador/desensamblador. **Riesgo pendiente:** confundir una predicción estática o estimación geométrica con un resultado físico y un diagnóstico causal validados.
