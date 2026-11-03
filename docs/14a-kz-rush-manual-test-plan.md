# KZ-Rush: guía para una futura sesión manual

Fase 4D.1 · 2026-11-03 · **plan no autorizado para ejecución actual**.
Base técnica y direcciones C: [auditoría 14](14-kz-rush-observability-audit.md).

Etiquetas: **[V]** bytes/archivos originales; **[D]** fuente documental identificada; **[I]** inferencia; **[H]** hipótesis pendiente. Ninguna etiqueta indica una observación de gameplay realizada en esta fase.

## 1. Antes de considerar jugar

**No iniciar el servidor, conectarse, activar cvars ni probar saltos ahora.** Esta guía describe qué hacer únicamente después de una autorización posterior que identifique destino, operador/sesión y acciones. No autoriza preparar una instalación ni modificar `reference/`.

**[V] Riesgo:** el plugin llama a `setTop` y puede reescribir tops durante resultados normales, EB o JB (C267960/290880/297524 → C329436). Además guarda configuración al inicializarse (C46772 → C47208). Apagar HUD, chat o `/dt` **no** demuestra que deje de guardar récords.

### Lista de preparación segura, pendiente de autorización

- [ ] Usar una copia experimental aislada, nunca LAN original por defecto.
- [ ] Operador confirma que configs, `amxx_datadir/ljtop`, módulos y demás plugins no comparten datos ni sincronización con producción; comprobar también posibles bases externas de otros plugins.
- [ ] Propietario de datos autoriza sesión y copias; respaldo y recuperación de la copia experimental verificados. No probar una restauración sobre el servidor original.
- [ ] Registrar versión/hash del plugin, mapa, AMXX/módulos/JIT y cliente. Hash esperado del `.amxx`: `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e`.
- [ ] Imagen descomprimida esperada: `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433`. Si no coincide, detener comparaciones con estos informes.
- [ ] Obtener configuración efectiva **sin asignar valores** mediante operador autorizado; no deducirla de defaults del informe.
- [ ] Identificar canales disponibles y restricciones localhost. Los ajustes no son necesariamente accesibles a un jugador LAN remoto aunque sea administrador.
- [ ] Probar la captura local, desconectado, sólo bajo la autorización futura; comprobar ruta de archivos, espacio y privacidad. No cambiar `server.cfg`.
- [ ] Mantener arma, mapa/punto/superficie/altura, física, FPS, parámetros de red, receptor y opciones constantes por bloque.
- [ ] Acordar parada inmediata si hay riesgo para datos originales o configuración inesperada.

Si algún punto de aislamiento queda sin demostrar, **no realizar la sesión**. No basta con prometer saltos cortos ni con que el servidor sea «sólo LAN».

## 2. Identificar qué se puede mostrar

| Elemento | Qué significa | Precaución |
|---|---|---|
| `/dt` o `/detailed` | [V] Alterna detalle futuro por jugador; init0; C95108–95376 | No consulta historial; ejecutarlo otra vez lo desactiva. Registrar aviso exacto enabled/disabled. |
| Consola de strafes | [V] Requiere `ljs_strafes_console` y puertas de presentación | Default1 no garantiza valor efectivo1. |
| `[DETAILED]` | [V] Cabecera de detalle por frame | Puede seguir `Too much info to show` si >15 strafes o >300 frames. |
| Columnas | [V] Gain/loss, frames y métrica seleccionada | Conservar cabecera y modo. No asumir efficiency/overlaps/desync/angle simultáneos. |
| `ljs_strafes_real_gain` | [V]0 muestra neto no negativo; no0 gain bruto | No sumar décimas impresas como si fueran Float exactos. |
| `ljs_strafes_full_overlap` | [V] Cambia exportación dentro de calcStrafes | **No cambiarla** como si fuera un ajuste sólo visual. |
| Última columna | [V] Render contiene0 efficiency,1 overlaps,2 desync,3 angle | Límite de cvar sugiere máximo2. No forzar3; registrar si la opción realmente es accesible. |
| Diagnóstico `[PRE]` | [V] Existe ruta consola C154064 | `ljs_pre_console` default0; si no está habilitado, no activarlo en LAN para completar esta guía. |
| HUD pre completo/corto | [V] Selección del receptor y cvars de familia | Completo conserva más precisión; corto no expone p* directamente. |
| `/ljtop` y variantes | [V] Consulta tops almacenados | No es archivo de todos los intentos ni reemplazo del detalle. |
| `/lj`, `/stats`, menús y `/savelj` | [V] Incluyen ajustes/guardado, no meras consultas personales | No usarlos para «leer sin cambiar». `/savelj` escribe cfg. |

