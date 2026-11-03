# Distance and landing: a jump result is not a block requirement

**A recorded jump distance, the player's horizontal displacement, a nominal block size and the geometry required to land are different quantities.** KZ-Rush documents both an orientation effect caused by the axis-aligned player box and a last-frame collision reconstruction. These explain why a distance number alone cannot establish whether a particular block was reachable—or why it was missed.

This document adds an external reference model to the UQ JumpStats 2.42 audit. It does not replace UQ's measured formulas, specify a new application architecture, implement capture, or change any plugin/configuration.

## 1. Evidence, access and compatibility with the existing audit

### Evidence labels

- **Documented fact [D]:** explicitly stated by an identified source. An article's explanation is documentary evidence, not an independent engine-code or runtime verification.
- **Inference [I]:** a mathematical consequence or research requirement derived here, with its assumptions stated. Not an attributed plugin implementation.
- **Hypothesis [H]:** a proposed explanation or expected behavior that still needs source/runtime evidence. It must not be used as a confirmed diagnostic.

Unless otherwise specified, distances are engine units, velocities are units/second, and `dt` is a movement-step duration in seconds. Article examples do not establish a universal fixed frame rate.

### Sources and the claims they support

Both complete **article text bodies** were accessible on **2026-11-02**, including the displayed equations and the concluding caveats. Embedded illustration links were available, but images were not independently measured/digitized. Neither article provides a complete LJ-plugin implementation or a demo-format specification. No linked third article, LAN package or engine source was inspected for this extension.

| Citation | Source and locator | Supported claims |
|---|---|---|
| [CD-G] | Kpoluk, **Calculating distance**, 13 May 2023: opening box/240-block discussion, 45° example and paragraph naming Flibo Bug | Box dimensions, map-axis alignment, 208-unit center displacement, rotated example, LJ-equivalent comparison and mention of **Estimated LJ**. |
| [CD-S] | Same article: paragraph beginning “The next thing to recall”, followed by the DeathClaw example | `PM_CategorizePosition`, under-2-unit ground snap, integer versus partial-frame endings in the described examples. |
| [CD-C] | Same article: A/B/C/D discussion and displayed equations ending with the S-to-C distance | Last-frame candidate movement, flat-surface collision fraction and horizontal endpoint displacement. |
| [CD-P] | Same article: paragraph beginning “Now consider the same task for our plugin” | Downward 2-unit trace to distinguish snap; A-to-B trace for a general surface rather than relying on D's height. |
| [CD-M] | Same article: final bhop-block discussion and concluding paragraph | Descending bhop blocks, mpbhop context, earlier reference snapshot, and explicitly omitted failed/duck/frame-selection details. |
| [LJ] | Kpoluk, **KZ-Rush LJ stats**, 20 Dec 2020: **Main and strafe statistics**, **JumpOff**, **Fuser2 and Height**, **Chat commands**, **LJ Settings Menu** | Documented `jof`, `land`, `last`, `/dt`, conditional block reporting, height context and Advanced-mode scope. Not their full internal algorithms. |
| [UQ] | Local `reference/uq_jumpstats.sma`, particularly `fwdPreThink:4252–4354,6502–6658`; existing documents linked below | UQ-specific distance/landing/helper boundaries and axis-probe limitations. Not evidence that UQ implements KZ-Rush's trace model. |

Evidence labels below use these citation IDs; the linked source table and paragraph locators identify their backing passages without inventing stable webpage anchors.

### What was checked against the existing documents

| Existing document reviewed | Boundary preserved here |
|---|---|
| [README](README.md) and [01 — Architecture](01-plugin-architecture.md), especially persistence/export | An article's demo reconstruction example does not prove that our demos or UQ files retain the required inputs. |
| [02 — Data inventory](02-data-inventory.md), direct observations and retention | Current movement reads and bounded beam samples are not a lossless, timestamped collision recording. |
| [03 — Metrics dictionary](03-metrics-dictionary.md), sections 2–3 | UQ's nonfailed result uses the smaller of direct/corrected **3D** candidates with ordinary `+32` or a ladder offset; failed distance and Landing helpers remain missing. |
| [04 — Frame analysis](04-frame-analysis.md), reconstruction limits | `/dt` is absent from the supplied UQ file. [LJ] now establishes that **KZ-Rush documents a command with that name**, not that it generated our original example or runs on the user's server. |
| [05 — Diagnostic capabilities](05-diagnostic-capabilities.md) and [06 — Open questions](06-open-questions.md) | Symptoms remain separate from causes; target-aware diagnosis and demo availability still require evidence. |

