# KZ-Rush: frame admission and PreThink state machine

Phase 4C · 2026-11-03 · static analysis of the SHA-256-identified local binary.
**Result: partial. No KZ Coach engine was implemented.**

## 1. Executive summary

The six direct `calcStrafes` calls and their immediate arguments, bad-frame
assignments, category branching, and normal history tail are reconstructed.
The complete mechanical PreThink CFG is available. **An exact decision from
pre-callback player state to post-callback state is not yet established.**

The principal blocker is an actual data dependency, not missing gameplay
terminology: `preCalc` receives `&flPrevHorSpeed` and forwards that reference
to `preBhop`, which writes through it at C168772. That helper's complete
correction predicate, and other helper-produced state, prevent a closed physical
input predicate and exact gain formula for all six sites. Interpretation stops
at those interfaces. This is not a disassembler inconsistency.

Important findings:

1. **[V]** Four air-terminal sites pass bad=1; the air fallback passes 0;
   the categorized-ground terminal site passes the ladder boolean (§4–5).
2. **[V]** Bad is a stack local initialized on each invocation, not persistent
   history. Every direct CS call has an explicit dominating assignment.
3. **[V]** Categorized ground is physical-ground-or-ladder, optionally promoted
   by a duck-release-gated trace test. It is not just `FL_ONGROUND` (§6).
4. **[V]** The ordinary air call C114580 does not require a nonzero start
   marker. Thus CS activity and a presentable active attempt are different axes.
5. **[V]** `findGoodFrame` selects jump-bug diagnostics; its return is always
   zero. No demonstrated retrospective edit to CS history was found (§7).
6. **[I]** Normal-return direct paths admit at most one CS call per invocation;
   this does not certify deduplication across invocations or exception paths.

### Evidence notation

**[V]** bytes/instructions or identified source directly inspected; **[D]** an
external documented contract; **[I]** a consequence with assumptions; **[H]**
unresolved. Binary evidence uses decimal C addresses, exclusive function ends,
and D roots. High confidence applies to local decoded operations, not to
runtime occurrence. Helper-boundary predicates are explicitly incomplete.

## 2. Integrity and methodology

| Check | Observed result [V; high confidence] |
|---|---|
| Original SHA-256 | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| In-memory decompressed SHA-256 | `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |
| Header | file/VM version 8; code C `[0,332116)` |
| Image coordinates | `I=4912+C`; initialized data begins I337028 |
| Global decode | 51,250 instructions; `validate` accepts targets and native ordinals |
| Existing generated artifacts | All ten outputs already present from `analyze(raw)` reproduce exactly |
| Inspector tests | `python3 -m unittest tools.amx_inspector.test_inspector -q`: 27 passed |
| PreThink | C[101720,117536), 2,524 instructions, 367 call-split basic blocks |
| Original protection | No writes to `reference/`; original hash rechecked at delivery |

Read [Phase 4B](11-kz-rush-frame-counters-reconstruction.md) in full first.
The existing inspector's `unpack_container`, `Header`, `decode`, `validate`,
`debug_info`, `references`, and `basic_blocks` were reused. No inspector changes,
tool installation, plugin execution, VM, emulation, compilation, server access,
or game-data/configuration changes were made. Source inspection is not native
execution. Temporary annotated text listings were analysis aids, not evidence
requiring preservation: the commands below recreate their underlying data.

### Reproducible commands

```sh
sha256sum reference/kz_jump_stats.amxx
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.amx_inspector.test_inspector -q
```

The complete CFG-generation recipe is in
[`hamPlayerPreThink.cfg.md`](../analysis/amx_disassembly/hamPlayerPreThink.cfg.md).
For any cited interval, this additional recipe prints exact opcodes, operands,
and exact-slot reference annotations without evaluating instructions:

```python
from pathlib import Path
from tools.amx_inspector.inspector import (
    AMXX_SHA, AMX_SHA, Header, unpack_container, decode, debug_info,
    definitions, validate, analyze, references,
)
raw = Path('reference/kz_jump_stats.amxx').read_bytes()
im = unpack_container(raw, AMXX_SHA, AMX_SHA)  # fails closed on either hash
h = Header.parse(im)
ins = decode(im[h.cod:h.dat], 0, h.dat-h.cod)
validate(ins, h.dat-h.cod, len(definitions(im,h)['natives']))
symbols = debug_info(im,h)['symbols']
for name, text in analyze(raw).items():
    p = Path('analysis/amx_disassembly') / name
    if p.exists():
        assert p.read_text() == text, name
