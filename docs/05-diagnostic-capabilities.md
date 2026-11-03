# Diagnostic capabilities: observable symptoms, mostly unproven causes

The supplied plugin can expose speed loss, acceleration counts and coarse strafe/jump summaries. It cannot, by itself, prove why a player mistimed a mouse/key transition or missed a target. In particular, low sync is **not proof of mouse–keyboard desynchronization**.

## Classification rules

- **Directly observable**: sufficient code-level evidence for the narrowly named symptom, during the relevant capture path.
- **Inferable**: requires an explicit reference, multiple metrics or comparable attempts; not a demonstrated cause.
- **Not currently demonstrable**: required signal/context is not established in the supplied source.
- A signal observed in RAM is not automatically available in a historical file. The availability column matters as much as the classification.

All citations below refer to [`reference/uq_jumpstats.sma`](../reference/uq_jumpstats.sma), using function and line ranges. Only one `.sma` was supplied; missing includes and the absent `/dt` implementation constrain every conclusion.

## Capability matrix

| Requested diagnosis | Classification / what can actually be said | Evidence and availability | Missing evidence / causal boundary |
|---|---|---|---|
| Insufficient prestrafe | **Inferable.** Numerical takeoff speed is observable; calling it insufficient needs a target appropriate to jump, weapon and settings. | `prestrafe = speed`, e.g. `fwdPreThink`, 3599–3600; current horizontal speed 2193–2202; summary output 5827–5858. Selected tops retain some summaries, not every attempt. | No optimal prestrafe model or target-specific required speed. A low value does not identify whether run-up, turn, key timing or a different constraint caused it. |
| Inefficient air acceleration | **Inferable** as performance relative to a controlled reference. Nongain samples are directly counted, but are not theoretical efficiency. | `fwdPostThink`, 7889–7906; final sync aggregation `fwdPreThink`, 4553–4583, 4670–4672. | No ideal acceleration denominator or continuous wish-angle model. Buttonless samples and slot 0 can be excluded. No `efficiency` formula from the supplied `/dt` example. |
| Strafe change too early / too late | **Not currently demonstrable** as a technical timing diagnosis. Some transition times are observable. | `fwdPostThink`, 7835–7887: exclusive directional button onset plus a nominal turn flag; `fwdPreThink`, 4561–4579: duration percentages. | No required/optimal transition instant, raw input timeline, normalized yaw series or exact phase correlation. `old_angle1` has no visible update (declaration 48, comparisons 7824/7828), so the flag is not established as actual yaw change. |
| Poor mouse–button coordination | **Not currently demonstrable** as a distinct cause. At most, coarse association can be hypothesized. | Buttons and a comparison of `pev_angles[1]` to an unwritten baseline are inspected in `fwdPostThink`, 7813–7887; sync checks **speed increase**, 7889–7906. | No saved joint mouse/button samples; no raw mouse input. The source does not reject good sync when key and turn directions are ostensibly mismatched. Forward/backward and diagonal movement also preclude a universal A-left/D-right interpretation. |
| Velocity losses | **Directly observable** for sampled decreases in horizontal speed. | `fwdPreThink`, 2909–2926: accumulates `TempSpeed - speed` per strafe. Available in aggregates, not a timestamped loss curve. Visual nongain markers instead use PostThink versus PreThink (7897–7905); a sampled PreThink loss can coexist with a green marker. | Does not establish cause. Collision, duck behavior, input, settings or other plugin effects require additional evidence. Zero acceleration is a bad-sync sample but **not** positive loss. |
| A strafe with little new speed gain | **Directly observable** as low contribution to the jump's running speed maximum; **inferable** as an underperforming strafe. | `fwdPreThink`, 2901–2907: gain increments only on a new all-jump maximum; output aggregation 4579–4583. | Recovery below an earlier maximum can receive zero reported gain despite positive acceleration. Strafe duration and start speed must be accounted for; low gain alone does not prove poor technique. |
| Inconsistent takeoffs | **Inferable** across comparable attempts; individual takeoff speed/origin are observed. | `fwdPreThink`, 3557–3600, 3674–3694; conditional `edgedist` 6583–6588. | No all-attempt archive or stable attempt IDs. Must compare like-for-like type, map/block, weapon, settings, duck state and sampling conditions; no arbitrary edge threshold is justified. |
| Incorrect trajectory | **Not currently demonstrable** as correctness. A bounded position trace is observable. | `fnSaveBeamPos`, 8094–8122, stores at most 100 positions; `fwdPreThink`, 2940–2953, clears initial samples. | No intended route/target, complete geometry or complete timestamped path. A visibly different curve can be described, not automatically judged wrong. |
| Imprecise landings | **Inferable** only for the source's restricted block/edge estimates and an agreed target; arbitrary landing accuracy is **not currently demonstrable**. | `fwdPreThink`, 4334–4350, uses missing `LandingCalculate`; edge/block traces 6502–6658; reporting gates 4617–4635. | No target point/region, landing polygon or exact helper implementation. Distance correction is not proof of the actual contact location. |
| Recurrent errors across attempts | **Inferable** from a separately obtained comparable series of summaries; **not currently demonstrable** from a single top entry. | Tops serializers `save_tops*`, 6850–6991; bounded/reused active state `fwdPreThink`, 2107–2180, 3602–3620. | Selected records omit ordinary attempts and many failures. An unbiased repetition dataset is missing. Recurrent low gain is a repeated symptom, not a proven repeated cause. |
| Missed jump versus invalidated result | **Directly observable** only as separate internal conditions, not from the shared failed flag alone. | Falling condition `fwdPreThink`, 2928–2931; ladder/script/validity paths also set `failed_jump`, 4544–4549, 4590–4594, 4645–4662. | A displayed failed label cannot establish that the player failed to reach a platform. Exact result text also depends on missing dictionary. |
| Collision-associated failure | **Inferable** from touch warning plus result context; causal contact type is **not currently demonstrable**. | `HamTouch`, 6804–6816, flags descending airborne touches; `fwdTouch`, 6819–6844, invalidates selected classes. | No retained contact normal, contact point, impulse or full collision sequence. A touch flag is not proof that a wall, ceiling or edge caused the outcome. |