**No contradiction requiring an earlier-document edit was found.** Earlier absence claims are scoped to the supplied UQ source. KZ-Rush's documented `last` is a shortfall; this does not establish the meaning of an unspecified “Lasting” field or UQ's missing `LandingCalculate` helper. [D: LJ, UQ]

## 2. Four quantities that must not share one meaning

| Quantity | Meaning in this investigation | What it does not establish |
|---|---|---|
| **Horizontal displacement** | Endpoint separation in XY, `sqrt((x_end−x_start)^2 + (y_end−y_start)^2)`, for explicitly chosen reference positions. [D: CD-C] | Not the sum of distances along a curved flight path; not automatically the displayed LJ result. [I] |
| **Recorded jump distance** | A producer-defined statistic with its own start/end selection, corrections, dimensionality and offsets. UQ's actual calculation is in 03; KZ-Rush's article explains a different measurement procedure. [D: UQ, CD-C, CD-P] | Not automatically a physical gap, a required center displacement, or an interchangeable value across plugins. [I] |
| **Nominal block size** | The labeled edge-to-edge crossing span in examples such as “240 block”; it must be tied to the actual takeoff and landing edges. [D: CD-G; I: explicit measurement requirement] | Not necessarily a brush's outer size, an arbitrary two-point distance, or the player's displacement. A label does not identify a landing polygon. [I] |
| **Geometric requirement / difficulty** | Required travel and collision feasibility for the player's box relative to specified support surfaces, orientation, height and intended crossing. [I, based on CD-G, CD-P, CD-M] | Not a complete skill rating, probability of success, or minimum prestrafe/strafe-efficiency target. Geometry alone does not supply those models. [I] |

**[D: CD-G] Axis-aligned example:** for the article's ideal 240-unit crossing, the center needs to move **208** horizontally; the remaining **32** comes from the footprint's extent at takeoff and landing. Those 32 units are geometric support reach, not extra airborne motion or acceleration.

**[I] Consequence:** even a correctly recorded endpoint distance cannot answer “was this enough for that block?” without the metric convention, relevant edges, actual takeoff position and landing opportunity. Equal scalar distances can end at different lateral positions or represent different collision endpoints.

### Do not silently reconcile the article's normalization

**[D: CD-G, CD-C]** The opening examples add 32 to the required center displacement to express ordinary-LJ-equivalent difficulty. Later, the displayed S-to-C equation is a horizontal distance **with no explicit `+32`**.

**[I] Interpretation boundary:** name that later result `d_SC` when discussing its arithmetic. Do not assume it is the complete final HUD value, insert an omitted `+32`, or remove UQ's explicit `+32`. Exact S/C reference conventions and final KZ-Rush output normalization need plugin-source or known-output verification. This distinction is unresolved—not a demonstrated contradiction in either implementation.

## 3. The 32 × 32 AABB and Flibo Bug

### Documented geometry

**[D: CD-G]** The player collision box has a **32 × 32** square footprint; its height is **72 standing** and **36 crouched**. It is an **axis-aligned bounding box (AABB)**: its axes stay aligned to the map. Turning the player's view does not rotate this collision footprint.

**[I] Consequences:** view direction and block orientation are different inputs. Crouching changes the documented height, not the horizontal footprint width. It does not make the box horizontally narrower; it still matters for vertical reference coordinates and collision timing.

**[D: CD-G]** For the article's 240-unit block rotated **45°**, the center-travel requirement becomes:

```text
required center displacement = 240 − 32*sqrt(2) ≈ 194.745 units
ordinary-LJ-equivalent comparison = 194.745… + 32 ≈ 226.745 units
```

