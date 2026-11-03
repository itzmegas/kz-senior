# Data inventory: available state is not a retained jump recording

The supplied source reads movement state during player callbacks, reduces it into jump/strafe aggregates, and keeps a small, lossy trajectory buffer. It does **not** demonstrate a complete, timestamped recording of position, velocity, view angles and buttons for every attempt.

## Scope and evidence conventions

- Audited file: [`reference/uq_jumpstats.sma`](../reference/uq_jumpstats.sma), version `2.42` in lines 1–24. Only this source was supplied. Custom includes, translation dictionary, companion tops source, configuration and demos were not supplied.
- References below use `function, lines` in that file. Line numbers refer to the unmodified supplied bytes, not another release.
- **Direct**: read from an API. **Calculated**: arithmetic/counters over observations. **Inferred**: a state/type/validity judgment from conditions.
- **History** means actual retained samples, not a variable declared `static`. Values surviving temporarily in RAM after output are not an addressable archive of completed attempts.
- Frequencies describe code paths, **not an assumed fixed 100 Hz**. Registration is `FM_PlayerPreThink`/`FM_PlayerPostThink`, not a user-command recorder (`plugin_init`, 434–442).

## 1. Direct observations

| Data and representation | Capture / API | Update moment | History and after-jump retention |
|---|---|---|---|
| Position XYZ: shared scratch `origin[3]`; local `vOrigin[3]` | `fwdPreThink`, `pev_origin`, 2183–2195; `fnSaveBeamPos`, 8094–8102 | Eligible PreThink; extra branch-specific reads; beam capture during active nonfailed air processing | Scratch is overwritten, including deliberate Z corrections. Selected origins and up to 100 beam points survive temporarily; no full position log. |
| Velocity XYZ: local `velocity[3]`, `Vvelocity[3]` | `fwdPreThink`, `pev_velocity`, 2193–2202, 2442–2465, 2792–2799; `fwdPostThink`, 7817–7821; `HamTouch`, 6808–6814 | PreThink, active-jump PostThink and touches | No complete velocity timeline. Z is explicitly zeroed for horizontal-speed calculations; later branches reread the full vector. Only selected snapshots retain XYZ. |
| Current movement/jump/duck button bitmask: `button`, `buttons`, `buttonsNew` | `fwdPreThink`, `pev_button`, 2183–2188; `fwdPostThink`, 7813–7815 | Eligible PreThink; PostThink while `g_Jumped` | No raw button history. W/A/S/D conventions correspond to `IN_FORWARD`, `IN_MOVELEFT`, `IN_BACK`, `IN_MOVERIGHT`, **not verified physical key bindings**. Jump/duck checked separately, e.g. 2374–2383, 3462, 6221. |
| Previous engine buttons: `oldbuttons` | `fwdPreThink`, `pev_oldbuttons`, 2183–2188 | Eligible PreThink | One engine-provided previous mask, not an array of commands. Distinct from the plugin's filtered `strafecounter_oldbuttons`. |
| Entity angle vector: `angles[3]`, `angle[3]` | `fwdPreThink`, `pev_angles`, 2808–2824; `fwdPostThink`, `pev_angles`, 7811–7834 | Anti-script block in nonfailed air processing; active-jump PostThink | `old_angles[id][3]` is updated; `old_angle1[id]` is compared but has **no visible assignment** (declaration 48, comparisons 7824/7828). No retained angle series or raw mouse deltas. The source uses `pev_angles`, **not `pev_v_angle`**; exact view/entity-angle correspondence requires engine validation. |
| Engine flags: `flags`, including `FL_ONGROUND`, `FL_INWATER` | `fwdPreThink`, `pev_flags`, 2186–2198; `HamTouch`, 6812 | Eligible PreThink / touch | Current mask only. Air/ground transitions become inferred state and event snapshots. |
| Movement mode: `movetype[id]` | `fwdPreThink`, `pev_movetype`, 2195 | Eligible PreThink | Last value only; `MOVETYPE_FLY` drives ladder handling, 3225–3294. |
| Weapon/player speed limit: `weapSpeed[id]`, `weapSpeedOld[id]`, `Pmaxspeed` | `fwdPreThink`, `pev_maxspeed`, 2105, 2184–2192 | Eligible PreThink | Previous/current pair, not history. Changes can reset the attempt, 2269–2277. Do not confuse this limit with measured jump `maxspeed`. |
| Current weapon ID/name: `wpn`, `weapon_name`, `weapon_name1`; incidental `clip`, `ammo` | `fwdPreThink`, `get_user_weapon(id, clip, ammo)`, `get_weaponname`, 4443–4453 | Result finalization, not every air sample | Local ID/name support output and category routing. Clip/ammo are API output locals with no demonstrated coaching use/history. Weapon-specific selected tops and SQL call payloads retain weapon information; see 01. |
| Player gravity and water level | `fwdPreThink`, `pev_gravity`, `pev_waterlevel`, 2190–2192, 2280–2290 | Eligible PreThink / legality check | Current validation inputs, not per-frame export. |
| Solid state and ground entity classname: `ClassName[32]` | `fwdPreThink`, `pev_solid`, `pev_groundentity`, `pev_classname`, 3110–3129 | Ground branch, **inside `!pev_solid` condition** | Temporary classification/filter input. Not a general surface ID history. |
| Touch entity classnames: `ClassName`, `ClassName2` | `fwdTouch`, `pev_valid`, `pev_classname`, 6819–6844 | Touch callback, selected entity classes | Reduced to booleans and resets; entity identity, contact normal and collision impulse are not archived. |
| Ladder entity IDs and bounds: `entlist[256]`, `ladderxyz`, `ladderminxyz`, `laddersize` | `plugin_init`, `find_ent_by_class`, `entity_get_vector(EV_VEC_maxs/mins/size)`, 448–458 | Initialization enumeration | Map-lifetime arrays, not changing per-frame surface telemetry. Nearby ladder lookup uses `find_sphere_class`, e.g. `fwdPreThink`, 3245–3258. |
| Trace endpoints: `slidez[id][4][3]`, `endhj[id]`, `tmpEdgeOrigin`, `tmpblockOrigin`, `tmpcheckblock` | `fwdPreThink`, `EngFunc_TraceLine` + `get_tr2(TR_vecEndPos)`, 2576–2618, 3080–3098, 6443–6658 | Conditional slide, airborne HJ and edge/block branches | Some endpoint arrays persist in RAM, many locals do not. No general map mesh, material, friction, plane-normal or collision journal is stored by these sites. |
| Game time: `jumpoff_time`, `last_land_time`, `FallTime`, `FallTime1`, ladder/duck/bhop timestamps | `fwdPreThink`, `get_gametime`, e.g. 2318–2358, 3290–3294, 3560, 3682, 6695–6738; `fwdPostThink`, 7843–7884 | State-specific events; `last_land_time` is updated **while not grounded** | Event/last-sample times only; no timestamp accompanying each beam or sync sample. |
| Slowdown field | `fwdPreThink`, `entity_get_float(id, EV_FL_fuser2)`, 4356 onward | Result eligibility/validation branch | Current check, not an acceleration model or historical input. |
| Environment/cvars | `plugin_init`, pointers 424–431; `plugin_cfg`, cached values 487–649; `fwdPreThink`, comparisons 2280–2290 | Startup cache plus selected live legality reads | Context/filters, not embedded alongside every jump record. `server_frame`, 1282–1313, can actively enforce settings. |
| Player identity and participation: name, IP, auth ID, team, alive/admin/bot flags | `client_putinserver`, `get_user_name/ip/authid`, 1322–1333; `fwdPreThink`, `get_user_team`, `pev_deadflag`, 1998–2093; `client_connect`, 8589–8735 | Connection and eligibility callbacks | Per-player state; selected identities are written to tops/logs. IP/auth data need privacy handling if reused. |
| Map name and display recipients | `plugin_init`, `get_mapname`, 460; `fwdPreThink`, `is_user_spectating_player`, 2204–2208 | Map init / each eligible PreThink | Map context and transient recipient list; spectator helper implementation is in an unavailable include. |
| Client command text: `command[32]` | `client_command`, `read_argv/read_args`, 1428–1476 | Client command callback | Used for resets and demo-info heuristic, not a retained input stream. |

