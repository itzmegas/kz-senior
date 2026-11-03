# KZ-Rush: reconstrucción estática de contadores por frame

Fase 4B · 2026-11-03 · binario local identificado por SHA-256.
Resultado: reconstrucción del núcleo de `calcStrafes`, no implementación de KZ Coach ni reproducción ejecutable del plugin.

## 1. Resumen ejecutivo

**Se puede decidir qué modifica una llamada admitida a `calcStrafes` conociendo sus argumentos, las muestras anteriores/actuales y los acumuladores por dirección. Un frame descrito solamente por teclas, giro, velocidad y gain no basta: también se necesitan inicios por tecla, estado anterior, categorización de suelo, invalidación y límites.** La admisión completa del llamador todavía no está reconstruida.

Cinco resultados principales:

1. **[V] `iGainNum` es un índice de dirección, no una cantidad:** selecciona la tecla anterior activa cuyo inicio sea más temprano; empates favorecen W, S, A, D, en ese orden.
2. **[V] Denominador y numerador tienen atribución diferente:** todas las teclas anteriores activas reciben un frame; solamente la dirección seleccionada puede recibir un good frame, si `!bBadLastFrame && flGain > 0`.
3. **[V] Overlaps no acumula todos los solapamientos del segmento:** conserva una racha que se reinicia, en las cuatro direcciones, cuando la muestra anterior contiene como máximo una tecla.
4. **[V] Desync depende de velocidad y orientación anteriores, dirección seleccionada y giro actual/anterior.** No depende directamente del signo del gain; giro cero puede contar como desync.
5. **[V] El cierre es por dirección liberada, suelo categorizado o último frame inválido.** Un mismo frame puede entrar en varios denominadores y producir varias filas; gain/good/desync/ángulo se atribuyen a una sola dirección.

Las pruebas siguientes son estáticas: descompresión, lectura, decodificación y comparación de bytes. No se ejecutó el `.amxx`, una VM, compilador ni servidor. No se modificó `reference/`, configuración, récords ni almacenamiento de juego.

### Convenciones y fuentes de evidencia

| Marca | Significado |
|---|---|
| **[V]** | Verificado en instrucciones o código fuente identificado; no observación del juego. |
| **[D]** | Documentado por una fuente identificable; no demuestra identidad con el binario. |
| **[I]** | Consecuencia fundamentada, con supuestos explícitos. |
| **[H]** | Hipótesis pendiente; no base para una implementación fiel. |

Las direcciones son decimales. En adelante **CS** significa `calcStrafes`, C `[182596,192488)`. Su listado verificable es [`analysis/amx_disassembly/calcStrafes.txt`](../analysis/amx_disassembly/calcStrafes.txt); los ámbitos y dimensiones proceden de [`symbols.json`](../analysis/amx_disassembly/symbols.json). Los rangos citados son inclusivos para las instrucciones mencionadas, salvo intervalos `[inicio,fin)`. Confianza alta significa que operandos y ramas sustentan la regla local; no certifica sincronización física ni entradas de dominio excepcional.

## 2. Integridad del binario y del inspector

### Identidad y límites [V; confianza alta]

