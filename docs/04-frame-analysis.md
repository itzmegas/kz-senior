# Frame analysis: what this source actually measures

**The supplied JumpStats 2.42 source implements speed-based sync, button-based strafe segments, aggregate gain/loss, and a post-jump frame visualization. It does not supply a `/dt` report or definitions for `[MAIN]`, `[DETAILED]`, efficiency, overlaps, desync, or an ideal/error angle.** Those requested meanings cannot be reconstructed faithfully from this file alone.

## Evidence boundary

- Only `reference/uq_jumpstats.sma` was analyzed: 9,364 lines, SHA-256 `D4D786AF106886659BA4D3EEE8698C196679CFDB1E1148E5CDD15934120701E5`. The source was not edited.
- Citations use `file:function:line` or `file:function:first-last`; `globals` means declarations outside a function. All line numbers refer to this source snapshot.
- **Confirmed** means visible source behavior, not a successful compilation or an observed game session. **Derived** means an explicit consequence of that behavior. **Unavailable** means the supplied artifacts do not establish it. Hypotheses are labeled separately.
- Includes, notably `uq_jumpstats_const.inc` and `uq_jumpstats_stocks.inc`, are absent. Constants such as `NSTRAFES`, `NVAR`, `SCRIPTFRAMES`, `INFO_ONE`, and `INFO_ZERO` therefore have no verified definitions here. The usual interpretation of `INFO_ONE`/`INFO_ZERO` as 1/0 is not independently established. Dictionary text is also unavailable: the source registers `uq_jumpstats.txt`, but shows localization keys rather than the rendered column labels. Evidence: `reference/uq_jumpstats.sma:includes:12-22`; `reference/uq_jumpstats.sma:plugin_init:148-152`.

## 1. Requested `/dt` fields versus available evidence

A case-insensitive, whole-file literal search returned **zero matches** for `/dt`, `[MAIN]`, `[DETAILED]`, `efficien`, `overlap`, and `desync`. This was checked against command registration, the general command handler, menu construction, metric production, and output consumers—not just inferred from the search.

| Requested item | Finding | Closest confirmed behavior; not an equivalence |
|---|---|---|
| `/dt` | **Unavailable:** no visible registration or report handler | `/stats`/`/ljstats`/`/uqstats`, `/strafe` aliases, `/istrafe`, and `/beam` aliases are registered instead. `reference/uq_jumpstats.sma:plugin_init:359-418` |
| `[MAIN]` / `[DETAILED]` | **Unavailable:** neither literal nor a visible two-tier report contract | General jump HUD and console output plus per-strafe rows. Three option menus select toggles, not these report tiers. `reference/uq_jumpstats.sma:fwdPreThink:5726-5871`; `reference/uq_jumpstats.sma:Option:8906-9004`; `reference/uq_jumpstats.sma:Option2:9060-9122`; `reference/uq_jumpstats.sma:Option3:9199-9283` |
| Efficiency | **Unavailable:** no ideal acceleration, optimal-speed denominator, or efficiency formula is visible | Sync is a ratio of speed-increasing versus non-increasing eligible samples; gain is maximum speed minus prestrafe. `reference/uq_jumpstats.sma:fwdPostThink:7889-7919`; `reference/uq_jumpstats.sma:fwdPreThink:4670-4672,4873-4874` |
| Overlaps | **Unavailable as a metric:** no named overlap counter, duration, percentage, or report column | Multiple movement buttons prevent a new segment and clear remembered segment buttons, but still qualify for speed-based sync. `reference/uq_jumpstats.sma:fwdPostThink:7836-7930` |
| Desync | **Unavailable:** no input-to-turn mismatch percentage or timing-error formula | Non-increasing speed is called the bad-sync bucket; it is not a separately established desync definition. `reference/uq_jumpstats.sma:fwdPostThink:7895-7905` |
| Angle | **Partly available as inputs, unavailable as the requested metric** | Component `[1]` drives nominal turn flags; unchanged component `[0]` increments `angles_arry`. Neither becomes an ideal/error angle report. `reference/uq_jumpstats.sma:fwdPostThink:7811-7834`; `reference/uq_jumpstats.sma:fwdPreThink:2806-2825` |

The generic `client_command` strips `/` or `.` to compare a fixed list of reset/teleport commands; it does not dispatch a hidden `/dt`. Evidence: `reference/uq_jumpstats.sma:client_command:1428-1477`.

