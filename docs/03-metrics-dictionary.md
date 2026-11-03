# Metrics dictionary: what the supplied JumpStats actually measures

This dictionary describes **only `reference/uq_jumpstats.sma`, version 2.42** (`VERSION`, line 24). It separates visible calculations from missing helper implementations and metrics requested for KZ Coach that this source does not provide. It is evidence for interpreting the reference, not a specification for a newer plugin or an implementation plan.

## Read this first

- A successful ordinary jump uses the **smaller of two 3D endpoint distances, plus 32 units**. It is not simply horizontal displacement or accumulated path length.
- A failed jump can call `GetFailedDistance`, but that function's body is **not supplied**. Do not substitute a guessed ballistic formula.
- Jump names describe a state machine with timing, height, input and previous-jump conditions. They are not labels inferred from speed alone.
- FOG, efficiency, overlaps, desync, a numerical strafe-angle metric and an induck-frame metric are **not visibly implemented**. Related counters or booleans are not equivalent measurements.

### Evidence convention

All source references below are to [`../reference/uq_jumpstats.sma`](../reference/uq_jumpstats.sma); `fwdPreThink:4201–4331` means that function and the file's physical line numbers. Unqualified references within lines 1996–6748 refer to `fwdPreThink`; other functions are named where relevant. Formula notation is explanatory, not new plugin code. Positions/distances are engine units; horizontal speed is units per second; `get_gametime()` differences are seconds; frame values count callback samples, not milliseconds.

| Evidence level | Meaning |
|---|---|
| **Visible** | Calculation or condition is present in the supplied `.sma`. |
| **Missing helper** | The call and arguments are visible, but the implementation is not. |
| **Absent** | No producer/formula for the requested metric was found in this `.sma`; not proof that every other JumpStats version lacks it. |

The missing project includes are `uq_jumpstats_const.inc`, `uq_jumpstats_stocks.inc` (lines 19–20), and `uq_jumpstats_sql.inc` (line 766). Consequently `JumpType`'s enum declaration, `NSTRAFES`, `NVAR`, `GRAVITY`, `SCRIPTFRAMES`, translated strings, helper contracts and SQL behavior cannot be reconstructed completely. Translation file `uq_jumpstats.txt` is referenced at line 152 but not supplied. A localization key is evidence of an output branch, **not evidence of its exact rendered wording**.

## 1. Core metric inventory

| Requested metric | Actual producer/formula | Evidence and limits |
|---|---|---|
| Speed | Zero velocity Z, then `vector_length(velocity)`, equivalent to `sqrt(vx² + vy²)`. | `fwdPreThink:2193–2202`. Post-think independently samples horizontal `fSpeed`, lines 7817–7821. |
| Prestrafe | Snapshot of `speed[id]` at jump initialization. | Ordinary/real-ladder/drop/count setup: 3731–3732, 3784–3785; next-bhop: 3599–3600; multi-bhop: 4042–4043. Ladder movement snapshots it before departure, 3245–3263. Slide: 2533. Not a maximum over the entire ground run. |
| Prestrafe FOG | **Absent.** No exposed frame-on-ground counter or FOG formula. | Ground timers at 2329–2358, 6695–6728 are state expiry checks, not FOG output. Do not relabel them as FOG. |
| Maxspeed | Starts at prestrafe; updated only when sampled `speed > maxspeed` during active, airborne, not-yet-failed pre-think. | `fwdPreThink:2806`, 2892–2908; initialization references above. A pre-think peak, not necessarily the post-think physics peak. |
| Overall gain | `maxspeed − prestrafe`. | `fwdPreThink:4873–4874`. Not cumulative positive acceleration. |
| Per-strafe gain | If `speed > maxspeed`, add `speed − maxspeed` to current strafe, then advance the global maximum. | `fwdPreThink:2901–2907`. **Only new all-jump records count**: recovering previously lost speed contributes no gain until it exceeds that maximum. Slot 0 can receive gains before the first numbered strafe. |
| Per-strafe loss | If `speed < TempSpeed`, add `TempSpeed − speed`; then set `TempSpeed = speed`. | `fwdPreThink:2909–2926`. Sum of downward pre-think changes; equality adds nothing. `TempSpeed` starts at 0 at jump setup, so the first sample is not a loss from prestrafe. No separate aggregate-loss output is visibly calculated. |
| Per-strafe sync | `100 × good / (good + bad)`, integer arithmetic; zero if denominator is zero. | `fwdPreThink:4571–4578`. Good/bad production below. |
| Overall sync | `100 × Σgood / (Σgood + Σbad)` for numbered strafes `1..strafe_num`, integer arithmetic; zero if `Σgood == 0`. | `fwdPreThink:4553–4583`, 4670–4672. Weighted by eligible samples, not the average of per-strafe percentages. Slot 0 is excluded. |
| Duration | `Fulltime = last_land_time − jumpoff_time`; strafe share `100 × (timestamp[j] − timestamp[j−1]) / Fulltime`. | `fwdPreThink:4561–4570`. This is the visible time-per-strafe percentage, not a confirmed report field named Duration. `last_land_time` updates while **not on ground** (2318–2322), so `Fulltime` ends at the last sampled airborne pre-think, not the landing instant. No visible zero-duration guard. |
| Efficiency | **Absent.** | `frames_gained_speed` and `frames` increment at 2892–2899, but no ratio/output uses them in this `.sma`. Do not invent `gain / ideal gain`, `good frames / all frames`, or distance efficiency. |
| Overlaps | **Absent as a metric.** | Multi-key conditions reset the strafe input history at `fwdPostThink:7921–7928`; no overlap counter/percentage is emitted. Those frames can still enter sync's denominator. |
| Desync | **Absent as a named metric/formula.** | Failed gain samples are not explicitly called desync; no-input frames are separate and optional (7918–7919). Neither justifies a guessed desync definition. |
| Angle | **Absent as a numerical jump/strafe-angle metric.** | Entity-angle component `[1]` comparisons affect strafe detection (`fwdPostThink:7824–7834`); component `[0]` equality affects a script heuristic (`fwdPreThink:2810–2824`). The API read is `pev_angles`, not `pev_v_angle`; correspondence to actual view/mouse motion is unverified. Neither computes ideal angle, angle error, or angle change per strafe. |
| Jump frames | `FullJumpFrames++` whenever post-think sees `g_Jumped`. | `fwdPostThink:7801–7806`. Reset at 2149 and next-bhop setup 3504. It is not guarded by `!FL_ONGROUND`; takeoff post-think can count. `frames` at 2897 is a different pre-think counter. |
| Jumpoff | `edgedist` from three axis-aligned traces; formula and limits in section 3. | `fwdPreThink:6502–6685`. Distinct from continuous trainer value `jof`. |
| Landing | `LandingCalculate(id, foot_probe_origin, jumpoff_origin)`, with an optional retry and `−0.06250`. | `fwdPreThink:4334–4354`. **Missing helper**; exact geometry is not recoverable. Not visibly `distance − block − jumpoff`. |
| Induck | No induck-frame/count/percentage output. `in_duck` tracks pre-jump duck sequencing, and `Type_Bhop_In_Duck`/`Type_Up_Bhop_In_Duck` are classifications. | `fwdPreThink:3570–3594`, 6221–6439. `duckstring` is an output flag, not a duration. Beam duck flags sample crouched state, not a published induck metric. |

