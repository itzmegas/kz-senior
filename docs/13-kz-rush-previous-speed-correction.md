# KZ-Rush: conditional previous-speed correction

Phase 4D · 2026-11-03 · static analysis only.
**Result: partial at the gameplay boundary; the local correction is reconstructed.**

## 1. Executive summary

**[V]** `preBhop` does not always change previous speed. Its sole explicit
write through the speed reference is C168772. Let `p` be the incoming previous
horizontal-speed scalar and `m` the Float cell returned by `pev(id,56)`:

```text
x = floatmul(FloatCell(1067030938), m)
M = floatsqroot(floatsub(floatmul(x,x), float(16)))
K = floatmul(FloatCell(1061997773), M)

p* = K  if preBhop is called, !bJumpbug, and !(p <= M)
     p  otherwise
flGain = floatsub(v,p*)
```

The factors are binary32 approximations to 1.2 and 0.8, not exact decimals.
For ordinary finite inputs with `M>=0`, correction requires `p>M`, lowers `p`,
and increases gain. It can convert an apparent loss into positive gain.
It cannot convert positive gain into loss in that domain. **[I]**

**[V/I]** The caller route requires categorized `G=0, PG=1` and the jump-edge
conditions in §6. It is not a general per-frame normalization. The five air
calls consume post-helper `p*`; the ground call C115148 is incompatible with
this correction route under the bounded alias/native contracts below.

**[H]** A complete physical-input predicate is not established: capture/category
history, native identity and three `calcLandingAir` admission dependencies
remain. No joint physical reachability of arbitrary caller/helper states is
claimed. No KZ Coach code, server action or next phase is authorized here.

## 2. Integrity and methodology

| Object | Independently checked result [V] |
|---|---|
| Original SHA-256 | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| Decompressed SHA-256 | `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |
| Header | file/VM v8, flags2, cod4912, dat337028, hea=size1576260, stp1592644 |
| Code | C[0,332116); I=4912+C |
| Initialized data | I[337028,1576260); I=337028+D |
| Debug | I1576260 onward; function/local symbols agree with prior reports |
| Decode | 51,250 instructions; branch targets and native indices validated |
| preBhop | debug C[164904,171748); 1,123 instructions, 93 call-split blocks |
| Existing analyzer outputs | Every existing output emitted by `analyze(raw)` reproduced exactly |
| Inspector tests | 27 passed, `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.amx_inspector.test_inspector -q` |

Both prior reports were read in full before conclusions. Existing inspector
APIs were reused without changes. Decompression and decoding are not bytecode
evaluation. No plugin, VM, emulator, compiler or server was run; no dependency
was installed. Original references and previous reports were not edited.

Evidence notation: **[V]** decoded bytes or identified source; **[D]** documented
contract; **[I]** conditional deduction; **[H]** unresolved dependency. Confidence
is high for local instructions, conditional for physical interpretation, and
unknown for installed-native equivalence. Decimal C addresses and exclusive
function/block ends are used throughout.

Reproduce a cited instruction range without execution:

```python
from pathlib import Path
from tools.amx_inspector.inspector import (
    AMXX_SHA, AMX_SHA, unpack_container, Header, definitions,
    debug_info, decode, validate, references, basic_blocks,
)
raw = Path('reference/kz_jump_stats.amxx').read_bytes()
im = unpack_container(raw, AMXX_SHA, AMX_SHA)  # stop on either mismatch
h = Header.parse(im)
ins = decode(im[h.cod:h.dat], 0, h.dat-h.cod)
validate(ins, h.dat-h.cod, len(definitions(im,h)['natives']))
symbols = debug_info(im,h)['symbols']
region = [i for i in ins if 164904 <= i.c < 171748]
blocks = basic_blocks(region, {i.c:i for i in ins})
assert len(region) == 1123 and len(blocks) == 93
assert [(i.c,i.operands) for i in region
        if i.spec.name in ('SREF_S_PRI','SREF_S_ALT')] == [(168772,(20,))]