lo, hi = 101720, 117536  # substitute any cited [lo, hi) interval
for i in ins:
    if lo <= i.c < hi:
        print(i.c, i.spec.name, i.operands, references(i,symbols))
```

Use `PYTHONDONTWRITEBYTECODE=1` when running the recipe. Symbol matches on
constants are address candidates, not proven reads. Array pointees require
tracking `IDXADDR/LOAD_I/ADD/STOR_I`; names alone are never the evidence.

## 3. PreThink CFG and early exits

The [readable region graph](../analysis/amx_disassembly/hamPlayerPreThink.cfg.md)
records conditions, successors, reads, writes and attempt effects. Its
[mechanical graph](../analysis/amx_disassembly/hamPlayerPreThink.blocks.json)
retains every decoded instruction's block membership and all normal edges.
These complement each other: a region is not falsely presented as one basic
block, and the JSON does not pretend to resolve array aliases or gameplay.

**[V; high]** The only explicit PreThink returns are C101900, C102084 and
C117532. The first two call `resetVars` C96448 and bypass all capture/history:

* C101732–101900: `!is_user_alive(id) || pev(id,69)==8`.
* C101908–102084: `get_cvar_num(D1176544)<2 ||
  get_cvar_num(D1176588)!=2000`. Reading unpacked data cells identifies these
  strings as `sv_gravity` and `sv_maxvelocity` respectively.

**[D]** Official headers identify selector 69 as movetype and 8 as NOCLIP
(§11). That physical meaning is distinct from the binary numeric predicate.
**[V]** The hook-used reset at C104028 continues into the callback. It must not
be modeled as an early return. Native failure/BOUNDS aborts are outside these
three normal return edges.

## 4. Audit of the six calls

### Notation and argument origins

All variables below are per-id unless stated otherwise:

| Alias | Binary storage / meaning [V] |
|---|---|
| `G`, `PG` | categorized ground D326980, previous category D327112 |
| `B` | block-stats-show D333460; its value at the named branch, not entry value |
| `S` | start marker vector D325660; nonzero means `!is_zero_vec(S)`, helper C[3268,3464) |
| `M` | stats mode D449664 |
| `T`, `L`, `W` | trigger contact D333724, slide D328576, water D328840 |
| `Z`, `PZ`, `SZ` | current/previous/start origin Z, roots D331084/D331612/D325660 |
| `VZ` | current velocity Z, root D329500 |
| `SD`, `D` | start-in-duck D326320, current in-duck D327904 |
| `H` | `bSameHeight`, FRM−32 |
| `v`, `p*` | current horizontal-speed local FRM−4, possibly corrected previous-speed local FRM−8 |
| `E` | the two initial rejection guards passed and execution reaches this region normally |

The start vector check compares all three components to zero, not just Z and
not a tolerance. The exact helper end can be obtained from `symbols.json`;
the local predicate is the helper result observed at each call.

**[V; high]** Common actual argument tuple is
`(id, v, floatsub(v,p*), G, bad)`.
FRM−4 is initialized by `vector_hor_length(current velocity)` C102424–102492;
FRM−8 by the previous vector norm C102504–102572. **But** C107800 passes its
address to `preCalc` C140812 via the call C107976. Therefore `p*` is the
post-helper value, not unconditionally the norm first calculated.

All predicates below are exact **local control predicates after preceding
helpers return**, not a closed expression in physical inputs at callback entry.
`A` abbreviates `E && !B at C109396 && !G`.
`Q` abbreviates nonzero S, `VZ<0`, and `!B` at C111424.
`R` is `M!=2 || g_flLanding!=0` after the branch's landing calculation.

| Callsite C | Entry predicate | flHorSpeed | flGain | bGround | bBadLastFrame | Subsequent effects | Evidence |
|---:|---|---|---|---|---|---|---|
| 110880 | A; S nonzero; M=2; T or L | v | v−p* | 0 | 1 | showDistance/showStrafes; B=1; later air calls suppressed | C110428–111028; `STOR_S_PRI -36` C110692 |
| 112240 | A; after surface gate !B; Q; SD; Z<=SZ; PZ>SZ; R | v | v−p* | 0 | 1 | displays; B=1; join fallback test/history | C111224–112392; assignment C111852 |
| 113728 | A; after surface gate !B; Q; !SD; PZ>SZ−18; Z<=SZ−18; D; R | v | v−p* | 0 | 1 | calcDistanceAir(1)/calcLandingAir before CS; displays and B=1 after | C112864–113880; assignment C113340 |
| 114252 | Same lower-plane predicate as preceding row, but !D; R | v | v−p* | 0 | 1 | calcLandingAir before CS; displays and B=1 after | C112864–114400; assignment C113900 |
| 114580 | A and !B at C114432 after all earlier air branches | v | v−p* | 0 | 0 | jump C115252; no terminal displays at this site | C114404–114588; `ZERO_S -36` C114452 |
| 115148 | E; !B at C109396; G; !PG; S nonzero; M=2 or H | v | v−p* | 1 | ladder!=0 | distance/landing before CS; displays; common tail rearms B on G | C114596–115244; assignments C114900/C114948 |

The first four terminal air routes set failed=1. C110880 sets H=0; the other
three set H=1. Ground-terminal failed is assigned `g_bTouched` C114840,
independently of bad. Distance/landing and display calls are not expanded into
their own complete state machines here; their outputs and transitive writes
remain a dependency, especially `R`.

### Two important negative predicates

**[V]** C114580 does **not** require S nonzero or Q. If start detection clears
S, the fallback can still call CS. Calling it “active airborne attempt only”
would be false. No frame-count guard exists in the caller at this site.

**[V]** Crossing SZ at C112536/C112688 optionally calculates distance and sets
no-duck state. `JZER C112864` at C112728 rejoins directly before the lower
plane test. Thus crossing SZ in this invocation is **not required** for
C113728/C114252. Those require crossing SZ−18. This resolves conflicting
research readings using the actual jump target, not agreement between readers.

### Helper-boundary blockers

**[V]** At C143648, `PUSH_S 32` forwards the previous-speed reference to
`preBhop` C164904 via C143680. Its FRM+20 is that reference; `SREF_S_PRI 20`
at C168772 writes through it. The complete dominating correction predicate
and formula remain **[H]**. By contrast, `LREF_S_PRI 32; PUSH_PRI` at
C142332/C142340 and analogous sites dereferences the argument before passing
it to `preLadder`, `preSlide`, `preWater`, `preFirstDD`, `preGstrafe`,
`preFirstJump`, `preFalling`, `preBounce`, and `preSlip`. Those sequences do
not establish reference forwarding. `calcJumpOff`,
edge/jump-bug checking and distance/landing helpers also produce state used
here. The table deliberately does not claim these dependencies are reduced.

## 5. bBadLastFrame

**[V; high]** FRM−36 is created with `PUSH_C 0` at C109092. There are seven
subsequent explicit assignments, not six: 1 at C110692/C111852/C113340/
C113900/C114900, and 0 at C114452/**C114948**. The last zero was not in the
six-site list from Phase 4B. The two ladder alternatives merge before C115148.

| Question | Answer, bounded to the decoded direct paths |
|---|---|
| When 0? | Ordinary air fallback; non-ladder categorized-ground terminal |
| When 1? | Trigger/slide terminal in mode 2; descending height-plane terminal; ladder terminal |
| Previous invocation retained? | No: stack-local initialization, not a persistent global |
| Every CS call assigned? | Yes, explicit assignment dominates each direct site |
| Flags involved? | Indirectly via category, ladder, duck and slide state |
| Speed/position/distance involved? | Descending VZ and origin-plane crossings; distance/landing helper results gate some sites |
| Equivalent to invalid sample? | No universal equivalence. It is an explicit branch flag, not every reason CS is skipped |
| Necessarily landing? | No: the four air-terminal sites pass G=0 |
| Retrospective correction? | No demonstrated connection from findGoodFrame; previous-speed corrections are a separate unresolved dependency |
| Can counters still grow? | Yes: CS C183584–184392 records history; C186128–186320 increments each previous active key's Frames; overlaps/desync/angle still run |

**[V]** CS C186708 skips good/gain/loss for bad, not all accounting. It reaches
the desync/angle region C187168 onward. Bad also requests closure of all
previous active directions (C189716–190028). A bad-marked call that fails the
capacity guards does none of that; caller presentation can nevertheless proceed.

## 6. Categorized ground

### Physical and categorized layers [V; high]

* `ladder = pev(id,69)==5`, C103116–103168. This is the plugin's label;
  **[D]** the official numeric movetype name is FLY, not an independent proof
  of physical contact with a ladder.
* `water = (flags&16)!=0 && pev(id,87)>=2`, C102908–103076.
* `inDuck = flags&16384`, C103176–103252.
* `physical = ((flags&512)!=0) || ladder`, C103344–103468;
  previous physical uses previous flags/ladder C103480–103612.
* `G=physical`, C107092–107132. If !physical, !(buttons&4),
  (prevButtons&4), and isCategorized(id)!=0, write G=1 C107140–107368.
* Normal tail copies G to PG, C115944–116008. A guard-return does not.

| physical | Duck-release gate | isCategorized | G |
|---:|---:|---:|---:|
| 1 | any | not called | 1 |
| 0 | 0 | not called | 0 |
| 0 | 1 | 0 | 0 |
| 0 | 1 | nonzero | 1 |

There is no separate surface-material or water term in this local truth table.
Slide/water instead affect other admission and diagnostic paths. Reaching
ground closes CS directions; remaining on ground normally does not call CS
through the ground branch because !PG is required.

### isCategorized C[117536,118768)

**[V]** Reject if previous vertical velocity >180 (C117548–117660). Copy
current origin to endpoint; create a trace handle and issue engfunc selector
32. First start/end origins are identical. Read trace field 4; if fraction<1,
return false at C118108. Otherwise lower endpoint Z by 2 (C118116–118188),
repeat the trace, read field 7's Z, field 1 and field 0, then free the handle.
Return true exactly when normalZ>=Float(0.7) and !startSolid and !allSolid
(C118592–118764). The threshold cell is 1060320051, not an exact real 0.7.

**[D]** Identified official headers map engfunc 32 to TraceHull and those
trace fields to fraction/plane normal/startSolid/allSolid (§11). **[I]** This
is a near-ground category test, not interchangeable with the raw ground bit.
The early fraction-rejection path has no explicit free_tr2 before returning;
no runtime leak or installed-module lifetime behavior is claimed.

**[H]** These are the direct writes observed in PreThink, not an exhaustive
global alias/writer inventory or a proof of initial category values for every
client lifecycle. resetVars does not visibly reset G/PG in its decoded body.

## 7. findGoodFrame

**[V; high]** C[304728,306316), one global direct callsite C106720 found by
scanning decoded CALL targets. Entry decrements `g_iWaitForGoodFrame` D447524;
returns zero if the new value is zero, if !(flags&512), or ArraySize<40
(C304728–304996). Negative values are not rejected by an explicit <=0 test
inside this helper; its observed caller only selects it when wait>0.

Continuing path:

* Derive distance using rounded last-ground Z and jump-bug-land Z
  C305012–305212; exact sign/argument transformation is not certified here.
* `framesShift=wait_after_decrement−40`, C305232–305288.
* Read current origin Z and ArrayGetCell(originArray,39), C305292–305452.
* Predict Z from that array value plus
  `(prevVelocityZ − (float(sv_gravity)/2 * prevFrameTime))*prevFrameTime`,
  C305464–305844, under ordinary finite Float semantics.
* Current Z below prediction chooses `jumpBugNotPoss` C306112;
  otherwise `jumpBugFailed` C306292. Both paths return zero.

**[V]** The helper does not search all 40 elements for a candidate. It reads
one fixed element, decrements wait and calls diagnostics. PreThink appends
current Z before this call when physical-ground is false, deleting element 0
first if the array size is >=40 (C105548–105800). When physical-ground is true,
that append is skipped. Thus a fixed index's physical age depends on the path.
The ground-array clear occurs later C106968–107084.

The two diagnostic bodies were inspected as formatting/presentation routines;
no demonstrated CS frame-array/strafe-counter rewrite or gain correction was
found there. **[I]** The name suggests recovery, but the observed body is a
delayed jump-bug diagnostic, not a frame selector for CS. **[H]** A complete
transitive alias proof is not supplied. If no guard passes, it returns 0
without selecting a diagnostic; the wait decrement remains.

## 8. Capture chronology and history

**[V]** Registrations reported in Phase 4B: PreThink C13068, PostThink C13136,
CmdStart C13792, all with registration post=0. This does not establish the
engine's total scheduling order or identify a callback with a rendered frame.

```text
Retained state from last normally completed PreThink
 → initial guards [may reset+return without refreshing retained state]
 → current pev capture; current/previous/old speed norms
 → physical/category/diagnostic checks
 → preCalc(&previousSpeed) and pattern update
 → start-marker/reset/height/admission branches
 → zero or one direct calcStrafes call, subject to callee capacity
 → optional terminal presentation
 → common rearm/category-arrival bookkeeping
 → oldButtons←prevButtons; prevButtons←buttons
 → oldVelocity←prevVelocity; prevVelocity←velocity
 → prevOrigin←origin; prevAngles←angles; remaining histories
 → normal return
