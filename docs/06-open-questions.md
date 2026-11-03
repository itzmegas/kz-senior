# Open questions and required verification

The principal blocker is **source/report provenance**: the supplied JumpStats 2.42 source does not demonstrate the `/dt` producer described in the request. Resolving that mismatch is more important than choosing an implementation strategy.

## Evidence boundary

The audit is static and limited to [`reference/uq_jumpstats.sma`](../reference/uq_jumpstats.sma). The header/version and dependency declarations are at lines 1–24; custom SQL inclusion is at line 766. No include implementation, installed binary, dictionary, server configuration, demo or runtime capture was supplied. A missing implementation is not evidence that an installed package can never provide it.

## Priority 0 — establish what is actually installed

| Question | Evidence / why unresolved | Required verification |
|---|---|---|
| Which plugin and exact build produce `/dt`, `[MAIN]`, `[DETAILED]` and the example fields? | No matching command registration, report literals or metric identifiers in the supplied file. `plugin_init`, 357–418, registers other commands; `client_command`, 1428–1476, handles command resets/demo-info heuristic, not `/dt`. | Obtain that producer's complete source, include files, dictionary and version/build identity. Keep the example's origin explicit; do not map its fields to this file by similarity. |
| Does this `.sma` match the server's loaded `.amxx`? Is its “official” status established? | Header says JumpStats 2.42 by BorJomi; registration is `register_plugin("JumpStats", VERSION, "BorJomi")` (`plugin_init`, 148–152). This does not authenticate deployment or official status. | Obtain installed plugin listing/version and distributable provenance; compare exact source package and binary identities. No binary build was performed in this phase. |
| What are the missing constants and helper definitions? | `uq_jumpstats_const.inc`, `uq_jumpstats_stocks.inc`, lines 19–20; undefined-here `JumpType`, `NSTRAFES`, `NVAR`, `NTOP`, `SCRIPTFRAMES`, `LandingCalculate`, `UpBhop_calc`, observer/state helpers. | Obtain the matching includes without substituting a similarly named release. Confirm capacities, enum numbers, hull/duck semantics and helper formulas. |
| What exact text/units/precision does the HUD or console show? | `register_dictionary("uq_jumpstats.txt")`, `plugin_init`, 152; `%L` metric formatting `fwdPreThink`, 4579, 5735–5858. | Obtain matching dictionary and active language configuration. Argument order is auditable; absent translation content is not. |
| Which runtime configuration and other plugins influence sampling and validity? | `plugin_cfg`, 475–649, loads/caches settings; weapon/settings filters `fwdPreThink`, 2269–2290; cross-plugin assumptions at 664–679. | Read existing active configuration and plugin list; document map, weapon, gravity, airaccelerate, FPS policy and other movement-affecting plugins without changing them. |

## Priority 1 — verify measurement semantics before diagnostics

| Question | What is already established | Verification still needed |
|---|---|---|
| Is `pev_angles` an adequate view-angle signal, and is the nominal yaw baseline ever updated? | It is the actual field read, not `pev_v_angle`: `fwdPreThink`, 2811; `fwdPostThink`, 7815. `old_angle1` appears only in declaration 48 and raw greater/less comparisons 7824/7828; no visible assignment. | Inspect missing includes for baseline updates; compare entity/view angles using supported existing tools in a separate non-record test. Confirm component conventions, wrap crossings, quantization and phase alignment. Do not relabel as raw mouse movement or verified frame-to-frame turning. |
| What is the actual callback cadence and PreThink/PostThink pairing? | Separate callbacks are registered, `plugin_init`, 434–442; `speed` is read in PreThink and `fSpeed` compared in PostThink, 2193–2202, 7817–7821, 7897–7906. | Confirm actual cadence versus client command rate/server simulation and behavior under varying frame duration. No `usercmd.msec` or per-sample duration is captured here; “74 frames” cannot be converted to exact seconds by assumption. |
| How representative is sync across a whole jump? | Requires a movement button; equality is bad; slot 0 is excluded in aggregate (`fwdPostThink`, 7889–7919; `fwdPreThink`, 4566–4581). | Compare counted and excluded samples, takeoff/landing boundaries and transition cases. The missing `efficiency` algorithm must be independently established, not identified with sync. |
| What happens at timestamp/array boundaries? | Strafe timestamps are written before incrementing the slot, `fwdPostThink`, 7843–7884; endpoints overwritten in `fwdPreThink`, 4564–4565. Capacities come from missing constants. | Confirm repeated keys, diagonal-to-single transitions, no-turn samples, zero elapsed time, exact capacity and overflow boundaries using the full source package. Static review identifies risks; it does not prove every branch reachable. |
| Can delayed keys and incorrect mouse turns be distinguished? | No direct matching test in good/bad sync; no saved joint angle/button/time series (`fwdPostThink`, 7824–7930). | Obtain actual `/dt` semantics and establish whether original samples, rather than only rounded text, exist. Even a joint series needs a justified desired movement/transition reference before causal labels. |
| How accurate are failed and successful distance corrections? | Failed distance calls unavailable `GetFailedDistance` with saved failure snapshots and `GRAVITY`; its formula is **unknown**. The nonfailed result uses the smaller of direct and corrected candidates, with visible correction arithmetic (`fwdPreThink`, 4252–4331). | Obtain the helper and constant definitions, then validate ground level, duck correction, actual frame duration, same/different-height landings, direction changes and correction branches against independent known geometry. Do not change official measurement constants during audit. |
| What exactly is Landing / “Lasting”? | `LandingCalculate` is called and adjusted, but implementation absent (`fwdPreThink`, 4334–4350); no separate metric named “Lasting” was located. | Obtain helper and dictionary; determine whether “Lasting” was a typo, translation, or another producer's metric. No equivalence is assumed. |
| Are block/edge estimates valid off-axis or near complex/moving geometry? | Dominant-axis traces at offsets −18/0/+18; selected class handling and a map-specific correction (`fwdPreThink`, 6502–6658). Branches 6643 and 6648 contain self-comparisons `tmpjblock[0] <= tmpjblock[0]`. | Reproduce with known blocks, diagonals and movement entities separately. Verify selection logic and HUD recipient indexing at 6672–6682; treat as static inconsistencies, not silently corrected formulas. |
| Does the failed label mean a missed platform? | No: falling, ladder warnings, script suspicion and other validity paths share the flag (`fwdPreThink`, 2928–2931, 4544–4549, 4590–4594, 4645–4662). | Separate the reason paths when interpreting existing outputs. Obtain dictionary and real samples; do not train a failure-cause label on `failed_jump` alone. |
| Are FPS/script warnings reliable? | FPS warning uses vertical-speed differences, not measured FPS (`fwdPreThink`, 2475–2495). Anti-script counter compares angle component `[0]` for exact equality, 2813–2824; `SCRIPTFRAMES` unavailable. | Validate false positives/negatives with full package and controlled non-record samples. Unchanged angle is not proof of cheating; no such verdict is justified by this audit. |