**Hypothesis only:** `/dt` could belong to a different plugin, version, or omitted include. Nothing supplied identifies which one or proves that hypothesis. Likewise, absent dictionary text could contain a familiar label, but a label alone would not establish the missing calculation. Do not rename the available sync/gain/beam values to the requested metrics.

## 2. Sampling and state: what “frame” means here

The source registers `fwdPreThink` and `fwdPostThink` under the corresponding player-think forwards. This report uses **sample** for an execution of those paths; it does not assume each sample equals one rendered client frame or one raw input command. No user-command duration/history is collected in the visible measurement path. Evidence: `reference/uq_jumpstats.sma:plugin_init:434-436`; `reference/uq_jumpstats.sma:fwdPreThink:2183-2202`; `reference/uq_jumpstats.sma:fwdPostThink:7813-7821`.

| Stage | Confirmed operations |
|---|---|
| PreThink admission | Connected non-bot player; optional admin restriction; alive and selected team. There are additional early exits for invalid states. `reference/uq_jumpstats.sma:fwdPreThink:1996-2004,2093-2094` |
| PreThink baseline | Reads `pev_button`, `pev_oldbuttons`, flags, origin, velocity, and movement type. Z velocity is removed before `speed[id] = vector_length(velocity)`, so this baseline is horizontal speed. `reference/uq_jumpstats.sma:fwdPreThink:2183-2202` |
| Airborne PreThink accumulation | Requires `in_air`, not on ground, and not already failed. Tracks the angle heuristic, beam samples, maximum-speed increases, and preceding-PreThink speed losses. `reference/uq_jumpstats.sma:fwdPreThink:2806-2825,2888-2926` |
| PostThink accumulation | Alive, connected, non-bot, and `g_Jumped`; increments `FullJumpFrames`, reads buttons/angles, and measures horizontal speed again. This gate does **not** repeat PreThink's team/admin/ground/failed checks. `reference/uq_jumpstats.sma:fwdPostThink:7799-7821` |
| Finalization | A branch for `(failed_jump || on-ground) && in_air` performs result calculations/output, subject to further validation/early exits, then calls `JumpReset`. `reference/uq_jumpstats.sma:fwdPreThink:4135-4147,6119-6193` |
| Reset | `JumpReset` requests a reset; the next admitted reset block clears jump flags, total counters, beam samples, and optional frame-marker state. Per-strafe arrays are also cleared in the takeoff paths. `reference/uq_jumpstats.sma:JumpReset:8125-8130`; `reference/uq_jumpstats.sma:fwdPreThink:2107-2180,3770-3788` |

Three distinct counters must not be conflated:

- `FullJumpFrames` increments in the active-jump PostThink path, regardless of movement-button presence. It is used by the beam baseline and anti-script gate. `reference/uq_jumpstats.sma:fwdPostThink:7803-7806`; `reference/uq_jumpstats.sma:fwdPreThink:4544-4549,5721`.
- `frames` and `frames_gained_speed` increment in the narrower airborne PreThink path; the latter compares to a static `old_speed`, which is then updated. The visible file contains no consumer calculating sync from this pair, and no visible reset of `old_speed`. `reference/uq_jumpstats.sma:fwdPreThink:2136-2137,2892-2899`.
- Per-strafe good/bad counts are produced by **PostThink speed versus the saved PreThink baseline**, only with at least one of the four movement buttons held. `reference/uq_jumpstats.sma:fwdPostThink:7889-7919`.

Consequently, `FullJumpFrames` need not equal the final sync denominator. PreThink early exits also mean the visible code does not guarantee a freshly updated baseline on every PostThink execution.

## 3. Strafe segmentation: buttons plus nominal turn flags

### Actual segment boundary rule

`buttonsNew` and `buttons` are both reads of the current `pev_button`; `buttonsNew` is not a separately captured input-edge structure. The edge test uses the plugin's own `strafecounter_oldbuttons`. Evidence: `reference/uq_jumpstats.sma:fwdPostThink:7808-7815,7836-7838`.

A new segment requires:

1. Exactly one of `IN_MOVELEFT`, `IN_MOVERIGHT`, `IN_BACK`, `IN_FORWARD` is held; the other three must be absent.
2. That key is absent from `strafecounter_oldbuttons`.
3. Either `turning_left` or `turning_right` is true. **There is no requirement that the chosen key match the particular turn direction.**