The article calls this orientation-dependent effect **Flibo Bug**. It describes the rotated 240 as easier than an ordinary 227 and mentions a separate measuring plugin's **Estimated LJ** parameter. It does not supply that parameter's full algorithm. [D: CD-G]

**[I] Important limit:** this is a geometric equivalence under the example's crossing conditions, not proof that every nominal 240 rotated block is easier than every 227. Finite landing width, height, lateral approach, obstacles and moving surfaces can change feasibility. Rotating the camera alone does not reproduce rotating the map geometry.

### Optional mathematical generalization—not a sourced plugin formula

**[I]** For an ideal stationary crossing between sufficiently wide, parallel, same-height support edges separated by `B` along their horizontal unit normal `n = (cos θ, sin θ)`, with `B` greater than the projected box width, the square's projected full width is:

```text
w(θ) = 32*(abs(cos θ) + abs(sin θ))
ideal center-travel threshold along n = B − w(θ)
ordinary-LJ-equivalent comparison = B − w(θ) + 32
```

This follows from projecting the fixed square onto the edge normal: each support boundary contributes a half-width of reach. It reproduces 208/240 at 0° and approximately 194.745/226.745 at 45° for `B=240`.

It assumes travel along that normal, adequate lateral support and an otherwise feasible vertical trajectory. It ignores engine tolerances, finite corners, snap eligibility and obstructions; the threshold is not a guarantee of contact. It is **not** a recovered KZ-Rush **Estimated LJ** implementation, a UQ formula, or a general arbitrary-map difficulty score.

## 4. Landing is an event inside movement, not just a final position

### 4.1 Documented ground-snap versus collision paths

**[D: CD-S]** The article attributes a short ground snap to `PM_CategorizePosition`: with **less than 2 units** between the box and the ground in the described situation, the engine places it on the ground. It says this often ends flat-ground jumps after an integer number of frames. Over a gap that support may be absent, allowing flight into part of another frame.

**[I] Boundary:** “less than 2” is not a complete universal grounded predicate. The article does not give every eligibility condition, equality-at-2 behavior, accepted surface normals, collision masks or tolerance. A nearby wall is not thereby a landing; XY overlap alone is not a validated grounded state.

**[D: CD-S, CD-C]** The 73rd/74th-frame DeathClaw example illustrates this distinction; it is not a universal duration for all LJ techniques, stances, settings or frame times.

### 4.2 Reconstructing contact within the last frame

**[D: CD-C]** The article distinguishes:

| Point | Role in the illustrated movement step |
|---|---|
| `S` | Start reference for the jump-distance calculation. |
| `A` | Last airborne position; the illustration's text describes the box's lower edge at A. |
| `B` | Where that movement step would end without the block collision. |
| `C` | Collision position reached partway through A→B. |
| `D` | Actual position after collision response and the remaining movement, attributed to `PM_FlyMove`. |

**[I] Coordinate caution:** these schematic points are not an API contract for `pev_origin`. Mapping their Z to center/feet and choosing the correct velocity phase needs verification, especially if the hull changes with ducking. Use one consistent reference throughout an equation.

The documented candidate endpoint is, componentwise:

```text
B = A + V_A*dt
```

For the illustrated case where **C and D have the same height**, the article reconstructs:

```text
fraction = (z_A − z_D)/(z_A − z_B)
C = A + (B − A)*fraction
d_SC = sqrt((x_C − x_S)^2 + (y_C − y_S)^2)
```

These are the article's last-step equations, not UQ's ballistic/minimum-distance algorithm. The linear A→B expression must not be expanded into a claim that velocity is constant throughout the entire jump or that gravity can be ignored. [D: CD-C; I: scope restriction]

**[I]** Under that single-segment interpolation, contact is `fraction*dt` into the step. A usable result requires nonzero `z_A−z_B`, a fraction in the relevant segment, correct inputs and the stated flat-height condition. With no such evidence, an algebraic answer is not proof of a real contact. Multiple collisions, slopes, hull changes or moving surfaces are not solved by this one equation.

**[I] Diagnostic consequence:** D is not interchangeable with C. It can include movement after the first contact; using the last recorded grounded position can change the measured endpoint. The direction and size of that error are not universally determined by the article.