### Sync producer, kept separate from geometric interpretation

In `fwdPostThink:7889–7919`, any of A/D/W/S held makes the current slot eligible. A sample is good only if **post-think horizontal `fSpeed > pre-think speed[id]`**; equality and reduction are bad. This is not a view/key-direction agreement test. No movement key produces `strafe_lost_frame++` only when `uq_istrafe` is enabled; that sample does not enter good/bad sync. Multiple keys still satisfy the eligible-key test.

`strafe_num` increments on a newly recognized **single** movement key plus a nonzero yaw-comparison result (`fwdPostThink:7835–7887`). The timestamp is stored at the old index before the index increments. Finalization overwrites timestamp 0 with takeoff time and timestamp `strafe_num` with last airborne time (`4562–4570`). Thus the first strafe's displayed time includes the interval before the first recognized strafe; it is not a clean start/end timestamp for that input alone.

**Index boundaries:** the stats-building guard at finalization is `strafe_num < NSTRAFES`, and output loops start at 1. If equal to `NSTRAFES`, that entire stats-build block is skipped. Runtime configured cap `NSTRAFES1` defaults to 14 (319), is loaded at 495, and resets only when `strafe_num > NSTRAFES1` (2209–2220). The compile-time capacity is missing; no safe relationship between both limits can be asserted.

## 2. Distance: exact visible arithmetic

### 2.1 Coordinate and sample conventions

Let `J = jumpoff_origin[id]`. Ordinary jump setup stores the current origin, adding 18 to Z if crouched (`fwdPreThink:3674–3680`); next-bhop and multi-bhop do the same (3588–3594, 4032–4037). These are **standing-center-equivalent Z coordinates**, not literal foot positions. Separately, `jumpoff_foot_height` uses origin Z minus 18 crouched or minus 36 standing (3557–3558, 4027–4028); that variable is not used in the visible successful-distance formula.

For the ballistic estimate, `frame_origin[0]`/`frame_velocity[0]` capture the first usable airborne sample and slot 1 is replaced by subsequent samples (`2779–2804`). The first active frame also replaces `frame_velocity[0]` (2940–2943), and later active frames replace `frame_velocity[1]` (3070–3073). Do not treat these as an array containing every jump frame.

### 2.2 Ordinary successful path

Within `fwdPreThink:4135–4331`:

1. Finalization runs when `(failed_jump || FL_ONGROUND) && in_air`.
2. Local `failed` snapshots the earlier `failed_jump` value. If true, `origin` becomes the saved `failed_origin`; otherwise it reads current landing origin (4181–4193).
3. If the player is currently crouched, add 18 to `origin.z` for candidate 1, then subtract it again before ballistic time calculation (4252–4272).

Define `norm3(A−B) = sqrt((Ax−Bx)² + (Ay−By)² + (Az−Bz)²)`. For an ordinary jump:

```text
D1 = norm3(J − normalized_landing_origin) + 32
g  = current sv_gravity
Q  = V0.z² + 2*g*(O0.z − unnormalized_landing_origin.z)
t  = (−sqrt(Q) − V1.z) / (−g)

L.x = O1.x + t*abs(V1.x), if O1.x < landing_origin.x
      O1.x − t*abs(V1.x), otherwise
L.y = O1.y + t*abs(V1.y), if O1.y < landing_origin.y
      O1.y − t*abs(V1.y), otherwise
L.z = landing_origin.z + (18 if currently crouched else 0)

D2 = norm3(J − L) + 32
distance = min(D1, D2), if local failed == false
```

Evidence: `D1` at 4257–4267; `Q`, `t` at 4274–4284; component projection at 4285–4304; Z normalization at 4306–4312; `D2` and minimum at 4316–4331.

**Literal details that matter:**

- Neither norm explicitly flattens Z. Accepted jumps often have equal normalized heights, but that does not make the actual formula universally horizontal.
- X/Y direction comes from comparing sample origin with final origin, not the signs of the recorded velocity. Equal coordinates take the subtract branch.
- The source computes `rDistance[2] = t*abs(V1.z)` (4293–4295) but does not use it to set `L.z`; it sets `L.z = origin.z` instead.
- It adds `last_land_time − jumpoff_time` to `frame2time` at 4314 **after** projecting X/Y. That addition is not reapplied to `D2` and is not the displayed per-strafe duration.
- No visible guards check `g == 0`, `Q < 0`, unavailable frame samples, or negative projected time. Missing helpers/settings may constrain runs, but the formula itself does not guard these cases.

### 2.3 Failed path and late-invalidated jumps

While actively airborne, `origin.z + 18 − J.z < 0` sets `failed_jump` (`2928–2931`). Otherwise, when `(ducked ? origin.z+18 : origin.z) >= J.z`, the code saves `failed_origin`, `failed_ducking`, and `failed_velocity` (`2932–2938`). The failure threshold always adds 18, even for a standing player; the snapshot threshold is stance-dependent.

If **local `failed` is true**, final distance is delegated exactly as follows (`4323–4329`):

```text
GetFailedDistance(offset, failed_ducking, GRAVITY,
                  jumpoff_origin, current_local_velocity,
                  failed_origin, failed_velocity)
offset = laddist for Type_ladder; otherwise 32.0
```