On a match, the current slot receives a timestamp, `strafe_num` increases by `INFO_ONE`, and the new slot receives a key-family tag: left/right = 1, back/forward = 2. `button_what` groups left/back as 1 and right/forward as 2 for trajectory-beam colors. Evidence: `reference/uq_jumpstats.sma:fwdPostThink:7836-7887`.

The remembered-button mask is cleared when multiple movement keys are held. Otherwise it updates only when one of the nominal turn flags is true; without a flag it can remain stale. Thus returning from a multiple-key state to one key can start a segment even without a physical release of that key. There is no visible separate overlap statistic. Evidence: `reference/uq_jumpstats.sma:fwdPostThink:7921-7930`.

### Important limitation: the yaw baseline is not visibly updated

The nominal turn calculation compares `old_angle1[id]` with `pev_angles[1]`: smaller current value means `turning_right`, larger means `turning_left`, equality means neither. However, **`old_angle1` appears only in its global declaration and these two comparisons; this file never assigns the current angle back to it.** Evidence: `reference/uq_jumpstats.sma:globals:48`; `reference/uq_jumpstats.sma:fwdPostThink:7824-7834`.

Therefore this snapshot does not establish frame-to-frame yaw-change detection. Taken literally without hidden include effects, it compares against the initial global value, not the preceding sample. It also contains no angle-wrap normalization in that comparison. A faithful description must preserve this discrepancy rather than silently substituting an intended previous-yaw update. Missing include contents prevent proving the complete compiled program's behavior.

### Slot zero and time attribution

- Takeoff paths reset the segment count/mask, speed buffers, sync buckets, timestamps, and no-button counts; for example the ordinary path sets `strafe_num = 0`, clears the mask, initializes prestrafe/maxspeed, and clears arrays. `reference/uq_jumpstats.sma:fwdPreThink:3650,3682-3683,3731-3732,3768-3788`.
- Before a recognized first segment, speed/sync samples can accumulate in **slot 0**. The report sums only slots `1..strafe_num`, so slot-0 sync and loss are excluded from reported sync/rows. Ladder slot-0 gain has a separate output exception. `reference/uq_jumpstats.sma:fwdPreThink:2901-2911,4562-4583,4600-4602,5874-5876`; `reference/uq_jumpstats.sma:fwdPostThink:7895-7903`.
- A new segment timestamps the **old** slot before incrementing. At finalization slot 0 is overwritten with `jumpoff_time`, and the last segment slot with `last_land_time`. The row time is `100 * (timestamp[j] - timestamp[j-1]) / Fulltime`, where `Fulltime = last_land_time - jumpoff_time`. Thus the first row includes time before the first recognized segment; it is not a perfect count of that segment's input samples. `reference/uq_jumpstats.sma:fwdPostThink:7843-7847,7856-7860`; `reference/uq_jumpstats.sma:fwdPreThink:4561-4570`.
- Despite its name, `last_land_time` is refreshed while **not on ground**. It is the last such recorded sample, not a proven exact physical landing time. This calculation does not use the separately extrapolated `frame2time`; there is no visible zero-`Fulltime` guard at row calculation. `reference/uq_jumpstats.sma:fwdPreThink:2318-2322,4314,4561-4570`.

The configurable maximum defaults to 14; exceeding the configured value requests a reset and returns at the next PreThink check. This is separate from the unknown compile-time array capacity `NSTRAFES`. Evidence: `reference/uq_jumpstats.sma:plugin_init:319`; `reference/uq_jumpstats.sma:fwdPreThink:2209-2220`.

## 4. Sync: exact numerator, denominator, and exclusions

Within active-jump PostThink, if **any** of left/right/forward/back is pressed and the current slot is within `NSTRAFES`:

| Condition | Update |
|---|---|
| PostThink horizontal `fSpeed > speed[id]` saved in PreThink | Add `INFO_ONE` to `strafe_stat_sync[id][slot][0]` (good) |
| Otherwise, including equal speed | Add `INFO_ONE` to `[1]` (bad); optionally mark the sample red in `line_lost` |
| No movement button | Neither good nor bad; optionally increment `strafe_lost_frame` instead |

Evidence: `reference/uq_jumpstats.sma:fwdPostThink:7889-7919`.

**No actual turn, correct key/turn pairing, or exclusive one-key input is required for a sync sample.** Exclusive input is a segmentation condition, not a sync condition. A multiple-key sample can be good or bad based solely on the speed comparison.