## 2. Calculated data and bounded histories

| Data / variable | Computation and update | What is retained / discarded |
|---|---|---|
| Horizontal speed `speed[id]` | Z-zeroed vector length in `fwdPreThink`, 2193–2202 | Current PreThink scalar. HUD `DoSpeed`, 1394–1410, independently samples at a scheduled rate, floors to integer and is not the jump sampling clock. |
| PostThink horizontal speed `fSpeed` | `fwdPostThink`, 7817–7821 | Current local scalar only. Compared to the PreThink `speed[id]` for sync, 7897–7906. |
| Prestrafe / maxspeed / previous speed | `prestrafe`, `maxspeed` initialized at jump/type branches, e.g. `fwdPreThink`, 3599–3600; peak and loss tracking 2892–2926 | Jump aggregates; no original speed curve. `TempSpeed` is overwritten each eligible air sample. |
| Per-strafe gain/loss `strafe_stat_speed[id][s][0/1]` | `fwdPreThink`, 2901–2926 | Two aggregate scalars per slot, **gain only counts new all-jump speed maxima**. Not every positive speed increment. |
| Sync counters `strafe_stat_sync[id][s][0/1]`, final `sync_[id]` | `fwdPostThink`, 7889–7906; aggregate `fwdPreThink`, 4553–4583, 4670–4672 | Counts, then integer percentages. Slot 0 excluded from final summation `1..strafe_num`. `goodSyncTemp`/`badSyncTemp` are shared result scratch scalars (declaration 57), not per-player histories. |
| Pre-duck sync `doubleduck_stat_sync`, `dd_sync` | `fwdPostThink`, 7934–7949; `fwdPreThink`, 3811–3821 | Separate counters/percentage; displayed value adds 5 if raw percentage is below 96. Not interchangeable with jump sync. |
| Frame counts `frames`, `frames_gained_speed`, `FullJumpFrames` | `fwdPreThink`, 2892–2899; `fwdPostThink`, 7803–7806 | Counters over different conditions/callback phases. The first pair's ratio is not shown as a supplied `efficiency` implementation. No timestamp/frame-ID table. |
| Strafe count, start markers and duration | `strafe_num`, `strafe_stat_time`; `fwdPostThink`, 7835–7887; result calculations `fwdPreThink`, 4561–4579 | Bounded transition timestamps, later overwritten with takeoff/end markers; duration reported as percent of `Fulltime`, not an archived duration per raw sample. |
| Optional per-slot nongain marks `line_lost`, counts `lost_frame_count`, erasure markers `line_erase`, `line_erase_strnum` | `fwdPostThink`, 7904–7914; guarded by `uq_istrafe` | Binary flags in `[33][NSTRAFES][NVAR]`; not formatted `/dt` tokens. Index advances only in movement-button branch, including successful samples. Source-defined capacity values `NVAR`/`NSTRAFES` are missing with constants include. |
| Optional buttonless counts `strafe_lost_frame` | `fwdPostThink`, 7918–7919 | Counts per slot when no W/A/S/D movement bit, not overlap/desync counters. Collected only with `uq_istrafe`. |
| Trajectory `gBeam_points[id][100][3]`, `gBeam_count`, `gBeam_duck`, `gBeam_button`, `gBeam_button_what` | `fnSaveBeamPos`, 8094–8122; called by `fwdPreThink`, 2888–2891, 3075–3076 | At most 100 XYZ points with duck flag and coarse movement marker. No velocity, yaw, timestamp, complete key mask or reliable key-change event attached. First-air initialization clears earlier points, 2940–2953. No file serialization demonstrated. |
| Two origin/velocity slots `frame_origin[id][2][3]`, `frame_velocity[id][2][3]` | `fwdPreThink`, declarations 2101, initialization/filling 2779–2802; additional velocity writes 2940–2943, 3070–3072 | First/rolling snapshots for correction, **not a ring buffer of all frames**. Cleared at new jump branches, e.g. 3612–3620. |
| Failed-attempt snapshots `failed_origin`, `failed_velocity`, `failed_ducking`; takeoff `jumpoff_origin`, `pre_jumpoff_origin`, `jumpoff_foot_height` | `fwdPreThink`, 2095–2101, 2928–2939, 3557–3558, 3588–3596, 3674–3694 | Last eligible failure snapshot/event origins used by distance calculation. Not all failed trajectory samples. Some Z values are normalized, not untouched API observations. |
| Alternating samples `firstorig`, `secorig`, `firstvel`, `secvel`; `SurfFrames`, `oldSurfFrames` | `fwdPreThink`, 2442–2495, 2544–2565 | Previous/alternate samples and vertical differences. Origin Z is subsequently zeroed. `SurfFrames` and `fps_hight` are heuristic measurements, not captured FPS or command duration. |
| Duck preparation speeds `statsduckspeed[id][500]`, `prest`, `prest1`, `ducks` | `fwdPreThink`, 6221–6269; output examples 5694, 5883 | Sparse preparation-event speeds, not 500 air frames. Reset/overwriting follows preparation and jump state; not a durable multi-attempt database. |
| Height `oldjump_height`, `jheight`, `heightoff_origin`, `x_heightland_origin`, `upheight` | `fwdPreThink`, 2374–2439, 2827–2877, 3357–3385, 3570–3578 | Event/maximum/height-difference summaries with duck corrections. `jheight` is set on first decrease of absolute takeoff-relative height, not continuously archived. |
| Edge/block/landing `jof`, `edgedist`, `jumpblock`, `Landing`, `land_origin`, `distance`, `distance2` | `fwdPreThink`, 4274–4350, 6443–6658 | Conditional geometric estimates and corrected result values. `LandingCalculate` implementation is missing; traces select a dominant world axis rather than recording arbitrary platform contours. |
| Formatted result buffers `strMess`, `strM`, localized HUD/console arguments | `fwdPreThink`, 4553–4672, 5694–5949 | Temporary strings over aggregates; `40*NSTRAFES` buffers do not contain original frame state. Exact output text depends on unavailable `uq_jumpstats.txt`. |