`GetFailedDistance` and `GRAVITY` are missing. We cannot verify its integration, stance correction, interpolation, time step, endpoint, units beyond the surrounding convention, or whether it uses the same gravity as the successful path. The success path explicitly reads `sv_gravity`; the failure call passes a different, undefined-in-this-file symbol.

**Failure color does not prove failed-distance calculation.** Local `failed` is captured at 4181–4193, before later checks can set `failed_jump`: hook protection (4195–4199), height checks (4236–4248), ladder height (4260–4263), noslow/FPS/duck-bhop checks (4356–4366), entity/trigger protection (4435–4441), and later validation. Those jumps can keep `min(D1,D2)` while being shown as failed or excluded from tops. The two booleans are not synchronized after the snapshot.

### 2.4 Special distances

| Branch | Exact difference from ordinary distance | Source |
|---|---|---|
| `Type_ladder` | On ladder departure, `J.xy = current origin.xy`, `J.z = ladder_max_z + 35.031250`. `laddist = min(ladder_size.x, ladder_size.y) + 0.03125`; if greater than 10, replace with 4. Both D1 and D2 add `laddist`, **not 32**. Failure passes that same offset to missing helper. | `fwdPreThink:3278–3311`, 4258–4266, 4317–4329. |
| Other jump types | No separate distance formula by type: bhop, standup bhop, up bhop, duck bhop, count/drop/standup-count, weird jump, real-ladder bhop and multi-bhop use ordinary offset 32 when they reach ordinary finalization. | 4257–4331. Types influence validation and classification, not a separate visible norm. |
| Slide success | `slideland = current origin.z − (18 crouched, 36 standing)`; `slidedist = slideland − groundslide`. This is a **vertical difference**, not ordinary flight distance. | 2629–2641. Ground output requires `slidim && FL_ONGROUND && Pmaxspeed == 250.0` (2666). |
| Slide masked output | If `needslide − groundslide == slidedist`, print `floor(slidedist).xxx`; otherwise print the float. | 2672–2682, 2695–2700. `.xxx` intentionally withholds fractional digits; it is not a measured fractional value. |
| Slide failure | When `velocity.y == 0`, airborne, `!failslide` and wait timer has fired, set `failslidez` from stance-adjusted origin Z; output `failslidez − groundslide`. | 2647–2663, 2735–2744. This check uses Y only, not total horizontal speed. |

Slide support probes origin ±16 along X/Y, tracing down 500. It compares only adjacent pairs 0→1, 1→2, 2→3 (not a global min/max or pair 3→0); a higher-to-lower difference over 149 triggers the `landslide` capture (`2576–2645`).

## 3. Jumpoff, block, landing and heights

### 3.1 Jumpoff is an axis-probe result

For the one-shot airborne measurement (`fwdPreThink:6502–6658`), the gate is `!FL_ONGROUND && g_Jumped && !edgedone && movetype != MOVETYPE_FLY`. It starts from **stored takeoff origin**, at Z minus 36.1, or minus 40 when a `func_door` is found within 48 units.

Three probes use transverse offsets `−18, 0, +18`. Dominant direction is chosen from the **current** velocity:

| Direction condition | Trace start | Trace end (behind takeoff) | Block-search endpoint |
|---|---|---|---|
| `vy > 0 && abs(vy) > abs(vx)` | `J.y + 100` | `J.y − 16` | `J.y + uq_maxedge + 1` |
| `vy < 0 && abs(vy) > abs(vx)` | `J.y − 100` | `J.y + 16` | `J.y − uq_maxedge + 1` |
| `vx > 0 && abs(vx) > abs(vy)` | `J.x + 100` | `J.x − 16` | `J.x + uq_maxedge + 1` |
| `vx < 0 && abs(vx) > abs(vy)` | `J.x − 100` | `J.x + 16` | `J.x − uq_maxedge + 1` |

The other horizontal coordinate receives the transverse offset. For each nonzero trace-hit-to-end distance:

```text
edgedist = norm3(edge_hit − behind_takeoff_point) − 0.031250
```

Evidence: 6531–6589. **The last nonzero probe overwrites prior values**; there is no minimum, average, angle projection or interpolation to the actual instant of leaving the edge. Strict dominance means exactly equal `abs(vx)` and `abs(vy)` (including zero velocity) has no direction branch. This is axis-specific geometry, not a universal diagonal-edge metric.

`jof`, the continuous ground/trainer value, uses the same three offsets and formula but traces from 200 units ahead rather than 100, always uses current origin Z minus 36.1, and requires grounded, not jumped, trainer enabled, not flying (`6443–6500`). It resets to 0 while airborne (2318–2322). `Dojof:1357–1367` displays nonzero values white above 5 and red otherwise. Do not conflate its sampling with `edgedist`.

### 3.2 Block distance and visible selection defects

For each probe, a second line trace goes from edge hit to the block-search endpoint. A nonzero hit distance becomes:

```text
candidate_block[i] = floor(norm3(block_hit − edge_hit)) + 1
```

At 6601–6633, the hit is lowered by 1, moved another 2 along dominant direction, and a vertical probe spans 18 units; exact equality of the checked Z values marks `block_checking[i] = 1` and prevents selecting that candidate.

Selection is literally (`6638–6653`):

1. If candidate 0 is nonzero and ≤ candidates 1 and 2, choose it only if not marked.
2. Else if candidate 1 is nonzero and ≤ candidate 2 and `candidate[0] <= candidate[0]`, choose it only if not marked.
3. Else if candidate 2 is nonzero and ≤ candidate 1 and `candidate[0] <= candidate[0]`, choose it only if not marked.
4. Else set block to 0.

The self-comparisons are tautologies, not valid minimum checks. The first branch can fail solely because a different candidate is 0, despite a valid candidate 0. A matching but marked branch does not fall through and does not clear the previous value; `jumpblock` starts at sentinel **1000** on reset (2126). Do not silently document this as “minimum valid block.” On map `prochallenge_longjump`, subtract 1 from the selected/surviving block (6655–6658).

### 3.3 Landing has a missing geometric definition

For non-ladder distance >64 (`4336–4354`):