At finalization:

- Row sync = `good[j] * 100 / (good[j] + bad[j])` when that denominator is positive; otherwise 0.
- `goodSyncTemp` and `badSyncTemp` are scalar scratch totals reset for this finalization, then filled by summing rows `1..strafe_num`. They are not raw per-frame state or per-player history.
- Overall sync = `goodSyncTemp * 100 / (goodSyncTemp + badSyncTemp)` when the good total is positive; otherwise `INFO_ZERO`. Arithmetic is integer-valued, unlike the row-time percentage.

Evidence: `reference/uq_jumpstats.sma:globals:57-58`; `reference/uq_jumpstats.sma:fwdPreThink:4552-4583,4670-4672`.

**Derived example, not a captured jump:** with `INFO_ONE = 1`, 3 good and 2 bad counted samples yield 60% sync. Extra no-button samples do not change that percentage. This does not quantify efficiency against optimal acceleration, time-weight samples, or diagnose why a sample failed to gain speed.

### Double-duck sync is a different metric

`sync_doubleduck` is enabled by a new ground duck press and cleared, with its buckets reset, when the jump is active. Outside `g_Jumped`, the PostThink fallback compares horizontal post speed with `speed[id]` and increments double-duck good/bad counts **without checking movement buttons**. Its displayed `dd_sync` is the bucket ratio, then receives **+5 if below 96**, or is 0 when there are no samples. It is not the overall strafe sync formula. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:3434-3450,3811-3822`; `reference/uq_jumpstats.sma:fwdPostThink:7932-7950`.

## 5. Gain and loss: three different quantities

| Value | Confirmed calculation | Interpretation limit |
|---|---|---|
| Per-strafe gain `[0]` | In airborne PreThink, only when `speed > maxspeed`, add `speed - maxspeed` to the current slot, then replace `maxspeed` | New **jump-wide speed records**, not every positive speed delta. `reference/uq_jumpstats.sma:fwdPreThink:2901-2908` |
| Per-strafe loss `[1]` | If `speed < TempSpeed`, add `TempSpeed - speed`; then set `TempSpeed = speed` | Decreases between eligible PreThink samples, not the amount of failed PostThink acceleration. `reference/uq_jumpstats.sma:fwdPreThink:2909-2926` |
| Jump gain passed to HUD/console | `maxspeed - prestrafe` | Maximum-speed improvement, not landing-speed improvement, net acceleration, or efficiency. `reference/uq_jumpstats.sma:fwdPreThink:4873-4874,5745,5830` |

**Derived example, not a captured jump:** after an initialized maximum of 280, speeds 300, 290, 295, 305 contribute record gains 20, 0, 0, 5 and a loss of 10. Recovering from 290 to 295 does not add reported per-strafe gain, even though a PostThink acceleration sample could be good. The two measurements use different phases and comparisons.

Loss also feeds validation: once a slot's loss exceeds 5, checks involving `firstvel`, `secvel`, and `SurfFrames` can set `Checkframes`. At finalization loss above 200 sets `duckstring`; above 200 with `Checkframes` can mark the jump failed. These are explicit thresholds, not definitions of desync or overlaps. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:2909-2922,4585-4594`.

## 6. Closest available reporting

### HUD and console: aggregate rows after the jump

