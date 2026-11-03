# hamPlayerPreThink: static control-flow map

Phase 4C, 2026-11-03. Entry C101720; exclusive end C117536.
**Partial semantic reconstruction, not an executable model.** See [report](../../docs/12-kz-rush-prethink-state-machine.md).

## Evidence boundary

[V] The existing inspector decodes 2,524 instructions in this function into
367 call-split basic blocks, with no unresolved indirect control transfer.
There are three `RETN` instructions: C101900, C102084, C117532.
The companion `hamPlayerPreThink.blocks.json` contains the complete mechanical
graph, including call continuations, not a claim that every path is feasible.
The semantic regions below deliberately group multiple basic blocks.

`T/F` mean a predicate's true/false edge. Numeric C addresses are decimal.
Register-level comparisons use PRI as left operand, ALT as right operand;
call arguments are pushed right-to-left. `B` means `g_bBlockStatsShow[id]`.
Read/write descriptions below are manually resolved array accesses, not proof
of a complete transitive alias analysis. Unexpanded calls remain dependencies.

## Region graph and attempt effects

| Region C | Condition / relevant instruction | Successors | Reads | Writes | Attempt effect |
|---|---|---|---|---|---|
| 101720–101852 | `!is_user_alive(id) || pev(id,69)==8`; `JZER 101904` | T:101860, F:101904 | id, native state | none before branch | Reject callback |
| 101860–101900 | `CALL 96448`, `RETN` | return | id | resetVars effects | Reset; no history tail |
| 101904–102036 | `sv_gravity<2 || sv_maxvelocity!=2000`; `JZER 102088` | T:102044, F:102088 | cvars | none | Configuration rejection |
| 102044–102084 | `CALL 96448`, `RETN` | return | id | resetVars effects | Reset; no history tail |
| 102088–103332 | Native captures, speed norms, slide helper | 103336 | pev selectors 34,84,81,120,118,126,69,87,60; prev/old velocity | current gravity/flags/buttons/velocity/origin/angles/slide/water/ladder/duck/fuser2; speed locals | Capture; no CS yet |
| 103336–103612 | bit 512 or ladder, current and previous | 103624 | flags, ladder and histories | local ground booleans | Physical-state baseline |
| 103624–103808 | gametime < last weapon change + 2 | 103812 | time/history | touched=1 if true | Marks attempt context |
| 103816–104036 | hook-used; physical ground and speed<260 clear flag, otherwise resetVars | 104040 | hook, ground, speed | hook or reset state | Reset here does NOT return |
| 104040–104312 | prev vz<0 and current vz>0 | 104316 | velocity histories | B=1 if true | Suppresses later admission |
| 104320–105040 | slide/water set used flags, clear bug checks; ground and speed<260 clears used flags | 105048 | slide/water/ground/speed | used/check flags | Special-surface bookkeeping |
| 105048–105252 | gravity product | 105264 | sv_gravity, entity gravity, previous frame time | dV_grav local | Start predicate input |
| 105264–106528 | Physical ground: clear last-ground, initialize checks; otherwise append current Z, cap array at 40, edge checks | 106532 | origins, velocities, helpers | diagnostic array/check/block state | Auxiliary admission dependency |
| 106532–106960 | jump-bug checking; mode=2 and wait>0 calls findGoodFrame C106720, otherwise alternate helpers | 106968 | check/mode/wait | diagnostic state; B if jumpbug-done | Unexpanded helper dependency |
| 106968–107084 | physical ground | 107092 | bGround | clear origin array and wait | Diagnostic reset, not CS reset |
| 107092–107132 | unconditional copy | 107140 | bGround | CatGround=bGround | Category baseline |
| 107140–107368 | !physical-ground and !(buttons&4) and (prevButtons&4), then isCategorized!=0 | 107376 | buttons, trace helper | CatGround=1 if accepted | Category override |
| 107376–107620 | CatGround and PrevCatGround; edgeFriction | 107628 | categories, previous speed | friction counter | Continuous ground bookkeeping |
| 107628–107772 | !CatGround and PrevCatGround | 107784 | categories | bHighJump via calcJumpOff | [I] Departure preparation |
| 107784–108004 | preCalc(...,&prevSpeed,...), updatePatterns | 108016 | categories, speeds, histories | potentially corrected previous-speed local and helper state | **Unresolved transitive effects** |
| 108016–109080 | nonzero start and CatGround and !PrevCatGround; duck-dependent height tolerance | 109092 | start/current Z, duck | bSameHeight | Landing eligibility |
| 109092–109360 | locals initialized to 0; current/previous trigger contact marks touched; mode<2 sets B | 109368 | contacts/mode | bad=0, failed=0, touched/B | Global call gate preparation |
| 109368–109444 | !B, then !CatGround | B:115252; air:109456; ground:114596 | B, category | none | Separate presentation and physical axes |
| 109456–110420 | PrevCatGround; departure predicate in report | 110428 | vertical speed/gravity, old buttons/duck/mode | startDistance/startStrafes OR zero start vector | Start or discard start marker |
| 110428–110672 | nonzero start and mode=2 and (trigger or slide) | T:110684; F:111032 | start/mode/contacts | none | Special terminal route |
| 110684–111028 | bad=1; touched-TP distance; **CS C110880**; displays; B=1 | 111032 | CS arguments | counters, outputs, B | Terminal presentation |
| 111032–111216 | trigger or slide or water | 111224 | contact/surface booleans | B=1 if true | Reject ordinary continuation |
| 111224–111456 | nonzero start and vz<0 and !B | T:111468; F:114404 | start/velocity/B | none | Descending candidate |
| 111468–111496 | start-in-duck | T:111508; F:112404 | start duck | none | Height branch |
| 111508–111832 | currentZ<=startZ and prevZ>startZ | T:111844; F:112392 | origins | none | Cross start plane |
| 111844–112112 | bad=failed=sameHeight=1; calcDistanceAir(0), calcLandingAir; mode!=2 or landing!=0 | T:112124; F:112392 | mode, helper-produced landing | locals and auxiliary state | Conditional terminal admission |
| 112124–112388 | **CS C112240**; displays; B=1 | 112392→114404 | CS arguments | counters, outputs, B | Terminal presentation |
| 112404–112728 | prevZ>startZ and currentZ<=startZ | T:112740; F:112864 | origins | none | **Not a dominator of C113044** |
| 112740–112860 | !noDuckStatsState → calcDistanceAir(0), set noDuckStatsState | 112864 | noDuck state | distance state/noDuck flag | Optional preparatory side effect |
| 112864–113280 | prevZ>startZ−18 and currentZ<=startZ−18 | T:113292; F:114404 | origins | none | Independent lower-plane test |
| 113292–113320 | current in-duck | T:113332; F:113892 | duck flag | none | Select terminal calculation |
| 113332–113600 | bad=failed=sameHeight=1; calcDistanceAir(1), calcLandingAir; mode!=2 or landing!=0 | T:113612; F:113880 | helper landing/mode | locals, distance/landing state | Conditional terminal admission |
| 113612–113876 | **CS C113728**; displays; B=1 | 113880→114404 | CS arguments | counters, outputs, B | Terminal presentation |
| 113892–114124 | bad=failed=sameHeight=1; calcLandingAir; mode!=2 or landing!=0 | T:114136; F:114404 | helper landing/mode | locals, landing state | Conditional terminal admission |
| 114136–114400 | **CS C114252**; displays; B=1 | 114404 | CS arguments | counters, outputs, B | Terminal presentation |
| 114404–114440 | !B | T:114452; F:114588 | B | none | Air fallback gate |
| 114452–114588 | bad=0; **CS C114580**; JUMP 115252 | 115252 | CS arguments | counters | Ordinary admission, even without start marker |
| 114596–114800 | !PrevCatGround and nonzero start and (mode=2 or sameHeight) | T:114812; F:115252 | category history/start/mode/local | none | [I] Eligible arrival |
| 114812–115028 | failed=touched; ladder: bad=1, touched-LD distance; otherwise bad=0, calcDistance/calcLanding | 115032 | touched/ladder | locals, distance/landing state | Ground terminal preparation |
| 115032–115244 | **CS C115148**; displays | 115252 | CS arguments | counters, outputs | Terminal presentation |
| 115252–115492 | copy prev trigger; CatGround clears B/touched/current trigger | 115500 | contacts/category | corresponding history/flags | Rearm on category |
| 115500–115864 | CatGround and !PrevCatGround | 115872 | category history | noDuck/friction/block/jumpOff/landing/beam fields zero | Arrival bookkeeping reset |
| 115872–117508 | common history tail | 117516 | current/previous captures | previous/old flags/buttons/velocities/origins/angles/other histories | Advances capture even with no CS admission |
| 117516–117532 | stack unwind, CONST_PRI 1, RETN | return | locals | stack only | Normal exit |

