# KZ Coach — Phase 1 source audit

**The supplied plugin is useful as a source of movement observations and aggregate definitions, but it is not demonstrated to be a complete diagnostic dataset.** Its sync measures counted speed-gaining samples, not direct mouse–keyboard coordination. The `/dt` example cannot be attributed to the supplied source.

## Executive findings

1. **The evidence set is incomplete.** `reference/` contains one file, `uq_jumpstats.sma`, identifying itself as JumpStats 2.42 by BorJomi. Custom includes, dictionary, companion tops plugin source, deployed binary, configuration and demos are absent. “Official” provenance and deployed-source equivalence are not verified (`plugin_init`, 148–152; dependencies, 12–22, 766; companion check, 664–679).
2. **The requested `/dt` report is not implemented in the supplied file.** Registered commands and generic command handler do not establish `/dt`, `[DETAILED]`, efficiency, overlaps, desync or per-frame `<`/`>` tokens (`plugin_init`, 357–418; `client_command`, 1428–1476). Their meanings remain unresolved, not guessed from a different implementation.
3. **Sync is acceleration-based.** With any W/A/S/D movement bit, PostThink horizontal speed greater than PreThink speed counts good; equal/decreased counts bad. Exclusive movement buttons plus nominal turn flags segment strafes, but do not define good sync. Slot 0 is omitted from the final sum. The yaw baseline `old_angle1` has no visible update, so actual frame-to-frame turning is not established (`fwdPostThink`, 7813–7930; declaration 48; `fwdPreThink`, 4553–4583, 4670–4672).
4. **Reported strafe gain is not every positive acceleration.** It counts improvements of the whole jump's running maximum. Recovery below an earlier maximum can show no gain. Loss accumulates sampled decreases; total gain is `maxspeed - prestrafe` (`fwdPreThink`, 2892–2926, 4873–4874).
5. **There is no demonstrated lossless jump timeline.** Current position/velocity/buttons and entity angles are read; only selected snapshots, aggregates, optional binary nongain marks and at most 100 trajectory points remain in active RAM. Beam points have no per-sample timestamp, velocity, yaw or full button mask (`fwdPreThink`, 2183–2202, 2779–2824; `fwdPostThink`, 7813–7821, 7904–7919; `fnSaveBeamPos`, 8094–8122).
6. **Distance and failed status need care.** Nonfailed distance selects between direct and corrected candidates; failed distance delegates to an unavailable helper. `failed_jump` can also mark invalidity/script/ladder conditions, not merely a missed platform (`fwdPreThink`, 2928–2939, 4252–4331, 4544–4549, 4645–4662). Landing also relies on an unavailable helper (4334–4350).
7. **Persistence is selective, not a training journal.** Local tops retain selected aggregate records; anti-script log is conditional; SQL details are unavailable. HUD/demo visibility is not evidence of structured demo telemetry (`save_tops*`, 6850–6991; `Log_script`, 1212–1239 and call 5988; SQL include, 766; `client_command`, 1437–1448).

## Read the audit

| Document | Answers |
|---|---|
| [01 — Plugin architecture](01-plugin-architecture.md) | Components, dependencies, callbacks, player state, dataflow, lifecycle, storage and export. |
| [02 — Data inventory](02-data-inventory.md) | Direct/calculated/inferred data; capture timing, history and post-jump retention. |
| [03 — Metrics dictionary](03-metrics-dictionary.md) | Implemented formulas, units, jump classification, variant paths and inconsistencies. |
| [04 — Frame analysis](04-frame-analysis.md) | Why `/dt` cannot be decoded from this source; exact sync/strafe/visual-marker behavior and reconstruction limits. |
| [05 — Diagnostic capabilities](05-diagnostic-capabilities.md) | Observable symptoms versus inferable or unprovable causes. |
| [06 — Open questions](06-open-questions.md) | Missing evidence, verification priorities and safe next research steps. |

## Answers for planning

| Question | Evidence-based answer |
|---|---|
| What information is available? | Current movement state, event snapshots, jump/strafe aggregates and a bounded visual trajectory; actual export is much narrower than capture. See 02. |
| What does each statistic mean? | Definitions can be established for the implemented metrics; missing `/dt` fields, FOG and helper-dependent formulas cannot all be established. See 03–04. |
| What errors can be reliably detected? | Sampled speed losses and low contributions to the running maximum are observable symptoms. Insufficient prestrafe or inconsistency need controlled comparisons. Late keys versus wrong mouse turn is not currently demonstrated. See 05. |
| What additional information is needed? | Matching `/dt` source, missing dependencies/dictionary, deployed version/configuration and proof of available temporal/input/geometry channels. See 06. |
| What can be reused conceptually? | Capture sites, transition criteria, explicit metric definitions, presentation/persistence boundaries and known counterexamples form a useful investigation baseline. Geometry corrections, anti-script heuristics and record-selection logic need validation rather than blind reuse. See 01–06. |

## Recommended next step

**Obtain the exact source package that generated the `/dt` example and identify the deployed build before planning telemetry or coaching logic.** Then validate a few known successful/failed and input-transition scenarios using existing outputs and separately designated non-record material. Resolve what is actually retained and at what precision before deciding the next phase's data requirements.

No application architecture, technology stack, new plugin code or configuration changes are proposed or implemented in this phase.

## Audit provenance and verification

| Item | Value |
|---|---|
| Date | 2026-11-01 |
| Supplied source | `reference/uq_jumpstats.sma` |
| Size / line count | 303,164 bytes / 9,364 lines |
| SHA-256 | `D4D786AF106886659BA4D3EEE8698C196679CFDB1E1148E5CDD15934120701E5` |
| Method | Static inspection of supplied source, connected call paths and formula/output/reset sites; file/function/line citations throughout. |
| Source navigation | Direct file inspection: workspace has no `.git` or `.codegraph`; no Git repository or index was created. |
| Changes | Documentation under `docs/` only; original source hash verified unchanged. |
| Not performed | Compilation, execution, dependency installation, server/client configuration changes, live movement tests, demo-format analysis or authentication of official provenance. |

Line references identify this exact source snapshot. Missing includes prevent a complete-package audit, and static risks are not presented as reproduced runtime defects.