## Priority 2 — storage, demos and reproducibility

| Question | Evidence / uncertainty | Required verification |
|---|---|---|
| What does SQL actually persist and under what failure modes? | `#include <uq_jumpstats_sql.inc>`, 766; initialization/calls visible, implementation absent. | Obtain schema and include; verify precision, selection policy, transaction/error handling and whether any all-attempt data exists. Do not infer SQL schema from local tops. |
| Do client consoles or demos preserve all displayed text? | Calls send console/HUD output (`fwdPreThink`, 5827–5949); no client file writer here. Demo-info path only emits version HUD (`client_command`, 1437–1448). | Inspect actual client logging settings, recording mode and demo format separately. Do not treat presentation as persistent structured telemetry. |
| Can a demo reconstruct commands, view, velocity and exact attempt boundaries? | No demo parser/exporter is supplied; visual beams/messages are presentation (`fnSaveBeamPos`, 8094–8122; `client_command`, 1437–1448). | Analyze real sample bytes and applicable engine/demo specifications, including player/observer/HLTV differences, timestamp precision, quantization, omitted data and interpolation. Reproduce extraction against a known event before relying on it. |
| Are all attempts/failures available for comparisons? | Local tops are selection/update records (`checktops*`, 7185–7731); anti-script log is conditional (`Log_script`, 1212–1239; call 5988). Active arrays are reset/reused (2107–2180, 3602–3620). | Inspect actual existing files and missing SQL implementation. A list of records is selection-biased; no demonstrated denominator for success rate or recurrent-error frequency. |
| What is safe to reuse without changing official behavior? | Hooks, counters and geometry are identifiable, but licensing/redistribution terms and package authority are not established in header 1–24. | Confirm provenance/license and official validity constraints before reuse. First reuse these findings as measurement specifications and test cases, not as permission to alter the plugin. |
| What privacy constraints apply? | Identity includes name/IP/auth ID (`client_putinserver`, 1322–1324); log writes identity (`Log_script`, 1212–1239); tops use identity columns (`save_tops*`, 6850–6991). | Agree on consent, redaction and retention before collecting/sharing real logs or demos. No actual player dataset was accessed in this audit. |

## Safe next-phase verification order

1. Resolve producer and version mismatch; complete the source/dependency/dictionary evidence set.
2. Read deployment/configuration evidence without changing server settings or loading a new plugin.
3. Collect already available example outputs and separately designated non-record demos, with consent and contextual metadata.
4. Cross-check speed, sync denominators, strafe boundaries, distance and landing on a small set of controlled scenarios: clean single-key strafe, diagonal/overlap, buttonless gap, yaw wrap, speed loss/recovery, successful/failed same-height jump and invalidated result.
5. Establish which observations survive export and how much precision is lost. Only then agree on an evidence-based diagnosis specification for the next planning phase.

These are recommended research steps, **not implemented tests or new telemetry**. No new application architecture, technology stack, thresholds or coaching algorithms are selected here.

## Audit safety note

Running this plugin is not a passive audit: `plugin_cfg`, 682–703, and `server_frame`, 1282–1313, enforce cvars; `tskFps`, 1274–1280, can send client settings; anti-script code can issue punishment commands (`kick_function`/`ban_function`, 6749–6797). None was executed. Do not use official-record or validity-sensitive sessions for unreviewed experiments.