### 4.3 What KZ-Rush says its plugin does

**[D: CD-P]** Its stated procedure first repeats the engine's **2-unit downward trace from the last airborne position**:

1. If it hits the ground, the article treats the snap as having occurred and uses **A's X/Y** as the endpoint.
2. Otherwise, it reconstructs the movement toward B. For general surfaces it obtains `fraction` from an **A→B trace**, rather than assuming `z_C = z_D`.

**[I]** Reproduction therefore requires collision queries equivalent to the intended player-box movement, not merely applying the flat-height formula or casting an arbitrary center ray. **The article does not disclose the trace API, hull identifier, filtering, precision, start-solid handling or full response algorithm.** This document does not choose or invent those details.

**[D: LJ]** KZ-Rush describes `jof` as proximity of takeoff to the block edge, `land` as reserve at landing, and `last` on failures as the distance shortfall. It reports `block` when jof and land can be determined. These are documented metric meanings, **not sufficient formulas** to derive `land`/`last` on arbitrary geometry. In particular, no general identity `land = recorded distance − nominal block − jof` is established here.

## 5. What KZ Coach would need to measure or reproduce this

The following are **inferred evidence requirements [I]**, not implemented capture features or a technology selection. Existing UQ availability follows [02](02-data-inventory.md); KZ-Rush documentation is not proof of an available export.

| Required evidence | Purpose | Current boundary / approximation limit |
|---|---|---|
| Producer/version, metric convention and start/end definitions | Separate displacement, displayed distance, nominal span and equivalent difficulty. | UQ source is identified; equivalence to the deployed build and KZ-Rush output conventions remains unverified. [UQ; 03, 06] |
| Timestamped `S`, last-air `A`, grounded/end `D`, full `V_A`, actual step `dt`, sample IDs and engine/callback phase | Reconstruct the last step and avoid pairing values from different phases. | UQ reads position/velocity and keeps selected snapshots, but no demonstrated complete phase-aligned export with per-step duration. A frame count alone is insufficient. [UQ; 02, 04] |
| Hull bounds, standing/crouched state and transitions; coordinate reference | Convert schematic positions consistently; reproduce box collision and vertical clearance. | UQ has duck checks/beam flags, not a verified exported hull-transition sequence. Horizontal width alone cannot establish landing time. [CD-G; UQ; 02] |
| Ground state, actual landing/support entity, collision/snap evidence, trace fraction/end and surface information | Distinguish snap, first contact, wall touch and subsequent movement. | UQ's touch flags and axis-probe endpoints are not a retained collision journal. Trace semantics and the complete grounding predicate remain unverified. [CD-P; UQ; 02] |
| Intended target, actual takeoff/landing support boundaries, heights, orientation, finite lateral extent and intervening obstructions | Compute a block requirement, reserve/shortfall or lateral miss against that target. | A map name, scalar block number or two point measurements do not establish all this geometry. UQ's dominant-axis probes are not a general rotated-surface model. [CD-G; UQ: `fwdPreThink:6502–6658`] |
| Map/build identity and collision representation; entity transforms/motion at the relevant times | Match traces to what the engine encountered, including moving blocks. | A current static surface position cannot automatically reproduce an earlier moving-platform contact. No such historical geometry export was demonstrated. [CD-M; UQ; 02] |
| Physics context: jump technique, gravity/settings, FOG, fuser2, stance and mpbhop behavior as applicable | Compare equivalent attempts and interpret vertical opportunity; reproduce more than the single last step. | [LJ] documents FOG/fuser2/height; that does not create these metrics in UQ or show their persistence. Exact simulation inputs require separate verification. |
| Validity/failure reason and all-attempt retention with precision metadata | Separate misses from invalidations and compare repeated attempts without top-record selection bias. | UQ's failed flag is overloaded; tops are selective and active arrays are reused. [UQ; 01–03, 05] |
| Synchronized button/view observations, if diagnosing input causes | Link geometric symptoms to technique rather than guessing from distance. | Not necessary merely to compute XY endpoint separation, but necessary for stronger causal coaching. Neither article proves access to the complete raw stream; UQ sync is not direct coordination. [LJ; UQ; 04–05] |

