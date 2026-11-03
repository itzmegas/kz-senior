# Read-only AMXX v8 inspector

Inspect the pinned KZ-Rush binary without executing bytecode. Python 3.9+ and
its standard library are sufficient; no installation, Pawn compiler, or server
is used. Run commands from the repository root.

## Quick path

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.amx_inspector.test_inspector -v
PYTHONDONTWRITEBYTECODE=1 python3 -m tools.amx_inspector.inspector --output analysis/amx_disassembly-new
```

The default input is `reference/kz_jump_stats.amxx`. The default output is
`analysis/amx_disassembly`. **Choose a new output directory** when reproducing
the checked-in listings: the tool refuses existing output directories rather
than overwriting previous evidence. It also refuses output inside the project's
`reference/`, including resolved symlink aliases. The input is opened `rb`.
The tool never writes an extracted image.

## Evidence

| Output | Meaning |
| --- | --- |
| `<function>.txt` | C/I, original bytes, numeric opcode, signed operands, length, targets and symbol annotations |
| `<function>.blocks.json` | Structural basic blocks, successors, calls and unresolved indirect control |
| `validation.json` | Identity, header, progression and exact byte/instruction counts |
| `opcodes.json` | Explicit 144-entry ISA plus global boundary-scan frequencies |
| `symbols.json` | Public/native tables and bounded debug records, including locals and lines |
| `references.json` | Exact-address confirmed slot accesses and candidate constant/address matches |

`C` is code-relative, `I` is image-absolute, `D` is data-relative, and `FRM` is
signed frame-relative. Displayed cell operands retain signed decimal values and
their original bytes. Neither names nor equal constants prove a data dependency.

## Scope and failures

Only the expected AMXX/image hashes and target coordinates are admitted by the
CLI. The low-level parsing/decoding functions accept controlled synthetic inputs
for tests; they do not provide an identity-bypass CLI option. The supported
container is exactly one 32-bit AMXX v3 entry, non-compact AMX v8; the bounded
decompressor caps images at 32 MiB. Other variants fail explicitly.

Regions run in the order `cmdDetailed`, `fwCmdStart`, `calcStrafes`. A format-only
global scan after the first local decode establishes independent instruction
boundaries; it does **not** reconstruct or validate the whole plugin's CFG.
Direct targets are checked against that map, including targets of any referenced
external case table. CASETBL is not executable. No unknown bytes are skipped.

Identity/header/debug errors exit nonzero without creating output. A region
error produces an explicitly `INVALID / PARTIAL` listing, records its reason,
exits nonzero, and prevents later stages. Existing output is never reused, so
an old successful listing cannot masquerade as a new failed stage.

The inspector resolves only exact symbol addresses and scopes. It does not
propagate pointers, infer array element accesses, reconstruct formulas, or
execute native/indirect calls. Native direct pointers are not native-table
indices. `SYSREQ_N` does not exist in this pinned ISA.

See [the validation report](../../docs/10-amx-disassembly-validation.md) for
normative sources, observed results, and the next research boundary.