| Objeto | Resultado verificado |
|---|---|
| Original | `reference/kz_jump_stats.amxx`, 114387 bytes |
| SHA-256 original | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| Imagen descomprimida | 1684270 bytes; descomprimida en memoria, sin escribirla |
| SHA-256 imagen | `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |
| AMX | versión de archivo/VM 8, flags 2, definición 8 bytes |
| Código, coordenadas I | `[4912,337028)`; longitud 332116 |
| Datos inicializados, I | `[337028,1576260)`; longitud 1239232 |
| `hea=size`, `stp` | 1576260 y 1592644; no confundir cabecera relativa a imagen con direcciones D de ejecución |
| Debug | empieza en I=1576260; 1280 símbolos, 4473 líneas, 6 archivos; cola cero 31780 bytes |
| Decodificación global | 51250 instrucciones contiguas; destinos y ordinales nativos validados |
| Compatibilidad | Los artefactos existentes se reprodujeron byte por byte mediante `analyze(raw)` |

**[V]** `I = 4912 + C` para código; `I = 337028 + D` para datos inicializados. Ejemplos: C183584 → I188496; D808 → I337836. Los locales FRM son relativos al frame de stack, no posiciones de la imagen. Estas conversiones están comprobadas por `Header.c_to_i`/`d_to_i` y los bytes del listado, no por nombres.

**[V]** Las 27 pruebas de `tools.amx_inspector.test_inspector` pasaron. La ISA está fijada a AlliedModders/amxmodx `8fc12670ea86470a0bfed4c35db5de73d3a39e8a`, como documenta [10](10-amx-disassembly-validation.md). No fue necesario modificar el inspector.

### Nativas, comparaciones y locales [V; confianza alta]

La tabla de definiciones identifica `float` ordinal 0; `floatmul` 1 y 17; `floatdiv` 2 y 20; `floatcmp` 5. Los duplicados son entradas distintas con el mismo nombre, no ordinales intercambiables. En CS se usan 0, 17 y 20 para efficiency.

Se decodificaron además los cuerpos compilados: C756–852 convierte FRM+16 con `SYSREQ_C 0`, compara FRM+12 contra ese resultado con `SYSREQ_C 5`, y usa `SGRTR` contra cero; C1200–1296 hace lo mismo con `SLESS`. Las variantes Float/Float C684–752 y C1128–1196 llaman directamente `floatcmp`. Esto verifica operandos y sentido de `>`/`<`, no solamente los nombres debug. La implementación de las nativas en el módulo instalado y su tratamiento de NaN/división por cero no están contenidos en este AMXX.

| FRM | Ámbitos relevantes en CS | Interpretación segura |
|---|---|---|
| −36 | `i`: `[184420,186124)`, `[186128,186328)`; `iGainNum`: `[186332,192480)` | No llamar `iGainNum` a los primeros bucles. |
| −44 | `i`: `[186356,186692)`; `flCos`: `[187200,189132)`; bucles `[189268,189468)` y `[189480,189632)`; `bFinished`: `[189636,192480)` | El mismo offset no representa el mismo valor durante toda la función. |
| −48 | `iVelRight`: `[187244,189132)`; `i`: `[189648,191916)` | No interpretar el índice del cierre como velocidad. |
| −52 / −56 | `iTurnRight` / `flRightAngle`, hasta C189132 | No sobreviven semánticamente al bloque auxiliar. |

Se comprobó que no hay dos locales con la misma dirección base y ámbitos solapados dentro de CS. No es una prueba universal de ausencia de alias de memoria; sí resuelve la reutilización relevante de slots escalares.

### Reproducción sin ejecutar bytecode

Desde la raíz del repositorio, estas operaciones solamente leen y decodifican:

```python
from pathlib import Path
from tools.amx_inspector.inspector import (
    AMXX_SHA, AMX_SHA, Header, unpack_container, definitions,
    debug_info, decode, validate, analyze,
)
raw = Path("reference/kz_jump_stats.amxx").read_bytes()
image = unpack_container(raw, AMXX_SHA, AMX_SHA)
h = Header.parse(image)
code = image[h.cod:h.dat]
instructions = decode(code, 0, len(code))
validate(instructions, len(code), len(definitions(image, h)["natives"]))
for name, text in analyze(raw).items():
    p = Path("analysis/amx_disassembly") / name
    if p.exists():
        assert p.read_text() == text, name
# Ejemplo: inspección adicional, no evaluación de instrucciones.
for ins in instructions:
    if 211520 <= ins.c < 213536:
        print(ins.c, ins.spec.name, ins.operands)