### Reproduction versus approximation

- **[I] Summary-only interpretation:** it can explain a producer's reported values; it cannot recover C or prove target feasibility from one distance scalar.
- **[I] Restricted geometric approximation:** known parallel-edge geometry can support the section 3 ideal comparison; verified last-step snapshots on an appropriate flat surface can support section 4 interpolation. Each assumption must remain visible, not be presented as engine-exact.
- **[I] Engine-faithful reproduction:** requires matching movement/collision semantics, hull, timing and world state, verified against known cases. The articles give the conceptual procedure, not enough implementation details to claim parity.

**[D: CD-C; I: availability boundary]** The article asks the reader to imagine a demo parser extracting `dt` and velocity. It does not specify demo channels, recording mode, quantization or extraction guarantees. Our earlier warning stands: a visible HUD or a playable demo is not proof that the required structured inputs survive. No demo was parsed for this document.

## 6. Potential diagnostics and their evidence threshold

These are **potential inferences [I]**, conditional on obtaining and validating the stated data. They are not new capabilities already available in KZ Coach or proof of player intent.

| Potential observation / diagnosis | Without target geometry | What target/collision evidence would add | Causal limit |
|---|---|---|---|
| Horizontal displacement between verified references | Can measure with correct S/end positions and convention. | Separates achieved displacement from the requirement of a particular landing. | Displacement alone does not say why the jump failed. |
| End-of-frame endpoint differs from first contact | Possible only with adequate last-step/contact evidence; summaries do not suffice. | General geometry/traces can establish C and distinguish it from D. | A discrepancy can be a measurement issue, not a player error. |
| A rotated “240” is not equivalent to an axis-aligned 240 | Cannot infer orientation from the number 240. | Known edge orientation and support extent permit a restricted geometric comparison. | Flibo geometry does not imply improved strafing or establish skill difficulty in full. |
| Takeoff leaves more reserve than comparable attempts | Cannot judge a scalar position as early/late relative to an unknown edge. | Actual takeoff boundary, hull, timing and approach permit a contextual jof/reserve comparison. | More reserve is not automatically avoidable; [LJ] notes minimum jumpoff depends on the particular run/frame alignment. |
| Short of target / landing reserve | Cannot derive it from “distance minus block label.” | Target surface, first-contact geometry, movement/height and a defined margin convention can support a geometric shortfall/reserve estimate. | Still does not isolate low prestrafe, air acceleration or input timing as the cause. |
| Lateral or wrong-surface miss despite adequate scalar travel | Not demonstrable from distance, maxspeed and sync alone. | Intended finite landing region plus hull trajectory/contact identity can reveal a spatial mismatch. | Correctness requires a declared intended target; closest surface is not necessarily the target. |
| Failure associated with moving-block height/reference | At most an unexplained height difference without entity history. | Historical surface state and landing/jump snapshots can test the moving-block explanation. | Must separate a real constraint from measurement normalization; not every lower takeoff is an execution error. |
| Recurrent landing inconsistency | A retained comparable endpoint series can show variation, but not target accuracy. | Same target/geometry/settings and a defined margin can reveal repeated spatial symptoms. | Repeated symptoms do not establish repeated input causes; selected tops are insufficient. |

**[H] Pending validation:** late takeoff, a poor lateral approach, or inadequate acceleration could explain a particular failed attempt. Neither article nor the supplied UQ aggregates establishes which explanation is correct for a real player. Testing a counterfactual—“this attempt would have landed if input X changed”—requires more than reconstructing its observed collision.

## 7. Special cases and open questions before implementation

### Special-case limits