## Why sync cannot answer the priority coordination question

The actual test is: with any W/A/S/D movement bit active, did horizontal speed measured in PostThink exceed the PreThink speed? Successful samples increment `[0]`; all other eligible samples increment `[1]` (`fwdPostThink`, 7889–7906). A/D exclusivity and nominal turn flags affect **strafe segmentation**, not that good/bad test (`fwdPostThink`, 7835–7887). The flags compare against `old_angle1`, which has no visible update in this file (48, 7824–7834); do not silently substitute an intended previous-frame comparison.

Consequently, the implementation does **not** distinguish:

1. a delayed key transition after the mouse turns;
2. an early or reversed mouse turn while holding a key;
3. a geometrically poor but accelerating angle;
4. other reasons for failing to gain speed.

This is a statement about missing discriminating evidence, not a claim that these cases are physically equivalent. See [frame analysis](04-frame-analysis.md) for exact counter denominators and boundary effects.

## Safe language for a future coach

| Supported observation | Unsupported replacement |
|---|---|
| “This strafe added little to your previous maximum.” | “You did not accelerate during this strafe.” |
| “A smaller fraction of counted movement samples gained speed.” | “Your mouse and keyboard were out of sync.” |
| “Takeoff speed was lower than your comparable successful attempts.” | “Your prestrafe technique caused the failure.” |
| “The source flagged a descending touch / invalidity condition.” | “You hit the wall and therefore failed.” |

These examples are wording constraints, not implemented features or a proposed application architecture.

## Evidence that would unlock stronger conclusions

First obtain the matching source for `/dt`, custom includes/dictionary and the installed binary/version information. Then verify, using existing observation facilities and separate non-record test material, whether a synchronized, lossless series of input state, angles, position/velocity, event phase and time is available at all. Required additions are **research requirements**, not authorization to modify the official plugin.

Any causal diagnosis would also require explicit intended jump/landing context and a validated reference or movement model, rather than thresholds guessed from these aggregates. Demos require separate proof of which channels they preserve; HUD visibility is insufficient evidence.