See [metrics dictionary](03-metrics-dictionary.md) and [frame analysis](04-frame-analysis.md) for formulas, exclusions and boundary errors. A calculated speed percentage is not an independently captured coordination signal.

## 3. Inferred states, not extra sensors

| Inference | Evidence / limits |
|---|---|
| Jump start, air, ground, duck, bhop, ladder and jump type: `g_Jumped`, `in_air`, `in_bhop`, `in_duck`, `in_ladder`, `OnGround`, `jump_type` and preparation flags | Conditions over buttons/flags/mode/time; `fwdPreThink`, 3140–3294, 3462–3625, 6221–6438. Some helper semantics and enum values depend on missing includes. These are plugin state-machine labels, not dedicated engine jump/landing events. |
| Nominal turn direction `turning_left/right` | Comparison of current entity yaw with `old_angle1` in `fwdPostThink`, 7824–7834. No visible update of that baseline or angular normalization; **not established as previous-sample yaw change**. Magnitude is not stored. |
| Dominant motion axis `direct_for_strafe` | Sign and largest absolute horizontal velocity component near height detection in `fwdPreThink`, 2854–2871. Discrete ±X/±Y, not a continuous heading or desired movement vector. |
| Script suspicion `angles_arry`, `find_script` | Count of unchanged angle component `[0]` in `fwdPreThink`, 2808–2824, combined with thresholds and other conditions, 4511–4549. Not evidence of physical mouse motion or proven cheating. |
| Collision/trigger/bug/FPS warnings | `HamTouch`, 6804–6816; `fwdTouch`, 6819–6844; `fwdPreThink`, 2475–2510, 2879–2886, 2909–2921. Reduced flags cannot establish contact cause, surface normal or actual FPS. |
| `failed_jump` | Geometric falling condition, 2928–2931, but also validity/anti-script paths, 4544–4549, 4590–4594, 4645–4662. **A failed label is not uniquely a missed landing.** |