```

| Data | Producer / copy point [V] | CS interpretation / exception |
|---|---|---|
| command duration, forward/side move | fwCmdStart C99728–100076, get_uc selectors 1/3/4 | Not direct CS key-state capture; own callback guard applies |
| buttons | pev selector81 C102252–102328 | Current N versus retained P in CS; old/prev copy C116016–116152 |
| velocities | selector120 C102336–102412 | CS gain uses local corrected p*, desync uses retained vector; copy C116160–116364 |
| angles | selector126 C102752–102828 | Current/retained yaw; prev copy C116484–116580 |
| flags and category | C115872–116008 copies | No copy on two early return paths |
| frameCount | CS C184392 increments after history write | No increment on rejected CS capacity entry |
| post-think height | hamPlayerPostThink C101404–101720 | Current raw flags against cached flags; preHeight capture, not direct CS counting |

**[V/I]** A normal callback with B blocking CS still advances capture history.
Consequently capture continuity does not imply all intervals appear in the CS
arrays. An early callback return can leave stale button/velocity/angle state;
the next admitted callback can compare against that older sample. A press and
release wholly inside skipped callbacks need not be represented in CS P/N.
This is a possible information loss under explicit scheduling assumptions,
not an observed engine bug or proof of one callback per command.

**[V]** resetVars C96448–99728 clears CS counts/metrics and wait, assigns
0.02 frame-time defaults, but does not visibly copy/reset all cached buttons,
vectors, flags or G/PG. startStrafes C182492–182592 resets only frameCount and
strafeCount (stores C182540/C182584). First-call per-direction initialization
remains conditional inside CS as documented in Phase 4B.

## 9. Attempt-state model

This is a product of axes, not a single authoritative gameplay enum:

* Player: physical bits, movetype, water/duck/slide; captured now.
* Capture: cached flags/buttons/vectors/category and time histories.
* Attempt: start marker, start duck/ladder, counters and distance fields.
* Presentation: B, touched/trigger and local failed/sameHeight/bad.

| Source state | Predicate | Destination | Action | Callsite / evidence |
|---|---|---|---|---|
| Any | initial rejection | reset capture-skipped | resetVars, return | C101880/C102064 [V] |
| G previous, !G now | departure predicate true | start marker initialized | startDistance; startStrafes | C110304/C110332 [V]; “departure” [I] |
| Same transition | departure predicate false | start marker absent | zero start vector | C110352–110412 [V] |
| !G and !B | no accepted terminal branch | ordinary CS capture | bad=0, CS | C114580 [V], regardless of start marker |
| !G and !B | trigger/slide terminal or eligible descending plane | presented/blocked | CS bad=1, display, set B | four terminal air calls [V] |
| B | call gate | capture-only | skip CS; reach history tail | C109400→115252 [V] |
| !PG and G | start marker and (M=2 or H) and !B | presented arrival | CS with ladder bad; display | C115148 [V]; arrival [I] |
| G | normal tail | presentation rearmed | clear B/touched/trigger | C115328–115492 [V] |
| !PG and G | normal tail | arrival bookkeeping reset | clear landing/friction/etc. | C115500–115864 [V] |

**[V]** On !G/PG the departure predicate encoded C109496–110268 is:
`VZ>0 || (M==2 && (VZ>=−dV_grav/2 || prevLadder)) ||
(doubleDuck && VZ>=−dV_grav)`.
`doubleDuck = !prevInDuck && !(prevButtons&4) && (oldButtons&4)`.
`dV_grav = float(sv_gravity)*entityGravity*prevFrameTime` C105048–105252.
The called startDistance copies previous origin/start posture and records
attempt fields; those helper effects must be respected, not fabricated as a
new enum. The preCalc dependency still precedes these predicates.

**[V]** H for categorized arrival is a strict tolerance `<0.03125` around
currentZ−startZ, except !startDuck/currentDuck compares to startZ−18
(C108016–109080). It is initialized to zero. Physical equal-height is an
interpretation [I], not exact equality or the raw ground-bit test.

## 10. Limits, duplicate closure and special transitions

| Case | Status | Demonstrable result / remaining condition |
|---|---|---|
| frameCount=499 | Resolved locally | CS admits, writes index499, increments to500: C182608–184392 [V] |
| frameCount=500 | Resolved locally | Entry returns before recording; caller still runs its tail/display path [V] |
| strafeCount=50 | Resolved locally | Entry rejects equality, C182700–182728 [V] |
| strafeCount=49 and multiple emits | Resolved under conditions | No second capacity guard inside close loop; index50 can meet BOUNDS49. Global reachability remains unproven [I] |
| Duplicate closures within invocation | Resolved under conditions | At most one direct CS site on ordinary returning paths; multiple different key directions can still close [I] |
| Duplicate closures across callbacks | Pending | Requires complete reset/helper/counter reachability; CS itself has no emitted latch |
| Ground→air | Resolved under conditions | !G/PG departure test; initialize or clear marker; fallback may still call CS |
| Air→ground | Resolved under conditions | G/!PG plus start and mode/H permit terminal; otherwise no ground CS |
| Air→ladder | Resolved under conditions | movetype==5 makes G=1; eligible ground terminal bad=1 |
| Ladder→air | Resolved under conditions | previous ladder can satisfy mode2 departure term; full auxiliary state effects unresolved |
| Water | Resolved locally, helper dependency | water predicate known; sets B before ordinary air admission; preWater effects pending |
| Teleport / invalid movement | Partial | trigger/slide path and vz sign-reversal suppression known; not every teleport detector/writer audited |
| No previous keys | Resolved locally | CS still records history, no per-key F, overlap clears; admission does not require a key |
| Multiple previous keys | Resolved locally | Multiple F and possible rows; unique gain selector; capacity caveat |
| Last gain negative | Resolved locally | bad=1 suppresses gain/loss; bad=0 accounts loss for q; ground alone does not suppress |
| Direction change on arrival | Resolved under conditions | G inhibits aerial key initialization; counts P and closes each P, even if N changes |

The caller contains no demonstrated protective strafeCount recheck before its
CS calls. A static potentially faulting path is not an observed overflow or
evidence of silent truncation. BOUNDS is a VM check, not permission to write
past a row. Rejected calls do not inform the caller through a tested result.

## 11. Natives and external contracts

Official source consulted at pinned AlliedModders/amxmodx revision
`8fc12670ea86470a0bfed4c35db5de73d3a39e8a`, fetched read-only on 2026-11-03:

* [float.cpp](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/float.cpp)
* [fakemeta_const.inc](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/plugins/include/fakemeta_const.inc)
* [hlsdk_const.inc](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/plugins/include/hlsdk_const.inc)

| Native / contract | Identified source result | Scope |
|---|---|---|
| floatmul | float.cpp L111–119: reinterpret params, multiply REAL | [V-source], not installed build identity |
| floatdiv | L126–134: operand1 / operand2, no local denominator guard | [V-source]; no promise about build-specific exceptional arithmetic |
| floatcmp | L223–239: equal→0, greater→1, otherwise−1 | [V-source]; NaN is not ordinary total numeric ordering |
| floatsqroot | L244–254: sqrt then result<0 check | [V-source]; do not infer an input-negative guard |
| floatsin / floatcos | L313–339: ToRadians then sin/cos | [V-source]; bytecode passes unit1; Phase4B documents degree contract [D] |
| numeric flags | hlsdk_const L24/46/51/56: duck4, water16, ground512, ducking16384 | [D] mapping used to name inspected binary masks |
| movetype | hlsdk_const L92/95: FLY5, NOCLIP8 | [D]; plugin's ladder state is equality to5 |
| traces | fakemeta_const L78,558–565 names TraceHull and fields | [D]; exact trace collision behavior depends on engine/modules |

**[V]** Compiled operators C684–752 (`>`), C1128–1196 (`<`) and
C1300–1368 (`<=`) push formal arg2 then arg1 into floatcmp and compare its
result against zero with SGRTR/SLESS/SLEQ. This fixes the operand ordering used
in §4/9 rather than trusting the debug operator names.

**[H]** No installed AMXX/fakemeta/engine build was identified or inspected.
`pev`, `get_uc`, full Ham callback scheduling and yaw normalization are not
verified against that installed environment. This phase confirms numeric call
sites and source contracts where stated, not an end-to-end build equivalence.
Finite ordinary motion is the interpretive domain; NaN, infinity, signed-zero,
precision/JIT and zero-speed normalization are not certified.

## 12. Eight static scenario traces

These are reasoned paths [I], not execution or an emulated algorithm. Each
assumes finite inputs, coherent arrays, normal helper returns, and capacity
unless explicitly varied. No speeds, angles or distances are invented.

| Scenario | Initial assumptions / admission | CS and accounting | History / closure / uncertainty |
|---|---|---|---|
| 1. Normal LongJump | E; !G/PG; departure predicate true; helpers preserve ordinary coherent state; B false | startDistance/startStrafes; C114580 on nonterminal air callbacks; C115148 on eligible G/!PG with H or M2 | P is previous committed buttons; final G closes P; normal tail advances. Named LongJump classification and p* corrections remain conditional |
| 2. Ends bad | E, !G, S nonzero, M2, T or L, B false at main gate | C110880 bad1; historical sample/F/O/D/A may grow; no good/gain/loss; P closures filtered by full_overlap | displays then B1; history advances. No physical touchdown required |
| 3. Failed without valid arrival | E, !G, S nonzero, descending; SD with start-plane crossing or !SD with lower-plane crossing; R true | matching C112240/113728/114252, bad1 and failed1 | B1 suppresses subsequent air CS; tail advances. If R false, fallback can instead process bad0; helper landing decides R |
| 4. Key changes last sample | Scenario1 final eligible category transition; P old key, N different key | C115148, G1; count old P; no aerial initialization; close old P | new N retained at tail; belongs to future interpretation, not retroactively to old counters |
| 5. Two keys on arrival | Same eligible category transition; two P directions | Both Frames grow; q chosen by earliest start; at most one G/gain/D/A attribution; both may emit | full_overlap filters each; row-capacity caveat. No single-row guarantee |
| 6. Early return | dead/native state rejection or cvar rejection | no CS, resetVars then RETN | No common copies; retained buttons/vectors/categories may be stale. Next callback requires re-evaluation, not synthetic missing samples |
| 7. Frame limit | Air fallback with frameCount499 and row capacity | first call writes499 and raises500; next admitted site invokes CS but CS rejects | Caller still advances history and may eventually display; tail has no replay of rejected sample |
| 8. Near strafe limit | CS entry count49, >=2 P directions satisfy emit | first row can use49 and increment50; second reaches BOUNDS49 at index50 | Static local fault path only; caller-level reachable invariant not proven. Fault may prevent normal tail; no post-fault state invented |

For every admitted CS path the exact counter rules are those of Phase4B, not
additional gameplay assumptions. These partial traces do not replace the
missing entry-to-helper-state reconstruction.

## 13. Compatibility and correction of Phase 4B

| Phase4B rule | This phase's result |
|---|---|
| Frames for every active previous key | Compatible; bad admission still reaches that region |
| Good only selected direction, positive gain, not bad | Compatible; bad=0 does not by itself imply positive gain |
| Overlap from previous-key cardinality | Compatible; admission does not replace P with N |
| Desync even when bad | Compatible; terminal bad routes are concrete callers |
| Signed angular accumulation | Compatible; neither ground nor bad universally suppresses it |
| Closure by release/ground/bad | Compatible; all three can coincide, evaluated per direction |
| full_overlap filters emission, not accumulation | Compatible; caller does not change that local rule |

**Correction proposal (not a silent edit):** Phase4B §3 describes flGain as the
current norm minus the previous norm. New evidence is `PUSHADDR -8` C107800
before `preCalc`, then forwarding by reference. The contradiction is with an
unconditional raw-norm interpretation, not with the callsite's `floatsub(v,p*)`.
Replace that interpretation with “current horizontal-speed local minus the
possibly corrected previous-speed local.” Good/gain/loss formulas stay valid
in terms of the supplied gain; physical attribution cannot yet be exact.
Document11 remains unchanged so this correction remains visible.

The bad-store inventory also adds C114948 (zero on non-ladder arrival).
No previous local counter rule was disproved. No claim of fully resolved
cross-callback duplication or overflow prevention is introduced.

## 14. Remaining uncertainty and completion assessment

**Blocked against complete success:** preCalc/pre* correction and helper state
are not fully reduced; R depends on landing helpers; category initial/global
writer inventory is incomplete; row-capacity and cross-callback closure
invariants are unproven. Thus the six calls have explicit local predicates,
but none is advertised as a complete physical-input admission specification.

The complete mechanical CFG, explicit normal returns, local bad assignments,
category test, history-copy sequence, and local capacity behavior are resolved.
External build identity/scheduling remains separate from those binary facts.
No inconsistent instruction decode was detected. No phase advancement follows
from publishing this partial result.

## 15. Minimum next research and engine recommendation

**Do not implement a fidelity-claimed independent engine yet.** It is possible
to discuss interfaces or evidence requirements, but not to promise KZ-Rush
equivalence or authorize implementation from this report.

Minimum next static work, only with a subsequent authorized scope:

1. Expand preCalc's by-reference `preBhop` correction, plus relevant calcJumpOff
   and distance/landing/diagnostic state writers. Specify p* and R from known inputs.
2. Audit category/start/block/counter writers and reset reachability globally;
   prove or bound cross-callback duplicate and 49→multiple-row scenarios.
3. Identify source/build provenance for the actual engine/AMXX modules and
   establish callback/command ordering statically where possible.

No live capture, HUD, trainer, replay or motor was produced. No server or
records were accessed. The unproven helper contracts—not the number of static
call sites—are the remaining barrier to the requested end-to-end guarantee.