```

Ejecutar Python con `PYTHONDONTWRITEBYTECODE=1`; prueba observada: `python3 -m unittest tools.amx_inspector.test_inspector -q`. Los auxiliares fuera de CS se inspeccionaron mediante esa API en memoria; no se publicaron nuevos listados completos ni se cambió la CLI.

## 3. Cronología de captura

**[V; alta]** `plugin_init` registra Ham PreThink en C13068 y Ham PostThink en C13136, ambos con parámetro `post=0`; `fwCmdStart` se registra en C13792 también como pre. «PostThink» identifica aquí la función del motor interceptada, no el parámetro post del registro Ham.

**[V; alta]** Las seis llamadas directas a CS encontradas en la decodificación global están en `hamPlayerPreThink`: C110880, 112240, 113728, 114252, 114580 y 115148. No hay llamada directa desde `fwCmdStart` ni desde `hamPlayerPostThink`. Esto no demuestra por sí solo ausencia de llamadas indirectas.

| Dato | Productor | Consumidor | Momento de captura | Dirección C | Evidencia | Incertidumbre |
|---|---|---|---|---|---|---|
| Duración del comando | `fwCmdStart` | historial de tiempo | CmdStart admitido; `get_uc` miembro 1, conversión/división por 1000 | 99728–100076; 99856, 99900 | [V] listado completo y llamadas | No identifica por sí sola una muestra física de CS. |
| Forward/side move | `fwCmdStart` | estado e historial | miembros 3 y 4 del comando | 99976, 100052 | [V] `get_uc` y stores | No son las teclas que usa directamente CS. |
| W/S/A/D actuales | `hamPlayerPreThink` | `new_WSAD` de CS | lectura actual de `pev`, selector 81 | 102252–102328; 182768–183152 | [V] `pev`, store a D327244 y máscaras | No son una captura directa de botones en CmdStart. |
| W/S/A/D anteriores | final de PreThink anterior admitido | `prev_WSAD`, denominadores, cierre | copia de botones antes de retornar del callback | 116016–116156; 183192–183576 | [V] D327508←327376←327244 | Un early return puede impedir avanzar historia. |
| Velocidad actual | PreThink | norma horizontal y `flGain` | selector `pev` 120 | 102336–102492 | [V] buffer D329500, llamada C4400 | No es velocidad deseada del comando. |
| Velocidad anterior | final de PreThink | norma anterior y auxiliares | copia D329500→330028; anterior→old D330556 | 116160–116364 | [V] llamadas de copia | No confundir `prev` con `old`. |
| `flHorSpeed` | PreThink, local −4 | argumento FRM+16 de CS | norma de velocidad actual | 102424–102492; llamadas citadas arriba | [V] `vector_hor_length` | Admisión del intento pendiente. |
| `flGain` | PreThink | CS, histórico y good/gain/loss | norma actual menos norma anterior | 110804–110880 y análogos | [V] `floatsub`, argumentos apilados | No es aceleración ideal ni necesariamente efecto aislado de una tecla. |
| Ángulos actual/anterior | PreThink y su cola | auxiliares de giro | `pev` selector 126; copia a anterior al terminar | 102752–102828; 116484–116580 | [V] D332140→332668 | `pev_angles`, no demostrado equivalente a todo movimiento de mouse. |
| `g_flFrameGain` | CS | detalle posterior | antes de incrementar frameCount | 183584–183684 | [V] acceso indexado desde D808, `STOR_I` | También se escribe en llamada marcada bad. |
| `g_iFrameWSAD` | CS | detalle posterior | botones anteriores, bits W=8,S=4,A=2,D=1 del formato propio | 183692–183972 | [V] shifts/OR, raíz D66940 | No confundir este empaquetado con máscaras del motor. |
| `g_iFrameDirection` | CS | detalle posterior | comparación yaw actual/anterior | 183980–184204 | [V] llamada C212488, raíz D133072 | Representación de giro, no entrada cruda del mouse. |
| `g_iFrameStrafe` | CS | detalle posterior | contador de filas antes de cerrar direcciones de esta llamada | 184212–184392 | [V] raíz D199204, count D324604; después `INC_I` frameCount | Una sola etiqueta histórica no describe todas las atribuciones simultáneas. |
| Suelo de CS | PreThink | resets/cierre | `g_bCatGround`, no flags sin más | 103344–103468; 107092–107368; 110772 y análogos | [V] flags 512 o ladder; categorización adicional | Falta expandir `isCategorized` y todas las rutas de admisión. |
| `bBadLastFrame` | PreThink, local −36 | good/gain/loss y cierre | seleccionado por rama del intento | stores 110692,111852,113340,113900,114452,114900 | [V] escrituras 1/0 y paso de argumento | No se ha reducido cada predicado de esas ramas a entradas físicas. |

**[I; media]** El patrón es comparar dos muestras PreThink admitidas, atribuyendo a botones anteriores la variación actual−anterior, y avanzar el historial al final. El binario del plugin no contiene el bucle físico del motor: no se afirma un orden total CmdStart→simulación→PreThink ni una correspondencia uno-a-uno con frames renderizados. `hamPlayerPostThink` C101404–101716 captura una altura cuando detecta transición de flags; no es el productor directo de estos contadores.

## 4. Modelo de estado por frame

**[V; alta]** Orden observado dentro de CS:

1. Validar capacidad (C182608–182728); construir cuatro booleanos nuevos y anteriores.
2. Escribir histórico en el índice frameCount y después incrementarlo (C183584–184392).
3. Si `!bGround`, inicializar direcciones previas del primer frame y detectar nuevas pulsaciones (C184396–186116).
4. Incrementar `Frames[i]` por cada `prev[i]` activo (C186128–186320).
5. Seleccionar `iGainNum` por inicio mínimo (C186332–186684).
6. Acumular gain/good o loss si no bad; después desync/ángulo si hay dirección seleccionada, incluso si bad (C186696–189124).
7. Actualizar overlaps (C189136–189624); evaluar cierres y emitir filas (C189636–191908).

Abreviaturas explicativas: `F/G/O/D/A` = Frames/GoodFrames/Overlaps/Desync/Angle; `P/N` = vectores anterior/nuevo; `q` = dirección seleccionada. No son variables nuevas del plugin.

### Inicialización y escrituras encontradas

| Acumulador por dirección | Raíz D | Reset de primer frame | Reset nueva pulsación | Actualización |
|---|---:|---|---|---|
| Frames | 266128 | CS184716–184792 | CS185524–185600 | `INC_I` C186304 por cada P[i] |
| GoodFrames | 268108 | CS184968–185044 | CS185776–185852 | `INC_I` C187020, solamente q |
| Overlaps | 268768 | CS185052–185128 | CS185860–185936 | `INC_I` C189444; ceros C189536–189612 |
| Desync | 269428 | CS185136–185212 | CS185944–186020 | ocho sitios `INC_I`: C187740,187888,188072,188220,188436,188616,188804,188984 |
| Angle | 270088 | CS185220–185296 | CS186028–186104 | `floatadd` C189100, store C189120 |

**[V; alta]** Ambos resets son condicionales: primer frame exige `!bGround && frameCount==1 && P[i]`; escribe `Start[i]=frameCount−1`. Nueva pulsación exige `!bGround && N[i] && !P[i]`; escribe `Start[i]=frameCount`. Cada uno pone a cero los siete acumuladores, incluidos gain y loss. **No existe un reset incondicional de todas las direcciones en cada frame aéreo.** Evidencia de puertas: C184396–184576 y C185304–185400.

**[V/I]** Fuera de CS se encontraron raíces de estos contadores en `resetVars`, C96996–97500; la rutina C96448 también pone frameCount/strafeCount a cero (C96768/96812). La búsqueda global por operandos es evidencia de esos accesos, no una prueba de exclusividad frente a alias, escrituras por rangos o llamadas indirectas. No se afirma inventario universal de escritores resuelto.

## 5. Significado exacto de `iGainNum`

**[V; alta]** C186332 inicializa `q=-1`; C186344 inicializa mínimo=500. Bucle i=0..3: requiere P[i]; carga Start[i]; `JSGEQ` salta si inicio≥mínimo; si menor, guarda i en q y el inicio en mínimo (C186396–186668). No consulta `flGain`, velocidad ni giro para elegir q.

| Valor | Condición exhaustiva local | Teclas/velocidad/giro | Ramas posteriores |
|---:|---|---|---|
| −1 | No hay P[i] con Start[i]<500 | Puede no haber teclas; también estado de inicios fuera de rango | Salta gain/good/loss y auxiliares mediante C186736/C187188. Denominadores y overlaps siguen sus propias reglas. |
| 0 | W anterior activa y gana el mínimo estricto | Puede estar sola o con cualquier combinación; independiente de velocidad/giro | Good/gain/loss W; desync por iVelRight; angle W. |
| 1 | S anterior activa y gana el mínimo; W no lo gana | Igual independencia; empate con W lo pierde | Rama C187904–188228. |
| 2 | A anterior activa y gana el mínimo; W/S no lo ganan | No significa «dos teclas» | Rama C188236–188624, compara flCos. |
| 3 | D anterior activa y gana el mínimo; W/S/A no lo ganan | No significa «tres frames con gain» | Rama residual C188632–188992, compara flCos. |

**[I]** Con inicios iguales gana el primer índice: W antes que S antes que A antes que D. Una tecla recién pulsada N no compite hasta figurar en P de una llamada posterior. Conocer solamente las teclas actuales no determina q.

## 6. Fórmula completa de efficiency y good frame

**[V; alta]** Para cada dirección i, desde su último reset local:

```text
F[i] aumenta en 1 si P[i] != 0.
G[i] aumenta en 1 si q == i y !bBadLastFrame y flGain > 0.
Efficiency de la fila emitida i = floatmul(100.0, floatdiv(float(G[i]), float(F[i]))).
```

Es una reconstrucción fiel de condiciones y orden de las nativas, no pseudocódigo de toda la función. Numerador y denominador son contadores de llamadas admitidas con esas condiciones, no gain acumulado ni aceleración óptima. Evidencia: C186184–186304; C186696–187028; conversiones C191264/C191368, división C191404, multiplicación C191444, store C191464.

| Pregunta | Respuesta sustentada por esas ramas |
|---|---|
| ¿Basta gain positivo? | No: debe existir q y el frame no ser bad. Solo q recibe el numerador. |
| ¿Tecla activa? | Sí, en P, no necesariamente en N. |
| ¿Exige acuerdo giro/tecla o velocidad determinada? | No en esta rama. Esas señales se evalúan después para desync. |
| ¿Pérdidas o igualdad? | Entran en F por tecla; no en G. Si elegible, `Loss[q] ← Loss[q] − flGain`, incluyendo cero. |
| ¿Sin giro? | No se excluye de G. |
| ¿Dos, tres o cuatro teclas? | Todas reciben denominador; como máximo una recibe numerador. |
| ¿Takeoff/landing? | No hay exclusión genérica por nombre de frame. Ground no impide esta acumulación; bad sí impide G, no F. La admisión decide qué llamada llega. |
| ¿F=0? | No hay guarda explícita junto a floatdiv. En una fila normal, P[i] y el incremento previo hacen F≥1; no se promete resultado para estado corrupto ni de la nativa ante cero. |
| ¿Diferencias W/A/S/D? | Misma regla local; diferente selección por antigüedad y desempate. |

**[V]** Cuando bad es verdadero, C186708 salta a C187168, no a la salida de auxiliares: no omite desync/angle. Confundir esos destinos cambiaría el modelo.

## 7. Algoritmo de overlaps

**[V; alta]** C189136–189240 suma los cuatro booleanos P. C189244 pone la suma en ALT; C189248 pone 1 en PRI; `JSGEQ` C189256 salta al reset si **1≥suma**. Si suma>1, C189324–189444 incrementa O[i] solamente para P[i] activa; si no, C189480–189612 recorre y limpia las cuatro direcciones.

```text
si sum(P) <= 1: O[0..3] = 0
si sum(P) > 1: para cada i con P[i], O[i] += 1
               para las demás direcciones, O[i] conserva su valor