for i in region:
    print(i.c, i.spec.name, i.operands, references(i,symbols))
```

Run Python with `PYTHONDONTWRITEBYTECODE=1`. Reference annotations are slot
candidates, not automatically dereferenced global accesses. No numeric trace
below was obtained by evaluating Pawn instructions.

## 3. Complete CFG and function inventory

The [93-block table](../analysis/amx_disassembly/preBhop.cfg.md) contains
`Block C | Predicate | Reads | Writes | Successors | Effect on p* | Evidence`.
The [machine-readable graph](../analysis/amx_disassembly/preBhop.blocks.json)
contains every decoded instruction, operands, native names and debug-slot
annotations. Register-level predicates are deliberately distinguished from
the symbolic source-level predicates below.

| Region C | Role / predicate | Effect on p* | Evidence |
|---|---|---|---|
| 164904–167284 | Duck/element-height and label bookkeeping; internal branches reconverge at167284 | No explicit speed-reference write | [V] full CFG; no early RETN |
| 167284–167532 | Read selector56 and compute M | Reads local−68, writes local−68 | [V] §5 |
| 167532–167720 | bJumpbug!=0 formats jumpbug diagnostics, jumps169048 | Preserves p | [V] LOAD_S28, JZER167720, JUMP169048 |
| 167720–167784 | Read p, compare p<=M | Select correction iff comparison false | [V] LREF_S20; CALL1300; JZER168720 |
| 167784–168720 | p<=M; classify FOG/old-speed diagnostic, three formatter alternatives | Preserves p under formatter contract | [V] calls168024/168360/168636, merge168712→169048 |
| 168720–169048 | Compute K, store reference, format diagnostic | p*←K | [V] SYSREQ17 C168756, SREF_S20 C168772 |
| 169048–171036 | Jumpbug/non-jumpbug speed-difference diagnostics | Reads post-correction p* | [V] float subtraction/comparison branches in graph |
| 171036–171748 | Store element fields and return | Non-jumpbug element post-speed can receive p* | [V] C171380–171464; sole RETN171744 |

### Arguments and locals [V; debug symbols plus uses]

| FRM | Meaning / transport |
|---:|---|
| +12 | id, indexed-array/native argument |
| +16 | current horizontal speed, by value |
| +20 | previous horizontal-speed address, ident2 reference; LREF/SREF |
| +24 | old horizontal speed, by value; distinct from previous |
| +28 | bJumpbug, integer boolean derived by preCalc |
| +32 | iel, element index, by value |
| −64 | szJumpName[16], local cell buffer |
| −68 | flMaxHorSpeed, initialized at167288; pev output then transformed |

No early normal returns: all first-region paths reconverge at167284; only
RETN171744 exits. BOUNDS/native faults are not modeled as normal successors.
Direct Pawn calls are compiled comparisons `<` (six), `>` (three), `<=`, `-`
and `==`, not movement helpers. Native inventory: `formatex` (16), `floatsub`
(8), `floatadd` (4), `floatmul` (3), `pev` (1), `floatsqroot` (1). **[V]**

### Global memory inventory and scope

**[V]** Indexed loads establish reads of `g_iFOG` D325396,
`g_flPreHorSpeed` D329104, `g_flPrevFuser2` D333328,
`g_flPrevOrigin` D331612, `g_flPreHeight` D329236 and element metadata
`g_iElementType` D339532 / `g_flElementHeight` D342832. Element arrays
also participate in read/modify/write bookkeeping in the first region.
Writes include element pre-speed D340192, FOG D340852, post-speed D341512,
fuser2 D342172, height D342832, count D343492, AXN detection D325528,
and color cells D376888/892/896. Formatter destinations include console
D366196, HUD D344812 and short HUD D355504. The graph retains instructions
for each access; symbols alone are not evidence of its direction.

**[H]** This is an identified-root inventory, not universal disjointness of
dynamic arrays/native destinations. No direct Phase4B metric-root access
or CS call occurs in preBhop. This does not prove every transitive native
side effect absent on an unidentified runtime.

## 4. Pointer provenance and writer audit

```text
PreThink FRM−8 initialized at C102572 from previous vector norm
  → PUSHADDR −8 C107800: push caller-frame-relative address A
  → CALL preCalc C107976, 32 argument bytes
  → preCalc FRM+32 contains A (not *A)
  → PUSH_S32 C143648: push A unchanged
  → CALL preBhop C143680, 24 argument bytes
  → preBhop FRM+20 contains A
  → LREF_S_PRI20 C167724: PRI←memory[A], original p read
  → SREF_S_PRI20 C168772: memory[A]←PRI, i.e. caller FRM−8←K
  → caller later LOAD_S−8; floatsub(v,p*); CS flGain argument