- `/strafe`, `/strafes`, `/strafestat`, and `/strafestats` toggle `streifstat`. General stats commands toggle `g_lj_stats`. Evidence: `reference/uq_jumpstats.sma:plugin_init:359-368`; `reference/uq_jumpstats.sma:streif_stats:8256-8268`; `reference/uq_jumpstats.sma:cmdljStats:8185-8227`.
- Each formatted strafe row receives, in order, **segment index, record gain, loss, percentage of jump time, sync** through `UQSTATS_HUDSTRSTATS1`. Those argument meanings are confirmed; exact headings, punctuation, units, and decimal formatting require the missing dictionary. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:4570-4583`.
- HUD and console target the jumper or detected spectators with `g_lj_stats[viewer]` enabled. The strafe HUD additionally checks **`streifstat[jumper]`**, not the viewer's flag; success/failure determines its colors. Console rows do not require `streifstat`. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:5726-5730,5763-5767,5807-5811,5821-5871`.
- Console output reuses the already-formatted row buffer, splitting at newlines into a 40-cell temporary buffer. This is not a separate detailed per-frame dump. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:5863-5871`.

### `/istrafe`: red/green frame strip, drawn after finalization

The feature is globally gated by `uq_istrafe` (`kz_uq_istrafes`, default 0), then by each viewer's `ingame_strafe` flag. The toggle refuses when the ordinary beam is enabled; the ordinary-beam toggle similarly refuses while in-game strafe stats are enabled. Evidence: `reference/uq_jumpstats.sma:plugin_init:312,411-412`; `reference/uq_jumpstats.sma:ingame_st_stats:8563-8585`; `reference/uq_jumpstats.sma:cmdljbeam:8269-8287`.

During sampling, bad sync writes `1` to `line_lost[slot][sample]`; good samples rely on the cleared/default zero. The per-slot cursor advances for all button-bearing samples. No-button samples are counted separately as `strafe_lost_frame`. Evidence: `reference/uq_jumpstats.sma:fwdPostThink:7895-7919`; `reference/uq_jumpstats.sma:fwdPreThink:2163-2179`.

At finalization, the code copies good/bad totals to `st1`/`st2` and calls `epta` for the jumper and enabled spectators. Despite the feature's name, this call is **after collecting the jump**, not live per-frame text. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:5698-5724`.

`epta` creates a spatial strip near the player's final origin:

- A blue baseline has length `FullJumpFrames`; the initial location/orientation is selected by `direct_for_strafe`. That direction is a dominant horizontal-velocity-axis classification captured in the jump-height path, **not** a reported view-angle error. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:2831-2872`; `reference/uq_jumpstats.sma:epta:1491-1554,1576-1608,1797-1829`.
- For each reported segment `1..str_num`, it advances by the total no-button count and draws one mark per good+bad count. `line_lost` chooses **red for bad, green otherwise**; alternating segments have a four-unit vertical offset. The direction branches mirror the same logic. Evidence: `reference/uq_jumpstats.sma:epta:1687-1770,1907-1990`.
- **Reconstruction limit:** no-button positions are not recorded individually. The renderer puts that segment's no-button total before its marks, regardless of where those samples actually occurred. Slot-0 samples are omitted even though the blue baseline includes all active-jump PostThink samples. The strip is therefore not an exact chronological full-jump replay.
- **Viewer-state caveat:** `l_lost` is passed from the jumper, but red-mark cleanup writes `line_lost[id]` using `epta`'s recipient ID. For self-rendering, this can mutate the same array later supplied to spectators; the player-index render order can affect subsequent viewers. For spectator rendering, cleanup addresses the spectator's state instead. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:5710-5721`; `reference/uq_jumpstats.sma:epta:1749-1754,1970-1975`.
- Marker writes are capped by `NVAR`, but the sample cursor still advances; the renderer has no corresponding visible `count_l < NVAR` check. Created-entity counts likewise have no local capacity check in those loops. Numeric safe limits cannot be established without the missing constants and runtime evidence. Evidence: `reference/uq_jumpstats.sma:globals:28,32`; `reference/uq_jumpstats.sma:fwdPostThink:7904-7913`; `reference/uq_jumpstats.sma:epta:1694-1696,1749-1767,1915-1917,1970-1988`.

### Ordinary trajectory beam: different colors, different meaning

`fnSaveBeamPos` keeps at most **100 origin samples**, plus duck and button-marker flags, while `g_Jumped` is true. Its airborne calls are in PreThink; the first-air-frame path also clears the beam buffer, so this is not guaranteed to retain every takeoff sample. Evidence: `reference/uq_jumpstats.sma:fnSaveBeamPos:8094-8123`; `reference/uq_jumpstats.sma:fwdPreThink:2888-2891,2940-2953,3075-3076`.

The rendered path is projected onto a fixed jump-relative Z plane. **Red means ducking**, not bad sync. In beam type 2, recorded button groups are green (left/back) or blue (right/forward); otherwise the path is yellow. The marker is set by segmentation and cleared on key release, so it is not an independent raw key-state history. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:2293-2316,6119-6188`; `reference/uq_jumpstats.sma:fwdPostThink:7840-7886`; `reference/uq_jumpstats.sma:fnSaveBeamPos:8104-8119`.

The `i == 100` landing-connector branch sits inside `i < 100` and is unreachable as written. Thus even that code must not be used as evidence of a complete landing-connected trajectory. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:6122-6138`.