## Exact-edge example: the two height tests

```text
C112728 JZER C112864  -- failure of crossing startZ skips preparation only
    fallthrough C112736 ... conditional calcDistanceAir(0) ...
C112864 ... previousZ > startZ-18 ... currentZ <= startZ-18 ...
C113280 JZER C114404  -- failure skips the lower-plane terminal branches
```

[V] Therefore C113728/C114252 do NOT require crossing startZ in this same
invocation. A semantic nesting inferred from the source-like visual layout
would incorrectly exclude legitimate CFG paths.

## Reproduce the mechanical graph

Run from the repository root with Python bytecode-cache writes disabled. This
only decompresses, decodes and serializes control-flow metadata; it never
evaluates an AMX instruction. Redirect stdout outside `reference/` if desired.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import json
from pathlib import Path
from tools.amx_inspector.inspector import (
    AMXX_SHA, AMX_SHA, Header, unpack_container, decode,
    definitions, validate, basic_blocks,
)
im = unpack_container(Path('reference/kz_jump_stats.amxx').read_bytes(), AMXX_SHA, AMX_SHA)
h = Header.parse(im)
instructions = decode(im[h.cod:h.dat], 0, h.dat-h.cod)
validate(instructions, h.dat-h.cod, len(definitions(im,h)['natives']))
known = {i.c:i for i in instructions}
region = [i for i in instructions if 101720 <= i.c < 117536]
blocks = basic_blocks(region, known)
assert len(region) == 2524 and len(blocks) == 367
assert not any(b['indirect_unresolved'] for b in blocks)
print(json.dumps({'evidence':'V', 'coordinate':'C',
    'function':'hamPlayerPreThink', 'range_C':[101720,117536],
    'blocks':blocks}, indent=2, sort_keys=True))
PY
```

Each JSON block retains its instruction C addresses, exclusive end, successors,
direct callee targets and unresolved-control flag. Calls have a continuation
edge; callees are not treated as intraprocedural successors. Native failures,
BOUNDS faults, or helper non-return are not represented by those ordinary edges.
No gameplay interpretation or read/write inference is embedded in that JSON.