1. Call `LandingCalculate(id, origin with Z−36.1, J)`.
2. If `distance < jumpblock + edgedist + Landing`, call again with ballistic `land_origin` at Z−36.1, subtract **0.06250**, and set `land_bug=true`.
3. Otherwise `land_bug=false`.

No helper body is supplied; neither “landing overlap” nor “distance beyond edge” is verified as its exact meaning. Output hides Landing when `block + Landing + edgedist > distance + 10` **or** `Landing <= 0` (`4617–4627`, 5922–5932). The retry is not itself a different distance formula.

Edge output also requires non-ladder type, nonzero `edgedist <100`, block strictly between the user's configured lower/upper bounds, and for successful output `block + edgedist < distance` (`4617–4635`). Failure output can omit Landing or omit block. HUD failure-with-block has no `block+edge<distance` condition at 4629; console failure-with-block **does** at 5934. Exact zero edge is hidden even though it could be geometrically meaningful. Spectator jumpoff visibility checks `edgedist[i]` but displays `edgedist[id]` (6672–6682), so it can depend on the spectator's own stale measurement.

### 3.4 Height-related metrics

| Value | Actual calculation/condition | Source |
|---|---|---|
| Normalized landing height difference | `height_difference = J.z − landing_origin.z − (18 if landing crouched else 0)`. Positive means lower landing; negative means higher landing. | `fwdPreThink:4201–4203`. |
| Jump/fall height display | Capture `heightoff_origin = origin.z + (18 if crouched else 0)` on a new grounded jump press; later grounded result compares similarly normalized landing Z with it. Print zero/up/down branch, absolute value for down. | 2374–2439. Independent from distance acceptance and from apex height. |
| Apex-like jump height `jheight` | During active flight, update `oldjump_height = abs(J.z − origin.z)`. On its first decrease while `jheight==0`, save the previous value, plus 18 if **currently** crouched. | 2827–2838, 2877. Sampled turning-point estimate; absolute difference and changing stance can affect it. Not an analytical parabola apex. |
| Up-bhop height | `checkbhop = previous J.z − current origin.z − (18 if currently crouched else 0)`. If `<−1`, `upheight = abs(checkbhop)`; threshold is delegated to missing `UpBhop_calc(upheight)`. | 3562–3578. |
| Direction used by in-game graph | At first captured `jheight`, dominant velocity axis maps `+Y→1, −Y→2, +X→3, −X→4`; ties leave it unchanged. | 2854–2871. Not a numerical jump angle. |

## 4. Jump classification: transitions, not just names

### 4.1 Shared gates and state history

Reset sets `jump_type = Type_None`, clears active-air/bhop/duck/count flags and counters, and sets `old_type_dropbj = Type_Null` (`fwdPreThink:2107–2151`). `JumpReset` merely schedules this via `g_reset=true` (`8125–8135`); it does not clear everything immediately.

The main new-grounded-jump gate is `!slide_protec && IN_JUMP && !old_IN_JUMP && FL_ONGROUND && !bhopaem && !UpcjFail` (3462). For brevity, conditions below assume their enclosing gate. They execute in source order; later rules can replace earlier labels.

`nextbhop`/`bhopaem` are historical windows, not a FOG count. Airborne observations refresh their timers; grounded elapsed time over **0.1 seconds** expires them (2325–2358). A general grounded timeout resets state after **0.4 seconds**, or **0.5 for `Type_Drop_CountJump`** (6688–6728). Duck-chain continuation uses **strictly less than 0.3 seconds** since `duckoff_time` (6223). Grounded Count/Double/Multi with `doubleduck`, no DD-weird flag, `duckstartz−origin.z<18`, and time since grounded Duck press **>0.4s** requests reset and clears doubleduck (3452–3458). These are distinct literal boundaries; do not normalize them to a common frame rule.

### 4.2 Fall, slide and ladder branches