Si `/dt` o los canales necesarios no están disponibles bajo el permiso concedido, registrar el bloqueo y posponer ese objetivo. No usar RCON, cambiar cvars, instalar instrumentación o parchear el plugin como solución improvisada.

## 3. Captura local propuesta

**[I] Preferencia:** consola completa + captura del HUD por intento + ficha externa de identificación. Una demo es apoyo contextual, no garantía de preservar toda la consola ni los estados internos.

Sólo en una sesión posteriormente autorizada:

1. Verificar soporte de la build del cliente antes de usar comandos. Captura del SO/Steam evita depender de un comando de motor no comprobado.
2. **[D/H]** `record nombre` / `stop` se documentan para CS1.6 en la fuente D4 del informe14. Usar nombre único, por ejemplo `kzr_s01_e01_b01`, únicamente si se confirmó soporte. Comprobar el `.dem` local en la ruta efectiva; no prometer captura de HUD/chat/consola completa.
3. **[D/H]** `condebug` / `-condebug` y `qconsole.log` tienen documentación comunitaria (D5), pero aquí no se verificaron ruta, estado inicial ni semántica de esa build. No alternarlo a ciegas ni dejar registro ilimitado; usarlo sólo si se verificó localmente cómo iniciarlo y detenerlo.
4. **[H]** `condump` y `snapshot` no están confirmados para el cliente elegido. No dependa de ellos: guardar imágenes del SO y copiar texto visible es el respaldo.
5. Marcar cada intento en notas externas. Un `echo` local es opcional sólo si está documentado/comprobado; nunca enviar marcadores al chat por defecto.
6. Guardar texto antes de que salga del scrollback; capturar HUD antes de que desaparezca. Si no se pudo, anotar «captura incompleta», no recrearlo desde memoria.
7. No usar `log on`, `exec`, `writecfg`, `rcon`, comandos de guardado del plugin ni cambios de física para registrar evidencia.

Los archivos son locales al cliente, pero pueden revelar nombres, SteamID, chat, IP o voz. Conservar originales privados y copias redactadas para compartir. Demos/logs/vídeo crecen; vigilar espacio. La carga de vídeo puede alterar FPS: no alternarla entre condiciones sin anotarlo.

## 4. Ficha de cada intento

Copiar esta plantilla en **notas externas de la futura sesión**; no rellenar cifras como si ya existieran resultados.

```text
ID: S01-E01-I001
Fecha/hora local y orden del intento:
Experimento / condición / repetición:
Build cliente / AMXX / módulos / plugin y mapa identificados:
Mapa / punto / superficie / alturas / arma:
FPS y parámetros de red/física conocidos, sin cambiarlos:
Jugador fuente / receptor (propio o espectador):
Canales y opciones efectivos; cómo se conocieron:
Aviso de /dt y estado esperado:
Acciones intentadas (no confundir intención con inputs del servidor):
Incidentes: contactos, duck, pausa, lag, caída de FPS, cambio de arma:
Consola completa: archivo y rango de líneas:
HUD/chat: archivos de imagen y contexto visible:
Demo/vídeo, si existe: nombre y intervalo relativo:
PRE íntegro, si aparece (conservar etiqueta, pre/post/max/FOG/fuser2):
Resumen principal y cabeceras:
Filas: tipo, gain/loss, frames, efficiency/overlap/desync/angle visibles:
Detalle por frame íntegro; advertencias o truncamientos:
Resultado: observado / no hubo salida / captura incompleta / bloqueado:
Interpretación compatible:
Explicaciones alternativas y dato faltante:
Comparación válida: sí/no, motivo:
Riesgo/incidente de persistencia y acción de parada:
```