| Case | What is documented versus unresolved |
|---|---|
| **Descending bhop blocks / mpbhop** | **[D: CD-M]** Without mpbhop, the block can descend with the player before jumping; more bhop FOG means a lower departure, and faster block motion makes the example harder. The article says its plugin remembers an earlier position when the engine has placed the player on the block but descent has not begun. Exact callback/frame selection and normalization are not given. **[I]** Keep actual departure and that earlier reference distinct. |
| **Duck/no-duck and jump variants** | **[D: CD-G, CD-M, LJ]** Hull height, flight-height context and technique matter; the distance article explicitly leaves detailed duck/failure/frame-selection handling to developers. **[I]** Do not extrapolate a same-height LJ example to CJ, all bhops or every stance transition. |
| **Different-height landings, slopes, corners, multiple contacts** | **[D: CD-P]** General surfaces motivate the A→B trace. **[I]** The flat `z_C=z_D` interpolation and ideal parallel-edge width correction do not solve these cases. Full collision/grounding rules are still needed. |
| **Teleports, slide, water, ceiling contact** | **[D: LJ]** Advanced mode includes cases ending on teleports, slide or water and different platform heights; the height section notes ceiling contact can reduce actual height. It does not provide all distance algorithms for those cases. **[I]** Treat endpoint/event type as context, not assume ordinary landing semantics. |
| **Failed or invalidated results** | **[D: CD-M]** Failed-jump detail is omitted. **[D: UQ]** `GetFailedDistance` is missing and a failed label can reflect invalidation. **[I]** No universal failure-distance or last-shortfall algorithm can be reconstructed from these sources. |
| **Precision and thresholds** | **[D: CD-S, CD-C]** The text supplies a less-than-2 snap description and a step fraction. **[I]** It does not establish engine epsilon, exact grazing-contact acceptance or sufficient output precision. A marginal contact cannot be certified from rounded statistics. |

### Questions to resolve, in order

1. **Metric identity:** what exact start/end references and normalization produce each deployed plugin's displayed distance? How does KZ-Rush's final result relate to the article's `d_SC` and opening `+32` equivalence?
2. **Contact contract:** what constitutes a valid supporting landing versus wall/edge contact, including exact snap conditions, surface normals, equality thresholds and tolerances? Which trace/hull semantics reproduce it?
3. **Temporal contract:** which callback/velocity phase and actual `dt` define A→B, S and C? How are stance changes, multiple collisions and platform movement handled within that step?
4. **Target contract:** how are the intended support edges/region and nominal size established on rotated, finite, different-height or moving geometry? What exactly does **Estimated LJ** calculate beyond the published 45° example?
5. **Available evidence:** can existing permitted outputs or specific demo modes expose the necessary data and precision, or only summaries? Verify with real sample bytes before choosing a future capture path.
6. **Validation baseline:** which independently known axis/45° crossings, snap/partial-frame landings, duck variants, misses and moving-block cases can confirm the measurement model without changing official-record settings?
7. **Coaching boundary:** what additional reference or movement model would justify causal input advice after a geometric symptom is established?

**Recommended next research step [I]:** agree on the measurement/target definitions, obtain matching plugin/helper evidence where available, then validate a small set of known geometry/contact cases using separately designated non-record material. Do not choose a stack or change capture/plugins merely to fill the unknowns in this document.

## Key Learnings:

1. **[D: CD-G; I]** Fixed AABB orientation makes nominal block span and required player displacement diverge; a distance record alone is not a block-clearance certificate.
2. **[D: CD-S, CD-C, CD-P]** Ground snap, partial-frame first contact and post-contact endpoint must be distinguished; last-frame reconstruction needs trustworthy time, state and collision evidence.
3. **[D: UQ, LJ; I]** External KZ-Rush descriptions extend the research evidence, not UQ's implemented/exported capabilities. Target geometry and measurement provenance are prerequisites for stronger landing diagnostics.

**Not checked:** plugin/engine implementations beyond the previously supplied UQ source, linked third articles, image measurements, demo parsing or runtime behavior. **Risk:** applying a flat-surface or summary-only approximation outside its assumptions can mislabel measurement differences or geometric constraints as player errors.

[CD-G]: https://kz-rush.ru/en/page/calculating-distance
[CD-S]: https://kz-rush.ru/en/page/calculating-distance
[CD-C]: https://kz-rush.ru/en/page/calculating-distance
[CD-P]: https://kz-rush.ru/en/page/calculating-distance
[CD-M]: https://kz-rush.ru/en/page/calculating-distance
[LJ]: https://kz-rush.ru/en/article/kz-rush-lj-stats
[UQ]: ../reference/uq_jumpstats.sma