```

**[V]** Reverse argument pushes and AMX PROC frame layout put the first formal
at FRM+12. PreCalc's tuple is `(id,G,PG,categorized,v,&p,old,highJump)`;
its six-argument preBhop tuple is `(id,v,&p,old,bJumpbug,iel)`.
`PUSHADDR` adds the current frame base; `PUSH_S` loads the stored pointer;
`LREF_S` dereferences it; `SREF_S` stores through it. These distinct operations,
not matching offset numbers, prove provenance.

There is one explicit SREF speed write and no param-derived alternate STOR_I,
MOVS or second SREF write in the analyzed body. **[V]** The address does escape
to formatter Float varargs (C167876,168212,168488,168824), so an unconditional
"pointer never escapes" claim would be false. Formats have `pre %.3f`,
`post %.3f`, `max %.3f` fields. **[D/I]** The pinned AMXX formatter contract
reads Float varargs and writes its destination, not its Float operands;
installed native identity/destination disjointness remains a boundary.

| Other helper | preCalc call C / previous-speed load C | Audit result |
|---|---|---|
| preLadder | 142360/142332; 143168/143140 | LREF_S32 then PUSH_PRI: scalar, no speed address |
| preSlide | 142568/142540; 144868/144840 | Same scalar transport |
| preWater | 142740/142712; 145076/145048 | Same scalar transport |
| preFirstDD | 143304/143276 | Same scalar transport |
| preGstrafe | 143368/143340 | Same scalar; PUSHADDR−8 C143332 is preCalc's iel, not PreThink's speed |
| preFirstJump | 143504/143476 | Same scalar transport |
| preFalling | 144228/144200 | Same scalar transport |
| preBounce | 144472/144444 | Same scalar transport |
| preSlip | 144644/144608 | Same scalar transport |

**[V]** None receives A through these arguments; none runs before preBhop on
the selected route. **[I]** Ordinary isolated Pawn stack semantics therefore
exclude mutation of the caller local through those scalar arguments.
**[H]** This is not a proof against arbitrary native stack introspection,
corrupt state, all transitive global writes, or hidden aliases outside the
identified transport. Siblings can produce globals relevant to later/other
attempts; those effects are not equated with overwriting p*.

After preCalc C107976 there is no direct store or PUSHADDR−8 before the six
CS sites. Additional scalar reads go to calcLandingAir (§7); those cannot
write the caller local through their scalar argument. **[V/I]**

## 5. Exact local arithmetic and comparison

| C | Operation / dataflow [V] |
|---|---|
| 167300–167340 | pev(id,56,&local−68) |
| 167352–167400 | native17 floatmul, formal operands constant1067030938 and captured m; store x |
| 167412–167452 | native17 floatmul(x,x) |
| 167464–167488 | integer16 passed to compiled Float-minus-int operator C380 |
| 380–452 | convert formal arg2 using native0 float; native4 floatsub(arg1,converted16) |
| 167496–167524 | native19 floatsqroot; store M |
| 167724–167776 | load original p through A; compiled <= C1300; false jumps168720 |
| 168724–168772 | native17 floatmul(constant1061997773,M); write through A |

Compiled `<=` calls floatcmp(arg1,arg2) and compares its result `<=0`.
Thus the actual predicate is **not** an integer comparison of Float cells.
Constants: `1067030938 = 0x3f99999a = 1.2000000476837158`;
`1061997773 = 0x3f4ccccd = 0.800000011920929`.

**[I]** In real arithmetic one may write
`M≈sqrt((1.2m)^2−16)`, `K≈0.8M`. This is explanatory algebra, not bit-for-bit
runtime reproduction. Preserve native-call order, Float conversion of16,
intermediate rounding and compiled comparison. The installed Float/JIT/module
build is unidentified. Negative radicands, NaN, infinity, underflow and signed
zero must not be assigned invented behavior. In particular `!(p<=M)` is not
universally interchangeable with `p>M` for exceptional native comparisons.

The local formula has no vertical velocity, gravity, frame-time, current-v
or old-v input. Old-v affects caller bJumpbug and diagnostics; state affects
reachability. Selector56 is retained as a numeric native field here; a physics
interpretation of that field is not needed to establish these operations.

## 6. Reachability predicates

### A. Local verified predicate

**[V]** On normal entry/return with valid buffers and ordinary native contracts:
`write = (bJumpbug==0) && !FloatLE(p,M)`.
Earlier element/duck branches all reconverge; FOG/old-speed diagnostic branches
after successful `p<=M` do not lead back to the write. No minimum-current-speed
or extra jump-category comparison dominates C168772 inside preBhop.

### B. Caller predicate, bounded to captured state

Define values at preCalc entry:

```text
DD = !prevInDuck && !(prevButtons & 4) && (oldButtons & 4)
J  = !DD && (prevButtons & 2) && !(oldButtons & 2)
JB = (FOG == 1) && (oldHorizontalSpeedCell != 0)
CALL = !G && PG && !prevLadder && !DD && J && (FOG <= 10)
WRITE = PreThinkReachesPreCalc && CALL && !JB && !FloatLE(p,M)
```

**[V]** DD/J: C141648–141968; !G: C141988; PG: C143008;
!prevLadder: C143048; !DD: C143196; J: C143396;
FOG<=10: signed `10>=FOG` C143448; JB: C143532–143612.
There is no extra local `FOG>=0` guard. JB tests the Float cell against zero
with JZER, not a reconstructed Float comparison.

**[V]** G/PG are categorized globals D326980/D327112, not merely current and
previous raw ground bits. At C107816–107956 PreThink passes those values and
`PG && !physicalGround` as the separate categorized argument. The latter and
highJump are not correction gates. Ground's ladder/slide/water helpers are on
other branches and do not precede this selected call.

**[V/D]** PreThink initial normal guards require alive, selector69!=8,
`get_cvar_num(sv_gravity)>=2`, and `sv_maxvelocity==2000` (doc12 §3).
G is set from physical-ground-or-ladder and optional duck-release trace category
(doc12 §6). Buttons, previous flags/ladder/duck, FOG and old velocity are
retained state, not reconstructed solely from present physical velocity.

**[H]** B does not become a closed raw-gameplay predicate: native alive/trace
results, lifecycle/history initialization, earlier diagnostic/reset/helper
state writers and external scheduling remain inputs. `PreThinkReachesPreCalc`
means the actual C107976 event after those operations, not merely passing the
two initial guards. No prior report's partial state model is silently promoted
to a complete gameplay proof.

## 7. Propagation to all six calcStrafes calls

`W` below means WRITE above, compatible with the site's post-helper admission
predicate. All rows assume CS capacity admits the call. Site predicates A/Q/R
and height crossings are specified in doc12 §4, not replaced by W.

| Callsite | Original/corrected p* | Predicate | flGain expression and native C | Subsequent use | Evidence |
|---:|---|---|---|---|---|
| 110880 | p or K; W not excluded by G alone | doc12 A, S!=0, Mmode2, trigger or slide; joint physical reachability pending | floatsub(v,p*),110836; p load110804 | bad1: history, no good/gain/loss | [V/I] explicit argument construction |
| 112240 | p or K; dependent landing admission | A,Q,startDuck,cross start plane,R | floatsub(v,p*),112196; p load112164 | bad1; history and closure | [V/I] same operations individually decoded |
| 113728 | p or K; dependent landing admission | A,Q,!startDuck,cross lower plane,duck,R | floatsub(v,p*),113684; p load113652 | bad1; history and closure | [V/I] individual decode |
| 114252 | p or K; dependent landing admission | preceding lower-plane predicate,!duck,R | floatsub(v,p*),114208; p load114176 | bad1; history and closure | [V/I] individual decode |
| 114580 | p or K | A and !block after terminal branches | floatsub(v,p*),114536; p load114504 | bad0: selected-direction accounting enabled | [V/I] individual decode |
| 115148 | raw p with respect to this writer | G,!PG,S!=0,!block,(mode2 or sameHeight) | floatsub(v,p),115104; p load115072 | bad=ladder | [V/I] !G/PG correction route incompatible |

Each six-site construction loads p* then v and calls `floatsub`; none computes
gain before C107976. No restoring assignment was found. There is no direct G
write between preCalc and CS; G stores precede preCalc at C107132/107368,
and later category-history copy is C116008. No intervening G address argument
was identified. **[V/I]** This establishes ground incompatibility within the
audited transport, not immunity to arbitrary unknown-native memory effects.

**[V] Admission dependency:** scalar p* is also pushed at C111948,113436,113960
into calcLandingAir C111972,113460,113984. Its result participates in
`R=(mode!=2 || landing!=0)` before C112240/113728/114252 respectively
(tests C112112,113600,114124). **[H]** The complete transformation from p* to
landing was not reconstructed here; whether a correction actually changes
admission is unresolved, not asserted. It is incorrect to claim p* has no
pre-CS decision dependency. Other admission helpers remain bounded by doc12.

## 8. Impact on Phase4B metrics

This section compares supplied gains on the same admitted CS state; it does
not compare entire executions with potentially different landing admission.

| Metric | Direct or control-flow effect [V/I] | Evidence |
|---|---|---|
| g_flFrameGain | Records corrected gain even on bad1 | CS183584–183684 |
| g_iWSADGoodFrames | q only; !bad && gain>0; sign crossing can add a good frame | CS186696–187028 |
| g_flWSADGain | q only; !bad && gain>0: add supplied gain | CS186808–186932 |
| g_flWSADLoss | q only; !bad && not(gain>0): subtract supplied gain, including zero | CS187036–187160 |
| g_flStrafeGain/Loss | Copies changed direction totals when a row emits | CS190276–191080 |
| g_flStrafeEfficiency | 100*float(Good)/float(Frames); numerator may change, not direct gain ratio | CS191264–191464 |
| g_iWSADOverlaps | No dependence on scalar p*/gain in same-call update; previous key cardinality | CS189136–189624 |
| g_iWSADDesync | No demonstrated same-call dependence; uses previous vector, not corrected scalar | CS187200–188992 |
| g_flWSADAngle | No demonstrated same-call dependence; yaw delta and q | CS188996–189120 |

Frames increases for each previous active key, independently of gain sign.
q is selected by earliest start, independently of gain. Bad skips good/gain/loss
at C186708 but not history, Frames, overlaps, desync, angle or closure.
Counter changes through *different admission* remain possible dependencies,
not demonstrated effects on overlaps/desync. Existing resets and row filters
still apply; positive gain alone does not guarantee a higher emitted efficiency.

For finite nonnegative M with a correction, `K<p`. In real arithmetic,
`gainCorrected−gainRaw=p−K>0`; floating rounding can hide a small increase.
The strict `gain>0` comparison is the affected accounting branch, not a
separate positive/negative loss comparison. Conditions for sign changes:

| Raw → corrected | Real-arithmetic condition on same v,p,K | Result |
|---|---|---|
| negative → positive | K<v<p | q good/gain instead of loss, unless bad |
| positive → negative | impossible for K<p | No such finite-domain correction trace |
| zero → positive | v=p and K<p | q good/gain instead of zero loss, unless bad |
| positive → zero | impossible for K<p | No such finite-domain correction trace |
| negative → zero | v=K<p | zero loss update, still not good |

These inequalities explain direction; exact boundary results require the
native Float evaluation/rounding, not algebra alone. **[I/H]**

## 9. Edge cases

Let `C` mean the complete caller gate, `L` mean !JB && !FloatLE(p,M), and
`g=FloatSub(v,p*)`. Counter outcomes are §8, conditioned on admission and q.

| Case / entry | Reachable branch and p* | Gain / affected counters | Uncertainty |
|---|---|---|---|
| p=0, finite M>=0 | p<=M: preserve0 | g=v; no correction-induced change | Exceptional M excluded |
| v=0 | C&&L may write K; current v is not a local gate | g=−K, nonpositive for K>=0; no good increment | Whether caller states jointly occur |
| Constant horizontal norm v=p | C&&L: K, else p | positive after correction if K<p; otherwise zero | Exact rounding boundary |
| Raw positive gain v>p | correction lowers p | remains positive; larger gain total, same good test | Admission effects separate |
| Raw speed loss v<p | C&&L may write | loss remains, becomes zero, or becomes good according to v vs K | Native rounding |
| Proposed corrected value >p | impossible with finite M>=0 and p>M | No increasing-speed writer branch | Exceptional arithmetic not classified |
| Corrected value <p | sole finite correction case | gain nondecreases | Requires C&&L |
| Gain sign crossing | K<v<p | negative→positive possible in symbolic state | Not a demonstrated engine trajectory |
| Gravity0 | PreThink cvar<2 guard returns before chain | no CS from this invocation; resetVars runs | Direct helper call is outside callback path |
| Frame time0 | absent from local formula | same local p* if C/L/M same | Frame-time effects on preceding state not closed |
| First frame after reset | reset does not initialize every capture vector/category (doc12 §8) | use actual retained state; do not force p=0 or no correction | Full lifecycle initialization unresolved |
| Ground→air | G0,PG1 compatible; jump-edge and other gates still needed | K only if C&&L | Categorized versus physical transition |
| Bhop label | insufficient input | apply C and L, not name-based classification | Named gameplay category not evidence |
| Current ladder | physical ladder categorizes G1 in ordinary capture; correction G0 fails | p unchanged by this writer | Unknown native/global corruption excluded |
| Previous ladder | prevLadder nonzero blocks call | p unchanged | Numeric movetype mapping in doc12 |
| Water | no independent water gate inside local formula or !G route | apply C/L; later admission can be blocked by water | Full water/helper state not reduced |
| Attempt ends bad1 | if admitted, g uses p* | history changes, good/gain/loss skipped; other counters follow own rules | Three landing gates unresolved |
| K=0 | possible symbolic M=0 with p>0, !JB and C | p*=0, g=v | Whether selector56/native sqrt yields exact0 is not proven |

Writing zero is not an explicit constant-zero branch. The expression can
produce zero if its native inputs/results do; tiny positive products may also
depend on underflow handling. A negative square-root radicand is unresolved,
not silently clamped to zero by this reconstruction. **[V/I/H]**

## 10. Six static traces (not executions)

All traces assume normal native returns, valid indices and buffers, finite
ordinary Float values where inequalities are used. Additional admission
conditions are explicit assumptions, not claims of physical occurrence.

1. **No preBhop:** assume G1 at preCalc C141988. Ground branch bypasses
   C143680; no speed-reference write. If doc12 ground arrival predicates
   hold, CS115148 uses `FloatSub(v,p)` via C115104. Counters follow bad=ladder.
   Global/native alias exclusions remain bounded as §4. **[V/I]**
2. **Call without change:** assume C and JB0 and p<=M. C143680 enters;
   C167764 returns true, C167776 does not jump168720; diagnostics merge169048.
   p*=p. Assuming air fallback admission, C114536→114580 uses v−p, bad0;
   q good iff that supplied gain>0. No novel physical state assumed. **[V/I]**
3. **Single write:** assume C, JB0, finite M>=0 and p>M.
   C167776→168720; C168756 computes K; C168772 writes A. p*=K.
   Assuming fallback admission, C114536 supplies v−K to CS114580.
   History records it; q accounting depends on its sign. **[V/I]**
4. **Sign change:** same as3, additionally K<v<p and enough separation for
   native rounding to preserve strict signs. Raw gain<0; corrected gain>0.
   CS186708 permits accounting if bad0, strict positive comparison selects
   q gain and good rather than loss. Efficiency's numerator may increase;
   denominator rule is unchanged. Actual engine reachability is unproven. **[I]**
5. **bad0 without correction:** assume C but JB1 (FOG1 and old-speed cell
   nonzero at C143532–143612). C167544 selects diagnostic branch; jump169048
   skips write. Assume !block fallback admission C114432→114580; gain=v−p,
   not v−K. History/F update and q accounting apply normally. **[V/I]**
6. **bad1 with symbolic corrected input:** assume C, JB0, p>M, plus the
   post-helper lower-plane predicates and R true for C113728. C168772 sets K;
   C113436 passes K by value to calcLandingAir C113460; assumed R passes
   C113600; C113684 computes v−K; C113728 passes bad1.
   CS records corrected history but C186708 skips good/gain/loss. F/O/D/angle
   remain governed by their own inputs; closure requested. Joint caller-state
   consistency and landing transformation are unresolved. **[V/I/H]**

## 11. Cross-check and proposed errata

Prior reports remain unchanged.

| Earlier statement | Disposition / proposed correction |
|---|---|
| Doc11 §3 row flGain: current norm minus previous norm | Conditional only: subtract post-helper previous scalar; raw norm remains correct when no write |
| Doc12 §4 reference forwarding and C168772 writer | Confirmed independently; add exact formula, !JB and !(p<=M) |
| Doc12 all six use v−p* | Confirmed per native call; do not infer every site can receive K; C115148 cannot on the bounded normal route |
| Doc12 correction predicate unknown | Local predicate now resolved; raw-gameplay/lifecycle predicate remains partial |
| Doc11 good, gain/loss, efficiency rules | Still valid for supplied gain; sign may differ from raw speed difference |
| Doc11 desync uses previous vector | Confirmed distinction: changing scalar p* does not replace that vector |
| Doc12 landing R dependency | Stronger dependency identified: three calcLandingAir calls receive p* before admission |
| Interpretation of preBhop as bhop-only | Not established by its name; use concrete G/PG/button/FOG/JB gates |

## 12. Remaining uncertainty and completion verdict

**Partial success, not a blocked pointer reconstruction.** Pointer provenance,
the single explicit write, exact local arithmetic order, local/captured-state
gates, six gain constructions and metric consumers are established. The report
does not meet the stronger "any physical PreThink route" success criterion.

Unclosed boundaries:

* Actual installed AMXX/Float/formatter/fakemeta/engine build, exceptional
  arithmetic and native destination disjointness.
* Complete lifecycle/writer inventory for category, FOG, velocity/button history
  and earlier helper-produced attempt state; no global alias theorem.
* Complete calcLandingAir transformation from p* into landing/admission on
  three routes, and joint reachability of correction with each terminal branch.
* Physics meaning of selector56 and its attainable values on this installation;
  no assumed numeric maxspeed/gravity/frame-time values fill these gaps.

## 13. Recommendation for the next authorized phase

Investigate statically the three `calcLandingAir` calls and all writers of its
landing result, then close joint branch reachability using the category/FOG
history producers. Identify installed native-source/build provenance before
claiming bitwise fidelity or exceptional-value behavior. Do not implement KZ
Coach, capture live data, start a server, or advance phase without authorization.

## 14. Verification scope

Hashes, full decode/target validation, existing-output reproduction, 93-block
coverage, one explicit speed SREF and one normal return were checked. The
inspector's 27 tests passed. Documentation/graph cross-links were checked.
No RED/GREEN behavior test applies to this passive static report; there was no
inspector or application behavior change. Native execution and physical tests
were deliberately not performed. Generated graphs are evidence, not emulators.