Identificar imágenes como `S01-E01-I001-hud`, `...-console-01`, `...-console-02`; no sobrescribir intentos. La hora local ayuda a ordenar, pero no identifica un callback del servidor. Incluir el periodo anterior al salto: PRE puede aparecer antes del resumen final. No emparejar dos líneas sólo porque contienen números parecidos.

## 5. Secuencia sugerida, sólo tras autorización

Los objetivos detallados, hipótesis, alternativas y falsación están en E1–E14 del [informe14 §8](14-kz-rush-observability-audit.md). Cada fila siguiente comparte preparación segura, constantes y riesgo de récords de §1. **No son instrucciones para ejecutar ahora.**

| Orden / experimento | Acción manual futura | Qué observar y guardar | Límite de interpretación |
|---|---|---|---|
| 1 — E1 normal | Salto sencillo, guardar antes de otro | aviso dt, principal, filas, detalle, HUD | silencio puede ser filtro, no ausencia de cálculo |
| 2 — E2 un strafe | Una tecla sostenida en aire | tipo, frames, efficiency, gain/loss y WSAD | tecla humana sostenida no fija número de callbacks |
| 3 — E7 gain/loss | Tramos de aceleración/desaceleración | signos del detalle, loss y cabecera bruto/neto | 0.0 no fija signo original; gain no prueba preBhop |
| 4 — E3 cambio | A→D manual; giro revertido en bloque separado | agrupaciones, tipo, giro, angle si accesible | historia y yaw exacto siguen ocultos |
| 5 — E4 dos teclas | Una combinación constante por bloque | máscaras multitecla, filas, efficiency | ausencia de fila puede ser full_overlap |
| 6 — E5 overlaps | Multitecla seguida de una tecla frente a cierre en multitecla | racha/contador y detalle completo | no contar todos los overlaps del intento como una suma |
| 7 — E6 desync | Giro habitual/contrario, sin cambiar sensibilidad | desync, gain/loss, giro, vídeo auxiliar | no es simplemente pérdida de velocidad |
| 8 — E10 aterrizaje | Tecla sostenida hasta después de llegar | fila terminal, jof/landing y detalle | no identifica bGround ni bad inequívocamente |
| 9 — E8 bhop | Bhop ordinario, historia anotada | PRE íntegro y HUD completo/corto, FOG | maniobra no garantiza llamada preBhop |
| 10 — E14 candidato de corrección | Catalogar líneas pre de E8, sin buscar extremos | post, max, etiqueta y contexto del mismo evento | bad y post≈0.8max sólo son compatibles con corrección |
| Opcional — E9 JB | Sólo técnica/área autorizada en copia aislada | jumpbug pre y avisos success/failure | post de formato JB es v, no p*; puede escribir top |
| Opcional — E12 inválido | Intento corto sin llegada prevista, sin órdenes de reset | Failed o silencio y siguiente base | Failed no identifica bad ni asegura no-persistencia |
| Separado — E13 opciones | Sólo cambios de presentación expresamente autorizados en copia | valores previos, aviso/menú/cabecera y bloque nuevo | no cambiar full_overlap; no comparar dos inputs humanos como idénticos |
| No controlado — E11 bad | Sólo catalogar incidentes, no forzar colisiones | resultado completo si aparece | prueba exacta requiere flag/instrumentación; no ejecutable con salida actual |