## 4. Retention and export boundaries

| Destination / lifetime | Demonstrated contents |
|---|---|
| Active-player RAM | Raw current state, selected event snapshots, strafe summaries, optional binary marks and bounded trajectory described above. Shared scratch variables must not be mistaken for separate records per player. |
| After final output | There is no completed-jump collection exposed here. Reset requests set `g_reset`; next eligible PreThink clears state, frames, beam points and optional marks (`JumpReset`, 8125–8135; `fwdPreThink`, 2107–2180). New-jump branches separately clear strafe arrays, e.g. 3602–3620. Survival between callbacks does not guarantee later retrieval. |
| Local tops / map tops | Selected records, not all attempts; serializers `save_tops*`, 6850–6991; `save_maptop`, 6992–7010. Read/update paths and quantization are detailed in [architecture](01-plugin-architecture.md). No per-frame state written by those serializers. |
| Server anti-script text log | `Log_script`, 1212–1239, called under conditional suspicion path at 5979–5988: summary, identity, counts, formatted strafe text. Not a universal attempt log. |
| SQL | Calls and custom SQL include exist (`plugin_cfg`, 712–716; include 766), but schema, precise persistence and error behavior cannot be verified without `uq_jumpstats_sql.inc`. |
| HUD / chat / console / visual beam | Presentation only: e.g. `fwdPreThink`, 5712–5949; `DoSpeed`, 1373–1410; `epta`, 1491–1994. No promise that client console text is saved to disk. |
| Demo | `client_command`, 1437–1448, displays version information based on a command heuristic. No structured frame exporter or demo parser is demonstrated. What a particular demo contains requires separate format and recording-mode investigation. |

## 5. Missing inputs that must not be assumed

In the supplied file there is no `FM_CmdStart`/`get_uc`/`UC_*` capture, `usercmd.msec`, `forwardmove`/`sidemove`, raw mouse delta, per-sample clock, wish-direction/velocity-angle series, acceleration ideal, complete collision geometry, target landing region, attempt ID, or archived all-attempt timeline. The positive evidence for the actual hooks and sampled fields is `plugin_init`, 434–442, `fwdPreThink`, 2183–2202, and `fwdPostThink`, 7813–7821. Missing includes prevent an absolute claim about the complete installed plugin package.

**Next investigation:** obtain the exact installed source package and the producer of the supplied `/dt` example before treating that richer report as an available dataset.