| Branch | Actual predicate and effects | Source |
|---|---|---|
| Slide candidate | Airborne vertical sample change is less than `SurfFrames/1.7`, except exact change 4.0; on `slide_gs_longjumps` or `b2j_slide_longjumps`, sets `slide`. Otherwise it resets non-ladder jumps when no ladder within 200. | 2497–2513. |
| `Type_Slide` | In the other arm of that check, existing `slide` plus old A/current D or old D/current A initiates `slidim`, `g_Jumped`, prestrafe and `Type_Slide`; a 1.5s reset task is scheduled. | 2514–2540. Both speed-exception and slide-detection map gates use `slide_gs_longjumps` / `b2j_slide_longjumps` (2263, 2499). |
| Weird fall | Airborne, `notjump`, not flying, not `Type_ladderBhop`; if normalized fall from last grounded origin >1, not `cjjump`, and type is None/count/double/multi/drop/standup-count or `ddforcj`, assign `Type_WeirdLongJump`; clear `ddforcj`. | 3132–3138, 3151–3178. |
| DD-weird variant | In that same airborne `notjump` branch, **exact** vertical velocity `−240.0` independently assigns `Type_WeirdLongJump`, sets `ddbeforwj`, and chooses `DDWJ` localization keys. | 3181–3189. No distinct enum is assigned. |
| Drop-bhop detection | Alternative airborne branch: `!notjump`, not flying, not `in_ladder`, type not Slide. A drop from stored normalized `dropbjorigin.z` >2 assigns `Type_Drop_BhopLongJump`, clears bhop windows, sets `dropbhop`. If drop <30 and old type neither Drop-Bhop nor None, save old type and its strings. | 3192–3222. |
| Ladder entry | Flying sets ladder-check time; first flying observation sets `firstladder`, clears bhop/height flags, requests reset and returns. | 3225–3244. |
| Ladder movement arm | Flying plus Forward/Back/**IN_LEFT/IN_RIGHT** sets `ladderjump`, searches ladder within 18, stores its index if found, and snapshots pre/max. These keys are not the A/D `IN_MOVELEFT/IN_MOVERIGHT` symbols. | 3245–3263. |
| `Type_ladderBhop` from ladder jump | Flying plus Jump assigns ladder-bhop keys; clears ladderjump/in-air/in-ladder/bhop, sets `notjump`, clears dropbhop. | 3265–3275. |
| `Type_ladder` departure | No longer flying while `ladderjump` is true initializes active ladder flight, special J/offset, timestamps and strafe state. There is no additional Jump-button requirement in this branch. | 3278–3354. |
| `Type_Real_ladder_Bhop` | In ordinary grounded takeoff's non-nextbhop arm, `in_ladder` is true: clear it and assign real-ladder-bhop. A later `oldjump_typ1==1` rule can replace it with ladder-bhop. | 3627–3669. No producer sets `oldjump_typ1` to 1 in this `.sma`; its only visible assignment clears it to 0 (3668). |

### 4.3 Bhop, standup, duck and up branches

| Branch | Actual predicate and assignment | Source |
|---|---|---|
| Next-bhop setup | Main grounded press gate plus `nextbhop && !ddafterJump`: initialize active bhop, save previous J, reset numbered-strafe stats, snapshot pre/max. Reject if `cjjump && now−duckoff_time <0.2`. | 3502–3625. |
| Duck-bhop arm | In next-bhop setup, old and current Duck held, `duckbhop` true, and type HJ/LJ/None → `Type_DuckBhop`, then clear `duckbhop`. | 3539–3544. |
| Up arm | In next-bhop setup, `checkbhop <−1` → `upBhop=true`, save `upheight`, call missing `UpBhop_calc`; current Duck held also assigns `Type_Up_Bhop_In_Duck`. | 3562–3578. |
| Non-up induck arm | Otherwise, if type is not DuckBhop and current Duck held → `Type_Bhop_In_Duck`. Button state, not an induck-frame percentage. | 3580–3585. |
| First airborne up classification | `first_frame && in_bhop && type != DuckBhop && upBhop`: preserve Up-Bhop-In-Duck if already set; else `velocity.z < upbhop_koeff` → `Type_Up_Bhop`; otherwise → `Type_Up_Stand_Bhop`; clear `upBhop`. | 2940–2976. Numerical coefficient unavailable. |
| First airborne ordinary classification | Same first-frame bhop gate without up arm: preserve Bhop-In-Duck; else `velocity.z <229.0` → `Type_BhopLongJump`; otherwise → `Type_StandupBhopLongJump`, also restoring `J.z = pre_jumpoff_origin.z`. | 2978–2995. Exact 229 goes to standup. |
| `Type_Multi_Bhop` | Separate new grounded Jump press arm with `bhopaem && !ddafterJump && !slide_protec && !UpcjFail`; rejects `ddforcj`, initializes active jump and pre/max, assigns Multi-Bhop and increments `bhop_num`. | 4006–4094. Unlike next-bhop setup, no visible `in_bhop=true` assignment here. |
| Early release/duck-bhop arm | Grounded release of Jump, `nextbhop && !cjjump && !bhopaem`, type not Drop-Bhop, no protections or `ddafterJump`: old/current Duck and `duckbhop` plus LJ/None → DuckBhop; otherwise sets `bhopaem=true` and optionally shows early warning. | 4096–4134. This arm itself does not initialize a new measured flight. |
| Preparing `duckbhop` | In low-pre fallback to LJ, normalized J Z differs from current origin by exactly 18, old/current Duck held and flag previously false → `duckbhop=true`; else clear it. Nearby ladder sets protection flags. | 3737–3765. |

### 4.4 Count-jump chain and all subtypes

**Duck start gate:** not active air; a new Duck press; grounded or `posible_dropcj`; not `in_duck`; no `UpcjFail` (`6221`). `posible_dropcj` is allowed only for a new Duck during Drop-Bhop/Weird type when a downward trace finds the foot-relative hit within 18 units (`6197–6217`).

| Transition | Exact branch | Source |
|---|---|---|
| Start chain | If `now−duckoff_time >=0.3`, set ducks to 1, `prest1=speed`, `duckstartz=origin.z`, store `statsduckspeed[1]`, set `started_cj_pre`. Save normalized `first_duck_z`. | 6261–6293. |
| Extend chain | If `now−duckoff_time <0.3`, set `started_multicj_pre`, `prest=speed`, increment ducks and store speed. Normalized current Z >first duck Z+4 rejects/reset. | 6223–6247. |
| Drop chain | Starting chain with `!dropupcj && now−FallTime <0.3` and ladder/drop/weird/dropbhop history → `Type_Drop_CountJump`, `multidropcj=0`, `dropaem=true`; clear ladder/drop state. | 6294–6307. |
| Complete first duck | Not active air, old Duck held, grounded/possible-drop, no UpcjFail, and **not physically ducked**. If `started_cj_pre`, update duckoff timestamp/origin, clear flag; non-drop → `Type_CountJump`, `jump_typeOld=1`; drop keeps Drop-Count and sets `multidropcj=0`. | 6324–6368. |
| Complete second duck | Same completion gate; `else if started_multicj_pre`: non-drop → `Type_Double_CountJump`, `jump_typeOld=2`; drop → `multidropcj=1`, `jump_typeOld=2`. | 6370–6407. |
| Complete third or later duck | After either branch, independent `if ducks>2`: non-drop → `Type_Multi_CountJump`, `jump_typeOld=3`; drop → `multidropcj=2`, `jump_typeOld=3`. | 6409–6437. More than three ducks does not create a new enum. |
| After-jump modifier | For each non-drop completion above, either `nextbhop` or `bhopaem` sets `CjafterJump=1/2/3`, `ddafterJump=true`, and CJAJ/DCJAJ/MCJAJ keys; otherwise resets those modifiers and uses normal keys. | 6344–6360, 6385–6400, 6415–6430. Duck-start code also clears bhop windows, so this condition's execution depends on intervening state changes; the presence of this branch is not proof it is always reachable. |
| Direct duck-after-jump conversion | Outer gate allows tracked `x_jump` or ladder plus grounded new Duck press, but the changing-state body additionally requires `x_jump`. It rejects higher normalized landing unless ladder; records `ddforcjafterbhop`/`ddforcjafterladder`, sets `ddforcj`. Independently, new grounded duck presses increment `ddnum`. | 3357–3402, 3434–3444. |
| Conversion at actual jump | Main takeoff with `ddforcj`: if StandUp-Count, mark `ddstandcj`; clear ddforcj. If not StandUp-Count and either not Drop-Count or after-ladder: ddnum 1/2/≥3 → Count/Double/Multi and `CjafterJump=1/2/3`; clear ddnum/bhop windows. | 3466–3496. ddnum=0 has no assignment arm. |
| Standup-count detector | Not `cjjump`, old or current Duck, and Drop-Count/ddforcj/ddafterJump/Count/Double/Multi history; **`−2.0 < origin.z−duckstartz <−1.21`** → `Type_StandUp_CountJump`; copy prior chain selector `jump_typeOld` 1/2/3 to `multiscj` 0/1/2; refresh FallTime. | 3405–3432. No numerical mapping for another prior selector is supplied. |

**Standup-count output has nine visible subtype branches**, priority `dropaem` → `ddstandcj` → ordinary (`4799–4861`):

| `multiscj` | `dropaem=true` | Else `ddstandcj=true` | Else |
|---|---|---|---|
| 0 | DROPSCJ keys; HUD type 29 | SCJAF keys; HUD type 32 | Base SCJ state; HUD type 35 |
| 1 | DROPDSCJ keys; HUD type 30 | DSCJAF keys; HUD type 33 | DSCJ keys; HUD type 36 |
| 2 | DROPMSCJ keys; HUD type 31 | MSCJAF keys; HUD type 34 | MSCJ keys; HUD type 37 |

For Drop-Count, `multidropcj=0/1/2` selects HUD types 26/27/28; selectors 1/2 change `Jtype` to DROPDCJ/DROPMCJ (4782–4797). For ordinary Count/Double/Multi, matching `CjafterJump=1/2/3` branches further prioritize **after-bhop**, then **after-ladder**, then generic **after-jump**; without the matching modifier they use normal Count/Double/Multi (`4678–4704`, 4721–4775). The words in uppercase here identify visible key suffixes, not recovered translation text.

### 4.5 Takeoff and finalization reclassification

| Rule | Predicate and replacement | Source |
|---|---|---|
| Drop state at takeoff | In non-nextbhop main takeoff, `dropbhop && type not Drop-Count/StandUp-Count` → Drop-Bhop, then clear dropbhop. | 3699–3704. |
| Count flight arm | Count/Double/Multi set `cjjump=true`. | 3706–3709. |
| Height-mismatched count | Count/Double/Multi, neither `ddstandcj` nor `CjafterJump`, and `abs(duckstartz−J.z)>4`: speed <200 → LJ; otherwise → Weird. | 3710–3724. Exactly 200 goes Weird. |
| Drop-count height rejection | Drop-Count selector 0 and `origin.z−first_duck_z >4` → reset and return. | 3726–3729. |
| Low-pre LJ fallback | Let `k = 1.112*Pmaxspeed`. With `pre<k`, exclude Ladder-Bhop, Drop-Bhop, Weird, Count/Double/Multi, Bhop/Standup-Bhop and Drop-Count; nested exclusions also preserve StandUp-Count and Real-Ladder-Bhop. All remaining types → LJ. | 3731–3743. It is not an unconditional default. |
| High-pre LJ at takeoff | Existing LJ with `pre>k` → Weird. | 3801–3807. Equality matches neither strict threshold. |
| Restore temporary drop label | At finalization, if saved old type is not Null and current type Drop-Bhop, restore old enum and strings. | 4137–4142. This restores any label saved by the shallow-drop rule, not only LJ. |
| HJ detection | During active flight, trace downward 133 from `(current x,y,J.z+28)`. Hit depth `d` strictly between 64 and 133 sets `detecthj=2`; depth ≥133 sets `detecthj=1` only if flag not 2. Once flag 1, probe is skipped. Final LJ plus flag 1 → HJ. | 3078–3098, 4419–4423. A prior flag 2 prevents HJ promotion even if a later probe clears 133. |
| High-pre final LJ/HJ | Final LJ/HJ with `pre>1.112*Pmaxspeed` → **Drop-Bhop**, not Weird. | 4425–4433. This is a different replacement from takeoff. |

### 4.6 Display-only/unknown numeric branches

The numeric HUD switch at `4674–4868` has cases 0,1,2,3,4,5,6,7,9,11,12,13,15,16,17,18,19,20,21,22,23,24; cases 8,10,14 are absent. Some are linked to named types by nearby comments and independent comparisons, but **the enum declaration is missing**. Case 4 is commented `//??`; case 12 `//nothing`; cases 16 and 20 have only localization keys. Do not invent jump mechanics or official names for those unconstructed branches. `Type_Nothing` and `Type_Nothing2` are excluded from map-top eligibility (5026), but their producers and numeric identities are not visible. `Type_None` is the reset state and `Type_Null` a saved-type sentinel, not verified reportable techniques.

For completeness, every numeric dispatch arm is retained here; numbers in the second column are suffixes of **`UQSTATS_HUD_JUMPTYPE<n>`**, not inferred enum IDs:

| Numeric case | Key suffix / branch selection |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 2 | Matching `CjafterJump==1`: after-bhop→3, else after-ladder→4, else→5; without modifier→6 |
| 3 | 7 |
| 4 | 8 |
| 5 | 9 |
| 6 | `!ddbeforwj`→10; otherwise→11 |
| 7 | 12 |
| 9 | Matching `CjafterJump==2`: after-bhop→13, else after-ladder→14, else→15; without modifier→16 |
| 11 | Matching `CjafterJump==3`: after-bhop→17, else after-ladder→18, else→19; without modifier→20 |
| 12 | 21 |
| 13 | 22 |
| 15 | 23 |
| 16 | 24 |
| 17 | 25 |
| 18 | `multidropcj` 0/1/2→26/27/28; no other-selector arm |
| 19 | Drop 0/1/2→29/30/31; else after-state 0/1/2→32/33/34; else normal 0/1/2→35/36/37; no other-selector arm |
| 20 | 38 |
| 21 | 39 |
| 22 | 40 |
| 23 | 41 |
| 24 | 42 |

There is no default arm. Drop-Count selector 1/2 updates `Jtype` but not `Jtype1` in this switch (4791, 4796), unlike StandUp-Count variants which update both. Therefore different output/storage paths need not carry equally specific text labels.

## 5. Acceptance, failure and report filtering

Classification and statistical validity are different. A reset may suppress output entirely; `failed_jump=true` may preserve output but block ranking.

### Height acceptance before distance

For local `failed == false`, using `h = height_difference` (`4201–4250`):

| Type family | Exact height rules |
|---|---|
| Bhop, Standup-Bhop, Bhop-In-Duck | Reject `h<−22`. Also reject `−18<h<=−1`. The interval `−22<=h<=−18` survives these negative-height checks. |
| All other types | Reject `h<−1`, except Drop-Bhop and StandUp-Count at **exactly −18**. |
| Standup-Bhop afterward | `h>1` sets failed flag; `0<h<=1` survives. |
| Any other non-Drop-Bhop afterward | `h>0` resets and returns. |
| Drop-Bhop afterward | `h>0.02` sets failed flag; positive values up to 0.02 survive. |
| Ladder additional check | `abs(J.z−normalized current origin.z)>4` sets failed flag (4260–4263), but earlier general height checks also apply. |

### Distance window

`tmp_dist = floor((250−Pmaxspeed)*0.73)` when weapon maxspeed differs from 250 and type is not Ladder; ordinary minimum becomes `min_distance−tmp_dist` (`4369–4380`). Defaults: `min_distance=215`, `min_distance_other=120`, maximum 290 (`238–239`, 317, 615–617). Bounds are inclusive; outside resets (`4382–4408`).

| Type | Minimum |
|---|---|
| Ordinary types except the explicitly listed exceptions below | Adjusted ordinary minimum |
| Ladder, Multi-Bhop, Real-Ladder-Bhop, Bhop-In-Duck, Up-Bhop-In-Duck, Up-Bhop, Up-Stand-Bhop | `min_distance_other` (not weapon-adjusted) |
| DuckBhop | Adjusted ordinary minimum **minus 150** (65 with defaults and maxspeed 250), not its chat “good” threshold 120 |

Additional visible checks:

- Grounded/flying/airborne state and legal settings constrain observations. Normal speed above 450 resets (1400 for two specially named slide maps); a maxspeed change also resets (2262–2277). With legal checks enabled, settings must match edgefriction 2, player gravity 1, footsteps 1, cheats 0, gravity 800, selected AA, maxspeed 320, stepsize 18, maxvelocity 2000, and waterlevel <2 (2280–2291).
- Two detected integer-fraction vertical-velocity observations can set `bug_true`; finalization then resets (2879–2886, 4144–4147). The state logic does not visibly clear the intermediate flag on a noninteger sample; do not describe it as a proven consecutive-frame test.
- `!uq_noslow && fuser2==0` for non-ladder sets failed; high-FPS heuristic for non-ladder sets failed; DuckBhop pre>200 sets a bug flag and later failed (4149–4153, 4356–4366). These are not alternative distance producers.
- `check_for_bug_distance(distance,t_type,Pmaxspeed)` is a **missing helper**. Its argument group comes from numeric cases: 0/1→1; 2/9/11/6/7/15/17/18/19→2; 3/5/21/22→3; 13→4; 23/24→5; 12→6; everything else remains 0 (4455–4484). Do not infer absent enum mappings from this alone.
- When bug checking is enabled, `(maxspeed+prestrafe)/distance <2.1` resets, or `<2.0` for Ladder (4486–4499).
- Any numbered strafe record-gain >40 resets unless Ladder, Real-Ladder-Bhop or Slide (5007–5013). Loss >200 with `Checkframes` sets failed; loss >200 also marks `duckstring` (4585–4594).
- `not_save=true` when pre exceeds `Pmaxspeed*1.2` and noslow is off (or the earlier LJ/HJ strict `1.112` condition); this blocks saving, not necessarily display (4531–4540, 5021). The earlier final reclassification can already have removed LJ/HJ before that LJ/HJ test.
- Script heuristic checks more than four strafes, entity-angle component `[0]` equality count above missing `SCRIPTFRAMES`, distance above selected tier, detection enabled and `!not_save`. `FullJumpFrames>80` sets failed; otherwise `find_script` eventually sets failed (4544–4549, 4659–4662). This is not a strafe-angle metric.
- Every implemented technique has enable/disable output gates (4876–5004), including StandUp-Count's six normal/drop selector combinations and Drop-Count's three selectors. Multi-Bhop additionally resets/suppresses when the player's `multibhoppre` toggle is false (5016–5019). Map top excludes `ddstandcj` and after-jump count variants and requires maxspeed 250 (5026); Count/Double/Multi tops also exclude after-jump variants (5031, 5060, 5089). StandUp-Count tops exclude `ddstandcj` (5308–5427).

## 6. Additional measured values and output tiers

### Extra pre-jump/frame values

| Value | Visible meaning | Source |
|---|---|---|
| `prest1` | Ground speed at the first duck-start of a new chain. | 6265–6269; console 5881, 5890. |
| `prest` | Speed at a subsequent duck-start within the <0.3s continuation window. | 6223–6228; console 5891. |
| `statsduckspeed[n]` | Snapshot at nth duck start; display loops start at array index 2 and label it `n−1`. | 6228, 6269, 5692–5694, 5882–5883. This presentation is intentionally offset from the stored duck index. |
| `ducks` | Number of recognized duck starts in chain, not airborne crouched frames. | 6227, 6265–6267. Array capacity is 500 (61); no visible bound check before indexed writes. |
| `bhop_num` | Increment in Multi-Bhop initialization; reset to 0 at ordinary main takeoff/early-release handling. | 3464, 4073, 4108. Not every raw jump press increments it. |
| Duck sync (`dd_sync`) | Good/bad post-think speed comparison while `!g_Jumped && sync_doubleduck`; no key requirement. At takeoff, `floor_integer(100*good/(good+bad))`, then add **5 if result <96**; denominator 0 →0. | 3434–3450, 3811–3822, 7932–7950. Raw 95 becomes 100; raw 96 stays 96; raw 0 with nonzero denominator becomes 5. This is discontinuous and not interchangeable with air sync. |
| `SurfFrames` / FPS heuristic | Absolute difference of alternating captured vertical velocities; sampled during the first two airborne observations, reuses old value if difference >41. If airborne `SurfFrames<7.9` and FPS gate enabled, mark high FPS; grounded `SurfFrames>7.9` clears it. | 2442–2495. It is not a directly measured FPS or a precise frames-per-second value. |
| Entity-angle `[0]` equality count | Increment when `abs(current_angles[0]−old_angles[0])==0` during active flight; update saved full angles afterward. | 2808–2824. Reset at 2109 and 3506; saved old angles are not visibly reset there. Not a raw mouse/view-motion recording. |
| Duck/no-duck annotation | `duckstring=true` when currently crouched at final coordinate normalization; also forced true on per-strafe loss >200. Its false branch appends a localization annotation. | 4306–4309, 4585–4589, 4604–4606. Not proof that the whole jump was crouched or uncrouched. |
| Beam points | Up to 100 origin samples, each with crouched and movement-input metadata. | `fnSaveBeamPos:8094–8123`. Sample cap is not jump duration; no induck counter is derived here. |

### Distance achievement tiers are separate from jump technique

`get_colorchat_by_distance:7954–8092` returns thresholds in order good/pro/holy/leet/god. Defaults below come from `plugin_init:154–236`; configured values loaded by `plugin_cfg` replace them.

| Technique family routed by function | Defaults: good / pro / holy / leet / god |
|---|---|
| LJ, HJ | 240 / 245 / 250 / 253 / 255 |
| Count | 250 / 255 / 260 / 265 / 267 |
| Double/Multi-Count | 250 / 255 / 260 / 265 / 270 |
| Ladder | 150 / 160 / 170 / 180 / 190 |
| Weird, **all Drop-Count selectors**, Ladder-Bhop | 255 / 260 / 265 / 270 / 272 |
| Bhop, Standup-Bhop | 230 / 235 / 240 / 245 / 247 |
| Drop-Bhop | 240 / 250 / 265 / 270 / 272 |
| StandUp-Count, not drop, selector 0 | Base 245 / 250 / 255 / 260 / 262, plus `aircj` |
| StandUp-Count, not drop, selector 1 or 2 | Same base plus `aircj +10` |
| StandUp-Count, drop, any selector | 255 / 260 / 265 / 270 / 272 |
| Bhop-In-Duck, Up-Bhop-In-Duck | 205 / 210 / 215 / 218 / 220 |
| Up-Bhop | 225 / 230 / 235 / 240 / 245 |
| Up-Stand-Bhop | 230 / 235 / 240 / 244 / 246 registered defaults; **its good cvar name incorrectly duplicates `kz_uq_good_upbj`** (232). Distinct configured good thresholds are therefore not assured. |
| Real-Ladder-Bhop | 240 / 250 / 265 / 270 / 272 |
| DuckBhop | 120 / 130 / 140 / 150 / 160 |

`aircj=0` for configured AA≤10 except alias 1; otherwise 10. Alias 0 means 10AA and alias 1 means 100AA (`2236–2260`). This adjustment affects only the non-drop StandUp-Count family in this function. For non-250 maxspeed and non-Ladder, all five thresholds subtract `tmp_dist=floor((250−Pmaxspeed)*0.73)` (4370–4373, 8084–8090); this changes thresholds, **not measured distance**.

No explicit Multi-Bhop family exists here: unmatched types retain initializer `[0,0,280,0,0]` (7956–7958). Multi-Bhop also has no ordinary/multi-count chat announcement arm (`6044–6115`); do not claim it uses Bhop tiers. Announcement tier priority is `distance>=god`, else `>=leet`, else `>=holy`, else `>=pro`, else `>=good`, only if not failed (6051–6112). Below good produces no such announcement. Invalid or nonmonotonic configuration is not sorted or validated by this function.

## 7. Precision, inconsistencies and verification limits

### Verified limits to preserve in interpretation

1. **Distance is not universal horizontal path length:** 3D norms, min of observed/projected endpoints, 32 or ladder offset, and a wholly different slide vertical metric.
2. **Failure status is not a distance-method tag:** the local `failed` snapshot can differ from later `failed_jump`.
3. **Gain is asymmetric with loss:** new record increases versus every sampled decrease; summing displayed numbered-strafe gains omits slot 0 and need not equal overall gain.
4. **No true angle history update is visible:** `old_angle1` is declared (48) and compared (7824, 7828), but no assignment updates it anywhere in the supplied `.sma`. The comparisons therefore cannot be assumed to mean previous-frame yaw. A missing include could change global state; that possibility is unverified, not a repair to the visible code. Yaw wraparound correction is also absent.
5. **Frame endpoints differ:** FullJumpFrames is post-think while active; duration ends at last airborne pre-think; sync excludes no-key samples and slot 0; beam points stop at 100. These denominators are not interchangeable.
6. **Block selection is not a reliable minimum:** self-comparisons, zero candidates, marked-branch retention, last-probe edge overwrite and strict dominant-axis ties remain real source limitations.
7. **Exact-equality gates are brittle:** vertical velocity `−240`, a standup-count height exception of exactly `−18`, and block-probe equal Z tests do not use tolerances. The code's strict/open intervals must not be replaced with rounded report values when explaining classification.
8. **Bounds/truncation:** integer sync division discards fractional percentage; block distance is `floor+1` (even an exact integer is increased); slide `.xxx` intentionally hides precision; stat strings are limited to `40*NSTRAFES`, and console extraction uses a 40-cell line buffer (`4554–4579`, `5865–5870`). Exact final numerical formatting in localized output cannot be verified without the dictionary.
9. **Stored precision differs from displayed precision:** local tops round `distance`, maxspeed and prestrafe multiplied by 1,000,000 (`checktops1:7187–7191`); block top rounds distance likewise (`checktops_block:7364–7366`). These are scaled integer storage values, not proof of six-decimal measurement accuracy. SQL behavior is missing.
10. **No compile/runtime verification:** missing includes prevent reconstructing helper behavior and enum capacities; this document is a static trace, not proof of physical accuracy, runtime reachability of every branch, or compatibility with another report version.

### Source-only acceptance checklist

- [x] Successful distance traced to both candidates and minimum selection.
- [x] Failed helper call documented without inventing its body.
- [x] Ladder/slide exceptions and late-failure distinction covered.
- [x] Every visible named jump-type assignment and subtype-selection family recorded.
- [x] Requested but absent fields kept distinct from related flags/counters.
- [x] Geometric selection, sampling, integer arithmetic and missing-dependency limits surfaced.

**Next evidence needed:** the exact includes and translation dictionary used by the running plugin, plus an actual requested report sample/version, before equating this source's output with a richer metrics report.