## 7. `angles_arry` and anti-script: heuristic, not angle quality

The airborne, not-failed PreThink block reads `pev_angles`. When script detection is enabled, **exact equality of current and saved component `[0]`** increments `angles_arry`, then the entire vector is saved to `old_angles`. A changed value does not decrement or reset the count, so this is an accumulated unchanged-component count, not a consecutive-run length. It neither examines the segmentation component `[1]` nor records the angle value/delta per frame. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:2806-2825`.

`angles_arry` is reset in the main reset block and a bhop-start path; no `old_angles` reset/seed is visible. The first checked comparison can therefore use initial or previous-jump state. Evidence: `reference/uq_jumpstats.sma:globals:28`; `reference/uq_jumpstats.sma:fwdPreThink:2107-2109,2806-2825,3502-3506`.

The final anti-script predicate requires all of:

1. More than four recognized segments.
2. `angles_arry > SCRIPTFRAMES` and script detection enabled.
3. Distance strictly above a selected good/pro/holy/leet/god threshold.
4. `!not_save`, where excessive prestrafe with noslow disabled can set `not_save`.

Threshold selection uses the jump-dependent distance categories and `uq_script_work` (0 through 4); its default is 2. If the predicate passes, **more than 80 `FullJumpFrames` marks the jump failed without setting `find_script`; otherwise it sets `find_script`**. Evidence: `reference/uq_jumpstats.sma:plugin_init:340-344`; `reference/uq_jumpstats.sma:fwdPreThink:4501-4549`.

For `find_script`, a warning is appended to strafe output and the jump is marked failed. Later the console warns, the log is written, and configured punishment 1/2 invokes kick/ban; 0 invokes neither. The log labels `angles_arry` as **“Cheated Frames”**, but that string does not validate cheating. It records aggregate jump values, `FullJumpFrames`, `angles_arry`, and formatted strafe rows—not full angle/input traces. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:4659-4663,5942-5945,5969-6001`; `reference/uq_jumpstats.sma:Log_script:1212-1245`.

**Limits:** `SCRIPTFRAMES` is undefined in the supplied file, exact-equality sensitivity is visible but uncalibrated, and there are no supplied false-positive measurements or detection tests. The log call recomputes sync with an unguarded `goodSyncTemp + badSyncTemp` denominator, unlike the normal overall-sync assignment; whether the preceding state guarantees a nonzero denominator is not established here. Evidence: `reference/uq_jumpstats.sma:fwdPreThink:4670-4672,5986-5988`.

## 8. Exact reconstruction limits

| Can be reconstructed from the visible logic | Cannot be reconstructed from these artifacts |
|---|---|
| Conditional speed comparisons, bucket formulas, slot attribution, timestamp formulas, report argument order, beam color decisions, and anti-script predicate structure | `/dt` command behavior, `[MAIN]`/`[DETAILED]` layouts, or formulas for efficiency/overlaps/desync/ideal or error angle |
| Why no-button samples and slot 0 are excluded from reported sync | Exact original keys, yaw progression, individual no-button positions, movement-command magnitudes, or command durations from the aggregate rows |
| The limited good/bad marker sequence while allocated bounds and unmodified state permit | A complete immutable per-frame trace: `line_lost` is optional, bounded, and modified during rendering; the trajectory buffer has 100 entries and no angle history |
| How the supplied source intends to format localized results | Exact rendered labels, widths, rounding, or units without `uq_jumpstats.txt`; numeric array limits and `SCRIPTFRAMES` without includes |
| Source-level discrepancies such as the unwritten yaw baseline | Whether hidden include code corrects them, whether this snapshot builds, or how it behaves in a particular server/client environment |

**Verification performed:** connected source reads; whole-file symbol/literal searches; producer-to-consumer tracing for sync, strafe state, gains/losses, frame markers, angle counters, and report paths; SHA-256 checked before and after research. No plugin changes, compilation, game execution, or external API-semantic assumptions were used.

## Key Learnings:

1. This source's sync is an eligible-sample speed-increase ratio, not a verified efficiency, overlap, desync, or angle metric.
2. Segment recognition, PreThink gain/loss, PostThink sync, and total jump-frame counting have different gates and cannot be merged into one exact timeline.
3. `/istrafe` is the nearest frame-level report, but it is a post-jump beam with lost-position and mutable-viewer-state limitations; `angles_arry` is a separate unchanged-component heuristic.