Usar bloques cortos preacordados y guardar todos los intentos, no sólo los «buenos». Cinco repeticiones pueden orientar una exploración, pero no constituyen potencia estadística ni reproducibilidad exacta. No usar macros, emuladores o plugins para obtener inputs idénticos.

## 6. Lectura rápida de PRE

**[V/D]** Todos estos significados son reconstrucción estática, todavía no observaciones de juego:

- `pre` = `g_flPreHorSpeed`, velocidad pre almacenada; **no es el p original** de la corrección.
- `jumpbug ... post` = velocidad actual v. Ese formato no incluye M.
- `good/minloss/bad ... post` = argumento de velocidad anterior que llega al formateador; es p* sólo si se ejecutó el write C168772.
- `max` = M local de preBhop; no asumir que sea Maxspeed del salto principal.
- Hay **dos rutas bad con el mismo texto**, una sin corrección y otra con corrección. Un valor post cercano a0.8max es un candidato, no prueba de la ruta.
- HUD completo no JB contiene p/p* a3 decimales; HUD corto contiene s y diferencia redondeada a0, no el p* directo.
- Consola pre usa buffer máximo79; guardar el texto tal como llegó, incluido truncamiento. No completar fuser2/max por intuición.

No es posible recuperar el p previo al write a partir de la etiqueta `pre`. Por ello la sesión puede contrastar valores visibles, pero no demostrar causalmente todas las condiciones de Fases4C/4D sin otra evidencia.

## 7. Cuándo invalidar una comparación

- Build/hash/mapa/arma/superficie/altura/opciones o receptor diferentes sin control explícito.
- Datos de canales distintos o columnas distintas tratados como la misma métrica.
- FPS/red/física cambiados, lag, pausas, contacto inesperado o salida de la zona de prueba.
- Activación dt no confirmada, `Too much info to show`, cabecera perdida, texto truncado o scrollback incompleto.
- Intentos mezclados, orden dudoso, PRE atribuido al salto equivocado, demo sin vínculo al ID.
- Sumar gains a una decimal para exigir igualdad exacta con acumulados; reconstruir GoodFrames sin tolerancia de redondeo.
- Tomar Failed como prueba de bad, silencio como reset, o vídeo como observación de `g_bCatGround`.
- Cambiar full_overlap durante un bloque: puede cambiar filas/conteo, no sólo aspecto.

Una comparación inválida se conserva con su motivo. No borrar ni repetir hasta producir el resultado deseado.

## 8. Parada y cierre seguro

En una sesión futura autorizada, detener las maniobras ante riesgo de escritura compartida, cambio inesperado de configuración/valores, error del plugin, pérdida de captura o aislamiento incierto. No intentar llegar a500 frames/50 strafes: detalle se corta antes y hay rutas de límite no verificadas en gameplay.

Guardar evidencia local; cerrar con `stop` **solamente** la demo que se haya iniciado. Detener el registro local sólo por su mecanismo previamente verificado. Salir del cliente de prueba sin órdenes de reset/guardado/cambio de mapa o servidor. No ejecutar `/savelj`, borrar tops, restaurar bases ni «deshacer» registros para ocultar resultados. Si se detecta una posible escritura, informar al operador con el ID y no reparar a ciegas.

**[I]** Dejar de saltar no revierte escrituras ya realizadas ni garantiza que el plugin no escriba al desconectar. La protección debe venir del aislamiento previo, no de una orden de parada. Cualquier restauración o cambio del servidor requiere otra autorización.

## 9. Criterio de cierre del bloque futuro

Entregar conteo de intentos/capturas completas/inválidas, archivos locales, opciones efectivas y cada observación con alternativas. Clasificar como compatible, incompatible bajo supuestos, o inconclusa; nunca «preBhop confirmado» sólo por gain positivo o bad.

La siguiente acción actual es **revisar este plan y resolver los datos faltantes**, no jugar. No se autoriza avanzar de fase ni implementar KZ Coach.
