# Phase 4 — validated static AMXX v8 disassembly

## 1. Executive summary

**[V] All three requested regions are fully decoded and structurally validated.**
There are no unknown opcodes, truncated instructions, invalid direct control
targets, or invalid native indices in those regions. Both original hashes match.
The implementation is Python standard-library-only and never executes Pawn,
natives, a compiler, or a server.

This is **not a decompilation**. In particular, none of the twelve requested
frame/strafe arrays has a demonstrated element read/write in this phase: their
base-address constant matches remain candidates until pointer flow is traced.

Evidence categories throughout: **[V]** verified in bytes/instructions or an
observed check; **[D]** documented in the pinned normative source; **[I]** inferred;
**[H]** hypothesis. No metric formula is asserted as verified.

## 2. Binary identity and coordinates

| [V] Property | Observed value |
| --- | --- |
| Input | `reference/kz_jump_stats.amxx` |
| AMXX bytes | 114387 |
| AMXX SHA-256, before and after | `8398b9c2fbb61dfca7492c2767cd9a59fbd1be871f6b5bbf95e024c2d0ba541e` |
| AMXX magic / version / entries | `0x414d5858` / `0x0300` / 1 |
| Entry cell / compressed bytes / offset | 4 / 114363 / 24 |
| Image bytes / SHA-256 | 1684270 / `d5e4ac324cf57feca12d2ced0ecec5eb53ca44686b5b9bb8cec93d41610ec433` |
| Inner magic / file version / VM version / flags | `0xf1e0` / 8 / 8 / 2 (DEBUG, not compact) |
| `cod`, `dat`, `hea`, `size`, `stp` | 4912, 337028, 1576260, 1576260, 1592644 |
| Code | C `[0,332116)`; I `[4912,337028)` |
| Initialized data | D `[0,1239232)`; I `[337028,1576260)` |
| Debug | I `[1576260,1684270)` |

**[D]** `C` addresses are relative to `cod`; `I=cod+C`. Data addresses use
`I=dat+D`, not `cod+D`. Frame operands are signed `FRM` offsets and have no
static image address. Original cell bytes remain in every listing.

## 3. Normative source and previous research

Read before implementation: [08](08-kz-rush-binary-analysis.md),
[09](09-amx-disassembler-research.md),
[09b](09b-kztimer-jumpstats-comparison.md), and
[09c](09c-exolent-jumpstats-source-analysis.md). Their semantic comparisons are
not used as opcode specifications.

All normative links below use official AMX Mod X revision
`8fc12670ea86470a0bfed4c35db5de73d3a39e8a`:

- **[D]** [amx.cpp:131–279](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.cpp#L131): numeric OPCODE enumeration.
- **[D]** [amx.cpp:508–775](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.cpp#L508): `amx_BrowseRelocate`, fixed/variable lengths and absolute relocation.
- **[D]** [amx.cpp:2075–2110](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.cpp#L2075): CALL, JUMP and `JREL`; `JREL` target is `C+8+signed_operand`.
- **[D]** [amx.cpp:2445–2521](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.cpp#L2445): native calls, inline debug and SWITCH/CASETBL dispatch.
- **[D]** [amx.h:263–281](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amx.h#L263), [amxxfile.cpp](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amxxfile.cpp): packed image header and container entry reading.
- **[D]** [amxdbg.h:63–123](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amxdbg.h#L63), [amxdbg.cpp:82–230](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/amxmodx/amxdbg.cpp#L82): debug records and traversal.
- **[D]** [compiler/libpc300/sc.h:235–237](https://github.com/alliedmodders/amxmodx/blob/8fc12670ea86470a0bfed4c35db5de73d3a39e8a/compiler/libpc300/sc.h#L235): global=0, local=1, static=2. Static variables have D storage with local scope, not FRM storage.

**[V]** A separate source comparison found the tool's complete 145-name enum
(including invalid NONE) identical to the pinned enum. All 56 one-operand,
66 zero-operand and 15 absolute-target entries from the corresponding relocation
groups matched the tool's lengths; SYSREQ_C and obsolete debug formats were
checked separately. `PROC=46`, `CALL=49`, `MOVS=117`, `FLOAT_MUL=138`.

Source bytes read from the public pinned revision had these SHA-256 values
(the tool runs offline and does not download them):

| File | SHA-256 |
| --- | --- |
| `amx.cpp` | `8c78ef4b2a216a71482cbeb76ef0a7fb3fa5717494cd03451172c9cbefdc89f9` |
| `amx.h` | `364eff0d132977ee69752b63c8f698244aa07e681e01ff8e111f1b90c3d9229d` |
| `amxdbg.h` | `e279c50e0f0bf051e0872d514578373374b7d33d0215236c66f390d6e8c32352` |
| `amxdbg.cpp` | `7ad8492fb59759d57d8a7168106bc9f3ac53e6e8a797e870f1e3821fde5db424` |
| `amxxfile.cpp` | `577af2c4d58058a3a8d633a5412e2c9457157e0ba533d82a08f0976c02e45318` |

## 4. Tool design and reproduction

Source: [`tools/amx_inspector/inspector.py`](../tools/amx_inspector/inspector.py).
See its [README](../tools/amx_inspector/README.md) for output definitions and
supported-format restrictions.

1. Open input `rb`; validate pinned SHA-256, AMXX structure, bounded zlib stream,
   image hash, packed header, exact coordinates and metadata bounds.
2. Parse public/native definitions and debug files, lines, symbols/dimensions,
   tags, machines and states. Require any remaining debug bytes to be zero.
3. Decode A locally. Establish independent instruction boundaries by a linear,
   format-only scan from C=0. No other function semantics are interpreted.
4. Validate A against this map; only then decode/validate B, then C. Each region
   must start at its matching debug entry and PROC, end exactly at the independently
   established debug endpoint, and have no terminal fallthrough past that endpoint.
5. Check direct control destinations, table destinations, executable/table
   distinction, and native indices; annotate exact-address symbol evidence.
6. Write deterministic text/JSON outputs to a new directory outside `reference/`.
   Refuse existing output; identity errors produce no listing. Region failures
   produce explicit INVALID/PARTIAL evidence and stop progression.

```sh
# From repository root:
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.amx_inspector.test_inspector -v
PYTHONDONTWRITEBYTECODE=1 python3 -m tools.amx_inspector.inspector --output analysis/amx_disassembly-new
```

**[V]** `analysis/amx_disassembly/` contains the delivered result. For comparison,
generate to a new directory and use `diff -ru` against it; do not overwrite
evidence. Output has no timestamps or absolute workspace paths added by the tool.
Debug strings are original binary metadata, not newly inferred source paths.

## 5. Opcode coverage

**[V]** Explicit formats cover all 144 non-NONE opcodes in the pinned enum.
The global boundary scan covers 332116 bytes and 51250 records, including case
tables, with **75 distinct opcodes**, no unknown opcode and no truncated record.
This does not claim global CFG validation. Frequencies and formats are in
[`opcodes.json`](../analysis/amx_disassembly/opcodes.json).

**[D]** CALL, ordinary jumps and SWITCH operands are absolute C addresses in
this unrelocated file. CASETBL is `opcode,count,default,(value,target)*count`,
length `4*(3+2*count)`; it is not executable. Obsolete FILE/SYMBOL use a byte-counted
payload, LINE/SRANGE have two cells, SYMTAG one. SYSREQ_C takes a native index;
SYSREQ_D takes a direct native pointer. **SYSREQ_N is absent** from this enum.
The tool never substitutes a newer Pawn/SourcePawn ISA.

## 6. Automated checks

**[V]** 27 tests pass with standard-library `unittest`. Synthetic cases cover
valid/invalid headers and magic, both hashes, bad zlib and stream bounds,
known/unknown/truncated instructions, signed FRM, C/I/D, absolute jumps,
signed relative jumps, calls, native index bounds, SWITCH and variable CASETBL,
invalid/out-of-range/non-boundary/table targets, external-table targets,
executable fallthrough into table data, static-symbol storage, native-flow
metadata, indirect CIP writes through SCTRL register 6, obsolete inline debug,
and enum anchors. SCTRL's control behavior follows `amx.cpp:1984–2005`.

**[V]** The real-input integration test checks A/B/C instruction and byte counts,
two identical artifact generations, successful validation, and unchanged input
hash. Initial RED was an unavailable inspector module. A later focused RED
exposed three implementation gaps (external case-table targets, static-symbol
storage, native flow metadata); one correction batch fixed all three, and the
26-test suite passed. An additional RED/GREEN control-register test pins SCTRL
register 6 as an unresolved indirect CIP write, not fallthrough; SCTRL is absent
from the target binary. The final suite has 27 tests. No runtime execution is
part of any test.

## 7–9. Progressive region validation

| [V] Region | C interval | Bytes | Records | Basic blocks | Direct target operands |
| --- | --- | ---: | ---: | ---: | ---: |
| `cmdDetailed` | `[95108,95376)` | 268 | 42 | 5 | 4 |
| `fwCmdStart` | `[99728,100076)` | 348 | 55 | 8 | 2 |
| `calcStrafes` | `[182596,192488)` | 9892 | 1729 | 169 | 114 |

**[V]** Each interval agrees with its function debug symbol and independent
global instruction boundaries, starts with PROC, and ends with RETN exactly at
the requested endpoint. This validates structural intervals, not exclusive
source-level function ownership. Every direct target is an instruction boundary
within global code; external targets are explicitly marked, not rejected.

**[V]** `cmdDetailed` has two CALLs to C=10512 (`client_print_f`), one conditional
jump and one JUMP. `fwCmdStart` has one conditional jump, one CALL to C=212
(`operator/(_:,Float:)`) and four SYSREQ_C instructions naming `is_user_alive`
or `get_uc`. Its indirect LOAD_I/STOR_I instructions remain visible without
claiming their pointee semantics.

**[V]** `calcStrafes` has thirteen CALL instructions and eight SYSREQ_C
instructions. Direct call destinations include C=684, 756, 1200, **192488**,
211520, 212028, 212488 and 212980. C=192488 is outside this interval but is a
valid global boundary named `saveBeam`; it is not an error. Neither a debug
interval end nor a call destination is treated as a proof of formula semantics.

**[V]** No SWITCH, CASETBL, JREL, CALL_PRI, JUMP_PRI, SYSREQ_PRI or SYSREQ_D occurs
inside these three regions. Switch/case and JREL behavior is tested synthetically;
global observed switches/tables are counted, not semantically interpreted.

## 10. Calls and symbol references

Full evidence: [`references.json`](../analysis/amx_disassembly/references.json),
the three `.txt` listings and `.blocks.json` graphs. `symbols.json` preserves
118 public definitions, 111 natives, 1280 debug symbols, 4473 line records,
6 files, 71 tags, 1 empty automaton, 0 states and 31780 trailing zero bytes.

**[V] Confirmed slot references:** frame-local/argument operands such as
`cmdDetailed` C=95128 `LOAD_S_PRI FRM=12` (`id`) are direct slot reads. A direct
global example in `calcStrafes` is C=190060 `LOAD_PRI D=455416`, debug name
`g_cvarStrafesFullOverlap`. This proves a slot read, not a cvar interpretation
or any efficiency/overlap formula. ADDR/PUSHADDR prove address formation;
LREF/SREF prove slot-level pointer access, not a resolved pointee.

**[V] Candidate constants:** all twelve requested array names match CONST_ALT
operands in `calcStrafes`; the numeric coincidence and debug addresses are
verified, but an effective array access remains **[I] candidate**, not confirmed.

| Debug symbol | D base / CONST_ALT operand | Example instruction C |
| --- | ---: | ---: |
| `g_flFrameGain` | 808 | 183584 |
| `g_iFrameWSAD` | 66940 | 183692 |
| `g_iFrameDirection` | 133072 | 183980 |
| `g_iFrameStrafe` | 199204 | 184212 |
| `g_iFrameCount` | 265336 | 182608 |
| `g_iStrafeFrames` | 277480 | 190384 |
| `g_flStrafeGain` | 284212 | 190560 |
| `g_flStrafeLoss` | 290944 | 190736 |
| `g_iStrafeOverlaps` | 297676 | 190912 |
| `g_flStrafeEfficiency` | 304408 | 191088 |
| `g_iStrafeDesync` | 311140 | 191472 |
| `g_flStrafeAngle` | 317872 | 191648 |

Constants can coincide with unrelated addresses: for example, an immediate
argument-byte-count equal to `MapName`'s D address is deliberately only a candidate.
No name-based classification is upgraded to a data-flow claim.

## 11. Unresolved structures and blockers

**[V] No blocking decoding/control inconsistency remains in the requested regions.**
No register-indirect call/jump, SCTRL, or direct-native-pointer form appears in
the global boundary scan. The
31780-byte debug tail is verified zero padding; it is not interpreted as records.
The source compiler build identity cannot be established from this binary;
compatibility here is demonstrated structurally against the pinned ISA, not
asserted from tool/header recognition alone.

Unresolved: register/pointer propagation, indexed array element identity,
aliasing, native side effects and interprocedural dependencies. These do not
block a static instruction listing. They do block definitive metric formulas.

## 12. Limitations and safety

- One specific 32-bit non-compact AMXX/AMX format and pinned CLI input only;
  no general-purpose loader, relocation, bytecode execution or decompiler.
- The global scan validates formats/boundaries, not every function or global
  edge/native index. Only the three requested regions receive CFG validation.
  An unknown record anywhere in that scan blocks boundary establishment rather
  than guessing through it, even if it lies outside a requested region.
- Basic blocks are structural, include unreachable code, and split at calls;
  they do not prove source-level reachability or unique function ownership.
- Exact-address symbol matching does not prove pointer provenance. Array extents
  are recorded from debug dimensions but are not used to guess memory accesses.
- Debug line numbers are preserved zero-based; no unavailable source is
  reconstructed. FILE/SYMBOL inline payloads remain opaque, bounded records.
- No reference file, production code, server, compiler, statistics or game hook
  was modified; no dependency was installed. Ghidra/REA/Lysis were not used.

## 13. Recommended next phase — not implemented

Trace register and stack values within the validated `calcStrafes` blocks,
starting from the twelve candidate base constants. For each candidate, prove
the index calculation and effective LOAD_I/STOR_I (or callee effect), retaining
C-address evidence and unresolved aliases. Only then investigate formulas and
compare with the source implementations in 09b/09c. Do not infer player
diagnostics, success rules or live capture from the current listings.