```

Reconstrucción fiel del bloque local; no incluye resets anteriores. Cuenta muestras, no eventos de transición. Trata A+D, W+S, W+A, S+D y todas las otras combinaciones de al menos dos teclas por la misma prueba de cardinalidad, sin cancelar pares opuestos. El uso de P alinea la racha con el frame que acaba de atribuirse, mientras N decide liberaciones.

**[I]** Habitualmente representa la racha de solapamiento al final del strafe, no el total histórico. Si una dirección permanece inactiva durante otras muestras multi-tecla, su O no aumenta ni se borra en este bloque; por eso «racha» es una explicación condicionada al recorrido de esa dirección, no una definición universal por sí sola.

**[V; alta]** En cierre, `full_overlap!=0 || F[i]>O[i]` permite emitir (C190060 `LOAD_PRI D455416`; C190068 `JNZ`; C190228 `XCHG`, C190232 `SGRTR`). El cvar no cambia el incremento de overlaps ni el selector q: permite conservar segmentos completamente solapados. C190912–191080 copia el entero a `g_iStrafeOverlaps`. `showStrafes` C195080–211520 lo presenta como entero; no se reconstruyó una conversión porcentual.

## 8. Algoritmo de desync y ángulo

### Auxiliares compilados [V; confianza alta para aritmética finita]

Sean `(vx,vy)` los dos primeros componentes de **g_flPrevVelocity**, raíz D330028, y p el yaw **g_flPrevAngles[][1]**, raíz D332668. C211520–212024 carga esas raíces, no D330556 (`old`). Se pasan unidades angulares 1 a `floatcos`/`floatsin`, interpretadas como grados según el contrato AMXX.

| Variable | Reconstrucción | Función / instrucciones |
|---|---|---|
| `h` | `sqrt(vx*vx + vy*vy)` si suma>0; de lo contrario cero | `vector_hor_length`, C4400–4724; `floatmul`, `floatadd`, comparación C4652, `floatsqroot` C4688 |
| `flCos` | `(vx*cos(p) + vy*sin(p)) / h` | `calcVelocityCos`, C211520–212024; `floatmul` 211688/211872, `floatadd` 211908, longitud 211980, `floatdiv` 212008 |
| `iVelRight` | `sign(vx*sin(p) − vy*cos(p))` | `isVelocityOnRight`, C212028–212484; `floatsub` 212424, llamada sign C212468 |
| `sign(z)` | +1 si z>0; −1 si z<0; 0 si ninguno | C3096–3264; comparaciones C3144/C3220 y retornos |

El nombre `flCos` no demuestra idealidad de un ángulo; la fórmula es una proyección normalizada. Si h=0, el bytecode no contiene guarda antes de dividir. El resultado exacto depende del módulo nativo, pendiente; no se asigna un valor inventado.

Sean c yaw actual y p yaw anterior, pasados en ese orden a `isTurningRight` y `getRightAngle` desde CS187296–187572. Los cuerpos C212488–212976 y C212980–213532 tienen esta reconstrucción fiel por ramas:

| Condición, evaluada en orden | `iTurnRight` | `flRightAngle` |
|---|---:|---|
| c>90 y p<−90 | +1 | p+360−c |
| c<−90 y p>90 | −1 | p−(c+360) |
| Sin cruce anterior; c<p | +1 | p−c |
| Sin cruce anterior; c>p | −1 | p−c |
| Sin cruce anterior; c=p | 0 | 0 |

Celdas verificadas como Float: 1119092736=90.0, −1028390912=−90.0, 1135869952=360.0. Los umbrales son estrictos. No es un normalizador general para yaw arbitrariamente fuera de rango ni una garantía de giro corto para saltos de ángulo excepcionales. «Derecha» es el significado devuelto por esta función; la equivalencia física exige convención del motor.

### Condiciones exactas de incremento [V; confianza alta]

Definiciones: v=`iVelRight`, t=`iTurnRight`, f=`flCos`; q debe ser válido. Cada fila siguiente incrementa **D[q] una vez** si se cumple su disyunción:

| q / tecla | Condición | Rango CS y control |
|---|---|---|
| 0 / W | `(v>0 && t>=0) || (v<0 && t<=0)` | C187584–187896; tests con PRI=0, ALT=v/t; `JSGEQ`, `JSGRTR`, `JSLEQ`, `JSLESS`; increments 187740/187888 |
| 1 / S | `(v>0 && t<=0) || (v<0 && t>=0)` | C187904–188228; increments 188072/188220 |
| 2 / A | `(f>0 && t>=0) || (f<0 && t<=0)` | C188236–188624; llamadas C188304/C188484 a >/<; increments 188436/188616 |
| 3 / D | `(f>0 && t<=0) || (f<0 && t>=0)` | C188632–188992; llamadas C188672/C188852; increments 188804/188984 |

**[V/I]** Para W, v<0 y giro derecho t=+1 no incrementan; para S, sí. Con v>0 y giro izquierdo t=−1 ocurre la misma distinción W/S. A/D no prueban v: usan la proyección f. No puede resumirse esto en una regla universal «velocidad izquierda vs mouse derecho» ni «mouse contrario a tecla».

Con t=0, W/S incrementan si v≠0; A/D, si f tiene signo estricto. Con v=0, W/S no incrementan; eso no decide A/D. La velocidad lateral nula no implica velocidad horizontal nula. Con gain negativo, cero o frame bad, la misma tabla sigue siendo aplicable si q existe. Un cambio de giro no cierra por sí solo un segmento; puede cambiar esta clasificación dentro de la misma tecla.

**[V; alta]** C188996–189120 suma `flRightAngle` a A[q]. En el cierre se exporta `floatabs(A[i])`, no suma de magnitudes ni error respecto de un ángulo óptimo. **[I]** Giros opuestos pueden cancelarse antes del valor absoluto final. D se copia como entero a la fila (C191472–191640), no como porcentaje.

## 9. Segmentación y cierre

**[V; alta]** Para cada i=0..3, `bFinished` se pone a cero (C189704). El bloque C189716–190028 equivale a:

```text
finished[i] = P[i] && (bGround || bBadLastFrame || !N[i])
emit[i] = finished[i] && (full_overlap != 0 || F[i] > O[i])
```

Es simplificación booleana fiel de esas ramas, no de la admisión externa. La fila emitida usa `g_iStrafeCount` como índice, guarda type=i, F/gain/loss/O/efficiency/D/abs(A), y después incrementa count (C190276–191900).

| Situación | Resultado local |
|---|---|
| Nueva tecla aérea | Inicia su estado mediante N&&!P; el frame actual todavía se atribuye a P. |
| Cambio exclusivo A→D | A se contabiliza y cierra en esa llamada; D se inicializa, recibe muestras cuando llegue a P. |
| Se sueltan todas | Cada P activa puede cerrar; la muestra todavía no es «sin teclas» para los contadores. |
| Teclas simultáneas | Estados por tecla independientes; denominadores múltiples, selector q único. |
| Aterrizaje en transición | Ground omite inicializaciones aéreas y solicita cierre de cada P activa; el filtro overlap sigue aplicándose. |
| Último frame bad | F y overlaps se actualizan, G/gain/loss no; D/A sí si q válido; solicita cierres. |
| Cambio de giro solamente | No aparece en el predicado de cierre. |
| Frame sin P activa | No aumenta F, q normalmente −1 y limpia O; no cierra por tecla anterior. |

**[V/I]** La liberación evita reemitir esa tecla en la siguiente muestra ordinaria, porque P deja de incluirla. CS no deja una bandera persistente «ya emitido» ni limpia los acumuladores por el mero acto de emitir; otra llamada bad/ground con la misma P podría repetir el cierre. Probar que el llamador impide toda duplicación exige terminar su máquina de estados. No se promete deduplicación universal.

### Capacidad y orden de las filas

**[V; alta]** No interpretar `JSGRTR` por el nombre de la variable: C182636 mueve frameCount a ALT; C182640 pone 500 en PRI; C182648 continúa solamente si **500>frameCount**. En caso contrario retorna C182664. Igualmente C182700–182728 exige **50>strafeCount**. Por tanto rechaza igualdad al entrar, no solo valores superiores.

`BOUNDS 32/499/49/3` limita clientes, frame, filas y direcciones a 0..32/0..499/0..49/0..3 respectivamente. **[I]** Si una llamada entra con count=49 y emite varias direcciones, el segundo cierre puede alcanzar `BOUNDS 49` con índice 50: no hay una nueva guarda de capacidad entre direcciones. Esto es un camino local condicionado, no un fallo observado ni prueba de que la admisión lo haga alcanzable. No se afirma truncamiento silencioso; BOUNDS es una comprobación de VM.

## 10. Trazas manuales verificables

Son deducciones **[I]** de las ramas **[V]** anteriores, sin ejecutar el plugin ni un modelo emulado. Se suponen llamadas admitidas, capacidad disponible, buffers finitos válidos e historial coherente. Salvo indicación, bad=false, ground=false, acumuladores de la tecla iniciados en cero. Una flecha significa `(P,N)` de una llamada; no supone que toda observación real necesariamente llegue a CS.

### T1. Strafe limpio de cinco muestras positivas

Supuesto: una única tecla k activa en P durante cinco llamadas; k es q; la quinta libera o cierra en ground; no hay sixth sample añadido.

| Muestra | F[k] después | G[k] después | O[k] | Ramas |
|---:|---:|---:|---:|---|
| 1 | 1 | 1 | 0 | reset inicial si corresponde; INC F, gain>0, INC G; suma(P)=1 limpia O |
| 2 | 2 | 2 | 0 | mismas acumulaciones |
| 3 | 3 | 3 | 0 | mismas acumulaciones |
| 4 | 4 | 4 | 0 | mismas acumulaciones |
| 5 | 5 | 5 | 0 | acumula antes del cierre; emite si solicitado |

Efficiency=100%. D y A no se determinan por gain positivo: faltan signos/orientaciones. Gain acumulado es la suma de cinco valores positivos no especificados.

### T2. Cinco muestras: dos positivas y tres negativas

Mismos supuestos, signos asumidos `+,+,−,−,−`: F progresa 1,2,3,4,5; G 1,2,2,2,2; O=0. Efficiency=40%; gain suma los dos incrementos y loss resta los tres negativos. Su orden no cambia esos totales bajo esos supuestos, pero sí podría cambiar desync/angle si cambian sus entradas. No se inventan magnitudes.

### T3. A → A+D → D

Supuesto adicional: A tenía inicio anterior al nuevo D y suficientes muestras propias; cada flecha se procesa y luego hay una muestra D→D.

| Llamada | Inicio/selector | Incrementos F | Overlaps después | Cierre |
|---|---|---|---|---|
| P=A, N=AD | inicializa D; q=A | A+1 | todos cero | ninguno |
| P=AD, N=D | q=A por inicio anterior | A+1,D+1 | O[A]=1,O[D]=1 | A cierra; se conserva si F[A]>1 o full_overlap |
| P=D, N=D | q=D | D+1 | todos cero | ninguno |

La muestra compartida entra en dos F, pero su G/gain/D/A solamente van a A. Un gain positivo de esa muestra no hace good a D. Si D termina más tarde tras muestras exclusivas, su overlap de entrada ya fue borrado.

### T4. W+A → W → W+D

Supuesto adicional: W/A iniciaron juntos, ambas activas por una primera muestra, y D es nueva. Si P=WA,N=W: q=W por desempate; F[W]=F[A]=1, O[W]=O[A]=1; A solicita cierre, se filtra con full_overlap=0 porque 1 no es mayor que 1, o se emite con full_overlap!=0. Si P=W,N=WD: inicializa D; q=W; F[W]=2; se limpian todos los O. Una siguiente P=WD mantiene q=W por antigüedad e incrementa F[W]/F[D] y ambos O. No se necesita un cambio de giro para estos cierres/inicios.

### T5. Tercer solapamiento: W+S → W+S → ninguna

Supuesto: ambos inicios iguales y acumuladores cero. Dos llamadas con P=WS incrementan F[W]/F[S] a 1/2 y O[W]/O[S] a 1/2; q=W. La segunda libera ambas: full_overlap=0 descarta ambas filas si no hubo muestras exclusivas; full_overlap!=0 permite dos filas, W y luego S. S puede tener efficiency=0 aunque ambos gains sean positivos, por selección exclusiva de W. El par opuesto no se cancela en la prueba de overlap.

### T6–T10. Entradas insuficientes y transiciones

| Caso | Entradas asumidas | Ramas confirmadas y resultado | No determinado |
|---|---|---|---|
| Cambio de giro, misma tecla A | P=N=A, q=A; f>0; t pasa +1→−1 | F aumenta en ambas; primer D[A]+1, segundo no; no hay cierre por giro | Gain/good y A requieren gain/deltas; el signo f es supuesto, no velocidad inventada. |
| Cambio de tecla, mismo giro | P=A,N=D; t constante | Cuenta A, inicializa D y cierra A, aunque t no cambie | D[A] requiere f; salida depende del filtro y estado previo. |
| Frame sin teclas | P=N=0000 | No F/G/D/A; q=−1; O[0..3]=0; histórico sí se registra | Gain histórico puede ser cualquiera; P≠0,N=0 sería el caso de liberación, distinto. |
| Giro cero | q válido, c=p, t=0 | F según P; G según gain/bad; W/S añaden D si v≠0, A/D si f>0 o f<0; delta angular cero | Si h=0 no se fija f; no se deduce desync solo de «sin mouse». |
| Transición en aterrizaje | P=AD,N=D, ground=true; A anterior a D | No inicialización aérea; F[A]++,F[D]++; q=A; O de activas aumenta; ambas solicitan cierre | Valores finales dependen de acumuladores, full_overlap, bad y espacio; no solo de P/N. |

## 11. Comparación con investigaciones previas

Están disponibles [03](03-metrics-dictionary.md), [04](04-frame-analysis.md), [09b](09b-kztimer-jumpstats-comparison.md) y [09c](09c-exolent-jumpstats-source-analysis.md). Las columnas externas siguientes son **[D] respecto de esos informes**, que contienen sus propias referencias **[V] a fuentes**; no se revalidó aquí íntegramente su código ni se supone parentesco entre proyectos.

| Métrica | KZ-Rush verificado | UQ | Exolent | KZTimer | Consecuencia para KZ Coach |
|---|---|---|---|---|---|
| Efficiency/sync | CS186128–187028/191088–191464: G exclusivo por inicio / F por tecla | 03 §1,04 §4: sync PostThink>PreThink, exige alguna tecla; efficiency no visible | 09c §1: sync aéreo por aumento de velocidad; admite ausencia de teclas | 09b §4.3: sync por incremento entre callbacks; sin exigir teclas | No renombrar los cuatro cocientes como equivalentes. |
| Gain | CS186808–186932: suma positivos de q, salvo bad | 03 §1: suma solo nuevos récords globales | 09c §1: suma todos los incrementos positivos del segmento | 09b §4.3: suma incrementos positivos | Recuperar velocidad perdida no significa lo mismo en UQ. |
| Overlaps | CS189136–189624: cardinalidad>1, reset≤1, entero final | 03/04: no métrica visible; multitecla cambia historial | 09c: no contador equivalente demostrado | 09b: no contador equivalente demostrado | No reemplazar con porcentaje de todas las muestras multitecla. |
| Desync | CS187584–188992: tabla v/t/f por q | 03/04: no fórmula nombrada | 09c: sync no demuestra coordinación direccional | 09b: sync no exige acuerdo mouse/tecla | Conservar clasificación, no interpretar cada pérdida como desync. |
| Segmentación | CS184396–186116/189716–190264: inicios/cierres por tecla | 04 §3: tecla única y giro; baseline angular problemático | 09c §1: grupos AW/SD habilitados por yaw | 09b §4.2: AW/SD y cualquier giro | No importar alternancia AW/SD al binario KZ-Rush. |
| Ángulo | CS188996–189120: suma firmada, abs al cerrar | 03: no métrica numérica equivalente | 09c: no métrica equivalente establecida | 09b: comparación yaw sin normalización circular | No llamar a este ángulo «error respecto del ideal». |

**[D]** La [documentación oficial de KZ-Rush](https://kz-rush.ru/en/article/kz-rush-lj-stats), Kpoluk, 2020-12-20, consultada 2026-11-03, define efficiency como porcentaje de frames positivos, overlap como muestras multitecla al final y desync como desacuerdo mouse/tecla. **[I]** Coincide con la intención general, pero omite selección q, inclusión de t=0 y dependencia de orientación. No prueba identidad de versión con este archivo. Las fórmulas del presente informe proceden del binario, no del artículo ni de otros plugins.

## 12. Riesgos y ambigüedades pendientes

1. **Admisión externa incompleta:** expandir cada rama que llama CS y cada asignación de bad; faltan predicados completos para fallos, slide/agua/teleport y primer/último sample. Tener los seis sitios de llamada no basta.
2. **Fase física:** plugin y registros no fijan todo el orden del motor ni la relación comando/muestra. Debe contrastarse estáticamente con fuentes del entorno correspondiente, sin iniciar servidor.
3. **Suelo categorizado:** falta expansión íntegra de `isCategorized` y correcciones de `findGoodFrame` C304728–306316. No sustituir `g_bCatGround` por `FL_ONGROUND`.
4. **Dominio nativo:** división por h=0, NaN, infinitos, signed zero y precisión trigonométrica dependen del módulo AMXX; no se ejecutó ni verificó su build instalado. Umbrales yaw ±90 exactos y entradas fuera del rango habitual necesitan tratamiento explícito.
5. **Alias/duplicaciones/límites:** el barrido de constantes no prueba ausencia de escritores indirectos; el cierre multitecla cerca de 50 filas y la prevención global de duplicados siguen condicionados al llamador.
6. **Presentación:** se localizó `showStrafes` y formatos enteros/Float; no se certificaron todas las opciones de HUD ni todas las transformaciones agregadas del pie de salida. Este informe reconstruye las filas, no todas las pantallas.

Las discrepancias de lectura entre agentes se resolvieron contra instrucciones: reset inicial condicional, overlap≤1, raíz prevVelocity y guardas `500>count`/`50>count`. No se usó consenso entre agentes como evidencia binaria.

## 13. Qué podemos reproducir con certeza

**[V/I]** Para una llamada local admitida, con estado e inputs finitos dentro del dominio de las nativas: empaquetado de teclas, atribución anterior/actual, resets por tecla, selector q y desempates, incrementos F/G/O/D, acumulación de ángulo, predicados de cierre, filtro full_overlap y fórmulas/copia de métricas por fila. «Reproducir» significa aquí especificación estática respaldada, no código autorizado.

## 14. Qué todavía no podemos reproducir

No se puede prometer identidad end-to-end con KZ-Rush dada únicamente una secuencia de teclas/yaw/speed. Faltan admisión completa del intento, categorización/corrección, reglas de historial tras early returns, garantías de deduplicación y dominio exacto de nativas externas. No se fuerza una respuesta total al criterio de finalización.

## 15. Recomendación para la siguiente fase

**Continuar investigación, no comenzar implementación.** Siguiente unidad concreta: reconstruir el CFG de `hamPlayerPreThink` y las seis llamadas a CS, incluyendo bad, `g_bCatGround`, resets y correcciones; fijar después la semántica estática de las nativas Float del entorno. La entrega debe producir una tabla completa de admisión/estado y resolver los límites señalados antes de autorizar un modelo aislado.

Validaciones realizadas: hashes original/imagen, límites, símbolos/ámbitos, correspondencia C/I/D, reproducción exacta de artefactos, decodificación global, destinos/nativas, 27 pruebas y revisión estructural de este documento. No hubo cambios de código, pruebas del juego, ejecución del plugin, compilación, acceso al servidor ni modificaciones de referencias o datos de producción.
